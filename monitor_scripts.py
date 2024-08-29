import os
import sys
import time
from datetime import datetime

def append_to_report(directory, script_name):
    """Appends the date, time, and script name to a report file."""
    report_path = os.path.join(directory, 'execution_report.txt')
    with open(report_path, 'a') as report:
        report.write(f"Script '{script_name}' executed on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

def monitor_directory(directory):
    """Monitors a directory for Python script execution."""
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py") and file != os.path.basename(__file__):
                # If the script is being run, append to the report
                append_to_report(directory, file)

if __name__ == "__main__":
    if len(sys.argv) != 2:

