/* Mizaj front-end. No framework: fast on low-end phones. */
(() => {
  "use strict";
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const store = {
    get(k) { try { return JSON.parse(localStorage.getItem(k)); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* private mode */ } },
    del(k) { try { localStorage.removeItem(k); } catch (e) { /* ignore */ } },
  };
  const me = () => store.get("mz_me") || {};
  const setMe = (patch) => store.set("mz_me", Object.assign(me(), patch));
  const params = new URLSearchParams(location.search);

  async function api(path, body, opts = {}) {
    const init = { method: body ? "POST" : "GET", headers: {}, credentials: "same-origin" };
    if (body instanceof FormData) init.body = body;
    else if (body) { init.headers["Content-Type"] = "application/json"; init.body = JSON.stringify(body); }
    const res = await fetch(path, Object.assign(init, opts));
    let data = {};
    try { data = await res.json(); } catch (e) { /* non-JSON */ }
    if (!res.ok) throw new Error(data.error || "Something went wrong. Please try again.");
    return data;
  }

  function track(name, props) {
    const body = JSON.stringify({ name, props: props || {}, path: location.pathname, ref: document.referrer, profile_id: me().pid || null });
    try {
      if (navigator.sendBeacon) navigator.sendBeacon("/api/events", new Blob([body], { type: "application/json" }));
      else fetch("/api/events", { method: "POST", body, headers: { "Content-Type": "application/json" }, keepalive: true });
    } catch (e) { /* ignore */ }
    try { if (window.fbq && ["test_complete", "checkout_view", "share_click"].includes(name)) window.fbq("trackCustom", name, props || {}); } catch (e) { /* ignore */ }
  }

  function toast(msg) {
    const t = document.createElement("div");
    t.className = "toast"; t.textContent = msg; document.body.appendChild(t);
    setTimeout(() => t.remove(), 2600);
  }

  function source() {
    let src = store.get("mz_src");
    if (!src) {
      src = { ref: document.referrer && !document.referrer.includes(location.host) ? document.referrer.slice(0, 150) : "" };
      ["utm_source", "utm_medium", "utm_campaign"].forEach((k) => { if (params.get(k)) src[k] = params.get(k).slice(0, 60); });
      if (params.get("ref")) src.utm_source = src.utm_source || ("ref-" + params.get("ref").slice(0, 40));
      store.set("mz_src", src);
    }
    return src;
  }

  async function copyText(text) {
    try { await navigator.clipboard.writeText(text); toast("Copied ✓"); }
    catch (e) {
      const ta = document.createElement("textarea"); ta.value = text; document.body.appendChild(ta); ta.select();
      try { document.execCommand("copy"); toast("Copied ✓"); } catch (e2) { toast(text); }
      ta.remove();
    }
  }

  function busy(btn, on) {
    if (!btn) return;
    if (on) { btn.dataset.label = btn.innerHTML; btn.disabled = true; btn.innerHTML = '<span class="spinner"></span>'; }
    else { btn.disabled = false; if (btn.dataset.label) btn.innerHTML = btn.dataset.label; }
  }

  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])); }

  // ---------- global bits ----------
  source();
  track("page_view");
  document.addEventListener("click", (e) => {
    const cta = e.target.closest("[data-cta]");
    if (cta) track("cta_click", { cta: cta.dataset.cta });
    const cp = e.target.closest("[data-copy]");
    if (cp) { e.preventDefault(); copyText(cp.dataset.copy); }
    const cpf = e.target.closest("[data-copy-from]");
    if (cpf) { e.preventDefault(); const el = $(cpf.dataset.copyFrom); if (el) copyText(el.textContent.trim()); }
  });

  const counter = $("[data-tests-taken]");
  if (counter) {
    const wrap = counter.closest("span"); if (wrap) wrap.classList.add("hidden");
    api("/api/stats/public").then((d) => {
      if (d.tests_taken >= 100) { counter.textContent = d.tests_taken.toLocaleString("en-PK"); wrap && wrap.classList.remove("hidden"); }
    }).catch(() => {});
  }

  // ---------- quiz ----------
  const quiz = $("#quiz");
  if (quiz) initQuiz(quiz);

  async function initQuiz(root) {
    const test = root.dataset.test;
    const key = "mz_quiz_" + test;
    let bank;
    try { bank = await (await fetch(root.dataset.src)).json(); } catch (e) { toast("Couldn't load the test. Please refresh."); return; }
    const items = bank.items;
    let st = store.get(key);
    if (!st || Date.now() - (st.t || 0) > 86400000 * 2) st = { answers: {}, idx: 0, lang: "en" };
    const milan = params.get("milan");
    if (milan) {
      st.milan = milan;
      const b = $("[data-milan-banner]", root);
      if (b) { b.classList.remove("hidden"); $("[data-milan-from]", b).textContent = params.get("from") || "Someone"; }
    }
    const save = () => { st.t = Date.now(); store.set(key, st); };
    const steps = { intro: $('[data-step="intro"]', root), questions: $('[data-step="questions"]', root), end: $('[data-step="end"]', root) };
    const show = (name) => { Object.entries(steps).forEach(([k, el]) => el.classList.toggle("hidden", k !== name)); window.scrollTo(0, 0); };
    const bar = $("[data-bar]", root), count = $("[data-count]", root), qtext = $("[data-qtext]", root), ans = $("[data-answers]", root);
    const marks = new Set();

    $$("[data-lang]", root).forEach((b) => b.addEventListener("click", () => {
      st.lang = b.dataset.lang; save(); syncLang(); if (!steps.questions.classList.contains("hidden")) render();
      track("lang_switch", { lang: st.lang, test });
    }));
    function syncLang() { $$("[data-lang]", root).forEach((b) => b.classList.toggle("on", b.dataset.lang === st.lang)); }
    syncLang();

    const begin = $("[data-begin]", root);
    if (Object.keys(st.answers).length && st.idx > 0) begin.textContent = "Continue where I left off →";
    begin.addEventListener("click", () => { track("test_start", { test }); show("questions"); render(); });

    function render() {
      const it = items[st.idx];
      const ur = st.lang === "ur";
      bar.style.width = Math.round((100 * st.idx) / items.length) + "%";
      count.textContent = st.idx + 1 + " / " + items.length;
      qtext.textContent = ur ? it.ur : it.en;
      qtext.classList.toggle("ur", ur);
      qtext.setAttribute("dir", ur ? "rtl" : "ltr");
      const opts = it.options ? it.options.map((o, i) => ({ v: i, en: o.en, ur: o.ur })) : bank.scale.map((s) => ({ v: s.value, en: s.en, ur: s.ur }));
      ans.className = (it.options ? "opts" : "scale") + (ur ? " ur" : "");
      ans.innerHTML = "";
      opts.forEach((o, i) => {
        const b = document.createElement("button");
        b.type = "button";
        b.innerHTML = '<span class="dot"></span><span></span>';
        b.lastChild.textContent = ur ? o.ur : o.en;
        if (st.answers[it.id] === o.v) b.classList.add("sel");
        b.addEventListener("click", () => choose(it, o.v, b));
        b.dataset.k = String(i + 1);
        ans.appendChild(b);
      });
      $("[data-back]", root).style.visibility = st.idx === 0 ? "hidden" : "visible";
    }

    function choose(it, v, btn) {
      st.answers[it.id] = v;
      $$("button", ans).forEach((b) => b.classList.remove("sel"));
      btn.classList.add("sel");
      const pct = Math.round((100 * (st.idx + 1)) / items.length);
      [25, 50, 75].forEach((m) => { if (pct >= m && !marks.has(m)) { marks.add(m); track("test_progress", { test, pct: m }); } });
      setTimeout(() => {
        if (st.idx < items.length - 1) { st.idx += 1; save(); render(); }
        else { save(); bar.style.width = "100%"; finish(); }
      }, 160);
    }

    $("[data-back]", root).addEventListener("click", () => { if (st.idx > 0) { st.idx -= 1; save(); render(); } });
    document.addEventListener("keydown", (e) => {
      if (steps.questions.classList.contains("hidden")) return;
      const b = $(`[data-answers] button[data-k="${e.key}"]`, root);
      if (b) b.click();
    });

    function finish() {
      show("end");
      const nm = $("#qname"); if (nm && me().name) nm.value = me().name;
    }

    $("[data-submit]", root).addEventListener("click", async (e) => {
      const btn = e.currentTarget, err = $("[data-err]", root);
      err.textContent = "";
      const missing = items.filter((it) => !(it.id in st.answers));
      if (missing.length > items.length * 0.1) {
        st.idx = items.indexOf(missing[0]); save(); show("questions"); render();
        toast("A few questions were skipped. Please answer them."); return;
      }
      busy(btn, true);
      const m = me();
      const name = ($("#qname").value || "").trim();
      try {
        const res = await api("/api/results", Object.assign({
          test, answers: st.answers, name, milan: st.milan || null,
          profile_id: st.milan ? null : m.pid, key: st.milan ? null : m.key,
        }, source()));
        const patch = { pid: res.profile_id, key: res.key, name: name || m.name };
        if (test === "personality") patch.type = res.outcome;
        if (test === "mizaj") patch.mizaj = res.outcome;
        if (st.milan && res.profile_id !== m.pid) store.set("mz_me", patch); else setMe(patch);
        store.del(key);
        track("test_complete", { test });
        location.href = params.get("then") === "milan" ? "/milan/?ready=1" : res.redirect;
      } catch (ex) { err.textContent = ex.message; busy(btn, false); }
    });

    if (params.get("start") === "1") begin.click();
  }

  // ---------- buy buttons (result, milan, palm) ----------
  function ownerCtx(el) {
    const c = el.closest("[data-profile][data-key]") || $("#result") || $("#milan-view") || $("#palm-view");
    const m = me();
    if (c && c.dataset.key) return { pid: c.dataset.profile || c.dataset.member, key: c.dataset.key };
    if (c && c.dataset.member) return { pid: c.dataset.member, key: c.dataset.key || (m.pid === c.dataset.member ? m.key : "") };
    return { pid: m.pid, key: m.key };
  }
  $$("[data-buy]").forEach((b) => b.addEventListener("click", async () => {
    const ctx = ownerCtx(b);
    busy(b, true);
    try {
      const res = await api("/api/orders", { profile_id: ctx.pid, key: ctx.key, product: b.dataset.buy, pair_id: b.dataset.pair || null });
      track("checkout_view", { product: b.dataset.buy });
      location.href = res.url;
    } catch (e) { toast(e.message); busy(b, false); }
  }));

  // ---------- result page ----------
  const result = $("#result");
  if (result) {
    if (result.dataset.owner === "1") {
      setMe({ pid: result.dataset.profile, key: result.dataset.key, name: result.dataset.name || me().name,
              type: result.dataset.type || me().type, mizaj: result.dataset.mizaj || me().mizaj });
    }
    const shareData = (() => { try { return JSON.parse($("#share-data").textContent); } catch (e) { return null; } })();
    const publicUrl = location.origin + "/p/" + result.dataset.profile;
    $$("[data-share]").forEach((b) => b.addEventListener("click", () => share(b.dataset.share, shareData, publicUrl)));

    const ccreate = $("[data-milan-create]");
    if (ccreate) ccreate.addEventListener("click", () => createMilan(ccreate));
    const save = $("[data-contact-save]");
    if (save) save.addEventListener("click", async () => {
      const err = $("[data-contact-err]"); err.textContent = "";
      const email = $("#c-email").value.trim(), phone = $("#c-wa").value.trim();
      if (!email && !phone) { err.textContent = "Enter an email or WhatsApp number."; return; }
      busy(save, true);
      try { await api("/api/profile", { profile_id: me().pid, key: me().key, email, phone }); $("[data-contact-box]").innerHTML = '<p class="ok">Saved ✓ We\'ll keep your result safe.</p>'; }
      catch (e) { err.textContent = e.message; busy(save, false); }
    });
    const cmp = $("[data-compare]");
    if (cmp) cmp.addEventListener("click", async () => {
      busy(cmp, true);
      try {
        const m = me();
        const res = await api("/api/milan/compare", { target: cmp.dataset.compare, profile_id: m.pid, key: m.key });
        location.href = res.redirect;
      } catch (e) { toast(e.message); busy(cmp, false); }
    });
    if (location.hash === "#report") { const r = $("#report"); if (r) setTimeout(() => r.scrollIntoView(), 50); }
  }
  bindRedeem();

  function bindRedeem() {
    const rb = $("[data-redeem]");
    if (!rb) return;
    rb.addEventListener("click", async () => {
      const err = $("[data-redeem-err]"); err.textContent = "";
      const ctx = ownerCtx(rb);
      const order = $("#order");
      busy(rb, true);
      try {
        await api("/api/redeem", { profile_id: order ? order.dataset.profile : ctx.pid, key: ctx.key || me().key,
                                   code: $("#code").value, pair_id: order ? order.dataset.pair || null : null });
        toast("Unlocked 🎉");
        location.href = order ? (order.dataset.pair ? "/milan/" + order.dataset.pair : "/p/" + order.dataset.profile + "#report") : location.pathname + "#report";
        if (!order) location.reload();
      } catch (e) { err.textContent = e.message; busy(rb, false); }
    });
  }

  async function createMilan(btn) {
    const m = me();
    if (!m.pid || !m.type) {
      const need = $("[data-milan-needtest]");
      if (need) need.classList.remove("hidden");
      location.href = "/test/personality/?then=milan";
      return;
    }
    busy(btn, true);
    try {
      const rel = $("#relation") ? $("#relation").value : "rishta";
      const res = await api("/api/milan", { profile_id: m.pid, key: m.key, relation: rel });
      const out = $("[data-milan-out]");
      $("[data-milan-link]").textContent = res.invite_url;
      const nm = m.name ? m.name + " wants" : "I want";
      $("[data-milan-wa]").href = "https://wa.me/?text=" + encodeURIComponent(nm + " to see how well we match 💞 Take this free 8-minute test: " + res.invite_url);
      out.classList.remove("hidden");
      btn.classList.add("hidden");
      track("milan_share", { relation: rel });
    } catch (e) { toast(e.message); busy(btn, false); }
  }

  // ---------- milan landing / invite ----------
  const mstart = $("#milan-start");
  if (mstart) {
    const b = $("[data-milan-create]", mstart);
    b.addEventListener("click", () => createMilan(b));
    if (!me().type) b.textContent = "Take the test, then invite →";
    if (params.get("ready") === "1" && me().type) b.click();
  }
  const join = $("[data-milan-join]");
  if (join && me().type && me().pid) {
    join.classList.remove("hidden");
    join.addEventListener("click", async () => {
      busy(join, true);
      try { const r = await api("/api/milan/join", { pair_id: join.dataset.milanJoin, profile_id: me().pid, key: me().key }); location.href = r.redirect; }
      catch (e) { toast(e.message); busy(join, false); }
    });
  }
  const sm = $("[data-share-milan]");
  if (sm) sm.addEventListener("click", () => {
    track("share_click", { kind: "milan" });
    const url = location.origin + "/milan/";
    window.open("https://wa.me/?text=" + encodeURIComponent("We got " + sm.dataset.shareMilan + "% on Mizaj Milan 💞 Test your match: " + url), "_blank");
  });

  // ---------- sharing ----------
  async function share(kind, d, url) {
    track("share_click", { kind });
    const name = d && d.who ? d.who : "";
    const text = d ? (d.code ? `${name ? name + " is" : "I'm"} ${d.code}: ${d.name} (${d.name_en}) ${d.emoji || ""}\n"${d.share_line}"` : `My mizaj is ${d.mizaj.name}, ${d.mizaj.nickname}`) + "\nWhat's your mizaj? Free test:" : "What's your mizaj?";
    const link = url + "?utm_source=" + (kind === "whatsapp" ? "whatsapp" : "share") + "&utm_medium=result";
    if (kind === "whatsapp") { window.open("https://wa.me/?text=" + encodeURIComponent(text + " " + link), "_blank"); return; }
    if (kind === "native" && navigator.share) { try { await navigator.share({ title: "My Mizaj", text, url: link }); } catch (e) { /* cancelled */ } return; }
    if (kind === "native") { copyText(text + " " + link); return; }
    if (kind === "card" && d) {
      try {
        const blob = await storyCard(d);
        const file = new File([blob], "mizaj-" + (d.code || d.mizaj.key).toLowerCase() + ".png", { type: "image/png" });
        if (navigator.canShare && navigator.canShare({ files: [file] })) { try { await navigator.share({ files: [file], text: text + " " + link }); return; } catch (e) { /* fall through */ } }
        const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = file.name; a.click();
        setTimeout(() => URL.revokeObjectURL(a.href), 4000);
        toast("Saved. Post it to your story ✨");
      } catch (e) { toast("Couldn't make the card on this phone."); }
    }
  }

  function wrapText(ctx, text, maxW) {
    const words = String(text || "").split(" "), lines = []; let line = "";
    words.forEach((w) => { const t = line ? line + " " + w : w; if (ctx.measureText(t).width > maxW && line) { lines.push(line); line = w; } else line = t; });
    if (line) lines.push(line);
    return lines;
  }

  function star(ctx, x, y, r, color) {
    ctx.save(); ctx.translate(x, y); ctx.strokeStyle = color; ctx.lineWidth = 3;
    for (let k = 0; k < 2; k++) { ctx.save(); ctx.rotate((k * Math.PI) / 4); ctx.strokeRect(-r, -r, 2 * r, 2 * r); ctx.restore(); }
    ctx.restore();
  }

  async function storyCard(d) {
    try { await Promise.all([document.fonts.load("700 160px Fraunces"), document.fonts.load("600 60px 'Noto Nastaliq Urdu'"), document.fonts.load("700 40px Manrope")]); } catch (e) { /* fonts optional */ }
    const W = 1080, H = 1920, c = document.createElement("canvas"); c.width = W; c.height = H;
    const x = c.getContext("2d");
    const famColors = { Danishwar: "#6B4FA0", "Ahl-e-Dil": "#2E8A6A", Pasban: "#2F6DB0", Fankar: "#D98C2B" };
    const mzColors = { damvi: "#D2544A", safravi: "#E39B2D", balghami: "#2E8A8A", saudavi: "#5A4A78" };
    const base = d.code ? famColors[d.family] : mzColors[d.mizaj.key];
    const g = x.createLinearGradient(0, 0, W, H); g.addColorStop(0, base); g.addColorStop(1, "#1B1530");
    x.fillStyle = g; x.fillRect(0, 0, W, H);
    for (let i = 0; i < 6; i++) for (let j = 0; j < 10; j++) star(x, 90 + i * 180, 90 + j * 190, 46, "rgba(255,255,255,0.06)");
    x.fillStyle = "#FBF6EE"; x.textAlign = "center";
    x.font = "700 46px Manrope"; x.fillText("mizaj.pk", W / 2, 150);
    x.font = "600 44px Manrope"; x.globalAlpha = 0.85;
    x.fillText(d.who ? d.who + " is" : "I am", W / 2, 520); x.globalAlpha = 1;
    if (d.code) {
      x.font = "700 230px Fraunces"; x.fillText(d.code, W / 2, 760);
      x.font = "700 74px Fraunces"; x.fillText(d.name, W / 2, 880);
      x.font = "600 46px Manrope"; x.fillText(d.name_en + " " + (d.emoji || ""), W / 2, 950);
      x.font = "600 64px 'Noto Nastaliq Urdu'"; x.fillText(d.name_ur || "", W / 2, 1080);
    } else {
      x.font = "700 160px Fraunces"; x.fillText(d.mizaj.name, W / 2, 760);
      x.font = "600 52px Manrope"; x.fillText(d.mizaj.nickname + " · " + d.mizaj.quality.split(" (")[0], W / 2, 860);
      x.font = "600 64px 'Noto Nastaliq Urdu'"; x.fillText(d.mizaj.name_ur || "", W / 2, 990);
    }
    x.font = "italic 600 50px Fraunces";
    wrapText(x, "“" + (d.share_line || d.tagline || "") + "”", 880).slice(0, 4).forEach((ln, i) => x.fillText(ln, W / 2, 1230 + i * 70));
    if (d.code && d.mizaj) {
      x.fillStyle = "rgba(255,255,255,0.14)"; roundRect(x, 190, 1500, 700, 110, 55); x.fill();
      x.fillStyle = "#FBF6EE"; x.font = "700 46px Manrope"; x.fillText("Mizaj: " + d.mizaj.name + " · " + d.mizaj.nickname, W / 2, 1572);
    }
    x.font = "700 44px Manrope"; x.fillStyle = "#E8A33D"; x.fillText("What's your mizaj? Free test at mizaj.pk", W / 2, 1780);
    return await new Promise((res) => c.toBlob(res, "image/png"));
  }
  function roundRect(x, l, t, w, h, r) { x.beginPath(); x.moveTo(l + r, t); x.arcTo(l + w, t, l + w, t + h, r); x.arcTo(l + w, t + h, l, t + h, r); x.arcTo(l, t + h, l, t, r); x.arcTo(l, t, l + w, t, r); x.closePath(); }

  // ---------- order page ----------
  const order = $("#order");
  if (order) initOrder(order);

  function initOrder(root) {
    const oid = root.dataset.order;
    let status = root.dataset.status;
    const showState = () => $$("[data-state]", root).forEach((el) => el.classList.toggle("hidden", el.dataset.state !== (status === "created" ? "created" : status)));
    showState();
    const done = () => { location.href = root.dataset.pair ? "/milan/" + root.dataset.pair : "/p/" + root.dataset.profile + "#report"; };
    if (status === "paid") setTimeout(done, 1200);
    let polling = null;
    const poll = () => {
      if (polling) return;
      polling = setInterval(async () => {
        try {
          const s = await api("/api/orders/" + oid + "/status");
          if (s.status !== status) { status = s.status; showState(); if (status === "paid") { clearInterval(polling); setTimeout(done, 1200); } if (status === "rejected") clearInterval(polling); }
        } catch (e) { /* keep polling */ }
      }, 6000);
    };
    if (status === "proof") poll();
    $$("[data-method-tab]", root).forEach((t) => t.addEventListener("click", () => {
      $$("[data-method-tab]", root).forEach((x) => x.classList.toggle("on", x === t));
      $$("[data-method]", root).forEach((p) => p.classList.toggle("hidden", p.dataset.method !== t.dataset.methodTab));
      track("pay_method", { method: t.dataset.methodTab });
    }));
    const form = $("[data-proof]", root);
    if (form) form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const err = $("[data-err]", form); err.textContent = "";
      const tab = $("[data-method-tab].on", root) || $("[data-method-tab]", root);
      const btn = $("button[type=submit]", form); busy(btn, true);
      try {
        const r = await api("/api/orders/" + oid + "/proof", { method: tab ? tab.dataset.methodTab : "", tid: form.tid.value, sender: form.sender.value, email: form.email.value });
        status = r.status; showState();
        if (status === "paid") setTimeout(done, 1200); else poll();
      } catch (ex) { err.textContent = ex.message; busy(btn, false); }
    });
    const sp = $("[data-safepay]", root);
    if (sp) sp.addEventListener("click", async () => {
      busy(sp, true);
      try { const r = await api("/api/orders/" + oid + "/safepay", {}); location.href = r.redirect; }
      catch (e) { toast(e.message); busy(sp, false); }
    });
  }

  // ---------- palm ----------
  const palmForm = $("#palm-form");
  if (palmForm) {
    const file = $("#palm-file"), pick = $("[data-palm-pick]"), err = $("[data-palm-err]"), busyEl = $("[data-palm-busy]");
    pick.addEventListener("click", () => { track("palm_start"); file.click(); });
    file.addEventListener("change", async () => {
      err.textContent = "";
      const f = file.files[0]; if (!f) return;
      pick.classList.add("hidden"); busyEl.classList.remove("hidden");
      try {
        const blob = await shrink(f, 1280);
        const fd = new FormData();
        fd.append("image", blob, "palm.jpg"); fd.append("hand", $("#hand").value);
        fd.append("profile_id", me().pid || ""); fd.append("key", me().key || "");
        const r = await api("/api/palm", fd);
        if (!r.is_palm) throw new Error(r.retake_tip || "We couldn't see a palm clearly. Try again in good light.");
        if (!me().pid) setMe({ pid: r.profile_id, key: r.key });
        location.href = r.url;
      } catch (e) { err.textContent = e.message; pick.classList.remove("hidden"); busyEl.classList.add("hidden"); file.value = ""; }
    });
  }
  function shrink(file, max) {
    return new Promise((resolve, reject) => {
      const img = new Image(), url = URL.createObjectURL(file);
      img.onload = () => {
        const s = Math.min(1, max / Math.max(img.width, img.height));
        const c = document.createElement("canvas"); c.width = Math.round(img.width * s); c.height = Math.round(img.height * s);
        c.getContext("2d").drawImage(img, 0, 0, c.width, c.height);
        URL.revokeObjectURL(url);
        c.toBlob((b) => (b ? resolve(b) : reject(new Error("Couldn't read that photo."))), "image/jpeg", 0.85);
      };
      img.onerror = () => { URL.revokeObjectURL(url); reject(new Error("That file doesn't look like a photo.")); };
      img.src = url;
    });
  }
  const sp = $("[data-share-palm]");
  if (sp) sp.addEventListener("click", () => { track("share_click", { kind: "palm" }); window.open("https://wa.me/?text=" + encodeURIComponent("AI ne meri haath ki lakeerein parh lin ✋😅 Try yours free: " + location.origin + "/palm/?utm_source=whatsapp"), "_blank"); });

  // ---------- burj & adad ----------
  const burj = $("#burj-form");
  if (burj) {
    if (me().type) $("#btype").value = me().type;
    burj.addEventListener("submit", async (e) => {
      e.preventDefault();
      const out = $("#burj-out"), err = $("[data-err]", burj); err.textContent = "";
      try {
        const d = await api("/api/fun/zodiac?dob=" + encodeURIComponent($("#dob").value) + "&type=" + encodeURIComponent($("#btype").value));
        const s = d.sign, bn = d.birth_number;
        out.innerHTML = `<div class="card"><span class="eyebrow">Your burj</span><h2>${esc(s.symbol)} ${esc(s.en)} · ${esc(s.roman)} <span class="ur">${esc(s.ur)}</span></h2>
          <p class="muted">${esc(s.element)} · ${esc(s.vibe)}</p><p>${esc(s.personality)}</p>
          <p><b>In the family:</b> ${esc(s.in_a_family)}</p><p class="notice">😂 ${esc(s.meme)}</p></div>` +
          (d.mashup ? `<div class="card"><span class="eyebrow">${esc(s.en)} × ${esc(d.type.code)} ${esc(d.type.name)}</span><h3>${esc(d.mashup)}</h3></div>` :
            `<div class="card"><p>Know your personality type? <a href="/test/personality/">Take the free test</a> and come back for your mash-up.</p></div>`) +
          (bn && bn.meaning ? `<div class="card"><span class="eyebrow">Birth number</span><h3>${esc(bn.number)} · ${esc(bn.meaning.title)}</h3><p>${esc(bn.meaning.personality)}</p></div>` : "") +
          `<button class="btn btn-wa" id="burj-share">Share</button>`;
        out.classList.remove("hidden");
        $("#burj-share").addEventListener("click", () => { track("share_click", { kind: "burj" }); window.open("https://wa.me/?text=" + encodeURIComponent(`I'm a ${s.en}${d.type ? " " + d.type.code : ""}: ${d.mashup || s.meme} ✨ Find yours: ${location.origin}/burj/?utm_source=whatsapp`), "_blank"); });
      } catch (ex) { err.textContent = ex.message; }
    });
  }
  const adad = $("#adad-form");
  if (adad) {
    adad.addEventListener("submit", async (e) => {
      e.preventDefault();
      const out = $("#adad-out"), err = $("[data-err]", adad); err.textContent = "";
      try {
        const q = "name=" + encodeURIComponent($("#aname").value) + ($("#adob").value ? "&dob=" + $("#adob").value : "");
        const d = await api("/api/fun/numerology?" + q);
        const n = d.name_number, mm = n.meaning || {};
        out.innerHTML = `<div class="card"><span class="eyebrow">${n.system === "abjad" ? "Abjad value" : "Name number"}: ${esc(n.total)}</span>
          <h2>${esc(n.number)} · ${esc(mm.title || "")} <span class="ur">${esc(mm.ur_title || "")}</span></h2><p>${esc(mm.personality || "")}</p>
          <p><b>Strengths:</b> ${esc(mm.strengths || "")}</p><p><b>Watch:</b> ${esc(mm.watch || "")}</p><p class="small muted">Colour: ${esc(mm.colour || "")} · Day: ${esc(mm.day || "")}</p></div>` +
          (d.birth_number && d.birth_number.meaning ? `<div class="card"><span class="eyebrow">Birth number</span><h3>${esc(d.birth_number.number)} · ${esc(d.birth_number.meaning.title)}</h3><p>${esc(d.birth_number.meaning.personality)}</p></div>` : "") +
          `<button class="btn btn-wa" id="adad-share">Share</button>`;
        out.classList.remove("hidden");
        $("#adad-share").addEventListener("click", () => { track("share_click", { kind: "adad" }); window.open("https://wa.me/?text=" + encodeURIComponent(`My name's Abjad number is ${n.number}: ${mm.title || ""} ✨ Find yours: ${location.origin}/adad/?utm_source=whatsapp`), "_blank"); });
      } catch (ex) { err.textContent = ex.message; }
    });
  }

  // ---------- lead forms ----------
  $$("[data-lead]").forEach((f) => f.addEventListener("submit", async (e) => {
    e.preventDefault();
    const err = $("[data-err]", f); err.textContent = "";
    const body = { kind: f.dataset.lead }; new FormData(f).forEach((v, k) => { body[k] = v; });
    const btn = $("button[type=submit]", f); busy(btn, true);
    try { await api("/api/leads", body); f.reset(); $("[data-ok]", f).classList.remove("hidden"); busy(btn, false); btn.classList.add("hidden"); }
    catch (ex) { err.textContent = ex.message; busy(btn, false); }
  }));
})();
