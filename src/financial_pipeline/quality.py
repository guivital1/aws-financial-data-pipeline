"""Data-quality checks shared by local, CI and cloud workflows."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from typing import Any


@dataclass(frozen=True)
class QualityIssue:
    check: str
    message: str
    series_slug: str | None = None


VALUE_RANGES: dict[str, tuple[float, float]] = {
    "usd_brl": (1.0, 20.0),
    "cdi": (-1.0, 1.0),
    "selic_monthly": (-5.0, 10.0),
    "ipca": (-10.0, 20.0),
}


def validate_records(
    records: Iterable[dict[str, Any]],
    *,
    as_of: date | None = None,
    daily_freshness_days: int = 7,
    monthly_freshness_days: int = 62,
) -> list[QualityIssue]:
    """Return all quality issues instead of failing at the first bad row."""

    materialized = list(records)
    issues: list[QualityIssue] = []
    seen: set[tuple[str, str]] = set()
    latest: dict[str, tuple[date, str]] = {}

    for index, record in enumerate(materialized):
        slug = str(record.get("series_slug") or "")
        raw_date = str(record.get("observation_date") or "")
        value = record.get("value")
        frequency = str(record.get("frequency") or "")

        if not slug or not raw_date or value is None:
            issues.append(
                QualityIssue("not_null", f"row {index} misses a required field", slug or None)
            )
            continue

        try:
            parsed_date = date.fromisoformat(raw_date)
        except ValueError:
            issues.append(QualityIssue("valid_date", f"invalid date {raw_date!r}", slug))
            continue

        key = (slug, raw_date)
        if key in seen:
            issues.append(
                QualityIssue("unique_observation", f"duplicate observation {raw_date}", slug)
            )
        seen.add(key)

        try:
            numeric_value = float(value)
        except (TypeError, ValueError):
            issues.append(QualityIssue("numeric_value", f"non-numeric value {value!r}", slug))
        else:
            if slug in VALUE_RANGES:
                minimum, maximum = VALUE_RANGES[slug]
                if not minimum <= numeric_value <= maximum:
                    issues.append(
                        QualityIssue(
                            "accepted_range",
                            f"value {numeric_value} is outside [{minimum}, {maximum}]",
                            slug,
                        )
                    )

        if slug not in latest or parsed_date > latest[slug][0]:
            latest[slug] = (parsed_date, frequency)

    reference = as_of or date.today()
    for slug, (latest_date, frequency) in sorted(latest.items()):
        maximum_age = monthly_freshness_days if frequency == "monthly" else daily_freshness_days
        age = (reference - latest_date).days
        if age > maximum_age:
            issues.append(
                QualityIssue(
                    "freshness",
                    f"latest observation is {age} days old; SLA is {maximum_age}",
                    slug,
                )
            )

    return issues


def assert_quality(records: Iterable[dict[str, Any]], **kwargs: Any) -> None:
    """Raise a compact exception suitable for CI and orchestration logs."""

    issues = validate_records(records, **kwargs)
    if issues:
        summary = "; ".join(
            f"{issue.check}[{issue.series_slug or 'dataset'}]: {issue.message}" for issue in issues
        )
        raise ValueError(f"data quality failed with {len(issues)} issue(s): {summary}")
