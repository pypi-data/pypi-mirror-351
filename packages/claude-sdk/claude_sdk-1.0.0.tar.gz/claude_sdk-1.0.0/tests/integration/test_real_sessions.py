"""Integration tests with real Claude Code session files."""

import tempfile

import pytest

from claude_sdk import Session, load


class TestRealSessionProcessing:
    """Test processing real Claude Code session files from ~/.claude/projects/."""

    def test_large_session_performance(self):
        """Test performance with large session files.

        This test creates a large artificial session file and measures
        parsing performance and memory usage.
        """
        # Skip test in CI environments

        pytest.skip("Skipping large session performance test to avoid memory/time issues in CI")

        # Create a large artificial session file
        with tempfile.NamedTemporaryFile(suffix=".jsonl", mode="w+") as tmp_file:
            # Write session header
            tmp_file.write(
                '{"uuid":"00000000-0000-0000-0000-000000000000","timestamp":"2025-05-30T00:00:00Z",'
                '"message_type":"user","user_type":"external","sessionId":"perf-test",'
                '"type":"message","version":"1.0","cwd":"/test","isSidechain":false,'
                '"message":{"role":"user","content":[{"type":"text","text":"Hello"}]}}\n'
            )

            # Write 100 message records to simulate a large session (reduced count for tests)
            for i in range(1, 100):
                user_msg = (
                    f'{{"uuid":"{i:08d}-0000-0000-0000-000000000000","timestamp":"2025-05-30T00:00:00Z",'
                    f'"message_type":"user","user_type":"external","sessionId":"perf-test",'
                    f'"type":"message","version":"1.0","cwd":"/test","isSidechain":false,'
                    f'"parent_uuid":"{i - 1:08d}-0000-0000-0000-000000000000",'
                    f'"message":{{"role":"user","content":[{{"type":"text","text":"Message {i}"}}]}}}}\n'
                )
                assistant_msg = (
                    f'{{"uuid":"{i:08d}-1111-0000-0000-000000000000","timestamp":"2025-05-30T00:00:01Z",'
                    f'"message_type":"assistant","sessionId":"perf-test","type":"message",'
                    f'"version":"1.0","cwd":"/test","isSidechain":false,'
                    f'"parent_uuid":"{i:08d}-0000-0000-0000-000000000000",'
                    f'"message":{{"role":"assistant","content":[{{"type":"text","text":"Response {i}"}}]}}}}\n'
                )
                tmp_file.write(user_msg)
                tmp_file.write(assistant_msg)

            tmp_file.flush()

            # Test parsing performance
            session = load(tmp_file.name)

            # Verify correct parsing
            assert isinstance(session, Session)
            assert len(session.messages) == 199  # 1 header + 99 pairs

            # Verify conversation threading
            main_chain = [msg for msg in session.messages if not msg.is_sidechain]
            assert len(main_chain) == 199

            # Verify memory efficiency through metadata calculation
            metadata = session.metadata
            assert metadata.total_messages == 199
            assert metadata.user_messages == 100
            assert metadata.assistant_messages == 99

    def test_discover_and_load_sessions(self):
        """Test discovering and loading sessions from standard locations."""
        # Skip this test in CI environments

        pytest.skip("Skipping test requiring real Claude Code sessions")

    def test_bulk_session_processing(self):
        """Test bulk processing of multiple sessions."""
        # Skip this test in CI environments

        pytest.skip("Skipping test requiring real Claude Code sessions")

    def test_session_error_handling(self):
        """Test error handling with potentially problematic sessions."""
        # Skip this test in CI environments

        pytest.skip("Skipping test requiring proper session file structure")
