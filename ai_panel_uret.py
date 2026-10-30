# -*- coding: utf-8 -*-
"""Pafta AI müfredat planını Markdown ve canlı HTML panel olarak üretir."""
from __future__ import annotations

import datetime as dt
import html
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "ai_mufredat_plan_v3.json"
HTML_OUT = ROOT / "AI_MUFREDAT_PANELI.html"
MD_OUT = ROOT / "AI_MUFREDAT_PLANI.md"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def lessons(data: dict):
    for track in data["tracks"]:
        for module in track["modules"]:
            for lesson in module["lessons"]:
                yield track, module, lesson


def validate(data: dict) -> None:
    ids = []
    allowed_statuses = set(data["statuses"])
    for track in data["tracks"]:
        if len(track["modules"]) != 6:
            raise ValueError(f"{track['id']}: altı modül gerekli")
        expected_ranks = ["minik", "tesviye", "kucuk-orta", "buyuk-orta", "basalti", "baspehlivan"]
        if [m["rank"] for m in track["modules"]] != expected_ranks:
            raise ValueError(f"{track['id']}: rütbe sırası bozuk")
        for module in track["modules"]:
            for lesson in module["lessons"]:
                ids.append(lesson["id"])
                if not lesson["id"].startswith(track["id"] + "-"):
                    raise ValueError(f"Yanlış ID/track eşleşmesi: {lesson['id']}")
                if lesson.get("status", "Planlandı") not in allowed_statuses:
                    raise ValueError(f"Bilinmeyen durum: {lesson['id']}")
                for key in ("title", "summary", "side", "tools"):
                    if not lesson.get(key):
                        raise ValueError(f"Eksik alan: {lesson['id']}/{key}")
    duplicates = [key for key, count in Counter(ids).items() if count > 1]
    if duplicates:
        raise ValueError("Yinelenen ders ID'leri: " + ", ".join(duplicates))
    known = set(ids)
    for _, _, lesson in lessons(data):
        if "onkosul" not in lesson or not isinstance(lesson["onkosul"], list):
            raise ValueError(f"Önkoşul listesi eksik: {lesson['id']}")
        missing = set(lesson["onkosul"]) - known
        if missing:
            raise ValueError(f"Bilinmeyen önkoşul: {lesson['id']} → {sorted(missing)}")
        if lesson["id"] in lesson["onkosul"]:
            raise ValueError(f"Ders kendine önkoşul olamaz: {lesson['id']}")


def markdown(data: dict) -> str:
    total = sum(1 for _ in lessons(data))
    track_total = len(data["tracks"])
    module_total = sum(len(t["modules"]) for t in data["tracks"])
    lines = [
        "# Pafta AI Güvenlik Müfredat Planı",
        "",
        f"**Kapsam:** {track_total} track · {module_total} modül · {total} ders · Yalnız başlık planı, ders içerikleri henüz yazılmadı.",
        "",
        "Her dersin ilk durumu **Planlandı**; yazım ve bağımsız denetim tamamlandıkça paneldeki durum ilerletilir.",
        "",
        data.get("field_goals", ""),
        "",
    ]
    for track in data["tracks"]:
        count = sum(len(m["lessons"]) for m in track["modules"])
        lines += [f"# Track: `{track['id']}` — {track['name']} ({count} ders)", ""]
        for index, module in enumerate(track["modules"], 1):
            lines += [
                f"## {index}. Modül — {module['name']} · {module['title']}",
                "",
                "| Ders | Başlık | Tek cümlelik kazanım | Taraf | Gerçek araç | Durum |",
                "|---|---|---|---|---|---|",
            ]
            for lesson in module["lessons"]:
                lines.append(
                    f"| `{lesson['id']}` | {lesson['title']} | {lesson['summary']} | "
                    f"{lesson['side']} | {lesson['tools']} | {lesson.get('status', 'Planlandı')} |"
                )
            lines.append("")
    return "\n".join(lines)


