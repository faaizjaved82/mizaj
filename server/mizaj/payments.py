"""Orders and payments.

Launch flow (works with no merchant account): the buyer sends money by Raast,
JazzCash, Easypaisa or bank transfer, then submits the transaction ID. The owner
gets a Telegram message with an Approve button; one tap unlocks the report.

Gateway flow (once a merchant account is approved): Safepay hosted checkout for
cards and wallets, and Gumroad (preferred) or Lemon Squeezy hosted checkout for
international cards in USD. All of them mark the order paid automatically.
"""
from __future__ import annotations

import hashlib
import hmac
import logging
import re
from urllib.parse import quote, urlencode, urlparse

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
    approve, reject = _admin_link(order["id"], "approve"), _admin_link(order["id"], "reject")
    head = "✅ Auto-unlocked — please verify" if order["status"] == "paid" else "💰 New payment to verify"
    text = (f"<b>{head}</b>\n{notify.esc(p['name'])} — <b>PKR {order['amount']:,}</b>\n"
            f"Method: {notify.esc(order['method'])}\nTID: <code>{notify.esc(order['tid'])}</code>\n"
            f"Sender: {notify.esc(order['sender'])}\nOrder: {order['id']}")
    rows = [[("Reject / revoke ❌", reject)]] if order["status"] == "paid" else [[("Approve ✅", approve), ("Reject ❌", reject)]]
    notify.telegram(text, rows)


def _admin_link(oid: str, action: str) -> str:
    """Signed one-tap link for the owner's Telegram buttons (opens a confirm page)."""
    return f"{settings.site_url}/admin/order/{oid}?a={action}&s={notify.sign(oid, action)}"


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
        if method in ("safepay", "lemonsqueezy", "gumroad"):
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


# ---------- Gumroad (international cards; merchant of record, pays out to a Pakistani bank) ----------
# The buyer opens the Gumroad product link with ?order_id=<oid>. After the sale Gumroad POSTs a
# "Ping" (form-encoded; fields as built by Purchase#payload_for_ping_notification in Gumroad's
# source) to /api/webhooks/gumroad/<GUMROAD_PING_SECRET>, echoing our id back as url_params[order_id].
# Pings are not signed, so the secret path, seller id, order, product and price are all checked,
# and with GUMROAD_ACCESS_TOKEN the sale is confirmed with Gumroad's API before anything unlocks.
# Gumroad retries a ping only on 5xx or a connection failure, so anything authentic we can't use
# gets a 200 plus a Telegram alert to the owner, and 503 is kept for "Gumroad's API didn't answer".

GUMROAD_API = "https://api.gumroad.com/v2"


class GumroadUnavailable(Exception):
    """Gumroad's API could not be reached: answer 503 so Gumroad retries the ping later."""


def gumroad_url(order: dict) -> str | None:
    base = settings.gr_links.get(order["product"])
    if not base:
        return None
    sep = "&" if "?" in base else "?"
    return f"{base}{sep}{urlencode({'order_id': order['id'], 'wanted': 'true'})}"


def _last_segment(url: object) -> str:
    """'https://mizaj.gumroad.com/l/mizaj-full?x=1' -> 'mizaj-full'; a bare permalink stays as it is."""
    return urlparse(str(url or "")).path.rstrip("/").rsplit("/", 1)[-1]


def _true(v: object) -> bool:
    return str(v).strip().lower() in ("true", "1")


def _cents(v: object) -> int:
    try:
        return int(str(v).strip())
    except ValueError:
        return -1


def _usd_cents(order: dict) -> int:
    return round(float(content.product(order["product"])["usd"]) * 100)


def _ping_order_id(ping: dict) -> str:
    oid = ping.get("url_params[order_id]")  # form-encoded ping (the default)
    if oid is None and isinstance(ping.get("url_params"), dict):  # JSON ping
        oid = ping["url_params"].get("order_id")
    return str(oid or "").strip()[:32]


def _ping_permalinks(ping: dict) -> set[str]:
    # permalink: the custom one (mizaj-full); product_permalink: the full product URL;
    # short_product_id: Gumroad's random permalink.
    return {_last_segment(ping.get(k)) for k in ("permalink", "product_permalink", "short_product_id")} - {""}


def _ping_amount(ping: dict) -> str:
    cents = _cents(ping.get("price"))
    return f"{str(ping.get('currency') or 'usd').upper()} {cents / 100:.2f}" if cents >= 0 else "an unknown amount"


