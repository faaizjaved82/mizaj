@AGENTS.md

## Notes for Claude Code

- On the VPS you are `claude-server`: your handshake is `docs/handoff/CLAUDE_CODE.md`. Work through it in order and
  report in `ops/log/`.
- In a claude.ai cloud session you are `claude-cloud`: the weekly routine is `ops/COO_PLAYBOOK.md`; you also review
  open Codex pull requests before writing the Monday report.
- Production lives at `/opt/mizaj` (app in `/opt/mizaj/app`, settings in `/opt/mizaj/.env`, data in
  `/opt/mizaj/data`). Read `/opt/mizaj/.env` only to check which keys are set; never print or commit values.
