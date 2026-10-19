// PAFTA ön yüzü: harita, ders paftası, tezgah (editör + çıktı + Röntgen), tekrar.
import { render, codeBlock, stripAnno, regexParcala, dilAdi } from "./md.js";
import { esc } from "./hl.js";
import { Editor } from "./editor.js";

const TOKEN = document.querySelector('meta[name="pafta-token"]').content;
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const view = $("#view");
const S = { state: null, ranks: {}, lesson: null, tid: "python", idx: 0, bench: null, mode: null };

const KIND_LABEL = { anlat: "Anlat", tahmin: "Tahmin", gorev: "Görev" };
const KIND_ICON = { anlat: "≡", tahmin: "?", gorev: "✎" };

// ── hata tercümanı ───────────────────────────────────────────────────────────
const ERR_TR = {
  SyntaxError: "Python kodu okuyamadı. Çoğu zaman sebep eksik iki nokta (:), kapanmamış parantez ya da tırnak, veya yanlış yazılmış bir anahtar kelimedir. İşaretlenen satıra ve bir üstündekine bak.",
  IndentationError: "Girinti hatası: bir bloğun içindeki satırlar aynı miktarda içeride olmalı (4 boşluk). İki noktalı (:) satırdan sonra blok bekleniyor olabilir.",
  TabError: "Girintide sekme (Tab) ve boşluk karışmış. Sadece boşluk kullan.",
  NameError: "Bu isim tanımlı değil. Ya yazım hatası var ya da değişkeni/fonksiyonu tanımlamadan önce kullandın. Python büyük-küçük harfe duyarlıdır: Print ≠ print.",
  TypeError: "Tür uyuşmazlığı: bir işlemi onu desteklemeyen türe uyguladın (ör. \"5\" + 3) ya da fonksiyona yanlış sayıda/türde argüman verdin.",
  ValueError: "Tür doğru ama değer uygun değil. Örnek: int(\"abc\") — metin ama sayıya çevrilemez.",
  IndexError: "Dizinin sınırları dışına çıktın. Uzunluğu n olan bir dizide geçerli indeksler 0 … n-1 (ya da -1 … -n).",
  KeyError: "Sözlükte bu anahtar yok. Önce `in` ile kontrol et ya da .get(anahtar, varsayılan) kullan.",
  ZeroDivisionError: "Sıfıra bölme. Böleni kontrol et.",
  AttributeError: "Bu nesnenin böyle bir niteliği ya da metodu yok. Nesnenin türünü kontrol et — çoğu zaman beklediğin şey yerine None gelmiştir.",
  UnboundLocalError: "Fonksiyonun içinde bu değişkene atama yaptığın için Python onu yerel saydı ama atamadan önce okudun. Dıştakini kastediyorsan global/nonlocal gerekir.",
  RecursionError: "Özyineleme çok derinleşti. Büyük ihtimalle temel durum (base case) eksik ya da hiç ulaşılamıyor.",
  ModuleNotFoundError: "Böyle bir modül bulunamadı. Adı doğru mu? Standart kütüphanede değilse kurulu olmayabilir.",
  ImportError: "Modül bulundu ama içinden istediğin isim alınamadı. Adı doğru yazdın mı?",
  FileNotFoundError: "Dosya bulunamadı. Yol ve ad doğru mu? Program görev klasöründe çalışır.",
  EOFError: "input() girdi bekledi ama Girdi kutusunda okunacak satır yok. Alttaki ‘Girdi’ kutusuna satır ekle.",
  StopIteration: "Yineleyici tükendi: next() ile alınacak eleman kalmadı.",
  AssertionError: "Bir assert koşulu yanlış çıktı.",
  OverflowError: "Sayı bu işlem için fazla büyük.",
  PermissionError: "Bu dosya/klasör için iznin yok.",
  UnicodeDecodeError: "Baytlar bu kodlamayla çözülemedi. encoding parametresini kontrol et (çoğu zaman utf-8).",
  UnicodeEncodeError: "Metin bu kodlamaya çevrilemedi.",
  NotImplementedError: "Henüz yazılmamış (soyut) bir metot çağrıldı.",
  ConnectionRefusedError: "Bağlantı reddedildi: o adreste/portta dinleyen bir sunucu yok.",
  TimeoutError: "İşlem zaman aşımına uğradı.",
  RuntimeError: "Çalışma zamanı hatası. Mesajı oku; genelde durum yanlış (ör. döngüde sözlüğü değiştirmek).",
  OSError: "İşletim sistemi düzeyinde bir hata (dosya, soket, izin).",
  KeyboardInterrupt: "Program kesildi.",
  MemoryError: "Bellek yetmedi.",
  "Zaman aşımı": "Program süre sınırında bitmedi. Sonsuz döngü var mı? while koşulu hiç yanlış olmuyor olabilir, ya da input() sonsuza dek bekliyor olabilir.",
  "SüreçBitti": "Program sonuç üretemeden süreci sonlandırdı.",
  "DesenHatası": "Desen derlenemedi. Sık sebepler: kapanmamış parantez ( ya da köşeli parantez [, başında hiçbir şey olmayan bir niceleyici (* + ? {}), geçersiz bir kaçış dizisi ya da yanlış yazılmış bir grup sözdizimi (?P<ad>...).",
  "SPLHatası": "Arama çalıştırılamadı. Sık sebepler: arama sourcetype=<tablo> ile başlamıyor, komutun önünde | unutulmuş, yanlış yazılmış bir alan ya da komut adı, eval içinde metinler için çift tırnak yerine tek tırnak (tek tırnak alan adı demektir), ya da iki arama arasında boş satır yok.",
  "KQLHatası": "Sorgu çalıştırılamadı. Sık sebepler: işlecin önünde | unutulmuş, yanlış yazılmış bir sütun ya da işleç adı (KQL büyük-küçük harfe duyarlıdır: Where ≠ where), metin karşılaştırmasında = yerine == gerekiyor, ya da iki sorgu arasında boş satır yok.",
  "SQLHatası": "SQLite sorguyu çalıştıramadı. Mesajın Türkçesi önde, aslı parantez içinde. Sık sebepler: yanlış yazılmış tablo ya da sütun adı, iki sütun arasında eksik virgül, metin değerinde tek tırnak yerine çift tırnak, WHERE içinde toplama fonksiyonu (orası HAVING olmalı) ya da kapanmamış bir parantez.",
  "ÇıkışKodu": "Betik sıfırdan farklı bir çıkış koduyla bitti. Kabuk dünyasında 0 başarı, diğer her şey hatadır. Hata akışındaki (kırmızı) mesajı ve işaretli satırı oku: genelde yanlış yazılmış bir komut, bulunamayan bir dosya ya da eksik bir argüman.",
};

// ── altyapı ───────────────────────────────────────────────────────────────────
async function api(path, body) {
  const opt = { method: body ? "POST" : "GET", headers: { "X-Pafta-Token": TOKEN } };
  if (body) { opt.headers["Content-Type"] = "application/json"; opt.body = JSON.stringify(body); }
  const r = await fetch(path, opt);
  const data = await r.json().catch(() => ({}));
  if (r.status === 403 && /belirteç|yasak/.test(data.error || "")) {
    // Sunucu yeniden başladıysa belirteç değişmiştir; yeni sayfa yeni belirteci taşır.
    let yenilendi = false;
    try { yenilendi = sessionStorage.getItem("pafta-yenile") === "1"; sessionStorage.setItem("pafta-yenile", "1"); } catch (e) { /* depolama yoksa bir kez dene */ }
    if (!yenilendi) location.reload();
  }
  if (!r.ok) throw new Error(data.error || r.statusText);
  try { sessionStorage.removeItem("pafta-yenile"); } catch (e) { /* önemsiz */ }
  return data;
}

let toastT;
function toast(msg) {
  const t = $("#toast");
  t.textContent = msg;
  t.classList.add("show");
  clearTimeout(toastT);
  toastT = setTimeout(() => t.classList.remove("show"), 2400);
}

function debounce(fn, ms) {
  let t;
  const d = (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); };
  d.flush = (...a) => { clearTimeout(t); fn(...a); };
  return d;
}

const trDate = (d = new Date()) => d.toLocaleDateString("tr-TR");
const pad = (n, w = 2) => String(n).padStart(w, "0");

function setTheme(t) {
  document.documentElement.dataset.theme = t;
  $("#themeBtn").textContent = t === "ozalit" ? "OZALİT" : "MAVİ KOPYA";
}

async function refreshHeader() {
  try {
    const st = await api("/api/state");
    S.state = st;
    $("#streakChip b").textContent = st.streak;
    const b = $("#dueBadge");
    b.textContent = st.due_count;
    b.hidden = !st.due_count;
    return st;
  } catch (e) { return S.state; }
}

// ── hata kartı ────────────────────────────────────────────────────────────────
function errCard(err) {
  if (!err) return "";
  const tr = ERR_TR[err.type] || "Python bir hata yükseltti. Mesajı ve işaretli satırı incele.";
  const parts = [];
  if (err.where === "kod-girdi") parts.push(`Program şu girdiyle çalıştırılırken hata verdi: <code>${esc(JSON.stringify(err.stdin))}</code>`);
  if (err.where === "kod-test") parts.push("Test, kodundaki fonksiyonu çağırdığında kodun hata verdi.");
  if (err.where === "test") {
    parts.push(err.missing
      ? `Test, kodunda <code>${esc(err.missing)}</code> adını arıyor ama bulamadı. Görevdeki adı harfi harfine kullandın mı?`
      : "Hata testin içinde oluştu. Bu genelde fonksiyonun beklenmeyen türde bir değer döndürdüğünde (ör. None) olur.");
  }
  if (err.suggest) parts.push(`Bunu mu demek istedin: <code>${esc(err.suggest)}</code>?`);
  if (err.frames && err.frames.length > 1) {
    parts.push("Çağrı zinciri: " + err.frames.map(f => `<code>${esc(f.func === "<module>" ? "ana kod" : f.func + "()")}</code> s.${f.line}`).join(" → "));
  }
  let raw = `${err.type}: ${err.msg}`;
  if (err.text) raw += `\n    ${err.text.trim()}`;
  const where = err.line && err.where !== "test" ? `<button type="button" class="goto" data-line="${err.line}">satır ${err.line}</button>` : "";
  return `<div class="errcard"><div class="et">${esc(err.type)} ${where}</div><p>${tr}</p>` +
    parts.map(p => `<p>${p}</p>`).join("") + `<div class="raw">${esc(raw)}</div></div>`;
}

