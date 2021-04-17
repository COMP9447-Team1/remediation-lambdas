import boto3, os, sys, json, logging
import urllib3 
http = urllib3.PoolManager() # not sure not why inside of def - is it executed only once?

# Set the global variables
globalVars  = {}
globalVars['Owner']                 = "Rudy"
globalVars['Environment']           = "Development"
globalVars['REGION_NAME']           = "us-east-1"
globalVars['tagName']               = "Serverless-GuardDuty-Findings-To-CloudWatch-Events"
globalVars['SNSTopicArn']           = "arn:aws:sns:us-east-1:221094580673:GuardDuty_to_Slack"

sns_client = boto3.client('sns')

# Set the log format
logger = logging.getLogger()
for h in logger.handlers:
  logger.removeHandler(h)

h = logging.StreamHandler(sys.stdout)
FORMAT = ' [%(levelname)s]/%(asctime)s/%(name)s - %(message)s'
h.setFormatter(logging.Formatter(FORMAT))
logger.addHandler(h)
logger.setLevel(logging.INFO)

"""
If User provides different values, override defaults
"""
def setGlobalVars():
    try:
        if os.environ['SNSTopicArn']:
            globalVars['SNSTopicArn']  = os.environ['SNSTopicArn']
    except KeyError as e:
        logger.error('ERROR: SNS Topic ARN is missing, Using default GlobalVars - {0}'.format( globalVars['SNSTopicArn'] ) )
        logger.error('ERROR: {0}'.format( str(e) ) )
        pass

"""
This function pushes GuardDuty *Findings* to SNS Topic to be picked up ITSM Tools for Alerting.
"""

def push_To_SNS_Topic(event):
    try:
        response = sns_client.publish(
            TopicArn = globalVars['SNSTopicArn'],
            Message = json.dumps(event),
            Subject = event['detail']['title']
        )
        logger.info('SUCCESS: Pushed GuardDuty Finding to SNS Topic')
        
        giveUserOptions()
        
        return "Successly pushed to Notification to SNS Topic"
    except KeyError as e:
        logger.error('ERROR: Unable to push to SNS Topic: Check [1] SNS Topic ARN is invalid, [2] IAM Role Permissions{0}'.format( str(e) ) )
        logger.error('ERROR: {0}'.format( str(e) ) )
    

def giveUserOptions():
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

            md_text = "*" + "Would you like to" + "*" + "\n\n" + "Stop EC2 instance: @aws invoke StopEC2Instance --region us-east-1" +  "*\n\n" + "Block IP: @aws invoke blockIP --region us-east-1" +  "*\n\n" +"Ignore" + "*\n\n" +  "To execute these remediations, please copy and paste the aws commands back into the channel"
        
            
            
            
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



def lambda_handler(event, context):
    print(event)
    print(context)
    
    setGlobalVars()
    return push_To_SNS_Topic(event)

if __name__ == '__main__':
    lambda_handler(None, None)