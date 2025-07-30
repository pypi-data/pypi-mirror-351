"""Integration tests for claude_sdk."""

from pathlib import Path

import pytest

from claude_sdk.errors import ParseError
from claude_sdk.models import MessageType, Role
from claude_sdk.parser import parse_complete_session


class TestEndToEndParsing:
    """Test complete parsing pipeline from JSONL files to ParsedSession objects."""

    @pytest.fixture
    def fixtures_dir(self):
        """Get the fixtures directory path."""
        return Path(__file__).parent.parent / "fixtures"

    def test_realistic_session_parsing(self, fixtures_dir):
        """Test parsing a realistic Claude Code session file."""
        session_file = fixtures_dir / "realistic_session.jsonl"

        # Parse the session
        parsed_session = parse_complete_session(session_file)

        # Verify session structure
        assert parsed_session.session_id == "test-session-001"
        assert len(parsed_session.messages) == 6  # 3 user + 3 assistant/tool_result

        # Verify message threading
        assert parsed_session.conversation_tree is not None
        root_messages = [msg for msg in parsed_session.messages if msg.parent_uuid is None]
        assert len(root_messages) == 1
        assert root_messages[0].message.role == Role.USER

        # Verify tool usage extraction
        tool_messages = [
            msg
            for msg in parsed_session.messages
            if msg.message_type == MessageType.ASSISTANT
            and any(block.type == "tool_use" for block in msg.message.content)
        ]
        assert len(tool_messages) >= 2  # At least 2 tool use messages

        # Verify session metadata
        metadata = parsed_session.metadata
        assert metadata.total_messages == 6
        assert metadata.total_tool_executions >= 2
        assert metadata.session_start is not None
        assert metadata.session_end is not None

        # Verify conversation threading integrity
        for message in parsed_session.messages:
            if message.parent_uuid is not None:
                # Find parent message
                parent_found = any(
                    msg.uuid == message.parent_uuid for msg in parsed_session.messages
                )
                assert (
                    parent_found
                ), f"Parent {message.parent_uuid} not found for message {message.uuid}"

    def test_complex_branching_session_parsing(self, fixtures_dir):
        """Test parsing a session with branching conversations and sidechains."""
        session_file = fixtures_dir / "complex_branching_session.jsonl"

        parsed_session = parse_complete_session(session_file)

        # Verify basic structure
        assert parsed_session.session_id == "session-branch-001"
        assert len(parsed_session.messages) >= 8  # At least 8 valid messages in conversation

        # Verify sidechain handling
        sidechain_messages = [msg for msg in parsed_session.messages if msg.is_sidechain]
        main_chain_messages = [msg for msg in parsed_session.messages if not msg.is_sidechain]

        assert len(sidechain_messages) >= 2  # Should have sidechain messages
        assert len(main_chain_messages) >= 6  # Should have main chain messages

        # Verify conversation tree includes both chains
        tree = parsed_session.conversation_tree
        assert tree is not None

        # Check that all messages are properly threaded
        all_message_ids = {msg.uuid for msg in parsed_session.messages}
        for message in parsed_session.messages:
            if message.parent_uuid is not None:
                assert message.parent_uuid in all_message_ids

    def test_tool_only_session_parsing(self, fixtures_dir):
        """Test parsing a session with only tool interactions."""
        session_file = fixtures_dir / "tool_only_session.jsonl"

        parsed_session = parse_complete_session(session_file)

        # Verify structure
        assert parsed_session.session_id == "tool-only-session"
        assert len(parsed_session.messages) == 4  # 2 assistant tool_use + 2 tool_result

        # Verify all messages are tool-related
        tool_use_messages = [
            msg for msg in parsed_session.messages if msg.message_type == MessageType.ASSISTANT
        ]
        tool_result_messages = [
            msg
            for msg in parsed_session.messages
            if msg.message_type == MessageType.USER and msg.tool_use_result is not None
        ]

        assert len(tool_use_messages) == 2
        assert len(tool_result_messages) == 2

        # Verify metadata reflects tool-only nature
        metadata = parsed_session.metadata
        assert metadata.total_tool_executions == 2
        assert metadata.total_messages == 4

    def test_empty_session_handling(self, fixtures_dir):
        """Test handling of empty session files."""
        session_file = fixtures_dir / "empty_session.jsonl"

        # Empty sessions should raise a ParseError since they can't form a valid ParsedSession
        with pytest.raises(ParseError) as exc_info:
            parse_complete_session(session_file)

        # Error should mention empty message list
        assert "empty message list" in str(exc_info.value).lower()

    def test_interrupted_session_parsing(self, fixtures_dir):
        """Test parsing an interrupted/incomplete session."""
        session_file = fixtures_dir / "interrupted_session.jsonl"

        parsed_session = parse_complete_session(session_file)

        # Should handle incomplete session gracefully
        assert len(parsed_session.messages) >= 1
        assert parsed_session.session_id == "interrupted-session"

        # Verify metadata is calculated correctly even for incomplete session
        metadata = parsed_session.metadata
        assert metadata.total_messages > 0

    def test_complete_pipeline_workflow(self, fixtures_dir):
        """Test the complete workflow from file discovery to parsed session."""
        from claude_sdk.parser import discover_sessions

        # Discover sessions in fixtures directory
        sessions = discover_sessions(fixtures_dir)

        # Should find all test JSONL files except empty ones potentially
        assert len(sessions) >= 4  # At least our test files

        # Parse each discovered session
        parsed_sessions = []
        for session_path in sessions:
            try:
                parsed_session = parse_complete_session(session_path)
                parsed_sessions.append(parsed_session)
            except ParseError:
                # Some files (like malformed) may intentionally fail
                continue

        # Should successfully parse at least the valid sessions
        assert len(parsed_sessions) >= 3

        # Verify each parsed session has required structure
        for session in parsed_sessions:
            assert hasattr(session, "session_id")
            assert hasattr(session, "messages")
            assert hasattr(session, "metadata")
            assert isinstance(session.messages, list)


class TestErrorScenarios:
    """Test error handling and edge cases in the parsing pipeline."""

    @pytest.fixture
    def fixtures_dir(self):
        """Get the fixtures directory path."""
        return Path(__file__).parent.parent / "fixtures"

    def test_malformed_data_error_handling(self, fixtures_dir, caplog):
        """Test parsing malformed JSONL data logs warnings and continues gracefully."""
        session_file = fixtures_dir / "malformed_session.jsonl"

        # Parser should handle malformed data gracefully, not raise exceptions
        parsed_session = parse_complete_session(session_file)

        # Should get at least one valid message despite malformed lines
        assert len(parsed_session.messages) >= 1

        # Should log warnings about validation errors
        assert len(caplog.records) > 0
        warning_messages = [
            record.message for record in caplog.records if record.levelname == "WARNING"
        ]
        assert len(warning_messages) > 0

        # Check that warnings contain validation error information
        validation_warnings = [msg for msg in warning_messages if "validation error" in msg.lower()]
        assert len(validation_warnings) > 0

    def test_nonexistent_file_error(self):
        """Test handling of nonexistent file paths."""
        nonexistent_file = Path("/nonexistent/session.jsonl")

        with pytest.raises(ParseError) as exc_info:
            parse_complete_session(nonexistent_file)

        assert "not found" in str(exc_info.value).lower()

    def test_invalid_file_format_error(self, tmp_path):
        """Test handling of non-JSONL files."""
        invalid_file = tmp_path / "not_jsonl.txt"
        invalid_file.write_text("This is not JSONL data")

        with pytest.raises(ParseError):
            parse_complete_session(invalid_file)
