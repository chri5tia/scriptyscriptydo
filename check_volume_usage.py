#!/usr/bin/env python3

import subprocess
import os
from datetime import datetime

def append_to_report(directory, script_name):
    """Appends the date, time, and script name to a report file."""
    report_path = os.path.join(directory, 'execution_report.txt')
    with open(report_path, 'a') as report:
        report.write(f"Script '{script_name}' executed on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Call this at the start of the script
directory = os.path.dirname(os.path.realpath(__file__))
script_name = os.path.basename(__file__)
append_to_report(directory, script_name)

def get_processes_using_volume(volume):
    try:
        # Use lsof to list open files on the specified volume
        result = subprocess.run(['lsof', '+D', volume], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.returncode == 0:
            if result.stdout:
                print(f"Processes using the volume '{volume}':\n")
                print(result.stdout)
            else:
                print(f"No processes are using the volume '{volume}'.")
        else:
            print(f"Error occurred: {result.stderr}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    volume = input("Enter the full path of the volume (e.g., /Volumes/YourVolume): ")
    get_processes_using_volume(volume)

