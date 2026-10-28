"""Gumroad checkout links and the Ping webhook (T33). Gumroad's API is faked: no network."""
import html
from urllib.parse import unquote

import httpx
import pytest
from fastapi.testclient import TestClient

from mizaj import db, notify, payments
from mizaj.api import app
from mizaj.config import settings

SELLER = "seller-abc123"
SECRET = "ping-secret-for-tests"
BASE = "https://mizaj.gumroad.com/l/"
LINKS = ",".join(f"{p}={BASE}mizaj-{p}" for p in ("full", "career", "couple", "palm", "bundle"))
PING_URL = f"/api/webhooks/gumroad/{SECRET}"


class FakeGumroad:
    """Stands in for httpx.get against https://api.gumroad.com/v2/sales/<id>."""

    def __init__(self):
        self.sales: dict[str, dict] = {}
        self.calls: list[tuple[str, dict]] = []
        self.down = False
        self.alerts: list[tuple[str, list | None]] = []

    def add(self, sale_id: str, product: str = "full", price: int = 900, **extra) -> None:
        self.sales[sale_id] = {"id": sale_id, "seller_id": SELLER, "product_id": f"prod-{product}",
                               "product_permalink": f"rnd{product}", "price": price, "currency": "usd",
                               "refunded": False, "partially_refunded": False, "chargedback": False, **extra}

    def get(self, url, headers=None, timeout=None, **kw):
        self.calls.append((url, headers or {}))
        if self.down:
            raise httpx.ConnectError("unreachable")
        sale = self.sales.get(unquote(url.rsplit("/", 1)[-1]))
        body = {"success": True, "sale": sale} if sale else {"success": False, "message": "The sale was not found."}
        return httpx.Response(200, json=body, request=httpx.Request("GET", url))

    def texts(self) -> str:
        return html.unescape("\n".join(t for t, _ in self.alerts))


@pytest.fixture()
def gumroad(monkeypatch):
    monkeypatch.setattr(settings, "gumroad_links", LINKS)
    monkeypatch.setattr(settings, "gumroad_seller_id", SELLER)
    monkeypatch.setattr(settings, "gumroad_ping_secret", SECRET)
    monkeypatch.setattr(settings, "gumroad_access_token", "token-for-tests")
    fake = FakeGumroad()
    monkeypatch.setattr(payments.httpx, "get", fake.get)
    monkeypatch.setattr(notify, "telegram", lambda text, buttons=None: fake.alerts.append((text, buttons)) or True)
    return fake


@pytest.fixture()
def client():
    return TestClient(app)


def new_order(product: str = "full") -> dict:
    prof = db.create_profile()
    return payments.create_order(prof["id"], product)


def ping_for(order: dict, product: str = "full", **over) -> dict:
    """A form-encoded Gumroad Ping as Purchase#payload_for_ping_notification builds it."""
    data = {"seller_id": SELLER, "sale_id": f"S-{order['id']}==", "product_id": f"prod-{product}",
            "product_name": "Mizaj report", "permalink": f"mizaj-{product}",
            "product_permalink": f"{BASE}mizaj-{product}", "short_product_id": f"rnd{product}",
            "email": "buyer@example.com", "price": "900", "gumroad_fee": "140", "currency": "usd", "quantity": "1",
            "refunded": "false", "disputed": "false", "dispute_won": "false", "url_params[order_id]": order["id"]}
    data.update(over)
    return {k: v for k, v in data.items() if v is not None}


def status(order: dict) -> str:
    return payments.get_order(order["id"])["status"]


def test_gumroad_url_builds_query(gumroad, monkeypatch):
    order = new_order("career")
    assert payments.gumroad_url(order) == f"{BASE}mizaj-career?order_id={order['id']}&wanted=true"
    monkeypatch.setattr(settings, "gumroad_links", f"career={BASE}mizaj-career?a=1&b=two")
    assert payments.gumroad_url(order) == f"{BASE}mizaj-career?a=1&b=two&order_id={order['id']}&wanted=true"
    monkeypatch.setattr(settings, "gumroad_links", "")
    assert payments.gumroad_url(order) is None


def test_order_page_prefers_gumroad_then_lemonsqueezy(gumroad, client, monkeypatch):
    monkeypatch.setattr(settings, "lemonsqueezy_links", "full=https://mizaj.lemonsqueezy.com/buy/abc")
    prof = db.create_profile()
    order = payments.create_order(prof["id"], "full")
    client.cookies.set("mzk", f"{prof['id']}.{prof['key']}")
    page = client.get(f"/order/{order['id']}").text
    assert f"{BASE}mizaj-full?order_id={order['id']}&amp;wanted=true" in page and "lemonsqueezy" not in page
    monkeypatch.setattr(settings, "gumroad_links", "")
    page = client.get(f"/order/{order['id']}").text
    assert "https://mizaj.lemonsqueezy.com/buy/abc?" in page and "gumroad" not in page


def test_valid_ping_unlocks(gumroad, client):
    order = new_order("full")
    ping = ping_for(order)
    gumroad.add(ping["sale_id"])
    r = client.post(PING_URL, data=ping)
    assert r.status_code == 200, r.text
    o = payments.get_order(order["id"])
    assert o["status"] == "paid" and o["method"] == "gumroad" and o["gateway_ref"] == ping["sale_id"]
    assert o["currency"] == "USD" and o["amount"] == 9 and o["email"] == "buyer@example.com"
    url, headers = gumroad.calls[0]
    assert url == "https://api.gumroad.com/v2/sales/S-" + order["id"] + "%3D%3D"
    assert headers["Authorization"] == "Bearer token-for-tests"
    assert "Paid by gumroad" in gumroad.texts() and "not unlocked" not in gumroad.texts()
    assert client.get("/api/health").json()["gumroad"] is True


