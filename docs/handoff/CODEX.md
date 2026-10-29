# Mizaj operator handoff for Codex (`codex`)

Written 29 October 2026 by `claude-cloud`, the acting COO who built and relaunched Mizaj. From today **you run
Mizaj day to day**: the product, the content, the code, the social and ads machinery, the weekly numbers and the
task board. The owner, Faaiz Javed, makes decisions about money and accounts; `claude-server` (Claude Code on the
VPS) does anything that needs the server; a scheduled Claude session reviews your server and payment changes on
Mondays. Everything you need is in this repo. Nothing important lives only in a chat.

> **29 Oct 2026, later the same day:** the owner gave the operator role to Claude Code on his Mac (`claude-ops`).
> Read "you" in this file as the operator, whoever that is; `codex` now does images and independent code reviews.

---

## 0. Your first session (about an hour)

1. Read, in this order: this file → `AGENTS.md` (team, workflow, hard rules) → `docs/PLAN.md` (the business and
   every decision so far) → `content/STYLE.md` (v3, the voice: for everyone) → `ops/TASKS.md` (the board) → the
   newest files in `ops/log/` → `docs/ADS.md` → `docs/RUNBOOK.md` (production).
2. Set up and prove the toolchain:
   ```bash
   python3 -m venv .venv && . .venv/bin/activate && pip install -e server -e social pytest
   cd server && python -m pytest -q && cd ..        # 38 tests on main (T40 merged)
   python build.py                                  # 177 pages into dist/
   npm install --no-save playwright && npx playwright install chromium   # once, at the repo root (tools/ uses it)
   mkdir -p /tmp/mizaj && (cd server && ADMIN_TOKEN=dev MIZAJ_DATA_DIR=/tmp/mizaj PAY_RAAST_ID=03000000000 uvicorn mizaj.api:app --port 8300) &
   node tools/e2e.cjs http://127.0.0.1:8300 /tmp/shots dev   # phone-sized end-to-end test, must print ALL E2E CHECKS PASSED
   ```
   Python must be 3.11+ (macOS's `python3` is 3.9: use `python3.12 -m venv`). The e2e test needs a manual payment
   method set (the dummy `PAY_RAAST_ID` above), or the TID form is hidden.
   `tools/render_social.py` and `tools/make_og.py` need Node + Playwright (`tools/shoot.cjs` uses `require("playwright")`).
3. Review and merge **PR #4 (T40, regional pricing)**: https://github.com/faaizjaved82/mizaj/pull/4. It is payment
   logic written by `claude-cloud`; you are the second reviewer the rules require. Read the diff and the 10 tests in
   `server/tests/test_regional_pricing.py`; check the checkout for an `intl` order shows `$9` and "Charged as PKR
   2,520 by Safepay"; merge when satisfied (CI is green). Then add a task for `claude-server`: one Safepay sandbox
   card payment from a non-Pakistan timezone.
4. Take over the board: tasks owned by `claude-cloud` that are not "done" are now yours (see §6). Set your first
   task to `doing`, and end the session with `ops/log/<date>-codex-<slug>.md`.

---

## 1. The business on one page

- **What:** a free personality test (16 types with our own names) plus the four classical temperaments shown as
  elements (Air, Fire, Water, Earth; Hippocrates → Galen → Ibn Sina). Together: one of 64 cards in **the Mizaj
  Deck**. Paid one-time reports go deeper. Also: Mizaj Milan (a test for two), Career Compass (interest test for
  students and career changers), AI palm reading, zodiac × type and name numbers (all "for fun").
- **Who:** everyone who wants to know more about themselves, others and the world: students, professionals and
  managers, educators, marketers, couples and families, young and old, any country. Not one culture (owner, 29 Oct).
- **Money:** phase 1 = one-time reports ($9 / PKR 599 full report up to $24 / PKR 1,999 bundle), B2B school and team
  packs. Phase 2 = subscriptions ("Mizaj Plus", design in `docs/PLAN.md` §3, task T43).
- **Growth:** ads + socials (owner, 29 Oct), powered by the share card and Milan invites; B2B sales to schools and
  teams; search pages.
- **Goal:** PKR 15–20 lakh cumulative profit by 30 June 2027.
- **Honest constraint:** a $9 one-time report doesn't pay for broad ads on the first sale (`docs/ADS.md` §1). Phase 1
  ads are a capped test to find what does pay; subscriptions are what make ads work at scale.

---

## 2. The story so far

| When | What happened |
| --- | --- |
| Before 28 Oct | mizaj.pk was an old personality-test site with no revenue, no payment flow and no social presence. |
| 28 Oct | `claude-cloud` researched the market (`docs/research/01–04`), rebuilt everything (site, tests, 63,000 words of reports, payments, admin, social engine, deploy, financial model), set up the team (`AGENTS.md`, handoffs, CI) and a weekly Monday review. The owner created the GitHub repo; `claude-server` deployed to the VPS (T01–T03, T07 done; weekly stats arrive); you made the first illustration set (T21). |
| 28 Oct (evening) | Owner: the images "look bad", "not properly placed", "too Pakistani". Research 05 (social trends) and 06 (going international). Repositioned for "desis everywhere"; built **the Mizaj Deck** (cards drawn in code); retired the illustrations; new 3:4 social renderer; new 30-day plan; ART_BRIEF v2 for you (T31). |
| 29 Oct | Owner: "forget the word desis… it's for everyone". No Gumroad (PR #3 closed). Ads + socials now; subscriptions in phase 2. STYLE v3; all content, site copy and the social plan made universal; card-first checkout for every country; ad pixel events; `docs/ADS.md` + 9 ad creatives; regional pricing built (PR #4). Then this handoff: you run the project. |

Full detail: `git log`, `ops/log/`, `docs/PLAN.md` §2.

---

## 3. Your job: the operating loop

### Every working day (15–30 minutes)
- Check GitHub: CI on `main` green? New issues or PRs? Deploys happen automatically within 10 minutes of a push to
  `main`; a failed health check rolls back and alerts the owner on Telegram.
- Pick the next task from `ops/TASKS.md` and ship it (branch → PR → merge when allowed, see §8).
- Keep `ops/TASKS.md` true: status changes in the same commit as the work.

### Every Monday (about 2 hours): the weekly loop (`ops/COO_PLAYBOOK.md`)
1. **Numbers:** read `ops/stats/latest.json` (the server pushes it Monday 6:10am PKT). If it's missing or older than
   8 days, add a task for `claude-server`. If ads ran, read the owner's ad export in `ops/ads/<date>.csv` (§5).
2. **Report:** write `ops/reports/<YYYY-MM-DD>.md`: a 5-line plain summary first (verdict vs plan, key numbers, what
   changed, what needs the owner), then the table and decisions. The server forwards new reports to the owner on
   Telegram when it deploys.
3. **Content:** write and render next week's 8–10 social posts (`social/plan/week-<date>.json`, same schema as
   `launch30.json`, days continuing from the last queued day) and refresh ad creatives that are tiring.
4. **Revenue:** draft school and team outreach into `ops/outreach/<date>.md` (you can't send email; the owner does),
   log them in `ops/outreach.md`. Never invent contact addresses.
5. **One product improvement** the numbers point to, tested.
6. **Log:** `ops/log/<date>-codex-weekly.md`.

A scheduled Claude session also runs Mondays at 10:39am PKT as **reviewer**: it reads your report and log, and
reviews/merges your open PRs that touch `server/`, `deploy/`, `social/mizaj_social/` or payments. Open those PRs by
Monday morning and say "needs review" in the description.

### Every month
- Re-check `docs/PLAN.md` §5 against actuals; after 3+ weeks of real data, update `ops/model.py` (task T45).
- Refresh the research where it's stale (ad costs, formats).
- Write a one-page month summary for the owner in `ops/reports/`.

---

## 4. The system

### 4.1 Repo map
| Path | What |
| --- | --- |
| `content/` | Every word users read, as JSON: `types/<CODE>.json` (16 reports), `mizaj/<key>.json` (4 element guides), `compat/` (dimensions + element pairs), `careers/` (RIASEC careers, advice), `questions/` (3 banks, English + Urdu), `fun/` (zodiac, numerology), `products.json` (prices), `STYLE.md` (voice) |
| `server/mizaj/` | FastAPI app: `api.py` (routes), `scoring.py` (test scoring), `reports.py` (result/report views, entitlements, Milan), `payments.py` (orders, manual TID flow, Safepay, Lemon Squeezy, codes), `deck.py` (the card), `web.py` (Jinja env, `money()`, deck helpers), `content.py` (loads content), `db.py` (SQLite schema), `stats.py` (dashboard, digest, weekly export), `notify.py` (Telegram, email), `ai.py` (palm reading), `config.py` (all settings from env) |
| `server/tests/` | pytest suite (28 on main). Payment changes need tests here. |
| `site/templates/`, `site/static/` | Jinja templates (shared by the static build and live pages), `css/main.css`, `css/deck.css`, `js/app.js` (quiz, results, story card canvas, checkout, sharing, pixels), images (`img/el/` element emblems, `img/logo.svg`), `og/` link previews |
| `build.py` | Static build: 177 pages + sitemap, robots, `llms.txt`; FAQs, legal text, test landing configs live here |
| `tools/` | `render_social.py` (social + ads renderer), `cards.py` (card/story/fan HTML for tools), `slides.css`, `shoot.cjs` (Playwright screenshotter), `make_og.py` (link previews), `e2e.cjs` (browser test) |
| `social/` | `plan/launch30.json` (30-day calendar), `plan/ads.json` (ad creatives), `media/` and `queue/` (rendered posts the autoposter reads), `ads/` (rendered ads), `mizaj_social/poster.py` (autoposter) |
| `deploy/` | `setup.sh`, `update.sh` (auto-deploy + rollback), `backup.sh`, `export_stats.sh`, Caddy site file, systemd units/timers |
| `ops/` | `TASKS.md`, `log/`, `reports/`, `stats/`, `COO_PLAYBOOK.md`, `model.py` + `model.json` (financial model) |
| `docs/` | `PLAN.md`, `ADS.md`, `RUNBOOK.md`, `handoff/` (this file, `CLAUDE_CODE.md`, `ART_BRIEF.md`), `research/01–06`, `sales/` (school/team emails, reply templates), `review/` (T21 evidence) |

### 4.2 How a visitor flows
Static page (Caddy) → `/test/<id>/` quiz in `app.js` → `POST /api/results` (scores, creates a profile with a private
key kept in localStorage + cookie, stores utm fields) → `/p/<profile>` result page (server-rendered: deck card hero,
free sections, paywall teasers, Milan invite, share buttons) → `[data-buy]` → `POST /api/orders` → `/order/<id>`
checkout → paid (Safepay redirect/webhook, Telegram-approved manual TID, or a code) → report unlocks on the result
page (`entitlements()` reads paid orders). Milan: `POST /api/milan` creates a pair, the invite link lets the second
person take the test and `join`; both see `/milan/<pair>`.

### 4.3 Content model: legacy names to know
- Types: `name` and `name_ur` are the **Urdu** names (only for the Urdu view; never in English copy). Readers see
  `name_en`. `family` is an internal key (`Danishwar`, `Ahl-e-Dil`, `Pasban`, `Fankar`) used for colours and
  grouping; readers see `content.FAMILIES[key]["en"]` (The Thinkers, The Heart-led, The Guardians, The Makers).
- Element guides: keys `damvi` (Air), `safravi` (Fire), `balghami` (Water), `saudavi` (Earth). `global_name` is the
  element; `classical` the Greek name; `name` the Unani name (heritage line only).
- Old key names kept on purpose (templates depend on them): `free.pakistani_archetype` (a universal everyday scene),
  `premium.relationships.rishta_tips` ("when things get serious" tips), `talk_before_marriage`, `fasting`,
  `seasons.rains`, Milan relation value `rishta` (label "Partner / fiancé(e)"). Templates fall back from old keys
  (`pk_path`, `talk_before_nikah`, `ramadan`); don't remove the fallbacks until you've checked no content uses them.
- Everything a template prints must follow STYLE v3. CI's brand guard fails the build on the banned trademark words.

### 4.4 The Mizaj Deck (the visual identity)
- One builder: `server/mizaj/deck.py` → `card(code, key, bars, line)` HTML, styled by `site/static/css/deck.css`.
  Used by result/type/element page heroes, the home hero, social slides (`tools/cards.py`), link previews
  (`tools/make_og.py`). The downloadable 9:16 story card is drawn in canvas in `app.js` (`storyCard`) from
  `deck.card_data()`; **if you change the card, change both** and compare a download with a rendered slide.
- Element colours: Air `#D2544A`, Fire `#E39B2D`, Water `#2E8A8A`, Earth `#5A4A78` (same as the logo quadrants);
  paper `#F4F1EA`, ink `#17131F`. Fonts: Fraunces, Manrope, JetBrains Mono, Caveat.
- Card number: type index × 4 + element index + 1 ("No. 07/64"); "Best with" = the highest-scoring element pair;
  "opposite" = all four letters flipped.
- **Character art (your T31):** 16 small non-human ink characters on transparent backgrounds at
  `site/static/img/deck/<code>.webp`; everything picks them up automatically (`deck.art_path`). Spec:
  `docs/handoff/ART_BRIEF.md`. Do the 4-character style test first and get the owner's OK in the PR.

### 4.5 Payments
- **Manual (Pakistan, live from day 1):** Raast / bank / JazzCash / Easypaisa; buyer enters the transaction ID;
  owner gets a Telegram message with signed Approve/Reject links; duplicates refused; `/admin` lists pending.
- **Safepay (cards from any country, pending owner approval T10/T15):** hosted checkout, HMAC-verified return;
  sandbox first (T11). International cards cost about 0.3% more.
- **Regional pricing (PR #4):** client sends `region` (`pk` if the visitor's timezone is Asia/Karachi or they chose
  PKR in the footer); `intl` orders = USD price × `USD_PKR_RATE` (default 280), rounded up to 10, charged in PKR.
- **Lemon Squeezy:** code exists but is dormant (it can't pay out to Pakistan after its move to Stripe). Gumroad:
  dropped; branch `claude-cloud/T33-gumroad` kept for reference only.
- **Codes:** `/admin` creates unlock or discount codes (schools, teams, creators, gifts).
- **Refunds:** refund by hand, then reject the order in `/admin` (locks the report).
- Phase 2 subscriptions: nothing built. Don't build before T43 is approved.

### 4.6 Social pipeline
`social/plan/*.json` (posts with slides of kinds `cover, quote, text, list, type, mizaj, grid, versus, pick, cta`;
see the docstring in `tools/render_social.py`) → `python tools/render_social.py [plan] [ids]` → 1080×1440 JPEGs in
`social/media/<id>/` + 1080×1350 Instagram crops (`ig-NN.jpg`) + `social/queue/<id>.json`. The server's autoposter
(`mizaj-social` timer, every 30 min) posts due items to Instagram and Facebook once `SOCIAL_START_DATE` and the Meta
tokens are set (T08/T09); TikTok/YouTube items go to Telegram as nudges for a human to post with a trending sound.
**When you replace or remove posts, delete their old `social/media/<id>` and `social/queue/<id>.json`, or they may
still be posted.** Keep the media folder lean (JPEG quality 80; about 90 MB for 47 posts).

### 4.7 Ads pipeline
`social/plan/ads.json` (`"kind": "ads"`: each ad has `segment`, `landing`, `primary_text`, `headline`,
`description`, `button`, slides) → `python tools/render_social.py social/plan/ads.json` → `social/ads/<id>/`
(`feed-NN.jpg` 4:5, `story-NN.jpg` 9:16, `copy.txt` with a tracked URL using `utm_source={{site_source_name}}`,
`utm_medium=paid`, `utm_campaign=<segment>`, `utm_content=<id>`). The owner uploads them in Meta Ads Manager.
The site fires `Lead` (finished test), `InitiateCheckout` and `Purchase` (value, currency) to the Meta pixel and the
TikTok pixel when `META_PIXEL_ID` / `TIKTOK_PIXEL_ID` are set. Server-side purchase events (T44) aren't built yet.

### 4.8 Numbers
- `ops/stats/latest.json` (+ dated copies): 8 weeks of aggregates (visits, starts, completes, completion rate,
  orders by product, revenue PKR/USD, buyer rate, Milan invites/completions, palm reads, shares, leads, sources,
  type mix). Only aggregates ever leave the server.
- `/admin` (owner's token) shows the live dashboard; a 9:05am Telegram digest goes to the owner daily.
- Ad numbers: you can't open Meta Ads Manager. Ask the owner to export a weekly CSV (campaign, ad set, ad, country,
  spend, impressions, clicks, results) into `ops/ads/<date>.csv`; join it with the stats' utm sources.

### 4.9 Production
VPS owned by the owner (shared with his other projects `/opt/faaizjaved` and `/opt/639hz`: never touch them).
`/opt/mizaj/app` (git checkout), `/opt/mizaj/.env` (secrets), `/opt/mizaj/data/mizaj.db` (SQLite), `/opt/mizaj/www`
(static site), Caddy, systemd: `mizaj-api` (port 8200) and timers `mizaj-update` (10 min), `mizaj-digest` (9:05),
`mizaj-backup` (nightly, 21 days), `mizaj-stats` (Mon 6:10), `mizaj-social` (30 min). You don't have server access:
anything there is a task for `claude-server` (the owner opens Claude Code on the VPS; its handshake is
`docs/handoff/CLAUDE_CODE.md`).

---

## 5. What's connected

| Service | Status (29 Oct) | Controlled by | Setting / where |
| --- | --- | --- | --- |
| GitHub `faaizjaved82/mizaj` (private) | Live; CI on every push/PR | owner (you push via PRs/branches) | `.github/workflows/ci.yml` |
| VPS + Caddy + systemd | Deployed (T03); auto-deploy and weekly stats proven | owner + `claude-server` | `deploy/` |
| Domain mizaj.pk (DNS → VPS) | To confirm (T05) | owner | registrar |
| Telegram bot (alerts, approvals, digest, social nudges, weekly report) | Reuses the owner's secretary bot | owner + `claude-server` | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_OWNER_ID` |
| Manual payment details | To confirm (T04/T06) | owner | `PAY_*`, `SUPPORT_WHATSAPP` |
| Safepay (cards, any country) | Not applied yet (T10, T15) | owner → `claude-server` | `SAFEPAY_*`; `USD_PKR_RATE` after PR #4 |
| Instagram, Facebook Page, TikTok, YouTube | Not created yet (T08); bios in `launch30.json` | owner | `META_PAGE_ID`, `META_PAGE_ACCESS_TOKEN`, `META_IG_USER_ID`, `SOCIAL_START_DATE`, `SOCIALS` |
| Meta ads account + pixel | Not created yet (T41) | owner | `META_PIXEL_ID` |
| TikTok pixel | Later | owner | `TIKTOK_PIXEL_ID` |
| Anthropic API (AI palm reading) | Not set (T12) | owner | `ANTHROPIC_API_KEY`, `MIZAJ_AI_MODEL`, `AI_DAILY_CAP` |
| Resend (report emails) | Not set (T14) | owner | `RESEND_API_KEY`, `MAIL_FROM` |
| Umami analytics | Optional | owner | `PUBLIC_UMAMI_*` |
| Lemon Squeezy | Dormant | — | `LEMONSQUEEZY_*` |
| Gumroad | Dropped (PR #3 closed) | — | — |
| The owner's Claude Docs plan | Superseded by `docs/PLAN.md` for agents | owner | link in `docs/PLAN.md` |
| Klaviyo on the owner's account | Belongs to another brand (Straw & Sol). **Keep Mizaj out of it.** | owner | — |

Every key is documented in `.env.example`. Secrets live only in `/opt/mizaj/.env` on the server.

---

## 6. Status today and what's next

**Live?** `main` is deployable and the server pulls it every 10 minutes. Whether https://mizaj.pk is publicly
reachable with payments working is unconfirmed (T04–T06, T30 are waiting on the owner and `claude-server`). Ask
`claude-server` for a launch log if `ops/log/` still has none.

**Open PRs:** #4 (T40 regional pricing): review and merge first.

**Owner's open actions** (keep a short list in each weekly report): T04 payment details · T05 DNS · T08 social
accounts · T10/T15 Safepay with international cards · T12 Anthropic key · T14 Resend · T16 trademark · T39
fact-check the heritage posts · T41 Meta ad account, pixel and ad budget · T43 approve the subscription design.

**Your priorities, in order:**
1. **T40** review + merge (PR #4), then ask `claude-server` for the sandbox check.
2. **T32** review the 28–29 Oct repositioning on `main` with fresh eyes (copy, layout at 360px, story card download
   on iPhone and Android, OG images, `deck.py`).
3. **T31** Deck characters (style test of 4 → owner approval → 12 more).
4. **T34** group "Chemistry" card (2–8 people, one shareable grid) — the strongest share mechanic in research 05.
5. **T44** server-side purchase events, so ads can optimise for purchases.
6. **T42 / T45** ads reporting in the weekly report; rebuild the financial model with the ads funnel and USD orders.
7. **T22, T23, T24, T38** security review, more tests (+ e2e in CI), Lighthouse ≥ 90 on cheap phones, slide
   overflow check.
8. **T26** blog for search: topics for everyone (e.g. "The world's oldest personality test", "How each type handles
   a new job", "Your element and sleep", "What teachers should know about the 16 types", "Personality and marketing:
   the 64 audiences", "Couples: talking about plans by type").
9. **T36** rarity line on cards once 1,000+ results exist (label it "among Mizaj test-takers").
10. **T43** subscription design for owner approval (pricing, what's included, provider, cancel flow), then build.

---

## 7. Recipes

- **Change words users read:** edit `content/*.json` (keep keys and list lengths), follow STYLE v3, run tests +
  build, check the page, push (content may go straight to `main` once CI is green).
- **Change prices:** `content/products.json` (`price`, `list_price`, `usd`) — that's a payment-adjacent change: say
  so in the PR and get a review; update `docs/PLAN.md` §3 and `ads.json` copy if prices appear there.
- **Add a page:** template in `site/templates/`, a `write(...)` line in `build.py`, link it from nav/footer if needed.
- **Change the card:** `deck.py` + `deck.css` + `storyCard` in `app.js`; re-run `python tools/make_og.py` and
  re-render social/ads; commit the regenerated images.
- **Next week's posts:** copy the schema of a `launch30.json` post into `social/plan/week-<date>.json`, render that
  file only, view several JPEGs (text must not overflow), commit `social/media` + `social/queue`.
- **New ad:** add to `social/plan/ads.json`, render, check `copy.txt`; tell the owner which ad set it belongs to.
  Follow `docs/ADS.md` §3 (no personal-attribute claims, no medical claims, no trademark words).
- **Something on the server:** add a `claude-server` task with exact commands and a check; never ask for secrets in
  git or logs.
- **Before every push:** `cd server && python -m pytest -q`, `python build.py`, the brand guard grep from CI; for UI
  changes, run `tools/e2e.cjs` and look at screenshots at phone width.

---

## 8. Rules and review (summary of `AGENTS.md`)

- **You may merge your own** content, docs, images, social/ads plans and renders once CI is green.
- **You need a second reviewer** (the Monday Claude session, `claude-server`, or the owner) for anything in
  `server/`, `deploy/`, `social/mizaj_social/` and anything touching payments or prices. Open the PR, say "needs
  review" and why; don't merge it yourself.
- **You review** PRs from `claude-cloud` and `claude-server` (like PR #4).
- Hard rules: no MBTI / Myers-Briggs / 16Personalities words or type names (footer disclaimer excepted); no medical
  claims; fun tools labelled "for fun" and out of relationship decisions; compatibility never uses religion,
  ethnicity, caste or family background; no dating framing; no real living people; phase 1 = one-time prices only;
  refunds, disclaimers and privacy promises stay; never commit secrets or personal data; never touch the owner's
  other projects; never spend money, sign up for services or contact customers or partners — draft and hand over.

---

## 9. Gotchas

- `main` is production. Never push a half-finished change or a half-rendered `social/` folder.
- The story card download is canvas code that mirrors `deck.py`; they drift if you change one.
- `money()` prints both currencies; CSS shows one (`html.pk` class from timezone or the footer toggle,
  `localStorage mz_cur`). Server-side, only the region on the order decides what's charged (after PR #4).
- Removing a post from a plan doesn't remove its old queue file: delete `social/media/<id>` and
  `social/queue/<id>.json`.
- Instagram's API wants ≤ 4:5, so the renderer crops 3:4 slides to `ig-NN.jpg`; keep key content inside the central
  4:5 area.
- Slides with grain compress badly; keep JPEG quality at 80 and check `du -sh social/media` before committing.
- `ASSET_VERSION` in `server/mizaj/web.py` busts browser caches for CSS/JS: bump it when you change them.
- The CI brand guard greps `content/`, `site/templates/`, `social/plan/`. Words like "Executive" as a job title are
  fine; the trademark names as type names are not.
- `content` and the Jinja env are cached (`lru_cache`): restart the local server after editing content.
- Research files are snapshots dated 28 Oct; network-blocked sources mean figures are directional.

---

## 10. Index

| Need | Read |
| --- | --- |
| The business, decisions, prices, numbers | `docs/PLAN.md` |
| Team, workflow, hard rules | `AGENTS.md` |
| Voice and names | `content/STYLE.md` |
| Task board | `ops/TASKS.md` |
| Weekly loop | `ops/COO_PLAYBOOK.md` |
| Ads | `docs/ADS.md`, `social/plan/ads.json` |
| Production, keys, incidents | `docs/RUNBOOK.md`, `.env.example`, `docs/handoff/CLAUDE_CODE.md` |
| Art | `docs/handoff/ART_BRIEF.md` |
| Research | `docs/research/01-global-personality.md`, `02-astro-palm-numerology-tibb.md`, `03-pakistan-payments-marketing.md`, `04-pakistan-demand.md`, `05-social-trends-2026.md`, `06-international-gtm.md` |
| Sales | `docs/sales/schools.md`, `teams.md`, `replies.md` |
| History | `git log`, `ops/log/` |


---

## Appendix: notes for specific tasks

- **T22 security review:** access control on reports (profile key and cookie), the admin token and signed Telegram
  approval links, rate limiting, the `/api/palm` upload, template escaping (XSS), SQL parameterisation, payment state
  transitions, Safepay and Lemon Squeezy signature checks. Fixes come with a test each; payment fixes need review.
- **T23 tests and CI:** profile/cookie edge cases, code expiry, bundle entitlements, Milan join rules, stats and digest
  maths, the autoposter's due-time and catch-up logic (`social/mizaj_social/poster.py`); run `tools/e2e.cjs` in CI
  with Playwright; keep CI under 5 minutes.
- **T24 speed and accessibility:** Lighthouse mobile ≥ 90 (performance and accessibility) on `/`,
  `/test/personality/` and a result page; contrast, labels, focus, tap targets, font loading (the Nastaliq Urdu font
  and four Google font families are heavy: subset or load them only where needed), layout shift. Older readers are
  part of the audience: keep text large and contrast high.
- **T25 Urdu QA:** the `ur` fields in `content/questions/*.json` (natural, gender-neutral, consistent). Several items
  changed on 28–29 Oct.
- **T34 group card:** 2–8 people join a group link, each takes the test, everyone sees a colour-coded grid of pairs
  (Milan scores) and can save one 9:16 group card built from the deck style. Frame for friends, families and teams;
  never dating.
- **T36 rarity:** compute from aggregate results only, label "among Mizaj test-takers", and only once there are 1,000+
  results.
- **T38 slide overflow check:** a Playwright pass over each rendered slide that fails when text overflows its box.
- **T44 server-side events:** send Purchase (value, currency, order id as event id for deduplication with the
  browser pixel) to the Meta Conversions API and TikTok Events API when an order is marked paid, using hashed email
  only if the buyer gave one; tokens live in `/opt/mizaj/.env`.

Welcome aboard. Keep it honest, keep it kind, and let the numbers decide.
