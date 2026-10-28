"""Orders and payments.

Launch flow (works with no merchant account): the buyer sends money by Raast,
JazzCash, Easypaisa or bank transfer, then submits the transaction ID. The owner
gets a Telegram message with an Approve button; one tap unlocks the report.

Gateway flow (once a merchant account is approved): Safepay hosted checkout for
cards and wallets, and Lemon Squeezy hosted checkout for diaspora cards in USD.
Both mark the order paid automatically.
"""
from __future__ import annotations

import hashlib
import hmac
import logging
import re
from urllib.parse import urlencode

import httpx

from . import content, db, notify
from .config import settings

log = logging.getLogger("mizaj.payments")

TID_RE = re.compile(r"^[A-Za-z0-9\-]{6,32}$")


class PaymentError(ValueError):
    pass


def price_for(product: str, coupon: str | None) -> tuple[int, str | None]:
    p = content.product(product)
    amount, used = p["price"], None
    if coupon:
        row = db.q1("SELECT * FROM codes WHERE code = ? AND kind = 'discount' AND uses_left > 0", coupon.upper())
        if row and (row["product"] in (product, "*")) and not _expired(row):
            amount = max(0, round(amount * (100 - row["discount_pct"]) / 100))
            used = row["code"]
    return amount, used


def _expired(row) -> bool:
    return bool(row["expires_at"] and row["expires_at"] < db.now())


def create_order(profile_id: str, product: str, pair_id: str | None = None, coupon: str | None = None) -> dict:
    content.product(product)  # validates
    if product == "couple" and not pair_id:
        raise PaymentError("A couple report needs a completed Mizaj Milan pair.")
    amount, used = price_for(product, coupon)
    oid = db.new_id(12)
    t = db.now()
    db.run("""INSERT INTO orders (id, profile_id, pair_id, product, amount, currency, status, coupon, created_at, updated_at)
              VALUES (?,?,?,?,?,?,?,?,?,?)""", oid, profile_id, pair_id, product, amount, "PKR", "created", used, t, t)
    db.log_event("order_created", profile_id, props={"product": product, "amount": amount})
    return dict(db.q1("SELECT * FROM orders WHERE id = ?", oid))


def get_order(oid: str) -> dict | None:
    r = db.q1("SELECT * FROM orders WHERE id = ?", oid)
    return dict(r) if r else None


def submit_proof(oid: str, method: str, tid: str, sender: str, email: str = "", phone: str = "") -> dict:
    order = get_order(oid)
    if not order:
        raise PaymentError("Order not found.")
    if order["status"] == "paid":
        return order
    if method not in {m["key"] for m in settings.manual_methods()}:
        raise PaymentError("Please choose a payment method.")
    tid = tid.strip().replace(" ", "")
    if not TID_RE.match(tid):
        raise PaymentError("Please enter the transaction ID exactly as shown in your app or SMS (6-32 letters/digits).")
    clash = db.q1("SELECT id FROM orders WHERE method = ? AND tid = ? AND id != ?", method, tid, oid)
    if clash:
        raise PaymentError("This transaction ID has already been used. If this is a mistake, contact us on WhatsApp.")
    status = "paid" if settings.auto_approve_manual else "proof"
    t = db.now()
    db.run("""UPDATE orders SET method = ?, tid = ?, sender = ?, email = ?, phone = ?, status = ?, updated_at = ?,
              paid_at = CASE WHEN ? = 'paid' THEN ? ELSE paid_at END WHERE id = ?""",
           method, tid, sender.strip()[:60], email.strip()[:120], phone.strip()[:30], status, t, status, t, oid)
    order = get_order(oid)
    db.log_event("proof_submitted", order["profile_id"], props={"product": order["product"], "method": method})
    _alert_owner_proof(order)
    if status == "paid":
        _after_paid(order)
    return order


