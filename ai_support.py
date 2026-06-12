"""MyTraderHub AI support assistant."""
import logging
import os
import re

import requests

from secrets_manager import get_secret

log = logging.getLogger("hub.ai_support")

SYSTEM_PROMPT = """You are MyTraderHub Support, a helpful trading dashboard assistant.
You help users with: portfolio overview, watchlists, price alerts, trade journal/calendar,
paper trading via Alpaca, order placement, and account questions.
Keep answers concise (2-4 sentences), friendly, and actionable. Do not give specific financial advice.
If unsure, suggest using the in-app features or checking Alpaca paper trading docs."""

FAQ_HINTS = [
    (r"\b(alerts?|price alerts?)\b", "Set price alerts from the Watchlist: tap a ticker, choose Above/Below, enter a target price, and tap Set. Alerts run in the background and can notify you via Telegram if configured."),
    (r"\b(watchlist|watch)\b", "Open Watch from the bottom nav to search tickers, view live quotes, read news, and set alerts. Tap any row for the detail sheet."),
    (r"\b(calendar|journal|trade journal)\b", "The Journal tab shows your trade calendar with daily P/L dots. Tap a day with trades to see details. Summary stats appear below the grid."),
    (r"\b(order|buy|sell|cancel)\b", "View open orders and history on the Account page. Cancel open orders with the Cancel button. Use the watchlist sheet for quick buy/sell entry."),
    (r"\b(account|portfolio|equity|buying power)\b", "Account shows portfolio value, cash, buying power, day trade count, and PDT status from your linked Alpaca paper account."),
    (r"\b(plan|usage|limit|subscription)\b", "Your plan and usage limits are on Settings. Free tier includes daily AI chats and alerts; upgrade for higher limits."),
    (r"\b(connect|alpaca|api|key)\b", "Link Alpaca paper keys in mytraderhub_keys.json on the server, or set APCA_API_KEY_ID and APCA_API_SECRET_KEY in the environment."),
    (r"\b(login|sign)\b", "Sign in from the login page with your Telegram user id. Sessions stay active until you clear cookies."),
]


def _fallback_reply(message: str, history: list | None = None) -> str:
    text = (message or "").strip().lower()
    if not text:
        return "Hi! I'm the MyTraderHub AI assistant. Ask me about watchlists, alerts, orders, or your journal."

    for pattern, answer in FAQ_HINTS:
        if re.search(pattern, text):
            return answer

    greetings = ("hi", "hello", "hey", "help")
    if text in greetings or any(text.startswith(g + " ") for g in greetings):
        return (
            "Hello! I can help with watchlists, price alerts, the trade journal, "
            "account balances, and orders. What would you like to know?"
        )

    return (
        "I'm here to help with MyTraderHub features — watchlists, alerts, journal, and account. "
        "Try asking about a specific feature, or open Help & Support above for step-by-step guides."
    )


def _openai_reply(message: str, history: list | None = None) -> str | None:
    api_key = get_secret("OPENAI_API_KEY")
    if not api_key:
        return None

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for item in (history or [])[-8:]:
        role = item.get("role", "user")
        content = (item.get("content") or "").strip()
        if role in ("user", "assistant") and content:
            messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": message})

    try:
        resp = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": get_secret("OPENAI_MODEL", "gpt-4o-mini"),
                "messages": messages,
                "max_tokens": 300,
                "temperature": 0.4,
            },
            timeout=30,
        )
        if resp.ok:
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()
        log.warning("OpenAI chat failed: %s", resp.text[:200])
    except Exception as exc:
        log.warning("OpenAI request error: %s", exc)
    return None


def chat(message: str, history: list | None = None) -> dict:
    text = (message or "").strip()
    if not text:
        return {"ok": False, "error": "message required"}

    reply = _openai_reply(text, history) or _fallback_reply(text, history)
    return {"ok": True, "reply": reply, "bot": "MyTraderHub AI"}
