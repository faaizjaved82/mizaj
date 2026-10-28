"""Build the static site into dist/.  Usage: python build.py

Renders every public page from site/templates + content/, copies site/static,
publishes the question banks, and writes sitemap.xml, robots.txt and llms.txt.
"""
from __future__ import annotations

import json
import shutil
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "server"))

from mizaj import content, reports  # noqa: E402
from mizaj.config import settings  # noqa: E402
from mizaj.web import env, render  # noqa: E402

DIST = settings.dist_dir
TODAY = date.today().isoformat()
pages: list[tuple[str, float]] = []


def pair_slug(a: str, b: str) -> str:
    return "-".join(sorted([a.lower(), b.lower()]))


env().globals["pair_slug"] = pair_slug


def write(url: str, html: str, priority: float = 0.5, sitemap: bool = True) -> None:
    path = DIST / url.strip("/") / "index.html" if url.endswith("/") else DIST / url.lstrip("/")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
    if sitemap:
        pages.append((url, priority))


TESTS = {
    "personality": {
        "id": "personality", "count": 48, "eyebrow": "Free personality test · 16 Mizaj types",
        "title": "Which of the 16 Mizaj types are you?",
        "lead": "48 quick statements about everyday life. Agree or disagree, go with your gut, and find your type in about 8 minutes.",
        "bullets": ["No sign-up, completely free", "Questions in English or Urdu", "Your type, strengths, watch-outs and a share card"],
        "note": "There are no right or wrong answers. Answer as you usually are, not as you'd like to be.",
    },
    "mizaj": {
        "id": "mizaj", "count": 24, "eyebrow": "Asli Mizaj test · Unani temperament",
        "title": "Garam ya thanda? Find your Asli Mizaj",
        "lead": "24 questions about your body, sleep, appetite and moods, based on the classical Unani signs of temperament described by Ibn Sina.",
        "bullets": ["4 minutes, free", "Damvi, Safravi, Balghami or Saudavi", "Foods and habits that traditionally suit you"],
        "note": "Traditional wellness wisdom for self-understanding, not a medical diagnosis.",
    },
    "interests": {
        "id": "interests", "count": 24, "eyebrow": "Career Compass · interest code",
        "title": "What kind of work would you actually enjoy?",
        "lead": "24 activities. Tell us which ones you'd enjoy and get your 3-letter interest code, matched to streams, degrees and careers in Pakistan.",
        "bullets": ["4 minutes, free", "For students from grade 8 to university", "Works even better with your personality type"],
        "note": "Think about whether you'd enjoy the activity, not whether you're good at it yet.",
    },
}

FAQS = [
    ("Is the test really free?", "Yes. Every test and your basic result are free forever, with no sign-up. If you want to go deeper, you can unlock a full report with a one-time payment. There are no subscriptions."),
    ("How accurate is it?", "Our tests are carefully written and scored, but no personality test is a diagnosis. Think of your result as a mirror and a conversation starter. Most people find their type describes them well; if yours feels off, retake it on a calm day and answer as you usually are."),
    ("Is this the MBTI?", "No. Mizaj uses its own questions, its own 16 type names and adds Unani temperament. We use the familiar four-letter codes, which describe Jungian preferences, but we are independent and not affiliated with the Myers & Briggs Foundation."),
    ("What is mizaj in Unani medicine?", "Tibb-e-Unani describes four temperaments based on warmth and moisture: Damvi (warm-moist), Safravi (warm-dry), Balghami (cool-moist) and Saudavi (cool-dry). They shape energy, moods and which foods suit you. It's traditional wellness wisdom, not medical advice."),
    ("Can I take it in Urdu?", "Yes. Every question is available in Urdu; switch with the اردو button at any time."),
    ("How do I pay?", "Raast, JazzCash, Easypaisa or bank transfer with zero fees, or debit/credit card. Outside Pakistan, international cards in USD."),
    ("What about my privacy?", "No sign-up needed. We store your answers to show your result, we never sell your data, and palm photos are read once and deleted. You can ask us to delete everything at any time."),
    ("Can schools or companies use Mizaj?", "Yes. We offer Career Compass for schools and Mizaj for Teams for companies, with bulk codes, summaries and workshops."),
]

