"""示例：如何使用 LLM 的 tools use 功能。

这个示例展示了如何：
1. 初始化 AnthropicClient
2. 注册工具（web search, web crawler, code runner）
3. 使用工具进行对话
"""

import asyncio
import os
from coding_agent.tools import AnthropicClient, ToolExecutor


async def main():
    """主函数：演示 tools use 功能。"""
    
    # 1. 初始化 LLM 客户端
    print("🚀 初始化 Anthropic/Kimi 客户端...")
    try:
        client = AnthropicClient()
        print("✅ 客户端初始化成功\n")
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        print("\n请确保设置了以下环境变量:")
        print("  - ANTHROPIC_BASE_URL")
        print("  - ANTHROPIC_AUTH_TOKEN")
        print("  - ANTHROPIC_MODEL (可选)")
        return

    # 2. 初始化工具执行器
    print("🔧 初始化工具执行器...")
    executor = ToolExecutor()
    print("✅ 工具执行器初始化成功\n")

    # 3. 注册工具
    print("📝 注册工具...")
    
    # 注册 web search 工具
    client.register_tool(
        name="web_search",
        description="搜索网络以查找相关信息。可以用于查找代码示例、文档、最佳实践等。",
        parameters={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "搜索查询字符串"
                },
                "max_results": {
                    "type": "integer",
                    "description": "返回的最大结果数量",
                    "default": 5
                }
            },
            "required": ["query"]
        },
        function=executor.execute_web_search,
    )
    print("  ✅ 注册 web_search 工具")

    # 注册 web crawler 工具
    client.register_tool(
        name="web_crawl",
        description="抓取网页内容并提取文本。用于获取特定网页的详细信息。",
        parameters={
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "要抓取的网页URL"
                },
                "extract_text": {
                    "type": "boolean",
                    "description": "是否提取纯文本内容",
                    "default": True
                }
            },
            "required": ["url"]
        },
        function=executor.execute_web_crawl,
    )
    print("  ✅ 注册 web_crawl 工具")

    # 注册 code runner 工具
    client.register_tool(
        name="code_runner",
        description="代码执行器，支持运行 python 和 javascript 代码",
        parameters={
            "type": "object",
            "properties": {
                "language": {
                    "type": "string",
                    "enum": ["python", "javascript"],
                    "description": "编程语言"
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
    print("  ✅ 注册 code_runner 工具\n")

    # 4. 使用工具进行对话
    print("💬 开始对话...\n")
    print("=" * 60)
    
    # 示例 1: 使用 code runner 判断素数
    user_message = "编程判断 3214567 是否是素数。"
    print(f"用户: {user_message}\n")
    
    messages = [{"role": "user", "content": user_message}]
    
    result = await client.generate_with_tools(messages=messages, max_tokens=4000)
    
    print(f"助手: {result['content']}\n")
    
    if result['tool_calls']:
        print("🔧 工具调用记录:")
        for i, call in enumerate(result['tool_calls'], 1):
            print(f"\n  {i}. {call['name']}")
            print(f"     输入: {call['input']}")
            print(f"     结果: {call['result']}")
    
    print("\n" + "=" * 60)
    print("✅ 示例完成！")


if __name__ == "__main__":
    asyncio.run(main())

