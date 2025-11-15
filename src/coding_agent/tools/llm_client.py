"""LLM client for integrating with language models."""

import os
import json
from typing import Optional, Dict, Any, List, Callable

try:
    from anthropic import AsyncAnthropic
except ImportError:
    AsyncAnthropic = None


class AnthropicClient:
    """Anthropic/Kimi API client wrapper with tools use support."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        auth_token: Optional[str] = None,
        model: Optional[str] = None,
        small_fast_model: Optional[str] = None,
    ):
        """Initialize Anthropic client from environment variables or explicit parameters.

        Args:
            base_url: Anthropic base URL (or set ANTHROPIC_BASE_URL env var)
            auth_token: Authentication token (or set ANTHROPIC_AUTH_TOKEN env var)
            model: Model name for general tasks (or set ANTHROPIC_MODEL env var)
            small_fast_model: Model name for quick tasks (or set ANTHROPIC_SMALL_FAST_MODEL env var)
        """
        if AsyncAnthropic is None:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")

        self.base_url = base_url or os.getenv("ANTHROPIC_BASE_URL")
        self.auth_token = auth_token or os.getenv("ANTHROPIC_AUTH_TOKEN")
        self.model = model or os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
        self.small_fast_model = small_fast_model or os.getenv(
            "ANTHROPIC_SMALL_FAST_MODEL", self.model
        )

        if not self.base_url:
            raise ValueError(
                "ANTHROPIC_BASE_URL environment variable or base_url parameter is required"
            )
        if not self.auth_token:
            raise ValueError(
                "ANTHROPIC_AUTH_TOKEN environment variable or auth_token parameter is required"
            )

        self.client = AsyncAnthropic(
            base_url=self.base_url, api_key=self.auth_token, max_retries=2
        )

        # Tool registry: maps tool name to callable function
        self.tool_registry: Dict[str, Callable] = {}

        # Tool definitions for API
        self.tool_definitions: List[Dict[str, Any]] = []

    def register_tool(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        function: Callable,
    ) -> None:
        """Register a tool for use with the LLM.

        Args:
            name: Tool name
            description: Tool description
            parameters: JSON schema for tool parameters
            function: Callable function to execute when tool is called
        """
        self.tool_registry[name] = function
        self.tool_definitions.append({
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": parameters,
            }
        })

    async def _execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Any:
        """Execute a registered tool.

        Args:
            tool_name: Name of the tool to execute
            tool_input: Input parameters for the tool

        Returns:
            Tool execution result
        """
        if tool_name not in self.tool_registry:
            raise ValueError(f"Tool '{tool_name}' not registered")

        tool_function = self.tool_registry[tool_name]

        # Execute the tool (handle both sync and async functions)
        import asyncio
        if asyncio.iscoroutinefunction(tool_function):
            result = await tool_function(**tool_input)
        else:
            result = tool_function(**tool_input)

        return result

    async def generate_text(
        self, prompt: str, max_tokens: int = 4000, model: Optional[str] = None
    ) -> str:
        """Generate text using the LLM.

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            model: Model to use (defaults to ANTHROPIC_MODEL)

        Returns:
            Generated text
        """
        model_to_use = model or self.model

        message = await self.client.messages.create(
            model=model_to_use, max_tokens=max_tokens, messages=[{"role": "user", "content": prompt}]
        )

        return message.content[0].text

    async def generate_with_tools(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        max_tokens: int = 4000,
        model: Optional[str] = None,
        max_iterations: int = 5,
    ) -> Dict[str, Any]:
        """Generate text with tool use support.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            tools: List of tool definitions (uses registered tools if None)
            max_tokens: Maximum tokens to generate
            model: Model to use (defaults to ANTHROPIC_MODEL)
            max_iterations: Maximum number of tool call iterations

        Returns:
            Dictionary with 'content' (final text) and 'tool_calls' (list of tool calls made)
        """
        model_to_use = model or self.model
        tools_to_use = tools if tools is not None else self.tool_definitions

        conversation_messages = messages.copy()
        tool_calls_made = []

        for iteration in range(max_iterations):
            # Create message with or without tools
            if tools_to_use:
                response = await self.client.messages.create(
                    model=model_to_use,
                    max_tokens=max_tokens,
                    messages=conversation_messages,
                    tools=tools_to_use,
                )
            else:
                response = await self.client.messages.create(
                    model=model_to_use,
                    max_tokens=max_tokens,
                    messages=conversation_messages,
                )

            # Check if the model wants to use a tool
            if response.stop_reason == "tool_use":
                # Process tool calls
                tool_results = []

                for content_block in response.content:
                    if content_block.type == "tool_use":
                        tool_name = content_block.name
                        tool_input = content_block.input
                        tool_use_id = content_block.id

                        # Execute the tool
                        try:
                            tool_result = await self._execute_tool(tool_name, tool_input)
                            tool_calls_made.append({
                                "name": tool_name,
                                "input": tool_input,
                                "result": tool_result,
                            })

                            # Format result for API
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": tool_use_id,
                                "content": json.dumps(tool_result) if not isinstance(tool_result, str) else tool_result,
                            })
                        except Exception as e:
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": tool_use_id,
                                "content": f"Error executing tool: {str(e)}",
                                "is_error": True,
                            })

                # Add assistant's response and tool results to conversation
                conversation_messages.append({
                    "role": "assistant",
                    "content": response.content,
                })
                conversation_messages.append({
                    "role": "user",
                    "content": tool_results,
                })
            else:
                # No more tool calls, return final response
                final_text = ""
                for content_block in response.content:
                    if hasattr(content_block, "text"):
                        final_text += content_block.text

                return {
                    "content": final_text,
                    "tool_calls": tool_calls_made,
                    "stop_reason": response.stop_reason,
                }

        # Max iterations reached
        return {
            "content": "Maximum tool use iterations reached",
            "tool_calls": tool_calls_made,
            "stop_reason": "max_iterations",
        }

    async def analyze_requirement(self, request: str) -> str:
        """Analyze a coding requirement.

        Args:
            request: User's coding request

        Returns:
            Analysis text
        """
        analysis_prompt = f"""Analyze the following coding request and provide a detailed breakdown:

