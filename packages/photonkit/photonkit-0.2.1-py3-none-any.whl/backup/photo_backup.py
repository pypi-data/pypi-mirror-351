# backup/photo_backup.py
# CLI entry point for PhotonKit: EXIF cache, min-date filtering, progress feedback, EXIF inspection

import argparse
import sys
from pathlib import Path
import datetime
from backup.utils.file_utils import is_hidden_or_system_file, get_file_type
from backup.utils.metadata_utils import extract_camera_model_and_date, ensure_exiftool
from backup.utils.path_utils import get_target_path
from backup.utils.cache_utils import load_cache, append_cache_record
from backup.utils.inspect_exif import inspect_exif

import shutil
import os

def main():
    parser = argparse.ArgumentParser(
        description="PhotonKit – safely organize and manage your camera photos."
    )
    parser.add_argument(
        "--source",
        help="Path to the source folder or volume (e.g., SD card)"
    )
    parser.add_argument(
        "--target",
        help="Path to the backup folder or volume (e.g., external drive)"
    )
    parser.add_argument(
        "--skip-dupe", default="true",
        help=(
            "(default) true, skip files that already exist in target. "
            "false allows duplicates (IMG_1234-1.jpg, etc)."
        )
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be copied without actually copying."
    )
    parser.add_argument(
        "--min-date",
        help="Only sync files with EXIF date on or after this YYYY-MM-DD."
    )
    parser.add_argument(
        "--exif",
        help="Show full EXIF and important tags for a file, then exit."
    )

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(0)

    args = parser.parse_args()

    # --- EXIF INSPECTION MODE ---
    if args.exif:
        file_path = Path(args.exif).expanduser().resolve()
        if not file_path.exists():
            print(f"❌ File does not exist: {file_path}")
            sys.exit(2)
        inspect_exif(file_path)
        sys.exit(0)

    # --- REGULAR BACKUP MODE ---
    if not args.source or not args.target:
        print("❌ --source and --target are required unless --exif is used.")
        parser.print_help()
        sys.exit(1)

    skip_dupe = args.skip_dupe.lower() in ("true", "yes", "1")
    dry_run = args.dry_run

    min_date = None
    if args.min_date:
        try:
            min_date = datetime.datetime.strptime(args.min_date, "%Y-%m-%d").date()
        except Exception:
            print(f"❌ Invalid --min-date format. Use YYYY-MM-DD.")
            sys.exit(1)

    source = Path(args.source).expanduser().resolve()
    target = Path(args.target).expanduser().resolve()
    if not source.exists():
        print(f"❌ Source does not exist: {source}")
        return
    target.mkdir(parents=True, exist_ok=True)

    print(f"📥 Indexing source: {source}")
    print(f"📤 Target: {target}")
    if min_date:
        print(f"⏳ Only syncing files on or after: {min_date}")

    copied = 0
    skipped = 0
    errored = 0

    try:
        ensure_exiftool()

        for root, _, files in os.walk(source):
            dir_path = Path(root)
            cache = load_cache(dir_path)
            uncached_files = [f for f in files if f not in cache]
            if uncached_files:
                print(f"Building cache for {dir_path} ...")
            for idx, f in enumerate(files):
                src_path = dir_path / f

                # Skip hidden, system, dirs
                if is_hidden_or_system_file(src_path) or src_path.is_dir():
                    continue

                # Skip unsupported types
                category = get_file_type(src_path.suffix)
                if not category:
                    print(f"⚠️  Skipping unsupported type: {src_path}")
                    skipped += 1
                    continue

                # Use cache if available, else extract and append (with progress)
                if f in cache:
                    camera = cache[f]["camera"]
                    year = cache[f]["year"]
                    date_str = cache[f]["date"]
                else:
                    camera, year, date_str = extract_camera_model_and_date(src_path)
                    append_cache_record(dir_path, f, camera, year, date_str, build_mode=True, counter=idx+1)

                # --min-date filtering
                if min_date:
                    try:
                        file_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                        if file_date < min_date:
                            skipped += 1
                            continue  # skip this file
                    except Exception:
                        print(f"⚠️  Could not parse date for {src_path}: {date_str}")
                        skipped += 1
                        continue

                target_dir = target / year / date_str / camera / category
                base_target_path = target_dir / src_path.name
                final_target_path = get_target_path(base_target_path, skip_dupe)

                if dry_run:
                    if final_target_path is not None:
                        print(f"Would copy: {src_path} -> {final_target_path}")
                        copied += 1
                    else:
                        print(f"⚠️  Would skip: {src_path} (cannot resolve unique destination, likely a duplicate or naming conflict)")
                        skipped += 1
                    continue

                # Perform copy if not dry-run
                target_dir.mkdir(parents=True, exist_ok=True)
                print(f"Copying {src_path} -> {final_target_path} ... ", end="", flush=True)
                try:
                    if final_target_path is None:
                        print("⏩ skipped (dupe or conflict)")
                        skipped += 1
                        continue
                    shutil.copy2(src_path, final_target_path)
                    print("✅ success")
                    copied += 1
                except Exception as e:
                    print(f"❌ error: {e}")
                    errored += 1

                # Print cache progress every 100 files when building cache
                if f not in cache and (idx + 1) % 100 == 0:
                    print(f"  ...{idx + 1}")

        print(f"\nDone! Copied: {copied}, Skipped: {skipped}, Errors: {errored}")
        if dry_run:
            print("Dry run complete. No files were copied.")

    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user. Exiting cleanly.")

if __name__ == "__main__":
    main()
