# 2026-10-30 · claude-ops · T32: fresh-eyes review of the 28–29 Oct repositioning

Scope from the handoff: copy, layout at 360px, the story card download on iPhone and Android, OG images, and
`deck.py` (plus `web.py`, `reports.py`, `content.py`, the OG paths in `api.py` and the checkout). I reviewed the code
myself. A subagent read all user-facing copy against STYLE v3, and I checked each of its findings in the files
before acting.

## What's solid
- **`deck.py`:**
  - Card numbers follow the `TYPE_CODES` × `MIZAJ_KEYS` order.
  - "Best with" matches the highest pair score in `content/compat/mizaj_pairs.json` for every element (Air–Earth 85,
    Fire–Water 84).
  - The opposite flips all four letters.
  - Text is escaped.
  - `card()` (HTML) and `card_data()` (the canvas story card) carry the same fields.
- **Story card download:** I took both tests in a phone browser, then pressed "Save my card".
  - Android (Pixel 7, Chromium) and iPhone 13 (WebKit) produced identical 1080×1920 PNGs that match the card on the
    result page.
  - Real iPhones open the share sheet instead (`navigator.canShare`); I tested the download fallback.
- **Layout at 360px:** result, home, type, element, compatibility, pricing, Milan and schools pages have no
  horizontal scroll and no console errors.
- **OG images:** all 178 `og:image` references in `dist/` point to files that exist (`.jpg` paths after the switch
  from `.png`).
- **Checkout and payments:** reviewed under T40 (PR #4).
- **Copy:**
  - No MBTI type names in content.
  - Element guides keep "traditionally" and the disclaimers.
  - Zodiac and numbers are labelled for fun.
  - Compatibility never weighs religion, ethnicity, caste or family.
  - The 9 ads and the sampled social posts are clean.

## Fixed
- **PR #5 (merged, site only):**
  - **Urdu names in the meta descriptions of all 136 compatibility pages:** "How a Darvesh (INFJ)…" is now "How The
    Mystic (INFJ)…".
  - **"Is this the MBTI?" FAQ heading on the home page:** it's now "Is this the same as other 16-type tests?". The
    duplicate Myers & Briggs line on About is gone.
  - **Milan relation:** it showed "Rishta"; it now shows "Partner" and the other labels.
  - **Unani and Urdu labels:** "INTJ · Damvi" is now "INTJ · Air"; "Khushk/Tar" is now "Dry/Moist"; "Burj" is now
    "Zodiac".
  - **Urdu words:** "Ye page nahi mila", "Say salaam" and "Shukriya!" are gone.
  - **One-culture defaults:**
    - "Ramadan" is now "fasting days" in the teasers.
    - The career hero is now "Which path actually fits you?" ("because a friend did").
    - Schools: "stream" is now "subjects and path".
    - The PKR counselling comparison is now currency-neutral.
    - Placeholders and the checkout time zone are updated.
- **PR #6 (open, needs review):**
  - **Shared result link titles used the Urdu or Unani name:** "Sam is INFJ: Darvesh" and "My mizaj is Saudavi" now
    use English names, with 2 new tests that fail on the old code.
  - **Zodiac mash-up:** the Urdu name is replaced by the English one, with an `ASSET_VERSION` bump.
  - **Unlock email:** "Shukriya!" is now "Thank you!".
  - **Palm-reader prompt:** "Pakistani storyteller… cricket, shaadi" is gone; the prompt now sets a global voice.

## Still open
- **T49 (claude-ops), content pass:**
  - 9 of the 16 type archetype quotes are cousin or wedding scenes.
  - INFJ's "Should I say yes to the proposal?" reads as an arranged match.
  - Family sections lean on "the family's good name" and "what will people say" (INTJ, INFP, ESTP and ESFJ
    `premium.relationships.family`; ESFJ `blind_spots[0]`; `careers/advice.json` `for_parents`).
  - Some `rishta_tips` read as an arranged process (ESTJ[2], ESFJ[0], ESFJ[3]).
  - `content/types/SCHEMA.md:45` still asks writers for "Pakistani routes (MDCAT)".
  - The numerology Abjad example uses a religious name.
- **Milan:** the copy offers "parent", but the relation list has no Parent option. Adding one is a small `api.py` and
  template change, which I'll fold into T49's follow-up PR.
- **For @owner:**
  - School and team prices on `/schools/` and `/teams/` are PKR only ("Outside Pakistan we quote in your currency").
    Should we publish USD prices (the team pack already has $9)?
  - Terms still repeats the Myers & Briggs non-affiliation line. That's legal text; I left it unless you want it
    footer-only.

## Needs
- @claude-cloud (Monday reviewer): review and merge PR #6.
- @claude-server: nothing new.
