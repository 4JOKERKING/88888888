"""
市场价格数据源

数据来源:
- 全国农产品商务信息公共服务平台 http://pfsc.agri.cn/
- 农业农村部市场信息司
- 预留真实 API 接口位置，当前使用预设模拟数据

真实接入方式（后续升级）:
1. 农业农村部数据开放平台 → 申请API密钥
2. 各州/市农业局发布的每周价格监测报告 → 爬虫解析
"""

from datetime import datetime, timedelta
import random

# ============================================================
# 预设云南主要市场数据（覆盖30天，模拟真实价格波动）
# ============================================================

# 基准价格: (最低价, 最高价, 均价, 单位)
PRICE_BASE = {
    "番茄": (2.0, 6.0, 3.5, "元/公斤"),
    "辣椒": (3.0, 8.0, 5.0, "元/公斤"),
    "马铃薯": (1.5, 3.5, 2.2, "元/公斤"),
    "葡萄": (6.0, 18.0, 10.0, "元/公斤"),
    "茶叶": (40.0, 200.0, 80.0, "元/公斤"),
}

MARKETS = [
    "昆明王旗营蔬菜批发市场",
    "呈贡龙城农贸市场",
    "曲靖麒麟农产品批发市场",
    "大理古城农贸市场",
    "玉溪红塔农贸市场",
    "昭通珠泉农贸市场",
    "丽江古城区农贸市场",
]


def get_prices(crop_type: str, days: int = 30) -> list[dict]:
    """
    获取指定作物近N天的市场价格。

    返回:
    [
        {"date": "2026-07-22", "price": 3.8, "unit": "元/公斤", "market": "呈贡龙城"},
        ...
    ]
    """
    if crop_type not in PRICE_BASE:
        crop_type = "番茄"

    lo, hi, avg, unit = PRICE_BASE[crop_type]
    records = []

    for i in range(days):
        date = (datetime.now() - timedelta(days=days - 1 - i)).strftime("%Y-%m-%d")
        # 随机浮动 ±30%
        price = round(avg + random.uniform(-avg * 0.3, avg * 0.3), 1)

        # 保证在合理区间内
        price = max(lo * 0.8, min(hi * 1.2, price))

        records.append({
            "date": date,
            "price": price,
            "unit": unit,
            "market": random.choice(MARKETS),
        })

    return records


def get_price_summary(crop_type: str) -> dict:
    """价格摘要（诊断时展示用）"""
    prices = get_prices(crop_type, days=7)
    latest = prices[-1]["price"]
    week_avg = round(sum(p["price"] for p in prices) / len(prices), 1)
    trend = "上涨" if latest > week_avg else "下跌" if latest < week_avg else "持平"

    return {
        "crop_type": crop_type,
        "latest_price": latest,
        "unit": PRICE_BASE.get(crop_type, PRICE_BASE["番茄"])[3],
        "week_average": week_avg,
        "trend": trend,
        "data_source": "模拟数据",
    }
