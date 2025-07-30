# Product Requirements Document: Analysis Helpers

## Overview

Add analysis utilities and convenience functions to make the parsed session data useful for real workflows. This milestone focuses on practical utilities for working with session data.

## Functional Requirements

### Session Discovery (FR-1)

- **FR-1.1**: Auto-discover all session files in `~/.claude/projects/`
- **FR-1.2**: Filter sessions by date range, project, file size
- **FR-1.3**: Session metadata preview without full parsing
- **FR-1.4**: Handle nested project directory structures

### Analysis Utilities (FR-2)

- **FR-2.1**: Tool usage analysis across sessions
- **FR-2.2**: Cost/token aggregation and reporting
- **FR-2.3**: Session comparison utilities
- **FR-2.4**: Conversation flow analysis (turn counts, tool chains)
- **FR-2.5**: Performance metrics (duration, tokens/second)

### Export Functions (FR-3)

- **FR-3.1**: Export session data to JSON format
- **FR-3.2**: Export tool usage to CSV for analysis
- **FR-3.3**: Export cost reports with timestamps
- **FR-3.4**: Export conversation text (clean format)

### Batch Processing (FR-4)

- **FR-4.1**: Process multiple sessions efficiently
- **FR-4.2**: Parallel processing for large session collections
- **FR-4.3**: Progress reporting for batch operations
- **FR-4.4**: Memory-efficient streaming for large datasets

## Public API Extensions

```python
# Batch analysis
def analyze_sessions(session_paths: List[Path]) -> BatchAnalysis
def analyze_project(project_dir: Path) -> ProjectAnalysis

# Export utilities
def export_to_json(session: ParsedSession, output_path: Path) -> None
def export_tool_usage_csv(sessions: List[ParsedSession], output_path: Path) -> None

# Analysis helpers
def calculate_costs(sessions: List[ParsedSession]) -> CostReport
def extract_tool_patterns(sessions: List[ParsedSession]) -> ToolUsageReport
```

## Non-Functional Requirements

- **NFR-1**: Batch process 100+ sessions efficiently
- **NFR-2**: Memory usage scales linearly with batch size
- **NFR-3**: Export 1000+ tool records to CSV in < 5 seconds
- **NFR-4**: Progress indicators for long-running operations

## Success Criteria

- [ ] Analyze entire `~/.claude/projects/` directory efficiently
- [ ] Generate useful cost and usage reports
- [ ] Export session data in common formats
- [ ] Handle large session collections (100+ files)
- [ ] Provide clear progress feedback for batch operations

## Dependencies

- Core Session Parser (M01)
- pandas (optional, for advanced CSV export)
- concurrent.futures for parallel processing
