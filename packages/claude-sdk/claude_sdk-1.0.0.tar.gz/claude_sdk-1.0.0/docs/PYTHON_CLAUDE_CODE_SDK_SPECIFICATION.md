# 🐍 Python Claude Code SDK: Technical Specification

**Version**: 0.1.0-draft
**Status**: Design Phase
**Priority**: T0 - Observability Foundation

---

## **Overview**

A composable, low-level Python library providing rich abstractions over Claude Code's data model and execution capabilities. Designed for building observability systems, pattern recognition, and downstream optimization tools (DSPy integration, workflow automation, etc.).

### **Core Principles**
- **Modern Monolith**: Single package with clean module separation and clear boundaries
- **Data Access First**: Clean, efficient access to Claude Code's data structures
- **Type Safety**: Full typing with Pydantic runtime validation and mypy --strict
- **Minimal Abstractions**: Provide data types and parsers, not opinions
- **Sync-First**: Synchronous API for simplicity (async can be added later)
- **Robust Error Handling**: Sealed error hierarchy with rich context

---

## **Implementation Phases**

### **T0: Data Access Foundation** 🎯
**Goal**: Rich data model, session parsing, data extraction
- [ ] Claude Code JSONL format parsing with robust error handling
- [ ] Message threading and conversation reconstruction
- [ ] Tool usage extraction and correlation
- [ ] Performance metrics access (cost, timing, token usage)
- [ ] Raw data structures with zero interpretation
- [ ] Comprehensive type coverage with mypy --strict

### **T1: Execution Engine**
**Goal**: Programmatic Claude Code execution and session management
- [ ] Claude binary integration (`--output-format json`)
- [ ] Session configuration and management
- [ ] Synchronous subprocess execution with timeout handling
- [ ] Rich error context and recovery strategies
- [ ] Command validation and safety checks

### **T2: Git Integration** ⚠️ **RESEARCH NEEDED**
**Goal**: Correlate AI interactions with actual code changes
- [ ] Research: `GitPython` vs `pygit2` vs `dulwich`
- [ ] Git state capture (before/after execution)
- [ ] Diff analysis and file change tracking
- [ ] Commit correlation with session outcomes
- [ ] Branch/merge workflow awareness

### **T3: MCP Support** ⚠️ **LOWEST PRIORITY**
**Goal**: Model Context Protocol server integration
- [ ] MCP server configuration (JSON + Python config)
- [ ] Runtime MCP server management
- [ ] Tool permission handling
- [ ] Standard stdio MCP support

---

## **Modern Monolith Package Structure**

```
claude_sdk/
├── __init__.py              # Public API exports
├── models.py                # Pydantic data models
├── parser.py                # JSONL parsing and session reconstruction
├── executor.py              # Claude binary execution
├── errors.py                # Sealed error hierarchy
├── git.py                   # Git integration (T2)
├── mcp.py                   # MCP support (T3)
└── utils.py                 # Common utilities

tests/
├── test_models.py
├── test_parser.py
├── test_executor.py
├── fixtures/
│   └── sample_sessions/     # Real JSONL files for testing
└── conftest.py

examples/
├── basic_analysis.py
├── batch_processing.py
└── dspy_integration.py
```

---

## **Data Model Architecture**

### **Core Types**

