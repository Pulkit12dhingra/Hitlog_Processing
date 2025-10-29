from __future__ import annotations

from typing import Dict, List

import pandas as pd

from telegraph_ranker.domain import OutputRow
from telegraph_ranker.io_utils import ARTICLE_PREFIX, REG_URL
from telegraph_ranker.models.node import Node


def _build_nodes(df: pd.DataFrame) -> Dict[str, Node]:
    """Create Node registry for all encountered pages."""
    nodes: Dict[str, Node] = {}
    for _, row in df.iterrows():
        url = row["page_url"]
        if url not in nodes:
            nodes[url] = Node(url=url, name=row["page_name"])
    return nodes


def _link_edges(df: pd.DataFrame, nodes: Dict[str, Node]) -> None:
    """Create directed edges between consecutive pages per user."""
    for _uid, grp in df.groupby("user_id", sort=False):
        prev_url: str | None = None
        for _, row in grp.iterrows():
            cur_url = row["page_url"]
            if prev_url is not None:
                nodes[prev_url].neighbors.add(cur_url)
            prev_url = cur_url


def _accumulate_weights(df: pd.DataFrame, nodes: Dict[str, Node]) -> None:
    """Traverse user journeys and assign +1 to seen article nodes upon registration."""
    for _uid, grp in df.groupby("user_id", sort=False):
        seen_in_journey: set[str] = set()
        for _, row in grp.iterrows():
            url = row["page_url"]

            if url.startswith(ARTICLE_PREFIX) and url not in seen_in_journey:
                seen_in_journey.add(url)

            if url == REG_URL:
                for art_url in seen_in_journey:
                    nodes[art_url].weight += 1
                seen_in_journey.clear()


def build_ranking(df: pd.DataFrame) -> pd.DataFrame:
    """
    Graph-based approach:
    - Build Node objects and edges from consecutive events per user.
    - Apply the same freeze/commit journey rule used in the timestamp approach.
    - Return article weights as a sorted DataFrame.
    """
    nodes = _build_nodes(df)
    _link_edges(df, nodes)
    _accumulate_weights(df, nodes)

    # Collect article nodes with positive weight
    records: List[OutputRow] = [
        {"page_name": n.name, "page_url": n.url, "total": int(n.weight)}
        for n in nodes.values()
        if n.url.startswith(ARTICLE_PREFIX) and n.weight > 0
    ]

    result = (
        pd.DataFrame.from_records(records, columns=["page_name", "page_url", "total"])
        .sort_values(["total", "page_url"], ascending=[False, True], kind="mergesort")
        .reset_index(drop=True)
    )
    return result
