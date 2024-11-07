#!/bin/bash

# Run sh refresh.sh to refresh payments

git fetch origin && git rebase origin/develop
ddev restart
ddev composer install
ddev setup
say Finished!
