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
def main(request: str, output: Optional[str], verbose: bool, api_key: Optional[str]):
    """Coding AI Agent - Analyzes your coding request and generates code.
    
    REQUEST: Your coding request/description
    
    Examples:
    
        coding-agent "Create a Python function to calculate fibonacci numbers"
        
        coding-agent "Generate a FastAPI endpoint for user authentication" -o auth.py
        
        coding-agent "Write a script to parse JSON and extract specific fields" --verbose
    """
    asyncio.run(_run_agent(request, output, verbose, api_key))


async def _run_agent(request: str, output: Optional[str], verbose: bool, api_key: Optional[str]):
    """Run the agent asynchronously."""
    try:
        # Initialize LLM client if API key provided
        llm_client = None
        if api_key:
            try:
                from .tools.llm_client import OpenAIClient
                llm_client = OpenAIClient(api_key)
            except ImportError:
                click.echo("Warning: OpenAI client not available, running without LLM")
        
        # Create and run the agent loop
        click.echo(f"🤖 Processing request: {request}")
        if verbose:
            click.echo("-" * 50)
        
        loop = AgenticLoop(llm_client=llm_client)
        final_state = await loop.run(request)
        
        # Display results
        if verbose:
            click.echo("\n📋 Analysis:")
            click.echo(final_state.analysis or "No analysis generated")
            
            click.echo("\n✅ Todo List:")
            for task in final_state.todo_list:
                status_icon = "⏳" if task.status.value == "pending" else "✅"
                click.echo(f"  {status_icon} {task.content} ({task.priority} priority)")
        
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