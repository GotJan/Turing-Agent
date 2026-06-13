"""Turing Agent — create_tool: a self-growing agent with hot-reload (inspired by Turing Machine)"""

import os, json, getpass
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

TOOLS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools")
os.makedirs(TOOLS_DIR, exist_ok=True)
_dynamic_tools: dict = {}

def get_llm(model="deepseek-chat", base_url="https://api.deepseek.com"):
    api_key = os.getenv("OPENAI_API_KEY") or getpass.getpass("API Key: ")
    return ChatOpenAI(model=model, api_key=api_key, base_url=base_url, temperature=0)

def _load_tool_code(code: str, name: str):
    ns = {}
    exec(code, {"__builtins__": __builtins__}, ns)
    run_func = ns.get("run")
    if run_func and callable(run_func):
        run_func.__name__ = name
        run_func.__doc__ = ns.get("TOOL_DESC", "")
        return run_func
    return None

@tool
def create_tool(name: str, code: str, description: str, params_schema: dict = None) -> str:
    """Create and register a new tool. code must contain TOOL_DESC, TOOL_PARAMS, and def run function. Auto-persists and registers for immediate use in current session."""
    try:
        if "TOOL_DESC" not in code or "TOOL_PARAMS" not in code or "def run(" not in code:
            return "Error: code must contain TOOL_DESC, TOOL_PARAMS, def run"
        if not name.replace("_", "").isalnum():
            return "Error: name must be alphanumeric with underscores only"
        tool_path = os.path.join(TOOLS_DIR, f"{name}.py")
        with open(tool_path, "w", encoding="utf-8") as f:
            f.write(code)
        run_func = _load_tool_code(code, name)
        if not run_func:
            return f"Warning: code saved to {tool_path}, but no run function found"
        _dynamic_tools[name] = tool(run_func)
        return f"Tool '{name}' created!\n   Desc: {run_func.__doc__}\n   Saved: {tool_path}"
    except Exception as e:
        return f"Error: {type(e).__name__}: {e}"

def load_existing_tools():
    """Load persisted tools from tools/ directory on startup"""
    if not os.path.isdir(TOOLS_DIR):
        return
    for fname in os.listdir(TOOLS_DIR):
        if not fname.endswith(".py"):
            continue
        name = fname[:-3]
        try:
            code = open(os.path.join(TOOLS_DIR, fname), "r", encoding="utf-8").read()
            run_func = _load_tool_code(code, name)
            if run_func:
                _dynamic_tools[name] = tool(run_func)
        except Exception:
            pass

SYSTEM_PROMPT = "You are an agent that can use tools to solve user problems."

def _find_tool(name: str):
    return create_tool if name == "create_tool" else _dynamic_tools.get(name)

def run_streaming(query: str, max_loop: int = 20):
    """Manual ReAct loop — rebinds tools each iteration so newly created tools are immediately available"""
    load_existing_tools()
    llm = get_llm()
    messages = [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=query)]
    print(f"You: {query}\nAgent: ", end="", flush=True)

    for _ in range(max_loop):
        # Rebind all tools each iteration — hot-reload core
        all_tools = [create_tool] + list(_dynamic_tools.values())
        response = llm.bind_tools(all_tools).invoke(messages)
        messages.append(response)

        if not response.tool_calls:
            print(response.content)
            break

        for tc in response.tool_calls:
            t = _find_tool(tc["name"])
            result = str(t.invoke(tc["args"])) if t else f"Error: tool {tc['name']} not found"
            messages.append(ToolMessage(content=result, tool_call_id=tc["id"]))
            print(f"  [{tc['name']}] -> {result[:100]}\n  ", end="", flush=True)
    else:
        print("... (max iterations reached)")

    if _dynamic_tools:
        print(f"\nTool pool: {[create_tool.name] + list(_dynamic_tools.keys())}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        run_streaming(sys.argv[1])
    else:
        print('Usage: python Turing-Agent.py "your question"')
