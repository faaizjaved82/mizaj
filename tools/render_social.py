"""Render the social plan into JPEG slides + queue files.  Usage: python tools/render_social.py [plan.json] [id,id]

Look: the Mizaj Deck (collectible cards on an aura) for type and element posts, Field Notes (paper, ink,
marginalia) for editorial posts. Slides are 1080x1440 (3:4, the Instagram grid); key content sits inside the
central 4:5 area so the 1080x1350 crops for the Instagram API lose nothing.

Output: social/media/<post id>/NN.jpg (1080x1440 full set, for TikTok photo mode and the zip)
        social/media/<post id>/ig-NN.jpg (1080x1350, at most 10, for Instagram/Facebook via the API)
        social/queue/<post id>.json (what the autoposter reads)

Slide kinds (fields):
  cover {title, subtitle?, note?, hand?}      paper, big serif headline, handwritten aside
  quote {text, note?}                          paper, one blunt line set huge
  text {title, text, note?}                    paper, heading + paragraph
  list {title, items[], note?}                 paper, numbered list
  type {code, key?, text}                      a deck card on its aura, `text` as the caption
  mizaj {key, text}                            an element card on its aura
  grid {title, cells[{code|key, text}]}        up to 4 mini cards ("each type as...")
  versus {title, a, b, a_text, b_text}         two elements or types side by side (a/b = mizaj key or type code)
  pick {title, subtitle?}                      four face-down cards: pause and pick
  cta {title, subtitle?}                       aura + fanned element cards + mizaj.pk
"""
from __future__ import annotations

import html
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cards import EL, FONTS, ROOT, aura_style, card, content, emblem, fan  # noqa: E402

FAMILY_ORDER = ["Danishwar", "Ahl-e-Dil", "Pasban", "Fankar"]
e = html.escape


def foot(n: int, total: int) -> str:
    return f'<div class="foot"><span class="wm">mizaj</span><span>{n:02d}/{total:02d}</span></div>'


def _post_el(post: dict) -> str:
    """The element whose colours a post's paper slides borrow (first type/element slide, else Fire)."""
    for s in post.get("slides", []):
        if s.get("key") in EL:
            return s["key"]
        if s.get("code") in content.TYPE_CODES:
            return {"Danishwar": "safravi", "Ahl-e-Dil": "damvi", "Pasban": "saudavi", "Fankar": "balghami"}[content.family_of(s["code"])]
    return "safravi"


def mini(cell: dict) -> str:
    if cell.get("code"):
        t = content.type_summary(cell["code"])
        head, sub = t["code"], t["name_en"]
        pip = {"Danishwar": "#6B4FA0", "Ahl-e-Dil": "#2E8A6A", "Pasban": "#2F6DB0", "Fankar": "#D98C2B"}[t["family"]]
    else:
        m = content.mizaj_summary(cell["key"])
        head, sub, pip = EL[cell["key"]]["name"], m["nickname"], EL[cell["key"]]["color"]
    return (f'<div class="mini"><div class="mc">{e(head)}<small style="color:{pip}">●</small></div>'
            f'<div class="mn">{e(sub)}</div><div class="mt">{e(cell["text"])}</div></div>')


def half(ref: str) -> str:
    """One side of a versus slide: a compact element or type card."""
    if ref in EL:
        m = content.mizaj_summary(ref)
        return (f'<div class="vs-side" style="--c1:{EL[ref]["color"]}">{emblem(ref, EL[ref]["color"], "vs-emb")}'
                f'<div class="vs-name">{EL[ref]["name"]}</div><div class="vs-sub">{e(m["nickname"])}</div></div>')
    t = content.type_summary(ref)
    return (f'<div class="vs-side"><div class="vs-code">{e(t["code"])}</div>'
            f'<div class="vs-name">{e(t["name_en"])}</div><div class="vs-sub">{e(content.FAMILIES[t["family"]]["en"])}</div></div>')


