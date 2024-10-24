#!/bin/bash

# Define source directories to back up
INCLUDE=(
    "/Applications"
    "/Users/christia/.bashrc"
    "/Users/christia/.command_log"
    "/Users/christia/.ssh"
    "/Users/christia/.zprofile"
    "/Users/christia/.zshrc"
    "/Users/christia/Desktop"
    "/Users/christia/Documents"
    "/Users/christia/Downloads"
    "/Users/christia/Movies"
    "/Users/christia/Music"
    "/Users/christia/Pictures"
    "/Users/christia/Public"
    "/Users/christia/Safe"
)

# Destination for the backup
DESTINATION="/Volumes/Seagate/Izar/"

# Build the rsync command with include options
for dir in "${INCLUDE[@]}"; do
    rsync -avh --delete "$dir" "$DESTINATION"
done

echo "Backup completed successfully."

