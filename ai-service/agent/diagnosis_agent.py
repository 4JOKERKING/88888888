"""
Agent 综合研判模块 — 双模支持

模式1: DeepSeek LLM 推理（真实，需API Key）
模式2: 规则引擎（兜底，离线可用）

配置: 设置环境变量 DEEPSEEK_API_KEY 或在下方硬编码
注册: https://platform.deepseek.com/ → API Keys
"""

import os
import json

# DeepSeek API 配置（OpenAI 兼容）
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")  # 启动前: set DEEPSEEK_API_KEY=sk-xxx
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"

# 规则引擎依赖
from models.disease_db import CONFIDENCE_THRESHOLD

GROWTH_STAGE_RISK = {
    "苗期": {"weight": "medium", "note": "苗期感染病害对后期产量影响极大"},
    "开花坐果期": {"weight": "high", "note": "正值产量形成关键期，病害对花器和幼果的损害直接影响最终产量"},
    "结果期": {"weight": "high", "note": "果实膨大和成熟阶段，病害可导致大量落果和果实品质下降"},
    "成熟期": {"weight": "medium", "note": "接近采收，需权衡药剂防治与农药安全间隔期"},
    "休眠期": {"weight": "low", "note": "植株代谢缓慢，病害发展速度慢"},
}

CATEGORY_WEATHER_NOTE = {
    "真菌": "当前湿热天气利于真菌孢子萌发和菌丝扩展",
    "细菌": "风雨和灌溉水飞溅会加速细菌病害传播",
    "卵菌": "土壤含水量高和空气湿度大是卵菌病害暴发的关键条件",
    "病毒": "高温干旱有利于传毒昆虫种群增长，间接加剧病毒病",
}


async def agent_analysis(recognition: dict, rag: dict, crop_type: str,
                         growth_stage: str, location: str,
                         weather_data: dict | None = None) -> dict:
    """
    Agent 研判入口 — 优先用 DeepSeek LLM，失败回退规则引擎
    """
    disease = recognition["disease"]

    if disease == "健康":
        return _healthy_response(crop_type, location, weather_data)

    # 尝试 LLM 推理
    if DEEPSEEK_API_KEY:
        try:
            return await _llm_analysis(
                recognition, rag, crop_type, growth_stage, location, weather_data
            )
        except Exception as e:
            print(f"[AGENT] LLM推理失败({e})，回退规则引擎")

    # 规则引擎兜底
    return _rule_based_analysis(
        recognition, rag, crop_type, growth_stage, location, weather_data
    )


async def _llm_analysis(recognition: dict, rag: dict, crop_type: str,
                        growth_stage: str, location: str,
                        weather_data: dict | None) -> dict:
    """调用 DeepSeek LLM 做综合研判"""
    from openai import AsyncOpenAI

    client = AsyncOpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url=DEEPSEEK_BASE_URL,
    )

    # 构建天气描述
    weather_desc = "天气数据暂无"
    if weather_data:
        weather_desc = (
            f"当前{weather_data['location']}气温{weather_data['temperature']}℃，"
            f"湿度{weather_data['humidity']}%，天气{weather_data['weather_desc']}，"
            f"降雨量{weather_data['rainfall']}mm"
        )
        if weather_data.get("forecast"):
            fcs = weather_data["forecast"][:3]
            parts = [f"{f['date']}: {f['weather']}" for f in fcs]
            weather_desc += "，未来三天：" + "；".join(parts)

    prompt = f"""你是云南省农业技术推广站的植保专家。根据以下信息，为农户提供病害诊断和防治建议。

【基本信息】
作物：{crop_type}
生育期：{growth_stage}
地块位置：{location}

【AI识别结果】
病害：{recognition['disease']}
类别：{recognition.get('category', '未知')}
置信度：{recognition['confidence']:.1%}
严重程度：{recognition['severity']}

【当前天气】
{weather_desc}

【农技知识库检索结果】
{rag.get('detail', rag.get('summary', ''))}
来源：{rag.get('source_title', '未知文献')}

请以JSON格式输出（严格JSON，不要markdown代码块）：

{{
  "overall_assessment": "200字以内的综合评估，结合天气和生育期分析风险",
  "risk_level": "low/medium/high/critical",
  "risk_factors": ["具体风险因素1", "具体风险因素2"],
  "recommended_actions": ["具体操作步骤1", "具体操作步骤2", ...],
  "follow_up_days": 7
}}

要求：
1. overall_assessment要具体，提到天气数据和生育期的实际影响
2. risk_level根据严重程度+天气+生育期综合判断
3. recommended_actions至少4条，按优先级排列
4. follow_up_days根据严重程度：严重=3，中等=5，轻度=7"""

    response = await client.chat.completions.create(
        model=DEEPSEEK_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=800,
    )

    content = response.choices[0].message.content.strip()

    # 清理可能的 markdown 代码块
    if content.startswith("```"):
        content = content.split("\n", 1)[1]
        if content.endswith("```"):
            content = content[:-3]

    result = json.loads(content)

    # 补充天气因素文案
    if weather_data:
        result["weather_factor"] = (
            f"气温{weather_data['temperature']}℃，湿度{weather_data['humidity']}%，"
            f"{weather_data['weather_desc']}"
        )
    else:
        result["weather_factor"] = "天气数据暂无"

    return result


