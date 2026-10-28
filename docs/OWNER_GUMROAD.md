# Owner steps: international card payments with Gumroad (task T15)

**Why Gumroad:** the research (`docs/research/06-international-gtm.md`) found it is the only easy checkout that
(1) pays out to a Pakistani bank account, (2) handles VAT and sales tax for buyers in the UK, EU, US and elsewhere
as merchant of record, and (3) explicitly allows "for fun" readings such as palm reading. Lemon Squeezy, which the
site was built for, is moving onto Stripe's system, which does not support Pakistan. Fees: 10% + $0.50 per sale.
Paddle (cheaper, 5% + $0.50) is task T35 for later; it does not allow palm reading.

Time needed: about 30 minutes, plus Gumroad's payout verification.

## 1. Create the account
1. Sign up at gumroad.com with the Mizaj email. Name the profile **Mizaj**.
2. Settings → Payments: add your Pakistani bank account for payouts (PKR) and complete the identity and tax form.
3. Settings → Advanced: note your **Ping** setting (we will give you the URL to paste, see step 3).

## 2. Create 5 products (Products → New product → "Digital product")
Make each product with exactly this name and price. No subscription, no "pay what you want", no free trial.
Leave the content empty (the report unlocks on mizaj.pk, not on Gumroad); in the receipt text write:
"Thank you! Go back to mizaj.pk: your report unlocks automatically within a minute."

| Product | Price (USD) | Permalink to choose |
| --- | --- | --- |
| Full Mizaj Report | $9 | `mizaj-full` |
| Career Compass | $14 | `mizaj-career` |
| Mizaj Milan: Couple Report | $15 | `mizaj-couple` |
| Full AI Palm Reading (for fun) | $5 | `mizaj-palm` |
| Complete Mizaj Bundle | $24 | `mizaj-bundle` |

Turn on "Allow customers to choose a quantity: off" and set refunds to match our 7-day promise.

## 3. Send claude-server three things (never paste them in GitHub or chat logs)
- the 5 product links,
- your Gumroad **access token** (Settings → Advanced → Applications → create an app named "Mizaj", then
  "Generate access token"),
- your Gumroad **seller id** (shown in the Ping settings).

`claude-server` puts them in `/opt/mizaj/.env` once task T33 (the automatic unlock) is merged. Until then the
checkout shows overseas visitors a "get a payment link on WhatsApp" button, and you can send them a product link
by hand and unlock their report with a code from the admin page.
