# backup/lib/metadata_utils.py
# Metadata utilities: EXIF extraction using exiftool CLI text parsing, with camera overrides for special cases

import subprocess
import datetime
import re
from pathlib import Path
from backup.utils.file_utils import get_file_type
from backup.utils.camera_overrides import get_exif_fields_for

EXIFTOOL_TIMEOUT = 5  # seconds
MAX_CAMERA_NAME_LEN = 32

def normalize_camera_name(name: str) -> str:
    """Sanitize and truncate camera model into filesystem-safe string."""
    if not name:
        return "camera-default"
    name = re.sub(r"[^a-zA-Z0-9]+", "-", name).strip("-").lower()
    return name[:MAX_CAMERA_NAME_LEN] if name else "camera-default"

def extract_camera_model_and_date(path: Path) -> tuple[str, str, str]:
    """
    Extracts camera model and date using exiftool and any override rules.
    Returns (camera_model, year, date_str)
    """
    filetype = path.suffix.lower().lstrip(".")
    exif = {}
    try:
        result = subprocess.run(
            ["exiftool", str(path)],
            capture_output=True,
            text=True,
            timeout=EXIFTOOL_TIMEOUT,
        )
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    exif[k.strip()] = v.strip()
    except Exception:
        pass

    # Determine make (for override rules)
    make = exif.get("Make", "").lower()
    overrides = get_exif_fields_for(make, filetype)
    model_field = overrides.get("model", "Camera Model Name")
    date_field = overrides.get("date", "Date/Time Original")

    # Camera Model
    camera_model = (
        exif.get(model_field)
        or exif.get("Camera Model Name")
        or exif.get("Model")
        or ""
    )
    camera_model = normalize_camera_name(camera_model)

    # Date Extraction
    dt_str = exif.get(date_field, "")
    if dt_str:
        # Remove milliseconds/timezone if present
        dt_main = dt_str.split()[0] if " " in dt_str else dt_str
        dt_main = dt_main.split(".")[0]
        try:
            dt = datetime.datetime.strptime(dt_main, "%Y:%m:%d")
            return camera_model, dt.strftime("%Y"), dt.strftime("%Y-%m-%d")
        except Exception:
            # Try date+time without ms/tz
            try:
                dt_short = dt_str[:19]  # "YYYY:MM:DD HH:MM:SS"
                dt = datetime.datetime.strptime(dt_short, "%Y:%m:%d %H:%M:%S")
                return camera_model, dt.strftime("%Y"), dt.strftime("%Y-%m-%d")
            except Exception:
                pass

    # Fallback: filesystem mtime
    try:
        timestamp = path.stat().st_mtime
        dt = datetime.datetime.fromtimestamp(timestamp)
        return camera_model, dt.strftime("%Y"), dt.strftime("%Y-%m-%d")
    except Exception:
        return camera_model, "unknown", "unknown-date"

def ensure_exiftool():
    """Ensure ExifTool is installed, else raise an informative error."""
    try:
        subprocess.run(["exiftool", "-ver"], capture_output=True, check=True)
    except Exception:
        raise EnvironmentError("ExifTool not found. Install via `brew install exiftool`.")
