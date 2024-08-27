import os
import re
import time
import sys

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
    print(f"  Size: {readable_size} ({metadata['size']} bytes)")  # Added exact size in bytes
def search_files_for_duplicates(base_directory):
    file_dict = {}
    for root, _, files in os.walk(base_directory):
        # Skip Trash folders
        if 'Trash' in root:
            continue
        for file in files:
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
                                    tag_duplicate(path)
                                    duplicate_count += 1
                            print(f"Keeping '{file_paths[keep_index]}' and tagging others as duplicates.")
                            break
                        else:
                            print("Invalid file number. Please try again.")
                    except ValueError:
                        print("Invalid input. Please enter 'a' to keep all files or a valid file number (1, 2, etc.).")

    print(f"\nTotal files marked as duplicates: {duplicate_count}")

def search_files_for_duplicates(base_directory):
    """Search through all directories for files with similar names."""
    file_dict = {}

    for root, _, files in os.walk(base_directory):
        if 'Trash' in root:
            continue  # Skip Trash folders
        for file in files:
            match = re.match(r'(IMG_\d{4})[\s\S]*?(\.\w+)', file)
            if match:
                file_id = match.group(1)
                extension = match.group(2)
                key = f"{file_id}{extension}"
                if key not in file_dict:
                    file_dict[key] = []
                file_dict[key].append(os.path.join(root, file))

    return file_dict

def tag_duplicate(filepath):
    """Tag a file as a duplicate by renaming it with a _DUPLICATE suffix."""
    directory, filename = os.path.split(filepath)
    name, ext = os.path.splitext(filename)
    duplicate_name = f"{name}_DUPLICATE{ext}"
    duplicate_path = os.path.join(directory, duplicate_name)

    os.rename(filepath, duplicate_path)
    print(f"Tagged '{filepath}' as a duplicate.")

def get_external_volumes():
    """Get a list of external mounted volumes (for macOS/Linux)."""
    external_volumes = []
    volumes_dir = "/Volumes"

    if os.path.isdir(volumes_dir):
        for volume in os.listdir(volumes_dir):
            volume_path = os.path.join(volumes_dir, volume)
            if os.path.ismount(volume_path):
                # Only add external volumes, exclude system volumes
                external_volumes.append(volume_path)

    return external_volumes

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 find_duplicates.py <starting_directory>")
    else:
        starting_directory = sys.argv[1]
        if not os.path.isdir(starting_directory):
            print(f"The directory '{starting_directory}' does not exist.")
        else:
            # Get only external volumes to search
            volumes_to_search = get_external_volumes()
            volumes_to_search.append(starting_directory)  # Add the starting directory

            for volume in volumes_to_search:
                print(f"Searching in {volume}...")
                file_dict = search_files_for_duplicates(volume)
                resolve_duplicates(file_dict)
