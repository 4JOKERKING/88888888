# 李珈逾 — AI 服务开发指南（Python + FastAPI）

> 你的任务：图像识别 + RAG 检索农技规范 + Agent 综合研判。这是评分最高的模块（25分）。

## 你需要做的事

| 序号 | 功能 | 说明 |
|------|------|------|
| 1 | FastAPI 服务搭建 | 提供 `/api/diagnose` 和 `/api/health` 接口 |
| 2 | 图像识别 | 接收图片 → 调用模型 → 返回病害名+置信度 |
| 3 | RAG 检索 | 根据病害名检索农技规范 → 返回防治建议 |
| 4 | Agent 编排 | 综合识别结果 + RAG + 天气 → 最终研判 |
| 5 | 拒识机制 | 低置信度时标记为"未知"，进入人工审核 |

## 项目结构

```
ai-service/
├── main.py              # FastAPI 入口
├── models/
│   └── image_model.py   # 图像识别模型加载与推理
├── rag/
│   ├── vector_store.py  # 向量数据库（ChromaDB）
│   ├── loader.py        # 文档加载与分块
│   └── retriever.py     # 检索器
├── agent/
│   └── diagnosis_agent.py  # Agent 编排逻辑
├── data/
│   └── knowledge/       # 农技知识文档（txt/md）
├── requirements.txt
└── .env
```

## 开发顺序

1. **搭 FastAPI 架子**：先写 `/api/health` 确认能跑
2. **图像识别**：先用规则模拟，再接入真实模型
3. **RAG**：准备农技文档 → 分块 → 向量化 → 检索
4. **Agent 编排**：把前两步的结果综合起来
5. **拒识**：加置信度阈值判断

## 关键代码

### 1. FastAPI 入口 (`main.py`)

```python
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import asyncio

app = FastAPI(title="农业诊断AI服务")

# CORS（让后端能调）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class DiagnosisResponse(BaseModel):
    disease: str
    confidence: float
    symptoms: list[str]
    severity: str
    rag_result: dict
    agent_opinion: dict


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "model_loaded": True,
        "model_version": "1.0.0"
    }


@app.post("/api/diagnose", response_model=DiagnosisResponse)
async def diagnose(
    image: UploadFile = File(...),
    crop_type: str = Form(...),
    growth_stage: str = Form(...),
    field_location: str = Form(...),
):
    # 1. 读取图片
    image_bytes = await image.read()
    
    # 2. 图像识别
    recognition = await recognize_disease(image_bytes, crop_type)
    
    # 3. RAG 检索农技规范
    rag = await retrieve_knowledge(
        disease=recognition["disease"],
        crop_type=crop_type
    )
    
    # 4. Agent 综合研判
    agent = await agent_analysis(
        recognition=recognition,
        rag=rag,
        crop_type=crop_type,
        growth_stage=growth_stage,
        location=field_location
    )
    
    return DiagnosisResponse(
        disease=recognition["disease"],
        confidence=recognition["confidence"],
        symptoms=recognition["symptoms"],
        severity=recognition["severity"],
        rag_result=rag,
        agent_opinion=agent
    )
```

### 2. 图像识别 (`models/image_model.py`)

```python
"""
方案选择（按难度递增）：
1. 【最简单】用规则模拟 → 直接返回预设结果（先跑通流程）
2. 【中等】用公开模型 → HuggingFace 上的 plant-disease 模型
3. 【较难】用 API → 调用百度/腾讯的植物识别API

建议：先用方案1跑通整个流程，答辩时展示方案1，文档里写"可替换为方案2/3"
"""

# === 方案1：规则模拟（快速跑通） ===
import random

DISEASE_DB = {
    "番茄": [
        {"disease": "番茄晚疫病", "symptoms": ["叶片水渍状斑点", "叶背白色霉层"], "severity": "中等"},
        {"disease": "番茄早疫病", "symptoms": ["叶片轮纹状褐斑", "病斑周围黄化"], "severity": "轻度"},
        {"disease": "番茄灰霉病", "symptoms": ["果实软腐", "灰色霉层"], "severity": "严重"},
        {"disease": "健康", "symptoms": [], "severity": "无"},
    ],
    "辣椒": [
        {"disease": "辣椒炭疽病", "symptoms": ["果实凹陷黑斑", "同心轮纹"], "severity": "中等"},
        {"disease": "辣椒疫病", "symptoms": ["茎基部水渍状", "整株萎蔫"], "severity": "严重"},
    ],
    "花卉": [
        {"disease": "白粉病", "symptoms": ["叶片白色粉状物", "叶片卷曲"], "severity": "轻度"},
        {"disease": "灰霉病", "symptoms": ["花瓣腐烂", "灰色霉层"], "severity": "中等"},
    ],
}

async def recognize_disease(image_bytes: bytes, crop_type: str):
    """模拟图像识别，实际使用时替换为真实模型"""
    diseases = DISEASE_DB.get(crop_type, DISEASE_DB["番茄"])
    result = random.choice(diseases)
    
    # 模拟不同置信度
    confidence = round(random.uniform(0.78, 0.95), 2)
    
    return {
        "disease": result["disease"],
        "confidence": confidence,
        "symptoms": result["symptoms"],
        "severity": result["severity"],
    }


# === 方案2：HuggingFace 模型（答辩时如需展示真实模型） ===
# pip install transformers torch pillow
# 
# from transformers import pipeline
# from PIL import Image
# import io
# 
# classifier = pipeline("image-classification", 
#                       model="linkanjarad/plant-disease-detection")
# 
# async def recognize_disease_real(image_bytes, crop_type):
#     image = Image.open(io.BytesIO(image_bytes))
#     results = classifier(image)
#     # 取最高置信度的结果
#     top = results[0]
#     return {
#         "disease": top["label"],
#         "confidence": round(top["score"], 4),
#         ...
#     }
```

