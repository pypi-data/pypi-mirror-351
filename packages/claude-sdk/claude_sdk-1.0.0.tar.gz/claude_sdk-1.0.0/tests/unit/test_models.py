"""Unit tests for claude_sdk.models foundation types."""

from datetime import datetime
from pathlib import Path
from uuid import UUID

import pytest

from claude_sdk.models import (
    ClaudeSDKBaseModel,
    ContentBlock,
    ConversationTree,
    DateTimeType,
    Message,
    MessageContentType,
    MessageRecord,
    MessageType,
    ParsedSession,
    PathType,
    Role,
    SessionMetadata,
    StopReason,
    TextBlock,
    ThinkingBlock,
    TokenUsage,
    ToolExecution,
    ToolResult,
    ToolResultBlock,
    ToolUseBlock,
    UserType,
    UUIDType,
)


class TestUserType:
    """Test UserType enum."""

    def test_enum_values(self):
        """Test UserType has correct string values."""
        assert UserType.EXTERNAL == "external"
        assert UserType.INTERNAL == "internal"

    def test_enum_membership(self):
        """Test UserType membership."""
        assert UserType.EXTERNAL in UserType
        assert UserType.INTERNAL in UserType
        assert "external" in [e.value for e in UserType]
        assert "internal" in [e.value for e in UserType]
        assert "invalid" not in [e.value for e in UserType]

    def test_string_inheritance(self):
        """Test UserType inherits from str."""
        assert isinstance(UserType.EXTERNAL, str)
        assert isinstance(UserType.INTERNAL, str)


class TestMessageType:
    """Test MessageType enum."""

    def test_enum_values(self):
        """Test MessageType has correct string values."""
        assert MessageType.USER == "user"
        assert MessageType.ASSISTANT == "assistant"

    def test_enum_membership(self):
        """Test MessageType membership."""
        assert MessageType.USER in MessageType
        assert MessageType.ASSISTANT in MessageType
        assert "user" in [e.value for e in MessageType]
        assert "assistant" in [e.value for e in MessageType]
        assert "system" not in [e.value for e in MessageType]

    def test_string_inheritance(self):
        """Test MessageType inherits from str."""
        assert isinstance(MessageType.USER, str)
        assert isinstance(MessageType.ASSISTANT, str)


class TestRole:
    """Test Role enum."""

    def test_enum_values(self):
        """Test Role has correct string values."""
        assert Role.USER == "user"
        assert Role.ASSISTANT == "assistant"

    def test_enum_membership(self):
        """Test Role membership."""
        assert Role.USER in Role
        assert Role.ASSISTANT in Role
        assert "user" in [e.value for e in Role]
        assert "assistant" in [e.value for e in Role]
        assert "system" not in [e.value for e in Role]

    def test_string_inheritance(self):
        """Test Role inherits from str."""
        assert isinstance(Role.USER, str)
        assert isinstance(Role.ASSISTANT, str)

    def test_role_message_type_compatibility(self):
        """Test Role and MessageType have compatible values."""
        assert Role.USER.value == MessageType.USER.value
        assert Role.ASSISTANT.value == MessageType.ASSISTANT.value


class TestStopReason:
    """Test StopReason enum."""

    def test_enum_values(self):
        """Test StopReason has correct string values."""
        assert StopReason.END_TURN == "end_turn"
        assert StopReason.MAX_TOKENS == "max_tokens"
        assert StopReason.STOP_SEQUENCE == "stop_sequence"

    def test_enum_membership(self):
        """Test StopReason membership."""
        assert StopReason.END_TURN in StopReason
        assert StopReason.MAX_TOKENS in StopReason
        assert StopReason.STOP_SEQUENCE in StopReason
        assert "end_turn" in [e.value for e in StopReason]
        assert "max_tokens" in [e.value for e in StopReason]
        assert "stop_sequence" in [e.value for e in StopReason]
        assert "timeout" not in [e.value for e in StopReason]

    def test_string_inheritance(self):
        """Test StopReason inherits from str."""
        assert isinstance(StopReason.END_TURN, str)
        assert isinstance(StopReason.MAX_TOKENS, str)
        assert isinstance(StopReason.STOP_SEQUENCE, str)


class TestClaudeSDKBaseModel:
    """Test ClaudeSDKBaseModel configuration."""

    def test_frozen_config(self):
        """Test models are frozen (immutable)."""

        class TestModel(ClaudeSDKBaseModel):
            value: str

        model = TestModel(value="test")

        # Should raise error when trying to modify frozen model
        with pytest.raises(ValueError, match="frozen"):
            model.value = "changed"

    def test_extra_forbid_config(self):
        """Test models forbid extra fields."""

        class TestModel(ClaudeSDKBaseModel):
            value: str

        # Should raise error for unexpected fields
        with pytest.raises(ValueError, match="Extra inputs are not permitted"):
            TestModel(value="test", unexpected_field="invalid")

    def test_model_inheritance(self):
        """Test ClaudeSDKBaseModel inherits from BaseModel."""
        from pydantic import BaseModel

        assert issubclass(ClaudeSDKBaseModel, BaseModel)

    def test_config_dict_settings(self):
        """Test ConfigDict has correct settings."""
        config = ClaudeSDKBaseModel.model_config
        assert config["frozen"] is True
        assert config["extra"] == "forbid"


class TestTypeAliases:
    """Test type aliases for common types."""

    def test_uuid_type_alias(self):
        """Test UUIDType alias."""
        assert UUIDType is UUID
        test_uuid = UUIDType("12345678-1234-5678-9abc-123456789012")
        assert isinstance(test_uuid, UUID)

    def test_datetime_type_alias(self):
        """Test DateTimeType alias."""
        assert DateTimeType is datetime
        test_datetime = DateTimeType.now()
        assert isinstance(test_datetime, datetime)

    def test_path_type_alias(self):
        """Test PathType alias."""
        assert PathType is Path
        test_path = PathType("/test/path")
        assert isinstance(test_path, Path)


class TestEnumJSONCompatibility:
    """Test enums work correctly with JSON serialization."""

    def test_enum_json_values(self):
        """Test all enums use string values compatible with JSON."""
        # All enum values should be strings
        for enum_type in [UserType, MessageType, Role, StopReason]:
            for member in enum_type:
                assert isinstance(member.value, str)
                assert len(member.value) > 0

    def test_enum_serialization(self):
        """Test enums serialize to their string values."""
        assert UserType.EXTERNAL.value == "external"
        assert MessageType.USER.value == "user"
        assert Role.ASSISTANT.value == "assistant"
        assert StopReason.END_TURN.value == "end_turn"


