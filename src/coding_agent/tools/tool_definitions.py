"""Tool definitions for LLM tool use."""

from typing import Dict, Any, List


def get_web_search_tool_definition() -> Dict[str, Any]:
    """Get web search tool definition.
    
    Returns:
        Tool definition dictionary
    """
    return {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "搜索网络以查找相关信息。可以用于查找代码示例、文档、最佳实践等。",
            "parameters": {
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
            }
        }
    }


def get_web_crawler_tool_definition() -> Dict[str, Any]:
    """Get web crawler tool definition.
    
    Returns:
        Tool definition dictionary
    """
    return {
        "type": "function",
        "function": {
            "name": "web_crawl",
            "description": "抓取网页内容并提取文本。用于获取特定网页的详细信息。",
            "parameters": {
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
            }
        }
    }


def get_code_runner_tool_definition() -> Dict[str, Any]:
    """Get code runner tool definition (example from Kimi).
    
    Returns:
        Tool definition dictionary
    """
    return {
        "type": "function",
        "function": {
            "name": "code_runner",
            "description": "代码执行器，支持运行 python 和 javascript 代码",
            "parameters": {
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
            }
        }
    }


def get_all_tool_definitions() -> List[Dict[str, Any]]:
    """Get all available tool definitions.
    
    Returns:
        List of tool definitions
    """
    return [
        get_web_search_tool_definition(),
        get_web_crawler_tool_definition(),
        get_code_runner_tool_definition(),
    ]

