// Screenshot every element with [data-out] in an HTML file. Usage: node shoot.cjs page.html outdir [jpeg|png]
const { chromium } = require("playwright");
const { mkdirSync } = require("node:fs");
const { resolve, join } = require("node:path");

(async () => {
  const [, , page, outdir, fmt = "jpeg"] = process.argv;
  mkdirSync(outdir, { recursive: true });
  const browser = await chromium.launch();
  const p = await (await browser.newContext({ deviceScaleFactor: 1 })).newPage();
  await p.goto("file://" + resolve(page), { waitUntil: "networkidle" });
  await p.evaluate(async () => { await document.fonts.ready; });
  const els = await p.$$("[data-out]");
  for (const el of els) {
    const opts = { path: join(outdir, await el.getAttribute("data-out")), type: fmt };
    if (fmt === "jpeg") opts.quality = 86;
    await el.screenshot(opts);
  }
  await browser.close();
  console.log(`rendered ${els.length} images into ${outdir}`);
})().catch((e) => { console.error(e); process.exit(1); });
