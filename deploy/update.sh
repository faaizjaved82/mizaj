#!/usr/bin/env bash
# Pull the latest code from GitHub; if anything changed, rebuild the site and restart. Runs every 10 minutes.
set -euo pipefail
ROOT=/opt/mizaj
cd "$ROOT/app"
OLD=$(sudo -u mizaj git rev-parse HEAD)
sudo -u mizaj git pull --ff-only -q origin main || { echo "git pull failed"; exit 1; }
NEW=$(sudo -u mizaj git rev-parse HEAD)
if [ "$OLD" = "$NEW" ] && [ "${1:-}" != "--force" ]; then exit 0; fi
sudo -u mizaj "$ROOT/venv/bin/pip" install -q -e "$ROOT/app/server" -e "$ROOT/app/social"
sudo -u mizaj env MIZAJ_ENV_FILE="$ROOT/.env" MIZAJ_DIST_DIR="$ROOT/app/dist" "$ROOT/venv/bin/python" "$ROOT/app/build.py"
rsync -a --delete "$ROOT/app/dist/" "$ROOT/www/"
systemctl restart mizaj-api
sleep 2
if curl -fsS http://127.0.0.1:8200/api/health >/dev/null; then
  echo "deployed $NEW"
  # Forward any new weekly COO report to the owner on Telegram.
  for f in $(sudo -u mizaj git diff --name-only --diff-filter=A "$OLD" "$NEW" -- ops/reports/ 2>/dev/null); do
    sudo -u mizaj env MIZAJ_ENV_FILE="$ROOT/.env" PYTHONPATH="$ROOT/app/server" "$ROOT/venv/bin/python" - "$ROOT/app/$f" <<'PY' || true
import sys
from mizaj import notify
text = open(sys.argv[1], encoding="utf-8").read()
head = "\n".join(text.splitlines()[:30])
notify.telegram("📊 <b>Weekly COO report</b>\n\n" + notify.esc(head)[:3500])
PY
  done
else
  echo "health check failed after deploy of $NEW, rolling back to $OLD"
  sudo -u mizaj git reset -q --hard "$OLD"
  sudo -u mizaj env MIZAJ_ENV_FILE="$ROOT/.env" MIZAJ_DIST_DIR="$ROOT/app/dist" "$ROOT/venv/bin/python" "$ROOT/app/build.py"
  rsync -a --delete "$ROOT/app/dist/" "$ROOT/www/"
  systemctl restart mizaj-api
  sudo -u mizaj env MIZAJ_ENV_FILE="$ROOT/.env" PYTHONPATH="$ROOT/app/server" "$ROOT/venv/bin/python" -c \
    "from mizaj import notify; notify.telegram('⚠️ Mizaj deploy of $NEW failed its health check and was rolled back to $OLD.')" || true
  exit 1
fi
