#!/bin/bash
# cull_mover.sh — Move any Finder-tagged files (default tag "cull") into a local "cull" subfolder.
# Usable manually (with flags) or via cron/launchd.

set -euo pipefail
IFS=$'\n\t'

# Defaults
DEFAULT_ROOT="/Volumes/T7 Touch/PHOTOS/Studio"
TAG="cull"                  # Finder tag to match (case-insensitive)
RECURSIVE=1                 # Recursively process directories by default
DRY_RUN=0
LOGFILE=""                  # e.g., "$HOME/Library/Logs/cull_mover.log"
VERBOSE=0
EXT_FILTER=()               # e.g., ("jpg" "jpeg" "png" "heic" ...)
NOOP_PREFIX="Would move"

# Full paths (cron-safe)
FIND="/usr/bin/find"
XATTR="/usr/bin/xattr"
PLUTIL="/usr/bin/plutil"
GREP="/usr/bin/grep"
MKDIR="/bin/mkdir"
MV="/bin/mv"
DIRNAME="/usr/bin/dirname"
BASENAME="/usr/bin/basename"
DATE="/bin/date"
REALPATH="/usr/bin/realpath"

usage() {
  cat <<EOF
Usage: $(basename "$0") [options] [PATH ...]
Move files tagged with a Finder tag (default: "cull") into a "cull" subfolder
next to each file. Paths can be files or directories. With no PATH, uses:
  ${DEFAULT_ROOT}

Options:
  -t, --tag TAG          Finder tag to match (default: cull, case-insensitive)
  -n, --dry-run          Show what would happen; do not modify anything
  -r, --recursive        Recurse into subdirectories (default ON)
      --no-recursive     Only process files directly in given directories
  -e, --ext LIST         Comma-separated extensions to include (e.g. jpg,jpeg,heic,cr3)
  -l, --log FILE         Append actions to FILE (no logging by default)
  -v, --verbose          Verbose output
  -h, --help             Show this help

Examples:
  $(basename "$0")                          # Process default Studio root recursively
  $(basename "$0") -n -e jpg,jpeg,heic .    # Dry-run current dir for those extensions
  $(basename "$0") --tag Cull /path/to/folder /path/to/file.CR3
  $(basename "$0") --no-recursive /some/dir # Only files directly in /some/dir

Notes:
- Finder tags come from extended attribute: com.apple.metadata:_kMDItemUserTags
- Files already inside a 'cull' folder are skipped.
- Name collisions are handled by adding _1, _2, ... before the extension.
EOF
}

log() {
  local msg="$1"
  if [[ -n "$LOGFILE" ]]; then
    "$DATE" +"%Y-%m-%d %H:%M:%S" >> "$LOGFILE"
    echo " [$(basename "$0")] $msg" >> "$LOGFILE"
  fi
  if (( VERBOSE )); then
    echo "$msg"
  fi
}

# Return 0 if file has Finder tag TAG (case-insensitive)
has_tag() {
  local file="$1"
  local tag_pat
  # Quote for grep regex; ensure leading quote in plutil -p output is matched loosely:
  tag_pat=$(printf '%s' "$TAG" | /usr/bin/sed 's/[^^$.*+?()[\]{}|\\]/[&]/g')

  # Read xattr (binary plist) -> plutil -p (structured) -> grep for tag
  if "$XATTR" -p 'com.apple.metadata:_kMDItemUserTags' "$file" 2>/dev/null \
      | "$PLUTIL" -p - 2>/dev/null \
      | "$GREP" -qi "\"${tag_pat}"; then
    return 0
  fi
  return 1
}

