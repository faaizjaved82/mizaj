"""Owner alerts (Telegram) and customer email (Resend). Both dry-run when not configured."""
from __future__ import annotations

import hashlib
import hmac
import html
import logging

import httpx

from .config import settings

log = logging.getLogger("mizaj.notify")


def sign(*parts: str) -> str:
    msg = "|".join(parts).encode()
    return hmac.new(settings.secret_key.encode(), msg, hashlib.sha256).hexdigest()[:32]


def verify(sig: str, *parts: str) -> bool:
    return hmac.compare_digest(sig or "", sign(*parts))


def telegram(text: str, buttons: list[list[tuple[str, str]]] | None = None) -> bool:
    """Send an HTML message to the owner. buttons = rows of (label, url)."""
    if not (settings.telegram_bot_token and settings.telegram_owner_id) or settings.dry_run:
        log.info("[telegram dry-run] %s", text)
        return False
    payload: dict = {"chat_id": settings.telegram_owner_id, "text": text[:4000], "parse_mode": "HTML",
                     "disable_web_page_preview": True}
    if buttons:
        payload["reply_markup"] = {"inline_keyboard": [[{"text": t, "url": u} for t, u in row] for row in buttons]}
    try:
        r = httpx.post(f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage", json=payload, timeout=10)
        r.raise_for_status()
        return True
    except httpx.HTTPError as e:
        log.warning("telegram failed: %s", e)
        return False


def esc(s: object) -> str:
    return html.escape(str(s or ""))


def email(to: str, subject: str, html_body: str) -> bool:
    if not to or "@" not in to:
        return False
    if not settings.resend_api_key or settings.dry_run:
        log.info("[email dry-run] to=%s subject=%s", to, subject)
        return False
    try:
        r = httpx.post("https://api.resend.com/emails", timeout=15,
                       headers={"Authorization": f"Bearer {settings.resend_api_key}"},
                       json={"from": settings.mail_from, "to": [to], "subject": subject, "html": html_body,
                             "reply_to": settings.support_email})
        r.raise_for_status()
        return True
    except httpx.HTTPError as e:
        log.warning("email failed: %s", e)
        return False


def email_shell(title: str, body_html: str, cta_label: str = "", cta_url: str = "") -> str:
    cta = (f'<p style="margin:28px 0"><a href="{esc(cta_url)}" style="background:#1B1530;color:#FBF6EE;'
           f'padding:14px 22px;border-radius:999px;text-decoration:none;font-weight:600">{esc(cta_label)}</a></p>'
           if cta_url else "")
    return f"""<div style="background:#FBF6EE;padding:32px 16px;font-family:Helvetica,Arial,sans-serif;color:#231C2E">
<div style="max-width:560px;margin:0 auto;background:#fff;border-radius:18px;padding:32px">
<p style="font-size:22px;font-weight:700;margin:0 0 4px">mizaj <span style="color:#C8443A">مزاج</span></p>
<h1 style="font-size:22px;margin:18px 0 12px">{esc(title)}</h1>
<div style="font-size:16px;line-height:1.6">{body_html}</div>{cta}
<p style="font-size:13px;color:#7a7186;margin-top:28px">Questions? Reply to this email. Mizaj · mizaj.pk</p>
</div></div>"""
