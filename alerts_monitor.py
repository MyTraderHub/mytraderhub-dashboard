"""
alerts_monitor.py — Background thread that checks price alerts every 5 minutes.
Fires Telegram notifications via notify_hub when an alert triggers.
"""
import logging
import threading
import time

from dashboard_engine import _alpaca_get, check_alerts_against_prices

log = logging.getLogger("hub.alerts")


def _get_prices_for_alerts(alerts: list) -> dict:
    tickers = list({a["ticker"] for a in alerts})
    prices = {}
    for ticker in tickers:
        try:
            snap = _alpaca_get(f"/v2/stocks/{ticker}/snapshot")
            if snap and snap.get("latestTrade"):
                prices[ticker] = float(snap["latestTrade"].get("p", 0) or 0)
        except Exception:
            pass
    return prices


def run_alerts_monitor(stop_event: threading.Event):
    log.info("Price alerts monitor started")
    while not stop_event.is_set():
        try:
            from dashboard_engine import _load_alerts
            alerts = _load_alerts()
            if alerts:
                prices = _get_prices_for_alerts(alerts)
                triggered = check_alerts_against_prices(prices)
                for alert in triggered:
                    try:
                        import notify_hub as nh
                        price = alert.get("triggered_price", "?")
                        msg = (f"{alert['ticker']} crossed {alert['direction']} "
                               f"${alert['target_price']} (now ${price})")
                        nh.send_alert(msg)
                        log.info("Alert triggered: %s", msg)
                    except Exception as exc:
                        log.warning("Alert notify failed: %s", exc)
        except Exception as exc:
            log.warning("Alerts monitor error: %s", exc)
        stop_event.wait(300)
