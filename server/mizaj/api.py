"""The Mizaj web app: JSON API + dynamic pages (results, reports, checkout, admin).

Static pages (home, tests, type pages ...) are pre-built into dist/ by build.py and
served by Caddy; in development this app serves dist/ too.
"""
from __future__ import annotations

import logging
import time
from collections import defaultdict, deque
from datetime import date
from typing import Any

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from . import ai, content, db, notify, payments, reports, scoring, stats
from .config import settings
from .web import render

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
log = logging.getLogger("mizaj")

app = FastAPI(title="Mizaj", docs_url=None, redoc_url=None, openapi_url=None)

OWNER_COOKIE = "mzk"
ADMIN_COOKIE = "mza"
YEAR = 60 * 60 * 24 * 365


# ---------- helpers ----------

_buckets: dict[tuple[str, str], deque] = defaultdict(deque)


def client_ip(request: Request) -> str:
    fwd = request.headers.get("x-forwarded-for", "")
    return fwd.split(",")[0].strip() if fwd else (request.client.host if request.client else "?")


def limit(request: Request, name: str, per_hour: int) -> None:
    key = (name, client_ip(request))
    q, now = _buckets[key], time.time()
    while q and q[0] < now - 3600:
        q.popleft()
    if len(q) >= per_hour:
        raise HTTPException(429, "Too many requests. Please slow down and try again shortly.")
    q.append(now)


def owned_profiles(request: Request) -> dict[str, str]:
    raw = request.cookies.get(OWNER_COOKIE, "")
    out = {}
    for part in raw.split("~"):
        if "." in part:
            pid, key = part.split(".", 1)
            out[pid] = key
    return out


def is_owner(request: Request, pid: str, key: str | None = None) -> bool:
    prof = db.get_profile(pid)
    if not prof:
        return False
    k = key or owned_profiles(request).get(pid)
    return bool(k) and k == prof["key"]


def remember_owner(resp, request: Request, pid: str, key: str) -> None:
    owned = owned_profiles(request)
    owned.pop(pid, None)
    items = [(pid, key), *owned.items()][:6]
    resp.set_cookie(OWNER_COOKIE, "~".join(f"{p}.{k}" for p, k in items), max_age=YEAR,
                    httponly=True, samesite="lax", secure=settings.site_url.startswith("https"))


def require_owner(request: Request, body: dict) -> dict:
    pid, key = str(body.get("profile_id") or ""), str(body.get("key") or "")
    prof = db.get_profile(pid)
    if not prof or not (key == prof["key"] or is_owner(request, pid)):
        raise HTTPException(403, "Please take the test first.")
    return dict(prof)


def page(html: str, status: int = 200) -> HTMLResponse:
    return HTMLResponse(html, status_code=status)


def message_page(title: str, text: str, cta: tuple[str, str] | None = None, status: int = 200) -> HTMLResponse:
    return page(render("message.html", title=title, text=text, cta=cta), status)


@app.exception_handler(HTTPException)
async def http_error(request: Request, exc: HTTPException):
    if request.url.path.startswith("/api/"):
        return JSONResponse({"error": exc.detail}, status_code=exc.status_code)
    return message_page("Hmm.", str(exc.detail), ("Go home", "/"), exc.status_code)


def _clip(v: Any, n: int) -> str:
    return str(v or "").strip()[:n]


# ---------- API ----------

@app.get("/api/health")
def health():
    db.q1("SELECT 1")
    return {"ok": True, "ai": settings.has_ai, "safepay": settings.has_safepay}


@app.get("/api/stats/public")
def public_stats():
    return {"tests_taken": stats.public_test_count()}


