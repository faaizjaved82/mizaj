import hashlib
import hmac
import json

import pytest
from fastapi.testclient import TestClient

from mizaj import content, db, notify, payments, scoring
from mizaj.api import app


def answers_for(code: str) -> dict:
    """Answers that produce the given 4-letter type."""
    out = {}
    for it in content.questions("personality")["items"]:
        idx = list(content.DIMENSIONS).index(it["dim"])
        want_first = code[idx] == content.DIMENSIONS[it["dim"]]["a"]
        agree = (it["key"] == 1) == want_first
        out[it["id"]] = 5 if agree else 1
    return out


def mizaj_answers(target: str) -> dict:
    sign = {"damvi": (1, 1), "safravi": (1, -1), "balghami": (-1, 1), "saudavi": (-1, -1)}[target]
    out = {}
    for it in content.questions("mizaj")["items"]:
        best = max(range(len(it["options"])), key=lambda i: sign[0] * it["options"][i].get("h", 0) + sign[1] * it["options"][i].get("m", 0))
        out[it["id"]] = best
    return out


@pytest.fixture()
def client():
    return TestClient(app)


AVAILABLE = [c for c in content.TYPE_CODES if (content.settings.content_dir / "types" / f"{c}.json").exists()]


@pytest.mark.parametrize("code", content.TYPE_CODES)
def test_personality_scoring_hits_every_type(code):
    got, scores = scoring.score_personality(answers_for(code))
    assert got == code
    assert all(scores["dims"][d]["strength"] == 100 for d in scores["dims"])


@pytest.mark.parametrize("key", content.MIZAJ_KEYS)
def test_mizaj_scoring_hits_every_quadrant(key):
    got, scores = scoring.score_mizaj(mizaj_answers(key))
    assert got == key
    assert -100 <= scores["heat"] <= 100 and -100 <= scores["moisture"] <= 100


def test_neutral_answers_are_valid():
    code, _ = scoring.score_personality({it["id"]: 3 for it in content.questions("personality")["items"]})
    assert len(code) == 4
    key, s = scoring.score_mizaj({it["id"]: 0 for it in content.questions("mizaj")["items"]})
    assert key in content.MIZAJ_KEYS


def test_too_few_answers_rejected():
    with pytest.raises(scoring.ScoringError):
        scoring.score_personality({"p01": 5})


def test_full_purchase_flow(client):
    code = AVAILABLE[0]
    r = client.post("/api/results", json={"test": "personality", "answers": answers_for(code), "name": "Ayesha", "utm_source": "tiktok"})
    assert r.status_code == 200, r.text
    res = r.json()
    pid, key = res["profile_id"], res["key"]
    assert res["outcome"] == code

    r = client.post("/api/results", json={"test": "mizaj", "answers": mizaj_answers("saudavi"), "profile_id": pid, "key": key})
    assert r.json()["profile_id"] == pid

    page = client.get(f"/p/{pid}")
    assert page.status_code == 200 and code in page.text and "Saudavi" in page.text
    assert "Unlock your Full Mizaj Report" in page.text
    premium_marker = content.type_profile(code)["premium"]["superpowers"][0]["title"]
    assert premium_marker not in page.text

    # a stranger sees the free view only
    stranger = TestClient(app)
    pub = stranger.get(f"/p/{pid}")
    assert pub.status_code == 200 and "Compare with Ayesha" in pub.text and "data-buy" not in pub.text

    r = client.post("/api/orders", json={"profile_id": pid, "key": key, "product": "full"})
    assert r.status_code == 200, r.text
    oid = r.json()["order_id"]
    assert r.json()["amount"] == content.product("full")["price"]
    assert client.get(f"/order/{oid}").status_code == 200
    assert stranger.get(f"/order/{oid}").status_code == 403

    r = client.post(f"/api/orders/{oid}/proof", json={"method": "jazzcash", "tid": "bad tid!", "sender": "Ali"})
    assert r.status_code == 400
    r = client.post(f"/api/orders/{oid}/proof", json={"method": "jazzcash", "tid": "12345678901", "sender": "Ali", "email": "a@example.com"})
    assert r.json()["status"] == "proof"

    # same TID can't be reused on another order
    oid2 = client.post("/api/orders", json={"profile_id": pid, "key": key, "product": "palm"}).json()["order_id"]
    r = client.post(f"/api/orders/{oid2}/proof", json={"method": "jazzcash", "tid": "12345678901", "sender": "Ali"})
    assert r.status_code == 400

    # owner approves from the Telegram link
    sig = notify.sign(oid, "approve")
    assert client.get(f"/admin/order/{oid}?a=approve&s={sig}").status_code == 200
    assert client.get(f"/admin/order/{oid}?a=approve&s=forged").status_code == 403
    r = stranger.post(f"/admin/order/{oid}", data={"a": "approve", "s": sig})
    assert r.status_code == 200
    assert client.get(f"/api/orders/{oid}/status").json()["status"] == "paid"

    page = client.get(f"/p/{pid}")
    assert premium_marker in page.text
    assert "Foods to favour" in page.text
    assert stranger.get(f"/p/{pid}").text.count(premium_marker) == 0

    # report link restores ownership on another device
    other = TestClient(app)
    r = other.get(f"/report/{pid}?k={key}", follow_redirects=False)
    assert r.status_code == 303
    assert premium_marker in other.get(f"/p/{pid}").text


