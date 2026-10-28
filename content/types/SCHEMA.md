# Type profile schema

One file per type: `content/types/<CODE>.json` (e.g. `INTJ.json`). Valid UTF-8 JSON, 2-space indent.
`free` is shown to everyone on the result page and the public SEO page. `premium` is the paid Full Report, so it must feel clearly worth paying for: deeper, more specific, more personal and more practical than `free`, with no repetition of free text.

Word counts are targets (±15%). Total per type: about 3,500 words.

```json
{
  "code": "INTJ",
  "name": "Mansooba-saaz",
  "name_ur": "منصوبہ ساز",
  "name_en": "The Strategist",
  "family": "Danishwar",
  "emoji": "♟️",
  "colors": ["#hex primary", "#hex accent"],
  "tagline": "One line, max 12 words, that makes this type feel seen.",
  "share_line": "First-person brag for share cards, max 14 words, e.g. 'I had the plan before the group chat even started.'",
  "keywords": ["5 one-word traits"],
  "rarity": "approximate share of people, as a string like 'about 2% of people'",
  "free": {
    "summary": "Two paragraphs, 160-200 words total. Who they are, what drives them, how others see them.",
    "strengths": ["5 items, each 8-15 words"],
    "watchouts": ["3 items, each 8-15 words, kind but honest"],
    "pakistani_archetype": "One vivid relatable line, 20-35 words: 'You're the one who ...' set in Pakistani everyday life.",
    "in_relationships": "40-60 words teaser.",
    "at_work": "40-60 words teaser.",
    "fictional_twins": ["4 well-known fictional characters (global films, books, cartoons) who show this type, as 'Name (Work)'"]
  },
  "premium": {
    "deep_dive": "3-4 paragraphs, 400-500 words. The inner world: core motivation, core fear, how they process the world, the gap between how they feel inside and how they come across.",
    "superpowers": [{"title": "2-4 words", "text": "70-90 words with a concrete example"}],
    "blind_spots": [{"title": "2-4 words", "text": "70-90 words: the pattern, why it happens, one fix"}],
    "relationships": {
      "love_and_marriage": "120-150 words: what they need from a spouse, how they show love, typical friction.",
      "rishta_tips": ["5 practical tips for the rishta/marriage stage, 15-25 words each, e.g. what to ask, what to reveal, red flags they tend to miss"],
      "family": "100-130 words: with parents and in a joint family; handling expectations and izzat; as a sibling.",
      "friendship": "70-90 words.",
      "best_matches": ["3 type codes that tend to fit well"],
      "growth_matches": ["2 type codes that are challenging but growth-inducing"]
    },
    "career": {
      "work_style": "100-120 words",
      "ideal_environment": "60-80 words",
      "careers": [{"title": "Career", "why": "20-30 words", "pk_path": "Concrete Pakistani route, 15-30 words: degree, entry test (MDCAT, ECAT, NUST NET, LUMS LCAT/SAT, CSS, ICAP/ACCA etc.), or freelancing/remote route"}],
      "think_twice": [{"title": "Career", "why": "15-25 words, respectful"}],
      "as_a_leader": "60-80 words",
      "as_a_team_member": "60-80 words",
      "money_style": "60-80 words: spending, saving, risk, committees (BC), business instincts"
    },
    "communication": {
      "how_they_talk": "60-80 words",
      "how_to_talk_to_them": ["4 tips for others, 12-20 words each"],
      "conflict_style": "60-80 words"
    },
    "stress": {
      "triggers": ["4 items"],
      "signs": ["4 items: what stress looks like in this type"],
      "reset": ["4 concrete recovery actions"]
    },
    "growth_plan": [
      {"week": 1, "focus": "3-6 words", "why": "30-40 words", "actions": ["3 small daily actions, 10-20 words each"]},
      {"week": 2, "focus": "...", "why": "...", "actions": ["..."]},
      {"week": 3, "focus": "...", "why": "...", "actions": ["..."]},
      {"week": 4, "focus": "...", "why": "...", "actions": ["..."]}
    ],
    "with_each_mizaj": {
      "damvi": "40-60 words: how this type shows up when the person's Unani temperament is Damvi (warm-moist, Air, sociable, cheerful)",
      "safravi": "40-60 words: with Safravi (warm-dry, Fire, driven, quick temper)",
      "balghami": "40-60 words: with Balghami (cool-moist, Water, calm, steady, slow)",
      "saudavi": "40-60 words: with Saudavi (cool-dry, Earth, thoughtful, serious, deep)"
    },
    "letter": "A personal letter to this type, 150-200 words, starting 'Dear <Name>,' (use the Roman Urdu type name) and signed '— Mizaj'. Encouraging, specific, moving."
  }
}
```

Counts: `superpowers` 6, `blind_spots` 5, `careers` 10, `think_twice` 3.
Careers must span government, corporate, entrepreneurial and creative/freelance options realistic in Pakistan in 2026 (include at least two remote or freelance options).
