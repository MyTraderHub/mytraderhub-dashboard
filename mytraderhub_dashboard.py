"""MyTraderHub Flask dashboard application."""
import logging
import os
import threading
from datetime import datetime
from functools import wraps

from flask import Flask, jsonify, redirect, render_template, request, session, url_for

import dashboard_engine as de
from alerts_monitor import run_alerts_monitor

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("hub.dashboard")

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("authenticated"):
            if request.path.startswith("/api/"):
                return jsonify({"ok": False, "error": "unauthorized"}), 401
            return redirect(url_for("page_login"))
        return f(*args, **kwargs)
    return decorated


@app.route("/login", methods=["GET", "POST"])
def page_login():
    if request.method == "POST":
        session["authenticated"] = True
        session["tg_user_id"] = request.form.get("user_id", "default")
        return redirect(url_for("page_home"))
    return render_template("login.html", page="login")


@app.route("/")
@require_auth
def page_home():
    return render_template("home.html", page="home")


@app.route("/watchlist")
@require_auth
def page_watchlist():
    return render_template("watchlists.html", page="watchlist")


@app.route("/account")
@require_auth
def page_account():
    return render_template("account.html", page="account")


@app.route("/calendar")
@require_auth
def page_calendar():
    return render_template("calendar.html", page="calendar")


@app.route("/api/account")
@require_auth
def api_account():
    return jsonify({"ok": True, **de.get_account()})


@app.route("/api/home")
@require_auth
def api_home():
    return jsonify({"ok": True, **de.get_home_data()})


@app.route("/api/market_bar")
@require_auth
def api_market_bar():
    return jsonify({"ok": True, "items": de.get_market_bar()})


@app.route("/api/orders")
@require_auth
def api_orders_list():
    return jsonify({"ok": True, "orders": de.get_open_orders()})


@app.route("/api/orders/<order_id>", methods=["DELETE"])
@require_auth
def api_orders_cancel(order_id):
    ok = de.cancel_alpaca_order(order_id)
    return jsonify({"ok": ok})


@app.route("/api/orders/history")
@require_auth
def api_orders_history():
    orders = de.get_order_history(limit=50)
    return jsonify({"ok": True, "orders": orders})


@app.route("/api/orders/place", methods=["POST"])
@require_auth
def api_orders_place():
    body = request.get_json(silent=True) or {}
    symbol = (body.get("symbol") or body.get("ticker") or "").strip().upper()
    side = (body.get("side") or "buy").strip().lower()
    try:
        qty = float(body.get("qty") or 0)
    except (ValueError, TypeError):
        return jsonify({"ok": False, "error": "invalid qty"}), 400
    order_type = (body.get("type") or "market").strip().lower()
    limit_price = body.get("limit_price")
    if not symbol or qty <= 0:
        return jsonify({"ok": False, "error": "symbol and qty required"}), 400
    result = de.place_simple_order(symbol, side, qty, order_type, limit_price)
    return jsonify({"ok": "error" not in result, **result})


@app.route("/api/stocks/<ticker>/news")
@require_auth
def api_stock_news(ticker):
    ticker = ticker.upper().strip()
    limit = min(int(request.args.get("limit", 5)), 10)
    news = de.get_ticker_news(ticker, limit=limit)
    return jsonify({"ok": True, "ticker": ticker, "news": news})


@app.route("/api/calendar")
@require_auth
def api_calendar():
    try:
        year = int(request.args.get("year", datetime.now().year))
        month = int(request.args.get("month", datetime.now().month))
    except (ValueError, TypeError):
        year, month = datetime.now().year, datetime.now().month
    user_id = session.get("tg_user_id", "default")
    data = de.get_calendar_data(year, month, user_id=user_id)
    return jsonify(data)


@app.route("/api/calendar/day")
@require_auth
def api_calendar_day():
    date_str = request.args.get("date", "")
    if not date_str:
        return jsonify({"ok": False, "error": "date required"}), 400
    user_id = session.get("tg_user_id", "default")
    trades = de.get_day_trades(date_str, user_id=user_id)
    return jsonify({"ok": True, "date": date_str, "trades": trades})


@app.route("/api/alerts")
@require_auth
def api_alerts_list():
    user_id = session.get("tg_user_id", "default")
    return jsonify({"ok": True, "alerts": de.get_alerts(user_id=user_id)})


@app.route("/api/alerts", methods=["POST"])
@require_auth
def api_alerts_create():
    body = request.get_json(silent=True) or {}
    ticker = (body.get("ticker") or "").strip().upper()
    direction = (body.get("direction") or "above").strip().lower()
    try:
        target_price = float(body.get("target_price") or 0)
    except (ValueError, TypeError):
        return jsonify({"ok": False, "error": "invalid target_price"}), 400
    if not ticker or target_price <= 0 or direction not in ("above", "below"):
        return jsonify({"ok": False, "error": "ticker, target_price, direction required"}), 400
    user_id = session.get("tg_user_id", "default")
    result = de.save_alert(ticker, target_price, direction, user_id=user_id)
    return jsonify(result)


@app.route("/api/alerts/<alert_id>", methods=["DELETE"])
@require_auth
def api_alerts_delete(alert_id):
    user_id = session.get("tg_user_id", "default")
    ok = de.delete_alert(alert_id, user_id=user_id)
    return jsonify({"ok": ok})


_alerts_stop = threading.Event()
threading.Thread(
    target=run_alerts_monitor,
    args=(_alerts_stop,),
    daemon=True,
    name="alerts-monitor",
).start()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
