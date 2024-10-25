#!/bin/bash

# Run sh notes/updates.sh to for composer updates

# TODO: Prompt to run refresh or start first
echo "*** Run the refresh or start script first ***"
# sh notes/refresh.sh
ddev composer update -W
cd patches
# git apply --reject *
ddev drush updb > dbupdates.txt
ddev drush updb -y
ddev drush cex -y
