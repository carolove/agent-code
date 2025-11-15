"""Tool executor for handling tool calls."""

import subprocess
import tempfile
import os
from typing import Dict, Any, Optional

from .web_search import WebSearch
from .web_crawler import WebCrawler


class ToolExecutor:
    """Executes tools called by the LLM."""

    def __init__(self):
        """Initialize tool executor."""
        self.web_search: Optional[WebSearch] = None
        self.web_crawler: Optional[WebCrawler] = None

    async def execute_web_search(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """Execute web search.

        Args:
            query: Search query
            max_results: Maximum number of results

        Returns:
            Search results dictionary
        """
        if self.web_search is None:
            try:
                self.web_search = WebSearch()
            except Exception as e:
                return {"error": f"Failed to initialize web search: {str(e)}"}

        try:
            results = await self.web_search.search(query, max_results)
            return {
                "success": True,
                "query": query,
                "results": [
                    {
                        "title": r.title,
                        "url": r.url,
                        "snippet": r.snippet,
                        "source": r.source,
                    }
                    for r in results
                    if r.source != "error"
                ],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def execute_web_crawl(self, url: str, extract_text: bool = True) -> Dict[str, Any]:
        """Execute web crawl.

        Args:
            url: URL to crawl
            extract_text: Whether to extract text

        Returns:
            Crawled page dictionary
        """
        if self.web_crawler is None:
            try:
                self.web_crawler = WebCrawler()
            except Exception as e:
                return {"error": f"Failed to initialize web crawler: {str(e)}"}

        try:
            page = await self.web_crawler.fetch(url, extract_text)
            
            if page.error:
                return {
                    "success": False,
                    "url": url,
                    "error": page.error,
                    "status_code": page.status_code,
                }
            
            return {
                "success": True,
                "url": page.url,
                "title": page.title,
                "text": page.text[:5000] if extract_text else "",  # Limit text length
                "status_code": page.status_code,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def execute_code_runner(self, language: str, code: str) -> Dict[str, Any]:
        """Execute code in a sandboxed environment.

        Args:
            language: Programming language (python or javascript)
            code: Code to execute

        Returns:
            Execution result dictionary
        """
        if language not in ["python", "javascript"]:
            return {"success": False, "error": f"Unsupported language: {language}"}

        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".py" if language == "python" else ".js",
                delete=False,
            ) as f:
                f.write(code)
                temp_file = f.name

            try:
                # Execute code
                if language == "python":
                    result = subprocess.run(
                        ["python3", temp_file],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                else:  # javascript
                    result = subprocess.run(
                        ["node", temp_file],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )

                return {
                    "success": result.returncode == 0,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode,
                }
            finally:
                # Clean up temp file
                os.unlink(temp_file)

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Code execution timeout (5s limit)"}
        except Exception as e:
            return {"success": False, "error": str(e)}

