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
TRAINING_QUEUE_FILE = "data/training_queue.json"
STRATEGY_PDFS_FILE = "data/strategy_pdfs.json"
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
            "unrealized_pl": 0.0,
            "has_open": False,
        }

    def _blank_day():
        return {
            "trade_count": 0, "pl_sum": 0.0, "outcome": "pending",
            "tickers": [], "unrealized_pl": 0.0, "has_open": False,
        }

    def _add_open_day(day_key: str, sym: str, upl: float) -> None:
        if not day_key.startswith(f"{year}-{month:02d}"):
            return
        target = clean_days.setdefault(day_key, _blank_day())
        target["has_open"] = True
        target["unrealized_pl"] = round(target.get("unrealized_pl", 0) + upl, 2)
        if sym not in target["tickers"]:
            target["tickers"].append(sym)

    entry_dates = _position_entry_dates()
    today = datetime.now().strftime("%Y-%m-%d")
    for pos in get_positions():
        sym = (pos.get("symbol") or "").upper()
        if not sym:
            continue
        entry = entry_dates.get(sym, today)
        upl = float(pos.get("unrealized_pl") or 0)
        _add_open_day(entry, sym, upl)
        if today != entry:
            _add_open_day(today, sym, upl)

    total_trades = sum(d["trade_count"] for d in clean_days.values())
    total_wins = sum(days[ts]["wins"] for ts in clean_days if ts in days)
    win_rate = round(total_wins / total_trades * 100, 1) if total_trades else 0
    month_pl = round(sum(d["pl_sum"] for d in clean_days.values()), 2)
    month_unrealized = round(sum(d.get("unrealized_pl", 0) for d in clean_days.values()), 2)

    return {
        "year": year,
        "month": month,
        "days": clean_days,
        "month_pl": month_pl,
        "month_unrealized": month_unrealized,
        "win_rate": win_rate,
        "total_trades": total_trades,
        "open_positions": get_positions(),
    }


def get_day_trades(date_str: str, user_id: str = "default") -> list:
    """All trades for a specific YYYY-MM-DD date, including open positions."""
    db = DatabaseManager()
    try:
        rows = db.get_decisions(user_id=user_id, limit=500)
    except Exception:
        rows = []
    trades = [r for r in rows if (r.get("timestamp") or "")[:10] == date_str]

    today = datetime.now().strftime("%Y-%m-%d")
    entry_dates = _position_entry_dates()
    for pos in get_positions():
        sym = (pos.get("symbol") or "").upper()
        entry = entry_dates.get(sym, today)
        if entry != date_str and date_str != today:
            continue
        if any(t.get("ticker", "").upper() == sym and t.get("is_open") for t in trades):
            continue
        trades.append({
            "ticker": sym,
            "outcome": "open",
            "r_multiple": 0,
            "entry_price": pos.get("entry_price"),
            "exit_price": None,
            "setup_type": f"{(pos.get('side') or '').upper()} · open",
            "is_open": True,
            "unrealized_pl": pos.get("unrealized_pl"),
            "qty": pos.get("qty"),
            "side": pos.get("side"),
        })
    return trades


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


def get_positions() -> list:
    """Open Alpaca positions with unrealized P&L."""
    data = _alpaca_get("/v2/positions")
    if not isinstance(data, list):
        return []
    positions = []
    for p in data:
        qty = float(p.get("qty") or 0)
        side = "short" if qty < 0 else "long"
        positions.append({
            "symbol": p.get("symbol", ""),
            "qty": abs(qty),
            "side": side,
            "entry_price": float(p.get("avg_entry_price") or 0),
            "current_price": float(p.get("current_price") or 0),
            "market_value": float(p.get("market_value") or 0),
            "cost_basis": float(p.get("cost_basis") or 0),
            "unrealized_pl": round(float(p.get("unrealized_pl") or 0), 2),
            "unrealized_plpc": round(float(p.get("unrealized_plpc") or 0) * 100, 2),
        })
    return positions


