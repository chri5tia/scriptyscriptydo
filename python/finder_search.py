import subprocess
import sys
import os

from datetime import datetime

def append_to_report(directory, script_name):
    """Appends the date, time, and script name to a report file."""
    report_path = os.path.join(directory, 'execution_report.txt')
    with open(report_path, 'a') as report:
        report.write(f"Script '{script_name}' executed on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Call this at the start of the script
directory = os.path.dirname(os.path.realpath(__file__))
script_name = os.path.basename(__file__)
append_to_report(directory, script_name)

def search_file_in_finder(file_name):
    # AppleScript command to open a Finder window with the search results
    script = f'''
    tell application "Finder"
        activate
        set searchTerm to "{file_name}"
        set searchFolder to "/"
        open (POSIX file searchFolder) -- Open root directory in Finder
        delay 1
        tell application "System Events"
            keystroke searchTerm
        end tell
    end tell
    '''
    # Run the AppleScript via osascript
    subprocess.run(["osascript", "-e", script])

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 search.py <filename>")
    else:
        file_name = sys.argv[1]
        search_file_in_finder(file_name)

