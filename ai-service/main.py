"""
农业诊断 AI 服务 — FastAPI 入口
启动: uvicorn main:app --reload --port 8000
文档: http://localhost:8000/docs

环境变量(可选, 在 .env 文件中配置):
  DEEPSEEK_API_KEY  — DeepSeek API Key (不设置则用规则引擎兜底)

功能模块:
  models/disease_db.py       — 图像识别（6作物35+病害）
  rag/knowledge_base.py      — RAG知识检索（30+防治方案）
  rag/vector_store.py        — 真实RAG ChromaDB（可选）
  models/real_model.py       — 真实图像识别 HuggingFace（可选）
  agent/diagnosis_agent.py   — Agent综合研判
  data_sources/weather_api.py — 和风天气API + 模拟兜底
  data_sources/market_api.py  — 市场价格数据
  data_sources/bulletin_api.py — 农业病虫通报
  data/knowledge/            — 农技知识文档（6文件）

模式切换: USE_REAL_MODEL / USE_REAL_RAG
"""
# 加载 .env 文件（无需额外依赖）
import os
from pathlib import Path
_env_path = Path(__file__).parent / ".env"
if _env_path.exists():
    for _line in _env_path.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip())
    print("[STARTUP] .env loaded")

from fastapi import FastAPI, UploadFile, File, Form, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="农业诊断AI服务", version="2.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# 模式配置
# ============================================================
USE_REAL_MODEL = True    # HSV像素分析真实模型
USE_REAL_RAG = True      # TF-IDF 向量检索


# ============================================================
# 响应模型
# ============================================================
class DiagnosisResponse(BaseModel):
    disease: str
    confidence: float
    symptoms: list[str]
    severity: str
    rag_result: dict
    agent_opinion: dict


@app.on_event("startup")
async def startup():
    """服务启动时加载模型和向量库"""
    if USE_REAL_RAG:
        try:
            from rag.vector_store import load_index
            load_index()
            print("[STARTUP] 真实 RAG 已加载")
        except Exception as e:
            print(f"[STARTUP] RAG 加载失败: {e}")

    if USE_REAL_MODEL:
        from models.real_model import is_available
        print(f"[STARTUP] 真实模型(像素分析): {'可用' if is_available() else '不可用(需pip install pillow)'}")

    # 报告数据源状态
    from data_sources.weather_api import is_real_available as weather_ok
    print(f"[STARTUP] 天气API: {'真实' if weather_ok() else '模拟'} "
          f"(设置环境变量 QWEATHER_KEY 启用真实API)")


# ============================================================
# 核心接口
# ============================================================

@app.get("/api/health")
def health():
    from data_sources.weather_api import is_real_available as weather_ok
    model_type = "hsv_pixel_analysis" if USE_REAL_MODEL else "simulated"
    rag_type = "tfidf_vector" if USE_REAL_RAG else "keyword_match"
    return {
        "status": "ok",
        "version": "2.1.0",
        "model": model_type,
        "rag": rag_type,
        "weather_api": "open_meteo" if weather_ok() else "simulated",
        "crops_covered": list(DISEASE_DB.keys()),
        "diseases_count": sum(len(v) for v in DISEASE_DB.values()),
        "knowledge_entries": len(KNOWLEDGE_BASE),
    }


