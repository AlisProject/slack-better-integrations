import os
import re
import json
import requests
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
  logger.info(event)

  comment = event['github_payload']['comment']['body']
  comment_user = event['github_payload']['comment']['user']['login']
  comment_url = event['github_payload']['comment']['html_url']

  issue_title = event['github_payload']['issue']['title']
  repository = event['github_payload']['repository']['name']

  user_icon_url = event['github_payload']['comment']['user']['avatar_url']
  user_mappings = event['github_user_mappings']

  # todo: リポジトリごとに飛ばし分け
  slack_webhook_url = event['github_repository_mappings']['default']['slack_incomming_webhook']

  comment_link = '\n\n<' + comment_url + '|`' + repository + ': ' + issue_title + '`>'

  slack_user_name = get_slack_user_name(user_mappings, comment_user)

  comment = replace_mentions(user_mappings, comment)
  # comment = convert_forms(comment)
  # comment = convert_regex(comment)

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
    result = result.replace('@' + mapping['github_user_key'], '<@' + mapping['slack_id'] + '>')

  return result


def get_slack_user_name(user_mappings, comment_user):
  result = comment_user
  for mapping in user_mappings:
    if comment_user == mapping['github_user_key']:
      result = mapping['slack_name']

  return result


def convert_forms(comment):
  result = comment

  f = open(os.path.dirname(__file__) + '/github_slack_form_mappings.json')
  form_mappings = json.load(f)

  for key, value in form_mappings.items():
    result = result.replace(key, value)

  return result


def convert_regex(comment):
  result = comment

  # Quotes
  result = re.sub('\{quote\}', '```', result)

  # Links
  result = re.sub('\[([^|]+)\]', r'<\1>', result)
  result = re.sub('\[([^[\]|]+?)\|([^[\]|]+?)\]', '<\\2|\\1>', result)

  # Header TODO: fix
  result = re.sub('^h[0-6]\.(\s*)([^\n|^$]*)', '*\\2*', result)
  result = re.sub('\\nh[0-6]\.(\s*)([^\n|^$]*)', '\n*\\2*', result)

  # Lists
  result = re.sub('^[-|*|#]\s', '• ', result)
  result = re.sub('\\n[-|*|#]\s', '\\n• ', result)
  result = re.sub('\\n[-|*|#]{2}\s', '\n　• ', result)
  result = re.sub('\\n[-|*|#]{3}\s', '\n　　• ', result)
  result = re.sub('\\n[-|*|#]{4}\s', '\n　　　• ', result)
  result = re.sub('\\n[-|*|#]{5}\s', '\n　　　　• ', result)
  result = re.sub('\\n[-|*|#]{6}\s', '\n　　　　　• ', result)

  return result
