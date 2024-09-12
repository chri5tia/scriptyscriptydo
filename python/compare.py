import os
import sys

def get_files_in_directory(directory):
    """Recursively gather all files in the given directory and its subdirectories."""
    files = {}
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(root, filename)
            filesize = os.path.getsize(filepath)
            if filename in files:
                files[filename].append((filepath, filesize))
            else:
                files[filename] = [(filepath, filesize)]
    return files

def compare_directories(dir1_files, dir2_files):
    """Compare files between two directories and categorize them."""
    same_name_and_size_different_location = []
    same_name_and_size_one_location = []

    all_files = set(dir1_files.keys()).union(set(dir2_files.keys()))

    for filename in all_files:
        if filename in dir1_files and filename in dir2_files:
            dir1_size = set(size for _, size in dir1_files[filename])
            dir2_size = set(size for _, size in dir2_files[filename])

            if dir1_size == dir2_size:
                dir1_paths = set(path for path, _ in dir1_files[filename])
                dir2_paths = set(path for path, _ in dir2_files[filename])

                if dir1_paths != dir2_paths:
                    same_name_and_size_different_location.append((filename, dir1_paths, dir2_paths))
            else:
                same_name_and_size_one_location.append((filename, dir1_files[filename], dir2_files[filename]))
        else:
            if filename in dir1_files:
                same_name_and_size_one_location.append((filename, dir1_files[filename], []))
            if filename in dir2_files:
                same_name_and_size_one_location.append((filename, [], dir2_files[filename]))

    return same_name_and_size_different_location, same_name_and_size_one_location

def write_report(same_location, one_location):
    """Write the report to a text file on the desktop."""
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    report_path = os.path.join(desktop_path, "report.txt")

    with open(report_path, "w") as report:
        report.write("Files with the same name and size but in different locations:\n\n")
        for filename, dir1_paths, dir2_paths in same_location:
            report.write(f"{filename}:\n")
            report.write(f"  In Directory 1:\n")
            for path in dir1_paths:
                report.write(f"    {path}\n")
            report.write(f"  In Directory 2:\n")
            for path in dir2_paths:
                report.write(f"    {path}\n")
            report.write("\n")

        report.write("Files with the same name and size that are only in one directory:\n\n")
        for filename, dir1_files, dir2_files in one_location:
            report.write(f"{filename}:\n")
            if dir1_files:
                report.write(f"  Only in Directory 1:\n")
                for path, size in dir1_files:
                    report.write(f"    {path} (Size: {size} bytes)\n")
            if dir2_files:
                report.write(f"  Only in Directory 2:\n")
                for path, size in dir2_files:
                    report.write(f"    {path} (Size: {size} bytes)\n")
            report.write("\n")

    print(f"Report saved as '{report_path}'.")

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 compare.py path/to/first/directory path/to/second/directory")
        sys.exit(1)

    dir1 = sys.argv[1]
    dir2 = sys.argv[2]

    if not os.path.isdir(dir1) or not os.path.isdir(dir2):
        print("One or both specified paths are not valid directories.")
        sys.exit(1)

    # Get files in both directories
    dir1_files = get_files_in_directory(dir1)
    dir2_files = get_files_in_directory(dir2)

    # Compare directories
    same_location, one_location = compare_directories(dir1_files, dir2_files)

    # Write the report
    write_report(same_location, one_location)

    print("Comparison complete. Report saved on your desktop as 'report.txt'.")

if __name__ == "__main__":
    main()
