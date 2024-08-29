import os
import sys
import shutil
from datetime import datetime

def get_files_with_sizes(directory):
    files_with_sizes = {}
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            size = os.path.getsize(file_path)
            files_with_sizes[(file, size)] = file_path
    return files_with_sizes

def compare_directories(current_dir, compare_dir):
    current_files = get_files_with_sizes(current_dir)
    compare_files = get_files_with_sizes(compare_dir)

    missing_files = []

    for file_info, file_path in current_files.items():
        if file_info not in compare_files:
            missing_files.append(file_path)

    return missing_files

def generate_report(missing_files, rescue_dir, report_only):
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_name = f"RescuedFiles_{current_time}.txt"
    report_path = os.path.join(rescue_dir, report_name)

    with open(report_path, "w") as report_file:
        for file in missing_files:
            if not report_only:
                dest_file_path = os.path.join(rescue_dir, os.path.basename(file))
                shutil.copy2(file, dest_file_path)
                report_file.write(f"Copied: {file} -> {dest_file_path}\n")
            else:
                report_file.write(f"Missing: {file}\n")

    print(f"Report saved to '{report_path}'")

if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python3 script_name.py /path/to/compare_directory [--report-only]")
        sys.exit(1)

    current_dir = os.getcwd()
    compare_dir = sys.argv[1]
    report_only = len(sys.argv) == 3 and sys.argv[2] == "--report-only"

    rescue_dir = os.path.join(current_dir, "Rescued files")

    if not os.path.exists(rescue_dir):
        os.makedirs(rescue_dir)

    missing_files = compare_directories(current_dir, compare_dir)

    if missing_files:
        generate_report(missing_files, rescue_dir, report_only)
    else:
        print("All files match by name and size. No files to rescue.")
