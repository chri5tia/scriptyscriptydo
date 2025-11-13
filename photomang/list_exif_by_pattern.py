#!/usr/bin/env python3
import csv
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

IMAGE_EXTS = {".jpg", ".jpeg", ".cr2", ".cr3", ".raf", ".arw", ".tif", ".tiff", ".png", ".dng", ".heic", ".heif"}

def have_exiftool() -> bool:
    return shutil.which("exiftool") is not None

def use_mdls() -> bool:
    # macOS metadata fallback
    return sys.platform == "darwin" and shutil.which("mdls") is not None

def find_candidate_files(start_pattern: str, root: Path) -> list[Path]:
    pat = start_pattern  # match prefix of basename (case-sensitive by default)
    results = []
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix.lower() not in IMAGE_EXTS:
            continue
        if p.name.startswith(pat):
            results.append(p)
    return results

def exiftool_read_batch(paths: list[Path]) -> dict[str, dict]:
    """Call exiftool once for all files; return map path->tag dict."""
    if not paths:
        return {}
    cmd = [
        "exiftool",
        "-j",          # JSON
        "-n",          # numeric where applicable (keeps dates parseable)
        "-fast2",
        "-EXIF:Model",
        "-EXIF:Make",
        "-DateTimeOriginal",
        "-CreateDate",
    ] + [str(p) for p in paths]
    out = subprocess.check_output(cmd)
    data = json.loads(out.decode("utf-8", errors="ignore"))
    outmap = {}
    for item in data:
        # exiftool returns "SourceFile"
        src = item.get("SourceFile")
        if src:
            outmap[os.path.abspath(src)] = item
    return outmap

def mdls_read(path: Path) -> dict:
    """Very light fallback using mdls (macOS)."""
    # Useful attributes: kMDItemAcquisitionMake, kMDItemAcquisitionModel, kMDItemContentCreationDate
    cmd = ["mdls", "-raw",
           "-name", "kMDItemAcquisitionMake",
           "-name", "kMDItemAcquisitionModel",
           "-name", "kMDItemContentCreationDate",
           str(path)]
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode("utf-8", errors="ignore").splitlines()
    except subprocess.CalledProcessError:
        out = []
    # mdls returns each value on its own line in the same order
    # If missing, it may print "(null)" or nothing
    def clean(v: str | None):
        if not v:
            return None
        v = v.strip()
        return None if v in {"(null)", ""} else v

    return {
        "Make": clean(out[0] if len(out) > 0 else None),
        "Model": clean(out[1] if len(out) > 1 else None),
        # Coerce to a single date key similar to exiftool’s
        "DateTimeOriginal": clean(out[2] if len(out) > 2 else None) or None,
        "CreateDate": None,  # mdls doesn’t distinguish; we use ContentCreationDate above
    }

def has_full_exif(tags: dict) -> tuple[bool, str | None, str | None]:
    model = tags.get("Model") or tags.get("EXIF:Model")
    # Prefer DateTimeOriginal; fallback to CreateDate
    date = tags.get("DateTimeOriginal") or tags.get("CreateDate")
    return (bool(model and date), model, date)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 list_exif_by_pattern.py \"2011 06 19\" [--show-missing]", file=sys.stderr)
        sys.exit(1)

    start_pattern = sys.argv[1]
    show_missing = "--show-missing" in sys.argv[2:]

    root = Path(".").resolve()
    files = find_candidate_files(start_pattern, root)

    if not files:
        print("No matching files found.", file=sys.stderr)
        sys.exit(0)

    # Gather metadata
    meta_map: dict[str, dict] = {}
    if have_exiftool():
        try:
            meta_map = exiftool_read_batch(files)
        except Exception as e:
            print(f"exiftool failed ({e}); falling back to mdls if available.", file=sys.stderr)
            if not use_mdls():
                sys.exit(2)

    rows_with = []
    rows_missing = []

    for f in files:
        tags = None
        if meta_map:
            tags = meta_map.get(str(f.resolve()))
        if tags is None:
            if use_mdls():
                tags = mdls_read(f)
            else:
                tags = {}

        ok, model, cdate = has_full_exif(tags)
        row = {
            "path": str(f),
            "filename": f.name,
            "size_bytes": f.stat().st_size,
            "model": model or "",
            "capture_date": cdate or "",
        }
        if ok:
            rows_with.append(row)
        else:
            rows_missing.append(row)

    # CSV output: by default only “full EXIF” rows
    writer = csv.DictWriter(sys.stdout, fieldnames=["path", "filename", "size_bytes", "model", "capture_date"])
    writer.writeheader()
    for r in rows_with:
        writer.writerow(r)

    # Optional section for missing
    if show_missing and rows_missing:
        print("\n# MISSING_EXIF\n")
        writer = csv.DictWriter(sys.stdout, fieldnames=["path", "filename", "size_bytes", "model", "capture_date"])
        writer.writeheader()
        for r in rows_missing:
            writer.writerow(r)

    print(f"\nSummary: {len(rows_with)} with full EXIF, {len(rows_missing)} missing key fields, scanned {len(files)} files.")

if __name__ == "__main__":
    main()

