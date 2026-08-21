CREATE EXTERNAL TABLE IF NOT EXISTS financial_analytics.bcb_raw (
    series_id          integer,
    series_slug        string,
    series_name        string,
    frequency          string,
    unit               string,
    observation_date   string,
    year               integer,
    month              integer,
    value              double,
    raw_value          string,
    source             string,
    source_url         string,
    ingested_at        string
)
ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
LOCATION 's3://REPLACE_WITH_RAW_BUCKET/raw/source=bcb/';
