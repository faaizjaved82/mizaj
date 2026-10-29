# Weekly operating playbook

Run every Monday by `claude-ops`, the operator (see `docs/handoff/CODEX.md`). A scheduled Claude session runs the same
morning at 10:39am Pakistan time as **reviewer** (section 7). Goal: PKR 15–20 lakh cumulative profit by
30 June 2027. About two hours, in this order.

## 0. Catch up
- Read `ops/TASKS.md`, every `ops/log/` entry since last Monday and the open pull requests. Merge what's yours to
  merge (content, docs, images, social and ad plans with green CI). Review PRs from `claude-cloud` and
  `claude-server`. Unblock tasks waiting on you.
- Add new tasks you discover for the right owner.

## 1. Read the numbers
- `ops/stats/latest.json` (the server writes it Monday 6:10am): last 8 weeks of visits, test starts and completions,
  completion rate, paid orders by product, revenue (PKR and USD), buyer rate, Milan invites and completions, palm
  reads, shares, leads, top sources (utm), type mix. If it's missing or older than 8 days, add a task for
  `claude-server` (the weekly export or the deploy key needs attention) and say so in the report.
- If ads ran: `ops/ads/<date>.csv` (the owner's export; format in `ops/ads/README.md`). Compute, by audience,
  creative and country: spend, CTR, cost per finished test, share rate, purchases, revenue per finished test, B2B
  leads. Apply the kill and scale rules in `docs/ADS.md` §4 and write the decisions down.
- Compare with `docs/PLAN.md` §5 and `ops/model.py` (monthly targets ÷ 4.3 for a week).

## 2. Write `ops/reports/<YYYY-MM-DD>.md`
- First 5 lines, plain language, for the owner (the server forwards them on Telegram when it deploys): verdict
  (ahead / on / behind plan), the two numbers that matter most, what changed, what needs the owner.
- Then: a table (metric, this week, last week, plan, status); what worked (top posts, ads, sources); what didn't;
  at most 3 changes for this week, each with an owner ("claude-ops", "codex", "owner", "claude-server", "assistant").
- Update `ops/model.py` assumptions only when 3+ weeks of actuals disagree; note the change in the report.

## 3. Ship next week's content
- Write 8–10 posts into `social/plan/week-<YYYY-MM-DD>.json` (same schema as `launch30.json`; `day` numbers continue
  from the last queued day). Double down on the formats and audiences that performed. Follow `content/STYLE.md` v3:
  for everyone (students, professionals, educators, marketers, families, young and old), no single culture as the
  default.
- Calendar: plan around moments that are global or widely shared (exam and results seasons in both hemispheres,
  back-to-school, New Year resolutions, Valentine's week as couples and friends not dating, Ramadan as one fasting
  tradition among several for element-and-fasting posts, year-end "Mizaj Wrapped" data drops). Never make a
  religious or national holiday the default setting.
- Render: `python tools/render_social.py social/plan/week-<date>.json`, look at several JPEGs, commit
  `social/media/` + `social/queue/`. If ads are running, refresh tired creatives in `social/plan/ads.json`.

## 4. Grow revenue
- **Schools:** draft 5 personalised emails a week to principals or heads of careers (`docs/sales/schools.md`) into
  `ops/outreach/<date>.md`; the owner sends them. Log each in `ops/outreach.md` (date, organisation, contact, status).
  Use only contact addresses published on the organisation's own website; otherwise leave the recipient blank.
- **Teams:** 2 drafts a week to HR / L&D heads (`docs/sales/teams.md`).
- **Creators:** list 5 creators who fit (psychology, careers, teaching, relationships, workplace humour) with handles
  and a draft DM offering a creator code; add them to `ops/outreach.md`. You never send anything yourself.

## 5. Improve the product
- One improvement a week that the numbers point to (result-page copy, a price test proposal, a new search page, a
  fix). Run `cd server && python -m pytest -q`, `python build.py` and the CI brand guard before pushing; for UI work,
  `tools/e2e.cjs` and screenshots at phone width. Server, deploy, autoposter and payment changes go in a PR for review
  (section 7). Never remove the disclaimers, refund promise or privacy guarantees.

## 6. Log
- `ops/log/<date>-claude-ops-weekly.md`: what you did, what's blocked, what you need from whom (`@owner`,
  `@claude-server`, `@claude-cloud`).

## 7. The Monday reviewer (scheduled Claude session)
- Reads the new report and log, reviews and merges (or comments on) open PRs that need a second reviewer, checks the
  brand and legal rules on the week's content, and flags anything risky to the owner in its own log entry. It does
  not write the weekly report or the posts; that's the operator's job.
