"""Render link-preview images (1200x630 PNG) into site/static/og/. Usage: python tools/make_og.py"""
from __future__ import annotations

import html
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cards import FONTS, ROOT, aura_style, card, content, deck, fan  # noqa: E402

e = html.escape
LOGO = "../site/static/img/logo.svg"


def og(out: str, style: str, note: str, title: str, lede: str, visual: str) -> str:
    return (f'<div class="og aura grain" style="{style}" data-out="{out}"><div class="ogtxt"><div class="note">{e(note)}</div>'
            f'<div class="h1">{e(title)}</div><div class="lede">{e(lede)}</div><div class="url">mizaj.pk</div></div>'
            f'<div style="position:relative;z-index:2;flex:0 0 auto">{visual}</div></div>')


def main() -> None:
    parts = []
    for c in content.TYPE_CODES:
        t = content.type_summary(c)
        parts.append(og(f"types/{c.lower()}.jpg", aura_style(deck.aura_key(c, None)),
                        f"{content.FAMILIES[t['family']]['en']} · The Mizaj Deck", f"{c} · {t['name_en']}", t["tagline"],
                        card(c, None, scale=5.4)))
    for k in content.MIZAJ_KEYS:
        m = content.mizaj_summary(k)
        parts.append(og(f"mizaj/{k}.jpg", aura_style(k), f"{m['quality'].split(' (')[-1].rstrip(')')} · Unani temperament",
                        f"{m['global_name']} · {m['nickname']}", m["tagline"], card(None, k, scale=5.4)))
    parts.append(og("default.jpg", aura_style("balghami", "damvi"), "Free · 8 minutes · any phone", "What's your mizaj?",
                    "Your type, your element, your match. The personality test for everyone who wants to understand people.",
                    card("INFJ", "balghami", scale=5.4)))
    page = ROOT / "tools" / ".og.html"
    page.write_text(f'<!doctype html><meta charset="utf-8">{FONTS}<link rel="stylesheet" href="slides.css"><body>{"".join(parts)}</body>', encoding="utf-8")
    out = ROOT / "site" / "static" / "og"
    for sub in ("types", "mizaj"):
        (out / sub).mkdir(parents=True, exist_ok=True)
    subprocess.run(["node", str(ROOT / "tools" / "shoot.cjs"), str(page), str(out), "jpeg"], check=True, cwd=str(ROOT / "tools"))
    icon = ('<div data-out="../img/apple-touch-icon.png" style="width:180px;height:180px;background:#F4F1EA;display:grid;place-items:center">'
            f'<img src="{LOGO}" style="width:150px;height:150px"></div>')
    page.write_text(f'<!doctype html><meta charset="utf-8"><body style="margin:0">{icon}</body>', encoding="utf-8")
    subprocess.run(["node", str(ROOT / "tools" / "shoot.cjs"), str(page), str(out), "png"], check=True, cwd=str(ROOT / "tools"))
    page.unlink()


if __name__ == "__main__":
    main()
