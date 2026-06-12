"""MyTraderHub dashboard engine — Alpaca, AI, and data helpers."""
import calendar as _cal
import json
import logging
import os
import threading
import time
import uuid
from datetime import datetime, timedelta

import requests

from database_manager import DatabaseManager

log = logging.getLogger("hub.engine")

ALPACA_BASE = "https://paper-api.alpaca.markets"
ALPACA_DATA_BASE = "https://data.alpaca.markets"
ALERTS_FILE = "data/price_alerts.json"
KEYS_FILE = "mytraderhub_keys.json"

_cache: dict = {}
_cache_lock = threading.Lock()


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


def _alpaca_headers() -> dict:
    keys = _load_keys()
    return {
        "APCA-API-KEY-ID": keys.get("alpaca_key_id", ""),
        "APCA-API-SECRET-KEY": keys.get("alpaca_secret_key", ""),
    }


def _alpaca_get(path: str, params: dict | None = None):
    try:
        resp = requests.get(
            f"{ALPACA_BASE}{path}",
            headers=_alpaca_headers(),
            params=params or {},
            timeout=15,
        )
        if resp.ok:
            return resp.json()
    except Exception as exc:
        log.warning("Alpaca GET %s failed: %s", path, exc)
    return None


def _alpaca_post(path: str, payload: dict):
    try:
        resp = requests.post(
            f"{ALPACA_BASE}{path}",
            headers={**_alpaca_headers(), "Content-Type": "application/json"},
            json=payload,
            timeout=15,
        )
        if resp.ok:
            return resp.json()
        return {"error": resp.text, "status": resp.status_code}
    except Exception as exc:
        log.warning("Alpaca POST %s failed: %s", path, exc)
        return {"error": str(exc)}


def _alpaca_delete(path: str):
    try:
        resp = requests.delete(
            f"{ALPACA_BASE}{path}",
            headers=_alpaca_headers(),
            timeout=15,
        )
        return resp.ok
    except Exception as exc:
        log.warning("Alpaca DELETE %s failed: %s", path, exc)
        return False


def _alpaca_data_get(path: str, params: dict | None = None):
    try:
        resp = requests.get(
            f"{ALPACA_DATA_BASE}{path}",
            headers=_alpaca_headers(),
            params=params or {},
            timeout=15,
        )
        if resp.ok:
            return resp.json()
    except Exception as exc:
        log.warning("Alpaca data GET %s failed: %s", path, exc)
    return None


def _cached(key: str, ttl: int, fn):
    now = time.time()
    with _cache_lock:
        entry = _cache.get(key)
        if entry and now - entry["ts"] < ttl:
            return entry["val"]
    val = fn()
    with _cache_lock:
        _cache[key] = {"ts": now, "val": val}
    return val


def get_account() -> dict:
    data = _cached("account", 30, lambda: _alpaca_get("/v2/account") or {})
    if not isinstance(data, dict):
        return {}
    return {
        "portfolio_value": float(data.get("portfolio_value") or 0),
        "buying_power": float(data.get("buying_power") or 0),
        "cash": float(data.get("cash") or 0),
        "equity": float(data.get("equity") or 0),
        "daytrade_count": int(data.get("daytrade_count") or 0),
        "pattern_day_trader": bool(data.get("pattern_day_trader")),
        "status": data.get("status", ""),
    }


def get_home_data() -> dict:
    account = get_account()
    equity = account.get("equity", 0)
    last_equity = float(
        (_alpaca_get("/v2/account") or {}).get("last_equity") or equity
    )
    daily_pl = round(equity - last_equity, 2)
    daily_pl_pct = round(daily_pl / last_equity * 100, 2) if last_equity else 0
    return {
        "portfolio_value": account.get("portfolio_value", 0),
        "daily_pl": daily_pl,
        "daily_pl_pct": daily_pl_pct,
        "buying_power": account.get("buying_power", 0),
        "cash": account.get("cash", 0),
    }


def get_open_orders() -> list:
    data = _alpaca_get("/v2/orders", {"status": "open", "limit": 50})
    if not isinstance(data, list):
        return []
    return [
        {
            "id": o.get("id", ""),
            "symbol": o.get("symbol", ""),
            "side": o.get("side", ""),
            "qty": o.get("qty"),
            "type": o.get("type", ""),
            "limit_price": o.get("limit_price"),
            "status": o.get("status", ""),
        }
        for o in data
    ]


def cancel_alpaca_order(order_id: str) -> bool:
    return _alpaca_delete(f"/v2/orders/{order_id}")


