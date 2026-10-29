// End-to-end check in a real browser at phone size. Usage: node tools/e2e.cjs http://127.0.0.1:8300 outdir ADMIN_TOKEN
const { chromium, devices } = require("playwright");
const { mkdirSync } = require("node:fs");

const [, , BASE, OUT, ADMIN] = process.argv;
mkdirSync(OUT, { recursive: true });
const errors = [];
let step = 0;
const shot = async (page, name, full = true) => { step += 1; await page.screenshot({ path: `${OUT}/${String(step).padStart(2, "0")}-${name}.png`, fullPage: full }); };
const ok = (cond, msg) => { if (!cond) throw new Error("FAILED: " + msg); console.log("✓", msg); };

async function takeTest(page, test, pick) {
  await page.goto(`${BASE}/test/${test}/`);
  await page.click("[data-begin]");
  for (let i = 0; i < 60; i++) {
    if (await page.isVisible('[data-step="end"]')) break;
    const btns = await page.$$("[data-answers] button");
    await btns[pick(i, btns.length)].click();
    await page.waitForTimeout(220);
  }
  ok(await page.isVisible('[data-step="end"]'), `${test} test reaches the end screen`);
}

(async () => {
  const browser = await chromium.launch();
  const phone = devices["iPhone 13"];
  // Pakistan time zone: the buyer gets PKR prices and the manual Raast/JazzCash flow tested below.
  const ctx = await browser.newContext({ ...phone, timezoneId: "Asia/Karachi" });
  const page = await ctx.newPage();
  page.on("console", (m) => { if (m.type() === "error" && !/fonts\.g|favicon|apple-touch|Failed to load resource/.test(m.text())) errors.push(m.text()); });
  page.on("pageerror", (e) => errors.push(String(e)));

  await page.goto(BASE + "/");
  await shot(page, "home");
  ok((await page.textContent("h1")).includes("mizaj"), "home renders hero");

  // personality test: answers vary so the result is a real mix
  await takeTest(page, "personality", (i, n) => [3, 1, 4, 0, 3, 2, 4, 1][i % 8] % n);
  await page.fill("#qname", "Ayesha");
  await shot(page, "test-end", false);
  await Promise.all([page.waitForURL(/\/p\//), page.click("[data-submit]")]);
  await page.waitForLoadState("networkidle");
  await shot(page, "result");
  const pid = page.url().split("/p/")[1].split("#")[0];
  ok(await page.isVisible("[data-buy='full']"), "result page offers the full report");

  // mizaj test attaches to the same profile
  await takeTest(page, "mizaj", (i, n) => (i * 7) % n);
  await Promise.all([page.waitForURL(/\/p\//), page.click("[data-submit]")]);
  ok(page.url().includes(pid), "mizaj result joins the same profile");
  await page.goto(`${BASE}/p/${pid}#mizaj`);
  await shot(page, "result-with-mizaj");

  // buy: manual Raast/JazzCash flow
  await page.click(".sticky-buy [data-buy='full']");
  await page.waitForURL(/\/order\//);
  await shot(page, "checkout");
  const orderUrl = page.url();
  await page.fill("#tid", "33445566778");
  await page.fill("#sender", "Ayesha K");
  await page.fill("#oemail", "ayesha@example.com");
  await page.click("[data-proof] button[type=submit]");
  await page.waitForSelector('[data-state="proof"]:not(.hidden)');
  await shot(page, "verifying", false);

  // owner approves from the admin dashboard
  const admin = await (await browser.newContext()).newPage();
  await admin.goto(BASE + "/admin");
  await admin.fill("#token", ADMIN);
  await Promise.all([admin.waitForURL(BASE + "/admin"), admin.click("button[type=submit]")]);
  await admin.screenshot({ path: `${OUT}/admin.png`, fullPage: true });
  await admin.click("form[action^='/admin/order/'] button");
  ok((await admin.textContent("h1")).includes("Done"), "owner approves the payment");

  // buyer's page unlocks by itself (polling) and lands on the report
  await page.waitForURL(/#report/, { timeout: 20000 });
  await page.waitForLoadState("networkidle");
  ok(await page.isVisible("text=Your 6 superpowers"), "premium report is visible after approval");
  await shot(page, "full-report");

  // Mizaj Milan invite, partner on another phone
  await page.goto(BASE + "/milan/");
  await page.click("[data-milan-create]");
  await page.waitForSelector("[data-milan-out]:not(.hidden)");
  const invite = (await page.textContent("[data-milan-link]")).trim().replace(/^https?:\/\/[^/]+/, BASE);
  await shot(page, "milan-invite", false);
  const partner = await (await browser.newContext({ ...phone })).newPage();
  partner.on("pageerror", (e) => errors.push(String(e)));
  await partner.goto(invite);
  await shot(partner, "milan-landing", false);
  await partner.click("[data-milan-start]");
  await partner.waitForURL(/test\/personality/);
  ok(await partner.isVisible("[data-milan-banner]:not(.hidden)"), "invitee sees the Milan banner");
  await partner.click("[data-begin]");
  for (let i = 0; i < 60; i++) {
    if (await partner.isVisible('[data-step="end"]')) break;
    const btns = await partner.$$("[data-answers] button");
    await btns[[1, 3, 0, 4, 2, 4][i % 6]].click();
    await partner.waitForTimeout(200);
  }
  await partner.fill("#qname", "Bilal");
  await Promise.all([partner.waitForURL(/\/milan\//), partner.click("[data-submit]")]);
  ok(await partner.isVisible("text=Overall Mizaj Milan score"), "partner lands on the match page");
  await shot(partner, "milan-match");

  // fun tools
  await page.goto(BASE + "/burj/");
  await page.fill("#dob", "2001-08-05");
  await page.click("#burj-form button[type=submit]");
  await page.waitForSelector("#burj-out:not(.hidden)");
  await shot(page, "burj");
  await page.goto(BASE + "/adad/");
  await page.fill("#aname", "عائشہ");
  await page.click("#adad-form button[type=submit]");
  await page.waitForSelector("#adad-out:not(.hidden)");
  await shot(page, "adad");

  // shared link seen by a stranger
  const stranger = await (await browser.newContext({ ...phone })).newPage();
  await stranger.goto(`${BASE}/p/${pid}`);
  ok(await stranger.isVisible("[data-compare]"), "stranger sees 'Compare with Ayesha'");
  ok(!(await stranger.isVisible("text=Your 6 superpowers")), "stranger does not see the paid report");
  await shot(stranger, "shared-result");

  // B2B lead
  await page.goto(BASE + "/schools/");
  await page.fill("[data-lead] [name=name]", "Mrs Khan");
  await page.fill("[data-lead] [name=org]", "Test School");
  await page.fill("[data-lead] [name=phone]", "03001112222");
  await page.click("[data-lead] button[type=submit]");
  await page.waitForSelector("[data-ok]:not(.hidden)");
  ok(true, "school lead form submits");
  await shot(page, "schools");

  for (const p of ["/types/", "/types/infj/", "/mizaj/saudavi/", "/compatibility/", "/compatibility/estp-infj/", "/pricing/", "/palm/", "/career/", "/teams/", "/about/", "/privacy/"]) {
    const r = await page.goto(BASE + p);
    ok(r.status() === 200, `page ${p} loads`);
  }
  await page.goto(BASE + "/types/infj/");
  await shot(page, "type-page");
  await page.goto(BASE + "/mizaj/saudavi/");
  await shot(page, "mizaj-page");
  await page.goto(BASE + "/pricing/");
  await shot(page, "pricing");

  const desktop = await (await browser.newContext({ viewport: { width: 1366, height: 900 } })).newPage();
  await desktop.goto(BASE + "/");
  await desktop.screenshot({ path: `${OUT}/desktop-home.png`, fullPage: true });

  await browser.close();
  if (errors.length) { console.log("Browser errors:\n" + errors.join("\n")); process.exit(1); }
  console.log("ALL E2E CHECKS PASSED");
})().catch((e) => { console.error(e); console.log("Browser errors:\n" + errors.join("\n")); process.exit(1); });
