#!/usr/bin/env bash
# Art of Telling — Student Materials Auto-Publish
# End-to-end pipeline, meant to be invoked on a schedule (cron):
#   1. Sync new/updated student-facing PDFs from the "Art of Telling" Drive folder
#   2. Regenerate the public handouts.html index
#   3. Fill any still-empty per-session handout marker blocks
#   4. Commit + push to GitHub if anything changed
#   5. Print the Notion "Media Kit Backlog" payload for the calling agent to log
#
# Nothing is pushed and no Notion payload is produced if there's nothing new.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="${AOT_REPO_DIR:-/home/user/workspace/art-of-telling}"

echo "== 1/5 Syncing Drive -> local handouts =="
python3 "$SCRIPT_DIR/sync_drive_to_site.py"

NEW_COUNT=$(python3 -c "import json; print(len(json.load(open('$SCRIPT_DIR/new_publishes.json'))))")

if [ "$NEW_COUNT" = "0" ]; then
  echo "No new or updated student materials. Nothing to publish. Exiting."
  exit 0
fi

echo "== 2/5 Regenerating handouts.html =="
python3 "$SCRIPT_DIR/generate_handouts_page.py"

echo "== 3/5 Filling empty per-session marker blocks =="
python3 "$SCRIPT_DIR/inject_session_markers.py"

echo "== 4/5 Committing (local) to git =="
cd "$REPO_DIR"
git add -A
if git diff --cached --quiet; then
  echo "No file changes to commit (unexpected, but nothing to do)."
else
  git config user.email "jamesfmulhern@gmail.com" || true
  git config user.name "James F. Mulhern" || true
  git commit -m "Auto-publish new student course materials

$(python3 -c "
import json
items = json.load(open('$SCRIPT_DIR/new_publishes.json'))
for i in items:
    print(f\"- {i['title']} ({i['session']})\")
")"
  echo "Committed locally. NOTE: this script does NOT push — the calling"
  echo "agent must run 'git fetch/rebase/push' itself as a direct bash call"
  echo "with github credentials attached, since credentials do not"
  echo "propagate into this nested script."
fi

echo "== 5/5 Notion backlog payload =="
python3 "$SCRIPT_DIR/log_to_notion.py" > "$SCRIPT_DIR/notion_payload.json"
cat "$SCRIPT_DIR/notion_payload.json"
echo ""
echo "NOTE: the agent running this script must pass notion_payload.json's"
echo "contents to the notion-create-pages tool to complete the backlog log."
