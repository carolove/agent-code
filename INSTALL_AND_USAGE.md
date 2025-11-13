# Installation and Usage Guide

## Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation Options

#### Option 1: Install from requirements.txt (Recommended)

```bash
# Clone or navigate to the project directory
cd /home/chendan/vnet/agent-code

# Install all dependencies including Anthropic/Kimi and web search
pip install -r requirements.txt
```

#### Option 2: Install via setup.py with extras

```bash
# Install with all features (Anthropic/Kimi + OpenAI + Web Search)
pip install -e ".[all]"

# Or install specific features:
# - Only Anthropic/Kimi support
pip install -e ".[anthropic]"

# - Only web search
pip install -e ".[search]"

# - All LLM providers
pip install -e ".[llms]"

# For development (includes all features + dev tools)
pip install -e ".[dev]"
```

### Environment Setup

#### For Anthropic/Kimi API:

```bash
# Set these in your shell config (.bashrc, .zshrc, etc.) or export manually
export ANTHROPIC_BASE_URL="https://api.kimi.com/coding/"
export ANTHROPIC_AUTH_TOKEN="sk-kimi-xxxx"
export ANTHROPIC_MODEL="kimi-for-coding"
export ANTHROPIC_SMALL_FAST_MODEL="kimi-for-coding"
```

#### Alternative: Create a .env file

Create a `.env` file in the project root:

```bash
ANTHROPIC_BASE_URL=https://api.kimi.com/coding/
ANTHROPIC_AUTH_TOKEN=sk-kimi-xxxx
ANTHROPIC_MODEL=kimi-for-coding
ANTHROPIC_SMALL_FAST_MODEL=kimi-for-coding
```

Then load it:
```bash
export $(cat .env | xargs)
```

### Verify Installation

Test if the package is installed correctly:

```bash
# Check if the command is available
coding-agent --help

# Test basic functionality (without LLM - uses fallback mode)
coding-agent "Create a Python function to add two numbers"
```

## Usage Examples

### Basic Usage (Fallback Mode - No API Required)

```bash
# Generate code using built-in logic (no LLM needed)
coding-agent "Create a Python function to calculate fibonacci numbers"
```

### With Anthropic/Kimi API

```bash
# Set up environment variables first (see Environment Setup above)

# Generate code with LLM-enhanced analysis
coding-agent "Create a REST API endpoint for user authentication with JWT"

# Verbose mode to see detailed analysis
coding-agent "Build a machine learning classifier" --verbose
```

### With Web Search

```bash
# Enable web search to gather context and examples
coding-agent "Create a web scraper for news articles" --web-search

# Combined with verbose mode to see search results
coding-agent "Implement a Redis cache in Python" --web-search --verbose

# Save output to file
coding-agent "Create a FastAPI application" --web-search -o app.py
```

### Advanced Examples

```bash
# Generate code for complex tasks with web research
coding-agent """
Create a Python script that:
1. Connects to a PostgreSQL database
2. Fetches data from a table
3. Processes the data
4. Generates a report
""" --web-search --verbose -o data_processor.py

# Use with custom Anthropic endpoint
export ANTHROPIC_BASE_URL="your-custom-endpoint"
export ANTHROPIC_AUTH_TOKEN="your-token"
coding-agent "Implement OAuth2 flow" --web-search
```

## Troubleshooting

### ImportError: anthropic package not installed

```bash
# Install the missing package
pip install anthropic
```

### ImportError: ddgs package not installed

```bash
# Install web search support
pip install ddgs
```

### Error: ANTHROPIC_BASE_URL environment variable is required

Make sure you've set the environment variables:
```bash
export ANTHROPIC_BASE_URL="your-api-url"
export ANTHROPIC_AUTH_TOKEN="your-token"
```

### ModuleNotFoundError: No module named 'coding_agent'

Install the package in development mode:
```bash
pip install -e .
```

## Performance Tips

1. **Use web search for complex topics**: `--web-search` flag greatly improves results for unfamiliar topics
2. **Verbose mode for debugging**: Use `-v` to see what the agent is doing
3. **Save results to files**: Use `-o filename.py` to save generated code
4. **Set model appropriately**: Use `ANTHROPIC_SMALL_FAST_MODEL` for quick tasks

## Development

### Running Tests

```bash
pytest
```

### Code Quality

```bash
# Format code
black src/ tests/

# Type checking
mypy src/

# Linting
flake8 src/ tests/
```

## Next Steps

- Explore examples in the `examples/` directory
- Read the architecture documentation in `CLAUDE.md`
- Customize the agent behavior by modifying actions in `src/coding_agent/actions/`
