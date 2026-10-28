"""Social and link-preview layouts built around the Mizaj Deck card (server/mizaj/deck.py)."""
from __future__ import annotations

import html
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "server"))
from mizaj import content, deck  # noqa: E402
from mizaj.deck import EL, BEST_WITH, aura_style, emblem, opposite  # noqa: E402,F401

e = html.escape
PREFIX = "../site/static/"
FONTS = ('<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,600;0,9..144,700;'
         '1,9..144,500;1,9..144,600&family=Manrope:wght@500;600;700;800&family=JetBrains+Mono:wght@500;700'
         '&family=Caveat:wght@600;700&display=block" rel="stylesheet">')


def card(code: str | None = None, key: str | None = None, bars=None, line: str | None = None, scale: float = 10) -> str:
    """A deck card at `scale` px per em (10 gives an 860px-wide card)."""
    return f'<div style="font-size:{scale}px">{deck.card(code, key, bars=bars, line=line, prefix=PREFIX)}</div>'


def story(code: str | None, key: str | None, who: str = "", bars=None, out: str = "story.png") -> str:
    """A 1080x1920 share card: the deck card on an aura, with the social hooks underneath."""
    t = content.type_summary(code) if code else None
    m = content.mizaj_summary(key) if key else None
    hooks = []
    if key:
        hooks.append(f'Best with: <b>{EL[BEST_WITH[key]]["name"]}</b>')
    if code:
        hooks.append(f'Tag your opposite: <b>{opposite(code)}</b>')
    return (f'<div class="story aura grain" style="{aura_style(deck.aura_key(code, key))}" data-out="{out}">'
            f'<div class="s-head"><span class="wordmark">mizaj</span><span class="mono">The Mizaj Deck</span></div>'
            f'<div class="s-who">{e(who) + " pulled" if who else "I pulled"}</div>'
            f'{card(code, key, bars=bars, line=(t or m)["share_line"])}'
            f'<div class="hooks">{"".join(f"<span>{h}</span>" for h in hooks)}</div>'
            f'<div class="s-foot">What\'s your card? <b>mizaj.pk</b></div></div>')


def fan(keys=None, backs: bool = False) -> str:
    keys = keys or content.MIZAJ_KEYS
    if backs:  # face down: numbered, no hint of the element
        cards = "".join(f'<div class="fc"><div><span class="num">{i}</span></div></div>' for i in range(1, 5))
    else:
        cards = "".join(f'<div class="fc"><div>{emblem(k, EL[k]["color"], "")}{EL[k]["name"]}</div></div>' for k in keys)
    return f'<div class="fan{" backs" if backs else ""}">{cards}</div>'
