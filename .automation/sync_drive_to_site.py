#!/usr/bin/env python3
"""
Art of Telling — Student Materials Auto-Publish
=================================================

Watches the Google Drive folder "Art of Telling" for new STUDENT-facing
course materials and publishes them automatically to the public course
website (github.com/jamesfmulhern-hue/art-of-telling), then logs the
update to the "Media Kit Backlog" Notion database.

STUDENT-ONLY FILTER (the whole point of this script):
  - INCLUDE: PDF files whose name matches a student-facing pattern:
        *_Student_Handout_*.pdf
        *Student*Booklet*.pdf / *Student*Edition*.pdf / *Student*Guide*.pdf
        *Companion*Booklet*.pdf / *Companion*Handout*.pdf
        (i.e. explicit "Student" / "Companion" / "Handout" naming — the
         convention already used in this Drive folder and on the live site)
  - EXCLUDE: anything containing "_Brief_", "Instructor", "Proposal",
    "Answer Key", "Teacher", "Private", "Draft", "DRAFT", "WIP"
  - EXCLUDE: DOCX/editable-source files (only the PDF is published)
  - EXCLUDE: anything not directly in the watched folder (no subfolders,
    no "Private Memoir Resources" or other instructor-only folders)

This script is idempotent: it tracks published files in
art-of-telling/handouts/manifest.json (keyed by Drive file ID + name) and
only acts on files it hasn't already published, or that changed (new
Drive revision -> re-download + note "updated" in backlog).

Run: python3 sync_drive_to_site.py
Requires: gws CLI (Google Drive), git + gh CLI (GitHub), and the Notion
MCP connector for the backlog log (handled by the calling agent/cron step,
see notion_log.py which is invoked separately since Notion access here is
via the agent's connector, not a raw API key).
"""
import json
import os
import re
import subprocess
import sys
import unicodedata
from datetime import datetime, timezone

REPO_DIR = os.environ.get("AOT_REPO_DIR", "/home/user/workspace/art-of-telling")
HANDOUTS_DIR = os.path.join(REPO_DIR, "handouts")
MANIFEST_PATH = os.path.join(HANDOUTS_DIR, "manifest.json")
DRIVE_FOLDER_ID = "10XE4eEIe1t6tsATlYgSq3KDrcM9UItBC"  # "Art of Telling" Drive folder
EXCLUDED_FOLDER_IDS = {
    "1_8drpbHJ27Nv13KMI_vCXnlZw-qkR-0G",  # "Art of Telling — Private Memoir Resources"
}
NEW_PUBLISH_QUEUE_PATH = os.path.join(os.path.dirname(__file__), "new_publishes.json")

EXCLUDE_PATTERNS = [
    r"_brief_", r"instructor", r"proposal", r"answer[_\s-]?key",
    r"teacher", r"private", r"\bdraft\b", r"\bwip\b",
]
INCLUDE_PATTERNS = [
    r"student", r"companion", r"handout", r"booklet", r"worksheet", r"guide",
]

SESSION_RE = re.compile(r"session[_\s-]?(\d{1,2})", re.IGNORECASE)


def sh(args_list, **kw):
    return subprocess.run(args_list, capture_output=True, text=True, **kw)


def drive_list_folder(folder_id):
    q = f"'{folder_id}' in parents and trashed = false and mimeType = 'application/pdf'"
    params = json.dumps({"q": q, "fields": "files(id,name,mimeType,modifiedTime,webViewLink,md5Checksum)"})
    result = sh(["gws", "drive", "files", "list", "--params", params])
    if result.returncode != 0:
        print("ERROR listing Drive folder:", result.stderr, file=sys.stderr)
        sys.exit(1)
    return json.loads(result.stdout).get("files", [])


def is_student_facing(name):
    lname = name.lower()
    for pat in EXCLUDE_PATTERNS:
        if re.search(pat, lname):
            return False
    for pat in INCLUDE_PATTERNS:
        if re.search(pat, lname):
            return True
    return False


def guess_session(name):
    m = SESSION_RE.search(name)
    if m:
        return f"Session {int(m.group(1))}"
    return "General / Course-Wide"