```python
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, Union, Literal
from uuid import UUID
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, field_validator
from pydantic.types import PositiveInt, PositiveFloat

# === Session Management ===
class SessionConfig(BaseModel):
    """Configuration for Claude Code execution."""
    model_config = ConfigDict(frozen=True, extra='forbid')

    model: str = "claude-sonnet-4"
    max_turns: Optional[PositiveInt] = None
    output_format: Literal["text", "json", "stream-json"] = "json"
    allowed_tools: List[str] = Field(default_factory=list)
    disallowed_tools: List[str] = Field(default_factory=list)
    system_prompt: Optional[str] = None
    append_system_prompt: Optional[str] = None
    mcp_config: Optional[Path] = None  # T3
    permission_prompt_tool: Optional[str] = None  # T3

    @field_validator('output_format')
    @classmethod
    def validate_output_format(cls, v: str) -> str:
        if v not in {"text", "json", "stream-json"}:
            raise ValueError(f"Invalid output format: {v}")
        return v

class ClaudeSession:
    """Represents a Claude Code session with configuration and state."""

    def __init__(
        self,
        id: str,
        config: SessionConfig,
        directory: Path,
        git_context: Optional['GitContext'] = None,  # T2
    ) -> None:
        self.id = id
        self.config = config
        self.directory = directory
        self.git_context = git_context

# === Message Types (Direct mapping to Claude Code JSONL) ===
class UserType(str, Enum):
    """Type of user interaction."""
    EXTERNAL = "external"
    INTERNAL = "internal"

class MessageType(str, Enum):
    """Type of message in conversation."""
    USER = "user"
    ASSISTANT = "assistant"

class Role(str, Enum):
    """Role in conversation."""
    USER = "user"
    ASSISTANT = "assistant"

class StopReason(str, Enum):
    """Reason why message generation stopped."""
    END_TURN = "end_turn"
    MAX_TOKENS = "max_tokens"
    STOP_SEQUENCE = "stop_sequence"

class ContentBlock(BaseModel):
    """Base class for message content blocks."""
    model_config = ConfigDict(frozen=True, extra='forbid')
    type: str

class TextBlock(ContentBlock):
    """Plain text content block."""
    type: Literal["text"] = "text"
    text: str

class ThinkingBlock(ContentBlock):
    """Thinking/reasoning content block."""
    type: Literal["thinking"] = "thinking"
    thinking: str
    signature: str

class ToolUseBlock(ContentBlock):
    """Tool usage content block."""
    type: Literal["tool_use"] = "tool_use"
    id: str
    name: str
    input: Dict[str, Any]

class TokenUsage(BaseModel):
    """Token usage statistics."""
    model_config = ConfigDict(frozen=True, extra='forbid')

    input_tokens: int = Field(ge=0)
    cache_creation_input_tokens: int = Field(default=0, ge=0)
    cache_read_input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(ge=0)
    service_tier: str = "standard"

class Message(BaseModel):
    """A single message in conversation."""
    model_config = ConfigDict(frozen=True, extra='forbid')

    id: Optional[str] = None
    role: Role
    model: Optional[str] = None
    content: List[Union[TextBlock, ThinkingBlock, ToolUseBlock]]
    stop_reason: Optional[StopReason] = None
    usage: Optional[TokenUsage] = None

class MessageRecord(BaseModel):
    """Complete message record from Claude Code JSONL."""
    model_config = ConfigDict(frozen=True, extra='forbid')

    parent_uuid: Optional[UUID] = Field(default=None, alias="parentUuid")
    is_sidechain: bool = Field(alias="isSidechain")
    user_type: UserType = Field(alias="userType")
    cwd: Path
    session_id: str = Field(alias="sessionId")
    version: str
    message_type: MessageType = Field(alias="type")
    message: Message
    cost_usd: Optional[PositiveFloat] = Field(default=None, alias="costUSD")
    duration_ms: Optional[PositiveInt] = Field(default=None, alias="durationMs")
    request_id: Optional[str] = Field(default=None, alias="requestId")
    uuid: UUID
    timestamp: datetime

class ToolResult(BaseModel):
    """Result of tool execution."""
    model_config = ConfigDict(frozen=True, extra='forbid')

    tool_use_id: str
    content: str
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    interrupted: bool = False
    is_error: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)

# === Summary Records (Compacted Sessions) ===
class SummaryRecord(BaseModel):
    """Summary record for compacted conversation."""
    model_config = ConfigDict(frozen=True, extra='forbid')

    type: Literal["summary"] = "summary"
    summary: str
    leaf_uuid: UUID = Field(alias="leafUuid")
```

### **Execution Types**

