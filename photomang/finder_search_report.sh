# ------------------------------------------------------------------------------
# finder_search_report.sh
#
# Description:
#   Captures the current search term from the frontmost Finder window on macOS
#   and appends it to a persistent log at:
#       ~/Library/Logs/finder_searches.txt
#   Each entry is recorded as:
#       "search term" - mm/dd/yy
#   The file is then made unique and sorted in-place (sort -u).
#
# Usage:
#   bash finder_search_report.sh
#   # or:
#   chmod +x finder_search_report.sh && ./finder_search_report.sh
#
# Behavior:
#   - Uses AppleScript via `osascript` to read the front Finder window title.
#   - Extracts the term from titles like: Searching “Studio”
#   - Skips logging if there is no active Finder search.
#   - Appends a line: "<term>" - MM/DD/YY
#   - De-duplicates and sorts the entire log: `sort -u` (note: loses original order).
#
# Outputs:
#   - ~/Library/Logs/finder_searches.txt
#       Example:
#         "Studio" - 09/07/25
#         "IMG_6675" - 09/06/25
#
# Requirements:
#   - macOS with Finder running.
#   - `osascript` (AppleScript) available.
#   - Script must have permission to control Finder (System Settings > Privacy & Security > Automation/Accessibility, if prompted).
#
# Notes:
#   - The extraction relies on Finder’s English title pattern “Searching “…”.
#     If your system is localized or Finder changes its window title format,
#     update the sed expression accordingly.
#   - Log is deduplicated and sorted lexicographically; if you want to preserve
#     chronological order or keep multiple dates per term, remove the final
#     `sort -u` line.
#   - The search *path* is not logged by design.
#   - To run automatically (e.g., every few minutes), add a LaunchAgent (launchd)
#     that calls this script; place the .plist in ~/Library/LaunchAgents.
# ------------------------------------------------------------------------------


#!/bin/bash

# Path to the log file
LOG_FILE="$HOME/Library/Logs/finder_searches.txt"

# Create the log file if it doesn't exist
if [ ! -f "$LOG_FILE" ]; then
    touch "$LOG_FILE"
fi

# Run AppleScript to capture the search term from Finder
SEARCH_QUERY=$(osascript -e '
tell application "Finder"
    try
        set search_query to the name of the front Finder window
    on error
        set search_query to "No Active Search"
    end try
end tell

-- Extract only the part between the quotes, e.g., Searching “Studio” becomes Studio
do shell script "echo " & quoted form of search_query & " | sed -E \"s/Searching [“'\''](.*)[”'\'']/\\1/\""
')

# Format the date for the log
DATE=$(date '+%m/%d/%y')

# Log the search query and date if the search is active
if [[ "$SEARCH_QUERY" != "No Active Search" && -n "$SEARCH_QUERY" ]]; then
    echo "\"$SEARCH_QUERY\" - $DATE" >> "$LOG_FILE"
fi

# Remove duplicates and sort the file
sort -u "$LOG_FILE" -o "$LOG_FILE"
