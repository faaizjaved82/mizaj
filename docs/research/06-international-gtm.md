# Mizaj international go-to-market: payments, pricing, markets, domain, languages

Prepared 28 Oct 2026 for the pivot from mizaj.pk (Pakistan-only) to an English-first international brand. Current
one-time USD prices in `content/products.json`: Palm $5, Full report $9, Career Compass $14, Mizaj Milan couple $15,
Bundle $24.

## Read this first: method and limits

- **About 50 WebSearch queries** (standard and extended). Most facts come from search-result summaries of the cited
  page, not the full page.
- **WebFetch was blocked.** paddle.com, docs.lemonsqueezy.com and polar.sh all failed with "host not allowed" in this
  session. RDAP/WHOIS lookups were also blocked by the proxy.
- **Primary sources read directly (not snippets):**
  - Polar's Acceptable Use Policy and supported-countries page, read from Polar's public source repo
    (github.com/polarsource/polar, HEAD commit `089a23fd`, 28 Oct 2026).
  - Gumroad's prohibited-products page and payout-country code, read from Gumroad's public source repo
    (github.com/antiwork/gumroad, HEAD commit `33999876`, 28 Oct 2026).
  - Domain availability was checked against the registry with the Shopify domain-check connector on 28 Oct 2026. It
    is a point-in-time check, and nothing was registered.
- Labels: **[official]** = the provider's own page or code. **[secondary]** = a blog, review or guide; several are
  written by competing payment companies (Dodo, Creem, Fungies), so treat them with care. **[estimate]** = my
  calculation or judgement.

---

## 1. Getting paid internationally from Pakistan (2026)

### 1.1 Summary table

| Platform | Pakistani seller eligible? | Payout route to Pakistan | Fees (headline) | Tax as MoR | Astrology / palm / "pseudo-science" | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| **Gumroad** | Yes | Stripe cross-border payout in **PKR** to a local bank. No Payoneer or Wise | 10% + $0.50 direct (30% via Discover), card processing reportedly extra | Yes, since 1 Jan 2025 | **Allowed** if sold "for insight, reflection or entertainment" | Easiest fit for the product mix; most expensive |
| **Paddle** | Yes (not on unsupported list) | Wire or Payoneer, monthly, $100 minimum | 5% + $0.50 | Yes | **Prohibited:** "pseudo-science… clairvoyance, horoscopes, fortune-telling"; also medical advice | Best economics for core reports if approved; no palm |
| **Polar** | Yes (Pakistan on official payout list), individuals OK | Stripe Connect Express to a Pakistani bank | ~5% + $0.50 since May 2026 (was 4% + $0.40) | Yes | **Prohibited:** pseudo-science, medical/health advice, products for minors; "Spiritual & Astrology" needs review | Workable for core reports only |
| **Lemon Squeezy** | Yes today (bank payouts) | Bank payout in USD via Stripe (1% non-US payout fee). PayPal payout unusable in PK | 5% + $0.50, +1.5% intl, +1.5% PayPal | Yes | No explicit ban found; bans "services of any kind" | Works now; strategic risk from Stripe Managed Payments migration |
| **Stripe Managed Payments** | **No** (Pakistan not a supported business location) | n/a | ~6.4%+ reported | Yes | n/a | Not available |
| **FastSpring** | Unconfirmed | Bank payout, twice monthly, $100 minimum | Unpublished, quote only | Yes | Unknown | Software-focused; skip |
| **2Checkout (Verifone)** | Possible, but underwriting rejections are common | Wire, Payoneer, PayPal; rolling 90-day reserve | Not verified | Yes (2Monetize plan) | Unknown | Skip |
| **Payoneer Checkout / card requests** | Yes (Payoneer works in PK) | Payoneer balance to Pakistani bank | 3.99% + $0.49 card; 1% receive; ~2% FX; $29.95/yr if <$6k | **No** (you owe VAT/GST yourself) | n/a | Fallback only |
| **Stripe via Atlas / US LLC** | Yes via a US entity | Stripe to US bank, then onward | Atlas $500 one-time + annual compliance | **No** (unless Managed Payments via the US entity) | Stripe rules apply | Not worth it at current volume |
| **PayPal** | **No** (Pakistan residents can't receive) | n/a | n/a | n/a | n/a | Not available |
| **Wise** | **No** account for PK residents | Can only receive PKR into a PK bank from a sender abroad | n/a | n/a | n/a | Not a receiving route |
| **Dodo Payments** | **No** per official docs (conflicting blog) | n/a | 4% + $0.40 (+1.5% intl) | Yes | n/a | Not available |
| **Creem** | "Limited" for Pakistan | n/a | 3.9% + $0.40 | Yes | n/a | Unclear |

### 1.2 Platform detail

**Gumroad**
- Gumroad is the merchant of record. Since 1 Jan 2025 it "will handle ALL your tax obligations" **[official]**
  https://gumroad.com/taxes. The pricing page says it collects tax "in regions where we have tax obligations as a
  merchant of record" **[official]** https://gumroad.com/pricing.
- Fees: 10% + $0.50 per direct sale and 30% for sales through the Discover marketplace **[official]**
  https://gumroad.com/pricing. A 2026 guide says card processing (2.9% + $0.30) is charged on top of the 10% + 50¢
  **[secondary]** https://dodopayments.com/blogs/gumroad-fees-explained.
- **Pakistan payouts:** Gumroad's code lists Pakistan in `CROSS_BORDER_PAYOUTS_COUNTRIES` (Stripe cross-border
  payouts) with payout currency PKR. **[official, source code]** https://github.com/antiwork/gumroad/blob/main/app/models/country.rb
  (read 28 Oct 2026). A guide says Gumroad pays Pakistanis in rupees to a local account, not USD, and does not
  support Payoneer or Wise **[secondary]** https://www.lilachbullock.com/gumroad-in-pakistan/.
