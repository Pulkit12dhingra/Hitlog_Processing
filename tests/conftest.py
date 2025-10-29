"""Pytest fixtures for CLI tests."""

from __future__ import annotations

import os
from pathlib import Path

import pytest


@pytest.fixture
def sample_csv_path(tmp_path: Path) -> Path:
    """Create a minimal sample CSV for testing CLI functionality."""
    csv_path = tmp_path / "sample_hitlog.csv"
    csv_content = """\
page_name,page_url,user_id,timestamp
Article A,/articles/a,u001,2025-10-27 10:00:00
Register,/register,u001,2025-10-27 10:05:00
Article A,/articles/a,u002,2025-10-27 11:00:00
Article B,/articles/b,u002,2025-10-27 11:02:00
Register,/register,u002,2025-10-27 11:10:00
Article B,/articles/b,u003,2025-10-27 12:00:00
Register,/register,u003,2025-10-27 12:05:00
Article C,/articles/c,u004,2025-10-27 13:00:00
"""
    csv_path.write_text(csv_content)
    return csv_path


@pytest.fixture
def outputs_dir(tmp_path: Path) -> Path:
    """Create a temporary directory for test outputs."""
    output_dir = tmp_path / "outputs"
    output_dir.mkdir(exist_ok=True)
    return output_dir


@pytest.fixture
def run_cli_env() -> dict:
    """Return environment variables for running CLI commands."""
    env = os.environ.copy()
    # Ensure PYTHONPATH includes src directory if needed
    return env
