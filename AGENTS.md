# Mizaj: rules for every agent working in this repo

Mizaj (mizaj.pk) is a Pakistani self-discovery business: free personality and Unani temperament tests, one-time paid
reports, Mizaj Milan couple reports, Career Compass for students, and school/team programmes. Goal: PKR 15–20 lakh
cumulative profit by 30 June 2027. The owner is Faaiz Javed. Read `README.md` for the layout and `docs/RUNBOOK.md` for
how production works. The full plan is the owner's doc "Mizaj Relaunch: COO Plan".

## The team

| Name in tasks/logs | Who | Best at | Works through |
| --- | --- | --- | --- |
| `owner` | Faaiz | Decisions, money, accounts that need his identity (GitHub, Meta, Safepay, domain, bank) | Telegram, GitHub, chat |
| `claude-cloud` | Claude (acting COO) in claude.ai cloud sessions, incl. the scheduled Monday review | Strategy, the plan, content, product changes, weekly report, reviewing PRs | This repo (push to `main` or PRs) |
| `claude-server` | Claude Code running on the VPS | Deploying, server config and `.env`, logs, live checks, aggregate DB queries, payment-gateway tests | SSH session on the VPS; pushes with the server's deploy key |
| `codex` | ChatGPT Codex (and ChatGPT for images) | Images and visual assets, a second opinion on code, tests, frontend polish, accessibility, performance | PRs from its own branches |

Start a session by reading: this file, `ops/TASKS.md` (the task board), the newest files in `ops/log/`, and your own
handoff in `docs/handoff/` (`CLAUDE_CODE.md` for the server, `CODEX.md` for Codex).

## How we work together

1. **Pick work from `ops/TASKS.md`.** Take a task whose owner is you (or `anyone`), set it to `doing` in your first
   commit. Add new tasks you discover at the bottom with an owner and a one-line "done when".
2. **Branch per task:** `<agent>/<task-id>-<slug>`, e.g. `codex/T21-type-illustrations`. Small doc or content fixes
   by `claude-cloud` may go straight to `main`.
3. **Pull request into `main`.** CI (`.github/workflows/ci.yml`) must pass: backend tests and a full site build.
   Say in the PR what changed, how you checked it, and any follow-up for someone else.
4. **Review rule:** content, docs and images may be merged by their author once CI is green. Anything in `server/`,
   `deploy/` or `social/mizaj_social/`, and anything that touches payments, needs a review from another agent
   (`claude-cloud` reviews Codex PRs in the Monday session; ask `codex` to review Claude PRs in the PR) or the owner.
5. **Leave a log entry at the end of every session:** a new file `ops/log/<YYYY-MM-DD>-<agent>-<slug>.md` with what
   you did, what's blocked, and what you need from whom (name them: `@owner`, `@claude-server`, `@codex`,
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
- Follow `content/STYLE.md` for every word users see: Pakistani context, no medical claims (Unani guidance is
  traditional wellness wisdom with a disclaimer), astrology/numerology/palm reading labelled "for fun" and kept out
  of rishta, never consider caste or sect, no dating framing, no real living people as examples.
- No subscriptions, trials or auto-renewal; one-time prices from `content/products.json`; the 7-day refund promise,
  the disclaimers and the privacy guarantees stay.
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
| Illustrations (optional; pages and slides pick them up automatically) | `site/static/img/types/<code>.webp`, `site/static/img/mizaj/<key>.webp`, `site/static/img/hero.webp`; spec in `docs/handoff/ART_BRIEF.md` |
| Social calendar and slides | `social/plan/*.json` → `social/media/`, `social/queue/` |
| Weekly numbers, reports, task board, log | `ops/stats/`, `ops/reports/`, `ops/TASKS.md`, `ops/log/` |
