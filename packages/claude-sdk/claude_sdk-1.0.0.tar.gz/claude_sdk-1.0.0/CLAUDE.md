# Claude Code Development Guide

This file contains comprehensive instructions for Claude Code when working on this Python SDK project. It covers all tools, commands, and workflows to ensure optimal productivity.

## Project Overview

This is a Python SDK for parsing Claude Code session files (JSONL format) using Pydantic models with strict type safety.

- **Language**: Python 3.11+
- **Package Manager**: `uv` (NOT `python` or `pip`)
- **Type Checker**: `basedpyright` (NOT `mypy`)
- **Formatter/Linter**: `ruff`
- **Test Framework**: `pytest`
- **Build Tool**: `just` (task runner)

## Critical Command Rules

### ❌ NEVER USE THESE:
- `python` (command not found in this environment)
- `pip install`
- `mypy`
- `black` or `isort` (use ruff instead)

### ✅ ALWAYS USE THESE:
- `uv run <command>` for running Python tools
- `just <task>` for development tasks
- `basedpyright` for type checking
- `ruff` for formatting and linting

## Essential Commands

### Package Management
```bash
# Install all dependencies (run this first!)
just install

# Update dependencies
just update

# Install development dependencies
uv sync --dev
```

### Development Workflow
```bash
# Format code and fix linting issues
just fmt

# Run linting only (without fixing)
just lint

# Type check with basedpyright
just typecheck

# Run all tests
just test

# Run tests with coverage
just test-cov

# Run all checks (format, lint, typecheck, test)
just check
```

### Running Tests
```bash
# All tests
uv run pytest

# With coverage
uv run pytest --cov=claude_sdk --cov-report=html --cov-report=term

# Specific test file
uv run pytest tests/unit/test_models.py

# Specific test marker
uv run pytest -m "not slow"

# Verbose output
uv run pytest -v
```

### Type Checking
```bash
# Check all source files
uv run basedpyright

# Check specific file
uv run basedpyright src/claude_sdk/models.py

# Check with extra strictness
uv run basedpyright --strict
```

### Code Quality
```bash
# Format all files
uv run ruff format .

# Fix linting issues
uv run ruff check --fix .

# Check without fixing
uv run ruff check .

# Format specific file
uv run ruff format src/claude_sdk/models.py
```

### Project Information
```bash
# Show project info
just info

# List all available tasks
just --list

# Clean build artifacts
just clean

# Build package
just build
```

## File Structure Understanding

```
.
├── src/claude_sdk/          # Main package source
│   ├── __init__.py         # Package initialization
│   ├── models.py           # Pydantic data models
│   ├── parser.py           # JSONL parsing logic
│   ├── errors.py           # Error hierarchy
│   ├── executor.py         # Execution utilities
│   ├── utils.py            # Utility functions
│   └── py.typed            # Type marker file
├── tests/                  # Test suite
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── fixtures/           # Test data
├── docs/                   # Documentation
├── examples/               # Usage examples
├── .simone/                # Simone project management
├── pyproject.toml          # Project configuration
├── justfile                # Task definitions
├── .pre-commit-config.yaml # Pre-commit hooks
└── .python-version         # Python version
```

## Development Workflow

### 1. Starting Work
```bash
cd /Users/darin/.claude/py_sdk
just install                # Install dependencies
just check                  # Verify everything works
```

### 2. Making Changes
```bash
# Edit files...
just fmt                    # Format and fix linting
just test                   # Run tests
just typecheck              # Check types
```

### 3. Before Committing
```bash
just check                  # Run all quality checks
# Should show: "All checks passed!"
```

### 4. Full Quality Check
```bash
just fmt && just lint && just typecheck && just test-cov
```

## Configuration Details

### pyproject.toml Key Settings
- **Python Version**: >=3.11
- **Dependencies**: pydantic>=2.11.5
- **Dev Tools**: basedpyright, ruff, pytest, hypothesis
- **Type Checking**: Strict mode with comprehensive checks
- **Coverage**: HTML and terminal reporting

### basedpyright Configuration
- **Mode**: Strict type checking
- **Target**: Python 3.11
- **Include**: `src/` directory only
- **Reports**: All type safety violations

### ruff Configuration
- **Target**: Python 3.11
- **Line Length**: 100 characters
- **Enabled**: E, W, F, I, B, C4, UP, RUF, SIM, TCH, PTH
- **Auto-fix**: Available for most issues

## Simone Project Management

This project uses the Simone framework for task management:

```bash
# Current status
cat .simone/00_PROJECT_MANIFEST.md

# Current sprint
ls .simone/03_SPRINTS/S01_M01_Data_Models/

# Task documentation
find .simone -name "T*_S*" -type f
```

## Troubleshooting

### Common Issues

1. **`python: command not found`**
   - Solution: Use `uv run python` instead of `python`

2. **Import errors in tests**
   - Solution: Run `just install` to install dependencies

3. **Type checking failures**
   - Solution: Run `just typecheck` to see specific issues
   - Use `uv run basedpyright <file>` for specific files

4. **Linting failures**
   - Solution: Run `just fmt` to auto-fix most issues

5. **Test failures**
   - Solution: Run `uv run pytest -v` for verbose output

### Quality Standards

- **Type Safety**: 0 errors, 0 warnings with basedpyright
- **Test Coverage**: 100% on all production code
- **Linting**: All ruff checks must pass
- **Formatting**: Consistent with ruff format

## Example Workflows

### Adding a New Model
```bash
# 1. Edit the model file
vim src/claude_sdk/models.py

# 2. Add tests
vim tests/unit/test_models.py

# 3. Check quality
just check

# 4. If issues, fix them
just fmt                    # Fix formatting
uv run basedpyright        # Check types
uv run pytest -v          # Verify tests
```

### Running Specific Tests
```bash
# Test specific class
uv run pytest tests/unit/test_models.py::TestUserType

# Test specific method
uv run pytest tests/unit/test_models.py::TestUserType::test_enum_values

# Test with coverage
uv run pytest tests/unit/test_models.py --cov=claude_sdk.models
```

### Checking Type Safety
```bash
# Check specific model
uv run basedpyright src/claude_sdk/models.py

# Check all with verbose output
uv run basedpyright --verbose

# Check with stats
uv run basedpyright --stats
```

This guide ensures consistent, high-quality development practices throughout the project.
