"""Requirement analysis action."""

from typing import Any, Dict
import click
from .base import BaseAction
from ..core.state import AgentState


class AnalyzeRequirementAction(BaseAction):
    """Analyzes the user's coding requirement."""
    
    def __init__(self, llm_client=None):
        super().__init__(
            name="analyze_requirement",
            description="Analyze user requirement and create a detailed analysis"
        )
        self.llm_client = llm_client
    
    async def execute(self, state: AgentState, **kwargs) -> Dict[str, Any]:
        """Analyze the user's coding request.

        Args:
            state: Current agent state

        Returns:
            Dictionary with analysis results
        """
        user_request = state.user_request

        # If LLM client is available, use it for better analysis
        if self.llm_client:
            try:
                analysis = await self.llm_client.analyze_requirement(user_request)
                return {"analysis": analysis}
            except Exception as e:
                # Fallback to simple analysis if LLM fails
                click.echo(f"Warning: LLM analysis failed: {str(e)}", err=True)

        # Fallback analysis without LLM
        analysis = f"""Basic analysis of request: "{user_request}"

The user wants code to be generated based on their requirements. This requires:
1. Understanding the specific coding task
2. Creating a plan with actionable steps
3. Generating clean, functional code
4. Ensuring the code meets user expectations

Next step: Create a detailed todo list with specific tasks to accomplish this goal."""

        return {"analysis": analysis}