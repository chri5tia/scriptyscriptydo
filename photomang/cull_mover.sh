#!/bin/bash
# cull_mover.sh — Move any file tagged "cull" into a local "cull" subfolder.
# Works without Spotlight. Reads Finder tags from extended attributes.
# Safe to run repeatedly (idempotent). Skips anything already inside a cull folder.

set -euo pipefail
IFS=$'\n\t'

ROOT="/Volumes/T7 Touch/PHOTOS/Studio"
LOGFILE="$HOME/Library/Logs/cull_mover.log"

# Full paths (cron-safe)
FIND="/usr/bin/find"
XATTR="/usr/bin/xattr"
PLUTIL="/usr/bin/plutil"
MKDIR="/bin/mkdir"
MV="/bin/mv"
DIRNAME="/usr/bin/dirname"
DATE="/bin/date"
BASENAME="/usr/bin/basename"

log() {
  "$DATE" +"%Y-%m-%d %H:%M:%S" >> "$LOGFILE"
  echo " [$("$BASENAME" "$0")] $*" >> "$LOGFILE"
}

# Return 0 (true) if the file has a Finder tag "cull" (case-insensitive)
has_cull_tag() {
  local file="$1"
  # Read binary plist from com.apple.metadata:_kMDItemUserTags and parse it
  # If no tags/xattr, xattr -p exits nonzero; suppress errors.
  if "$XATTR" -p 'com.apple.metadata:_kMDItemUserTags' "$file" 2>/dev/null \
      | "$PLUTIL" -p - 2>/dev/null \
      | /usr/bin/grep -qi '"cull'; then
    return 0
  fi
  return 1
}

main() {
  if [[ ! -d "$ROOT" ]]; then
    log "Root not found or volume not mounted: $ROOT — exiting."
    exit 0
  fi

  # Walk all files under ROOT, skip anything already inside a /cull/ directory
  # and skip the cull directories themselves.
  # Using -print0 to handle spaces/newlines in filenames.
  "$FIND" "$ROOT" \
    -type f ! -path "*/cull/*" -print0 \
  | while IFS= read -r -d '' file; do
      if has_cull_tag "$file"; then
        parent="$("$DIRNAME" "$file")"
        target="$parent/cull"

        # Create target folder if missing
        if [[ ! -d "$target" ]]; then
          if "$MKDIR" -p "$target"; then
            log "Created: $target"
          else
            log "ERROR: Could not create $target"
            continue
          fi
        fi

        # Move file (no overwrite). If a same-named file exists, append a counter.
        base="$(basename "$file")"
        dest="$target/$base"
        if [[ -e "$dest" ]]; then
          # Add a numeric suffix before extension
          name="${base%.*}"
          ext="${base##*.}"
          if [[ "$name" == "$ext" ]]; then ext=""; else ext=".$ext"; fi
          i=1
          while [[ -e "$target/${name}_$i$ext" ]]; do
            ((i++))
          done
          dest="$target/${name}_$i$ext"
        fi

        if "$MV" -n "$file" "$dest"; then
          log "Moved: $file  ->  $dest"
        else
          log "ERROR: Failed to move: $file"
        fi
      fi
    done
}

main

