import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DashboardTests(unittest.TestCase):
    def test_snapshot_contains_all_financial_series(self):
        payload = json.loads(
            (ROOT / "docs" / "data" / "financial-series.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            set(payload["series"]),
            {"usd_brl", "cdi", "selic_monthly", "ipca"},
        )
        self.assertTrue(all(item["records"] for item in payload["series"].values()))

    def test_dashboard_has_interactive_controls(self):
        html = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
        self.assertIn('id="series-chart"', html)
        self.assertIn('data-range="365"', html)
        self.assertIn('data-series="usd_brl"', html)

    def test_social_metadata_uses_public_pages_url(self):
        html = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
        public_url = "https://guivital1.github.io/aws-financial-data-pipeline/"
        self.assertIn(f'content="{public_url}"', html)
        self.assertIn(f'content="{public_url}og.jpg"', html)


if __name__ == "__main__":
    unittest.main()