// Görev argüman bekliyorsa betik onlarla çalışır; hangileri olduğunu çıktının üstünde göster
function argvSatiri(res) {
  if (!res.argv?.length) return "";
  const goster = a => (/\s|^$/.test(a) ? JSON.stringify(a) : a);
  return `<div class="out-meta" style="margin:0 0 8px">argümanlar: <code>${esc(res.argv.map(goster).join(" "))}</code></div>`;
}

function segsHtml(segs) {
  if (!segs || !segs.length) return "";
  return segs.map(([k, t]) => k === "out" ? esc(t) : `<span class="s-${k}">${esc(t)}</span>`).join("");
}

// SQL: her ifadenin sonucu ayrı bir tablo; değiştiren komutlar tek satırlık özet
function sqlTablolar(tablolar, max = 200, kql = false) {
  return (tablolar || []).map(t => {
    if (!t.sutunlar) {
      const ne = t.degisen !== undefined ? `${t.degisen} satır etkilendi` : "tamam";
      return `<div class="sql-bas"><span class="ln">s.${t.satir}</span><b>${esc(t.komut)}</b> · ${ne}</div>`;
    }
    const n = t.satirlar.length;
    // SPL'in çok değerli alanları \x1f ile ayrık gelir: Splunk'taki gibi her değer ayrı satırda
    const hucre = v => v === null ? `<td class="null">${kql ? "" : "NULL"}</td>`
      : `<td${/^-?\d+(\.\d+)?$/.test(v) ? ' class="num"' : ""}>${esc(v).replace(/\x1f/g, "<br>")}</td>`;
    const govde = t.satirlar.slice(0, max).map(r => `<tr>${r.map(hucre).join("")}</tr>`).join("");
    const fazla = n > max ? `<div class="out-meta">ilk ${max} satır gösteriliyor</div>` : "";
    return `<div class="sql-sonuc"><div class="sql-bas"><span class="ln">s.${t.satir}</span>${n} satır${t.kesildi ? " (ilk 500)" : ""}</div>` +
      (n ? `<table class="sql-tablo"><thead><tr>${t.sutunlar.map(c => `<th>${esc(c)}</th>`).join("")}</tr></thead><tbody>${govde}</tbody></table>${fazla}`
        : `<div class="out-meta">sonuç boş · hiçbir satır koşulu sağlamadı</div>`) + `</div>`;
  }).join("");
}

// ── TEZGAH ────────────────────────────────────────────────────────────────────
class Bench {
  constructor(host, ctx) {
    this.ctx = ctx;  // {track, checkable(), check(code), lessonRef(), saveDraft(code)}
    this.host = host;
    this.results = {};
    this.tab = "out";
    host.innerHTML = `
      <div class="bench-bar">
        <button type="button" class="btn primary small" data-b="run">▶ Çalıştır <kbd>Ctrl+↵</kbd></button>
        <button type="button" class="btn ok small" data-b="check" hidden>✓ Kontrol et <kbd>Ctrl+⇧+↵</kbd></button>
        <button type="button" class="btn small" data-b="xray" title="Kodu adım adım yürüt, her satırda değişkenleri gör">◎ Röntgen</button>
        <button type="button" class="btn small" data-b="dis" title="Python'un bu kodu çevirdiği bytecode">Bytecode</button>
        <span class="sp"></span>
        <span class="save" data-b="save"></span>
        <button type="button" class="linkish" data-b="reset">başa al</button>
      </div>
      <div class="bench-ed"></div>
      <div class="bench-panel">
        <div class="tabs" role="tablist">
          <button type="button" class="tab on" data-tab="out"><i class="dot"></i>Çıktı</button>
          <button type="button" class="tab" data-tab="check" hidden><i class="dot"></i>Kontrol</button>
          <button type="button" class="tab" data-tab="xray"><i class="dot"></i>Röntgen</button>
          <button type="button" class="tab" data-tab="dis">Bytecode</button>
          <span class="sp"></span>
          <button type="button" class="tab stdin-toggle" data-b="stdin">Girdi ▸</button>
        </div>
        <div class="stdin-box" hidden><span class="label">Girdi (stdin) · her satır bir input() çağrısına gider</span><textarea rows="3" spellcheck="false"></textarea></div>
        <div class="pane"></div>
      </div>`;
    this.pane = $(".pane", host);
    this.stdinBox = $(".stdin-box", host);
    this.stdin = $(".stdin-box textarea", host);
    this.saveLbl = $('[data-b="save"]', host);
    this.draft = debounce(code => {
      const p = this.ctx.saveDraft?.(code);
      if (p) p.then(() => { this.saveLbl.textContent = "kaydedildi"; }).catch(() => { this.saveLbl.textContent = "kaydedilemedi"; });
      else this.saveLbl.textContent = "";
    }, 700);
    this.ed = new Editor($(".bench-ed", host), {
      onChange: code => { this.saveLbl.textContent = this.ctx.saveDraft ? "…" : ""; this.draft(code); this.xrayStale = true; },
      onRun: () => this.run(),
      onCheck: () => this.ctx.checkable() && this.check(),
      onSave: () => { this.draft.flush(this.ed.value); },
      dil: ctx.dil || "python",
    });
    this.ayarla(ctx.dil || "python", ctx.ozellik || { roentgen: true, dis: "Bytecode" });
    host.addEventListener("click", e => {
      const b = e.target.closest("[data-b]");
      if (b) {
        const a = b.dataset.b;
        if (a === "run") this.run();
        else if (a === "check") this.check();
        else if (a === "xray") this.xray();
        else if (a === "dis") this.dis();
        else if (a === "reset") this.reset();
        else if (a === "stdin") this.toggleStdin();
        return;
      }
      const t = e.target.closest("[data-tab]");
      if (t) { this.show(t.dataset.tab); return; }
      const g = e.target.closest(".goto");
      if (g) this.ed.gotoLine(+g.dataset.line);
    });
    this.pane.addEventListener("keydown", e => {
      if (this.tab !== "xray" || !this.x) return;
      const adim = this.x.res.kind === "iz" ? i => this.izStep(i) : i => this.xstep(i);
      if (e.key === "ArrowRight") { e.preventDefault(); adim(this.x.i + 1); }
      if (e.key === "ArrowLeft") { e.preventDefault(); adim(this.x.i - 1); }
    });
    this.show("out");
  }

  // Dile göre düğmeler, etiketler ve boş durum metinleri
  ayarla(dil, ozellik) {
    this.dil = dil;
    this.ozellik = ozellik;
    this.ed.dil = dil;
    const h = this.host;
    const xr = !!ozellik.roentgen, ds = ozellik.dis;
    $('[data-b="xray"]', h).hidden = !xr;
    $('[data-tab="xray"]', h).hidden = !xr;
    $('[data-b="dis"]', h).hidden = !ds;
    $('[data-tab="dis"]', h).hidden = !ds;
    if (ds) { $('[data-b="dis"]', h).textContent = ds; $('[data-tab="dis"]', h).textContent = ds; }
    $('[data-b="xray"]', h).title = dil === "python" ? "Kodu adım adım yürüt, her satırda değişkenleri gör" : "Betiği iz modunda çalıştır: hangi satır hangi sırayla çalıştı";
    $(".stdin-box .label", h).textContent = {
      python: "Girdi (stdin) · her satır bir input() çağrısına gider",
      regex: "Metin · desen bu metnin içinde aranır",
      bash: "Girdi (stdin) · read komutu satırları buradan okur",
      powershell: "Girdi · satırlar $Girdi dizisine gelir",
      javascript: "Girdi (stdin) · require(\"fs\").readFileSync(0, \"utf8\") ile okunur",
    }[dil] || "Girdi";
    this.stdin.rows = dil === "regex" ? 4 : 3;
    this.girdiAdi = dil === "regex" ? "Metin" : "Girdi";
    const vt = ["sql", "kql", "spl"].includes(dil);        // bu dillerin girdisi örnek veritabanıdır
    $('[data-b="stdin"]', h).hidden = vt;
    this.toggleStdin(dil === "regex" ? true : vt ? false : !this.stdinBox.hidden);
  }

  setStdin(t) {
    this.stdin.value = t || "";
    if (t) this.toggleStdin(true);
  }

  load({ code = "", stdin = "", resetCode = "", checkable = false }) {
    this.resetCode = resetCode;
    this.ed.value = code;
    this.stdin.value = stdin;
    if (stdin) this.toggleStdin(true);
    $('[data-b="check"]', this.host).hidden = !checkable;
    $('[data-tab="check"]', this.host).hidden = !checkable;
    this.results = {};
    this.x = null;
    this.saveLbl.textContent = "";
    $$(".tab .dot", this.host).forEach(d => d.className = "dot");
    this.show("out");
  }

  setCode(code) {
    this.ed.value = code;
    this.ctx.saveDraft?.(code);
    this.show("out");
  }

  toggleStdin(force) {
    const open = force ?? this.stdinBox.hidden;
    this.stdinBox.hidden = !open;
    $('[data-b="stdin"]', this.host).textContent = `${this.girdiAdi || "Girdi"} ${open ? "▾" : "▸"}`;
  }

  reset() {
    if (this.ed.value === this.resetCode) return;
    if (!confirm("Editördeki kodu başlangıç haline döndürmek istiyor musun?")) return;
    this.setCode(this.resetCode);
  }

  dot(tab, cls) {
    const d = $(`[data-tab="${tab}"] .dot`, this.host);
    if (d) d.className = "dot " + (cls || "");
  }

  busy(tab, msg) {
    this.show(tab);
    this.pane.className = "pane empty";
    this.pane.innerHTML = msg;
  }