def _alert_owner_proof(order: dict) -> None:
    p = content.product(order["product"])
    approve = f"{settings.site_url}/admin/order/{order['id']}?a=approve&s={notify.sign(order['id'], 'approve')}"
    reject = f"{settings.site_url}/admin/order/{order['id']}?a=reject&s={notify.sign(order['id'], 'reject')}"
    head = "✅ Auto-unlocked — please verify" if order["status"] == "paid" else "💰 New payment to verify"
    text = (f"<b>{head}</b>\n{notify.esc(p['name'])} — <b>PKR {order['amount']:,}</b>\n"
            f"Method: {notify.esc(order['method'])}\nTID: <code>{notify.esc(order['tid'])}</code>\n"
            f"Sender: {notify.esc(order['sender'])}\nOrder: {order['id']}")
    rows = [[("Reject / revoke ❌", reject)]] if order["status"] == "paid" else [[("Approve ✅", approve), ("Reject ❌", reject)]]
    notify.telegram(text, rows)


def mark_paid(oid: str, method: str | None = None, gateway_ref: str | None = None) -> dict | None:
    order = get_order(oid)
    if not order:
        return None
    if order["status"] != "paid":
        t = db.now()
        db.run("""UPDATE orders SET status = 'paid', paid_at = ?, updated_at = ?, method = COALESCE(?, method),
                  gateway_ref = COALESCE(?, gateway_ref) WHERE id = ?""", t, t, method, gateway_ref, oid)
        order = get_order(oid)
        _after_paid(order)
        if method in ("safepay", "lemonsqueezy"):
            p = content.product(order["product"])
            notify.telegram(f"💳 <b>Paid by {method}</b>: {notify.esc(p['name'])} — {order['currency']} {order['amount']:,}")
    return order


def reject(oid: str, reason: str = "") -> dict | None:
    order = get_order(oid)
    if not order:
        return None
    db.run("UPDATE orders SET status = 'rejected', note = ?, updated_at = ? WHERE id = ?", reason[:200], db.now(), oid)
    order = get_order(oid)
    if order.get("email"):
        body = ("<p>We could not find a payment matching the transaction ID you entered "
                f"(<b>{notify.esc(order['tid'])}</b>).</p><p>If you did pay, reply to this email with a screenshot "
                "and we will unlock your report straight away.</p>")
        notify.email(order["email"], "We couldn't verify your Mizaj payment", notify.email_shell("Payment not found", body))
    db.log_event("order_rejected", order["profile_id"], props={"product": order["product"]})
    return order


def _after_paid(order: dict) -> None:
    db.log_event("paid", order["profile_id"], props={"product": order["product"], "amount": order["amount"],
                                                      "method": order["method"]})
    prof = db.get_profile(order["profile_id"])
    if prof is None:
        return
    to = order.get("email") or prof["email"]
    if not to:
        return
    p = content.product(order["product"])
    link = f"{settings.site_url}/report/{prof['id']}?k={prof['key']}"
    body = (f"<p>Shukriya! Your <b>{notify.esc(p['name'])}</b> is unlocked.</p>"
            "<p>Keep this email: the button below always opens your full report, on any phone or laptop.</p>")
    notify.email(to, f"Your {p['name']} is ready", notify.email_shell("Your report is ready", body, "Open my report", link))


# ---------- voucher codes (B2B seats, influencer gifts, discounts) ----------

def create_codes(product: str, count: int, kind: str = "unlock", discount_pct: int = 0, uses: int = 1,
                 org: str = "", note: str = "", prefix: str = "MZ") -> list[str]:
    content.product(product) if product != "*" else None
    codes = []
    for _ in range(count):
        code = f"{prefix}-{db.new_id(6).upper()}"
        db.run("""INSERT INTO codes (code, product, kind, discount_pct, uses_left, org, note, created_at)
                  VALUES (?,?,?,?,?,?,?,?)""", code, product, kind, discount_pct, uses, org, note, db.now())
        codes.append(code)
    return codes


