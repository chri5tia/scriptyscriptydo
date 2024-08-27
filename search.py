import subprocess
import sys

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

