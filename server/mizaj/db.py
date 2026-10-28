"""SQLite storage. One file at settings.db_path, created on first use."""
from __future__ import annotations

import json
import secrets
import sqlite3
import string
import threading
import time
from contextlib import contextmanager
from typing import Any, Iterator

from .config import settings

SCHEMA = """
CREATE TABLE IF NOT EXISTS profiles (
  id TEXT PRIMARY KEY,              -- public slug used in share links
  key TEXT NOT NULL,                -- private access key (report links)
  name TEXT, email TEXT, phone TEXT, city TEXT, gender TEXT, birth_date TEXT,
  ref TEXT, utm_source TEXT, utm_medium TEXT, utm_campaign TEXT,
  plan TEXT,                        -- NULL | full | bundle (best purchase so far)
  created_at REAL NOT NULL, updated_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS results (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  profile_id TEXT NOT NULL REFERENCES profiles(id),
  test TEXT NOT NULL,               -- personality | mizaj | interests
  answers TEXT NOT NULL, scores TEXT NOT NULL, outcome TEXT NOT NULL,
  created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS results_profile ON results(profile_id, test);
CREATE TABLE IF NOT EXISTS pairs (
  id TEXT PRIMARY KEY, a_profile TEXT NOT NULL, b_profile TEXT,
  relation TEXT,                    -- rishta | spouse | friend | sibling | colleague
  created_at REAL NOT NULL, completed_at REAL
);
CREATE TABLE IF NOT EXISTS orders (
  id TEXT PRIMARY KEY,
  profile_id TEXT NOT NULL, pair_id TEXT,
  product TEXT NOT NULL, amount INTEGER NOT NULL, currency TEXT NOT NULL DEFAULT 'PKR',
  method TEXT,                      -- jazzcash | easypaisa | bank | safepay | gumroad | lemonsqueezy | code
  status TEXT NOT NULL,             -- created | proof | paid | rejected | refunded
  tid TEXT, sender TEXT, coupon TEXT, gateway_ref TEXT, note TEXT,
  email TEXT, phone TEXT,
  created_at REAL NOT NULL, updated_at REAL NOT NULL, paid_at REAL
);
CREATE INDEX IF NOT EXISTS orders_status ON orders(status);
CREATE UNIQUE INDEX IF NOT EXISTS orders_tid ON orders(method, tid) WHERE tid IS NOT NULL;
CREATE TABLE IF NOT EXISTS palm (
  id TEXT PRIMARY KEY, profile_id TEXT NOT NULL,
  hand TEXT, reading TEXT NOT NULL, created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS codes (
  code TEXT PRIMARY KEY, product TEXT NOT NULL,
  kind TEXT NOT NULL DEFAULT 'unlock', -- unlock | discount
  discount_pct INTEGER NOT NULL DEFAULT 0,
  uses_left INTEGER NOT NULL DEFAULT 1, org TEXT, note TEXT,
  created_at REAL NOT NULL, expires_at REAL
);
CREATE TABLE IF NOT EXISTS leads (
  id INTEGER PRIMARY KEY AUTOINCREMENT, kind TEXT NOT NULL,
  name TEXT, org TEXT, role TEXT, phone TEXT, email TEXT, city TEXT, size TEXT, message TEXT,
  status TEXT NOT NULL DEFAULT 'new', created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS subscribers (
  id INTEGER PRIMARY KEY AUTOINCREMENT, profile_id TEXT, email TEXT, whatsapp TEXT,
  topic TEXT, created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY AUTOINCREMENT, ts REAL NOT NULL, name TEXT NOT NULL,
  profile_id TEXT, path TEXT, ref TEXT, props TEXT
);
CREATE INDEX IF NOT EXISTS events_ts ON events(ts, name);
CREATE TABLE IF NOT EXISTS kv (k TEXT PRIMARY KEY, v TEXT NOT NULL);
"""

_local = threading.local()
_init_lock = threading.Lock()
_initialised = False


