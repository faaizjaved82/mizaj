"""Scores test answers on the server (the browser's score is never trusted)."""
from __future__ import annotations

from . import content


class ScoringError(ValueError):
    pass


def _answered(items: list[dict], answers: dict, min_ratio: float) -> None:
    got = sum(1 for it in items if it["id"] in answers)
    if got < len(items) * min_ratio:
        raise ScoringError(f"Please answer at least {int(len(items) * min_ratio)} questions ({got} answered).")


def score_personality(answers: dict[str, int]) -> tuple[str, dict]:
    bank = content.questions("personality")
    items = bank["items"]
    _answered(items, answers, 0.9)
    sums = {d: 0 for d in content.DIMENSIONS}
    maxes = {d: 0 for d in content.DIMENSIONS}
    strongest = {d: (0, 0) for d in content.DIMENSIONS}  # (abs contribution, sign) for tie-breaks
    for it in items:
        v = answers.get(it["id"])
        if v is None:
            continue
        v = int(v)
        if not 1 <= v <= 5:
            raise ScoringError("Answers must be between 1 and 5.")
        contrib = it["key"] * (v - 3)
        d = it["dim"]
        sums[d] += contrib
        maxes[d] += 2
        if abs(contrib) > strongest[d][0]:
            strongest[d] = (abs(contrib), 1 if contrib > 0 else -1)
    code, dims = "", {}
    for d, meta in content.DIMENSIONS.items():
        s, mx = sums[d], max(maxes[d], 1)
        if s == 0:
            first = strongest[d][1] > 0  # lean towards the single strongest answer; else second letter
        else:
            first = s > 0
        pct_first = round(50 + 50 * s / mx)
        if first and pct_first <= 50:
            pct_first = 51
        if not first and pct_first >= 50:
            pct_first = 49
        letter = meta["a"] if first else meta["b"]
        code += letter
        dims[d] = {"letter": letter, "pct_a": pct_first, "pct_b": 100 - pct_first,
                   "strength": abs(pct_first - 50) * 2}
    return code, {"dims": dims}


def _mizaj_axis_limits(items: list[dict]) -> dict:
    lim = {"h_pos": 0, "h_neg": 0, "m_pos": 0, "m_neg": 0}
    for it in items:
        hs = [o.get("h", 0) for o in it["options"]]
        ms = [o.get("m", 0) for o in it["options"]]
        lim["h_pos"] += max(0, max(hs))
        lim["h_neg"] += min(0, min(hs))
        lim["m_pos"] += max(0, max(ms))
        lim["m_neg"] += min(0, min(ms))
    return lim


def score_mizaj(answers: dict[str, int]) -> tuple[str, dict]:
    bank = content.questions("mizaj")
    items = bank["items"]
    _answered(items, answers, 0.85)
    h = m = 0
    for it in items:
        idx = answers.get(it["id"])
        if idx is None:
            continue
        idx = int(idx)
        if not 0 <= idx < len(it["options"]):
            raise ScoringError("Invalid option.")
        h += it["options"][idx].get("h", 0)
        m += it["options"][idx].get("m", 0)
    lim = _mizaj_axis_limits(items)
    # Normalise each axis to -100..100 against the side it landed on.
    h_norm = round(100 * h / (lim["h_pos"] if h >= 0 else -lim["h_neg"] or 1)) if h else 0
    m_norm = round(100 * m / (lim["m_pos"] if m >= 0 else -lim["m_neg"] or 1)) if m else 0
    warm, moist = h >= 0, m >= 0
    key = {(True, True): "damvi", (True, False): "safravi",
           (False, True): "balghami", (False, False): "saudavi"}[(warm, moist)]
    # Secondary: flip the weaker axis.
    if abs(h_norm) <= abs(m_norm):
        secondary = {(True, True): "balghami", (True, False): "saudavi",
                     (False, True): "damvi", (False, False): "safravi"}[(warm, moist)]
    else:
        secondary = {(True, True): "safravi", (True, False): "damvi",
                     (False, True): "saudavi", (False, False): "balghami"}[(warm, moist)]
    balanced = abs(h_norm) < 12 and abs(m_norm) < 12  # Mu'tadil: close to the centre on both axes
    return key, {"heat": h_norm, "moisture": m_norm, "raw": {"h": h, "m": m},
                 "secondary": secondary, "balanced": balanced}


def score_interests(answers: dict[str, int]) -> tuple[str, dict]:
    bank = content.questions("interests")
    items = bank["items"]
    _answered(items, answers, 0.85)
    sums = {c: 0 for c in "RIASEC"}
    counts = {c: 0 for c in "RIASEC"}
    for it in items:
        v = answers.get(it["id"])
        if v is None:
            continue
        v = int(v)
        if not 1 <= v <= 3:
            raise ScoringError("Answers must be between 1 and 3.")
        sums[it["code"]] += v
        counts[it["code"]] += 1
    pct = {c: round(100 * (sums[c] - counts[c]) / (2 * counts[c])) if counts[c] else 0 for c in sums}
    order = sorted("RIASEC", key=lambda c: (-pct[c], "RIASEC".index(c)))
    return "".join(order[:3]), {"pct": pct, "order": order}


SCORERS = {"personality": score_personality, "mizaj": score_mizaj, "interests": score_interests}


def score(test: str, answers: dict) -> tuple[str, dict]:
    fn = SCORERS.get(test)
    if not fn:
        raise ScoringError("Unknown test.")
    if not isinstance(answers, dict) or len(answers) > 200:
        raise ScoringError("Invalid answers.")
    return fn({str(k)[:8]: v for k, v in answers.items()})
