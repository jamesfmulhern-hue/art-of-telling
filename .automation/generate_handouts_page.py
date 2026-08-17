#!/usr/bin/env python3
"""
Generates handouts.html — the clean public index of student-facing course
materials for The Art of Telling — from manifest.json.

Only entries in manifest.json are rendered. manifest.json is maintained by
sync_drive_to_site.py, which enforces the "student documents only" filter.
This script contains NO filtering logic itself — it only renders what it's given.
"""
import json
import os
import sys
from datetime import datetime, timezone

REPO_DIR = os.environ.get("AOT_REPO_DIR", "/home/user/workspace/art-of-telling")
MANIFEST_PATH = os.path.join(REPO_DIR, "handouts", "manifest.json")
OUTPUT_PATH = os.path.join(REPO_DIR, "handouts.html")

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Handouts &amp; Course Materials — The Art of Telling</title>
<meta name="description" content="The complete, current library of student handouts, worksheets, and companion booklets for The Art of Telling — a creative writing salon with James F. Mulhern.">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22%3E%3Crect width=%22100%22 height=%22100%22 fill=%22%230F2545%22/%3E%3Ctext x=%2250%22 y=%2266%22 text-anchor=%22middle%22 font-family=%22Georgia,serif%22 font-size=%2256%22 fill=%22%23C9B97E%22%3EA%3C/text%3E%3C/svg%3E">
<meta name="author" content="James F. Mulhern">
<meta name="keywords" content="The Art of Telling, creative writing salon handouts, course materials, student worksheets, memoir guide, poetry booklet, James F. Mulhern, Silver Current Press">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="https://art-of-telling.com/handouts.html">
<meta property="og:type" content="website">
<meta property="og:site_name" content="The Art of Telling — A Creative Writing Salon">
<meta property="og:title" content="Handouts &amp; Course Materials — The Art of Telling">
<meta property="og:description" content="The complete, current library of student handouts, worksheets, and companion booklets for The Art of Telling.">
<meta property="og:url" content="https://art-of-telling.com/handouts.html">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Handouts &amp; Course Materials — The Art of Telling">
<meta name="twitter:description" content="The complete, current library of student handouts, worksheets, and companion booklets for The Art of Telling.">
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebPage",
  "name": "Handouts \\u0026 Course Materials \\u2014 The Art of Telling",
  "description": "The complete, current library of student handouts, worksheets, and companion booklets for The Art of Telling.",
  "url": "https://art-of-telling.com/handouts.html",
  "isPartOf": {
    "@type": "WebSite",
    "name": "The Art of Telling \\u2014 A Creative Writing Salon",
    "url": "https://art-of-telling.com/"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Silver Current Press",
    "url": "https://silvercurrentpress.com"
  },
  "author": {
    "@type": "Person",
    "name": "James F. Mulhern",
    "url": "https://www.authorjamesmulhern.com"
  },
  "inLanguage": "en"
}
</script>
</head>
<body class="aot-inner" style="margin:0;background:#F8F4EA;">
<!-- return-to-salon ribbon -->
<div id="scp-return-ribbon" style="
  background: #10182E;
  color: #F8F1DD;
  text-align: center;
  padding: 10px 16px;
  font-family: system-ui, -apple-system, 'Segoe UI', sans-serif;
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 0.02em;
  border-bottom: 3px solid #6E4A0E;
  position: relative;
  z-index: 9999;
">
  <a href="https://salon.silvercurrentpress.com"
     style="color: #F8F1DD; text-decoration: none; display:inline-flex; align-items:center; gap:8px;"
     onmouseover="this.style.color='#F0D080'"
     onmouseout="this.style.color='#F8F1DD'">
    <span style="font-size:16px; line-height:1;">&#8592;</span>
    <span>Back to <strong style="color:#F0D080;">The 2601 Salon</strong></span>
  </a>
</div>
"""

# Everything between the ribbon and the closing </style> tag (the full house
# stylesheet) is copied verbatim from an existing simple page so visual
# language stays perfectly consistent. We inline it once here.
STYLE_LINK = '<link rel="stylesheet" href="css/styles.css">\n'

BODY_OPEN = """<div class="aot-back-bar"><a href="index.html">&larr; Back to Menu</a></div>
<main class="aot-main"><section class="aot-section" id="handouts-index">
  <div class="section-kicker">Course Library</div>
  <h2>Handouts &amp; Course Materials</h2>
  <div class="aot-orn"><span class="l"></span><span class="pip"></span><span class="pip-c"></span><span class="pip"></span><span class="l"></span></div>
  <p class="aot-lead">Every student handout, worksheet, and companion booklet currently assigned in The Art of Telling &mdash; kept up to date automatically as new materials are introduced. Instructor-only materials are not listed here.</p>
