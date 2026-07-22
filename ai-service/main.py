"""
农业诊断 AI 服务 — FastAPI 入口
启动: uvicorn main:app --reload --port 8000
文档: http://localhost:8000/docs
"""
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="农业诊断AI服务", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


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


# ============================================================
# 接口
# ============================================================

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
    """
    接收图片和作物信息，返回诊断结果。
    流程: 图像识别 → RAG检索 → Agent综合研判
    """
    # 1. 读取图片
    image_bytes = await image.read()

    # 2. 图像识别
    recognition = recognize_disease(image_bytes, crop_type)

    # 3. RAG 检索
    rag = retrieve_knowledge(recognition["disease"], crop_type)

    # 4. Agent 综合研判
    agent = agent_analysis(recognition, rag, crop_type, growth_stage, field_location)

    return DiagnosisResponse(
        disease=recognition["disease"],
        confidence=recognition["confidence"],
        symptoms=recognition["symptoms"],
        severity=recognition["severity"],
        rag_result=rag,
        agent_opinion=agent,
    )


# ============================================================
# 图像识别（模拟版本 — 后续替换真实模型）
# ============================================================

import random

DISEASE_DB = {
    "番茄": [
        {"disease": "番茄晚疫病", "symptoms": ["叶片水渍状暗绿色斑点", "叶背白色霉层", "病斑扩展迅速"], "severity": "中等"},
        {"disease": "番茄早疫病", "symptoms": ["叶片同心轮纹状褐斑", "病斑周围黄化", "茎秆黑褐色凹陷"], "severity": "轻度"},
        {"disease": "番茄灰霉病", "symptoms": ["果实软腐", "灰色霉层密布", "花器腐烂"], "severity": "严重"},
        {"disease": "番茄叶霉病", "symptoms": ["叶面黄绿色斑点", "叶背紫褐色霉层", "下部叶片先发病"], "severity": "轻度"},
        {"disease": "番茄青枯病", "symptoms": ["整株萎蔫", "茎秆维管束褐变", "根系腐烂"], "severity": "严重"},
        {"disease": "健康", "symptoms": [], "severity": "无"},
    ],
    "辣椒": [
        {"disease": "辣椒炭疽病", "symptoms": ["果实凹陷黑褐色病斑", "同心轮纹明显", "病斑上小黑点"], "severity": "中等"},
        {"disease": "辣椒疫病", "symptoms": ["茎基部水渍状缢缩", "整株急速萎蔫", "根系变褐"], "severity": "严重"},
        {"disease": "辣椒病毒病", "symptoms": ["叶片花叶黄绿相间", "植株矮化", "果实畸形"], "severity": "中等"},
        {"disease": "健康", "symptoms": [], "severity": "无"},
    ],
    "花卉": [
        {"disease": "白粉病", "symptoms": ["叶片和嫩茎覆盖白色粉状物", "叶片卷曲皱缩", "花蕾畸形"], "severity": "轻度"},
        {"disease": "灰霉病", "symptoms": ["花瓣水渍状腐烂", "灰色霉层", "花梗软腐折断"], "severity": "中等"},
        {"disease": "根腐病", "symptoms": ["根系褐变腐烂", "植株生长停滞", "叶片发黄萎蔫"], "severity": "严重"},
        {"disease": "健康", "symptoms": [], "severity": "无"},
    ],
}

# 默认病害库（作物类型未知时使用）
DEFAULT_DISEASES = [
    {"disease": "未知病害A", "symptoms": ["叶片异常斑点", "生长不良"], "severity": "无法判断"},
]

CONFIDENCE_THRESHOLD = 0.70  # 低于此值触发拒识


def recognize_disease(image_bytes: bytes, crop_type: str) -> dict:
    """
    图像识别（模拟版）
    实际部署时替换为 HuggingFace/TensorFlow 模型推理。
    """
    diseases = DISEASE_DB.get(crop_type)
    if not diseases:
        diseases = DISEASE_DB.get("番茄")  # 默认用番茄

    result = random.choice(diseases)

    # 健康 → 高置信度；有病 → 随机模拟
    if result["disease"] == "健康":
        confidence = round(random.uniform(0.92, 0.98), 2)
    else:
        confidence = round(random.uniform(0.72, 0.94), 2)

    return {
        "disease": result["disease"],
        "confidence": confidence,
        "symptoms": result["symptoms"],
        "severity": result["severity"],
    }