@app.post("/api/results")
async def create_result(request: Request):
    limit(request, "results", 40)
    body = await request.json()
    test = body.get("test")
    try:
        outcome, scores = scoring.score(test, body.get("answers") or {})
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    pid, key = str(body.get("profile_id") or ""), str(body.get("key") or "")
    prof = db.get_profile(pid) if pid else None
    milan = _clip(body.get("milan"), 16)
    if milan or not prof or prof["key"] != key:
        prof = db.create_profile(name=_clip(body.get("name"), 40), ref=_clip(body.get("ref"), 60),
                                 utm_source=_clip(body.get("utm_source"), 60),
                                 utm_medium=_clip(body.get("utm_medium"), 60),
                                 utm_campaign=_clip(body.get("utm_campaign"), 80))
    elif body.get("name"):
        db.update_profile(prof["id"], name=_clip(body.get("name"), 40))
    db.save_result(prof["id"], test, body.get("answers"), scores, outcome)
    db.log_event("test_complete", prof["id"], props={"test": test, "outcome": outcome})
    redirect = f"/p/{prof['id']}#{test}"
    if milan and test == "personality":
        pair = db.q1("SELECT * FROM pairs WHERE id = ?", milan)
        if pair and not pair["b_profile"] and pair["a_profile"] != prof["id"]:
            db.run("UPDATE pairs SET b_profile = ?, completed_at = ? WHERE id = ?", prof["id"], db.now(), milan)
            db.log_event("milan_completed", prof["id"], props={"pair": milan})
            _notify_milan_partner(dict(pair), prof)
            redirect = f"/milan/{milan}"
    resp = JSONResponse({"profile_id": prof["id"], "key": prof["key"], "outcome": outcome, "redirect": redirect})
    remember_owner(resp, request, prof["id"], prof["key"])
    return resp


def _notify_milan_partner(pair: dict, partner) -> None:
    a = db.get_profile(pair["a_profile"])
    if a and a["email"]:
        link = f"{settings.site_url}/milan/{pair['id']}"
        body = f"<p><b>{notify.esc(partner['name'] or 'Your partner')}</b> just finished the test. Your Mizaj Milan result is ready.</p>"
        notify.email(a["email"], "Your Mizaj Milan match is ready", notify.email_shell("Your match is ready", body, "See our match", link))


@app.post("/api/profile")
async def update_profile(request: Request):
    body = await request.json()
    prof = require_owner(request, body)
    db.update_profile(prof["id"], name=_clip(body.get("name"), 40) or None, email=_clip(body.get("email"), 120) or None,
                      phone=_clip(body.get("phone"), 30) or None, city=_clip(body.get("city"), 40) or None,
                      birth_date=_clip(body.get("birth_date"), 10) or None)
    if body.get("email") or body.get("phone"):
        db.run("INSERT INTO subscribers (profile_id, email, whatsapp, topic, created_at) VALUES (?,?,?,?,?)",
               prof["id"], _clip(body.get("email"), 120), _clip(body.get("phone"), 30), "result", db.now())
        db.log_event("contact_captured", prof["id"])
    return {"ok": True}


@app.post("/api/milan")
async def create_milan(request: Request):
    limit(request, "milan", 30)
    body = await request.json()
    prof = require_owner(request, body)
    if "personality" not in db.latest_results(prof["id"]):
        raise HTTPException(400, "Take the personality test first, then invite your partner.")
    relation = body.get("relation") if body.get("relation") in ("rishta", "spouse", "friend", "sibling", "colleague") else "rishta"
    pid = db.new_id(8)
    db.run("INSERT INTO pairs (id, a_profile, relation, created_at) VALUES (?,?,?,?)", pid, prof["id"], relation, db.now())
    db.log_event("milan_invite", prof["id"], props={"relation": relation})
    return {"pair_id": pid, "invite_url": f"{settings.site_url}/milan/{pid}"}


def _complete_pair(pair_id: str, prof) -> None:
    db.run("UPDATE pairs SET b_profile = ?, completed_at = ? WHERE id = ? AND b_profile IS NULL", prof["id"], db.now(), pair_id)
    db.log_event("milan_completed", prof["id"], props={"pair": pair_id})


@app.post("/api/milan/compare")
async def milan_compare(request: Request):
    """'Compare with them' on someone's shared result: a pair with the shared profile as A."""
    limit(request, "milan", 30)
    body = await request.json()
    target = db.get_profile(_clip(body.get("target"), 16))
    if not target or "personality" not in db.latest_results(target["id"]):
        raise HTTPException(404, "That result isn't available.")
    pid = db.new_id(8)
    db.run("INSERT INTO pairs (id, a_profile, relation, created_at) VALUES (?,?,?,?)", pid, target["id"], "friend", db.now())
    mine = db.get_profile(_clip(body.get("profile_id"), 16))
    if mine and mine["id"] != target["id"] and is_owner(request, mine["id"], _clip(body.get("key"), 40)) \
            and "personality" in db.latest_results(mine["id"]):
        _complete_pair(pid, mine)
        return {"pair_id": pid, "redirect": f"/milan/{pid}"}
    from urllib.parse import quote
    return {"pair_id": pid, "redirect": f"/test/personality/?milan={pid}&from={quote(target['name'] or '')}"}