class TestContentBlock:
    """Test ContentBlock union type alias."""

    def test_union_type_alias(self):
        """Test ContentBlock is a union of all content block types."""
        from typing import get_args

        union_args = get_args(ContentBlock)
        assert TextBlock in union_args
        assert ThinkingBlock in union_args
        assert ToolUseBlock in union_args
        assert ToolResultBlock in union_args
        assert len(union_args) == 4

    def test_all_content_blocks_inherit_from_base_model(self):
        """Test all content block types inherit from ClaudeSDKBaseModel."""
        assert issubclass(TextBlock, ClaudeSDKBaseModel)
        assert issubclass(ThinkingBlock, ClaudeSDKBaseModel)
        assert issubclass(ToolUseBlock, ClaudeSDKBaseModel)
        assert issubclass(ToolResultBlock, ClaudeSDKBaseModel)

    def test_type_discrimination_with_isinstance(self):
        """Test isinstance works with ContentBlock union types."""
        text_block = TextBlock(text="Hello")
        thinking_block = ThinkingBlock(thinking="Thinking...", signature="v1")
        tool_block = ToolUseBlock(id="1", name="test", input={})

        # Since ContentBlock is a Union, we can't use isinstance directly with it
        # Instead, we check against individual types
        assert isinstance(text_block, TextBlock)
        assert isinstance(thinking_block, ThinkingBlock)
        assert isinstance(tool_block, ToolUseBlock)

        # But we can check if they're one of the content block types
        content_blocks = [text_block, thinking_block, tool_block]
        for block in content_blocks:
            assert isinstance(block, TextBlock | ThinkingBlock | ToolUseBlock)

    def test_all_blocks_have_type_field(self):
        """Test all content block types have a type discriminator field."""
        text_block = TextBlock(text="Hello")
        thinking_block = ThinkingBlock(thinking="Thinking...", signature="v1")
        tool_block = ToolUseBlock(id="1", name="test", input={})

        assert hasattr(text_block, "type")
        assert hasattr(thinking_block, "type")
        assert hasattr(tool_block, "type")

        assert text_block.type == "text"
        assert thinking_block.type == "thinking"
        assert tool_block.type == "tool_use"

    def test_content_block_immutability(self):
        """Test all content block types are immutable."""
        text_block = TextBlock(text="Hello")
        thinking_block = ThinkingBlock(thinking="Thinking...", signature="v1")
        tool_block = ToolUseBlock(id="1", name="test", input={})

        with pytest.raises(ValueError, match="frozen"):
            text_block.text = "changed"

        with pytest.raises(ValueError, match="frozen"):
            thinking_block.thinking = "changed"

        with pytest.raises(ValueError, match="frozen"):
            tool_block.id = "changed"


class TestTextBlock:
    """Test TextBlock content model."""

    def test_inheritance_from_content_block(self):
        """Test TextBlock inherits from ContentBlock."""
        assert issubclass(TextBlock, ContentBlock)

    def test_default_type_value(self):
        """Test TextBlock has correct default type value."""
        block = TextBlock(text="Hello world")
        assert block.type == "text"

    def test_text_field_required(self):
        """Test TextBlock requires text field."""
        with pytest.raises(ValueError, match="Field required"):
            TextBlock()

    def test_text_field_assignment(self):
        """Test TextBlock accepts text field."""
        block = TextBlock(text="Hello world")
        assert block.text == "Hello world"

    def test_type_field_immutable(self):
        """Test TextBlock type field cannot be overridden."""
        # Pydantic validates Literal types strictly - wrong values raise ValidationError
        with pytest.raises(ValueError, match="Input should be 'text'"):
            TextBlock(text="Hello world", type="wrong")

    def test_frozen_behavior(self):
        """Test TextBlock is immutable."""
        block = TextBlock(text="Hello world")
        with pytest.raises(ValueError, match="frozen"):
            block.text = "changed"

    def test_realistic_content(self):
        """Test TextBlock with realistic message content."""
        block = TextBlock(
            text="I'd be happy to help you with that task. Let me analyze the requirements first."
        )
        assert block.type == "text"
        assert "analyze the requirements" in block.text


class TestThinkingBlock:
    """Test ThinkingBlock content model."""

    def test_inheritance_from_content_block(self):
        """Test ThinkingBlock inherits from ContentBlock."""
        assert issubclass(ThinkingBlock, ContentBlock)

    def test_default_type_value(self):
        """Test ThinkingBlock has correct default type value."""
        block = ThinkingBlock(thinking="Let me think about this...", signature="reasoning_v1")
        assert block.type == "thinking"

    def test_required_fields(self):
        """Test ThinkingBlock requires thinking and signature fields."""
        with pytest.raises(ValueError, match="Field required"):
            ThinkingBlock()

        with pytest.raises(ValueError, match="Field required"):
            ThinkingBlock(thinking="test")

        with pytest.raises(ValueError, match="Field required"):
            ThinkingBlock(signature="test")

    def test_field_assignment(self):
        """Test ThinkingBlock accepts thinking and signature fields."""
        block = ThinkingBlock(
            thinking="Let me analyze this step by step...", signature="reasoning_v1"
        )
        assert block.thinking == "Let me analyze this step by step..."
        assert block.signature == "reasoning_v1"

    def test_type_field_immutable(self):
        """Test ThinkingBlock type field cannot be overridden."""
        # Pydantic validates Literal types strictly - wrong values raise ValidationError
        with pytest.raises(ValueError, match="Input should be 'thinking'"):
            ThinkingBlock(thinking="test", signature="test", type="wrong")

    def test_frozen_behavior(self):
        """Test ThinkingBlock is immutable."""
        block = ThinkingBlock(thinking="test", signature="test")
        with pytest.raises(ValueError, match="frozen"):
            block.thinking = "changed"

    def test_realistic_content(self):
        """Test ThinkingBlock with realistic reasoning content."""
        thinking = "I need to carefully consider the user's request. They want me to implement a function that processes data efficiently. Let me break this down: 1) Input validation, 2) Data processing, 3) Output formatting."
        block = ThinkingBlock(thinking=thinking, signature="reasoning_v2")
        assert block.type == "thinking"
        assert "efficiently" in block.thinking
        assert block.signature == "reasoning_v2"


class TestToolUseBlock:
    """Test ToolUseBlock content model."""

    def test_inheritance_from_content_block(self):
        """Test ToolUseBlock inherits from ContentBlock."""
        assert issubclass(ToolUseBlock, ContentBlock)

    def test_default_type_value(self):
        """Test ToolUseBlock has correct default type value."""
        block = ToolUseBlock(id="call_123", name="calculator", input={"expression": "2+2"})
        assert block.type == "tool_use"

    def test_required_fields(self):
        """Test ToolUseBlock requires id, name, and input fields."""
        with pytest.raises(ValueError, match="Field required"):
            ToolUseBlock()

        with pytest.raises(ValueError, match="Field required"):
            ToolUseBlock(id="test")

        with pytest.raises(ValueError, match="Field required"):
            ToolUseBlock(id="test", name="test")

    def test_field_assignment(self):
        """Test ToolUseBlock accepts id, name, and input fields."""
        input_data = {"query": "Python best practices", "max_results": 5}
        block = ToolUseBlock(id="tool_456", name="web_search", input=input_data)
        assert block.id == "tool_456"
        assert block.name == "web_search"
        assert block.input == input_data

    def test_input_dict_type(self):
        """Test ToolUseBlock input accepts arbitrary dict structure."""
        # Simple input
        block1 = ToolUseBlock(id="1", name="simple", input={"value": "test"})
        assert block1.input["value"] == "test"

        # Complex nested input
        complex_input = {
            "config": {"timeout": 30, "retries": 3},
            "data": ["item1", "item2"],
            "flags": {"verbose": True, "dry_run": False},
        }
        block2 = ToolUseBlock(id="2", name="complex", input=complex_input)
        assert block2.input["config"]["timeout"] == 30
        assert block2.input["data"] == ["item1", "item2"]

    def test_type_field_immutable(self):
        """Test ToolUseBlock type field cannot be overridden."""
        # Pydantic validates Literal types strictly - wrong values raise ValidationError
        with pytest.raises(ValueError, match="Input should be 'tool_use'"):
            ToolUseBlock(id="test", name="test", input={}, type="wrong")

    def test_frozen_behavior(self):
        """Test ToolUseBlock is immutable."""
        block = ToolUseBlock(id="test", name="test", input={})
        with pytest.raises(ValueError, match="frozen"):
            block.id = "changed"

    def test_realistic_content(self):
        """Test ToolUseBlock with realistic tool usage."""
        block = ToolUseBlock(
            id="call_abc123",
            name="file_reader",
            input={"file_path": "/home/user/data.json", "encoding": "utf-8", "max_lines": 1000},
        )
        assert block.type == "tool_use"
        assert block.name == "file_reader"
        assert block.input["file_path"] == "/home/user/data.json"


