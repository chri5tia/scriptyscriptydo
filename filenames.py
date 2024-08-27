import re
import os
import sys
import time

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
    print(f"{label}:")
    print(f"  Path: {filepath}")
    print(f"  Size: {metadata['size']} bytes")
    print(f"  Creation Date: {metadata['creation_time']}")
    print(f"  Modification Date: {metadata['modification_time']}\n")

def suggest_new_name(file_name):
    # Suggest a new name based on the first four digits found in the name
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
    # Define the expected patterns
    patterns = [
        re.compile(r'^IMG_\d{4}\.JPG$'),
        re.compile(r'^IMG_\d{4}\.CR2$'),
        re.compile(r'^MVI_\d{4}\.MOV$')
    ]

    # List all files in the given directory
    files = os.listdir(directory)

    # Check each file against the patterns
    out_of_pattern_files = [f for f in files if not any(pattern.match(f) for pattern in patterns)]

    if out_of_pattern_files:
        print("Files that do not match the patterns:")
        for file in out_of_pattern_files:
            print(file)
            suggested_name = suggest_new_name(file)
            if suggested_name:
                new_path = os.path.join(directory, suggested_name)
                if os.path.exists(new_path):
                    # Display metadata for both files
                    display_file_info(os.path.join(directory, file), "Original File")
                    display_file_info(new_path, "Existing Target File")

                    # Ask the user if they want to overwrite the existing file
                    response = input(f"A file named '{suggested_name}' already exists. Do you want to overwrite it? (y/n): ").lower()
                    if response == 'y':
                        old_path = os.path.join(directory, file)
                        os.rename(old_path, new_path)
                        print(f"Overwritten and renamed '{file}' to '{suggested_name}'.")
                    else:
                        print(f"Skipped renaming '{file}'.")
                else:
                    # Ask the user if they want to rename the file
                    response = input(f"Do you want to rename '{file}' to '{suggested_name}'? (y/n): ").lower()
                    if response == 'y':
                        old_path = os.path.join(directory, file)
                        os.rename(old_path, new_path)
                        print(f"Renamed '{file}' to '{suggested_name}'.")
                    else:
                        print(f"Skipped renaming '{file}'.")
            else:
                print(f"No suggestion for renaming '{file}'.")
    else:
        print("All files match the patterns.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 filenames.py <directory>")
    else:
        directory = sys.argv[1]
        if not os.path.isdir(directory):
            print(f"The directory '{directory}' does not exist.")
        else:
            check_files(directory)