@app.post("/api/milan/join")
async def milan_join(request: Request):
    """Complete an invite with a result the invitee already has."""
    body = await request.json()
    prof = require_owner(request, body)
    pair = db.q1("SELECT * FROM pairs WHERE id = ?", _clip(body.get("pair_id"), 16))
    if not pair or pair["b_profile"] or pair["a_profile"] == prof["id"]:
        raise HTTPException(400, "This invite is already used.")
    if "personality" not in db.latest_results(prof["id"]):
        raise HTTPException(400, "Take the personality test first.")
    _complete_pair(pair["id"], prof)
    _notify_milan_partner(dict(pair), prof)
    return {"redirect": f"/milan/{pair['id']}"}


@app.post("/api/orders")
async def new_order(request: Request):
    limit(request, "orders", 40)
    body = await request.json()
    prof = require_owner(request, body)
    product = str(body.get("product") or "")
    pair_id = _clip(body.get("pair_id"), 16) or None
    if pair_id:
        pair = db.q1("SELECT * FROM pairs WHERE id = ?", pair_id)
        if not pair or prof["id"] not in (pair["a_profile"], pair["b_profile"]) or not pair["b_profile"]:
            raise HTTPException(400, "That Mizaj Milan pair isn't complete yet.")
    try:
        order = payments.create_order(prof["id"], product, pair_id, _clip(body.get("coupon"), 30) or None)
    except (KeyError, payments.PaymentError) as e:
        raise HTTPException(400, str(e) if isinstance(e, payments.PaymentError) else "Unknown product.") from e
    return {"order_id": order["id"], "url": f"/order/{order['id']}", "amount": order["amount"]}


@app.post("/api/orders/{oid}/proof")
async def order_proof(oid: str, request: Request):
    limit(request, "proof", 20)
    body = await request.json()
    try:
        order = payments.submit_proof(oid, str(body.get("method") or ""), str(body.get("tid") or ""),
                                      str(body.get("sender") or ""), str(body.get("email") or ""), str(body.get("phone") or ""))
    except payments.PaymentError as e:
        raise HTTPException(400, str(e)) from e
    return {"status": order["status"]}


@app.get("/api/orders/{oid}/status")
def order_status(oid: str):
    order = payments.get_order(oid)
    if not order:
        raise HTTPException(404, "Order not found.")
    return {"status": order["status"], "profile_id": order["profile_id"], "pair_id": order["pair_id"]}


@app.post("/api/orders/{oid}/safepay")
def order_safepay(oid: str):
    order = payments.get_order(oid)
    if not order or order["status"] == "paid":
        raise HTTPException(400, "This order can't be paid by card.")
    try:
        return {"redirect": payments.safepay_checkout_url(order)}
    except payments.PaymentError as e:
        raise HTTPException(400, str(e)) from e
    except Exception as e:  # gateway errors must not leak details
        log.exception("safepay init failed")
        raise HTTPException(502, "Card checkout is not responding. Please use Raast, JazzCash or Easypaisa.") from e


@app.post("/api/redeem")
async def redeem(request: Request):
    limit(request, "redeem", 15)
    body = await request.json()
    prof = require_owner(request, body)
    try:
        order = payments.redeem(str(body.get("code") or ""), prof["id"], _clip(body.get("pair_id"), 16) or None)
    except payments.PaymentError as e:
        raise HTTPException(400, str(e)) from e
    return {"status": order["status"], "product": order["product"]}


@app.post("/api/palm")
async def palm(request: Request, image: UploadFile = File(...), hand: str = Form("right"),
               profile_id: str = Form(""), key: str = Form("")):
    limit(request, "palm", 6)
    prof = db.get_profile(profile_id) if profile_id else None
    if not prof or not (prof["key"] == key or is_owner(request, profile_id)):
        prof = db.create_profile()
    raw = await image.read(8 * 1024 * 1024 + 1)
    if len(raw) > 8 * 1024 * 1024:
        raise HTTPException(413, "That photo is too large. Please use one under 8 MB.")
    pers = db.latest_results(prof["id"]).get("personality")
    try:
        reading = ai.read_palm(raw, "left" if hand == "left" else "right", prof["name"], pers["outcome"] if pers else None)
    except ai.AIError as e:
        raise HTTPException(400, str(e)) from e
    if not reading.get("is_palm"):
        return JSONResponse({"is_palm": False, "retake_tip": reading.get("retake_tip")})
    palm_id = db.new_id(10)
    db.run("INSERT INTO palm (id, profile_id, hand, reading, created_at) VALUES (?,?,?,?,?)",
           palm_id, prof["id"], hand, db.dumps(reading), db.now())
    db.log_event("palm_read", prof["id"])
    resp = JSONResponse({"is_palm": True, "palm_id": palm_id, "url": f"/palm/{palm_id}",
                         "profile_id": prof["id"], "key": prof["key"]})
    remember_owner(resp, request, prof["id"], prof["key"])
    return resp


