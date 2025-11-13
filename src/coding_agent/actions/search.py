"""Web search action."""

from typing import Any, Dict, List
import click
from .base import BaseAction
from ..core.state import AgentState
from ..tools.web_search import WebSearch, SearchResult


class WebSearchAction(BaseAction):
    """Performs web searches to gather information."""

    def __init__(self):
        super().__init__(
            name="web_search",
            description="Search the web for information to help with coding tasks"
        )
        self.search_tool = None
        self.search_history: List[Dict[str, Any]] = []

    async def execute(self, state: AgentState, **kwargs) -> Dict[str, Any]:
        """Execute web search based on the current state.

        Args:
            state: Current agent state

        Returns:
            Dictionary with search results
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
                    "search_results": [],
                    "error": str(e)
                }

        # Determine what to search for based on current state
        queries = self._generate_search_queries(state)

        if not queries:
            click.echo("ℹ️  No search queries generated")
            return {"search_performed": False, "search_results": []}

        click.echo(f"📊 Will perform {len(queries)} search query(ies)")

        # Perform searches
        all_results = []
        total_results_found = 0
        successful_queries = 0
        failed_queries = 0

        for query in queries:
            click.echo(f"🔍 Searching: '{query}'")
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

        # Print summary
        click.echo(f"\n{'='*60}")
        click.echo(f"📋 DDGS SEARCH SUMMARY")
        click.echo(f"{'='*60}")
        click.echo(f"Total queries executed: {len(queries)}")
        click.echo(f"Successful queries: {successful_queries}")
        click.echo(f"Failed queries: {failed_queries}")
        click.echo(f"Total results found: {total_results_found}")
        click.echo(f"Search source: DDGS (ddgs package)")
        click.echo(f"{'='*60}\n")

        return {
            "search_performed": len(all_results) > 0,
            "search_results": all_results,
            "search_history": self.search_history,
            "summary": {
                "total_queries": len(queries),
                "successful_queries": successful_queries,
                "failed_queries": failed_queries,
                "total_results": total_results_found
            }
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