def _rule_based_analysis(recognition: dict, rag: dict, crop_type: str,
                         growth_stage: str, location: str,
                         weather_data: dict | None) -> dict:
    """规则引擎（Agent不可用时的兜底方案）"""
    disease = recognition["disease"]
    confidence = recognition["confidence"]
    severity = recognition["severity"]
    category = recognition.get("category", "")

    risk_level, risk_factors = _evaluate_risk(
        disease, confidence, severity, category, growth_stage, location, weather_data
    )

    weather_factor = _build_weather_factor(category, weather_data)

    overall = (
        f"经AI诊断，{crop_type}（{growth_stage}）感染了{disease}（{category}类病害），"
        f"严重程度评定为「{severity}」，模型置信度{confidence:.0%}。"
        f"综合风险等级：{_risk_label(risk_level)}。"
        f"{'；'.join(risk_factors)}"
    )

    actions = _generate_actions(disease, severity, rag)

    follow_up = {"严重": 3, "中等": 5, "轻度": 7}.get(severity, 7)

    return {
        "overall_assessment": overall,
        "risk_level": risk_level,
        "weather_factor": weather_factor,
        "risk_factors": risk_factors,
        "recommended_actions": actions,
        "follow_up_days": follow_up,
    }


def _healthy_response(crop_type: str, location: str,
                      weather_data: dict | None = None) -> dict:
    weather_note = ""
    if weather_data:
        weather_note = (
            f"当前{location}气温{weather_data['temperature']}℃，"
            f"湿度{weather_data['humidity']}%，{weather_data['weather_desc']}。"
        )
    return {
        "overall_assessment": f"{crop_type}植株未见明显病害症状，生长状态良好。{weather_note}建议继续保持日常田间管理和定期巡查。",
        "risk_level": "low",
        "weather_factor": weather_note or "天气数据暂无",
        "risk_factors": [],
        "recommended_actions": [
            "【常规】继续定期田间巡查（建议每周2次），关注天气变化",
            "【常规】按时完成常规农事任务（施肥、灌溉、整枝、除草）",
            "【预防】雨季前喷施一次保护性杀菌剂预防",
            "【记录】拍照记录当前健康状态作为对照基线",
            "【提醒】发现任何异常及时拍照上传诊断",
        ],
        "follow_up_days": 14,
    }


# ============================================================
# 规则引擎辅助函数
# ============================================================

def _evaluate_risk(disease, confidence, severity, category, growth_stage, location, weather):
    risk_level = "low"
    risk_factors = []

    if confidence < CONFIDENCE_THRESHOLD:
        risk_level = "high"
        risk_factors.append(f"模型置信度仅{confidence:.0%}（阈值{CONFIDENCE_THRESHOLD:.0%}），建议人工复核")

    sev_map = {"严重": "critical", "中等": "high", "轻度": "medium", "无": "low"}
    sev_risk = sev_map.get(severity, "low")
    rank = ["low", "medium", "high", "critical"]
    if rank.index(sev_risk) > rank.index(risk_level):
        risk_level = sev_risk

    if severity == "严重":
        risk_factors.append(f"{disease}已达严重程度，需在24小时内紧急处理")
    elif severity == "中等":
        risk_factors.append(f"{disease}处于中等发展期，建议3天内采取措施")

    stage_info = GROWTH_STAGE_RISK.get(growth_stage)
    if stage_info:
        if stage_info["weight"] == "high":
            if rank.index("high") > rank.index(risk_level):
                risk_level = "high"
            risk_factors.append(stage_info["note"])

    if weather_data:
        humidity = weather_data.get("humidity", 70)
        rain = weather_data.get("rainfall", 0)
        if humidity > 85 and category in ["真菌", "卵菌", "细菌"]:
            risk_factors.append(f"{location}湿度{humidity}%偏高，{category}类病害扩散风险上升")
            if rank.index("high") > rank.index(risk_level):
                risk_level = "high"
        if rain > 10 and category in ["真菌", "卵菌"]:
            risk_factors.append(f"降雨{rain}mm，雨后需重点关注病害暴发")

    return risk_level, risk_factors


def _build_weather_factor(category, weather):
    if not weather:
        return CATEGORY_WEATHER_NOTE.get(category, "天气数据暂无")
    return (
        f"当前气温{weather['temperature']}℃，湿度{weather['humidity']}%，"
        f"天气{weather['weather_desc']}。"
        f"{'湿度偏高，利于病害发展。' if weather['humidity'] > 85 else ''}"
    )


def _generate_actions(disease, severity, rag):
    actions = []
    if severity == "严重":
        actions.append(f"【紧急·24h内】立即按防治方案处理{disease}：{rag['summary']}")
        actions.append("【紧急】立即通知农技人员到场确认并指导施药")
        actions.append("【紧急】隔离病区，限制人员和工具流动，防止扩散")
    elif severity == "中等":
        actions.append(f"【3日内】按防治方案处理{disease}：{rag['summary']}")
        actions.append("【辅助】通知农技人员确认诊断结果")
    else:
        actions.append(f"【观察】{rag['summary']}")

    if severity in ["严重", "中等"]:
        actions.append("【辅助】处理后3-5天追拍照片复查，评估防治效果")
        actions.append("【辅助】处理后观察是否有药害症状")
    else:
        actions.append("【辅助】一周后追拍图片复查")

    if rag.get("source_title"):
        actions.append(f"【参考】详见：{rag['source_title']} {rag.get('source_section', '')}")

    return actions


def _risk_label(level):
    return {"low": "低风险", "medium": "中风险", "high": "高风险", "critical": "极高风险"}.get(level, level)
