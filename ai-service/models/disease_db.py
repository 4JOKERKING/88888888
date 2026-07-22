"""
病害数据库 — 覆盖云南6大特色作物，30+种常见病害
"""
import random

# ============================================================
# 病害库：作物 → 病害列表
# ============================================================

DISEASE_DB = {
    "番茄": [
        {"disease": "番茄晚疫病", "category": "卵菌", "symptoms": [
            "叶片出现水渍状暗绿色斑点", "湿度大时叶背出现白色霉层",
            "病斑扩展迅速，几天内可遍布全株", "茎秆出现黑褐色条斑"
        ], "severity": "中等"},
        {"disease": "番茄早疫病", "category": "真菌", "symptoms": [
            "叶片出现同心轮纹状褐色病斑", "病斑周围组织黄化",
            "茎秆和叶柄出现黑褐色椭圆形凹陷斑", "下部老叶先发病"
        ], "severity": "轻度"},
        {"disease": "番茄灰霉病", "category": "真菌", "symptoms": [
            "果实出现水渍状软腐", "病部密布灰色霉层",
            "花器变褐腐烂", "叶片出现V形大病斑"
        ], "severity": "严重"},
        {"disease": "番茄叶霉病", "category": "真菌", "symptoms": [
            "叶面出现黄绿色褪绿斑点", "叶背出现紫褐色绒状霉层",
            "下部叶片最先发病向上蔓延", "严重时叶片枯死脱落"
        ], "severity": "轻度"},
        {"disease": "番茄青枯病", "category": "细菌", "symptoms": [
            "整株急速萎蔫青枯", "茎秆维管束变褐",
            "横切茎秆可挤出白色菌脓", "根系变褐腐烂"
        ], "severity": "严重"},
        {"disease": "番茄溃疡病", "category": "细菌", "symptoms": [
            "叶片边缘坏死呈火烧状", "茎秆出现纵向裂缝和溃疡斑",
            "果实出现鸟眼状斑点", "维管束黄褐色"
        ], "severity": "严重"},
        {"disease": "番茄白粉病", "category": "真菌", "symptoms": [
            "叶片表面覆盖白色粉状物", "严重时叶片卷曲皱缩",
            "植株生长势减弱", "果实品质下降"
        ], "severity": "轻度"},
        {"disease": "健康", "category": "", "symptoms": [], "severity": "无"},
    ],
    "辣椒": [
        {"disease": "辣椒炭疽病", "category": "真菌", "symptoms": [
            "果实出现圆形凹陷黑褐色病斑", "病斑表面有明显同心轮纹",
            "潮湿时病斑上出现橘红色黏质物", "病果易脱落或腐烂"
        ], "severity": "中等"},
        {"disease": "辣椒疫病", "category": "卵菌", "symptoms": [
            "茎基部出现水渍状暗绿色缢缩", "整株急速萎蔫倒伏",
            "根部变褐腐烂", "潮湿时病部长出白色絮状霉层"
        ], "severity": "严重"},
        {"disease": "辣椒病毒病", "category": "病毒", "symptoms": [
            "叶片出现黄绿相间的花叶", "植株矮化生长停滞",
            "叶片变小呈蕨叶状", "果实畸形变小"
        ], "severity": "中等"},
        {"disease": "辣椒褐斑病", "category": "真菌", "symptoms": [
            "叶片出现圆形或不规则形褐色病斑", "病斑中央灰白色边缘褐色",
            "严重时叶片大量脱落", "茎秆也可受害"
        ], "severity": "轻度"},
        {"disease": "辣椒疮痂病", "category": "细菌", "symptoms": [
            "叶片出现水渍状小斑点后变褐", "病斑边缘隆起中央凹陷",
            "果实出现圆形隆起疮痂状病斑", "严重时叶片脱落植株枯死"
        ], "severity": "中等"},
        {"disease": "健康", "category": "", "symptoms": [], "severity": "无"},
    ],
    "花卉": [
        {"disease": "白粉病", "category": "真菌", "symptoms": [
            "叶片和嫩茎表面覆盖白色粉状物", "叶片卷曲皱缩",
            "花蕾畸形不能正常开放", "植株生长势减弱"
        ], "severity": "轻度"},
        {"disease": "灰霉病", "category": "真菌", "symptoms": [
            "花瓣出现水渍状腐烂斑点", "腐烂处长出浓密灰色霉层",
            "花梗软腐折断", "叶片也可受害腐烂"
        ], "severity": "中等"},
        {"disease": "根腐病", "category": "真菌", "symptoms": [
            "根系变褐腐烂失去吸收功能", "植株地上部萎蔫黄化",
            "生长停滞不发新根", "严重时整株枯死"
        ], "severity": "严重"},
        {"disease": "黑斑病", "category": "真菌", "symptoms": [
            "叶片出现圆形黑色病斑", "病斑扩大后叶片枯黄脱落",
            "由下部叶片向上蔓延", "严重时仅剩顶端少量叶片"
        ], "severity": "中等"},
        {"disease": "锈病", "category": "真菌", "symptoms": [
            "叶片出现黄色疱状突起（锈孢子堆）", "疱状突起破裂散出锈褐色粉末",
            "严重时叶片枯焦", "植株生长衰弱"
        ], "severity": "轻度"},
        {"disease": "健康", "category": "", "symptoms": [], "severity": "无"},
    ],
    "马铃薯": [
        {"disease": "马铃薯晚疫病", "category": "卵菌", "symptoms": [
            "叶片出现水渍状暗绿色斑点", "叶背出现白色霉轮",
            "茎秆出现褐色条斑", "块茎切面呈褐色坏死"
        ], "severity": "严重"},
        {"disease": "马铃薯早疫病", "category": "真菌", "symptoms": [
            "叶片出现同心轮纹状褐色病斑", "病斑周围黄化",
            "下部叶片先发病枯死", "块茎出现黑褐色凹陷腐烂"
        ], "severity": "中等"},
        {"disease": "马铃薯黑胫病", "category": "细菌", "symptoms": [
            "茎基部变黑腐烂有臭味", "植株矮化叶片黄化",
            "根系和匍匐茎腐烂", "块茎从脐部开始腐烂"
        ], "severity": "严重"},
        {"disease": "马铃薯病毒病", "category": "病毒", "symptoms": [
            "叶片出现花叶或斑驳", "植株矮化卷叶",
            "块茎变小产量下降", "种薯带毒可代代相传"
        ], "severity": "中等"},
        {"disease": "健康", "category": "", "symptoms": [], "severity": "无"},
    ],
    "葡萄": [
        {"disease": "葡萄霜霉病", "category": "卵菌", "symptoms": [
            "叶片正面出现淡黄色水渍状斑点", "叶背对应处长出白色霜状霉层",
            "嫩梢和幼果也可受害", "严重时叶片焦枯脱落"
        ], "severity": "中等"},
        {"disease": "葡萄黑痘病", "category": "真菌", "symptoms": [
            "叶片出现红褐色圆形小斑点", "病斑边缘深褐色中央灰白色凹陷",
            "嫩梢、叶柄、果梗均可受害", "果实出现鸟眼状病斑"
        ], "severity": "中等"},
        {"disease": "葡萄白粉病", "category": "真菌", "symptoms": [
            "叶片表面出现白色粉状霉层", "幼果表面覆盖白粉并停止生长",
            "严重时果粒开裂腐烂", "新梢生长受阻"
        ], "severity": "轻度"},
        {"disease": "葡萄灰霉病", "category": "真菌", "symptoms": [
            "成熟果实出现水渍状腐烂", "腐烂处长出灰色霉层",
            "花序受害后变褐腐烂脱落", "储藏期可继续发病"
        ], "severity": "严重"},
        {"disease": "健康", "category": "", "symptoms": [], "severity": "无"},
    ],
    "茶叶": [
        {"disease": "茶饼病", "category": "真菌", "symptoms": [
            "嫩叶出现圆形凹陷半透明病斑", "叶背病斑处隆起呈饼状",
            "病斑表面出现白色粉状物", "病叶卷曲畸形易脱落"
        ], "severity": "中等"},
        {"disease": "茶炭疽病", "category": "真菌", "symptoms": [
            "成叶边缘出现不规则形褐色病斑", "病斑上有明显同心轮纹",
            "病斑上散生黑色细小粒点", "病叶枯死脱落"
        ], "severity": "轻度"},
        {"disease": "茶云纹叶枯病", "category": "真菌", "symptoms": [
            "叶片出现云纹状灰白色和褐色相间病斑", "病斑边缘有褐色线纹",
            "严重时叶片枯死", "老叶和成叶易感病"
        ], "severity": "中度"},
        {"disease": "茶根腐病", "category": "真菌", "symptoms": [
            "根系变褐腐烂", "地上部叶片黄化脱落",
            "植株生长势衰弱", "严重时整株枯死"
        ], "severity": "严重"},
        {"disease": "健康", "category": "", "symptoms": [], "severity": "无"},
    ],
}

CONFIDENCE_THRESHOLD = 0.70  # 低于此值触发拒识


def recognize_disease(image_bytes: bytes, crop_type: str) -> dict:
    """
    图像识别（模拟版本）
    实际部署时替换为 real_model.py 中的真实模型推理。
    """
    diseases = DISEASE_DB.get(crop_type)
    if not diseases:
        diseases = DISEASE_DB.get("番茄")  # 默认用番茄

    result = random.choice(diseases)

    if result["disease"] == "健康":
        confidence = round(random.uniform(0.92, 0.98), 2)
    else:
        confidence = round(random.uniform(0.72, 0.94), 2)

    return {
        "disease": result["disease"],
        "category": result["category"],
        "confidence": confidence,
        "symptoms": result["symptoms"],
        "severity": result["severity"],
    }