"""

BODY_CLOSE = """</section></main>
<div class="aot-back-bar"><a href="index.html">&larr; Back to Menu</a></div>
"""

FOOTER = """<footer class="aot-foot">
  <svg class="sun" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
    <g fill="none" stroke="#D4A82C" stroke-width="4">
      <circle cx="50" cy="50" r="14"/>
      <circle cx="50" cy="50" r="20" stroke-opacity=".8"/>
    </g>
    <g stroke="#D4A82C" stroke-width="4.5" stroke-linecap="round">
      <line x1="50" y1="6"  x2="50" y2="26"/>
      <line x1="50" y1="74" x2="50" y2="94"/>
      <line x1="6"  y1="50" x2="26" y2="50"/>
      <line x1="74" y1="50" x2="94" y2="50"/>
      <line x1="20" y1="20" x2="34" y2="34"/>
      <line x1="66" y1="66" x2="80" y2="80"/>
      <line x1="80" y1="20" x2="66" y2="34"/>
      <line x1="34" y1="66" x2="20" y2="80"/>
    </g>
    <g fill="#D4A82C"><circle cx="50" cy="50" r="6"/></g>
  </svg>
  <div class="signature">&mdash; The Art of Telling &mdash;</div>
  <h3>Your story matters. Come learn to tell it.</h3>
  <p>Ten sessions &nbsp;&middot;&nbsp; 90 minutes each &nbsp;&middot;&nbsp; In person or on Zoom</p>
  <p style="margin-top:14px">Presented by Silver Current Press &middot; Philadelphia</p>
  <div class="imprint" style="margin-top:18px;line-height:1.55">
    Silver Current Press &nbsp;&middot;&nbsp; Philadelphia<br>
    <span style="font-family:'Cormorant Garamond',serif;font-style:italic;font-weight:600;font-size:14px;letter-spacing:.04em;text-transform:none;color:#E8C547">
      A small literary imprint &mdash; fiction, poetry, and the art of the well-made book
    </span>
  </div>
  <div style="margin-top:24px;padding-top:18px;border-top:1px solid #A6831C;font-family:'Cormorant Garamond',serif;font-style:italic;font-size:13px;line-height:1.6;color:#E8C547;max-width:680px;margin-left:auto;margin-right:auto">
    <p style="margin:0">Course materials, lesson plans, discussion questions, and worksheets &copy; 2026 James Mulhern. All rights reserved.</p>
  </div>
</footer>
<div id="mulhern-gathering-room-bar" style="background:#F8F1DD;color:#1E2947;text-align:center;padding:10px 16px;font-family:Georgia,'EB Garamond',serif;font-size:13px;border-top:1px solid #d4c69e;">See James Mulhern&rsquo;s full body of work &mdash; fiction, courses, and publishing &mdash; in <a href="https://silvercurrentpress.com/elsewhere.html" style="color:#7B1F35;font-weight:600;text-decoration:none;">The Gathering Room &rarr;</a></div>
<script data-cfasync="false" src="/cdn-cgi/scripts/5c5dd728/cloudflare-static/email-decode.min.js"></script><script src="js/return-ribbon.js" defer></script>
</body>
</html>
"""


def session_sort_key(session_label):
    if session_label == "General / Course-Wide":
        return (0, 0)
    try:
        n = int(session_label.replace("Session ", "").strip())
        return (1, n)
    except ValueError:
        return (2, session_label)


def render_card(item):
    updated = item.get("published_date", "")
    updated_html = f'<span class="aot-handout-date" style="display:block;font-size:12px;color:#7A6A3A;margin-top:2px">Added {updated}</span>' if updated else ""
    return (
        f'<a class="aot-handout-link" href="handouts/{item["filename"]}" download>'
        f'<span class="aot-handout-icon" aria-hidden="true">PDF</span>'
        f'<span><strong>{item["title"]}</strong>{updated_html}</span>'
        f'</a>'
    )


def main():
    if not os.path.exists(MANIFEST_PATH):
        print(f"No manifest found at {MANIFEST_PATH}; nothing to render.")
        sys.exit(1)

    with open(MANIFEST_PATH) as f:
        manifest = json.load(f)

    items = manifest.get("published", [])

    # Group by session
    groups = {}
    for item in items:
        session = item.get("session", "General / Course-Wide")
        groups.setdefault(session, []).append(item)

    sections_html = []
    if not items:
        sections_html.append('<p class="aot-lead" style="font-style:italic">No materials have been published yet. Check back soon.</p>')
    else:
        for session in sorted(groups.keys(), key=session_sort_key):
            group_items = sorted(groups[session], key=lambda i: i["title"])
            cards = "\n        ".join(render_card(i) for i in group_items)
            sections_html.append(
                f'''<section class="aot-handouts" aria-label="{session} Handouts">
      <h4>{session}</h4>
      <div class="aot-handouts-list">
        {cards}
      </div>
    </section>'''
            )

    generated = datetime.now(timezone.utc).strftime("%B %-d, %Y") if os.name != "nt" else datetime.now(timezone.utc).strftime("%B %d, %Y")

    html = (
        HEAD
        + STYLE_LINK
        + BODY_OPEN
        + "\n  " + "\n  ".join(sections_html) + "\n"
        + f'  <p style="margin-top:24px;font-size:13px;color:#7A6A3A;text-align:center">Last updated {generated} &middot; updated automatically as new student materials are added.</p>\n'
        + BODY_CLOSE
        + FOOTER
    )

    with open(OUTPUT_PATH, "w") as f:
        f.write(html)

    print(f"Wrote {OUTPUT_PATH} with {len(items)} published item(s) across {len(groups)} group(s).")


if __name__ == "__main__":
    main()