Request: "{request}"

Please provide:
1. What type of code needs to be created (function, class, script, etc.)
2. Key requirements and constraints
3. Input/output specifications
4. Any edge cases to consider
5. Technology stack or language specifics

Provide a clear, concise analysis that will help in creating a todo list and generating code."""

        return await self.generate_text(analysis_prompt, max_tokens=2000)

    async def generate_code(self, request: str, analysis: str, todo_items: list) -> str:
        """Generate code based on analysis.

        Args:
            request: Original user request
            analysis: Analysis of the requirements
            todo_items: List of todo items to guide generation

        Returns:
            Generated code
        """
        code_prompt = f"""Generate code based on the following requirements:

User Request: "{request}"

Analysis:
{analysis}

Todo Items:
{"\n".join([f"- {item.content}" for item in todo_items])}

Please generate clean, well-documented code that fulfills the requirements. Include:
1. Clear function/class definitions
2. Proper error handling
3. Docstrings and comments
4. Example usage if appropriate

Return only the code without additional explanations."""

        return await self.generate_text(code_prompt, max_tokens=4000)


class OpenAIClient:
    """OpenAI API client wrapper (kept for backward compatibility)."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize OpenAI client.

        Args:
            api_key: OpenAI API key (or set OPENAI_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable or api_key parameter is required")

    async def generate_text(self, prompt: str, max_tokens: int = 1000) -> str:
        """Generate text using the LLM.

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text
        """
        return f"Generated response for: {prompt[:50]}..."

    async def analyze_requirement(self, request: str) -> str:
        """Analyze a coding requirement.

        Args:
            request: User's coding request

        Returns:
            Analysis text
        """
        return f"Analysis of coding request: {request}"

    async def generate_code(self, request: str, analysis: str) -> str:
        """Generate code based on analysis.

        Args:
            request: Original user request
            analysis: Analysis of the requirements

        Returns:
            Generated code
        """
        return f'"""\nGenerated code for: {request}\n\n{analysis}\n"""\n\n\ndef generated_function():\n    """Implementation goes here."""\n    pass'