#!/bin/bash

git fetch origin && git rebase origin/develop
ddev restart
rm -r docroot/modules/contrib
rm -r vendor
ddev composer install
ddev setup
# ddev auth ssh
# ddev copy-db --env @openpayments.prod
say Finished!