  show(tab) {
    this.tab = tab;
    $$(".tab[data-tab]", this.host).forEach(t => t.classList.toggle("on", t.dataset.tab === tab));
    const r = this.results[tab];
    this.pane.className = "pane";
    this.pane.tabIndex = tab === "xray" ? 0 : -1;
    if (!r) {
      this.pane.className = "pane empty";
      const py = this.dil === "python";
      this.pane.innerHTML = {
        out: { regex: "▶ Çalıştır deseni Metin kutusundaki metinde arar;<br>eşleşmeler işaretlenir",
          sql: "▶ Çalıştır sorguyu örnek veritabanında çalıştırır;<br>her sorgunun sonucu bir tablo olarak görünür",
          kql: "▶ Çalıştır sorguyu örnek veritabanında çalıştırır;<br>boş satırla ayrılmış her sorgu ayrı bir tablo verir",
          spl: "▶ Çalıştır aramayı örnek veritabanında çalıştırır;<br>boş satırla ayrılmış her arama ayrı bir tablo verir" }[this.dil]
          || "▶ Çalıştır ile kodun çıktısı burada görünür",
        check: "✓ Kontrol et ile görev testleri burada koşar",
        xray: py ? "◎ Röntgen kodu adım adım yürütür:<br>her satırda hangi isim hangi nesneyi gösteriyor, gör"
          : "◎ Röntgen betiği iz modunda çalıştırır:<br>hangi satırın hangi sırayla, hangi değerlerle çalıştığını gör",
        dis: { python: "Python kodunu önce bytecode'a çevirir, sonra onu yürütür.<br>Bytecode düğmesi o çeviriyi gösterir",
          regex: "Ağaç, desenin regex motoru tarafından nasıl parçalara ayrıldığını gösterir",
          sql: "Plan, SQLite'ın sorguyu nasıl yürüteceğini gösterir:<br>tabloyu baştan sona mı tarıyor, indeksle mi arıyor",
          kql: "SQL düğmesi KQL sorgunun SQL karşılığını gösterir:<br>her | aşaması bir WITH adımına dönüşür",
          spl: "SQL düğmesi aramanın SQL karşılığını gösterir:<br>her | komutu bir WITH adımına dönüşür" }[this.dil] || "",
      }[tab];
      return;
    }
    if (tab === "out") this.paintOut(r);
    if (tab === "check") this.paintCheck(r);
    if (tab === "xray") (this.x.res.kind === "iz" ? this.paintIz() : this.paintXray());
    if (tab === "dis") this.paintDis(r);
  }

  async run() {
    this.busy("out", "çalışıyor…");
    this.ed.clearMarks();
    try {
      const res = await api("/api/run", { track: this.ctx.track, code: this.ed.value, stdin: this.stdin.value, mode: "run", ...(this.ctx.lessonRef?.() || {}) });
      this.results.out = res;
      this.dot("out", res.error ? "bad" : "ok");
      this.show("out");
    } catch (e) { this.busy("out", "Sunucuya ulaşılamadı: " + esc(e.message)); }
  }

  paintOut(res) {
    if (res.eslesmeler) return this.paintEslesme(res);
    if (res.tablolar) {
      const meta = res.error ? "" : `<div class="out-meta">${res.tablolar.length ? "— bitti —" : "betikte çalışan bir ifade yok"}</div>`;
      this.pane.innerHTML = sqlTablolar(res.tablolar, 200, res.kql) + errCard(res.error) + meta;
      if (res.error?.line) this.ed.mark(res.error.line, "err");
      return;
    }
    const body = segsHtml(res.segs);
    const bos = { python: "program çıktı vermeden bitti (print kullandın mı?)", bash: "betik çıktı vermeden bitti (echo kullandın mı?)",
      powershell: "betik çıktı vermeden bitti" }[this.dil] || "çıktı yok";
    const meta = res.error ? "" : `<div class="out-meta">${body ? "— bitti —" : bos}${res.truncated ? " · çıktı kesildi" : ""}</div>`;
    this.pane.innerHTML = `${argvSatiri(res)}<pre class="out">${body}</pre>${errCard(res.error)}${meta}`;
    if (res.error?.line && res.error.where !== "test") this.ed.mark(res.error.line, "err");
    else if (res.uyari_satir) this.ed.mark(res.uyari_satir, "err");
  }

  // Regex: metni eşleşmeler işaretli göster, altında eşleşme tablosu
  paintEslesme(res) {
    if (res.error) { this.pane.innerHTML = errCard(res.error); if (res.error.line) this.ed.mark(res.error.line, "err"); return; }
    const es = res.eslesmeler, metin = res.metin || "";
    let html = "", konum = 0;
    for (const e of es) {
      if (e.son === e.bas) continue;
      html += esc(metin.slice(konum, e.bas)) + `<mark>${esc(metin.slice(e.bas, e.son))}</mark>`;
      konum = e.son;
    }
    html += esc(metin.slice(konum));
    const grupVar = es.some(e => e.gruplar.length);
    const satirlar = es.slice(0, 200).map((e, i) => {
      const gr = Object.keys(e.adli).length
        ? Object.entries(e.adli).map(([k, v]) => `${esc(k)}=${esc(JSON.stringify(v))}`).join(" ")
        : e.gruplar.map((g, j) => `${j + 1}=${esc(JSON.stringify(g))}`).join(" ");
      return `<tr><td>${i + 1}</td><td>${esc(JSON.stringify(e.metin))}</td><td>${e.bas}–${e.son}</td>${grupVar ? `<td>${gr}</td>` : ""}</tr>`;
    }).join("");
    const ozet = es.length ? `${es.length} eşleşme` : "eşleşme yok";
    this.pane.innerHTML = `<div class="check-sum ${es.length ? "pass" : "fail"}" style="font-size:12px">${ozet}</div>` +
      (metin ? `<pre class="rx-metin">${html}</pre>` : `<div class="out-meta">Metin kutusu boş: desenin arayacağı metni oraya yaz</div>`) +
      (es.length ? `<table class="rx-tablo"><thead><tr><th>#</th><th>eşleşme</th><th>konum</th>${grupVar ? "<th>gruplar</th>" : ""}</tr></thead><tbody>${satirlar}</tbody></table>` : "");
  }

  async check() {
    this.busy("check", "testler koşuyor…");
    this.ed.clearMarks();
    try {
      const res = await this.ctx.check(this.ed.value);
      this.results.check = res;
      this.dot("check", res.status === "pass" ? "ok" : "bad");
      this.show("check");
      if (res.status === "pass") this.ctx.onPass?.(res);
    } catch (e) { this.busy("check", "Sunucuya ulaşılamadı: " + esc(e.message)); }
  }

  paintCheck(res) {
    const checks = res.checks || [];
    const okN = checks.filter(c => c.ok).length;
    let head;
    if (res.status === "pass") head = `<div class="check-sum pass">✓ ${okN}/${checks.length} kontrol geçti — onaylandı</div>`;
    else if (res.status === "error") head = `<div class="check-sum fail">✗ Testler başlamadan program hata verdi</div>`;
    else if (res.status === "timeout") head = `<div class="check-sum fail">✗ Süre aşıldı</div>`;
    else head = `<div class="check-sum fail">✗ ${okN}/${checks.length} kontrol geçti</div>`;
    const list = checks.map(c => `<li class="${c.ok ? "ok" : "no"}"><span class="ic">${c.ok ? "✓" : "✗"}</span><span>${render(c.msg).replace(/^<p>|<\/p>$/g, "")}</span>` +
      (!c.ok && (c.got !== undefined || c.exp !== undefined)
        ? `<div class="ge">${c.exp !== undefined ? `<span>beklenen</span><code>${esc(c.exp)}</code>` : ""}${c.got !== undefined ? `<span>senin</span><code>${esc(c.got)}</code>` : ""}</div>` : "") + "</li>").join("");
    const outText = segsHtml(res.segs);
    const out = outText ? `<div class="out-meta">programın çıktısı</div><pre class="out">${outText}</pre>` : "";
    this.pane.innerHTML = head + `<ul class="checks">${list}</ul>` + errCard(res.error) + out;
    if (res.error?.line && res.error.where !== "test") this.ed.mark(res.error.line, "err");
  }

  async xray() {
    this.busy("xray", "röntgen çekiliyor…");
    try {
      const res = await api("/api/run", { track: this.ctx.track, code: this.ed.value, stdin: this.stdin.value, mode: "trace", ...(this.ctx.lessonRef?.() || {}) });
      this.results.xray = res;
      this.x = { res, i: 0 };
      this.xrayStale = false;
      this.dot("xray", res.error ? "bad" : "ok");
      this.show("xray");
      this.pane.focus();
    } catch (e) { this.busy("xray", "Sunucuya ulaşılamadı: " + esc(e.message)); }
  }

  paintXray() {
    const res = this.x.res;
    if (!res.steps || !res.steps.length) {
      this.pane.innerHTML = errCard(res.error) || '<div class="pane empty">İzlenecek adım yok.</div>';
      if (res.error?.line) this.ed.mark(res.error.line, "err");
      return;
    }
    const n = res.steps.length;
    this.pane.innerHTML = `<div class="xray">
      <div class="xray-ctl">
        <button type="button" class="btn small" data-x="first" title="Başa">⏮</button>
        <button type="button" class="btn small" data-x="prev" title="Geri (←)">◀</button>
        <input type="range" min="0" max="${n - 1}" value="${this.x.i}" aria-label="Adım">
        <button type="button" class="btn small" data-x="next" title="İleri (→)">▶</button>
        <button type="button" class="btn small" data-x="last" title="Sona">⏭</button>
        <span class="info"></span>
      </div>
      <div class="xray-frames"></div>
      <div class="xray-out"><span class="label">bu adıma kadar çıktı</span><pre></pre>
        <div class="xray-legend">aynı renkli kare = aynı nesne (aynı id)<br>sarı isim = bu adımda değişti${res.truncated ? "<br>ilk 500 adım gösteriliyor" : ""}</div>
        ${res.error ? errCard(res.error) : ""}</div>
    </div>`;
    const range = $("input[type=range]", this.pane);
    range.addEventListener("input", () => this.xstep(+range.value));
    $$("[data-x]", this.pane).forEach(b => b.addEventListener("click", () => {
      const a = b.dataset.x, i = this.x.i;
      this.xstep(a === "first" ? 0 : a === "last" ? n - 1 : a === "prev" ? i - 1 : i + 1);
    }));
    this.xstep(this.x.i);
  }

