#!/bin/bash

echo "--- ScriptyDo Password Generator ---"

while :; do
  # Generate 8 alphanumeric characters
  PASS=$(LC_ALL=C tr -dc 'A-Za-z0-9' < /dev/urandom | head -c 8)

  # Validate: Starts with letter, contains 0-9, contains a-z, contains A-Z
  if [[ $PASS =~ ^[A-Za-z] ]] && \
     [[ $PASS =~ [0-9] ]] && \
     [[ $PASS =~ [a-z] ]] && \
     [[ $PASS =~ [A-Z] ]]; then
    break
  fi
done

echo $PASS |pbcopy
echo "Your new potential EUA password: $PASS"
echo "Copied to clipboard!"
echo "-------------------------------------"
open https://eua.cms.gov/iam/im/pri/cui7/index.jsp