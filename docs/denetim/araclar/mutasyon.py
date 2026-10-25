"""Denetim: görevlerin örnek çözümlerini küçük hatalarla bozar; testler bozuk sürümü yakalıyor mu?
    python denetim_mutasyon.py <anlık görüntü kökü> [--en-cok N] ders...
Çıktı: her görev için üretilen/yakalanan mutant sayısı ve GEÇEN (zayıf test adayı) mutantların listesi.
"""
import re
import sys
from concurrent.futures import ThreadPoolExecutor

ROOT = sys.argv[1]
sys.path.insert(0, ROOT)
from engine.lessons import Library  # noqa: E402
from engine import runners  # noqa: E402

args = sys.argv[2:]
EN_COK = 24
if args and args[0] == "--en-cok":
    EN_COK, args = int(args[1]), args[2:]

KURALLAR = [
    (r"-gt\b", "-ge"), (r"-ge\b", "-gt"), (r"-lt\b", "-le"), (r"-le\b", "-lt"),
    (r"-eq\b", "-ne"), (r"-ne\b", "-eq"), (r"-ceq\b", "-eq"), (r"-cmatch\b", "-match"), (r"-clike\b", "-like"),
    (r"(?<![<>=!-])>=", ">"), (r"(?<![<>=!-])<=", "<"), (r"(?<=[\w)\]] )>(?=[ \w(])", ">="), (r"(?<=[\w)\]] )<(?=[ \w(])", "<="),
    (r"==", "!="), (r"!=", "=="),
    (r"\band\b", "or"), (r"\bor\b", "and"), (r"-and\b", "-or"), (r"-or\b", "-and"), (r"&&", "||"),
    (r"\basc\b", "desc"), (r"\bdesc\b", "asc"), (r"-Descending\b", ""), (r"-Oldest\b", ""), (r"\bsort -r\b", "sort"),
    (r"(?<![\w.\-])([1-9]\d{0,3})(?![\w.])", None),   # sayı + 1
]


def mutantlar(kod):
    out = []
    for desen, yeni in KURALLAR:
        for m in re.finditer(desen, kod):
            y = str(int(m.group(1)) + 1) if yeni is None else yeni
            mut = kod[:m.start()] + y + kod[m.end():]
            if mut != kod:
                out.append((f"{m.group(0)!r}→{y!r} @{kod.count(chr(10), 0, m.start()) + 1}", mut))
    return out


lib = Library()
idler = {}
for tid in lib.track_ids():
    t = lib.track(tid)
    for mod in t["modules"]:
        for lid in mod["lessons"]:
            idler[lid] = (tid, t.get("runner"))

genel_uretilen = genel_gecen = 0
for lid in args:
    tid, rad = idler[lid]
    les = lib.lesson(tid, lid)
    for i, st in enumerate(les["steps"]):
        if st["kind"] != "gorev" or not st.get("solution"):
            continue
        kosucu = runners.for_step(runners.get(rad), st)
        temel = kosucu.test(st["solution"], st)
        if temel.get("status") != "pass":
            print(f"{lid}:{i} çözüm kendisi geçmiyor: {temel.get('status')}")
            continue
        muts = mutantlar(st["solution"])
        if len(muts) > EN_COK:   # eşit aralıklı örneklem
            adim = len(muts) / EN_COK
            muts = [muts[int(k * adim)] for k in range(EN_COK)]

        def dene(m):
            ad, kod = m
            try:
                r = kosucu.test(kod, st)
                return ad, r.get("status")
            except Exception as e:
                return ad, "istisna:" + type(e).__name__

        with ThreadPoolExecutor(4) as ex:
            sonuc = list(ex.map(dene, muts))
        gecen = [ad for ad, durum in sonuc if durum == "pass"]
        genel_uretilen += len(sonuc)
        genel_gecen += len(gecen)
        print(f"{lid}:{i} «{st['title']}» {len(sonuc)} mutant, {len(sonuc) - len(gecen)} yakalandı"
              + (f" · GEÇEN: {gecen}" if gecen else ""))
print(f"toplam {genel_uretilen} mutant, {genel_gecen} geçen")
