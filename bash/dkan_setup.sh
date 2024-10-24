#!/bin/bash

mkdir dkan
cd dkan
ddev config --auto
ddev get getdkan/ddev-dkan
ddev restart
ddev dkan-init --moduledev
ddev dkan-site-install
ddev dkan-frontend-install
ddev dkan-frontend-build