@app.post("/api/leads")
async def lead(request: Request):
    limit(request, "leads", 10)
    body = await request.json()
    kind = body.get("kind") if body.get("kind") in ("school", "team", "partner", "creator", "contact") else "contact"
    f = {k: _clip(body.get(k), 300 if k == "message" else 80) for k in
         ("name", "org", "role", "phone", "email", "city", "size", "message")}
    if not (f["phone"] or f["email"]):
        raise HTTPException(400, "Please leave a phone number or email so we can reach you.")
    db.run("""INSERT INTO leads (kind, name, org, role, phone, email, city, size, message, created_at)
              VALUES (?,?,?,?,?,?,?,?,?,?)""", kind, *f.values(), db.now())
    notify.telegram(f"📇 <b>New {kind} lead</b>\n" + "\n".join(f"{k}: {notify.esc(v)}" for k, v in f.items() if v))
    db.log_event("lead", props={"kind": kind})
    return {"ok": True}


@app.post("/api/subscribe")
async def subscribe(request: Request):
    limit(request, "subscribe", 20)
    body = await request.json()
    email, wa = _clip(body.get("email"), 120), _clip(body.get("whatsapp"), 30)
    if not (email or wa):
        raise HTTPException(400, "Please enter an email or WhatsApp number.")
    db.run("INSERT INTO subscribers (profile_id, email, whatsapp, topic, created_at) VALUES (?,?,?,?,?)",
           _clip(body.get("profile_id"), 16) or None, email, wa, _clip(body.get("topic"), 40), db.now())
    return {"ok": True}


ALLOWED_EVENTS = {"page_view", "test_start", "test_progress", "result_view", "share_click", "checkout_view",
                  "pay_method", "palm_start", "milan_share", "pricing_view", "cta_click", "lang_switch"}


@app.post("/api/events")
async def events(request: Request):
    limit(request, "events", 600)
    try:
        body = await request.json()
    except ValueError:
        return {"ok": False}
    name = str(body.get("name") or "")
    if name in ALLOWED_EVENTS:
        props = body.get("props") if isinstance(body.get("props"), dict) else {}
        db.log_event(name, _clip(body.get("profile_id"), 16) or None, _clip(body.get("path"), 200),
                     _clip(body.get("ref"), 200), {k: str(v)[:60] for k, v in list(props.items())[:8]})
    return {"ok": True}


@app.get("/api/fun/zodiac")
def fun_zodiac(dob: str, type: str = ""):
    try:
        d = date.fromisoformat(dob)
    except ValueError as e:
        raise HTTPException(400, "Please enter a valid date.") from e
    sign = reports.zodiac_for(d)
    out = {"sign": sign, "birth_number": reports.birth_number(d), "disclaimer": content.zodiac().get("disclaimer")}
    code = type.upper()
    if code in content.TYPE_CODES:
        out["mashup"] = sign.get("type_mashups", {}).get(code)
        out["type"] = content.type_summary(code)
    return out


@app.get("/api/fun/numerology")
def fun_numerology(name: str, dob: str = ""):
    name = name.strip()[:60]
    if not name:
        raise HTTPException(400, "Please enter a name.")
    out = {"name": name, "name_number": reports.name_number(name), "disclaimer": content.numerology().get("disclaimer")}
    if dob:
        try:
            out["birth_number"] = reports.birth_number(date.fromisoformat(dob))
        except ValueError:
            pass
    return out


@app.post("/api/webhooks/lemonsqueezy")
async def ls_webhook(request: Request):
    raw = await request.body()
    try:
        payload = await request.json()
    except ValueError:
        raise HTTPException(400, "bad json")
    if not payments.lemonsqueezy_webhook(raw, request.headers.get("x-signature", ""), payload):
        raise HTTPException(401, "bad signature")
    return {"ok": True}


# ---------- dynamic pages ----------