def _position_entry_dates() -> dict[str, str]:
    """Best-effort entry date per symbol from recent filled orders."""
    params = {"status": "filled", "limit": 200, "direction": "desc"}
    data = _alpaca_get("/v2/orders", params)
    if not isinstance(data, list):
        return {}
    dates: dict[str, str] = {}
    for o in reversed(data):
        sym = (o.get("symbol") or "").upper()
        if not sym or sym in dates:
            continue
        ts = o.get("filled_at") or o.get("created_at") or ""
        if ts:
            dates[sym] = ts[:10]
    return dates


def get_training_queue(user_id: str = "default") -> list:
    items = _read_json(TRAINING_QUEUE_FILE, [])
    return [i for i in items if i.get("user_id", "default") == user_id]


def save_training_queue_item(item: dict, user_id: str = "default") -> dict:
    items = _read_json(TRAINING_QUEUE_FILE, [])
    item = dict(item)
    item["user_id"] = user_id
    item.setdefault("id", str(uuid.uuid4())[:8])
    item.setdefault("created_at", datetime.now().strftime("%Y-%m-%d %H:%M"))
    items.insert(0, item)
    _write_json(TRAINING_QUEUE_FILE, items)
    return item


def _register_strategy_pdf_file(filename: str, text: str, user_id: str = "default") -> dict:
    """Persist extracted PDF text and trigger async rule compilation."""
    import strategy_compiler as sc

    pdfs = _read_json(STRATEGY_PDFS_FILE, [])
    entry = {
        "id": str(uuid.uuid4())[:8],
        "user_id": user_id,
        "filename": filename,
        "text_chars": len(text or ""),
        "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    pdfs = [p for p in pdfs if p.get("user_id") != user_id]
    pdfs.insert(0, entry)
    _write_json(STRATEGY_PDFS_FILE, pdfs)

    text_path = f"data/strategy_text_{user_id}.txt"
    os.makedirs("data", exist_ok=True)
    with open(text_path, "w", encoding="utf-8") as f:
        f.write(text or "")

    sc.trigger_compile_async(text, user_id=user_id)
    return {"ok": True, "pdf_id": entry["id"]}


def get_strategy_text(user_id: str = "default") -> str:
    path = f"data/strategy_text_{user_id}.txt"
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def export_trades_csv(user_id: str = "default") -> str:
    """Alpaca-compatible FILL activity CSV (brokerage import format)."""
    params = {"activity_types": "FILL", "direction": "desc", "page_size": 500}
    data = _alpaca_get("/v2/account/activities", params)
    if not isinstance(data, list):
        data = []

    db = DatabaseManager()
    try:
        decisions = db.get_decisions(user_id=user_id, limit=500)
    except Exception:
        decisions = []

    lines = [
        "Date,Time,Symbol,Description,Action,Quantity,Price,Commission,Net Amount,Order ID",
    ]

    for act in data:
        ts = act.get("transaction_time") or act.get("date") or ""
        date_part = ts[:10] if ts else ""
        time_part = ts[11:19] if len(ts) > 11 else ""
        sym = act.get("symbol", "")
        side = (act.get("side") or "").upper()
        action = "BUY" if side == "BUY" else "SELL" if side == "SELL" else side
        qty = act.get("qty") or act.get("cum_qty") or "0"
        price = act.get("price") or "0"
        order_id = act.get("order_id") or act.get("id") or ""
        net = round(float(qty) * float(price), 2) if qty and price else ""
        lines.append(
            f"{date_part},{time_part},{sym},,{action},{qty},{price},0,{net},{order_id}"
        )

    seen = {(act.get("symbol", ""), (act.get("transaction_time") or "")[:10]) for act in data}
    for d in decisions:
        ts = (d.get("timestamp") or "")[:10]
        sym = d.get("ticker", "")
        if (sym, ts) in seen:
            continue
        entry = d.get("entry_price")
        exit_p = d.get("exit_price")
        if entry is not None:
            lines.append(f"{ts},,{sym},Journal Entry,BUY,1,{entry},0,{entry},")
        if exit_p is not None and d.get("outcome") in ("win", "loss"):
            lines.append(f"{ts},,{sym},Journal Exit,SELL,1,{exit_p},0,{exit_p},")

    return "\n".join(lines) + "\n"
