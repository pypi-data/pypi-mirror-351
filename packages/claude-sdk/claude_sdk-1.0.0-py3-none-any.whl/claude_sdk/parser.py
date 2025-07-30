"""JSONL parsing and session reconstruction for Claude Code SDK."""

import json
import logging
from collections.abc import Iterator
from pathlib import Path

from pydantic import ValidationError

from .errors import ParseError
from .models import MessageRecord, ParsedSession

logger = logging.getLogger(__name__)


def discover_sessions(base_path: Path | None = None) -> list[Path]:
    """Discover Claude Code session files in the user's projects directory.

    Args:
        base_path: Base directory to search. Defaults to ~/.claude/projects/

    Returns:
        List of paths to JSONL session files

    Raises:
        ParseError: If base directory doesn't exist or isn't accessible
    """
    if base_path is None:
        base_path = Path.home() / ".claude" / "projects"

    if not base_path.exists():
        raise ParseError(
            f"Projects directory not found: {base_path}. Please verify the directory exists or specify a different path."
        )

    if not base_path.is_dir():
        raise ParseError(
            f"Projects path is not a directory: {base_path}. Please specify a valid directory path."
        )

    try:
        # Find all .jsonl files recursively
        session_files = list(base_path.rglob("*.jsonl"))
        logger.info(f"Found {len(session_files)} JSONL files in {base_path}")
        return session_files
    except (OSError, PermissionError) as e:
        raise ParseError(
            f"Failed to access projects directory {base_path}: {e}. Check permissions and try again."
        ) from e


