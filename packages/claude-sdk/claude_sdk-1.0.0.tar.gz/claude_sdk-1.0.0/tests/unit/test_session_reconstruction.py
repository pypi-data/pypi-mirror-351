"""Unit tests for session reconstruction and metadata functionality."""

from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4

import pytest

from claude_sdk.models import (
    ConversationTree,
    Message,
    MessageRecord,
    MessageType,
    ParsedSession,
    Role,
    SessionMetadata,
    TextBlock,
    TokenUsage,
    ToolResult,
    ToolUseBlock,
    UserType,
)


class TestConversationTreeConstruction:
    """Test conversation tree building and threading logic."""

    def test_build_conversation_tree_linear_conversation(self):
        """Test building conversation tree from linear conversation."""
        # Create a linear conversation: msg1 -> msg2 -> msg3
        uuid1, uuid2, uuid3 = uuid4(), uuid4(), uuid4()
        timestamp = datetime.now()

        messages = [
            MessageRecord(
                uuid=uuid1,
                parentUuid=None,  # Root message
                sessionId="session_123",
                message=Message(role=Role.USER, content=[TextBlock(text="Hello")]),
                timestamp=timestamp,
                isSidechain=False,
                userType=UserType.EXTERNAL,
                cwd=Path("/test"),
                version="1.0.0",
                type=MessageType.USER,
            ),
            MessageRecord(
                uuid=uuid2,
                parentUuid=uuid1,  # Child of uuid1
                sessionId="session_123",
                message=Message(role=Role.ASSISTANT, content=[TextBlock(text="Hi there")]),
                timestamp=timestamp + timedelta(seconds=1),
                isSidechain=False,
                userType=UserType.EXTERNAL,
                cwd=Path("/test"),
                version="1.0.0",
                type=MessageType.ASSISTANT,
            ),
            MessageRecord(
                uuid=uuid3,
                parentUuid=uuid2,  # Child of uuid2
                sessionId="session_123",
                message=Message(role=Role.USER, content=[TextBlock(text="How are you?")]),
                timestamp=timestamp + timedelta(seconds=2),
                isSidechain=False,
                userType=UserType.EXTERNAL,
                cwd=Path("/test"),
                version="1.0.0",
                type=MessageType.USER,
            ),
        ]

        session = ParsedSession(session_id="session_123", messages=messages)
        tree = session.build_conversation_tree()

        # Verify tree structure
        assert len(tree.root_messages) == 1
        assert tree.root_messages[0] == uuid1

        assert str(uuid1) in tree.parent_to_children
        assert str(uuid2) in tree.parent_to_children
        assert str(uuid3) not in tree.parent_to_children  # Leaf node

        assert tree.parent_to_children[str(uuid1)] == [str(uuid2)]
        assert tree.parent_to_children[str(uuid2)] == [str(uuid3)]

        assert len(tree.orphaned_messages) == 0
        assert len(tree.circular_references) == 0

    def test_build_conversation_tree_branching_conversation(self):
        """Test building conversation tree with branching (multiple children)."""
        # Create branching: uuid1 -> uuid2, uuid3
        uuid1, uuid2, uuid3 = uuid4(), uuid4(), uuid4()
        timestamp = datetime.now()

        messages = [
            MessageRecord(
                uuid=uuid1,
                parentUuid=None,
                sessionId="session_123",
                message=Message(role=Role.USER, content=[TextBlock(text="Root")]),
                timestamp=timestamp,
                isSidechain=False,
                userType=UserType.EXTERNAL,
                cwd=Path("/test"),
                version="1.0.0",
                type=MessageType.USER,
            ),
            MessageRecord(
                uuid=uuid2,
                parentUuid=uuid1,
                sessionId="session_123",
                message=Message(role=Role.ASSISTANT, content=[TextBlock(text="Branch 1")]),
                timestamp=timestamp + timedelta(seconds=1),
                isSidechain=False,
                userType=UserType.EXTERNAL,
                cwd=Path("/test"),
                version="1.0.0",
                type=MessageType.ASSISTANT,
            ),
            MessageRecord(
                uuid=uuid3,
                parentUuid=uuid1,  # Same parent as uuid2
                sessionId="session_123",
                message=Message(role=Role.ASSISTANT, content=[TextBlock(text="Branch 2")]),
                timestamp=timestamp + timedelta(seconds=2),
                isSidechain=False,
                userType=UserType.EXTERNAL,
                cwd=Path("/test"),
                version="1.0.0",
                type=MessageType.ASSISTANT,
            ),
        ]

        session = ParsedSession(session_id="session_123", messages=messages)
        tree = session.build_conversation_tree()

        # Verify branching structure
        assert len(tree.root_messages) == 1
        assert tree.root_messages[0] == uuid1

        children = tree.parent_to_children[str(uuid1)]
        assert len(children) == 2
        assert str(uuid2) in children
        assert str(uuid3) in children

        assert len(tree.orphaned_messages) == 0
        assert len(tree.circular_references) == 0

    def test_build_conversation_tree_orphaned_messages(self):
        """Test handling of orphaned messages (parent not found)."""
        uuid1, uuid2, uuid_missing = uuid4(), uuid4(), uuid4()
        timestamp = datetime.now()

        messages = [
            MessageRecord(
                uuid=uuid1,
                parentUuid=None,
                sessionId="session_123",
                message=Message(role=Role.USER, content=[TextBlock(text="Root")]),
                timestamp=timestamp,
                isSidechain=False,
                userType=UserType.EXTERNAL,
                cwd=Path("/test"),
                version="1.0.0",
                type=MessageType.USER,
            ),
            MessageRecord(
                uuid=uuid2,
                parentUuid=uuid_missing,  # Parent doesn't exist in session
                sessionId="session_123",
                message=Message(role=Role.ASSISTANT, content=[TextBlock(text="Orphaned")]),
                timestamp=timestamp + timedelta(seconds=1),
                isSidechain=False,
                userType=UserType.EXTERNAL,
                cwd=Path("/test"),
                version="1.0.0",
                type=MessageType.ASSISTANT,
            ),
        ]

        session = ParsedSession(session_id="session_123", messages=messages)
        tree = session.build_conversation_tree()

        # Verify orphaned message detection
        assert len(tree.root_messages) == 1
        assert tree.root_messages[0] == uuid1

        assert len(tree.orphaned_messages) == 1
        assert tree.orphaned_messages[0] == uuid2

        assert len(tree.circular_references) == 0

    def test_build_conversation_tree_circular_reference(self):
        """Test detection of circular references."""
        uuid1, uuid2 = uuid4(), uuid4()
        timestamp = datetime.now()

        messages = [
            MessageRecord(
                uuid=uuid1,
                parentUuid=uuid2,  # Points to uuid2
                sessionId="session_123",
                message=Message(role=Role.USER, content=[TextBlock(text="Msg1")]),
                timestamp=timestamp,
                isSidechain=False,
                userType=UserType.EXTERNAL,
                cwd=Path("/test"),
                version="1.0.0",
                type=MessageType.USER,
            ),
            MessageRecord(
                uuid=uuid2,
                parentUuid=uuid1,  # Points back to uuid1 - circular!
                sessionId="session_123",
                message=Message(role=Role.ASSISTANT, content=[TextBlock(text="Msg2")]),
                timestamp=timestamp + timedelta(seconds=1),
                isSidechain=False,
                userType=UserType.EXTERNAL,
                cwd=Path("/test"),
                version="1.0.0",
                type=MessageType.ASSISTANT,
            ),
        ]

        session = ParsedSession(session_id="session_123", messages=messages)
        tree = session.build_conversation_tree()

        # Verify circular reference detection
        assert len(tree.circular_references) == 2  # Both messages form circular refs
        circular_uuids = {ref[0] for ref in tree.circular_references}
        assert uuid1 in circular_uuids
        assert uuid2 in circular_uuids

    def test_build_conversation_tree_multiple_roots(self):
        """Test conversation tree with multiple root messages."""
        uuid1, uuid2, uuid3, uuid4_val = uuid4(), uuid4(), uuid4(), uuid4()
        timestamp = datetime.now()

        messages = [
            MessageRecord(
                uuid=uuid1,
                parentUuid=None,  # Root 1
                sessionId="session_123",
                message=Message(role=Role.USER, content=[TextBlock(text="Root 1")]),
                timestamp=timestamp,
                isSidechain=False,
                userType=UserType.EXTERNAL,
                cwd=Path("/test"),
                version="1.0.0",
                type=MessageType.USER,
            ),
            MessageRecord(
                uuid=uuid2,
                parentUuid=uuid1,  # Child of root 1
                sessionId="session_123",
                message=Message(role=Role.ASSISTANT, content=[TextBlock(text="Child 1")]),
                timestamp=timestamp + timedelta(seconds=1),
                isSidechain=False,
                userType=UserType.EXTERNAL,
                cwd=Path("/test"),
                version="1.0.0",
                type=MessageType.ASSISTANT,
            ),
            MessageRecord(
                uuid=uuid3,
                parentUuid=None,  # Root 2
                sessionId="session_123",
                message=Message(role=Role.USER, content=[TextBlock(text="Root 2")]),
                timestamp=timestamp + timedelta(seconds=2),
                isSidechain=False,
                userType=UserType.EXTERNAL,
                cwd=Path("/test"),
                version="1.0.0",
                type=MessageType.USER,
            ),
            MessageRecord(
                uuid=uuid4_val,
                parentUuid=uuid3,  # Child of root 2
                sessionId="session_123",
                message=Message(role=Role.ASSISTANT, content=[TextBlock(text="Child 2")]),
                timestamp=timestamp + timedelta(seconds=3),
                isSidechain=False,
                userType=UserType.EXTERNAL,
                cwd=Path("/test"),
                version="1.0.0",
                type=MessageType.ASSISTANT,
            ),
        ]

        session = ParsedSession(session_id="session_123", messages=messages)
        tree = session.build_conversation_tree()

        # Verify multiple roots
        assert len(tree.root_messages) == 2
        assert uuid1 in tree.root_messages
        assert uuid3 in tree.root_messages

        # Verify parent-child relationships
        assert tree.parent_to_children[str(uuid1)] == [str(uuid2)]
        assert tree.parent_to_children[str(uuid3)] == [str(uuid4_val)]

        assert len(tree.orphaned_messages) == 0
        assert len(tree.circular_references) == 0


