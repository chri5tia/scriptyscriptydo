import re
import os
import sys
import time
from datetime import datetime

def is_hidden(filepath):
    """Check if a file is hidden."""
    return os.path.basename(filepath).startswith('.')

def append_to_report(directory, script_name):
    """Appends the date, time, and script name to a report file."""
    report_path = os.path.join(directory, 'execution_report.txt')
    if not is_hidden(report_path):
        with open(report_path, 'a') as report:
            report.write(f"Script '{script_name}' executed on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Call this at the start of the script
directory = os.path.dirname(os.path.realpath(__file__))
script_name = os.path.basename(__file__)
append_to_report(directory, script_name)

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

def write_report(report_path, renamed_files, skipped_files):
    """Write a report with the renamed and skipped files."""
    if not is_hidden(report_path):
        with open(report_path, 'w') as report:
            report.write(f"Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            if renamed_files:
                report.write("Renamed Files:\n")
                for old_name, new_name in renamed_files:
                    report.write(f"  {old_name} -> {new_name}\n")
            else:
                report.write("No files were renamed.\n")

            if skipped_files:
                report.write("\nSkipped Files (Target name already existed):\n")
                for skipped_file in skipped_files:
                    report.write(f"  {skipped_file}\n")
            else:
                report.write("\nNo files were skipped due to target name conflicts.\n")

def check_files(directory):
    """Check files and rename them unless the target name already exists or the file is marked as a duplicate."""
    # Define the expected patterns
    patterns = [
        re.compile(r'^IMG_\d{4}\.JPG$'),
        re.compile(r'^IMG_\d{4}\.CR2$'),
        re.compile(r'^MVI_\d{4}\.MOV$')
    ]

    # Lists to store renamed and skipped files
    renamed_files = []
    skipped_files = []

    # List all files in the given directory
    files = os.listdir(directory)

    # Check each file against the patterns
    out_of_pattern_files = [f for f in files if not any(pattern.match(f) for pattern in patterns)]

    if out_of_pattern_files:
        for file in out_of_pattern_files:
            # Skip hidden files, dot-underscore files created by macOS, and files with _DUPLICATE in the name
            if is_hidden(file) or file.startswith("._") or "_DUPLICATE" in file:
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
                    renamed_files.append((file, suggested_name))
            else:
                print(f"No suggestion for renaming '{file}'.")

    else:
        print("All files match the patterns.")

    # Write the report
    report_path = os.path.join(directory, f"renaming_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    write_report(report_path, renamed_files, skipped_files)
    print(f"\nReport generated: {report_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 filenames.py <directory>")
    else:
        directory = sys.argv[1]
        if not os.path.isdir(directory):
            print(f"The directory '{directory}' does not exist.")
        else:
            check_files(directory)