LEGAL = {
    "privacy": ("Privacy policy", [
        ("Who we are", "Mizaj (mizaj.pk) is a Pakistani self-discovery service. Contact: " + settings.support_email + "."),
        ("What we collect", "Your test answers and results; a name if you give one; an email or WhatsApp number if you choose to save your result or buy a report; payment details you enter (transaction ID and sender name; card payments are handled entirely by our payment provider and we never see card numbers); and basic usage events (pages viewed, tests started and finished) to improve the site."),
        ("Palm photos", "If you use AI palm reading, your photo is resized on your phone, sent securely to our AI provider (Anthropic) to generate the reading, and then discarded. We do not store palm images. We keep only the text of your reading."),
        ("How we use it", "To show your results and reports, deliver what you buy, reply to you, prevent fraud, and understand which parts of Mizaj help people. If you give an email or WhatsApp number, we may send you your result link and occasional Mizaj updates; you can opt out at any time."),
        ("What we never do", "We never sell your personal data. We never share your individual results with schools, employers or anyone else unless you took the test through their code, and even then they see only what the programme describes."),
        ("Cookies", "We use a small cookie to remember which results are yours on this device, and optional analytics. You can clear cookies at any time."),
        ("Keeping and deleting data", "We keep results so you can come back to them. Email us and we'll delete your profile, results and orders (we may keep minimal payment records the law requires)."),
        ("Children", "Mizaj is for people aged 13 and over. Students under 18 should use Mizaj with a parent's or school's guidance."),
        ("Changes", "We'll update this page if anything changes and show the date at the top."),
    ]),
    "terms": ("Terms of use", [
        ("What Mizaj is", "Mizaj offers personality, temperament and interest tests and reports for self-reflection and entertainment. They are not psychological, psychiatric or medical assessments, diagnoses or treatment, and should not be the only basis for important decisions such as marriage, careers, hiring or health."),
        ("Temperament and wellness", "Mizaj temperament guidance reflects traditional Unani wellness wisdom for general interest. It is not medical advice. Consult a qualified doctor or hakeem before changing your diet or routine, especially if you are pregnant, unwell or taking medicine."),
        ("Fun features", "Burj (zodiac), Ilm-e-Adad (numerology) and palm reading are for entertainment only. They do not predict the future."),
        ("Payments", "Paid reports are one-time digital purchases in Pakistani rupees (or US dollars outside Pakistan). There are no subscriptions. Reports unlock after payment is confirmed. See our refund policy."),
        ("Fair use", "Don't misuse the service, attack it, scrape it, resell reports or upload images of other people's hands without their permission. Reports are for personal use; schools and companies need a Mizaj programme."),
        ("Our content", "All test questions, type names and report text are original Mizaj content, protected by copyright. Mizaj is independent and not affiliated with the Myers & Briggs Foundation; MBTI and Myers-Briggs are its trademarks."),
        ("Liability", "We work hard to make Mizaj accurate and helpful but provide it as is. To the extent the law allows, our total liability is limited to what you paid us in the last 12 months."),
        ("Law", "These terms are governed by the laws of Pakistan."),
    ]),
    "refunds": ("Refund policy", [
        ("7-day refund promise", "If a paid report doesn't feel worth it, message us within 7 days of purchase on WhatsApp or by email with your order details and we'll refund you in full to the account you paid from. No long questions."),
        ("Payment problems", "If you paid but your report didn't unlock, or you were charged twice, contact us and we'll fix it or refund the duplicate right away."),
        ("How long refunds take", "Wallet and Raast refunds are usually sent within 2 working days. Card refunds depend on your bank and can take 5 to 10 working days."),
        ("Bulk and school purchases", "Codes bought for schools and companies can be refunded if they haven't been used, within 30 days."),
    ]),
}


