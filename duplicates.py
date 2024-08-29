import os
import re
import time
import sys
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

def search_files_for_duplicates(base_directory):
    """Search through all directories for files with similar names, disregarding _DUPLICATE files."""
    file_dict = {}

    for root, _, files in os.walk(base_directory):
        # Skip Trash folders
        if 'Trash' in root:
            continue
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

def resolve_duplicates(file_dict):
    """Resolve duplicates by asking the user which file to keep and tagging others."""
    duplicate_count = 0  # Counter for duplicate files
    skip_all_size_mismatches = False  # Flag to skip all results with different sizes
    changed_files = []  # List to track renamed files

    for key, file_paths in file_dict.items():
        if len(file_paths) > 1:
            print(f"\n{len(file_paths)} duplicates found for '{key}':")

            sizes = []
            for i, path in enumerate(file_paths):
                metadata = get_file_metadata(path)
                sizes.append(metadata['size'])  # Capture exact file sizes in bytes
                display_file_info(path, f"File {i + 1}")

            # Check if all file sizes are exactly the same in bytes
            if all(size == sizes[0] for size in sizes):
                print("All files have exactly the same size in bytes.\n")
            else:
                print("The files have different sizes in bytes.\n")

                if skip_all_size_mismatches:
                    print("Skipping these files due to different sizes (automatically).\n")
                    continue

                # Ask the user if they want to skip this result due to size difference
                skip_different_sizes = input("Do you want to skip these files because they have different sizes? ([y]es/[n]o/[s]kip all): ").lower()

                if skip_different_sizes == 'y':
                    print("Skipping these files due to different sizes.\n")
                    continue
                elif skip_different_sizes == 's':
                    skip_all_size_mismatches = True
                    print("Skipping these files and all future size mismatches.\n")
                    continue

            while True:
                response = input(f"Do you want to keep [a]ll files or choose a specific file by number (1, 2, etc.)? ").lower()

                if response == 'a':
                    print("Keeping all files. No duplicates will be tagged.")
                    break
                else:
                    try:
                        # Convert the input into a file index number
                        keep_index = int(response) - 1
                        if 0 <= keep_index < len(file_paths):
                            for i, path in enumerate(file_paths):
                                if i != keep_index:
                                    new_path = tag_duplicate(path)
                                    changed_files.append(new_path)  # Track the renamed file path
                                    duplicate_count += 1
                            print(f"Keeping '{file_paths[keep_index]}' and tagging others as duplicates.")
                            break
                        else:
                            print("Invalid file number. Please try again.")
                    except ValueError:
                        print("Invalid input. Please enter 'a' to keep all files or a valid file number (1, 2, etc.).")

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
    # Get the current working directory
    starting_directory = os.getcwd()

    # Confirm the directory with the user
    confirmation = input(f"Are you sure you want to search for duplicates in '{starting_directory}' and all its subdirectories? (yes/no): ").strip().lower()

    if confirmation == 'yes':
        print(f"Searching in {starting_directory}...")
        file_dict = search_files_for_duplicates(starting_directory)
        resolve_duplicates(file_dict)
    else:
        print("Operation canceled.")
