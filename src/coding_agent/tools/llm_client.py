"""LLM client for integrating with language models."""

import os
from typing import Optional, Dict, Any

try:
    from anthropic import AsyncAnthropic
except ImportError:
    AsyncAnthropic = None


class AnthropicClient:
    """Anthropic/Kimi API client wrapper."""

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