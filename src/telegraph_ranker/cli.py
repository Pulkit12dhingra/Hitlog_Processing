from __future__ import annotations

import argparse

from telegraph_ranker.io_utils import read_hitlog, write_output
from telegraph_ranker.approaches import graph_based, timestamp_based


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Compute influential articles leading to registration."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to input hitlog CSV (e.g., data/logs/hitlog_2025-10-27.csv)",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to output CSV (e.g., data/outputs/top_influential.csv)",
    )
    parser.add_argument(
        "--approach",
        choices=["timestamp", "graph"],
        default="timestamp",
        help="Ranking approach: timestamp (default) or graph.",
    )
    return parser.parse_args()


def main() -> None:
    """Entry point for command-line execution."""
    args = parse_args()
    df = read_hitlog(args.input)

    if args.approach == "graph":
        result = graph_based.build_ranking(df)
    else:
        result = timestamp_based.build_ranking(df)

    write_output(result, args.output)
    print(f"Wrote {len(result)} rows to {args.output}")


if __name__ == "__main__":
    main()
