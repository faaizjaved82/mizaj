# Ads playbook, phase 1

Owner decision (29 Oct 2026): Mizaj grows through ads and socials; subscriptions come in phase 2. This is how to
spend the first ad money so it buys learning, not just traffic. Creatives: `social/plan/ads.json`, rendered into
`social/ads/<id>/` (`feed-NN.jpg` 4:5 for feeds, `story-NN.jpg` 9:16 for Stories and Reels, `copy.txt` with the
text, headline, button and the tracked link). All figures below are estimates from public benchmarks
(`docs/research/03-…` §5 and `06-…` §3.1); week 1 replaces them with real numbers.

## 1. The honest maths first

The funnel from an ad to money:

| Step | Assumption (estimate) |
| --- | --- |
| Ad seen → click | 1.5% |
| Click → starts a test | 60% |
| Starts → finishes | 65% |
| **Impressions per finished test** | **about 170** (cost per finished test ≈ CPM ÷ 5.85) |
| Finished test → buys a report | 2–3% |
| Extra free users from shares and Milan invites | +25% |

| Market | CPM (Meta) | Cost per finished test | Revenue per finished test | Pays back on the first purchase? |
| --- | --- | --- | --- | --- |
| Pakistan | about $1.2 | about $0.21 | about $0.10 (3% × PKR 750 average) | No (about 45%) |
| India | about $1.4 | about $0.24 | about $0.15 (1% × $12) | No (about 60%) |
| Philippines | about $3.5 | about $0.60 | about $0.29 (2% × $12) | No (about 50%) |
| UAE | about $6.5 | about $1.10 | about $0.29 | No (about 25%) |
| UK / US | $12–16 | $2.00–2.70 | about $0.29–0.44 | No (10–20%) |

**What this means:** a $9 one-time report does not pay for broad ads on its own in any market. Ads make money only
when one or more of these is true, which is what phase 1 must test:
1. **Retargeting converts.** People who finished a test and see a "your full report" ad a day later buy at several
   times the cold rate. Retargeting audiences are small and cheap.
2. **B2B leads.** One school or company deal (PKR 15,000–150,000) pays for months of ads. Educator and manager ads
   that send people to `/schools/` and `/teams/` can afford PKR 500–1,000 per lead.
3. **Sharing.** Every share card and Milan invite brings free users. If each finished test brings 0.5 more, the
   cost per finished test effectively falls by a third.
4. **Phase 2 subscriptions** raise what each customer is worth over time; that is what lets apps in this category
   buy ads profitably.

## 2. Phase 1 plan: 3 weeks, capped

**Budget (owner decides):** PKR 60,000 total (about $215), at most PKR 3,000 a day. Do not raise it until the rules in
§4 say so.

**Objective:** Meta "Sales" or "Leads" campaign optimised for the website **Lead** event (a finished test). Use
"Purchase" only once there are 50+ purchases a week. TikTok later: its $50/day campaign minimum is above this budget.

| Ad set | Who | Where | Creatives | Landing | Daily |
| --- | --- | --- | --- | --- | --- |
| A. Everyone, cheap reach | 18–65+, broad (Advantage+ audience) | Pakistan | a01, a07, a08 | test | PKR 800 |
| B. Students | 16–24, broad; interests: university, exams, careers | Pakistan, Philippines | a02 | `/career/` | PKR 500 |
| C. Professionals | 24–55, broad; interests: management, productivity, HR | Pakistan, UAE | a03 | test | PKR 500 |
| D. Educators (B2B) | Interests: teachers, school administration, education | Pakistan | a04 | `/schools/` | PKR 500 |
| E. Families and couples | 25–65, broad | Pakistan, UAE, UK (small) | a06 | `/milan/` | PKR 400 |
| F. Retargeting | Finished a test in the last 14 days, didn't buy | All | a01 feed + a "your full report" variant | result page | PKR 300 |

- Marketers (a05) start organically on socials and LinkedIn; add as an ad set if organic posts get saves.
- Placements: Advantage+ placements, with both the 4:5 and 9:16 images uploaded for each ad.
- Links: use the "Website URL" in each `copy.txt`. It carries `utm_campaign` and `utm_content`, so every test
  taker is tagged with the ad that brought them, and the Monday report can split results by ad (T42).

## 3. Ad rules (Meta policy and our brand)
- Never assert or imply a personal attribute: no "Are you over 50?", "Are you an introvert?" style lines aimed at
  the reader. Talk about types and situations instead ("One colleague plans, another improvises").
- No medical or mental-health claims; temperament stays "traditional wisdom". Palm, zodiac and numbers stay "for fun".
- No MBTI, Myers-Briggs or 16Personalities words or type names (STYLE.md rule 1).
- Don't promise "never a subscription": phase 2 will add one.

## 4. Kill and scale rules (check every 3 days)
- **Kill an ad** with a link CTR under 0.8% after 3,000 impressions.
- **Kill an ad set** whose cost per finished test is above 2× the table in §1 after 50 finished tests.
- **Keep** ad set D (educators) if it brings at least one real school conversation a week, whatever the CPL.
- **Scale an ad set by 20%** (at most every 3 days) when its 7-day revenue per finished test, counting B2B leads at
  PKR 1,500 each, is at least 80% of its cost per finished test.
- **Stop everything** if total spend reaches the owner's cap.

## 5. Setup (owner, about one hour; task T41)
1. Meta Business Suite → create a Business portfolio "Mizaj" and an ad account (currency PKR). Use a card with
   international online payments switched on, and check the advance-tax and filer points in research 03 §5.5 with
   your bank.
2. Events Manager → create a Pixel (Dataset) → send its **ID** (a number, not a secret) to `claude-server` to put in
   `META_PIXEL_ID` in `/opt/mizaj/.env`. Verify the domain mizaj.pk (Brand safety → Domains; `claude-server` can add
   the DNS TXT record).
3. Check the Pixel fires: open mizaj.pk, finish a test, and look for **Lead** in Events Manager → Test events.
   The site already sends `Lead` (finished test), `InitiateCheckout` and `Purchase` (with value and currency).
4. Create the campaign in §2 with the creatives from `social/ads/`. Set the spending limit on the account.

## 6. What gets measured (every Monday, T42)
Spend, impressions, CTR, cost per finished test, share rate, Milan invites, purchases and revenue per finished
test, by ad set, creative and country; B2B leads by source. All from the Meta report plus the site's own aggregate
stats (utm fields), never personal data.
