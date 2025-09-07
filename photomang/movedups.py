import os
import shutil

def is_hidden(filepath):
    """Check if a file or directory is hidden."""
    # Check if the file or directory starts with a dot (.)
    return os.path.basename(filepath).startswith('.') or '/.' in filepath

def create_autodups_folder():
    """Create the 'autodups' folder if it doesn't already exist."""
    autodups_folder = os.path.join(os.getcwd(), 'autodups')
    if not os.path.exists(autodups_folder):
        os.makedirs(autodups_folder)
    return autodups_folder

def move_duplicate_files_to_autodups():
    """Move all non-hidden files with '_DUPLICATE' in their name to the 'autodups' folder."""
    current_directory = os.getcwd()
    autodups_folder = create_autodups_folder()

    moved_files = 0

    for root, _, files in os.walk(current_directory):
        # Skip the 'autodups' folder itself
        if 'autodups' in root:
            continue
        for file in files:
            file_path = os.path.join(root, file)
            if '_DUPLICATE' in file and not is_hidden(file_path):
                try:
                    destination_path = os.path.join(autodups_folder, file)
                    shutil.move(file_path, destination_path)
                    print(f"Moved: {file_path} -> {destination_path}")
                    moved_files += 1
                except FileNotFoundError:
                    print(f"File not found or already moved: {file_path}")
                except Exception as e:
                    print(f"An error occurred while moving {file_path}: {e}")

    if moved_files == 0:
        print("No files with '_DUPLICATE' found.")
    else:
        print(f"Total files moved: {moved_files}")

if __name__ == "__main__":
    move_duplicate_files_to_autodups()