@app.get("/p/{pid}", response_class=HTMLResponse)
def result_page(pid: str, request: Request):
    prof = db.get_profile(pid)
    if not prof:
        raise HTTPException(404, "We couldn't find that result.")
    owner = is_owner(request, pid)
    view = reports.profile_view(dict(prof), owner)
    if not view["results"]:
        raise HTTPException(404, "This profile has no results yet.")
    pers = view["results"].get("personality")
    mz = view["results"].get("mizaj")
    og = f"{settings.site_url}/og/types/{pers['code'].lower()}.png" if pers else (
        f"{settings.site_url}/og/mizaj/{mz['key']}.png" if mz else None)
    title = (f"{prof['name'] + ' is' if prof['name'] else 'I am'} {pers['code']}: {pers['name']}" if pers
             else f"My mizaj is {mz['name']}")
    db.log_event("result_view", pid, path=f"/p/{pid}", props={"owner": owner})
    pairs = [dict(r) for r in db.q("SELECT * FROM pairs WHERE a_profile = ? OR b_profile = ? ORDER BY created_at DESC",
                                    pid, pid)] if owner else []
    palms = [dict(r) for r in db.q("SELECT id, created_at FROM palm WHERE profile_id = ? ORDER BY created_at DESC", pid)] if owner else []
    return page(render("result.html", view=view, owner=owner, profile=dict(prof) if owner else {"id": pid, "name": prof["name"]},
                       pairs=pairs, palms=palms, title=title, og_image=og,
                       description=(pers or mz)["tagline"], noindex=True))


@app.get("/report/{pid}")
def report_link(pid: str, k: str, request: Request):
    prof = db.get_profile(pid)
    if not prof or prof["key"] != k:
        raise HTTPException(404, "This report link isn't valid.")
    resp = RedirectResponse(f"/p/{pid}#report", status_code=303)
    remember_owner(resp, request, pid, k)
    return resp


@app.get("/milan/{pair_id}", response_class=HTMLResponse)
def milan_page(pair_id: str, request: Request):
    pair = db.q1("SELECT * FROM pairs WHERE id = ?", pair_id)
    if not pair:
        raise HTTPException(404, "This Mizaj Milan link isn't valid.")
    pair = dict(pair)
    inviter = db.get_profile(pair["a_profile"])
    owned = owned_profiles(request)
    member = next((m for m in (pair["a_profile"], pair["b_profile"]) if m and m in owned and is_owner(request, m)), None)
    if not pair["b_profile"]:
        return page(render("milan_invite.html", pair=pair, inviter_name=inviter["name"] if inviter else "",
                           is_inviter=member == pair["a_profile"], title="Mizaj Milan invite",
                           description="Take the free test and see how well you match.", noindex=True))
    unlocked = reports.pair_unlocked(pair)
    view = reports.couple_view(pair, premium=bool(member) and unlocked)
    db.log_event("milan_view", member, props={"pair": pair_id, "unlocked": unlocked})
    return page(render("milan.html", view=view, member=member, unlocked=unlocked, pair=pair,
                       key=owned.get(member) if member else None, title="Mizaj Milan",
                       description="Our personality and temperament match.", noindex=True))


@app.get("/order/{oid}", response_class=HTMLResponse)
def order_page(oid: str, request: Request):
    order = payments.get_order(oid)
    if not order:
        raise HTTPException(404, "Order not found.")
    if not is_owner(request, order["profile_id"]):
        raise HTTPException(403, "Please open this page on the phone where you took the test.")
    prof = db.get_profile(order["profile_id"])
    db.log_event("checkout_view", order["profile_id"], props={"product": order["product"]})
    return page(render("order.html", order=order, product=content.product(order["product"]), profile=dict(prof),
                       methods=settings.manual_methods(), card=settings.has_safepay,
                       usd_link=payments.lemonsqueezy_url(order), title="Checkout", noindex=True,
                       request_card_failed=request.query_params.get("card") == "failed"))


@app.get("/pay/safepay/return")
def safepay_return(order: str, tracker: str = "", sig: str = ""):
    ok = payments.safepay_verify_return(order, tracker, sig)
    return RedirectResponse(f"/order/{order}" + ("" if ok else "?card=failed"), status_code=303)


@app.get("/palm/{palm_id}", response_class=HTMLResponse)
def palm_page(palm_id: str, request: Request):
    row = db.q1("SELECT * FROM palm WHERE id = ?", palm_id)
    if not row:
        raise HTTPException(404, "Reading not found.")
    owner = is_owner(request, row["profile_id"])
    premium = owner and "palm" in reports.entitlements(row["profile_id"])
    view = ai.palm_view(db.loads(row["reading"], {}), premium)
    prof = db.get_profile(row["profile_id"])
    return page(render("palm_reading.html", view=view, owner=owner, premium=premium, palm_id=palm_id,
                       profile=dict(prof) if owner else None, title="My AI palm reading",
                       description=view.get("headline") or "An AI palm reading, for fun.", noindex=True))


