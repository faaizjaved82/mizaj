# Art brief: Mizaj illustrations

For whoever generates images (normally `codex` using ChatGPT image generation). The site and the social-slide
renderer use these files automatically when they exist at the paths below.

## Style (same for every image, so the set looks like one family)

- **Look:** flat editorial illustration with soft grain, gentle shapes, subtle shadows; modern Pakistani life;
  warm and witty, never cartoonish or childish. Think magazine spot illustration, not stock art or 3D.
- **People:** contemporary young Pakistanis (18–35), varied skin tones and regions, modest everyday clothing
  (shalwar kameez, kurta, dupatta, sweaters, shawls, jeans with kurta). Mix of men and women across the set
  (8 and 8 for the types, alternate within each family). Faces simple and friendly; no real or famous people.
- **Never:** text, letters, numbers or logos inside the image; religious symbols; alcohol; romance or dating poses;
  stereotypes of any ethnicity, province, sect or class; flags.
- **Palette:** background cream `#FBF6EE` (or transparent). Accents from the brand: ink `#1B1530`, saffron `#E8A33D`,
  pomegranate `#C8443A`, plus the family colour of each type: Danishwar (NT) purple `#6B4FA0`, Ahl-e-Dil (NF)
  green `#2E8A6A`, Pasban (SJ) blue `#2F6DB0`, Fankar (SP) amber `#D98C2B`. Mizaj colours: Damvi `#D2544A`,
  Safravi `#E39B2D`, Balghami `#2E8A8A`, Saudavi `#5A4A78`.
- **Motif:** where it fits naturally, an eight-pointed star (girih) pattern in a cushion, tile, rug or window.
- **Format:** generate square (1024×1024), subject centred with margin, then export **WebP, 800×800, under 120 KB**.

## Files to make

### 16 types → `site/static/img/types/<code>.webp` (lowercase code, e.g. `intj.webp`)

Prompt pattern: *"Flat editorial illustration, soft grain, cream background, [person], [scene], [props], accents of
[family colour], modern Pakistani setting, no text."* Scenes (read the type's `tagline` and `pakistani_archetype` in
`content/types/<CODE>.json` for more):

| Code | Name | Scene idea |
| --- | --- | --- |
| INTJ | Mansooba-saaz, The Strategist | Calm person at a desk with a chessboard and a planning notebook, chai cup, city lights through the window |
| INTP | Falsafi, The Philosopher | Person on a charpai surrounded by open books and sketches of ideas, late-night lamp |
| ENTJ | Sipah-salar, The General | Confident person directing a busy shaadi-planning table, clipboard, everyone looking to them |
| ENTP | Hazir-jawab, The Quick Wit | Grinning person mid-debate at a dhaba table, hands gesturing, friends laughing |
| INFJ | Darvesh, The Mystic | Quiet person by a window at dusk, journal in hand, reading the room at a family gathering behind |
| INFP | Shayar, The Poet | Person writing poetry in a notebook under a tree, dried flowers, headphones |
| ENFJ | Ustaad, The Mentor | Person encouraging younger cousins around a study table before exams |
| ENFP | Rangeela, The Free Spirit | Person with paint on hands, phone full of ideas, colourful rickshaw behind |
| ISTJ | Amanatdar, The Trustee | Person with neatly labelled document folders, spare passport photos, everything in order |
| ISFJ | Muhafiz, The Protector | Person bringing tea and medicine to an elder, warm home interior |
| ESTJ | Muntazim, The Organizer | Person with a checklist directing a mehndi set-up, lights going up on time |
| ESFJ | Mezbaan, The Host | Person welcoming guests at the door with a laden tray, warm living room |
| ISTP | Karigar, The Craftsman | Person fixing a motorbike or a sound system with focused calm, tools neatly around |
| ISFP | Musawwir, The Artist | Person arranging flowers and fabric, camera nearby, soft light |
| ESTP | Jaanbaz, The Daredevil | Person mid-cricket shot in a street match, dust and energy |
| ESFP | Mehfil ki Jaan, The Life of the Party | Person leading the dance at a dholki, dhol, fairy lights, friends clapping |

### 4 mizaj → `site/static/img/mizaj/<key>.webp`
Still-life, no people, symbolic of the temperament and its element:

| Key | Mizaj | Still-life idea |
| --- | --- | --- |
| damvi | Damvi, warm and moist, Air, spring | Pomegranates, rose petals drifting on a spring breeze, a light breezy curtain |
| safravi | Safravi, warm and dry, Fire, summer | A small flame or diya, saffron threads, turmeric, red chillies, summer sun |
| balghami | Balghami, cool and moist, Water, winter | Flowing water, cucumber slices, a clay matka with condensation, rain |
| saudavi | Saudavi, cool and dry, Earth, autumn | Mountains in the distance, dates, almonds, a clay pot, falling autumn leaves |

### 1 home hero → `site/static/img/hero.webp` (export 840×840)
Four young Pakistanis of clearly different temperaments around a chai table at home (one animated storyteller, one
quiet observer, one organiser pouring tea, one laughing), an eight-pointed-star tile pattern on the wall, cream
background, brand accents.

## After adding images

1. `python build.py` must pass; open `/types/intj/` locally and check the image doesn't cover text on a phone width.
2. Re-render the social posts so slides pick up the art: `python tools/render_social.py` (re-renders all posts;
   commit the changed `social/media/` files).
3. Commit with a message like "art: 16 type illustrations" and open the PR.