class TestEnhancedSessionMetadata:
    """Test enhanced session metadata calculation."""

    def test_calculate_metadata_comprehensive(self):
        """Test comprehensive metadata calculation with all features."""
        timestamp = datetime.now()

        # Create usage data
        usage1 = TokenUsage(
            input_tokens=100,
            output_tokens=50,
            cache_creation_input_tokens=20,
            cache_read_input_tokens=10,
        )
        usage2 = TokenUsage(
            input_tokens=150,
            output_tokens=75,
            cache_creation_input_tokens=30,
            cache_read_input_tokens=15,
        )

        # Create messages with various content
        tool_block = ToolUseBlock(id="tool_1", name="bash", input={"command": "ls"})

        messages = [
            MessageRecord(
                uuid=uuid4(),
                parentUuid=None,
                sessionId="session_123",
                message=Message(role=Role.USER, content=[TextBlock(text="Hello")], usage=usage1),
                timestamp=timestamp,
                isSidechain=False,
                userType=UserType.EXTERNAL,
                cwd=Path("/test"),
                version="1.0.0",
                type=MessageType.USER,
                costUSD=0.05,
                durationMs=1000,
            ),
            MessageRecord(
                uuid=uuid4(),
                parentUuid=None,
                sessionId="session_123",
                message=Message(role=Role.ASSISTANT, content=[tool_block], usage=usage2),
                timestamp=timestamp + timedelta(seconds=2),
                isSidechain=False,
                userType=UserType.EXTERNAL,
                cwd=Path("/test"),
                version="1.0.0",
                type=MessageType.ASSISTANT,
                costUSD=0.10,
                durationMs=2000,
            ),
        ]

        session = ParsedSession(session_id="session_123", messages=messages)
        metadata = session.calculate_metadata()

        # Verify comprehensive metadata
        assert abs(metadata.total_cost - 0.15) < 1e-10  # Handle floating point precision
        assert metadata.total_messages == 2
        assert metadata.user_messages == 1
        assert metadata.assistant_messages == 1

        # Token aggregations
        assert metadata.total_input_tokens == 250  # 100 + 150
        assert metadata.total_output_tokens == 125  # 50 + 75
        assert metadata.cache_creation_tokens == 50  # 20 + 30
        assert metadata.cache_read_tokens == 25  # 10 + 15

        # Tool usage
        assert metadata.tool_usage_count["bash"] == 1
        assert metadata.total_tool_executions == 1

        # Timing
        assert metadata.session_start == timestamp
        assert metadata.session_end == timestamp + timedelta(seconds=2)
        assert metadata.session_duration == timedelta(seconds=2)
        assert metadata.total_duration_ms == 3000  # 1000 + 2000
        assert metadata.average_response_time == 1500.0  # (1000 + 2000) / 2

    def test_calculate_metadata_empty_session(self):
        """Test metadata calculation for empty session."""
        session = ParsedSession(session_id="session_123", messages=[])
        metadata = session.calculate_metadata()

        assert metadata.total_cost == 0.0
        assert metadata.total_messages == 0
        assert metadata.user_messages == 0
        assert metadata.assistant_messages == 0
        assert metadata.total_input_tokens == 0
        assert metadata.total_output_tokens == 0
        assert metadata.tool_usage_count == {}
        assert metadata.total_tool_executions == 0
        assert metadata.session_start is None
        assert metadata.session_end is None
        assert metadata.session_duration is None
        assert metadata.average_response_time is None

    def test_calculate_metadata_multiple_tools(self):
        """Test metadata calculation with multiple tool types."""
        timestamp = datetime.now()

        # Create messages with different tools
        messages = [
            MessageRecord(
                uuid=uuid4(),
                parentUuid=None,
                sessionId="session_123",
                message=Message(
                    role=Role.ASSISTANT,
                    content=[
                        ToolUseBlock(id="tool_1", name="bash", input={"command": "ls"}),
                        ToolUseBlock(id="tool_2", name="read", input={"file": "test.txt"}),
                    ],
                ),
                timestamp=timestamp,
                isSidechain=False,
                userType=UserType.EXTERNAL,
                cwd=Path("/test"),
                version="1.0.0",
                type=MessageType.ASSISTANT,
            ),
            MessageRecord(
                uuid=uuid4(),
                parentUuid=None,
                sessionId="session_123",
                message=Message(
                    role=Role.ASSISTANT,
                    content=[
                        ToolUseBlock(id="tool_3", name="bash", input={"command": "pwd"}),
                    ],
                ),
                timestamp=timestamp + timedelta(seconds=1),
                isSidechain=False,
                userType=UserType.EXTERNAL,
                cwd=Path("/test"),
                version="1.0.0",
                type=MessageType.ASSISTANT,
            ),
        ]

        session = ParsedSession(session_id="session_123", messages=messages)
        metadata = session.calculate_metadata()

        # Verify tool usage counts
        assert metadata.tool_usage_count["bash"] == 2  # tool_1 and tool_3
        assert metadata.tool_usage_count["read"] == 1  # tool_2
        assert metadata.total_tool_executions == 3

    def test_calculate_metadata_missing_costs(self):
        """Test metadata calculation when some messages have no cost."""
        timestamp = datetime.now()

        messages = [
            MessageRecord(
                uuid=uuid4(),
                parentUuid=None,
                sessionId="session_123",
                message=Message(role=Role.USER, content=[TextBlock(text="Hello")]),
                timestamp=timestamp,
                isSidechain=False,
                userType=UserType.EXTERNAL,
                cwd=Path("/test"),
                version="1.0.0",
                type=MessageType.USER,
                costUSD=0.05,  # Has cost
            ),
            MessageRecord(
                uuid=uuid4(),
                parentUuid=None,
                sessionId="session_123",
                message=Message(role=Role.ASSISTANT, content=[TextBlock(text="Hi")]),
                timestamp=timestamp + timedelta(seconds=1),
                isSidechain=False,
                userType=UserType.EXTERNAL,
                cwd=Path("/test"),
                version="1.0.0",
                type=MessageType.ASSISTANT,
                # costUSD=None (no cost)
            ),
        ]

        session = ParsedSession(session_id="session_123", messages=messages)
        metadata = session.calculate_metadata()

        # Should only include the cost from the first message
        assert metadata.total_cost == 0.05
        assert metadata.total_messages == 2


