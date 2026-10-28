"""Render the social plan into JPEG slides + queue files.  Usage: python tools/render_social.py [plan.json]

Output: social/media/<post id>/NN.jpg (full set, for TikTok photo mode and the zip)
        social/media/<post id>/ig-NN.jpg (at most 10, for Instagram/Facebook via the API)
        social/queue/<post id>.json (what the autoposter reads)
"""
from __future__ import annotations

import html
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "server"))
from mizaj import content  # noqa: E402

FONTS = '<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,600;0,9..144,700;1,9..144,600&family=Manrope:wght@500;600;700;800&family=Noto+Nastaliq+Urdu:wght@400;600&display=block" rel="stylesheet">'
FAMILY_ORDER = ["Danishwar", "Ahl-e-Dil", "Pasban", "Fankar"]
e = html.escape


def foot(n: int, total: int) -> str:
    return (f'<div class="foot"><span><img src="../site/static/img/logo.svg">mizaj.pk</span>'
            f'<span>{n}/{total}</span></div>')


def slide_html(s: dict, n: int, total: int, out: str) -> str:
    k = s["kind"]
    if k == "cover":
        inner = (f'<div class="eyebrow">Mizaj · مزاج</div><div class="big">{e(s["title"])}</div>'
                 f'<div class="sub">{e(s.get("subtitle", ""))}</div><img class="mark" src="../site/static/img/logo.svg"><div class="swipe">Swipe →</div>')
        cls = "ink"
    elif k == "type":
        t = content.type_summary(s["code"])
        inner = (f'<div class="eyebrow">{e(t["family"])}</div><div class="code">{e(t["code"])}</div>'
                 f'<div class="tname">{e(t["name"])} · {e(t["name_en"])} {t.get("emoji", "")}</div>'
                 f'<div class="ur tur">{e(t["name_ur"])}</div><div class="quote">{e(s["text"])}</div>')
        art = ROOT / "site" / "static" / "img" / "types" / f'{t["code"].lower()}.webp'
        if art.exists():
            inner += f'<img class="art" src="../site/static/img/types/{t["code"].lower()}.webp">'
        cls = f'fam-{t["family"]}'
    elif k == "mizaj":
        m = content.mizaj_summary(s["key"])
        inner = (f'<div class="eyebrow">{e(m["quality"])}</div><div class="code" style="font-size:140px">{e(m["name"])}</div>'
                 f'<div class="tname">{e(m["nickname"])} {m.get("emoji", "")}</div><div class="ur tur">{e(m["name_ur"])}</div>'
                 f'<div class="quote">{e(s["text"])}</div>')
        art = ROOT / "site" / "static" / "img" / "mizaj" / f'{s["key"]}.webp'
        if art.exists():
            inner += f'<img class="art" src="../site/static/img/mizaj/{s["key"]}.webp">'
        cls = f'mz-{s["key"]}'
    elif k == "list":
        items = "".join(f"<li>{e(i)}</li>" for i in s.get("items", []))
        inner = f'<div class="mid">{e(s["title"])}</div><ul class="items">{items}</ul>'
        cls = "light"
    elif k == "cta":
        inner = (f'<div class="eyebrow">Free · 8 minutes · English & اردو</div><div class="big">{e(s["title"])}</div>'
                 f'<div class="sub">{e(s.get("subtitle", ""))}</div><div class="cta-url">mizaj.pk</div><img class="mark" src="../site/static/img/logo.svg">')
        cls = "pom"
    elif k == "family":
        cells = "".join(f'<div class="cell"><div class="c">{e(c["code"])}</div><div class="n">{e(content.type_summary(c["code"])["name"])}</div>'
                        f'<div class="t">{e(c["text"])}</div></div>' for c in s["cells"])
        inner = f'<div class="eyebrow">{e(s["title"])}</div><div class="grid4">{cells}</div>'
        cls = f'fam-{s["family"]}'
    else:  # text
        inner = f'<div class="mid">{e(s.get("title", ""))}</div><div class="body">{e(s.get("text", ""))}</div>'
        cls = "light"
    return f'<div class="slide {cls}" data-out="{out}">{inner}{foot(n, total)}</div>'


def ig_slides(slides: list[dict]) -> list[dict]:
    """Instagram's API takes 10 images: fold 16 type slides into 4 family slides."""
    if len(slides) <= 10:
        return slides
    types = [s for s in slides if s["kind"] == "type"]
    others = [s for s in slides if s["kind"] != "type"]
    fams = []
    for fam in FAMILY_ORDER:
        cells = [s for s in types if content.family_of(s["code"]) == fam]
        if cells:
            info = content.FAMILIES[fam]
            fams.append({"kind": "family", "family": fam, "title": f"{fam} · {info['en']}", "cells": cells})
    covers = [s for s in others if s["kind"] == "cover"][:1]
    ctas = [s for s in others if s["kind"] == "cta"][-1:]
    middle = [s for s in others if s not in covers and s not in ctas]
    return (covers + fams + middle + ctas)[:10]


def render_post(p: dict) -> dict:
    out_dir = ROOT / "social" / "media" / p["id"]
    full, ig = p["slides"], ig_slides(p["slides"])
    parts = [slide_html(s, i + 1, len(full), f"{i + 1:02d}.jpg") for i, s in enumerate(full)]
    if ig is not full:
        parts += [slide_html(s, i + 1, len(ig), f"ig-{i + 1:02d}.jpg") for i, s in enumerate(ig)]
    page = ROOT / "tools" / f".render-{p['id']}.html"
    page.write_text(f'<!doctype html><meta charset="utf-8">{FONTS}<link rel="stylesheet" href="slides.css"><body>{"".join(parts)}</body>',
                    encoding="utf-8")
    subprocess.run(["node", str(ROOT / "tools" / "shoot.cjs"), str(page), str(out_dir)], check=True,
                   cwd=str(ROOT / "tools"), stdout=subprocess.DEVNULL)
    page.unlink()
    media = [f"ig-{i + 1:02d}.jpg" for i in range(len(ig))] if ig is not full else [f"{i + 1:02d}.jpg" for i in range(len(full))]
    item = {k: p[k] for k in ("id", "day", "time", "pillar", "platforms", "title", "caption", "hashtags") if k in p}
    item.update({"tiktok_caption": p.get("tiktok_caption", ""), "audio_hint": p.get("audio_hint", ""),
                 "reel_hook": p.get("reel_hook", ""), "media": media,
                 "full": [f"{i + 1:02d}.jpg" for i in range(len(full))]})
    q = ROOT / "social" / "queue" / f"{p['id']}.json"
    q.parent.mkdir(parents=True, exist_ok=True)
    q.write_text(json.dumps(item, ensure_ascii=False, indent=1), encoding="utf-8")
    return item


def main() -> None:
    plan = json.loads(Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / "social" / "plan" / "launch30.json").read_text())
    only = set(sys.argv[2].split(",")) if len(sys.argv) > 2 else None
    for p in plan["posts"]:
        if only and p["id"] not in only:
            continue
        render_post(p)
        print("rendered", p["id"])


if __name__ == "__main__":
    main()
