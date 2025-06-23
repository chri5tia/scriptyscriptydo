#!/bin/bash

ddev composer clear-cache
ddev composer config --global --unset github-oauth.github.cms.gov
ddev composer dump-autoload --optimize
rm -rf vendor
mv .ddev/.env .ddev/.env.bak
ddev restart
ddev composer install
say BOOOOOOM!
