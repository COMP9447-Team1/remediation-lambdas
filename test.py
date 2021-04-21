import re

def ipaddr_replace_last_dgt(ip, d):
    pattern = "(\d+)\.(\d+)\.(\d+)\.(\d+)"

    numbers = re.match(pattern, ip)
    lst =  list(numbers.groups())
    lst[-1] = str(d)

    # compile back
    s = lst[0]
    for i in lst[1:]:
        s = s + "." + i
    
    return s

ip = "12.34.56.78"
ipmod = ipaddr_replace_last_dgt(ip,1) + "\\24"
instanceID = "INSTANCE"

actions = {
   "Stop EC2 instance": "@aws invoke StopEC2Instance --region us-east-1 --payload " +  '{"id": "' + instanceID + '"}',
   "Ban IP address": "@aws invoke EC2BlockIPAddress --region us-east-1  --payload " +        '{"id": "' + instanceID + '\n "ip": ' + ip + '"}',
   "Ban IP entire subnet": "@aws invoke EC2BlockIPAddress --region us-east-1  --payload " +  '{"id": "' + instanceID + '\n "ip": ' + ipmod +'"}',
   "Ignore": "(do nothing)"
}
           

print(actions)           