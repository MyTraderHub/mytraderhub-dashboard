# ⚠️ READ THIS FIRST

Your **pinned "altusflow" folder** lives on **your computer**.  
This Cloud Agent runs inside **mytraderhub-dashboard** — a different project.  
That is why you do not see files in your pinned folder yet.

---

## Fix it in 30 seconds

### Step 1 — Open your pinned altusflow folder in terminal

In Cursor:
1. Find **altusflow** in your pinned top folders
2. Right-click it → **Open in Integrated Terminal**

### Step 2 — Run this one command

```bash
curl -fsSL https://raw.githubusercontent.com/MyTraderHub/mytraderhub-dashboard/cursor/agency-landing-page-8cad/altusflow/sync-to-your-altusflow-folder.sh | bash
```

### Step 3 — Refresh the file explorer

Press `Cmd+Shift+E` / `Ctrl+Shift+E` — you should now see:

```
your-pinned-altusflow/
├── website/
│   ├── index.html       ← landing page
│   └── chatbot.js       ← chat assistant
└── docs/
    ├── sales/
    └── prompts/
```

---

## For future Cloud Agent work

To have the agent write **directly** into your altusflow folder:

1. In Cursor, open **File → Open Folder**
2. Select your local **AltusFlow.ai** repo (or pinned altusflow folder)
3. Run the Cloud Agent from **that** project — not mytraderhub-dashboard

Or connect it to GitHub: https://github.com/AltusFlow-ai/AltusFlow.ai

---

## Preview the website (after sync)

```bash
python3 -m http.server 8080
```

Open: http://localhost:8080/website/index.html
