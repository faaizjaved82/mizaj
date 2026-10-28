import os
import sys
import tempfile
from pathlib import Path

_tmp = tempfile.mkdtemp(prefix="mizaj-test-")
os.environ.update({
    "MIZAJ_ENV_FILE": "/nonexistent",
    "MIZAJ_DATA_DIR": _tmp,
    "MIZAJ_DIST_DIR": str(Path(_tmp) / "dist-none"),
    "SITE_URL": "http://testserver",
    "ADMIN_TOKEN": "admin-secret",
    "SECRET_KEY": "test-secret",
    "PAY_JAZZCASH_NUMBER": "03001234567",
    "PAY_JAZZCASH_TITLE": "Mizaj Test",
    "PAY_BANK_IBAN": "PK00TEST0000000000000000",
    "PAY_RAAST_ID": "03001234567",
    "LEMONSQUEEZY_WEBHOOK_SECRET": "ls-secret",
    "SAFEPAY_SECRET_KEY": "sp-secret",
})
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
