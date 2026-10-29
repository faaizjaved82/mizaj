# 2026-10-29 · claude-cloud · Handoff: Codex runs the project

**Owner's direction:** pack everything up so Codex can keep running the entire project.

## Done
- `docs/handoff/CODEX.md` rewritten as the operator handoff: first session, the business on one page, the story so
  far, the daily/weekly/monthly loop, the system (repo map, visitor flow, content model and legacy keys, the Mizaj
  Deck, payments, social and ads pipelines, numbers, production), what's connected (every service, its status, who
  controls it, its setting), status and priorities, recipes, review rules, gotchas, an index, task notes.
- `docs/PLAN.md`: the current plan in the repo (decisions log, products and prices, phase 2 subscription outline,
  growth engine, ads maths, financial model, rules, risks). It supersedes the Claude Docs plan for agents.
- Roles: `AGENTS.md` (codex runs the project; claude-cloud is the Monday second reviewer; review rule), `CLAUDE.md`,
  `README.md` (start here), `ops/COO_PLAYBOOK.md` rewritten for the operator and for everyone, `docs/RUNBOOK.md`
  (payments and weekly loop), `docs/handoff/ART_BRIEF.md` (audience), `ops/ads/README.md` (ad export format).
- Task board: open claude-cloud tasks moved to codex (T27, T29, T34, T36, T42, T43, T44); T40 review is codex's; new
  T45 (rebuild the model) and T46 (this handoff).
- The scheduled Monday session is now "Mizaj Monday reviewer" (reviews and merges server/payment PRs, checks content
  against the rules, logs findings); it no longer writes reports or posts.

## Needs
- @codex: start with `docs/handoff/CODEX.md` §0, then review and merge PR #4.
- @owner: the open actions listed in `docs/handoff/CODEX.md` §6.
