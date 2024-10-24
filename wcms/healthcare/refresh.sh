#!/bin/bash

# Run sh refresh.sh to refresh healthcare

ddev auth ssh
git checkout develop
git fetch origin
git rebase origin/develop
ddev restart
ddev composer install
ddev setup
ddev copy-db
cd docroot/frontend

