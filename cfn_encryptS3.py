import json
import boto3
import urllib3 

http = urllib3.PoolManager() # not sure not why inside of def - is it executed only once?
client = boto3.client('s3')
def lambda_handler(event, context):
    # TODO implement
    print("event", event)
    print("context", context)
    
    bucketName = 'ian-ng-team-1'
    bucketOwner = '221094580673'
    
    invokingEvent = json.loads(event["invokingEvent"])
    bucketOwner = invokingEvent['configurationItem']['awsAccountId']
    bucketName = invokingEvent['configurationItem']['resourceName']

    try:
        # TODO: write code...
        response = client.get_bucket_encryption(
            Bucket=bucketName,
            ExpectedBucketOwner=bucketOwner
        )
    except Exception as e:
        if ('ServerSideEncryptionConfigurationNotFoundError' in str(e)):
            print("enabling encryption")
            result = 'Server Side Encryption is now SUCCESSFULLY enabled for S3 Bucket ' + bucketName
            
            response = client.put_bucket_encryption(
                Bucket=bucketName,
                ServerSideEncryptionConfiguration={
                    'Rules': [
                        {
                            'ApplyServerSideEncryptionByDefault': {
                                'SSEAlgorithm': 'AES256'
                            },
                            'BucketKeyEnabled': True
                        },
                    ]
                },
                ExpectedBucketOwner=bucketOwner
            )
            
            # === Slack Notifications part ====
            try: #  try logic to catch errors
                # webhooks dict contains basically the Bot's private keys
                webhooks =  {
                    "team1": "https://hooks.slack.com/services/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",
                    "rudy-guardduty": "https://hooks.slack.com/services/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",
                }
                
                # parameters
                channel = "rudy-guardduty"
                url = webhooks[channel]
                
                # my own var
                md_text = "*"+( event.get('detail-type', "Config Rule") + "*\n\n" + result + "\n")
                
                msg = {
                    "channel": "#%s".format(channel),
                    "username": "WEBHOOK_USERNAME",
                    "text": md_text,
                    "icon_emoji": ":white_check_mark:"
                }
                
                encoded_msg = json.dumps(msg).encode('utf-8')
                resp = http.request('POST',url, body=encoded_msg)
                print({
                    "message": md_text, 
                    "status_code": resp.status, 
                    "response": resp.data
                })
            except Exception as e:
                print(e)
                raise
            # ==== Slack END ===

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
