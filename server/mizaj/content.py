"""Loads the editorial content (content/*.json) once and serves it to the API and pages."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from .config import settings

TYPE_CODES = ["INTJ", "INTP", "ENTJ", "ENTP", "INFJ", "INFP", "ENFJ", "ENFP",
              "ISTJ", "ISFJ", "ESTJ", "ESFJ", "ISTP", "ISFP", "ESTP", "ESFP"]
MIZAJ_KEYS = ["damvi", "safravi", "balghami", "saudavi"]
FAMILIES = {
    "Danishwar": {"en": "The Thinkers", "letters": "NT", "color": "#6B4FA0"},
    "Ahl-e-Dil": {"en": "The Heart-led", "letters": "NF", "color": "#2E8A6A"},
    "Pasban": {"en": "The Guardians", "letters": "SJ", "color": "#2F6DB0"},
    "Fankar": {"en": "The Makers", "letters": "SP", "color": "#D98C2B"},
}
DIMENSIONS = {
    "EI": {"a": "E", "b": "I", "a_name": "Extravert", "b_name": "Introvert", "a_ur": "Mehfil", "b_ur": "Khalwat", "label": "Energy"},
    "SN": {"a": "S", "b": "N", "a_name": "Sensing", "b_name": "Intuition", "a_ur": "Haqiqat", "b_ur": "Khayal", "label": "Perception"},
    "TF": {"a": "T", "b": "F", "a_name": "Thinking", "b_name": "Feeling", "a_ur": "Dimagh", "b_ur": "Dil", "label": "Decisions"},
    "JP": {"a": "J", "b": "P", "a_name": "Judging", "b_name": "Perceiving", "a_ur": "Nizam", "b_ur": "Azad", "label": "Lifestyle"},
}


def family_of(code: str) -> str:
    if code[1] == "N":
        return "Danishwar" if code[2] == "T" else "Ahl-e-Dil"
    return "Pasban" if code[3] == "J" else "Fankar"


def _read(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=None)
def questions(test: str) -> dict:
    return _read(settings.content_dir / "questions" / f"{test}.json")


@lru_cache(maxsize=None)
def type_profile(code: str) -> dict:
    code = code.upper()
    if code not in TYPE_CODES:
        raise KeyError(code)
    return _read(settings.content_dir / "types" / f"{code}.json")


@lru_cache(maxsize=None)
def mizaj_profile(key: str) -> dict:
    if key not in MIZAJ_KEYS:
        raise KeyError(key)
    return _read(settings.content_dir / "mizaj" / f"{key}.json")


@lru_cache(maxsize=None)
def compat_dimensions() -> dict:
    return _read(settings.content_dir / "compat" / "dimensions.json")


@lru_cache(maxsize=None)
def mizaj_pairs() -> dict:
    return _read(settings.content_dir / "compat" / "mizaj_pairs.json")["pairs"]


@lru_cache(maxsize=None)
def riasec() -> dict:
    return _read(settings.content_dir / "careers" / "riasec.json")


@lru_cache(maxsize=None)
def career_advice() -> dict:
    return _read(settings.content_dir / "careers" / "advice.json")


@lru_cache(maxsize=None)
def zodiac() -> dict:
    return _read(settings.content_dir / "fun" / "zodiac.json")


@lru_cache(maxsize=None)
def numerology() -> dict:
    return _read(settings.content_dir / "fun" / "numerology.json")


@lru_cache(maxsize=None)
def catalog() -> dict:
    return _read(settings.content_dir / "products.json")["products"]


def product(key: str) -> dict:
    p = catalog().get(key)
    if not p:
        raise KeyError(key)
    return p


def type_summary(code: str) -> dict:
    """The lightweight, public slice of a type used on cards and share images."""
    t = type_profile(code)
    return {k: t.get(k) for k in ("code", "name", "name_ur", "name_en", "family", "emoji", "colors",
                                    "tagline", "share_line", "keywords", "rarity")}


def mizaj_summary(key: str) -> dict:
    m = mizaj_profile(key)
    return {k: m.get(k) for k in ("key", "name", "name_ur", "quality", "classical", "element", "nickname",
                                    "season", "colors", "emoji", "tagline", "share_line")}


def mizaj_pair(a: str, b: str) -> dict:
    pairs = mizaj_pairs()
    return pairs.get(f"{a}+{b}") or pairs.get(f"{b}+{a}") or {}