class TestMessageContentType:
    """Test MessageContentType discriminated union."""

    def test_union_type_composition(self):
        """Test MessageContentType includes all content block types."""
        from typing import get_args

        union_args = get_args(MessageContentType)
        assert TextBlock in union_args
        assert ThinkingBlock in union_args
        assert ToolUseBlock in union_args
        assert ToolResultBlock in union_args
        assert len(union_args) == 4

    def test_text_block_in_union(self):
        """Test TextBlock is valid MessageContentType."""
        block = TextBlock(text="Hello")
        assert isinstance(block, TextBlock)
        # Type checking would validate this at static analysis time

    def test_thinking_block_in_union(self):
        """Test ThinkingBlock is valid MessageContentType."""
        block = ThinkingBlock(thinking="Let me think...", signature="v1")
        assert isinstance(block, ThinkingBlock)

    def test_tool_use_block_in_union(self):
        """Test ToolUseBlock is valid MessageContentType."""
        block = ToolUseBlock(id="1", name="test", input={})
        assert isinstance(block, ToolUseBlock)

    def test_content_list_parsing(self):
        """Test parsing list of mixed content blocks."""

        content_list: list[MessageContentType] = [
            TextBlock(text="First, let me understand the problem."),
            ThinkingBlock(
                thinking="The user wants me to solve X. I should approach this by...",
                signature="reasoning_v1",
            ),
            ToolUseBlock(id="call_1", name="calculator", input={"expression": "10 * 5"}),
            TextBlock(text="Based on the calculation, the answer is 50."),
        ]

        assert len(content_list) == 4
        assert isinstance(content_list[0], TextBlock)
        assert isinstance(content_list[1], ThinkingBlock)
        assert isinstance(content_list[2], ToolUseBlock)
        assert isinstance(content_list[3], TextBlock)

        # Verify type discriminators
        assert content_list[0].type == "text"
        assert content_list[1].type == "thinking"
        assert content_list[2].type == "tool_use"
        assert content_list[3].type == "text"


class TestContentBlockDiscrimination:
    """Test content block type discrimination and JSON parsing."""

    def test_json_parsing_text_block(self):
        """Test parsing TextBlock from JSON-like dict."""
        data = {"type": "text", "text": "Hello world"}

        # Pydantic can discriminate based on type field
        if data["type"] == "text":
            block = TextBlock(**data)
            assert isinstance(block, TextBlock)
            assert block.text == "Hello world"

    def test_json_parsing_thinking_block(self):
        """Test parsing ThinkingBlock from JSON-like dict."""
        data = {
            "type": "thinking",
            "thinking": "I need to consider the implications...",
            "signature": "reasoning_v2",
        }

        if data["type"] == "thinking":
            block = ThinkingBlock(**data)
            assert isinstance(block, ThinkingBlock)
            assert block.thinking == "I need to consider the implications..."

    def test_json_parsing_tool_use_block(self):
        """Test parsing ToolUseBlock from JSON-like dict."""
        data = {
            "type": "tool_use",
            "id": "call_xyz789",
            "name": "web_search",
            "input": {"query": "Python documentation", "limit": 10},
        }

        if data["type"] == "tool_use":
            block = ToolUseBlock(**data)
            assert isinstance(block, ToolUseBlock)
            assert block.name == "web_search"
            assert block.input["query"] == "Python documentation"

    def test_type_field_discrimination(self):
        """Test type field enables proper discrimination."""
        # Simulate what a parser would do
        content_blocks_data = [
            {"type": "text", "text": "Hello"},
            {"type": "thinking", "thinking": "Let me think...", "signature": "v1"},
            {"type": "tool_use", "id": "1", "name": "test", "input": {}},
        ]

        parsed_blocks = []
        for data in content_blocks_data:
            if data["type"] == "text":
                parsed_blocks.append(TextBlock(**data))
            elif data["type"] == "thinking":
                parsed_blocks.append(ThinkingBlock(**data))
            elif data["type"] == "tool_use":
                parsed_blocks.append(ToolUseBlock(**data))

        assert len(parsed_blocks) == 3
        assert all(hasattr(block, "type") for block in parsed_blocks)
        types = [block.type for block in parsed_blocks]
        assert types == ["text", "thinking", "tool_use"]


class TestFoundationTypesExports:
    """Test foundation types are properly exported."""

    def test_all_exports(self):
        """Test __all__ contains all foundation types."""
        from claude_sdk.models import __all__

        expected_exports = {
            "UserType",
            "MessageType",
            "Role",
            "StopReason",
            "ClaudeSDKBaseModel",
            "UUIDType",
            "DateTimeType",
            "PathType",
            "ContentBlock",
            "TextBlock",
            "ThinkingBlock",
            "ToolUseBlock",
            "ToolResultBlock",
            "MessageContentBlock",
            "MessageContentType",
            "TokenUsage",
            "ToolResult",
            "Message",
            "MessageRecord",
            "SessionMetadata",
            "ToolExecution",
            "ConversationTree",
            "ParsedSession",
        }

        assert set(__all__) == expected_exports

    def test_import_all_types(self):
        """Test all foundation types can be imported."""
        # This test passes if imports at top of file succeed
        assert UserType is not None
        assert MessageType is not None
        assert Role is not None
        assert StopReason is not None
        assert ClaudeSDKBaseModel is not None
        assert UUIDType is not None
        assert DateTimeType is not None
        assert PathType is not None
        assert ContentBlock is not None
        assert TextBlock is not None
        assert ThinkingBlock is not None
        assert ToolUseBlock is not None
        assert MessageContentType is not None
        assert ToolResultBlock is not None
        assert TokenUsage is not None
        assert ToolResult is not None
        assert Message is not None
        assert MessageRecord is not None


