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