class TestToolExecutionExtraction:
    """Test tool execution extraction and correlation."""

    def test_extract_tool_executions_basic(self):
        """Test basic tool execution extraction."""
        timestamp = datetime.now()
        tool_use_id = "tool_123"

        # Create tool use block
        tool_use_block = ToolUseBlock(id=tool_use_id, name="bash", input={"command": "ls -la"})

        messages = [
            MessageRecord(
                uuid=uuid4(),
                parentUuid=None,
                sessionId="session_123",
                message=Message(role=Role.ASSISTANT, content=[tool_use_block]),
                timestamp=timestamp,
                isSidechain=False,
                userType=UserType.EXTERNAL,
                cwd=Path("/test"),
                version="1.0.0",
                type=MessageType.ASSISTANT,
            ),
            MessageRecord(
                uuid=uuid4(),
                parentUuid=None,
                sessionId="session_123",
                message=Message(role=Role.USER, content=[TextBlock(text="Tool result returned")]),
                timestamp=timestamp + timedelta(seconds=2),
                isSidechain=False,
                userType=UserType.EXTERNAL,
                cwd=Path("/test"),
                version="1.0.0",
                type=MessageType.USER,
                toolUseResult=ToolResult(
                    tool_use_id=tool_use_id, content="file1.txt\nfile2.txt", is_error=False
                ),
            ),
        ]

        session = ParsedSession(session_id="session_123", messages=messages)
        executions = session.extract_tool_executions()

        assert len(executions) == 1
        execution = executions[0]
        assert execution.tool_name == "bash"
        assert execution.input == {"command": "ls -la"}
        assert execution.output.content == "file1.txt\nfile2.txt"
        assert execution.output.is_error is False
        assert execution.duration == timedelta(seconds=2)
        assert execution.timestamp == timestamp

    def test_extract_tool_executions_multiple_tools(self):
        """Test extraction with multiple tool executions."""
        timestamp = datetime.now()

        # Create multiple tool use/result pairs
        tool_id_1, tool_id_2 = "tool_1", "tool_2"

        messages = [
            # First tool use
            MessageRecord(
                uuid=uuid4(),
                parentUuid=None,
                sessionId="session_123",
                message=Message(
                    role=Role.ASSISTANT,
                    content=[ToolUseBlock(id=tool_id_1, name="bash", input={"command": "ls"})],
                ),
                timestamp=timestamp,
                isSidechain=False,
                userType=UserType.EXTERNAL,
                cwd=Path("/test"),
                version="1.0.0",
                type=MessageType.ASSISTANT,
            ),
            # Second tool use
            MessageRecord(
                uuid=uuid4(),
                parentUuid=None,
                sessionId="session_123",
                message=Message(
                    role=Role.ASSISTANT,
                    content=[ToolUseBlock(id=tool_id_2, name="read", input={"file": "test.txt"})],
                ),
                timestamp=timestamp + timedelta(seconds=1),
                isSidechain=False,
                userType=UserType.EXTERNAL,
                cwd=Path("/test"),
                version="1.0.0",
                type=MessageType.ASSISTANT,
            ),
            # First tool result
            MessageRecord(
                uuid=uuid4(),
                parentUuid=None,
                sessionId="session_123",
                message=Message(
                    role=Role.USER,
                    content=[TextBlock(text="Tool result 1")],
                ),
                timestamp=timestamp + timedelta(seconds=3),
                isSidechain=False,
                userType=UserType.EXTERNAL,
                cwd=Path("/test"),
                version="1.0.0",
                type=MessageType.USER,
                toolUseResult=ToolResult(
                    tool_use_id=tool_id_1, content="file1.txt", is_error=False
                ),
            ),
            # Second tool result
            MessageRecord(
                uuid=uuid4(),
                parentUuid=None,
                sessionId="session_123",
                message=Message(
                    role=Role.USER,
                    content=[TextBlock(text="Tool result 2")],
                ),
                timestamp=timestamp + timedelta(seconds=4),
                isSidechain=False,
                userType=UserType.EXTERNAL,
                cwd=Path("/test"),
                version="1.0.0",
                type=MessageType.USER,
                toolUseResult=ToolResult(
                    tool_use_id=tool_id_2, content="file content", is_error=False
                ),
            ),
        ]

        session = ParsedSession(session_id="session_123", messages=messages)
        executions = session.extract_tool_executions()

        assert len(executions) == 2

        # Executions should be sorted by timestamp
        assert executions[0].tool_name == "bash"
        assert executions[0].duration == timedelta(seconds=3)

        assert executions[1].tool_name == "read"
        assert executions[1].duration == timedelta(seconds=3)  # 4 - 1

    def test_extract_tool_executions_with_message_level_results(self):
        """Test extraction when tool results are in message-level tool_use_result field."""
        timestamp = datetime.now()
        tool_id = "tool_123"

        tool_result = ToolResult(
            tool_use_id=tool_id, content="Command executed", stdout="success", is_error=False
        )

        messages = [
            MessageRecord(
                uuid=uuid4(),
                parentUuid=None,
                sessionId="session_123",
                message=Message(
                    role=Role.ASSISTANT,
                    content=[ToolUseBlock(id=tool_id, name="bash", input={"command": "echo test"})],
                ),
                timestamp=timestamp,
                isSidechain=False,
                userType=UserType.EXTERNAL,
                cwd=Path("/test"),
                version="1.0.0",
                type=MessageType.ASSISTANT,
                toolUseResult=tool_result,  # Result at message level
                durationMs=1500,
            ),
        ]

        session = ParsedSession(session_id="session_123", messages=messages)
        executions = session.extract_tool_executions()

        assert len(executions) == 1
        execution = executions[0]
        assert execution.tool_name == "bash"
        assert execution.output == tool_result
        assert execution.duration == timedelta(milliseconds=1500)

    def test_extract_tool_executions_missing_results(self):
        """Test extraction when tool use has no corresponding result."""
        timestamp = datetime.now()

        messages = [
            MessageRecord(
                uuid=uuid4(),
                parentUuid=None,
                sessionId="session_123",
                message=Message(
                    role=Role.ASSISTANT,
                    content=[ToolUseBlock(id="tool_orphan", name="bash", input={"command": "ls"})],
                ),
                timestamp=timestamp,
                isSidechain=False,
                userType=UserType.EXTERNAL,
                cwd=Path("/test"),
                version="1.0.0",
                type=MessageType.ASSISTANT,
            ),
        ]

        session = ParsedSession(session_id="session_123", messages=messages)
        executions = session.extract_tool_executions()

        # Should not create execution without corresponding result
        assert len(executions) == 0


