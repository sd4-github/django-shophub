# =============================================================================
# python_scripts/04_file_operations.py  --  Python file operations (Django)
# =============================================================================
# Purpose: hands-on Python file I/O that backs the `files` upload app.
# Run with:  .venv/bin/python python_scripts/04_file_operations.py
#
# Topics: open modes, context managers, read/write/append, read in chunks,
#         pathlib.Path, safe filenames, shutil, tempfile.
# The `files` app (files/fileops.py + files/views.py) uses exactly these ideas.

import os
import shutil
import tempfile
from pathlib import Path

BASE = Path(tempfile.mkdtemp(prefix="fileops_demo_"))  # throwaway sandbox dir
print("sandbox:", BASE)

# --- 1) open() modes ---------------------------------------------------------
# "w"  truncate+write | "a" append | "r" read | "b" binary | "+" read-write
p = BASE / "notes.txt"
with open(p, "w", encoding="utf-8") as f:     # context manager => auto-close
    f.write("line one\n")                     # overwrite whole file
with open(p, "a", encoding="utf-8") as f:
    f.write("line two\n")                     # append at end
print(open(p).read())                          # read whole file (text mode)

# --- 2) read in chunks (streaming big files without loading into RAM) --------
with open(p, "r", encoding="utf-8") as f:
    while True:
        chunk = f.read(4)                     # read up to 4 CHARS at a time
        if not chunk:
            break
        print("chunk:", repr(chunk))

# --- 3) pathlib.Path (modern) vs os.path (legacy) ----------------------------
path = BASE / "sub" / "deep" / "file.txt"
path.parent.mkdir(parents=True, exist_ok=True)   # create dirs
path.write_text("hello")                          # pathlib quick write
print("name:", path.name, "suffix:", path.suffix)
print("exists:", path.exists(), "absolute:", path.resolve())
# legacy equivalent (still seen in older code):
print("basename:", os.path.basename(str(path)))

# --- 4) SAFE FILENAMES (security --- never trust client input) ---------------
# A malicious client could send  "../../etc/passwd". ALWAYS strip dirs:
def safe_filename(name: str) -> str:
    return os.path.basename(name.replace("\\", "/"))

print("unsafe:", safe_filename("../../etc/passwd"))     # -> passwd
print("unsafe:", safe_filename("..\\..\\evil.txt"))     # -> evil.txt

# --- 5) extension whitelist ---------------------------------------------------
def allowed(name: str, whitelist: set) -> bool:
    return Path(name).suffix.lower() in whitelist

print("txt ok:", allowed("a.TXT", {".txt"}))

# --- 6) shutil: move/copy/remove ----------------------------------------------
src = BASE / "move_me.txt"
src.write_text("data")
dest = shutil.move(str(src), str(BASE / "moved.txt"))    # move (handles cross-device)
print("moved to:", dest)
print("copy:", Path(shutil.copy(dest, BASE / "copy.txt")).name)
Path(BASE / "copy.txt").unlink()                          # delete a file
print("copy exists now:", (BASE / "copy.txt").exists())

# --- 7) tempfile: transient files auto-cleaned ---------------------------------
with tempfile.NamedTemporaryFile(mode="w", delete=True) as tf:
    tf.write("temp data")
    print("temp path:", tf.name)
# file is gone after the `with` block when delete=True

# --- cleanup -------------------------------------------------------------------
shutil.rmtree(BASE, ignore_errors=True)        # remove whole sandbox tree
print("cleaned up sandbox:", not BASE.exists())