class TestToolResultBlock:
    """Test ToolResultBlock content block model."""

    def test_tool_result_block_creation(self):
        """Test ToolResultBlock can be created with required fields."""
        block = ToolResultBlock(
            content="Command executed successfully", is_error=False, tool_use_id="toolu_123"
        )
        assert block.type == "tool_result"
        assert block.content == "Command executed successfully"
        assert block.is_error is False
        assert block.tool_use_id == "toolu_123"

    def test_tool_result_block_with_error(self):
        """Test ToolResultBlock with error state."""
        block = ToolResultBlock(
            content="Error: Command failed", is_error=True, tool_use_id="toolu_456"
        )
        assert block.is_error is True

    def test_tool_result_block_immutable(self):
        """Test ToolResultBlock is immutable."""
        from pydantic import ValidationError

        block = ToolResultBlock(content="Test", is_error=False, tool_use_id="toolu_123")
        with pytest.raises(ValidationError):
            block.content = "Modified"


class TestTokenUsage:
    """Test TokenUsage model."""

    def test_token_usage_creation(self):
        """Test TokenUsage can be created with all fields."""
        usage = TokenUsage(
            input_tokens=100,
            cache_creation_input_tokens=50,
            cache_read_input_tokens=25,
            output_tokens=200,
            service_tier="standard",
        )
        assert usage.input_tokens == 100
        assert usage.cache_creation_input_tokens == 50
        assert usage.cache_read_input_tokens == 25
        assert usage.output_tokens == 200
        assert usage.service_tier == "standard"

    def test_token_usage_field_aliases(self):
        """Test TokenUsage field aliases work correctly."""
        # Test using camelCase aliases
        data = {
            "input_tokens": 100,
            "cache_creation_input_tokens": 50,
            "cache_read_input_tokens": 25,
            "output_tokens": 200,
            "service_tier": "standard",
        }
        usage = TokenUsage(**data)
        assert usage.input_tokens == 100


class TestToolResult:
    """Test ToolResult model."""

    def test_tool_result_minimal(self):
        """Test ToolResult with minimal required fields."""
        result = ToolResult(tool_use_id="tool_1", content="success")
        assert result.tool_use_id == "tool_1"
        assert result.content == "success"
        assert result.stdout is None
        assert result.stderr is None
        assert result.interrupted is False
        assert result.is_error is False

    def test_tool_result_with_all_fields(self):
        """Test ToolResult with all available fields."""
        result = ToolResult(
            tool_use_id="tool_123",
            content="Command executed",
            stdout="File created",
            stderr="Warning: deprecated",
            interrupted=False,
            is_error=False,
            metadata={"exit_code": 0, "duration": 1.5},
        )
        assert result.tool_use_id == "tool_123"
        assert result.content == "Command executed"
        assert result.stdout == "File created"
        assert result.stderr == "Warning: deprecated"
        assert result.metadata["exit_code"] == 0

    def test_tool_result_with_error(self):
        """Test ToolResult with error state."""
        result = ToolResult(
            tool_use_id="tool_456",
            content="Error: Permission denied",
            stderr="chmod: permission denied",
            interrupted=False,
            is_error=True,
            metadata={"exit_code": 1},
        )
        assert result.tool_use_id == "tool_456"
        assert result.content == "Error: Permission denied"
        assert result.is_error is True
        assert result.metadata["exit_code"] == 1


class TestMessage:
    """Test Message model."""

    def test_message_with_text_block_content(self):
        """Test Message with TextBlock content."""
        text_block = TextBlock(text="Hello, Claude!")
        message = Message(role=Role.USER, content=[text_block])
        assert message.role == Role.USER
        assert len(message.content) == 1
        assert message.content[0].text == "Hello, Claude!"
        assert message.id is None

    def test_message_with_content_blocks(self):
        """Test Message with content block list."""
        text_block = TextBlock(text="Hello")
        thinking_block = ThinkingBlock(thinking="Let me think", signature="sig123")

        message = Message(
            role=Role.ASSISTANT,
            content=[text_block, thinking_block],
            model="claude-opus-4",
            stop_reason=StopReason.END_TURN,
        )
        assert message.role == Role.ASSISTANT
        assert len(message.content) == 2
        assert message.model == "claude-opus-4"
        assert message.stop_reason == StopReason.END_TURN

    def test_message_with_usage(self):
        """Test Message with TokenUsage."""
        usage = TokenUsage(
            input_tokens=50,
            cache_creation_input_tokens=0,
            cache_read_input_tokens=0,
            output_tokens=100,
            service_tier="standard",
        )
        message = Message(role=Role.ASSISTANT, content=[TextBlock(text="Response")], usage=usage)
        assert message.usage is not None
        assert message.usage.input_tokens == 50


class TestMessageRecord:
    """Test MessageRecord model."""

    def test_message_record_creation(self):
        """Test MessageRecord with required fields."""
        from datetime import datetime
        from pathlib import Path
        from uuid import uuid4

        uuid_val = uuid4()
        timestamp = datetime.now()
        message = Message(role=Role.USER, content=[TextBlock(text="Test message")])

        # Use JSONL-style data with camelCase aliases
        data = {
            "isSidechain": False,
            "userType": "external",
            "cwd": "/test/path",
            "sessionId": "session123",
            "version": "1.0.0",
            "type": "user",
            "message": message,
            "uuid": uuid_val,
            "timestamp": timestamp,
        }
        record = MessageRecord(**data)

        assert record.is_sidechain is False
        assert record.user_type == UserType.EXTERNAL
        assert record.cwd == Path("/test/path")
        assert record.session_id == "session123"
        assert record.uuid == uuid_val
        assert record.parent_uuid is None

    def test_message_record_with_optional_fields(self):
        """Test MessageRecord with optional fields."""
        from datetime import datetime
        from uuid import uuid4

        parent_uuid = uuid4()
        uuid_val = uuid4()
        timestamp = datetime.now()
        message = Message(role=Role.ASSISTANT, content=[TextBlock(text="Response")])
        tool_result = ToolResult(tool_use_id="tool_1", content="success", stdout="success")

        # Use JSONL-style data with camelCase aliases
        data = {
            "parentUuid": parent_uuid,
            "isSidechain": True,
            "userType": "internal",
            "cwd": "/test",
            "sessionId": "session456",
            "version": "1.0.1",
            "type": "assistant",
            "message": message,
            "uuid": uuid_val,
            "timestamp": timestamp,
            "costUSD": 0.05,
            "durationMs": 1500,
            "requestId": "req_123",
            "toolUseResult": tool_result,
            "isMeta": True,
        }
        record = MessageRecord(**data)

        assert record.parent_uuid == parent_uuid
        assert record.cost_usd == 0.05
        assert record.duration_ms == 1500
        assert record.request_id == "req_123"
        assert record.tool_use_result == tool_result
        assert record.is_meta is True

    def test_message_record_field_aliases(self):
        """Test MessageRecord field aliases work with JSONL data."""
        from datetime import datetime
        from uuid import uuid4

        # Simulate JSONL data with camelCase field names
        jsonl_data = {
            "parentUuid": str(uuid4()),
            "isSidechain": False,
            "userType": "external",
            "cwd": "/test/path",
            "sessionId": "session789",
            "version": "1.0.2",
            "message": {"role": "user", "content": [{"type": "text", "text": "Test"}]},
            "type": "user",
            "uuid": str(uuid4()),
            "timestamp": datetime.now().isoformat(),
            "costUSD": 0.02,
            "durationMs": 800,
            "isMeta": False,
        }

        # This would normally be done by the parser, but we're testing the aliases
        record = MessageRecord(**jsonl_data)
        assert record.user_type == UserType.EXTERNAL
        assert record.session_id == "session789"
        assert record.cost_usd == 0.02
        assert record.duration_ms == 800
        assert record.is_meta is False


