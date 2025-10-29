from __future__ import annotations

from pathlib import Path
from typing import Final

import pandas as pd

ARTICLE_PREFIX: Final[str] = "/articles/"
REG_URL: Final[str] = "/register"


def read_hitlog(path: str | Path) -> pd.DataFrame:
    """Read and normalize the hit log CSV."""
    df = pd.read_csv(path)

    # Basic normalization / safety
    for col in ("page_name", "page_url", "user_id"):
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    # Drop rows without a user_id or timestamp (cannot order)
    df = df.dropna(subset=["user_id", "timestamp"]).copy()

    # Ensure UTC and chronological order per user
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df = df.sort_values(["user_id", "timestamp"], kind="mergesort").reset_index(
        drop=True
    )

    # Keep only article and registration events (focus graph)
    mask = df["page_url"].str.startswith(ARTICLE_PREFIX) | (df["page_url"] == REG_URL)
    return df.loc[mask].copy()


def write_output(result: pd.DataFrame, path: str | Path) -> None:
    """Write the ranking DataFrame to CSV with the required schema."""
    required_cols = ["page_name", "page_url", "total"]
    missing = [c for c in required_cols if c not in result.columns]
    if missing:
        cols = ", ".join(missing)
        msg = f"Result missing required columns: {cols}"
        raise ValueError(msg)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(path, index=False)
