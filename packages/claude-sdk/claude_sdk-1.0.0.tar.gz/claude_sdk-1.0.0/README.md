# Claude SDK

> Typed Python SDK for parsing and analyzing Claude Code sessions

A clean, intuitive interface for working with Claude Code JSONL session files. Designed for CLI-based workflows, the SDK provides a simple API to access messages, analyze costs, and extract structured data from your Claude Code sessions.

## Features

- **Simple API**: `session = load("conversation.jsonl")` - that's it!
- **Session Analysis**: Easily access cost, tool usage, and performance metrics
- **Message Access**: Clean iteration through conversation messages
- **Type Safety**: Full typing with Pydantic models and basedpyright --strict
- **CLI-Friendly**: Rich docstrings with examples for `help()` discovery
- **Memory Efficient**: Optimized for large session files

## Installation

```bash
pip install claude-sdk
```

## Quick Start

```python
from claude_sdk import load, find_sessions

# Load a session from a JSONL file
session = load("conversation.jsonl")

# Access session properties
print(f"Session ID: {session.session_id}")
print(f"Total cost: ${session.total_cost:.4f}")
print(f"Tools used: {', '.join(session.tools_used)}")
print(f"Messages: {len(session.messages)}")

# Iterate through messages
for msg in session.messages:
    print(f"{msg.role}: {msg.text[:50]}...")  # Show message preview
    if msg.tools:
        print(f"  Tools: {', '.join(msg.tools)}")
    if msg.cost:
        print(f"  Cost: ${msg.cost:.4f}")

# Find all sessions in ~/.claude/projects/
session_paths = find_sessions()
print(f"Found {len(session_paths)} sessions")

# Process multiple sessions
for path in session_paths[:5]:  # First 5 sessions
    try:
        session = load(path)
        print(f"Session {session.session_id}: {len(session.messages)} messages, ${session.total_cost:.4f}")
    except Exception as e:
        print(f"Error loading {path}: {e}")
```

## Key Concepts

### Session Object

The `Session` class is your primary interface to Claude Code session data:

```python
session = load("conversation.jsonl")

# Core properties
session.session_id          # Unique session identifier
session.messages            # List of Message objects
session.total_cost          # Total session cost in USD
session.tools_used          # Set of tool names used
session.duration            # Session duration as timedelta

# Analysis properties
session.tool_costs          # Cost breakdown by tool
session.cost_by_turn        # Cost per message turn
session.tool_executions     # Detailed tool execution records
```

### Message Object

Each message in a session provides rich information:

```python
for msg in session.messages:
    msg.role                # "user" or "assistant"
    msg.text                # Full message text content
    msg.cost                # Message cost if available
    msg.is_sidechain        # True if in a sidechain
    msg.timestamp           # Message creation time
    msg.uuid                # Unique message identifier
    msg.parent_uuid         # Parent message UUID
    msg.tools               # List of tools used
```

## Tool Usage Analysis

Analyze tool patterns and costs:

```python
from claude_sdk import load

session = load("conversation.jsonl")

# Get cost breakdown by tool
for tool, cost in session.tool_costs.items():
    print(f"{tool}: ${cost:.4f} USD")

# Analyze Bash tool usage
bash_commands = []
for msg in session.messages:
    if "Bash" in msg.tools:
        bash_commands.append(msg.text)

print(f"Found {len(bash_commands)} Bash commands")
```

## Error Handling

The SDK provides a clean error hierarchy:

```python
from claude_sdk import load, ClaudeSDKError, ParseError

try:
    session = load("conversation.jsonl")
except FileNotFoundError:
    print("Session file not found!")
except ParseError as e:
    print(f"Error parsing session: {e}")
except ClaudeSDKError as e:
    print(f"General SDK error: {e}")
```

## Development

This project uses modern Python tooling:

- **uv** for fast dependency management
- **basedpyright** for strict type checking
- **ruff** for formatting and linting
- **pytest** for testing
- **just** for convenient commands

### Development Commands

```bash
# Install dependencies
just install

# Run all checks
just check

# Format code
just fmt

# Type check
just typecheck

# Run tests
just test

# Run tests with coverage
just test-cov
```

## Performance

The SDK is optimized for large session files:

- Memory-efficient streaming parser for JSONL files
- Single-pass algorithms for metadata calculation
- Efficient conversation threading reconstruction
- Handles sessions with 1000+ messages without excessive memory usage

## License

MIT License - see LICENSE file for details.
