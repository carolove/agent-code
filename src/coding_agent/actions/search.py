"""Web search and crawl action."""

from typing import Any, Dict, List
import click
from .base import BaseAction
from ..core.state import AgentState
from ..tools.web_search import WebSearch, SearchResult
from ..tools.web_crawler import WebCrawler


class WebSearchAction(BaseAction):
    """Performs web searches and optionally crawls the results to gather information."""

    def __init__(self, enable_crawling: bool = True, max_crawl_urls: int = 3):
        super().__init__(
            name="web_search",
            description="Search the web and crawl results for information to help with coding tasks"
        )
        self.search_tool = None
        self.crawler_tool = None
        self.search_history: List[Dict[str, Any]] = []
        self.crawl_history: List[Dict[str, Any]] = []
        self.enable_crawling = enable_crawling
        self.max_crawl_urls = max_crawl_urls

    async def execute(self, state: AgentState, **kwargs) -> Dict[str, Any]:
        """Execute web search and crawling based on the current state.

        Args:
            state: Current agent state

        Returns:
            Dictionary with search and crawl results
        """
        # Initialize search tool if not already done
        if self.search_tool is None:
            try:
                self.search_tool = WebSearch()
                click.echo("✅ DDGS search tool initialized successfully")
            except Exception as e:
                click.echo(f"❌ Failed to initialize web search: {str(e)}", err=True)
                return {
                    "search_performed": False,
                    "crawl_performed": False,
                    "search_results": [],
                    "crawl_results": [],
                    "error": str(e)
                }

        # Initialize crawler tool if crawling is enabled
        if self.enable_crawling and self.crawler_tool is None:
            try:
                self.crawler_tool = WebCrawler()
                click.echo("✅ Web crawler initialized successfully")
            except Exception as e:
                click.echo(f"⚠️  Failed to initialize web crawler: {str(e)}", err=True)
                click.echo("ℹ️  Continuing with search only (no crawling)")
                self.enable_crawling = False

        # Determine what to search for based on current state
        queries = self._generate_search_queries(state)

        if not queries:
            click.echo("ℹ️  No search queries generated")
            return {
                "search_performed": False,
                "crawl_performed": False,
                "search_results": [],
                "crawl_results": []
            }

        click.echo(f"📊 Will perform {len(queries)} search query(ies)")

        # Perform searches
        all_results = []
        all_urls_to_crawl = []
        total_results_found = 0
        successful_queries = 0
        failed_queries = 0

        for query in queries:
            click.echo(f"\n🔍 Searching: '{query}'")
            try:
                results = await self.search_tool.search(query, max_results=3)

                # Filter out error results
                valid_results = [r for r in results if r.source != "error"]
                error_results = [r for r in results if r.source == "error"]

                if error_results:
                    click.echo(f"   ⚠️  Warning: {error_results[0].snippet}")

                if valid_results:
                    successful_queries += 1
                    total_results_found += len(valid_results)
                    click.echo(f"   ✅ Found {len(valid_results)} result(s)")

                    # Collect URLs for crawling
                    for result in valid_results[:2]:  # Top 2 results per query
                        if WebCrawler.is_valid_url(result.url):
                            all_urls_to_crawl.append(result.url)
                            click.echo(f"   📄 Queued for crawl: {result.url[:60]}...")
                        else:
                            click.echo(f"   ⚠️  Invalid URL (skipping): {result.url[:60]}...")
                else:
                    click.echo(f"   ⚠️  No valid results returned")
                    failed_queries += 1

                search_entry = {
                    "query": query,
                    "results": [result.to_dict() for result in results]
                }
                all_results.append(search_entry)
                self.search_history.append(search_entry)

            except Exception as e:
                click.echo(f"   ❌ Search failed: {str(e)}", err=True)
                failed_queries += 1
                continue

        # Print search summary
        click.echo(f"\n{'='*60}")
        click.echo(f"📋 DDGS SEARCH SUMMARY")
        click.echo(f"{'='*60}")
        click.echo(f"Total queries executed: {len(queries)}")
        click.echo(f"Successful queries: {successful_queries}")
        click.echo(f"Failed queries: {failed_queries}")
        click.echo(f"Total results found: {total_results_found}")
        click.echo(f"URLs queued for crawling: {len(all_urls_to_crawl)}")
        click.echo(f"Search source: DDGS (ddgs package)")
        click.echo(f"{'='*60}\n")

        # Crawl the URLs if enabled
        crawl_results = []
        crawl_summary = None

        if self.enable_crawling and all_urls_to_crawl and self.crawler_tool:
            # Deduplicate URLs while preserving order
            seen = set()
            unique_urls = []
            for url in all_urls_to_crawl:
                if url not in seen:
                    seen.add(url)
                    unique_urls.append(url)

            # Limit number of URLs to crawl
            urls_to_crawl = unique_urls[:self.max_crawl_urls]

            click.echo(f"\n🕷️  Starting web crawl for {len(urls_to_crawl)} URL(s)...")

            # Fetch pages concurrently
            crawl_results_dict = await self.crawler_tool.fetch_multiple(
                urls_to_crawl, max_concurrent=3
            )

            # Process results
            for url, page in crawl_results_dict.items():
                crawl_entry = page.to_dict()
                crawl_results.append(crawl_entry)
                self.crawl_history.append(crawl_entry)

            # Crawl summary
            successful_crawls = len([r for r in crawl_results if r["status_code"] == 200])
            failed_crawls = len([r for r in crawl_results if r["error"]])
            total_content_size = sum(r.get("content_length", 0) for r in crawl_results)

            crawl_summary = {
                "total_urls": len(urls_to_crawl),
                "successful_crawls": successful_crawls,
                "failed_crawls": failed_crawls,
                "total_content_size": total_content_size
            }

            # Print crawl summary
            click.echo(f"\n{'='*60}")
            click.echo(f"🕷️  WEB CRAWL SUMMARY")
            click.echo(f"{'='*60}")
            click.echo(f"Total URLs crawled: {len(urls_to_crawl)}")
            click.echo(f"Successful crawls: {successful_crawls}")
            click.echo(f"Failed crawls: {failed_crawls}")
            click.echo(f"Total content size: {total_content_size} bytes")
            click.echo(f"Crawler: {'httpx (async)' if self.crawler_tool.prefer_async else 'requests (sync)'}")
            click.echo(f"{'='*60}\n")
        elif not self.enable_crawling:
            click.echo("ℹ️  Web crawling is disabled")
        elif not all_urls_to_crawl:
            click.echo("ℹ️  No valid URLs to crawl")
        else:
            click.echo("ℹ️  Crawler not available")

        return {
            "search_performed": len(all_results) > 0,
            "crawl_performed": len(crawl_results) > 0,
            "search_results": all_results,
            "crawl_results": crawl_results,
            "search_history": self.search_history,
            "crawl_history": self.crawl_history,
            "search_summary": {
                "total_queries": len(queries),
                "successful_queries": successful_queries,
                "failed_queries": failed_queries,
                "total_results": total_results_found
            } if all_results else None,
            "crawl_summary": crawl_summary
        }

    def _generate_search_queries(self, state: AgentState) -> List[str]:
        """Generate search queries based on the current state.

        Args:
            state: Current agent state

        Returns:
            List of search query strings
        """
        queries = []
        user_request = state.user_request

        # If we have no analysis yet, search for general information
        if not state.analysis:
            # Extract key terms and search for examples
            queries.append(f"how to implement {user_request} python example")
            queries.append(f"best practices {user_request} programming")

        # If we need to generate code, search for relevant examples
        if state.analysis and state.todo_list:
            # Search for each pending task
            pending_tasks = state.get_pending_tasks()
            for task in pending_tasks[:2]:  # Limit to top 2 tasks
                task_content = task.content.lower()
                if "function" in task_content or "class" in task_content:
                    queries.append(f"python {task.content} example implementation")
                elif "api" in task_content:
                    queries.append(f"how to create {task.content}")
                elif "database" in task_content:
                    queries.append(f"python database {task.content} tutorial")

        # Search for specific error context if any
        if state.context.get("error"):
            queries.append(f"python {state.context['error']} solution")

        # Remove duplicates and limit total queries
        unique_queries = []
        for query in queries:
            if query not in unique_queries:
                unique_queries.append(query)

        return unique_queries[:3]  # Limit to 3 queries max