def gumroad_ping(secret: str, ping: dict) -> int:
    """Handle a Gumroad Ping and return the HTTP status to answer with.

    404 unless the path secret matches; 403 for another seller id; 503 if Gumroad's API didn't answer;
    otherwise 200: unlocked, already unlocked by this sale (a repeated ping), or not usable (owner alerted).
    """
    if not settings.has_gumroad_ping or not hmac.compare_digest(
            str(secret).encode(), settings.gumroad_ping_secret.encode()):
        return 404
    if str(ping.get("seller_id") or "") != settings.gumroad_seller_id:
        _gumroad_alert("The ping came from a different Gumroad seller id (check GUMROAD_SELLER_ID).", ping)
        return 403
    oid = _ping_order_id(ping)
    order = get_order(oid) if oid else None
    if not order:
        _gumroad_alert("No matching Mizaj order (bought straight from Gumroad?). "
                       "Send the buyer an unlock code from /admin.", ping)
        return 200
    sale_id = str(ping.get("sale_id") or "").strip()
    if order["status"] == "paid":
        if not (order.get("method") == "gumroad" and order.get("gateway_ref") == sale_id):
            _gumroad_alert("This order was already unlocked another way. Unless you unlocked it by hand for this "
                           "sale, the buyer may have paid twice: check and refund one payment.", ping, order)
        return 200
    problem = _gumroad_problem(order, ping, sale_id)
    if problem is None and settings.gumroad_access_token:
        try:
            problem = _gumroad_api_problem(order, ping, sale_id)
        except GumroadUnavailable as e:
            log.warning("gumroad api unavailable: %s", e)
            _gumroad_alert("Gumroad's API didn't answer, so the sale isn't confirmed yet. Gumroad will retry "
                           "the ping; unlock by hand if the sale is genuine.", ping, order)
            return 503
    if problem:
        _gumroad_alert(problem, ping, order)
        return 200
    email = str(ping.get("email") or "").strip()[:120]
    db.run("UPDATE orders SET currency = 'USD', amount = ?, email = COALESCE(NULLIF(email, ''), ?) WHERE id = ?",
           _cents(ping.get("price")) // 100, email or None, order["id"])
    mark_paid(order["id"], "gumroad", sale_id)
    if _true(ping.get("test")):
        notify.telegram(f"🧪 That Gumroad sale was a test purchase by the seller account. Reject order {order['id']} "
                        "so it doesn't count as revenue.", [[("Reject ❌", _admin_link(order["id"], "reject"))]])
    return 200


def _gumroad_problem(order: dict, ping: dict, sale_id: str) -> str | None:
    """Why this authentic ping must not unlock the order, or None if it may."""
    if not sale_id:
        return "The ping has no sale id."
    want = _last_segment(settings.gr_links.get(order["product"]))
    if not want or want not in _ping_permalinks(ping):
        return f"The product bought ({ping.get('permalink') or '?'}) is not the one ordered ({order['product']})."
    if str(ping.get("currency") or "usd").strip().lower() != "usd":
        return f"Paid in {_ping_amount(ping)}, not US dollars."
    if _cents(ping.get("price")) < _usd_cents(order):
        return f"Paid {_ping_amount(ping)}, but {order['product']} costs USD {_usd_cents(order) / 100:.2f}."
    if any(_true(ping.get(k)) for k in ("refunded", "disputed", "chargebacked")):
        return "Gumroad marks this sale as refunded or disputed."
    used = db.q1("SELECT id FROM orders WHERE method = 'gumroad' AND gateway_ref = ? AND id != ?", sale_id, order["id"])
    if used:
        return f"This Gumroad sale already unlocked order {used['id']}."
    return None


def _gumroad_api_problem(order: dict, ping: dict, sale_id: str) -> str | None:
    """Confirm the sale with Gumroad's API (the token only sees our own sales). None = it agrees."""
    try:
        r = httpx.get(f"{GUMROAD_API}/sales/{quote(sale_id, safe='')}", timeout=10,
                      headers={"Authorization": f"Bearer {settings.gumroad_access_token}"})
    except httpx.HTTPError as e:
        raise GumroadUnavailable(type(e).__name__) from e
    if r.status_code >= 500:
        raise GumroadUnavailable(f"HTTP {r.status_code}")
    try:
        data = r.json()
    except ValueError:
        data = None
    data = data if isinstance(data, dict) else {}
    sale = data.get("sale")
    if data.get("success") is not True or not isinstance(sale, dict):
        return f"Gumroad's API did not confirm the sale (HTTP {r.status_code}: {str(data.get('message') or '')[:100]})."
    if str(sale.get("id") or sale_id) != sale_id:
        return "Gumroad's API returned a different sale."
    if sale.get("seller_id") and sale["seller_id"] != settings.gumroad_seller_id:
        return "Gumroad's API says the sale belongs to another seller."
    # The API's product_permalink is Gumroad's random one (the ping's short_product_id): match product_id first.
    same = (ping.get("product_id") and sale.get("product_id") == ping.get("product_id")) or \
        _last_segment(sale.get("product_permalink")) in _ping_permalinks(ping)
    if not same:
        return "Gumroad's API says the sale is for a different product."
    if any(_true(sale.get(k)) for k in ("refunded", "partially_refunded", "chargedback")):
        return "Gumroad's API says the sale was refunded or charged back."
    if "price" in sale and _cents(sale["price"]) < _usd_cents(order):
        return "Gumroad's API shows a lower price than the product costs."
    return None


def _gumroad_alert(problem: str, ping: dict, order: dict | None = None) -> None:
    log.warning("gumroad sale %s not used: %s", ping.get("sale_id"), problem)
    text = (f"⚠️ <b>Gumroad sale not unlocked</b>\n{notify.esc(problem)}\n"
            f"Product: {notify.esc(ping.get('product_name') or ping.get('permalink'))}, {notify.esc(_ping_amount(ping))}\n"
            f"Sale: <code>{notify.esc(ping.get('sale_id'))}</code>{' (test)' if _true(ping.get('test')) else ''}\n"
            f"Buyer: {notify.esc(ping.get('email'))}")
    rows = None
    if order:
        text += f"\nOrder: {order['id']} ({notify.esc(content.product(order['product'])['name'])}, {order['status']})"
        if order["status"] != "paid":
            rows = [[("Unlock anyway ✅", _admin_link(order["id"], "approve"))]]
    notify.telegram(text, rows)
