#!/bin/bash

# Run sh refresh.sh to refresh payments

git fetch origin && git rebase origin/develop
ddev restart
ddev composer install
ddev site-install
ddev drush @sdismedicaid.prod sql-dump --structure-tables-list='cache_*,queue,batch' --skip-tables-list='cache_*,queue,batch' -Dssh.tty=0 > backups/production.sql
ddev import-db --file ./backups/production.sql
say Finished!
