# Move AltusFlow files to your AltusFlow repository

Your website and docs currently live in **mytraderhub-dashboard** under `altusflow/`. They should live in **`AltusFlow-ai/AltusFlow.ai`** alongside your other docs.

---

## Option A — Copy into an existing local AltusFlow folder (recommended)

If you already have a local folder with AltusFlow docs:

### 1. Clone or open your AltusFlow repo

```bash
git clone https://github.com/AltusFlow-ai/AltusFlow.ai.git
cd AltusFlow.ai
```

### 2. Copy the website and docs folders

From wherever you have the mytraderhub-dashboard clone:

```bash
# Copy website
cp -r path/to/mytraderhub-dashboard/altusflow/website ./

# Copy sales docs (merge into your existing docs/ if you have one)
mkdir -p docs/sales docs/prompts
cp path/to/mytraderhub-dashboard/altusflow/docs/sales/* docs/sales/
cp path/to/mytraderhub-dashboard/altusflow/docs/prompts/* docs/prompts/

# Optional: copy the index README
cp path/to/mytraderhub-dashboard/altusflow/README.md ./ALTUSFLOW_WEBSITE_INDEX.md
```

### 3. Commit and push

```bash
git add website/ docs/
git commit -m "Add landing page, chatbot, and sales docs"
git push origin main
```

---

## Option B — Pull from the mytraderhub branch

```bash
cd AltusFlow.ai
git remote add dashboard https://github.com/MyTraderHub/mytraderhub-dashboard.git
git fetch dashboard cursor/agency-landing-page-8cad
git checkout dashboard/cursor/agency-landing-page-8cad -- altusflow/
# Then move altusflow/website and altusflow/docs to repo root as shown above
```

---

## After moving — where to find files

| File | Location in your AltusFlow repo |
|------|--------------------------------|
| Landing page | `website/index.html` |
| Chatbot | `website/chatbot.js` |
| ICP guidelines | `docs/sales/ICP_Guidelines.md` |
| Sales strategy | `docs/sales/Sales_Strategy.md` |
| Lead sourcing prompt | `docs/prompts/lead-sourcing-specialist.md` |

---

## In Cursor

1. **File → Open Folder** → select your local `AltusFlow.ai` folder (not mytraderhub-dashboard).
2. Press `Cmd+P` / `Ctrl+P` and type `website/index.html`.
3. Your other docs and the website will all be in one workspace.
