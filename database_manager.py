"""SQLite + JSON dual-write database manager."""
import json
import os
import sqlite3
import threading
from datetime import datetime

DB_PATH = "data/mytraderhub.db"
DECISIONS_JSON = "data/decisions.json"

_lock = threading.Lock()


def _ensure_dirs():
    os.makedirs("data", exist_ok=True)


def _read_json(path: str, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def _write_json(path: str, data) -> None:
    _ensure_dirs()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


class DatabaseManager:
    def __init__(self):
        _ensure_dirs()
        self._init_db()

    def _conn(self):
        return sqlite3.connect(DB_PATH)

    def _init_db(self):
        with _lock:
            conn = self._conn()
            try:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS decisions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL DEFAULT 'default',
                        ticker TEXT,
                        timestamp TEXT,
                        outcome TEXT,
                        r_multiple REAL,
                        grade TEXT,
                        entry_price REAL,
                        exit_price REAL,
                        setup_type TEXT,
                        notes TEXT
                    )
                """)
                conn.commit()
            finally:
                conn.close()

    def get_decisions(self, user_id: str = "default", limit: int = 100) -> list:
        with _lock:
            conn = self._conn()
            try:
                conn.row_factory = sqlite3.Row
                rows = conn.execute(
                    "SELECT * FROM decisions WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
                    (user_id, limit),
                ).fetchall()
                return [dict(r) for r in rows]
            except Exception:
                items = _read_json(DECISIONS_JSON, [])
                return [d for d in items if d.get("user_id", "default") == user_id][:limit]
            finally:
                conn.close()

    def save_decision(self, data: dict, user_id: str = "default") -> dict:
        data = dict(data)
        data["user_id"] = user_id
        if not data.get("timestamp"):
            data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with _lock:
            conn = self._conn()
            try:
                conn.execute(
                    """INSERT INTO decisions
                       (user_id, ticker, timestamp, outcome, r_multiple, grade,
                        entry_price, exit_price, setup_type, notes)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        user_id,
                        data.get("ticker", ""),
                        data.get("timestamp", ""),
                        data.get("outcome", "pending"),
                        float(data.get("r_multiple") or 0),
                        data.get("grade", ""),
                        data.get("entry_price"),
                        data.get("exit_price"),
                        data.get("setup_type", ""),
                        data.get("notes", ""),
                    ),
                )
                conn.commit()
            finally:
                conn.close()

            items = _read_json(DECISIONS_JSON, [])
            items.insert(0, data)
            _write_json(DECISIONS_JSON, items)

        return data