```python
from dataclasses import dataclass
from datetime import timedelta

@dataclass
class ExecutionResult:
    session_id: str
    claude_output: 'ClaudeOutput'
    git_before: Optional['GitState'] = None  # T2
    git_after: Optional['GitState'] = None   # T2
    duration: timedelta
    cost_usd: float
    exit_success: bool

@dataclass
class ToolExecution:
    tool_name: str
    input: Dict[str, Any]
    output: ToolResult
    duration: timedelta
    timestamp: datetime

@dataclass
class ClaudeOutput:
    role: str
    cost_usd: float
    duration_ms: int
    duration_api_ms: int
    result: str
    session_id: str
```

---

## **Core Abstractions**

### **1. Session Builder (Composable Configuration)**

```python
class ClaudeSessionBuilder:
    def __init__(self, directory: Union[str, Path]):
        self.directory = Path(directory)
        self.config = SessionConfig()

    def with_model(self, model: str) -> 'ClaudeSessionBuilder':
        self.config.model = model
        return self

    def with_max_turns(self, turns: int) -> 'ClaudeSessionBuilder':
        self.config.max_turns = turns
        return self

    def with_system_prompt(self, prompt: str) -> 'ClaudeSessionBuilder':
        self.config.system_prompt = prompt
        return self

    def with_git_tracking(self) -> 'ClaudeSessionBuilder':  # T2
        # Implementation TBD
        return self

    def with_mcp_config(self, config: Path) -> 'ClaudeSessionBuilder':  # T3
        self.config.mcp_config = config
        return self

    async def build(self) -> ClaudeSession:
        session_id = generate_session_id()
        return ClaudeSession(
            id=session_id,
            config=self.config,
            directory=self.directory
        )
```

### **2. Data Streaming (Raw Access)**

```python
import aiofiles
from typing import AsyncIterator

class TraceStream:
    def __init__(self, session_file: Optional[Path] = None):
        self.session_file = session_file

    async def record(self, record: MessageRecord) -> None:
        if self.session_file:
            async with aiofiles.open(self.session_file, 'a') as f:
                await f.write(record.model_dump_json() + '\n')

    async def stream_records(self) -> AsyncIterator[MessageRecord]:
        if not self.session_file or not self.session_file.exists():
            return

        async with aiofiles.open(self.session_file, 'r') as f:
            async for line in f:
                if line.strip():
                    try:
                        data = json.loads(line)
                        if data.get('type') in ['user', 'assistant']:
                            yield MessageRecord.model_validate(data)
                    except (json.JSONDecodeError, ValidationError):
                        continue
```

### **3. Session Parser (JSONL Processing)**