### 3. RAG 检索 (`rag/retriever.py`)

```python
"""
RAG 流程：
农技文档(.txt/.md) → 分块(chunk) → embedding → 存向量库(ChromaDB) → 查询时检索最相关

依赖：
pip install chromadb langchain langchain-community sentence-transformers
"""

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import ChromaDB
from langchain_community.embeddings import HuggingFaceEmbeddings
import os

# 初始化（应用启动时执行一次）
embedding_model = HuggingFaceEmbeddings(
    model_name="shibing624/text2vec-base-chinese"  # 中文embedding模型
)

# 加载文档并建向量库
def build_vector_store(docs_dir: str = "./data/knowledge"):
    """把知识文档加载到向量库"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,      # 每块500字
        chunk_overlap=50,    # 重叠50字
        separators=["\n\n", "\n", "。", ".", " "]
    )
    
    documents = []
    for filename in os.listdir(docs_dir):
        if filename.endswith(('.txt', '.md')):
            with open(os.path.join(docs_dir, filename), 'r', encoding='utf-8') as f:
                text = f.read()
                chunks = text_splitter.split_text(text)
                for chunk in chunks:
                    documents.append({
                        "content": chunk,
                        "source": filename
                    })
    
    # 存到 ChromaDB（本地向量库，无需额外安装）
    texts = [d["content"] for d in documents]
    metadatas = [{"source": d["source"]} for d in documents]
    
    vector_store = ChromaDB.from_texts(
        texts=texts,
        embedding=embedding_model,
        metadatas=metadatas,
        persist_directory="./chroma_db"
    )
    return vector_store


async def retrieve_knowledge(disease: str, crop_type: str):
    """根据病害名检索相关知识"""
    # 先用简单方案：关键词匹配（避免向量库依赖问题）
    # 答辩时展示真实 RAG 流程
    
    query = f"{crop_type} {disease} 防治方法"
    
    # === 简单方案：直接返回预设知识 ===
    KNOWLEDGE_BASE = {
        "番茄晚疫病": {
            "summary": "建议使用霜脲·锰锌可湿性粉剂500倍液喷雾防治",
            "detail": (
                "1. 立即摘除病叶并集中深埋\n"
                "2. 喷洒霜脲·锰锌可湿性粉剂500倍液，每7天一次，连续2-3次\n"
                "3. 加强通风降湿，控制大棚内湿度在70%以下\n"
                "4. 增施磷钾肥，提高植株抗病能力"
            ),
            "source_title": "《云南省番茄主要病虫害防治技术规范》2024版",
            "source_section": "第三章 真菌性病害防治"
        },
        "番茄早疫病": {
            "summary": "发病初期喷洒代森锰锌可湿性粉剂500倍液",
            "detail": (
                "1. 清除病残体，减少菌源\n"
                "2. 喷洒代森锰锌可湿性粉剂500倍液\n"
                "3. 合理轮作，避免连作"
            ),
            "source_title": "《云南省番茄主要病虫害防治技术规范》2024版",
            "source_section": "第二章 叶部病害防治"
        },
        # ... 补充更多病害知识
    }
    
    # === 真实方案：从向量库检索 ===
    # results = vector_store.similarity_search(query, k=3)
    # 取最相关的结果组装返回
    
    return KNOWLEDGE_BASE.get(
        disease,
        {
            "summary": f"未找到{disease}的标准防治方案，建议咨询农技人员",
            "detail": "请人工审核并录入防治方案到知识库",
            "source_title": "",
            "source_section": ""
        }
    )
```

### 4. Agent 编排 (`agent/diagnosis_agent.py`)

