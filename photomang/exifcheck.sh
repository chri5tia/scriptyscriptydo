for file in *.jpg; do
    creation_date=$(mdls -raw -name kMDItemDateTimeOriginal "$file")
    if [ "$creation_date" == "(null)" ]; then
        echo "$file"
    fi
done

