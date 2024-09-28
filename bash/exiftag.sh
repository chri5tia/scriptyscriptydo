#!/bin/bash

# Confirm the directory being checked
echo "Checking for files in directory: $(pwd)"

# Initialize counters for tagged and untagged files
tagged_count=0
untagged_count=0

# Use `find` to recursively search for all .jpg files in the current directory and subdirectories
find . -type f -name "*.jpg" | while read -r file; do
    # Check the EXIF content creation date using mdls
    creation_date=$(mdls -raw -name kMDItemDateTimeOriginal "$file")

    # Check if the "No EXIF" tag is present
    has_no_exif_tag=$(tag -l "$file" | grep "No EXIF")

    # If the creation date is null, add the "No EXIF" tag
    if [ "$creation_date" == "(null)" ]; then
        if [ -z "$has_no_exif_tag" ]; then
            tag -a "No EXIF" "$file"
            echo "Tagged $file with 'No EXIF'"
            ((tagged_count++))
        fi
    else
        # If the creation date exists and the file has the "No EXIF" tag, remove it
        if [ -n "$has_no_exif_tag" ]; then
            tag -r "No EXIF" "$file"
            echo "Removed 'No EXIF' tag from $file"
            ((untagged_count++))
        fi
    fi
done

# Report the number of files that were tagged and untagged
echo "$tagged_count file(s) were tagged with 'No EXIF'."
echo "$untagged_count file(s) had the 'No EXIF' tag removed."
