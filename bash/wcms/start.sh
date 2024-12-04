#!/bin/bash

ddev restart
ddev composer install
ddev drush updb -y
ddev drush cim -y
say Finished!
