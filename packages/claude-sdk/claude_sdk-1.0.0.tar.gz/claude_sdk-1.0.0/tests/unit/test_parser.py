"""Unit tests for claude_sdk.parser."""

import json
import tempfile
from pathlib import Path

import pytest

from claude_sdk.errors import ParseError
from claude_sdk.models import MessageRecord, MessageType, Role, UserType
from claude_sdk.parser import (
    SessionParser,
    discover_sessions,
    parse_jsonl_file,
    parse_session_file,
)


@pytest.fixture
def temp_projects_dir():
    """Create a temporary projects directory structure."""
    with tempfile.TemporaryDirectory() as tmpdir:
        projects_dir = Path(tmpdir) / "projects"
        projects_dir.mkdir()
        yield projects_dir


@pytest.fixture
def sample_jsonl_data():
    """Sample JSONL record data for testing."""
    return {
        "parentUuid": None,
        "isSidechain": False,
        "userType": "external",
        "cwd": "/Users/test/project",
        "sessionId": "test-session-123",
        "version": "1.0.0",
        "type": "user",
        "message": {"role": "user", "content": [{"type": "text", "text": "Hello world"}]},
        "uuid": "550e8400-e29b-41d4-a716-446655440000",
        "timestamp": "2024-01-01T12:00:00Z",
    }


@pytest.fixture
def valid_jsonl_file(temp_projects_dir, sample_jsonl_data):
    """Create a valid JSONL file for testing."""
    project_dir = temp_projects_dir / "test-project"
    project_dir.mkdir()

    jsonl_file = project_dir / "session.jsonl"
    with jsonl_file.open("w") as f:
        # Write valid record
        f.write(json.dumps(sample_jsonl_data) + "\n")
        # Write another valid record with different UUID
        data2 = sample_jsonl_data.copy()
        data2["uuid"] = "550e8400-e29b-41d4-a716-446655440001"
        f.write(json.dumps(data2) + "\n")

    return jsonl_file


@pytest.fixture
def malformed_jsonl_file(temp_projects_dir, sample_jsonl_data):
    """Create a JSONL file with malformed data for testing."""
    project_dir = temp_projects_dir / "test-project"
    project_dir.mkdir()

    jsonl_file = project_dir / "malformed.jsonl"
    with jsonl_file.open("w") as f:
        # Valid record
        f.write(json.dumps(sample_jsonl_data) + "\n")
        # Invalid JSON
        f.write('{"invalid": json}\n')
        # Valid JSON but invalid schema
        f.write('{"missing": "required_fields"}\n')
        # Empty line
        f.write("\n")
        # Another valid record
        data2 = sample_jsonl_data.copy()
        data2["uuid"] = "550e8400-e29b-41d4-a716-446655440002"
        f.write(json.dumps(data2) + "\n")

    return jsonl_file


class TestDiscoverSessions:
    """Test session file discovery functionality."""

    def test_discover_sessions_default_path(self):
        """Test discovery with default path."""
        # This test might fail if ~/.claude/projects doesn't exist
        # That's expected behavior - the function should raise ParseError
        home_claude_projects = Path.home() / ".claude" / "projects"

        if home_claude_projects.exists():
            sessions = discover_sessions()
            assert isinstance(sessions, list)
            # All files should be .jsonl files
            for session_path in sessions:
                assert session_path.suffix == ".jsonl"
        else:
            with pytest.raises(ParseError, match="Projects directory not found"):
                discover_sessions()

    def test_discover_sessions_custom_path(self, temp_projects_dir, valid_jsonl_file):
        """Test discovery with custom path."""
        sessions = discover_sessions(temp_projects_dir)
        assert len(sessions) == 1
        assert sessions[0] == valid_jsonl_file
        assert sessions[0].name == "session.jsonl"

    def test_discover_sessions_multiple_files(self, temp_projects_dir):
        """Test discovery of multiple JSONL files."""
        # Create multiple project directories with JSONL files
        for i in range(3):
            project_dir = temp_projects_dir / f"project-{i}"
            project_dir.mkdir()
            jsonl_file = project_dir / f"session-{i}.jsonl"
            jsonl_file.write_text('{"test": "data"}\n')

        sessions = discover_sessions(temp_projects_dir)
        assert len(sessions) == 3

        # Check all are .jsonl files
        for session_path in sessions:
            assert session_path.suffix == ".jsonl"

    def test_discover_sessions_empty_directory(self, temp_projects_dir):
        """Test discovery in empty directory."""
        sessions = discover_sessions(temp_projects_dir)
        assert sessions == []

    def test_discover_sessions_nonexistent_path(self):
        """Test discovery with nonexistent path."""
        nonexistent_path = Path("/nonexistent/path")
        with pytest.raises(ParseError, match="Projects directory not found"):
            discover_sessions(nonexistent_path)

    def test_discover_sessions_file_not_directory(self, temp_projects_dir):
        """Test discovery when path points to a file."""
        file_path = temp_projects_dir / "not_a_directory.txt"
        file_path.write_text("test")

        with pytest.raises(ParseError, match="Projects path is not a directory"):
            discover_sessions(file_path)


