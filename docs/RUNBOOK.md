# Mizaj runbook

Plain-language guide for the owner, an assistant, or Claude Code running on the server.

## 1. How it fits together

- **Website** (`mizaj.pk`): static pages served by Caddy from `/opt/mizaj/www`; the app (`mizaj-api`, port 8200)
  handles results, reports, checkout, Milan, palm reading and `/admin`.
- **Auto-deploy**: every 10 minutes the server pulls GitHub `main`; if anything changed it rebuilds, restarts and
  health-checks. A failed health check rolls back and sends a Telegram alert.
- **Alerts**: Telegram messages to the owner for every payment to verify (Approve / Reject buttons), every school or
  team lead, a daily digest at 9:05am, social posts to make by hand, and any failure.
- **Backups**: nightly copy of the database in `/opt/mizaj/backups` (21 days).
- **Weekly stats**: Monday 6:10am the server writes aggregate numbers (no personal data) to `ops/stats/latest.json`
  and pushes them to GitHub, where the weekly COO session reads them.
- **Social autoposter**: every 30 minutes posts whatever is due from `social/queue/` to Instagram and Facebook, and
  sends TikTok / Shorts posts to Telegram for posting by hand with a trending sound.

## 2. First-time setup (once)

Easiest: open Claude Code on the server and give it `docs/handoff/CLAUDE_CODE.md`; it walks through all of this
and tells you the few things only you can do. By hand:


1. Create an empty private GitHub repo `mizaj` and push this project to it (`main` branch).
2. On the server, as root: `REPO_URL=git@github.com:<you>/mizaj.git bash deploy/setup.sh`
   (download `deploy/setup.sh` from the repo first). It prints a deploy key: add it in GitHub, repo Settings,
   Deploy keys, tick "Allow write access", then run the script again. It prints your admin password at the end.
3. DNS at your .pk registrar: `A` records for `mizaj.pk` and `www.mizaj.pk` pointing at the server's IP.
   HTTPS is automatic once DNS resolves.
4. Fill `/opt/mizaj/.env` (see `.env.example`): at least one payment method (Raast ID or IBAN, JazzCash, Easypaisa),
   `SUPPORT_WHATSAPP`, and later the keys below. Then `systemctl restart mizaj-api`.
   Telegram is copied from your existing secretary bot automatically if it's on the same server.

## 3. Payments

**Day 1 (no merchant account needed):** buyers send money by Raast, bank, JazzCash or Easypaisa and enter the
transaction ID. You get a Telegram message; check your app or SMS for that TID and amount, tap Approve, confirm.
The buyer's page unlocks by itself. Duplicate TIDs are refused automatically. `/admin` lists everything waiting.
Set `AUTO_APPROVE_MANUAL=true` only if approvals become a bottleneck (unlocks instantly, you can still reject).

**Card + wallet gateway (Safepay):** apply at getsafepay.com with your CNIC, NTN and bank details (the site already
has the terms, privacy and refund pages they ask for). When approved, put the sandbox keys in `.env`
(`SAFEPAY_ENV=sandbox`), buy a report with a test card, confirm it unlocks, then switch to production keys.
The integration follows Safepay's documented hosted checkout (init order, redirect, HMAC-SHA256 signature on the
tracker); if their current API differs, ask Claude on the server: "adapt server/mizaj/payments.py to Safepay's
current docs and test in sandbox". PayFast is the alternative with lower published fees (Raast QR 0.6%).

**Gumroad (international cards in USD, the preferred overseas checkout):** the owner creates the five products in
`docs/OWNER_GUMROAD.md`. On the server set `GUMROAD_LINKS` (`full=https://….gumroad.com/l/mizaj-full,career=…`),
`GUMROAD_SELLER_ID`, `GUMROAD_ACCESS_TOKEN` and `GUMROAD_PING_SECRET` (make one with `openssl rand -hex 24`), restart,
and check `curl localhost:8200/api/health` shows `"gumroad": true`. Then paste this into Gumroad, Settings → Advanced
→ Ping: `https://mizaj.pk/api/webhooks/gumroad/<GUMROAD_PING_SECRET>`. The checkout button sends the buyer to the
product with `?order_id=…`; Gumroad pings back after the sale and the report unlocks once the secret, seller id,
product, price (at least the `usd` price), "not refunded" and, with the token, Gumroad's own API all agree. Anything
else (a sale with no Mizaj order, an offer code or purchasing-power-parity discount that lowers the price, a second
payment) is not unlocked: you get a Telegram alert, with an "Unlock anyway" button when there is an order. Keep the
secret out of chats and GitHub; if it leaks, change it in `.env` and in Gumroad. To test, buy a product while logged in
to Gumroad as yourself: the ping is marked as a test, the order unlocks, and Telegram offers a button to reject it so
it doesn't count as revenue. Gumroad's "Send test ping" button only proves the URL works (it has no order, so you
get a "no matching Mizaj order" alert). Refunds: refund in Gumroad, then reject the order in `/admin`.

