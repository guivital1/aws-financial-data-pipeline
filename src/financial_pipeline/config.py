"""Official BCB series used by the pipeline."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SeriesConfig:
    slug: str
    code: int
    name: str
    frequency: str
    unit: str
    lookback_days: int


SERIES: dict[str, SeriesConfig] = {
    "usd_brl": SeriesConfig(
        slug="usd_brl",
        code=1,
        name="USD/BRL sell exchange rate",
        frequency="daily",
        unit="BRL per USD",
        lookback_days=400,
    ),
    "cdi": SeriesConfig(
        slug="cdi",
        code=12,
        name="CDI interest rate",
        frequency="daily",
        unit="percent per day",
        lookback_days=400,
    ),
    "selic_monthly": SeriesConfig(
        slug="selic_monthly",
        code=4390,
        name="Accumulated Selic rate in the month",
        frequency="monthly",
        unit="percent per month",
        lookback_days=1_826,
    ),
    "ipca": SeriesConfig(
        slug="ipca",
        code=433,
        name="IPCA inflation rate",
        frequency="monthly",
        unit="monthly percent change",
        lookback_days=1_826,
    ),
}
