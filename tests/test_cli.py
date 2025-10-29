from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd


def _run_cli(input_csv: Path, output_csv: Path, approach: str, env: dict) -> None:
    cmd = [
        sys.executable,
        "-m",
        "telegraph_ranker.cli",
        "--input",
        str(input_csv),
        "--output",
        str(output_csv),
        "--approach",
        approach,
    ]
    proc = subprocess.run(cmd, env=env, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise AssertionError(
            f"CLI failed (rc={proc.returncode})\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )


def _assert_schema_and_nonempty(csv_path: Path) -> pd.DataFrame:
    assert csv_path.exists(), f"Missing output: {csv_path}"
    df = pd.read_csv(csv_path)
    assert list(df.columns) == ["page_name", "page_url", "total"]
    assert len(df) >= 2  # we expect at least /a and /b rows
    return df


def test_cli_timestamp_and_graph(sample_csv_path, outputs_dir, run_cli_env) -> None:
    out_ts = outputs_dir / "influence_timestamp.csv"
    out_gr = outputs_dir / "influence_graph.csv"

    _run_cli(sample_csv_path, out_ts, "timestamp", run_cli_env)
    _run_cli(sample_csv_path, out_gr, "graph", run_cli_env)

    df_ts = _assert_schema_and_nonempty(out_ts)
    df_gr = _assert_schema_and_nonempty(out_gr)

    # Totals should match across approaches
    t = {r["page_url"]: int(r["total"]) for _, r in df_ts.iterrows()}
    g = {r["page_url"]: int(r["total"]) for _, r in df_gr.iterrows()}
    assert t == g

    # Spot-check expected values
    assert t["/articles/a"] == 2
    assert t["/articles/b"] == 2
    assert "/articles/c" not in t


def test_cli_idempotent_overwrite(sample_csv_path, outputs_dir, run_cli_env) -> None:
    """Running the CLI twice should overwrite output deterministically."""
    out_path = outputs_dir / "out.csv"
    _run_cli(sample_csv_path, out_path, "timestamp", run_cli_env)
    first = pd.read_csv(out_path)

    _run_cli(sample_csv_path, out_path, "timestamp", run_cli_env)
    second = pd.read_csv(out_path)

    # Compare JSON representations for a robust equality check
    assert json.loads(first.to_json(orient="records")) == json.loads(
        second.to_json(orient="records")
    )
