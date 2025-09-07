#!/bin/bash

# Path to the log file where we track which serial numbers have been searched
LOG_FILE="$HOME/Library/Logs/serial_searches.txt"

# Directory to search for images
SEARCH_DIR="/Volumes/T7 Touch/PHOTOS/Studio"

# Ensure the log file exists
if [ ! -f "$LOG_FILE" ]; then
    touch "$LOG_FILE"
fi

# Check if a 4-digit serial number was provided
if [ -z "$1" ]; then
    echo "Usage: $0 [4-digit serial number]"
    exit 1
fi

SERIAL="$1"

# Check if the serial number is valid (only 4 digits)
if ! [[ "$SERIAL" =~ ^[0-9]{4}$ ]]; then
    echo "Error: Please enter a valid 4-digit serial number."
    exit 1
fi

# Check if the number has already been searched
if grep -q "$SERIAL" "$LOG_FILE"; then
    echo "Note: Serial number $SERIAL has already been searched."
else
    echo "$SERIAL" >> "$LOG_FILE"
    sort -u "$LOG_FILE" -o "$LOG_FILE"
    echo "Serial number $SERIAL has been logged as searched."
fi

# Perform the search for image files in the /Volumes/T7 Touch/PHOTOS/Studio directory
echo "Searching for files with serial $SERIAL in $SEARCH_DIR..."

# Search for images using the patterns
image_results=$(find "$SEARCH_DIR" -type f \( -name "*IMG_$SERIAL*" -o -name "*DSC_$SERIAL*" -o -name "*DSCF$SERIAL*" \) 2>/dev/null)

if [[ -z "$image_results" ]]; then
    echo "No direct image files found."
    exit 0
fi

# Store file metadata
declare -A metadata_groups

# Collect metadata for each file and group by multiple attributes
while IFS= read -r file; do
    file_size=$(mdls -name kMDItemFSSize "$file" | awk -F' = ' '{print $2}' | awk '{printf "%.2f MB", $1/1048576}')
    creation_date=$(mdls -name kMDItemFSCreationDate "$file" | awk -F' = ' '{print $2}' | tr -d '"')
    modification_date=$(mdls -name kMDItemFSContentChangeDate "$file" | awk -F' = ' '{print $2}' | tr -d '"')
    content_created_date=$(mdls -name kMDItemContentCreationDate "$file" | awk -F' = ' '{print $2}' | tr -d '"')
    created_by=$(mdls -name kMDItemCreator "$file" | awk -F' = ' '{print $2}' | tr -d '"')
    pixel_width=$(mdls -name kMDItemPixelWidth "$file" | awk -F' = ' '{print $2}' | tr -d '"')
    pixel_height=$(mdls -name kMDItemPixelHeight "$file" | awk -F' = ' '{print $2}' | tr -d '"')
    dimensions="${pixel_width}x${pixel_height}"

    # Group files by each attribute
    metadata_groups["File Size: $file_size"]+="$file|"
    metadata_groups["Dimensions: $dimensions"]+="$file|"
    metadata_groups["Content Created: $content_created_date"]+="$file|"
    metadata_groups["Modification Date: $modification_date"]+="$file|"
    metadata_groups["Creator: $created_by"]+="$file|"
done <<< "$image_results"

# Print grouped results in MySQL-style \G format
count=1
for group_key in "${!metadata_groups[@]}"; do
    IFS='|' read -r -a file_list <<< "${metadata_groups[$group_key]}"
    if [[ ${#file_list[@]} -gt 1 ]]; then
        echo "*************************** $count. row ***************************"
        echo "**Group By:** $group_key"
        echo "Number of Files: ${#file_list[@]}"
        echo "Files:"

        sub_count=1
        for file_path in "${file_list[@]}"; do
            if [[ -n "$file_path" ]]; then
                # Get detailed metadata for the file
                creation_date=$(mdls -name kMDItemFSCreationDate "$file_path" | awk -F' = ' '{print $2}' | tr -d '"')
                modification_date=$(mdls -name kMDItemFSContentChangeDate "$file_path" | awk -F' = ' '{print $2}' | tr -d '"')
                content_created_date=$(mdls -name kMDItemContentCreationDate "$file_path" | awk -F' = ' '{print $2}' | tr -d '"')
                file_size=$(mdls -name kMDItemFSSize "$file_path" | awk -F' = ' '{print $2}' | awk '{printf "%.2f MB", $1/1048576}')
                created_by=$(mdls -name kMDItemCreator "$file_path" | awk -F' = ' '{print $2}' | tr -d '"')
                pixel_width=$(mdls -name kMDItemPixelWidth "$file_path" | awk -F' = ' '{print $2}' | tr -d '"')
                pixel_height=$(mdls -name kMDItemPixelHeight "$file_path" | awk -F' = ' '{print $2}' | tr -d '"')
                dimensions="${pixel_width}x${pixel_height}"
                tags=$(mdls -name kMDItemUserTags "$file_path" | awk -F' = ' '{print $2}' | tr -d '"')

                echo "  *************************** $count.$sub_count row ***************************"
                echo "  Filename: $(basename "$file_path")"
                echo "  Creation Date: $creation_date"
                echo "  Modification Date: $modification_date"
                echo "  Content Created: $content_created_date"
                echo "  Size (MB): $file_size"
                echo "  Created By: $created_by"
                echo "  Dimensions: $dimensions"
                echo "  Tags: $tags"
                echo "  Path: $file_path"
                echo ""

                sub_count=$((sub_count + 1))
            fi
        done

        echo ""
        count=$((count + 1))
    fi
done

echo
echo "Search complete."
