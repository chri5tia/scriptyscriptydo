#!/bin/bash

# Run sh refresh.sh to refresh healthcare

git checkout develop
git fetch origin
git rebase origin/develop
ddev composer install
ddev restart
ddev setup
