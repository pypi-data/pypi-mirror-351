# Release Notes - Claude SDK v1.0.0

## Overview

First stable release of the Claude SDK for parsing and analyzing Claude Code sessions. This release provides a clean, intuitive API for working with Claude Code JSONL session files, with a focus on CLI-based workflows.

## Key Features

- **Simple API**: `session = load("conversation.jsonl")` - intuitive and straightforward
- **Session Analysis**: Easy access to cost, tool usage, and performance metrics
- **Message Access**: Clean iteration through conversation messages
- **Type Safety**: Full typing with Pydantic models and basedpyright --strict
- **CLI-Friendly**: Rich docstrings with examples for `help()` discovery
- **Memory Efficient**: Optimized for large session files

## Improvements

- **CLI-Friendly Error Messages**: All error messages now provide clear, actionable guidance
- **Performance Optimization**: Efficient parsing of large session files (>1MB)
- **Memory Efficiency**: Optimized algorithms for bulk session processing
- **Comprehensive Documentation**: Rich docstrings with examples
- **Production Ready**: Package configured for PyPI distribution
- **End-to-End Testing**: Validated with real-world Claude Code sessions

## Usage Example

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
```

## Installation

```bash
pip install claude-sdk
```

## License

MIT License - see LICENSE file for details.

---

Generated with Claude Code 🤖
