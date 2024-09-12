import os

def remove_duplicate_suffix():
    # Get the current directory
    current_directory = os.getcwd()
    
    # Iterate through the files in the current directory
    for filename in os.listdir(current_directory):
        # Check if the file contains '_DUPLICATE'
        if '_DUPLICATE' in filename:
            # Create a new name by replacing '_DUPLICATE' with an empty string
            new_filename = filename.replace('_DUPLICATE', '')
            # Get full paths for renaming
            old_filepath = os.path.join(current_directory, filename)
            new_filepath = os.path.join(current_directory, new_filename)
            # Rename the file
            os.rename(old_filepath, new_filepath)
            print(f'Renamed: {filename} -> {new_filename}')

if __name__ == "__main__":
    remove_duplicate_suffix()

