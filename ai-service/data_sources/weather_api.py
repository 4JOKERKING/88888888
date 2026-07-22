"""
天气数据源

主数据源: Open-Meteo (https://open-meteo.com/)
  - 完全免费，无需注册，无需API Key
  - 全球天气数据，每小时更新
  - 免费额度: 10,000次/天（远超需求）

备选: 模拟数据（Open-Meteo 不可用时自动切换）
"""

import time
from datetime import datetime

# 缓存
_cache = {}
CACHE_TTL = 1800  # 30分钟

# Open-Meteo 免费API（无需Key）
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

# 云南主要城市经纬度
CITY_COORDS = {
    "昆明呈贡": (24.88, 102.80),
    "昆明": (25.04, 102.72),
    "曲靖": (25.49, 103.79),
    "玉溪": (24.35, 102.55),
    "大理": (25.59, 100.23),
    "红河": (23.37, 102.42),
    "昭通": (27.34, 103.72),
    "丽江": (26.86, 100.23),
    "普洱": (22.78, 100.97),
    "临沧": (23.88, 100.09),
    "楚雄": (25.05, 101.55),
    "文山": (23.37, 104.24),
    "西双版纳": (21.99, 100.80),
    "德宏": (24.43, 98.58),
    "保山": (25.12, 99.17),
}


async def get_weather(location: str, force_refresh: bool = False) -> dict:
    """获取天气数据，真实API优先，失败回退模拟"""
    cache_key = location.strip()

    # 查缓存
    if not force_refresh and cache_key in _cache:
        data, ts = _cache[cache_key]
        if time.time() - ts < CACHE_TTL:
            return data

    # 1. 尝试 Open-Meteo（免费，无需Key）
    coords = _find_coords(location)
    if coords:
        try:
            data = await _fetch_open_meteo(coords[0], coords[1], location)
            if data:
                _cache[cache_key] = (data, time.time())
                return data
        except Exception as e:
            print(f"[WEATHER] Open-Meteo 请求失败: {e}")

    # 2. 兜底模拟
    data = _simulate_weather(location)
    data["source"] = "simulated"
    _cache[cache_key] = (data, time.time())
    return data


async def _fetch_open_meteo(lat: float, lon: float, location: str) -> dict | None:
    """调用 Open-Meteo 免费API"""
    import httpx

    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,weather_code",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code",
        "timezone": "Asia/Shanghai",
        "forecast_days": 4,
    }

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(OPEN_METEO_URL, params=params)
        if resp.status_code != 200:
            return None

        data = resp.json()
        current = data.get("current", {})
        daily = data.get("daily", {})

        temp = current.get("temperature_2m", 20)
        humidity = current.get("relative_humidity_2m", 70)
        rain = current.get("precipitation", 0)
        wind = current.get("wind_speed_10m", 2)
        code = current.get("weather_code", 0)
        desc = _weather_code_to_desc(code)

        risk_note = _build_risk_note(humidity, rain, desc)

        # 未来三天预报
        forecast = []
        if daily:
            for i in range(min(3, len(daily.get("time", [])))):
                forecast.append({
                    "date": daily["time"][i],
                    "temp_max": daily["temperature_2m_max"][i] if daily.get("temperature_2m_max") else None,
                    "temp_min": daily["temperature_2m_min"][i] if daily.get("temperature_2m_min") else None,
                    "precip": daily["precipitation_sum"][i] if daily.get("precipitation_sum") else 0,
                    "weather": _weather_code_to_desc(daily["weather_code"][i]) if daily.get("weather_code") else "",
                })

        return {
            "location": location,
            "temperature": round(temp, 1),
            "humidity": humidity,
            "rainfall": round(rain, 1),
            "wind_speed": round(wind, 1),
            "weather_desc": desc,
            "risk_note": risk_note,
            "forecast": forecast,
            "source": "open-meteo",
        }


def _weather_code_to_desc(code: int) -> str:
    """WMO天气码 → 中文描述"""
    mapping = {
        0: "晴", 1: "晴", 2: "多云", 3: "阴",
        45: "雾", 48: "雾凇",
        51: "小毛毛雨", 53: "毛毛雨", 55: "大毛毛雨",
        61: "小雨", 63: "中雨", 65: "大雨",
        71: "小雪", 73: "中雪", 75: "大雪",
        80: "阵雨", 81: "中阵雨", 82: "大阵雨",
        95: "雷暴", 96: "雷暴伴冰雹", 99: "强雷暴伴冰雹",
    }
    return mapping.get(code, "阴")


def _find_coords(location: str) -> tuple | None:
    """从预存坐标查找城市"""
    for name, coords in CITY_COORDS.items():
        if name in location or location in name:
            return coords
    # 模糊匹配: 取location的前2字符在CITY_COORDS的key中查找
    for name, coords in CITY_COORDS.items():
        if len(location) >= 2 and location[:2] in name:
            return coords
    return None


def _build_risk_note(humidity: float, rain: float, desc: str) -> str:
    parts = []
    if humidity > 85:
        parts.append(f"湿度{humidity}%偏高(>85%)，利于真菌和卵菌病害扩散")
    elif humidity > 70:
        parts.append(f"湿度{humidity}%中等偏高")
    else:
        parts.append(f"湿度{humidity}%，干燥条件不利于多数病害")

    if rain > 10:
        parts.append(f"降雨量{rain}mm，雨后需防病害暴发")
    elif rain > 0:
        parts.append(f"有小量降雨")

    if any(w in desc for w in ["雨", "雷暴", "阵雨"]):
        parts.append("降水天气，建议雨前预防性施药")
    return "。".join(parts)


def _simulate_weather(location: str) -> dict:
    """模拟天气（API不可用时兜底）"""
    import random
    month = datetime.now().month

    if month in [6, 7, 8, 9]:
        temp = round(random.uniform(20, 28), 1)
        humidity = round(random.uniform(70, 92), 1)
        rain = round(random.uniform(0, 30), 1)
        desc = random.choice(["多云转阵雨", "阴有小雨", "小雨转阴", "阴", "阵雨转多云"])
    elif month in [3, 4, 5]:
        temp = round(random.uniform(16, 26), 1)
        humidity = round(random.uniform(45, 70), 1)
        rain = round(random.uniform(0, 10), 1)
        desc = random.choice(["晴", "多云", "晴间多云"])
    elif month in [10, 11]:
        temp = round(random.uniform(14, 22), 1)
        humidity = round(random.uniform(50, 75), 1)
        rain = round(random.uniform(0, 15), 1)
        desc = random.choice(["晴", "多云", "阴", "阵雨"])
    else:
        temp = round(random.uniform(5, 15), 1)
        humidity = round(random.uniform(40, 65), 1)
        rain = round(random.uniform(0, 5), 1)
        desc = random.choice(["晴", "多云", "晴间多云"])

    return {
        "location": location,
        "temperature": temp,
        "humidity": humidity,
        "rainfall": rain,
        "wind_speed": round(random.uniform(0.5, 4.0), 1),
        "weather_desc": desc,
        "risk_note": _build_risk_note(humidity, rain, desc),
        "forecast": [],
        "source": "simulated",
    }


def is_real_available() -> bool:
    """Open-Meteo 始终可用（无需Key）"""
    return True
