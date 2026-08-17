#!/usr/bin/env python3
"""
Reads new_publishes.json (written by sync_drive_to_site.py) and prints the
exact notion-create-pages payload needed to log each new/updated student
material into the "Media Kit Backlog" Notion database.

This script does NOT call Notion directly (no raw Notion API key is
configured in this environment) — it emits the payload for the calling
agent to pass to the notion-create-pages connector tool in one batch call.
This keeps the Notion write auditable and lets the connector's own auth
handle the request.

Usage: python3 log_to_notion.py
Prints a JSON payload to stdout; empty list if there's nothing new.
"""
import json
import os
import sys

NEW_PUBLISH_QUEUE_PATH = os.path.join(os.path.dirname(__file__), "new_publishes.json")
SITE_BASE_URL = "https://art-of-telling.com"
DATA_SOURCE_ID = "7e38a618-6e83-42ee-871f-ef887021d450"  # Media Kit Backlog


def build_payload():
    if not os.path.exists(NEW_PUBLISH_QUEUE_PATH):
        return {"pages": []}

    with open(NEW_PUBLISH_QUEUE_PATH) as f:
        new_items = json.load(f)

    pages = []
    for item in new_items:
        pages.append({
            "properties": {
                "Item": item["title"],
                "Session": item["session"],
                "Type": "Updated File" if item.get("was_update") else "New Publish",
                "date:Published Date:start": item["published_date"],
                "Live URL": f"{SITE_BASE_URL}/handouts/{item['filename']}",
                "Source File": item.get("drive_link", ""),
                "Status": "Done",
                "Notes": "Auto-published by the student materials sync workflow.",
            }
        })

    return {"parent": {"data_source_id": DATA_SOURCE_ID}, "pages": pages}


if __name__ == "__main__":
    payload = build_payload()
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    if not payload.get("pages"):
        sys.exit(0)