class TestSessionValidation:
    """Test comprehensive session validation."""

    def test_validate_session_integrity_all_valid(self):
        """Test validation with completely valid session."""
        timestamp = datetime.now()
        uuid1, uuid2 = uuid4(), uuid4()

        messages = [
            MessageRecord(
                uuid=uuid1,
                parentUuid=None,
                sessionId="session_123",
                message=Message(role=Role.USER, content=[TextBlock(text="Hello")]),
                timestamp=timestamp,
                isSidechain=False,
                userType=UserType.EXTERNAL,
                cwd=Path("/test"),
                version="1.0.0",
                type=MessageType.USER,
                costUSD=0.01,
            ),
            MessageRecord(
                uuid=uuid2,
                parentUuid=uuid1,
                sessionId="session_123",
                message=Message(role=Role.ASSISTANT, content=[TextBlock(text="Hi")]),
                timestamp=timestamp + timedelta(seconds=1),
                isSidechain=False,
                userType=UserType.EXTERNAL,
                cwd=Path("/test"),
                version="1.0.0",
                type=MessageType.ASSISTANT,
                costUSD=0.02,
            ),
        ]

        # Create session with properly calculated metadata
        session = ParsedSession.from_message_records(messages)
        is_valid, issues = session.validate_session_integrity()

        assert is_valid is True
        assert len(issues) == 0

    def test_validate_session_integrity_inconsistent_session_ids(self):
        """Test validation detects inconsistent session IDs."""
        timestamp = datetime.now()

        messages = [
            MessageRecord(
                uuid=uuid4(),
                parentUuid=None,
                sessionId="session_123",
                message=Message(role=Role.USER, content=[TextBlock(text="Hello")]),
                timestamp=timestamp,
                isSidechain=False,
                userType=UserType.EXTERNAL,
                cwd=Path("/test"),
                version="1.0.0",
                type=MessageType.USER,
            ),
            MessageRecord(
                uuid=uuid4(),
                parentUuid=None,
                sessionId="session_456",  # Different session ID
                message=Message(role=Role.ASSISTANT, content=[TextBlock(text="Hi")]),
                timestamp=timestamp + timedelta(seconds=1),
                isSidechain=False,
                userType=UserType.EXTERNAL,
                cwd=Path("/test"),
                version="1.0.0",
                type=MessageType.ASSISTANT,
            ),
        ]

        session = ParsedSession(session_id="session_123", messages=messages)
        is_valid, issues = session.validate_session_integrity()

        assert is_valid is False
        assert any("inconsistent session_id" in issue for issue in issues)

    def test_validate_session_integrity_metadata_mismatch(self):
        """Test validation detects metadata calculation mismatches."""
        timestamp = datetime.now()

        messages = [
            MessageRecord(
                uuid=uuid4(),
                parentUuid=None,
                sessionId="session_123",
                message=Message(role=Role.USER, content=[TextBlock(text="Hello")]),
                timestamp=timestamp,
                isSidechain=False,
                userType=UserType.EXTERNAL,
                cwd=Path("/test"),
                version="1.0.0",
                type=MessageType.USER,
                costUSD=0.05,
            ),
        ]

        # Create session with incorrect metadata
        incorrect_metadata = SessionMetadata(
            total_cost=0.10,  # Should be 0.05
            total_messages=2,  # Should be 1
            user_messages=0,  # Should be 1
        )

        session = ParsedSession(
            session_id="session_123", messages=messages, metadata=incorrect_metadata
        )
        is_valid, issues = session.validate_session_integrity()

        assert is_valid is False
        assert any("cost mismatch" in issue for issue in issues)
        assert any("message count mismatch" in issue for issue in issues)
        assert any("User message count mismatch" in issue for issue in issues)

    def test_validate_session_integrity_orphaned_messages(self):
        """Test validation detects orphaned messages in conversation tree."""
        timestamp = datetime.now()
        missing_uuid = uuid4()

        messages = [
            MessageRecord(
                uuid=uuid4(),
                parentUuid=missing_uuid,  # Parent doesn't exist
                sessionId="session_123",
                message=Message(role=Role.USER, content=[TextBlock(text="Orphaned")]),
                timestamp=timestamp,
                isSidechain=False,
                userType=UserType.EXTERNAL,
                cwd=Path("/test"),
                version="1.0.0",
                type=MessageType.USER,
            ),
        ]

        session = ParsedSession.from_message_records(messages)
        is_valid, issues = session.validate_session_integrity()

        assert is_valid is False
        assert any("orphaned messages" in issue for issue in issues)

    def test_validate_session_integrity_duplicate_uuids(self):
        """Test validation detects duplicate UUIDs."""
        timestamp = datetime.now()
        duplicate_uuid = uuid4()

        messages = [
            MessageRecord(
                uuid=duplicate_uuid,  # Same UUID
                parentUuid=None,
                sessionId="session_123",
                message=Message(role=Role.USER, content=[TextBlock(text="Message 1")]),
                timestamp=timestamp,
                isSidechain=False,
                userType=UserType.EXTERNAL,
                cwd=Path("/test"),
                version="1.0.0",
                type=MessageType.USER,
            ),
            MessageRecord(
                uuid=duplicate_uuid,  # Same UUID - invalid!
                parentUuid=None,
                sessionId="session_123",
                message=Message(role=Role.ASSISTANT, content=[TextBlock(text="Message 2")]),
                timestamp=timestamp + timedelta(seconds=1),
                isSidechain=False,
                userType=UserType.EXTERNAL,
                cwd=Path("/test"),
                version="1.0.0",
                type=MessageType.ASSISTANT,
            ),
        ]

        session = ParsedSession.from_message_records(messages)
        is_valid, issues = session.validate_session_integrity()

        assert is_valid is False
        assert any("Duplicate UUIDs" in issue for issue in issues)


