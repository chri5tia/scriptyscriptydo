#!/bin/bash

# Define the target directory
TARGET_DIR="$HOME/Temporary"

# Check if directory exists to avoid errors
if [ -d "$TARGET_DIR" ]; then
    # Find files older than 7 days and delete them
    find "$TARGET_DIR" -type f -mtime +7 -delete
    
    # Optional: Remove empty directories older than 7 days
    find "$TARGET_DIR" -type d -empty -mtime +7 -delete

    # Let me know it's done
    say Temporary files are clean!
fi
