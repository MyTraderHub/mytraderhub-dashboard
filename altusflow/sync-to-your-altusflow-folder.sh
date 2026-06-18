#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# Run this script FROM your pinned "altusflow" folder on your computer.
#
# In Cursor: right-click your pinned altusflow folder → "Open in Integrated Terminal"
# Then run:
#   curl -fsSL https://raw.githubusercontent.com/MyTraderHub/mytraderhub-dashboard/cursor/agency-landing-page-8cad/altusflow/sync-to-your-altusflow-folder.sh | bash
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

BRANCH="cursor/agency-landing-page-8cad"
REPO="MyTraderHub/mytraderhub-dashboard"
BASE="https://raw.githubusercontent.com/${REPO}/${BRANCH}/altusflow"

echo ""
echo "▸ AltusFlow sync — installing into: $(pwd)"
echo ""

mkdir -p website docs/sales docs/prompts

download() {
  local remote_path="$1"
  local local_path="$2"
  echo "  ↓ ${local_path}"
  curl -fsSL "${BASE}/${remote_path}" -o "${local_path}"
}

download "website/index.html"                    "website/index.html"
download "website/chatbot.js"                    "website/chatbot.js"
download "website/README.md"                       "website/README.md"
download "docs/sales/ICP_Guidelines.md"          "docs/sales/ICP_Guidelines.md"
download "docs/sales/Sales_Strategy.md"           "docs/sales/Sales_Strategy.md"
download "docs/prompts/lead-sourcing-specialist.md" "docs/prompts/lead-sourcing-specialist.md"
download "README.md"                             "WEBSITE_AND_DOCS_INDEX.md"

echo ""
echo "✓ Done! Your pinned altusflow folder now has:"
echo ""
echo "  website/index.html          ← landing page"
echo "  website/chatbot.js          ← chat assistant"
echo "  docs/sales/                 ← ICP + sales strategy"
echo "  docs/prompts/               ← lead sourcing prompt"
echo ""
echo "Preview:  python3 -m http.server 8080"
echo "          → http://localhost:8080/website/index.html"
echo ""
echo "Commit to your AltusFlow repo:"
echo "  git add website/ docs/ WEBSITE_AND_DOCS_INDEX.md"
echo "  git commit -m 'Add landing page, chatbot, and sales docs'"
echo "  git push"
echo ""
