#!/usr/bin/env bash

# Packaging Layers
cd layers/common
./package.sh

# Deploy
cd ../..
sls deploy

# Notification for Mac
if [ "$(uname)" == 'Darwin' ]; then
  osascript -e 'display notification "Done." with title "Deploy Script"'
fi