  xstep(i) {
    const res = this.x.res, steps = res.steps;
    i = Math.max(0, Math.min(steps.length - 1, i));
    this.x.i = i;
    const st = steps[i], prev = steps[i - 1];
    const range = $("input[type=range]", this.pane);
    if (range) range.value = i;
    const ev = { line: "satır", return: "dönüş", exception: "hata" }[st.ev] || st.ev;
    const top = st.frames[st.frames.length - 1];
    $(".info", this.pane).innerHTML = `adım ${i + 1}/${steps.length} · satır ${st.line} · <span class="ev-${st.ev}">${ev}</span>${top && top.name !== "<module>" ? " · " + esc(top.name) + "()" : ""}`;
    const prevVars = {};
    if (prev) for (const f of prev.frames) for (const [k, v] of f.vars) prevVars[f.name + ":" + k] = v.r;
    const color = id => `hsl(${(id * 2654435761 % 4294967296) / 4294967296 * 360} 72% 58%)`;
    const frames = st.frames.slice().reverse().map((f, fi) => {
      const rows = f.vars.map(([k, v]) => {
        const changed = prevVars[f.name + ":" + k] !== v.r;
        return `<tr class="${changed && prev ? "changed" : ""}"><td class="n">${esc(k)}</td><td class="t">${esc(v.t)}</td>` +
          `<td class="v"><i class="oid" style="background:${color(v.id)}" title="id ${v.id}"></i>${esc(v.r)}</td></tr>`;
      }).join("") || `<tr><td class="t" colspan="3">— henüz isim yok —</td></tr>`;
      const isTop = fi === 0;
      const ret = isTop && st.ev === "return" && f.name !== "<module>" ? `<div class="ret">↩ döndürülen: ${esc(st.ret.r)}</div>` : "";
      const exc = isTop && st.ev === "exception" ? `<div class="ret" style="color:var(--bad)">⚠ ${esc(st.exc)}</div>` : "";
      return `<div class="frame ${isTop ? "top" : ""}"><div class="frame-h"><span>${f.name === "<module>" ? "global (ana kod)" : esc(f.name) + "() çerçevesi"}</span><span>satır ${f.line}</span></div><table>${rows}</table>${ret}${exc}</div>`;
    }).join("");
    $(".xray-frames", this.pane).innerHTML = frames;
    $(".xray-out pre", this.pane).textContent = res.out.slice(0, st.out);
    this.ed.mark(st.line, "step");
  }

  // Bash/PowerShell izi: çalışan komutlar sırayla, satır işaretiyle
  paintIz() {
    const res = this.x.res, iz = res.iz || [];
    if (!iz.length) {
      this.pane.innerHTML = (errCard(res.error) || "") + '<div class="out-meta">İzlenecek komut yok.</div>' +
        (res.out ? `<pre class="out">${esc(res.out)}</pre>` : "");
      return;
    }
    const n = iz.length;
    this.pane.innerHTML = `<div class="xray">
      <div class="xray-ctl">
        <button type="button" class="btn small" data-x="first" title="Başa">⏮</button>
        <button type="button" class="btn small" data-x="prev" title="Geri (←)">◀</button>
        <input type="range" min="0" max="${n - 1}" value="${this.x.i}" aria-label="Adım">
        <button type="button" class="btn small" data-x="next" title="İleri (→)">▶</button>
        <button type="button" class="btn small" data-x="last" title="Sona">⏭</button>
        <span class="info"></span>
      </div>
      <div class="xray-frames"><ul class="iz-liste">${iz.map((s, i) =>
        `<li data-i="${i}"><span class="ln">s.${s.line}${s.derinlik > 1 ? " " + "↳".repeat(s.derinlik - 1) : ""}</span><span>${esc(s.metin)}</span></li>`).join("")}</ul></div>
      <div class="xray-out">${argvSatiri(res)}<span class="label">betiğin çıktısı</span><pre>${esc(res.out || "")}</pre>
        <div class="xray-legend">her satır, yorumlayıcının çalıştırdığı bir komuttur<br>değişkenler yerine değerleri yazılmış haldedir</div>
        ${res.error ? errCard(res.error) : ""}</div>
    </div>`;
    const range = $("input[type=range]", this.pane);
    range.addEventListener("input", () => this.izStep(+range.value));
    $$("[data-x]", this.pane).forEach(b => b.addEventListener("click", () => {
      const a = b.dataset.x, i = this.x.i;
      this.izStep(a === "first" ? 0 : a === "last" ? n - 1 : a === "prev" ? i - 1 : i + 1);
    }));
    $(".iz-liste", this.pane).addEventListener("click", e => {
      const li = e.target.closest("li[data-i]");
      if (li) this.izStep(+li.dataset.i);
    });
    this.izStep(this.x.i);
  }

  izStep(i) {
    const iz = this.x.res.iz;
    i = Math.max(0, Math.min(iz.length - 1, i));
    this.x.i = i;
    const range = $("input[type=range]", this.pane);
    if (range) range.value = i;
    $$(".iz-liste li", this.pane).forEach((li, j) => li.classList.toggle("on", j === i));
    const on = $(".iz-liste li.on", this.pane);
    if (on) on.scrollIntoView({ block: "nearest" });
    $(".info", this.pane).textContent = `komut ${i + 1}/${iz.length} · satır ${iz[i].line}`;
    this.ed.mark(iz[i].line, "step");
  }

  async dis() {
    this.busy("dis", "çıkarılıyor…");
    try {
      const res = await api("/api/run", { track: this.ctx.track, code: this.ed.value, mode: "dis", ...(this.ctx.lessonRef?.() || {}) });
      this.results.dis = res;
      this.show("dis");
    } catch (e) { this.busy("dis", "Sunucuya ulaşılamadı: " + esc(e.message)); }
  }

  paintDis(res) {
    if (res.error) { this.pane.innerHTML = errCard(res.error); return; }
    const html = esc(res.text).replace(/\b([A-Z][A-Z_]{2,})\b/g, '<span class="op">$1</span>')
      .replace(/^(\s*\d+)(?=\s)/gm, '<span class="ln">$1</span>');
    const aciklama = {
      regex: "LITERAL = düz karakter (kod numarası) · IN = karakter kümesi · MAX_REPEAT = açgözlü tekrar · MIN_REPEAT = tembel tekrar · SUBPATTERN = grup · AT = çapa · BRANCH = alternatif",
      sql: "SCAN = tablonun tamamı okunur · SEARCH = indeks ya da anahtarla doğrudan arama · TEMP B-TREE = sıralamak/gruplamak için geçici yapı · girinti = iç içe adım",
      kql: "her | aşaması bir WITH adımı (a1, a2, ...) · [__sira] = sort/top sonrası sırayı taşıyan gizli sütun · contains/has/startswith = KQL gibi büyük-küçük harfe duyarsız yardımcı fonksiyonlar",
      spl: "her | komutu bir WITH adımı (a1, a2, ...) · [__sira] = olayların sırasını taşıyan gizli sütun · spl_esit/spl_wild = aramadaki büyük-küçük harfe duyarsız eşitlik ve * joker karakteri",
    }[this.dil] || "sol sütun: kaynak satırı · sonra: bayt konumu · komut · argüman";
    this.pane.innerHTML = `<div class="out-meta" style="margin:0 0 8px">${aciklama}</div><pre class="dis">${html}</pre>`;
  }
}

// ── HARİTA ────────────────────────────────────────────────────────────────────
function lessonStats(lesson, steps) {
  const total = lesson.kinds.length;
  let done = 0;
  for (let i = 0; i < total; i++) if (steps[`${lesson.id}:${i}`]?.done) done++;
  return { total, done };
}

