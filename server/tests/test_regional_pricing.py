"""T40 regional pricing: buyers in Pakistan pay the PKR price; everyone else pays the USD price,
charged by Safepay in PKR at USD_PKR_RATE (rounded up to the nearest 10)."""
import hashlib
import hmac
import math
import sqlite3

import pytest
from fastapi.testclient import TestClient

from mizaj import config, content, db, payments, web
from mizaj.api import app
from mizaj.config import settings


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.setattr(settings, "usd_pkr_rate", 280.0)  # the default, whatever the local env says
    return TestClient(app)


def expected_intl(usd: float, rate: float) -> int:
    return math.ceil(round(usd * rate) / 10) * 10


def _profile(client) -> dict:
    answers = {it["id"]: 3 for it in content.questions("personality")["items"]}
    r = client.post("/api/results", json={"test": "personality", "answers": answers})
    assert r.status_code == 200, r.text
    return r.json()


def _order(client, p: dict, product: str = "full", **extra) -> dict:
    r = client.post("/api/orders", json={"profile_id": p["profile_id"], "key": p["key"], "product": product, **extra})
    assert r.status_code == 200, r.text
    return payments.get_order(r.json()["order_id"])


def test_rate_setting_comes_from_env(monkeypatch):
    monkeypatch.setenv("USD_PKR_RATE", "300.5")
    assert config.Settings().usd_pkr_rate == 300.5
    for bad in ("", "abc", "0", "-5"):
        monkeypatch.setenv("USD_PKR_RATE", bad)
        assert config.Settings().usd_pkr_rate == 280.0
    monkeypatch.delenv("USD_PKR_RATE")
    assert config.Settings().usd_pkr_rate == 280.0


def test_pk_order_keeps_the_pkr_price(client):
    p = _profile(client)
    for product in ("full", "palm", "career", "bundle"):
        o = _order(client, p, product, region="pk")
        assert o["amount"] == content.product(product)["price"]
        assert o["currency"] == "PKR" and o["region"] == "pk"


def test_missing_or_unknown_region_defaults_to_pk(client):
    p = _profile(client)
    for extra in ({}, {"region": None}, {"region": ""}, {"region": "mars"}):
        o = _order(client, p, **extra)
        assert o["amount"] == content.product("full")["price"] and o["region"] == "pk"
    assert payments.create_order(p["profile_id"], "palm")["region"] == "pk"  # callers that don't pass a region


def test_intl_order_is_the_usd_price_in_pkr(client):
    p = _profile(client)
    for product in ("full", "palm", "career", "bundle"):
        o = _order(client, p, product, region="intl")
        assert o["amount"] == expected_intl(content.product(product)["usd"], 280.0)
        assert o["currency"] == "PKR" and o["region"] == "intl"
    r = client.post("/api/orders", json={"profile_id": p["profile_id"], "key": p["key"], "product": "full", "region": "INTL"})
    assert r.json()["region"] == "intl" and r.json()["amount"] == expected_intl(content.product("full")["usd"], 280.0)


def test_intl_amount_uses_the_rate_setting_and_rounds_up_to_10(client, monkeypatch):
    p = _profile(client)
    full, career = content.product("full"), content.product("career")
    monkeypatch.setattr(settings, "usd_pkr_rate", 281.0)
    assert _order(client, p, "full", region="intl")["amount"] == expected_intl(full["usd"], 281.0)
    assert _order(client, p, "career", region="intl")["amount"] == expected_intl(career["usd"], 281.0)
    monkeypatch.setattr(settings, "usd_pkr_rate", 300.0)
    assert _order(client, p, "full", region="intl")["amount"] == expected_intl(full["usd"], 300.0)
    assert _order(client, p, "full", region="pk")["amount"] == full["price"]  # the rate never touches PKR prices
    # the rounding itself
    assert payments.usd_to_pkr(9, 281) == 2530       # 2529 -> 2530
    assert payments.usd_to_pkr(9, 280) == 2520       # already a multiple of 10
    assert payments.usd_to_pkr(9, 283.34) == 2550    # 2550.06 -> 2550
    assert payments.usd_to_pkr(9, 283.4) == 2560     # 2550.6 -> 2551 -> 2560
    assert payments.usd_to_pkr(14, 281) == 3940      # 3934 -> 3940


def test_discount_code_applies_the_same_way_in_both_regions(client):
    p = _profile(client)
    disc = payments.create_codes("*", 1, kind="discount", discount_pct=20, uses=5)[0]
    pk = _order(client, p, "bundle", coupon=disc, region="pk")
    intl = _order(client, p, "bundle", coupon=disc, region="intl")
    assert pk["amount"] == round(content.product("bundle")["price"] * 0.8) and pk["coupon"] == disc
    assert intl["amount"] == round(expected_intl(content.product("bundle")["usd"], 280.0) * 0.8) and intl["coupon"] == disc
    # a code for another product does nothing in either region
    palm_only = payments.create_codes("palm", 1, kind="discount", discount_pct=50, uses=5)[0]
    for region in ("pk", "intl"):
        o = _order(client, p, "full", coupon=palm_only, region=region)
        assert o["amount"] == payments.base_price("full", region) and o["coupon"] is None
    # the international checkout shows the discounted dollar price
    discounted = content.product("bundle")["usd"] * 80 / 100
    assert payments.usd_price(intl) == discounted
    assert web._usd(discounted) in client.get(f"/order/{intl['id']}").text


