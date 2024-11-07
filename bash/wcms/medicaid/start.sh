#!/bin/bash

# Run sh.start when starting on a new branch

git checkout develop
git fetch origin
git rebase origin/develop
ddev restart
ddev composer install
ddev drush updb
ddev drush cim -y
say Finished!
