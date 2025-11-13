"""Agentic Action Loop implementation."""

from typing import Dict, List, Type
from .state import AgentState, TaskStatus
from ..actions.base import BaseAction
from ..actions import AnalyzeRequirementAction, CreateTodoAction, GenerateCodeAction, WebSearchAction


class AgenticLoop:
    """Main agentic action loop that orchestrates agent behavior."""

    def __init__(self, llm_client=None, enable_web_search: bool = False):
        self.llm_client = llm_client
        self.enable_web_search = enable_web_search
        self.actions: Dict[str, BaseAction] = {}
        self._register_default_actions()

    def _register_default_actions(self) -> None:
        """Register default actions for the coding agent."""
        self.register_action(AnalyzeRequirementAction(self.llm_client))
        self.register_action(CreateTodoAction(self.llm_client))
        self.register_action(GenerateCodeAction(self.llm_client))
        if self.enable_web_search:
            self.register_action(WebSearchAction())

    def register_action(self, action: BaseAction) -> None:
        """Register an action with the loop."""
        self.actions[action.name] = action

    def _determine_next_action(self, state: AgentState) -> BaseAction:
        """Determine the next action based on current state."""
        # Start with analysis if not done yet
        if not state.analysis and state.current_step == "start":
            # If web search is enabled, search first to gather context
            if self.enable_web_search and not state.context.get("search_performed"):
                return self.actions["web_search"]
            return self.actions["analyze_requirement"]

        # Create todo list if not done yet
        if not state.todo_list and state.analysis:
            return self.actions["create_todo"]

        # Check for pending tasks
        pending_tasks = state.get_pending_tasks()
        if pending_tasks and not state.generated_code:
            # Search for implementation examples if needed
            if self.enable_web_search and state.current_step == "planned":
                return self.actions["web_search"]
            return self.actions["generate_code"]

        # If all tasks are done or no tasks needed, mark complete
        if not pending_tasks or state.generated_code:
            state.mark_complete()
            # Return a no-op action
            return self.actions["analyze_requirement"]  # Will check is_complete before executing

        return self.actions["analyze_requirement"]

    async def run(self, user_request: str) -> AgentState:
        """Run the agentic loop for a user request.

        Args:
            user_request: The user's coding request

        Returns:
            Final agent state
        """
        # Initialize state
        state = AgentState(user_request=user_request)

        # Run loop until complete
        while not state.is_complete:
            # Determine next action
            action = self._determine_next_action(state)

            # Skip if action can't execute (fallback)
            if not action.can_execute(state):
                state.mark_complete()
                break

            # Execute action
            try:
                result = await action.execute(state)

                # Update state with results
                if "analysis" in result:
                    state.analysis = result["analysis"]
                    state.current_step = "analyzed"

                if "todo_list" in result:
                    for task_data in result["todo_list"]:
                        from ..core.state import Task
                        task = Task(**task_data)
                        state.add_task(task)
                    state.current_step = "planned"

                if "code" in result:
                    state.generated_code = result["code"]
                    state.current_step = "completed"
                    # Mark all tasks as completed
                    for task in state.todo_list:
                        state.update_task_status(task.id, TaskStatus.COMPLETED)

                # Store search results in context
                if "search_results" in result:
                    state.context["search_results"] = result["search_results"]
                    state.context["search_performed"] = result.get("search_performed", False)
                    if "summary" in result:
                        state.context["search_summary"] = result["summary"]

            except Exception as e:
                # Handle errors gracefully
                state.context["error"] = str(e)
                state.mark_complete()
                break

        return state