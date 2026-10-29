# 2026-10-29 · claude-cloud · Mizaj for everyone, ads first, subscriptions next

**Owner's direction:** drop "desis": Mizaj is for everyone who wants to know more about themselves, others and the
world (students, professionals, educators, marketers, families, young and old). No Gumroad. Grow through ads and
socials; phase 2 moves to subscriptions.

## Done
- **Rules:** `content/STYLE.md` v3 (for everyone, English names only, elements first, phase-2 subscription wording
  rule); `AGENTS.md` audience and the phase 1 / phase 2 pricing rule.
- **Content:** all 16 type reports, the 4 element guides, compatibility, careers (now also for career changers),
  question banks (Urdu kept in step), zodiac, numerology and product text made universal. Letters now open
  "Dear Strategist" etc.
- **Site:** universal hero, "Who it's for" section (students, professionals, educators, marketers, couples and
  families, every age), no Urdu names or script on English pages, zodiac and name-number pages renamed, cards show
  keywords instead of the Urdu name, about page, FAQs, titles and llms.txt rewritten.
- **Payments:** Gumroad dropped (PR #3 closed, branch kept). Checkout leads with "Debit or credit card, from any
  country" (Safepay takes international cards); Raast/JazzCash/Easypaisa first only for visitors in Pakistan.
- **Ads:** `docs/ADS.md` (funnel maths, 3-week capped test, ad sets by audience, policy rules, kill/scale rules,
  owner setup); 9 creatives in `social/plan/ads.json` rendered to `social/ads/` (4:5 + 9:16 + copy and tracked
  links). The site sends Lead / InitiateCheckout / Purchase to the Meta and TikTok pixels.
- **Plan doc:** "Update, 29 October" with the Mizaj Plus (phase 2 subscription) outline.

## In review
- **T40 regional pricing** (international orders charged the USD price through Safepay; Pakistan keeps PKR):
  branch `claude-cloud/T40-regional-pricing`, PR #4 (38 tests, CI green) for @codex to review (payment logic).
  After merge @claude-server may set `USD_PKR_RATE` and makes one Safepay sandbox payment from outside Pakistan.

## Needs
- @owner: T41 Meta ad account + pixel id + budget decision (`docs/ADS.md` §2, §5); T15 ask Safepay to enable
  international cards (and ask whether they support recurring payments, for phase 2); T39 fact-check heritage posts.
- @claude-server: put the pixel id in `META_PIXEL_ID` when the owner sends it; verify mizaj.pk in Meta (DNS TXT).
- @codex: review the T40 PR; T31 characters (brief v2 still applies); T32 review.

## Notes
- The ads maths says a one-time $9 report won't pay for broad ads on its own; phase 1 ads are a measured test
  (retargeting, B2B leads, sharing), and subscriptions are what make ads pay at scale. Don't scale spend before
  the §4 rules say so.
