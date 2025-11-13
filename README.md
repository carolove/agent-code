# this is a practise project, don't trust it.
# Coding Agent

An agentic coding assistant that analyzes requirements, creates todo lists, and generates code using the Agentic Action Loop programming model.

## Installation

```bash
pip install -e .
```

## Usage

```bash
coding-agent "Create a Python function to calculate fibonacci numbers"
```

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/ tests/

# Type checking
mypy src/

# Lint
flake8 src/ tests/
```
