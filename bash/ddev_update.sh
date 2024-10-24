#!/bin/bash

echo	"Upgrading ddev..."
brew upgrade ddev
echo	"Deleting ddev images..."
ddev delete images --all
echo	"run ddev config --auto in each environment"
echo	"Finished upgrading ddev..."
