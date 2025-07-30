"""
Optimization data analysis example.

This example demonstrates how to extract performance data from Claude Code sessions
to optimize your workflow. It calculates various metrics like token efficiency,
cost per operation, and tool usage patterns.
"""

from pathlib import Path

from claude_sdk import find_sessions, load


def analyze_tool_efficiency(session_path: str | Path) -> dict:
    """Analyze the efficiency of different tools in a session.

    Args:
        session_path: Path to the session file

    Returns:
        Dictionary with tool efficiency metrics
    """
    session = load(session_path)

    # Extract tool usage
    tool_count: dict[str, int] = {}
    tool_cost: dict[str, float] = {}
    tool_tokens: dict[str, int] = {}
    tool_duration: dict[str, int] = {}

    for execution in session.tool_executions:
        tool_name = execution.tool_name

        # Count occurrences
        tool_count[tool_name] = tool_count.get(tool_name, 0) + 1

        # Add cost if available
        if execution.cost:
            tool_cost[tool_name] = tool_cost.get(tool_name, 0.0) + execution.cost

        # Track token usage
        if execution.tokens:
            tool_tokens[tool_name] = tool_tokens.get(tool_name, 0) + execution.tokens

        # Track duration
        if execution.duration_ms:
            tool_duration[tool_name] = tool_duration.get(tool_name, 0) + execution.duration_ms

    # Calculate efficiency metrics
    efficiency_metrics = {}
    for tool in tool_count:
        efficiency_metrics[tool] = {
            "count": tool_count.get(tool, 0),
            "total_cost": tool_cost.get(tool, 0.0),
            "cost_per_use": tool_cost.get(tool, 0.0) / tool_count.get(tool, 1),
            "total_tokens": tool_tokens.get(tool, 0),
            "tokens_per_use": tool_tokens.get(tool, 0) / tool_count.get(tool, 1),
            "total_duration_ms": tool_duration.get(tool, 0),
            "avg_duration_ms": tool_duration.get(tool, 0) / tool_count.get(tool, 1),
        }

    return efficiency_metrics


def analyze_bulk_sessions() -> tuple[dict, dict, set[str]]:
    """Analyze all available sessions to find optimization opportunities.

    Returns:
        Tuple containing:
        - Tool efficiency metrics across all sessions
        - Session performance metrics
        - Set of all tools used
    """
    # Find all sessions
    session_paths = find_sessions()
    print(f"Found {len(session_paths)} sessions to analyze")

    # Aggregate metrics
    all_tool_metrics: dict[str, dict] = {}
    session_metrics: dict[str, dict] = {}
    all_tools: set[str] = set()

    # Process each session
    for i, path in enumerate(session_paths):
        try:
            session = load(path)
            session_id = session.session_id

            # Get tool efficiency for this session
            tool_metrics = analyze_tool_efficiency(path)

            # Merge with overall metrics
            for tool, metrics in tool_metrics.items():
                all_tools.add(tool)
                if tool not in all_tool_metrics:
                    all_tool_metrics[tool] = {
                        "count": 0,
                        "total_cost": 0.0,
                        "total_tokens": 0,
                        "total_duration_ms": 0,
                    }

                all_tool_metrics[tool]["count"] += metrics["count"]
                all_tool_metrics[tool]["total_cost"] += metrics["total_cost"]
                all_tool_metrics[tool]["total_tokens"] += metrics["total_tokens"]
                all_tool_metrics[tool]["total_duration_ms"] += metrics["total_duration_ms"]

            # Store session metrics
            session_metrics[session_id] = {
                "total_cost": session.total_cost,
                "message_count": len(session.messages),
                "tools_used": len(session.tools_used),
                "duration": session.duration.total_seconds() if session.duration else None,
                "cost_per_message": session.total_cost / len(session.messages)
                if session.messages
                else 0,
            }

            # Show progress for long runs
            if (i + 1) % 10 == 0:
                print(f"Processed {i + 1}/{len(session_paths)} sessions...")

        except Exception as e:
            print(f"Error processing {path}: {e}")
            continue

    # Calculate averages across all sessions
    for tool in all_tool_metrics:
        count = all_tool_metrics[tool]["count"]
        if count > 0:
            all_tool_metrics[tool]["avg_cost_per_use"] = (
                all_tool_metrics[tool]["total_cost"] / count
            )
            all_tool_metrics[tool]["avg_tokens_per_use"] = (
                all_tool_metrics[tool]["total_tokens"] / count
            )
            all_tool_metrics[tool]["avg_duration_ms"] = (
                all_tool_metrics[tool]["total_duration_ms"] / count
            )

    return all_tool_metrics, session_metrics, all_tools


