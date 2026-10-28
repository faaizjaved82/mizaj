"""Funnel numbers for the admin page, the daily Telegram digest and the weekly COO export."""
from __future__ import annotations

import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from . import db
from .config import settings

_cache: dict[str, tuple[float, int]] = {}
BASELINE_TESTS = 0  # add any tests taken on the old site here if known


def public_test_count() -> int:
    hit = _cache.get("tests")
    if hit and hit[0] > time.time() - 300:
        return hit[1]
    n = (db.q1("SELECT COUNT(*) c FROM results")["c"] or 0) + BASELINE_TESTS
    _cache["tests"] = (time.time(), n)
    return n


def _since(days: float) -> float:
    return time.time() - days * 86400


def window(start: float, end: float | None = None) -> dict:
    end = end or time.time()
    ev = {r["name"]: r["c"] for r in db.q(
        "SELECT name, COUNT(*) c FROM events WHERE ts >= ? AND ts < ? GROUP BY name", start, end)}
    tests = {r["test"]: r["c"] for r in db.q(
        "SELECT test, COUNT(*) c FROM results WHERE created_at >= ? AND created_at < ? GROUP BY test", start, end)}
    paid = db.q("""SELECT product, currency, COUNT(*) c, SUM(amount) s FROM orders
                   WHERE status = 'paid' AND paid_at >= ? AND paid_at < ? GROUP BY product, currency""", start, end)
    revenue_pkr = sum(r["s"] or 0 for r in paid if r["currency"] == "PKR")
    revenue_usd = sum(r["s"] or 0 for r in paid if r["currency"] == "USD")
    orders_paid = sum(r["c"] for r in paid)
    new_profiles = db.q1("SELECT COUNT(*) c FROM profiles WHERE created_at >= ? AND created_at < ?", start, end)["c"]
    leads = db.q1("SELECT COUNT(*) c FROM leads WHERE created_at >= ? AND created_at < ?", start, end)["c"]
    pending = db.q1("SELECT COUNT(*) c FROM orders WHERE status = 'proof'")["c"]
    starts = ev.get("test_start", 0)
    completes = sum(tests.values())
    return {
        "visits": ev.get("page_view", 0), "test_starts": starts, "tests": tests, "test_completes": completes,
        "completion_rate": round(100 * completes / starts, 1) if starts else None,
        "new_profiles": new_profiles, "result_views": ev.get("result_view", 0),
        "checkout_views": ev.get("checkout_view", 0), "orders_created": ev.get("order_created", 0),
        "orders_paid": orders_paid, "by_product": {r["product"]: r["c"] for r in paid},
        "revenue_pkr": revenue_pkr, "revenue_usd": revenue_usd,
        "buyer_rate": round(100 * orders_paid / new_profiles, 2) if new_profiles else None,
        "milan_invites": ev.get("milan_invite", 0), "milan_completed": ev.get("milan_completed", 0),
        "palm_reads": ev.get("palm_read", 0), "shares": ev.get("share_click", 0),
        "contacts": ev.get("contact_captured", 0), "leads": leads, "pending_payments": pending,
    }


def top_sources(start: float, limit: int = 8) -> list[dict]:
    rows = db.q("""SELECT COALESCE(NULLIF(utm_source,''), NULLIF(ref,''), 'direct') src, COUNT(*) c
                   FROM profiles WHERE created_at >= ? GROUP BY src ORDER BY c DESC LIMIT ?""", start, limit)
    return [{"source": r["src"], "profiles": r["c"]} for r in rows]


def outcome_mix(start: float) -> dict:
    rows = db.q("SELECT test, outcome, COUNT(*) c FROM results WHERE created_at >= ? GROUP BY test, outcome", start)
    out: dict = {}
    for r in rows:
        out.setdefault(r["test"], {})[r["outcome"]] = r["c"]
    return out


def dashboard() -> dict:
    return {"today": window(_day_start(0)), "d7": window(_since(7)), "d30": window(_since(30)),
            "all": window(0), "sources": top_sources(_since(30)), "mix": outcome_mix(_since(30))}


def _day_start(days_ago: int) -> float:
    tz = ZoneInfo(settings.tz)
    d = datetime.now(tz).replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days_ago)
    return d.timestamp()


def digest_text() -> str:
    y0, y1 = _day_start(1), _day_start(0)
    y, w = window(y0, y1), window(_since(7))
    total = window(0)
    lines = [
        f"<b>Mizaj daily · {datetime.fromtimestamp(y0, ZoneInfo(settings.tz)).strftime('%a %d %b')}</b>",
        f"Tests completed: <b>{y['test_completes']}</b> (7d {w['test_completes']})",
        f"Paid orders: <b>{y['orders_paid']}</b> · PKR <b>{y['revenue_pkr']:,}</b>" + (f" + USD {y['revenue_usd']}" if y['revenue_usd'] else ""),
        f"7-day revenue: PKR {w['revenue_pkr']:,} · buyer rate {w['buyer_rate'] or 0}%",
        f"Milan invites/completed: {y['milan_invites']}/{y['milan_completed']} · palm reads {y['palm_reads']}",
        f"B2B leads: {y['leads']} · payments waiting: <b>{total['pending_payments']}</b>",
        f"All-time revenue: PKR {total['revenue_pkr']:,}",
    ]
    src = top_sources(_since(7), 3)
    if src:
        lines.append("Top sources (7d): " + ", ".join(f"{s['source']} {s['profiles']}" for s in src))
    return "\n".join(lines)


def weekly_export() -> dict:
    """Aggregate-only (no personal data) snapshot the weekly COO session reads from the repo."""
    weeks = []
    for i in range(8):
        start, end = _since(7 * (i + 1)), _since(7 * i)
        weeks.append({"weeks_ago": i, **window(start, end)})
    return {"generated_at": datetime.now(ZoneInfo(settings.tz)).isoformat(timespec="minutes"),
            "weeks": weeks, "all_time": window(0), "sources_30d": top_sources(_since(30), 15),
            "outcome_mix_30d": outcome_mix(_since(30))}
