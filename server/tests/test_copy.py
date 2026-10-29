"""English copy on dynamic pages: readers see the English type and element names, never the Urdu/Unani ones."""
import re

from fastapi.testclient import TestClient

from mizaj import content
from mizaj.api import app
from test_flow import answers_for, mizaj_answers


def _title(html: str) -> str:
    return re.search(r'<meta property="og:title" content="([^"]*)"', html).group(1)


def test_result_title_uses_english_type_name():
    client = TestClient(app)
    r = client.post("/api/results", json={"test": "personality", "answers": answers_for("INFJ"), "name": "Sam"})
    pid = r.json()["profile_id"]
    t = content.type_profile("INFJ")
    title = _title(TestClient(app).get(f"/p/{pid}").text)  # what a shared link previews
    assert title == f"Sam is INFJ: {t['name_en']}"
    assert t["name"] not in title


def test_element_only_result_title_uses_element_name():
    client = TestClient(app)
    r = client.post("/api/results", json={"test": "mizaj", "answers": mizaj_answers("saudavi")})
    title = _title(TestClient(app).get(f"/p/{r.json()['profile_id']}").text)
    assert title == "My element is Earth"
