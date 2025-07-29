# backup/utils/inspect_exif.py

import subprocess
from pathlib import Path

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
        camera_model = None
        date_original = None
        for line in result.stdout.splitlines():
            if "Camera Model Name" in line:
                camera_model = line.split(":", 1)[1].strip()
            if "Date/Time Original" in line:
                date_original = line.split(":", 1)[1].strip()
        print("\n---")
        print(f"Camera Model Name      : {camera_model if camera_model else '[Not Found]'}")
        print(f"Date/Time Original     : {date_original if date_original else '[Not Found]'}")
    except Exception as e:
        print(f"❌ Exception: {e}")
