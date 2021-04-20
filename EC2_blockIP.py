import boto3
import hashlib
import json
import urllib2


# ID of the security group we want to update
# SECURITY_GROUP_ID = "sg-XXXX"

# Description of the security rule we want to replace
# SECURITY_RULE_DESCR = "My Home IP"

"""
def lambda_handler(event, context):
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
"""



def lambda_handler(event, context):
    new_ip_address = list(event.values())[0]
    result = update_security_group(new_ip_address)
    return result
    
def gen_iprange(ip_addr, i = 32):
    if(ip_addr.find("/") == -1): # hash not found
        # i - Cisco style range (or whatever it's called)
        #  * 32 means to specify 1 IP address only
        #  * 24 means to specify the entire subnet (e.g. 192.168.10.* )
        #  * 0 means to block the entire IPv4 range ie the internet (lol)
        #  Too sleepy to remember the name for the thing, but it's calculated as,
        #  `2^(32-i)` many IPv4 addresses (to specify) 
        buf = "{s}/{d}".format(ip_addr, i)
    else:
        buf = ip_addr
    
    return buf

def update_security_group(new_ip_address):
    client = boto3.client('ec2')
    
    #response = client.describe_security_groups(GroupIds=[SECURITY_GROUP_ID])
    response = client.describe_security_groups()
    
    # see https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.SecurityGroup.ip_permissions
    processed_ip = gen_iprange(ip_addr)
    
    # TODO check if it permits or bans upon input 
    
    new = {
        "FromPort": -1, # all ports
        "ToPort": -1, # all ports
        "IpProtocol": "-1", # all protocols
        "IpRanges": {}, # to be set
    }
    new["IpRanges"]["CidrIp"] = processed_ip
    new["IpRanges"]["Description"] = processed_ip + " has been ban-hammered!"
    
    group = response['SecurityGroups'][0]
    for permission in group['IpPermissions']:
        new_permission = copy.deepcopy(permission)
        new_permission['IpRanges'].update(new)


    client.revoke_security_group_ingress(GroupId=group['GroupId'], IpPermissions=[permission])
    client.authorize_security_group_ingress(GroupId=group['GroupId'], IpPermissions=[new_permission])
        
        
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
        md_text = "*\u1F528 Ban successful*\n\n*" + processed_ip + "*has been banned."
        
        msg = {
            "channel": "#{}".format(channel),
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
    print('did it work??', result)
