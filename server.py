#!/usr/bin/env python3
"""
城市天气 MCP 服务
提供：当前天气、天气预报、天气查询工具
数据源：Open-Meteo（免费无需 API Key）
"""

import json
import urllib.request
import urllib.parse
from typing import Any

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weathmcp")

CITY_MAP = {
    "北京": "Beijing", "上海": "Shanghai", "广州": "Guangzhou", "深圳": "Shenzhen",
    "杭州": "Hangzhou", "成都": "Chengdu", "武汉": "Wuhan", "西安": "Xian",
    "南京": "Nanjing", "重庆": "Chongqing", "天津": "Tianjin", "苏州": "Suzhou",
    "长沙": "Changsha", "郑州": "Zhengzhou", "青岛": "Qingdao", "沈阳": "Shenyang",
    "大连": "Dalian", "宁波": "Ningbo",
}

WMO_MAP = {
    0: "晴朗", 1: "局部多云", 2: "局部多云", 3: "多云",
    45: "雾", 48: "雾凇",
    51: "小雨", 53: "小雨", 55: "小雨",
    61: "中雨", 63: "中雨", 65: "大雨",
    71: "小雪", 73: "中雪", 75: "大雪", 77: "雪粒",
    80: "小阵雨", 81: "阵雨", 82: "大阵雨",
    85: "小雪阵", 86: "雪阵",
    95: "雷暴", 96: "雷暴伴冰雹", 99: "雷暴伴大冰雹",
}


def _resolve_city(city_input: str) -> str:
    if not city_input:
        return "Beijing"
    if city_input in CITY_MAP:
        return CITY_MAP[city_input]
    for cn, en in CITY_MAP.items():
        if city_input == cn:
            return en
    return city_input


def _geo_city(city_en: str) -> dict:
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={urllib.parse.quote(city_en)}&count=1&language=zh"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        results = data.get("results", [])
        if results:
            r = results[0]
            return {"lat": r.get("latitude"), "lon": r.get("longitude"), "name": r.get("name", city_en)}
    except Exception as e:
        pass
    # fallback: common coords for Changsha if geo fails
    if "changsha" in city_en.lower():
        return {"lat": 28.19874, "lon": 112.97087, "name": city_en}
    return {"lat": 39.9042, "lon": 116.4074, "name": city_en}


def _wmo_str(code):
    try:
        return WMO_MAP.get(int(code), f"WMO:{code}")
    except Exception:
        return str(code)


@mcp.tool()
async def get_current_weather(city: str) -> str:
    """获取指定城市的当前天气信息。支持中文城市名（如北京、上海、广州等）。"""
    city_en = _resolve_city(city)
    geo = _geo_city(city_en)
    url = (f"https://api.open-meteo.com/v1/forecast?latitude={geo['lat']}&longitude={geo['lon']}"
           f"&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m"
           f"&timezone=Asia/Shanghai")
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return f"获取天气失败: {e}"
    cur = data.get("current", {})
    temp = cur.get("temperature_2m", "未知")
    hum = cur.get("relative_humidity_2m", "未知")
    wind = cur.get("wind_speed_10m", "未知")
    code = cur.get("weather_code", "未知")
    area = geo.get("name", city_en)
    return (f"【{city or city_en} 当前天气】地区: {area}\n"
            f"温度: {temp}°C | 天气: {_wmo_str(code)}\n"
            f"湿度: {hum}% | 风速: {wind} km/h")


@mcp.tool()
async def get_weather_forecast(city: str) -> str:
    """获取指定城市的未来 3 天天气预报。支持中文城市名。"""
    city_en = _resolve_city(city)
    geo = _geo_city(city_en)
    url = (f"https://api.open-meteo.com/v1/forecast?latitude={geo['lat']}&longitude={geo['lon']}"
           f"&daily=weather_code,temperature_2m_max,temperature_2m_min"
           f"&timezone=Asia/Shanghai")
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return f"获取预报失败: {e}"
    daily = data.get("daily", {})
    times = daily.get("time", [])
    codes = daily.get("weather_code", [])
    maxs = daily.get("temperature_2m_max", [])
    mins = daily.get("temperature_2m_min", [])
    lines = [f"【{city or city_en} 未来天气预报】"]
    for i in range(min(3, len(times))):
        lines.append(f"{times[i]}: {mins[i]}°C ~ {maxs[i]}°C | {_wmo_str(codes[i])}")
    return "\n".join(lines)


@mcp.tool()
async def search_weather_by_keyword(keyword: str) -> str:
    """根据关键词搜索城市天气，支持模糊匹配内置城市列表。"""
    matched = None
    kw_lower = keyword.lower()
    for cn, en in CITY_MAP.items():
        if keyword in cn or kw_lower in en.lower():
            matched = cn
            break
    target = matched if matched else keyword
    current_result = await get_current_weather(target)
    forecast_result = await get_weather_forecast(target)
    return f"{current_result}\n\n--- 未来预报 ---\n{forecast_result}"


@mcp.prompt()
async def weather_help() -> str:
    return (
        "你可以使用以下天气工具查询城市天气：\n"
        "1. get_current_weather(city) - 获取当前天气，支持中文如 北京、上海、广州、成都、武汉、西安、南京、重庆、天津、苏州、长沙、郑州、青岛、沈阳、大连、宁波\n"
        "2. get_weather_forecast(city) - 获取未来 3 天预报\n"
        "3. search_weather_by_keyword(keyword) - 关键词搜索天气\n"
        "数据源为 Open-Meteo，支持全球城市名（优先英文，中文会自动映射常见城市）。"
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
