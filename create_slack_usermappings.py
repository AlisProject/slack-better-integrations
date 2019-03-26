import os
import json
from slackclient import SlackClient

slack_token = os.environ["SLACK_API_TOKEN"]
sc = SlackClient(slack_token)

members = sc.api_call("users.list")['members']

i = 0
user_mappings = {}
for member in members:
    # deleted, bot or single channel guest members
    if member['deleted'] or member['is_bot'] or member['name'] == 'slackbot' or member['is_ultra_restricted']:
        continue

    name = member['real_name'] if 'real_name' in member else member['name']

    i += 1
    user_mappings['ORIGIN_NAME_HERE' + str(i)] = {'name': name, 'id': member['id']}

f = open('jira_user_mappings.json', 'w')
json.dump(user_mappings, f, ensure_ascii=False)

print('Dump members to jira_user_mappings.json')