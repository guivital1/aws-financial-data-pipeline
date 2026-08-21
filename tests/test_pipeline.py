import json
import tempfile
import unittest
from pathlib import Path

from financial_pipeline.pipeline import select_series, write_jsonl


class PipelineTests(unittest.TestCase):
    def test_unknown_series_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unknown series"):
            select_series(["not_a_series"])

    def test_write_jsonl_returns_record_count(self) -> None:
        records = [{"series_slug": "ipca", "value": 0.07}]
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "nested" / "data.jsonl"
            count = write_jsonl(records, destination)

            self.assertEqual(count, 1)
            self.assertEqual(json.loads(destination.read_text()), records[0])


if __name__ == "__main__":
    unittest.main()
