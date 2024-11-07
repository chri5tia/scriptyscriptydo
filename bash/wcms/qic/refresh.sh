#!/bin/bash

# Run sh refresh.sh to refresh healthcare

git checkout develop
git fetch origin
git rebase origin/develop
ddev restart
ddev composer install
ddev setup-backend
ddev setup-frontend
