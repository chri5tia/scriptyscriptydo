#!/usr/bin/env bash
# suyncgoodphotos.sh
# Copy from SOURCE to DEST, pruning dirs named "Notes" or "Archive" anywhere.

set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  copy_skip_notes_archive.sh "SOURCE_DIR" "DEST_DIR" [--dry-run]

Notes:
- SOURCE_DIR must be on /Volumes/T7 Touch (safety check).
- Copies the *contents* of SOURCE_DIR into DEST_DIR (src/ -> dest/).
- Skips any directory named exactly "Notes" or "Archive" at any depth.
- Use --dry-run to preview.
EOF
}

[[ $# -lt 2 ]] && { usage; exit 1; }

SRC=$1; DST=$2; DRY=${3:-}
# Resolve absolute paths
SRC=$(cd "$SRC" 2>/dev/null && pwd) || { echo "Source not found: $1" >&2; exit 1; }
mkdir -p "$DST"
DST=$(cd "$DST" 2>/dev/null && pwd)

# Safety: enforce source on T7 Touch
case "$SRC" in
  /Volumes/T7\ Touch/*|/Volumes/T7\ Touch) ;;
  *) echo "Refusing: SOURCE_DIR is not on /Volumes/T7 Touch -> $SRC" >&2; exit 1 ;;
esac

# Prefer Homebrew rsync (better macOS metadata), else fall back to /usr/bin/rsync
if command -v /opt/homebrew/bin/rsync >/dev/null 2>&1; then
  RSYNC=/opt/homebrew/bin/rsync
  # -aHAX : archive + hardlinks + ACLs + xattrs
  # --crtimes : preserve creation time (birthtime)
  # --fileflags/--protect-decmpfs : preserve macOS flags & compression
  META_FLAGS=(-aHAX --crtimes --fileflags --xattrs --protect-decmpfs)
else
  RSYNC=/usr/bin/rsync
  # macOS built-in rsync (2.6.9) – preserves perms/times/xattrs/resource forks
  META_FLAGS=(-aE)
fi

EXCLUDES=(
  --exclude='*/Notes/**'
  --exclude='*/Archive/**'
)

COMMON_FLAGS=(
  --protect-args
  --info=stats2,progress2
)

[[ "$DRY" == "--dry-run" ]] && COMMON_FLAGS+=(--dry-run) && echo ">>> DRY RUN"

# Trailing slash on SRC copies *contents* into DEST
"$RSYNC" "${META_FLAGS[@]}" "${COMMON_FLAGS[@]}" "${EXCLUDES[@]}" "$SRC/" "$DST/"

echo "Done."
