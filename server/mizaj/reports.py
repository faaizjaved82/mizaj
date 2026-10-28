"""Builds result pages and paid reports from scores + content, and works out what a profile has paid for."""
from __future__ import annotations

import hashlib
from datetime import date

from . import content, db

DIM_WEIGHTS = {"EI": 0.2, "SN": 0.3, "TF": 0.25, "JP": 0.25}


# ---------- entitlements ----------

def entitlements(profile_id: str) -> set[str]:
    feats: set[str] = set()
    for r in db.q("SELECT product FROM orders WHERE profile_id = ? AND status = 'paid'", profile_id):
        try:
            feats.update(content.product(r["product"])["includes"])
        except KeyError:
            pass
    return feats


def pair_unlocked(pair: dict) -> bool:
    members = [m for m in (pair["a_profile"], pair["b_profile"]) if m]
    marks = ",".join("?" * len(members))
    row = db.q1(f"""SELECT 1 FROM orders WHERE status = 'paid' AND (
                      (product = 'couple' AND pair_id = ?) OR
                      (product = 'bundle' AND profile_id IN ({marks})))""", pair["id"], *members)
    return row is not None


# ---------- individual results ----------

def personality_view(code: str, scores: dict, premium: bool) -> dict:
    t = content.type_profile(code)
    fam = content.family_of(code)
    view = {
        **content.type_summary(code),
        "family_info": {"name": fam, **content.FAMILIES[fam]},
        "dims": [{**content.DIMENSIONS[d], "key": d, **scores["dims"][d]} for d in content.DIMENSIONS],
        "free": t["free"],
    }
    if premium:
        view["premium"] = t["premium"]
    return view


def mizaj_view(key: str, scores: dict, premium: bool, type_code: str | None = None) -> dict:
    m = content.mizaj_profile(key)
    view = {**content.mizaj_summary(key), "scores": scores, "free": m["free"], "disclaimer": m.get("disclaimer"),
            "secondary": content.mizaj_summary(scores["secondary"]) if scores.get("secondary") else None}
    if premium:
        view["premium"] = m["premium"]
        if type_code:
            view["with_type"] = content.type_profile(type_code)["premium"]["with_each_mizaj"].get(key)
    return view


def career_view(interests: dict | None, type_code: str | None, premium: bool) -> dict:
    data = content.riasec()
    view: dict = {"available": interests is not None}
    if interests:
        code = interests["outcome"]
        pct = interests["scores"]["pct"]
        view["code"] = code
        view["codes"] = [{"letter": c, "pct": pct[c], "name": data["codes"][c]["name"],
                          "nickname": data["codes"][c].get("nickname"), "ur": data["codes"][c].get("ur"),
                          "summary": data["codes"][c]["summary"]} for c in interests["scores"]["order"]]
        view["pairs_note"] = data.get("pairs_note")
        if premium:
            take = {0: 6, 1: 4, 2: 2}
            careers = []
            for i, c in enumerate(code):
                for job in data["codes"][c]["careers"][: take[i]]:
                    careers.append({**job, "code": c})
            view["careers"] = careers
            view["subjects"] = [{"letter": c, "text": data["codes"][c].get("subjects")} for c in code]
            view["strengths"] = {c: data["codes"][c].get("strengths", []) for c in code}
            view["advice"] = content.career_advice()
    if type_code:
        t = content.type_profile(type_code)
        view["type_teaser"] = t["free"]["at_work"]
        if premium:
            view["type_career"] = t["premium"]["career"]
    return view


def profile_view(profile: dict, viewer_has_key: bool) -> dict:
    """Everything a result page needs. Premium sections only for the owner who has paid."""
    results = db.latest_results(profile["id"])
    feats = entitlements(profile["id"]) if viewer_has_key else set()
    out: dict = {"id": profile["id"], "name": profile["name"], "results": {}, "owned": sorted(feats)}
    pers = results.get("personality")
    type_code = pers["outcome"] if pers else None
    if pers:
        out["results"]["personality"] = personality_view(type_code, pers["scores"], "full" in feats)
    if "mizaj" in results:
        mz = results["mizaj"]
        out["results"]["mizaj"] = mizaj_view(mz["outcome"], mz["scores"], "mizaj_full" in feats, type_code)
    if "interests" in results or pers:
        out["results"]["career"] = career_view(results.get("interests"), type_code, "career" in feats)
    if pers and "mizaj" in results:
        out["combo"] = f"{type_code} · {content.mizaj_summary(results['mizaj']['outcome'])['global_name']}"
    return out


