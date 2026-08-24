import unittest
from datetime import date

from financial_pipeline.quality import assert_quality, validate_records


def record(**overrides):
    base = {
        "series_slug": "usd_brl",
        "observation_date": "2026-08-20",
        "frequency": "daily",
        "value": 5.2,
    }
    return {**base, **overrides}


class QualityTests(unittest.TestCase):
    def test_valid_record_passes_all_checks(self) -> None:
        self.assertEqual(validate_records([record()], as_of=date(2026, 8, 24)), [])

    def test_duplicate_and_out_of_range_are_reported_together(self) -> None:
        rows = [record(value=99), record(value=99)]
        checks = {issue.check for issue in validate_records(rows, as_of=date(2026, 8, 24))}
        self.assertEqual(checks, {"accepted_range", "unique_observation"})

    def test_stale_daily_series_fails_freshness_sla(self) -> None:
        issues = validate_records([record(observation_date="2026-07-01")], as_of=date(2026, 8, 24))
        self.assertEqual([issue.check for issue in issues], ["freshness"])

    def test_assert_quality_raises_ci_friendly_summary(self) -> None:
        with self.assertRaisesRegex(ValueError, "data quality failed"):
            assert_quality([record(value=None)], as_of=date(2026, 8, 24))


if __name__ == "__main__":
    unittest.main()
