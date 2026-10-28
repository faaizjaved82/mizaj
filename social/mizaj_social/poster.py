"""Content queue -> Instagram + Facebook (Graph API) and Telegram nudges for TikTok/Shorts.

The queue is social/queue/*.json (built from the plan by social/render.py). Each item has
"day" (1 = SOCIAL_START_DATE) and "time" (Pakistan time). Media are served by the site at
{SITE_URL}/s/<id>/<n>.png so the Graph API can fetch them.

What happened to each post is kept in MIZAJ_DATA_DIR/social_log.json, outside git.
"""
from __future__ import annotations

import json
import logging
import os
import time
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import httpx

log = logging.getLogger("mizaj.social")
ROOT = Path(__file__).resolve().parents[2]
TZ = ZoneInfo("Asia/Karachi")


def env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def _load_env_file() -> None:
    path = Path(env("MIZAJ_ENV_FILE") or ROOT / ".env")
    if path.exists():
        for line in path.read_text().splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


_load_env_file()
SITE = env("SITE_URL", "https://mizaj.pk").rstrip("/")
GRAPH = f"https://graph.facebook.com/{env('META_GRAPH_VERSION', 'v23.0')}"
DATA = Path(env("MIZAJ_DATA_DIR") or ROOT / "data")
QUEUE = ROOT / "social" / "queue"
DRY = env("DRY_RUN").lower() in ("1", "true", "yes")


def start_date() -> date | None:
    s = env("SOCIAL_START_DATE")
    return date.fromisoformat(s) if s else None


def due_at(item: dict) -> datetime | None:
    start = start_date()
    if not start:
        return None
    hh, mm = (int(x) for x in item.get("time", "20:00").split(":"))
    d = start + timedelta(days=int(item["day"]) - 1)
    return datetime(d.year, d.month, d.day, hh, mm, tzinfo=TZ)


def media_urls(item: dict) -> list[str]:
    return [f"{SITE}/s/{item['id']}/{name}" for name in item.get("media", [])]


# ---------- log ----------

def load_log() -> dict:
    p = DATA / "social_log.json"
    try:
        return json.loads(p.read_text())
    except (OSError, ValueError):
        return {}


def save_log(data: dict) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    tmp = DATA / "social_log.json.tmp"
    tmp.write_text(json.dumps(data, indent=1))
    tmp.replace(DATA / "social_log.json")


# ---------- channels ----------

def telegram(text: str, buttons: list[tuple[str, str]] | None = None) -> None:
    token, chat = env("TELEGRAM_BOT_TOKEN"), env("TELEGRAM_OWNER_ID")
    if DRY or not (token and chat):
        log.info("[telegram dry-run] %s", text)
        return
    payload: dict = {"chat_id": chat, "text": text[:4000], "parse_mode": "HTML", "disable_web_page_preview": True}
    if buttons:
        payload["reply_markup"] = {"inline_keyboard": [[{"text": t, "url": u}] for t, u in buttons]}
    httpx.post(f"https://api.telegram.org/bot{token}/sendMessage", json=payload, timeout=15).raise_for_status()


def _post(http: httpx.Client, url: str, data: dict) -> dict:
    r = http.post(url, data={**data, "access_token": env("META_PAGE_ACCESS_TOKEN")})
    if r.status_code >= 400:
        raise RuntimeError(f"Graph API {r.status_code}: {r.text[:300]}")
    return r.json()


def caption_for(item: dict) -> str:
    tags = " ".join(item.get("hashtags", []))
    return f"{item['caption']}\n\n{tags}".strip()


