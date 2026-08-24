"""Run business data-quality checks against the public dashboard snapshot."""

from __future__ import annotations

import json
from pathlib import Path

from financial_pipeline.quality import assert_quality

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "data" / "financial-series.json"


def main() -> None:
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    records = []
    for slug, series in payload["series"].items():
        records.extend(
            {
                "series_slug": slug,
                "observation_date": item["date"],
                "value": item["value"],
                "frequency": series["frequency"],
            }
            for item in series["records"]
        )
    assert_quality(records)
    series_count = len(payload["series"])
    print(f"Quality gate passed for {len(records)} observations across {series_count} series")


if __name__ == "__main__":
    main()
