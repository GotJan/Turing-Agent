---
AIGC:
    Label: "1"
    ContentProducer: 001191110102MACQD9K64018705
    ProduceID: 850336082563833_0/project_7650647351467639080-files/README.zh-CN.md
    ReservedCode1: ""
    ContentPropagator: 001191110102MACQD9K64028705
    PropagateID: 850336082563833#1781345005303
    ReservedCode2: ""
---
# Turing Agent

> 一个以图灵为灵感的自生长 Agent，仅 100 行代码——唯一的内置工具是创造工具，所以理论上能做任何事。

灵感源自图灵机：一条极简规则，却能产生通用计算。这里的规则就是 `create_tool`——Agent 在运行时自己编写工具、落盘持久化、立即调用。没有预定义工具列表，没有静态能力边界。

## 工作原理

```
用户提问
  → Agent 发现需要某个工具
  → Agent 调用 create_tool(name, code, description, params_schema)
  → 工具保存到磁盘并注册到内存
  → Agent 在同一轮对话中立即调用新工具
  → 循环往复
```

手动 ReAct 循环在每次迭代时重新绑定完整工具列表，新创建的工具**立即可用**——无需重启。

## 快速开始

```bash
pip install langchain-openai langgraph

# 设置 API Key
export OPENAI_API_KEY="sk-..."
# 或使用 DeepSeek（默认）
export OPENAI_API_KEY="sk-..."
export OPENAI_BASE_URL="https://api.deepseek.com"

python Turing-Agent.py "上海今天天气怎么样？"
```

Agent 会：
1. 发现自己没有天气查询工具
2. 调用 `create_tool` 写一个
3. 调用新创建的天气工具
4. 返回结果

下次运行时，天气工具已从 `tools/` 目录自动加载。

## 工具规范

Agent 创建的每个工具遵循以下契约：

```python
TOOL_DESC = "工具的功能描述"
TOOL_PARAMS = {
    "type": "object",
    "properties": {
        "param1": {"type": "string", "description": "参数说明"}
    },
    "required": ["param1"]
}
def run(param1: str) -> str:
    return "结果"
```

三个必要元素：`TOOL_DESC`、`TOOL_PARAMS`、`def run`。

## 架构

```
Turing-Agent.py          # 98 行，全部代码
tools/                   # 自动创建，持久化生成的工具
  ├── get_weather.py
  ├── calculate.py
  └── ...
```

| 组件 | 职责 |
|------|------|
| `create_tool` | 唯一内置工具——将代码写入磁盘并注册 |
| `_load_tool_code` | 在沙盒命名空间中执行工具代码 |
| `load_existing_tools` | 启动时加载已持久化的工具 |
| `run_streaming` | 支持热更新的手动 ReAct 循环 |

## 配置

修改 `get_llm()` 切换模型：

```python
# OpenAI
def get_llm(model="gpt-4o", base_url="https://api.openai.com/v1"):

# DeepSeek（默认）
def get_llm(model="deepseek-chat", base_url="https://api.deepseek.com"):

# 任何 OpenAI 兼容端点
def get_llm(model="your-model", base_url="https://your-endpoint/v1"):
```

## 理论能力

大多数 Agent 出厂就带着预制功能——固定的工具集、写死的 UI 层、内置的数据库。它们的上限就是开发者发布时的水平。

Turing Agent 只有一个 `create_tool`，却可以理论上长出：

- **数据库层** — 创建工具来持久化数据到 SQLite、Redis 或任何存储
- **UI 层** — 创建工具来生成和提供 Web 界面
- **Skill 系统** — 创建工具来将其他工具组合为高阶技能
- **MCP 集成** — 创建工具来连接任何外部服务或协议
- **记忆与知识** — 创建工具来管理长期记忆和检索
- **任意 API 封装** — 创建工具来即时对接任何第三方服务

换句话说，理论上它可以与当前最强的 Agent 达到一致能力——并且超越它们。因为它们的能力是预组装的，上线即封顶。Turing Agent 的上限无限：需要什么，就长什么。

区别在于：**它们发布功能，Turing Agent 生长功能。**

## 为什么叫 "Turing"？

艾伦·图灵证明了一台只有最小指令集的机器可以计算任何可计算的东西。这个 Agent 应用了同样的原理：一个工具（`create_tool`）能引导出所有其他工具。Agent 不是带着能力来的——它是长出来的。

## 请我喝咖啡 ☕

如果这个项目对你有帮助，请我喝杯咖啡吧~

<div align="center">
  <img src="assets/wechat.png" width="180" alt="微信" />
  &nbsp;&nbsp;
  <img src="assets/alipay.png" width="180" alt="支付宝" />
</div>

## 许可证

MIT

---

> 本内容由 Coze AI 生成，请遵循相关法律法规及《人工智能生成合成内容标识办法》使用与传播。
