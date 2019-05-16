Slack better integration
===

# Prerequisite
- docker
- direnv

# JIRA

## Usage

```bash
cp -p jira_slack_user_mappings.json.txt.sample jira_slack_user_mappings.json.txt

# Edit `jira_user_mappings`
vi jira_slack_user_mappings.json.txt
``` 

### Helper

#### For list Slack users

```bash
pip install -r requirements_env.txt

# Add Slack API Token to `SLACK_API_TOKEN`
direnv edit

./create_slack_usermappings.py
```

#### For list JIRA users

```bash
pip install -r requirements_env.txt

# Add JIRA information to `JIRA_*`
direnv edit

./get_jira_users.py
```

# GitHub

## Usage

Add WebHook setting to GitHub.
- https://github.com/YOUR_NAME_HERE/YOUR_REPOSITORY_HERE/settings/hooks
  - Payload URL: The URL that generated by deployment.
  - Content Type: application/json
  - Which events would you like to trigger this webhook?:
    - Let me select individual events.:
      - Issue comments
      - Pull request reviews
      - Pull request review comments


# Deployment

```bash
yarn deploy
```

# Local test

- prerequisite: `python-lambda-local`

```bash
pip install python-lambda-local
```

- exec:
  
```bash
python-lambda-local -f hello handler.py empty_event.json
``` 
 