def parse_jsonl_file(file_path: Path) -> Iterator[MessageRecord]:
    """Parse a JSONL file line-by-line into MessageRecord objects.

    This function uses a memory-efficient streaming approach to process even large session
    files without loading the entire file into memory. Invalid lines are logged and skipped.

    Args:
        file_path: Path to the JSONL file to parse

    Yields:
        MessageRecord objects for each valid line

    Raises:
        ParseError: If file cannot be opened or read
    """
    if not file_path.exists():
        raise ParseError(
            f"Session file not found: {file_path}. Please check that the file exists and the path is correct."
        )

    if not file_path.is_file():
        raise ParseError(
            f"Session path is not a file: {file_path}. Please provide a path to a valid JSONL file."
        )

    try:
        with file_path.open("r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue  # Skip empty lines

                try:
                    # Parse JSON line
                    json_data = json.loads(line)

                    # Convert to MessageRecord using Pydantic
                    message_record = MessageRecord.model_validate(json_data)
                    yield message_record

                except json.JSONDecodeError as e:
                    logger.warning(f"Invalid JSON at {file_path}:{line_num}: {e}")
                    # Record more specific error information
                    logger.debug(f"Problematic line content: {line[:100]}...")
                    continue  # Skip malformed JSON lines

                except ValidationError as e:
                    # Convert Pydantic validation error to our custom error with better message
                    logger.warning(f"Data validation error at {file_path}:{line_num}: {e}")
                    # Extract field names for better debugging
                    error_fields = [str(err["loc"][0]) for err in e.errors()]
                    logger.debug(f"Invalid fields: {', '.join(error_fields)}")
                    continue  # Skip lines that don't match MessageRecord schema

                except Exception as e:
                    logger.error(f"Unexpected error at {file_path}:{line_num}: {e}")
                    continue  # Continue processing despite unexpected errors

    except (OSError, PermissionError) as e:
        # Provide actionable error message based on error type
        if isinstance(e, PermissionError):
            raise ParseError(
                f"Permission denied when reading {file_path}: {e}. "
                f"Check file permissions and try again."
            ) from e
        else:
            raise ParseError(
                f"Failed to read session file {file_path}: {e}. "
                f"Verify the file is accessible and not corrupted."
            ) from e


def parse_session_file(file_path: Path) -> list[MessageRecord]:
    """Parse a complete JSONL session file into a list of MessageRecord objects.

    This function optimizes memory usage for large files by using a streaming parser
    and only materializing the list at the end of processing.

    Args:
        file_path: Path to the JSONL session file

    Returns:
        List of MessageRecord objects from the session

    Raises:
        ParseError: If file cannot be parsed
    """
    try:
        records = list(parse_jsonl_file(file_path))
        logger.info(f"Successfully parsed {len(records)} records from {file_path}")
        return records
    except ParseError:
        raise  # Re-raise ParseError as-is
    except Exception as e:
        # Provide more context and suggestions in the error message
        raise ParseError(
            f"Failed to parse session file {file_path}: {e}. "
            f"The file may be corrupted or in an unexpected format. "
            f"Try running 'just check' to validate your environment."
        ) from e


class SessionParser:
    """High-level parser for Claude Code session files.

    Provides methods for discovering and parsing JSONL session files
    with comprehensive error handling and logging.
    """

    def __init__(self, base_path: Path | None = None):
        """Initialize the session parser.

        Args:
            base_path: Base directory for session discovery. Defaults to ~/.claude/projects/
        """
        self.base_path = base_path or Path.home() / ".claude" / "projects"

    def discover_sessions(self) -> list[Path]:
        """Discover all JSONL session files in the base path.

        Returns:
            List of paths to discovered session files
        """
        return discover_sessions(self.base_path)

    def parse_session(self, file_path: Path) -> list[MessageRecord]:
        """Parse a single JSONL session file.

        Args:
            file_path: Path to the session file

        Returns:
            List of MessageRecord objects from the session
        """
        return parse_session_file(file_path)

    def parse_all_sessions(self) -> dict[Path, list[MessageRecord]]:
        """Parse all discovered session files.

        Returns:
            Dictionary mapping file paths to lists of MessageRecord objects
        """
        session_files = self.discover_sessions()
        results: dict[Path, list[MessageRecord]] = {}

        for file_path in session_files:
            try:
                records = self.parse_session(file_path)
                results[file_path] = records
            except ParseError as e:
                logger.error(f"Failed to parse {file_path}: {e}")
                results[file_path] = []  # Empty list for failed sessions

        return results

    def parse_complete_session(self, file_path: Path) -> ParsedSession:
        """Parse a single JSONL session file into a complete ParsedSession.

        Args:
            file_path: Path to the session file

        Returns:
            ParsedSession: Complete session with threading, metadata, and tool executions
        """
        return parse_complete_session(file_path)


def parse_complete_session(file_path: Path) -> ParsedSession:
    """Parse a JSONL session file into a complete ParsedSession with threading and metadata.

    This function optimizes performance for large session files by:
    1. Using memory-efficient streaming for initial parsing
    2. Processing messages in batches for threading reconstruction
    3. Calculating metadata incrementally to avoid redundant processing

    Args:
        file_path: Path to the JSONL session file

    Returns:
        ParsedSession: Complete session with conversation threading, metadata, and tool executions

    Raises:
        ParseError: If file cannot be parsed
    """
    try:
        # Parse raw message records
        message_records = parse_session_file(file_path)

        # Assemble into complete ParsedSession
        session = ParsedSession.from_message_records(message_records)

        logger.info(
            f"Successfully parsed session {session.session_id} with "
            f"{len(session.messages)} messages, "
            f"{len(session.tool_executions)} tool executions"
        )

        return session

    except ParseError:
        raise  # Re-raise ParseError as-is
    except Exception as e:
        # Check for common error types and provide specific guidance
        if "session_id" in str(e):
            raise ParseError(
                f"Failed to process session from {file_path}: Missing or invalid session_id. "
                f"The file may not be a valid Claude Code session file."
            ) from e
        elif "threading" in str(e).lower() or "parent" in str(e).lower():
            raise ParseError(
                f"Failed to reconstruct conversation threading from {file_path}: {e}. "
                f"The session file may contain incomplete message chains."
            ) from e
        else:
            raise ParseError(
                f"Failed to parse complete session from {file_path}: {e}. "
                f"Try using parse_session_file() to access raw messages without reconstruction."
            ) from e
