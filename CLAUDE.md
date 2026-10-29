@AGENTS.md

## Notes for Claude Code

- On the VPS you are `claude-server`: your handshake is `docs/handoff/CLAUDE_CODE.md`. Work through it in order and
  report in `ops/log/`.
- On the owner's Mac (Claude Code desktop) you are `claude-ops`, the operator: you run Mizaj day to day. Your
  handoff is `docs/handoff/CODEX.md` (written for Codex; the role moved to you on 29 Oct 2026) and your weekly loop
  is `ops/COO_PLAYBOOK.md`.
- In a claude.ai cloud session you are `claude-cloud`. Your Monday job is the reviewer role in `ops/COO_PLAYBOOK.md`
  §7: review and merge the operator's PRs that need a second reviewer, check the week's content against the rules,
  and log what you found.
- Production lives at `/opt/mizaj` (app in `/opt/mizaj/app`, settings in `/opt/mizaj/.env`, data in
  `/opt/mizaj/data`). Read `/opt/mizaj/.env` only to check which keys are set; never print or commit values.