def test_json_ping_and_no_access_token(gumroad, client, monkeypatch):
    monkeypatch.setattr(settings, "gumroad_access_token", "")
    order = new_order("bundle")
    ping = ping_for(order, "bundle", price=2400)
    del ping["url_params[order_id]"]
    ping["url_params"] = {"order_id": order["id"]}
    r = client.post(PING_URL, json=ping)
    assert r.status_code == 200 and status(order) == "paid"
    assert payments.get_order(order["id"])["amount"] == 24
    assert gumroad.calls == []  # no token: Gumroad's API isn't asked


def test_wrong_path_secret_is_404(gumroad, client, monkeypatch):
    order = new_order()
    ping = ping_for(order)
    gumroad.add(ping["sale_id"])
    assert client.post("/api/webhooks/gumroad/wrong-secret", data=ping).status_code == 404
    assert client.post(f"{PING_URL}x", data=ping).status_code == 404
    monkeypatch.setattr(settings, "gumroad_ping_secret", "")  # not configured: the webhook doesn't exist
    assert client.post(PING_URL, data=ping).status_code == 404
    assert status(order) == "created" and gumroad.calls == [] and gumroad.alerts == []


def test_wrong_seller_not_paid(gumroad, client):
    order = new_order()
    ping = ping_for(order, seller_id="someone-else")
    gumroad.add(ping["sale_id"])
    assert client.post(PING_URL, data=ping).status_code == 403
    assert status(order) == "created" and "different Gumroad seller" in gumroad.texts()


def test_wrong_product_not_paid(gumroad, client):
    order = new_order("full")
    ping = ping_for(order, "palm", price="900")  # a $5 product, even if the price looked right
    gumroad.add(ping["sale_id"], "palm")
    r = client.post(PING_URL, data=ping)
    assert r.status_code == 200 and status(order) == "created"
    assert "not the one ordered" in gumroad.texts()
    text, buttons = gumroad.alerts[-1]
    assert buttons and "a=approve" in buttons[0][0][1]  # owner can still unlock with one tap


def test_underpayment_not_paid(gumroad, client):
    order = new_order("career")  # $14
    ping = ping_for(order, "career", price="1399")
    gumroad.add(ping["sale_id"], "career", price=1399)
    assert client.post(PING_URL, data=ping).status_code == 200
    assert status(order) == "created" and "costs USD 14.00" in gumroad.texts()
    other = new_order("career")
    ping = ping_for(other, "career", price="1400", currency="eur")
    assert client.post(PING_URL, data=ping).status_code == 200
    assert status(other) == "created" and "not US dollars" in gumroad.texts()


def test_refunded_not_paid(gumroad, client):
    order = new_order()
    ping = ping_for(order, refunded="true")
    gumroad.add(ping["sale_id"])
    assert client.post(PING_URL, data=ping).status_code == 200
    assert status(order) == "created" and "refunded" in gumroad.texts()


def test_api_disagrees_not_paid(gumroad, client):
    order = new_order()
    ping = ping_for(order)  # the API doesn't know this sale
    assert client.post(PING_URL, data=ping).status_code == 200
    assert status(order) == "created" and "did not confirm" in gumroad.texts()

    refunded = new_order()
    ping = ping_for(refunded)
    gumroad.add(ping["sale_id"], refunded=True)
    assert client.post(PING_URL, data=ping).status_code == 200
    assert status(refunded) == "created"

    other_product = new_order()
    ping = ping_for(other_product)
    gumroad.add(ping["sale_id"], "palm", price=500)
    assert client.post(PING_URL, data=ping).status_code == 200
    assert status(other_product) == "created" and "different product" in gumroad.texts()


def test_api_down_asks_gumroad_to_retry(gumroad, client):
    order = new_order()
    ping = ping_for(order)
    gumroad.add(ping["sale_id"])
    gumroad.down = True
    assert client.post(PING_URL, data=ping).status_code == 503
    assert status(order) == "created" and "didn't answer" in gumroad.texts()
    gumroad.down = False  # Gumroad's retry goes through
    assert client.post(PING_URL, data=ping).status_code == 200 and status(order) == "paid"


def test_duplicate_ping_is_idempotent(gumroad, client):
    order = new_order()
    ping = ping_for(order)
    gumroad.add(ping["sale_id"])
    assert client.post(PING_URL, data=ping).status_code == 200
    paid = payments.get_order(order["id"])
    n_alerts = len(gumroad.alerts)
    assert client.post(PING_URL, data={**ping, "retry_count": "1"}).status_code == 200
    again = payments.get_order(order["id"])
    assert again["status"] == "paid" and again["paid_at"] == paid["paid_at"] and again["gateway_ref"] == ping["sale_id"]
    assert len(gumroad.alerts) == n_alerts  # no second "paid" message, no alert


def test_one_sale_unlocks_one_order(gumroad, client):
    first, second = new_order(), new_order()
    ping = ping_for(first)
    gumroad.add(ping["sale_id"])
    assert client.post(PING_URL, data=ping).status_code == 200 and status(first) == "paid"
    replay = {**ping, "url_params[order_id]": second["id"]}
    assert client.post(PING_URL, data=replay).status_code == 200
    assert status(second) == "created" and "already unlocked order" in gumroad.texts()


def test_ping_without_order_alerts_owner(gumroad, client):
    ping = ping_for({"id": "nope"})
    del ping["url_params[order_id]"]
    assert client.post(PING_URL, data=ping).status_code == 200
    assert "No matching Mizaj order" in gumroad.texts()