async function renderMap(tid) {
  S.mode = "map";
  const st = await refreshHeader();
  const aktifler = (st?.tracks || []).filter(t => t.status === "active");
  if (!tid) tid = (st?.last && aktifler.some(t => t.id === st.last.track)) ? st.last.track : (aktifler[0]?.id || "python");
  let tv;
  try { tv = await api(`/api/track/${tid}`); }
  catch (e) { view.innerHTML = `<div class="page"><div class="empty-state">Bu yol bulunamadı: ${esc(tid)}<br><a class="btn" href="#/">Haritaya dön</a></div></div>`; return; }
  const track = tv.track, steps = tv.steps;
  if (track.status !== "active" || !track.order.length) {
    view.innerHTML = `<div class="page"><div class="empty-state">${esc(track.name)} yolu henüz yazılmadı.<br><br><a class="btn" href="#/">Haritaya dön</a></div></div>`;
    return;
  }
  S.mapTid = tid;
  const ranks = track.ranks || [];
  let lessonsDone = 0, lessonsTotal = 0, gorevDone = 0, gorevTotal = 0;
  let firstOpen = null;
  for (const m of track.modules) for (const l of m.lessons) {
    if (l.missing) continue;
    lessonsTotal++;
    const s = lessonStats(l, steps);
    if (s.total && s.done === s.total) lessonsDone++;
    else if (!firstOpen) firstOpen = { lesson: l, module: m };
    l.kinds.forEach((k, i) => { if (k === "gorev") { gorevTotal++; if (steps[`${l.id}:${i}`]?.done) gorevDone++; } });
  }
  const last = st.last && st.last.track === tid ? st.last : null;
  const currentId = last ? last.lesson : firstOpen?.lesson.id;
  const curRank = ranks.find(r => r.id === (firstOpen?.module.rank)) || ranks[ranks.length - 1] || { name: "—" };
  const cta = last
    ? `<a class="btn primary" href="#/ders/${tid}/${last.lesson}/${last.step}">Kaldığın yerden → ${esc(last.lesson.toUpperCase())}</a>`
    : `<a class="btn primary" href="#/ders/${tid}/${track.order[0]}/0">İlk paftayı aç →</a>`;
  const pct = (a, b) => (b ? Math.round(a / b * 100) : 0);
  const [kahraman1, kahraman2, kahraman3] = track.kahraman || ["Minik'ten", "Başpehlivan", "'a"];

  const rankHtml = ranks.map((r, ri) => {
    const mods = track.modules.filter(m => m.rank === r.id);
    if (!mods.length) return "";
    const allDone = mods.every(m => m.lessons.every(l => { const s = lessonStats(l, steps); return s.total && s.done === s.total; }));
    return `<section class="rank ${allDone ? "done" : ""}"><div class="rank-tag"><span class="n">${pad(ri + 1)}</span>${esc(r.name)}</div><div class="rank-body">` +
      mods.map(m => `<div class="mod"><div class="mod-head"><span class="mod-num">M${pad(m.index)}</span><span class="mod-title">${esc(m.title)}</span>` +
        (m.zen ? `<span class="mod-zen">“${esc(m.zen)}”</span>` : "") + `</div><div class="chain">` +
        m.lessons.map(l => {
          const s = lessonStats(l, steps);
          const cls = l.missing ? "missing" : s.total && s.done === s.total ? "done" : s.done ? "part" : "";
          const cur = l.id === currentId ? " current" : "";
          return `<a class="node ${cls}${cur}" href="#/ders/${tid}/${l.id}/0" title="${esc(l.summary || l.title)}">` +
            `<span class="nid"><span>${esc(l.id.toUpperCase())}</span><span>${s.done}/${s.total}</span></span><span class="nt">${esc(l.title)}</span>` +
            `<span class="np"><i style="width:${pct(s.done, s.total)}%"></i></span></a>`;
        }).join("") + `</div></div>`).join("") + `</div></section>`;
  }).join("");

  const sekmeler = aktifler.map(t => `<a href="#/yol/${t.id}" class="${t.id === tid ? "on" : ""}">${esc(t.name)}` +
    `<small>${t.steps_done || 0}/${t.steps_total || 0}</small></a>`).join("");

  const groups = [["her-iki", "⚔ Her iki taraf"], ["savunma", "🔵 Savunma tarafı"], ["okuma", "🟡 Okuyabilecek kadar"]];
  const roads = groups.map(([g, name]) => {
    const ts = st.tracks.filter(t => t.group === g);
    return `<div class="road-col"><span class="label">${name}</span>` + ts.map(t => {
      const aktif = t.status === "active";
      const etiket = aktif ? (t.hazir === false ? "KURULUM GEREKİR" : t.id === tid ? "AÇIK" : "AKTİF") : "PLANLI";
      return `<div class="road ${aktif ? "active" : ""}" ${aktif ? `data-go="#/yol/${t.id}"` : ""}>` +
        `<b>${esc(t.name)}</b><span class="st ${aktif ? "on" : ""}">${etiket}</span>` +
        `<p>${esc(t.role || "")}</p></div>`;
    }).join("") + `</div>`;
  }).join("");

  const sira = Math.max(1, aktifler.findIndex(t => t.id === tid) + 1);
  view.innerHTML = `<div class="map">
    ${aktifler.length > 1 ? `<nav class="yol-sekme" aria-label="Dil yolları">${sekmeler}</nav>` : ""}
    <section class="hero">
      <div class="hero-main">
        <div class="hero-kicker"><span class="label">Yol ${pad(sira)} · ${esc(track.name)}</span><span class="dim"></span><span class="label">Rütbe: ${esc(curRank.name)}</span></div>
        <h1 class="hero-title">${esc(kahraman1)}<br><em>${esc(kahraman2)}</em>${esc(kahraman3 || "")}</h1>
        <p class="hero-sub">${esc(track.tagline || "")}</p>
        <div class="hero-cta">${cta}${st.due_count ? `<a class="btn" href="#/tekrar">Tekrar · ${st.due_count} görev</a>` : ""}<a class="btn" href="#/tezgah/${track.dil || tid}">Serbest tezgah</a></div>
      </div>
      <div class="hero-cells">
        <div class="cell"><span class="label">Seri</span><span class="cell-val">${st.streak}<small>gün</small></span></div>
        <div class="cell"><span class="label">Tekrar bekleyen</span><span class="cell-val">${st.due_count}<small>görev</small></span></div>
        <div class="cell"><span class="label">Pafta</span><span class="cell-val">${lessonsDone}<small>/ ${lessonsTotal}</small></span><span class="bar"><i style="width:${pct(lessonsDone, lessonsTotal)}%"></i></span></div>
        <div class="cell"><span class="label">Görev</span><span class="cell-val">${gorevDone}<small>/ ${gorevTotal}</small></span><span class="bar"><i style="width:${pct(gorevDone, gorevTotal)}%"></i></span></div>
      </div>
    </section>
    ${track.hazir === false ? `<div class="callout tuzak" style="margin-top:16px"><div class="ct">Kurulum gerekiyor</div><p>Bu yolun yorumlayıcısı bu bilgisayarda bulunamadı. ${track.dil === "bash" ? "Git for Windows (Git Bash) kurulunca" : "Yorumlayıcı kurulunca"} paftalar çalışır.</p></div>` : ""}
    <div class="sec-head"><h2>Paftalar</h2><span class="dimline"></span><span class="label">${track.order.length} pafta · ${ranks.length} rütbe · her pafta: anlat → tahmin → görev</span></div>
    ${rankHtml}
    <div class="sec-head"><h2>Yol haritası</h2><span class="dimline"></span><span class="label">purple team dilleri · aynı motor, yeni yol</span></div>
    <div class="roads">${roads}</div>
  </div>`;
  view.onclick = e => {
    const g = e.target.closest("[data-go]");
    if (g) location.hash = g.dataset.go;
  };
}

// ── DERS ──────────────────────────────────────────────────────────────────────
function stepDone(i) { return !!S.lesson.progress.steps[i]?.done; }

function lessonComplete() {
  return S.lesson.lesson.steps.every((_, i) => stepDone(i));
}

async function renderLesson(tid, lid, idx, opts = {}) {
  const same = S.mode === "lesson" && S.lesson && S.lesson.lesson.id === lid && S.tid === tid && !opts.force;
  if (!same) {
    let v;
    try { v = await api(`/api/lesson/${tid}/${lid}`); }
    catch (e) { view.innerHTML = `<div class="page"><div class="empty-state">Bu pafta bulunamadı: ${esc(lid)}<br><a class="btn" href="#/">Haritaya dön</a></div></div>`; return; }
    S.lesson = v; S.tid = tid; S.mode = "lesson";
    S.yol = v.track || { id: tid, dil: "python", ozellik: { roentgen: true, dis: "Bytecode" }, ranks: [] };
    S.ranks = Object.fromEntries((S.yol.ranks || []).map(r => [r.id, r.name]));
    const L = v.lesson, loc = v.loc, mod = loc.module || { index: 0, title: "", rank: "" };
    view.onclick = null;
    view.innerHTML = `<div class="lesson">
      <div class="sheet-wrap"><article class="sheet" id="sheet">
        <div class="sheet-head">
          <div class="crumbs"><a class="label" href="#/yol/${tid}">← ${esc(S.yol.name || "Harita")}</a><span class="label">M${pad(mod.index)} · ${esc(mod.title)}</span><span class="label">${esc(L.id.toUpperCase())} / ${loc.total}</span></div>
          <h1 class="sheet-title">${esc(L.title)}</h1>
          <p class="sheet-summary">${esc(L.summary)}</p>
          <div class="dims" id="dims"></div>
        </div>
        <div class="sheet-body" id="stepBody"></div>
        <div class="sheet-foot" id="stepFoot"></div>
        <div class="antet" id="antet"></div>
      </article></div>
      <section class="bench" id="bench"></section>
    </div>`;
    S.bench = new Bench($("#bench"), {
      track: tid,
      dil: S.yol.dil,
      ozellik: S.yol.ozellik,
      checkable: () => S.lesson.lesson.steps[S.idx]?.kind === "gorev",
      lessonRef: () => ({ lesson: lid, step: S.idx }),
      check: async code => {
        const res = await api("/api/check", { track: tid, lesson: lid, step: S.idx, code });
        if (res.progress) {
          S.lesson.progress.steps[S.idx] = Object.assign(S.lesson.progress.steps[S.idx] || {}, { attempts: res.progress.attempts });
          paintTaskStatus();
        }
        return res;
      },
      onPass: res => onPass(res),
      saveDraft: code => {
        const st = S.lesson.lesson.steps[S.idx];
        if (st?.kind !== "gorev") return null;
        S.lesson.progress.drafts[S.idx] = code;
        return api("/api/draft", { track: tid, lesson: lid, step: S.idx, code });
      },
    });
    $("#sheet").addEventListener("click", sheetClick);
  }
  showStep(Math.max(0, Math.min(idx, S.lesson.lesson.steps.length - 1)));
}

function antet() {
  const L = S.lesson.lesson, loc = S.lesson.loc, mod = loc.module || {};
  const doneN = L.steps.filter((_, i) => stepDone(i)).length;
  const durum = lessonComplete() ? "ONAYLI" : doneN ? `${doneN}/${L.steps.length}` : "ÇİZİLİYOR";
  return `<div><span>Pafta</span><b>${esc(L.id.toUpperCase())}</b></div><div><span>Konu</span><b>${esc(L.title)}</b></div><div><span>Rütbe</span><b>${esc(S.ranks[mod.rank] || mod.rank || "—")}</b></div>` +
    `<div><span>Adım</span><b>${S.idx + 1} / ${L.steps.length}</b></div><div><span>Modül</span><b>M${pad(mod.index || 0)} · ${esc(mod.title || "")}</b></div><div><span>Ölçek</span><b>1 : 1</b></div>` +
    `<div><span>Çizen</span><b>SEN</b></div><div><span>Tarih</span><b>${trDate()}</b></div><div><span>Durum</span><b>${durum}</b></div>`;
}

function paintDims() {
  const L = S.lesson.lesson;
  $("#dims").innerHTML = L.steps.map((s, i) =>
    `<button type="button" class="dim ${stepDone(i) ? "done" : ""} ${i === S.idx ? "cur" : ""}" data-step="${i}" title="${esc(s.title || KIND_LABEL[s.kind])}">` +
    `<span class="box">${stepDone(i) ? "✓" : KIND_ICON[s.kind]}</span><span class="k">${i + 1} · ${KIND_LABEL[s.kind]}</span></button>`).join("") +
    `<span class="dim-total">${L.steps.length} ADIM</span>`;
  $("#antet").innerHTML = antet();
}

