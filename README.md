---
# Turing Agent

> A Turing-inspired self-growing agent in just 100 lines of code — its only built-in tool is creating tools, so theoretically it can do anything.

Inspired by the Turing Machine: one simple rule that gives rise to universal computation. Here, that rule is `create_tool` — the agent writes its own tools at runtime, persists them, and uses them immediately. No pre-defined tool list, no static capabilities.

## How It Works

```
User asks a question
  → Agent realizes it needs a tool
  → Agent calls create_tool(name, code, description, params_schema)
  → Tool is saved to disk and registered in memory
  → Agent calls the newly created tool in the same conversation
  → Repeat
```

The manual ReAct loop rebinds the full tool list on every iteration, so newly created tools are **immediately available** — no restart needed.

## Quick Start

```bash
pip install langchain-openai langgraph

# Set your API key
export OPENAI_API_KEY="sk-..."
# Or for DeepSeek (default)
export OPENAI_API_KEY="sk-..." 
export OPENAI_BASE_URL="https://api.deepseek.com"

python Turing-Agent.py "What's the weather in Shanghai?"
```

The agent will:
1. Realize it has no weather tool
2. Call `create_tool` to write one
3. Call the new weather tool
4. Return the result

Next time you run it, the weather tool is already loaded from `tools/`.

## Tool Specification

Every tool created by the agent follows this contract:

```python
TOOL_DESC = "Description of what the tool does"
TOOL_PARAMS = {
    "type": "object",
    "properties": {
        "param1": {"type": "string", "description": "Parameter description"}
    },
    "required": ["param1"]
}
def run(param1: str) -> str:
    return "result"
```

Three required elements: `TOOL_DESC`, `TOOL_PARAMS`, `def run`.

## Architecture

```
Turing-Agent.py          # 98 lines, the whole thing
tools/                   # Auto-created, persists generated tools
  ├── get_weather.py
  ├── calculate.py
  └── ...
```

| Component | Role |
|-----------|------|
| `create_tool` | The only built-in tool — writes code to disk and registers it |
| `_load_tool_code` | Executes tool code in sandboxed namespace |
| `load_existing_tools` | Loads persisted tools on startup |
| `run_streaming` | Manual ReAct loop with hot-reload |

## Configuration

Edit `get_llm()` to switch models:

```python
# OpenAI
def get_llm(model="gpt-4o", base_url="https://api.openai.com/v1"):

# DeepSeek (default)
def get_llm(model="deepseek-chat", base_url="https://api.deepseek.com"):

# Any OpenAI-compatible endpoint
def get_llm(model="your-model", base_url="https://your-endpoint/v1"):
```

## Theoretical Capabilities

Most agents come with pre-built features — a fixed set of tools, a hardcoded UI layer, a baked-in database. Their ceiling is whatever the developer shipped.

Turing Agent starts with nothing but `create_tool`, yet can theoretically grow:

- **Database layer** — create tools that persist data to SQLite, Redis, or any storage
- **UI layer** — create tools that generate and serve web interfaces
- **Skill system** — create tools that compose other tools into higher-order skills
- **MCP integration** — create tools that connect to any external service or protocol
- **Memory & knowledge** — create tools that manage long-term memory and retrieval
- **Any API wrapper** — create tools for any third-party service on the fly

In other words, it can theoretically reach parity with the most powerful agents out there — and surpass them. Because their capabilities are pre-assembled and capped at release time. Turing Agent's ceiling is unbounded: it grows whatever it needs, when it needs it.

The difference: **they ship features. Turing Agent grows them.**

## Why "Turing"?

Alan Turing proved that a machine with a minimal instruction set can compute anything computable. This agent applies the same principle: one tool (`create_tool`) that can bootstrap any other tool. The agent doesn't come with capabilities — it grows them.

## Sponsor

If this project helped you, consider buying me a coffee ☕

<div align="center">
  <img src="assets/wechat.png" width="180" alt="WeChat" />
  &nbsp;&nbsp;
  <img src="assets/alipay.png" width="180" alt="Alipay" />
</div>

## License

MIT

---

