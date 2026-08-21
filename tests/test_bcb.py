import json
import unittest
from datetime import date, datetime, timezone

from financial_pipeline.bcb import BCBClient, BCBError, normalize_observations
from financial_pipeline.config import SERIES


class BCBClientTests(unittest.TestCase):
    def test_build_url(self) -> None:
        self.assertEqual(
            BCBClient.build_url(433, date(2026, 1, 1), date(2026, 8, 21)),
            "https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados?formato=json&dataInicial=01%2F01%2F2026&dataFinal=21%2F08%2F2026",
        )

    def test_fetch_normalizes_payload(self) -> None:
        payload = json.dumps(
            [{"data": "01/07/2026", "valor": "0.07"}]
        ).encode()
        client = BCBClient(transport=lambda _url, _timeout: payload)

        records = client.fetch(
            SERIES["ipca"],
            start_date=date(2026, 7, 1),
            end_date=date(2026, 7, 31),
        )

        self.assertEqual(records[0]["series_id"], 433)
        self.assertEqual(records[0]["observation_date"], "2026-07-01")
        self.assertEqual(records[0]["value"], 0.07)
        self.assertEqual(records[0]["year"], 2026)
        self.assertEqual(records[0]["month"], 7)

    def test_invalid_value_raises_domain_error(self) -> None:
        with self.assertRaises(BCBError):
            normalize_observations(
                SERIES["ipca"],
                [{"data": "01/07/2026", "valor": "invalid"}],
                source_url="https://example.invalid",
                ingested_at=datetime(2026, 8, 21, tzinfo=timezone.utc),
            )

    def test_duplicate_dates_are_rejected(self) -> None:
        payload = [
            {"data": "01/07/2026", "valor": "0.07"},
            {"data": "01/07/2026", "valor": "0.08"},
        ]
        with self.assertRaisesRegex(BCBError, "Duplicate date"):
            normalize_observations(
                SERIES["ipca"], payload, source_url="https://example.invalid"
            )


if __name__ == "__main__":
    unittest.main()