def get_order_history(limit: int = 50) -> list:
    """Fetch filled/cancelled orders from Alpaca."""
    params = {"status": "all", "limit": limit, "direction": "desc"}
    data = _alpaca_get("/v2/orders", params)
    if not isinstance(data, list):
        return []
    orders = []
    for o in data:
        orders.append({
            "id": o.get("id", ""),
            "ticker": o.get("symbol", ""),
            "side": o.get("side", ""),
            "qty": o.get("qty") or o.get("notional") or "0",
            "qty_type": "notional" if o.get("notional") else "shares",
            "order_type": o.get("type", "market"),
            "status": o.get("status", ""),
            "filled_qty": o.get("filled_qty", "0"),
            "filled_avg": o.get("filled_avg_price") or "",
            "limit_price": o.get("limit_price") or "",
            "tif": o.get("time_in_force", ""),
            "created_at": o.get("created_at", "")[:10] if o.get("created_at") else "",
        })
    return orders


def get_ticker_news(ticker: str, limit: int = 5) -> list:
    data = _alpaca_data_get("/v1beta1/news", {
        "symbols": ticker.upper(),
        "limit": limit,
        "sort": "desc",
    })
    items = data if isinstance(data, list) else (data or {}).get("news", [])
    return [
        {
            "headline": i.get("headline", ""),
            "source": i.get("source", ""),
            "url": i.get("url", ""),
            "published": (i.get("created_at") or "")[:10],
            "summary": (i.get("summary") or "")[:180],
        }
        for i in (items or [])[:limit]
    ]


def get_calendar_data(year: int, month: int, user_id: str = "default") -> dict:
    """Trade data grouped by day for calendar view."""
    db = DatabaseManager()
    try:
        rows = db.get_decisions(user_id=user_id, limit=500)
    except Exception:
        rows = []

    days: dict[str, dict] = {}
    for r in rows:
        ts = (r.get("timestamp") or "")[:10]
        if not ts:
            continue
        try:
            y, m, _ = ts.split("-")
            if int(y) != year or int(m) != month:
                continue
        except Exception:
            continue
        entry = days.setdefault(ts, {
            "trade_count": 0, "pl_sum": 0.0, "wins": 0,
            "losses": 0, "pending": 0, "tickers": [],
        })
        entry["trade_count"] += 1
        outcome = (r.get("outcome") or "pending").lower()
        rm = float(r.get("r_multiple") or 0)
        entry["pl_sum"] = round(entry["pl_sum"] + rm, 2)
        if outcome == "win":
            entry["wins"] += 1
        elif outcome == "loss":
            entry["losses"] += 1
        else:
            entry["pending"] += 1
        ticker = r.get("ticker", "")
        if ticker and ticker not in entry["tickers"]:
            entry["tickers"].append(ticker)

    clean_days: dict[str, dict] = {}
    for ts, d in days.items():
        if d["wins"] > 0 and d["losses"] == 0:
            outcome = "win"
        elif d["losses"] > 0 and d["wins"] == 0:
            outcome = "loss"
        elif d["wins"] > 0 and d["losses"] > 0:
            outcome = "mixed"
        else:
            outcome = "pending"
        clean_days[ts] = {
            "trade_count": d["trade_count"],
            "pl_sum": d["pl_sum"],
            "outcome": outcome,
            "tickers": d["tickers"],
        }

    total_trades = sum(d["trade_count"] for d in clean_days.values())
    total_wins = sum(days[ts]["wins"] for ts in clean_days)
    win_rate = round(total_wins / total_trades * 100, 1) if total_trades else 0
    month_pl = round(sum(d["pl_sum"] for d in clean_days.values()), 2)

    return {
        "year": year,
        "month": month,
        "days": clean_days,
        "month_pl": month_pl,
        "win_rate": win_rate,
        "total_trades": total_trades,
    }


def get_day_trades(date_str: str, user_id: str = "default") -> list:
    """All trades for a specific YYYY-MM-DD date."""
    db = DatabaseManager()
    try:
        rows = db.get_decisions(user_id=user_id, limit=500)
    except Exception:
        rows = []
    return [r for r in rows if (r.get("timestamp") or "")[:10] == date_str]


def _load_alerts() -> list:
    return _read_json(ALERTS_FILE, [])


def _save_alerts(alerts: list) -> None:
    _write_json(ALERTS_FILE, alerts)


def get_alerts(user_id: str = "default") -> list:
    return [a for a in _load_alerts() if a.get("user_id") == user_id]


def save_alert(ticker: str, target_price: float, direction: str,
               user_id: str = "default") -> dict:
    alerts = _load_alerts()
    alert = {
        "id": str(uuid.uuid4())[:8],
        "user_id": user_id,
        "ticker": ticker.upper(),
        "target_price": round(float(target_price), 2),
        "direction": direction,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "triggered": False,
    }
    alerts.append(alert)
    _save_alerts(alerts)
    return {"ok": True, "alert_id": alert["id"], "alert": alert}


