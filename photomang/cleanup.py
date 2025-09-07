"""
This script scans a directory tree for files with redundant "_DUPLICATE"
suffixes (e.g., "IMG_1234_DUPLICATE_DUPLICATE.JPG") and cleans them up by
collapsing them into a single "_DUPLICATE". All changes are logged to a
persistent report file.

Usage:
    python3 cleanup.py

Behavior:
    - Starts at the current working directory (recursively scans subfolders).
    - Ignores hidden AppleDouble files (names beginning with "._").
    - Detects filenames containing repeated "_DUPLICATE" sequences.
    - Renames them by collapsing multiple "_DUPLICATE" suffixes into one.
      Example:
        "IMG_1234_DUPLICATE_DUPLICATE_DUPLICATE.JPG"
        → "IMG_1234_DUPLICATE.JPG"
    - Appends a timestamped log of each rename to
      "duplicate_cleanup_report.txt" in the working directory.
    - Prints each rename action to the console as well.

Notes:
    - Runs destructively (renames in place). There is no undo.
    - Existing files with the intended cleaned-up name may cause collisions;
      in that case, only a FileNotFoundError is caught.
    - The report file is cumulative — it appends new entries on each run.
    - Adjust `base_directory` and `report_file` in the code if you want to
      scan a different folder or store the report elsewhere.
"""


import os
import re
from datetime import datetime

def cleanup_duplicate_suffixes(base_directory, report_file):
    """Search for files with multiple _DUPLICATE suffixes and clean them up, logging the changes."""
    report_created = False

    with open(report_file, 'a') as report:
        for root, _, files in os.walk(base_directory):
            for file in files:
                # Skip hidden files (those starting with ._)
                if file.startswith('._'):
                    continue

                # Look for files with multiple _DUPLICATE suffixes
                if '_DUPLICATE_DUPLICATE' in file:
                    cleaned_file = re.sub(r'(_DUPLICATE)+', '_DUPLICATE', file)
                    old_path = os.path.join(root, file)
                    new_path = os.path.join(root, cleaned_file)

                    if old_path != new_path:
                        try:
                            os.rename(old_path, new_path)
                            # Log the renaming with date and time
                            log_entry = f"{datetime.now()}: Renamed '{old_path}' to '{new_path}'\n"
                            report.write(log_entry)
                            print(log_entry.strip())  # Also print to console
                            report_created = True
                        except FileNotFoundError as e:
                            print(f"Error renaming '{old_path}': {e}")

    if report_created:
        print(f"\nReport has been created or updated: '{report_file}'")

if __name__ == "__main__":
    base_directory = '.'  # Set the directory to the current one or specify another directory
    report_file = 'duplicate_cleanup_report.txt'  # Specify the report file name
    cleanup_duplicate_suffixes(base_directory, report_file)
