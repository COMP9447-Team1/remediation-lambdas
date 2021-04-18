import json
import boto3
import botocore

ec2 = boto3.client('ec2')


def lambda_handler(event, context):
    instance_id = event['id']
    
    try:
        ec2.stop_instances(InstanceIds=[instance_id], DryRun=True)
    except botocore.exceptions.ClientError as e:
        if 'DryRunOperation' not in str(e):
            raise

    # Dry run succeeded, call stop_instances without dryrun
    try:
        response = ec2.stop_instances(InstanceIds=[instance_id], DryRun=False)
        print(response)
    except botocore.exceptions.ClientError as e:
        print(e)
    
    
    return "succesfully stopped EC2 instance with instance id: " + instance_id