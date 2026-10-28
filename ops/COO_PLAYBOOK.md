# Weekly COO playbook

Run every Monday by the scheduled Claude session (or by anyone, by hand). Goal: PKR 15–20 lakh cumulative profit by
30 June 2027 (base plan: about 34 lakh). One session, about an hour of work, in this order.

## 0. Catch up with the team
- Read `ops/TASKS.md` and every `ops/log/` entry since last Monday. Review open pull requests from `codex`
  (and `claude-server`): merge what's good and green, comment on the rest. Unblock tasks waiting on you.
- Add new tasks you discover for the right owner; end the session with your own `ops/log/` entry.

## 1. Read the numbers
- `ops/stats/latest.json` (written by the server every Monday 6:10am): last 8 weeks of tests, completion rate, paid
  orders by product, revenue, buyer rate, Milan invites/completions, palm reads, shares, contacts, leads, top sources,
  type mix. If it's missing or older than 8 days, say so in the report: the server or its deploy key needs attention.
- Compare with the base plan in `ops/model.py` (monthly targets; divide by 4.3 for a week).

## 2. Write `ops/reports/<YYYY-MM-DD>.md`
- One-line verdict (ahead / on / behind plan) with the two numbers that matter most this week.
- Table: metric, this week, last week, plan, status.
- What worked (top 3 posts or sources), what didn't, what we change this week (max 3 changes, each with an owner:
  "auto" for things this session does, "owner" or "assistant" for people).
- Update `ops/model.py` assumptions only when 3+ weeks of actuals disagree with them; note the change.

## 3. Ship next week's content
- Write 8–10 new posts into `social/plan/week-<YYYY-MM-DD>.json` (same schema as `launch30.json`, `day` numbers
  continuing from the last queued day). Double down on the pillars and formats that performed; keep the brand rules in
  `content/STYLE.md`. Watch the calendar: Ramadan about 8 Feb–9 Mar 2027 (no playful fun-zone posts, more mizaj
  sehri/iftar content), Eid about 9–10 Mar, exam and result seasons, wedding season Nov–Feb.
- Render: `python tools/render_social.py social/plan/week-<date>.json`, commit media + queue.

## 4. Grow revenue
- Schools: draft 5 personalised outreach emails per week in the owner's Gmail (DRAFTS only, never send) to
  principals or heads of careers at private schools and colleges, using `docs/sales/schools.md`. Prioritise cities and
  chains not contacted before; keep a log in `ops/outreach.md` (date, school, contact, status).
- Teams: 2 drafts per week to HR/L&D heads, using `docs/sales/teams.md`.
- Creators: list 5 Pakistani creators (psychology, relationships, desi family humour, student life) with handles and
  a draft DM offering a creator code; add to `ops/outreach.md`.

## 5. Improve the product (small, safe changes only)
- One improvement a week that the numbers point to (copy on the result page, price test, a new SEO page, a fix).
  Run `cd server && python -m pytest -q` and `python build.py` before committing. Never change payment logic
  without tests passing. Never remove the disclaimers, refund promise or privacy guarantees.

## 6. Report to the owner
- Email the owner (to themselves, from their Gmail) a one-screen summary: verdict, 5 numbers, 3 changes made,
  anything that needs them (approvals waiting, keys missing, leads to call). Plain language, no jargon.
- Commit everything with a clear message and push to `main` (the server deploys within 10 minutes).
