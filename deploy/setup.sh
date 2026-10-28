#!/usr/bin/env bash
# One-time (idempotent) setup of Mizaj on the VPS that already runs faaizjaved.com. Run as root:
#   REPO_URL=git@github.com:faaizjaved82/mizaj.git bash setup.sh
# Everything lives under /opt/mizaj and runs as the `mizaj` user. Other sites are not touched.
set -euo pipefail
ROOT=/opt/mizaj
REPO_URL=${REPO_URL:?set REPO_URL, e.g. git@github.com:faaizjaved82/mizaj.git}

echo "== user and folders"
id mizaj >/dev/null 2>&1 || useradd --system --create-home --home-dir "$ROOT" --shell /bin/bash mizaj
install -d -o mizaj -g mizaj -m 750 "$ROOT" "$ROOT/data" "$ROOT/backups"
install -d -o mizaj -g mizaj -m 755 "$ROOT/www"
chmod 755 "$ROOT"

echo "== packages"
apt-get update -qq
apt-get install -y -qq python3-venv python3-pip git curl rsync sqlite3 >/dev/null

echo "== deploy key"
if [ ! -f "$ROOT/.ssh/id_ed25519" ]; then
  sudo -u mizaj mkdir -p "$ROOT/.ssh"
  sudo -u mizaj ssh-keygen -q -t ed25519 -N "" -C "mizaj@vps" -f "$ROOT/.ssh/id_ed25519"
  sudo -u mizaj bash -c "ssh-keyscan -t ed25519 github.com >> $ROOT/.ssh/known_hosts 2>/dev/null"
fi
echo "---- DEPLOY KEY: add to GitHub repo Settings > Deploy keys, tick 'Allow write access' ----"
cat "$ROOT/.ssh/id_ed25519.pub"
echo "------------------------------------------------------------------------------------------"

if [ ! -d "$ROOT/app/.git" ]; then
  sudo -u mizaj git clone -q "$REPO_URL" "$ROOT/app" || { echo "Add the deploy key above to GitHub, then rerun."; exit 2; }
fi

echo "== env file"
if [ ! -f "$ROOT/.env" ]; then
  install -o mizaj -g mizaj -m 600 "$ROOT/app/.env.example" "$ROOT/.env"
  sed -i "s|^SECRET_KEY=.*|SECRET_KEY=$(openssl rand -hex 32)|; s|^ADMIN_TOKEN=.*|ADMIN_TOKEN=$(openssl rand -hex 12)|; s|^MIZAJ_DATA_DIR=.*|MIZAJ_DATA_DIR=$ROOT/data|" "$ROOT/.env"
  # Reuse the owner's Telegram secretary bot if it exists on this server
  if [ -f /opt/faaizjaved/.env ]; then
    for k in TELEGRAM_BOT_TOKEN TELEGRAM_OWNER_ID; do
      v=$(grep -E "^$k=" /opt/faaizjaved/.env | cut -d= -f2- || true)
      [ -n "$v" ] && sed -i "s|^$k=.*|$k=$v|" "$ROOT/.env"
    done
  fi
  echo "Created $ROOT/.env. Your admin password is: $(grep ^ADMIN_TOKEN= $ROOT/.env | cut -d= -f2)"
fi

echo "== python"
[ -d "$ROOT/venv" ] || sudo -u mizaj python3 -m venv "$ROOT/venv"
sudo -u mizaj "$ROOT/venv/bin/pip" install -q --upgrade pip

echo "== services"
cp "$ROOT/app/deploy/systemd/"*.service "$ROOT/app/deploy/systemd/"*.timer /etc/systemd/system/
systemctl daemon-reload
bash "$ROOT/app/deploy/update.sh" --force
systemctl enable --now mizaj-api mizaj-update.timer mizaj-digest.timer mizaj-backup.timer mizaj-stats.timer mizaj-social.timer

echo "== caddy"
install -d /etc/caddy/sites
cp "$ROOT/app/deploy/mizaj.caddy" /etc/caddy/sites/mizaj.caddy
grep -q "import /etc/caddy/sites/\*.caddy" /etc/caddy/Caddyfile || { cp /etc/caddy/Caddyfile /etc/caddy/Caddyfile.bak.$(date +%s); printf '\nimport /etc/caddy/sites/*.caddy\n' >> /etc/caddy/Caddyfile; }
caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile
systemctl reload caddy

echo "== done. Point mizaj.pk and www.mizaj.pk (A records) at this server's IP; Caddy gets HTTPS automatically."
curl -fsS http://127.0.0.1:8200/api/health && echo
