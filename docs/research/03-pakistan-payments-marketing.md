# mizaj.pk: Pakistan payments, pricing and marketing research

Prepared 28 Oct 2026 for the mizaj.pk relaunch (low-priced digital self-discovery reports, PKR 300–2,500, plus diaspora sales in USD/GBP).

## Read this first: how this was researched, and its limits

- **Method:** About 60 WebSearch queries, standard mode with extended mode where results were thin. Every fact below comes from a search-result summary of the cited page. I could not read the full pages.
- **WebFetch was blocked.** The session's network policy rejected every host I tried: safepay.helpscoutdocs.com, xstak.com and propakistani.pk. Following the tool's guidance, I stopped trying further hosts. To fetch primary pages, those domains need to be allowed in the session's network settings.
- **The search budget ran out partway through.** The limit is 200 searches per turn, shared across agents. That left sections 2 (Stripe Atlas, Paddle's and Lemon Squeezy's Pakistan eligibility), 6 (legal) and 7 (WhatsApp, email and SMS) only partly researched. Where I add context from background knowledge, it is labelled **[UNVERIFIED – background knowledge]** and has no source URL. Treat it as a to-do to verify, not as a fact.
- **Labels:** "Third-party" means a review, aggregator or competitor site, not the provider. "Estimate" means my own calculation or judgement.
- **Exchange-rate assumption:** about PKR 280 per USD. This rate is quoted in a 2026 Pakistan TikTok-ads guide (https://www.atnrco.com/post/tiktok-marketing-in-pakistan). I did not verify it against SBP. All USD↔PKR conversions below are estimates at that rate.

---

## 1. Payment gateways for a small online seller in Pakistan

### 1.0 Context that drives the choice

- In FY2024-25, about 684 million e-commerce transactions went through bank accounts or digital wallets, against about 52 million through debit or credit cards. Accounts and wallets were 93% of online purchases, up from 87% in FY24. Source: SBP Annual Payment Systems Review FY25, released 3 Nov 2025 — https://www.sbp.org.pk/assets/document/publications/Annual-Payment-Systems-Review-FY25.pdf ; https://www.sbp.org.pk/press/2025/Pr-03-Nov-2025.pdf
- **Implication (estimate):** For a PKR 300–2,500 digital product, wallets (JazzCash, Easypaisa) and Raast matter more than cards. Cards matter mainly for the diaspora and for premium urban buyers.
- SBP directed banks and other regulated entities to enable Raast P2M (person-to-merchant) payments in e-commerce by March 2025, either directly or through SBP-regulated EMIs, PSOs or PSPs. Source: ProPakistani, 29 Nov 2024 — https://propakistani.pk/2024/11/29/sbp-orders-to-enable-raast-payments-in-online-shopping-stores/amp/ ; Profit — https://profit.pakistantoday.com.pk/?p=158734
- A final withholding tax of 0.25%–2% on gross receipts from digitally ordered goods and services has applied since July 2025. Payment intermediaries collect it. Source: Simpaisa blog, 23 Jun 2026 (vendor) — https://www.simpaisa.com/blogs/how-to-set-up-online-payments-for-a-new-pakistan-e-commerce-store
- Typical onboarding package across gateways: NTN, business bank account, KYC documents and a live store URL. "Most reputable gateways respond within 2–5 business days." Source: Simpaisa, 23 Jun 2026 (vendor) — same URL as above.
- Policies a gateway expects on the website: Terms & Conditions, Privacy Policy, Service Policy, Shipping Policy, and a Refund, Return or Cancellation Policy. Source: PayFast partner guide, third-party Scribd upload — https://www.scribd.com/document/890936512/Partner-Guide-PayFast
- An older SBP circular on internet merchant accounts requires the merchant's business to be permissible under Pakistani law, with a registered place of business in Pakistan. Source: https://www.sbp.org.pk/epd/2000/c6.htm

### 1.1 Comparison table

The cells summarise the detailed notes in 1.2–1.10. "n/f" means not found in this research.

| Provider | Methods | Setup fee | Transaction fee | Settlement | Docs (sole prop) | API / webhooks / sandbox | Approval time |
|---|---|---|---|---|---|---|---|
| **Safepay** | Cards (local and intl), wallets, bank accounts, Raast (Shopify Raast app) | None per a 2026 review | Conflicting. Official help centre: 2.5% flat incl. taxes. 2026 review: cards 2.9% + Rs30; intl +0.3%; wallets and Raast 1.5%; excl. tax | T+1 to T+3 (third-party) | CNIC (front and back), bank account in proprietor's name, account-maintenance certificate; possible D&B on-site check | Yes. Official Node and .NET SDKs, sandbox env, webhooks in dashboard | n/f |
| **PayFast (APPS)** | Raast QR, Raast RTP, bank accounts, wallets, local and intl cards | Conflicting: PKR 20,000 (third-party citing partner guide) vs none | **Official:** Raast QR 0.60%, Raast RTP 0.95%, accounts/wallets 2.20%, local cards 2.95%, intl cards 3.50%, excl. service tax | T+1 to T+2 (third-party) | CNIC, business registration (e.g. NTN), utility bill, account-maintenance certificate | Sandbox exists; server-to-server callbacks (third-party) | n/f |
| **JazzCash gateway** | JazzCash wallet, voucher (OTC), debit/credit cards | n/f | 2.32% (Mobilink Bank schedule of charges) | n/f | Merchant account in your own name (vendor claim) | API with IPN; docs behind NDA; HTTPS needed for IPN (vendor claim) | n/f |
| **Easypaisa / Easypay** | Easypaisa wallet, OTC; cards (historically) | Free in 2015 (outdated) | No current published rate. 2015: 1% wallet, 2% OTC, 3% card (outdated) | Wallet: daily and instant. OTC: 7 working days | Online application, KYC and due diligence, live website or app | REST APIs; plugins for WooCommerce, OpenCart, Magento, PrestaShop | n/f |
| **Paymob PK** | Cards and wallets via API, POS, Tap-on-Phone | n/f | n/f (no published PK rate card) | n/f | n/f | API (marketing claim) | Licence status: SBP in-principle approval, Nov 2024 |
| **XPay (XStak)** | Cards, wallets (dynamic routing) | "No setup costs" (vendor) | Not published; third-party estimate 1.5%–2.5% | n/f | n/f | Shopify apps, custom web and app integration | n/f |
| **UBL e-commerce gateway** | Cards (3DS), settles to a UBL account | PKR 40,000 + PKR 50,000 a year (Jan 2024 third-party table) | 3.5% (same table) | To UBL account | Business account at UBL | n/f | n/f |
| **HBL IPG / HBLPay** | Cards incl. PayPak and UnionPay | Up to PKR 100,000 + up to PKR 100,000 a year | MDR set by average ticket size | n/f | Registered business, HBL company account, applicant aged 25 or over | Free Magento and WooCommerce plugins | 10–15 working days from the legal stage |
| **Meezan** | All major card schemes | n/f | n/f | n/f | n/f | n/f | n/f |
| **Raast P2M (direct via bank)** | Raast QR, Raast ID, Request-to-Pay from any bank or wallet app | n/f | 0% MDR on Raast QR (Bank Alfalah); MSPs may charge for dynamic QR, webhooks and links | T+1 (Bank Alfalah) | Business bank account | Only through an MSP or gateway | n/f |
| **NayaPay Business (Arc)** | Cards (online and POS), incoming transfers | n/f | Online cards 2.99% + Rs30; POS 2% (older help article) | To revenue account | Registered businesses of many legal types | Invoices and receipts; API n/f | n/f |
| **SadaPay** | Raast P2M (customers pay nothing) | n/f | n/f | n/f | n/f | n/f | n/f |

### 1.2 Safepay

- **Fees, official help centre:** a flat 2.5% per successful local PKR transaction, inclusive of taxes; "no hidden fees, no yearly fees and no minimum balance". The article notes it has been updated and points to a newer fee breakdown, which I could not retrieve. Sources: https://safepay.helpscoutdocs.com/article/120-how-much-does-safepay-charge ; https://safepay.helpscoutdocs.com/article/131-safepay-fee-breakdown
- **Fees, 2026 third-party review:** no setup or monthly fees. Domestic cards cost 2.9% + Rs30 per successful charge; international cards add 0.3%; wallet and Raast transactions cost 1.5%. A card dispute costs Rs3,000 and an optional routing service Rs15,000 a month. Rates exclude taxes. Source: PaymentPop, "Safepay Reviews (2026)" — https://paymentpop.com/merchant-accounts/safepay-customer-reviews/
- **Older rates, for context only:** 3.3% + Rs30 (Dawn; KrASIA). Sources: https://www.dawn.com/news/amp/1542800 ; https://kr-asia.com/pakistani-fintech-firm-safepay-receives-y-combinators-backing
- **Documents for a sole proprietor:** a scan of the original, valid CNIC (front and back) of the proprietor and of any authorised signatory. The bank account must be in the proprietor's name, with a bank account maintenance certificate. Without these documents Safepay cannot let you accept live payments. Safepay may run an on-site check through Dun & Bradstreet Pakistan covering company profile, CNIC and NTN. Sources: https://safepay.helpscoutdocs.com/article/152-list-of-documents-you-need-to-provide-safepay ; https://safepay.helpscoutdocs.com/article/83-what-bank-account-to-link-to-safepay ; https://safepay.helpscoutdocs.com/article/121-onsite-merchant-verification
- **Settlement:** funds go to the linked bank account. The dashboard shows each transaction's expected timeline, and settlement reports break settlement down per transaction. No day-count is published. Source: https://safepay.helpscoutdocs.com/article/94-how-settlement-works . Third-party guides say T+2 to T+3 (one) and T+1 to T+3 (another). Sources: https://www.buzzinteractive.co/blog/payment-gateways-in-pakistan ; https://www.photonpay.com/hk/blog/article/payment-gateway-in-pakistan?lang=en
- **API, webhooks and sandbox:** the official Node SDK `@sfpy/node-sdk` takes an environment setting (example: `'sandbox'`) and has a `webhooks` option on checkout. Source: https://www.npmjs.com/package/@sfpy/node-sdk . Per the official .NET library, webhook subscriptions are managed from the Webhooks tab in the dashboard's Developer section. Source: https://packages.nuget.org/packages/SFPY.net . Developer docs are at developers.getsafepay.com (referenced at https://tessl.io/registry/skills/github/membranedev/application-skills/safepay ).
- **Raast:** Safepay's Shopify app is described as Pakistan's first Shopify payment app for Raast. Source: https://apps.shopify.com/safepay-alternate-payments
- **Status:** described as an SBP-licensed PSO/PSP backed by Y Combinator and Stripe, with more than 200,000 unique customers. Source: third-party summaries in https://paymentpop.com/merchant-accounts/safepay-customer-reviews/ and https://kr-asia.com/pakistani-fintech-firm-safepay-receives-y-combinators-backing
- **Approval time:** not found.

### 1.3 PayFast (Avanza Premier Payment Services, APPS)

- **Official pricing, excluding service tax:** RAAST QR 0.60%; RAAST RTP 0.95%; bank accounts and wallets 2.20%; local cards 2.95%; international cards 3.50%. Source: https://gopayfast.com/pricing/
- **Setup fee is contested:** a third-party review cites a PKR 20,000 setup charge from the partner guide; another says the pricing page shows no setup or maintenance charges. Sources: https://rapidgateway.pk/resources/payfast-pakistan-review (competitor site) ; https://www.smart.houseofpakistan.com/payment-gateway-in-pakistan/
- **Documents for a sole proprietor:** valid CNIC, a business registration document (e.g. NTN), a business address document (utility bill), and an account maintenance certificate. Also needed: business registration with local authorities and a Pakistani business bank account. Source: PayFast partner guide on Scribd (third-party upload) — https://www.scribd.com/document/890936512/Partner-Guide-PayFast ; https://www.scribd.com/document/830160195/Partner-Guide99
- **Settlement:** T+1 to T+2 per third-party reviews. Source: https://rapidgateway.pk/resources/payfast-pakistan-review
- **Sandbox and webhooks:** integrators build against the PayFast sandbox while the merchant account is pending. Payments are confirmed by a server-to-server callback, which is signature-verified. Sources (vendor and community): https://ecosire.com/de/apps/woocommerce/payfast-pakistan-gateway ; https://pub.dev/packages/payfast_flutter/versions/0.0.5
- **Licence:** in May 2021 PayFast became the first Pakistani payment gateway to get a commercial licence from SBP. Source: https://propakistani.pk/2021/05/25/payfast-becomes-first-pakistani-payment-gateway-to-get-commercial-license-from-sbp/ . A competitor site says PayFast was the first licensed gateway live on Raast P2M, in May 2024; treat that cautiously. Source: https://rapidgateway.pk/resources/payfast-pakistan-review
- **Shopify app:** fees vary by merchant volume and are billed in USD. Source: https://apps.shopify.com/payfast-gateway-app

### 1.4 JazzCash merchant / online payment gateway

- **MDR:** 2.32% for "Payment Acceptance Service Charges via Online Payment Gateway (Merchants)", covering mobile account, voucher, and credit or debit card. Source: Mobilink Bank schedule of charges — https://mobilinkbank.com/assets/documents/BB-SOC-Apr-June-2024-Q2-Final.pdf ; Q1 2026 schedule — https://mobilinkbank.com/assets/documents/SOC_Q1_2026.pdf
- **Refunds:** "If merchant attempts refund within the same day, merchant will not be charged the MDR." Source: https://mobilinkbank.com/assets/documents/SOC_Q1_2026.pdf
- **Integration (vendor claims):** you need a verified merchant account in your own name, with Merchant ID, API password and Integrity Salt issued at onboarding. The site must run over HTTPS to receive IPN. Integration docs sit behind a merchant account and NDA, and there is no public test account. Sources: https://docs.ecosire.com/odoo-modules/jazzcash-gateway ; https://ecosire.com/apps/shopify/payment-jazzcash
- **Scale:** 29.2 million monthly active users and more than 60 million registered users in Q1 2026 (Jazz). Sources: https://jazz.com.pk/media-center/detail/jazzworld-revenue-grows-23-to-over-pkr-269-billion-in-h1-2026 ; https://pkrevenue.com/jazzworld-revenue-growth-q1-2026-pakistan/
- **Setup fee, settlement and approval time:** not found.

### 1.5 Easypaisa merchant / Easypay

- **Eligibility:** any business or entity with a live website or mobile app selling products or services. Registration is through the Easypaisa Merchant Registration Portal.
- **Process:** online application with documents, then KYC and due diligence, integration, and go-live.
- **Settlement:** Easypaisa mobile account, daily and instant; OTC, 7 working days. A merchant portal shows transactions, settlements and reversals.
- Source for the three points above: https://easypaisa.com.pk/?p=16718
- **APIs:** REST APIs for OTC and mobile-account initiation and status inquiry. Source: third-party Scribd copy — https://www.scribd.com/document/512029435/Easypaisa-REST-APIs-without-RSA-Integration-Guide
- **Fees:** no current published schedule found. In 2015 setup was free, with no annual charge, and fees of 1% (mobile account), 2% (outlet) and 3% (cards). Those rates are outdated. Source: https://propakistani.pk/2015/07/27/online-payments-accept-credit-debit-card-payments-in-pakistan-with-easypay/
- **Scale:** more than 22 million monthly active users and about 60 million registered users in 2026. Sources: https://propakistani.pk/2026/05/08/easypaisa-bank-delivers-record-q1-2026-results-with-profit-before-tax-of-pkr-3-66-bn/amp/ ; https://www.phoneworld.com.pk/easypaisa-digital-bank-hy2026-results-profit-8-26-billion/

### 1.6 Paymob Pakistan

- Paymob announced its Pakistan entry in April 2022 with online, POS and Tap-on-Phone products. Source: https://www.dailynewsegypt.com/2022/04/15/paymob-announces-its-market-entry-to-pakistan/
- In Nov 2024 SBP gave in-principle approval to Accept Technologies (PayMob) as an EMI and PSP, with six months to get ready before applying for pilot operations. Whether pilot or commercial permission followed was not found. Source: https://profit.pakistantoday.com.pk/2024/11/05/sbp-approves-pilot-operations-for-digital-payment-providers-amidst-rapid-growth-in-e-money-usage
- No published Pakistan fees, settlement terms or document list found. **Not recommended for launch until its licence status and pricing are confirmed.**

### 1.7 XPay (XStak)

- The vendor says it uses usage-based pricing with "no setup costs or hidden fees", but no rate is published. Sources: https://www.xstak.com/blog/paypal-alternative ; https://xstak.com/xpay-pricing
- A third-party comparison lists XPay at a 1.5%–2.5% merchant fee and calls it "XPay by PostEx", which conflicts with the XStak attribution. Sources: https://www.indiehackers.com/product/xpay-pakistan ; https://digiteazy.com/payment-gateway-pakistan/
- XStak claims dynamic routing saves merchants up to 30% on fees (vendor claim). Source: https://www.xstak.com/blog/dynamic-payment-routing
- Shopify apps exist. A non-Shopify-Payments gateway on the Basic plan adds Shopify's 2% third-party fee. Sources: https://apps.shopify.com/xpay ; https://loop2tech.com/blog/shopify-payment-gateway-pakistan

### 1.8 Bank gateways: UBL, HBL, Meezan

- **UBL:** running since 2013; PCI DSS certified, 3-D Secure, fraud screening; settles to a UBL account. Source: https://ubldigital.com/UBL-Digital/UBL-Netbanking/e-commerce-payment-gateway . A Jan 2024 third-party table lists UBL at PKR 40,000 setup, PKR 50,000 a year and 3.5% MDR, with Alfalah, MCB and HBL at 2.5%–2.8% MDR. Source: https://www.xstak.com/blog/payment-gateways-in-pakistan
- **HBL:** requires a registered business in Pakistan, a company bank account at HBL, and an applicant aged at least 25. The MDR is set by the expected average ticket. Setup is up to PKR 100,000 one-time and maintenance up to PKR 100,000 a year. Documentation takes 10–15 working days from the legal stage. Free Magento and WooCommerce plugins; UnionPay supported; contact hbl.ipg@hbl.com. Sources: https://www.hbl.com/assets/documents/HBL_IPG_FAQs.pdf ; https://www.hbl.com/assets/documents/HBL%E2%80%99s_Ecommerce_Suite.pdf ; https://wordpress.org/plugins/hblpay-payment-gateway-for-woocommerce/
- **Meezan:** its gateway accepts all major card schemes, and it announced an Islamic e-commerce gateway in 2022. No onboarding criteria or fees found. Sources: https://www.meezanbank.com/?p=163341 ; https://propakistani.pk/2022/02/01/meezan-bank-set-to-launch-pakistans-first-islamic-e-commerce-payment-gateway/amp/
- **Verdict (estimate):** bank gateways have high fixed costs, need a company or registered-business account, and take weeks. They are unsuitable for a PKR 300–2,500 launch.

### 1.9 Raast P2M (Raast QR, Raast ID, Request-to-Pay)

- SBP launched Raast P2M in Dec 2023. Source: https://www.sbp.org.pk/press/2023/Pr-06-Dec-2023.pdf ; https://propakistani.pk/2023/12/06/sbp-rolls-out-much-awaited-raast-p2m-service/
- **Merchant cost:** Bank Alfalah says the MDR on the Raast scheme is 0%: "merchants will not be charged any fees" for Raast QR. Settlement is T+1. Merchant service providers may charge for add-ons such as dynamic QR, webhooks, payment links, reconciliation and faster settlement. Sources: https://www.bankalfalah.com/personal-banking/raast-p2m-qr/ ; https://bankalfalah.com/business-banking/retail-payment-solution/raast-p2m-qr/
- **Customer cost:** none for paying merchants via Raast P2M. Sources: SBP P2M instructions as summarised in https://www.settlix.net/blog/what-is-raast-qr/ ; SadaPay — https://sadapay.pk/blogs/raast-qr-payments
- **Subsidy:** a Rs3.5 billion subsidy (Sept 2025 to June 2026, described as part of a three-year programme) reimburses merchants 0.5% of each P2M QR transaction or Rs100, whichever is lower. The search summary did not say which of these two articles carried it: https://tribune.com.pk/story/2570322/sbp-to-use-raast-for-govt-payments ; https://www.brecorder.com/news/amp/40385604 . **Whether it was extended past June 2026 is not verified.**
- **Regulatory cap:** in 2023 SBP reportedly capped the P2M MDR at 1%, not to be passed on to customers. Source: https://profit.pakistantoday.com.pk/2023/11/26/can-raast-do-for-pakistan-what-upi-did-for-india . Through a gateway, PayFast charges 0.60% for Raast QR and 0.95% for RTP: https://gopayfast.com/pricing/
- **Implication (estimate):** Raast is the cheapest rail. Use it through a gateway so you get webhooks and automatic order fulfilment. A static Raast QR or Raast ID on your own bank account costs nothing, but you have to reconcile payments by hand.

### 1.10 NayaPay and SadaPay business options

- **NayaPay Business (Arc):** supports registered businesses of many legal structures. Source: https://help.nayapay.com/article/60-what-type-of-business-entities-are-supported-by-nayapay-business . Card acceptance costs 2% on POS and 2.99% + Rs30 online, per an older help article. Source: https://help.nayapay.com/article/116-how-much-does-it-cost-to-accept-payments . A revenue account receives online-sales funds, with default limits of PKR 2,000,000 incoming and PKR 2,000,000 outgoing a month. Source: https://help.nayapay.com/article/154-can-i-receive-money-against-my-online-sales-in-my-nayapay-arc-account . Transfers out are free up to Rs25,000 a month in aggregate. Source: https://help.nayapay.com/article/120-will-i-be-charged-for-withdrawing-funds-from-my-account
- **SadaPay:** no current merchant or business product or fee schedule found. Customers pay nothing for Raast P2M QR. Source: https://sadapay.pk/blogs/raast-qr-payments . Merchant accounts for freelancers were announced back in 2020. Source: https://www.mastercard.com/news/eemea/en/newsroom/press-releases/en/2020/may/sadapay-and-mastercard-collaborate-to-simplify-digital-payments-in-pakistan
- **Limitation (estimate):** NayaPay's PKR 2 million a month incoming cap and the Rs30 fixed card fee make it a fallback, not a primary gateway.

### 1.11 What the fees mean at mizaj.pk price points (estimate)

Fees are per transaction in PKR, before tax unless stated. These are my calculations from the rates cited above.

| Rail / provider | PKR 300 sale | PKR 999 sale | PKR 2,500 sale |
|---|---|---|---|
| Safepay card at 2.9% + Rs30 (review rate) | 38.7 (12.9%) | 59.0 (5.9%) | 102.5 (4.1%) |
| Safepay wallet or Raast at 1.5% (review rate) | 4.5 | 15.0 | 37.5 |
| Safepay at 2.5% flat incl. tax (help centre) | 7.5 | 25.0 | 62.5 |
| PayFast Raast QR, 0.60% | 1.8 | 6.0 | 15.0 |
| PayFast wallet or account, 2.20% | 6.6 | 22.0 | 55.0 |
| PayFast local card, 2.95% | 8.9 | 29.5 | 73.8 |
| JazzCash gateway, 2.32% | 7.0 | 23.2 | 58.0 |
| NayaPay online card at 2.99% + Rs30 | 39.0 (13%) | 59.9 | 104.8 |

**Key takeaway (estimate):** a fixed Rs30 per card transaction makes a PKR 300 card sale uneconomic. Push low-ticket items to Raast and wallets, or bundle them up to PKR 500 or more.

### 1.12 Recommendation for section 1

- **Fastest launch: Safepay.**
  - Public SDKs with a sandbox environment and dashboard webhooks.
  - Cards, wallets and Raast in one integration.
  - An explicit sole-proprietor document list (CNIC plus a bank account and its maintenance certificate).
  - Before signing, get the current fee schedule in writing: does the Rs30 fixed card fee still apply, and are rates tax-inclusive?
  - **PayFast is a close alternative.** Its pricing is published and percentage-only, and it has the cheapest gateway Raast rates (0.60% QR). It needs NTN and a utility bill as well.
- **Best for scale: PayFast as the primary gateway, with a Raast-first checkout.** Raast QR at 0.60% and wallets at 2.20% are the lowest published gateway rates found. Once volume justifies it, add a direct JazzCash merchant account (2.32%) or Easypaisa (daily and instant settlement), or negotiate custom MDRs.
- **Avoid at launch:** bank gateways (high setup and annual fees, weeks to onboard), Paymob (licence and pricing unconfirmed), and SadaPay (no business product found).

---

## 2. Cross-border: accepting USD/GBP from the diaspora

- **Simplest route (estimate):** accept international cards through the local gateway and settle in PKR.
  - PayFast international cards cost 3.50%: https://gopayfast.com/pricing/
  - Safepay international cards add 0.3% per a 2026 review: https://paymentpop.com/merchant-accounts/safepay-customer-reviews/
  - This needs no new entity. The checkout shows PKR, and the cardholder's bank converts.
- **Payoneer:**
  - Receiving card payments costs about 3.99% plus a fixed fee; receiving by bank transfer is free or up to 1%. The Payoneer guide is undated. Source: https://www.payoneer.com/resources/country-guides/paypal-to-payoneer/
  - In May 2025 Payoneer added a 3% fee for Pakistani users withdrawing to non-local-currency bank accounts (USD, EUR, GBP). Source: Profit, 3 May 2025 — https://profit.pakistantoday.com.pk/2025/05/03/payoneer-slaps-3-withdrawal-fee-on-pakistani-users-sparking-backlash-among-freelancers ; https://english.aaj.tv/news/amp/330415412
  - PKR withdrawals carry a conversion fee of about 2% (varies by bank). Source: https://www.payoneer.com/resources/country-guides/paypal-to-payoneer/
- **Paddle (merchant of record):**
  - Pays out via Payoneer in USD only, and the seller bears Payoneer's fees.
  - Bank payouts in the destination's local currency carry no Paddle fee; some countries incur a $15 SWIFT fee.
  - Payouts arrive within about 3 working days.
  - Sources: https://www.paddle.com/help/manage/get-paid/when-and-how-do-i-get-paid ; https://paddle.com/help/manage/get-paid/is-there-a-fee-taken-for-payouts
  - **Pakistan's eligibility as a seller country was not verified.**
- **Lemon Squeezy (merchant of record):**
  - Headline fee is 5% + 50¢: https://dodopayments.com/blogs/lemonsqueezy-review
  - Pays out by bank or PayPal twice a month: https://docs.lemonsqueezy.com/help/getting-started/getting-paid
  - A secondary source says non-US sellers pay 1% per payout, the minimum is $50, and Pakistan is on the bank-payout list. The official list excerpt I saw was cut off, so this is unverified. Source: https://www.lilachbullock.com/?p=148746 ; official list — https://docs.lemonsqueezy.com/help/getting-started/supported-countries
  - PayPal is not available in Pakistan, so the PayPal payout option does not help. Source: same secondary article.
  - A possible 2026 migration to Stripe Managed Payments is unconfirmed.
- **Gumroad:**
  - Pays out only to a local bank account in local currency: https://gumroad.com/help/article/13-getting-paid
  - Secondary sources say Pakistan is on the bank-deposit table with PKR payouts and a $100 minimum, and that Payoneer and Wise are not accepted. Unverified. Sources: https://www.lilachbullock.com/?p=148734 ; https://quasa.io/ur/media/pakstan-my-gumroad-payout-pkr-mmkn-mgr-r-frokht-ky-asl-koty-zyad
  - Gumroad's fee rate was not verified in this session.
- **Stripe / Stripe Atlas:** not researched; the search budget ran out. **[UNVERIFIED – background knowledge]** Stripe does not support accounts for Pakistan-based businesses. Atlas means forming a US entity (Delaware C-corp or LLC), which brings US tax filings and ongoing costs. That is heavy for a PKR 300–2,500 product line. Verify before acting.
- **Recommendation (estimate):**
  - **Phase 1:** take diaspora card payments through the PK gateway's international-card rail (3.0%–3.5%), with prices shown in PKR and an approximate USD/GBP label.
  - **Phase 2,** if diaspora revenue is material (for example above about USD 500 a month): add a merchant of record (Lemon Squeezy, Paddle or Gumroad) for real USD/GBP pricing and VAT handling. Do this only after confirming Pakistan payout eligibility in the provider's own onboarding. Budget an all-in cost of about 6%–12% per small sale (my estimate from the 5% + 50¢ headline on a $9 sale, plus payout and FX costs).

---

## 3. Digital consumer benchmarks

### 3.1 What Pakistanis pay for digital subscriptions

| Product | PKR price | Date / status | Source |
|---|---|---|---|
| Netflix Mobile | 250 / month | 2026 guide | https://www.nsave.com/pakistan/2026-world-cup-streaming-costs |
| Netflix Basic / Standard / Premium | 450 / 800 / 1,100 a month (tier naming inconsistent across sources) | 2026 guides | https://www.nsave.com/pakistan/2026-world-cup-streaming-costs ; https://www.calendar-uk.co.uk/frequently-asked-questions/how-much-are-netflix-packages-in-pakistan |
| Spotify Premium Individual / Duo | 379 / 519 a month | Official page, current | https://www.spotify.com/pk/premium/ |
| Spotify Premium Student | 199 / month | Official | https://www.spotify.com/pk/student/ |
| YouTube Premium Individual / Family | 479 / 899 a month | Undated ProPakistani page; may be outdated | https://propakistani.pk/?p=700292 |
| YouTube Premium Student | 329 / month | Launch-era, undated | https://www.geo.tv/latest/502806-youtube-premium-and-youtube-music-make-pakistan-debut |
| ChatGPT Go | 1,400 / month | Launched Oct 2025; PKR billing | https://propakistani.pk/2025/10/10/chatgpt-go-brings-cheaper-gpt-5-access-to-pakistan/ ; https://gnnhd.tv/news/51712/lowest-priced-chatgpt-subscription-plan-introduced-in-pakistan |
| ChatGPT Plus / Business / Pro | 5,700 / 8,499 / 49,900 a month | Oct 2025 reports | https://gnnhd.tv/news/51712/lowest-priced-chatgpt-subscription-plan-introduced-in-pakistan |
| Canva Pro | 9,200 / year (about 767 a month, my calculation) | Official PK page; date not shown | https://www.canva.com/ur_pk/pricing/ |

- **Takeaway (estimate):** PKR 199–479 a month is the "impulse" band for mass digital subscriptions, and PKR 1,400 is a premium AI tool. A PKR 300–500 one-off report sits in impulse territory. PKR 1,500–2,500 needs strong perceived value, a gift or couple framing, or a bundle.

### 3.2 Courses and reports

- LUMS Centre for Educational Studies online evening courses are PKR 12,000 (e.g. Nutrition & Wellness) to PKR 28,000 (3-month Mobile App Development); undated. Source: https://lums.edu.pk/node/11222 (and related LUMS CES pages)
- Quality web development courses cost PKR 15,000–80,000 (local training firm's guide). Source: https://www.idtpakistan.pk/blog/best-web-development-course-islamabad
- A creator's Python course was promoted at PKR 8,800, down from PKR 49,000 (single promo). Source: https://t.me/s/codanics/435
- No Pakistan PKR prices were found for personality, astrology or numerology reports. Reference points abroad:
  - US numerology "Personality Decoder" report: $7 (or $29.99 without sign-up). Source: https://www.newswire.com/news/life-pathway-reading-review-2026-looking-for-more-than-a-free-numerology
  - Indian numerology report: ₹499. Source: https://www.smartpuja.com/astrology/numerology-report
  - Pakistan-based Fiverr sellers price astrology and numerology readings up to $50–$100. Sources: https://fiverr.com/qfazeem/use-numerology-to-make-an-80-page-report ; https://fiverr.com/fastdataentry8/do-palmistry-and-numerology

### 3.3 Cards vs wallets

- At FY25 end there were 53.1 million debit cards and 2.2 million credit cards. Source: SBP Annual Payment Systems Review FY25 — https://www.sbp.org.pk/assets/document/publications/Annual-Payment-Systems-Review-FY25.pdf
- 93% of online purchases were paid through accounts or wallets: about 684 million transactions, against about 52 million by card. Same source.
- Retail payments totalled 9.1 billion transactions (PKR 612 trillion) in FY25. Digital channels carried 88% of retail transactions, and e-money wallet app volume and value doubled. Sources: same; https://profit.pakistantoday.com.pk/2025/11/03/sbp-releases-annual-payment-systems-review-for-fy25/
- As of Q3 FY25 there were 22.6 million mobile-banking app users, 5.3 million e-money users and 68.5 million branchless-banking wallet users. Source: https://thefinancialdaily.com/sbp-releases-its-fy-25-third-quarterly-review-of-payment-systems/
- **JazzCash:** 29.2 million monthly active users in Q1 2026 and more than 60 million registered. Sources: https://pkrevenue.com/jazzworld-revenue-growth-q1-2026-pakistan/ ; https://jazz.com.pk/media-center/detail/jazzworld-revenue-grows-23-to-over-pkr-269-billion-in-h1-2026
- **Easypaisa:** more than 22 million monthly active users in 2026 (18.2 million at H1 2025) and about 60 million registered. Sources: https://propakistani.pk/2026/05/08/easypaisa-bank-delivers-record-q1-2026-results-with-profit-before-tax-of-pkr-3-66-bn/amp/ ; https://www.phoneworld.com.pk/easypaisa-digital-bank-hy2026-results-profit-8-26-billion/ ; https://propakistani.pk/2025/08/23/easypaisa-digital-bank-reports-profit-before-tax-of-rs-3-64bn-for-h1-2025/amp/

### 3.4 Cash on delivery share

- ECDB: nearly 94% of online-order transactions were paid by COD in 2022, and 93.9% of online stores offered COD in 2023. Source: https://ecommercedb.com/insights/the-top-categories-for-online-shopping-in-pakistan-fashion-most-popular/4395 ; https://ecommercedb.com/markets/pk/all
- 2025-labelled estimates of 65%–75% (eGrow) and over 70% (Alibaba seller blog) are unsourced. Sources: https://www.egrow.com/en/blog/the-state-of-cod-e-commerce-in-2026-markets-trends-and-opportunities ; https://seller.alibaba.com/businessblogs/how-to-start-an-ecommerce-business-in-pakistan-in-2026-sourcing-compliance--selling-on-alibabacom-px002dd3o
- Budget 2025-26 doubled the withholding sales tax on e-commerce transactions from 1% to 2%. Source: https://www.techjuice.pk/new-tax-imposed-on-online-shopping/
- **Note:** COD is irrelevant for an instant digital report. The relevant fact is the habit of distrusting prepayment, which argues for showing a free preview before payment (estimate).

---

## 4. Social media and internet in Pakistan

### 4.1 Internet, mobile and smartphones

- **Internet users:** 117 million (45.6% of the population). This is DataReportal Digital 2026 as reported secondhand. Sources: https://www.phoneworld.com.pk/influencer-marketing-pakistan-performance-deals-creators-commission/ ; https://salmangul.com/digital-marketing-pakistan/ ; primary report: https://datareportal.com/reports/digital-2026-pakistan
- **Unconnected population:** Pakistan has the second-largest offline population, almost 140 million people, after India. Source: https://datareportal.com/reports/digital-2026-six-billion-internet-users
- **Mobile subscriptions:** about 210 million, with teledensity above 83% and 161.7 million mobile broadband subscribers. Told to the National Assembly, 23 Oct 2026. Sources: https://radio.gov.pk/23-10-2026/pakistans-mobile-subscribers-reach-210-million-na-told ; https://www.arabnews.pk/pakistan/pakistans-mobile-subscriptions-reach-210-million-as-broadband-use-expands-3005039
- **Broadband:** about 162 million mobile broadband and 3.8 million fixed broadband subscribers (Aug 2026 data). Source: https://en.wikipedia.org/wiki/Internet_in_Pakistan
- **Smartphones:** smartphone usage is 71.6%, per the Economic Survey 2025-26. Source: https://www.phoneworld.com.pk/pakistan-smartphone-usage-71-percent-economic-survey-2026/ . A conflicting, poorly sourced figure says 48% of active devices are smartphones. Source: https://meatechwatch.com/?p=32484

### 4.2 Platforms

Ad reach and audience counts are not the same as unique people.

- **Total social media user identities:** 79.9 million (31.2% of the population), Oct 2025. Source: DataReportal via https://www.phoneworld.com.pk/influencer-marketing-pakistan-performance-deals-creators-commission/ ; https://retailnews.asia/pakistan-ad-market-shifts-to-influencers-as-social-media-reaches-80-million-users
- **TikTok:** ad reach of 79.9 million adults aged 18+ (54.6% of adults), per DataReportal Digital 2026. An alternative figure of 66.9 million adults also circulates. Sources: https://marketintelligencetools.com/reports/tiktok-statistics/ ; https://collabscafe.com/blog/state-of-pakistan-creator-economy-2026
- **YouTube:** about 54 million to 55.9 million. Sources: https://www.phoneworld.com.pk/influencer-marketing-pakistan-performance-deals-creators-commission/ ; https://weproms.com/blog/youtube-marketing-pakistan-businesses-2026/
- **Facebook:**
  - DataReportal/Meta ad reach: 49.4 million (2025). Source: https://weproms.com/blog/youtube-marketing-pakistan-businesses-2026/
  - NapoleonCat (Meta audience): 71.2 million in June 2026 and 66.0 million in Sept 2026; 75.4% male. Sources: https://stats.napoleoncat.com/facebook-users-in-pakistan/2026/06/ ; https://stats.napoleoncat.com/facebook-users-in-pakistan/
- **Instagram:** about 22 million (DataReportal, secondhand), or 24.0 million to 25.6 million (NapoleonCat, Mar–Sept 2026). Sources: https://www.phoneworld.com.pk/influencer-marketing-pakistan-performance-deals-creators-commission/ ; https://stats.napoleoncat.com/instagram-users-in-pakistan/
- **WhatsApp:** 93.7 million users in 2025 (Statista model). A vendor blog claims more than 100 million in 2026 and use by about 90% of smartphone users. Sources: https://www.statista.com/recent/statistics/p/154/ ; https://chatdaddy.tech/blog/whatsapp-marketing-pakistan
- **Snapchat:** no 2025–2026 figure found. 2024 estimates conflict: 26.35 million to 35.6 million (31.9 million per Oberlo). A PTA-cited 18.8 million accounts also appears. Sources: https://oberlo.com/statistics/snapchat-users-by-country ; https://www.answeriq.com/snapchat-users/

### 4.3 Age and gender split

- **Facebook:** 25–34 is the largest group (41.1% in Sept 2026; 29.4 million in June 2026). Users are about 75% male. Sources: https://stats.napoleoncat.com/facebook-users-in-pakistan/ ; https://stats.napoleoncat.com/facebook-users-in-pakistan/2026/06/
- **Instagram:** 18–24 is the largest group (42.5%, June 2026). Users are 63.8% male. Source: https://stats.napoleoncat.com/instagram-users-in-pakistan/
- **Implication (estimate):** Instagram and TikTok are where the 18–24 self-discovery audience is, and Instagram has a relatively higher female share. Facebook skews older and male. Female-skewed creatives and placements will cost more to reach women; this is an assumption to test.

### 4.4 Language mix

- A 2026 corpus study of 15,000 posts from Facebook, Instagram, X and WhatsApp groups at ten Pakistani universities found the discourse heavily Urdu–English mixed, written in Roman Urdu spelling. Source: https://journals.usa.edu.pk/sajahs/article/view/9
- Code-switching and code-mixing in Pakistani electronic media rose substantially over 2011–2022. Source: https://escholar.umt.edu.pk/items/63535279-71fc-43fb-8233-d775712fcc25
- Twitter users tend to start inter-sentential switches in English before moving into Urdu (qualitative study). Source: https://ejournal.khazar.org/index.php/kjhss/article/view/8
- **No quantified English/Urdu/Roman-Urdu split was found.** Implication (estimate): write ad copy and result pages in English and Roman Urdu, with Urdu script as an option for older or Facebook audiences. A/B test the variants.

---

## 5. Paid acquisition costs in Pakistan

All the figures in this section come from agency or vendor blogs, not from platform data. Validate them in your own ad accounts.

### 5.1 Meta (Facebook and Instagram)

- **CPM:** quoted ranges are PKR 100–400, PKR 100–600, PKR 100–800 and PKR 280–1,100. In USD, $0.60–$1.80. Sources: https://360socialagency.com/blog/facebook-ads-cost-in-pakistan ; https://www.husbar.com/blog/facebook-ads-cost-pakistan ; https://siffar.com/facebook-ads-costs-in-pakistan-a-comprehensive-guide-for-2025/ ; https://seonextlevel.com/facebook-advertising-cost-in-pakistan/ ; https://www.stackmatix.com/blog/facebook-ads-cpm-by-country-2026
- **CPC:** PKR 5 to 80+ for broad audiences; PKR 140–422 for traffic campaigns (repeated in two sources). Same sources.
- **CPL:**
  - PKR 50–150 for broad offers and PKR 500–2,000+ for high-ticket offers.
  - Broad range PKR 281–845.
  - PKR 150–400 for fashion and food; PKR 800–2,000+ for real estate and education.
  - Same source set; the search summary did not tie each range to a single URL.
- **Starting budgets:** PKR 1,000–3,000 a day, and PKR 50,000–150,000 for a first-month test. Sources: https://siffar.com/facebook-ads-costs-in-pakistan-a-comprehensive-guide-for-2025/ ; https://thedesignsfirm.com/en/blog/facebook-instagram-ads-cost-in-pakistan
- **Global comparison:** a $1.14 average CPC and $11.62 CPM in 2026. Source: https://makometrics.com/blog/facebook-ads-cost-benchmarks

### 5.2 TikTok

- **CPM:**
  - PKR 150–400 (one Pakistan guide).
  - $4–8, or about PKR 1,100–2,250 (an agency analysis at about PKR 280 per USD).
  - A merchant anecdote of PKR 40–80.
  - Sources: https://unboxed.global/social-media-ads-cost-pakistan/ ; https://www.atnrco.com/post/tiktok-marketing-in-pakistan ; https://weproms.com/blog/tiktok-ads-cost-pakistan-2026/ ; https://community.shopify.com/t/tiktok-ads-strategy/646196
- **Minimums:** $20 a day per ad group and $50 a day per campaign, about PKR 5,600 and PKR 14,000 (my estimate at the assumed rate). Sources: https://www.stackmatix.com/blog/tiktok-ads-cost-2026-pricing-breakdown ; https://admanage.ai/blog/tiktok-ads-cost
- **Lead ads:** as of Aug 2026, no verified Pakistani TikTok cost-per-lead benchmark existed. One agency suggests PKR 150,000–300,000 for a first lead campaign. Source: https://weproms.com/blog/tiktok-lead-ads-pakistan-cost-quality/

### 5.3 Google Ads

- **CPC tiers:** PKR 20–80 for low-competition keywords, PKR 80–250 for moderate, and PKR 250–600+ for high competition. Source: https://growbiztech.com/how-much-do-google-ads-cost-in-pakistan-small-business-budget-guide-2026/
- **Typical spend:** most small and mid-sized businesses pay PKR 20–80; education, real estate and legal pay PKR 300–800. E-commerce runs PKR 20–150, close to PKR 50 on average. Sources: https://marketist.pk/blog/google-ads-cost-in-pakistan/ ; https://weproms.com/blog/is-google-ads-worth-it-pakistan-2026/
- **Example:** about PKR 260 CPC for "IELTS coaching Lahore". Source: https://weproms.com/blog/google-ads-quality-score-cpc-lever-pakistan/

### 5.4 Influencer rates

- **Micro tier (10K–100K followers):**
  - Instagram post PKR 15,000–120,000; Reel PKR 25,000–180,000; TikTok PKR 20,000–150,000. Source: https://voosha.io/blog/influencer-rates-in-pakistan
  - PKR 15,000–75,000 per Reel or TikTok at 10K–50K followers; PKR 50,000–200,000 at 50K–100K. Source: https://collabscafe.com/blog/pakistan-influencer-rates-2026
  - PKR 10,000–75,000 per Reel or TikTok. Source: https://weproms.com/blog/influencer-rates-pakistan-rate-card/
- **Nano tier (1K–10K):** PKR 3,000–15,000 per paid post. Source: https://weproms.com/blog/influencer-pricing-pakistan-2026-pkr-rates/
- **Macro tier (100K–1M):** about PKR 120,000–500,000 per Instagram post. Source: https://voosha.io/blog/influencer-rates-in-pakistan
- **Packaging:** quotes usually cover one Reel plus one Story; Story-only packages cost 30%–50% of the Reel rate; Karachi creators are priciest. Source: https://collabscafe.com/blog/pakistan-influencer-rates-2026
- **Trend:** Pakistani brands are shifting to commission or sales-based creator deals. Source: https://www.phoneworld.com.pk/influencer-marketing-pakistan-performance-deals-creators-commission/

### 5.5 Pakistan-specific ad-payment issues

- **Cards:** Meta accepts Visa, Mastercard and Amex. The official page is old. Source: https://www.facebook.com/business/help/212763688755026 . Many Pakistani debit cards ship with international online transactions switched off, so you must enable them. Source: https://thrivehash.com/blog/facebook-ads-payment-pakistan
- **SBP limits:**
  - Paragraph 14A of Chapter 14 of SBP's Foreign Exchange Manual reportedly lets banks remit up to USD 400,000 a year for each company, firm or sole proprietorship to approved digital service providers, including Google, Facebook, Instagram and YouTube.
  - SBP reportedly does not allow commercial payments abroad on personal cards.
  - Source: blog, https://pakera.pk/pay-google-meta-ads-from-pakistan/ . **Verify with your bank.**
- **Advance tax on card payments abroad:** sources conflict on the Section 236Y rate. One says 0.5% for filers and 1% for non-filers; another says 0.5% for active filers and 10% for non-filers. Sources: https://pakera.pk/pay-google-meta-ads-from-pakistan/ ; https://spendfigo.com/guides/meta-ads/pakistan . **Being on the Active Taxpayers List clearly matters.**
- **Provincial sales tax:** one blog claims 16% withholding on Meta ad payments, creditable if you are registered with PRA. This is unverified. Source: https://orahjewels.com/blogs/journals/hidden-tax-cost-digital-ads-pakistan
- **PKR billing:** one 2026 guide says Meta has offered PKR billing in Pakistan for years. This is unconfirmed. Source: https://velocedigital.co/blog/facebook-ads-cost-pakistan

---

## 6. Legal and regulatory

**Coverage warning:** the search budget ran out before this section was researched. The sourced facts are few. Everything marked [UNVERIFIED] needs checking with FBR, SECP, PTA, provincial revenue authorities, or a Pakistani tax or legal adviser.

### 6.1 Sourced facts

- **Gateway onboarding for a sole proprietor:** CNIC, NTN or other business registration, a utility bill, and a bank account maintenance certificate (PayFast). Safepay asks for CNIC and a bank account in the proprietor's name. Sources: https://www.scribd.com/document/890936512/Partner-Guide-PayFast ; https://safepay.helpscoutdocs.com/article/152-list-of-documents-you-need-to-provide-safepay
- **HBL** requires a registered business with an HBL company account, and an applicant aged 25 or over. Source: https://www.hbl.com/assets/documents/HBL_IPG_FAQs.pdf
- **SBP:** an internet merchant must run a business permissible under Pakistani law, with a registered place of business in Pakistan. Source: https://www.sbp.org.pk/epd/2000/c6.htm
- **Tax on digital sales:** since July 2025 a final withholding tax of 0.25%–2% on gross receipts from digitally ordered goods and services, collected by payment intermediaries. Source: Simpaisa (vendor) — https://www.simpaisa.com/blogs/how-to-set-up-online-payments-for-a-new-pakistan-e-commerce-store . Withholding sales tax on e-commerce rose from 1% to 2% in Budget 2025-26. Source: https://www.techjuice.pk/new-tax-imposed-on-online-shopping/
- **Refund practice:** use separate refund paths for prepaid and COD orders, refunding prepaid orders to the original source. Local store templates commonly use a 7-day window, but there is no official rule for it. Source: Simpaisa, Aug 2026 — https://www.simpaisa.com/blogs/how-to-handle-refunds-and-returns-digitally-in-pakistan-e-commerce
- **Refund cost:** JazzCash charges no MDR on a refund made the same day. Source: https://mobilinkbank.com/assets/documents/SOC_Q1_2026.pdf

### 6.2 Not verified in this session

- **[UNVERIFIED – background knowledge] Sole proprietorship:**
  - Pakistan has no separate incorporation for a sole proprietorship. The owner registers for an individual NTN on FBR's IRIS portal, free and online, and adds the business name and address.
  - A bank then opens a sole-proprietor business account against the NTN.
  - A Single Member Company (SMC-Pvt Ltd) is incorporated with SECP under the Companies Act 2017. It costs more in compliance (annual returns, audited accounts) but gives limited liability, and some gateways and banks prefer it.
  - Verify SECP fees and timelines at secp.gov.pk.
- **[UNVERIFIED – background knowledge] Income tax:**
  - A sole proprietor's profit from domestic digital sales is business income taxed at normal individual slab rates.
  - Withholding deducted by payment intermediaries (above) may be final or adjustable depending on the section. Confirm under the Finance Act 2025 provisions.
  - Active Taxpayers List status reduces several withholding rates, including on ad payments.
  - **Provincial sales tax on services** (PRA, SRB, KPRA, BRA) may apply to online services. Check whether "digital reports" fall into a taxable category in your province.
- **[UNVERIFIED – background knowledge] PECA 2016 as amended in 2025:**
  - The January 2025 amendment created a Social Media Protection and Regulatory Authority and a National Cyber Crime Investigation Agency.
  - It added an offence for intentionally spreading "false or fake information", with imprisonment and fines.
  - PECA also covers unauthorised access to and misuse of data and identity information.
  - Verify the current text and any court challenges before relying on this.
- **[UNVERIFIED – background knowledge] Data protection:** as far as I know, Pakistan's Personal Data Protection Bill had not been enacted by mid-2026. Check its current status. Even without a statute, these are prudent (estimate):
  - **Consent:** get explicit, granular consent for birth date, quiz answers and especially palm photos. Palm images can be treated as biometric-like data.
  - **Minimise palm images:** process them and delete them after the report, or make retention opt-in.
  - **Disclosures:** publish a privacy policy covering what you collect, why, how long you keep it, your processors (gateway, email or WhatsApp provider, hosting), cross-border transfer, and deletion requests.
  - **Minors:** block under-18 users, or get guardian consent.
  - **Payments:** do not store card data; leave it to the PCI-DSS gateway.
- **[UNVERIFIED – background knowledge] Consumer protection:** provincial consumer protection laws (e.g. Punjab Consumer Protection Act 2005) and consumer courts apply. The federal E-Commerce Policy (2019) set expectations for disclosure and refunds. Gateways in practice require a visible refund or cancellation policy (sourced above).
  - **For digital reports (estimate):** state that reports are delivered instantly and are non-refundable once generated, except for technical failure or duplicate payment. Offer a short goodwill window, and honour duplicate-charge refunds the same day.
- **[UNVERIFIED – background knowledge] PTA blocking risk:**
  - PTA can block or remove online content under PECA section 37 on grounds including religion, decency, morality and public order.
  - Pakistan has blocked major platforms before.
  - Fortune-telling or astrology-style claims can attract religious criticism.
  - **Mitigation (estimate):** frame the product as personality or temperament self-discovery for entertainment and reflection. Avoid predictive or "fate" claims. Keep the domain off any shared or bad-reputation hosting. Have a backup domain and a non-Meta channel (email list) in case of platform blocks.
  - No evidence was found in this session of PTA acting against personality-test sites.

---

## 7. Email, WhatsApp and SMS marketing in Pakistan

**Coverage warning:** this section was not researched before the search budget ran out. The only sourced items are these:

- WhatsApp has about 93.7 million users in Pakistan (Statista model, 2025). Source: https://www.statista.com/recent/statistics/p/154/
- A vendor claims more than 100 million users and use by about 90% of smartphone users. Source: https://chatdaddy.tech/blog/whatsapp-marketing-pakistan

The rest is unverified:

- **[UNVERIFIED – background knowledge] WhatsApp Business Platform pricing:**
  - Meta moved from per-conversation to per-message pricing on 1 July 2025.
  - Marketing templates are charged per delivered message.
  - Utility templates (order or report delivery) are cheaper, and free inside an open 24-hour customer-service window.
  - Service replies are free.
  - Pakistan's per-message rates were not verified. Get them from Meta's official rate card (developers.facebook.com/docs/whatsapp/pricing).
  - Business Solution Providers (BSPs) add their own markup or platform fee.
- **[UNVERIFIED] BSPs:** global BSPs such as Twilio, 360dialog, Gupshup and Wati serve Pakistan. Local agencies resell access. Pakistan-specific BSP pricing was not researched.
- **Open rates:** no Pakistan-specific measured data on email vs WhatsApp open rates was found. Vendor claims of very high WhatsApp open rates are common, but they are marketing claims, not benchmarks.
- **SMS costs:** not researched. **[UNVERIFIED]** Pakistani bulk-SMS aggregators sell branded (masked) and unmasked SMS. Masking requires PTA-compliant registration through the aggregator. Get quotes.
- **Practical approach (estimate):**
  - Deliver reports by email (cheap, and a durable owned channel).
  - Send a WhatsApp utility message with the report link only when the user opts in.
  - Use WhatsApp marketing templates sparingly: they cost per message, and Meta's quality ratings penalise spam.

---

## 8. Recommendations for mizaj.pk

### 8.1 Payment stack

| Layer | Recommendation | Why |
|---|---|---|
| Entity | Start as a sole proprietor: individual NTN with business name, plus a sole-proprietor business current account. Move to an SMC when revenue or gateway requirements justify it. | Fastest legal path; meets the Safepay and PayFast sole-proprietor document lists (sec. 1.2, 1.3). [Entity specifics unverified, sec. 6.2] |
| Primary gateway at launch | **Safepay**, or **PayFast** if Safepay's current card fee still includes Rs30 fixed. Apply to both in week 1 and go live with whichever approves first. | Safepay: SDKs, sandbox and webhooks are public. PayFast: transparent percentage-only rates, Raast QR 0.60%, wallets 2.20%. |
| Checkout order | 1) Raast (QR / RTP); 2) JazzCash and Easypaisa wallets; 3) cards (local and international) | 93% of online purchases are by account or wallet (SBP FY25); Raast is cheapest. |
| Pre-approval fallback | A static Raast QR or Raast ID on your business account, with manual fulfilment (0% MDR at Bank Alfalah). | Lets you take payments while gateway KYC is pending. |
| Scale stage (after about 1,500+ orders a month, estimate) | Negotiate custom MDRs; add a direct JazzCash merchant account (2.32%) or Easypaisa (instant settlement); consider XPay routing. | Lower blended MDR. |
| Diaspora | Phase 1: the PK gateway's international-card rail (PayFast 3.50%; Safepay about +0.3%). Phase 2: Lemon Squeezy, Paddle or Gumroad after confirming Pakistan payout eligibility. | Avoids a foreign entity. MoR payouts to Pakistan are unverified (sec. 2). |
| Website compliance pages | Terms, Privacy (covering palm images, birth date and answers), Refund/Cancellation, Service/Delivery (instant digital delivery), Contact with a Pakistani business address, HTTPS | Required by gateways (sec. 1.0) and JazzCash IPN (sec. 1.4) |