# Should we consider file by extension?
pass_ext_filter() {
  local file="$1"
  if ((${#EXT_FILTER[@]}==0)); then
    return 0
  fi
  local base ext
  base="$("$BASENAME" -- "$file")"
  ext="${base##*.}"
  if [[ "$base" == "$ext" ]]; then
    # no extension
    return 1
  fi
  ext="${ext,,}" # to lower
  for wanted in "${EXT_FILTER[@]}"; do
    if [[ "$ext" == "$wanted" ]]; then
      return 0
    fi
  done
  return 1
}

move_one() {
  local file="$1"
  local parent target base name ext dest i

  parent="$("$DIRNAME" -- "$file")"
  target="$parent/cull"

  if [[ "$parent" == *"/cull" ]] || [[ "$parent" == */cull/* ]]; then
    log "Skip (already in cull): $file"
    return 0
  fi

  # Ensure target exists
  if [[ ! -d "$target" ]]; then
    if (( DRY_RUN )); then
      log "$NOOP_PREFIX: create dir -> $target"
    else
      if "$MKDIR" -p -- "$target"; then
        log "Created: $target"
      else
        log "ERROR: Could not create $target"
        return 1
      fi
    fi
  fi

  base="$("$BASENAME" -- "$file")"
  name="${base%.*}"
  ext="${base##*.}"
  if [[ "$name" == "$ext" ]]; then ext=""; else ext=".$ext"; fi
  dest="$target/$base"

  if [[ -e "$dest" ]]; then
    i=1
    while [[ -e "$target/${name}_$i$ext" ]]; do
      ((i++))
    done
    dest="$target/${name}_$i$ext"
  fi

  if (( DRY_RUN )); then
    log "$NOOP_PREFIX: $file -> $dest"
  else
    if "$MV" -n -- "$file" "$dest"; then
      log "Moved: $file -> $dest"
    else
      log "ERROR: Failed to move: $file"
      return 1
    fi
  fi
}

process_file_list() {
  while IFS= read -r -d '' f; do
    # Extension filter first for speed
    if ! pass_ext_filter "$f"; then
      (( VERBOSE )) && echo "Skip (ext): $f"
      continue
    fi
    if has_tag "$f"; then
      move_one "$f"
    else
      (( VERBOSE )) && echo "Skip (no tag): $f"
    fi
  done
}

collect_files_from_dir() {
  local dir="$1"
  if (( RECURSIVE )); then
    "$FIND" "$dir" -type f ! -path "*/cull/*" -print0
  else
    "$FIND" "$dir" -maxdepth 1 -type f ! -path "*/cull/*" -print0
  fi
}

main() {
  local paths=()

  # Parse args
  while (($#)); do
    case "$1" in
      -t|--tag) TAG="$2"; shift 2 ;;
      -n|--dry-run) DRY_RUN=1; shift ;;
      -r|--recursive) RECURSIVE=1; shift ;;
      --no-recursive) RECURSIVE=0; shift ;;
      -e|--ext)
        IFS=',' read -r -a EXT_FILTER <<< "$2"
        # normalize to lower
        for i in "${!EXT_FILTER[@]}"; do EXT_FILTER[$i]="${EXT_FILTER[$i],,}"; done
        shift 2 ;;
      -l|--log) LOGFILE="$2"; shift 2 ;;
      -v|--verbose) VERBOSE=$((VERBOSE+1)); shift ;;
      -h|--help) usage; exit 0 ;;
      --) shift; break ;;
      -*)
        echo "Unknown option: $1" >&2
        usage; exit 2 ;;
      *)
        paths+=("$1"); shift ;;
    esac
  done

  # Default path if none supplied
  if ((${#paths[@]}==0)); then
    paths=("$DEFAULT_ROOT")
  fi

  # Validate paths
  local ok_any=0
  for p in "${paths[@]}"; do
    if [[ -e "$p" ]]; then
      ok_any=1
    else
      echo "Warning: path not found: $p" >&2
    fi
  done
  if (( ! ok_any )); then
    echo "No valid paths to process. Exiting." >&2
    exit 1
  fi

  (( VERBOSE )) && echo "Tag: '$TAG' | Recursive: $RECURSIVE | Dry-run: $DRY_RUN"
  if ((${#EXT_FILTER[@]})); then
    (( VERBOSE )) && echo "Extensions: ${EXT_FILTER[*]}"
  fi
  if [[ -n "$LOGFILE" ]]; then
    log "---- Run start (tag=$TAG, recursive=$RECURSIVE, dry=$DRY_RUN) ----"
  fi

  # Process paths
  for p in "${paths[@]}"; do
    if [[ -d "$p" ]]; then
      collect_files_from_dir "$p" | process_file_list
    elif [[ -f "$p" ]]; then
      printf '%s\0' "$p" | process_file_list
    else
      (( VERBOSE )) && echo "Skip (not file/dir): $p"
    fi
  done
}

main "$@"
