# Teardown checklist

When the AWS demonstration is complete, remove resources in this order:

1. Disable the EventBridge schedule.
2. Delete the QuickSight dataset and dashboard if activated.
3. Delete the Glue job, crawler, and Data Catalog tables.
4. Delete Athena saved queries and empty its query-results prefix.
5. Delete the Lambda function and its CloudWatch log group.
6. Empty and delete the project S3 buckets.
7. Remove project IAM roles and policies.
8. Keep the AWS Budget alert active until Billing shows no new project usage.

Filter resources by the tag `Project=aws-financial-data-pipeline` before deletion. Never delete resources that do not carry the project tag.
