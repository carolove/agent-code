"""Agent state management."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from enum import Enum


class TaskStatus(str, Enum):
    """Task status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class Task(BaseModel):
    """Represents a task in the todo list."""
    id: str
    content: str
    status: TaskStatus = TaskStatus.PENDING
    priority: str = "high"
    metadata: Optional[Dict[str, Any]] = None


class AgentState(BaseModel):
    """Central state for the agent."""
    
    # Original user request
    user_request: str
    
    # Current todo list
    todo_list: List[Task] = []
    
    # Generated analysis
    analysis: Optional[str] = None
    
    # Generated code
    generated_code: Optional[str] = None
    
    # Current step in the loop
    current_step: str = "start"
    
    # Additional context
    context: Dict[str, Any] = {}
    
    # Whether the agent has completed its work
    is_complete: bool = False
    
    def add_task(self, task: Task) -> None:
        """Add a task to the todo list."""
        self.todo_list.append(task)
    
    def update_task_status(self, task_id: str, status: TaskStatus) -> None:
        """Update the status of a task."""
        for task in self.todo_list:
            if task.id == task_id:
                task.status = status
                break
    
    def get_pending_tasks(self) -> List[Task]:
        """Get all pending tasks."""
        return [task for task in self.todo_list if task.status == TaskStatus.PENDING]
    
    def mark_complete(self) -> None:
        """Mark the agent as complete."""
        self.is_complete = True