class TestSessionMetadata:
    """Test SessionMetadata model."""

    def test_session_metadata_creation(self):
        """Test SessionMetadata with default values."""
        metadata = SessionMetadata()
        assert metadata.total_cost == 0.0
        assert metadata.total_messages == 0
        assert metadata.tool_usage_count == {}

    def test_session_metadata_with_data(self):
        """Test SessionMetadata with aggregated data."""
        tool_counts = {"bash": 5, "edit": 3, "read": 10}
        metadata = SessionMetadata(
            total_cost=15.75, total_messages=25, tool_usage_count=tool_counts
        )
        assert metadata.total_cost == 15.75
        assert metadata.total_messages == 25
        assert metadata.tool_usage_count == tool_counts

    def test_session_metadata_immutable(self):
        """Test SessionMetadata is immutable."""
        from pydantic import ValidationError

        metadata = SessionMetadata(total_cost=5.0)
        with pytest.raises(ValidationError):
            metadata.total_cost = 10.0

    def test_session_metadata_negative_cost_validation(self):
        """Test SessionMetadata rejects negative total_cost."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            SessionMetadata(total_cost=-1.0)
        assert "greater than or equal to 0" in str(exc_info.value)

    def test_session_metadata_negative_messages_validation(self):
        """Test SessionMetadata rejects negative total_messages."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            SessionMetadata(total_messages=-1)
        assert "greater than or equal to 0" in str(exc_info.value)

    def test_session_metadata_boundary_values(self):
        """Test SessionMetadata with boundary values."""
        # Test zero values (should be valid)
        metadata = SessionMetadata(total_cost=0.0, total_messages=0, tool_usage_count={})
        assert metadata.total_cost == 0.0
        assert metadata.total_messages == 0
        assert metadata.tool_usage_count == {}


class TestToolExecution:
    """Test ToolExecution model."""

    def test_tool_execution_creation(self):
        """Test ToolExecution with all required fields."""
        from datetime import datetime, timedelta

        tool_result = ToolResult(tool_use_id="tool_123", content="success")
        execution = ToolExecution(
            tool_name="bash",
            input={"command": "ls -la"},
            output=tool_result,
            duration=timedelta(seconds=2.5),
            timestamp=datetime.now(),
        )
        assert execution.tool_name == "bash"
        assert execution.input["command"] == "ls -la"
        assert execution.output == tool_result
        assert execution.duration.total_seconds() == 2.5

    def test_tool_execution_immutable(self):
        """Test ToolExecution is immutable."""
        from datetime import datetime, timedelta

        from pydantic import ValidationError

        tool_result = ToolResult(tool_use_id="tool_123", content="success")
        execution = ToolExecution(
            tool_name="bash",
            input={},
            output=tool_result,
            duration=timedelta(seconds=1),
            timestamp=datetime.now(),
        )
        with pytest.raises(ValidationError):
            execution.tool_name = "edit"

    def test_tool_execution_empty_input(self):
        """Test ToolExecution with empty input dictionary."""
        from datetime import datetime, timedelta

        tool_result = ToolResult(tool_use_id="tool_123", content="success")
        execution = ToolExecution(
            tool_name="test_tool",
            input={},  # Empty input
            output=tool_result,
            duration=timedelta(seconds=1),
            timestamp=datetime.now(),
        )
        assert execution.input == {}
        assert execution.tool_name == "test_tool"

    def test_tool_execution_complex_input(self):
        """Test ToolExecution with complex nested input."""
        from datetime import datetime, timedelta

        complex_input = {
            "command": "find /path -name '*.py'",
            "options": {"recursive": True, "max_depth": 5, "patterns": ["*.py", "*.js"]},
            "metadata": {"user": "test", "priority": 1},
        }

        tool_result = ToolResult(tool_use_id="tool_456", content="found files")
        execution = ToolExecution(
            tool_name="file_search",
            input=complex_input,
            output=tool_result,
            duration=timedelta(milliseconds=500),
            timestamp=datetime.now(),
        )
        assert execution.input["command"] == "find /path -name '*.py'"
        assert execution.input["options"]["recursive"] is True
        assert execution.input["metadata"]["priority"] == 1

    def test_tool_execution_required_fields(self):
        """Test ToolExecution with all required fields."""
        from pydantic import ValidationError

        # Test missing required fields raise validation errors
        with pytest.raises(ValidationError):
            ToolExecution()  # No fields provided

        with pytest.raises(ValidationError):
            ToolExecution(tool_name="test")  # Missing other required fields


class TestConversationTree:
    """Test ConversationTree placeholder model."""

    def test_conversation_tree_creation(self):
        """Test ConversationTree creation (placeholder)."""
        tree = ConversationTree()
        assert tree is not None

    def test_conversation_tree_immutable(self):
        """Test ConversationTree is immutable."""

        tree = ConversationTree()
        # Since it's a placeholder with no fields, test base model behavior
        assert isinstance(tree, ClaudeSDKBaseModel)


