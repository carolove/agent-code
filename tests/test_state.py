"""Tests for AgentState."""

import pytest
from coding_agent.core.state import AgentState, Task, TaskStatus


def test_task_creation():
    """Test Task model creation."""
    task = Task(id="test-1", content="Test task", priority="high")
    assert task.id == "test-1"
    assert task.content == "Test task"
    assert task.priority == "high"
    assert task.status == TaskStatus.PENDING


def test_agent_state_initialization():
    """Test AgentState initialization."""
    state = AgentState(user_request="Test request")
    assert state.user_request == "Test request"
    assert state.todo_list == []
    assert state.is_complete is False
    assert state.current_step == "start"


def test_add_task():
    """Test adding tasks to state."""
    state = AgentState(user_request="Test")
    task = Task(id="1", content="Task 1", priority="high")
    
    state.add_task(task)
    assert len(state.todo_list) == 1
    assert state.todo_list[0].content == "Task 1"


def test_update_task_status():
    """Test updating task status."""
    state = AgentState(user_request="Test")
    task = Task(id="1", content="Task 1", priority="high")
    state.add_task(task)
    
    state.update_task_status("1", TaskStatus.COMPLETED)
    assert state.todo_list[0].status == TaskStatus.COMPLETED


def test_get_pending_tasks():
    """Test getting pending tasks."""
    state = AgentState(user_request="Test")
    state.add_task(Task(id="1", content="Task 1", priority="high"))
    state.add_task(Task(id="2", content="Task 2", priority="medium"))
    
    pending = state.get_pending_tasks()
    assert len(pending) == 2
    
    state.update_task_status("1", TaskStatus.COMPLETED)
    pending = state.get_pending_tasks()
    assert len(pending) == 1
    assert pending[0].id == "2"