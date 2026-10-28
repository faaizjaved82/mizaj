# Handshake for Claude Code on the server (`claude-server`)

Hello from `claude-cloud`, the acting COO. I built Mizaj in a cloud session that cannot reach the owner's VPS, the
mizaj.pk domain, Meta, Safepay or any account that needs his identity. You can. Please take Mizaj live and finish the
tasks below. Work through them in order; each has a check. Ask the owner (Faaiz) only for what is marked **[owner]**.

Read first: `AGENTS.md` (team and rules), `docs/RUNBOOK.md` (how production works), `deploy/setup.sh`.

## What you're deploying

- A static site (Caddy serves `/opt/mizaj/www`) plus a FastAPI app (`mizaj-api`, port 8200) for results, reports,
  checkout, Milan, palm reading and `/admin`.
- systemd timers: auto-deploy from GitHub every 10 minutes (with rollback), 9:05am Telegram digest, nightly backup,
  Monday stats export, social autoposter every 30 minutes.
- It lives beside faaizjaved.com on the same server. Don't touch `/opt/faaizjaved`, `/opt/639hz`, their users or
  services. `setup.sh` only adds `/etc/caddy/sites/mizaj.caddy` and an import line if missing.

## Step 1: preflight (you, 5 min)

Run as a user with sudo and report the results in your log:
- `lsb_release -a; python3 --version; caddy version; df -h /; free -h`
- `grep -n "import /etc/caddy/sites" /etc/caddy/Caddyfile` (already there for faaizjaved.com: fine)
- `ss -ltnp | grep -E ':8200|:80|:443'` (8200 must be free)
- The server's public IPv4: `curl -4 -s ifconfig.me`

Check: Python ≥ 3.11, Caddy present, port 8200 free.

## Step 2: get the code onto the server (you + [owner], 10 min)

The repo is private: `git@github.com:faaizjaved82/mizaj.git`. `deploy/setup.sh` is idempotent and does everything
once the repo is cloned, but it lives inside the repo, so bootstrap like this:

```bash
sudo useradd --system --create-home --home-dir /opt/mizaj --shell /bin/bash mizaj || true
sudo -u mizaj mkdir -p /opt/mizaj/.ssh
sudo -u mizaj ssh-keygen -q -t ed25519 -N "" -C "mizaj@vps" -f /opt/mizaj/.ssh/id_ed25519
sudo -u mizaj bash -c "ssh-keyscan -t ed25519 github.com >> /opt/mizaj/.ssh/known_hosts"
sudo cat /opt/mizaj/.ssh/id_ed25519.pub
```

**[owner]** Add that public key at github.com/faaizjaved82/mizaj → Settings → Deploy keys → Add, and tick
**Allow write access** (the server pushes the weekly stats back). Then:

```bash
sudo -u mizaj git clone -q git@github.com:faaizjaved82/mizaj.git /opt/mizaj/app
sudo REPO_URL=git@github.com:faaizjaved82/mizaj.git bash /opt/mizaj/app/deploy/setup.sh
```

Check: the script ends with `{"ok":true,...}`; `systemctl status mizaj-api` is active; `systemctl list-timers
'mizaj-*'` shows five timers. Give the owner the admin password the script printed (or read it from
`/opt/mizaj/.env`, `ADMIN_TOKEN`), privately, not in git or logs.

## Step 3: settings (you + [owner], 10 min)

`/opt/mizaj/.env` was created from `.env.example`, with Telegram copied from the faaizjaved.com bot if present.
**[owner]** Ask for, and fill in:
- At least one payment method: `PAY_RAAST_ID` and/or `PAY_BANK_NAME`, `PAY_BANK_TITLE`, `PAY_BANK_IBAN`;
  `PAY_JAZZCASH_NUMBER` + `PAY_JAZZCASH_TITLE`; `PAY_EASYPAISA_NUMBER` + `PAY_EASYPAISA_TITLE`.
- `SUPPORT_WHATSAPP` (format `923001234567`) and `SUPPORT_EMAIL` if not hello@mizaj.pk.

Then `sudo systemctl restart mizaj-api`.
Check: `curl -s localhost:8200/api/health` is ok; if Telegram is set, `sudo -u mizaj env MIZAJ_ENV_FILE=/opt/mizaj/.env
PYTHONPATH=/opt/mizaj/app/server /opt/mizaj/venv/bin/python -m mizaj digest` sends a message to the owner.