class TestParseJsonlFile:
    """Test JSONL file parsing functionality."""

    def test_parse_valid_jsonl_file(self, valid_jsonl_file):
        """Test parsing a valid JSONL file."""
        records = list(parse_jsonl_file(valid_jsonl_file))
        assert len(records) == 2

        # Check first record
        record1 = records[0]
        assert isinstance(record1, MessageRecord)
        assert record1.user_type == UserType.EXTERNAL
        assert record1.message_type == MessageType.USER
        assert record1.message.role == Role.USER
        assert record1.session_id == "test-session-123"

        # Check second record has different UUID
        record2 = records[1]
        assert record1.uuid != record2.uuid

    def test_parse_malformed_jsonl_file(self, malformed_jsonl_file):
        """Test parsing JSONL file with malformed data."""
        records = list(parse_jsonl_file(malformed_jsonl_file))
        # Should get 2 valid records, skip 3 malformed lines
        assert len(records) == 2

        for record in records:
            assert isinstance(record, MessageRecord)

    def test_parse_nonexistent_file(self):
        """Test parsing nonexistent file."""
        nonexistent_file = Path("/nonexistent/file.jsonl")
        with pytest.raises(ParseError, match="Session file not found"):
            list(parse_jsonl_file(nonexistent_file))

    def test_parse_directory_not_file(self, temp_projects_dir):
        """Test parsing when path is a directory."""
        with pytest.raises(ParseError, match="Session path is not a file"):
            list(parse_jsonl_file(temp_projects_dir))

    def test_parse_empty_file(self, temp_projects_dir):
        """Test parsing empty JSONL file."""
        empty_file = temp_projects_dir / "empty.jsonl"
        empty_file.write_text("")

        records = list(parse_jsonl_file(empty_file))
        assert records == []


class TestParseSessionFile:
    """Test session file parsing wrapper functionality."""

    def test_parse_session_file_success(self, valid_jsonl_file):
        """Test successful session file parsing."""
        records = parse_session_file(valid_jsonl_file)
        assert len(records) == 2
        assert all(isinstance(record, MessageRecord) for record in records)

    def test_parse_session_file_with_errors(self, malformed_jsonl_file):
        """Test session file parsing with some malformed data."""
        records = parse_session_file(malformed_jsonl_file)
        assert len(records) == 2  # 2 valid records out of 5 lines

    def test_parse_session_file_nonexistent(self):
        """Test parsing nonexistent session file."""
        nonexistent_file = Path("/nonexistent/session.jsonl")
        with pytest.raises(ParseError):
            parse_session_file(nonexistent_file)


class TestSessionParser:
    """Test SessionParser class functionality."""

    def test_session_parser_init_default(self):
        """Test SessionParser initialization with default path."""
        parser = SessionParser()
        expected_path = Path.home() / ".claude" / "projects"
        assert parser.base_path == expected_path

    def test_session_parser_init_custom_path(self, temp_projects_dir):
        """Test SessionParser initialization with custom path."""
        parser = SessionParser(temp_projects_dir)
        assert parser.base_path == temp_projects_dir

    def test_session_parser_discover_sessions(self, temp_projects_dir, valid_jsonl_file):
        """Test session discovery through SessionParser."""
        parser = SessionParser(temp_projects_dir)
        sessions = parser.discover_sessions()
        assert len(sessions) == 1
        assert sessions[0] == valid_jsonl_file

    def test_session_parser_parse_session(self, temp_projects_dir, valid_jsonl_file):
        """Test single session parsing through SessionParser."""
        parser = SessionParser(temp_projects_dir)
        records = parser.parse_session(valid_jsonl_file)
        assert len(records) == 2
        assert all(isinstance(record, MessageRecord) for record in records)

    def test_session_parser_parse_all_sessions(self, temp_projects_dir):
        """Test parsing all sessions through SessionParser."""
        # Create multiple JSONL files
        sample_data = {
            "parentUuid": None,
            "isSidechain": False,
            "userType": "external",
            "cwd": "/Users/test/project",
            "sessionId": "test-session",
            "version": "1.0.0",
            "type": "user",
            "message": {"role": "user", "content": [{"type": "text", "text": "Hello"}]},
            "uuid": "550e8400-e29b-41d4-a716-446655440000",
            "timestamp": "2024-01-01T12:00:00Z",
        }

        project1 = temp_projects_dir / "project1"
        project1.mkdir()
        file1 = project1 / "session1.jsonl"
        file1.write_text(json.dumps(sample_data) + "\n")

        project2 = temp_projects_dir / "project2"
        project2.mkdir()
        file2 = project2 / "session2.jsonl"
        sample_data["uuid"] = "550e8400-e29b-41d4-a716-446655440001"
        file2.write_text(json.dumps(sample_data) + "\n")

        parser = SessionParser(temp_projects_dir)
        results = parser.parse_all_sessions()

        assert len(results) == 2
        assert all(len(records) == 1 for records in results.values())
        assert all(isinstance(records[0], MessageRecord) for records in results.values())

    def test_session_parser_parse_all_sessions_with_errors(
        self, temp_projects_dir, malformed_jsonl_file
    ):
        """Test parsing all sessions when some have errors."""
        parser = SessionParser(temp_projects_dir)
        results = parser.parse_all_sessions()

        # Should have one file with partial results (2 valid records)
        assert len(results) == 1
        assert len(results[malformed_jsonl_file]) == 2
