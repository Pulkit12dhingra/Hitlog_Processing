from __future__ import annotations

from typing import List

import pandas as pd

from telegraph_ranker.domain import OutputRow
from telegraph_ranker.io_utils import ARTICLE_PREFIX, REG_URL


def build_ranking(df: pd.DataFrame) -> pd.DataFrame:
    """
    Timestamp-based approach:
    - Iterate each user's chronologically ordered events.
    - Freeze each distinct article in the current journey (no double counting).
    - When '/register' is seen, commit +1 to all frozen articles; then reset.
    """
    # Accumulate weights with a simple dict keyed by article URL
    weights: dict[str, int] = {}
    names: dict[str, str] = {}

    for _uid, grp in df.groupby("user_id", sort=False):
        seen_in_journey: set[str] = set()

        for _, row in grp.iterrows():
            url = row["page_url"]
            if url.startswith(ARTICLE_PREFIX):
                if url not in seen_in_journey:
                    seen_in_journey.add(url)
                    # capture a stable name for this URL (first seen wins)
                    names.setdefault(url, row["page_name"])

            if url == REG_URL:
                for art_url in seen_in_journey:
                    weights[art_url] = weights.get(art_url, 0) + 1
                seen_in_journey.clear()

    # Build output rows
    records: List[OutputRow] = [
        {"page_name": names[u], "page_url": u, "total": int(w)}
        for u, w in weights.items()
        if w > 0
    ]

    result = (
        pd.DataFrame.from_records(records, columns=["page_name", "page_url", "total"])
        .sort_values(["total", "page_url"], ascending=[False, True], kind="mergesort")
        .reset_index(drop=True)
    )
    return result
