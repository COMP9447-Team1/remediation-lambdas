# Ian's imports - enforce policies
import boto3
import json
import time
import os
import random
# Tim's imports - Slack notifs
import urllib3 
# import json
http = urllib3.PoolManager() # not sure not why inside of def - is it executed only once?


def lambda_handler(event, context):
    # NOTE: This main function was SLIGHTLY updated
    # Change: added 'result' var so the same strings can be re-used
    # PS. Still not as good as the proper OOP programming with different classes etc, but that's something right?
    result = "Event handling failed for unknown reasons" #default string
    
    # Grab non-logged VPC ID from Security Hub finding
    print(event)
    print(context)
    
    isSecurityHubFinding = "detail-type" in event
    
    if isSecurityHubFinding:
        noncompliantVPC = str(event['detail']['findings'][0]['Resources'][0]['Id']).split("/")[-1]
        findingId = str(event['detail']['findings'][0]['Id'])
    else:
        invokingEvent = json.loads(event["invokingEvent"])
        noncompliantVPC = invokingEvent["configurationItem"]["configuration"]["vpcId"]
        
    # import lambda runtime vars
    lambdaFunctionName = os.environ['AWS_LAMBDA_FUNCTION_NAME']
    lambdaFunctionSeshToken = os.environ['AWS_SESSION_TOKEN']                
    # Get Flow Logs Role ARN from env vars
    deliverLogsPermissionArn = "arn:aws:iam::221094580673:role/flowlogsRole"         
    # Import boto3 clients
    cwl = boto3.client('logs')
    ec2 = boto3.client('ec2')
    securityhub = boto3.client('securityhub')              
    # set dynamic variable for CW Log Group for VPC Flow Logs
    print('ncvpc: ', noncompliantVPC)
    print('lfst: ', lambdaFunctionSeshToken)
    vpcFlowLogGroup = "VPCFlowLogs/" + noncompliantVPC 
    # create cloudwatch log group
    try:
        create_log_grp = cwl.create_log_group(logGroupName=vpcFlowLogGroup)
    except Exception as e:
        print(e)
        raise              
    # wait for CWL creation to propagate
    time.sleep(3)              
    # create VPC Flow Logging
    try:
        enableFlowlogs = ec2.create_flow_logs(
        DryRun=False,
        DeliverLogsPermissionArn=deliverLogsPermissionArn,
        LogGroupName=vpcFlowLogGroup,
        ResourceIds=[ noncompliantVPC ],
        ResourceType='VPC',
        TrafficType='REJECT',
        LogDestinationType='cloud-watch-logs'
        )
        print(enableFlowlogs)
    except Exception as e:
        print(e)
        raise
    # wait for Flow Log creation to propogate
    time.sleep(2)
    # searches for flow log status, filtered on unique CW Log Group created earlier
    try:
        confirmFlowlogs = ec2.describe_flow_logs(
        DryRun=False,
        Filters=[
            {
                'Name': 'log-group-name',
                'Values': [ vpcFlowLogGroup ]
            },
        ]
        )
        flowStatus = str(confirmFlowlogs['FlowLogs'][0]['FlowLogStatus'])
        if flowStatus == 'ACTIVE':
            try:
                result = 'Flow logging is now SUCCESSFULLY enabled for VPC ' + noncompliantVPC
                
                if isSecurityHubFinding:
                    response = securityhub.update_findings(
                        Filters={
                            'Id': [
                                {
                                    'Value': findingId,
                                    'Comparison': 'EQUALS'
                                }
                            ]
                        },
                        Note={
                            'Text': result,
                            #'Text': 'Flow logging is now enabled for VPC ' + noncompliantVPC,
                            'UpdatedBy': lambdaFunctionName
                        },
                        RecordState='ACTIVE'
                    )
                    print(response)
                    
            except Exception as e:
                print(e)
                raise
        else:
            result = "Enabling VPC flow logging failed! Remediate manually"
            print(result)
            #print('Enabling VPC flow logging failed! Remediate manually')
            return 1
    except Exception as e:
        print(e)
        raise

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
        md_text = "*"+( event.get('detail-type', "Config Rule") + "*\n\n" +
            result + "\n\n"
            #event.get('description', "-description is not currently present for this event-")  + "\n" +
            "VPC: "+noncompliantVPC ) 
        
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
