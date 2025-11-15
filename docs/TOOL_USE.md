# LLM Tools Use 功能文档

## 概述

本项目已集成 LLM Tools Use（工具使用）功能，允许 LLM 调用外部工具来完成任务。这类似于 Kimi、Claude 等模型的 function calling 能力。

## 架构说明

```
┌─────────────────┐
│   用户请求      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ AnthropicClient │ ◄─── 注册工具
│  (LLM Client)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  generate_with  │ ◄─── 发送消息 + 工具定义
│     _tools()    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LLM 决定是否   │
│   调用工具      │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
需要工具    直接回复
    │         │
    ▼         │
┌─────────────────┐
│ ToolExecutor    │
│  执行工具       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  返回结果给LLM  │
│  继续对话       │
└─────────────────┘
```

## 功能特性

- ✅ 支持注册自定义工具
- ✅ 内置 Web Search 工具
- ✅ 内置 Web Crawler 工具
- ✅ 内置 Code Runner 工具（Python/JavaScript）
- ✅ 自动处理工具调用循环
- ✅ 支持多轮工具调用

## 快速开始

### 1. 基本使用

```python
import asyncio
from coding_agent.tools import AnthropicClient, ToolExecutor

async def main():
    # 初始化客户端
    client = AnthropicClient()
    executor = ToolExecutor()
    
    # 注册工具
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
                    "description": "要执行的代码"
                }
            },
            "required": ["language", "code"]
        },
        function=executor.execute_code_runner,
    )
    
    # 使用工具
    messages = [{"role": "user", "content": "编程判断 3214567 是否是素数"}]
    result = await client.generate_with_tools(messages=messages)
    
    print(result['content'])  # LLM 的最终回复
    print(result['tool_calls'])  # 调用的工具列表

asyncio.run(main())
```

### 2. 环境变量配置

```bash
export ANTHROPIC_BASE_URL="https://api.moonshot.cn/v1"
export ANTHROPIC_AUTH_TOKEN="your-api-key"
export ANTHROPIC_MODEL="kimi-k2-turbo-preview"
```

## 内置工具

### Web Search

搜索网络以查找相关信息。

```python
client.register_tool(
    name="web_search",
    description="搜索网络以查找相关信息",
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "搜索查询"},
            "max_results": {"type": "integer", "default": 5}
        },
        "required": ["query"]
    },
    function=executor.execute_web_search,
)
```

### Web Crawler

抓取网页内容并提取文本。

```python
client.register_tool(
    name="web_crawl",
    description="抓取网页内容并提取文本",
    parameters={
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "网页URL"},
            "extract_text": {"type": "boolean", "default": True}
        },
        "required": ["url"]
    },
    function=executor.execute_web_crawl,
)
```

### Code Runner

执行 Python 或 JavaScript 代码。

```python
client.register_tool(
    name="code_runner",
    description="代码执行器，支持运行 python 和 javascript 代码",
    parameters={
        "type": "object",
        "properties": {
            "language": {"type": "string", "enum": ["python", "javascript"]},
            "code": {"type": "string", "description": "要执行的代码"}
        },
        "required": ["language", "code"]
    },
    function=executor.execute_code_runner,
)
```

## 自定义工具

你可以注册自己的工具：

```python
async def my_custom_tool(param1: str, param2: int) -> dict:
    """自定义工具函数。"""
    return {"result": f"处理了 {param1} 和 {param2}"}

client.register_tool(
    name="my_tool",
    description="我的自定义工具",
    parameters={
        "type": "object",
        "properties": {
            "param1": {"type": "string"},
            "param2": {"type": "integer"}
        },
        "required": ["param1", "param2"]
    },
    function=my_custom_tool,
)
```

## 示例

查看 `examples/tool_use_example.py` 获取完整示例。

运行测试：
```bash
python test_tool_use.py
```

## API 参考

### AnthropicClient.register_tool()

注册一个工具供 LLM 使用。

**参数：**
- `name` (str): 工具名称
- `description` (str): 工具描述
- `parameters` (dict): JSON Schema 格式的参数定义
- `function` (Callable): 工具执行函数

### AnthropicClient.generate_with_tools()

使用工具生成回复。

**参数：**
- `messages` (List[Dict]): 对话消息列表
- `tools` (Optional[List[Dict]]): 工具定义（默认使用已注册的工具）
- `max_tokens` (int): 最大生成 token 数
- `model` (Optional[str]): 模型名称
- `max_iterations` (int): 最大工具调用迭代次数

**返回：**
```python
{
    "content": "最终回复文本",
    "tool_calls": [
        {
            "name": "工具名称",
            "input": {"参数": "值"},
            "result": "执行结果"
        }
    ],
    "stop_reason": "end_turn"
}
```

