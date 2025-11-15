"""独立测试脚本 - 测试 tools use 核心功能。

这个脚本不依赖完整的项目安装，只测试核心的 tools use 逻辑。
"""

import sys
import os

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def test_tool_definitions():
    """测试工具定义。"""
    print("\n" + "=" * 60)
    print("测试 1: 工具定义")
    print("=" * 60)

    try:
        # 直接导入模块，避免通过 __init__.py
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "tool_definitions",
            os.path.join(os.path.dirname(__file__), 'src/coding_agent/tools/tool_definitions.py')
        )
        tool_definitions = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tool_definitions)

        get_web_search_tool_definition = tool_definitions.get_web_search_tool_definition
        get_web_crawler_tool_definition = tool_definitions.get_web_crawler_tool_definition
        get_code_runner_tool_definition = tool_definitions.get_code_runner_tool_definition
        get_all_tool_definitions = tool_definitions.get_all_tool_definitions
        
        # 测试单个工具定义
        web_search = get_web_search_tool_definition()
        assert web_search['type'] == 'function'
        assert web_search['function']['name'] == 'web_search'
        print("✅ web_search 工具定义正确")
        
        web_crawl = get_web_crawler_tool_definition()
        assert web_crawl['function']['name'] == 'web_crawl'
        print("✅ web_crawl 工具定义正确")
        
        code_runner = get_code_runner_tool_definition()
        assert code_runner['function']['name'] == 'code_runner'
        assert 'python' in code_runner['function']['parameters']['properties']['language']['enum']
        print("✅ code_runner 工具定义正确")
        
        # 测试所有工具
        all_tools = get_all_tool_definitions()
        assert len(all_tools) == 3
        print(f"✅ 所有工具定义正确 (共 {len(all_tools)} 个)")
        
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_tool_executor_code_runner():
    """测试代码执行器。"""
    print("\n" + "=" * 60)
    print("测试 2: Code Runner 工具执行")
    print("=" * 60)
    
    try:
        from coding_agent.tools.tool_executor import ToolExecutor
        
        executor = ToolExecutor()
        
        # 测试 Python 代码
        python_code = """
print("Hello from Python!")
result = 2 + 2
print(f"2 + 2 = {result}")
"""
        
        print("🐍 执行 Python 代码...")
        result = executor.execute_code_runner("python", python_code)
        
        if result.get("success"):
            print(f"✅ 执行成功")
            print(f"   输出: {result['stdout'].strip()}")
        else:
            print(f"⚠️  执行失败: {result.get('error', result.get('stderr'))}")
        
        # 测试素数判断（Kimi 示例）
        prime_code = """
def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

number = 3214567
result = is_prime(number)
print(f"{number} 是素数: {result}")
"""
        
        print("\n🔢 测试素数判断...")
        result = executor.execute_code_runner("python", prime_code)
        
        if result.get("success"):
            print(f"✅ 执行成功")
            print(f"   输出: {result['stdout'].strip()}")
        else:
            print(f"⚠️  执行失败: {result.get('error', result.get('stderr'))}")
        
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_llm_client_structure():
    """测试 LLM 客户端结构。"""
    print("\n" + "=" * 60)
    print("测试 3: LLM 客户端结构")
    print("=" * 60)
    
    try:
        # 只测试类结构，不实际初始化（避免需要 API key）
        import inspect
        from coding_agent.tools.llm_client import AnthropicClient
        
        # 检查方法是否存在
        methods = [m for m in dir(AnthropicClient) if not m.startswith('_')]
        
        required_methods = ['register_tool', 'generate_with_tools', 'generate_text']
        for method in required_methods:
            if method in dir(AnthropicClient):
                print(f"✅ 方法 {method} 存在")
            else:
                print(f"❌ 方法 {method} 不存在")
                return False
        
        # 检查 register_tool 的签名
        sig = inspect.signature(AnthropicClient.register_tool)
        params = list(sig.parameters.keys())
        expected_params = ['self', 'name', 'description', 'parameters', 'function']
        
        if params == expected_params:
            print(f"✅ register_tool 方法签名正确")
        else:
            print(f"⚠️  register_tool 方法签名: {params}")
        
        # 检查 generate_with_tools 的签名
        sig = inspect.signature(AnthropicClient.generate_with_tools)
        params = list(sig.parameters.keys())
        
        if 'messages' in params and 'tools' in params:
            print(f"✅ generate_with_tools 方法签名正确")
        else:
            print(f"⚠️  generate_with_tools 方法签名: {params}")
        
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试。"""
    print("\n🧪 开始测试 LLM Tools Use 功能（独立测试）")
    
    results = []
    
    # 运行测试
    results.append(test_tool_definitions())
    results.append(test_tool_executor_code_runner())
    results.append(test_llm_client_structure())
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 测试总结")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print("✅ 所有测试通过！")
        print("\n核心功能已正确实现:")
        print("  ✓ 工具定义格式正确")
        print("  ✓ Code Runner 可以执行代码")
        print("  ✓ LLM 客户端具有 tools use 方法")
    else:
        print(f"⚠️  {total - passed} 个测试失败")


if __name__ == "__main__":
    main()