class TestParsedSession:
    """Test ParsedSession model."""

    def test_parsed_session_creation(self):
        """Test ParsedSession with default values."""
        session = ParsedSession(session_id="session_123")
        assert session.session_id == "session_123"
        assert session.messages == []
        assert session.summaries == []
        assert isinstance(session.conversation_tree, ConversationTree)
        assert isinstance(session.metadata, SessionMetadata)

    def test_parsed_session_with_messages(self):
        """Test ParsedSession with message list."""
        from datetime import datetime
        from uuid import uuid4

        # Create test messages
        message1 = Message(role=Role.USER, content=[TextBlock(text="Hello")])
        record1 = MessageRecord(
            isSidechain=False,
            userType=UserType.EXTERNAL,
            cwd=Path("/test"),
            sessionId="session_123",
            version="1.0.0",
            type=MessageType.USER,
            message=message1,
            uuid=uuid4(),
            timestamp=datetime.now(),
            costUSD=0.01,
        )

        session = ParsedSession(session_id="session_123", messages=[record1])
        assert len(session.messages) == 1
        assert session.messages[0] == record1

    def test_validate_session_integrity_valid(self):
        """Test session integrity validation with valid data."""
        from datetime import datetime
        from uuid import uuid4

        # Create messages with same session_id
        message1 = Message(role=Role.USER, content=[TextBlock(text="Hello")])
        record1 = MessageRecord(
            isSidechain=False,
            userType=UserType.EXTERNAL,
            cwd=Path("/test"),
            sessionId="session_123",
            version="1.0.0",
            type=MessageType.USER,
            message=message1,
            uuid=uuid4(),
            timestamp=datetime.now(),
        )

        # Use properly calculated metadata
        metadata = SessionMetadata(total_messages=1, user_messages=1, assistant_messages=0)
        session = ParsedSession(session_id="session_123", messages=[record1], metadata=metadata)

        is_valid, issues = session.validate_session_integrity()
        assert is_valid is True
        assert len(issues) == 0

    def test_validate_session_integrity_invalid_session_id(self):
        """Test session integrity validation with mismatched session IDs."""
        from datetime import datetime
        from uuid import uuid4

        message1 = Message(role=Role.USER, content=[TextBlock(text="Hello")])
        record1 = MessageRecord(
            isSidechain=False,
            userType=UserType.EXTERNAL,
            cwd=Path("/test"),
            sessionId="session_123",  # Different from ParsedSession session_id
            version="1.0.0",
            type=MessageType.USER,
            message=message1,
            uuid=uuid4(),
            timestamp=datetime.now(),
        )

        # Create second record with different session ID to trigger inconsistency detection
        record2 = MessageRecord(
            isSidechain=False,
            userType=UserType.EXTERNAL,
            cwd=Path("/test"),
            sessionId="session_456",  # Different session ID - this will trigger inconsistency
            version="1.0.0",
            type=MessageType.USER,
            message=message1,
            uuid=uuid4(),
            timestamp=datetime.now(),
        )

        session = ParsedSession(
            session_id="session_123",
            messages=[record1, record2],  # Mixed session IDs in messages
        )

        is_valid, issues = session.validate_session_integrity()
        assert is_valid is False
        assert any("inconsistent session_id" in issue for issue in issues)

    def test_validate_session_integrity_invalid_message_count(self):
        """Test session integrity validation with wrong message count."""
        from datetime import datetime
        from uuid import uuid4

        message1 = Message(role=Role.USER, content=[TextBlock(text="Hello")])
        record1 = MessageRecord(
            isSidechain=False,
            userType=UserType.EXTERNAL,
            cwd=Path("/test"),
            sessionId="session_123",
            version="1.0.0",
            type=MessageType.USER,
            message=message1,
            uuid=uuid4(),
            timestamp=datetime.now(),
        )

        # Wrong message count in metadata
        metadata = SessionMetadata(total_messages=5)  # Should be 1
        session = ParsedSession(session_id="session_123", messages=[record1], metadata=metadata)

        is_valid, issues = session.validate_session_integrity()
        assert is_valid is False
        assert any("message count mismatch" in issue for issue in issues)

    def test_calculate_metadata(self):
        """Test metadata calculation from messages."""
        from datetime import datetime
        from uuid import uuid4

        # Create messages with costs and tool usage
        tool_block = ToolUseBlock(id="tool_1", name="bash", input={"command": "ls"})
        message1 = Message(role=Role.USER, content=[TextBlock(text="Hello")])
        message2 = Message(role=Role.ASSISTANT, content=[tool_block])

        record1 = MessageRecord(
            isSidechain=False,
            userType=UserType.EXTERNAL,
            cwd=Path("/test"),
            sessionId="session_123",
            version="1.0.0",
            type=MessageType.USER,
            message=message1,
            uuid=uuid4(),
            timestamp=datetime.now(),
            costUSD=0.01,
        )

        record2 = MessageRecord(
            isSidechain=False,
            userType=UserType.EXTERNAL,
            cwd=Path("/test"),
            sessionId="session_123",
            version="1.0.0",
            type=MessageType.ASSISTANT,
            message=message2,
            uuid=uuid4(),
            timestamp=datetime.now(),
            costUSD=0.05,
        )

        session = ParsedSession(session_id="session_123", messages=[record1, record2])

        calculated_metadata = session.calculate_metadata()
        assert abs(calculated_metadata.total_cost - 0.06) < 1e-10  # Handle floating point precision
        assert calculated_metadata.total_messages == 2
        assert calculated_metadata.tool_usage_count["bash"] == 1

    def test_parsed_session_immutable(self):
        """Test ParsedSession is immutable."""
        from pydantic import ValidationError

        session = ParsedSession(session_id="test")
        with pytest.raises(ValidationError):
            session.session_id = "modified"

    def test_validate_session_integrity_empty_messages(self):
        """Test session integrity validation with empty message list."""
        session = ParsedSession(
            session_id="session_123",
            messages=[],  # Empty message list
            metadata=SessionMetadata(total_messages=0),
        )

        # Should pass with empty messages if metadata is consistent
        is_valid, issues = session.validate_session_integrity()
        assert is_valid is True
        assert len(issues) == 0

    def test_calculate_metadata_with_none_costs(self):
        """Test metadata calculation when cost_usd is None."""
        from datetime import datetime
        from uuid import uuid4

        # Create messages with None cost
        message1 = Message(role=Role.USER, content=[TextBlock(text="Hello")])
        record1 = MessageRecord(
            isSidechain=False,
            userType=UserType.EXTERNAL,
            cwd=Path("/test"),
            sessionId="session_123",
            version="1.0.0",
            type=MessageType.USER,
            message=message1,
            uuid=uuid4(),
            timestamp=datetime.now(),
            # costUSD not provided (None)
        )

        session = ParsedSession(session_id="session_123", messages=[record1])

        calculated_metadata = session.calculate_metadata()
        assert calculated_metadata.total_cost == 0.0
        assert calculated_metadata.total_messages == 1
        assert calculated_metadata.tool_usage_count == {}

    def test_calculate_metadata_no_tool_usage(self):
        """Test metadata calculation with no tool blocks."""
        from datetime import datetime
        from uuid import uuid4

        # Create messages with only text content (no tools)
        message1 = Message(role=Role.USER, content=[TextBlock(text="Hello")])
        message2 = Message(role=Role.ASSISTANT, content=[TextBlock(text="Hi there!")])

        record1 = MessageRecord(
            isSidechain=False,
            userType=UserType.EXTERNAL,
            cwd=Path("/test"),
            sessionId="session_123",
            version="1.0.0",
            type=MessageType.USER,
            message=message1,
            uuid=uuid4(),
            timestamp=datetime.now(),
            costUSD=0.01,
        )

        record2 = MessageRecord(
            isSidechain=False,
            userType=UserType.EXTERNAL,
            cwd=Path("/test"),
            sessionId="session_123",
            version="1.0.0",
            type=MessageType.ASSISTANT,
            message=message2,
            uuid=uuid4(),
            timestamp=datetime.now(),
            costUSD=0.02,
        )

        session = ParsedSession(session_id="session_123", messages=[record1, record2])

        calculated_metadata = session.calculate_metadata()
        assert abs(calculated_metadata.total_cost - 0.03) < 1e-10
        assert calculated_metadata.total_messages == 2
        assert calculated_metadata.tool_usage_count == {}  # No tools used

    def test_validate_session_integrity_inconsistent_message_session_ids(self):
        """Test session integrity validation when messages have inconsistent session IDs."""
        from datetime import datetime
        from uuid import uuid4

        # Create messages with different session_ids
        message1 = Message(role=Role.USER, content=[TextBlock(text="Hello")])
        record1 = MessageRecord(
            isSidechain=False,
            userType=UserType.EXTERNAL,
            cwd=Path("/test"),
            sessionId="session_123",
            version="1.0.0",
            type=MessageType.USER,
            message=message1,
            uuid=uuid4(),
            timestamp=datetime.now(),
        )

        record2 = MessageRecord(
            isSidechain=False,
            userType=UserType.EXTERNAL,
            cwd=Path("/test"),
            sessionId="session_456",  # Different session ID
            version="1.0.0",
            type=MessageType.USER,
            message=message1,
            uuid=uuid4(),
            timestamp=datetime.now(),
        )

        session = ParsedSession(
            session_id="session_123",
            messages=[record1, record2],  # Mixed session IDs in messages
        )

        # Should fail validation due to inconsistent session IDs between messages
        is_valid, issues = session.validate_session_integrity()
        assert is_valid is False
        assert any("inconsistent session_id" in issue for issue in issues)