class TestParsedSessionAssembly:
    """Test ParsedSession assembly from MessageRecord lists."""

    def test_from_message_records_basic(self):
        """Test basic session assembly from message records."""
        timestamp = datetime.now()
        messages = [
            MessageRecord(
                uuid=uuid4(),
                parentUuid=None,
                sessionId="session_123",
                message=Message(role=Role.USER, content=[TextBlock(text="Hello")]),
                timestamp=timestamp,
                isSidechain=False,
                userType=UserType.EXTERNAL,
                cwd=Path("/test"),
                version="1.0.0",
                type=MessageType.USER,
                costUSD=0.01,
            ),
        ]

        session = ParsedSession.from_message_records(messages)

        # Verify all components are assembled
        assert session.session_id == "session_123"
        assert len(session.messages) == 1
        assert isinstance(session.conversation_tree, ConversationTree)
        assert isinstance(session.metadata, SessionMetadata)
        assert session.metadata.total_cost == 0.01
        assert session.metadata.total_messages == 1
        assert isinstance(session.tool_executions, list)

    def test_from_message_records_auto_detect_session_id(self):
        """Test session ID auto-detection from messages."""
        timestamp = datetime.now()
        messages = [
            MessageRecord(
                uuid=uuid4(),
                parentUuid=None,
                sessionId="auto_detected_session",
                message=Message(role=Role.USER, content=[TextBlock(text="Hello")]),
                timestamp=timestamp,
                isSidechain=False,
                userType=UserType.EXTERNAL,
                cwd=Path("/test"),
                version="1.0.0",
                type=MessageType.USER,
            ),
        ]

        # Don't provide session_id - should auto-detect
        session = ParsedSession.from_message_records(messages)
        assert session.session_id == "auto_detected_session"

    def test_from_message_records_inconsistent_session_ids(self):
        """Test assembly fails with inconsistent session IDs."""
        timestamp = datetime.now()
        messages = [
            MessageRecord(
                uuid=uuid4(),
                parentUuid=None,
                sessionId="session_123",
                message=Message(role=Role.USER, content=[TextBlock(text="Hello")]),
                timestamp=timestamp,
                isSidechain=False,
                userType=UserType.EXTERNAL,
                cwd=Path("/test"),
                version="1.0.0",
                type=MessageType.USER,
            ),
            MessageRecord(
                uuid=uuid4(),
                parentUuid=None,
                sessionId="session_456",  # Different!
                message=Message(role=Role.ASSISTANT, content=[TextBlock(text="Hi")]),
                timestamp=timestamp + timedelta(seconds=1),
                isSidechain=False,
                userType=UserType.EXTERNAL,
                cwd=Path("/test"),
                version="1.0.0",
                type=MessageType.ASSISTANT,
            ),
        ]

        with pytest.raises(ValueError, match="Inconsistent session IDs"):
            ParsedSession.from_message_records(messages)

    def test_from_message_records_empty_list(self):
        """Test assembly fails with empty message list."""
        with pytest.raises(ValueError, match="Cannot create ParsedSession from empty message list"):
            ParsedSession.from_message_records([])

    def test_from_message_records_complex_session(self):
        """Test assembly with complex session including tools and conversation threading."""
        timestamp = datetime.now()
        uuid1, uuid2, uuid3 = uuid4(), uuid4(), uuid4()
        tool_id = "tool_123"

        messages = [
            # Root user message
            MessageRecord(
                uuid=uuid1,
                parentUuid=None,
                sessionId="complex_session",
                message=Message(role=Role.USER, content=[TextBlock(text="Can you list files?")]),
                timestamp=timestamp,
                isSidechain=False,
                userType=UserType.EXTERNAL,
                cwd=Path("/test"),
                version="1.0.0",
                type=MessageType.USER,
                costUSD=0.01,
            ),
            # Assistant response with tool use
            MessageRecord(
                uuid=uuid2,
                parentUuid=uuid1,
                sessionId="complex_session",
                message=Message(
                    role=Role.ASSISTANT,
                    content=[
                        TextBlock(text="I'll list the files for you."),
                        ToolUseBlock(id=tool_id, name="bash", input={"command": "ls -la"}),
                    ],
                ),
                timestamp=timestamp + timedelta(seconds=1),
                isSidechain=False,
                userType=UserType.EXTERNAL,
                cwd=Path("/test"),
                version="1.0.0",
                type=MessageType.ASSISTANT,
                costUSD=0.05,
            ),
            # Tool result
            MessageRecord(
                uuid=uuid3,
                parentUuid=uuid2,
                sessionId="complex_session",
                message=Message(
                    role=Role.USER,
                    content=[TextBlock(text="Tool result")],
                ),
                timestamp=timestamp + timedelta(seconds=3),
                isSidechain=False,
                userType=UserType.EXTERNAL,
                cwd=Path("/test"),
                version="1.0.0",
                type=MessageType.USER,
                toolUseResult=ToolResult(
                    tool_use_id=tool_id, content="file1.txt\nfile2.txt", is_error=False
                ),
            ),
        ]

        session = ParsedSession.from_message_records(messages)

        # Verify complete assembly
        assert session.session_id == "complex_session"
        assert len(session.messages) == 3

        # Verify conversation tree
        assert len(session.conversation_tree.root_messages) == 1
        assert session.conversation_tree.root_messages[0] == uuid1
        assert len(session.conversation_tree.orphaned_messages) == 0

        # Verify metadata
        assert abs(session.metadata.total_cost - 0.06) < 1e-10
        assert session.metadata.total_messages == 3
        assert session.metadata.user_messages == 2
        assert session.metadata.assistant_messages == 1
        assert session.metadata.tool_usage_count["bash"] == 1

        # Verify tool executions
        assert len(session.tool_executions) == 1
        execution = session.tool_executions[0]
        assert execution.tool_name == "bash"
        assert execution.input == {"command": "ls -la"}
        assert execution.duration == timedelta(seconds=2)


