"""Telegram notification helper."""
import logging
import os

import requests

log = logging.getLogger("hub.notify")


def send_alert(message: str) -> bool:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    if not token or not chat_id:
        log.debug("Telegram not configured, skipping alert: %s", message[:80])
        return False
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": message},
            timeout=10,
        )
        return resp.ok
    except Exception as exc:
        log.warning("Telegram send failed: %s", exc)
        return False