def print_optimization_report(tool_metrics: dict, session_metrics: dict, all_tools: set[str]):
    """Print a comprehensive optimization report.

    Args:
        tool_metrics: Tool efficiency metrics
        session_metrics: Session performance metrics
        all_tools: Set of all tools used
    """
    print("\n===== CLAUDE CODE OPTIMIZATION REPORT =====")

    # 1. Most expensive tools
    print("\n1. MOST EXPENSIVE TOOLS (by total cost)")
    expensive_tools = sorted(
        [(k, v["total_cost"]) for k, v in tool_metrics.items()], key=lambda x: x[1], reverse=True
    )
    for tool, cost in expensive_tools[:5]:
        print(f"  {tool}: ${cost:.4f}")

    # 2. Most expensive tools per use
    print("\n2. MOST EXPENSIVE TOOLS (per use)")
    expensive_per_use = sorted(
        [(k, v.get("avg_cost_per_use", 0)) for k, v in tool_metrics.items()],
        key=lambda x: x[1],
        reverse=True,
    )
    for tool, cost in expensive_per_use[:5]:
        print(f"  {tool}: ${cost:.4f} per use")

    # 3. Slowest tools
    print("\n3. SLOWEST TOOLS (average duration)")
    slowest_tools = sorted(
        [(k, v.get("avg_duration_ms", 0)) for k, v in tool_metrics.items()],
        key=lambda x: x[1],
        reverse=True,
    )
    for tool, duration in slowest_tools[:5]:
        print(f"  {tool}: {duration:.0f}ms average")

    # 4. Most used tools
    print("\n4. MOST FREQUENTLY USED TOOLS")
    frequent_tools = sorted(
        [(k, v["count"]) for k, v in tool_metrics.items()], key=lambda x: x[1], reverse=True
    )
    for tool, count in frequent_tools[:5]:
        print(f"  {tool}: {count} uses")

    # 5. Session statistics
    print("\n5. SESSION STATISTICS")
    total_sessions = len(session_metrics)
    total_cost = sum(s["total_cost"] for s in session_metrics.values())
    avg_cost = total_cost / total_sessions if total_sessions > 0 else 0

    print(f"  Total sessions: {total_sessions}")
    print(f"  Total cost: ${total_cost:.2f}")
    print(f"  Average cost per session: ${avg_cost:.2f}")
    print(f"  Total unique tools used: {len(all_tools)}")

    # 6. Optimization recommendations
    print("\n6. OPTIMIZATION RECOMMENDATIONS")

    # Identify expensive and frequently used tools
    high_impact_tools = []
    for tool, metrics in tool_metrics.items():
        if metrics["count"] >= 10 and metrics.get("avg_cost_per_use", 0) >= 0.001:
            high_impact_tools.append((tool, metrics["count"], metrics.get("avg_cost_per_use", 0)))

    high_impact_tools.sort(key=lambda x: x[1] * x[2], reverse=True)

    if high_impact_tools:
        print("  High-impact tools to optimize:")
        for tool, count, cost_per_use in high_impact_tools[:3]:
            print(
                f"  - {tool}: Used {count} times at ${cost_per_use:.4f} each (${count * cost_per_use:.4f} total)"
            )

    # Additional insights
    print("\n7. ADDITIONAL INSIGHTS")
    if expensive_per_use and expensive_per_use[0][1] > 0.01:
        print(
            f"  • Consider avoiding {expensive_per_use[0][0]} when possible (${expensive_per_use[0][1]:.4f} per use)"
        )

    if slowest_tools and slowest_tools[0][1] > 2000:
        print(
            f"  • {slowest_tools[0][0]} is particularly slow ({slowest_tools[0][1]:.0f}ms on average)"
        )

    print("\n===========================================")


if __name__ == "__main__":
    print("Claude Code SDK - Optimization Analysis Example")
    print("----------------------------------------------")

    # Run the analysis
    tool_metrics, session_metrics, all_tools = analyze_bulk_sessions()

    # Print the report
    print_optimization_report(tool_metrics, session_metrics, all_tools)
