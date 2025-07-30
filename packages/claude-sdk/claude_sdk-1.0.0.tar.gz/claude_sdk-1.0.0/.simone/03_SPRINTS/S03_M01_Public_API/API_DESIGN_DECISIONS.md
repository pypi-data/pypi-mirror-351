# API Design Decisions & Key Insights

This document captures the key decisions made during Sprint S03 planning to ensure continuity when execution begins.

## 🎯 Complete API Surface (FINAL)

### Core Functions
```python
from claude_sdk import load, find_sessions

# Primary function - load a single session
session: Session = load(path: str | Path) -> Session

# Secondary function - discover sessions
sessions: List[Path] = find_sessions(base_path: str | Path | None = None) -> List[Path]
```

### Session Object (Complete Interface)
```python
# Load session
session = load("conversation.jsonl")

# Core Properties (all read-only)
session.session_id: str                    # Session identifier
session.messages: List[Message]            # All messages (main + sidechains)
session.total_cost: float                  # Total session cost in USD
session.tools_used: Set[str]               # Set of tool names used
session.duration: timedelta | None         # Session duration
len(session.messages): int                 # Standard Python length

# Rich Analysis Properties
session.tool_costs: Dict[str, float]       # Cost breakdown by tool
session.cost_by_turn: List[float]          # Cost per message turn
session.tool_executions: List[ToolExecution]  # Detailed tool execution records
```

### Message Object Interface
```python
# Individual message access
for msg in session.messages:
    msg.role: str                          # "user" | "assistant"
    msg.text: str                          # Message text content
    msg.cost: float | None                 # Message cost if available
    msg.is_sidechain: bool                 # True if sidechain message
    msg.timestamp: datetime                # Message timestamp
    msg.uuid: UUID                         # Unique message identifier
    msg.parent_uuid: UUID | None           # Parent message UUID for threading
    msg.tools: List[str]                   # Tools used in this message
```

### Error Classes
```python
from claude_sdk import ParseError, ClaudeSDKError

# Exception hierarchy
ClaudeSDKError                             # Base exception
├── ParseError                             # File parsing errors
├── ValidationError                        # Data validation errors
└── SessionError                           # Session integrity errors
```

### Complete Import Interface
```python
# Essential imports (most common)
from claude_sdk import load, Session

# All available imports
from claude_sdk import (
    # Core functions
    load, find_sessions,

    # Main classes
    Session, Message,

    # Advanced classes (for power users)
    ToolExecution,

    # Error handling
    ParseError, ClaudeSDKError,

    # Version
    __version__
)
```

### Primary Usage Pattern
```python
from claude_sdk import load

# Simple, obvious API
session = load("conversation.jsonl")

# Session-level properties (natural and typed)
print(f"Cost: ${session.total_cost}")           # float
print(f"Tools: {session.tools_used}")           # set[str]
print(f"Duration: {session.duration}")          # timedelta
print(f"Messages: {len(session.messages)}")     # int - standard Python

# Messages are just a normal list - no magic
for msg in session.messages:                    # List[Message] - clear type
    print(f"{msg.role}: {msg.text}")
    if msg.cost: print(f"${msg.cost}")
    if msg.is_sidechain: print("(sidechain)")
```

### Key Function Naming Decisions
- ✅ `load(path)` - NOT `parse_session()` (more intuitive)
- ✅ `find_sessions(path)` - NOT `discover_sessions()` (clearer)
- ✅ `Session` - NOT `ParsedSession` (simpler)
- ✅ `Message` - NOT `MessageRecord` (cleaner)

## 🚫 Design Principles (What We Avoided)

### No Magic Behavior
- ❌ Hybrid objects that sometimes act like lists
- ❌ Special methods that confuse type checkers
- ❌ Multiple ways to access the same data

### No Complex Branching API
- ❌ `.main_chain`, `.branches`, `.sidechains` methods
- ✅ Simple filtering: `[msg for msg in session.messages if not msg.is_sidechain]`

### Keep It Obvious
- ❌ `session.count` vs `len(session)` confusion
- ✅ Standard Python: `len(session.messages)`

## 🎯 Primary User: Claude AI via CLI

### Key Insight: This Library is FOR Claude
- **Primary user**: Claude AI working via CLI tools (Bash, Read, Write, Edit)
- **Discovery method**: `help()` function, not web documentation
- **Usage pattern**: Quick analysis scripts, not web applications

### CLI-Optimized Documentation Strategy
- Rich docstrings discoverable via `help(load)`
- Working examples in `examples/` runnable with `python examples/file.py`
- Error messages actionable in CLI context
- No assumption of web UI or interactive environments

## 🔧 Branching/Threading Understanding

### What Sidechains Actually Are
- **Same conversation** with alternative exploration paths
- User changes mind: "Actually, let me see customer_data.csv instead"
- **Same sessionId**, different conversation paths from decision points
- Like git branches - same repo, different paths

### Implementation
- ✅ `message.is_sidechain` boolean property for filtering
- ✅ `parent_uuid` threading preserved in data
- ❌ No special branching API needed

## 📚 Documentation Requirements

### Docstring Standards
- Args, Returns, Raises, Examples sections
- Copy-pastable examples in docstrings
- CLI-focused usage patterns
- Immediate runnability

### Examples Structure
- `examples/basic_usage.py` - Core workflow
- `examples/tool_analysis.py` - Cost and tool analysis
- `examples/message_filtering.py` - Message iteration patterns

## 🚀 Sprint S03 Task Breakdown

### T01_S03: Public API Interface (Medium)
- Implement `load()` and `find_sessions()` functions
- Clean `__init__.py` exports
- Minimal `__all__` list
- Rich docstrings

### T02_S03: Documentation & Examples (Medium)
- Comprehensive docstrings for CLI discovery
- Working examples demonstrating clean API
- `help()` optimization

### T03_S03: Final Polish & Distribution (High)
- CLI-friendly error messages
- Performance optimization (>1MB files, >100 messages)
- PyPI packaging
- Real-world testing with `~/.claude/projects/` files

## 🔄 Execution Readiness

### Ready to Start
- ✅ API design finalized and documented
- ✅ Task breakdown complete with detailed acceptance criteria
- ✅ All dependencies met (Sprint S02 complete)
- ✅ Key insights captured for continuity

### Next Steps for New Chat
1. Start with T01_S03 (Public API Interface)
2. Review this document for context
3. Implement clean API: `session = load(path)`
4. Focus on CLI usability and type safety

## 📝 Version History
- 2025-05-29 22:30: Initial documentation of API design decisions
- Created during Sprint S03 planning session
- Captures insights for handoff to execution phase
EOF < /dev/null
