"""Shared Jinja environment for the static build (build.py) and the live pages (api.py)."""
from __future__ import annotations

import json
from functools import lru_cache

from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup

from . import content, deck
from .config import settings

ASSET_VERSION = "2"


def _paras(text: str | None) -> Markup:
    if not text:
        return Markup("")
    from markupsafe import escape
    parts = [p.strip() for p in str(text).split("\n") if p.strip()]
    return Markup("".join(f"<p>{escape(p)}</p>" for p in parts))


def _pkr(n: int | float | None) -> str:
    return f"PKR {int(n or 0):,}"


def money(p: dict, field: str = "price") -> Markup:
    """A price in both currencies; CSS shows PKR to visitors in Pakistan and USD to everyone else."""
    pkr = p.get(field) or 0
    if field == "list_price":
        usd = round(p.get("usd", 0) * (p.get("list_price", 0) / max(p.get("price", 1), 1)))
    else:
        usd = p.get("usd", 0)
    return Markup(f'<span class="cur-usd">${usd:,}</span><span class="cur-pkr">PKR {int(pkr):,}</span>')


def static_exists(rel: str) -> bool:
    """True when an optional asset (e.g. an illustration added later) is present in site/static."""
    return (settings.static_dir / rel.lstrip("/")).is_file()


def deck_card(code: str | None = None, key: str | None = None, dims: list | None = None, line: str | None = None) -> Markup:
    return Markup(deck.card(code or None, key or None, bars=deck.bars_from(dims), line=line))


def deck_aura(code: str | None = None, key: str | None = None) -> str:
    return deck.aura_style(deck.aura_key(code or None, key or None))


def deck_hooks(code: str | None = None, key: str | None = None) -> list[str]:
    hooks = []
    if key:
        hooks.append(f"Best with: {deck.EL[deck.BEST_WITH[key]]['name']}")
    if code:
        hooks.append(f"Your opposite: {deck.opposite(code)}")
    return hooks


def _tojson(v) -> Markup:
    s = json.dumps(v, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    return Markup(s)


@lru_cache(maxsize=1)
def env() -> Environment:
    e = Environment(loader=FileSystemLoader(str(settings.templates_dir)),
                    autoescape=select_autoescape(["html"]), trim_blocks=True, lstrip_blocks=True)
    e.filters["paras"] = _paras
    e.filters["pkr"] = _pkr
    e.filters["tojson_safe"] = _tojson
    e.globals.update(
        site_url=settings.site_url, v=ASSET_VERSION, families=content.FAMILIES, dimensions=content.DIMENSIONS,
        type_codes=content.TYPE_CODES, mizaj_keys=content.MIZAJ_KEYS,
        umami_id=settings.umami_id, umami_src=settings.umami_src,
        meta_pixel_id=settings.meta_pixel_id, tiktok_pixel_id=settings.tiktok_pixel_id,
        support_whatsapp=settings.support_whatsapp, support_email=settings.support_email,
        socials=settings.socials, static_exists=static_exists, money=money,
        deck_card=deck_card, deck_aura=deck_aura, deck_hooks=deck_hooks, deck_el=deck.EL, deck_data=deck.card_data,
    )
    return e


def render(template: str, **ctx) -> str:
    ctx.setdefault("products", content.catalog())
    ctx.setdefault("canonical", None)
    ctx.setdefault("og_image", f"{settings.site_url}/og/default.jpg")
    return env().get_template(template).render(**ctx)
