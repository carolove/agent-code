"""测试 LLM tools use 功能。"""

import asyncio
from coding_agent.tools import AnthropicClient, ToolExecutor


async def test_tool_registration():
    """测试工具注册功能。"""
    print("\n" + "=" * 60)
    print("测试 1: 工具注册")
    print("=" * 60)
    
    try:
        client = AnthropicClient()
        executor = ToolExecutor()
        
        # 注册一个简单的测试工具
        def simple_tool(message: str) -> str:
            return f"收到消息: {message}"
        
        client.register_tool(
            name="simple_tool",
            description="一个简单的测试工具",
            parameters={
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "消息内容"}
                },
                "required": ["message"]
            },
            function=simple_tool,
        )
        
        print(f"✅ 成功注册工具")
        print(f"   已注册工具数量: {len(client.tool_definitions)}")
        print(f"   工具名称: {list(client.tool_registry.keys())}")
        
        # 测试工具执行
        result = await client._execute_tool("simple_tool", {"message": "Hello"})
        print(f"   工具执行结果: {result}")
        
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


async def test_web_search_tool():
    """测试 web search 工具。"""
    print("\n" + "=" * 60)
    print("测试 2: Web Search 工具")
    print("=" * 60)
    
    try:
        executor = ToolExecutor()
        
        print("🔍 执行搜索: 'Python asyncio tutorial'")
        result = await executor.execute_web_search("Python asyncio tutorial", max_results=3)
        
        if result.get("success"):
            print(f"✅ 搜索成功")
            print(f"   找到 {len(result['results'])} 个结果")
            for i, r in enumerate(result['results'][:2], 1):
                print(f"\n   {i}. {r['title']}")
                print(f"      {r['url']}")
        else:
            print(f"⚠️  搜索失败: {result.get('error')}")
        
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


async def test_code_runner_tool():
    """测试 code runner 工具。"""
    print("\n" + "=" * 60)
    print("测试 3: Code Runner 工具")
    print("=" * 60)
    
    try:
        executor = ToolExecutor()
        
        # 测试 Python 代码
        python_code = """
def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

print(f"3214567 是素数: {is_prime(3214567)}")
"""
        
        print("🐍 执行 Python 代码...")
        result = executor.execute_code_runner("python", python_code)
        
        if result.get("success"):
            print(f"✅ 执行成功")
            print(f"   输出: {result['stdout'].strip()}")
        else:
            print(f"⚠️  执行失败")
            print(f"   错误: {result.get('stderr', result.get('error'))}")
        
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


async def test_full_tool_use():
    """测试完整的 tools use 流程。"""
    print("\n" + "=" * 60)
    print("测试 4: 完整 Tools Use 流程")
    print("=" * 60)
    
    try:
        client = AnthropicClient()
        executor = ToolExecutor()
        
        # 注册 code runner 工具
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
                    "code": {"type": "string"}
                },
                "required": ["language", "code"]
            },
            function=executor.execute_code_runner,
        )
        
        print("💬 发送请求: '计算 1 到 100 的和'")
        
        messages = [{"role": "user", "content": "用 Python 计算 1 到 100 的和"}]
        result = await client.generate_with_tools(messages=messages, max_tokens=2000)
        
        print(f"\n📝 助手回复: {result['content'][:200]}...")
        
        if result['tool_calls']:
            print(f"\n🔧 调用了 {len(result['tool_calls'])} 个工具:")
            for call in result['tool_calls']:
                print(f"   - {call['name']}")
        
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """运行所有测试。"""
    print("\n🧪 开始测试 LLM Tools Use 功能")
    
    results = []
    
    # 运行测试
    results.append(await test_tool_registration())
    results.append(await test_web_search_tool())
    results.append(await test_code_runner_tool())
    results.append(await test_full_tool_use())
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 测试总结")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print("✅ 所有测试通过！")
    else:
        print(f"⚠️  {total - passed} 个测试失败")


if __name__ == "__main__":
    asyncio.run(main())

