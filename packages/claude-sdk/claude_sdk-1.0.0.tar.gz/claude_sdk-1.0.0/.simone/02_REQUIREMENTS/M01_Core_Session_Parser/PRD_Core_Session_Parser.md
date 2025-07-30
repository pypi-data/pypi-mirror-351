# Product Requirements Document: Core Session Parser

## Overview

Implement the foundational session parsing functionality for the Claude SDK. This provides clean Python access to Claude Code's JSONL session files with typed data structures.

## Functional Requirements

### Core Parsing (FR-1)

- **FR-1.1**: Parse Claude Code JSONL session files from `~/.claude/projects/`
- **FR-1.2**: Handle all JSONL record types: user messages, assistant responses, tool results
- **FR-1.3**: Extract conversation threading via parent_uuid relationships
- **FR-1.4**: Aggregate session metadata: costs, token usage, tool usage counts
- **FR-1.5**: Graceful error handling for malformed/incomplete JSONL lines

### Data Models (FR-2)

- **FR-2.1**: MessageRecord model mapping directly to JSONL structure
- **FR-2.2**: Content blocks: TextBlock, ThinkingBlock, ToolUseBlock
- **FR-2.3**: ParsedSession container with messages + metadata
- **FR-2.4**: SessionMetadata with cost/usage aggregations
- **FR-2.5**: ToolExecution records extracted from tool usage

### Public API (FR-3)

- **FR-3.1**: `parse_session(file_path: Path) -> ParsedSession`
- **FR-3.2**: `discover_sessions(claude_dir: Path = None) -> List[Path]`
- **FR-3.3**: Clean imports: `from claude_sdk import parse_session, ParsedSession`
- **FR-3.4**: Type-safe API with full basedpyright compliance

## Non-Functional Requirements

- **NFR-1**: Handle session files up to 10MB efficiently
- **NFR-2**: Type safety with basedpyright strict mode (zero type: ignore)
- **NFR-3**: Memory usage < 100MB for typical session files
- **NFR-4**: Parse 1MB session file in < 2 seconds
- **NFR-5**: Robust error handling - continue parsing despite individual record failures

## Success Criteria

- [ ] Parse real Claude Code session files from user's ~/.claude directory
- [ ] Extract all message data with proper typing
- [ ] Reconstruct conversation threading accurately
- [ ] Calculate session costs and token usage correctly
- [ ] Handle error cases gracefully (corrupted JSONL, missing fields)
- [ ] Pass all type checking with basedpyright strict
- [ ] 100% test coverage on core parsing logic

## Out of Scope

- Session execution/creation (future milestone)
- Git integration (future milestone)
- MCP support (future milestone)
- Advanced analytics (M02)
- Export formats (M02)

## Dependencies

- Pydantic 2.x for data validation
- Python 3.11+ for modern typing features
- pathlib for file operations

## Testing Strategy

- Unit tests with hypothesis for data model property testing
- Integration tests with real (anonymized) session files
- Error case testing with malformed JSONL
- Performance benchmarks for large files
