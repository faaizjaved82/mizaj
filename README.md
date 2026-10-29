# Mizaj (mizaj.pk)

A self-discovery platform for everyone who wants to understand themselves and others: a free 16-type personality
test, the classical four-temperament test (Air, Fire, Water, Earth), Mizaj Milan compatibility, Career Compass for students and career changers, and fun tools (AI palm reading, zodiac × type, name numbers).
Free results, one-time paid reports, school and team programmes.

**Start here:** `docs/PLAN.md` (the business), `AGENTS.md` (team and rules), `docs/handoff/CODEX.md` (how the
project is run day to day).

| Folder | What's in it |
| --- | --- |
| `content/` | All editorial content: question banks, 16 type reports, 4 mizaj guides, compatibility, careers, zodiac, numerology, prices (`products.json`). Edit these to change what the site says. |
| `site/` | Templates, CSS, JS, images. `build.py` turns them into the static site in `dist/`. |
| `server/` | The web app (FastAPI): results, reports, payments, Milan, palm reading, admin, stats. Tests in `server/tests/`. |
| `social/` | Content plan, rendered slides (`media/`), posting queue (`queue/`) and the autoposter (`mizaj_social`). |
| `deploy/` | Server setup, Caddy site, systemd services and timers, auto-deploy, backups. |
| `ops/` | Financial model, weekly stats exported by the server, weekly COO reports, the COO playbook. |
| `docs/` | Runbook, research notes, sales kit. |
| `tools/` | Slide and link-preview renderers, browser end-to-end test. |

Start with `docs/RUNBOOK.md`. Agents (Claude Code, Codex) start with `AGENTS.md`, the task board `ops/TASKS.md`
and their handoff in `docs/handoff/`.

## Develop locally

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -e server -e social pytest
python build.py                       # builds dist/
cd server && python -m pytest -q      # 28 tests
uvicorn mizaj.api:app --port 8300     # serves API + dist/ at http://127.0.0.1:8300
node tools/e2e.cjs http://127.0.0.1:8300 /tmp/shots <ADMIN_TOKEN>   # browser test (needs Playwright)
python tools/render_social.py         # render social/plan/launch30.json into slides + queue
python tools/make_og.py               # regenerate link-preview images
python ops/model.py                   # financial model
```