class TestPerformanceWithLargeSessions:
    """Test performance with large session data."""

    def test_large_session_assembly_performance(self):
        """Test performance of session assembly with large message count."""
        import time

        timestamp = datetime.now()
        messages = []

        # Create a large session with 1000 messages
        for i in range(1000):
            uuid_val = uuid4()
            parent_uuid = messages[i - 1].uuid if i > 0 else None

            message = MessageRecord(
                uuid=uuid_val,
                parentUuid=parent_uuid,
                sessionId="large_session",
                message=Message(
                    role=Role.USER if i % 2 == 0 else Role.ASSISTANT,
                    content=[TextBlock(text=f"Message {i}")],
                ),
                timestamp=timestamp + timedelta(seconds=i),
                isSidechain=False,
                userType=UserType.EXTERNAL,
                cwd=Path("/test"),
                version="1.0.0",
                type=MessageType.USER if i % 2 == 0 else MessageType.ASSISTANT,
                costUSD=0.001,
            )
            messages.append(message)

        # Time the assembly
        start_time = time.perf_counter()
        session = ParsedSession.from_message_records(messages)
        end_time = time.perf_counter()

        duration = end_time - start_time

        # Performance requirement: should assemble 1000 messages in < 1 second
        assert duration < 1.0, f"Large session assembly too slow: {duration:.3f}s"

        # Verify correct assembly
        assert session.metadata.total_messages == 1000
        assert len(session.conversation_tree.root_messages) == 1
        assert abs(session.metadata.total_cost - 1.0) < 1e-10  # 1000 * 0.001

    def test_large_conversation_tree_performance(self):
        """Test conversation tree building performance with complex threading."""
        import time

        timestamp = datetime.now()
        messages = []

        # Create a complex tree: root with many children, each with their own children
        root_uuid = uuid4()
        messages.append(
            MessageRecord(
                uuid=root_uuid,
                parentUuid=None,
                sessionId="complex_tree",
                message=Message(role=Role.USER, content=[TextBlock(text="Root")]),
                timestamp=timestamp,
                isSidechain=False,
                userType=UserType.EXTERNAL,
                cwd=Path("/test"),
                version="1.0.0",
                type=MessageType.USER,
            )
        )

        # Create 50 direct children of root
        for i in range(50):
            child_uuid = uuid4()
            messages.append(
                MessageRecord(
                    uuid=child_uuid,
                    parentUuid=root_uuid,
                    sessionId="complex_tree",
                    message=Message(role=Role.ASSISTANT, content=[TextBlock(text=f"Child {i}")]),
                    timestamp=timestamp + timedelta(seconds=i + 1),
                    isSidechain=False,
                    userType=UserType.EXTERNAL,
                    cwd=Path("/test"),
                    version="1.0.0",
                    type=MessageType.ASSISTANT,
                )
            )

            # Each child has 5 grandchildren
            for j in range(5):
                grandchild_uuid = uuid4()
                messages.append(
                    MessageRecord(
                        uuid=grandchild_uuid,
                        parentUuid=child_uuid,
                        sessionId="complex_tree",
                        message=Message(
                            role=Role.USER, content=[TextBlock(text=f"Grandchild {i}-{j}")]
                        ),
                        timestamp=timestamp + timedelta(seconds=(i + 1) * 10 + j),
                        isSidechain=False,
                        userType=UserType.EXTERNAL,
                        cwd=Path("/test"),
                        version="1.0.0",
                        type=MessageType.USER,
                    )
                )

        # Total: 1 + 50 + (50 * 5) = 301 messages
        assert len(messages) == 301

        # Time the conversation tree building
        session = ParsedSession(session_id="complex_tree", messages=messages)
        start_time = time.perf_counter()
        tree = session.build_conversation_tree()
        end_time = time.perf_counter()

        duration = end_time - start_time

        # Performance requirement: should build tree for 301 messages in < 0.1 seconds
        assert duration < 0.1, f"Conversation tree building too slow: {duration:.3f}s"

        # Verify correct tree structure
        assert len(tree.root_messages) == 1
        assert tree.root_messages[0] == root_uuid
        assert len(tree.parent_to_children[str(root_uuid)]) == 50
        assert len(tree.orphaned_messages) == 0
        assert len(tree.circular_references) == 0
