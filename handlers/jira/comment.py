import os
import re
import json
import requests
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
  comment = event['jira_payload']['comment']['body']
  comment_user = event['jira_payload']['comment']['updateAuthor']['accountId']
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
  comment = convert_regex(comment, issue_url)

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
    if comment_user == mapping['jira_account_id']:
      result = mapping['slack_name']

  return result


def convert_forms(comment):
  result = comment

  f = open(os.path.dirname(__file__) + '/jira_slack_form_mappings.json')
  form_mappings = json.load(f)

  for key, value in form_mappings.items():
    result = result.replace(key, value)

  return result


def convert_regex(comment, issue_url):
  result = comment

  # Quotes/Panels
  result = re.sub('\{quote\}', '```', result)
  result = re.sub('\{noformat\}', '```', result)
  result = re.sub('\{panel[^\n]*\}', '```', result)

  # Image
  result = re.sub('\!.*\|.*\!', '<' + issue_url + '|:camera: 画像>', result)

  # Links
  result = re.sub('\|smart-link', '', result)
  result = re.sub('\[([^|]+)\]', r'<\1>', result)
  result = re.sub('\[([^[\]|]+?)\|([^[\]|]+?)\]', '<\\2|\\1>', result)

  # Header TODO: fix
  result = re.sub('^h[0-6]\.(\s*)([^\n|^$]*)', '*\\2*', result)
  result = re.sub('\\nh[0-6]\.(\s*)([^\n|^$]*)', '\n*\\2*', result)

  # Lists (番号付きリストは#が並ぶだけであり少々面倒なのでただのリストに置換している)
  result = re.sub('^[-|*|#]\s', '• ', result)
  result = re.sub('\\n[-|*|#]\s', '\\n• ', result)
  result = re.sub('\\n[-|*|#]{2}\s', '\n　• ', result)
  result = re.sub('\\n[-|*|#]{3}\s', '\n　　• ', result)
  result = re.sub('\\n[-|*|#]{4}\s', '\n　　　• ', result)
  result = re.sub('\\n[-|*|#]{5}\s', '\n　　　　• ', result)
  result = re.sub('\\n[-|*|#]{6}\s', '\n　　　　　• ', result)

  # Bold/Italic etc
  result = re.sub('(\*[^\n*]+\*)', ' \\1 ', result)
  result = re.sub('\{color\}', '* ', result)
  result = re.sub('\{color[^\n]*\}', ' *', result)
  result = re.sub('-([^\n-]+)-', ' ~\\1~ ', result)
  result = re.sub('\+([^\n-]+)\+', ' *\\1* ', result)
  result = re.sub('\+([^\n-]+)\+', ' _\\1_ ', result)

  return result