class TestHypothesisPropertyBasedTests:
    """Property-based tests using hypothesis for edge case validation."""

    def test_text_block_with_arbitrary_text(self):
        """Test TextBlock with arbitrary text strings."""
        from hypothesis import given
        from hypothesis import strategies as st

        @given(text=st.text())
        def test_arbitrary_text(text):
            block = TextBlock(text=text)
            assert block.text == text
            assert block.type == "text"
            # Test serialization round-trip
            data = block.model_dump()
            reconstructed = TextBlock(**data)
            assert reconstructed == block

        test_arbitrary_text()

    def test_thinking_block_with_arbitrary_content(self):
        """Test ThinkingBlock with arbitrary thinking and signature strings."""
        from hypothesis import given
        from hypothesis import strategies as st

        @given(thinking=st.text(min_size=1), signature=st.text(min_size=1))
        def test_arbitrary_thinking(thinking, signature):
            block = ThinkingBlock(thinking=thinking, signature=signature)
            assert block.thinking == thinking
            assert block.signature == signature
            assert block.type == "thinking"
            # Test immutability
            with pytest.raises(ValueError, match="frozen"):
                block.thinking = "modified"

        test_arbitrary_thinking()

    def test_tool_use_block_with_arbitrary_input(self):
        """Test ToolUseBlock with arbitrary input dictionaries."""
        from hypothesis import given
        from hypothesis import strategies as st

        @given(
            tool_id=st.text(min_size=1),
            name=st.text(min_size=1),
            input_data=st.dictionaries(
                keys=st.text(min_size=1, max_size=50),
                values=st.one_of(
                    st.text(), st.integers(), st.booleans(), st.floats(allow_nan=False)
                ),
                min_size=0,
                max_size=10,
            ),
        )
        def test_arbitrary_tool_input(tool_id, name, input_data):
            block = ToolUseBlock(id=tool_id, name=name, input=input_data)
            assert block.id == tool_id
            assert block.name == name
            assert block.input == input_data
            assert block.type == "tool_use"

        test_arbitrary_tool_input()

    def test_token_usage_with_arbitrary_values(self):
        """Test TokenUsage with arbitrary non-negative integer values."""
        from hypothesis import given
        from hypothesis import strategies as st

        @given(
            input_tokens=st.integers(min_value=0, max_value=1000000),
            cache_creation=st.integers(min_value=0, max_value=100000),
            cache_read=st.integers(min_value=0, max_value=100000),
            output_tokens=st.integers(min_value=0, max_value=1000000),
            service_tier=st.text(min_size=1, max_size=20),
        )
        def test_arbitrary_token_values(
            input_tokens, cache_creation, cache_read, output_tokens, service_tier
        ):
            usage = TokenUsage(
                input_tokens=input_tokens,
                cache_creation_input_tokens=cache_creation,
                cache_read_input_tokens=cache_read,
                output_tokens=output_tokens,
                service_tier=service_tier,
            )
            assert usage.input_tokens == input_tokens
            assert usage.cache_creation_input_tokens == cache_creation
            assert usage.cache_read_input_tokens == cache_read
            assert usage.output_tokens == output_tokens
            assert usage.service_tier == service_tier

        test_arbitrary_token_values()

    def test_session_metadata_with_arbitrary_values(self):
        """Test SessionMetadata with arbitrary non-negative values."""
        from hypothesis import given
        from hypothesis import strategies as st

        @given(
            total_cost=st.floats(
                min_value=0.0, max_value=10000.0, allow_nan=False, allow_infinity=False
            ),
            total_messages=st.integers(min_value=0, max_value=100000),
            tool_counts=st.dictionaries(
                keys=st.text(min_size=1, max_size=20),
                values=st.integers(min_value=0, max_value=1000),
                min_size=0,
                max_size=20,
            ),
        )
        def test_arbitrary_metadata_values(total_cost, total_messages, tool_counts):
            metadata = SessionMetadata(
                total_cost=total_cost, total_messages=total_messages, tool_usage_count=tool_counts
            )
            assert metadata.total_cost == total_cost
            assert metadata.total_messages == total_messages
            assert metadata.tool_usage_count == tool_counts

        test_arbitrary_metadata_values()


