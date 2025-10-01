#!/bin/bash

ddev restart
ddev auth ssh
ddev composer clear-cache
git checkout develop
git fetch origin
git rebase origin/develop
ddev composer install
ddev setup
ddev copy-db

say Finished!
