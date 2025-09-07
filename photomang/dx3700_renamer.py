#!/usr/bin/env python3
"""
dx3700_renamer.py

- Filters images where EXIF Model == "KODAK EASYSHARE DX3700"
- Renames to DCP_0000.JPG using number derived from current filename
- Confirms/asks for folder unless --yes
- Optional recursion and dry-run
- Duplicate naming: "DCP_0001 dup.JPG", then "DCP_0001 dup(1).JPG"...
- Preserves original atime/mtime so Finder "Modified" stays the same

Usage:
  python3 dx3700_renamer.py [PATH] [--yes] [--recursive] [--dry-run]

# ------------------------------------------------------------
# Setup instructions (for new terminal session):
#   cd ~/Sites/scripts/python/photomang
#   source .venv/bin/activate
#   python -m pip install --upgrade pip
#   python -m pip install Pillow
#
# Run script:
#   ./dx3700_renamer.py "/path/to/folder" -y
# ------------------------------------------------------------

"""
import argparse
import os
import re
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow is required. Install with: pip install Pillow", file=sys.stderr)
    sys.exit(1)

KODAK_MODEL = "KODAK EASYSHARE DX3700 Digital Camera"
EXIF_MODEL_TAG = 272  # 0x0110
IMG_EXTS = {".jpg", ".jpeg"}  # case-insensitive

def get_exif_model(path: Path) -> str | None:
    try:
        with Image.open(path) as im:
            exif = getattr(im, "getexif", None)
            if exif is None:
                return None
            data = exif()
            if not data:
                return None
            model = data.get(EXIF_MODEL_TAG)
            return str(model).strip() if model is not None else None
    except Exception:
        return None

def derive_dcp_number_from_filename(name: str) -> str | None:
    """
    Rule: find first integer in filename.
    If it has >=3 digits and first digit in {0,1,2,3}, drop that first digit (old rating).
    Otherwise use the whole integer. Left pad to 4.
    """
    m = re.search(r"(\d+)", name)
    if not m:
        return None
    num_str = m.group(1)
    if len(num_str) >= 3 and num_str[0] in {"0", "1", "2", "3"}:
        core = num_str[1:] or "0"
    else:
        core = num_str
    try:
        n = int(core)
    except ValueError:
        return None
    return f"{n:04d}"

def safe_target_with_dup(base_target: Path) -> Path:
    """
    If base_target exists, create "stem dup.ext"; if that exists, "stem dup(1).ext", etc.
    """
    if not base_target.exists():
        return base_target
    parent, stem, suffix = base_target.parent, base_target.stem, base_target.suffix
    candidate = parent / f"{stem} dup{suffix}"
    if not candidate.exists():
        return candidate
    i = 1
    while True:
        candidate = parent / f"{stem} dup({i}){suffix}"
        if not candidate.exists():
            return candidate
        i += 1

def rename_preserving_times(src: Path, dst: Path) -> None:
    """
    Rename src -> dst and restore original atime/mtime on the destination.
    """
    st = src.stat()
    at_ns = getattr(st, "st_atime_ns", int(st.st_atime * 1e9))
    mt_ns = getattr(st, "st_mtime_ns", int(st.st_mtime * 1e9))
    src.rename(dst)
    # Restore both access and modified times on the new path
    os.utime(dst, ns=(at_ns, mt_ns))

def process_file(path: Path, dry_run: bool) -> tuple[bool, str]:
    """
    Returns (worked?, message)
    - If EXIF Model matches and the desired target name already equals the current filename,
      do nothing (but report ok).
    """
    model = get_exif_model(path)
    if model != KODAK_MODEL:
        return (False, f"[skip] {path.name}: EXIF Model is '{model}'")

    dcp_digits = derive_dcp_number_from_filename(path.stem)
    if dcp_digits is None:
        return (False, f"[skip] {path.name}: no number in filename")

    base_target = path.with_name(f"DCP_{dcp_digits}.JPG")

    # Already correctly named?
    if path.name == base_target.name:
        return (True, f"[ok] {path.name} (already named)")

    target = safe_target_with_dup(base_target)

    if dry_run:
        return (True, f"[dry-run] {path.name} -> {target.name}")

    try:
        rename_preserving_times(path, target)
        return (True, f"[renamed] {path.name} -> {target.name}")
    except Exception as e:
        return (False, f"[error] Failed to rename {path.name}: {e}")

def iter_paths(folder: Path, recursive: bool):
    if recursive:
        yield from (p for p in folder.rglob("*") if p.is_file())
    else:
        yield from (p for p in folder.iterdir() if p.is_file())

def process_directory(folder: Path, recursive: bool, dry_run: bool) -> None:
    processed = renamed = skipped = 0
    for path in iter_paths(folder, recursive):
        if path.suffix.lower() not in IMG_EXTS:
            continue
        ok, msg = process_file(path, dry_run=dry_run)
        print(msg)
        if msg.startswith("[skip]"):
            skipped += 1
        else:
            processed += 1
            if msg.startswith("[renamed]") or msg.startswith("[dry-run]"):
                renamed += 1
    print(f"\nSummary in '{folder}':")
    print(f"  Processed   : {processed}")
    print(f"  Renamed/DR  : {renamed}")
    print(f"  Skipped     : {skipped}")

def main():
    ap = argparse.ArgumentParser(description="Rename Kodak DX3700 images to DCP_0000.JPG (timestamps preserved).")
    ap.add_argument("path", nargs="?", help="Folder to process. If omitted, you'll be prompted.")
    ap.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompt.")
    ap.add_argument("--recursive", "-r", action="store_true", help="Recurse into subfolders.")
    ap.add_argument("--dry-run", "-n", action="store_true", help="Show actions without renaming files.")
    args = ap.parse_args()

    if args.path:
        folder = Path(args.path).expanduser().resolve()
    else:
        raw = input("Enter the folder path to process (or press Enter for current directory): ").strip()
        folder = Path(raw or ".").expanduser().resolve()

    if not folder.exists() or not folder.is_dir():
        print(f"Error: '{folder}' is not a valid directory.", file=sys.stderr)
        sys.exit(2)

    if not args.yes:
        print(f"You are about to process: {folder}")
        print(f"  recursive: {args.recursive}")
        print(f"  dry-run  : {args.dry_run}")
        confirm = input("Proceed? [y/N]: ").strip().lower()
        if confirm not in {"y", "yes"}:
            print("Aborted.")
            sys.exit(0)

    process_directory(folder, recursive=args.recursive, dry_run=args.dry_run)

if __name__ == "__main__":
    main()
