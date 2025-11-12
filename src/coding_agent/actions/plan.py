"""Todo list creation action."""

import uuid
from typing import Any, Dict, List
from .base import BaseAction
from ..core.state import AgentState, Task, TaskStatus


class CreateTodoAction(BaseAction):
    """Creates a todo list based on analysis."""
    
    def __init__(self, llm_client=None):
        super().__init__(
            name="create_todo",
            description="Create a detailed todo list based on requirement analysis"
        )
        self.llm_client = llm_client
    
    async def execute(self, state: AgentState, **kwargs) -> Dict[str, Any]:
        """Create todo list from analysis.
        
        Args:
            state: Current agent state
            
        Returns:
            Dictionary with todo list
        """
        analysis = state.analysis
        user_request = state.user_request
        
        todo_list: List[Dict[str, Any]] = []
        
        if self.llm_client:
            try:
                todo_prompt = f"""Based on this analysis and user request, create a detailed todo list:

Analysis: {analysis}
User Request: "{user_request}"

Create a list of specific, actionable tasks to accomplish this coding request. Each task should be:
1. Specific and clear
2. Actionable (can be completed)
3. Ordered logically
4. Include estimated priority (high/medium/low)

Format as a list of tasks with id, content, and priority."""
                
                # Placeholder - in real implementation would call LLM
                todo_list = [
                    {
                        "id": str(uuid.uuid4())[:8],
                        "content": "Understand the core requirements and constraints",
                        "status": TaskStatus.PENDING,
                        "priority": "high"
                    },
                    {
                        "id": str(uuid.uuid4())[:8],
                        "content": "Design the code structure and architecture",
                        "status": TaskStatus.PENDING,
                        "priority": "high"
                    },
                    {
                        "id": str(uuid.uuid4())[:8],
                        "content": "Implement the main functionality",
                        "status": TaskStatus.PENDING,
                        "priority": "high"
                    },
                    {
                        "id": str(uuid.uuid4())[:8],
                        "content": "Add error handling and edge cases",
                        "status": TaskStatus.PENDING,
                        "priority": "medium"
                    },
                    {
                        "id": str(uuid.uuid4())[:8],
                        "content": "Write documentation and examples",
                        "status": TaskStatus.PENDING,
                        "priority": "low"
                    }
                ]
                
                return {"todo_list": todo_list}
            except Exception:
                pass
        
        # Fallback todo list without LLM
        todo_list = [
            {
                "id": "task-001",
                "content": "Analyze and understand the requirements",
                "status": TaskStatus.PENDING,
                "priority": "high"
            },
            {
                "id": "task-002",
                "content": f"Create implementation for: {user_request[:50]}...",
                "status": TaskStatus.PENDING,
                "priority": "high"
            },
            {
                "id": "task-003",
                "content": "Test and validate the generated code",
                "status": TaskStatus.PENDING,
                "priority": "medium"
            }
        ]
        
        return {"todo_list": todo_list}