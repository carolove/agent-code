"""Command-line interface for the coding agent."""

import asyncio
import click
from pathlib import Path
from typing import Optional

from .core.loop import AgenticLoop
from .core.state import AgentState


@click.command()
@click.argument("request", type=str, required=True)
@click.option(
    "--output", "-o",
    type=click.Path(),
    help="Save generated code to file"
)
@click.option(
    "--verbose", "-v",
    is_flag=True,
    help="Show detailed agent thinking process"
)
@click.option(
    "--api-key",
    type=str,
    envvar="OPENAI_API_KEY",
    help="OpenAI API key (or set OPENAI_API_KEY environment variable)"
)
@click.option(
    "--web-search", "-s",
    is_flag=True,
    help="Enable web search to gather context and examples"
)
@click.option(
    "--anthropic-base-url",
    type=str,
    envvar="ANTHROPIC_BASE_URL",
    help="Anthropic/Kimi base URL (or set ANTHROPIC_BASE_URL environment variable)"
)
@click.option(
    "--anthropic-auth-token",
    type=str,
    envvar="ANTHROPIC_AUTH_TOKEN",
    help="Anthropic/Kimi auth token (or set ANTHROPIC_AUTH_TOKEN environment variable)"
)
def main(
    request: str,
    output: Optional[str],
    verbose: bool,
    api_key: Optional[str],
    web_search: bool,
    anthropic_base_url: Optional[str],
    anthropic_auth_token: Optional[str]
):
    """Coding AI Agent - Analyzes your coding request and generates code.

    REQUEST: Your coding request/description

    Examples:

        coding-agent "Create a Python function to calculate fibonacci numbers"

        coding-agent "Generate a FastAPI endpoint for user authentication" -o auth.py

        coding-agent "Write a script to parse JSON and extract specific fields" --verbose

        coding-agent "Create a machine learning classifier" --web-search

    Environment Variables:

        ANTHROPIC_BASE_URL: Base URL for Anthropic/Kimi API
        ANTHROPIC_AUTH_TOKEN: Authentication token for Anthropic/Kimi API
        ANTHROPIC_MODEL: Model to use (default: claude-3-5-sonnet-20241022)
        ANTHROPIC_SMALL_FAST_MODEL: Model for quick tasks
        OPENAI_API_KEY: OpenAI API key (optional)
    """
    asyncio.run(_run_agent(request, output, verbose, api_key, web_search, anthropic_base_url, anthropic_auth_token))


async def _run_agent(
    request: str,
    output: Optional[str],
    verbose: bool,
    api_key: Optional[str],
    web_search: bool,
    anthropic_base_url: Optional[str],
    anthropic_auth_token: Optional[str]
):
    """Run the agent asynchronously."""
    try:
        # Initialize Anthropic/Kimi client if auth token provided
        llm_client = None
        if anthropic_auth_token or anthropic_base_url:
            try:
                from .tools.llm_client import AnthropicClient
                llm_client = AnthropicClient(
                    base_url=anthropic_base_url,
                    auth_token=anthropic_auth_token
                )
                click.echo("✨ Using Anthropic/Kimi LLM client")
            except ImportError as e:
                click.echo(f"Warning: {str(e)}, running without LLM", err=True)
            except ValueError as e:
                click.echo(f"Note: {str(e)}, using fallback mode", err=True)
        elif api_key:
            # Fall back to OpenAI
            try:
                from .tools.llm_client import OpenAIClient
                llm_client = OpenAIClient(api_key)
                click.echo("✨ Using OpenAI client")
            except ImportError:
                click.echo("Warning: OpenAI client not available, running without LLM")

        # Create and run the agent loop
        click.echo(f"🤖 Processing request: {request}")
        if web_search:
            click.echo("🔍 Web search enabled - will search for examples and context")
        if verbose:
            click.echo("-" * 50)

        loop = AgenticLoop(llm_client=llm_client, enable_web_search=web_search)
        final_state = await loop.run(request)
        
        # Display results
        if verbose:
            click.echo("\n📋 Analysis:")
            click.echo(final_state.analysis or "No analysis generated")

            click.echo("\n✅ Todo List:")
            for task in final_state.todo_list:
                status_icon = "⏳" if task.status.value == "pending" else "✅"
                click.echo(f"  {status_icon} {task.content} ({task.priority} priority)")

            # Display search results if available
            if final_state.context.get("search_results"):
                click.echo("\n🔍 Web Search Results:")
                for search_entry in final_state.context["search_results"]:
                    click.echo(f"\n  Query: {search_entry['query']}")
                    for idx, result in enumerate(search_entry['results'], 1):
                        if result['source'] != 'error':
                            click.echo(f"\n    {idx}. {result['title']}")
                            click.echo(f"       {result['snippet']}")
                            click.echo(f"       {result['url']}")
                        else:
                            click.echo(f"\n    {idx}. Error: {result['snippet']}")

        if final_state.generated_code:
            click.echo("\n💻 Generated Code:")
            click.echo("-" * 50)
            click.echo(final_state.generated_code)
            click.echo("-" * 50)
            
            # Save to file if requested
            if output:
                output_path = Path(output)
                output_path.write_text(final_state.generated_code)
                click.echo(f"\n✅ Code saved to: {output_path.absolute()}")
        else:
            click.echo("\n❌ No code was generated.")
            if final_state.context.get("error"):
                click.echo(f"Error: {final_state.context['error']}")
        
    except Exception as e:
        click.echo(f"\n❌ Error: {str(e)}", err=True)
        raise click.ClickException(str(e))


if __name__ == "__main__":
    main()