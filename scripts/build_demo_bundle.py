"""Create a demo bundle ZIP with a few representative files so `make demo` produces ./dist/demo_packet.zip

This script is intentionally dependency-free (stdlib only).
"""
import os
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist")
ZIP_PATH = os.path.join(DIST, "demo_packet.zip")

FILES_TO_INCLUDE = [
    os.path.join(ROOT, "raincheck_agent_logic.md"),
    os.path.join(ROOT, "actionuity_agent_logic.md"),
    os.path.join(ROOT, "generate_pitch_kit_pdf.py"),
    os.path.join(ROOT, "apps", "api", "templates", "base.html"),
]

os.makedirs(DIST, exist_ok=True)
with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
    added = 0
    for f in FILES_TO_INCLUDE:
        if os.path.exists(f):
            arcname = os.path.relpath(f, ROOT)
            zf.write(f, arcname)
            added += 1
    # If nothing matched, create a small README inside the zip
    if added == 0:
        zf.writestr("README.txt", "Demo packet placeholder. No source files were found to include.")

print(f"Demo bundle created: {ZIP_PATH}")
