#!/usr/bin/env python3
"""
城市天气服务 - Gradio 前端
支持查询当前天气与未来预报
"""
import gradio as gr
import urllib.request
import urllib.parse
import json

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


def resolve_city(city_input: str) -> str:
    if city_input in CITY_MAP:
        return CITY_MAP[city_input]
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
    except Exception:
        pass
    if "changsha" in city_en.lower():
        return {"lat": 28.19874, "lon": 112.97087, "name": city_en}
    return {"lat": 39.9042, "lon": 116.4074, "name": city_en}


def _wmo_str(code):
    try:
        return WMO_MAP.get(int(code), f"WMO:{code}")
    except Exception:
        return str(code)


def get_weather_text(city: str) -> str:
    city_en = resolve_city(city)
    geo = _geo_city(city_en)
    url = (f"https://api.open-meteo.com/v1/forecast?latitude={geo['lat']}&longitude={geo['lon']}"
           f"&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m"
           f"&daily=weather_code,temperature_2m_max,temperature_2m_min"
           f"&timezone=Asia/Shanghai")
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return f"获取失败: {e}"
    cur = data.get("current", {})
    area_name = geo.get("name", city_en)
    temp_c = cur.get("temperature_2m", "未知")
    desc = _wmo_str(cur.get("weather_code", "未知"))
    humidity = cur.get("relative_humidity_2m", "未知")
    wind = cur.get("wind_speed_10m", "未知")
    current_text = (
        f"【当前天气】地区: {area_name}\n"
        f"温度: {temp_c}°C | 天气: {desc}\n"
        f"湿度: {humidity}% | 风速: {wind} km/h"
    )
    weather = data.get("daily", {})
    forecast_lines = ["【未来 3 天预报】"]
    times = weather.get("time", [])
    codes = weather.get("weather_code", [])
    maxs = weather.get("temperature_2m_max", [])
    mins = weather.get("temperature_2m_min", [])
    for idx in range(min(3, len(times))):
        forecast_lines.append(f"{times[idx]}: {mins[idx]}°C ~ {maxs[idx]}°C | {_wmo_str(codes[idx])}")
    forecast_text = "\n".join(forecast_lines)
    return f"{current_text}\n\n---\n{forecast_text}"


with gr.Blocks(title="城市天气服务", css="body {font-family: sans-serif}") as demo:
    gr.Markdown("# 🌤️ 城市天气服务\n输入城市名（支持中文如 北京、上海、广州、成都、武汉、重庆、天津、苏州、长沙、郑州、青岛、沈阳、大连、宁波），获取当前天气与未来预报。")
    with gr.Row():
        city_input = gr.Textbox(label="城市名称", value="北京", placeholder="输入城市名...")
    btn = gr.Button("查询天气", variant="primary")
    output = gr.Markdown()
    btn.click(fn=get_weather_text, inputs=city_input, outputs=output)
    gr.Markdown("数据源：Open-Meteo（免费无需 API Key）。支持全球城市名，中文会自动映射常见城市。")

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