### 8.2 Launch prices

All prices in this table are estimates and recommendations, anchored to the benchmarks in sec. 3.

| Product | PKR price | Diaspora price | Rationale |
|---|---|---|---|
| Free test + short result | 0 | 0 | Lead capture and virality; Pakistani buyers distrust prepayment. |
| Mini report (one dimension, e.g. temperament summary) | **PKR 349** (keep it on Raast/wallet rails) | n/a | Near the Spotify Individual (379) and YouTube Premium (479) impulse band. Below about PKR 500, a Rs30 fixed card fee eats more than 6%. |
| Full personality or temperament report | **PKR 799** (launch offer PKR 599) | USD 7 / GBP 6 | Below Netflix Standard (800); in line with the $7 US personality-report reference. |
| Compatibility report (two people) | **PKR 1,299** | USD 12 / GBP 10 | Two-person value, giftable, and recruits the second person as a lead. |
| Bundle: full report + compatibility + 12-month guide | **PKR 2,199–2,499** | USD 19 / GBP 16 | Top of the target range; cheaper than ChatGPT Plus and far below courses (PKR 10,000+). |

At about PKR 280 per USD (assumption), USD 7 is about PKR 1,960. Diaspora prices are set for willingness to pay abroad, not by PKR parity.

- **Payment-method nudge (estimate):** show "Pay with Raast / JazzCash / Easypaisa" first. Accept cards on items of PKR 799 and above.

