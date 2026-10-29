# Art brief v2: characters for the Mizaj Deck

For whoever makes images (normally `codex` with ChatGPT image generation). Version 2, 28 Oct 2026 (audience updated 29 Oct). The first
set (people in Pakistani scenes, T21) has been retired: the owner found it too local and badly placed, and 2026
audiences read AI-made people as cheap. Read `docs/research/05-social-trends-2026.md` sections 2, 5 and 6 for the reasoning.

## What changed

Mizaj is for everyone (students, professionals, educators, marketers, families, young and old, any country). Every result is a collectible
card in **the Mizaj Deck**: 16 types × 4 elements (Air, Fire, Water, Earth) = 64 cards. The cards are drawn in code
(`server/mizaj/deck.py`, `site/static/css/deck.css`) and already look finished without any art. Art is an upgrade:
one small character per type that sits inside the card's art window, on top of the element's colour glow.

See the cards now: run the site (`AGENTS.md` → Commands) and open `/types/intj/`, or render the slides
(`python tools/render_social.py`) and look in `social/media/`.

## The characters

- **16 characters, one per type, non-human.** Small, rounded, gender-neutral "spirits" (think a friendly ink-drawn
  creature or figurine, not a person). No skin tones, no national dress, no realistic faces: everyone in the
  audience should see themselves. Simple dot eyes are fine.
- **One prop each** that says the type at a glance (table below). Props may carry one light cultural touch
  (a kite, a teapot, a bat, a drum), never more than one per character, and no single culture as the default across the set.
- **Hand-made look:** ink line with a visible hand (slight wobble), flat fills, a little risograph-style grain.
  Not 3D, not clay, not glossy, not anime, not Ghibli-like, no gradients.
- **Two colours only:** ink `#17131F` and paper `#F4F1EA`, on a **transparent background**. The card supplies the
  colour: the same character sits on Air coral, Fire saffron, Water teal or Earth plum, so it must read on all four.
- **Consistency matters more than detail.** Same line weight, same body proportions, same eye style, same
  scale across all 16. Lock a master sheet first, then make the rest from it (reference the master sheet in every
  prompt; ChatGPT's image editing with the sheet attached works).
- **Never:** text, letters, numbers or logos; religious symbols; flags; alcohol; romance or dating poses; real or
  famous people; anything scary.

| Code | Name | Prop and pose |
| --- | --- | --- |
| INTJ | The Strategist | Holds a chess knight, calm, one eyebrow up |
| INTP | The Philosopher | Sits on a stack of books, a tangle of thought-lines above its head |
| ENTJ | The General | Points forward with a rolled-up plan, chest out |
| ENTP | The Quick Wit | Mid-argument, two speech bubbles (empty, no text), grinning |
| INFJ | The Mystic | Holds a small lantern, eyes half closed |
| INFP | The Poet | Hugs a notebook with a pressed flower sticking out |
| ENFJ | The Mentor | Hands a small glowing seedling to someone off-card, warm smile |
| ENFP | The Free Spirit | Flies a kite, mid-skip |
| ISTJ | The Trustee | Carries a neat stack of labelled-looking boxes (no readable text) and a key ring |
| ISFJ | The Protector | Offers a steaming cup of tea with both hands |
| ESTJ | The Organizer | Clipboard in one hand, stopwatch in the other |
| ESFJ | The Host | Carries a laden tray of sweets, welcoming lean |
| ISTP | The Craftsman | Spins a wrench, focused |
| ISFP | The Artist | Paintbrush behind the ear, holding a small camera |
| ESTP | The Daredevil | Mid-leap with a skateboard or a ball, one foot off the ground |
| ESFP | The Life of the Party | Plays a small drum, mid-dance |

Optional later (do not start until the 16 are approved): 4 element spirits (Air, Fire, Water, Earth) for
element-only cards, same rules, saved as `air.webp`, `fire.webp`, `water.webp`, `earth.webp`.

## Files

- Path: `site/static/img/deck/<code>.webp`, lowercase (e.g. `intj.webp`).
- Size: **1200 × 700 px**, transparent background, character centred horizontally, standing on the bottom edge
  with about 8% margin, its height about 80% of the image. **WebP with alpha, under 90 KB each.**
- The site, the downloadable story card, the social slides and the link previews pick the files up automatically
  (`server/mizaj/deck.py` → `art_path`). No code change is needed.

## Process

1. **Style test first (T31a):** make INTJ, ENFP, ISFJ and ESTP only. Open a PR with the four files plus screenshots
   of `/types/intj/` and `/types/enfp/` at phone width and one rendered slide
   (`python tools/render_social.py social/plan/launch30.json <a post id with type slides>`). `claude-cloud` or the
   owner approves the style in the PR before you continue.
2. **The other 12 (T31b)** from the approved master sheet. Same checks. Re-render the social slides
   (`python tools/render_social.py`) and commit the changed `social/media/` files with the art.
3. Leave a log entry in `ops/log/` with the prompts you used, so anyone can make matching art later.