```python
import json
from typing import List
from pydantic import ValidationError

class ConversationNode:
    def __init__(self, message: MessageRecord):
        self.message = message
        self.children: List['ConversationNode'] = []

class ConversationTree:
    def __init__(self):
        self.root_messages: List[ConversationNode] = []

class SessionMetadata:
    def __init__(self):
        self.total_cost: float = 0.0
        self.total_messages: int = 0
        self.tool_usage_count: Dict[str, int] = {}

class ParsedSession:
    def __init__(self):
        self.session_id: str = ""
        self.messages: List[MessageRecord] = []
        self.summaries: List[SummaryRecord] = []
        self.conversation_tree: ConversationTree = ConversationTree()
        self.metadata: SessionMetadata = SessionMetadata()

class SessionParser:
    def __init__(self, file_path: Union[str, Path]):
        self.file_path = Path(file_path)

    async def parse(self) -> ParsedSession:
        session = ParsedSession()

        async with aiofiles.open(self.file_path, 'r') as f:
            async for line in f:
                if not line.strip():
                    continue

                try:
                    data = json.loads(line)

                    if data.get('type') == 'summary':
                        summary = SummaryRecord.model_validate(data)
                        session.summaries.append(summary)
                    elif data.get('type') in ['user', 'assistant']:
                        message = MessageRecord.model_validate(data)
                        session.messages.append(message)
                        if not session.session_id:
                            session.session_id = message.session_id
                except (json.JSONDecodeError, ValidationError) as e:
                    # Log error but continue processing
                    continue

        session.conversation_tree = self._build_conversation_tree(session.messages)
        session.metadata = self._calculate_metadata(session.messages)
        return session

    async def stream_records(self) -> AsyncIterator[MessageRecord]:
        async with aiofiles.open(self.file_path, 'r') as f:
            async for line in f:
                if line.strip():
                    try:
                        data = json.loads(line)
                        if data.get('type') in ['user', 'assistant']:
                            yield MessageRecord.model_validate(data)
                    except (json.JSONDecodeError, ValidationError):
                        continue

    async def get_conversation_tree(self) -> ConversationTree:
        messages = []
        async for message in self.stream_records():
            messages.append(message)
        return self._build_conversation_tree(messages)

    async def extract_tool_usage(self) -> List[ToolExecution]:
        tool_executions = []
        async for message in self.stream_records():
            if message.message.role == Role.ASSISTANT:
                for block in message.message.content:
                    if isinstance(block, ToolUseBlock):
                        tool_exec = ToolExecution(
                            tool_name=block.name,
                            input=block.input,
                            output=ToolResult(tool_use_id=block.id, content=""),  # Will need to correlate with results
                            duration=timedelta(milliseconds=message.duration_ms or 0),
                            timestamp=message.timestamp
                        )
                        tool_executions.append(tool_exec)
        return tool_executions

    def _build_conversation_tree(self, messages: List[MessageRecord]) -> ConversationTree:
        # Implementation for building conversation tree from parent_uuid relationships
        tree = ConversationTree()
        nodes_by_uuid = {}

        for message in messages:
            node = ConversationNode(message)
            nodes_by_uuid[message.uuid] = node

            if message.parent_uuid is None:
                tree.root_messages.append(node)
            elif message.parent_uuid in nodes_by_uuid:
                parent_node = nodes_by_uuid[message.parent_uuid]
                parent_node.children.append(node)

        return tree

    def _calculate_metadata(self, messages: List[MessageRecord]) -> SessionMetadata:
        metadata = SessionMetadata()
        metadata.total_messages = len(messages)

        for message in messages:
            if message.cost_usd:
                metadata.total_cost += message.cost_usd

        return metadata

    @staticmethod
    async def discover_sessions(claude_dir: Path) -> List[Path]:
        """Discover all session JSONL files in ~/.claude/projects/"""
        sessions = []
        projects_dir = claude_dir / "projects"

        if projects_dir.exists():
            for project_dir in projects_dir.iterdir():
                if project_dir.is_dir():
                    for file in project_dir.glob("*.jsonl"):
                        sessions.append(file)

        return sessions
```

### **3. Claude Executor (Process Management)**

