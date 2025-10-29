from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from typing import Dict, Set

import pandas as pd


ARTICLE_PREFIX = "/articles/"
REG_URL = "/register"


@dataclass(slots=True)
class Node:
    """Represents a page node in the site graph."""

    url: str
    name: str
    neighbors: Set[str] = field(default_factory=set)
    weight: int = 0


def normalize(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and prepare the log DataFrame for analysis."""
    for col in ("page_name", "page_url", "user_id"):
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    df = df.dropna(subset=["user_id", "timestamp"]).copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df = df.sort_values(["user_id", "timestamp"], kind="mergesort").reset_index(
        drop=True
    )

    mask = df["page_url"].str.startswith(ARTICLE_PREFIX) | (df["page_url"] == REG_URL)
    return df.loc[mask].copy()


def build_nodes(df: pd.DataFrame) -> Dict[str, Node]:
    """Initialize Node objects for each unique page."""
    nodes: Dict[str, Node] = {}
    for _, row in df.iterrows():
        url = row["page_url"]
        if url not in nodes:
            nodes[url] = Node(url=url, name=row["page_name"])
    return nodes


def link_edges(df: pd.DataFrame, nodes: Dict[str, Node]) -> None:
    """Add directed edges between consecutive pages for each user."""
    for _uid, grp in df.groupby("user_id", sort=False):
        prev_url: str | None = None
        for _, row in grp.iterrows():
            cur_url = row["page_url"]
            if prev_url is not None:
                nodes[prev_url].neighbors.add(cur_url)
            prev_url = cur_url


def accumulate_weights(df: pd.DataFrame, nodes: Dict[str, Node]) -> None:
    """Traverse user journeys and increment article influence weights."""
    for _uid, grp in df.groupby("user_id", sort=False):
        seen_in_journey: Set[str] = set()
        for _, row in grp.iterrows():
            url = row["page_url"]

            if url.startswith(ARTICLE_PREFIX) and url not in seen_in_journey:
                seen_in_journey.add(url)

            if url == REG_URL:
                for art_url in seen_in_journey:
                    nodes[art_url].weight += 1
                seen_in_journey.clear()


def build_influence_ranking(csv_path: str) -> pd.DataFrame:
    """
    Construct a DataFrame of influential articles based on registration journeys.
    """
    df = pd.read_csv(csv_path)
    df = normalize(df)

    nodes = build_nodes(df)
    link_edges(df, nodes)
    accumulate_weights(df, nodes)

    records = [
        {"page_name": n.name, "page_url": n.url, "total": int(n.weight)}
        for n in nodes.values()
        if n.url.startswith(ARTICLE_PREFIX) and n.weight > 0
    ]

    result = (
        pd.DataFrame(records, columns=["page_name", "page_url", "total"])
        .sort_values(["total", "page_url"], ascending=[False, True], kind="mergesort")
        .reset_index(drop=True)
    )
    return result


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Compute article influence ranking based on user journeys."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to the input CSV log file (e.g., hitlog_2025-10-27.csv)",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to the output CSV file for results",
    )
    return parser.parse_args()


def main() -> None:
    """Entry point for command-line execution."""
    args = parse_args()

    result = build_influence_ranking(args.input)

    if result.empty:
        print("No influential articles found.")
        return

    result.to_csv(args.output, index=False)
    print(f"Influence ranking saved to: {args.output}")
    print("\nTop 10 influential articles:")
    print(result.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
