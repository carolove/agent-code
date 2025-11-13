# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based agentic coding assistant that uses an "Agentic Action Loop" pattern to analyze requirements, create todo lists, and generate code. The system is built with asyncio, uses Pydantic for state management, and optionally integrates with OpenAI for enhanced capabilities.

## Development Commands

### Setup and Installation
```bash
pip install -e ".[dev]"  # Install with development dependencies
```

### Testing
```bash
pytest                    # Run all tests
pytest tests/test_state.py  # Run specific test file
```

### Code Quality
```bash
black src/ tests/         # Format code (line length: 88)
mypy src/                 # Type checking (strict mode enabled)
flake8 src/ tests/        # Lint code
```

### Running the Agent
```bash
coding-agent "Create a Python function to calculate fibonacci numbers"
coding-agent "Generate a FastAPI endpoint" -o output.py --verbose
```

## Architecture

### Core Components

**Agentic Action Loop Pattern**: The system follows a state-driven loop where actions are executed based on the current state:

1. **AgentState** (`src/coding_agent/core/state.py`): Central state management with tasks, analysis, and generated code
2. **AgenticLoop** (`src/coding_agent/core/loop.py`): Orchestrates the action sequence based on current state
3. **BaseAction** (`src/coding_agent/actions/base.py`): Abstract base class for all agent actions
4. **Actions**: Specific implementations in `src/coding_agent/actions/`:
   - `AnalyzeRequirementAction`: Analyzes user requirements
   - `CreateTodoAction`: Creates todo list of tasks
   - `GenerateCodeAction`: Generates code based on analysis and todos

### State Flow

1. **start** → **analyzed** → **planned** → **completed**
2. Each action updates the state and determines the next action
3. The loop continues until `state.is_complete` is True

### Key Design Patterns

- **Async/Await**: All core operations are async for concurrent processing
- **Pydantic Models**: Type-safe state management with validation
- **Action Registration**: Actions are registered with the loop and selected based on state
- **LLM Integration**: Optional OpenAI client for enhanced analysis/generation

## Important Implementation Details

- **Python Version**: 3.8+ required
- **Entry Point**: `coding-agent` CLI command defined in `src/coding_agent/cli.py`
- **Error Handling**: Graceful error handling with state context preservation
- **Task Management**: Tasks have priority levels and status tracking (pending/completed)
- **Code Generation**: Generated code is stored in `state.generated_code` and can be saved to file

## Dependencies

- **Runtime**: `openai`, `click`, `pydantic`, `jinja2`
- **Development**: `pytest`, `black`, `flake8`, `mypy`
- **Optional**: OpenAI API key for enhanced capabilities (via `--api-key` or `OPENAI_API_KEY` env var)