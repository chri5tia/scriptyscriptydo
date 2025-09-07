#!/bin/bash

git checkout develop
git fetch origin
git rebase origin/develop
ddev restart
ddev composer install
ddev setup-backend
ddev setup-frontend
say Finished!