def test_milan_flow_and_codes(client):
    a_code, b_code = AVAILABLE[0], AVAILABLE[-1]
    a = client.post("/api/results", json={"test": "personality", "answers": answers_for(a_code), "name": "Sara"}).json()
    pair = client.post("/api/milan", json={"profile_id": a["profile_id"], "key": a["key"], "relation": "rishta"}).json()
    pair_id = pair["pair_id"]
    assert client.get(f"/milan/{pair_id}").status_code == 200

    partner = TestClient(app)
    b = partner.post("/api/results", json={"test": "personality", "answers": answers_for(b_code), "name": "Bilal", "milan": pair_id}).json()
    assert b["redirect"] == f"/milan/{pair_id}"
    assert b["profile_id"] != a["profile_id"]
    view = partner.get(f"/milan/{pair_id}")
    assert view.status_code == 200 and "Overall Mizaj Milan score" in view.text and "Unlock for both of us" in view.text

    # a school code unlocks the couple report for both
    code = payments.create_codes("couple", 1, org="Test School")[0]
    r = partner.post("/api/redeem", json={"profile_id": b["profile_id"], "key": b["key"], "code": code, "pair_id": pair_id})
    assert r.status_code == 200, r.text
    assert "How to love each other well" in client.get(f"/milan/{pair_id}").text
    r = partner.post("/api/redeem", json={"profile_id": b["profile_id"], "key": b["key"], "code": code, "pair_id": pair_id})
    assert r.status_code == 400  # single use

    # compare from a shared result: stranger with an existing result joins instantly
    c = TestClient(app)
    cres = c.post("/api/results", json={"test": "personality", "answers": answers_for(b_code), "name": "Zain"}).json()
    r = c.post("/api/milan/compare", json={"target": a["profile_id"], "profile_id": cres["profile_id"], "key": cres["key"]})
    assert r.json()["redirect"].startswith("/milan/")
    r = TestClient(app).post("/api/milan/compare", json={"target": a["profile_id"]})
    assert r.json()["redirect"].startswith("/test/personality/?milan=")


def test_discount_code_and_bundle(client):
    code = AVAILABLE[1]
    p = client.post("/api/results", json={"test": "personality", "answers": answers_for(code)}).json()
    disc = payments.create_codes("*", 1, kind="discount", discount_pct=20, uses=5)[0]
    r = client.post("/api/orders", json={"profile_id": p["profile_id"], "key": p["key"], "product": "bundle", "coupon": disc})
    assert r.json()["amount"] == round(content.product("bundle")["price"] * 0.8)


def test_gateway_signatures(client):
    p = client.post("/api/results", json={"test": "personality", "answers": answers_for(AVAILABLE[0])}).json()
    oid = client.post("/api/orders", json={"profile_id": p["profile_id"], "key": p["key"], "product": "full"}).json()["order_id"]
    db.run("UPDATE orders SET gateway_ref = 'track_123' WHERE id = ?", oid)
    good = hmac.new(b"sp-secret", b"track_123", hashlib.sha256).hexdigest()
    assert client.get(f"/pay/safepay/return?order={oid}&tracker=track_123&sig=bad", follow_redirects=False).status_code == 303
    assert payments.get_order(oid)["status"] == "created"
    client.get(f"/pay/safepay/return?order={oid}&tracker=track_123&sig={good}", follow_redirects=False)
    assert payments.get_order(oid)["status"] == "paid"

    oid2 = client.post("/api/orders", json={"profile_id": p["profile_id"], "key": p["key"], "product": "career"}).json()["order_id"]
    body = json.dumps({"meta": {"event_name": "order_created", "custom_data": {"order_id": oid2}},
                       "data": {"id": "99", "attributes": {"status": "paid", "total": 1400}}}).encode()
    bad = client.post("/api/webhooks/lemonsqueezy", content=body, headers={"x-signature": "nope", "content-type": "application/json"})
    assert bad.status_code == 401
    sig = hmac.new(b"ls-secret", body, hashlib.sha256).hexdigest()
    ok = client.post("/api/webhooks/lemonsqueezy", content=body, headers={"x-signature": sig, "content-type": "application/json"})
    assert ok.status_code == 200
    o = payments.get_order(oid2)
    assert o["status"] == "paid" and o["currency"] == "USD" and o["amount"] == 14


def test_misc_endpoints(client):
    assert client.get("/api/health").json()["ok"]
    assert client.post("/api/leads", json={"kind": "school", "name": "Principal", "phone": "0300"}).json()["ok"]
    assert client.post("/api/leads", json={"kind": "school"}).status_code == 400
    z = client.get("/api/fun/zodiac?dob=2001-08-05&type=INTJ").json()
    assert z["sign"]["key"] == "leo" and z["mashup"]
    assert client.get("/api/fun/zodiac?dob=2000-12-25").json()["sign"]["key"] == "capricorn"
    assert client.get("/api/fun/zodiac?dob=2000-01-05").json()["sign"]["key"] == "capricorn"
    n = client.get("/api/fun/numerology?name=محمد").json()["name_number"]
    assert n["system"] == "abjad" and n["total"] == 92 and n["number"] == 11
    assert client.post("/api/events", json={"name": "page_view", "path": "/"}).json()["ok"]
    assert client.get("/admin").status_code == 200
    r = client.post("/admin/login", data={"token": "admin-secret"}, follow_redirects=False)
    assert r.status_code == 303
    dash = client.get("/admin")
    assert "Payments to verify" in dash.text


def test_palm_without_ai_key_is_graceful(client):
    from PIL import Image
    import io
    buf = io.BytesIO(); Image.new("RGB", (40, 40), "white").save(buf, "JPEG")
    r = client.post("/api/palm", files={"image": ("p.jpg", buf.getvalue(), "image/jpeg")}, data={"hand": "right"})
    assert r.status_code == 400 and "soon" in r.json()["error"]
