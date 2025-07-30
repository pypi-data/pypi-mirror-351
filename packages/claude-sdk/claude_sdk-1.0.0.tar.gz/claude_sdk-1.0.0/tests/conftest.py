"""Pytest configuration and shared fixtures."""

from pathlib import Path

import pytest


@pytest.fixture
def fixtures_dir() -> Path:
    """Return path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_session_file(fixtures_dir: Path) -> Path:
    """Return path to sample session file (will be added later)."""
    return fixtures_dir / "sample_session.jsonl"
