"""Render link-preview images (1200x630 PNG) into site/static/og/. Usage: python tools/make_og.py"""
from __future__ import annotations

import html
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "server"))
sys.path.insert(0, str(ROOT / "tools"))
from mizaj import content  # noqa: E402
from render_social import FONTS  # noqa: E402

e = html.escape
LOGO = "../site/static/img/logo.svg"


def og(out: str, cls: str, eyebrow: str, big: str, line2: str, ur: str, tag: str) -> str:
    return (f'<div class="slide og {cls}" data-out="{out}" style="justify-content:center">'
            f'<div class="eyebrow">{e(eyebrow)}</div><div class="code">{e(big)}</div>'
            f'<div class="tname" style="font-size:50px">{e(line2)}</div><div class="ur tur" style="font-size:48px">{e(ur)}</div>'
            f'<div style="font:600 34px Manrope;margin-top:18px;opacity:.9;max-width:760px">{e(tag)}</div>'
            f'<img src="{LOGO}" style="position:absolute;right:70px;top:70px;width:150px">'
            f'<div style="position:absolute;right:80px;bottom:56px;font:800 34px Manrope">mizaj.pk</div></div>')


def main() -> None:
    parts = []
    for c in content.TYPE_CODES:
        t = content.type_summary(c)
        parts.append(og(f"types/{c.lower()}.png", f"fam-{t['family']}", f"{t['family']} · What's your mizaj?", c,
                        f"{t['name']} · {t['name_en']} {t.get('emoji', '')}", t["name_ur"], t["tagline"]))
    for k in content.MIZAJ_KEYS:
        m = content.mizaj_summary(k)
        parts.append(og(f"mizaj/{k}.png", f"mz-{k}", m["quality"], m["name"], f"{m['nickname']} {m.get('emoji', '')}",
                        m["name_ur"], m["tagline"]))
    parts.append(og("default.png", "ink", "Free test · English & اردو", "mizaj", "What's your mizaj?", "مزاج",
                    "Personality, Unani temperament, couple match and career compass, made for Pakistan."))
    parts.append('<div data-out="../img/apple-touch-icon.png" style="width:180px;height:180px;background:#FBF6EE;display:grid;place-items:center">'
                 f'<img src="{LOGO}" style="width:150px;height:150px"></div>')
    page = ROOT / "tools" / ".og.html"
    page.write_text(f'<!doctype html><meta charset="utf-8">{FONTS}<link rel="stylesheet" href="slides.css"><body>{"".join(parts)}</body>', encoding="utf-8")
    out = ROOT / "site" / "static" / "og"
    for sub in ("types", "mizaj"):
        (out / sub).mkdir(parents=True, exist_ok=True)
    subprocess.run(["node", str(ROOT / "tools" / "shoot.cjs"), str(page), str(out), "png"], check=True, cwd=str(ROOT / "tools"))
    page.unlink()


if __name__ == "__main__":
    main()