const DIL_ETIKET = { python: "python|py", bash: "bash|sh", powershell: "powershell|ps1?", regex: "regex", sql: "sql", kql: "kql|kusto", spl: "spl|splunk", javascript: "javascript|js" };
const BOS_KOD = {
  python: "# Bu adımdaki örnekleri ⇢ Tezgaha al ile buraya getirip kurcalayabilirsin.\n",
  bash: "# Bu adımdaki örnekleri ⇢ Tezgaha al ile buraya getirip kurcalayabilirsin.\n",
  powershell: "# Bu adımdaki örnekleri ⇢ Tezgaha al ile buraya getirip kurcalayabilirsin.\n",
  regex: "",
  sql: "-- Bu adımdaki örnekleri ⇢ Tezgaha al ile buraya getirip kurcalayabilirsin.\n-- Tablolar: ekipler, personel, sunucular, biletler, olcumler\n",
  kql: "// Bu adımdaki örnekleri ⇢ Tezgaha al ile buraya getirip kurcalayabilirsin.\n// Tablolar: ekipler, personel, sunucular, biletler, olcumler\n",
  spl: "sourcetype=biletler | head 5\n",
  javascript: "// Bu adımdaki örnekleri ⇢ Tezgaha al ile buraya getirip kurcalayabilirsin.\n",
};
// Okuma yolları (C, PHP): kod çalıştırılmaz; görevlerde okunan kodun Python karşılığı yazılır
const OKUMA_BOS = "# Bu yolda okuduğun kod bu bilgisayarda çalıştırılamıyor.\n# Görevlerde onun yaptığını Python ile yazacaksın; tezgah o görevler içindir.\n";
const TAHMIN_DIL = {
  regex: { girdi: "Desen şu metinde aranıyor:", etiket: "Tahminin — yakalanan parçaları satır satır yaz", baslik: "Bu desen neleri yakalar?", kod: "" },
  sql: { etiket: "Tahminin — her sonuç satırını ayrı satıra, sütunları | ile ayırarak yaz (boş değer için NULL)",
    baslik: "Bu sorgu ne döndürür?", ornek: "ör. web01|72", kod: "-- Önce soldaki sorgunun sonucunu tahmin et.\n-- Tahmin ettikten sonra sorgu buraya gelir; değiştirip denersin.\n" },
  javascript: { kod: "// Önce soldaki kodun çıktısını tahmin et.\n// Tahmin ettikten sonra kod buraya gelir; değiştirip denersin.\n" },
  c: { baslik: "Bu C programı ne yazdırır?", kod: OKUMA_BOS },
  php: { baslik: "Bu PHP kodu ne yazdırır?", kod: OKUMA_BOS },
  spl: { etiket: "Tahminin — her sonuç satırını ayrı satıra, sütunları | ile ayırarak yaz (boş değer boş kalır)",
    baslik: "Bu arama ne döndürür?", ornek: "ör. web01|72", kod: "" },
  kql: { etiket: "Tahminin — her sonuç satırını ayrı satıra, sütunları | ile ayırarak yaz (boş değer boş kalır)",
    baslik: "Bu sorgu ne döndürür?", ornek: "ör. web01|72", kod: "// Önce soldaki sorgunun sonucunu tahmin et.\n// Tahmin ettikten sonra sorgu buraya gelir; değiştirip denersin.\n" },
};

function firstCode(md, dil = "python") {
  const re = new RegExp("```(?:" + (DIL_ETIKET[dil] || dil) + ")(?![^\\n]*norun)[^\\n]*\\n([\\s\\S]*?)```");
  const m = (md || "").match(re);
  if (!m) return { code: "", stdin: "" };
  if (dil === "regex") { const [desen, metin] = regexParcala(m[1]); return { code: desen, stdin: metin }; }
  return { code: stripAnno(m[1]), stdin: "" };
}

function showStep(i) {
  S.idx = i;
  const L = S.lesson.lesson, st = L.steps[i];
  const tid = S.tid, lid = L.id, dil = dilAdi(S.yol?.dil || "python");
  const okuma = S.yol?.okuma_dili;           // C, PHP: okunan dil; tezgah ve görevler Python
  if (location.hash !== `#/ders/${tid}/${lid}/${i}`) history.replaceState(null, "", `#/ders/${tid}/${lid}/${i}`);
  api("/api/visit", { track: tid, lesson: lid, step: i, done: false }).catch(() => {});
  $$(".stamp", $("#sheet")).forEach(s => s.remove());
  paintDims();
  const head = `<div class="step-kind"><span class="tag ${st.kind}">${KIND_LABEL[st.kind].toLocaleUpperCase("tr")}</span><span class="label">Adım ${i + 1} / ${L.steps.length}</span></div>`;
  let body = "";
  if (st.kind === "anlat") {
    body = `<h2 class="step-title">${esc(st.title || "Anlatım")}</h2><div class="md">${render(st.body, { dil })}</div>`;
    const ilk = firstCode(st.body, dil);
    S.bench.load({ code: okuma ? OKUMA_BOS : (ilk.code || BOS_KOD[dil] || ""), stdin: ilk.stdin, resetCode: ilk.code });
  } else if (st.kind === "tahmin") {
    const [q, expl] = (st.body || "").split(/\n\?\?\?\s*\n?/);
    const prog = S.lesson.progress.steps[i];
    const td = TAHMIN_DIL[okuma || dil] || {};
    const girdiMetni = td.girdi || "Girdi kutusunda şu satırlar var:";
    const ipucuEtiket = td.etiket || "Tahminin — çıktıyı satır satır yaz (hata bekliyorsan hatanın adını yaz)";
    body = `<h2 class="step-title">${esc(st.title || td.baslik || "Bu kod ne yazdırır?")}</h2><div class="md">${render(q || "", { dil })}</div>` +
      codeBlock(st.code, okuma || dil, { runnable: false, bench: false }) +
      (st.stdin ? `<div class="md"><p>${girdiMetni}</p></div>${codeBlock(st.stdin, "cikti")}` : "") +
      `<div class="guess"><span class="label">${ipucuEtiket}</span>` +
      `<textarea id="guessBox" rows="3" spellcheck="false" placeholder="${td.ornek || "ör. 42"}"></textarea>` +
      `<div class="guess-row"><button type="button" class="btn primary small" data-act="guess">Tahmini gönder</button>` +
      (prog?.done ? `<span class="label">daha önce: ${prog.guess_ok ? "doğru" : "yanlış"}</span>` : "") + `</div></div>` +
      `<div id="guessResult"></div><div class="md" id="guessExpl" hidden>${render(expl || "", { dil })}</div>`;
    S.bench.load({ code: td.kod ?? "# Önce soldaki kodun çıktısını tahmin et.\n# Tahmin ettikten sonra kod buraya gelir; değiştirip denersin.\n", resetCode: st.code });
  } else {
    const prog = S.lesson.progress.steps[i] || {};
    const draft = S.lesson.progress.drafts[i];
    body = `<h2 class="step-title">${esc(st.title || "Görev")}</h2><div class="md">${render(st.body, { dil })}</div>` +
      `<div class="task-status" id="taskStatus"></div>` +
      `<div class="hints" id="hints"></div><div id="solution"></div>`;
    S.bench.load({ code: draft ?? st.starter ?? "", stdin: st.stdin || "", resetCode: st.starter || "", checkable: true });
    S.hintN = 0;
  }
  $("#stepBody").innerHTML = head + body;
  if (st.kind === "gorev") paintTaskStatus();
  paintFoot();
  if (stepDone(i) && st.kind === "gorev") stamp("ONAYLANDI", `görev · ${trDate()}`, false);
  $(".sheet-wrap").scrollTop = 0;
}

function paintTaskStatus() {
  const st = S.lesson.lesson.steps[S.idx];
  const prog = S.lesson.progress.steps[S.idx] || {};
  const a = prog.attempts || 0;
  const passed = stepDone(S.idx);
  const canSolve = st.has_solution && (a >= 2 || passed || prog.revealed);
  $("#taskStatus").innerHTML =
    `<span class="st ${passed ? "pass" : ""}">${passed ? "✓ geçti" : a ? `${a} deneme` : "henüz denemedin"}</span>` +
    `<span class="label">Ctrl+⇧+↵ ile kontrol et</span><span style="flex:1"></span>` +
    (st.hints.length ? `<button type="button" class="btn small" data-act="hint" ${S.hintN >= st.hints.length ? "disabled" : ""}>İpucu ${S.hintN}/${st.hints.length}</button>` : "") +
    (st.has_solution ? `<button type="button" class="btn small" data-act="solution" ${canSolve ? "" : `title="2 denemeden sonra açılır"`}>Çözümü göster</button>` : "");
}

function paintFoot() {
  const L = S.lesson.lesson, st = L.steps[S.idx], last = S.idx === L.steps.length - 1;
  const blocked = st.kind !== "anlat" && !stepDone(S.idx);
  const next = S.lesson.loc.next;
  let right;
  if (last) {
    right = lessonComplete() || !blocked
      ? (next ? `<button type="button" class="btn primary" data-act="finish">Paftayı bitir → ${esc(next.toUpperCase())}</button>` : `<button type="button" class="btn primary" data-act="finish">Paftayı bitir ✓</button>`)
      : `<button type="button" class="linkish" data-act="skip">şimdilik atla</button><button type="button" class="btn primary" disabled>${st.kind === "gorev" ? "Önce görevi geç" : "Önce tahmin et"}</button>`;
  } else {
    right = blocked
      ? `<button type="button" class="linkish" data-act="skip">şimdilik atla</button><button type="button" class="btn primary" disabled>${st.kind === "gorev" ? "Önce görevi geç" : "Önce tahmin et"}</button>`
      : `<button type="button" class="btn primary" data-act="next">İleri →</button>`;
  }
  $("#stepFoot").innerHTML = `<button type="button" class="btn" data-act="prev" ${S.idx === 0 ? "disabled" : ""}>← Geri</button><span class="grow"></span>${right}`;
  if (lessonComplete() && last) {
    $("#stepBody").insertAdjacentHTML("beforeend", `<div class="done-card"><h3>Pafta onaylandı.</h3><p>Bu paftanın tüm adımlarını bitirdin. Görevler tekrar kutusuna girdi: yarın, sonra 3, 7, 16 ve 35 gün sonra yeniden sorulacaklar — kalıcı öğrenme bu aralıklarla olur.</p></div>`);
  }
}