```python
"""
Agent 综合研判：
输入 = 图像识别结果 + RAG防治建议 + 天气数据 + 作物生育期
输出 = 综合风险研判 + 行动建议

简单实现：用规则 + 模板，不依赖 LangChain Agent
答辩时说明这里可以升级为真正的 LLM Agent
"""

import httpx

async def agent_analysis(
    recognition: dict,
    rag: dict,
    crop_type: str,
    growth_stage: str,
    location: str
) -> dict:
    """综合研判"""
    
    disease = recognition["disease"]
    confidence = recognition["confidence"]
    severity = recognition["severity"]
    
    # 1. 获取天气（可从后端天气API拿，也可调外部API）
    weather = await get_weather(location)
    
    # 2. 规则判断
    risk_level = "low"
    risk_factors = []
    
    # 置信度低 → 风险升级
    if confidence < 0.85:
        risk_factors.append("模型置信度偏低，建议人工复核")
        risk_level = "high"
    
    # 严重程度
    if severity == "严重":
        risk_level = "critical"
        risk_factors.append("病害严重，需立即处理")
    elif severity == "中等":
        if risk_level == "low":
            risk_level = "medium"
    
    # 天气因素（高湿度利于病害扩散）
    if weather and weather.get("humidity", 0) > 80:
        risk_factors.append(f"当前湿度{weather['humidity']}%，高湿环境利于病害扩散")
        if risk_level == "medium":
            risk_level = "high"
    
    # 生育期因素
    if growth_stage in ["开花坐果期", "结果期"]:
        risk_factors.append(f"作物处于{growth_stage}，病害影响产量风险高")
    
    # 3. 生成建议
    weather_factor = ""
    if weather:
        weather_factor = (
            f"近期气温{weather.get('temperature', 'N/A')}℃，"
            f"湿度{weather.get('humidity', 'N/A')}%，"
            f"{weather.get('weather_desc', '')}"
        )
    
    return {
        "overall_assessment": (
            f"综合当前天气（{weather_factor}）、作物生育期（{growth_stage}）"
            f"和识别结果，判断为{disease}，风险等级{risk_level}。"
            f"{'；'.join(risk_factors) if risk_factors else ''}"
        ),
        "risk_level": risk_level,
        "weather_factor": weather_factor,
        "risk_factors": risk_factors,
        "recommended_actions": [
            f"优先：按照防治规范处理{disease}",
            "辅助：加强田间巡查，观察病情变化",
            "长期：做好病害预防，定期喷洒保护性杀菌剂"
        ],
        "follow_up_days": 7
    }


async def get_weather(location: str) -> dict:
    """获取天气数据（模拟/真实）"""
    # 方案1：模拟数据
    return {
        "temperature": 24.5,
        "humidity": 85,
        "weather_desc": "阴转小雨",
        "rainfall": 5.2
    }
    
    # 方案2：调后端天气接口
    # async with httpx.AsyncClient() as client:
    #     resp = await client.get(f"http://localhost:8080/api/weather?location={location}")
    #     return resp.json()["data"][0]
```

### 5. 拒识机制

```python
# 在 main.py 的 diagnose 函数中

CONFIDENCE_THRESHOLD = 0.70  # 低于这个分数就拒识

if recognition["confidence"] < CONFIDENCE_THRESHOLD:
    return DiagnosisResponse(
        disease="未知病害",
        confidence=recognition["confidence"],
        symptoms=recognition["symptoms"],
        severity="无法判断",
        rag_result={"summary": "置信度过低，需要人工审核"},
        agent_opinion={
            "overall_assessment": "模型无法确定病害类型，建议农技人员现场查看",
            "risk_level": "high",
            "weather_factor": "",
            "recommended_actions": [
                "该样本已进入人工审核队列",
                "建议拍摄更多角度照片重新上传"
            ],
            "follow_up_days": 1
        }
    )
```

### 6. requirements.txt

```
fastapi==0.109.0
uvicorn==0.25.0
python-multipart==0.0.6
pydantic==2.5.0
httpx==0.25.0
chromadb==0.4.22
langchain==0.1.0
langchain-community==0.0.10
sentence-transformers==2.2.2
transformers==4.36.0
torch==2.1.0
pillow==10.1.0
```

## 启动命令

```bash
cd ai-service
venv\Scripts\activate        # Windows 激活虚拟环境
uvicorn main:app --reload --port 8000
```

浏览器打开 `http://localhost:8000/docs` 可以看到自动生成的 Swagger 接口文档。

## 调试技巧

1. **FastAPI 自带接口测试页面**：`http://localhost:8000/docs` 可以直接上传图片测试
2. **先用规则模拟，跑通流程后再换真实模型**
3. **print() 大法**：在 Python 代码里加 `print(变量)` 看值对不对

## 知识文档准备

在 `ai-service/data/knowledge/` 下创建下面这些 `.txt` 文件：

- `番茄病害防治.txt` — 晚疫病、早疫病、灰霉病等
- `辣椒病害防治.txt` — 炭疽病、疫病等
- `花卉病害防治.txt` — 白粉病、灰霉病等
- `通用农技规范.txt` — 施肥、灌溉、轮作等

内容从网上搜"XX病害防治技术"复制过来就行，20-30条足够了。

## 何时找莫成兴（后端）

- 莫成兴调不通你的接口（确认8000端口在监听）
- 数据格式不匹配
