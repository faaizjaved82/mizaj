@AGENTS.md

## Notes for Claude Code

- On the VPS you are `claude-server`: your handshake is `docs/handoff/CLAUDE_CODE.md`. Work through it in order and
  report in `ops/log/`.
- In a claude.ai cloud session you are `claude-cloud`. Since 29 Oct 2026 `codex` runs the project day to day
  (`docs/handoff/CODEX.md`). Your Monday job is the reviewer role in `ops/COO_PLAYBOOK.md` §7: review and merge Codex
  PRs that need a second reviewer, check the week's content against the rules, and log what you found.
- Production lives at `/opt/mizaj` (app in `/opt/mizaj/app`, settings in `/opt/mizaj/.env`, data in
  `/opt/mizaj/data`). Read `/opt/mizaj/.env` only to check which keys are set; never print or commit values.