def page(data: dict) -> str:
    all_lessons = list(lessons(data))
    total = len(all_lessons)
    counts = Counter(l.get("status", "Planlandı") for _, _, l in all_lessons)
    track_total = len(data["tracks"])
    module_total = sum(len(t["modules"]) for t in data["tracks"])
    generated = dt.datetime.now().strftime("%d.%m.%Y %H:%M")
    sections = []
    for ti, track in enumerate(data["tracks"]):
        track_count = sum(len(m["lessons"]) for m in track["modules"])
        module_html = []
        for mi, module in enumerate(track["modules"]):
            rows = []
            for lesson in module["lessons"]:
                status = lesson.get("status", "Planlandı")
                side_class = {"Saldırı": "red", "Savunma": "blue", "Temel": "base", "Güvence": "blue", "Araştırma": "base"}[lesson["side"]]
                rows.append(f"""
<tr data-track="{esc(track['id'])}" data-status="{esc(status)}" data-rank="{esc(module['rank'])}" data-side="{esc(lesson['side'])}" data-tools="{esc(lesson['tools'])}" data-search="{esc((lesson['id']+' '+lesson['title']+' '+lesson['summary']+' '+lesson['tools']).lower())}">
 <td data-label="Ders"><code>{esc(lesson['id'])}</code></td><td data-label="Başlık ve kazanım"><strong>{esc(lesson['title'])}</strong><p>{esc(lesson['summary'])}</p></td>
 <td data-label="Taraf"><span class="side {side_class}">{esc(lesson['side'])}</span></td><td data-label="Gerçek araç">{esc(lesson['tools'])}</td>
 <td data-label="Durum"><span class="status s-{esc(status)}">{esc(status)}</span></td>
</tr>""")
            module_html.append(f"""
<details id="module-{esc(track['id'])}-{esc(module['rank'])}" class="module" open data-module-key="{esc(track['id'] + ':' + module['rank'])}" data-module-track="{esc(track['id'])}" data-rank="{esc(module['rank'])}">
 <summary><span class="rank">{mi+1:02d} · {esc(module['name'])}</span><span>{esc(module['title'])}</span><small>{len(module['lessons'])} ders</small></summary>
 <div class="table-wrap"><table><thead><tr><th>DERS</th><th>BAŞLIK VE KAZANIM</th><th>TARAF</th><th>GERÇEK ARAÇ</th><th>DURUM</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div>
</details>""")
        sections.append(f"""
<section class="track" data-track-section="{esc(track['id'])}">
 <header class="track-head"><span>TRACK / {ti+1:02d}</span><h2>{esc(track['id'])}</h2><p>{esc(track['name'])}</p><b>{track_count} ders</b></header>
 {''.join(module_html)}
</section>""")

    track_options = "".join(f'<option value="{esc(t["id"])}">{esc(t["id"])}</option>' for t in data["tracks"])
    rank_options = "".join(f'<option value="{r}">{n}</option>' for r, n in [("minik","Minik"),("tesviye","Tesviye"),("kucuk-orta","Küçük Orta"),("buyuk-orta","Büyük Orta"),("basalti","Başaltı"),("baspehlivan","Başpehlivan")])
    return f"""<!doctype html>
<html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Pafta · AI Müfredat Paneli</title>
<style>
:root{{--bg:#081d33;--panel:#0d2946;--panel2:#0a233d;--ink:#edf5ff;--soft:#adc3da;--faint:#7390ae;--line:rgba(184,214,246,.22);--yellow:#ffd43b;--green:#77dfb0;--red:#ff8d7e;--blue:#83c9ff;--purple:#c9aeff}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:14px/1.5 Verdana,'Segoe UI',sans-serif;background-image:linear-gradient(rgba(173,208,255,.045) 1px,transparent 1px),linear-gradient(90deg,rgba(173,208,255,.045) 1px,transparent 1px);background-size:32px 32px}}button,input,select{{font:inherit}}.page{{max-width:1440px;margin:auto;padding:28px 24px 70px}}.eyebrow{{font:600 11px Bahnschrift,'Segoe UI',sans-serif;letter-spacing:.18em;text-transform:uppercase;color:var(--faint)}}h1{{font:700 clamp(36px,6vw,64px)/1 Bahnschrift,'Segoe UI',sans-serif;letter-spacing:.02em;margin:6px 0 10px;text-transform:uppercase}}h1 em{{font-style:normal;color:var(--yellow)}}.lead{{color:var(--soft);max-width:900px;margin:0}}.meta{{margin-top:8px}}.summary{{display:grid;grid-template-columns:1.2fr repeat(3,1fr);border:1px solid var(--line);background:var(--panel2);margin:24px 0}}.stat{{padding:18px 20px;border-right:1px solid var(--line)}}.stat:last-child{{border:0}}.stat b{{display:block;font:700 38px/1.1 Bahnschrift,sans-serif;color:var(--yellow)}}.stat span{{color:var(--soft);font-size:12px}}.stat.Planlandı b{{color:var(--faint)}}.stat.Yazıldı b{{color:var(--yellow)}}.stat.Denetlendi b{{color:var(--green)}}.progress{{display:flex;height:7px;background:var(--line);margin-bottom:22px;overflow:hidden}}.progress i{{display:block;height:100%}}.progress .written{{background:var(--yellow)}}.progress .audited{{background:var(--green)}}.controls{{position:sticky;top:0;z-index:5;display:flex;gap:8px;flex-wrap:wrap;padding:12px;background:rgba(8,29,51,.96);border:1px solid var(--line);backdrop-filter:blur(10px)}}.controls input{{flex:1;min-width:220px}}.controls input,.controls select,.controls button{{background:var(--panel);border:1px solid var(--line);color:var(--ink);padding:8px 11px;outline:none}}.controls input:focus,.controls select:focus{{border-color:var(--yellow)}}.controls button{{cursor:pointer;color:var(--yellow)}}.result{{padding:10px 2px;color:var(--faint);font-size:12px}}.track{{margin:20px 0 32px}}.track-head{{display:grid;grid-template-columns:120px auto 1fr auto;align-items:center;gap:12px;border-left:4px solid var(--yellow);background:var(--panel);padding:14px 18px}}.track-head span{{color:var(--faint);font:11px Bahnschrift,sans-serif;letter-spacing:.14em}}.track-head h2{{font:700 24px Bahnschrift,sans-serif;margin:0;color:var(--yellow)}}.track-head p{{margin:0;color:var(--soft)}}.track-head b{{font:600 14px Bahnschrift,sans-serif}}.module{{border:1px solid var(--line);border-top:0;background:var(--panel2)}}.module summary{{display:grid;grid-template-columns:180px 1fr auto;gap:12px;align-items:center;padding:12px 16px;cursor:pointer;list-style:none}}.module summary::-webkit-details-marker{{display:none}}.module summary:before{{content:'−';color:var(--yellow);margin-right:8px}}.module:not([open]) summary:before{{content:'+'}}.module summary .rank{{color:var(--purple);font:600 12px Bahnschrift,sans-serif;letter-spacing:.08em;text-transform:uppercase}}.module summary small{{color:var(--faint)}}.table-wrap{{overflow-x:auto}}table{{border-collapse:collapse;width:100%;min-width:1000px}}th{{text-align:left;color:var(--faint);font:600 10px Bahnschrift,sans-serif;letter-spacing:.14em;padding:9px 12px;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}}td{{vertical-align:top;padding:12px;border-bottom:1px solid rgba(184,214,246,.1);color:var(--soft)}}td:first-child{{width:125px}}td:nth-child(2){{width:46%}}td:nth-child(3){{width:90px}}td:last-child{{width:105px}}td strong{{color:var(--ink);font-size:13px}}td p{{margin:5px 0 0;font-size:12px;line-height:1.55}}code{{color:var(--yellow);font:12px Consolas,monospace}}.side,.status{{display:inline-block;border:1px solid currentColor;padding:2px 6px;font:600 10px Bahnschrift,sans-serif;letter-spacing:.05em;white-space:nowrap}}.side.red{{color:var(--red)}}.side.blue{{color:var(--blue)}}.side.base{{color:var(--purple)}}.status.s-Planlandı{{color:var(--faint)}}.status.s-Yazıldı{{color:var(--yellow)}}.status.s-Denetlendi{{color:var(--green)}}.hidden{{display:none!important}}.footer{{border-top:1px solid var(--line);padding-top:16px;color:var(--faint);font-size:12px}}@media(max-width:800px){{.page{{padding:18px 12px 50px}}.summary{{grid-template-columns:1fr 1fr}}.stat:nth-child(2){{border-right:0}}.track-head{{grid-template-columns:1fr auto}}.track-head span,.track-head p{{display:none}}.module summary{{grid-template-columns:1fr auto}}.module summary .rank{{grid-column:1/-1}}.table-wrap{{overflow:visible}}table{{display:block;min-width:0}}thead{{display:none}}tbody{{display:grid;gap:12px;padding:12px}}tbody tr{{display:block;border:1px solid var(--line);background:var(--panel);padding:8px 12px}}td{{display:block;width:100%!important;padding:10px 0;border-bottom:1px solid var(--line)}}td:last-child{{border-bottom:0}}td::before{{content:attr(data-label);display:block;margin-bottom:5px;color:var(--faint);font:600 10px Bahnschrift,sans-serif;letter-spacing:.1em;text-transform:uppercase}}}}
</style></head><body><main class="page">
<div class="eyebrow">Pafta · AI güvenlik · plan ve ilerleme</div><h1>AI Müfredat <em>Paneli</em></h1>
<p class="lead">Sığ prompt tarifleri değil; model mekaniği, saldırı zincirleri ve ölçülebilir savunma. Bu aşamada yalnız ders başlıkları planlandı; ders içerikleri onay sonrası yazılacak.</p>
<p class="eyebrow meta">Son üretim: {generated} · Kaynak: {SOURCE.name} · <span id="refresh-state">20 saniyede bir yenilenir</span></p>
<section class="summary"><div class="stat"><b>{total}</b><span>{track_total} track · {module_total} modül · toplam ders</span></div><div class="stat Planlandı"><b>{counts['Planlandı']}</b><span>Planlandı</span></div><div class="stat Yazıldı"><b>{counts['Yazıldı']}</b><span>Yazıldı</span></div><div class="stat Denetlendi"><b>{counts['Denetlendi']}</b><span>Denetlendi</span></div></section>
<div class="progress" title="Yazıldı: %{counts['Yazıldı']/total*100:.2f} · Denetlendi: %{counts['Denetlendi']/total*100:.2f}"><i class="written" style="width:{counts['Yazıldı']/total*100:.2f}%" title="Yazıldı: {counts['Yazıldı']} ders (%{counts['Yazıldı']/total*100:.2f})"></i><i class="audited" style="width:{counts['Denetlendi']/total*100:.2f}%" title="Denetlendi: {counts['Denetlendi']} ders (%{counts['Denetlendi']/total*100:.2f})"></i></div>
<div class="controls"><input id="q" type="search" placeholder="Ders, kazanım veya araç ara…" aria-label="Ders ara"><input id="tools" type="search" placeholder="Araç filtrele…" aria-label="Araç filtrele"><select id="track"><option value="">Tüm track'ler</option>{track_options}</select><select id="rank"><option value="">Tüm rütbeler</option>{rank_options}</select><select id="side"><option value="">Tüm taraflar</option><option>Temel</option><option>Saldırı</option><option>Savunma</option><option>Güvence</option><option>Araştırma</option></select><select id="status"><option value="">Tüm durumlar</option><option>Planlandı</option><option>Yazıldı</option><option>Denetlendi</option></select><button id="reset" type="button">Sıfırla</button><button id="toggle" type="button">Modülleri kapat</button><button id="auto-refresh" type="button">Otomatik yenilemeyi durdur</button></div>
<div class="result" id="result"></div>{''.join(sections)}
<div class="footer">Durum akışı: <b>Planlandı → Yazıldı → Denetlendi</b>. “Denetlendi” yalnız bağımsız denetçi validate, tahmin, mutasyon ve derinlik kontrollerini tamamladığında kullanılır.<br>{esc(data.get('field_goals', ''))}</div>
</main><script>
const rows=[...document.querySelectorAll('tbody tr')], modules=[...document.querySelectorAll('.module')], tracks=[...document.querySelectorAll('[data-track-section]')];
const q=document.querySelector('#q'), tools=document.querySelector('#tools'), track=document.querySelector('#track'), rank=document.querySelector('#rank'), side=document.querySelector('#side'), status=document.querySelector('#status');
const FILTER_KEY='pafta-ai-plan-filter', VIEW_KEY='pafta-ai-plan-view', AUTO_KEY='pafta-ai-auto-refresh';
const filterControls={{q,tools,track,rank,side,status}};
let refreshTimer=null, autoRefresh=true;
if('scrollRestoration' in history)history.scrollRestoration='manual';
function store(key,value){{try{{sessionStorage.setItem(key,value)}}catch(e){{}}}}
function read(key){{try{{return sessionStorage.getItem(key)}}catch(e){{return null}}}}
function saveFilters(){{store(FILTER_KEY,JSON.stringify(Object.fromEntries(Object.entries(filterControls).map(([key,el])=>[key,el.value]))))}}
function saveView(){{const states={{}};modules.forEach(m=>states[m.dataset.moduleKey]=m.open);store(VIEW_KEY,JSON.stringify({{scrollY:window.scrollY,modules:states}}))}}
function syncToggle(){{document.querySelector('#toggle').textContent=modules.some(m=>m.open)?'Modülleri kapat':'Modülleri aç'}}
function apply(){{const needle=q.value.trim().toLocaleLowerCase('tr-TR'), toolNeedle=tools.value.trim().toLocaleLowerCase('tr-TR');let visible=0;rows.forEach(r=>{{const show=(!needle||r.dataset.search.includes(needle))&&(!toolNeedle||r.dataset.tools.toLocaleLowerCase('tr-TR').includes(toolNeedle))&&(!track.value||r.dataset.track===track.value)&&(!rank.value||r.dataset.rank===rank.value)&&(!side.value||r.dataset.side===side.value)&&(!status.value||r.dataset.status===status.value);r.classList.toggle('hidden',!show);if(show)visible++;}});modules.forEach(m=>{{const count=[...m.querySelectorAll('tbody tr:not(.hidden)')].length;m.classList.toggle('hidden',count===0);m.querySelector('summary small').textContent=count+' ders';}});tracks.forEach(t=>t.classList.toggle('hidden',![...t.querySelectorAll('.module:not(.hidden)')].length));document.querySelector('#result').textContent=visible+' / {total} ders gösteriliyor';saveFilters()}}
function updateAuto(){{document.querySelector('#auto-refresh').textContent=autoRefresh?'Otomatik yenilemeyi durdur':'Otomatik yenilemeyi başlat';document.querySelector('#refresh-state').textContent=autoRefresh?'20 saniyede bir yenilenir':'Otomatik yenileme durduruldu'}}
function scheduleRefresh(){{clearTimeout(refreshTimer);if(autoRefresh)refreshTimer=setTimeout(()=>{{saveFilters();saveView();location.reload()}},20000)}}
Object.values(filterControls).forEach(el=>el.addEventListener(el===q||el===tools?'input':'change',apply));
document.querySelector('#reset').addEventListener('click',()=>{{Object.values(filterControls).forEach(el=>el.value='');apply()}});
document.querySelector('#toggle').addEventListener('click',()=>{{const close=modules.some(m=>m.open);modules.forEach(m=>m.open=!close);saveView();syncToggle()}});
document.querySelector('#auto-refresh').addEventListener('click',()=>{{autoRefresh=!autoRefresh;store(AUTO_KEY,autoRefresh?'1':'0');updateAuto();scheduleRefresh()}});
modules.forEach(m=>m.addEventListener('toggle',()=>{{saveView();syncToggle()}}));
window.addEventListener('pagehide',()=>{{saveFilters();saveView()}});
try{{const filters=JSON.parse(read(FILTER_KEY)||'{{}}');for(const [key,el] of Object.entries(filterControls))if(typeof filters[key]==='string')el.value=filters[key]}}catch(e){{}}
autoRefresh=read(AUTO_KEY)!=='0';
let savedView=null;try{{savedView=JSON.parse(read(VIEW_KEY)||'null');if(savedView&&savedView.modules)modules.forEach(m=>{{const key=m.dataset.moduleKey;if(Object.prototype.hasOwnProperty.call(savedView.modules,key))m.open=Boolean(savedView.modules[key])}})}}catch(e){{}}
apply();syncToggle();updateAuto();scheduleRefresh();
if(savedView&&Number.isFinite(Number(savedView.scrollY)))requestAnimationFrame(()=>window.scrollTo(0,Number(savedView.scrollY)));
</script></body></html>"""


def main() -> None:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    validate(data)
    MD_OUT.write_text(markdown(data), encoding="utf-8", newline="\n")
    HTML_OUT.write_text(page(data), encoding="utf-8", newline="\n")
    total = sum(1 for _ in lessons(data))
    print(f"OK · {len(data['tracks'])} track · {total} ders · {HTML_OUT.name} · {MD_OUT.name}")


if __name__ == "__main__":
    main()
