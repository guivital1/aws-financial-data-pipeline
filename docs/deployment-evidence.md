# Deployment evidence

## Controlled foundation deployment

The first AWS deployment completed successfully in `us-east-2` on
2026-08-22 UTC. It created only the resources declared in the reviewed
CloudFormation change set:

- one private, encrypted S3 raw-data bucket;
- one ARM64 ingestion Lambda;
- one least-privilege Lambda execution role;
- one CloudWatch log group with seven-day retention.

No EventBridge schedule, Glue job, Athena resource, or QuickSight subscription
was created.

## First manual ingestion

The Lambda was invoked once with the `usd_brl` and `ipca` series. The invocation
returned HTTP status `200` and wrote a partitioned JSONL object under
`raw/source=bcb/`.

| Check | Result |
| --- | --- |
| Records written | 337 |
| Object size | 147,844 bytes |
| Content type | `application/x-ndjson` |
| Server-side encryption | `AES256` |
| Lambda memory | 256 MB |
| Lambda timeout | 30 seconds |
| Reserved concurrency | 1 |
| Schedule | Not created |

The exact account ID and generated bucket name are intentionally omitted from
the public repository. Operational identifiers remain available in the private
CloudFormation outputs in the AWS account.

## Analytical layer validation

The second reviewed deployment added the Glue Data Catalog, an on-demand Glue
job, a cost-guarded Athena workgroup, a disabled EventBridge rule, and a Lambda
error alarm. The first repeat execution exposed two narrow S3 permissions used
by Spark overwrite semantics; both were corrected through reviewed pull
requests before automation was enabled.

The final repeatable Glue run succeeded in 90 seconds and rewrote the curated
Parquet layer from the complete raw history.

| Series | Records | First observation | Latest observation |
| --- | ---: | --- | --- |
| CDI | 276 | 2025-07-18 | 2026-08-20 |
| IPCA | 60 | 2021-08-01 | 2026-07-01 |
| Selic monthly | 61 | 2021-08-01 | 2026-08-01 |
| USD/BRL | 277 | 2025-07-18 | 2026-08-21 |

The validation query returned all 674 deduplicated observations while scanning
7,387 bytes. The Athena workgroup stops any query that exceeds 10 MB, and its
temporary results expire after seven days. The monthly analytical view was also
created and validated with Selic, IPCA, and their approximate difference.

QuickSight was not activated during this deployment. Its pricing remains a
separate explicit decision so the pipeline cannot create an unnoticed recurring
subscription.
