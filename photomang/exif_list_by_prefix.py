#!/usr/bin/env python3
import argparse, json, shutil, subprocess, sys
from pathlib import Path

IMAGE_EXTS = {".jpg",".jpeg",".cr2",".cr3",".raf",".arw",".dng",".tif",".tiff",".heic",".heif",".png"}

def collect_candidates(prefix: str, root: Path):
    # Filter by basename prefix + known image extensions
    out = []
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in IMAGE_EXTS and p.name.startswith(prefix):
            out.append(p)
    return out

def main():
    ap = argparse.ArgumentParser(description="List files with Model + DateTimeOriginal by filename prefix.")
    ap.add_argument("prefix", help='Basename prefix, e.g. "2011 06 19"')
    ap.add_argument("--delim", default="||", help="Field delimiter (default: ||)")
    ap.add_argument("--vertical", action="store_true", help="Print in mysql-like \\G blocks")
    args = ap.parse_args()

    if shutil.which("exiftool") is None:
        print("exiftool not found in PATH", file=sys.stderr); sys.exit(2)

    root = Path(".").resolve()
    files = collect_candidates(args.prefix, root)
    if not files:
        # Quietly exit with no output if nothing matches
        sys.exit(0)

    # Call exiftool ONCE with the explicit file list (no recursion).
    # -q -q silences the “N files read” banners so JSON is clean.
    cmd = ["exiftool","-j","-n","-q","-q",
           "-FileName","-Directory","-DateTimeOriginal","-CreateDate","-Model"
          ] + [str(f) for f in files]

    try:
        out = subprocess.check_output(cmd)
    except subprocess.CalledProcessError:
        sys.exit(0)

    payload = out.decode("utf-8", "ignore").strip()
    if not payload:
        sys.exit(0)

    try:
        items = json.loads(payload)
    except json.JSONDecodeError:
        # If something still slips through, fail gracefully with no output.
        sys.exit(0)

    if args.vertical:
        for it in items:
            model = it.get("Model")
            dt = it.get("DateTimeOriginal") or it.get("CreateDate")
            if not (model and dt):
                continue
            fname = it.get("FileName","")
            path = f"{it.get('Directory','')}/{fname}" if fname else it.get("SourceFile","")
            print("***")
            print(f"FileName: {fname}")
            print(f"DateTimeOriginal: {dt}")
            print(f"Path: {path}")
    else:
        dlm = args.delim
        for it in items:
            model = it.get("Model")
            dt = it.get("DateTimeOriginal") or it.get("CreateDate")
            if not (model and dt):
                continue
            fname = it.get("FileName","")
            path = f"{it.get('Directory','')}/{fname}" if fname else it.get("SourceFile","")
            print(f"{fname}{dlm}{dt}{dlm}{path}")

if __name__ == "__main__":
    main()