def build() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(ROOT / "site" / "static", DIST)
    qdir = DIST / "data" / "q"
    qdir.mkdir(parents=True)
    for t in TESTS:
        (qdir / f"{t}.json").write_text(json.dumps(content.questions(t), ensure_ascii=False), encoding="utf-8")

    types = [content.type_summary(c) for c in content.TYPE_CODES]
    full_types = {c: content.type_profile(c) for c in content.TYPE_CODES}
    mizaj = [content.mizaj_summary(k) for k in content.MIZAJ_KEYS]

    write("/", render("home.html", types=types, mizaj=mizaj, faqs=FAQS, canonical="/",
                      title=None, description="Free personality test, Unani mizaj test, couple match and Career Compass, made for Pakistan. In English and Urdu."), 1.0)
    write("/tests/", render("tests.html", title="All tests", canonical="/tests/"), 0.8)
    for t, cfg in TESTS.items():
        write(f"/test/{t}/", render("test.html", test=cfg, title=cfg["title"], canonical=f"/test/{t}/",
                                     description=cfg["lead"]), 0.9)
    write("/career/", render("career.html", title="Career Compass for Pakistani students", canonical="/career/",
                             description="Which stream, degree and career fits you? A free interest test for Pakistani students and parents."), 0.8)
    write("/milan/", render("milan_landing.html", title="Mizaj Milan: couple and rishta compatibility", canonical="/milan/",
                            description="Test your match with your spouse, rishta or best friend. Free score, full report for both."), 0.9)
    write("/palm/", render("palm.html", title="AI palm reading", canonical="/palm/",
                           description="Snap your palm and get a playful AI palm reading. For fun; photos never stored."), 0.7)
    write("/burj/", render("burj.html", title="Burj: your zodiac sign and personality type", canonical="/burj/",
                           disclaimer=content.zodiac().get("disclaimer"),
                           description="Your zodiac sign (burj) meets your personality type. For fun."), 0.6)
    num = content.numerology()
    write("/adad/", render("adad.html", title="Ilm-e-Adad: the Abjad number of your name", canonical="/adad/",
                           intro=num.get("intro"), disclaimer=num.get("disclaimer"),
                           description="Find the Abjad (Ilm-e-Adad) number of your name in Urdu or English. For fun."), 0.6)

    write("/types/", render("types_index.html", types=types, title="The 16 Mizaj personality types", canonical="/types/",
                            description="All 16 Mizaj personality types, from Mansooba-saaz to Mehfil ki Jaan."), 0.8)
    for c, t in full_types.items():
        write(f"/types/{c.lower()}/", render("type.html", t=t, title=f"{c} personality: {t['name']}, {t['name_en']}",
                                             canonical=f"/types/{c.lower()}/", description=t["tagline"],
                                             og_image=f"{settings.site_url}/og/types/{c.lower()}.png"), 0.8)
    write("/mizaj/", render("mizaj_index.html", mizaj=mizaj, title="The 4 Unani temperaments (mizaj)", canonical="/mizaj/",
                            description="Damvi, Safravi, Balghami, Saudavi: the four Unani temperaments explained."), 0.8)
    for k in content.MIZAJ_KEYS:
        m = content.mizaj_profile(k)
        write(f"/mizaj/{k}/", render("mizaj_page.html", m=m, title=f"{m['name']} mizaj ({m['quality']})",
                                     canonical=f"/mizaj/{k}/", description=m["tagline"],
                                     og_image=f"{settings.site_url}/og/mizaj/{k}.png"), 0.8)

    blocks = content.compat_dimensions()
    scores = {}
    for i, a in enumerate(content.TYPE_CODES):
        for b in content.TYPE_CODES[i:]:
            dims, total = [], 0.0
            for j, d in enumerate(content.DIMENSIONS):
                key = a[j] * 2 if a[j] == b[j] else content.DIMENSIONS[d]["a"] + content.DIMENSIONS[d]["b"]
                blk = blocks[d][key]
                total += reports.DIM_WEIGHTS[d] * blk["score"]
                dims.append({"label": content.DIMENSIONS[d]["label"], "a": a[j], "b": b[j], **blk})
            slug, score = pair_slug(a, b), round(total)
            scores[slug] = score
            ta, tb = content.type_summary(a), content.type_summary(b)
            write(f"/compatibility/{slug}/", render("compat_pair.html", a=ta, b=tb, dims=dims, score=score,
                                                     title=f"{a} and {b} compatibility", canonical=f"/compatibility/{slug}/",
                                                     description=f"How a {ta['name']} ({a}) and a {tb['name']} ({b}) connect and clash, in love, marriage and friendship."), 0.5)
    write("/compatibility/", render("compat_index.html", scores=scores, title="16-type compatibility chart",
                                    canonical="/compatibility/", description="Compatibility of all 16 Mizaj types."), 0.7)

    write("/pricing/", render("pricing.html", title="Pricing", canonical="/pricing/"), 0.7)
    write("/schools/", render("schools.html", title="Career Compass for schools", canonical="/schools/",
                              description="Career guidance for every student: interest code, personality type and stream fit, with parent reports."), 0.7)
    write("/teams/", render("teams.html", title="Mizaj for teams", canonical="/teams/",
                            description="Team maps, reports and workshops that make teams work better."), 0.6)
    write("/about/", render("about.html", title="Our story", canonical="/about/"), 0.5)
    write("/contact/", render("contact.html", title="Contact", canonical="/contact/"), 0.4)
    for slug, (heading, sections) in LEGAL.items():
        write(f"/{slug}/", render("legal.html", heading=heading, sections=sections, updated="28 October 2026",
                                  title=heading, canonical=f"/{slug}/"), 0.2)
    write("/404.html", render("404.html", title="Not found", noindex=True), sitemap=False)

    # Social media files: public so the Graph API can fetch them; all.zip is for posting on TikTok by hand.
    media = ROOT / "social" / "media"
    if media.exists():
        import zipfile
        for post in sorted(p for p in media.iterdir() if p.is_dir()):
            dest = DIST / "s" / post.name
            shutil.copytree(post, dest)
            with zipfile.ZipFile(dest / "all.zip", "w", zipfile.ZIP_STORED) as z:
                for img in sorted(post.glob("[0-9][0-9].jpg")):
                    z.write(img, img.name)

    urls = "".join(f"<url><loc>{settings.site_url}{u}</loc><lastmod>{TODAY}</lastmod><priority>{p}</priority></url>" for u, p in pages)
    (DIST / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>')
    (DIST / "robots.txt").write_text(f"User-agent: *\nDisallow: /admin\nDisallow: /api/\nDisallow: /order/\nDisallow: /p/\nSitemap: {settings.site_url}/sitemap.xml\n")
    llms = [f"# Mizaj (mizaj.pk)", "", "> Pakistan's self-discovery platform: a free 16-type personality test, the Unani 'Asli Mizaj' temperament test, Mizaj Milan couple/rishta compatibility, and Career Compass for students. English and Urdu.", "",
            "## Tests", f"- [Personality test]({settings.site_url}/test/personality/): 48 questions, 16 Mizaj types",
            f"- [Asli Mizaj test]({settings.site_url}/test/mizaj/): Unani temperament (Damvi, Safravi, Balghami, Saudavi)",
            f"- [Career Compass]({settings.site_url}/career/): RIASEC interest code matched to Pakistani streams and careers",
            f"- [Mizaj Milan]({settings.site_url}/milan/): couple and rishta compatibility", "", "## The 16 types"]
    llms += [f"- [{t['code']} {t['name']} ({t['name_en']})]({settings.site_url}/types/{t['code'].lower()}/): {t['tagline']}" for t in types]
    llms += ["", "## The 4 mizaj"] + [f"- [{m['name']} ({m['quality']})]({settings.site_url}/mizaj/{m['key']}/): {m['tagline']}" for m in mizaj]
    (DIST / "llms.txt").write_text("\n".join(llms) + "\n", encoding="utf-8")
    print(f"built {len(pages)} pages into {DIST}")


if __name__ == "__main__":
    build()
