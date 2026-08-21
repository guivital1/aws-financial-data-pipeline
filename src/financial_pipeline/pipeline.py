"""Pipeline orchestration and local storage."""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from financial_pipeline.bcb import BCBClient
from financial_pipeline.config import SERIES, SeriesConfig


def collect(
    configs: Iterable[SeriesConfig],
    *,
    client: BCBClient | None = None,
) -> list[dict[str, Any]]:
    bcb_client = client or BCBClient()
    records: list[dict[str, Any]] = []
    for config in configs:
        records.extend(bcb_client.fetch(config))
    return sorted(records, key=lambda row: (row["series_slug"], row["observation_date"]))


def select_series(slugs: Iterable[str] | None = None) -> list[SeriesConfig]:
    selected = list(slugs or SERIES.keys())
    unknown = sorted(set(selected) - SERIES.keys())
    if unknown:
        raise ValueError(f"Unknown series: {', '.join(unknown)}")
    return [SERIES[slug] for slug in selected]


def write_jsonl(records: Iterable[dict[str, Any]], output_path: Path) -> int:
    materialized = list(records)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as output:
        for record in materialized:
            output.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")))
            output.write("\n")
    return len(materialized)
