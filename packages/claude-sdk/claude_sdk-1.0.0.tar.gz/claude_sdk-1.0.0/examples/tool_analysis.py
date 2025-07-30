"""Tool usage analysis example.

This example demonstrates how to use the Claude SDK to:
1. Load a session
2. Analyze tool usage patterns
3. Calculate tool costs
4. Extract detailed tool execution information
5. Find patterns in tool success/failure rates
"""

from collections import Counter, defaultdict
from pathlib import Path

from claude_sdk import find_sessions, load


def analyze_tool_usage(session_path):
    """Analyze tool usage in a Claude Code session."""
    print(f"\nAnalyzing tool usage in session: {session_path}")
    print("-" * 60)

    # Load the session
    session = load(session_path)

    # Skip if no tools used
    if not session.tools_used:
        print("No tools were used in this session.")
        return

    # Basic tool usage statistics
    print(f"Total tools used: {len(session.tools_used)}")
    print(f"Tool types: {', '.join(sorted(session.tools_used))}")

    # Count tool usage by type
    tool_counts = Counter()
    for msg in session.messages:
        for tool in msg.tools:
            tool_counts[tool] += 1

    print("\nTool usage by type:")
    for tool, count in tool_counts.most_common():
        print(f"  {tool}: {count} uses")

    # Cost analysis if costs are available
    if session.tool_costs:
        print("\nTool costs:")
        total_tool_cost = sum(session.tool_costs.values())
        for tool, cost in sorted(session.tool_costs.items(), key=lambda x: x[1], reverse=True):
            percentage = (cost / total_tool_cost * 100) if total_tool_cost else 0
            print(f"  {tool}: ${cost:.4f} ({percentage:.1f}%)")

    # Analyze tool usage patterns by message sequence
    print("\nTool usage patterns:")

    # Track message indices where tools are used
    tool_positions = defaultdict(list)
    for i, msg in enumerate(session.messages):
        for tool in msg.tools:
            tool_positions[tool].append(i)

    # Calculate tool distribution across conversation
    if tool_positions:
        total_messages = len(session.messages)
        print(f"  Distribution across {total_messages} messages:")
        for tool, positions in sorted(tool_positions.items()):
            # Calculate where in the conversation this tool appears
            if positions:
                first_use = min(positions)
                last_use = max(positions)
                first_pct = (first_use / total_messages) * 100
                last_pct = (last_use / total_messages) * 100
                print(
                    f"  {tool}: {len(positions)} uses, first at msg #{first_use + 1} ({first_pct:.1f}%), last at msg #{last_use + 1} ({last_pct:.1f}%)"
                )

    # Find tool sequences (which tools are commonly used together)
    tool_pairs = Counter()
    for i in range(len(session.messages) - 1):
        if session.messages[i].tools and session.messages[i + 1].tools:
            for tool1 in session.messages[i].tools:
                for tool2 in session.messages[i + 1].tools:
                    tool_pairs[(tool1, tool2)] += 1

    if tool_pairs:
        print("\nCommon tool sequences:")
        for (tool1, tool2), count in tool_pairs.most_common(3):
            print(f"  {tool1} → {tool2}: {count} times")

    # Success/failure analysis
    success_count = 0
    error_count = 0
    error_by_tool = Counter()

    # Analyze detailed tool executions
    if session.tool_executions:
        print(f"\nAnalyzing {len(session.tool_executions)} tool executions:")

        for execution in session.tool_executions:
            # Check if the tool execution resulted in an error
            is_error = hasattr(execution.output, "is_error") and execution.output.is_error

            if is_error:
                error_count += 1
                error_by_tool[execution.tool_name] += 1
            else:
                success_count += 1

        # Calculate success rate
        total_executions = success_count + error_count
        if total_executions > 0:
            success_rate = (success_count / total_executions) * 100
            print(f"  Overall success rate: {success_rate:.1f}%")
            print(f"  Successful executions: {success_count}")
            print(f"  Failed executions: {error_count}")

            # Show error rates by tool
            if error_count > 0:
                print("\nError rates by tool:")
                for tool in sorted(session.tools_used):
                    tool_errors = error_by_tool.get(tool, 0)
                    tool_total = tool_counts.get(tool, 0)
                    if tool_total > 0:
                        error_rate = (tool_errors / tool_total) * 100
                        print(
                            f"  {tool}: {error_rate:.1f}% error rate ({tool_errors}/{tool_total})"
                        )

        # Show a sample of tool executions
        max_samples = min(3, len(session.tool_executions))
        print(f"\nSample of {max_samples} tool executions:")

        for i, execution in enumerate(session.tool_executions[:max_samples]):
            is_error = hasattr(execution.output, "is_error") and execution.output.is_error
            status = "❌ ERROR" if is_error else "✓ Success"

            print(f"\nExecution {i + 1}: {status}")
            print(f"  Tool: {execution.tool_name}")
            if execution.duration:
                print(f"  Duration: {execution.duration}")

            # Show a preview of the input
            input_str = str(execution.input)
            if len(input_str) > 100:
                input_str = input_str[:97] + "..."
            print(f"  Input: {input_str}")

            # For most tool executions, show a preview of the output
            if hasattr(execution.output, "content"):
                content = execution.output.content
                if content and len(str(content)) > 100:
                    content = str(content)[:97] + "..."
                print(f"  Output: {content}")

            if is_error:
                print(f"  Error: {getattr(execution.output, 'error_type', 'Unknown')}")


def main():
    """Main function for tool analysis example."""
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

    # Find a session with tool usage
    tool_sessions = []
    for path in session_files:
        try:
            session = load(path)
            if session.tools_used:
                tool_sessions.append((path, len(session.tool_executions)))
        except Exception as e:
            print(f"Error loading {path}: {e}")

    if not tool_sessions:
        print("No sessions with tool usage found.")
        return

    # Sort by tool usage count and analyze the session with most tools
    tool_sessions.sort(key=lambda x: x[1], reverse=True)

    print(f"Found {len(tool_sessions)} sessions with tool usage:")
    for i, (path, count) in enumerate(tool_sessions):
        print(f"{i + 1}. {path.name}: {count} tool executions")

    # Analyze the session with the most tool usage
    most_tools_path = tool_sessions[0][0]
    analyze_tool_usage(most_tools_path)


if __name__ == "__main__":
    main()