def slide_html(s: dict, n: int, total: int, out: str, post_el: str) -> str:
    k = s["kind"]
    note = f'<div class="note">{e(s["note"])}</div>' if s.get("note") else ""
    wm = emblem(post_el, "#17131F", "emb-wm")
    if k == "cover":
        hand = s.get("hand", "swipe →")
        inner = (f'{wm}{note or "<div class=note>Mizaj · field notes</div>"}<div class="h1">{e(s["title"])}</div>'
                 f'<div class="lede">{e(s.get("subtitle", ""))}</div><div class="hand swipe">{e(hand)}</div>')
        return f'<div class="slide paper grain" data-out="{out}">{inner}{foot(n, total)}</div>'
    if k == "quote":
        inner = f'{wm}{note}<div class="h1" style="margin:auto 0">{e(s["text"])}</div>'
        return f'<div class="slide paper grain" data-out="{out}">{inner}{foot(n, total)}</div>'
    if k == "text":
        inner = f'{note}<div class="h2">{e(s.get("title", ""))}</div><div class="rule"></div><div class="body">{e(s.get("text", ""))}</div>'
        return f'<div class="slide paper grain" data-out="{out}">{wm}{inner}{foot(n, total)}</div>'
    if k == "list":
        items = "".join(f"<li>{e(i)}</li>" for i in s.get("items", []))
        inner = f'{note}<div class="h2">{e(s["title"])}</div><ol class="items">{items}</ol>'
        return f'<div class="slide paper grain" data-out="{out}">{wm}{inner}{foot(n, total)}</div>'
    if k == "type":
        key = s.get("key")
        el = key or _post_el({"slides": [s]})
        body = card(s["code"], key, line=content.type_summary(s["code"])["share_line"], scale=8.2)
        cap = f'<div class="caption">{e(s["text"])}</div>' if s.get("text") else ""
        return f'<div class="slide cardslide aura grain" style="{aura_style(el)}" data-out="{out}">{body}{cap}{foot(n, total)}</div>'
    if k == "mizaj":
        body = card(None, s["key"], line=content.mizaj_summary(s["key"])["share_line"], scale=8.2)
        cap = f'<div class="caption">{e(s["text"])}</div>' if s.get("text") else ""
        return f'<div class="slide cardslide aura grain" style="{aura_style(s["key"])}" data-out="{out}">{body}{cap}{foot(n, total)}</div>'
    if k in ("grid", "family"):
        title = s["title"]
        cells = "".join(mini(c) for c in s["cells"][:4])
        el = s.get("key") or _post_el({"slides": s["cells"]})
        return (f'<div class="slide aura grain" style="{aura_style(el)}" data-out="{out}"><div class="note">{e(title)}</div>'
                f'<div class="minis">{cells}</div>{foot(n, total)}</div>')
    if k == "versus":
        inner = (f'{note}<div class="h2" style="text-align:center">{e(s["title"])}</div><div class="vs">{half(s["a"])}<div class="vs-x">vs</div>{half(s["b"])}</div>'
                 f'<div class="vs-text"><p>{e(s.get("a_text", ""))}</p><p>{e(s.get("b_text", ""))}</p></div>')
        return f'<div class="slide paper grain" data-out="{out}">{inner}{foot(n, total)}</div>'
    if k == "pick":
        inner = (f'<div class="note">Pause · pick · swipe</div><div class="h1">{e(s["title"])}</div>{fan(backs=True)}'
                 f'<div class="lede" style="margin-top:0">{e(s.get("subtitle", "Left to right: 1, 2, 3, 4. Swipe for yours."))}</div>')
        return f'<div class="slide center aura grain" style="{aura_style("saudavi", "safravi")}" data-out="{out}">{inner}{foot(n, total)}</div>'
    if k == "cta":
        inner = (f'<div class="note">Free · 8 minutes · English &amp; Urdu</div><div class="h1">{e(s["title"])}</div>{fan()}'
                 f'<div class="lede" style="margin-top:0">{e(s.get("subtitle", ""))}</div><div class="tag" style="margin-top:40px">mizaj.pk</div>')
        return f'<div class="slide center aura grain" style="{aura_style("balghami", "damvi")}" data-out="{out}">{inner}{foot(n, total)}</div>'
    raise ValueError(f"unknown slide kind: {k}")


def ig_slides(slides: list[dict]) -> list[dict]:
    """Instagram's API takes 10 images: fold 16 type slides into 4 family grids."""
    if len(slides) <= 10:
        return slides
    types = [s for s in slides if s["kind"] == "type"]
    others = [s for s in slides if s["kind"] != "type"]
    fams = []
    for fam in FAMILY_ORDER:
        cells = [{"code": s["code"], "text": s.get("text", "")} for s in types if content.family_of(s["code"]) == fam]
        if cells:
            fams.append({"kind": "family", "title": content.FAMILIES[fam]["en"], "cells": cells})
    covers = [s for s in others if s["kind"] in ("cover", "quote")][:1]
    ctas = [s for s in others if s["kind"] == "cta"][-1:]
    middle = [s for s in others if s not in covers and s not in ctas]
    return (covers + fams + middle + ctas)[:10]


def render_post(p: dict) -> dict:
    out_dir = ROOT / "social" / "media" / p["id"]
    if out_dir.exists():
        for old in out_dir.glob("*.jpg"):
            old.unlink()
    full, ig = p["slides"], ig_slides(p["slides"])
    pel = _post_el(p)
    parts = [slide_html(s, i + 1, len(full), f"{i + 1:02d}.jpg", pel) for i, s in enumerate(full)]
    if ig is not full:
        parts += [slide_html(s, i + 1, len(ig), f"ig-{i + 1:02d}.jpg", pel) for i, s in enumerate(ig)]
    page = ROOT / "tools" / f".render-{p['id']}.html"
    page.write_text(f'<!doctype html><meta charset="utf-8">{FONTS}<link rel="stylesheet" href="slides.css"><body>{"".join(parts)}</body>',
                    encoding="utf-8")
    subprocess.run(["node", str(ROOT / "tools" / "shoot.cjs"), str(page), str(out_dir)], check=True,
                   cwd=str(ROOT / "tools"), stdout=subprocess.DEVNULL)
    page.unlink()
    # Instagram's API wants 4:5 at most: crop the 3:4 renders to 1080x1350 around the centre.
    names = [f"ig-{i + 1:02d}.jpg" for i in range(len(ig))] if ig is not full else [f"{i + 1:02d}.jpg" for i in range(len(full))]
    media = []
    for i, name in enumerate(names):
        target = f"ig-{i + 1:02d}.jpg"
        with Image.open(out_dir / name) as im:
            im.crop((0, 45, 1080, 1395)).save(out_dir / target, quality=88)
        media.append(target)
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