function stamp(text, sub, anim = true) {
  $$(".stamp", $("#sheet")).forEach(s => s.remove());
  $("#sheet").insertAdjacentHTML("afterbegin", `<div class="stamp ${anim ? "thunk" : ""}">${esc(text)}<small>${esc(sub)}</small></div>`);
}

async function onPass(res) {
  const i = S.idx;
  const was = stepDone(i);
  S.lesson.progress.steps[i] = Object.assign(S.lesson.progress.steps[i] || {}, { done: true, attempts: res.progress?.attempts });
  paintDims();
  paintTaskStatus();
  paintFoot();
  stamp(lessonComplete() ? "PAFTA ONAYLANDI" : "ONAYLANDI", `${lessonComplete() ? S.lesson.lesson.id.toUpperCase() : "görev " + (i + 1)} · ${trDate()}`);
  if (!was) toast("Görev geçti. Tekrar kutusuna eklendi.");
  refreshHeader();
}

async function sheetClick(e) {
  const d = e.target.closest("[data-step]");
  if (d) { showStep(+d.dataset.step); return; }
  const a = e.target.closest("[data-act]");
  if (!a) return;
  const act = a.dataset.act, L = S.lesson.lesson, tid = S.tid, lid = L.id, i = S.idx;
  if (act === "run" || act === "bench") {
    const block = a.closest(".code");
    const src = block.dataset.src, metin = block.dataset.stdin || "";
    if (act === "bench") {
      S.bench.setCode(src);
      if (metin || dilAdi(S.yol?.dil) === "regex") S.bench.setStdin(metin);
      toast("Tezgaha alındı");
      return;
    }
    const out = $(".run-out", block);
    out.hidden = false;
    out.textContent = "çalışıyor…";
    try {
      const res = await api("/api/run", { track: tid, code: src, stdin: metin, mode: "run", lesson: lid, step: i });
      if (res.eslesmeler) {
        out.innerHTML = res.error ? `<span style="color:var(--bad)">${esc(res.error.type + ": " + res.error.msg)}</span>`
          : res.eslesmeler.length ? `<span class="label">${res.eslesmeler.length} eşleşme</span>\n` + res.eslesmeler.map(e => esc(JSON.stringify(e.metin))).join("\n")
          : '<span class="label">eşleşme yok</span>';
        return;
      }
      if (res.tablolar) {
        out.classList.add("sql");
        out.innerHTML = sqlTablolar(res.tablolar, 25, res.kql) +
          (res.error ? `<span style="color:var(--bad)">${esc(res.error.type + ": " + res.error.msg)}</span>` : "");
        return;
      }
      const txt = (res.segs || []).map(s => s[1]).join("");
      out.innerHTML = esc(txt) + (res.error ? `<span style="color:var(--bad)">${txt ? "\n" : ""}${esc(res.error.type + ": " + res.error.msg)}</span>` : "") || '<span class="label">çıktı yok</span>';
    } catch (err) { out.textContent = "Sunucuya ulaşılamadı."; }
    return;
  }
  if (act === "prev") { if (i > 0) showStep(i - 1); return; }
  if (act === "next" || act === "skip") {
    if (L.steps[i].kind === "anlat" && !stepDone(i)) {
      S.lesson.progress.steps[i] = { done: true };
      await api("/api/visit", { track: tid, lesson: lid, step: i, done: true }).catch(() => {});
      refreshHeader();
    }
    if (i < L.steps.length - 1) showStep(i + 1);
    else if (act === "skip" && S.lesson.loc.next) location.hash = `#/ders/${tid}/${S.lesson.loc.next}/0`;
    return;
  }
  if (act === "finish") {
    if (L.steps[i].kind === "anlat" && !stepDone(i)) {
      await api("/api/visit", { track: tid, lesson: lid, step: i, done: true }).catch(() => {});
    }
    location.hash = S.lesson.loc.next ? `#/ders/${tid}/${S.lesson.loc.next}/0` : "#/";
    return;
  }
  if (act === "guess") {
    const g = $("#guessBox").value;
    if (!g.trim()) { toast("Önce bir tahmin yaz"); return; }
    a.disabled = true;
    try {
      const r = await api("/api/guess", { track: tid, lesson: lid, step: i, guess: g });
      const actual = segsHtml((r.result.segs || []).filter(s => s[0] === "out"));
      const errTxt = r.result.error ? esc(`${r.result.error.type}: ${r.result.error.msg}`) : "";
      $("#guessResult").innerHTML =
        `<div class="result-line ${r.correct ? "good" : "badc"}">${r.correct ? "✓ Doğru tahmin" : "✗ Tahmin tutmadı"}</div>` +
        `<div class="verdict"><div class="${r.correct ? "good" : "badc"}"><span class="label">senin tahminin</span><pre>${esc(g)}</pre></div>` +
        `<div class="good"><span class="label">gerçek çıktı</span><pre>${actual}${errTxt ? `<span style="color:var(--bad)">${actual ? "\n" : ""}${errTxt}</span>` : ""}</pre></div></div>`;
      $("#guessExpl").hidden = false;
      if (!stepDone(i)) S.lesson.progress.steps[i] = { done: true, guess_ok: r.correct };
      if (!S.yol?.okuma_dili) S.bench.load({ code: L.steps[i].code, stdin: L.steps[i].stdin || "", resetCode: L.steps[i].code });
      paintDims();
      paintFoot();
      refreshHeader();
    } catch (err) { toast("Sunucuya ulaşılamadı"); }
    a.disabled = false;
    return;
  }
  if (act === "hint") {
    const st = L.steps[i];
    if (S.hintN < st.hints.length) {
      $("#hints").insertAdjacentHTML("beforeend", `<div class="callout ipucu"><div class="ct">İpucu ${S.hintN + 1}</div>${render(st.hints[S.hintN], { dil: S.yol?.dil })}</div>`);
      S.hintN++;
      paintTaskStatus();
    }
    return;
  }
  if (act === "solution") {
    const prog = S.lesson.progress.steps[i] || {};
    if ((prog.attempts || 0) < 2 && !stepDone(i) && !prog.revealed &&
      !confirm("Henüz 2 kez denemedin. Çözüme bakarsan bu görev yarın tekrar karşına çıkar. Yine de bakmak istiyor musun?")) return;
    try {
      const r = await api("/api/solution", { track: tid, lesson: lid, step: i });
      S.lesson.progress.steps[i] = Object.assign(prog, { revealed: true });
      $("#solution").innerHTML = `<div class="callout derin"><div class="ct">Örnek çözüm</div>${codeBlock(r.solution, dilAdi(S.yol?.dil || "python"), { dil: S.yol?.dil })}<p>Çözümü kopyalamak yerine kapatıp kendin yeniden yaz — beyin ancak üretirken öğrenir.</p></div>`;
      paintTaskStatus();
      refreshHeader();
    } catch (err) { toast(err.message); }
  }
}

// ── TEKRAR ────────────────────────────────────────────────────────────────────
async function renderReview() {
  S.mode = "review";
  view.onclick = null;
  const [st, r] = await Promise.all([refreshHeader(), api("/api/review")]);
  const boxes = r.kutular || [0, 0, 0, 0, 0, 0];
  const yolAdi = Object.fromEntries((st?.tracks || []).map(t => [t.id, t.name]));
  const names = ["Kutu 1 · 1 gün", "Kutu 2 · 3 gün", "Kutu 3 · 7 gün", "Kutu 4 · 16 gün", "Kutu 5 · 35 gün", "Ustalaştın"];
  view.innerHTML = `<div class="page">
    <span class="label">Aralıklı tekrar · Leitner kutuları</span>
    <h1 class="page-title">Tekrar</h1>
    <p class="page-sub">Geçtiğin her görev buraya düşer ve giderek uzayan aralıklarla yeniden sorulur. Her seferinde boş sayfadan yazarsın; doğru yazınca bir üst kutuya çıkar. Çözüme bakarsan kutu 1'e döner.</p>
    <div class="boxes">${boxes.map((n, i) => `<div><span class="label">${names[i]}</span><b>${n}</b></div>`).join("")}</div>
    ${r.items.length ? `<div class="rev-list">${r.items.map(it =>
      `<a class="rev" href="#/tekrar/${it.track}/${it.lesson}/${it.step}"><span class="rid">${esc(yolAdi[it.track] || it.track)}<br>${esc(it.lesson.toUpperCase())} · K${it.box}</span>` +
      `<span><b>${esc(it.title)}</b><small>${esc(it.lesson_title)} · vadesi ${esc(it.due)}</small></span><span class="btn small">Çöz →</span></a>`).join("")}</div>`
      : `<div class="empty-state">Bugün tekrar bekleyen görev yok.<br><br><a class="btn primary" href="#/">Haritaya dön</a></div>`}
  </div>`;
}

