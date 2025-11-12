"""Base action class for agentic actions."""

from abc import ABC, abstractmethod
from typing import Any, Dict
from ..core.state import AgentState


class BaseAction(ABC):
    """Base class for all agent actions."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    async def execute(self, state: AgentState, **kwargs) -> Dict[str, Any]:
        """Execute the action and return results.
        
        Args:
            state: Current agent state
            **kwargs: Additional arguments
            
        Returns:
            Dictionary containing action results
        """
        pass
    
    def can_execute(self, state: AgentState) -> bool:
        """Check if this action can be executed given the current state.
        
        Args:
            state: Current agent state
            
        Returns:
            True if action can execute, False otherwise
        """
        return True