"""Mizaj 8-month financial model (Nov 2026 - Jun 2027). python ops/model.py -> prints tables, writes ops/model.json

All money in PKR. Assumptions are explicit below so the weekly COO review can update them with actuals.
"""
import json
from pathlib import Path

MONTHS = ["Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun"]

BASE = {
    # completed tests per month (organic social + SEO + Milan invites + some paid)
    "tests": [4000, 10000, 16000, 16000, 24000, 30000, 36000, 40000],
    # share of test-takers who buy anything (research: 0.5-2% for 16P-style, 2-5% for quiz funnels)
    "buyer_rate": [0.012, 0.014, 0.018, 0.018, 0.020, 0.021, 0.022, 0.022],
    "aov": 950,  # mix of 599 full, 1,999 bundle, 1,299 Milan, 999 career, 299 palm
    # B2B: schools (paid classes) and team workshops
    "schools": [0, 0, 1, 2, 3, 4, 4, 3], "students_per_school": 150, "per_student": 380,
    "workshops": [0, 0, 0, 1, 1, 1, 2, 1], "workshop_fee": 150000, "team_packs": [0, 0, 1, 1, 2, 2, 3, 3], "team_pack": 18000,
    "sponsorship": [0, 0, 0, 25000, 50000, 75000, 75000, 100000],
    # costs
    "ads": [40000, 80000, 120000, 80000, 160000, 200000, 220000, 220000],
    "creators_pct": 0.08,  # creator commissions on B2C revenue (affiliate codes, 15-20% on their sales)
    "va": [0, 30000, 35000, 35000, 40000, 40000, 45000, 45000],  # social/ops assistant
    "gateway_pct": 0.025, "gateway_share": [0.0, 0.3, 0.6, 0.6, 0.65, 0.7, 0.7, 0.7],
    "wht_pct": 0.01,  # withholding on digital sales (research: 0.25-2%)
    "ai": [5000, 10000, 15000, 15000, 20000, 25000, 25000, 25000],
    "tools": [3000, 6000, 6000, 6000, 8000, 8000, 8000, 8000],  # email, domain, misc SaaS
    "facilitator_pct": 0.4,  # partner trainer's share of workshops
    "one_off": [60000, 0, 0, 0, 0, 0, 0, 0],  # registration, NTN, trademark filing
}


def scenario(name, traffic=1.0, conv=1.0, b2b=1.0, ads=1.0):
    a = BASE
    rows, cum = [], 0
    for i, m in enumerate(MONTHS):
        tests = round(a["tests"][i] * traffic)
        orders = round(tests * a["buyer_rate"][i] * conv)
        b2c = orders * a["aov"]
        schools = round(a["schools"][i] * b2b)
        school_rev = schools * a["students_per_school"] * a["per_student"]
        workshops = round(a["workshops"][i] * b2b)
        team_rev = workshops * a["workshop_fee"] + round(a["team_packs"][i] * b2b) * a["team_pack"]
        spons = round(a["sponsorship"][i] * b2b)
        revenue = b2c + school_rev + team_rev + spons
        cost = (round(a["ads"][i] * ads) + b2c * a["creators_pct"] + a["va"][i]
                + b2c * a["gateway_share"][i] * a["gateway_pct"] + revenue * a["wht_pct"]
                + a["ai"][i] + a["tools"][i] + workshops * a["workshop_fee"] * a["facilitator_pct"] + a["one_off"][i])
        profit = revenue - cost
        cum += profit
        rows.append({"month": m, "tests": tests, "orders": orders, "b2c": round(b2c), "schools": schools,
                     "b2b": round(school_rev + team_rev), "sponsor": spons, "revenue": round(revenue),
                     "costs": round(cost), "profit": round(profit), "cumulative": round(cum)})
    return {"name": name, "rows": rows, "total_revenue": sum(r["revenue"] for r in rows),
            "total_profit": round(cum), "june_profit": rows[-1]["profit"]}


SCENARIOS = [
    scenario("Conservative", traffic=0.55, conv=0.8, b2b=0.5, ads=0.7),
    scenario("Base", 1.0, 1.0, 1.0, 1.0),
    scenario("Upside", traffic=1.5, conv=1.15, b2b=1.4, ads=1.3),
]

if __name__ == "__main__":
    for s in SCENARIOS:
        print(f"\n== {s['name']}: revenue PKR {s['total_revenue']:,} | profit PKR {s['total_profit']:,} | June profit PKR {s['june_profit']:,}")
        print(f"{'':4}{'tests':>8}{'orders':>8}{'B2C':>11}{'B2B':>10}{'revenue':>11}{'costs':>10}{'profit':>11}{'cum':>12}")
        for r in s["rows"]:
            print(f"{r['month']:4}{r['tests']:>8,}{r['orders']:>8,}{r['b2c']:>11,}{r['b2b']:>10,}{r['revenue']:>11,}{r['costs']:>10,}{r['profit']:>11,}{r['cumulative']:>12,}")
    Path(__file__).with_name("model.json").write_text(json.dumps({"assumptions": BASE, "scenarios": SCENARIOS}, indent=1))