- Payout timing: sales are held at least 7 days, the minimum payout is $100, and new accounts are reviewed for 1–3
  weeks **[secondary]** https://www.lilachbullock.com/gumroad-in-pakistan/,
  https://insightraider.com/en/answers/when-does-gumroad-pay-out.
- **Category policy, verbatim [official]:** "fortune tellers" is prohibited. Gumroad's note says this covers
  "operating a prediction service: concrete claims about what will happen to a buyer, and readings framed as
  medical, legal or financial advice… It does not cover astrology, tarot, numerology, birth-chart and divination
  material sold for insight, reflection or entertainment… pre-written reports are all allowed. A one-off personalized
  reading is also allowed when it is sold as reflection or entertainment and makes no concrete promise"
  https://gumroad.com/prohibited (also read from `app/views/home/prohibited.html.erb` in Gumroad's repo).
  Mizaj's "for fun" palm reading fits this wording exactly.
- Gumroad has built-in purchasing-power-parity (PPP) pricing (`purchasing_power_parity_service.rb` in its repo)
  **[official, source code]** https://github.com/antiwork/gumroad. With PPP, regional prices need no extra tooling.
- Gumroad's sexual-content clause bans "dating services" **[official]** https://gumroad.com/prohibited. Mizaj Milan
  must stay framed as compatibility/rishta, never dating. That already matches STYLE.md.

**Paddle**
- Paddle says it acts as MoR for sellers in 200+ countries. Its sellable-country list can change for sanctions
  reasons, and the `/countries` API endpoint shows it **[official]**
  https://developer.paddle.com/concepts/sell/supported-countries-locales.
- One guide (checked "October 2026") says Pakistan is not on Paddle's unsupported list. Payouts go by wire or
  Payoneer, monthly, with a $100 adjustable threshold **[secondary]**
  https://jawadhassan.dev/blog/paddle-vs-lemonsqueezy-pakistan. A SWIFT payout costs $/€/£15 per transfer (same
  source). A developer post (2026) says "paddle → 5%+50c per transaction, also support Pakistan" **[secondary]**
  https://x.com/wzulfikar/status/2049835672203338010.
- **Category policy:** Paddle's AUP help page lists "digital services associated with pseudo-science including, but
  not limited to, clairvoyance, horoscopes, fortune-telling". It also lists medical advice, and human services not
  tied to a software offering **[official, via search snippet]**
  https://www.paddle.com/help/start/intro-to-paddle/what-am-i-not-allowed-to-sell-on-paddle. Confidence is
  medium-high. Two of three search summaries showed this wording on Paddle's page. The third saw only a truncated
  snippet. Polar's AUP uses the identical sentence (see below). Palm reading would very likely fall under it. The
  Unani diet and routine content risks the "medical advice" clause unless it is framed as traditional/cultural
  lifestyle content with a disclaimer.
- Paddle's review checks that the legal entity on the website matches the account, and that the refund-policy
  wording is acceptable **[secondary]**
  https://dev.to/pavelbuild/paddle-rejected-my-saas-3-times-heres-what-they-check-that-isnt-in-their-docs-5dnn.
  Paddle Billing also excludes "standalone human services" and marketplaces **[secondary]**
  https://highriskpaymentprovider.com/providers/paddle/.

**Polar (polar.sh)**
- **Pakistan is on Polar's official payout list.** Polar pays out through Stripe Connect Express. "As the Merchant
  of Record… Stripe Payments doesn't need to be available in your country." The list includes Pakistan, the
  Philippines, India, Indonesia, Turkey and Bangladesh **[official]**
  https://polar.sh/docs/merchant-of-record/supported-countries (read from `docs/merchant-of-record/supported-countries.mdx`
  in Polar's repo, 28 Oct 2026). Individuals can sell "given that Stripe Connect Express supports individual as a
  business type in your region" (same page).
- This lines up with Stripe adding Pakistan (`pk_bank_account`) to cross-border payouts on 25 Feb 2026
  **[official]** https://docs.stripe.com/changelog/clover/2026-02-25/cross-border-payouts-new-countries.
- Fees: Polar raised its base rate in May 2026 from 4% + $0.40 to 5% + $0.50 on the starter tier. Paid plans
  ($20/$100/$400 a month) cut the rate to 3.8%/3.6%/3.4% **[secondary]** https://fungies.io/polar-sh-review-2026,
  https://dev.to/chenningdev/receiving-usd-payments-in-pakistan-as-a-developer-what-actually-works-in-2026-1enb.
  Payouts take 4–7 business days **[official]** https://polar.sh/docs/features/finance/payouts.
- **Category policy, verbatim [official]** https://polar.sh/legal/acceptable-use-policy (read from source):
  - Prohibited #31: "Digital services associated with pseudo-science including, but not limited to, clairvoyance,
    horoscopes, fortune-telling".
  - Prohibited #32: "Medical and Health advice".
  - Prohibited #10: "Services used by, intended for, or advertised towards minors". This matters for Career
    Compass, which is aimed at FSc/A-level students.
  - "Restricted businesses that require closer review" include "Spiritual & Astrology services", "AI Content
    Generation tools" and "eBooks".
  - "Polar serves software companies (including B2B SaaS, Consumer Software, and Games)."

