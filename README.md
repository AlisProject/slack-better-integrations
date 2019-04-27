JIRA - Slack better integration
===

# Prerequisite
- serverless
- docker
- direnv

# Usage

```bash
cp -p jira_slack_user_mappings.json.txt.sample jira_slack_user_mappings.json.txt

# Edit `jira_user_mappings`
vi jira_slack_user_mappings.json.txt
``` 

## Helper

### For list Slack users

```bash
pip install -r requirements_env.txt

# Add Slack API Token to `SLACK_API_TOKEN`
direnv edit

./create_slack_usermappings.py
```

### For list JIRA users

```bash
pip install -r requirements_env.txt

# Add JIRA information to `JIRA_*`
direnv edit

./get_jira_users.py
```

# Deployment

```bash
sls deploy
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
 
