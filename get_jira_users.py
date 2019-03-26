import os
import re
from jira import JIRA
from jira.exceptions import JIRAError

user = os.environ['JIRA_USER']
password = os.environ['JIRA_PASSWORD']
options = {'server': os.environ['JIRA_URL']}

try:
    jira = JIRA(options=options, basic_auth=(user, password))
except JIRAError as e:
    if e.status_code == 401:
        print("Login to JIRA failed.")

users = jira.search_users('%', 0, 2000)

for user in users:
    if re.match(r"addon_*", user.name):
        continue

    print(user.key)