def connect() -> sqlite3.Connection:
    global _initialised
    conn = getattr(_local, "conn", None)
    if conn is None:
        settings.data_dir.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(settings.db_path, timeout=15, isolation_level=None)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA busy_timeout=15000")
        _local.conn = conn
    if not _initialised:
        with _init_lock:
            if not _initialised:
                conn.executescript(SCHEMA)
                _initialised = True
    return conn


def reset_for_tests() -> None:
    global _initialised
    conn = getattr(_local, "conn", None)
    if conn is not None:
        conn.close()
        _local.conn = None
    _initialised = False


@contextmanager
def tx() -> Iterator[sqlite3.Connection]:
    conn = connect()
    conn.execute("BEGIN IMMEDIATE")
    try:
        yield conn
        conn.execute("COMMIT")
    except Exception:
        conn.execute("ROLLBACK")
        raise


def q(sql: str, *args: Any) -> list[sqlite3.Row]:
    return connect().execute(sql, args).fetchall()


def q1(sql: str, *args: Any) -> sqlite3.Row | None:
    return connect().execute(sql, args).fetchone()


def run(sql: str, *args: Any) -> int:
    cur = connect().execute(sql, args)
    return cur.lastrowid or cur.rowcount


_ALPHA = string.ascii_lowercase + string.digits


def new_id(n: int = 10) -> str:
    return "".join(secrets.choice(_ALPHA) for _ in range(n))


def now() -> float:
    return time.time()


def dumps(v: Any) -> str:
    return json.dumps(v, ensure_ascii=False, separators=(",", ":"))


def loads(s: str | None, default: Any = None) -> Any:
    if not s:
        return default
    try:
        return json.loads(s)
    except ValueError:
        return default


# ---------- profiles ----------

def create_profile(**fields: Any) -> sqlite3.Row:
    pid, key, t = new_id(10), new_id(24), now()
    cols = {k: v for k, v in fields.items() if k in PROFILE_FIELDS and v}
    names = ", ".join(["id", "key", "created_at", "updated_at", *cols])
    marks = ", ".join("?" * (4 + len(cols)))
    run(f"INSERT INTO profiles ({names}) VALUES ({marks})", pid, key, t, t, *cols.values())
    return get_profile(pid)


PROFILE_FIELDS = ("name", "email", "phone", "city", "gender", "birth_date", "ref",
                  "utm_source", "utm_medium", "utm_campaign")


def get_profile(pid: str) -> sqlite3.Row | None:
    return q1("SELECT * FROM profiles WHERE id = ?", pid)


def update_profile(pid: str, **fields: Any) -> None:
    cols = {k: v for k, v in fields.items() if k in (*PROFILE_FIELDS, "plan") and v is not None}
    if not cols:
        return
    sets = ", ".join(f"{k} = ?" for k in cols)
    run(f"UPDATE profiles SET {sets}, updated_at = ? WHERE id = ?", *cols.values(), now(), pid)


def latest_results(pid: str) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for r in q("SELECT * FROM results WHERE profile_id = ? ORDER BY id", pid):
        out[r["test"]] = {"outcome": r["outcome"], "scores": loads(r["scores"], {}), "created_at": r["created_at"]}
    return out


def save_result(pid: str, test: str, answers: Any, scores: dict, outcome: str) -> int:
    return run("INSERT INTO results (profile_id, test, answers, scores, outcome, created_at) VALUES (?,?,?,?,?,?)",
               pid, test, dumps(answers), dumps(scores), outcome, now())


# ---------- events ----------

def log_event(name: str, profile_id: str | None = None, path: str | None = None,
              ref: str | None = None, props: dict | None = None) -> None:
    run("INSERT INTO events (ts, name, profile_id, path, ref, props) VALUES (?,?,?,?,?,?)",
        now(), name[:40], profile_id, (path or "")[:200], (ref or "")[:200], dumps(props or {}))


def kv_get(k: str, default: str | None = None) -> str | None:
    r = q1("SELECT v FROM kv WHERE k = ?", k)
    return r["v"] if r else default


def kv_set(k: str, v: str) -> None:
    run("INSERT INTO kv (k, v) VALUES (?, ?) ON CONFLICT(k) DO UPDATE SET v = excluded.v", k, v)
