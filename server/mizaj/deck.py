"""The Mizaj Deck: 16 types x 4 elements = 64 collectible cards.

One HTML builder for the card, used by the site (result, type and element pages), the social slides and the link
previews, so every surface shows the same object. Styles live in site/static/css/deck.css.
"""
from __future__ import annotations

import html
from functools import lru_cache

from . import content
from .config import settings

e = html.escape

# Unani temperament -> element. Colours match the logo quadrants.
EL = {
    "damvi": {"el": "air", "name": "Air", "color": "#D2544A", "deep": "#8E2F28"},
    "safravi": {"el": "fire", "name": "Fire", "color": "#E39B2D", "deep": "#A8601A"},
    "balghami": {"el": "water", "name": "Water", "color": "#2E8A8A", "deep": "#17504F"},
    "saudavi": {"el": "earth", "name": "Earth", "color": "#5A4A78", "deep": "#33284A"},
}
BEST_WITH = {"damvi": "saudavi", "saudavi": "damvi", "safravi": "balghami", "balghami": "safravi"}  # highest pair scores
FAM_COLOR = {"Danishwar": "#6B4FA0", "Ahl-e-Dil": "#2E8A6A", "Pasban": "#2F6DB0", "Fankar": "#D98C2B"}
FAM_EL = {"Danishwar": "safravi", "Ahl-e-Dil": "damvi", "Pasban": "saudavi", "Fankar": "balghami"}  # aura for type-only cards
_OPPOSITE = str.maketrans("EISNTFJP", "IENSFTPJ")


@lru_cache(maxsize=None)
def _svg(el: str) -> str:
    return (settings.static_dir / "img" / "el" / f"{el}.svg").read_text(encoding="utf-8")


def emblem(key: str, color: str = "currentColor", cls: str = "emb") -> str:
    return _svg(EL[key]["el"]).replace('color="#17131F"', f'color="{color}" class="{cls}" aria-hidden="true"', 1)


def deck_no(code: str | None, key: str | None) -> str:
    """'No. 07/64' for a full card; a type alone spans its four element cards; an element alone is one of four."""
    if code and key:
        return f"No. {content.TYPE_CODES.index(code) * 4 + content.MIZAJ_KEYS.index(key) + 1:02d}/64"
    if code:
        first = content.TYPE_CODES.index(code) * 4 + 1
        return f"Nos. {first:02d}–{first + 3:02d}"
    return f"Element {content.MIZAJ_KEYS.index(key) + 1}/4"


def opposite(code: str) -> str:
    return code.translate(_OPPOSITE)


def aura_key(code: str | None, key: str | None) -> str:
    return key or FAM_EL[content.family_of(code)]


def aura_style(key: str, key2: str | None = None) -> str:
    return f'--c1:{EL[key]["color"]};--c2:{EL[key2 or BEST_WITH[key]]["color"]}'


def art_path(code: str | None, key: str | None) -> str | None:
    """A character illustration for this card, if the art team has delivered one."""
    names = []
    if code and key:
        names.append(f"{code.lower()}-{EL[key]['el']}")
    if code:
        names.append(code.lower())
    if key:
        names.append(EL[key]["el"])
    for n in names:
        if (settings.static_dir / "img" / "deck" / f"{n}.webp").exists():
            return f"img/deck/{n}.webp"
    return None


