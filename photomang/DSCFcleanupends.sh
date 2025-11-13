for f in DSCF*[0-9][0-9][0-9][0-9]*.JPG; do
  clean=$(echo "$f" | sed -E 's/^(DSCF[0-9]{4}).*\.JPG$/\1.JPG/i')
  if [[ "$f" != "$clean" ]]; then
    echo mv "$f" "$clean"
  fi
done

