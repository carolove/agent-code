"""Main Coding Agent class - primary entry point for the agent."""

from typing import Optional
from .loop import AgenticLoop
from .state import AgentState


class CodingAgent:
    """Main Coding Agent class that provides a simple interface to the agentic system."""
    
    def __init__(self, llm_client=None):
        """Initialize the Coding Agent.
        
        Args:
            llm_client: Optional LLM client for enhanced capabilities
        """
        self.llm_client = llm_client
        self.loop = AgenticLoop(llm_client=llm_client)
    
    async def process_request(self, request: str) -> AgentState:
        """Process a coding request and return the final state.
        
        Args:
            request: The user's coding request
            
        Returns:
            Final agent state containing analysis, todo list, and generated code
        """
        return await self.loop.run(request)
    
    def process_request_sync(self, request: str) -> AgentState:
        """Synchronous version of process_request.
        
        Args:
            request: The user's coding request
            
        Returns:
            Final agent state
        """
        import asyncio
        return asyncio.run(self.process_request(request))