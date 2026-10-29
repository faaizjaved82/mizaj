# Task board

Owners: `owner` (Faaiz), `claude-ops` (runs the project since 29 Oct), `codex` (images, independent code review),
`claude-server`, `claude-cloud` (reviewer), `anyone`. Status: `todo` → `doing` → `review` → `done`
(or `blocked: <on whom>`). Claim a task by setting its status in your first commit; add new tasks at the bottom of the
right section with a "done when". Details of each agent's tasks are in `docs/handoff/`.

## Go live (this week)

| ID | Task | Owner | Status | Done when |
| --- | --- | --- | --- | --- |
| T01 | Preflight the VPS (handshake step 1) | claude-server | done | Results in a log entry |
| T02 | Create deploy key; owner adds it to GitHub with write access | claude-server + owner | done | `git clone` works as the `mizaj` user |
| T03 | Run `deploy/setup.sh`; services and timers running | claude-server | done | Health check ok, 5 timers listed |
| T04 | Fill payment details and WhatsApp in `/opt/mizaj/.env` | owner + claude-server | to confirm | Checkout shows Raast/wallet details |
| T05 | DNS A records for mizaj.pk and www → VPS | owner | to confirm | https://mizaj.pk loads with HTTPS |
| T06 | Prove the money path (handshake step 5) | claude-server | to confirm | Fake TID rejected via Telegram; code unlock works |
| T07 | Weekly stats round trip (handshake step 6) | claude-server | done | `ops/stats/latest.json` on GitHub |
| T08 | Create Instagram, Facebook Page, TikTok, YouTube with prepared bios and logo | owner | todo | Four profiles exist |
| T09 | Meta token + IG id in `.env`; set `SOCIAL_START_DATE` | claude-server | blocked: T08 | First post goes out by itself |

## Switch on growth

| ID | Task | Owner | Status | Done when |
| --- | --- | --- | --- | --- |
| T10 | Apply for Safepay merchant account (CNIC, NTN, bank) | owner | todo | Sandbox keys received |
| T11 | Test and fix Safepay checkout in sandbox, then production | claude-server | blocked: T10 | A real card payment unlocks a report |
| T12 | Anthropic API key in `.env`; test palm reading | owner + claude-server | todo | A palm reading works on the live site |
| T13 | Hire a part-time assistant (runbook §6) | owner | todo | Assistant posting TikToks daily |
| T14 | Resend account + DNS records; `RESEND_API_KEY` | owner + claude-server | todo | Report-link emails arrive |
| T15 | Ask Safepay to enable international cards on the merchant account (with T10) | owner | todo | A foreign card test payment succeeds |
| T16 | File the "Mizaj" trademark (classes 41 and 44) | owner | todo | Application number |

## Make it better

