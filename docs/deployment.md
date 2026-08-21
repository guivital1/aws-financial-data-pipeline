# Controlled AWS deployment

The first deployment intentionally creates only a private S3 bucket, one Lambda
function, its least-privilege execution role, and a seven-day CloudWatch log
group. No recurring schedule, Glue job, Athena query, or QuickSight subscription
is created at this stage.

## Guardrails

- Region: `us-east-2` (Ohio).
- Lambda: ARM64, 256 MB, 30-second timeout, concurrency limited to one.
- S3: public access blocked, AES-256 encryption, versioning enabled.
- IAM: the Lambda can write only to the bucket's `raw/` prefix.
- CloudWatch: logs expire after seven days.
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

## Safe teardown

Delete the stack only after noting the generated bucket name:

```bash
sam delete
```

The bucket is retained intentionally. Verify that it carries the project tags,
download any evidence required for the portfolio, empty that exact bucket, and
then delete it from S3.
