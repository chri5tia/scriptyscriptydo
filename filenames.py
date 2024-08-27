import re
import os
import sys
import time

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
    creation_time = time.ctime(stats.st_ctime)
    modification_time = time.ctime(stats.st_mtime)

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
    print(f"  Size: {readable_size}")
    print(f"  Creation Date: {metadata['creation_time']}")
    print(f"  Modification Date: {metadata['modification_time']}\n")

def suggest_new_name(file_name):
    """Suggest a new name based on the first four digits found in the name."""
    match = re.search(r'\d{4}', file_name)
    if match:
        number = match.group(0)
        if file_name.lower().endswith('.jpg'):
            return f"IMG_{number}.JPG"
        elif file_name.lower().endswith('.cr2'):
            return f"IMG_{number}.CR2"
        elif file_name.lower().endswith('.mov'):
            return f"MVI_{number}.MOV"
    return None

def check_files(directory):
    """Check files and rename them unless the target name already exists."""
    # Define the expected patterns
    patterns = [
        re.compile(r'^IMG_\d{4}\.JPG$'),
        re.compile(r'^IMG_\d{4}\.CR2$'),
        re.compile(r'^MVI_\d{4}\.MOV$')
    ]

    # List to store skipped files due to already having a target name
    skipped_files = []

    # List all files in the given directory
    files = os.listdir(directory)

    # Check each file against the patterns
    out_of_pattern_files = [f for f in files if not any(pattern.match(f) for pattern in patterns)]

    if out_of_pattern_files:
        for file in out_of_pattern_files:
            # Skip hidden dot-underscore files created by macOS
            if file.startswith("._"):
                continue

            suggested_name = suggest_new_name(file)
            if suggested_name:
                new_path = os.path.join(directory, suggested_name)
                old_path = os.path.join(directory, file)

                if os.path.exists(new_path):
                    # Display metadata for both files and skip renaming
                    display_file_info(old_path, "Original File")
                    display_file_info(new_path, "Existing Target File")
                    print(f"Skipping renaming of '{file}' to '{suggested_name}' because it already exists.\n")
                    skipped_files.append(file)
                else:
                    # Rename the file if the target name doesn't exist
                    os.rename(old_path, new_path)
                    print(f"Renamed '{file}' to '{suggested_name}'.\n")
            else:
                print(f"No suggestion for renaming '{file}'.")

    else:
        print("All files match the patterns.")

    # Print the list of skipped files due to target name already existing
    if skipped_files:
        print("\nThe following files were skipped because the target name already existed:")
        for skipped_file in skipped_files:
            print(f" - {skipped_file}")
    else:
        print("\nNo files were skipped due to target name conflicts.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 filenames.py <directory>")
    else:
        directory = sys.argv[1]
        if not os.path.isdir(directory):
            print(f"The directory '{directory}' does not exist.")
        else:
            check_files(directory)
