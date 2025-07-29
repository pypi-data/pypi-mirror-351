# inspect_exif.py
# Standalone CLI utility to print EXIF metadata from a file, and then print Camera Model Name & Date/Time Original

import sys
import subprocess
from pathlib import Path
import re

def inspect_exif(file_path: Path):
    try:
        result = subprocess.run(
            ["exiftool", str(file_path)],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode != 0:
            print(f"❌ Error running exiftool: {result.stderr.strip()}")
            return
        print(result.stdout)
        
        # Extract Camera Model Name and Date/Time Original from output
        camera_model = None
        date_original = None
        for line in result.stdout.splitlines():
            if "Camera Model Name" in line:
                # Handle both ":" and possible space before value
                camera_model = line.split(":", 1)[1].strip()
            if "Date/Time Original" in line:
                date_original = line.split(":", 1)[1].strip()
        
        print("\n---")
        print(f"Camera Model Name      : {camera_model if camera_model else '[Not Found]'}")
        print(f"Date/Time Original     : {date_original if date_original else '[Not Found]'}")

    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    if len(sys.argv) != 2:
        print("Usage: inspect_exif.py <file>")
        sys.exit(1)
    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"❌ File does not exist: {file_path}")
        sys.exit(2)
    inspect_exif(file_path)

if __name__ == "__main__":
    main()
