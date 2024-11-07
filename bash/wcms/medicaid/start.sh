#!/bin/bash

# Run sh.start when starting on a new branch

git checkout develop
git fetch origin
git rebase origin/develop
ddev restart
ddev composer install