async function renderReviewSolve(tid, lid, idx) {
  S.mode = "review-solve";
  view.onclick = null;
  const v = await api(`/api/lesson/${tid}/${lid}`);
  const st = v.lesson.steps[idx];
  S.yol = v.track || { id: tid, dil: "python", ozellik: { roentgen: true, dis: "Bytecode" } };
  const dil = dilAdi(S.yol.dil || "python");
  view.innerHTML = `<div class="lesson">
    <div class="sheet-wrap"><article class="sheet" id="sheet">
      <div class="sheet-head"><div class="crumbs"><a class="label" href="#/tekrar">← Tekrar</a><span class="label">${esc(S.yol.name || tid)} · ${esc(lid.toUpperCase())} · ${esc(v.lesson.title)}</span></div>
      <h1 class="sheet-title">${esc(st.title || "Görev")}</h1><p class="sheet-summary">Boş sayfadan, ezberden değil anlayarak yaz.</p></div>
      <div class="sheet-body"><div class="md">${render(st.body, { dil })}</div><div id="revStatus"></div><div class="hints" id="hints"></div></div>
      <div class="sheet-foot"><a class="btn" href="#/ders/${tid}/${lid}/0">Paftayı aç</a><span class="grow"></span><a class="btn" href="#/tekrar">Listeye dön</a></div>
    </article></div>
    <section class="bench" id="bench"></section></div>`;
  S.bench = new Bench($("#bench"), {
    track: tid,
    dil,
    ozellik: S.yol.ozellik,
    checkable: () => true,
    lessonRef: () => ({ lesson: lid, step: idx }),
    check: code => api("/api/check", { track: tid, lesson: lid, step: idx, code, review: true }),
    onPass: async res => {
      stamp("TEKRAR GEÇTİ", res.review ? `kutu ${res.review.box} · ${trDate()}` : trDate());
      const due = (await api("/api/review")).items.filter(it => !(it.track === tid && it.lesson === lid && it.step === idx));
      $("#revStatus").innerHTML = `<div class="done-card"><h3>Doğru.</h3><p>${res.review?.box >= 6 ? "Bu görevde ustalaştın." : `Kutu ${res.review?.box}'e çıktı; sonraki tekrar ${esc(res.review?.due || "")}.`}</p>` +
        (due.length ? `<a class="btn primary" href="#/tekrar/${due[0].track}/${due[0].lesson}/${due[0].step}">Sıradaki →</a>` : `<a class="btn primary" href="#/tekrar">Hepsi bitti →</a>`) + `</div>`;
      refreshHeader();
    },
  });
  S.bench.load({ code: st.starter || "", stdin: st.stdin || "", resetCode: st.starter || "", checkable: true });
}

// ── SERBEST TEZGAH ────────────────────────────────────────────────────────────
const TEZGAH_DILLER = [
  ["python", "Python", { roentgen: true, dis: "Bytecode" }],
  ["regex", "Regex", { roentgen: false, dis: "Ağaç" }],
  ["bash", "Bash", { roentgen: true, dis: null }],
  ["powershell", "PowerShell", { roentgen: true, dis: null }],
  ["sql", "SQL", { roentgen: false, dis: "Plan" }],
  ["kql", "KQL", { roentgen: false, dis: "SQL" }],
  ["spl", "SPL", { roentgen: false, dis: "SQL" }],
  ["javascript", "JS", { roentgen: false, dis: null }],
];
const TEZGAH_ORNEK = {
  python: `# Serbest tezgah: ne istersen dene. Kod otomatik kaydedilir.\n# ◎ Röntgen ile adım adım izle.\n\nhedefler = ["10.0.0.1", "10.0.0.2", "10.0.0.1"]\nbenzersiz = sorted(set(hedefler))\nfor i, ip in enumerate(benzersiz, 1):\n    print(i, ip)\n`,
  regex: String.raw`(?P<yil>\d{4})-(?P<ay>\d{2})-(?P<gun>\d{2})`,
  bash: `# Serbest tezgah (Git Bash). Girdi kutusu read ile okunur.\nfor dosya in rapor.txt veri.csv notlar.md; do\n  echo "\${dosya%.*} -> \${dosya##*.}"\ndone\n`,
  powershell: `# Serbest tezgah (Windows PowerShell). Girdi kutusu $Girdi dizisine gelir.\n1..5 | ForEach-Object { [pscustomobject]@{ Sayi = $_; Kare = $_ * $_ } } | Format-Table -AutoSize\n`,
  spl: `sourcetype=biletler durum=açık\n| stats count by oncelik\n| sort -count\n`,
  javascript: `// Serbest tezgah (Node.js). Girdi kutusu: require("fs").readFileSync(0, "utf8")\nconst sunucular = [{ ad: "web01", cpu: 72 }, { ad: "db01", cpu: 91 }, { ad: "web03", cpu: 18 }];\nconst yogun = sunucular.filter(s => s.cpu > 50).map(s => s.ad);\nconsole.log(yogun.join(", "));\n`,
  kql: `// Serbest tezgah (KQL). Sorgu SQLite'a çevrilip örnek veritabanında çalışır; SQL düğmesi karşılığını gösterir.\n// Tablolar: ekipler, personel, sunucular, biletler, olcumler\n\nbiletler\n| where durum == "açık"\n| summarize adet = count() by oncelik\n| sort by adet desc\n`,
  sql: `-- Serbest tezgah (SQLite). Örnek veritabanı her çalıştırmada sıfırdan kurulur.\n-- Tablolar: ekipler, personel, sunucular, biletler, olcumler\n\nSELECT s.ad, s.rol, COUNT(b.id) AS bilet\nFROM sunucular AS s\nLEFT JOIN biletler AS b ON b.sunucu_id = s.id\nGROUP BY s.id\nORDER BY bilet DESC, s.ad\nLIMIT 5;\n`,
};
const TEZGAH_METIN = { regex: "Kayıtlar: 2026-10-19 giriş, 2026-10-20 çıkış, 19.10.2026 eski biçim" };

async function renderPlayground(dil) {
  S.mode = "play";
  view.onclick = null;
  if (!TEZGAH_DILLER.some(d => d[0] === dil)) dil = "python";
  const [, , ozellik] = TEZGAH_DILLER.find(d => d[0] === dil);
  const r = await api(`/api/playground?dil=${encodeURIComponent(dil)}`);
  view.innerHTML = `<div class="playground"><section class="bench" id="bench"></section></div>`;
  S.bench = new Bench($("#bench"), {
    track: dil === "python" ? "python" : dil,
    dil,
    ozellik,
    checkable: () => false,
    saveDraft: code => api("/api/draft", { playground: code, dil }),
  });
  const secici = `<span class="dil-sec">${TEZGAH_DILLER.map(([k, ad]) =>
    `<button type="button" data-dil="${k}" class="${k === dil ? "on" : ""}">${ad}</button>`).join("")}</span>`;
  $(".bench-bar .sp", $("#bench")).insertAdjacentHTML("beforebegin", secici);
  $(".dil-sec", $("#bench")).addEventListener("click", e => {
    const b = e.target.closest("[data-dil]");
    if (b) location.hash = `#/tezgah/${b.dataset.dil}`;
  });
  S.bench.load({ code: r.code || TEZGAH_ORNEK[dil], stdin: TEZGAH_METIN[dil] || "", resetCode: TEZGAH_ORNEK[dil] });
}

// ── ayarlar ──────────────────────────────────────────────────────────────────
function openSettings() {
  const d = $("#dialog");
  const st = S.state || {};
  d.innerHTML = `<div class="dlg-head">Ayarlar</div><div class="dlg-body">
    <div class="dlg-row"><span>Tema</span><span><button class="btn small" data-theme-set="mavi">Mavi kopya</button> <button class="btn small" data-theme-set="ozalit">Ozalit</button></span></div>
    <div class="dlg-row"><span>Kısayollar</span><span class="mono">Ctrl+↵ çalıştır · Ctrl+⇧+↵ kontrol · Ctrl+/ yorum · Tab / ⇧Tab girinti · Röntgende ← →</span></div>
    <div class="dlg-row"><span>İlerleme dosyası</span><span class="mono">${esc(st.data_path || "")}</span></div>
    <div class="dlg-row"><span>İlerlemeyi sıfırla</span><button class="btn small" data-reset>Sıfırla…</button></div>
  </div><div class="dlg-foot"><button class="btn primary" data-close>Kapat</button></div>`;
  d.onclick = async e => {
    if (e.target.closest("[data-close]") || e.target === d) d.close();
    const t = e.target.closest("[data-theme-set]");
    if (t) { setTheme(t.dataset.themeSet); api("/api/settings", { key: "theme", value: t.dataset.themeSet }); }
    if (e.target.closest("[data-reset]")) {
      const w = prompt("Tüm ilerleme, taslaklar ve tekrar kutuları silinecek. Onaylamak için SIFIRLA yaz:");
      if (w === "SIFIRLA") { await api("/api/reset", { confirm: "SIFIRLA" }); d.close(); toast("İlerleme sıfırlandı"); route(); }
    }
  };
  d.showModal();
}

// ── yönlendirme ───────────────────────────────────────────────────────────────
function route() {
  const p = location.hash.replace(/^#\/?/, "").split("/").filter(Boolean).map(decodeURIComponent);
  const key = !p[0] || p[0] === "ders" || p[0] === "yol" ? "harita" : p[0];
  $$(".nav a").forEach(a => a.classList.toggle("on", a.dataset.nav === key));
  if (p[0] === "ders" && p[2]) return renderLesson(p[1], p[2], +(p[3] || 0));
  if (p[0] === "tekrar" && p[3] !== undefined) return renderReviewSolve(p[1], p[2], +p[3]);
  if (p[0] === "tekrar") return renderReview();
  if (p[0] === "tezgah") return renderPlayground(p[1]);
  if (p[0] === "yol" && p[1]) return renderMap(p[1]);
  return renderMap();
}

async function boot() {
  const st = await refreshHeader();
  if (st) {
    setTheme(st.settings?.theme || "mavi");
  }
  $("#themeBtn").addEventListener("click", () => {
    const t = document.documentElement.dataset.theme === "ozalit" ? "mavi" : "ozalit";
    setTheme(t);
    api("/api/settings", { key: "theme", value: t }).catch(() => {});
  });
  $("#settingsBtn").addEventListener("click", openSettings);
  // Editör odakta değilken de Ctrl+↵ çalıştırsın (editör kendi kısayolunu zaten işliyor)
  document.addEventListener("keydown", e => {
    if (e.defaultPrevented || !(e.ctrlKey || e.metaKey) || e.key !== "Enter") return;
    const b = S.bench;
    if (!b || !b.ed.ta.isConnected) return;
    if (e.target.closest?.("input, textarea, select") && !e.target.closest("#bench")) return;
    e.preventDefault();
    if (e.shiftKey) { if (b.ctx.checkable()) b.check(); }
    else b.run();
  });
  window.addEventListener("hashchange", route);
  setInterval(() => api("/api/ping", {}).catch(() => {}), 10000);
  route();
}

boot();