@app.post("/api/diagnose", response_model=DiagnosisResponse)
async def diagnose(
    image: UploadFile = File(...),
    crop_type: str = Form(...),
    growth_stage: str = Form(...),
    field_location: str = Form(...),
):
    """
    核心接口：接收图片和作物信息，返回完整诊断结果。
    流程: 图像识别 → 获取实时天气 → RAG检索 → Agent综合研判
    """
    image_bytes = await image.read()

    # 输入校验
    if len(image_bytes) == 0:
        return JSONResponse(status_code=400, content={"code": 400, "message": "图片不能为空"})
    if len(image_bytes) > 10 * 1024 * 1024:
        return JSONResponse(status_code=400, content={"code": 400, "message": "图片大小不能超过10MB"})

    try:
        from PIL import Image
        import io
        Image.open(io.BytesIO(image_bytes)).verify()
    except Exception:
        return JSONResponse(status_code=400, content={"code": 400, "message": "无法识别的图片格式(仅支持JPG/PNG)"})

    try:
        # --- 0. 并行: 图像识别 + 天气获取 ---
        import asyncio
        from data_sources.weather_api import get_weather

        async def _recognize():
            if USE_REAL_MODEL:
                return _recognize_real(image_bytes, crop_type)
            else:
                return recognize_disease(image_bytes, crop_type)

        recognition_future = asyncio.create_task(_recognize())
        weather_future = asyncio.create_task(get_weather(field_location))

        recognition = await recognition_future
        weather_data = await weather_future

        # --- 2. RAG 检索 ---
        if USE_REAL_RAG:
            rag = _retrieve_real(recognition["disease"], crop_type)
        else:
            rag = retrieve_knowledge(recognition["disease"], crop_type)

        # --- 3. Agent 综合研判（传入真实天气数据） ---
        agent = await agent_analysis(
            recognition, rag, crop_type, growth_stage, field_location,
            weather_data=weather_data,
        )

        return DiagnosisResponse(
            disease=recognition["disease"],
            confidence=recognition["confidence"],
            symptoms=recognition["symptoms"],
            severity=recognition["severity"],
            rag_result=rag,
            agent_opinion=agent,
        )

    except Exception as e:
        print(f"[ERROR] /api/diagnose failed: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"code": 500, "message": f"Internal error: {str(e)[:200]}"},
        )


# ============================================================
# 数据接口（供前端数据看板使用）
# ============================================================

@app.get("/api/weather/{location}")
async def get_weather_endpoint(location: str):
    """
    获取指定地点的天气数据。
    前端数据看板 → 天气趋势图
    """
    from data_sources.weather_api import get_weather
    return await get_weather(location)


@app.get("/api/market-prices")
def get_market_prices(
    crop_type: str = Query("番茄", description="作物类型"),
    days: int = Query(30, description="查询天数"),
):
    """
    获取市场价格历史数据。
    前端数据看板 → 价格趋势图
    """
    from data_sources.market_api import get_prices, get_price_summary
    return {
        "crop_type": crop_type,
        "summary": get_price_summary(crop_type),
        "records": get_prices(crop_type, days),
    }


@app.get("/api/bulletins")
def get_bulletins(
    crop_type: str = Query("", description="作物过滤"),
    disease: str = Query("", description="病害过滤"),
):
    """
    搜索相关农业病虫通报。
    """
    from data_sources.bulletin_api import search_bulletins
    return {
        "bulletins": search_bulletins(crop_type, disease),
    }


# ============================================================
# 真实模型调用（可选）
# ============================================================
def _recognize_real(image_bytes: bytes, crop_type: str) -> dict:
    """使用 ResNet50 深度学习模型识别病害"""
    from models.real_model import recognize_image

    results = recognize_image(image_bytes)
    if not results:
        return recognize_disease(image_bytes, crop_type)

    # top-3 相似病害
    top = results[0]
    alternatives = [r["label"] for r in results[1:4] if r["score"] > 0.3]

    return {
        "disease": top["label"],
        "category": top.get("category", ""),
        "confidence": round(top["score"], 4),
        "symptoms": (["ResNet50特征匹配 (2048维)", f"备选: {', '.join(alternatives)}"]
                     if alternatives else ["ResNet50特征匹配 (2048维)"]),
        "severity": top.get("severity", "无法判断"),
    }


def _retrieve_real(disease: str, crop_type: str) -> dict:
    from rag.vector_store import search as vector_search
    query = f"{crop_type} {disease} 防治方法 症状 药剂"
    results = vector_search(query, k=3)
    if not results:
        return retrieve_knowledge(disease, crop_type)
    best = results[0]
    detail = "\n".join([r["content"][:300] for r in results])
    sources = list(set(r["source"] for r in results))
    return {
        "summary": best["content"][:100],
        "detail": detail,
        "source_title": "、".join(sources),
        "source_section": f"向量检索 (相似度: {best['score']:.2%})",
    }


# ============================================================
# 导入模拟模块
# ============================================================
from models.disease_db import DISEASE_DB, recognize_disease
from rag.knowledge_base import KNOWLEDGE_BASE, retrieve_knowledge
from agent.diagnosis_agent import agent_analysis
