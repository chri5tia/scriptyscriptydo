#!/bin/bash

# Run sh refresh.sh to refresh healthcare

git fetch origin
git rebase origin/develop
ddev composer install
ddev restart
ddev setup
say Finished!
