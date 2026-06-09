"""Compile strategy PDF text into enforceable Python rule checks via Claude API."""
import hashlib
import json
import logging
import os
import re
import threading
import time
from datetime import datetime

import requests

log = logging.getLogger("hub.strategy_compiler")

RULES_FILE = "data/compiled_rules.json"
CLAUDE_URL = "https://api.anthropic.com/v1/messages"
KEYS_FILE = "mytraderhub_keys.json"

_compile_lock = threading.Lock()
_compile_threads: dict[str, threading.Thread] = {}


def _read_json(path: str, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def _write_json(path: str, data) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


def _load_keys() -> dict:
    return _read_json(KEYS_FILE, {})


def _load_store() -> dict:
    return _read_json(RULES_FILE, {})


def _save_store(store: dict) -> None:
    _write_json(RULES_FILE, store)


def _user_entry(store: dict, user_id: str) -> dict:
    return store.setdefault(user_id, {
        "status": "idle",
        "updated_at": "",
        "error": "",
        "rules": [],
    })


def _claude_json(system: str, user_text: str) -> dict | list | None:
    keys = _load_keys()
    api_key = keys.get("anthropic_api_key", "")
    if not api_key:
        log.warning("anthropic_api_key missing in %s", KEYS_FILE)
        return None
    try:
        resp = requests.post(
            CLAUDE_URL,
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": keys.get("claude_model", "claude-sonnet-4-20250514"),
                "max_tokens": 4096,
                "system": system,
                "messages": [{"role": "user", "content": user_text}],
            },
            timeout=120,
        )
        if not resp.ok:
            log.warning("Claude API error %s: %s", resp.status_code, resp.text[:500])
            return None
        body = resp.json()
        blocks = body.get("content") or []
        text = "".join(b.get("text", "") for b in blocks if b.get("type") == "text")
        text = text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
        return json.loads(text)
    except Exception as exc:
        log.warning("Claude request failed: %s", exc)
        return None


_COMPILE_SYSTEM = """You extract enforceable trading rules from strategy document text.
Return ONLY a JSON array. Each element:
{
  "id": "snake_case_id",
  "text": "human readable rule",
  "field": "short field tag like risk|entry|exit|size",
  "check_code": "def check(item):\\n    # item is dict with ticker, side, entry_price, stop_loss, target, qty, risk_pct, setup_type, notes\\n    # return (True, '') if OK else (False, 'violation message')\\n    ..."
}
Write safe checks using only item dict access and basic math. No imports, no I/O."""


def compile_from_text(text: str, user_id: str = "default") -> dict:
    """Synchronously compile rules from strategy text. Updates JSON store."""
    store = _load_store()
    entry = _user_entry(store, user_id)
    entry["status"] = "compiling"
    entry["updated_at"] = datetime.now().isoformat(timespec="seconds")
    entry["error"] = ""
    _save_store(store)

    if not (text or "").strip():
        entry["status"] = "error"
        entry["error"] = "empty strategy text"
        _save_store(store)
        return {"ok": False, "error": entry["error"]}

    clipped = text[:120000]
    parsed = _claude_json(_COMPILE_SYSTEM, clipped)
    if not isinstance(parsed, list):
        entry["status"] = "error"
        entry["error"] = "compiler returned invalid response"
        _save_store(store)
        return {"ok": False, "error": entry["error"]}

    rules = []
    for i, raw in enumerate(parsed):
        if not isinstance(raw, dict):
            continue
        rid = str(raw.get("id") or f"rule_{i + 1}")
        rules.append({
            "id": rid,
            "text": str(raw.get("text") or rid),
            "field": str(raw.get("field") or "rule"),
            "enabled": True,
            "check_code": str(raw.get("check_code") or "def check(item):\n    return (True, '')"),
        })

    entry["rules"] = rules
    entry["status"] = "ready"
    entry["text_hash"] = hashlib.sha256(clipped.encode()).hexdigest()[:16]
    entry["updated_at"] = datetime.now().isoformat(timespec="seconds")
    entry["error"] = ""
    _save_store(store)
    return {"ok": True, "rule_count": len(rules)}


def trigger_compile_async(text: str, user_id: str = "default") -> dict:
    """Kick off background compilation; returns immediately."""
    with _compile_lock:
        t = _compile_threads.get(user_id)
        if t and t.is_alive():
            return {"ok": True, "status": "compiling"}

        def _worker():
            try:
                compile_from_text(text, user_id=user_id)
            except Exception as exc:
                log.exception("compile failed for %s: %s", user_id, exc)
                store = _load_store()
                entry = _user_entry(store, user_id)
                entry["status"] = "error"
                entry["error"] = str(exc)
                _save_store(store)

        thread = threading.Thread(target=_worker, daemon=True, name=f"compile-{user_id}")
        _compile_threads[user_id] = thread
        thread.start()
    return {"ok": True, "status": "compiling"}


def get_compiled_rules(user_id: str = "default") -> dict:
    store = _load_store()
    entry = _user_entry(store, user_id)
    return {
        "status": entry.get("status", "idle"),
        "updated_at": entry.get("updated_at", ""),
        "error": entry.get("error", ""),
        "rules": [
            {
                "id": r.get("id"),
                "text": r.get("text"),
                "field": r.get("field"),
                "enabled": bool(r.get("enabled", True)),
            }
            for r in entry.get("rules", [])
        ],
    }


def toggle_rule(rule_id: str, enabled: bool, user_id: str = "default") -> dict:
    store = _load_store()
    entry = _user_entry(store, user_id)
    found = False
    for r in entry.get("rules", []):
        if r.get("id") == rule_id:
            r["enabled"] = bool(enabled)
            found = True
            break
    if not found:
        return {"ok": False, "error": "rule not found"}
    entry["updated_at"] = datetime.now().isoformat(timespec="seconds")
    _save_store(store)
    return {"ok": True}


def _exec_check(check_code: str, item: dict) -> tuple[bool, str]:
    safe_builtins = {
        "abs": abs, "float": float, "int": int, "len": len,
        "max": max, "min": min, "round": round, "str": str,
    }
    ns: dict = {}
    try:
        exec(check_code, {"__builtins__": safe_builtins}, ns)
        fn = ns.get("check")
        if not callable(fn):
            return True, ""
        ok, msg = fn(item)
        if ok:
            return True, ""
        return False, str(msg or "rule violated")
    except Exception as exc:
        log.debug("rule check error: %s", exc)
        return False, f"check error: {exc}"


def run_checks(item: dict, user_id: str = "default") -> list[str]:
    """Return human-readable violation strings for a training queue item."""
    store = _load_store()
    entry = _user_entry(store, user_id)
    violations: list[str] = []
    for rule in entry.get("rules", []):
        if not rule.get("enabled", True):
            continue
        ok, msg = _exec_check(rule.get("check_code", ""), dict(item or {}))
        if not ok:
            label = rule.get("text") or rule.get("id") or "rule"
            violations.append(msg if msg and msg != "rule violated" else label)
    return violations
