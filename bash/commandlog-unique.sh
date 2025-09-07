#!/bin/sh
# Deduplicate by command only (keep first timestamp + first path).
# Usage:
#   sh commandlog-unique.sh [INPUT_FILE [OUTPUT_FILE]]
# Options:
#   -n   Normalize whitespace in the COMMAND KEY (collapse runs of space, trim).
#   -e   Exact-line mode (ignore date/path logic; dedupe whole line).
# Notes:
#   • Default mode builds the key from fields $4..end (the command).
#   • Lines with fewer than 4 fields are passed through unchanged.
#   • Output is written atomically, then moved into place.

set -eu

usage() {
  cat <<'EOF'
Deduplicate a command log.

Default: dedupe by COMMAND ONLY (fields 4..end), preserving the first
timestamp + path that introduced that command.

Usage:
  sh commandlog-unique.sh [INPUT_FILE [OUTPUT_FILE]]

Options:
  -n  Normalize whitespace in the command key (collapse runs; trim ends).
  -e  Exact-line mode (dedupe whole line, byte-for-byte).
  -h  Help

Defaults:
  INPUT_FILE  = .command_log
  OUTPUT_FILE = <INPUT_FILE>_unique
EOF
}

normalize=0
exact=0

while getopts "neh" opt; do
  case "$opt" in
    n) normalize=1 ;;
    e) exact=1 ;;
    h) usage; exit 0 ;;
    *) usage; exit 2 ;;
  esac
done
shift $((OPTIND-1))

infile="${1:-.command_log}"

if [ $# -ge 2 ]; then
  outfile="$2"
else
  case "$infile" in
    */*) dir=${infile%/*}; base=${infile##*/}; outfile="${dir}/${base}_unique" ;;
    *)   outfile="${infile}_unique" ;;
  esac
fi

[ -f "$infile" ] || { echo "Error: input file not found: $infile" >&2; exit 1; }
[ "$outfile" = "$infile" ] && { echo "Error: output must differ from input." >&2; exit 1; }

outdir=$(dirname -- "$outfile")
base=$(basename -- "$outfile")
tmp=$(mktemp "${outdir}/${base}.XXXXXX")

if [ "$exact" -eq 1 ]; then
  # Exact whole-line uniqueness (previous behavior)
  if [ "$normalize" -eq 1 ]; then
    awk '
      {
        key=$0
        gsub(/[[:space:]]+/, " ", key); sub(/^ /,"",key); sub(/ $/,"",key)
        if (seen[key]++==0) print $0
      }
    ' "$infile" > "$tmp"
  else
    awk 'seen[$0]++==0' "$infile" > "$tmp"
  fi
else
  # Dedupe by command only (fields 4..end). Keep first full line.
  if [ "$normalize" -eq 1 ]; then
    awk '
      NF<4 { print; next }  # pass through short/odd lines
      {
        cmd = substr($0, index($0, $4))
        key = cmd
        gsub(/[[:space:]]+/, " ", key); sub(/^ /,"",key); sub(/ $/,"",key)
        if (seen[key]++==0) print $0
      }
    ' "$infile" > "$tmp"
  else
    awk '
      NF<4 { print; next }
      {
        cmd = substr($0, index($0, $4))
        if (seen[cmd]++==0) print $0
      }
    ' "$infile" > "$tmp"
  fi
fi

mv -f -- "$tmp" "$outfile"

in_lines=$(wc -l < "$infile" | tr -d ' ')
out_lines=$(wc -l < "$outfile" | tr -d ' ')
echo "Wrote ${out_lines} unique commands (from ${in_lines}) → ${outfile}"