```python
# claude_sdk/executor.py
import subprocess
import json
import shutil
from typing import Optional, List, Union
from pathlib import Path
from .models import ClaudeOutput, SessionConfig
from .errors import ExecutionError, ClaudeErrorCode

class ClaudeExecutor:
    """Synchronous executor for Claude Code binary."""

    def __init__(self, claude_binary: Union[str, Path] = "claude") -> None:
        self.claude_binary = self._resolve_binary(claude_binary)
        self.config = SessionConfig()
        self.timeout_seconds = 300  # 5 minutes default

    def with_config(self, config: SessionConfig) -> 'ClaudeExecutor':
        """Set execution configuration."""
        self.config = config
        return self

    def with_timeout(self, seconds: int) -> 'ClaudeExecutor':
        """Set execution timeout."""
        if seconds <= 0:
            raise ValueError("Timeout must be positive")
        self.timeout_seconds = seconds
        return self

    def execute_prompt(
        self,
        prompt: str,
        session_id: Optional[str] = None,
        working_directory: Optional[Path] = None
    ) -> ClaudeOutput:
        """Execute a prompt with Claude Code."""
        if not prompt.strip():
            raise ExecutionError(
                "Prompt cannot be empty",
                error_code=ClaudeErrorCode.INVALID_COMMAND
            )

        cmd = self._build_command(prompt, session_id)

        try:
            result = subprocess.run(
                cmd,
                cwd=working_directory,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                check=False  # We handle return codes manually
            )

            if result.returncode != 0:
                raise ExecutionError(
                    f"Claude execution failed with exit code {result.returncode}",
                    exit_code=result.returncode,
                    stderr=result.stderr,
                    command=cmd
                )

            # Parse JSON output if format is json
            if self.config.output_format == "json":
                try:
                    output_data = json.loads(result.stdout)
                    return ClaudeOutput.model_validate(output_data)
                except json.JSONDecodeError as e:
                    raise ExecutionError(
                        f"Failed to parse Claude output as JSON: {e}",
                        error_code=ClaudeErrorCode.INVALID_JSON,
                        cause=e
                    )
            else:
                # For text output, create a simple ClaudeOutput
                return ClaudeOutput(
                    role="assistant",
                    cost_usd=0.0,  # Not available in text mode
                    duration_ms=0,
                    duration_api_ms=0,
                    result=result.stdout,
                    session_id=session_id or "unknown"
                )

        except subprocess.TimeoutExpired:
            raise ExecutionError(
                f"Claude execution timed out after {self.timeout_seconds} seconds",
                error_code=ClaudeErrorCode.TIMEOUT,
                command=cmd
            )
        except FileNotFoundError:
            raise ExecutionError(
                f"Claude binary not found: {self.claude_binary}",
                error_code=ClaudeErrorCode.CLAUDE_NOT_FOUND,
                context={"binary_path": str(self.claude_binary)}
            )

    def resume_session(self, session_id: str, working_directory: Optional[Path] = None) -> ClaudeOutput:
        """Resume an existing session."""
        cmd = [str(self.claude_binary), "--session", session_id, "--continue"]
        cmd.extend(self._get_config_args())

        return self._execute_command(cmd, working_directory)

    def continue_latest_session(self, working_directory: Optional[Path] = None) -> ClaudeOutput:
        """Continue the latest session."""
        cmd = [str(self.claude_binary), "--continue-latest"]
        cmd.extend(self._get_config_args())

        return self._execute_command(cmd, working_directory)

    def _resolve_binary(self, claude_binary: Union[str, Path]) -> Path:
        """Resolve Claude binary path."""
        if isinstance(claude_binary, Path):
            if claude_binary.exists():
                return claude_binary
        else:
            # Try to find in PATH
            found = shutil.which(claude_binary)
            if found:
                return Path(found)

        raise ExecutionError(
            f"Claude binary not found: {claude_binary}",
            error_code=ClaudeErrorCode.CLAUDE_NOT_FOUND,
            context={"binary_path": str(claude_binary)}
        )

    def _build_command(self, prompt: str, session_id: Optional[str] = None) -> List[str]:
        """Build command line arguments."""
        cmd = [str(self.claude_binary)]

        if session_id:
            cmd.extend(["--session", session_id])

        cmd.extend([
            "--output-format", self.config.output_format,
            "--model", self.config.model,
            "--prompt", prompt
        ])

        cmd.extend(self._get_config_args())
        return cmd

    def _get_config_args(self) -> List[str]:
        """Get configuration arguments."""
        args = []

        if self.config.max_turns:
            args.extend(["--max-turns", str(self.config.max_turns)])

        if self.config.system_prompt:
            args.extend(["--system-prompt", self.config.system_prompt])

        if self.config.append_system_prompt:
            args.extend(["--append-system-prompt", self.config.append_system_prompt])

        for tool in self.config.allowed_tools:
            args.extend(["--allowed-tool", tool])

        for tool in self.config.disallowed_tools:
            args.extend(["--disallowed-tool", tool])

        if self.config.mcp_config:
            args.extend(["--mcp-config", str(self.config.mcp_config)])

        return args

    def _execute_command(self, cmd: List[str], working_directory: Optional[Path]) -> ClaudeOutput:
        """Execute a command and return parsed output."""
        # Similar implementation to execute_prompt but for pre-built commands
        # Implementation details similar to execute_prompt method
        pass
```

