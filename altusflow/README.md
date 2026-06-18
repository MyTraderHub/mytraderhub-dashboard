# AltusFlow.ai — Project Index

**Start here.** This folder contains the landing page, chatbot, and sales docs for AltusFlow.ai.

> These files belong in your **`AltusFlow-ai/AltusFlow.ai`** repository — not in MyTraderHub. Copy or merge this entire `altusflow/` folder into your local AltusFlow repo.

---

## Where to find everything

| What you need | Path |
|---------------|------|
| **Landing page** | `website/index.html` |
| **Chat assistant** | `website/chatbot.js` |
| **ICP & qualification rules** | `docs/sales/ICP_Guidelines.md` |
| **Sales positioning & objections** | `docs/sales/Sales_Strategy.md` |
| **Lead sourcing agent prompt** | `docs/prompts/lead-sourcing-specialist.md` |

---

## Folder layout

```
altusflow/                          ← merge this into your AltusFlow repo
├── README.md                       ← this file (project index)
├── website/
│   ├── index.html                  ← open in browser to preview
│   └── chatbot.js
└── docs/
    ├── sales/
    │   ├── ICP_Guidelines.md
    │   └── Sales_Strategy.md
    └── prompts/
        └── lead-sourcing-specialist.md
```

If your AltusFlow repo already has other docs, place this alongside them:

```
your-altusflow-repo/
├── website/          ← landing page lives here
├── docs/
│   ├── sales/        ← ICP + strategy (add next to your other docs)
│   └── prompts/
└── ...your other docs...
```

---

## Preview the website

From your repo root:

```bash
python3 -m http.server 8080
```

Open: **http://localhost:8080/website/index.html**  
(if merged at repo root)

Or: **http://localhost:8080/altusflow/website/index.html**  
(if still inside mytraderhub-dashboard during transition)

---

## Cursor references

```
@website/index.html
@docs/sales/ICP_Guidelines.md
@docs/sales/Sales_Strategy.md
@docs/prompts/lead-sourcing-specialist.md
```

---

## Move to your AltusFlow repository

See `MOVE_TO_ALTUSFLOW_REPO.md` for step-by-step instructions.
