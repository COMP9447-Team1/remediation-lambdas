# remediation-lambdas
Python lambdas than run set automated remediations.

## Lambdas

Human Github name | AWS lambda | Description
---- | ---- | ----
createVPCFlowlogs.py | CIS_2-9_RR | VPC flowlogs and notifications
**cfn**_encryptS3.py | cfn-s3-bucket-encrypt-S3BucketEncryptedCheck-5A01ILX84QBR | ??? + Slack notifications
Rudy-GuardDuty-To-Slack.py | Rudy-GuardDuty-To-Slack | Rudy-GuardDuty-To-Slack + Slack Options
EncryptS3.py | EncryptS3 | Encrypt S3
EC2BlockIPAddress.py | EC2BlockIPAddress | Block IP lambda

## Slack Webhooks

Turns out unless I'm an admin of the server, different Webhook links required for different channels. 

It's not worth compromising other teams by getting admins to add bot everywhere, so instead, we can have different webhooks for different channels.

The links are 'basically' bot's private keys, so treat them reasonably confidentially. Current listing,

Bot | Link | Channel 
---- | ---- | ----
AWS Daemon | https://hooks.slack.com/services/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 | team1
AWS Daemon | https://hooks.slack.com/services/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 | rudy-guardduty
