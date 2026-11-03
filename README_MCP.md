# 城市天气 MCP 服务 (Weather MCP)

基于 [Model Context Protocol](https://modelcontextprotocol.io/) 的城市天气查询 MCP 服务器。

## 功能特性

- **当前天气**：获取指定城市的当前温度、湿度、风速、天气状况等
- **未来预报**：获取指定城市未来 3 天天气预报
- **关键词搜索**：支持模糊匹配常见中文城市，查询天气
- 内置 18 个中国主要城市的支持（自动中英文映射）
- 数据源：`wttr.in`（免费、无需 API Key）

## 环境准备

```bash
pip install -r requirements.txt
```

依赖：
- `mcp>=1.0.0,<2.0.0` — Model Context Protocol SDK
- `requests>=2.31.0`

## 运行

### MCP 服务端（stdio 模式，供客户端使用）

```bash
python server.py
```

启动后监听 stdio，可通过任意 MCP 客户端连接调用工具：

```jsonc
// MCP Tool 列表
tools:
  - name: "get_current_weather"       // 获取当前天气（参数: city）
  - name: "get_weather_forecast"        // 获取未来 3 天预报（参数: city）
  - name: "search_weather_by_keyword"  // 关键词搜索天气（参数: keyword）
```

#### 示例对话 (SSE / SSE 消息)

请求：
```json
{"id": "get_current_weather", "type": "tool_call", "name": "get_current_weather", "arguments": {"city": "北京"}}
```

响应：
```json
{"content": [{"type": "text", "text": "【北京 当前天气】地区: Beijing\n温度: 12°C / 54°F\n天气状况: 部分多云\n湿度: 65%\n风速: 22 km/h"}], "isError": false}
```

调用 `get_weather_forecast("上海")` 可获取未来 3 天预报。
调用 `search_weather_by_keyword("成都")` 返回该城市当前的天气与未来预报。

### Web 前端（Gradio）

```bash
python app.py
```

浏览器访问 `http://localhost:7860`，输入城市名即可查看当前天气与 3 天预报。

## 支持的城市

中文城市名（自动映射为英文）：北京、上海、广州、深圳、杭州、成都、武汉、西安、南京、重庆、天津、苏州、长沙、郑州、青岛、沈阳、大连、宁波。

也可直接输入英文城市名（如 `London`、`Tokyo`），系统通过 wttr.in 直接查询全球城市。

## 项目结构

| 文件 | 说明 |
|------|------|
| `server.py` | MCP Server 主程序（stdio 模式），含 3 个工具 + 1 个 prompt |
| `app.py` | Gradio 前端页面，提供交互式 UI |
| `requirements.txt` | Python 依赖 |

## 技术架构

```
┌──────────────┐     stdio      ┌─────────────────┐
│  AI Client   │ ◄───────────► │  mcp server.py   │
│ (Claude/LLM) │   JSON-RPC    │  FastMCP         │
└──────────────┘                └────────┬──────────┘
                                         │ urllib.request
                                         ▼
                                  ┌─────────────┐
                                  │ wttr.in API │
                                  └─────────────┘
```

数据源免费无 Key；如需更高并发/缓存可替换为 OpenWeatherMap 或和风天气。
