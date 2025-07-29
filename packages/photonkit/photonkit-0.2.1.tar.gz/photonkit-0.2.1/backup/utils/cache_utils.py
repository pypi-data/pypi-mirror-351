# backup/lib/cache_utils.py
# CSV cache of extracted EXIF for each directory, with progress feedback

import csv
from pathlib import Path

CACHE_FILENAME = ".photonkit_cache.csv"
CACHE_HEADERS = ["filename", "camera", "year", "date"]

def load_cache(directory: Path) -> dict:
    """Load cache file from the directory, return as a dict."""
    cache = {}
    cache_path = directory / CACHE_FILENAME
    if cache_path.exists():
        with open(cache_path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cache[row["filename"]] = {
                    "camera": row["camera"],
                    "year": row["year"],
                    "date": row["date"],
                }
    return cache

def append_cache_record(directory: Path, filename: str, camera: str, year: str, date: str, build_mode: bool = False, counter: int = 0):
    """
    Append a single record to the directory's cache file.
    If build_mode, print progress every 100 files.
    """
    cache_path = directory / CACHE_FILENAME
    file_exists = cache_path.exists()
    with open(cache_path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CACHE_HEADERS)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "filename": filename,
            "camera": camera,
            "year": year,
            "date": date,
        })
    if build_mode and counter % 100 == 0 and counter > 0:
        print(f"  cache ...{counter}")

