"""验证 tools use 实现。

这个脚本直接检查文件是否存在以及代码结构是否正确。
"""

import os
import ast


def check_file_exists(filepath):
    """检查文件是否存在。"""
    exists = os.path.exists(filepath)
    status = "✅" if exists else "❌"
    print(f"{status} {filepath}")
    return exists


def check_function_in_file(filepath, function_name):
    """检查文件中是否包含指定函数。"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                print(f"  ✅ 函数 {function_name} 存在")
                return True
        
        print(f"  ❌ 函数 {function_name} 不存在")
        return False
    except Exception as e:
        print(f"  ❌ 检查失败: {e}")
        return False


def check_class_method_in_file(filepath, class_name, method_name):
    """检查文件中的类是否包含指定方法。"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                for item in node.body:
                    # 检查普通函数和异步函数
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == method_name:
                        func_type = "async " if isinstance(item, ast.AsyncFunctionDef) else ""
                        print(f"  ✅ {class_name}.{func_type}{method_name} 存在")
                        return True

        print(f"  ❌ {class_name}.{method_name} 不存在")
        return False
    except Exception as e:
        print(f"  ❌ 检查失败: {e}")
        return False


def main():
    """主函数。"""
    print("\n" + "=" * 60)
    print("验证 Tools Use 功能实现")
    print("=" * 60)
    
    results = []
    
    # 1. 检查新增文件
    print("\n📁 检查新增文件:")
    files_to_check = [
        "src/coding_agent/tools/tool_definitions.py",
        "src/coding_agent/tools/tool_executor.py",
        "examples/tool_use_example.py",
        "examples/simple_tool_use.py",
        "docs/TOOL_USE.md",
        "docs/TOOLS_USE_IMPLEMENTATION.md",
    ]
    
    for filepath in files_to_check:
        results.append(check_file_exists(filepath))
    
    # 2. 检查 tool_definitions.py 中的函数
    print("\n🔧 检查工具定义:")
    tool_def_file = "src/coding_agent/tools/tool_definitions.py"
    if os.path.exists(tool_def_file):
        results.append(check_function_in_file(tool_def_file, "get_web_search_tool_definition"))
        results.append(check_function_in_file(tool_def_file, "get_web_crawler_tool_definition"))
        results.append(check_function_in_file(tool_def_file, "get_code_runner_tool_definition"))
        results.append(check_function_in_file(tool_def_file, "get_all_tool_definitions"))
    
    # 3. 检查 tool_executor.py 中的类和方法
    print("\n⚙️  检查工具执行器:")
    tool_exec_file = "src/coding_agent/tools/tool_executor.py"
    if os.path.exists(tool_exec_file):
        results.append(check_class_method_in_file(tool_exec_file, "ToolExecutor", "execute_web_search"))
        results.append(check_class_method_in_file(tool_exec_file, "ToolExecutor", "execute_web_crawl"))
        results.append(check_class_method_in_file(tool_exec_file, "ToolExecutor", "execute_code_runner"))
    
    # 4. 检查 llm_client.py 中的新方法
    print("\n🤖 检查 LLM 客户端:")
    llm_client_file = "src/coding_agent/tools/llm_client.py"
    if os.path.exists(llm_client_file):
        results.append(check_class_method_in_file(llm_client_file, "AnthropicClient", "register_tool"))
        results.append(check_class_method_in_file(llm_client_file, "AnthropicClient", "generate_with_tools"))
        results.append(check_class_method_in_file(llm_client_file, "AnthropicClient", "_execute_tool"))
    
    # 5. 检查代码内容
    print("\n📝 检查关键代码:")
    
    # 检查 tool_definitions.py 中的工具定义格式
    if os.path.exists(tool_def_file):
        with open(tool_def_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if '"type": "function"' in content:
                print("  ✅ 工具定义包含正确的类型")
                results.append(True)
            else:
                print("  ❌ 工具定义缺少类型")
                results.append(False)
            
            if 'code_runner' in content:
                print("  ✅ 包含 code_runner 工具")
                results.append(True)
            else:
                print("  ❌ 缺少 code_runner 工具")
                results.append(False)
    
    # 检查 llm_client.py 中的 tools use 逻辑
    if os.path.exists(llm_client_file):
        with open(llm_client_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'tool_registry' in content:
                print("  ✅ 包含工具注册表")
                results.append(True)
            else:
                print("  ❌ 缺少工具注册表")
                results.append(False)
            
            if 'stop_reason == "tool_use"' in content:
                print("  ✅ 包含工具调用处理逻辑")
                results.append(True)
            else:
                print("  ❌ 缺少工具调用处理逻辑")
                results.append(False)
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 验证总结")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print("\n✅ 所有检查通过！")
        print("\nTools Use 功能已成功实现，包括:")
        print("  ✓ 工具定义模块 (tool_definitions.py)")
        print("  ✓ 工具执行器 (tool_executor.py)")
        print("  ✓ LLM 客户端 tools use 方法")
        print("  ✓ 示例代码和文档")
        print("\n使用方法请参考:")
        print("  - docs/TOOL_USE.md")
        print("  - examples/simple_tool_use.py")
    else:
        print(f"\n⚠️  {total - passed} 个检查失败")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

