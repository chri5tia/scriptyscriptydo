#!/bin/bash

# Source directory
SOURCE="/Volumes/T7 Touch/Izar Extension/Documents/Beargoyles/"
# Destination directory
DESTINATION="/Users/christia/Documents/Beargoyles (Copy)"

# Rsync command to sync without copying Notes folders
rsync -av --delete --exclude="Notes/" --exclude="*/Notes/" "$SOURCE" "$DESTINATION"

# Exit script
exit 0

