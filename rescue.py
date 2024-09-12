import os
import re
import sys
from datetime import datetime

def get_files_to_rename(directory):
    """Get all files in the directory that match the IMG_xxxx pattern."""
    files_to_rename = []
    for root, _, files in os.walk(directory):
        for file in files:
            # Match files that follow the IMG_xxxx pattern
            if re.match(r'IMG_\d{4}', file):
                file_path = os.path.join(root, file)
                files_to_rename.append(file_path)
    return files_to_rename

def generate_new_name(file_name, version=1):
    """Generate a new name in the format IMG_xxxx-av1."""
    # Extract the IMG_xxxx part from the original file name
    match = re.search(r'(IMG_\d{4})', file_name)

    if match:
        base_name = match.group(1)
    else:
        return file_name  # If no match, return the original name

    # Get the file extension (e.g., .jpg, .png)
    extension = os.path.splitext(file_name)[1]

    # Create the new name with the format IMG_xxxx-av1
    new_name = f"{base_name}-av{version}{extension}"

    return new_name

def rename_files(files_to_rename):
    """Rename files and generate a report."""
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_name = f"RenamedFilesReport_{current_time}.txt"
    report_path = os.path.join(os.getcwd(), report_name)

    version_counter = 1  # To keep track of the versioning

    with open(report_path, "w") as report_file:
        for file in files_to_rename:
            original_name = os.path.basename(file)
            new_name = generate_new_name(original_name, version=version_counter)
            version_counter += 1

            # Rename the file
            new_path = os.path.join(os.path.dirname(file), new_name)
            os.rename(file, new_path)

            # Write to the report
            report_file.write(f"Renamed: {file} -> {new_path}\n")

    print(f"Report saved to '{report_path}'")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 script_name.py /path/to/directory")
        sys.exit(1)

    directory = sys.argv[1]

    # Get all IMG_xxxx files in the directory
    files_to_rename = get_files_to_rename(directory)

    if files_to_rename:
        rename_files(files_to_rename)
    else:
        print("No files found matching the IMG_xxxx pattern.")