def delete_alert(alert_id: str, user_id: str = "default") -> bool:
    alerts = _load_alerts()
    before = len(alerts)
    alerts = [a for a in alerts if not (a["id"] == alert_id and a.get("user_id") == user_id)]
    if len(alerts) < before:
        _save_alerts(alerts)
        return True
    return False


def check_alerts_against_prices(prices: dict) -> list:
    """prices = {ticker: current_price}. Returns list of triggered alert dicts."""
    alerts = _load_alerts()
    triggered = []
    remaining = []
    for a in alerts:
        price = prices.get(a["ticker"])
        if price is None:
            remaining.append(a)
            continue
        hit = (a["direction"] == "above" and price >= a["target_price"]) or \
              (a["direction"] == "below" and price <= a["target_price"])
        if hit:
            a["triggered_price"] = price
            triggered.append(a)
        else:
            remaining.append(a)
    if triggered:
        _save_alerts(remaining)
    return triggered


def get_market_bar() -> list:
    symbols = ["SPY", "QQQ", "IWM", "VIXY"]
    results = []
    for sym in symbols:
        snap = _alpaca_get(f"/v2/stocks/{sym}/snapshot")
        label = "VIX" if sym == "VIXY" else sym
        if snap and snap.get("latestTrade"):
            price = float(snap["latestTrade"].get("p", 0) or 0)
            prev = float((snap.get("prevDailyBar") or {}).get("c", price) or price)
            chg = round((price - prev) / prev * 100, 2) if prev else 0
            results.append({"symbol": label, "price": price, "change_pct": chg})
        else:
            results.append({"symbol": label, "price": 0, "change_pct": 0})
    return results


USAGE_FILE = "data/usage.json"

PLAN_LIMITS = {
    "free": {
        "label": "Free",
        "ai_chats": 25,
        "price_alerts": 10,
        "ai_analyses": 15,
        "watchlist_tickers": 20,
    },
    "pro": {
        "label": "Pro",
        "ai_chats": 500,
        "price_alerts": 100,
        "ai_analyses": 200,
        "watchlist_tickers": 100,
    },
}


def _load_usage(user_id: str) -> dict:
    all_usage = _read_json(USAGE_FILE, {})
    return all_usage.get(user_id, {
        "plan": "free",
        "ai_chats": 0,
        "price_alerts": 0,
        "ai_analyses": 0,
        "watchlist_tickers": 0,
    })


def _save_usage(user_id: str, usage: dict) -> None:
    all_usage = _read_json(USAGE_FILE, {})
    all_usage[user_id] = usage
    _write_json(USAGE_FILE, all_usage)


def get_plan_usage(user_id: str = "default") -> dict:
    usage = _load_usage(user_id)
    plan_key = usage.get("plan", "free")
    limits = PLAN_LIMITS.get(plan_key, PLAN_LIMITS["free"])
    alert_count = len(get_alerts(user_id=user_id))

    metrics = [
        {
            "key": "ai_chats",
            "label": "AI Chats",
            "used": int(usage.get("ai_chats", 0)),
            "limit": limits["ai_chats"],
        },
        {
            "key": "ai_analyses",
            "label": "AI Analyses",
            "used": int(usage.get("ai_analyses", 0)),
            "limit": limits["ai_analyses"],
        },
        {
            "key": "price_alerts",
            "label": "Price Alerts",
            "used": alert_count,
            "limit": limits["price_alerts"],
        },
        {
            "key": "watchlist_tickers",
            "label": "Watchlist",
            "used": int(usage.get("watchlist_tickers", 0)),
            "limit": limits["watchlist_tickers"],
        },
    ]
    for m in metrics:
        m["pct"] = round(min(m["used"] / m["limit"], 1) * 100, 1) if m["limit"] else 0

    return {
        "plan": plan_key,
        "plan_label": limits["label"],
        "renewal": "Monthly",
        "metrics": metrics,
    }


def increment_usage(user_id: str, key: str, amount: int = 1) -> None:
    usage = _load_usage(user_id)
    usage[key] = int(usage.get(key, 0)) + amount
    _save_usage(user_id, usage)


def place_simple_order(symbol: str, side: str, qty: float, order_type: str = "market",
                       limit_price: float | None = None) -> dict:
    payload = {
        "symbol": symbol.upper(),
        "qty": str(qty),
        "side": side.lower(),
        "type": order_type,
        "time_in_force": "day",
    }
    if order_type == "limit" and limit_price:
        payload["limit_price"] = str(limit_price)
    return _alpaca_post("/v2/orders", payload) or {"error": "order failed"}