# ---------- admin ----------

def is_admin(request: Request) -> bool:
    return bool(settings.admin_token) and request.cookies.get(ADMIN_COOKIE) == notify.sign("admin", settings.admin_token)


@app.get("/admin", response_class=HTMLResponse)
def admin_home(request: Request):
    if not is_admin(request):
        return page(render("admin_login.html", title="Admin", noindex=True))
    return page(render("admin.html", s=stats.dashboard(), title="Admin", noindex=True,
                       pending=[dict(r) for r in db.q("SELECT * FROM orders WHERE status = 'proof' ORDER BY created_at")],
                       recent=[dict(r) for r in db.q("SELECT * FROM orders WHERE status IN ('paid','rejected') ORDER BY updated_at DESC LIMIT 25")],
                       leads=[dict(r) for r in db.q("SELECT * FROM leads ORDER BY created_at DESC LIMIT 25")],
                       sign=notify.sign))


@app.post("/admin/login")
async def admin_login(request: Request, token: str = Form(...)):
    limit(request, "admin_login", 10)
    if not settings.admin_token or token != settings.admin_token:
        raise HTTPException(403, "Wrong token.")
    resp = RedirectResponse("/admin", status_code=303)
    resp.set_cookie(ADMIN_COOKIE, notify.sign("admin", settings.admin_token), max_age=60 * 60 * 24 * 30,
                    httponly=True, samesite="strict", secure=settings.site_url.startswith("https"))
    return resp


@app.get("/admin/order/{oid}", response_class=HTMLResponse)
def admin_order_confirm(oid: str, a: str, s: str):
    if a not in ("approve", "reject") or not notify.verify(s, oid, a):
        raise HTTPException(403, "This link is not valid.")
    order = payments.get_order(oid)
    if not order:
        raise HTTPException(404, "Order not found.")
    return page(render("admin_confirm.html", order=order, action=a, sig=s,
                       product=content.product(order["product"]), title="Confirm", noindex=True))


@app.post("/admin/order/{oid}")
def admin_order_act(oid: str, request: Request, a: str = Form(...), s: str = Form(""), reason: str = Form("")):
    if not (notify.verify(s, oid, a) or is_admin(request)):
        raise HTTPException(403, "Not allowed.")
    if a == "approve":
        order = payments.mark_paid(oid)
        msg = "Approved. The customer's report is now unlocked."
    elif a == "reject":
        order = payments.reject(oid, reason)
        msg = "Rejected. The report is locked and the customer was told (if they left an email)."
    else:
        raise HTTPException(400, "Unknown action.")
    if not order:
        raise HTTPException(404, "Order not found.")
    return message_page("Done", msg, ("Open admin", "/admin"))


@app.post("/admin/codes", response_class=HTMLResponse)
def admin_codes(request: Request, product: str = Form(...), count: int = Form(1), kind: str = Form("unlock"),
                discount_pct: int = Form(0), uses: int = Form(1), org: str = Form(""), prefix: str = Form("MZ")):
    if not is_admin(request):
        raise HTTPException(403, "Not allowed.")
    codes = payments.create_codes(product, max(1, min(count, 500)), kind, max(0, min(discount_pct, 100)),
                                  max(1, uses), org[:80], prefix=(prefix or "MZ")[:8].upper())
    return page(render("admin_codes.html", codes=codes, product=product, org=org, title="Codes", noindex=True))


@app.get("/admin/leads.csv", response_class=PlainTextResponse)
def admin_leads_csv(request: Request):
    if not is_admin(request):
        raise HTTPException(403, "Not allowed.")
    rows = db.q("SELECT * FROM leads ORDER BY created_at DESC")
    head = "id,kind,name,org,role,phone,email,city,size,status,created\n"
    return head + "".join(",".join(f'"{str(r[k] or "").replace(chr(34), "")}"' for k in
                                   ("id", "kind", "name", "org", "role", "phone", "email", "city", "size", "status")) +
                          f",{time.strftime('%Y-%m-%d', time.localtime(r['created_at']))}\n" for r in rows)


# Static files (dev only; Caddy serves dist/ in production). Mounted last so routes win.
if settings.dist_dir.exists():
    app.mount("/", StaticFiles(directory=str(settings.dist_dir), html=True), name="static")
