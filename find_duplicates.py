import os
import re
import time
import sys
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS

def human_readable_size(size_in_bytes):
    """Convert a file size in bytes to a human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024

def get_file_metadata(filepath):
    """Get metadata of a file such as size, original content creation date, and file creation date."""
    stats = os.stat(filepath)
    size = stats.st_size  # in bytes
    file_creation_time = time.ctime(stats.st_ctime)

    # Try to get the original content creation date for media files (e.g., photos)
    original_creation_time = None
    if filepath.lower().endswith(('.jpg', '.jpeg', '.png', '.tiff')):
        try:
            image = Image.open(filepath)
            exif_data = image._getexif()
            if exif_data is not None:
                for tag, value in exif_data.items():
                    tag_name = TAGS.get(tag, tag)
                    if tag_name == "DateTimeOriginal":
                        original_creation_time = value
                        break
        except Exception as e:
            print(f"Error reading EXIF data for {filepath}: {e}")

    return {
        'size': size,
        'original_creation_time': original_creation_time,
        'file_creation_time': file_creation_time
    }

def display_file_info(filepath, label):
    """Prints the metadata of a file."""
    metadata = get_file_metadata(filepath)
    readable_size = human_readable_size(metadata['size'])
    print(f"{label}:")
    print(f"  Path: {filepath}")
    print(f"  Size: {readable_size}")

    # Display original content creation time if available
    if metadata['original_creation_time']:
        print(f"  Original Content Creation Date: {metadata['original_creation_time']}")
    else:
        print(f"  Original Content Creation Date: Not available or not applicable")

    print(f"  File Creation Date: {metadata['file_creation_time']}\n")

                if response == 'all':
                    print("Keeping all files. No duplicates will be tagged.")
                    break
                elif response == 'one':
                    keep_index = input(f"Which file do you want to keep? (Enter the file number): ")
                    try:
                        keep_index = int(keep_index) - 1
                        if 0 <= keep_index < len(file_paths):
                            for i, path in enumerate(file_paths):
                                if i != keep_index:
                                    tag_duplicate(path)
                                    duplicate_count += 1  # Increment the duplicate counter
                            print(f"Keeping '{file_paths[keep_index]}' and tagging others as duplicates.")
                            break
                        else:
                            print("Invalid file number. Please try again.")
                    except ValueError:
                        print("Please enter a valid number.")
                else:
                    print("Invalid response. Please type 'one' or 'all'.")

    print(f"\nTotal files marked as duplicates: {duplicate_count}")

def tag_duplicate(filepath):
    """Tag a file as a duplicate by renaming it with a _DUPLICATE suffix."""
    directory, filename = os.path.split(filepath)
    name, ext = os.path.splitext(filename)
    duplicate_name = f"{name}_DUPLICATE{ext}"
    duplicate_path = os.path.join(directory, duplicate_name)

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
