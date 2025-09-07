"""
This script automatically tags duplicate photos in one directory by comparing
them against a reference directory. It groups files by camera-style ID
(IMG_#### + SAME extension) and, for every group that also exists in the
comparison directory, renames the files in the ANALYZE directory by appending
"_DUPLICATE" before the extension. A cumulative report of changes is appended
to 'duplicates_report.txt'.

Usage:
    python3 autodup.py

Interactive flow:
    1) Prompts for:
       - Analyze directory (files here may be renamed).
       - Comparison directory (used only to detect duplicates).
       - Comma-separated list of subdirectory paths to ignore.
         (These must be absolute paths to match the internal check.)
    2) Asks for final confirmation summarizing the inputs.
    3) Scans the analyze directory recursively (skipping any ignored subdirs).
    4) Any file whose key (IMG_#### + extension) appears in the comparison
       directory is tagged as a duplicate by renaming:
         "<name><ext>" → "<name>_DUPLICATE<ext>".

Matching rule:
    - Filenames must START with the pattern: IMG_#### (four digits), followed by
      anything, and a standard extension. Example matches:
        IMG_0123.JPG, IMG_0123 edit.jpg, IMG_0123-final.CR2
    - The grouping key is strictly "IMG_####<extension>" (same case of extension).

Behavior:
    - Hidden files (names starting with ".") are ignored.
    - Files already containing "_DUPLICATE" in the base name are ignored.
    - The comparison is by name pattern only (no byte-size or content checks).
    - For each affected file in the analyze directory, the script renames it
      to include "_DUPLICATE" before the extension.
    - Appends a timestamped list of all renamed files to 'duplicates_report.txt'
      in the current working directory.

Notes:
    - Destructive renames (no undo). Test on a copy first.
    - On macOS (case-insensitive FS), be mindful of case-only differences.
    - If a file with the exact target name already exists, the underlying
      os.rename behavior may overwrite or fail depending on the OS/FS.
    - The "ignored directories" filter compares absolute paths; provide full,
      absolute paths for reliability (e.g., "/Volumes/T7 Touch/Photos/Gallery").
"""


import os
import re
import time
from datetime import datetime

def append_to_report(directory, script_name):
    """Appends the date, time, and script name to a report file."""
    report_path = os.path.join(directory, 'execution_report.txt')
    with open(report_path, 'a') as report:
        report.write(f"Script '{script_name}' executed on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

def is_hidden(filepath):
    return os.path.basename(filepath).startswith('.')

def human_readable_size(size_in_bytes):
    """Convert a file size in bytes to a human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024

def get_file_metadata(filepath):
    """Get metadata of a file such as size, creation date, and modification date."""
    stats = os.stat(filepath)
    size = stats.st_size  # in bytes
    creation_time = time.ctime(stats.st_ctime)  # File creation time
    modification_time = time.ctime(stats.st_mtime)  # Last modification time

    return {
        'size': size,
        'creation_time': creation_time,
        'modification_time': modification_time
    }

def display_file_info(filepath, label):
    """Prints the metadata of a file."""
    metadata = get_file_metadata(filepath)
    readable_size = human_readable_size(metadata['size'])
    print(f"{label}:")
    print(f"  Path: {filepath}")
    print(f"  Size: {readable_size} ({metadata['size']} bytes)")
    print(f"  Creation Date: {metadata['creation_time']}")
    print(f"  Modification Date: {metadata['modification_time']}\n")

def search_files_for_duplicates(base_directory, ignore_dirs):
    """Search through specified directory for files with similar names, disregarding _DUPLICATE files."""
    file_dict = {}

    for root, dirs, files in os.walk(base_directory):
        # Skip directories that are in the ignore list
        dirs[:] = [d for d in dirs if os.path.join(root, d) not in ignore_dirs]
        
        for file in files:
            # Skip hidden files
            if is_hidden(file):
                continue
            # Ignore files with _DUPLICATE in their names
            if '_DUPLICATE' in file:
                continue
            match = re.match(r'(IMG_\d{4})[\s\S]*?(\.\w+)', file)
            if match:
                file_id = match.group(1)
                extension = match.group(2)
                key = f"{file_id}{extension}"
                if key not in file_dict:
                    file_dict[key] = []
                file_dict[key].append(os.path.join(root, file))

    return file_dict

def resolve_duplicates(file_dict, comparison_directory, ignore_dirs):
    """Automatically marks duplicates based on comparison with another directory."""
    duplicate_count = 0  # Counter for duplicate files
    changed_files = []  # List to track renamed files

    # Get all files in the comparison directory
    comparison_files = search_files_for_duplicates(comparison_directory, ignore_dirs)

    for key, file_paths in file_dict.items():
        if key in comparison_files:
            for i, path in enumerate(file_paths):
                new_path = tag_duplicate(path)
                changed_files.append(new_path)  # Track the renamed file path
                duplicate_count += 1

    print(f"\nTotal files marked as duplicates: {duplicate_count}")

    # Save the list of changed files to a report
    save_report(changed_files)

def tag_duplicate(filepath):
    """Tag a file as a duplicate by renaming it with a _DUPLICATE suffix, unless it already has it."""
    directory, filename = os.path.split(filepath)
    name, ext = os.path.splitext(filename)

    # Avoid renaming if the file already has _DUPLICATE in its name
    if '_DUPLICATE' not in name:
        duplicate_name = f"{name}_DUPLICATE{ext}"
        duplicate_path = os.path.join(directory, duplicate_name)
        os.rename(filepath, duplicate_path)
        print(f"Tagged '{filepath}' as a duplicate.")
        return duplicate_path
    else:
        print(f"'{filepath}' already marked as duplicate. No changes made.")
        return filepath

def save_report(changed_files):
    """Append the list of changed files to a report file with the date and activities."""
    report_file = "duplicates_report.txt"
    with open(report_file, 'a') as report:
        report.write(f"\nReport generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.write("Files marked as duplicates:\n")
        for file_path in changed_files:
            report.write(f"{file_path}\n")
        report.write("\n")
    print(f"\nReport appended to '{report_file}'")

if __name__ == "__main__":
    # Ask the user for the directory to analyze and the one to compare with
    analyze_directory = input("Enter the directory to analyze and mark files in: ").strip()
    comparison_directory = input("Enter the directory to compare files with: ").strip()

    # Ask the user for directories to ignore
    ignore_dirs_input = input("Enter any subdirectories to ignore (comma-separated paths): ").strip()
    ignore_dirs = [os.path.abspath(dir.strip()) for dir in ignore_dirs_input.split(',')] if ignore_dirs_input else []

    # Confirm the directories with the user
    confirmation = input(f"Are you sure you want to search for duplicates in '{analyze_directory}' comparing with '{comparison_directory}' and ignoring {ignore_dirs}? (yes/no): ").strip().lower()

    if confirmation == 'yes':
        print(f"Searching in {analyze_directory} and comparing with {comparison_directory}...")
        file_dict = search_files_for_duplicates(analyze_directory, ignore_dirs)
        resolve_duplicates(file_dict, comparison_directory, ignore_dirs)
    else:
        print("Operation canceled.")

