# backup/lib/camera_overrides.py
# Returns which EXIF fields to use for a given make + file type for date and model

# This can be expanded as you discover more exceptions
OVERRIDES = {
    # (make, file_type): {"date": <EXIF field>, "model": <EXIF field>}
    ("apple", "mov"): {"date": "Create Date", "model": "Model"},
    ("apple", "mp4"): {"date": "Create Date", "model": "Model"},
    # You can add more here in the future
}

def get_exif_fields_for(make: str, filetype: str) -> dict:
    """
    Returns a dict {"date": ..., "model": ...} if there is a known override for this make and file type,
    else returns {} (empty dict).
    """
    key = (make.lower(), filetype.lower())
    return OVERRIDES.get(key, {})
