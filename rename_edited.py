import os
import sys
import re
from datetime import datetime

def get_files_with_sizes(directory):
    """Get files along with their sizes from the given directory."""
    files_with_sizes = {}
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            size = os.path.getsize(file_path)
            files_with_sizes[(file, size)] = file_path
    return files_with_sizes

def compare_directories(current_dir, compare_dir):
    """Compare two directories and find missing files in the current directory."""
    current_files = get_files_with_sizes(current_dir)
    compare_files = get_files_with_sizes(compare_dir)

    missing_files = []

    for file_info, file_path in current_files.items():
        if file_info not in compare_files:
            missing_files.append(file_path)

    return missing_files

def generate_new_name(file_name, version=1):
    """Generate a new name in the format *_xxxx-av"""
    # Try to find a 4-digit number in the original file name
    match = re.search(r'\d{4}', file_name)
    
    if match:
        # If a 4-digit number is found, use it
        number = match.group(0)
    else:
        # If no number is found, generate a new number
        number = "{:04d}".format(version)

    # Get the file extension (e.g., .jpg, .png)
    extension = os.path.splitext(file_name)[1]

    # Create the new name with the format *_xxxx-av*
    new_name = f"{os.path.splitext(file_name)[0]}_{number}-av{version}{extension}"

    return new_name

def rename_and_generate_report(missing_files):
    """Rename files and generate a report."""
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_name = f"RenamedFilesReport_{current_time}.txt"
    report_path = os.path.join(os.getcwd(), report_name)

    version_counter = 1  # To keep track of the versioning

    with open(report_path, "w") as report_file:
        for file in missing_files:
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
    if len(sys.argv) < 2:
        print("Usage: python3 script_name.py /path/to/compare_directory")
        sys.exit(1)

    current_dir = os.getcwd()
    compare_dir = sys.argv[1]

    missing_files = compare_directories(current_dir, compare_dir)

    if missing_files:
        rename_and_generate_report(missing_files)
    else:
        print("All files match by name and size. No files to rename.")

