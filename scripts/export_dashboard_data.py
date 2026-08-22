"""Export official BCB observations for the static portfolio dashboard."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from financial_pipeline.pipeline import collect, select_series


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "data" / "financial-series.json"


def main() -> None:
    records = collect(select_series())
    grouped: dict[str, dict[str, object]] = {}

    for record in records:
        slug = str(record["series_slug"])
        series = grouped.setdefault(
            slug,
            {
                "name": record["series_name"],
                "unit": record["unit"],
                "frequency": record["frequency"],
                "records": [],
            },
        )
        series["records"].append(
            {"date": record["observation_date"], "value": record["value"]}
        )

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "Banco Central do Brasil - SGS",
        "series": grouped,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    print(f"Exported {len(records)} observations to {OUTPUT}")


if __name__ == "__main__":
    main()