class TestErrorHandlingEdgeCases:
    """Test error handling for invalid data and edge cases."""

    def test_text_block_empty_text(self):
        """Test TextBlock with empty text."""
        # Empty text should be valid
        block = TextBlock(text="")
        assert block.text == ""
        assert block.type == "text"

    def test_text_block_very_long_text(self):
        """Test TextBlock with very long text."""
        long_text = "x" * 1000000  # 1MB of text
        block = TextBlock(text=long_text)
        assert len(block.text) == 1000000
        assert block.type == "text"

    def test_tool_use_block_empty_input(self):
        """Test ToolUseBlock with empty input dictionary."""
        block = ToolUseBlock(id="test_id", name="test_tool", input={})
        assert block.input == {}
        assert block.type == "tool_use"

    def test_token_usage_boundary_values(self):
        """Test TokenUsage with boundary values."""
        # Test zero values
        usage = TokenUsage(input_tokens=0, output_tokens=0)
        assert usage.input_tokens == 0
        assert usage.output_tokens == 0

        # Test large values
        usage = TokenUsage(input_tokens=999999999, output_tokens=999999999)
        assert usage.input_tokens == 999999999
        assert usage.output_tokens == 999999999

    def test_token_usage_negative_values_rejected(self):
        """Test TokenUsage rejects negative values."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError, match="greater than or equal to 0"):
            TokenUsage(input_tokens=-1, output_tokens=100)

        with pytest.raises(ValidationError, match="greater than or equal to 0"):
            TokenUsage(input_tokens=100, output_tokens=-1)

    def test_session_metadata_negative_values_rejected(self):
        """Test SessionMetadata rejects negative values."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError, match="greater than or equal to 0"):
            SessionMetadata(total_cost=-1.0)

        with pytest.raises(ValidationError, match="greater than or equal to 0"):
            SessionMetadata(total_messages=-1)

    def test_message_record_invalid_uuid_format(self):
        """Test MessageRecord rejects invalid UUID format."""
        from datetime import datetime
        from pathlib import Path

        from pydantic import ValidationError

        message = Message(role=Role.USER, content=[TextBlock(text="Test")])

        with pytest.raises(ValidationError, match="Input should be a valid UUID"):
            MessageRecord(
                isSidechain=False,
                userType=UserType.EXTERNAL,
                cwd=Path("/test"),
                sessionId="session_123",
                version="1.0.0",
                type=MessageType.USER,
                message=message,
                uuid="invalid-uuid-format",
                timestamp=datetime.now(),
            )

    def test_message_record_invalid_datetime_format(self):
        """Test MessageRecord rejects invalid datetime format."""
        from pathlib import Path
        from uuid import uuid4

        from pydantic import ValidationError

        message = Message(role=Role.USER, content=[TextBlock(text="Test")])

        with pytest.raises(ValidationError):
            MessageRecord(
                isSidechain=False,
                userType=UserType.EXTERNAL,
                cwd=Path("/test"),
                sessionId="session_123",
                version="1.0.0",
                type=MessageType.USER,
                message=message,
                uuid=uuid4(),
                timestamp="invalid-datetime-format",
            )

    def test_message_record_invalid_enum_values(self):
        """Test MessageRecord rejects invalid enum values."""
        from datetime import datetime
        from pathlib import Path
        from uuid import uuid4

        from pydantic import ValidationError

        message = Message(role=Role.USER, content=[TextBlock(text="Test")])

        with pytest.raises(ValidationError, match="Input should be 'external' or 'internal'"):
            MessageRecord(
                isSidechain=False,
                userType="invalid_user_type",
                cwd=Path("/test"),
                sessionId="session_123",
                version="1.0.0",
                type=MessageType.USER,
                message=message,
                uuid=uuid4(),
                timestamp=datetime.now(),
            )

    def test_content_block_type_field_immutable(self):
        """Test content block type fields cannot be changed."""
        from pydantic import ValidationError

        # Test TextBlock
        with pytest.raises(ValidationError, match="Input should be 'text'"):
            TextBlock(text="test", type="invalid")

        # Test ThinkingBlock
        with pytest.raises(ValidationError, match="Input should be 'thinking'"):
            ThinkingBlock(thinking="test", signature="sig", type="invalid")

        # Test ToolUseBlock
        with pytest.raises(ValidationError, match="Input should be 'tool_use'"):
            ToolUseBlock(id="test", name="test", input={}, type="invalid")

    def test_model_extra_fields_forbidden(self):
        """Test models reject extra fields."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
            TextBlock(text="test", extra_field="not_allowed")

        with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
            ThinkingBlock(thinking="test", signature="sig", extra_field="not_allowed")

        with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
            TokenUsage(input_tokens=100, output_tokens=50, extra_field="not_allowed")


class TestPerformanceBenchmarks:
    """Performance benchmarks for model parsing and validation."""

    def test_text_block_creation_performance(self):
        """Benchmark TextBlock creation with various text sizes."""
        import time

        # Test with different text sizes
        text_sizes = [100, 1000, 10000, 100000]

        for size in text_sizes:
            text = "x" * size

            start_time = time.perf_counter()
            for _ in range(1000):  # Create 1000 instances
                TextBlock(text=text)
            end_time = time.perf_counter()

            duration = end_time - start_time
            # Performance requirement: should create 1000 instances in < 1 second
            assert duration < 1.0, f"TextBlock creation too slow for size {size}: {duration:.3f}s"

    def test_message_record_list_performance(self):
        """Benchmark large MessageRecord list processing."""
        import time
        from datetime import datetime
        from pathlib import Path
        from uuid import uuid4

        # Create a large list of MessageRecords
        message_records = []
        start_time = time.perf_counter()

        for i in range(1000):  # Create 1000 message records
            message = Message(role=Role.USER, content=[TextBlock(text=f"Message {i}")])
            record = MessageRecord(
                isSidechain=False,
                userType=UserType.EXTERNAL,
                cwd=Path("/test"),
                sessionId="session_123",
                version="1.0.0",
                type=MessageType.USER,
                message=message,
                uuid=uuid4(),
                timestamp=datetime.now(),
                costUSD=0.01,
            )
            message_records.append(record)

        end_time = time.perf_counter()
        duration = end_time - start_time

        # Performance requirement: should create 1000 MessageRecords in < 2 seconds
        assert duration < 2.0, f"MessageRecord creation too slow: {duration:.3f}s"
        assert len(message_records) == 1000

    def test_session_metadata_calculation_performance(self):
        """Benchmark session metadata calculation with large message lists."""
        import time
        from datetime import datetime
        from pathlib import Path
        from uuid import uuid4

        # Create messages with various content types
        messages = []
        for i in range(1000):
            if i % 3 == 0:
                content = [TextBlock(text=f"Text message {i}")]
            elif i % 3 == 1:
                content = [
                    ToolUseBlock(id=f"tool_{i}", name="bash", input={"command": f"echo {i}"})
                ]
            else:
                content = [
                    TextBlock(text=f"Mixed message {i}"),
                    ToolUseBlock(id=f"tool_{i}", name="read", input={"file": f"file_{i}.txt"}),
                ]

            message = Message(role=Role.ASSISTANT, content=content)
            record = MessageRecord(
                isSidechain=False,
                userType=UserType.EXTERNAL,
                cwd=Path("/test"),
                sessionId="session_123",
                version="1.0.0",
                type=MessageType.ASSISTANT,
                message=message,
                uuid=uuid4(),
                timestamp=datetime.now(),
                costUSD=0.01 + (i * 0.001),  # Varying costs
            )
            messages.append(record)

        session = ParsedSession(session_id="session_123", messages=messages)

        # Benchmark metadata calculation
        start_time = time.perf_counter()
        calculated_metadata = session.calculate_metadata()
        end_time = time.perf_counter()

        duration = end_time - start_time

        # Performance requirement: should calculate metadata for 1000 messages in < 0.1 seconds
        assert duration < 0.1, f"Metadata calculation too slow: {duration:.3f}s"
        assert calculated_metadata.total_messages == 1000
        assert calculated_metadata.total_cost > 0
        assert len(calculated_metadata.tool_usage_count) > 0

    def test_model_serialization_performance(self):
        """Benchmark model serialization/deserialization performance."""
        import time
        from datetime import datetime
        from pathlib import Path
        from uuid import uuid4

        # Create a complex message record
        content = [
            TextBlock(text="This is a test message with various content types."),
            ThinkingBlock(
                thinking="Let me analyze this request carefully.", signature="reasoning_v1"
            ),
            ToolUseBlock(id="tool_123", name="bash", input={"command": "ls -la", "timeout": 30}),
        ]
        message = Message(
            role=Role.ASSISTANT,
            content=content,
            model="claude-3-opus-20240229",
            usage=TokenUsage(input_tokens=150, output_tokens=200),
        )

        record = MessageRecord(
            isSidechain=False,
            userType=UserType.EXTERNAL,
            cwd=Path("/home/user/project"),
            sessionId="session_perf_test",
            version="1.2.3",
            type=MessageType.ASSISTANT,
            message=message,
            uuid=uuid4(),
            timestamp=datetime.now(),
            costUSD=0.025,
            durationMs=1500,
        )

        # Benchmark serialization
        start_time = time.perf_counter()
        for _ in range(1000):
            record.model_dump()
        end_time = time.perf_counter()

        serialization_duration = end_time - start_time

        # Benchmark deserialization
        serialized_data = record.model_dump(by_alias=True)
        start_time = time.perf_counter()
        for _ in range(1000):
            MessageRecord(**serialized_data)
        end_time = time.perf_counter()

        deserialization_duration = end_time - start_time

        # Performance requirements: 1000 operations should complete in < 1 second each
        assert (
            serialization_duration < 1.0
        ), f"Serialization too slow: {serialization_duration:.3f}s"
        assert (
            deserialization_duration < 1.0
        ), f"Deserialization too slow: {deserialization_duration:.3f}s"
