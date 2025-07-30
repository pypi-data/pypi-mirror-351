"""Claude Code SDK - Typed Python wrapper for Claude Code CLI sessions.

This SDK provides a clean, intuitive interface for parsing and analyzing Claude Code
JSONL session files. It allows you to load session data, access messages, and analyze
costs, tool usage, and conversation patterns.

Basic usage:
```python
from claude_sdk import load, Session

# Load a session from a JSONL file
session = load("conversation.jsonl")

# Access session properties
print(f"Session ID: {session.session_id}")
print(f"Total cost: ${session.total_cost:.4f}")
print(f"Tools used: {session.tools_used}")
print(f"Messages: {len(session.messages)}")

# Iterate through messages
for msg in session.messages:
    print(f"{msg.role}: {msg.text}")
    if msg.cost:
        print(f"Cost: ${msg.cost:.4f}")
```

Finding session files:
```python
from claude_sdk import find_sessions

# Find all sessions in ~/.claude/projects/
session_paths = find_sessions()

# Find sessions in a specific directory
session_paths = find_sessions("/path/to/sessions")

# Load and analyze all sessions
for path in session_paths:
    session = load(path)
    print(f"Session {session.session_id}: ${session.total_cost:.4f} USD")
```

Error handling:
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

Common tool and cost analysis:
```python
from claude_sdk import load

session = load("conversation.jsonl")

# Analyze tool usage
print(f"Tools used: {', '.join(session.tools_used)}")
for tool, cost in session.tool_costs.items():
    print(f"{tool}: ${cost:.4f} USD")

# Find messages using specific tools
for msg in session.messages:
    if "Bash" in msg.tools:
        print(f"Bash command: {msg.text}")
```
"""

from pathlib import Path

from .errors import ClaudeSDKError, ParseError
from .message import Message
from .models import Role, SessionMetadata, TextBlock, ThinkingBlock, ToolExecution, ToolUseBlock
from .parser import discover_sessions, parse_complete_session
from .session import Session

__version__ = "1.0.0"


def load(file_path: str | Path) -> Session:
    """Load a Claude Code session from a JSONL file.

    This function parses a Claude Code session file and returns a Session object
    with all messages, metadata, and tool usage information. It handles all the
    complexity of parsing JSONL records, reconstructing the conversation threading,
    and calculating session statistics.

    Args:
        file_path: Path to the JSONL session file (can be string or Path object)
                  This is typically a .jsonl file in ~/.claude/projects/

    Returns:
        Session: Complete session object with the following key properties:
                - session_id: Unique identifier for the session
                - messages: List of Message objects in conversation order
                - total_cost: Total cost of the session in USD
                - tools_used: Set of tool names used in the session
                - duration: Total duration of the session
                - tool_costs: Dictionary mapping tools to their costs
                - cost_by_turn: List of costs per message turn

    Raises:
        ParseError: If the file cannot be parsed due to invalid format or corruption
        FileNotFoundError: If the specified file does not exist
        ClaudeSDKError: Base class for all SDK-specific exceptions
        ValueError: If the file contains invalid or incomplete data

    Example:
        ```python
        from claude_sdk import load

        # Basic usage
        session = load("conversation.jsonl")
        print(f"Session ID: {session.session_id}")
        print(f"Total cost: ${session.total_cost:.4f}")
        print(f"Tools used: {', '.join(session.tools_used)}")

        # Analyze message patterns
        for msg in session.messages:
            print(f"{msg.role}: {msg.text[:50]}...")  # Show message preview
            if msg.tools:
                print(f"  Tools: {', '.join(msg.tools)}")
            if msg.cost:
                print(f"  Cost: ${msg.cost:.4f}")

        # Error handling example
        try:
            session = load("possibly_corrupted.jsonl")
        except ParseError as e:
            print(f"Could not parse file: {e}")
        except FileNotFoundError:
            print("Session file not found!")
        ```

    CLI Usage:
        In Claude Code CLI context, you'll typically use this to load session files:
        ```python
        from claude_sdk import load
        from pathlib import Path

        # For a file you can see in ls output
        session = load("/path/to/your/session.jsonl")

        # With paths from find_sessions()
        session_paths = find_sessions()
        if session_paths:
            session = load(session_paths[0])
        ```
    """
    # Convert string path to Path object if needed
    if isinstance(file_path, str):
        file_path = Path(file_path)

    # Parse the session using the internal function
    parsed_session = parse_complete_session(file_path)

    # Convert to the public Session class
    return Session.from_parsed_session(parsed_session)


def find_sessions(base_path: str | Path | None = None) -> list[Path]:
    """Find Claude Code session files in a directory.

    This function discovers all Claude Code JSONL session files in the specified
    directory or in the default ~/.claude/projects/ directory. It identifies valid
    Claude Code session files by their .jsonl extension and content structure.

    Args:
        base_path: Directory to search for session files. If not provided,
                   defaults to ~/.claude/projects/. Can be a string path or
                   a Path object.

    Returns:
        List[Path]: List of paths to JSONL session files, sorted by modification
                    time (most recent first). The paths are absolute and can be
                    directly passed to the load() function.

    Raises:
        ParseError: If the directory doesn't exist or can't be accessed
        FileNotFoundError: If the specified directory does not exist
        PermissionError: If the directory can't be accessed due to permissions

    Example:
        ```python
        from claude_sdk import find_sessions, load

        # Basic usage - find all sessions in default directory (~/.claude/projects/)
        session_paths = find_sessions()
        print(f"Found {len(session_paths)} sessions")

        # Find sessions in a specific directory
        session_paths = find_sessions("/path/to/sessions")

        # Load the most recent session
        if session_paths:
            latest_session = load(session_paths[0])  # First is most recent
            print(f"Latest session: {latest_session.session_id}")
            print(f"Session date: {latest_session.messages[0].timestamp}")

        # Process all sessions in a directory
        for path in session_paths:
            try:
                session = load(path)
                print(f"Session {session.session_id}: {len(session.messages)} messages")
            except ParseError:
                print(f"Could not parse {path}")
        ```

    CLI Usage:
        In Claude Code CLI context, you'll typically use this to find sessions:
        ```python
        from claude_sdk import find_sessions

        # List recent sessions
        paths = find_sessions()
        for i, path in enumerate(paths[:5]):  # Show 5 most recent
            print(f"{i+1}. {path.name}")

        # Find sessions in specific project directory
        proj_dir = "/Users/username/.claude/projects/my_project"
        proj_sessions = find_sessions(proj_dir)
        ```

    Performance Notes:
        - For large directories with many files, this function is optimized to
          scan quickly using efficient directory traversal.
        - Memory usage is minimized by using generators and lazy evaluation
          for file discovery.
        - The results are cached in memory, so subsequent calls with the same
          base_path will be faster.
    """
    # Convert string path to Path object if needed
    if base_path is not None and isinstance(base_path, str):
        base_path = Path(base_path)

    # Use the internal discover_sessions function
    return discover_sessions(base_path)


# Type exports for static analysis
__all__ = [
    # Error handling
    "ClaudeSDKError",
    "Message",
    "ParseError",
    # Common model types
    "Role",
    # Main classes
    "Session",
    "SessionMetadata",
    "TextBlock",
    "ThinkingBlock",
    "ToolExecution",
    "ToolUseBlock",
    # Version
    "__version__",
    "find_sessions",
    # Core functions
    "load",
]
