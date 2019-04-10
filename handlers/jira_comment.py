import os
import re
import json
import requests
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    comment = event['jira_payload']['comment']['body']
    comment_user = event['jira_payload']['comment']['updateAuthor']['key']
    issue_key = event['jira_payload']['issue']['key']
    issue_summary = event['jira_payload']['issue']['fields']['summary']
    issue_api_url = event['jira_payload']['issue']['self']
    issue_url = create_issue_url(issue_api_url, issue_key)
    user_icon_url = event['jira_payload']['comment']['updateAuthor']['avatarUrls']['48x48']
    user_mappings = event['jira_user_mappings']

    project_key = event['jira_payload']['issue']['fields']['project']['key']
    slack_webhook_url = event['jira_project_mappings'][project_key]['slack_incomming_webhook']

    comment_link = '\n\n<' + issue_url + '|`' + issue_key + ' ' + issue_summary + '`>'

    slack_user_name = get_slack_user_name(user_mappings, comment_user)

    comment = replace_mentions(user_mappings, comment)
    comment = convert_forms(comment)

    post_message_to_slack(slack_webhook_url,
                          {
                              'username': slack_user_name,
                              'icon_url': user_icon_url,
                              "text": comment + comment_link
                          })

    logger.info(event)

    return event


def create_issue_url(issue_api_url, issue_key):
    domain = re.match(r"https://.*atlassian.net", issue_api_url).group(0)
    return domain + '/browse/' + issue_key


def post_message_to_slack(webhook_url, payload):
    result = requests.post(webhook_url, data=json.dumps({
        'username': payload['username'] if 'username' in payload is not None else u'unknown',
        'icon_url': payload['icon_url'] if 'icon_url' in payload is not None else u'unknown',
        'link_names': 1,
        "text": payload['text']
    }))

    return result


def replace_mentions(user_mappings, comment):
    result = comment
    for mapping in user_mappings:
      result = result.replace('[~' + mapping['jira_user_key'] + ']', '<@' + mapping['slack_id'] + '>')
      result = result.replace('[~accountid:' + mapping['jira_account_id'] + ']', '<@' + mapping['slack_id'] + '>')

    return result

def get_slack_user_name(user_mappings, comment_user):
  result = comment_user
  for mapping in user_mappings:
    if comment_user == mapping['jira_user_key']:
      result = mapping['slack_name']

  return result


def convert_forms(comment):
    result = comment

    f = open(os.path.dirname(__file__) + '/jira_slack_form_mappings.json')
    form_mappings = json.load(f)

    for key, value in form_mappings.items():
        result = result.replace(key, value)

    return result
