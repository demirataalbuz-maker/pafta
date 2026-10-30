"""Denetim: verilen derslerin tahmin adımlarını kendi koşucularında çalıştırır; çıktının boş olmayan
her satırı açıklamada (??? sonrası) ya da soru metninde geçiyor mu? `gercek` bloklu adımlarda blok kullanılır.
    python denetim_tahmin.py <anlık görüntü kökü> ders...
"""
import sys
ROOT = sys.argv[1]
sys.path.insert(0, ROOT)
from engine.lessons import Library  # noqa: E402
from engine import runners  # noqa: E402
from engine.sinav import tahmin_calistir  # noqa: E402


def normal(s):
    return " ".join(s.replace("`", "").split())


lib = Library()
idler = {}
for tid in lib.track_ids():
    t = lib.track(tid)
    for m in t["modules"]:
        for lid in m["lessons"]:
            idler[lid] = (tid, t.get("runner"))
toplam = supheli = 0
for lid in sys.argv[2:]:
    tid, rad = idler[lid]
    les = lib.lesson(tid, lid)
    for i, st in enumerate(les["steps"]):
        if st["kind"] != "tahmin":
            continue
        toplam += 1
        res, cikti = tahmin_calistir(runners.get(rad), st)
        govde = st.get("body", "")
        aciklama = normal(govde)
        eksik = [s for s in cikti.splitlines() if s.strip() and normal(s) not in aciklama]
        if res.get("error") and not st.get("gercek"):
            eksik.append("HATA: " + str(res["error"].get("type")) + " " + str(res["error"].get("msg"))[:120])
        durum = "uyuşuyor" if not eksik else "ŞÜPHELİ"
        if eksik:
            supheli += 1
        print(f"{lid}:{i} [{tid}/{rad}] {durum} · {len(cikti.splitlines())} satır" + ("" if not eksik else f" · eksik: {eksik[:4]}"))
print(f"{toplam} tahmin, {supheli} şüpheli")
