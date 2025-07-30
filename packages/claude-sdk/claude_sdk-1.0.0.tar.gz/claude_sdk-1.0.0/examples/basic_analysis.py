"""Basic session analysis example.

This example demonstrates how to use the Claude SDK to:
1. Find Claude Code session files
2. Load a session
3. Analyze basic session properties like cost and message counts
4. Work with individual messages
"""

from pathlib import Path

from claude_sdk import find_sessions, load


def analyze_session(session_path):
    """Analyze a single Claude Code session."""
    print(f"\nAnalyzing session: {session_path}")
    print("-" * 50)

    # Load the session
    session = load(session_path)

    # Display basic session properties
    print(f"Session ID: {session.session_id}")
    print(f"Total messages: {len(session.messages)}")
    print(f"Total cost: ${session.total_cost:.4f}")
    print(f"Tools used: {', '.join(session.tools_used) if session.tools_used else 'None'}")

    if session.duration:
        print(f"Session duration: {session.duration}")

    # Message analysis
    user_messages = session.get_messages_by_role("user")
    assistant_messages = session.get_messages_by_role("assistant")

    print("\nMessage breakdown:")
    print(f"  User messages: {len(user_messages)}")
    print(f"  Assistant messages: {len(assistant_messages)}")

    # Tool usage analysis if tools were used
    if session.tools_used:
        print("\nTool usage:")
        for tool in sorted(session.tools_used):
            # Use the metadata for tool counts
            count = session.metadata.tool_usage_count.get(tool, 0)
            print(f"  {tool}: {count} uses")

    # Print first few message exchanges
    max_preview = 3  # Show up to 3 message pairs
    print("\nConversation preview:")

    # Get the main conversation chain (no sidechains)
    main_chain = session.get_main_chain()
    for _i, msg in enumerate(main_chain[: max_preview * 2]):
        # Use the simplified Message properties for cleaner access
        text = msg.text
        if len(text) > 100:
            text = text[:97] + "..."
        print(f"  {msg.role}: {text}")

        # Show cost for assistant messages if available
        if msg.role == "assistant" and msg.cost:
            print(f"    Cost: ${msg.cost:.4f}")

        # Show tools used in this message
        if msg.tools:
            print(f"    Tools: {', '.join(msg.tools)}")


def main():
    """Main function for basic analysis example."""
    # Try to find session files
    try:
        # First look in fixtures for test data
        fixtures_dir = Path(__file__).parent.parent / "tests" / "fixtures"
        session_files = find_sessions(fixtures_dir)

        if not session_files:
            # If no fixtures, look in default location
            print("No session files found in fixtures, checking ~/.claude/projects/")
            session_files = find_sessions()
    except Exception as e:
        print(f"Error finding session files: {e}")
        return

    if not session_files:
        print("No Claude Code session files found.")
        return

    print(f"Found {len(session_files)} session files:")
    for i, path in enumerate(session_files):
        print(f"{i + 1}. {path.name}")

    # Analyze first session as an example
    if session_files:
        analyze_session(session_files[0])


if __name__ == "__main__":
    main()
