"""Batch processing example.

This example demonstrates how to use the Claude SDK to:
1. Find and process multiple Claude Code sessions
2. Extract aggregate statistics across sessions
3. Identify patterns and trends in tool usage
4. Compare costs across different sessions
"""

from collections import Counter

from claude_sdk import find_sessions, load


def batch_analyze_sessions(max_sessions=5):
    """Analyze multiple Claude Code sessions and extract aggregate statistics."""
    print("Finding Claude Code sessions...")
    session_paths = find_sessions()

    if not session_paths:
        print("No Claude Code sessions found.")
        return

    print(f"Found {len(session_paths)} sessions.")
    print(f"Analyzing up to {max_sessions} most recent sessions...\n")

    # Limit to most recent sessions
    sessions_to_analyze = min(len(session_paths), max_sessions)
    paths = session_paths[:sessions_to_analyze]

    # Collect aggregate statistics
    total_cost = 0.0
    total_messages = 0
    total_tools_used = 0
    all_tools = []
    session_info = []

    # Process each session
    for path in paths:
        try:
            print(f"Loading session: {path.name}")
            session = load(path)

            # Collect basic session info
            messages_count = len(session.messages)
            tools_count = len(session.tools_used)
            tool_list = list(session.tools_used)

            # Track statistics
            total_cost += session.total_cost
            total_messages += messages_count
            total_tools_used += tools_count
            all_tools.extend(tool_list)

            # Add to session info collection
            session_info.append(
                {
                    "id": session.session_id,
                    "messages": messages_count,
                    "tools": tools_count,
                    "cost": session.total_cost,
                    "duration": session.duration,
                    "path": path,
                }
            )

            print(f"  ID: {session.session_id}")
            print(f"  Messages: {messages_count}")
            print(f"  Tools used: {tools_count}")
            print(f"  Cost: ${session.total_cost:.4f}")
            print()

        except Exception as e:
            print(f"Error processing {path.name}: {e}")
            print()

    # Skip aggregate analysis if no sessions were loaded
    if not session_info:
        print("No sessions were successfully loaded.")
        return

    # Calculate and display aggregate statistics
    print("\n=== Aggregate Statistics ===")
    print(f"Total sessions analyzed: {len(session_info)}")
    print(f"Total cost: ${total_cost:.4f}")
    print(f"Average cost per session: ${total_cost / len(session_info):.4f}")
    print(f"Total messages: {total_messages}")
    print(f"Average messages per session: {total_messages / len(session_info):.1f}")

    # Tool usage analysis
    tool_counts = Counter(all_tools)
    print("\n=== Tool Usage Across All Sessions ===")
    for tool, count in tool_counts.most_common():
        print(f"  {tool}: {count} uses")

    # Cost analysis by session
    print("\n=== Sessions by Cost ===")
    for i, info in enumerate(sorted(session_info, key=lambda x: x["cost"], reverse=True), 1):
        print(f"{i}. ${info['cost']:.4f} - {info['id']} ({info['messages']} messages)")


def main():
    """Main function for batch processing example."""
    batch_analyze_sessions(max_sessions=5)


if __name__ == "__main__":
    main()