| ID | Task | Owner | Status | Done when |
| --- | --- | --- | --- | --- |
| T21 | 16 type + 4 mizaj illustrations + home hero (first art set) | codex | retired | Replaced by T31 after the desis-everywhere repositioning |
| T22 | Independent security and correctness review of `server/mizaj/` | codex | todo | Fix PR with tests, or findings log |
| T23 | More tests; e2e in CI | claude-ops | todo | CI runs them in under 5 minutes |
| T24 | Accessibility and speed on cheap Android phones | claude-ops | todo | Lighthouse mobile ≥ 90 perf + a11y |
| T25 | Urdu QA of the question banks | claude-ops | todo | PR with Urdu fixes |
| T26 | `/blog/` + 6 posts for search traffic | claude-ops | todo | 6 posts live |
| T27 | Weekly report and loop (`ops/COO_PLAYBOOK.md`), every Monday | claude-ops | todo | A report in `ops/reports/` every Monday |
| T28 | Review Codex PRs that need a second reviewer, every Monday (scheduled session) | claude-cloud | doing | No such PR waits more than a week |
| T29 | First 10 school outreach drafts and a pilot | claude-ops + owner | todo | 3 school pilots running by end of December |
| T30 | Write the server launch log entry; confirm T04–T06 and tick them | claude-server | todo | `ops/log/<date>-claude-server-launch.md` on `main` |
| T31 | Mizaj Deck character art, art brief v2 (`docs/handoff/ART_BRIEF.md`): style test of 4 first (T31a), then the other 12 (T31b) | codex | todo | 16 transparent WebP files in `site/static/img/deck/`, style approved in the PR |
| T32 | Review the repositioning on `main` (28–29 Oct: deck cards, everyone positioning) (new `server/mizaj/deck.py`, `web.py`, `reports.py`, `content.py`, OG paths in `api.py`, checkout layout) | claude-ops | review: PR #6 (PR #5 merged; notes in ops/log/2026-10-30-claude-ops-t32-review.md) | Review notes in `ops/log/`, fixes in a PR if needed |
| T33 | Gumroad checkout | claude-cloud | dropped | Owner decided against Gumroad (29 Oct); PR #3 closed, branch kept |
| T34 | Group "Chemistry" mode: add 2–8 friends or family and get one shareable grid card (research 05, format 2) | claude-ops | todo | `/group/` live with a 9:16 group card |
| T35 | Paddle as card processor | owner | dropped | Not needed in phase 1 (Safepay takes international cards) |
| T36 | Rarity line on the deck card ("1 in N Mizaj test-takers") from aggregate stats, once 1,000+ results exist | claude-ops | todo | Card shows a labelled rarity from `ops/stats/` |
| T37 | Re-render and requeue the 30-day plan for desis everywhere (new slide look, 3:4) | claude-cloud | done | New `social/plan/launch30.json`, `social/media/`, `social/queue/` on `main` |
| T38 | Add a slide overflow check to `tools/` (measure every rendered slide in the browser; fail on overflow) and run it in CI | claude-ops | todo | `python tools/render_social.py` fails loudly when text overflows |
| T39 | Fact-check the heritage posts before they go out: d04-a, d08-a, d11-a, d15-c, d19-a, d24-a, d27-a (the Canon's nine temperaments, the 1100s Latin translation, warming/cooling foods) | owner | todo | Owner OK, or corrections sent to codex |
| T40 | Regional pricing: international orders are charged the USD price (converted to PKR for Safepay), Pakistan keeps PKR prices; payment logic, tests + operator review | claude-ops (reviewer) | done (PR #4 merged 29 Oct) | Branch `claude-cloud/T40-regional-pricing` reviewed and merged; then `claude-server` makes one sandbox card payment from outside Pakistan |
| T41 | Ads phase 1: Meta Business + ad account, pixel id to claude-server, budget approved (`docs/ADS.md`) | owner | todo | First ad set live with the pixel firing Lead and Purchase |
| T42 | Ads reporting: weekly cost per finished test, share rate and revenue per finished test by audience and country in the Monday report | claude-ops | todo | Numbers in `ops/reports/` every Monday once ads run |
| T43 | Phase 2 subscriptions: design ("Mizaj Plus" outline in the plan doc), then build with Safepay recurring or a provider the owner picks | claude-ops + owner | todo | Owner approves the design; build task created |
| T44 | Server-side purchase events (Meta Conversions API / TikTok Events API) so manual and late payments count for ad optimisation | claude-ops | todo | Purchases reach Meta even when the buyer has closed the page |
| T45 | Rebuild the financial model (`ops/model.py`) for the ads funnel, regional (USD) orders and phase 2 subscriptions, after 2+ weeks of real numbers | claude-ops | todo | `docs/PLAN.md` §5 updated with the new base case |
| T46 | Handoff: Codex runs the project (`docs/handoff/CODEX.md`, `docs/PLAN.md`, playbook, roles) | claude-cloud | done | Codex's first log entry on `main` |
| T47 | Safepay sandbox card payment from a non-Pakistan time zone after T40; optionally set `USD_PKR_RATE` | claude-server | blocked: T10 | Full report charged about PKR 2,520 and unlocks; result in a log entry |
| T48 | Harden the region: a buyer abroad can pick PKR in the footer and pay PKR prices by card. Check the card's issuing country (Safepay) or a geo-IP header before charging the PKR price | claude-ops | todo | An `intl` buyer can't get the PKR price by switching currency; tests cover it |
| T49 | Content pass for STYLE v3: archetype quotes and family sections that default to cousins, weddings, arranged meetings and "what will people say"; `rishta_tips` wording; `content/types/SCHEMA.md` guidance; add a Parent option to Milan | claude-ops | todo | Every type's quote and family section works for a reader anywhere; T32 log items closed |