---

## **Public API Design**

```python
# claude_sdk/__init__.py
"""Claude Code SDK - Typed Python wrapper for Claude Code CLI."""

__version__ = "0.1.0"

# Core exports
from .models import (
    SessionConfig,
    ClaudeSession,
    MessageRecord,
    SummaryRecord,
    ToolExecution,
    ClaudeOutput,
    ExecutionResult,
    # Content types
    TextBlock,
    ThinkingBlock,
    ToolUseBlock,
    # Enums
    Role,
    MessageType,
    StopReason,
    UserType,
)

from .parser import (
    SessionParser,
    ParsedSession,
    ConversationTree,
    ConversationNode,
    SessionMetadata,
)

from .executor import ClaudeExecutor
from .errors import (
    ClaudeSDKError,
    ParseError,
    ExecutionError,
    SessionError,
    ClaudeErrorCode,
)

# Builder pattern
from .parser import ClaudeSessionBuilder

# Convenience functions
def parse_session(file_path: Union[str, Path]) -> ParsedSession:
    """Parse a Claude Code session file."""
    parser = SessionParser(file_path)
    return parser.parse()

def discover_sessions(claude_dir: Optional[Path] = None) -> List[Path]:
    """Discover all session files in Claude directory."""
    if claude_dir is None:
        claude_dir = Path.home() / ".claude"
    return SessionParser.discover_sessions(claude_dir)

def execute_prompt(prompt: str, **kwargs) -> ClaudeOutput:
    """Execute a prompt with default configuration."""
    executor = ClaudeExecutor()
    return executor.execute_prompt(prompt, **kwargs)

# Type exports for static analysis
__all__ = [
    # Version
    "__version__",
    # Core models
    "SessionConfig",
    "ClaudeSession",
    "MessageRecord",
    "SummaryRecord",
    "ToolExecution",
    "ClaudeOutput",
    "ExecutionResult",
    # Content types
    "TextBlock",
    "ThinkingBlock",
    "ToolUseBlock",
    # Enums
    "Role",
    "MessageType",
    "StopReason",
    "UserType",
    # Parser
    "SessionParser",
    "ParsedSession",
    "ConversationTree",
    "ConversationNode",
    "SessionMetadata",
    # Executor
    "ClaudeExecutor",
    # Errors
    "ClaudeSDKError",
    "ParseError",
    "ExecutionError",
    "SessionError",
    "ClaudeErrorCode",
    # Builder
    "ClaudeSessionBuilder",
    # Convenience functions
    "parse_session",
    "discover_sessions",
    "execute_prompt",
]
```

---

## **Usage Examples**

### **Basic Session Analysis**
```python
from claude_sdk import parse_session, discover_sessions
from pathlib import Path

def main() -> None:
    # Parse existing session
    session = parse_session("~/.claude/projects/my-project/session.jsonl")

    print(f"Session: {session.session_id}")
    print(f"Total messages: {len(session.messages)}")
    print(f"Total cost: ${session.metadata.total_cost:.4f}")
    print(f"Input tokens: {session.metadata.total_input_tokens}")
    print(f"Output tokens: {session.metadata.total_output_tokens}")

    # Tool usage analysis
    print("\nTool usage:")
    for tool_name, count in session.metadata.tool_usage_count.items():
        print(f"  {tool_name}: {count} times")

if __name__ == "__main__":
    main()
```

### **Live Session Execution**
```python
from claude_sdk import ClaudeExecutor, SessionConfig
from pathlib import Path

def main() -> None:
    # Configure and execute
    config = SessionConfig(
        model="claude-sonnet-4",
        max_turns=10,
        output_format="json"
    )

    executor = ClaudeExecutor().with_config(config).with_timeout(120)

    try:
        result = executor.execute_prompt(
            "Analyze the code in this directory and suggest improvements",
            working_directory=Path("/path/to/project")
        )

        print(f"Cost: ${result.cost_usd:.4f}")
        print(f"Duration: {result.duration_ms}ms")
        print(f"Result: {result.result[:200]}...")

    except ExecutionError as e:
        print(f"Execution failed: {e}")
        print(f"Error code: {e.error_code}")
        if e.context:
            print(f"Context: {e.context}")

if __name__ == "__main__":
    main()
```

