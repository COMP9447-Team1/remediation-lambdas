import re

ip = "12.34.56.78"
pattern = "(\d+)\.(\d+)\.(\d+)\.(\d+)"

numbers = re.match(pattern, ip)
lst =  list(numbers.groups())
lst[-1] = str(1)

s = lst[0]
for i in lst[1:]:
    s = s + "." + i
    
print(s)