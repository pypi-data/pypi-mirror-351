"""Performance benchmarks for the Claude SDK.

This module contains performance benchmarks for parsing and processing
Claude Code session files of various sizes.
"""

import json
import tempfile
import time
from pathlib import Path

from claude_sdk import Session
from claude_sdk.parser import parse_complete_session


def create_test_session(
    message_count: int, tool_count: int, message_size: int
) -> tuple[Path, dict]:
    """Create a test session file with specified characteristics.

    Args:
        message_count: Number of message pairs (user + assistant)
        tool_count: Number of tool uses per assistant message
        message_size: Approximate size of each message in characters

    Returns:
        Tuple containing the path to the created file and benchmark metadata
    """
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as tmp_file:
        tmp_path = Path(tmp_file.name)

    # Create message text with specified size
    message_text = "A" * message_size

    # Generate messages
    start_time = time.time()

    with tmp_path.open("w") as f:
        # Write initial user message
        user_msg = {
            "uuid": "00000000-0000-0000-0000-000000000000",
            "timestamp": "2025-05-30T00:00:00Z",
            "message_type": "user",
            "user_type": "external",
            "message": {"role": "user", "content": [{"type": "text", "text": message_text}]},
        }
        f.write(json.dumps(user_msg) + "\n")

        # Write message pairs
        for i in range(1, message_count):
            # User message
            user_uuid = f"{i:08d}-0000-0000-0000-000000000000"
            parent_uuid = (
                f"{i - 1:08d}-1111-0000-0000-000000000000"
                if i > 1
                else "00000000-0000-0000-0000-000000000000"
            )

            user_msg = {
                "uuid": user_uuid,
                "timestamp": f"2025-05-30T{i // 60:02d}:{i % 60:02d}:00Z",
                "message_type": "user",
                "user_type": "external",
                "parent_uuid": parent_uuid,
                "message": {"role": "user", "content": [{"type": "text", "text": message_text}]},
            }
            f.write(json.dumps(user_msg) + "\n")

            # Assistant message with tool uses
            assistant_uuid = f"{i:08d}-1111-0000-0000-000000000000"

            # Create tool content blocks
            content = []
            for t in range(tool_count):
                tool_block = {
                    "type": "tool_use",
                    "tool_use_id": f"tool_{i}_{t}",
                    "name": f"Tool{t}",
                    "input": {"query": f"input_{t}"},
                }
                content.append(tool_block)

                # Add tool result
                tool_result = {
                    "uuid": f"{i:08d}-2222-{t:04d}-0000-000000000000",
                    "timestamp": f"2025-05-30T{i // 60:02d}:{i % 60:02d}:01Z",
                    "message_type": "user",
                    "user_type": "internal",
                    "parent_uuid": assistant_uuid,
                    "tool_use_id": f"tool_{i}_{t}",
                    "tool_use_result": {"output": f"result_{t}", "is_error": False},
                }
                f.write(json.dumps(tool_result) + "\n")

            # Add text response
            content.append({"type": "text", "text": message_text})

            # Write assistant message
            assistant_msg = {
                "uuid": assistant_uuid,
                "timestamp": f"2025-05-30T{i // 60:02d}:{i % 60:02d}:02Z",
                "message_type": "assistant",
                "parent_uuid": user_uuid,
                "message": {"role": "assistant", "content": content},
            }
            f.write(json.dumps(assistant_msg) + "\n")

    generation_time = time.time() - start_time

    # Calculate file size
    file_size = tmp_path.stat().st_size

    # Return file path and metadata
    return tmp_path, {
        "message_count": message_count,
        "tool_count": tool_count,
        "message_size": message_size,
        "file_size_bytes": file_size,
        "file_size_mb": file_size / (1024 * 1024),
        "generation_time_seconds": generation_time,
    }


