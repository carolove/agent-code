"""Tools module for external integrations."""

from .llm_client import OpenAIClient, AnthropicClient
from .web_search import WebSearch, SearchResult
from .web_crawler import WebCrawler, WebPage
from .tool_definitions import (
    get_web_search_tool_definition,
    get_web_crawler_tool_definition,
    get_code_runner_tool_definition,
    get_all_tool_definitions,
)
from .tool_executor import ToolExecutor

__all__ = [
    "OpenAIClient",
    "AnthropicClient",
    "WebSearch",
    "SearchResult",
    "WebCrawler",
    "WebPage",
    "get_web_search_tool_definition",
    "get_web_crawler_tool_definition",
    "get_code_runner_tool_definition",
    "get_all_tool_definitions",
    "ToolExecutor",
]