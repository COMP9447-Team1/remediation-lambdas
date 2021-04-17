# remediation-lambdas
Python lambdas than run set automated remediations.

## Lambdae

Human Github name | AWS lambda | Description
---- | ---- | ----
createVPCFlowlogs.py | CIS_2-9_RR | VPC flowlogs and notifications
encryptS3.py | cfn-s3-bucket-encrypt-S3BucketEncryptedCheck-5A01ILX84QBR | Encrypt check + Slack notifications