# ---------- couples (Mizaj Milan) ----------

def _dim_key(dim: str, a: str, b: str) -> str:
    meta = content.DIMENSIONS[dim]
    if a == b:
        return a + a
    return meta["a"] + meta["b"]


def couple_view(pair: dict, premium: bool) -> dict:
    a_prof, b_prof = db.get_profile(pair["a_profile"]), db.get_profile(pair["b_profile"])
    ra, rb = db.latest_results(pair["a_profile"]), db.latest_results(pair["b_profile"])
    ta, tb = ra["personality"]["outcome"], rb["personality"]["outcome"]
    blocks_src = content.compat_dimensions()
    dims, total = [], 0.0
    for i, d in enumerate(content.DIMENSIONS):
        key = _dim_key(d, ta[i], tb[i])
        blk = blocks_src[d][key]
        total += DIM_WEIGHTS[d] * blk["score"]
        item = {"dim": d, "label": content.DIMENSIONS[d]["label"], "key": key, "a": ta[i], "b": tb[i],
                "score": blk["score"], "headline": blk["headline"]}
        if premium:
            item.update({k: blk[k] for k in ("connect", "friction", "tips")})
            item["talk_before_marriage"] = blk.get("talk_before_marriage") or blk.get("talk_before_nikah") or []
        dims.append(item)
    score = total
    mizaj = None
    if "mizaj" in ra and "mizaj" in rb:
        ma, mb = ra["mizaj"]["outcome"], rb["mizaj"]["outcome"]
        mp = content.mizaj_pair(ma, mb)
        score = 0.75 * total + 0.25 * mp.get("score", 70)
        mizaj = {"a": content.mizaj_summary(ma), "b": content.mizaj_summary(mb), "score": mp.get("score"),
                 "headline": mp.get("headline")}
        if premium:
            mizaj.update({k: mp.get(k) for k in ("dynamic", "home_life", "tips")})
    view = {
        "id": pair["id"], "relation": pair["relation"], "score": round(score),
        "a": {"name": a_prof["name"], "type": content.type_summary(ta)},
        "b": {"name": b_prof["name"], "type": content.type_summary(tb)},
        "dims": dims, "mizaj": mizaj, "premium": premium,
    }
    if premium:
        view["intro"] = blocks_src.get("intro")
        view["closing"] = blocks_src.get("closing")
        pa, pb = content.type_profile(ta)["premium"], content.type_profile(tb)["premium"]
        view["love"] = {"a": pa["relationships"]["love_and_marriage"], "b": pb["relationships"]["love_and_marriage"]}
        view["talk_to"] = {"a": pa["communication"]["how_to_talk_to_them"], "b": pb["communication"]["how_to_talk_to_them"]}
        view["conflict"] = {"a": pa["communication"]["conflict_style"], "b": pb["communication"]["conflict_style"]}
    return view


# ---------- fun: zodiac and numerology ----------

def zodiac_for(birth: date) -> dict:
    md = birth.strftime("%m-%d")
    for s in content.zodiac()["signs"]:
        start, end = s["start"], s["end"]
        if start <= end:
            if start <= md <= end:
                return s
        elif md >= start or md <= end:  # Capricorn wraps the year
            return s
    return content.zodiac()["signs"][0]


def _reduce(n: int) -> int:
    while n > 9 and n not in (11, 22):
        n = sum(int(c) for c in str(n))
    return n


def name_number(name: str) -> dict:
    data = content.numerology()
    abjad, latin = data["abjad"], data["latin"]
    total, system = 0, "latin"
    if any(ch in abjad for ch in name):
        system = "abjad"
        total = sum(abjad.get(ch, 0) for ch in name)
    else:
        total = sum(latin.get(ch, 0) for ch in name.lower())
    num = _reduce(total) if total else 0
    return {"system": system, "total": total, "number": num, "meaning": data["numbers"].get(str(num))}


def birth_number(birth: date) -> dict:
    data = content.numerology()
    num = _reduce(sum(int(c) for c in birth.strftime("%Y%m%d")))
    return {"number": num, "meaning": data["numbers"].get(str(num))}


def stable_pick(seed: str, n: int) -> int:
    return int(hashlib.sha256(seed.encode()).hexdigest(), 16) % n
