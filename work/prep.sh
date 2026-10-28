#!/bin/bash

git fetch origin
git rebase origin/develop
rm -r docroot/modules/contrib
rm -r vendor
read -p "New project setup? (y/n): " project
if [[ "$project" =~ ^[Yy]$ ]]; then
    read -p "Enter the ticket name: " ticket
    git checkout -b "$ticket"
    echo "Created branch: $ticket"
else
    echo "Okay, continuing on with the main branch..."
fi
ddev composer install
ddev setup
say Finished!
