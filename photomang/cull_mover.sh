#!/bin/bash
# cull_mover.sh — Find files tagged "cull" and move them (and their RAW/JPEG/-v variants)
# into a sibling "cull" folder. Usable manually or from launchd/cron.
# macOS only; does not require Spotlight.

set -euo pipefail
IFS=$'\n\t'

# Defaults
DEFAULT_ROOT="/Volumes/T7 Touch/PHOTOS/Studio"
TAG="cull"          # case-insensitive
RECURSIVE=1
DRY_RUN=0
LOGFILE=""
VERBOSE=0
SAY_START=1
SAY_DONE=1
NOOP_PREFIX="Would move"

# Full paths (cron/launchd-safe)
FIND="/usr/bin/find"
XATTR="/usr/bin/xattr"
PLUTIL="/usr/bin/plutil"
GREP="/usr/bin/grep"
MKDIR="/bin/mkdir"
MV="/bin/mv"
DIRNAME="/usr/bin/dirname"
BASENAME="/usr/bin/basename"
DATE="/bin/date"
SAY="/usr/bin/say"

usage() {
  cat <<EOF
Usage: $(basename "$0") [options] [PATH ...]
With no PATH, defaults to:
  ${DEFAULT_ROOT}

Options:
  -n, --dry-run        Show actions only; don't modify files
  -r, --recursive      Recurse into subdirectories (default ON)
      --no-recursive   Process files only in given directories (no descent)
  -l, --log FILE       Append actions to FILE
  -v, --verbose        Verbose output (use twice for more)
  -h, --help           Show this help

Behavior:
- Detects Finder tag "cull" (case-insensitive) via xattr 'com.apple.metadata:_kMDItemUserTags'.
- Moves each tagged file to a sibling directory named 'cull'.
- Also moves RAW/JPEG "pairs" and edited variants suffixed with '-v' that share the same stem.
  Example: IMG_1234.CR3 tagged -> moves IMG_1234.CR3, IMG_1234.JPG, IMG_1234-v.JPG, etc.
- Skips anything already inside a cull folder.
- Adds suffixes (_1, _2, ...) on name collisions as a safeguard.

Examples:
  $(basename "$0")                   # process ${DEFAULT_ROOT} recursively
  $(basename "$0") -n -v .           # dry-run current folder (recursive)
  $(basename "$0") --no-recursive "/path/to/a/folder"
  $(basename "$0") "/path/to/file.HEIC" "/path/to/another/dir"
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

has_cull_tag() {
  local file="$1"
  # Use mdls directly (case-insensitive match for the word "cull")
  if /usr/bin/mdls -name kMDItemUserTags "$file" 2>/dev/null \
      | /usr/bin/grep -qi '\<cull\>'; then
    return 0
  fi
  return 1
}

# Build the move set for a tagged file:
# - The file itself
# - Its "stem" siblings: same base (without extension) with any extension
# - If base is NAME-v, also include NAME.* and NAME-v.*
# - If base is NAME (no -v), include NAME.* and NAME-v.*
collect_variants() {
  local file="$1"
  local parent base name ext stem_plain
  parent="$("$DIRNAME" -- "$file")"
  base="$("$BASENAME" -- "$file")"
  name="${base%.*}"
  ext="${base##*.}"
  [[ "$name" == "$ext" ]] && ext="" || ext=".$ext"

  if [[ "$name" == *"-v" ]]; then
    stem_plain="${name%-v}"
  else
    stem_plain="$name"
  fi

  # Match: stem_plain.*  and  stem_plain-v.*
  "$FIND" "$parent" -maxdepth 1 -type f ! -path "*/cull/*" \
    \( -name "$stem_plain.*" -o -name "$stem_plain-v.*" \) -print0
}


safe_move() {
  local src="$1"
  local targetdir="$2"
  local base name ext dest i

  [[ -d "$targetdir" ]] || {
    if (( DRY_RUN )); then
      log "$NOOP_PREFIX: create dir -> $targetdir"
    else
      if "$MKDIR" -p -- "$targetdir"; then
        log "Created: $targetdir"
      else
        log "ERROR: Could not create $targetdir"
        return 1
      fi
    fi
  }

  base="$("$BASENAME" -- "$src")"
  name="${base%.*}"
  ext="${base##*.}"
  if [[ "$name" == "$ext" ]]; then ext=""; else ext=".$ext"; fi
  dest="$targetdir/$base"

  if [[ -e "$dest" ]]; then
    i=1
    while [[ -e "$targetdir/${name}_$i$ext" ]]; do
      ((i++))
    done
    dest="$targetdir/${name}_$i$ext"
  fi

  if (( DRY_RUN )); then
    log "$NOOP_PREFIX: $src -> $dest"
  else
    if "$MV" -n -- "$src" "$dest"; then
      log "Moved: $src -> $dest"
    else
      log "ERROR: Failed to move: $src"
      return 1
    fi
  fi
}

process_tagged_file() {
  local file="$1"
  local parent target
  parent="$("$DIRNAME" -- "$file")"
  target="$parent/cull"

  # Skip if already inside cull
  if [[ "$parent" == *"/cull" ]] || [[ "$parent" == */cull/* ]]; then
    (( VERBOSE > 1 )) && echo "Skip (already in cull): $file"
    return 0
  fi

  # Build the variant list (includes the file itself) without assoc arrays
  local candidates=()
  # Collect variants: stem.* and stem-v.* in same dir
  while IFS= read -r -d '' v; do
    [[ -f "$v" ]] || continue
    [[ "$v" == */cull/* ]] && continue
    candidates+=("$v")
  done < <(collect_variants "$file")

  # If none found (unlikely), at least move the file itself
  if ((${#candidates[@]}==0)); then
    candidates+=("$file")
  fi

  # Deduplicate with a simple O(n^2) check (small lists; fine here)
  local move_list=()
  local c
  for c in "${candidates[@]}"; do
    local already=0
    local m
    for m in "${move_list[@]}"; do
      if [[ "$m" == "$c" ]]; then already=1; break; fi
    done
    (( already )) || move_list+=("$c")
  done

  # Ensure target exists and move each
  for c in "${move_list[@]}"; do
    safe_move "$c" "$target"
  done
}


process_file_list() {
  while IFS= read -r -d '' f; do
    if has_cull_tag "$f"; then
      process_tagged_file "$f"
    else
      (( VERBOSE > 1 )) && echo "Skip (no tag): $f"
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
      -n|--dry-run) DRY_RUN=1; shift ;;
      -r|--recursive) RECURSIVE=1; shift ;;
      --no-recursive) RECURSIVE=0; shift ;;
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

  # Default path
  if ((${#paths[@]}==0)); then
    paths=("$DEFAULT_ROOT")
  fi

  # Speak start
  if (( SAY_START )); then
    "$SAY" "Starting cull move task" >/dev/null 2>&1 || true
  fi

  # Log banner
  if [[ -n "$LOGFILE" ]]; then
    log "---- Run start (recursive=$RECURSIVE dry=$DRY_RUN) ----"
  fi
  (( VERBOSE )) && echo "Recursive: $RECURSIVE | Dry-run: $DRY_RUN"

  local any_valid=0
  for p in "${paths[@]}"; do
    if [[ -d "$p" ]]; then
      any_valid=1
      collect_files_from_dir "$p" | process_file_list
    elif [[ -f "$p" ]]; then
      any_valid=1
      printf '%s\0' "$p" | process_file_list
    else
      echo "Warning: path not found: $p" >&2
    fi
  done

  if (( ! any_valid )); then
    echo "No valid paths to process." >&2
    exit 1
  fi

  # Speak done
  if (( SAY_DONE )); then
    "$SAY" "Culled photos have been moved" >/dev/null 2>&1 || true
  fi

  if [[ -n "$LOGFILE" ]]; then
    log "---- Run end ----"
  fi
}

main "$@"
