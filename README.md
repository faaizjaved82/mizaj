# Mizaj (mizaj.pk)

Pakistan's self-discovery platform: a free 16-type personality test, the Unani "Asli Mizaj" temperament test,
Mizaj Milan couple/rishta compatibility, Career Compass for students, and fun tools (AI palm reading, Burj, Ilm-e-Adad).
Free results, one-time paid reports, school and team programmes.

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
