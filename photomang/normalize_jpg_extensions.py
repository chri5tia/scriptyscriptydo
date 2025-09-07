"""
This script recursively normalizes image file extensions in the current
working directory: it renames .jpg/.jpeg (any case) to .JPG, skipping
hidden files and avoiding collisions. Every run appends to a persistent
'extension_normalization_report.txt' in the root directory, listing what
was renamed and what was skipped (when the target filename already exists).

Usage:
    # From the folder you want to process:
    python3 normalize_jpg_extensions.py

Behavior:
    - Walks the current working directory and all subfolders.
    - Skips hidden files (names starting with '.').
    - Renames files with extensions .jpg/.jpeg (any capitalization) to .JPG.
    - Appends a run log to 'extension_normalization_report.txt' in the
      top-level directory, including 'Renamed Files' and 'Skipped Files'.

Notes:
    - If a target path already exists (e.g., 'photo.JPG' already there),
      the original file is skipped and recorded in the report.
    - On macOS and other case-insensitive filesystems, changing only the
      case of the extension usually works, but if the OS blocks a case-only
      rename due to a temporary collision, you may need a two-step rename
      (temp name -> final). This script attempts a direct rename.
    - Run it from the directory you want normalized (it does not accept
      a directory argument in its current form).
"""

import os
from datetime import datetime

def is_hidden(filepath):
    """Check if a file is hidden."""
    return os.path.basename(filepath).startswith('.')

def normalize_extensions(directory):
    """Normalize .jpg, .jpeg, .JPEG to .JPG in the directory and subdirectories."""
    report_path = os.path.join(directory, "extension_normalization_report.txt")
    renamed_files = []
    skipped_files = []

    for root, _, files in os.walk(directory):
        for file in files:
            if is_hidden(file):
                continue  # Skip hidden files

            old_path = os.path.join(root, file)
            base, ext = os.path.splitext(file)
            if ext.lower() in ['.jpg', '.jpeg']:
                new_file = f"{base}.JPG"
                new_path = os.path.join(root, new_file)

                if os.path.exists(new_path):
                    skipped_files.append((old_path, new_path))
                else:
                    os.rename(old_path, new_path)
                    renamed_files.append((old_path, new_path))

    # Write to the persistent report file
    with open(report_path, 'a') as report:
        report.write(f"\nNormalization Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.write("Renamed Files:\n")
        for old, new in renamed_files:
            report.write(f"  {old} -> {new}\n")
        if not renamed_files:
            report.write("  None\n")

        report.write("\nSkipped Files (Target file already exists):\n")
        for old, new in skipped_files:
            report.write(f"  {old} -> {new}\n")
        if not skipped_files:
            report.write("  None\n")

    print(f"Normalization completed. Report updated: {report_path}")

if __name__ == "__main__":
    # Get the current working directory
    current_directory = os.getcwd()
    print(f"Running normalization in: {current_directory}")
    normalize_extensions(current_directory)
