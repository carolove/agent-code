"""Web search tools for querying information from the internet."""

import asyncio
from typing import List, Dict, Any, Optional

try:
    from ddgs import DDGS
except ImportError:
    DDGS = None


class SearchResult:
    """Represents a search result."""

    def __init__(self, title: str, url: str, snippet: str, source: str = "unknown"):
        self.title = title
        self.url = url
        self.snippet = snippet
        self.source = source

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "source": self.source,
        }


class WebSearch:
    """Web search interface supporting multiple search engines."""

    def __init__(self, backend: str = "ddgs"):
        """Initialize web search.

        Args:
            backend: Search backend to use ("ddgs")
        """
        if backend == "ddgs":
            if DDGS is None:
                raise ImportError(
                    "ddgs package not installed. Run: pip install ddgs"
                )
            self.searcher = DDGSSearch()
        else:
            raise ValueError(f"Unsupported search backend: {backend}")

    async def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        """Search the web for a query.

        Args:
            query: Search query string
            max_results: Maximum number of results to return

        Returns:
            List of search results
        """
        return await self.searcher.search(query, max_results)

    async def search_multiple(self, queries: List[str], max_results: int = 3) -> Dict[str, List[SearchResult]]:
        """Search for multiple queries.

        Args:
            queries: List of search query strings
            max_results: Maximum number of results per query

        Returns:
            Dictionary mapping query to list of results
        """
        results = {}
        for query in queries:
            results[query] = await self.search(query, max_results)
        return results


class DDGSSearch:
    """DDGS (formerly DuckDuckGo) search implementation."""

    async def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        """Search DDGS.

        Args:
            query: Search query
            max_results: Maximum number of results

        Returns:
            List of search results
        """
        # Run sync function in thread pool since ddgs is synchronous
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._sync_search, query, max_results)

    def _sync_search(self, query: str, max_results: int) -> List[SearchResult]:
        """Synchronous search implementation."""
        results = []
        try:
            with DDGS() as ddgs:
                # Search for results
                search_results = ddgs.text(query, max_results=max_results)

                for result in search_results:
                    search_result = SearchResult(
                        title=result.get("title", ""),
                        url=result.get("href", ""),
                        snippet=result.get("body", ""),
                        source="ddgs",
                    )
                    results.append(search_result)
        except Exception as e:
            # Return empty list or error result on failure
            results.append(
                SearchResult(
                    title="Search Error",
                    url="",
                    snippet=f"Failed to search: {str(e)}",
                    source="error",
                )
            )

        return results
