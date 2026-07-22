"""
农业通报数据源

数据来源:
- 云南省农业农村厅 http://nync.yn.gov.cn/
- 中国农业科学院植物保护研究所 https://www.caas.cn/
- 全国农技中心病虫测报 https://www.natesc.org.cn/

当前使用预设模拟数据，预留爬虫接口。
"""

from datetime import datetime, timedelta
import random

# ============================================================
# 预设近期云南省农业病虫通报
# ============================================================

BULLETINS = [
    {
        "id": 1,
        "title": "云南省2026年7月农作物病虫发生趋势预报",
        "source": "云南省农业农村厅",
        "url": "https://nync.yn.gov.cn/",
        "date": "2026-07-01",
        "summary": (
            "据全省病虫监测点调查，预计7月份番茄晚疫病在昆明、曲靖、玉溪等主产区中等偏重发生，"
            "辣椒疫病在文山、红河中等发生，马铃薯晚疫病在昭通、丽江中等偏重发生。"
            "各地应加强监测，雨后及时喷药预防。"
        ),
        "relevant_crops": ["番茄", "辣椒", "马铃薯"],
        "relevant_diseases": ["番茄晚疫病", "辣椒疫病", "马铃薯晚疫病"],
        "risk_level": "high",
    },
    {
        "id": 2,
        "title": "关于加强夏季蔬菜病害绿色防控的通知",
        "source": "云南省农业农村厅",
        "url": "https://nync.yn.gov.cn/",
        "date": "2026-06-15",
        "summary": (
            "当前我省进入高温多雨季节，蔬菜病害进入高发期。要求各地："
            "一是加强田间巡查监测，做到早发现早防治；"
            "二是推广生物农药和物理防治，减少化学农药用量；"
            "三是做好排水降湿，高垄栽培，降低病害发生风险。"
        ),
        "relevant_crops": ["番茄", "辣椒"],
        "relevant_diseases": [],
        "risk_level": "medium",
    },
    {
        "id": 3,
        "title": "2026年云南省马铃薯晚疫病防控技术指导意见",
        "source": "云南省农业科学院",
        "url": "https://www.yaas.org.cn/",
        "date": "2026-05-20",
        "summary": (
            "选用抗病品种（合作88、云薯505等），种薯消毒处理，"
            "高垄地膜覆盖栽培。出苗后每7-10天喷施保护性杀菌剂。"
            "发现中心病株立即拔除，全田喷洒烯酰吗啉1500倍液。"
            "昭通、曲靖、丽江产区需重点防范。"
        ),
        "relevant_crops": ["马铃薯"],
        "relevant_diseases": ["马铃薯晚疫病"],
        "risk_level": "high",
    },
    {
        "id": 4,
        "title": "2026年云南花卉病害春季防控要点",
        "source": "云南省花卉技术推广中心",
        "url": "https://nync.yn.gov.cn/",
        "date": "2026-03-10",
        "summary": (
            "春季气温回升，花卉白粉病、灰霉病进入发生期。"
            "大棚花卉应注意通风降湿，晴天中午强通风1-2小时。"
            "白粉病发生初期用三唑酮1000倍液防治，"
            "灰霉病用嘧霉胺1000倍液防治。及时清除衰败花瓣是关键。"
        ),
        "relevant_crops": ["花卉"],
        "relevant_diseases": ["白粉病", "灰霉病"],
        "risk_level": "medium",
    },
    {
        "id": 5,
        "title": "云南茶区茶饼病发生趋势及防控建议",
        "source": "云南省农业科学院茶叶研究所",
        "url": "https://www.yaas.org.cn/",
        "date": "2026-06-01",
        "summary": (
            "6-8月为茶饼病高发期，尤其是高山多雾茶园。"
            "建议：一是合理修剪保持茶蓬通风透光；"
            "二是增施磷钾肥提高茶树抗病力；"
            "三是发病初期喷洒多菌灵600倍液+百菌清600倍液，每10天一次。"
            "普洱、临沧、西双版纳茶区需重点监测。"
        ),
        "relevant_crops": ["茶叶"],
        "relevant_diseases": ["茶饼病"],
        "risk_level": "medium",
    },
]


def search_bulletins(crop_type: str = "", disease: str = "") -> list[dict]:
    """
    搜索相关农业通报。

    Args:
        crop_type: 作物类型（可选）
        disease: 病害名称（可选）

    Returns:
        匹配的通报列表，按相关度排序
    """
    results = []

    for b in BULLETINS:
        score = 0

        if crop_type and crop_type in b["relevant_crops"]:
            score += 2
        if disease and disease in b["relevant_diseases"]:
            score += 3
        if disease:
            # 提取核心关键词（去作物前缀和"病"后缀）
            keyword = disease.replace(crop_type, "").replace("病", "")
            if keyword and len(keyword) >= 2 and keyword in b["summary"]:
                score += 2

        if score > 0:
            results.append({**b, "relevance_score": score})

    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    return results[:3]


def get_latest_bulletin_summary(crop_type: str = "", disease: str = "") -> str:
    """
    获取最相关通报的摘要文本，供 Agent 研判时引用。
    无匹配时返回空字符串。
    """
    bulletins = search_bulletins(crop_type, disease)
    if not bulletins:
        return ""

    top = bulletins[0]
    return (
        f"【农业通报】{top['title']}（{top['source']} {top['date']}）："
        f"{top['summary'][:200]}"
    )
