"""Settings, read once from the environment (see .env.example).

Every integration has a dry-run mode: when its credentials are missing the
feature logs instead of failing, so the site runs end to end with no keys.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parents[2]


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def _bool(name: str, default: bool = False) -> bool:
    v = _env(name)
    return default if not v else v.lower() in ("1", "true", "yes", "on")


def _load_dotenv() -> None:
    """Minimal .env loader (no dependency). Real env vars win."""
    path = Path(_env("MIZAJ_ENV_FILE") or REPO_DIR / ".env")
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


_load_dotenv()


@dataclass
class Settings:
    site_url: str = field(default_factory=lambda: _env("SITE_URL", "https://mizaj.pk").rstrip("/"))
    data_dir: Path = field(default_factory=lambda: Path(_env("MIZAJ_DATA_DIR") or REPO_DIR / "data"))
    content_dir: Path = field(default_factory=lambda: Path(_env("MIZAJ_CONTENT_DIR") or REPO_DIR / "content"))
    templates_dir: Path = REPO_DIR / "site" / "templates"
    static_dir: Path = REPO_DIR / "site" / "static"
    dist_dir: Path = field(default_factory=lambda: Path(_env("MIZAJ_DIST_DIR") or REPO_DIR / "dist"))
    tz: str = field(default_factory=lambda: _env("TZ_NAME", "Asia/Karachi"))

    admin_token: str = field(default_factory=lambda: _env("ADMIN_TOKEN"))
    secret_key: str = field(default_factory=lambda: _env("SECRET_KEY", "dev-insecure-secret-change-me"))

    # Telegram alerts to the owner (can reuse an existing bot token; we only send messages)
    telegram_bot_token: str = field(default_factory=lambda: _env("TELEGRAM_BOT_TOKEN"))
    telegram_owner_id: str = field(default_factory=lambda: _env("TELEGRAM_OWNER_ID"))

    # Email (Resend API). Missing key = dry run.
    resend_api_key: str = field(default_factory=lambda: _env("RESEND_API_KEY"))
    mail_from: str = field(default_factory=lambda: _env("MAIL_FROM", "Mizaj <hello@mizaj.pk>"))
    support_email: str = field(default_factory=lambda: _env("SUPPORT_EMAIL", "hello@mizaj.pk"))
    support_whatsapp: str = field(default_factory=lambda: _env("SUPPORT_WHATSAPP"))  # e.g. 923001234567

    # AI (palm reading, personal notes). Missing key = feature shows "coming soon".
    anthropic_api_key: str = field(default_factory=lambda: _env("ANTHROPIC_API_KEY"))
    ai_model: str = field(default_factory=lambda: _env("MIZAJ_AI_MODEL", "claude-opus-5-5"))
    ai_daily_cap: int = field(default_factory=lambda: int(_env("AI_DAILY_CAP", "400")))

    # Manual wallet / bank transfer details shown at checkout
    jazzcash_number: str = field(default_factory=lambda: _env("PAY_JAZZCASH_NUMBER"))
    jazzcash_title: str = field(default_factory=lambda: _env("PAY_JAZZCASH_TITLE"))
    easypaisa_number: str = field(default_factory=lambda: _env("PAY_EASYPAISA_NUMBER"))
    easypaisa_title: str = field(default_factory=lambda: _env("PAY_EASYPAISA_TITLE"))
    bank_name: str = field(default_factory=lambda: _env("PAY_BANK_NAME"))
    bank_title: str = field(default_factory=lambda: _env("PAY_BANK_TITLE"))
    bank_iban: str = field(default_factory=lambda: _env("PAY_BANK_IBAN"))
    raast_id: str = field(default_factory=lambda: _env("PAY_RAAST_ID"))
    # Unlock immediately when a buyer submits a transaction ID; owner verifies later and can revoke.
    auto_approve_manual: bool = field(default_factory=lambda: _bool("AUTO_APPROVE_MANUAL", False))

    # Card / wallet gateway (Safepay). Missing keys = gateway button hidden.
    safepay_env: str = field(default_factory=lambda: _env("SAFEPAY_ENV", "sandbox"))  # sandbox | production
    safepay_api_key: str = field(default_factory=lambda: _env("SAFEPAY_API_KEY"))
    safepay_secret_key: str = field(default_factory=lambda: _env("SAFEPAY_SECRET_KEY"))
    safepay_webhook_secret: str = field(default_factory=lambda: _env("SAFEPAY_WEBHOOK_SECRET"))

    # International cards (diaspora) via Lemon Squeezy hosted checkout links. Missing = hidden.
    lemonsqueezy_webhook_secret: str = field(default_factory=lambda: _env("LEMONSQUEEZY_WEBHOOK_SECRET"))
    lemonsqueezy_links: str = field(default_factory=lambda: _env("LEMONSQUEEZY_LINKS"))  # product=url,product=url

    # Analytics / ads pixels (optional)
    umami_id: str = field(default_factory=lambda: _env("PUBLIC_UMAMI_ID"))
    umami_src: str = field(default_factory=lambda: _env("PUBLIC_UMAMI_SRC"))
    meta_pixel_id: str = field(default_factory=lambda: _env("META_PIXEL_ID"))
    tiktok_pixel_id: str = field(default_factory=lambda: _env("TIKTOK_PIXEL_ID"))

    # Public social profiles shown in the footer: "instagram=https://...,tiktok=https://..."
    socials_raw: str = field(default_factory=lambda: _env("SOCIALS"))

    dry_run: bool = field(default_factory=lambda: _bool("DRY_RUN", False))

    @property
    def socials(self) -> dict[str, str]:
        out = {}
        for part in self.socials_raw.split(","):
            if "=" in part:
                k, v = part.split("=", 1)
                out[k.strip()] = v.strip()
        return out

    @property
    def db_path(self) -> Path:
        return self.data_dir / "mizaj.db"

    @property
    def has_ai(self) -> bool:
        return bool(self.anthropic_api_key)

    @property
    def has_safepay(self) -> bool:
        return bool(self.safepay_api_key and self.safepay_secret_key)

    @property
    def ls_links(self) -> dict[str, str]:
        out = {}
        for part in self.lemonsqueezy_links.split(","):
            if "=" in part:
                k, v = part.split("=", 1)
                out[k.strip()] = v.strip()
        return out

    def manual_methods(self) -> list[dict]:
        """Zero-fee methods, cheapest and most instant first (Raast), then wallets."""
        m = []
        if self.bank_iban or self.raast_id:
            m.append({"key": "bank", "label": "Raast / Bank", "account": self.bank_iban,
                      "raast": self.raast_id, "title": self.bank_title, "bank": self.bank_name})
        if self.jazzcash_number:
            m.append({"key": "jazzcash", "label": "JazzCash", "account": self.jazzcash_number, "title": self.jazzcash_title})
        if self.easypaisa_number:
            m.append({"key": "easypaisa", "label": "Easypaisa", "account": self.easypaisa_number, "title": self.easypaisa_title})
        return m


settings = Settings()