def card(code: str | None = None, key: str | None = None, bars: list[tuple[str, int]] | None = None,
         line: str | None = None, prefix: str = "/", cls: str = "") -> str:
    """One deck card as HTML. Size it with font-size on .dcard (1em = 1/86 of the card's width)."""
    t = content.type_summary(code) if code else None
    m = content.mizaj_summary(key) if key else None
    ak = aura_key(code, key)
    el = EL[ak]
    if t:
        fam = t["family"]
        top_left = f'<i class="pip" style="background:{FAM_COLOR[fam]}"></i>{e(content.FAMILIES[fam]["en"])}'
    else:
        top_left = f'<i class="pip" style="background:{el["color"]}"></i>The Elements'
    art = art_path(code, key)
    if art:  # transparent ink-on-paper character over the element glow
        window = f'{emblem(ak, "rgba(255,255,255,.16)", "emb-bg")}<img class="char" src="{prefix}{art}" alt="">'
    elif t:
        window = f'{emblem(ak, "rgba(255,255,255,.2)", "emb-bg")}<div class="big">{e(t["code"])}</div>'
    else:
        window = emblem(ak, "#F4F1EA", "emb-solo")
    chip = f'<div class="chip">{emblem(key, "#F4F1EA", "emb-chip")}{e(el["name"])}</div>' if key else ""
    if t:
        name = t["name_en"]
        sub = t["code"] + (f' · {el["name"]} · {m["nickname"]}' if m else "")
        desi = t["name"] + (f' · {m["name"]}' if m else "")
    else:
        name = m["nickname"]
        sub = f'{el["name"]} · {m["quality"].split(" (")[-1].rstrip(")")}'
        desi = f'{m["name"]} · {m["classical"]}'
    rows = ""
    if bars:
        rows = '<div class="bars">' + "".join(
            f'<div class="row"><span>{e(lbl)}</span><b><i style="width:{int(pct)}%"></i></b><span>{int(pct)}%</span></div>'
            for lbl, pct in bars) + "</div>"
    quote = f'<div class="quote">“{e(line)}”</div>' if line else ""
    return (f'<div class="dcard {cls}" style="--c1:{el["color"]};--c2:{el["deep"]}">'
            f'<div class="in"><div class="top"><span>{top_left}</span><span>{deck_no(code, key)}</span></div>'
            f'<div class="art">{window}{chip}</div>'
            f'<div class="name">{e(name)}</div><div class="sub">{e(sub)}</div><div class="desi">{e(desi)}</div>'
            f'{rows}{quote}</div></div>')


def bars_from(personality_dims: list[dict] | None) -> list[tuple[str, int]] | None:
    """The three strongest preferences, for the card's stat bars."""
    if not personality_dims:
        return None
    rows = []
    for d in personality_dims:
        win_a = d.get("letter") == d.get("a")
        pct = d.get("pct_a") if win_a else d.get("pct_b")
        rows.append((d["a_name"] if win_a else d["b_name"], int(pct or 50)))
    return sorted(rows, key=lambda r: -r[1])[:3]


def card_data(code: str | None = None, key: str | None = None, dims: list[dict] | None = None) -> dict:
    """Everything the browser needs to draw the downloadable story card (site/static/js/app.js storyCard)."""
    t = content.type_summary(code) if code else None
    m = content.mizaj_summary(key) if key else None
    ak = aura_key(code, key)
    el = EL[ak]
    if t:
        top = content.FAMILIES[t["family"]]["en"]
        pip = FAM_COLOR[t["family"]]
        name = t["name_en"]
        sub = t["code"] + (f' · {el["name"]} · {m["nickname"]}' if m else "")
        desi = t["name"] + (f' · {m["name"]}' if m else "")
    else:
        top, pip, name = "The Elements", el["color"], m["nickname"]
        sub = f'{el["name"]} · {m["quality"].split(" (")[-1].rstrip(")")}'
        desi = f'{m["name"]} · {m["classical"]}'
    hooks = []
    if key:
        hooks.append(["Best with: ", EL[BEST_WITH[key]]["name"]])
    if code:
        hooks.append(["Tag your opposite: ", opposite(code)])
    return {
        "no": deck_no(code, key), "code": code or "", "el": el["el"] if key else "", "aura_el": el["el"],
        "el_name": el["name"] if key else "", "c1": el["color"], "deep": el["deep"], "c2": EL[BEST_WITH[ak]]["color"],
        "top": top, "pip": pip, "name": name, "sub": sub, "desi": desi, "bars": bars_from(dims) or [],
        "line": (t or m)["share_line"], "hooks": hooks, "art": ("/" + art_path(code, key)) if art_path(code, key) else "",
    }