def redeem(code: str, profile_id: str, pair_id: str | None = None) -> dict:
    code = code.strip().upper()
    with db.tx() as conn:
        row = conn.execute("SELECT * FROM codes WHERE code = ?", (code,)).fetchone()
        if not row or row["kind"] != "unlock" or row["uses_left"] <= 0 or _expired(row):
            raise PaymentError("This code is not valid or has already been used.")
        if row["product"] == "couple" and not pair_id:
            raise PaymentError("This code unlocks a couple report: open it from your Mizaj Milan page.")
        conn.execute("UPDATE codes SET uses_left = uses_left - 1 WHERE code = ?", (code,))
        oid, t = db.new_id(12), db.now()
        conn.execute("""INSERT INTO orders (id, profile_id, pair_id, product, amount, currency, method, status, coupon,
                        created_at, updated_at, paid_at) VALUES (?,?,?,?,0,'PKR','code','paid',?,?,?,?)""",
                     (oid, profile_id, pair_id, row["product"], code, t, t, t))
    db.log_event("code_redeemed", profile_id, props={"product": row["product"], "org": row["org"]})
    return get_order(oid)


# ---------- Safepay (cards + wallets) ----------
# Hosted checkout per Safepay's documented "custom integration": init an order to get a tracker
# token, redirect to the components page, and verify the HMAC-SHA256 signature of the tracker on
# return. Test in sandbox before switching SAFEPAY_ENV=production (see docs/RUNBOOK.md).

def _safepay_base() -> str:
    return "https://api.getsafepay.com" if settings.safepay_env == "production" else "https://sandbox.api.getsafepay.com"


def safepay_checkout_url(order: dict) -> str:
    if not settings.has_safepay:
        raise PaymentError("Card payments are not switched on yet.")
    r = httpx.post(f"{_safepay_base()}/order/v1/init", timeout=15, json={
        "client": settings.safepay_api_key, "amount": float(order["amount"]),
        "currency": "PKR", "environment": settings.safepay_env})
    r.raise_for_status()
    token = r.json()["data"]["token"]
    db.run("UPDATE orders SET gateway_ref = ?, method = 'safepay', updated_at = ? WHERE id = ?", token, db.now(), order["id"])
    qs = urlencode({"env": settings.safepay_env, "beacon": token, "source": "custom", "order_id": order["id"],
                    "redirect_url": f"{settings.site_url}/pay/safepay/return?order={order['id']}",
                    "cancel_url": f"{settings.site_url}/order/{order['id']}"})
    return f"{_safepay_base()}/components?{qs}"


def safepay_verify_return(order_id: str, tracker: str, sig: str) -> bool:
    order = get_order(order_id)
    if not order or not settings.safepay_secret_key or order.get("gateway_ref") != tracker:
        return False
    expected = hmac.new(settings.safepay_secret_key.encode(), tracker.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, sig or ""):
        return False
    mark_paid(order_id, "safepay", tracker)
    return True


# ---------- Lemon Squeezy (diaspora USD cards) ----------

def lemonsqueezy_url(order: dict) -> str | None:
    base = settings.ls_links.get(order["product"])
    if not base:
        return None
    sep = "&" if "?" in base else "?"
    return f"{base}{sep}{urlencode({'checkout[custom][order_id]': order['id']})}"


def lemonsqueezy_webhook(raw: bytes, signature: str, payload: dict) -> bool:
    if not settings.lemonsqueezy_webhook_secret:
        return False
    expected = hmac.new(settings.lemonsqueezy_webhook_secret.encode(), raw, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signature or ""):
        return False
    meta = payload.get("meta", {})
    if meta.get("event_name") != "order_created":
        return True
    oid = (meta.get("custom_data") or {}).get("order_id")
    attrs = payload.get("data", {}).get("attributes", {})
    if oid and attrs.get("status") == "paid":
        db.run("UPDATE orders SET currency = 'USD', amount = ? WHERE id = ?", int(attrs.get("total", 0)) // 100, oid)
        mark_paid(oid, "lemonsqueezy", str(payload.get("data", {}).get("id", "")))
    return True
