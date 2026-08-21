"""AWS Lambda ingestion entry point.

The Lambda runtime already includes boto3, so it is imported only when invoked.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any

from financial_pipeline.pipeline import collect, select_series


def handler(event: dict[str, Any], _context: Any) -> dict[str, Any]:
    bucket = os.environ.get("RAW_BUCKET")
    if not bucket:
        raise RuntimeError("RAW_BUCKET environment variable is required")

    requested_series = event.get("series") if event else None
    records = collect(select_series(requested_series))
    now = datetime.now(timezone.utc)
    key = (
        "raw/source=bcb/"
        f"ingestion_year={now:%Y}/ingestion_month={now:%m}/ingestion_day={now:%d}/"
        f"bcb-{now:%Y%m%dT%H%M%SZ}.jsonl"
    )
    body = "".join(
        f"{json.dumps(record, ensure_ascii=False, separators=(',', ':'))}\n"
        for record in records
    ).encode("utf-8")

    import boto3  # type: ignore[import-not-found]

    boto3.client("s3").put_object(
        Bucket=bucket,
        Key=key,
        Body=body,
        ContentType="application/x-ndjson",
        ServerSideEncryption="AES256",
    )
    return {"statusCode": 200, "bucket": bucket, "key": key, "records": len(records)}
