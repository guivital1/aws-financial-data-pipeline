# Data contract

Each raw JSON Lines observation contains the following fields:

| Field | Type | Meaning |
| --- | --- | --- |
| `series_id` | integer | Official SGS series code |
| `series_slug` | string | Stable project identifier |
| `series_name` | string | Human-readable indicator name |
| `frequency` | string | Daily or monthly |
| `unit` | string | Measurement unit published by the source |
| `observation_date` | ISO date | Date of the economic observation |
| `year` | integer | Partition helper derived from the observation date |
| `month` | integer | Partition helper derived from the observation date |
| `value` | number | Analysis-ready numeric value |
| `raw_value` | string | Original decimal representation for auditability |
| `source` | string | Data publisher |
| `source_url` | URL | Exact endpoint used for the ingestion |
| `ingested_at` | ISO timestamp | UTC ingestion timestamp |

The natural key is `(series_id, observation_date)`. Glue removes duplicates on this key before writing curated Parquet.
