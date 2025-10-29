from __future__ import annotations

from dataclasses import dataclass, field
from typing import Set


@dataclass(slots=True)
class Node:
    """Graph node keyed by page_url, with accumulated influence count."""

    url: str
    name: str
    neighbors: Set[str] = field(default_factory=set)  # store neighbor URLs
    weight: int = 0
