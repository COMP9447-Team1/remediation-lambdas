import json
import boto3
client = boto3.client('cloudformation')


def lambda_handler(event, context):
    # TODO implement
    roleArn = "arn:aws:iam::221094580673:role/service-role/CreateStack-role-9vv4yuf8"
    commandType = event['id']
    capabilities = ['CAPABILITY_IAM']
    stackName = commandType
    print(commandType)
    templateUrl = f"https://remediation-cfns.s3.amazonaws.com/{commandType}.yaml"
    print(templateUrl)
    print(event)
    print(context)

    response = client.create_stack(
        StackName=stackName,
        TemplateURL=templateUrl,
        Capabilities=capabilities,
        RoleARN=roleArn,
    )

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
