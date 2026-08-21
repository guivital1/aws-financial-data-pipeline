# Cost safety checklist

No cloud resources should be created before this checklist is complete.

- [ ] Create an AWS Budget with alerts at USD 2, USD 5, and USD 10.
- [ ] Confirm the account is still on the AWS Free Plan before deployment.
- [ ] Keep the ingestion Lambda below 256 MB and a 30-second timeout.
- [ ] Use S3 lifecycle rules for temporary Athena query results.
- [ ] Run Glue on demand during development; do not schedule it initially.
- [ ] Restrict Athena workgroups with a per-query scan limit.
- [ ] Verify QuickSight pricing and trial eligibility before activation.
- [ ] Tag every resource with `Project=aws-financial-data-pipeline`.
- [ ] Document teardown and delete unused resources after demonstrations.

AWS promotional credits fund cloud usage; they do not guarantee that every service is free. Billing alerts are notifications, not hard spending caps.