def test_intl_checkout_shows_dollars_and_card_only(client, monkeypatch):
    monkeypatch.setattr(settings, "safepay_api_key", "sp-key")  # card checkout switched on
    p = _profile(client)
    o = _order(client, p, "full", region="intl")
    full = content.product("full")
    r = client.get(f"/order/{o['id']}")
    assert r.status_code == 200
    page = r.text
    assert f">${full['usd']}</b>" in page
    assert f"Charged as PKR {o['amount']:,} by Safepay; your bank converts it." in page
    assert "data-safepay" in page
    assert "data-proof" not in page and "JazzCash" not in page and "Raast" not in page
    assert f"PKR {full['price']:,}" not in page  # the Pakistan price isn't offered abroad

    # Safepay not switched on: the WhatsApp/help fallback, still no manual methods
    monkeypatch.setattr(settings, "safepay_api_key", "")
    page = client.get(f"/order/{o['id']}").text
    assert "Card checkout is opening very soon" in page and "data-safepay" not in page
    assert f"Charged as PKR {o['amount']:,}; your bank converts it." in page
    assert "data-proof" not in page and "JazzCash" not in page

    # proof is still accepted if someone abroad pays a Pakistani relative's way
    r = client.post(f"/api/orders/{o['id']}/proof", json={"method": "jazzcash", "tid": "INTL00000001", "sender": "Cousin"})
    assert r.status_code == 200 and r.json()["status"] == "proof"


def test_pk_checkout_is_unchanged(client):
    p = _profile(client)
    o = _order(client, p, "full", region="pk")
    page = client.get(f"/order/{o['id']}").text
    assert "data-proof" in page and "JazzCash" in page and "Raast" in page
    assert f'<span class="cur-pkr">PKR {o["amount"]:,}</span>' in page and "Charged as" not in page
    # orders from before regional pricing (region NULL) are Pakistan orders
    db.run("UPDATE orders SET region = NULL WHERE id = ?", o["id"])
    page = client.get(f"/order/{o['id']}").text
    assert "data-proof" in page and "Charged as" not in page


def test_safepay_checkout_charges_the_stored_amount(client, monkeypatch):
    monkeypatch.setattr(settings, "usd_pkr_rate", 281.0)
    monkeypatch.setattr(settings, "safepay_api_key", "sp-key")
    sent, alerts = [], []

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"data": {"token": f"track_{len(sent)}"}}

    def fake_post(url, **kw):
        sent.append(kw["json"])
        return FakeResponse()

    monkeypatch.setattr(payments.httpx, "post", fake_post)
    monkeypatch.setattr(payments.notify, "telegram", lambda text, buttons=None: alerts.append(text) or True)
    p = _profile(client)
    o = _order(client, p, "full", region="intl")
    monkeypatch.setattr(settings, "usd_pkr_rate", 400.0)  # a later rate change doesn't reprice an open order
    r = client.post(f"/api/orders/{o['id']}/safepay")
    assert r.status_code == 200, r.text
    assert sent[-1]["amount"] == float(o["amount"]) == float(expected_intl(content.product("full")["usd"], 281.0))
    assert sent[-1]["currency"] == "PKR"
    tracker = payments.get_order(o["id"])["gateway_ref"]
    assert f"beacon={tracker}" in r.json()["redirect"]

    # paying marks it paid, and the owner's alert prints the PKR amount actually charged
    sig = hmac.new(b"sp-secret", tracker.encode(), hashlib.sha256).hexdigest()
    client.get(f"/pay/safepay/return?order={o['id']}&tracker={tracker}&sig={sig}", follow_redirects=False)
    paid = payments.get_order(o["id"])
    assert paid["status"] == "paid" and paid["region"] == "intl" and paid["amount"] == o["amount"]
    assert f"PKR {o['amount']:,}" in alerts[-1]

    pk = _order(client, p, "full", region="pk")
    client.post(f"/api/orders/{pk['id']}/safepay")
    assert sent[-1]["amount"] == float(content.product("full")["price"])


def test_region_column_is_added_to_an_existing_database(tmp_path, monkeypatch):
    old = sqlite3.connect(tmp_path / "mizaj.db")
    old.executescript("""
      CREATE TABLE orders (id TEXT PRIMARY KEY, profile_id TEXT NOT NULL, pair_id TEXT, product TEXT NOT NULL,
        amount INTEGER NOT NULL, currency TEXT NOT NULL DEFAULT 'PKR', method TEXT, status TEXT NOT NULL,
        tid TEXT, sender TEXT, coupon TEXT, gateway_ref TEXT, note TEXT, email TEXT, phone TEXT,
        created_at REAL NOT NULL, updated_at REAL NOT NULL, paid_at REAL);
      INSERT INTO orders (id, profile_id, product, amount, status, created_at, updated_at)
        VALUES ('old1', 'p1', 'full', 599, 'paid', 0, 0);""")
    old.commit()
    old.close()
    monkeypatch.setattr(settings, "data_dir", tmp_path)
    db.reset_for_tests()
    try:
        assert "region" in {r["name"] for r in db.q("PRAGMA table_info(orders)")}
        assert payments.get_order("old1")["region"] is None and payments.get_order("old1")["amount"] == 599
        db.reset_for_tests()
        db.connect()  # a second start is a no-op
        assert [r["name"] for r in db.q("PRAGMA table_info(orders)")].count("region") == 1
    finally:
        db.reset_for_tests()
