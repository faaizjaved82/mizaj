# Mizaj: rules for every agent working in this repo

Mizaj (mizaj.pk) is a self-discovery business for everyone (students, professionals, educators, marketers, families,
young and old), run from Pakistan: free personality and temperament (element) tests, one-time paid reports, Mizaj Milan couple reports, Career Compass for students, and school/team programmes. Goal: PKR 15–20 lakh
cumulative profit by 30 June 2027. The owner is Faaiz Javed. Read `README.md` for the layout and `docs/RUNBOOK.md` for
how production works. The plan and every decision so far: `docs/PLAN.md`.

## The team

| Name in tasks/logs | Who | Best at | Works through |
| --- | --- | --- | --- |
| `owner` | Faaiz | Decisions, money, accounts that need his identity (GitHub, Meta, Safepay, domain, bank) | Telegram, GitHub, chat |
| `claude-ops` | Claude Code on the owner's Mac (desktop app) | **Runs Mizaj day to day since 29 Oct 2026** (took over from `codex` the same day): the task board, product, content, code, social and ads machinery, the weekly report | This repo (branches, PRs, merges within the review rule) |
| `codex` | ChatGPT Codex (and ChatGPT for images) | Images and visual assets, an independent second opinion on code | PRs from its own branches |
| `claude-server` | Claude Code running on the VPS | Deploying, server config and `.env`, logs, live checks, aggregate DB queries, payment-gateway tests | SSH session on the VPS; pushes with the server's deploy key |
| `claude-cloud` | Claude in claude.ai cloud sessions, incl. the scheduled Monday reviewer | Second reviewer for server and payment PRs, strategy when the owner asks | This repo (reviews, PRs) |

Start a session by reading: this file, `ops/TASKS.md` (the task board), the newest files in `ops/log/`, `docs/PLAN.md`, and your own
handoff in `docs/handoff/` (`CODEX.md` for the operator, `claude-ops`; `CLAUDE_CODE.md` for the server).

## How we work together

1. **Pick work from `ops/TASKS.md`.** Take a task whose owner is you (or `anyone`), set it to `doing` in your first
   commit. Add new tasks you discover at the bottom with an owner and a one-line "done when".
2. **Branch per task:** `<agent>/<task-id>-<slug>`, e.g. `codex/T21-type-illustrations`. Small doc or content fixes
   by `claude-ops` (the operator) or `claude-cloud` may go straight to `main`.
3. **Pull request into `main`.** CI (`.github/workflows/ci.yml`) must pass: backend tests and a full site build.
   Say in the PR what changed, how you checked it, and any follow-up for someone else.
4. **Review rule:** content, docs, images and social/ad plans may be merged by their author once CI is green.
   Anything in `server/`, `deploy/` or `social/mizaj_social/`, and anything that touches payments or prices, needs a
   review from another agent or the owner: the scheduled Monday Claude session (or `claude-server`, or
   `codex`) reviews the operator's PRs; `claude-ops` reviews PRs from `claude-cloud`, `claude-server` and `codex`.
5. **Leave a log entry at the end of every session:** a new file `ops/log/<YYYY-MM-DD>-<agent>-<slug>.md` with what
   you did, what's blocked, and what you need from whom (name them: `@owner`, `@claude-ops`, `@claude-server`, `@codex`,
   `@claude-cloud`). One file per entry, so nobody's edits collide.
6. **Ask, don't guess:** if you need something another agent is better placed to do (images → codex; server
   access → claude-server; accounts or money → owner), add a task for them and say so in your log entry.
7. **Merging to `main` deploys to production within 10 minutes** (the server pulls, rebuilds, health-checks and
   rolls back on failure). Treat `main` as live.

## Hard rules (the brand and the law)

- Never commit secrets (`.env`, keys, tokens) or personal data (the database, names, phone numbers, emails, palm
  photos, order details). Stats leave the server only as aggregates (`ops/stats/`).
- Never use the words MBTI, Myers-Briggs or 16Personalities, or their type names (Architect, Logician, Commander,
  Advocate, Mediator, Campaigner, and so on), anywhere in the product or content. The one exception is the
  legal non-affiliation disclaimer in the site footer. Our type names are in
  `content/STYLE.md`.
- Follow `content/STYLE.md` for every word users see: written for everyone (no single culture as the default), no medical claims (Unani guidance is
  traditional wellness wisdom with a disclaimer), astrology/numerology/palm reading labelled "for fun" and kept out
  of relationship decisions, never consider caste, sect, religion or ethnicity in compatibility, no dating framing, no real living people as examples.
- Phase 1 (now): one-time prices from `content/products.json` only, no subscriptions or auto-renewal yet. Phase 2
  (owner's decision, 29 Oct 2026) adds subscriptions; build them only from a task on the board, with a clear price,
  easy cancel and no hidden renewals. The 7-day refund promise, the disclaimers and the privacy guarantees stay.
- Payment logic changes need tests (`server/tests/`) and a second reviewer.
- Don't touch other projects on the VPS (`/opt/faaizjaved`, `/opt/639hz`) or their services.
- Don't spend money, sign up for services or contact customers/partners on the owner's behalf; draft and hand over.

## Commands

```bash
python3 -m venv .venv && . .venv/bin/activate && pip install -e server -e social pytest
cd server && python -m pytest -q          # backend tests (must pass)
python build.py                           # static site into dist/ (must succeed)
uvicorn mizaj.api:app --port 8300         # run locally (from server/), serves dist/ too
node tools/e2e.cjs http://127.0.0.1:8300 /tmp/shots <ADMIN_TOKEN>   # phone-sized browser test (needs Playwright)
python tools/render_social.py [plan.json]  # render social slides + queue
python tools/make_og.py                   # link-preview images
python ops/model.py                       # financial model
```

## Where things go

| Thing | Path |
| --- | --- |
| Words users read (tests, reports, prices) | `content/` (JSON) |
| Page templates, CSS, JS | `site/templates/`, `site/static/` |
| Cards (the Mizaj Deck: one builder for site, slides and previews) | `server/mizaj/deck.py`, `site/static/css/deck.css`, emblems in `site/static/img/el/` |
| Character art (optional; cards pick it up automatically) | `site/static/img/deck/<code>.webp`; spec in `docs/handoff/ART_BRIEF.md` |
| Social calendar and slides | `social/plan/*.json` → `social/media/`, `social/queue/` |
| Weekly numbers, reports, task board, log | `ops/stats/`, `ops/reports/`, `ops/TASKS.md`, `ops/log/` |
