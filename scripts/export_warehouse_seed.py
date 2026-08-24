"""Convert the public dashboard snapshot into a dbt seed table."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "data" / "financial-series.json"
OUTPUT = ROOT / "analytics" / "seeds" / "bcb_observations.csv"


def main() -> None:
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    rows: list[dict[str, object]] = []
    for slug, series in sorted(payload["series"].items()):
        for record in series["records"]:
            rows.append(
                {
                    "series_slug": slug,
                    "series_name": series["name"],
                    "unit": series["unit"],
                    "frequency": series["frequency"],
                    "observation_date": record["date"],
                    "value": record["value"],
                    "source": payload["source"],
                    "snapshot_generated_at": payload["generated_at"],
                }
            )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8", newline="") as destination:
        writer = csv.DictWriter(destination, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Exported {len(rows)} observations to {OUTPUT}")


if __name__ == "__main__":
    main()
