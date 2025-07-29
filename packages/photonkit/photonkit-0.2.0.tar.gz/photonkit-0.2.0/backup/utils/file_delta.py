# backup/lib/file_delta.py
# Helper for building metadata-based source/target maps and finding copy deltas
# Uses one exiftool batch call (-j -r) to grab all EXIF data at once.

import os
import subprocess
import json
import datetime
from pathlib import Path
from backup.utils.file_utils import is_hidden_or_system_file, get_file_type
from backup.utils.metadata_utils import normalize_camera_name, extract_date_taken


def batch_extract_exif_map(folder: Path) -> dict[Path, dict]:
    """
    Runs one exiftool command to recursively extract ALL EXIF tags as JSON.
    Returns a map: { Path(<file>): { <tag>: <value>, ... } }
    """
    cmd = ["exiftool", "-j", "-r", str(folder)]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        exif_list = json.loads(result.stdout)
    except Exception as e:
        print(f"❌ Batch EXIF extraction failed: {e}")
        return {}

    exif_map: dict[Path, dict] = {}
    for entry in exif_list:
        src = Path(entry.get("SourceFile", ""))  # exiftool key for file path
        if src:
            exif_map[src] = entry
    return exif_map


def parse_exif_date(entry: dict, fallback_path: Path) -> tuple[str, str]:
    """
    Attempts to parse the first available EXIF date tag into (year, YYYY-MM-DD).
    Falls back to filesystem mtime if none present or parse fails.
    """
    for tag in ("DateTimeOriginal", "CreateDate", "ModifyDate"):
        dt_str = entry.get(tag)
        if dt_str:
            try:
                # exiftool format: "YYYY:MM:DD HH:MM:SS"
                dt = datetime.datetime.strptime(dt_str, "%Y:%m:%d %H:%M:%S")
                return dt.strftime("%Y"), dt.strftime("%Y-%m-%d")
            except Exception:
                break
    # fallback
    return extract_date_taken(fallback_path)


def build_file_map(folder: Path) -> dict[str, Path]:
    """
    Builds a dict mapping key = year_date_camera_filename to full file path.
    Uses batch_exif_map for camera + all EXIF, fast for large folders.
    """
    # 1) Gather and filter files
    all_files = []
    for root, _, files in os.walk(folder):
        for f in files:
            src = Path(root) / f
            if is_hidden_or_system_file(src) or src.is_dir():
                continue
            if get_file_type(src.suffix):
                all_files.append(src)

    print(f"  Scanning {len(all_files)} files for EXIF data...", flush=True)

    # 2) Batch EXIF
    exif_map = batch_extract_exif_map(folder)

    # 3) Build key→path map
    file_map: dict[str, Path] = {}
    for count, src in enumerate(all_files, 1):
        entry = exif_map.get(src, {})
        # date
        year, date_str = parse_exif_date(entry, src)
        # camera
        camera = normalize_camera_name(entry.get("Model", ""))
        # filename
        key = f"{year}_{date_str}_{camera}_{src.name}"
        file_map[key] = src

        if count % 100 == 0:
            print(f"  ...{count}", flush=True)

    print(f"  Indexed {len(all_files)} files.\n")
    return file_map


def find_source_delta(source_map: dict[str, Path], target_map: dict[str, Path]) -> list[str]:
    """
    Returns the list of keys present in source but not in target (files to copy).
    """
    return [k for k in source_map.keys() if k not in target_map]