### **Batch Data Access**
```python
from claude_sdk import discover_sessions, SessionParser
from pathlib import Path
from typing import Dict, List

def analyze_all_sessions() -> None:
    """Analyze all Claude sessions for usage patterns."""
    claude_dir = Path.home() / ".claude"
    session_paths = discover_sessions(claude_dir)

    total_cost = 0.0
    total_messages = 0
    total_sessions = 0
    tool_usage: Dict[str, int] = {}

    print(f"Found {len(session_paths)} session files")

    for session_path in session_paths:
        try:
            parser = SessionParser(session_path)
            session = parser.parse()

            total_cost += session.metadata.total_cost
            total_messages += len(session.messages)
            total_sessions += 1

            # Aggregate tool usage
            for tool, count in session.metadata.tool_usage_count.items():
                tool_usage[tool] = tool_usage.get(tool, 0) + count

        except ParseError as e:
            print(f"Failed to parse {session_path}: {e}")
            continue

    print(f"\n=== Summary ===")
    print(f"Total sessions: {total_sessions}")
    print(f"Total cost: ${total_cost:.2f}")
    print(f"Total messages: {total_messages}")
    print(f"Average cost per session: ${total_cost/total_sessions:.4f}")

    print(f"\n=== Most Used Tools ===")
    sorted_tools = sorted(tool_usage.items(), key=lambda x: x[1], reverse=True)
    for tool, count in sorted_tools[:10]:
        print(f"  {tool}: {count} uses")

if __name__ == "__main__":
    analyze_all_sessions()
```

### **DSPy Integration Example**
```python
from claude_sdk import SessionParser, ToolExecution
from typing import List, Dict, Any

def extract_dspy_traces(session_path: str) -> List[Dict[str, Any]]:
    """Extract DSPy-compatible traces from Claude session."""
    parser = SessionParser(session_path)
    session = parser.parse()

    traces = []

    for message in session.messages:
        # Convert to DSPy trace format
        trace = {
            "timestamp": message.timestamp.isoformat(),
            "role": message.message.role.value,
            "content": [block.model_dump() for block in message.message.content],
            "cost_usd": message.cost_usd or 0.0,
            "duration_ms": message.duration_ms or 0,
            "session_id": message.session_id,
            "uuid": str(message.uuid),
            "parent_uuid": str(message.parent_uuid) if message.parent_uuid else None,
        }

        if message.message.usage:
            trace["token_usage"] = message.message.usage.model_dump()

        traces.append(trace)

    return traces

def main() -> None:
    traces = extract_dspy_traces("~/.claude/projects/my-project/session.jsonl")
    print(f"Extracted {len(traces)} traces for DSPy analysis")

    # TODO: Feed into DSPy SIMBA optimizer
    # optimizer = dspy.SIMBA(traces=traces)
    # optimized_strategy = optimizer.optimize()

if __name__ == "__main__":
    main()
```

---

## **Dependencies & Project Setup**

