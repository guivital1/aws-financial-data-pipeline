# Controlled AWS deployment

The stack grows in two reviewed stages. The ingestion foundation is deployed
first. The analytical update adds a disabled weekday schedule, one on-demand
Glue job, a projected Glue table, a cost-limited Athena workgroup, and a Lambda
error alarm. QuickSight is deliberately outside this stack because activating
it requires a separate pricing decision.

## Guardrails

- Region: `us-east-2` (Ohio).
- Lambda: ARM64, 256 MB, 30-second timeout, concurrency limited to one.
- S3: public access blocked, AES-256 encryption, versioning enabled.
- IAM: the Lambda can write only to the bucket's `raw/` prefix.
- CloudWatch: logs expire after seven days.
- EventBridge: the weekday rule is created disabled and requires an explicit
  parameter change after validation.
- Glue: at most one run, two autoscaling `G.1X` workers, ten-minute timeout, and
  no automatic schedule.
- Athena: each query is stopped after 10 MB scanned; results expire after seven
  days.
- The S3 bucket is retained if the stack is deleted so data cannot disappear by
  accident. Empty it manually only after confirming the exact generated name.

## Prerequisites

1. Keep the AWS zero-spend budget enabled.
2. Install and authenticate AWS CLI and AWS SAM CLI locally.
3. Confirm the active account and region before every deployment:

```bash
aws sts get-caller-identity
aws configure get region
```

The expected account is the portfolio account and the expected deployment
region is `us-east-2`.

## Validate without deploying

```bash
sam validate --lint
sam build
```

## Review and deploy

Upload the versioned Glue script to the existing private project bucket before
deploying the analytical update:

```bash
aws s3 cp glue/transform_to_parquet.py \
  "s3://$PIPELINE_BUCKET/artifacts/glue/transform_to_parquet.py"
```

```bash
sam deploy
```

`confirm_changeset = true` is committed in `samconfig.toml`, so SAM must display
the exact change set and receive confirmation before it creates resources.

## First controlled invocation

After deployment, copy the function name from the CloudFormation outputs and
invoke it once:

```bash
aws lambda invoke \
  --region us-east-2 \
  --function-name aws-financial-data-pipeline-portfolio-ingestion \
  --cli-binary-format raw-in-base64-out \
  --payload '{"series":["usd_brl","ipca"]}' \
  response.json
```

Inspect the response, the seven-day log group, and the new object under the
bucket's `raw/source=bcb/` prefix before enabling any automation.

## Validate the analytical layer

Start exactly one transformation and wait for it to finish:

```bash
aws glue start-job-run \
  --region us-east-2 \
  --job-name aws-financial-data-pipeline-portfolio-transform
```

Then query `financial_analytics.bcb_curated` using the
`aws-financial-data-pipeline-portfolio` Athena workgroup. Only after validating
the Parquet records and alarm should `EnableDailySchedule=true` be deployed.

## Safe teardown

Delete the stack only after noting the generated bucket name:

```bash
sam delete
```

The bucket is retained intentionally. Verify that it carries the project tags,
download any evidence required for the portfolio, empty that exact bucket, and
then delete it from S3.
