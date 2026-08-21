# Cost safety checklist

No cloud resources should be created before this checklist is complete.

- [x] Create the `Portfolio AWS - Alerta de Gasto` budget with an email alert
  when actual cost exceeds USD 0.01.
- [ ] Confirm the account is still on the AWS Free Plan before deployment.
- [ ] Keep the ingestion Lambda below 256 MB and a 30-second timeout.
- [ ] Use S3 lifecycle rules for temporary Athena query results.
- [ ] Run Glue on demand during development; do not schedule it initially.
- [ ] Restrict Athena workgroups with a per-query scan limit.
- [ ] Verify QuickSight pricing and trial eligibility before activation.
- [ ] Tag every resource with `Project=aws-financial-data-pipeline`.
- [ ] Document teardown and delete unused resources after demonstrations.

The first deployment is intentionally limited to the private raw-data bucket,
the ingestion Lambda, and short-lived CloudWatch logs. See
[`deployment.md`](deployment.md) for the exact guardrails and review commands.

AWS promotional credits fund cloud usage; they do not guarantee that every service is free. Billing alerts are notifications, not hard spending caps.
