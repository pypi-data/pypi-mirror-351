# Claude SDK Development Commands

# Show available commands
default:
    @just --list

# Install dependencies
install:
    uv sync --dev

# Run all checks (format, lint, type check, test)
check: fmt lint typecheck test

# Format code with ruff
fmt:
    uv run ruff format .
    uv run ruff check --fix .

# Lint code with ruff
lint:
    uv run ruff check .

# Type check with basedpyright
typecheck:
    uv run basedpyright

# Run tests
test:
    uv run pytest

# Run tests with coverage
test-cov:
    uv run pytest --cov=claude_sdk --cov-report=html --cov-report=term

# Run tests with specific marker
test-mark marker:
    uv run pytest -m "{{marker}}"

# Run specific test file
test-file file:
    uv run pytest "{{file}}"

# Clean up build artifacts
clean:
    rm -rf build/
    rm -rf dist/
    rm -rf *.egg-info/
    rm -rf .coverage
    rm -rf htmlcov/
    rm -rf .pytest_cache/
    rm -rf .ruff_cache/
    find . -type d -name __pycache__ -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete

# Build package
build:
    uv build

# Install pre-commit hooks
setup-hooks:
    pre-commit install

# Run pre-commit hooks on all files
pre-commit:
    pre-commit run --all-files

# Update dependencies
update:
    uv sync --upgrade

# Show project info
info:
    @echo "Project: claude-sdk"
    @echo "Python: $(python --version)"
    @echo "uv: $(uv --version)"
    @echo "Environment: $(which python)"
    @uv run python -c "import claude_sdk; print(f'Package version: {claude_sdk.__version__}')" 2>/dev/null || echo "Package not installed"

# Development REPL with package loaded
repl:
    uv run python -c "import claude_sdk; print('claude_sdk imported successfully'); exec('import IPython; IPython.start_ipython(argv=[])')" 2>/dev/null || uv run python

# Install package in development mode
dev-install:
    uv pip install -e .

# Run example scripts
example script:
    uv run python examples/{{script}}.py
