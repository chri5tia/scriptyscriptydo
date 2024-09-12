for file in *.jpg; do
    creation_date=$(mdls -raw -name kMDItemDateTimeOriginal "$file")
    if [ "$creation_date" == "(null)" ]; then
        tag -a "No EXIF" "$file"
        echo "Tagged $file with 'No EXIF'"
    fi
done

