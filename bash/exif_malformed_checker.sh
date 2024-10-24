#!/bin/bash

# Confirm the directory being checked
echo "Checking for files in directory: $(pwd)"

# Initialize counters for various tags
no_exif_count=0
picasa_count=0
gimp_count=0
windows_live_count=0
chrome_count=0
other_edited_count=0
malformed_exif_count=0

# Use `find` to recursively search for all .jpg files in the current directory and subdirectories
find . -type f -name "*.jpg" | while read -r file; do

    # Check if EXIF data is present using exiftool
    exif_data=$(exiftool "$file" | grep -i "exif")
    
    # Check the EXIF Software tag for possible editors
    editor=$(exiftool -Software "$file" | awk -F': ' '{print $2}')

    # Check if the "No EXIF" tag is present
    has_no_exif_tag=$(tag -l "$file" | grep "No EXIF")

    # A. Check for presence of EXIF data
    if [ -z "$exif_data" ]; then
        if [ -z "$has_no_exif_tag" ]; then
            tag -a "No EXIF" "$file"
            echo "Tagged $file with 'No EXIF'"
            ((no_exif_count++))
        fi
    else
        # Remove "No EXIF" tag if EXIF data is present
        if [ -n "$has_no_exif_tag" ]; then
            tag -r "No EXIF" "$file"
            echo "Removed 'No EXIF' tag from $file"
        fi
    fi

    # B. Check for Picasa, GIMP, Windows Live, and Chrome edits
    if [[ "$editor" == *"Picasa"* ]]; then
        tag -a "Picasa" "$file"
        echo "Tagged $file with 'Picasa'"
        ((picasa_count++))
    fi

    if [[ "$editor" == *"GIMP"* ]]; then
        tag -a "GIMP" "$file"
        echo "Tagged $file with 'GIMP'"
        ((gimp_count++))
    fi

    if [[ "$editor" == *"Windows Live"* ]]; then
        tag -a "Mock up Windows Live" "$file"
        echo "Tagged $file with 'Mock up Windows Live'"
        ((windows_live_count++))
    fi

    if [[ "$editor" == *"Chrome"* ]]; then
        tag -a "GP Mockup" "$file"
        echo "Tagged $file with 'GP Mockup'"
        ((chrome_count++))
    fi

    # F. Other editors check
    if [[ -n "$editor" && "$editor" != *"Picasa"* && "$editor" != *"GIMP"* && "$editor" != *"Windows Live"* && "$editor" != *"Chrome"* ]]; then
        tag -a "Edited by other software" "$file"
        echo "Tagged $file with 'Edited by other software'"
        ((other_edited_count++))
    fi

    # Check for malformed EXIF data (catch warnings or errors from exiftool)
    exiftool_output=$(exiftool "$file" 2>&1)
    if echo "$exiftool_output" | grep -q "Warning: Invalid size"; then
        tag -a "Exif Malformed" "$file"
        echo "Tagged $file with 'Exif Malformed'"
        ((malformed_exif_count++))
    fi

done

# Report the number of files that were tagged
echo "$no_exif_count file(s) were tagged with 'No EXIF'."
echo "$picasa_count file(s) were tagged with 'Picasa'."
echo "$gimp_count file(s) were tagged with 'GIMP'."
echo "$windows_live_count file(s) were tagged with 'Mock up Windows Live'."
echo "$chrome_count file(s) were tagged with 'GP Mockup'."
echo "$other_edited_count file(s) were tagged with 'Edited by other software'."
echo "$malformed_exif_count file(s) were tagged with 'Exif Malformed'."

