"""最简单的 tools use 示例。

这个示例展示了如何使用 code_runner 工具来判断一个数是否是素数。
这是 Kimi API 文档中的示例。
"""

import asyncio
from coding_agent.tools import AnthropicClient, ToolExecutor


async def main():
    """主函数。"""
    
    # 1. 初始化客户端和执行器
    client = AnthropicClient()
    executor = ToolExecutor()
    
    # 2. 注册 code_runner 工具
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
    
    # 3. 发送请求（这是 Kimi 文档中的示例）
    messages = [
        {
            "role": "user",
            "content": "编程判断 3214567 是否是素数。"
        }
    ]
    
    print("🤖 发送请求: 编程判断 3214567 是否是素数。\n")
    
    # 4. 调用 LLM（会自动使用工具）
    result = await client.generate_with_tools(
        messages=messages,
        max_tokens=4000,
    )
    
    # 5. 显示结果
    print("=" * 60)
    print("📝 LLM 回复:")
    print("=" * 60)
    print(result['content'])
    print()
    
    # 6. 显示工具调用详情
    if result['tool_calls']:
        print("=" * 60)
        print("🔧 工具调用详情:")
        print("=" * 60)
        for i, call in enumerate(result['tool_calls'], 1):
            print(f"\n调用 #{i}: {call['name']}")
            print(f"输入参数:")
            for key, value in call['input'].items():
                if key == 'code':
                    print(f"  {key}:")
                    for line in value.split('\n'):
                        print(f"    {line}")
                else:
                    print(f"  {key}: {value}")
            print(f"\n执行结果:")
            if isinstance(call['result'], dict):
                for key, value in call['result'].items():
                    print(f"  {key}: {value}")
            else:
                print(f"  {call['result']}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        print("\n请确保设置了以下环境变量:")
        print("  export ANTHROPIC_BASE_URL='https://api.moonshot.cn/v1'")
        print("  export ANTHROPIC_AUTH_TOKEN='your-api-key'")
        print("  export ANTHROPIC_MODEL='kimi-k2-turbo-preview'")