def instagram(item: dict) -> str:
    ig = env("META_IG_USER_ID")
    if not (ig and env("META_PAGE_ACCESS_TOKEN")):
        raise RuntimeError("instagram not configured")
    urls = media_urls(item)[:10]  # Instagram carousels take up to 10 items in one post
    if DRY:
        return f"dry-run:{len(urls)} images"
    with httpx.Client(timeout=120) as http:
        if len(urls) == 1:
            container = _post(http, f"{GRAPH}/{ig}/media", {"image_url": urls[0], "caption": caption_for(item)})["id"]
        else:
            kids = [_post(http, f"{GRAPH}/{ig}/media", {"image_url": u, "is_carousel_item": "true"})["id"] for u in urls]
            container = _post(http, f"{GRAPH}/{ig}/media", {"media_type": "CAROUSEL", "children": ",".join(kids),
                                                             "caption": caption_for(item)})["id"]
        for _ in range(20):  # wait until Instagram has fetched the images
            st = http.get(f"{GRAPH}/{container}", params={"fields": "status_code",
                                                           "access_token": env("META_PAGE_ACCESS_TOKEN")}).json()
            if st.get("status_code") in (None, "FINISHED"):
                break
            if st.get("status_code") == "ERROR":
                raise RuntimeError(f"instagram container error: {st}")
            time.sleep(3)
        return _post(http, f"{GRAPH}/{ig}/media_publish", {"creation_id": container})["id"]


def facebook(item: dict) -> str:
    page = env("META_PAGE_ID")
    if not (page and env("META_PAGE_ACCESS_TOKEN")):
        raise RuntimeError("facebook not configured")
    urls = media_urls(item)[:10]
    if DRY:
        return f"dry-run:{len(urls)} images"
    with httpx.Client(timeout=120) as http:
        ids = [_post(http, f"{GRAPH}/{page}/photos", {"url": u, "published": "false"})["id"] for u in urls]
        data = {"message": caption_for(item)}
        for i, pid in enumerate(ids):
            data[f"attached_media[{i}]"] = json.dumps({"media_fbid": pid})
        return _post(http, f"{GRAPH}/{page}/feed", data)["id"]


def nudge(item: dict, platform: str) -> str:
    zip_url = f"{SITE}/s/{item['id']}/all.zip"
    text = (f"📲 <b>Time to post on {platform.title()}</b>: {item['title']}\n"
            f"Sound: {item.get('audio_hint', 'any trending sound')}\n\n"
            f"<b>Caption</b>\n{item.get('tiktok_caption') or caption_for(item)}")
    telegram(text, [("Download slides (zip)", zip_url), ("Preview first slide", media_urls(item)[0])])
    return "nudged"


CHANNELS = {"instagram": instagram, "facebook": facebook}


def post_due(now: datetime | None = None, catch_up_hours: int = 6) -> list[str]:
    now = now or datetime.now(TZ)
    done = load_log()
    out = []
    for path in sorted(QUEUE.glob("*.json")):
        item = json.loads(path.read_text())
        when = due_at(item)
        if not when or when > now or now - when > timedelta(hours=catch_up_hours):
            continue
        rec = done.setdefault(item["id"], {})
        for platform in item.get("platforms", []):
            if rec.get(platform, {}).get("ok"):
                continue
            try:
                if platform in CHANNELS and env("SOCIAL_AUTOPOST", "true").lower() != "false":
                    try:
                        ref = CHANNELS[platform](item)
                    except RuntimeError as e:
                        if "not configured" not in str(e):
                            raise
                        ref = nudge(item, platform)
                else:
                    ref = nudge(item, platform)
                rec[platform] = {"ok": True, "ref": ref, "at": now.isoformat(timespec="minutes")}
                out.append(f"{item['id']} -> {platform}: {ref}")
            except Exception as e:  # one bad post must not stop the rest
                attempts = rec.get(platform, {}).get("attempts", 0) + 1
                rec[platform] = {"ok": False, "error": str(e)[:300], "attempts": attempts}
                log.error("post %s to %s failed: %s", item["id"], platform, e)
                if attempts == 1:
                    telegram(f"⚠️ Mizaj post <b>{item['id']}</b> failed on {platform}: {str(e)[:200]}")
        save_log(done)
    return out


def upcoming(days: int = 7) -> list[str]:
    now = datetime.now(TZ)
    rows = []
    for path in sorted(QUEUE.glob("*.json")):
        item = json.loads(path.read_text())
        when = due_at(item)
        if when and now <= when <= now + timedelta(days=days):
            rows.append(f"{when:%a %d %b %H:%M}  {item['id']}  {','.join(item.get('platforms', []))}")
    return rows
