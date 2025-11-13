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
            except Exception as e:
                click.echo(f"Warning: Failed to initialize web search: {str(e)}", err=True)
                return {
                    "search_performed": False,
                    "search_results": [],
                    "error": str(e)
                }

        # Determine what to search for based on current state
        queries = self._generate_search_queries(state)

        if not queries:
            return {"search_performed": False, "search_results": []}

        # Perform searches
        all_results = []
        for query in queries:
            click.echo(f"🔍 Searching: {query}")
            try:
                results = await self.search_tool.search(query, max_results=3)
                search_entry = {
                    "query": query,
                    "results": [result.to_dict() for result in results]
                }
                all_results.append(search_entry)
                self.search_history.append(search_entry)
            except Exception as e:
                click.echo(f"Warning: Search failed for '{query}': {str(e)}", err=True)
                continue

        return {
            "search_performed": len(all_results) > 0,
            "search_results": all_results,
            "search_history": self.search_history
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
