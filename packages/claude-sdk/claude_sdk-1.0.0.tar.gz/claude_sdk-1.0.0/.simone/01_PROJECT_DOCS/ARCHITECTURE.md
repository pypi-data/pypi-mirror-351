# Python Claude Code SDK: Technical Architecture

## System Overview

A simple Python library for parsing Claude Code session files (JSONL) and extracting structured data. Focus: **read existing sessions, get the data out cleanly**.

### Core Principles
- **Data Access First**: Clean, efficient access to Claude Code's JSONL data
- **Type Safety**: Pydantic models for all data structures
- **Simple API**: `parse_session(file_path)` → structured data
- **Good Defaults**: Work out of the box, minimal configuration

## Technical Stack

### Core Dependencies
- **Python**: 3.11+
- **Pydantic**: 2.x (data validation, serialization)

### Development Tools
- **Package Manager**: uv (with dependency groups)
- **Linting**: ruff (with strict rules)
- **Testing**: pytest + hypothesis
- **Type Checking**: basedpyright (strict mode)
- **Pre-commit**: Automated quality checks

## Module Architecture

```
claude_sdk/
├── __init__.py              # Public API: parse_session, discover_sessions
├── models.py                # Pydantic data models (MessageRecord, etc.)
├── parser.py                # JSONL parsing logic
├── errors.py                # Simple error hierarchy
└── utils.py                 # Common utilities
```

### Core API
```python
# Main entry point
def parse_session(file_path: Path) -> ParsedSession:
    """Parse a Claude Code JSONL file into structured data."""

# Discovery helper
def discover_sessions(claude_dir: Path = None) -> List[Path]:
    """Find all session files in ~/.claude/projects/"""
```

## Data Flow

**Simple & Direct**:
```
JSONL File → parse_session() → ParsedSession (messages, metadata, tools)
```

## Core Data Types

### MessageRecord
- Complete representation of each JSONL line
- User messages, assistant responses, tool usage
- Timestamps, costs, token counts

### ParsedSession
- Container for all session data
- Conversation threading (parent_uuid relationships)
- Aggregated metadata (total cost, tool usage counts)
- Tool executions extracted and structured

### SessionMetadata
- Total cost, message count, token usage
- Tool usage patterns
- Session duration and performance stats

## Implementation Plan

### Phase 1: Core Parser (THIS MILESTONE)
**Goal**: Parse any Claude Code JSONL file, extract structured data

**What we build**:
- Pydantic models for all JSONL record types
- SessionParser that handles real session files
- Basic error handling for malformed data
- Simple API: `parse_session(path) → ParsedSession`

**Success**: Parse real session files, get clean data out

### Phase 2: Enhanced Analysis (FUTURE)
- Tool usage correlation
- Performance analysis helpers
- Export to common formats (CSV, JSON)
- Session comparison utilities

## Performance Architecture

### Memory Management
- **Streaming Parsers**: Process large files without loading entirely into memory
- **Lazy Loading**: Load conversation trees on-demand
- **Weak References**: Prevent circular references in conversation graphs

### I/O Optimization
- **Async File Operations**: aiofiles for large file processing
- **Batch Processing**: Group operations to reduce syscall overhead
- **Connection Pooling**: Reuse subprocess connections where possible

### Caching Strategy
- **Session Metadata**: Cache parsed metadata for repeated access
- **Validation Results**: Cache Pydantic validation for identical records
- **Git State**: Cache git status between operations

## Security Architecture

### Subprocess Security
- **Command Validation**: Whitelist allowed Claude CLI arguments
- **Path Sanitization**: Validate all file paths before execution
- **Timeout Enforcement**: Prevent runaway processes
- **Resource Limits**: Memory and CPU constraints for subprocesses

### Data Validation
- **Input Sanitization**: Validate all user inputs through Pydantic
- **Schema Enforcement**: Strict schema validation for all data models
- **Error Information**: Careful error message construction (no sensitive data)

### Configuration Security
- **Environment Variables**: Secure credential management
- **File Permissions**: Appropriate permissions for session files
- **Audit Trail**: Log all execution attempts with context

## Testing Strategy

### Unit Testing
- **Data Models**: Property-based testing with Hypothesis
- **Parsers**: Test with real session files (anonymized)
- **Executors**: Mock subprocess for predictable testing
- **Error Handling**: Comprehensive error condition coverage

### Integration Testing
- **End-to-End**: Real Claude execution in test environment
- **Performance**: Benchmark large file processing
- **Compatibility**: Test across Python 3.11+ versions
- **Platform**: Cross-platform testing (Windows, macOS, Linux)

### Test Data Management
- **Fixtures**: Real anonymized session files
- **Factories**: Generate test data with realistic patterns
- **Regression**: Preserve failing cases as regression tests

## Deployment Architecture

### Package Distribution
- **PyPI**: Standard Python package distribution
- **Semantic Versioning**: Clear version compatibility guarantees
- **Type Stubs**: Include .pyi files for type checkers
- **Documentation**: Sphinx-generated API documentation

### CI/CD Pipeline
- **Type Checking**: mypy --strict on all code
- **Linting**: ruff with strict configuration
- **Testing**: pytest with coverage requirements
- **Security**: Bandit security linting
- **Performance**: Benchmark regression testing

## Error Handling Architecture

### Error Hierarchy
```python
ClaudeSDKError (base)
├── ParseError (JSONL parsing failures)
├── ExecutionError (subprocess failures)
├── ValidationError (data validation failures)
└── SessionError (session management failures)
```

### Error Context
- **Structured Logging**: JSON-formatted error logs
- **Rich Context**: Include relevant state information
- **Error Codes**: Unique codes for programmatic handling
- **Recovery Strategies**: Suggested recovery actions

### Fault Tolerance
- **Graceful Degradation**: Continue processing despite individual record failures
- **Retry Logic**: Exponential backoff for transient failures
- **Circuit Breaker**: Prevent cascade failures in batch processing

This architecture provides a solid foundation for the four implementation phases while maintaining flexibility for future enhancements and integrations with the broader Claude Code ecosystem.
