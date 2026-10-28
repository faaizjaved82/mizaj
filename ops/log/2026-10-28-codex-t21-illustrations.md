# T21 illustrations

Connected the verified GitHub repository `faaizjaved82/mizaj` in this chat at
`/Users/faaizjaved/Desktop/Mizaj/repo`, preserving the old prototype folder and the
existing checkout at `/Users/faaizjaved/Mizaj`.

Read `AGENTS.md`, `docs/handoff/CODEX.md`, `docs/handoff/ART_BRIEF.md`, the task board,
latest handoff log, brand guide and runbook before starting T21.

Created 16 type characters, four temperament still lifes and the home hero using
ChatGPT's built-in image generation. The type set has eight men and eight women,
alternating within each family. Refined the skyline and four character designs to
meet the brief's exclusions and improve variety. Exported the exact 21 WebP paths:
800 by 800 for types/temperaments and 840 by 840 for the hero. The set totals
2,300,642 bytes; every file is below 120,000 bytes.

Validation:

- `python tools/check_art.py`: all 21 assets passed format, dimensions and size.
- `python build.py`: 177 public pages built successfully.
- Backend baseline: 28 tests passed.
- Chromium: all 21 illustrated public pages loaded their art at 360px with no
  horizontal overflow. Results are in `docs/review/T21-integration.json`.
- Phone screenshots are in `docs/review/`; the required sample social slide is
  `social/media/d02-b-each-type-at-a-shaadi/02.jpg`.
- Prompts, refinement prompts and output checksums are in
  `docs/review/T21-assets.json`.

The existing social plan is re-rendered locally. No posts, messages, customer data,
production credentials or VPS configuration are involved.

Next: @codex takes T22, followed by T23 through T26. Any backend/payment fixes need
an independent review as required by `AGENTS.md`. @claude-server remains responsible
for deployment and live payment-path verification.
