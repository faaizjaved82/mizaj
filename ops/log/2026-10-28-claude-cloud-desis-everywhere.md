# 2026-10-28 · claude-cloud · Desis everywhere + the Mizaj Deck

**Why:** the owner said the illustrations looked bad and badly placed, the brand was "too Pakistani", and asked
for better images and cards based on what works on social now. Audience decided with the owner: desis
everywhere (UK, US, Canada, Gulf, Pakistan). Domain stays mizaj.pk for now.

## Done (on `main`)
- **Research:** `docs/research/05-social-trends-2026.md` (result cards drive growth; collectible and hand-made
  looks are rising; AI-made people read as cheap; carousels for engagement, video for reach; Instagram grid is
  3:4) and `06-international-gtm.md` (Gumroad pays out to Pakistan; Lemon Squeezy is moving to Stripe, which
  doesn't; Paddle later; prices and markets).
- **Content:** STYLE.md v2; all 16 type reports, 4 element guides, compatibility, careers, questions (Urdu kept in
  step), zodiac/numerology and product bullets re-voiced for desis everywhere. Key renames: `pk_path` → `path`,
  `talk_before_nikah` → `talk_before_marriage`, mizaj `ramadan` → `fasting`, `global_name` added; code falls
  back to the old keys.
- **Site:** English names first, elements (Air/Fire/Water/Earth), USD by default with PKR for visitors in
  Pakistan (`money()`, `html.pk`, footer toggle), international-first checkout, de-localised titles, FAQs,
  terms and llms.txt.
- **The Mizaj Deck:** `server/mizaj/deck.py` + `site/static/css/deck.css` + element emblems in
  `site/static/img/el/`. One card builder used by result/type/element heroes, the home hero, the downloadable
  9:16 story card (canvas in `app.js`), social slides and link previews (now JPEG, 1.5 MB total).
- **Social:** new renderer (`tools/render_social.py`, `tools/cards.py`, `tools/slides.css`) with 10 slide kinds,
  3:4 renders + 4:5 crops for the Instagram API; new 30-day plan (47 posts) rendered and queued. Pinned:
  d01-a, d01-b, d01-c.
- **Art:** first illustration set retired; `docs/handoff/ART_BRIEF.md` v2 for 16 non-human ink characters (T31).
- **Plan doc:** "Update, 28 October" section added.

## In review
- **T33 Gumroad** on `claude-cloud/T33-gumroad`, PR #3 (42 tests). Payment logic: @codex please review before
  merge. After merge @claude-server sets the four `GUMROAD_*` keys (see the PR and `docs/RUNBOOK.md`).

## Needs
- @owner: T15 Gumroad account + 5 products (`docs/OWNER_GUMROAD.md`); T39 fact-check the heritage posts; T08
  social accounts if not done (bios are in `social/plan/launch30.json`).
- @codex: T31 deck characters (style test of 4 first), T32 review of this repositioning (pushed straight to
  `main` at the owner's request), T38 slide overflow check, PR #3 review.
- @claude-server: confirm the deploy picked up `765ba35`+ (new heroes on `/types/intj/`), then T30.

## Notes
- Every surface reads names and colours from `deck.py`; change the card there, not in templates.
- Rarity on cards (T36) waits for real aggregate data; never print population "rarity" as fact.