**Lemon Squeezy (owned by Stripe)**
- A Jan 28, 2026 update from the co-founder said the team was building Stripe Managed Payments and wanted an easy
  migration path for Lemon Squeezy users. It also acknowledged slower support and fewer product updates
  **[official]** https://www.lemonsqueezy.com/blog/2026-update.
- Stripe Managed Payments became generally available on 22 Apr 2026 **[official]**
  https://docs.stripe.com/changelog/dahlia/2026-04-22/managed-payments. It supports merchants in roughly 35–39
  countries, and Pakistan is not one of them **[secondary, competitor-written]**
  https://dodopayments.com/blogs/stripe-managed-payments-fees-explained,
  https://dodopayments.com/blogs/stripe-supported-countries-alternatives. **Risk [estimate]:** if Lemon Squeezy
  merchants are eventually moved to Managed Payments, a Pakistan-based seller could lose the rail. No forced
  migration date is documented **[secondary]** https://eden.so/blog/lemon-squeezy-alternatives/.
- Pakistan appears on Lemon Squeezy's bank-payout list. The payout methods are bank transfer and PayPal, Payoneer is
  not offered, and the minimum is $50 **[secondary]** https://www.lilachbullock.com/lemon-squeezy-in-pakistan/,
  https://jawadhassan.dev/blog/paddle-vs-lemonsqueezy-pakistan. An AgentaOS table dated 6 Oct 2026 marks it "Yes"
  for Pakistan **[secondary]** https://agentaos.ai/answers/which-merchant-of-record-pays-out-to-my-country.
- Fees: 5% + $0.50, plus 1.5% for buyers outside the US, 1.5% for PayPal checkouts and 0.5% for subscriptions
  **[secondary]** https://www.swell.is/content/lemon-squeezy-pricing. Payouts are free to US banks and **1% per payout
  to non-US banks**. PayPal payouts outside the US cost 3%, capped at $30 **[official]**
  https://docs.lemonsqueezy.com/help/getting-started/fees.
- **Category policy:** prohibits "Services of any kind", physical goods, regulated products and anything restricted
  by its payment partners. No astrology, psychic or pseudo-science entry was found **[official, via snippet]**
  https://docs.lemonsqueezy.com/help/getting-started/prohibited-products, https://www.lemonsqueezy.com/terms. Dating
  sites are banned (same page).

**FastSpring**
- The default payout schedule is twice a month with a $100 minimum **[official]**
  https://developer.fastspring.com/docs/receive-payouts. FastSpring does not publish its rates; you need a written
  quote **[secondary]** https://dodopayments.com/blogs/fastspring-pricing-explained/.
- Pakistan eligibility is unconfirmed. Its payout portal "does not support sellers in certain countries", and the
  list is not published **[secondary]** https://learnwithhasan.com/payment-gateways/fastspring/.
- A different provider (Freemius) notes that "transferring PKR… to a PK business account through wire transfer is
  not supported by regulation" **[official for Freemius]**
  https://freemius.com/changelog/improvements-to-the-wire-payout-methods/. Plan on USD payouts to a USD/FCY account
  or Payoneer.

**2Checkout / Verifone**
- Payouts go by wire, Payoneer or PayPal **[official]** https://www.2checkout.com/merchant-support/faq/. They run
  weekly, bi-weekly or monthly, and a percentage of sales is held on a rolling 90-day basis **[official]**
  https://verifone.cloud/docs/2checkout/Onboarding/Payouts.
- Pakistani guides say 2Checkout is technically available, but many Pakistani applicants are rejected in
  underwriting. Settlement is T+3 or slower, at fees above local alternatives **[secondary]**
  https://techparallel.com/best-payment-gateways-for-shopify-in-pakistan/,
  https://digiteazy.com/payment-gateway-pakistan/. Current rates were not verified.