def benchmark_parsing(file_path: Path, metadata: dict) -> dict:
    """Benchmark session parsing performance.

    Args:
        file_path: Path to the session file
        metadata: Session metadata from create_test_session

    Returns:
        Dictionary with benchmark results
    """
    # Measure parsing time
    start_time = time.time()
    parsed_session = parse_complete_session(file_path)
    parsing_time = time.time() - start_time

    # Measure conversion to Session time
    start_time = time.time()
    session = Session.from_parsed_session(parsed_session)
    conversion_time = time.time() - start_time

    # Measure metadata calculation time
    start_time = time.time()
    _ = session.metadata
    metadata_time = time.time() - start_time

    # Measure tool extraction time
    start_time = time.time()
    _ = session.tool_executions
    tool_extraction_time = time.time() - start_time

    # Clean up
    import contextlib

    # Import inside function to avoid module-level import
    with contextlib.suppress(Exception):
        file_path.unlink()

    # Return benchmark results
    return {
        **metadata,
        "parsing_time_seconds": parsing_time,
        "conversion_time_seconds": conversion_time,
        "metadata_calculation_time_seconds": metadata_time,
        "tool_extraction_time_seconds": tool_extraction_time,
        "total_processing_time_seconds": parsing_time
        + conversion_time
        + metadata_time
        + tool_extraction_time,
        "messages_per_second": metadata["message_count"] / parsing_time if parsing_time > 0 else 0,
        "mb_per_second": metadata["file_size_mb"] / parsing_time if parsing_time > 0 else 0,
    }


def run_benchmarks() -> list[dict]:
    """Run a series of benchmarks with different file sizes and characteristics.

    Returns:
        List of benchmark results
    """
    benchmarks = []

    # Test configurations
    configs = [
        # Small session (few messages, small size)
        {"message_count": 10, "tool_count": 1, "message_size": 100, "description": "Small session"},
        # Medium session (moderate messages, moderate size)
        {
            "message_count": 50,
            "tool_count": 2,
            "message_size": 500,
            "description": "Medium session",
        },
        # Large session (many messages, larger size)
        {
            "message_count": 200,
            "tool_count": 3,
            "message_size": 1000,
            "description": "Large session",
        },
        # Tool-heavy session (moderate messages, many tools)
        {
            "message_count": 50,
            "tool_count": 10,
            "message_size": 500,
            "description": "Tool-heavy session",
        },
        # Text-heavy session (moderate messages, large text)
        {
            "message_count": 50,
            "tool_count": 2,
            "message_size": 5000,
            "description": "Text-heavy session",
        },
    ]

    # Run benchmarks for each configuration
    for config in configs:
        print(f"Running benchmark: {config['description']}")

        # Create test file
        file_path, metadata = create_test_session(
            config["message_count"], config["tool_count"], config["message_size"]
        )

        # Add description
        metadata["description"] = config["description"]

        # Run benchmark
        result = benchmark_parsing(file_path, metadata)
        benchmarks.append(result)

        # Print result
        print(f"  File size: {result['file_size_mb']:.2f} MB")
        print(f"  Parse time: {result['parsing_time_seconds']:.3f} seconds")
        print(f"  Processing speed: {result['mb_per_second']:.2f} MB/sec")
        print()

    return benchmarks


def print_benchmark_report(results: list[dict]):
    """Print a formatted report of benchmark results.

    Args:
        results: List of benchmark results
    """
    print("\n===== CLAUDE SDK PERFORMANCE BENCHMARK REPORT =====")
    print("\nFile Sizes:")
    for result in results:
        print(f"  {result['description']}: {result['file_size_mb']:.2f} MB")

    print("\nParsing Performance:")
    for result in results:
        print(
            f"  {result['description']}: {result['parsing_time_seconds']:.3f} sec "
            + f"({result['mb_per_second']:.2f} MB/sec, {result['messages_per_second']:.1f} msgs/sec)"
        )

    print("\nMetadata Calculation Performance:")
    for result in results:
        print(f"  {result['description']}: {result['metadata_calculation_time_seconds']:.3f} sec")

    print("\nTool Extraction Performance:")
    for result in results:
        print(f"  {result['description']}: {result['tool_extraction_time_seconds']:.3f} sec")

    print("\nTotal Processing Performance:")
    for result in results:
        print(f"  {result['description']}: {result['total_processing_time_seconds']:.3f} sec")

    print("\n====================================================")


if __name__ == "__main__":
    print("Claude SDK Performance Benchmarks")
    print("--------------------------------")

    # Run benchmarks
    results = run_benchmarks()

    # Print report
    print_benchmark_report(results)