**Lemon Squeezy (fallback for any product without a Gumroad link):** create a Lemon Squeezy store, one product per
report at the USD prices in `content/products.json`, add a webhook to `https://mizaj.pk/api/webhooks/lemonsqueezy`
(event `order_created`), and set `LEMONSQUEEZY_LINKS` and `LEMONSQUEEZY_WEBHOOK_SECRET`. Lemon Squeezy is moving to
Stripe Managed Payments, which does not pay out to Pakistan, so check payouts first.

**Refunds:** refund to the account the buyer paid from, then in `/admin` reject the order (locks the report).

## 4. Codes (schools, teams, creators, gifts)

In `/admin`, "Create codes": product, how many, Unlock (free) or Discount (%), uses per code, organisation.
- School class pack: product `career`, kind Unlock, one per student, organisation = school name.
- Creator code: product `*`, kind Discount 15%, uses 1000, organisation = creator handle. Pay the creator 15–20% of
  sales; count them with `SELECT COUNT(*), SUM(amount) FROM orders WHERE coupon = 'CODE' AND status = 'paid'`.

## 5. Other keys (all optional; features switch on when set)

| Setting | Get it from | Turns on |
| --- | --- | --- |
| `ANTHROPIC_API_KEY` | console.anthropic.com, add billing, create key | AI palm reading (about PKR 6 a reading, capped at 400 a day) |
| `RESEND_API_KEY` | resend.com, add domain mizaj.pk (DNS records), create key | Report links by email |
| `META_PAGE_ID`, `META_PAGE_ACCESS_TOKEN`, `META_IG_USER_ID` | Same process as faaizjaved.com: Meta app, long-lived Page token, Instagram professional account linked to the Page | Automatic Instagram + Facebook posting |
| `SOCIAL_START_DATE` | The day you want post 1 to go out | Starts the 30-day calendar |
| `META_PIXEL_ID`, `TIKTOK_PIXEL_ID` | Ads managers | Ad tracking |
| `PUBLIC_UMAMI_ID`, `PUBLIC_UMAMI_SRC` | Your existing Umami | Privacy-friendly analytics |

## 6. Daily routine for an assistant (30–45 minutes)

1. Approve payments from Telegram as they arrive (or check `/admin` twice a day).
2. Post the TikTok / Shorts the Telegram nudge sends: download the zip, upload as a photo carousel, add the suggested
   trending sound, paste the caption.
3. Reply to Instagram/TikTok comments and DMs (template answers in `docs/sales/replies.md`).
4. Forward any school or company lead to the owner the same day.

## 7. Weekly COO loop (automatic)

A scheduled Claude session runs every Monday: reads `ops/stats/latest.json`, writes `ops/reports/<date>.md`
(numbers vs plan, what worked, what to change), updates the model with actuals, writes and renders the next week of
social posts into the queue, drafts school and company outreach emails in Gmail for the owner to send, and emails the
owner a one-screen summary. See `ops/COO_PLAYBOOK.md`.

## 8. When something breaks

- Site down: `systemctl status mizaj-api`, `journalctl -u mizaj-api -n 100`, `curl localhost:8200/api/health`.
- Deploy failed: Telegram says so and it has already rolled back. `journalctl -u mizaj-update -n 50`.
- Restore the database: `systemctl stop mizaj-api`, `gunzip -c /opt/mizaj/backups/mizaj-YYYYMMDD.db.gz > /opt/mizaj/data/mizaj.db`, `chown mizaj: /opt/mizaj/data/mizaj.db`, start again.
- Anything else: open Claude Code on the server in `/opt/mizaj/app` and describe the problem; this runbook and the
  tests (`cd server && python -m pytest`) are its starting point.