## Step 4: domain (you + [owner], 10 min + propagation)

**[owner]** At the .pk registrar (PKNIC or reseller): `A` records for `mizaj.pk` and `www.mizaj.pk` → the IP from
step 1. Remove any old records pointing at the previous host.
Check: `dig +short mizaj.pk` returns the IP; `curl -sI https://mizaj.pk` returns 200 (Caddy gets the certificate by
itself once DNS resolves; watch `journalctl -u caddy -n 50` if not).

## Step 5: prove the money path works (you, 15 min)

On your own phone or with curl, on https://mizaj.pk:
1. Take the personality test, open the result, tap Unlock, choose Raast/JazzCash, submit a fake TID like `TEST00001`.
2. The owner should get a Telegram message with Approve/Reject. Reject it (it's fake) from the link.
3. In `/admin` create one Unlock code for `full`, redeem it on the result page, confirm the full report shows.
4. Try `/milan/`, `/burj/`, `/adad/`, `/schools/` (submit a test lead, then tell the owner it was a test).

Check: all of the above work. Report anything odd as a task for `claude-cloud`.

## Step 6: weekly stats round trip (you, 5 min)

`sudo systemctl start mizaj-stats` then confirm a commit "ops: weekly stats" appears on GitHub `main`.
Check: `ops/stats/latest.json` exists on GitHub. If the push failed, the deploy key lacks write access.

## Step 7: social posting (you + [owner], 30 min, when the accounts exist)

**[owner]** creates Instagram `@mizaj.pk` (professional), Facebook Page "Mizaj", TikTok `@mizaj.pk`, YouTube
`@mizajpk`, with the bios in `social/plan/launch30.json` → `bios`, and the logo (`site/static/og/default.png` or
`site/static/img/logo.svg`).
You: get a long-lived Page access token and the Instagram user id the same way faaizjaved.com does
(`/opt/faaizjaved/app/engine/lifeengine/publishers/` and its docs show the flow), put `META_PAGE_ID`,
`META_PAGE_ACCESS_TOKEN`, `META_IG_USER_ID` in `/opt/mizaj/.env`, update `SOCIALS=` with the real profile URLs, and
set `SOCIAL_START_DATE` to the day the owner wants post 1 to go out.
Check: `sudo -u mizaj env MIZAJ_ENV_FILE=/opt/mizaj/.env /opt/mizaj/venv/bin/python -m mizaj_social upcoming`
lists the first week; after the first slot, the post is live on Instagram and Facebook and the TikTok nudge arrived on
Telegram.

## Step 8: card payments (you, when [owner] has Safepay sandbox keys)

Put sandbox keys in `.env` (`SAFEPAY_ENV=sandbox`), restart, buy a report with Safepay's test card, confirm it unlocks.
The integration in `server/mizaj/payments.py` follows Safepay's documented hosted checkout (order init → redirect to
components → HMAC-SHA256 of the tracker on return) but was written without access to their docs: compare it with
Safepay's current docs and fix it on a branch with tests, PR, ask `codex` or `claude-cloud` to review. Only then
switch to production keys.

## Step 9: AI palm reading (you, 5 min, when [owner] gives an Anthropic API key)

`ANTHROPIC_API_KEY=...` in `.env`, restart, upload a palm photo at `/palm/`.
Check: a reading appears; `journalctl -u mizaj-api | grep "palm usage"` shows token counts.

## Step 10: report back

Write `ops/log/<date>-claude-server-launch.md`: what's live, what's blocked and on whom, anything you changed.
Update `ops/TASKS.md` (T01–T09 statuses). Commit and push to `main` with the server's deploy key, or open a PR if you
changed code.

## Ongoing (whenever the owner opens you on the server)

- Health: `systemctl status mizaj-api`, `journalctl -u mizaj-update -n 30`, `ls -lh /opt/mizaj/backups | tail -3`.
- Numbers on request: aggregate queries on `/opt/mizaj/data/mizaj.db` (counts, sums). Never paste personal data
  into git, logs or chat beyond what the owner needs to act on.
- Anything the cloud agents can't reach (live site checks, logs, DB questions, gateway tests) is yours: look for
  tasks with owner `claude-server` in `ops/TASKS.md`.
