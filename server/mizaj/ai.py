"""AI palm reading (entertainment). The photo is processed in memory and never stored."""
from __future__ import annotations

import base64
import io
import json
import logging
from datetime import datetime

import anthropic
from PIL import Image, ImageOps

from . import content, db
from .config import settings

log = logging.getLogger("mizaj.ai")


class AIError(RuntimeError):
    pass


_LINE = {
    "type": "object", "additionalProperties": False,
    "required": ["seen", "summary", "detail"],
    "properties": {
        "seen": {"type": "string", "description": "What is visibly there: length, depth, curve, breaks, branches."},
        "summary": {"type": "string", "description": "One warm sentence, max 25 words."},
        "detail": {"type": "string", "description": "90-130 words of personality-style reading."},
    },
}
SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["is_palm", "retake_tip", "hand_shape", "heart", "head", "life", "fate", "mounts", "headline", "teaser", "type_note"],
    "properties": {
        "is_palm": {"type": "boolean"},
        "retake_tip": {"type": "string", "description": "If the photo is unusable, a short tip to retake it; else empty."},
        "hand_shape": {
            "type": "object", "additionalProperties": False, "required": ["element", "text"],
            "properties": {"element": {"type": "string", "enum": ["Earth", "Air", "Fire", "Water"]},
                           "text": {"type": "string", "description": "60-90 words"}},
        },
        "heart": _LINE, "head": _LINE, "life": _LINE, "fate": _LINE,
        "mounts": {"type": "array", "items": {
            "type": "object", "additionalProperties": False, "required": ["name", "text"],
            "properties": {"name": {"type": "string"}, "text": {"type": "string", "description": "30-50 words"}}}},
        "headline": {"type": "string", "description": "A catchy one-line title for this palm, max 10 words."},
        "teaser": {"type": "string", "description": "70-100 words: the free preview. Warm, specific, ends on curiosity."},
        "type_note": {"type": "string", "description": "60-90 words linking the palm to the person's personality type if given, else to their hand element."},
    },
}

SYSTEM = """You are Mizaj's palm reader: a warm, witty storyteller who reads palms as a fun mirror for personality, never as fortune-telling.

Read ONLY what is actually visible in the photo (line length, depth, curvature, breaks, forks, chains, hand and finger proportions, mount fullness) and translate it with traditional palmistry symbolism into personality insights: how the person loves, thinks, uses energy and pursues purpose.

Hard rules:
- Entertainment framing. Never predict events, dates, illness, death, lifespan, number of marriages or children, wealth, divorce, accidents or luck. The life line describes vitality and energy style, NEVER length of life.
- No religious claims; do not say the stars or lines control destiny.
- Kind and uplifting; a "challenge" is always paired with a strength.
- Write for everyone, anywhere: everyday scenes (work, study, friends, family, hobbies, travel) with no single culture,
  country or religion as the default; no slang only one community gets; never stereotype.
- Address the reader as "you". English, simple and vivid.
- If the image is not a clear palm (blurry, back of hand, not a hand, too dark), set is_palm=false, give a one-line retake_tip, and fill the other fields with empty strings, element "Earth" and an empty mounts list.
- Give 3 mounts when is_palm is true."""


def _quota_ok() -> bool:
    key = f"ai_calls:{datetime.now().strftime('%Y-%m-%d')}"
    used = int(db.kv_get(key, "0") or 0)
    if used >= settings.ai_daily_cap:
        return False
    db.kv_set(key, str(used + 1))
    return True


def prepare_image(raw: bytes) -> str:
    try:
        img = Image.open(io.BytesIO(raw))
        img = ImageOps.exif_transpose(img).convert("RGB")
    except Exception as e:  # Pillow raises many types for bad input
        raise AIError("That file doesn't look like a photo. Please upload a JPG or PNG of your palm.") from e
    img.thumbnail((1024, 1024))
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=85)  # re-encoding drops EXIF/location metadata
    return base64.standard_b64encode(buf.getvalue()).decode()


def read_palm(raw: bytes, hand: str, name: str | None, type_code: str | None) -> dict:
    if not settings.has_ai:
        raise AIError("Palm reading is switching on soon. Please check back in a day or two.")
    if not _quota_ok():
        raise AIError("Our palm reader is very busy today. Please try again tomorrow.")
    data = prepare_image(raw)
    who = f"Name: {name}." if name else "Name: not given."
    if type_code:
        t = content.type_summary(type_code)
        who += f" Personality type: {type_code} ({t['name_en']})."
    prompt = (f"{who} This is their {hand or 'dominant'} hand. Give a palm reading as JSON in the required schema.")
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key, timeout=90, max_retries=2)
    try:
        resp = client.beta.messages.create(
            model=settings.ai_model,
            max_tokens=4000,
            system=SYSTEM,
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            output_config={"effort": "low", "format": {"type": "json_schema", "schema": SCHEMA}},
            messages=[{"role": "user", "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": data}},
                {"type": "text", "text": prompt},
            ]}],
        )
    except anthropic.RateLimitError as e:
        raise AIError("Our palm reader is very busy right now. Please try again in a minute.") from e
    except anthropic.APIStatusError as e:
        log.error("palm reading API error %s: %s", e.status_code, e)
        raise AIError("Something went wrong reading your palm. Please try again.") from e
    except anthropic.APIConnectionError as e:
        log.error("palm reading connection error: %s", e)
        raise AIError("Something went wrong reading your palm. Please try again.") from e
    if resp.stop_reason == "refusal":
        raise AIError("We couldn't read this photo. Please try a different one: open palm, good light, plain background.")
    text = next((b.text for b in resp.content if b.type == "text"), "")
    try:
        reading = json.loads(text)
    except ValueError as e:
        raise AIError("Something went wrong reading your palm. Please try again.") from e
    log.info("palm usage in=%s out=%s", resp.usage.input_tokens, resp.usage.output_tokens)
    return reading


FREE_KEYS = ("is_palm", "retake_tip", "headline", "teaser", "hand_shape")


def palm_view(reading: dict, premium: bool) -> dict:
    if premium:
        return reading
    view = {k: reading.get(k) for k in FREE_KEYS}
    view["heart"] = {"summary": (reading.get("heart") or {}).get("summary", "")}
    view["locked"] = ["head", "life", "fate", "mounts", "type_note"]
    return view
