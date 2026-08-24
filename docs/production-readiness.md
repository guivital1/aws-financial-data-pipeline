# Production-readiness layer

This repository separates the inexpensive portfolio deployment from the local
engineering workflow used to prove dimensional modeling, orchestration and data
quality. The commands are the same in a laptop, Docker and CI.

## Medallion and dimensional design

| Layer | Current implementation | Production AWS equivalent |
| --- | --- | --- |
| Bronze | Immutable BCB JSONL in `raw/` | Encrypted S3 raw prefix |
| Silver | Typed, deduplicated Parquet | AWS Glue curated job |
| Gold | dbt dimensions, fact and analytical mart | dbt-athena or dbt-redshift |

The Gold layer has a clear grain:

- `dim_indicator`: one row per financial series;
- `dim_date`: one row per available observation date;
- `fct_financial_observation`: one indicator and one date per row;
- `mart_real_interest`: aligned monthly Selic and IPCA signal.

## Quality gates

Python checks fail before modeling when the snapshot has missing required
fields, duplicate series/date keys, invalid dates, values outside conservative
business ranges, or stale series. dbt then verifies keys, relationships and
nullability in the analytical layer.

## Orchestration

`orchestration/dags/financial_data_product.py` provides a production-shaped
Airflow DAG with explicit task dependencies and no catchup. The lightweight
portfolio path runs the identical commands through `make analytics` and GitHub
Actions, avoiding a persistent managed Airflow bill.

## Recovery and backfill

1. Re-run ingestion for the affected date range.
2. Preserve the raw object and its ingestion timestamp.
3. Re-run the Glue transformation for affected partitions.
4. Export the analytical seed or point dbt at Athena.
5. Run quality and dbt tests before publishing.

Repeated series/date keys are rejected before reaching the Gold layer. The raw
layer remains the audit source for replay and investigation.
