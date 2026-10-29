# Mizaj: the plan (current as of 29 October 2026)

This is the working business plan, kept in the repo so every agent can read it. The owner's original doc
("Mizaj Relaunch: COO Plan", a Claude Docs page at https://claude.ai/artifact/X1nM9nXFY2AJkYP4813wou) holds the same
history; where they differ, **this file and `content/STYLE.md` win**. Update this file when a decision changes.

## 1. What Mizaj is

A self-discovery platform for **everyone** who wants to know more about themselves, the people around them and the
world: students, professionals and managers, educators, marketers, couples, parents and families, young and old, in
any country. It is run from Pakistan by the owner, Faaiz Javed.

Two lenses, one result:
- **The 16 Mizaj types** (four-letter codes with our own names: The Strategist, The Poet, The Host, The Daredevil…),
  from a free 48-question test.
- **The four elements** (Air, Fire, Water, Earth): the classical temperaments of Hippocrates, Galen and Ibn Sina's
  *Canon of Medicine* ("mizaj" means temperament in Arabic, Persian, Turkish and Urdu), from a free 24-question test.

Together they make one of **64 collectible cards: the Mizaj Deck** (16 × 4). The card is the share object and the
brand's visual identity.

**Goal:** PKR 15–20 lakh cumulative profit by 30 June 2027.

## 2. Decisions so far (newest first)

| Date | Decision | Why |
| --- | --- | --- |
| 29 Oct | **For everyone**, not one culture ("forget the word desis"). English names only; Urdu stays a language option. | Owner direction: a universal audience. |
| 29 Oct | **No Gumroad.** Phase 1 takes cards worldwide through **Safepay** (international cards supported); Raast/JazzCash/Easypaisa for Pakistan. | Owner direction; Safepay already covers foreign cards. |
| 29 Oct | **Growth = ads + socials.** Phase 2 = **subscriptions** ("Mizaj Plus"). | Owner direction. Ads maths (`docs/ADS.md`) shows one-time reports alone don't pay for broad ads; subscriptions raise lifetime value. |
| 29 Oct | **Regional pricing:** visitors in Pakistan pay PKR prices; everyone else pays the USD price, charged through Safepay in PKR at `USD_PKR_RATE`. | Without it, foreign buyers pay ~$2 for a $9 report. PR #4. |
| 28 Oct | **The Mizaj Deck look**: collectible cards drawn in code on an element-coloured glow, plus a paper-and-ink "field notes" style for editorial posts. First AI illustration set retired. | Owner: images looked bad and badly placed. Research 05: result cards drive growth; hand-made/collectible looks are in; AI-made people read as cheap. |
| 28 Oct | Keep the domain **mizaj.pk** for now. | Owner's choice. Research 06 suggested getmizaj.com later. |
| 28 Oct | Relaunch from scratch: new site, tests, reports, payments, social engine, operations. | The old site made no money and had no footprint. |

## 3. Products and prices (phase 1: one-time, `content/products.json` is the source of truth)

| Product | Pakistan (PKR) | Everyone else (USD) | Includes |
| --- | --- | --- | --- |
| Full Mizaj Report | 599 (list 1,200) | $9 | `full` + `mizaj_full`: type report and element guide |
| Career Compass | 999 (list 2,000) | $14 | `career`: interest code, matched careers, routes |
| Mizaj Milan: Couple Report | 1,299 (list 2,500) | $15 | `couple`: report for two people |
| Full AI Palm Reading (for fun) | 299 (list 600) | $5 | `palm` |
| Complete Mizaj Bundle | 1,999 (list 6,600) | $24 | everything above |

Free forever: every test and a real result, the share card, Milan match score, zodiac × type, name number, palm
preview. **7-day refund promise.** B2B: school class pack PKR 300/student (min 50), career day PKR 500/student,
team pack PKR 1,500 or $9/person (min 10), team workshop from PKR 150,000; codes from `/admin`.

### Phase 2: Mizaj Plus (design awaiting owner approval, task T43)
- Members get every report for themselves, unlimited Milan matches (partner, family, colleagues), group cards for
  friends, families and teams, a monthly element-and-season guide, short weekly insights, and new deep dives
  (leading, parenting, studying, changing career, retiring).
- Seat plans for educators and managers (class and team maps).
- Price to test: about $5/month or $30/year (PKR 499/month in Pakistan); one-time reports stay on sale.
- Honest by design: clear price, one-tap cancel, reminder before yearly renewals.
- Needs: a recurring-payments provider for a Pakistani business (ask Safepay first) and the owner's go-ahead.

## 4. Growth engine

1. **Share loop:** every result is a card people save and post (9:16 story card, downloadable), plus WhatsApp and
   native share. Shared links show "Compare with <name>".
2. **Mizaj Milan:** a test for two people; every invite is a new test-taker.
3. **Socials:** 47-post, 30-day calendar (`social/plan/launch30.json`), rendered in the Deck look, auto-posted to
   Instagram and Facebook; TikTok/Shorts nudged to Telegram for posting by hand with a trending sound.
4. **Ads (phase 1 test):** `docs/ADS.md`: a capped 3-week test (suggested PKR 60,000) across audiences
   (everyone, students, professionals, educators, families, retargeting), optimised for finished tests (`Lead`).
   Scale only by the kill/scale rules. 9 creatives in `social/plan/ads.json` → `social/ads/`.
5. **B2B:** schools (Career Compass class packs) and teams (packs and workshops). One school deal pays for months
   of ads. Sales kit in `docs/sales/`.
6. **Search and AI assistants:** 177 static pages (16 type pages, 136 type-pair pages, 4 element pages, tools) and
   `llms.txt`.

**Formats that work now** (research 05): result cards with a status number, group compatibility, "each type as…"
grids, element vs element, pick-a-card, heritage explainers, data drops from our own aggregate stats, story
quizzes and "Add yours". Next growth feature: **group "Chemistry" card** (T34).

## 5. The numbers

### Ads maths (estimates; week 1 of ads replaces them)
Impressions per finished test ≈ 170 (1.5% CTR × 60% start × 65% finish). Cost per finished test ≈ CPM ÷ 5.85:
Pakistan ~$0.21, India ~$0.24, Philippines ~$0.60, UAE ~$1.10, UK/US ~$2.00–2.70. Revenue per finished test ≈
2–3% buyers × order value × 1.25 for sharing: ~$0.10 in Pakistan, ~$0.29 at USD prices. **One-time reports pay back
10–60% of broad ad spend on the first sale**, so phase 1 ads hunt for what does pay (retargeting, B2B leads,
sharing, cheapest markets) and phase 2 subscriptions carry ads at scale.

### Financial model (`ops/model.py`, built 28 Oct for organic growth in Pakistan)
Base case, PKR thousand:

| Month | Tests | Paid orders | Consumer revenue | B2B | Costs | Profit |
| --- | --- | --- | --- | --- | --- | --- |
| Nov | 4,000 | 48 | 46 | 0 | 112 | −67 |
| Dec | 10,000 | 140 | 133 | 0 | 139 | −6 |
| Jan | 16,000 | 288 | 274 | 75 | 205 | 143 |
| Feb | 16,000 | 288 | 274 | 307 | 228 | 353 |
| Mar | 24,000 | 480 | 456 | 407 | 341 | 522 |
| Apr | 30,000 | 630 | 599 | 489 | 402 | 685 |
| May | 36,000 | 792 | 752 | 657 | 505 | 904 |
| Jun | 40,000 | 880 | 836 | 475 | 453 | 858 |

Base case ≈ PKR 34 lakh profit by June 2027; conservative ≈ PKR 9 lakh, which is why B2B matters. **The model
predates the ads-first, international, regional-pricing direction**: rebuild it with an ads funnel and USD orders
once two weeks of real numbers exist (task T45). What must be true by 31 January: 16,000 finished tests a month,
≥1.8% buying, three schools paying.

## 6. Rules that never bend
No MBTI / Myers-Briggs / 16Personalities words or their type names (footer disclaimer excepted). No medical claims
(temperament = traditional wellness wisdom with a disclaimer). Zodiac, numbers and palm = "for fun", never in
relationship decisions. Compatibility never considers religion, ethnicity, caste or family background. No dating
framing. No real living people. Phase 1 = one-time prices; subscriptions only through T43, honestly. 7-day refunds,
disclaimers and privacy promises stay. Never commit secrets or personal data. Full list: `AGENTS.md`,
`content/STYLE.md`.

## 7. Risks and guardrails
| Risk | Guardrail |
| --- | --- |
| Traffic grows slower than plan | Weekly review vs plan; double down on formats and audiences that work; B2B carries revenue |
| Ads burn money | Capped test, kill/scale rules in `docs/ADS.md`; never scale without the numbers |
| Fake transaction IDs (manual payments) | Owner approves each one; duplicate IDs blocked; card gateway removes the issue |
| Foreign buyers undercharged | Regional pricing (PR #4) before Safepay goes live |
| Trademark complaint | Own names, questions and reports; disclaimer; file "Mizaj" trademark (T16) |
| Health complaints about element advice | Traditional-wisdom wording, "consult a doctor", no cure claims |
| Platform account restrictions | Original content; post to Instagram, Facebook, TikTok and YouTube; collect emails |
| AI cost spike (palm) | `AI_DAILY_CAP` (400/day); feature can be paused |
| Owner is the bottleneck | Card gateway, part-time assistant, partner facilitators on revenue share |
