# -*- coding: utf-8 -*-
"""Ders doğrulayıcı (bütün aktif yollar).

Her görev için: örnek çözüm testleri GEÇMELİ, başlangıç kodu GEÇMEMELİ.
Her tahmin için: kod çalışmalı ve ??? sonrası bir açıklama olmalı.
Anlatımdaki çalıştırılabilir örnekler hatasız çalışmalı (norun işaretliler hariç).

    python tools/validate.py                 # bütün aktif yollar
    python tools/validate.py --yol regex     # tek yol
    python tools/validate.py rx03 rx04       # belirli dersler (her yolda aranır)
"""
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from engine.lessons import Library  # noqa: E402
from engine.runners import get  # noqa: E402

FENCE = {"python": "python|py", "bash": "bash|sh", "powershell": "powershell|ps1?", "regex": "regex", "sql": "sql", "kql": "kql|kusto", "spl": "spl|splunk", "javascript": "javascript|js", "sigma": "sigma", "yara": "yara"}


def kod_deseni(dil):
    return re.compile(r"```(" + FENCE.get(dil, dil) + r")\b([^\n]*)\n(.*?)```", re.S)


def strip_anno(src):
    out = []
    for line in src.split("\n"):
        m = re.search(r"(^|\s)#!(?!/)\s?(.*)$", line)
        if m:
            code = line[:m.start()].rstrip()
            if not code.strip():
                continue
            line = code
        out.append(line)
    return "\n".join(out)


def regex_parcala(src):
    satirlar = src.split("\n")
    for i, s in enumerate(satirlar):
        if s.strip() == "---":
            return "\n".join(satirlar[:i]), "\n".join(satirlar[i + 1:])
    return src, ""


def jobs_for(lib, tid, dil, lid):
    les = lib.lesson(tid, lid)
    if les is None:
        return [("EKSİK", tid, f"{tid}/{lid}", None, None)]
    jobs = []
    if not les["steps"]:
        jobs.append(("BOŞ", tid, lid, None, None))
    for i, st in enumerate(les["steps"]):
        where = f"{tid}/{lid}:{i} {st['kind']} «{st['title'][:40]}»"
        if st["kind"] == "gorev":
            if not st.get("test"):
                jobs.append(("TESTSİZ", tid, where, None, None))
                continue
            if dil in ("sigma", "yara") and not st.get("stdin", "").strip():
                jobs.append(("GİRDİSİZ", tid, where, None, None))
            if not st.get("solution"):
                jobs.append(("ÇÖZÜMSÜZ", tid, where, None, None))
            else:
                jobs.append(("solution", tid, where, st, st["solution"]))
            jobs.append(("starter", tid, where, st, st.get("starter", "")))
        elif st["kind"] == "tahmin":
            if "???" not in st["body"]:
                jobs.append(("AÇIKLAMASIZ", tid, where, None, None))
            jobs.append(("tahmin", tid, where, st, st["code"]))
        else:
            for m in kod_deseni(dil).finditer(st["body"]):
                if "norun" in m.group(2):
                    continue
                kod = m.group(3)
                if dil == "regex":
                    desen, metin = regex_parcala(kod)
                    jobs.append(("ornek", tid, where, dict(st, stdin=metin), desen))
                else:
                    ornek_stdin = st.get("stdin", "")
                    if not ornek_stdin and dil in ("sigma", "yara"):
                        ornek_stdin = next((s.get("stdin", "") for s in les["steps"] if s.get("stdin")), "")
                    jobs.append(("ornek", tid, where, dict(st, stdin=ornek_stdin), strip_anno(kod)))
    return jobs


RUNNER_ADI = {}


def run_job(job):
    kind, tid, where, st, code = job
    runner = get(RUNNER_ADI[tid])
    if st is None:
        return (False, kind, where, "")
    if kind == "solution":
        r = runner.test(code, st)
        if r.get("status") != "pass":
            fails = [c for c in r.get("checks", []) if not c["ok"]]
            return (False, "ÇÖZÜM GEÇMEDİ", where, f"{r.get('status')} {fails[:2]} {r.get('error')}")
        return (True, kind, where, "")
    if kind == "starter":
        r = runner.test(code, st)
        if r.get("status") == "pass":
            return (False, "BAŞLANGIÇ GEÇİYOR", where, "")
        if r.get("status") == "internal":
            return (False, "İÇ HATA", where, r.get("detail", "")[-400:])
        return (True, kind, where, "")
    if kind == "tahmin" and st.get("gercek") is not None:
        return (True, kind, where, "")          # çalıştırılamayan dil: gerçek çıktıyı ders yazarı verdi
    if kind in ("tahmin", "ornek"):
        r = runner.run(code, st.get("stdin", ""), st.get("setup"))
        if r.get("status") not in ("ok", "error"):
            return (False, f"{kind.upper()} {r.get('status')}", where, str(r.get("error"))[:300])
        if r.get("status") == "error" and kind == "ornek":
            return (False, "ÖRNEK HATA VERİYOR", where, f"{r['error']['type']}: {r['error']['msg']} | {code[:80]!r}")
        if kind == "ornek" and tid in ("sigma", "yara") and not r.get("segs"):
            return (False, "ÖRNEK EŞLEŞMİYOR", where, f"Örnek kural örnek girdiyle eşleşmedi: {code[:80]!r}")
        if r.get("status") == "error" and kind == "tahmin" and "hata" not in st["body"].lower():
            return (False, "TAHMİN HATA VERİYOR (bilerek mi?)", where, f"{r['error']['type']}: {r['error']['msg']}")
        return (True, kind, where, "")
    return (False, kind, where, "")


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    args = sys.argv[1:]
    sadece_yol = None
    if "--yol" in args:
        i = args.index("--yol")
        sadece_yol = args[i + 1]
        args = args[:i] + args[i + 2:]
    wanted = set(args)
    lib = Library()
    jobs, toplam_ders, eksikler = [], 0, []
    for track in lib.tracks():
        tid = track["id"]
        if track.get("status") != "active" or (sadece_yol and tid != sadece_yol):
            continue
        RUNNER_ADI[tid] = track.get("runner", tid)
        dil = track.get("dil", tid)
        outline = lib.outline(tid)
        order = [l for l in outline["order"] if not wanted or l in wanted]
        toplam_ders += len(order)
        eksikler += [f"{tid}/{l['id']}" for m in outline["modules"] for l in m["lessons"] if l.get("missing")]
        for lid in order:
            jobs.extend(jobs_for(lib, tid, dil, lid))
    with ThreadPoolExecutor(max_workers=8) as ex:
        results = list(ex.map(run_job, jobs))
    bad = [r for r in results if not r[0]]
    counts = {}
    for _, kind, _, _ in [r for r in results if r[0]]:
        counts[kind] = counts.get(kind, 0) + 1
    print(f"{toplam_ders} ders, {len(jobs)} kontrol · geçen: {counts}")
    if eksikler and not wanted:
        print(f"Yazılmamış dersler ({len(eksikler)}): {' '.join(eksikler)}")
    for _, kind, where, detail in bad:
        print(f"  ✗ {kind:<22} {where}  {detail}")
    print("TEMİZ" if not bad else f"{len(bad)} SORUN")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
