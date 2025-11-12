"""Coding Agent - An agentic coding assistant."""

__version__ = "0.1.0"
__author__ = "Daniel Chen"
__email__ = "doke.hi@gmail.com"

from .core.agent import CodingAgent
from .core.loop import AgenticLoop
from .core.state import AgentState

__all__ = ["CodingAgent", "AgenticLoop", "AgentState"]