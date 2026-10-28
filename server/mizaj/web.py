"""Shared Jinja environment for the static build (build.py) and the live pages (api.py)."""
from __future__ import annotations

import json
from functools import lru_cache

from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup

from . import content
from .config import settings

ASSET_VERSION = "1"


def _paras(text: str | None) -> Markup:
    if not text:
        return Markup("")
    from markupsafe import escape
    parts = [p.strip() for p in str(text).split("\n") if p.strip()]
    return Markup("".join(f"<p>{escape(p)}</p>" for p in parts))


def _pkr(n: int | float | None) -> str:
    return f"PKR {int(n or 0):,}"


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
        socials=settings.socials,
    )
    return e


def render(template: str, **ctx) -> str:
    ctx.setdefault("products", content.catalog())
    ctx.setdefault("canonical", None)
    ctx.setdefault("og_image", f"{settings.site_url}/og/default.png")
    return env().get_template(template).render(**ctx)
