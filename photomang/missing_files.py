import os
import re

def find_missing_files(directory):
    # List all files in the directory
    files = os.listdir(directory)

    # Extract the file numbers and sort them, ignoring the prefix
    file_numbers = sorted(int(re.search(r'_(\d+)', f).group(1)) for f in files if re.search(r'_(\d+)', f))

    if not file_numbers:
        return "No numbered files found."

    # Find the minimum and maximum numbers in the series
    min_num, max_num = file_numbers[0], file_numbers[-1]

    # Generate the complete series
    missing_ranges = []
    last_num = min_num - 1

    for num in range(min_num, max_num + 1):
        if num not in file_numbers:
            if not missing_ranges or missing_ranges[-1][-1] != num - 1:
                missing_ranges.append([num, num])
            else:
                missing_ranges[-1][-1] = num

    # Format the missing files/ranges to be printed on separate lines
    formatted_missing = []
    for start, end in missing_ranges:
        if end - start >= 4:
            formatted_missing.append(f"{str(start).zfill(4)} through {str(end).zfill(4)}")
        else:
            formatted_missing.extend([f"{str(n).zfill(4)}" for n in range(start, end + 1)])

    return formatted_missing

def save_to_file(filename, missing_files):
    with open(filename, 'w') as file:
        file.write('\n'.join(missing_files))

# Example usage
directory = '.'  # Current directory or provide the path to the directory
missing_files = find_missing_files(directory)

if len(missing_files) <= 10:
    print("Missing files:\n", '\n'.join(missing_files))
else:
    output_file = 'missing_files_report.txt'
    save_to_file(output_file, missing_files)
    print(f"Too many missing files to list. Results have been saved to {output_file}.")