### 8.3 First-90-day paid-marketing budget (estimate)

- **Goal:** buy leads (free-test completers who opt in by email or WhatsApp) and validate conversion. Do not scale before the unit economics hold.
- **Suggested total: about PKR 500,000** (≈ USD 1,800 at the assumed rate).

| Month | Meta (FB + IG) | TikTok | Creators | Google Search | Total |
|---|---|---|---|---|---|
| 1, test | PKR 75,000 (≈ PKR 2,500 a day; 4–6 creatives, English vs Roman Urdu) | PKR 55,000 (about 10 days at the $20-a-day ad-group minimum) | PKR 30,000 (2–4 nano/micro creators at PKR 5,000–15,000) | PKR 0 | **PKR 160,000** |
| 2, iterate | PKR 90,000 | PKR 40,000 (only if CPL ≤ Meta's) | PKR 30,000 (1 micro creator at PKR 15,000–30,000 + affiliate commission) | PKR 10,000 (brand + "personality test Urdu"-type terms) | **PKR 170,000** |
| 3, scale winners | PKR 100,000 | PKR 30,000 | PKR 30,000 | PKR 10,000 | **PKR 170,000** |

- **Expected CPL (estimate, lead = free test completed + opt-in):** PKR 60–200 on Meta. This is derived from the cited Pakistani "broad offer" CPL of PKR 50–150 and the PKR 150–400 range for consumer categories. A free, shareable quiz should sit at the low end; education-style framing would push it higher.
  - TikTok CPL: unknown (no verified PK benchmark as of Aug 2026). Plan for parity with Meta, and cut TikTok if it runs above 1.5× Meta's CPL.
  - Google search CPC: about PKR 20–80 for low-competition terms.
- **Expected outcome (estimate):** PKR 500,000 at PKR 100–150 blended CPL gives about 3,300–5,000 leads.
- **Break-even check:**

| Lead→buyer conversion | Average order PKR 900: break-even CPL | Average order PKR 1,300: break-even CPL |
|---|---|---|
| 3% | PKR 27 | PKR 39 |
| 5% | PKR 45 | PKR 65 |
| 10% | PKR 90 | PKR 130 |

- **Implication (estimate):** at these price points, paid ads will **not pay back on the first purchase** unless conversion is high. Paid acquisition must be backed by:
  - a referral or compatibility loop, where each buyer invites a partner;
  - email and WhatsApp follow-up sequences;
  - organic TikTok and Instagram content.
- **Kill rules:**
  - Pause any ad set with a CPL above PKR 250 after PKR 10,000 spend.
  - Pause the whole programme at day 45 if blended lead→buyer conversion is below 3%.
- **Ad payments:** pay Meta, TikTok and Google with a business debit card that has international e-commerce enabled, and get on the Active Taxpayers List first. Withholding on foreign card spend is higher for non-filers (sec. 5.5).

### 8.4 Priority verification list before committing money

1. Safepay's current fee schedule (Rs30 fixed or 2.5% flat?), settlement days and approval time, in writing.
2. PayFast's setup fee (PKR 20,000 or none?) and approval time.
3. The FBR withholding provisions on digital sales (Finance Act 2025) and provincial sales tax on online services.
4. Pakistan payout eligibility on Lemon Squeezy, Paddle and Gumroad, by starting onboarding.
5. Meta's WhatsApp per-message rate card for Pakistan.
6. The current status of the Personal Data Protection Bill and the PECA 2025 amendment text.
7. Whether the Raast P2M subsidy continues after June 2026.

To finish sections 2, 6 and 7 properly, allow the blocked domains (safepay.helpscoutdocs.com, xstak.com, propakistani.pk, gopayfast.com, fbr.gov.pk, secp.gov.pk, developers.facebook.com) and run a follow-up search session.
