from __future__ import annotations

from typing import TypedDict


class OutputRow(TypedDict):
    """Typed representation of an output row."""

    page_name: str
    page_url: str
    total: int
