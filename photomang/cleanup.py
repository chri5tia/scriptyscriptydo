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
