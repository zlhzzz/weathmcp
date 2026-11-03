# 城市天气 MCP 服务 (Weather MCP)

基于 [Model Context Protocol](https://modelcontextprotocol.io/) 的城市天气查询 MCP 服务器。

## 功能特性

- **当前天气**：获取指定城市的当前温度、湿度、风速、天气状况等
- **未来预报**：获取指定城市未来 3 天天气预报
- **关键词搜索**：支持模糊匹配常见中文城市，查询天气
- 内置 18 个中国主要城市的支持（自动中英文映射）
- 数据源：`Open-Meteo`（免费、无需 API Key）

## 快速开始

```bash
pip install -r requirements.txt
python demo.py
```

## MCP 工具列表

- `get_current_weather(city)` — 当前天气
- `get_weather_forecast(city)` — 未来 3 天预报
- `search_weather_by_keyword(keyword)` — 关键词搜索

## Web 前端

```bash
python app.py
```

访问 `http://localhost:7860`。

## 项目结构

| 文件 | 说明 |
|------|------|
| `server.py` | MCP Server 主程序 |
| `demo.py` | 演示入口 |
| `app.py` | Gradio 前端 |
| `pyproject.toml` | 包配置 |
| `requirements.txt` | Python 依赖 |
