# Tools Use 功能快速开始

## 什么是 Tools Use？

Tools Use（工具使用）允许 LLM 调用外部工具来完成任务。例如：
- 需要搜索网络信息时，调用 web_search 工具
- 需要执行代码时，调用 code_runner 工具
- 需要抓取网页时，调用 web_crawl 工具

这就像给 LLM 配备了"工具箱"，让它能够完成更复杂的任务。

## 最简单的例子（5 分钟上手）

### 1. 设置环境变量

```bash
export ANTHROPIC_BASE_URL="https://api.moonshot.cn/v1"
export ANTHROPIC_AUTH_TOKEN="sk-your-api-key-here"
export ANTHROPIC_MODEL="kimi-k2-turbo-preview"
```

### 2. 创建一个 Python 文件 `test.py`

```python
import asyncio
from coding_agent.tools import AnthropicClient, ToolExecutor

async def main():
    # 初始化客户端和执行器
    client = AnthropicClient()
    executor = ToolExecutor()
    
    # 注册 code_runner 工具
    client.register_tool(
        name="code_runner",
        description="代码执行器，支持运行 python 和 javascript 代码",
        parameters={
            "type": "object",
            "properties": {
                "language": {
                    "type": "string",
                    "enum": ["python", "javascript"]
                },
                "code": {
                    "type": "string",
                    "description": "代码写在这里"
                }
            },
            "required": ["language", "code"]
        },
        function=executor.execute_code_runner,
    )
    
    # 发送请求
    messages = [{"role": "user", "content": "编程判断 3214567 是否是素数。"}]
    result = await client.generate_with_tools(messages=messages)
    
    # 打印结果
    print("LLM 回复:", result['content'])
    
    # 打印工具调用详情
    if result['tool_calls']:
        print("\n工具调用:")
        for call in result['tool_calls']:
            print(f"  - {call['name']}: {call['result']}")

asyncio.run(main())
```

### 3. 运行

```bash
python3 test.py
```

## 工作原理

```
你的请求: "编程判断 3214567 是否是素数"
    ↓
LLM 分析: "我需要写代码并执行它"
    ↓
LLM 调用工具: code_runner
    参数: {
        "language": "python",
        "code": "def is_prime(n): ..."
    }
    ↓
工具执行代码并返回结果
    ↓
LLM 基于结果生成回复: "3214567 不是素数"
```

## 内置的三个工具

### 1. Code Runner - 代码执行器

```python
client.register_tool(
    name="code_runner",
    description="代码执行器，支持运行 python 和 javascript 代码",
    parameters={
        "type": "object",
        "properties": {
            "language": {"type": "string", "enum": ["python", "javascript"]},
            "code": {"type": "string"}
        },
        "required": ["language", "code"]
    },
    function=executor.execute_code_runner,
)
```

**用途**: 执行 Python 或 JavaScript 代码
**示例请求**: "计算斐波那契数列的第 10 项"

### 2. Web Search - 网络搜索

```python
client.register_tool(
    name="web_search",
    description="搜索网络以查找相关信息",
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "max_results": {"type": "integer", "default": 5}
        },
        "required": ["query"]
    },
    function=executor.execute_web_search,
)
```

**用途**: 搜索网络信息
**示例请求**: "搜索 Python asyncio 的最佳实践"

### 3. Web Crawler - 网页抓取

```python
client.register_tool(
    name="web_crawl",
    description="抓取网页内容并提取文本",
    parameters={
        "type": "object",
        "properties": {
            "url": {"type": "string"},
            "extract_text": {"type": "boolean", "default": True}
        },
        "required": ["url"]
    },
    function=executor.execute_web_crawl,
)
```

**用途**: 抓取特定网页的内容
**示例请求**: "抓取 https://example.com 的内容"

## 注册所有工具的完整示例

```python
import asyncio
from coding_agent.tools import AnthropicClient, ToolExecutor

async def main():
    client = AnthropicClient()
    executor = ToolExecutor()
    
    # 注册所有三个工具
    client.register_tool(
        name="web_search",
        description="搜索网络以查找相关信息",
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "max_results": {"type": "integer", "default": 5}
            },
            "required": ["query"]
        },
        function=executor.execute_web_search,
    )
    
    client.register_tool(
        name="web_crawl",
        description="抓取网页内容并提取文本",
        parameters={
            "type": "object",
            "properties": {
                "url": {"type": "string"},
                "extract_text": {"type": "boolean", "default": True}
            },
            "required": ["url"]
        },
        function=executor.execute_web_crawl,
    )
    
    client.register_tool(
        name="code_runner",
        description="代码执行器，支持运行 python 和 javascript 代码",
        parameters={
            "type": "object",
            "properties": {
                "language": {"type": "string", "enum": ["python", "javascript"]},
                "code": {"type": "string"}
            },
            "required": ["language", "code"]
        },
        function=executor.execute_code_runner,
    )
    
    # 现在 LLM 可以使用所有三个工具
    messages = [{"role": "user", "content": "你的问题"}]
    result = await client.generate_with_tools(messages=messages)
    print(result['content'])

asyncio.run(main())
```

## 常见问题

### Q: 如何知道 LLM 调用了哪些工具？

A: 检查返回结果中的 `tool_calls` 字段：

```python
result = await client.generate_with_tools(messages=messages)
print(f"调用了 {len(result['tool_calls'])} 个工具")
for call in result['tool_calls']:
    print(f"工具: {call['name']}, 结果: {call['result']}")
```

### Q: 工具执行失败怎么办？

A: 工具执行失败时，错误信息会返回给 LLM，LLM 会尝试处理错误或告知用户。

### Q: 可以自定义工具吗？

A: 可以！创建一个函数，然后用 `register_tool` 注册：

```python
async def my_tool(param1: str) -> dict:
    # 你的逻辑
    return {"result": "..."}

client.register_tool(
    name="my_tool",
    description="我的自定义工具",
    parameters={...},
    function=my_tool,
)
```

### Q: 工具会自动调用吗？

A: 是的！LLM 会根据用户请求自动决定是否需要调用工具。你只需要注册工具，然后正常发送请求即可。

## 更多示例

查看项目中的示例文件：
- `examples/simple_tool_use.py` - 最简单的示例
- `examples/tool_use_example.py` - 完整功能示例

## 详细文档

- `docs/TOOL_USE.md` - 完整使用文档
- `docs/TOOLS_USE_IMPLEMENTATION.md` - 技术实现说明
- `TOOLS_USE_SUMMARY.md` - 功能总结

