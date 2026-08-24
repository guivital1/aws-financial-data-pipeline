"""Command-line entry point for local ingestion."""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
from pathlib import Path

from financial_pipeline.config import SERIES
from financial_pipeline.pipeline import collect, select_series, write_jsonl


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Collect official BCB financial series.")
    parser.add_argument(
        "--series",
        nargs="+",
        choices=sorted(SERIES),
        help="Series to collect. Defaults to all configured series.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="JSON Lines destination. Defaults to a timestamped file in data/raw.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    output = args.output or Path("data/raw") / f"bcb-{timestamp}.jsonl"
    records = collect(select_series(args.series))
    count = write_jsonl(records, output)
    print(f"Collected {count} observations into {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
