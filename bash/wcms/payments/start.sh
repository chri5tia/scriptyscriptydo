#!/bin/bash

# Run sh.start when starting on a new branch

git fetch origin
git rebase origin/develop
ddev restart
ddev composer install