# ============================================================
# RAG 检索（模拟版本 — 后续替换 ChromaDB + embedding）
# ============================================================

KNOWLEDGE_BASE = {
    "番茄晚疫病": {
        "summary": "霜脲·锰锌可湿性粉剂500倍液喷雾，配合通风降湿",
        "detail": (
            "1. 立即摘除病叶、病果并集中深埋，切勿随意丢弃\n"
            "2. 喷洒霜脲·锰锌可湿性粉剂500倍液，或烯酰·霜脲氰1500倍液\n"
            "3. 每7天喷洒一次，连续2-3次，注意轮换用药\n"
            "4. 加强大棚通风，控制棚内湿度在70%以下\n"
            "5. 增施磷钾肥和微量元素，提高植株抗病能力\n"
            "6. 合理密植，及时整枝打杈，改善通风透光条件"
        ),
        "source_title": "《云南省番茄主要病虫害防治技术规范》2024版",
        "source_section": "第三章 真菌性病害防治·第一节 晚疫病",
    },
    "番茄早疫病": {
        "summary": "代森锰锌可湿性粉剂500倍液喷雾，发病初期防治",
        "detail": (
            "1. 清除田间病残体，减少初侵染菌源\n"
            "2. 发病初期喷洒代森锰锌可湿性粉剂500倍液\n"
            "3. 或用苯醚甲环唑1500倍液，每7-10天一次\n"
            "4. 合理轮作，与非茄科作物轮作2-3年\n"
            "5. 施足基肥，增施磷钾肥，忌偏施氮肥\n"
            "6. 高垄栽培，地膜覆盖，降低田间湿度"
        ),
        "source_title": "《云南省番茄主要病虫害防治技术规范》2024版",
        "source_section": "第三章 真菌性病害防治·第二节 早疫病",
    },
    "番茄灰霉病": {
        "summary": "腐霉利烟剂熏棚 + 嘧霉胺喷雾，立即处理",
        "detail": (
            "1. ⚠️ 该病传播极快，必须立即处理，不得拖延\n"
            "2. 立即摘除所有感病果实和花器，装入密封袋带出棚外\n"
            "3. 使用腐霉利烟剂熏棚，密闭4-6小时后通风\n"
            "4. 喷洒嘧霉胺可湿性粉剂1000倍液\n"
            "5. 降低棚内湿度至60%以下，必要时加温排湿\n"
            "6. 停止浇水，待病情控制后再少量补水\n"
            "7. 发病严重时考虑提前采收未感病果实"
        ),
        "source_title": "《云南省番茄主要病虫害防治技术规范》2024版",
        "source_section": "第三章 真菌性病害防治·第三节 灰霉病",
    },
    "番茄叶霉病": {
        "summary": "氟硅唑乳油800倍液喷雾，加强通风透光",
        "detail": (
            "1. 摘除下部老叶、病叶，改善通风透光\n"
            "2. 喷洒氟硅唑乳油800倍液，或戊唑醇1500倍液\n"
            "3. 降低棚内湿度，晴天中午通风排湿\n"
            "4. 合理施肥，避免氮肥过量导致叶片徒长\n"
            "5. 选用抗病品种，如合作908、金棚1号等"
        ),
        "source_title": "《云南省番茄主要病虫害防治技术规范》2024版",
        "source_section": "第三章 真菌性病害防治·第四节 叶霉病",
    },
    "番茄青枯病": {
        "summary": "⚠️ 细菌性病害，药剂防治效果有限，以预防为主",
        "detail": (
            "1. 立即拔除病株，穴内撒石灰消毒，严禁补植\n"
            "2. 全田灌根：噻菌铜悬浮剂500倍液 + 中生菌素\n"
            "3. 周围健康植株灌根预防，每株200ml药液\n"
            "4. 停止大水漫灌，改为滴灌，防止病菌随水传播\n"
            "5. 下茬改种非茄科作物，或选用抗青枯病砧木嫁接\n"
            "6. 土壤偏酸时施用石灰调节pH至7.0以上"
        ),
        "source_title": "《云南省番茄主要病虫害防治技术规范》2024版",
        "source_section": "第四章 细菌性病害防治·第一节 青枯病",
    },
    "辣椒炭疽病": {
        "summary": "咪鲜胺1500倍液 + 苯醚甲环唑，轮换使用",
        "detail": (
            "1. 及时摘除病果并深埋，减少田间菌源\n"
            "2. 发病初期喷洒咪鲜胺1500倍液\n"
            "3. 或苯醚甲环唑水分散粒剂1500倍液\n"
            "4. 每7天一次，连续2-3次，雨后补喷\n"
            "5. 合理密植，保持行间通风\n"
            "6. 施足有机肥，增施钙肥提高果实抗性"
        ),
        "source_title": "《云南省辣椒病虫害绿色防控技术手册》2023版",
        "source_section": "第二章 真菌性病害",
    },
    "辣椒疫病": {
        "summary": "⚠️ 毁灭性病害！烯酰吗啉 + 霜脲·锰锌，高垄排水",
        "detail": (
            "1. ⚠️ 立即拔除并烧毁病株，病穴灌药消毒\n"
            "2. 全田喷洒烯酰吗啉水分散粒剂1500倍液\n"
            "3. 配合霜脲·锰锌可湿性粉剂500倍液灌根\n"
            "4. 立即停止浇水，开沟排水降低土壤湿度\n"
            "5. 在未发病区域铺设地膜阻隔病菌溅射\n"
            "6. 高垄栽培是预防疫病的最有效措施"
        ),
        "source_title": "《云南省辣椒病虫害绿色防控技术手册》2023版",
        "source_section": "第三章 卵菌病害",
    },
    "辣椒病毒病": {
        "summary": "以防控传毒昆虫（蚜虫/蓟马）为主，配合增施锌肥",
        "detail": (
            "1. 拔除严重病株（已无经济价值）\n"
            "2. 喷洒吡虫啉或啶虫脒防治蚜虫、蓟马等传毒媒介\n"
            "3. 叶面喷施0.1%硫酸锌 + 氨基寡糖素提高抗病性\n"
            "4. 加强肥水管理，促进植株恢复生长\n"
            "5. 田间操作时先管健株后管病株，避免接触传毒\n"
            "6. 苗期覆盖防虫网是最有效预防手段"
        ),
        "source_title": "《云南省辣椒病虫害绿色防控技术手册》2023版",
        "source_section": "第四章 病毒病",
    },
    "白粉病": {
        "summary": "三唑酮1000倍液或硫磺制剂，通风透光是关键",
        "detail": (
            "1. 剪除严重感病的枝叶并集中处理\n"
            "2. 喷洒三唑酮可湿性粉剂1000倍液\n"
            "3. 或使用硫磺悬浮剂300倍液（注意高温药害）\n"
            "4. 加强通风透光，避免偏施氮肥\n"
            "5. 合理修剪，降低种植密度\n"
            "6. 浇水时避免淋湿叶片，采用滴灌为佳"
        ),
        "source_title": "《云南花卉常见病害防治手册》2022版",
        "source_section": "第一章 白粉病类",
    },
    "灰霉病": {
        "summary": "嘧霉胺 + 异菌脲轮换使用，降湿通风",
        "detail": (
            "1. 摘除所有腐烂花朵和叶片，密封清出棚外\n"
            "2. 喷洒嘧霉胺可湿性粉剂1000倍液\n"
            "3. 或异菌脲可湿性粉剂750倍液，轮换用药\n"
            "4. 降低棚内湿度，提温降湿\n"
            "5. 避免在阴雨天或傍晚浇水\n"
            "6. 及时清除衰败花瓣是预防关键"
        ),
        "source_title": "《云南花卉常见病害防治手册》2022版",
        "source_section": "第二章 灰霉病类",
    },
    "根腐病": {
        "summary": "⚠️ 恶霉灵灌根 + 控水 + 换土，挽救难度大",
        "detail": (
            "1. 立即停止浇水，松土透气降低土壤湿度\n"
            "2. 恶霉灵可湿性粉剂1500倍液灌根，每株300ml\n"
            "3. 配合甲霜·噁霉灵1500倍液灌根，7天后再灌一次\n"
            "4. 严重病株挖除，穴内换新土后补栽\n"
            "5. 检查并改善排水系统，确保不积水\n"
            "6. 今后种植前用多菌灵对土壤进行消毒处理"
        ),
        "source_title": "《云南花卉常见病害防治手册》2022版",
        "source_section": "第三章 根部病害",
    },
}


