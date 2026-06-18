# ⚠️ READ THIS FIRST

Your **pinned "altusflow" folder** is on **your computer**.  
This Cloud Agent writes to **mytraderhub-dashboard** — run the command below to copy files into your pinned folder.

---

## Put files in your pinned altusflow folder

1. Right-click your pinned **altusflow** folder → **Open in Integrated Terminal**
2. Run:

```bash
curl -fsSL https://raw.githubusercontent.com/MyTraderHub/mytraderhub-dashboard/cursor/agency-landing-page-8cad/altusflow/sync-to-your-altusflow-folder.sh | bash
```

3. Refresh file explorer — you should see:

```
altusflow/
├── index.html       ← landing page
├── chatbot.js       ← chat assistant
└── docs/
    ├── sales/
    └── prompts/
```

## Preview

```bash
python3 -m http.server 8080
```

Open: http://localhost:8080/index.html