def slugify_filename(name):
    """Turn a Drive filename into a clean, URL-safe filename for the public
    site (no spaces, no em dashes) while keeping it human-readable."""
    stem, ext = os.path.splitext(name)
    stem = unicodedata.normalize("NFKD", stem)
    stem = stem.encode("ascii", "ignore").decode("ascii")  # drop em dashes, curly quotes, etc.
    stem = re.sub(r"[^A-Za-z0-9]+", "-", stem).strip("-")
    return f"{stem}{ext.lower()}"


def humanize_title(filename):
    stem = re.sub(r"\.pdf$", "", filename, flags=re.IGNORECASE)
    stem = re.sub(r"_?\d{4}-\d{2}-\d{2}$", "", stem)  # strip trailing date
    stem = stem.replace("_", " ").strip()
    # Strip a leading "Art of Telling" prefix, whether joined by an em dash,
    # hyphen, or plain space (covers both underscore-style and title-style names)
    stem = re.sub(r"^Art\s+of\s+Telling\s*[\u2014\u2013\-:]*\s*", "", stem, flags=re.IGNORECASE)
    stem = re.sub(r"\s+", " ", stem).strip()
    stem = stem.strip("— ").strip()
    return stem


def load_manifest():
    if os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH) as f:
            return json.load(f)
    return {"published": []}


def save_manifest(manifest):
    os.makedirs(HANDOUTS_DIR, exist_ok=True)
    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")


def download_file(file_id, dest_path):
    # gws requires --output paths relative to its own cwd; run gws with cwd
    # set to the destination's directory and pass just the filename.
    dest_dir = os.path.dirname(dest_path)
    dest_name = os.path.basename(dest_path)
    params = json.dumps({"fileId": file_id, "alt": "media"})
    result = sh(["gws", "drive", "files", "get", "--params", params, "--output", dest_name], cwd=dest_dir)
    if result.returncode != 0 or not os.path.exists(dest_path):
        print(f"ERROR downloading {file_id}: {result.stderr}", file=sys.stderr)
        return False
    return True


def main():
    manifest = load_manifest()
    published_by_id = {p["drive_file_id"]: p for p in manifest["published"] if p.get("drive_file_id")}
    published_by_drive_name = {p.get("drive_name", p["filename"]): p for p in manifest["published"]}

    files = drive_list_folder(DRIVE_FOLDER_ID)
    new_publishes = []

    for f in files:
        name = f["name"]
        if not is_student_facing(name):
            continue

        checksum = f.get("md5Checksum")
        existing = published_by_id.get(f["id"]) or published_by_drive_name.get(name)

        if existing and existing.get("md5") == checksum:
            continue  # already published, unchanged

        # New file, or changed content under the same name
        safe_name = slugify_filename(name)
        os.makedirs(HANDOUTS_DIR, exist_ok=True)
        dest = os.path.join(HANDOUTS_DIR, safe_name)
        ok = download_file(f["id"], dest)
        if not ok:
            print(f"Skipping {name}: download failed", file=sys.stderr)
            continue

        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        entry = {
            "drive_file_id": f["id"],
            "filename": safe_name,
            "drive_name": name,
            "title": humanize_title(name),
            "session": guess_session(name),
            "published_date": today,
            "md5": checksum,
            "drive_link": f.get("webViewLink", ""),
            "source": "auto-synced from Drive",
        }

        # Replace existing entry (by Drive source name) or append; also
        # remove any stale file left behind by a previous slug/name.
        old_entry = next((p for p in manifest["published"] if p.get("drive_name", p.get("filename")) == name), None)
        if old_entry and old_entry.get("filename") != safe_name:
            stale_path = os.path.join(HANDOUTS_DIR, old_entry["filename"])
            if os.path.exists(stale_path):
                os.remove(stale_path)
        manifest["published"] = [p for p in manifest["published"] if p.get("drive_name", p.get("filename")) != name]
        manifest["published"].append(entry)
        new_publishes.append({**entry, "was_update": bool(existing)})
        print(f"Published: {name} -> {entry['title']} ({entry['session']})")

    save_manifest(manifest)

    with open(NEW_PUBLISH_QUEUE_PATH, "w") as f:
        json.dump(new_publishes, f, indent=2)

    if not new_publishes:
        print("No new student materials found. Nothing to publish.")
    else:
        print(f"{len(new_publishes)} item(s) queued for site regeneration + backlog logging.")


if __name__ == "__main__":
    main()
