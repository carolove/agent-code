# Quick Start Guide for coding-agent

## What Was Added

### 1. Environment Variables Support for Anthropic/Kimi
- `ANTHROPIC_BASE_URL` - Base URL for the API
- `ANTHROPIC_AUTH_TOKEN` - Authentication token
- `ANTHROPIC_MODEL` - Model name (default: claude-3-5-sonnet-20241022)
- `ANTHROPIC_SMALL_FAST_MODEL` - Model for quick tasks
- `OPENAI_API_KEY` - Optional OpenAI support

### 2. Web Search Capabilities
- Integrated DuckDuckGo search (no API key needed)
- Auto-searches based on your coding request
- Provides examples and context for better code generation
- Can search multiple queries to gather comprehensive information

### 3. Requirements Files
- `requirements.txt` - Production dependencies
- `requirements-dev.txt` - Development dependencies
- `setup.py` updated with optional extras:
  - `[anthropic]` - Anthropic/Kimi support
  - `[search]` - Web search functionality
  - `[all]` - Everything
  - `[dev]` - Development tools + all features

### 4. Enhanced CLI Options
```bash
--web-search (-s)     # Enable web search
--verbose (-v)        # Show detailed process
--output (-o)         # Save to file
--anthropic-base-url  # Set base URL
--anthropic-auth-token # Set auth token
```

## How to Get Started

### Step 1: Install Dependencies

```bash
cd /home/chendan/vnet/agent-code

# Activate your virtual environment
source ~/.config/python12/bin/activate

# Install with all features
pip install -e ".[all]"

# Check if installation succeeded
coding-agent --help
```

### Step 2: Set Up Environment Variables

```bash
export ANTHROPIC_BASE_URL="https://api.kimi.com/coding/"
export ANTHROPIC_AUTH_TOKEN="sk-kimi-xxxxxxx"
export ANTHROPIC_MODEL="kimi-for-coding"
export ANTHROPIC_SMALL_FAST_MODEL="kimi-for-coding"
```

### Step 3: Run Your First Query

```bash
# Basic usage with web search
coding-agent "Create a Python function to calculate fibonacci numbers" --web-search

# Verbose mode to see what's happening
coding-agent "Create a REST API with FastAPI" --web-search --verbose

# Save to file
coding-agent "Build a machine learning classifier" --web-search -o ml_classifier.py
```

## Key Features

1. **Agentic Action Loop**: The agent follows a structured process:
   - Analyze requirements
   - Create todo list
   - Search web for context (if enabled)
   - Generate code based on findings

2. **Web Search Integration**: When enabled with `--web-search`:
   - Automatically searches for relevant examples
   - Gathers implementation patterns
   - Finds best practices
   - Uses this information for better code generation

3. **Multiple LLM Support**:
   - Anthropic/Kimi (primary, via environment variables)
   - OpenAI (fallback, via `--api-key` or `OPENAI_API_KEY`)
   - Fallback mode (no LLM, uses built-in logic)

4. **Flexible Output**:
   - Display results in terminal
   - Save to file with `-o` flag
   - Verbose mode for detailed process view

## Troubleshooting

### ImportError: anthropic package not installed
```bash
pip install anthropic
```

### ImportError: ddgs package not installed
```bash
pip install ddgs
```

### Error: environment variable is required
Make sure you set all four ANTHROPIC environment variables.

### Command not found: coding-agent
```bash
# Reinstall in development mode
pip install -e .

# Or add to PATH
export PATH="$PATH:/path/to/your/venv/bin"
```

## Example Queries to Try

```bash
# Simple function
coding-agent "Create a Python function to reverse a string" --web-search

# Web scraping
coding-agent "Write a web scraper for extracting product prices" --web-search -o scraper.py

# Machine learning
coding-agent "Build a sentiment analysis model with scikit-learn" --web-search --verbose

# API development
coding-agent "Create a FastAPI CRUD app for todos" --web-search -o main.py

# Database operations
coding-agent "Write SQLAlchemy models for a blog" --web-search -o models.py
```

## Complete Documentation

See `INSTALL_AND_USAGE.md` for detailed installation instructions,
environment setup, troubleshooting, and development guide.
