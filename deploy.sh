#!/usr/bin/env bash

# Packaging Layers
cd layers/common
./package.sh

# Deploy
cd ../..
sls deploy