### **pyproject.toml (uv-compatible)**
```toml
[project]
name = "claude-sdk"
version = "0.1.0"
description = "Typed Python wrapper for Claude Code CLI"
authors = [{name = "Your Name", email = "your.email@example.com"}]
readme = "README.md"
requires-python = ">=3.11"
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Typing :: Typed",
]

dependencies = [
    "pydantic>=2.0,<3.0",
]

[project.optional-dependencies]
# T2: Git integration
git = ["GitPython>=3.1.0"]
# T3: MCP support
mcp = ["mcp-sdk>=0.1.0"]
# Development dependencies
dev = [
    "mypy>=1.8.0",
    "ruff>=0.1.0",
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "hypothesis>=6.0.0",
    "types-python-dateutil",
]
# All optional dependencies
all = ["claude-sdk[git,mcp,dev]"]

[project.urls]
Homepage = "https://github.com/your-username/claude-sdk"
Repository = "https://github.com/your-username/claude-sdk"
Issues = "https://github.com/your-username/claude-sdk/issues"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
dev-dependencies = [
    "mypy>=1.8.0",
    "ruff>=0.1.0",
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "hypothesis>=6.0.0",
    "types-python-dateutil",
]

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true

[tool.ruff]
target-version = "py311"
line-length = 100

[tool.ruff.lint]
select = [
    "E",  # pycodestyle errors
    "W",  # pycodestyle warnings
    "F",  # pyflakes
    "I",  # isort
    "B",  # flake8-bugbear
    "C4", # flake8-comprehensions
    "UP", # pyupgrade
    "RUF", # Ruff-specific rules
]
ignore = [
    "E501",  # line too long, handled by formatter
    "B008",  # do not perform function calls in argument defaults
]

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]  # Allow unused imports in __init__.py
"tests/**/*.py" = [
    "S101",  # Allow assert statements in tests
    "ARG",   # Allow unused function args in tests
    "FBT",   # Allow boolean trap in tests
]

[tool.pytest.ini_options]
minversion = "7.0"
addopts = "-ra -q --strict-markers --strict-config"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
markers = [
    "slow: marks tests as slow (deselect with '-m "not slow"')",
    "integration: marks tests as integration tests",
]

[tool.coverage.run]
source = ["claude_sdk"]
omit = ["tests/*"]
branch = true

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if self.debug:",
    "if settings.DEBUG",
    "raise AssertionError",
    "raise NotImplementedError",
    "if 0:",
    "if __name__ == .__main__.:",
    "class .*\bProtocol\):",
    "@(abc\.)?abstractmethod",
]
show_missing = true
skip_covered = true
```

---

## **Success Criteria**

### **T0 Success Metrics**
- [ ] Parse any Claude Code JSONL session file without errors
- [ ] Reconstruct conversation threading perfectly
- [ ] Extract tool usage patterns with 100% accuracy
- [ ] Handle large session files (>1MB) efficiently
- [ ] Type safety with mypy --strict (zero Any types in public API)
- [ ] Comprehensive error handling with structured error codes
- [ ] Memory-efficient streaming for large files

### **T1 Success Metrics**
- [ ] Execute Claude Code programmatically with all configuration options
- [ ] Capture execution results with rich metadata
- [ ] Robust subprocess handling with timeout and error recovery
- [ ] Command validation and safety checks
- [ ] Handle all Claude Code error conditions gracefully

### **T2 Success Metrics** (Git Integration)
- [ ] Capture git state before/after Claude execution
- [ ] Correlate file changes with AI interactions
- [ ] Generate meaningful diff analysis
- [ ] Support complex git workflows (branches, merges)

### **T3 Success Metrics** (MCP)
- [ ] Configure MCP servers programmatically
- [ ] Manage MCP server lifecycle
- [ ] Handle MCP tool permissions properly
- [ ] Runtime validation of MCP configurations

---

## **Development Workflow**

### **Initial Setup**
```bash
# Clone or create project
git clone <repo> claude-sdk
cd claude-sdk

# Setup with uv
uv venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uv pip install -e ".[dev]"

# Run type checking
mypy claude_sdk/

# Run linting
ruff check claude_sdk/
ruff format claude_sdk/

# Run tests
pytest
```

### **Next Steps**

1. **Create modern monolith project structure**
2. **Implement T0: Core data models with Pydantic**
3. **Add JSONL parsing with robust error handling**
4. **Create comprehensive test suite with real session data**
5. **Add type checking and linting CI**
6. **Implement T1: Synchronous Claude executor**
7. **Add DSPy integration examples**

---

*This specification serves as the foundational design document for the Python Claude Code SDK. It prioritizes observability and composability while maintaining type safety, robust error handling, and sync-first simplicity.*
