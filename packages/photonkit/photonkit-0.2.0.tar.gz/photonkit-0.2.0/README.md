# PhotonKit

**PhotonKit** is a mildly opinionated, blazing-fast command-line toolkit for safely backing up and organizing your camera photos and videos. Designed for macOS photo wranglers, it reads EXIF metadata to group files by date and camera, prevents clobbering, and works seamlessly with both SD cards and massive archives.

- **Automated folder structure:** Organizes by year, date, camera, and file type.
- **Supports all major formats:** JPEG, HEIC, RAW (CR2/CR3/ARW/NEF), MOV, MP4, AVI, and more.
- **Resumable and safe:** Skips duplicates by default, or saves unique versions on demand.
- **Per-directory cache:** Re-scans are lightning fast, only extracting EXIF for new files.
- **Dry-run & date filtering:** Preview operations and filter files by EXIF date.
- **EXIF overrides:** Handles edge cases (like iPhone movies) using customizable rules.
- **MIT License:** Free for all personal and commercial use.

Perfect for anyone who wants to keep their photo archives pristine and searchable—no more messy folders or lost images.

See full documentation, installation, and usage at: [https://github.com/rsitools/photonkit](https://github.com/rsitools/photonkit)
