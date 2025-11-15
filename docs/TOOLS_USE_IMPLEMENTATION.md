# Tools Use 功能实现说明

## 概述

本次更新为项目添加了完整的 LLM Tools Use（工具调用）功能，参考了 Kimi API 的 tools use 示例。

## 新增文件

### 核心实现

1. **`src/coding_agent/tools/tool_definitions.py`**
   - 定义了标准的工具定义格式
   - 包含 web_search, web_crawl, code_runner 三个工具的定义

2. **`src/coding_agent/tools/tool_executor.py`**
   - 实现了工具的实际执行逻辑
   - 支持异步执行
   - 包含错误处理

3. **`src/coding_agent/tools/llm_client.py`** (更新)
   - 添加了 `register_tool()` 方法用于注册工具
   - 添加了 `generate_with_tools()` 方法支持工具调用
   - 添加了 `_execute_tool()` 方法执行工具
   - 支持多轮工具调用循环

### 示例和测试

4. **`examples/tool_use_example.py`**
   - 完整的使用示例
   - 展示如何注册和使用所有工具

5. **`examples/simple_tool_use.py`**
   - 最简单的示例（Kimi 文档示例）
   - 只使用 code_runner 工具

6. **`test_tool_use.py`**
   - 完整的测试套件
   - 测试工具注册、执行、完整流程

### 文档

7. **`docs/TOOL_USE.md`**
   - 完整的使用文档
   - API 参考
   - 示例代码

## 核心功能

### 1. 工具注册

```python
client.register_tool(
    name="tool_name",
    description="工具描述",
    parameters={...},  # JSON Schema
    function=callable_function,
)
```

### 2. 工具调用

```python
result = await client.generate_with_tools(
    messages=[{"role": "user", "content": "..."}],
    max_tokens=4000,
)
```

### 3. 内置工具

- **web_search**: 网络搜索（基于 DDGS）
- **web_crawl**: 网页抓取（基于 httpx/requests + BeautifulSoup）
- **code_runner**: 代码执行（支持 Python 和 JavaScript）

## 工作流程

```
1. 用户发送请求
   ↓
2. LLM 分析是否需要工具
   ↓
3. 如果需要，调用相应工具
   ↓
4. 工具执行并返回结果
   ↓
5. LLM 基于工具结果生成回复
   ↓
6. 返回最终结果
```

## 使用示例

### 基础示例（Kimi 文档示例）

```python
import asyncio
from coding_agent.tools import AnthropicClient, ToolExecutor

async def main():
    client = AnthropicClient()
    executor = ToolExecutor()
    
    # 注册工具
    client.register_tool(
        name="code_runner",
        description="代码执行器，支持运行 python 和 javascript 代码",
        parameters={
            "type": "object",
            "properties": {
                "language": {"type": "string", "enum": ["python", "javascript"]},
                "code": {"type": "string", "description": "代码写在这里"}
            },
            "required": ["language", "code"]
        },
        function=executor.execute_code_runner,
    )
    
    # 使用工具
    messages = [{"role": "user", "content": "编程判断 3214567 是否是素数。"}]
    result = await client.generate_with_tools(messages=messages)
    
    print(result['content'])

asyncio.run(main())
```

## 测试

运行测试：

```bash
# 测试所有功能
python test_tool_use.py

# 运行简单示例
python examples/simple_tool_use.py

# 运行完整示例
python examples/tool_use_example.py
```

## 环境配置

需要设置以下环境变量：

```bash
export ANTHROPIC_BASE_URL="https://api.moonshot.cn/v1"
export ANTHROPIC_AUTH_TOKEN="your-api-key"
export ANTHROPIC_MODEL="kimi-k2-turbo-preview"
```

## 技术细节

### 工具定义格式

遵循 OpenAI/Anthropic 的标准格式：

```json
{
  "type": "function",
  "function": {
    "name": "tool_name",
    "description": "工具描述",
    "parameters": {
      "type": "object",
      "properties": {
        "param1": {"type": "string", "description": "参数描述"}
      },
      "required": ["param1"]
    }
  }
}
```

### 工具执行流程

1. LLM 返回 `stop_reason="tool_use"`
2. 从 response.content 中提取 tool_use 块
3. 调用 `_execute_tool()` 执行工具
4. 将结果格式化为 `tool_result`
5. 添加到对话历史继续调用 LLM
6. 重复直到 LLM 不再需要工具或达到最大迭代次数

## 扩展性

可以轻松添加自定义工具：

```python
async def my_tool(param: str) -> dict:
    # 你的工具逻辑
    return {"result": "..."}

client.register_tool(
    name="my_tool",
    description="我的工具",
    parameters={...},
    function=my_tool,
)
```

## 注意事项

1. Code runner 有 5 秒超时限制
2. Web crawler 限制返回文本为 5000 字符
3. 最大工具调用迭代次数默认为 5 次
4. 工具函数可以是同步或异步的

## 下一步

- [ ] 添加更多内置工具
- [ ] 支持流式输出
- [ ] 添加工具调用缓存
- [ ] 优化错误处理
- [ ] 添加工具调用日志

