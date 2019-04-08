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

    project_key = event['jira_project_mappings']['issue']['fields']['project']['id']
    slack_webhook_url = event['jira_project_mappings'][project_key]

    comment_link = '\n\n<' + issue_url + '|`' + issue_key + ' ' + issue_summary + '`>'

    slack_user_name = user_mappings[comment_user]['name'] if comment_user in user_mappings else comment_user

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
    for key, value in user_mappings.items():
        result = result.replace('[~' + key + ']', '<@' + value['id'] + '>')

    return result


def convert_forms(comment):
    result = comment

    f = open(os.path.dirname(__file__) + '/jira_slack_form_mappings.json')
    form_mappings = json.load(f)

    for key, value in form_mappings.items():
        result = result.replace(key, value)

    return result