**Payoneer (Checkout / payment requests)**
- Pakistan fees: card payments up to 3.99% + $0.49 (effective 20 Oct 2024); 1% to receive into a USD/EUR/GBP
  account; and, from 23 Feb 2026, a $29.95 annual fee if the account receives less than $6,000 in 12 months
  **[secondary, citing Payoneer's schedule]** https://pakera.pk/payoneer-fees-pakistan-2026/.
- Withdrawal with conversion reportedly costs up to about 2% above mid-market (same source).
- Payoneer Checkout is reported as available to Pakistani Shopify merchants **[secondary, ~2.5 years old]**
  https://www.hulkapps.com/blogs/shopify-payment-providers/unlocking-e-commerce-potential-payoneer-checkout-shopify-integration-in-pakistan.
  A 2026 guide says Payoneer "cannot accept card payments from your own customers like Stripe can" **[secondary]**
  https://startglobal.co/us/international/pakistan/payoneer/.
- Payoneer is **not a merchant of record**. EU/UK VAT on digital sales to consumers would be Mizaj's own problem.
  From general knowledge (not re-verified here): non-EU sellers owe EU VAT from the first sale via the non-Union
  OSS.

**Stripe via Stripe Atlas (US entity)**
- Stripe is not directly available to Pakistan-based businesses **[secondary]**
  https://www.lilachbullock.com/stripe-in-pakistan/.
- Atlas costs $500 one-time for a Delaware company with an EIN and a US bank account **[secondary]**
  https://app.unil.ink/blog/stripe-atlas-2026, https://wpsimplepay.com/is-stripe-atlas-worth-the-money/. Founders
  in sanctioned jurisdictions are blocked, and Pakistan is not on that list **[secondary]** (same).
- Compliance burden: a foreign-owned single-member US LLC is a "foreign-owned domestic disregarded entity", with
  annual Form 5472 filings. Controlling it from Pakistan can raise Pakistani tax-residence questions **[secondary]**
  https://www.businesstoday.in/impact-feature/story/forming-a-us-llc-to-access-stripe-is-a-legitimate-move-the-tax-compliance-it-creates-is-not-small-519932-2026-03-10,
  https://zenoledger-site.pages.dev/blog/stripe-atlas-vs-zenoledger/.
- Plain Stripe is not an MoR. **[estimate]** A US entity might qualify for Stripe Managed Payments (MoR), but
  category rules would still apply. This is not worth it until international revenue is roughly $3–5k a month.

**PayPal**
- In Jan 2024 the government announced a pilot under which foreign clients would pay through PayPal and the money
  would land in freelancers' local accounts **[secondary, news]**
  https://www.geo.tv/latest/526076-finally-pakistani-freelancers-to-be-able-to-receive-payments-via-paypal. I found
  no confirmation that it went live.
- A June 2026 piece says PayPal in Pakistan is still not usable for receiving **[secondary]**
  https://en.dailypakistan.com.pk/19-Jun-2026/pakistan-freelance-exports-hit-1-6-billion-the-policy-agenda-nobody-is-talking-about.
- **Implication:** buyers can still pay with PayPal on Paddle, Lemon Squeezy or Gumroad checkouts. Only the seller
  side is blocked.

**Wise**
- USD account details require an address in a country where Wise lets you open a balance **[official]**
  https://www.wise.com/help/articles/2810318/can-i-get-usd-account-details. Pakistani residents can't sign up
  directly. Senders abroad can pay PKR into a Pakistani bank **[secondary]**
  https://abroadmate.me/guides/wise-in-pakistan-2026-guide.
- An older TechJuice report that Wise accounts were "coming to Pakistan… within weeks" is not borne out by 2026
  sources **[secondary]** https://www.techjuice.pk/wise-accounts-coming-to-pakistan-for-freelancers-within-weeks/.

**Dodo Payments / Creem**
- Dodo's docs say merchant accounts are supported only where KYC documents are issued in listed countries. Its
  Chinese-language Pakistan post says Pakistani onboarding is not supported, while the English post claims it is
  **[official/conflicting]** https://docs.dodopayments.com/miscellaneous/accepted-countries-and-territories.md,
  https://dodopayments.com/zh/blogs/sell-software-from-pakistan,
  https://dodopayments.com/blogs/sell-software-from-pakistan.
- AgentaOS marks Dodo "No" and Creem "Limited" for Pakistan **[secondary]**
  https://agentaos.ai/answers/which-merchant-of-record-pays-out-to-my-country.

### 1.3 Pakistan-side tax and compliance

- PSEB-registered IT/ITeS exporters pay a 0.25% final tax on export proceeds received through banks (s.154A).
  Registration needs an SECP company or registered firm plus an NTN **[secondary]**
  https://urcapk.com/taxation/pakistan-it-exports-pseb-registration-025-tax-rate/.
- Freelancer guides say registration cuts the rate from 1% to 0.25% **[secondary]**
  https://filekero.pk/guides/pseb-registration-freelancer.
- **Conflict:** Business Recorder reported that the regime expires 30 Jun 2026 unless extended **[news]**
  https://www.brecorder.com/news/amp/40358496. One advisory says Finance Bill 2026 extended it to 30 Jun 2029
  **[secondary]** https://urcapk.com/taxation/pakistan-it-exports-pseb-registration-025-tax-rate/. A May 2026 guide
  says the post-June-2026 status needs verification **[secondary]**
  https://taxwizard.pk/blog/how-to-claim-it-export-tax-pakistan-2026/. Owner to confirm with an accountant.
- Foreign income remitted through banking channels (Payoneer withdrawals, SWIFT) is treated as IT export income
  **[secondary]** https://vaultleap.com/blog/receiving-usd-payments-in-pakistan-2026. Whether MoR payouts for
  consumer reports qualify as "IT export" is an accountant question.

### 1.4 Consumer-law notes for international sales

- The EU Court of Justice held that a dating site's personality report generated from its personality test is
  **not** "digital content" under the Consumer Rights Directive. The 14-day withdrawal rules for services apply
  instead **[secondary, case summary]**
  https://www.scl.org/12076-what-proportion-of-an-online-membership-should-be-due-when-cancelled-cjeu-rules-on-consumer-rights-directive/.
  Mizaj's 7-day refund promise is shorter than the EU/UK 14-day withdrawal right. The MoR's buyer terms will
  probably govern; check them.
- The US FTC "click-to-cancel" rule was vacated by the Eighth Circuit (2025), but negative-option enforcement
  continues **[secondary]** https://www.wiggin.com/publication/ftcs-click-to-cancel-rule-has-been-vacated/,
  https://www.mondaq.com/unitedstates/contracts-and-commercial-law/1747036/ftcs-click-to-cancel-rule-gets-new-life-as-ftcs-enforcement-wave-continues-to-target-negative-option-sellers.
  Mizaj's no-subscription stance avoids this.
- Apple has rejected apps that "primarily feature astrology, horoscopes, palm reading, fortune telling or zodiac
  reports" as duplicates **[official forum]** https://developer.apple.com/forums/thread/737999. Staying web-first
  is the right call.

### 1.5 Fee impact on Mizaj price points [estimate, my arithmetic on the headline fees above]

| Price | Paddle / Polar (5% + 50¢) | Lemon Squeezy (6.5% + 50¢ + 1% payout) | Gumroad (10% + 50¢) | Gumroad if 2.9% + 30¢ processing is extra |
| --- | --- | --- | --- | --- |
| $5 | $0.75 (15%) | $0.88 (18%) | $1.00 (20%) | $1.45 (29%) |
| $9 | $0.95 (11%) | $1.17 (13%) | $1.40 (16%) | $1.96 (22%) |
| $15 | $1.25 (8%) | $1.61 (11%) | $2.00 (13%) | $2.74 (18%) |
| $24 | $1.70 (7%) | $2.28 (10%) | $2.90 (12%) | $3.80 (16%) |

The fixed 50¢ makes anything under about $7 inefficient on every MoR. Paddle's $15 SWIFT payout fee and Payoneer's
withdrawal FX come on top.

---

## 2. Pricing benchmarks (USD, 2026)

| Product | Model | Price | Source |
| --- | --- | --- | --- |
| 16Personalities Premium Career Suite | one-time | $29 (currency unlabelled on page); £24.99 UK; €29 EU | **[official]** https://www.16personalities.com/premium/career-suite; **[secondary]** https://mypassion.ai/blog/16personalities-career-test-review |
| 16Personalities full premium tier | one-time | ~$90–99 (unverified) | **[secondary]** https://jobcannon.io/blog/jobcannon-vs-16personalities |
| Truity full report (TypeFinder, Enneagram, Big Five) | one-time | ~$19–35 depending on test; $29–59 cited elsewhere | **[secondary]** https://themoneybees.co/blog/free-personality-tests-like-mbti, https://jobcannon.io/compare/jobcannon-vs-truity |
| Truity@Work (professional) | per test | from $9/test | **[official]** https://www.truity.com/page/truity-work-bigfive |
| Co-Star Plus | subscription | ~$2.99/mo or $19.99/yr; $9.99 one-time item (labels ambiguous) | **[secondary]** https://blog.whisper.day/reviews/co-star-review-2026/ |
| The Pattern "Go Deeper+" | subscription | $14.99/mo, $83.99/yr (US App Store); Bonds: 3 extra profiles $9.99 | **[official]** https://apps.apple.com/us/app/the-pattern-astrology/id1071085727 |
| CHANI | subscription | $11.99/mo, $107.99/yr | **[official]** https://apps.apple.com/app/id1532791252; https://adapty.io/paywall-library/chani/ |
| Nebula (astrology/palm/psychic) | subscription + per-minute | ~$7.99/week after 3-day trial; $24.99/mo; older listings $9.99/wk, $49.99/yr | **[secondary]** https://www.republicworld.com/initiatives/nebula-app-review-2026-features-cost-and-who-its-for-2026-09-16-137105, https://www.top10.com/psychic-reading/reviews/nebula |
| Automated compatibility (synastry) reports | one-time | $7–16 (Cafe Astrology $6.95; GetMyHoro €14.99) | **[secondary, vendor blog]** https://my-zodiac-ai.com/blog/how-much-does-synastry-report-cost-2026 |
| Written compatibility reports | one-time | $22–55 (Astrology Sphere £22; Astromara £37; The Inner Wheel $55) | same |
| Live synastry session | one-time | $100–250 | same |

**One-time vs subscription on the web**
- Test publishers that sell on the web (16Personalities, Truity) use **one-time** unlocks of about $19–35 (table
  above).
- Daily-content astrology apps (Co-Star, The Pattern, CHANI, Nebula) use **subscriptions**, mostly through app
  stores. Nebula's most common complaint is short free trials that turn into recurring charges **[secondary]**
  https://www.top10.com/psychic-reading/reviews/nebula.
- Vendor benchmarks put cold-traffic conversion for one-time offers at about 2–5%, against 0.5–2% for
  subscriptions **[secondary, vendor claim]** https://www.armemberplugin.com/subscription-vs-one-time-purchase/.
- Across 115,000 apps, 63.5% are subscription-only, and 23.2% also sell a lifetime (one-time) option **[official]**
  https://www.revenuecat.com/state-of-subscription-apps.
- **[estimate]** For a web quiz brand selling one deep report per life question, one-time is the better fit. "No
  subscription, no trial" is also a selling point against Nebula-style funnels.

---

## 3. Markets: who responds, and what reach costs

### 3.1 Ad cost benchmarks (CPM, USD)

These are directional only. Each source samples different advertisers: ecommerce sets run higher than awareness
campaigns. Compare figures within one source.

| Market | Meta (FB/IG) CPM | Instagram-specific | TikTok CPM |
| --- | --- | --- | --- |
| United States | $16.08 (Jul 2026) | $11.20–18.40 (Q1 2026) | $8.50; $6–12 |
| United Kingdom | $11.81 (Jul 2026) | $9.80–15.20 | $7.80; $5–10 |
| Saudi Arabia | $12.01 (Lebesgue); $4.20–8.00 (Stackmatix); $8–15 ecommerce, peaks $18–28 in Ramadan/National Day (BIMO) | – | Gulf $4–8 |
| UAE | $6.50 | – | Gulf $4–8 |
| Malaysia | $5.39 (Lebesgue); $4.80 (Adamigo) | $3.50–5.50 | SEA $1–3 |
| Brazil | $4.20 | $2.40–5.60 | $3.50; $2–4 |
| Turkey | $2.00–4.40 / $2.00–3.50 | – | no data |
| Philippines | $3.50 | – | $1–2 |
| Indonesia | $2.80 | – | $1.80; $1–2 |
| India | $1.36 (Jul 2026); $2.60 | $1.20–3.60 | – |
| Pakistan | $0.60–1.80; $0.80–1.50; $2.20 | – | – |

Sources:
- PaceAds citing Lebesgue, Jul 2026: https://paceads.com/research/meta-ads-statistics-2026
- Lebesgue country table: https://lebesgue.io/facebook-ads/facebook-cpm-by-country
- Stackmatix Instagram, Q1 2026: https://stackmatix.com/blog/platform-ad-cost-benchmarks-country-industry-2026
- Stackmatix Facebook: https://www.stackmatix.com/blog/facebook-ads-cpm-by-country-2026
- Adamigo (about 9 months old): https://www.adamigo.ai/blog/meta-ads-cpm-cpc-benchmarks-by-country-2026
- Adligator: https://adligator.com/blog/meta-ads-cpm-by-country-benchmarks
- BIMO (GCC): https://www.bimogroup.co/blog/meta-ads-benchmarks-gulf
- TikTok, Stackmatix: https://www.stackmatix.com/blog/tiktok-ads-cost-2026-pricing-breakdown
- TikTok, Variant: https://variant-intl.com/blog/tiktok-cpm-by-country.html
- TikTok, TikAdSuite: https://tikadsuite.com/blog/tiktok-cpm-rates/

Notes:
- TikTok's minimum daily ad-group budget is $20 in each of these markets **[secondary]**
  https://www.stackmatix.com/blog/tiktok-ads-cost-2026-pricing-breakdown.
- **Ad policy:** TikTok's ads policy has a "Horoscope and fortune-telling products and services" section with
  market-specific rules **[official, heading only seen]**
  https://ads.tiktok.com/help/article/tiktok-ads-policy-other-products-and-services. Meta and TikTok said in 2022
  that they are not banning astrology or tarot content **[news]**
  https://hypebae.com/2022/2/tarot-astrology-ban-tiktok-instagram-facebook-meta-rumors-paid-advertising-info.
  **[estimate]** Lead paid ads with the personality test; keep palm out of ad creative.

### 3.2 Where personality typing is big

- **16Personalities traffic by country:**
  - Semrush (Feb 2026): Japan 20.8%, US 16.7%, UK 5.3%, France 4.4%, Brazil 3.2% **[secondary]**
    https://semrush.com/website/16personalities.com/overview
  - Ahrefs (Oct 2026): Japan is 41.5% of search traffic **[secondary]**
    https://ahrefstop.com/websites/16personalities.com
  - Similarweb (Sep 2026, desktop): US 27.6%, Japan 9.6%, Canada 4%, Germany 3.2%, France 3% **[secondary]**
    https://www.similarweb.com/website/16personalities.com/
- **South Korea:** a Dec 2021 Hankook Research survey reportedly found that over half of Koreans had taken the
  test, including 9 in 10 people aged 19–28. Attribution came via search summary; see the MDPI study of MBTI
  perceptions in Korea **[secondary]** https://www.mdpi.com/2071-1050/16/10/4152. Newer "93%" claims could not be
  verified (same search).
- **Japan:** 41.3% of Gen Z women had taken the test (MERY Inc., Sep 2024) **[secondary]**
  https://www.fun-japan.jp/en/articles/14070. Google Trends interest rose "dozens of times" over three years
  **[news]** https://www.asiae.co.kr/en/article/2024090308431224915.
- **Malaysia:** The Star (Oct 2025) reported on Gen Z embracing four-letter types **[news]**
  https://www.thestar.com.my/lifestyle/living/2025/10/10/can-a-four-letter-code-really-define-who-you-are.
- **Mexico/Latin America:** typing is called "the horoscope of Gen Z" **[news]**
  https://www.excelsior.com.mx/trending/mbti-que-es-y-cuales-son-las-16-personalidades/1626266.
- **Astrology apps:** India holds an estimated 10–18% of global astrology-app installs, and Asia-Pacific 40–50% of
  downloads (2024) **[secondary, low reliability]**
  https://www.marketgrowthreports.com/market-reports/horoscope-and-astrology-apps-market-118691.
- **Gaps:** I found no hard data on personality-test interest in the Philippines, Indonesia, Turkey or the Gulf.
  Searches returned nothing usable, so treat those markets as hypotheses to test with cheap ads.

### 3.3 "Mizaj" across languages

- **Arabic** مِزَاج (mizāj), from the root م ز ج, "to mix, to blend". It covers bodily temperament or humour, and
  everyday "mood" **[dictionary]** https://www.wiktionary.com/wiki/%D9%85%D8%B2%D8%A7%D8%AC. An Iraqi app is
  literally called "Mazajk – مزاجك" ("your mood") **[official listing]** https://apps.apple.com/app/id6450610540.
  Arabic speakers will read the brand as "mood/temperament": a fit, not a clash.
- **Turkish** *mizaç* means a person's character or temperament, via Ottoman مزاج from Arabic **[dictionary]**
  https://wiki.neonvagabond.xyz/content/wiktionary_en_all_nopic_2024-05/A/miza%C3%A7.
- **Persian** *mezâj* means temperament, temper or nature. **Urdu/Hindi** *mizaaj* means temperament or mood
  **[dictionary]** https://wiki.neonvagabond.xyz/content/wiktionary_en_all_nopic_2024-05/A/%D9%85%D8%B2%D8%A7%D8%AC,
  https://poetistic.com/dictionary/mizaj?lang=en.
- **Medical/Unani sense** (Ibn Sina's four temperaments) **[reference]** https://www.britannica.com/science/mizaj.
  An Iranian app teaches the four temperaments ("Mood training", CafeBazaar) **[listing]**
  https://cafebazaar.ir/app/com.ghsoft.mazajshenasi?l=en.
- **Malay/Indonesian: not confirmed.** No KBBI or Dewan Bahasa entry for "mizaj" turned up (two searches). Don't
  assume Malay or Indonesian speakers recognise the word.
- **[estimate]** The name gives a native-word advantage in Arabic (Gulf), Turkish, Persian, Urdu and Hindi markets.
  In English markets it reads as a neutral, pronounceable coined name.

---

## 4. Domain and brand

**Availability.** Registry check through the Shopify domain connector on 28 Oct 2026. This is point-in-time, not a
hold, and nothing was registered.

| Domain | Status | First-year price quoted |
| --- | --- | --- |
| mizaj.com | **Taken** | – |
| mizaj.app | **Taken** | – |
| mizaj.co | **Taken** | – |
| mizaj.me | **Taken** | – |
| getmizaj.com | **Available** | $16 |
| trymizaj.com | **Available** | $16 |
| mymizaj.com | **Available** | $16 |
| mizajly.com (suggested by the tool) | Available | $16 |

A web search found no live site on mizaj.com, .app or .co, so they may be parked; who holds them is unknown.
Renewal prices are usually higher than first-year prices.

**Is .pk a handicap?**
- Google uses ccTLDs as a signal of a site's target country. It treats only some ccTLDs (for example .tv and .me) as
  generic. New gTLDs such as .app are treated as generic **[official]**
  https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites. .pk is a
  country-targeted ccTLD, so mizaj.pk is geotargeted to Pakistan in Google search.
- Registrars and vendors say ccTLDs build trust at home but can make foreign visitors assume a store is local-only,
  while .com "leads for global recognition". These are vendor claims, not studies **[secondary]**
  https://www.namesilo.com/blog/en/domain-names/country-domains-customer-trust,
  https://clispot-com.pages.dev/insights/conversion-sales/unlocking-global-sales-how-your-domain-name-impacts-international-e-commerce-conversions/.
- The comparison set mostly uses .com: 16personalities.com, truity.com, chani.com, asknebula.com (domains seen in
  the sources above).
- MoR reviews (Paddle) check that the brand and entity on the site match the account **[secondary]**
  https://dev.to/pavelbuild/paddle-rejected-my-saas-3-times-heres-what-they-check-that-isnt-in-their-docs-5dnn.
  Decide the international domain before applying.
- **[estimate]** Avoid "trymizaj": "try" suggests a trial, which conflicts with the no-trials promise.

---

## 5. Localization

- 16Personalities says its test is translated into "more than 35 languages… the most translated of the major
  personality tests on the Internet" (2021 interview) **[secondary]**
  https://vavel.media/en/2021/02/19/1060129-interview-16-personalities-understanding-the-strengths-and-weaknesses-of-your-own-personality-type-can-certainly-aid-in-positive-personal-growth.html.
- Its largest country is Japan by visits and by search traffic. France and Brazil are in its top five (Semrush,
  Ahrefs; see 3.2). **[estimate]** Localized markets (Japan, France, Brazil, Germany) make up well over a third of
  its traffic. Localization, rather than English alone, built its reach.
- Share of web content (W3Techs, Dec 2025): English 49.3%, Spanish 6.0%, German 5.9% **[secondary]**
  https://en.wikipedia.org/wiki/Languages_used_on_the_Internet. Portuguese is about 4.0–4.1% and Indonesian 1.0%
  **[secondary]** https://webiano.digital/english-still-runs-the-web-but-the-internet-is-speaking-more-languages/.
- Internet users by language (InternetWorldStats, dated 2020): English 25.9%, Chinese 19.4%, Spanish 7.9%, Arabic
  5.2% **[secondary]** https://en.wikipedia.org/wiki/Languages_used_on_the_Internet. Indonesia had about 230M
  internet users at the end of 2025 **[secondary]**
  https://webiano.digital/english-still-runs-the-web-but-the-internet-is-speaking-more-languages/.
- Localization vendors rank Spanish (LatAm and Spain) and Portuguese (Brazil) first for consumer-app ROI, then
  French, German, Japanese and Korean **[secondary, vendor]** https://mwm.ai/glossary/app-localization. A
  personality-assessment company's rollout started with Spanish and Portuguese **[secondary]**
  https://deepersignals.com/blog/the-core-drivers-is-coming-to-a-country-near-you.

---

## Recommendations for Mizaj

### A. Payment stack for international sales from Pakistan

Owner action. Claude must not sign up on the owner's behalf; these are applications for Faaiz to submit.

1. **Keep Safepay for PKR inside Pakistan.** It is unchanged; the local rail is covered in research file 03.
2. **Day-one international rail: Gumroad** (MoR).
   - Why:
     - It is the only MoR whose policy explicitly allows astrology, palm-style and divination reports "for
       insight, reflection or entertainment".
     - Pakistan is in its Stripe cross-border payout list (PKR to a local bank).
     - It has built-in PPP regional pricing.
     - Approval is fast.
   - Cost: 10% + 50¢, possibly plus card processing.
   - Use it permanently for the palm reading and any "for fun" products.
   - Integrate through Gumroad's checkout and webhooks.
3. **Apply in parallel to Paddle** for the core catalogue: personality report, Mizaj Milan, Career Compass sold to
   adults/parents, and a bundle without palm.
   - Why: about 5% + 50¢, USD payouts by Payoneer or wire, and the strongest MoR.
   - Conditions: frame Unani content as traditional lifestyle/culture with the existing disclaimer (Paddle bans
     medical advice), and leave palm/astrology out of the Paddle catalogue.
   - Once approved, move core-report volume to Paddle.
4. **Second choice if Paddle declines: Polar.**
   - Pakistan payouts are official, it accepts individuals, and it is API-first.
   - The same pseudo-science and medical bans apply.
   - It **bans products "intended for, or advertised towards minors"**, so Career Compass must not be sold to
     students there.
5. **Don't build on Lemon Squeezy as primary.** It works today, but its future is the Stripe Managed Payments
   migration, and Managed Payments doesn't support Pakistan.
6. **Skip for now:** Stripe Atlas/US LLC (revisit above about $3–5k/month international revenue) **[estimate]**,
   2Checkout, FastSpring, Payoneer Checkout (not an MoR), Dodo, PayPal and Wise (unavailable).
7. **Payouts and tax:**
   - Receive USD where possible: Payoneer for Paddle; a USD/FCY account for Stripe-based payouts.
   - Register with PSEB (needs an SECP company or registered firm plus NTN) for the 0.25% final tax.
   - Confirm with an accountant that the regime continues past June 2026.
8. **Refund policy:** EU/UK buyers have a 14-day withdrawal right, and a personality report counts as a service.
   Align the international refund wording with the chosen MoR's buyer terms. The Pakistan 7-day promise can stay.

### B. USD price points (one-time, no subscriptions) [estimate, to A/B test]

| Product | Now | Recommended global (Tier 1: US/UK/EU/Gulf/AU/CA) | Rationale |
| --- | --- | --- | --- |
| Palm reading (for fun, Gumroad only) | $5 | $5 | Impulse add-on; the 50¢ fixed fee makes lower prices inefficient |
| Full Mizaj Report | $9 | **$12** (test $9 vs $14) | Below 16Personalities ($29) and Truity ($19–35); above automated astrology reports |
| Career Compass | $14 | **$15** | Same band as competitors' single reports |
| Mizaj Milan couple report | $15 | **$19** (covers two people) | Automated synastry $7–16, written $22–55; ours combines personality and temperament |
| Complete bundle | $24 | **$29** | Anchors against a 16Personalities suite ($29) |

- Tier 2 (Philippines, Malaysia, Indonesia, Brazil, Turkey): about 40–50% off via PPP.
- Tier 3 (Pakistan, India, Bangladesh): local PKR pricing via Safepay, or about 60% PPP off on Gumroad.
- Keep the "one-time, no subscription, no trial" promise in all ad copy as a differentiator.

### C. Top 5 target markets [estimate, ranked]

1. **Pakistan plus the South Asian diaspora (UK, US, Canada, Gulf).**
   - The existing content (rishta, Unani, careers) fits without rework.
   - Pakistan CPMs are the cheapest seen ($0.60–2.20).
   - The diaspora pays in GBP/USD/AED, and Tier-1 CPMs ($11–16) can be targeted narrowly.
2. **Philippines.**
   - English-first, so no localization is needed.
   - Cheap reach: Meta about $3.50, TikTok $1–2.
   - Personality interest is assumed, not measured, so test before scaling.
3. **UAE, then Saudi Arabia.**
   - "Mizaj" is a native Arabic word, and the temperament tradition goes back to Ibn Sina.
   - High purchasing power.
   - UAE CPM about $6.50; Saudi $4–12, with Ramadan spikes.
   - English works in the UAE; Saudi needs Arabic.
4. **Malaysia (then Indonesia).**
   - High English use and documented Gen Z interest in personality types.
   - CPM about $4.80–5.40.
   - Indonesia is cheaper ($1.80–2.80) with 230M internet users, but needs Bahasa and has low ARPU.
5. **Brazil, once Portuguese is ready.**
   - A top-5 country for 16Personalities traffic.
   - Instagram CPM $2.40–5.60; TikTok $2–4.

Watch-list:
- Turkey: *mizaç* is the native word and CPMs are cheap, but there is no demand data.
- India: cheapest CPM ($1.36) and *mizaaj* is an everyday word, but a Pakistan-origin brand carries brand risk
  there.
- Japan and Korea: the biggest typing cultures, but saturated and language-heavy.
- Broad US/UK: expensive; use for retargeting only.

### D. Domain

- Make **getmizaj.com** the international home. It was available at $16 on 28 Oct 2026, it is a .com, and it reads
  as a CTA ("Get your Mizaj").
- Register **mymizaj.com** defensively.
- Keep **mizaj.pk** as the Pakistan storefront (PKR, Safepay, Urdu), with hreflang links between the two.
- mizaj.com, .app, .co and .me are all taken. The owner could enquire about buying mizaj.com or mizaj.app; the price
  is unknown.
- Avoid "trymizaj" (it implies a trial).
- Fix the domain before the MoR applications, because reviewers check that the site matches the account.

### E. First 3 languages after English [estimate]

1. **Arabic.**
   - Strongest brand fit: the word is native, and Ibn Sina's temperament heritage carries over.
   - Gulf purchasing power.
   - The rishta/nikah framing transfers.
   - Cost: RTL layout work.
2. **Spanish.**
   - The largest non-English web language: 6.0% of content and about 8% of users.
   - Vendors rank it the top ROI language.
   - Typing is called "the horoscope of Gen Z" in Mexico.
3. **Portuguese (Brazil).**
   - Proven personality-test demand (16Personalities top-5 country).
   - Cheap reach.
   - Second on vendor ROI lists.

Next wave: Turkish (*mizaç*), then Indonesian. Urdu stays on mizaj.pk for the home market. Lesson from
16Personalities: its biggest market is a non-English one (Japan), so localization, not English alone, drives scale.