def retrieve_knowledge(disease: str, crop_type: str) -> dict:
    """
    RAG 检索（模拟版）
    用关键词匹配预设知识库。实际部署替换为 ChromaDB/Milvus 向量检索。
    """
    result = KNOWLEDGE_BASE.get(disease)
    if result:
        return result

    # 未找到精确匹配 → 模糊匹配（查病害名中的关键词）
    for key, val in KNOWLEDGE_BASE.items():
        if any(word in disease for word in key):
            return val

    # 完全没匹配 → 返回兜底
    return {
        "summary": f"未找到「{disease}」的标准防治方案，建议咨询农技人员现场诊断",
        "detail": "该样本已标记为未知病害，请农技人员审核后补充知识库",
        "source_title": "",
        "source_section": "",
    }


# ============================================================
# Agent 综合研判
# ============================================================

def agent_analysis(
    recognition: dict,
    rag: dict,
    crop_type: str,
    growth_stage: str,
    location: str,
) -> dict:
    """
    Agent 编排：综合识别结果 + RAG + 生长阶段 进行风险研判。
    """
    disease = recognition["disease"]
    confidence = recognition["confidence"]
    severity = recognition["severity"]

    # --- 风险评估 ---
    risk_level = "low"
    risk_factors = []

    if disease == "健康":
        return {
            "overall_assessment": f"{crop_type}植株未见明显病害症状，生长状态良好。建议继续保持日常田间管理。",
            "risk_level": "low",
            "weather_factor": "",
            "risk_factors": [],
            "recommended_actions": [
                "继续定期巡查，关注天气变化",
                "按时完成常规农事任务（施肥/灌溉/整枝）",
                "发现异常及时拍照上传诊断",
            ],
            "follow_up_days": 14,
        }

    # 置信度低 → 拒识标记
    if confidence < CONFIDENCE_THRESHOLD:
        risk_level = "high"
        risk_factors.append(f"模型置信度仅{confidence:.0%}，低于阈值{CONFIDENCE_THRESHOLD:.0%}，建议人工复核")

    # 严重程度
    severity_levels = {"严重": "critical", "中等": "high", "轻度": "medium"}
    sev_risk = severity_levels.get(severity, "low")

    # 取较高风险
    risk_order = ["low", "medium", "high", "critical"]
    if risk_order.index(sev_risk) > risk_order.index(risk_level):
        risk_level = sev_risk

    if severity == "严重":
        risk_factors.append(f"{disease}已达严重程度，需立即处理防止扩散")
    elif severity == "中等":
        risk_factors.append(f"{disease}处于中等发展期，应在3天内处理")

    # 生育期因素
    if growth_stage in ["开花坐果期", "结果期"]:
        risk_factors.append(f"作物处于{growth_stage}，病害对产量影响较大，应优先处理")

    # --- 生成综合评估 ---
    overall = (
        f"经AI诊断，{crop_type}（{growth_stage}）感染了{disease}，"
        f"严重程度：{severity}，置信度：{confidence:.0%}。"
        f"{'；'.join(risk_factors)}"
    )

    # --- 行动建议 ---
    actions = []

    # 优先操作
    if severity == "严重":
        actions.append(f"【紧急】立即按防治方案处理{disease}：{rag['summary']}")
    elif severity == "中等":
        actions.append(f"【3日内】按防治方案处理{disease}：{rag['summary']}")
    else:
        actions.append(f"【观察】{rag['summary']}")

    # 通用辅助操作
    if severity in ["严重", "中等"]:
        actions.append("【辅助】通知农技人员到场确认")
        actions.append("【辅助】处理后3-5天追拍照片复查")
    else:
        actions.append("【辅助】加强田间巡查，一周后追拍复查")

    actions.append("【长期】将本次诊断记录归档，完善病害发生档案")
    actions.append(f"【参考】详见：{rag.get('source_title', '农技规范')}")

    follow_up = 3 if severity == "严重" else 5 if severity == "中等" else 7

    # 模拟天气因素
    weather_factor = "当前为夏季湿热天气，若近期有降雨将加速病害扩散"

    return {
        "overall_assessment": overall,
        "risk_level": risk_level,
        "weather_factor": weather_factor,
        "risk_factors": risk_factors,
        "recommended_actions": actions,
        "follow_up_days": follow_up,
    }
