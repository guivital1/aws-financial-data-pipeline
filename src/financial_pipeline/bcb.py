"""Small, dependency-free client for the Banco Central do Brasil SGS API."""

from __future__ import annotations

import json
import time
from collections.abc import Callable
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from financial_pipeline.config import SeriesConfig

BASE_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{code}/dados"
SOURCE_NAME = "Banco Central do Brasil - SGS"


class BCBError(RuntimeError):
    """Raised when BCB data cannot be retrieved or validated."""


Transport = Callable[[str, float], bytes]


def _default_transport(url: str, timeout: float) -> bytes:
    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "aws-financial-data-pipeline/0.1",
        },
    )
    with urlopen(request, timeout=timeout) as response:  # noqa: S310 - fixed HTTPS host
        return response.read()


class BCBClient:
    def __init__(
        self,
        *,
        timeout: float = 15,
        retries: int = 3,
        transport: Transport = _default_transport,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        if retries < 1:
            raise ValueError("retries must be at least 1")
        self.timeout = timeout
        self.retries = retries
        self.transport = transport
        self.sleeper = sleeper

    @staticmethod
    def build_url(series_code: int, start_date: date, end_date: date) -> str:
        if series_code <= 0:
            raise ValueError("series_code must be positive")
        if start_date > end_date:
            raise ValueError("start_date cannot be after end_date")
        query = urlencode(
            {
                "formato": "json",
                "dataInicial": start_date.strftime("%d/%m/%Y"),
                "dataFinal": end_date.strftime("%d/%m/%Y"),
            }
        )
        return f"{BASE_URL.format(code=series_code)}?{query}"

    def fetch(
        self,
        config: SeriesConfig,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[dict[str, Any]]:
        period_end = end_date or date.today()
        period_start = start_date or period_end - timedelta(days=config.lookback_days)
        url = self.build_url(config.code, period_start, period_end)
        payload = self._request_json(url)
        return normalize_observations(config, payload, source_url=url)

    def _request_json(self, url: str) -> list[dict[str, str]]:
        last_error: Exception | None = None
        for attempt in range(1, self.retries + 1):
            try:
                raw = self.transport(url, self.timeout)
                payload = json.loads(raw.decode("utf-8"))
                if not isinstance(payload, list):
                    raise BCBError("BCB response must be a JSON list")
                return payload
            except (
                HTTPError,
                URLError,
                TimeoutError,
                UnicodeDecodeError,
                json.JSONDecodeError,
            ) as exc:
                last_error = exc
                if attempt < self.retries:
                    self.sleeper(2 ** (attempt - 1))

        raise BCBError(f"BCB request failed after {self.retries} attempts: {last_error}")


def normalize_observations(
    config: SeriesConfig,
    payload: list[dict[str, str]],
    *,
    source_url: str,
    ingested_at: datetime | None = None,
) -> list[dict[str, Any]]:
    timestamp = (ingested_at or datetime.now(UTC)).isoformat()
    observations: list[dict[str, Any]] = []

    for item in payload:
        try:
            observation_date = datetime.strptime(item["data"], "%d/%m/%Y").date()
            decimal_value = Decimal(item["valor"].replace(",", "."))
        except (KeyError, TypeError, ValueError, InvalidOperation) as exc:
            raise BCBError(f"Invalid observation for series {config.code}: {item!r}") from exc

        observations.append(
            {
                "series_id": config.code,
                "series_slug": config.slug,
                "series_name": config.name,
                "frequency": config.frequency,
                "unit": config.unit,
                "observation_date": observation_date.isoformat(),
                "year": observation_date.year,
                "month": observation_date.month,
                "value": float(decimal_value),
                "raw_value": str(decimal_value),
                "source": SOURCE_NAME,
                "source_url": source_url,
                "ingested_at": timestamp,
            }
        )

    observations.sort(key=lambda row: (row["observation_date"], row["series_id"]))
    _validate_unique_dates(config, observations)
    return observations


def _validate_unique_dates(config: SeriesConfig, observations: list[dict[str, Any]]) -> None:
    dates: set[date] = set()
    for row in observations:
        parsed = date.fromisoformat(row["observation_date"])
        if parsed in dates:
            raise BCBError(f"Duplicate date {parsed} in series {config.code}")
        dates.add(parsed)
