#!/usr/bin/env bash
# Run FROM your pinned "altusflow" folder on your computer.
#
# curl -fsSL https://raw.githubusercontent.com/MyTraderHub/mytraderhub-dashboard/cursor/agency-landing-page-8cad/altusflow/sync-to-your-altusflow-folder.sh | bash
set -euo pipefail

BRANCH="cursor/agency-landing-page-8cad"
REPO="MyTraderHub/mytraderhub-dashboard"
BASE="https://raw.githubusercontent.com/${REPO}/${BRANCH}/altusflow"

echo ""
echo "▸ AltusFlow sync — installing into: $(pwd)"
echo ""

mkdir -p docs/sales docs/prompts

download() {
  local remote_path="$1"
  local local_path="$2"
  echo "  ↓ ${local_path}"
  curl -fsSL "${BASE}/${remote_path}" -o "${local_path}"
}

download "index.html"                              "index.html"
download "chatbot.js"                              "chatbot.js"
download "docs/sales/ICP_Guidelines.md"            "docs/sales/ICP_Guidelines.md"
download "docs/sales/Sales_Strategy.md"             "docs/sales/Sales_Strategy.md"
download "docs/prompts/lead-sourcing-specialist.md" "docs/prompts/lead-sourcing-specialist.md"
download "README.md"                               "README.md"

echo ""
echo "✓ Done! In your altusflow folder:"
echo ""
echo "  index.html          ← landing page"
echo "  chatbot.js          ← chat assistant"
echo "  docs/sales/"
echo "  docs/prompts/"
echo ""
echo "Preview:  python3 -m http.server 8080 → http://localhost:8080/index.html"
echo ""
