# =============================================================================
# files/fileops.py  --  Python file operations (interview-ready utility)
# =============================================================================
# File handling is a frequent interview topic. This module centralises the
# common patterns with clear comments, and is USED by the upload view.
# Run the companion python_scripts/04_file_operations.py for hands-on demos.
#
# Topics covered:
#   * open() modes           : "r", "w", "a", "wb", "rb", "+"
#   * with / context manager : guaranteed close even on exceptions
#   * reading in chunks      : streaming large files without loading into RAM
#   * pathlib.Path           : modern path handling (vs old os.path)
#   * safe filenames         : never trust client filenames
#   * file extensions        : whitelisting uploads
#   * shutil                 : move/copy/delete files & trees
#   * tempfile               : throwaway files for transient work

import mimetypes
import os
import shutil
from pathlib import Path


def safe_filename(filename: str) -> str:
    """Strip any directory components from an untrusted client filename.
       Never let a user upload '../../evil.txt' and write outside our dir!"""
    return os.path.basename(filename.replace("\\", "/"))


def allowed_extension(filename: str, whitelist: set[str]) -> bool:
    """Reject uploads whose extension isn't in the whitelist."""
    return Path(filename).suffix.lower() in whitelist


def save_upload(uploaded_file, dest_dir: str, whitelist: set[str]) -> Path:
    """Stream an uploaded file to disk in CHUNKS (low memory for big files).
       Returns the final Path, or raises ValueError if not allowed."""
    name = safe_filename(uploaded_file.name)
    if not allowed_extension(name, whitelist):
        raise ValueError(f"File type not allowed: {name}")

    Path(dest_dir).mkdir(parents=True, exist_ok=True)
    dest = Path(dest_dir) / name

    # Open the destination for BINARY writing, then copy chunk-by-chunk.
    # `uploaded_file.chunks()` yields memory-friendly pieces (default ~64KB).
    with open(dest, "wb") as out:
        for chunk in uploaded_file.chunks():
            out.write(chunk)               # write each chunk to disk
    return dest


def read_in_chunks(path: str, chunk_size: int = 1024) -> list[str]:
    """Read a text file line/block-by-block to show streaming reads.
       Returns the lines collected — the real point is the chunked read loop."""
    lines: list[str] = []
    with open(path, "r", encoding="utf-8") as f:
        while True:
            chunk = f.read(chunk_size)     # read up to chunk_size characters
            if not chunk:
                break                      # EOF
            lines.append(chunk)
    return lines


def write_text(path: str, text: str, mode: str = "w") -> None:
    """Write (or append) text using a context manager.
       mode='w' overwrites; mode='a' appends; 'w+' reads+overwrites."""
    with open(path, mode, encoding="utf-8") as f:
        f.write(text)


def analyze(path: str) -> dict:
    """Return basic metadata about a file (pathlib + os demos)."""
    p = Path(path)
    size = os.path.getsize(path)
    mime, _ = mimetypes.guess_type(path)
    return {
        "exists": p.exists(),
        "name": p.name,
        "size_bytes": size,
        "is_file": p.is_file(),
        "mime_type": mime,
        "absolute": str(p.resolve()),
    }


def move_file(src: str, dst_dir: str) -> Path:
    """Move a file into a directory using shutil (handles cross-device moves)."""
    Path(dst_dir).mkdir(parents=True, exist_ok=True)
    dest = shutil.move(src, dst_dir)       # returns the new path
    return Path(dest)
