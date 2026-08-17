#!/usr/bin/env python3
"""
Fills the existing empty HANDOUTS-sN / HANDOUTS-course marker blocks on
individual session pages (s1.html..s10.html, index.html) with auto-generated
handout links from manifest.json, matching the site's existing hand-authored
markup pattern (see s8.html).

SAFETY RULE: this script ONLY touches a marker block if it is currently
EMPTY (just "<!-- HANDOUTS-sN START --> <!-- HANDOUTS-sN END -->" with
nothing between them). If a marker block already has hand-written content
(like s8.html's curated descriptions), it is left completely untouched —
we never overwrite manually curated copy.
"""
import json
import os
import re
import sys

REPO_DIR = os.environ.get("AOT_REPO_DIR", "/home/user/workspace/art-of-telling")
MANIFEST_PATH = os.path.join(REPO_DIR, "handouts", "manifest.json")

CARD_TMPL = """        <a class="aot-handout-link" href="handouts/{filename}" download>
          <span class="aot-handout-icon" aria-hidden="true">PDF</span>
          <span>{title}</span>
        </a>"""


def load_manifest():
    with open(MANIFEST_PATH) as f:
        return json.load(f)


def group_by_session(manifest):
    groups = {}
    for item in manifest.get("published", []):
        groups.setdefault(item["session"], []).append(item)
    return groups


def marker_is_empty(html, marker):
    pattern = re.compile(
        rf"(<!-- HANDOUTS-{marker} START -->)(.*?)(<!-- HANDOUTS-{marker} END -->)",
        re.DOTALL,
    )
    m = pattern.search(html)
    if not m:
        return None, None
    inner = m.group(2).strip()
    return (inner == ""), m


def fill_marker(html, marker, items):
    pattern = re.compile(
        rf"(<!-- HANDOUTS-{marker} START -->)(.*?)(<!-- HANDOUTS-{marker} END -->)",
        re.DOTALL,
    )
    cards = "\n".join(CARD_TMPL.format(filename=i["filename"], title=i["title"]) for i in items)
    replacement = f"\\1\n{cards}\n        \\3"
    return pattern.sub(replacement, html, count=1)


def process_page(path, marker, items):
    if not os.path.exists(path):
        return "missing-file"
    with open(path) as f:
        html = f.read()

    is_empty, match = marker_is_empty(html, marker)
    if match is None:
        return "no-marker"
    if not is_empty:
        return "skipped-has-content"
    if not items:
        return "no-items"

    new_html = fill_marker(html, marker, items)
    # Reveal the section if it was hidden via the "empty" placeholder class
    # (used on index.html's course-wide handouts block before it has content).
    new_html = new_html.replace(
        f'class="aot-handouts empty" id="{marker}-handouts"',
        f'class="aot-handouts" id="{marker}-handouts"',
    )
    with open(path, "w") as f:
        f.write(new_html)
    return f"filled-{len(items)}"


def main():
    manifest = load_manifest()
    groups = group_by_session(manifest)

    results = {}

    # Session pages s1..s10
    for n in range(1, 11):
        session_label = f"Session {n}"
        items = groups.get(session_label, [])
        path = os.path.join(REPO_DIR, f"s{n}.html")
        results[f"s{n}"] = process_page(path, f"s{n}", items)

    # Course-wide materials on the homepage
    general_items = groups.get("General / Course-Wide", [])
    path = os.path.join(REPO_DIR, "index.html")
    results["course"] = process_page(path, "course", general_items)

    for k, v in results.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
