#!/bin/bash
git credential-cache exit
ddev composer clear-cache
ddev composer config --global --unset github-oauth.github.cms.gov
ddev composer dump-autoload --optimize
rm -rf vendor
mv .ddev/.env .ddev/.env.bak
ddev auth ssh
ddev restart
echo "Done."
say BOOOOOOM!
