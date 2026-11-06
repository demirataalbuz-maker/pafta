import json
import sys
sys.path.insert(0, r"C:\Users\demo12\Documents\Pafta-AI-GercekLab")
sys.path.insert(0, r"C:\Users\demo12\Documents\Pafta-AI-GercekLab\tools")
import test_ai_gercek as T
from engine.lessons import Library

lib = Library()
tid, lid = "ai-temel", "ai-temel-04"
idx, st = T.adim(lib, tid, lid)
sol = st["solution"]
HATALI = [
    ("top-p tam dağılımda", "kalan = olas[sira] / olas[sira].sum()", "kalan = olas[sira]"),
    ("eşikteki aday dışarıda", "        adaylar.append(i)\n        toplam += q\n        if toplam >= p:\n            break",
     "        if adaylar and toplam + q > p:\n            break\n        adaylar.append(i)\n        toplam += q"),
    ("sıcaklık yok", "logitler.double() / sicaklik", "logitler.double()"),
    ("son normalize yok", "(secili / secili.sum()).tolist()", "secili.tolist()"),
]
kodlar = [("referans", sol), ("başlangıç", st["starter"]), ("boş", ""),
          ("sabit", "def ornekleme_dagilimi(logitler, sicaklik=1.0, k=None, p=1.0):\n    return {'adaylar': [12, 7], 'olasiliklar': [0.6, 0.4]}\n")]
for ad, eski, yeni in HATALI:
    assert eski in sol, ad
    kodlar.append((ad, sol.replace(eski, yeni, 1)))
rapor = []
for ad, kod in kodlar:
    res, sure = T.kos(lib, tid, st, kod)
    kanit = [k for k in (res.get("ai_kanit") or []) if k.get("kaynak") == "gercek" and k.get("kabul")]
    gecti = res.get("status") == "pass" and bool(kanit)
    beklenen = ad == "referans"
    rapor.append({"ad": ad, "gecti": gecti, "dogru": gecti == beklenen, "sure": sure, "neden": T.kisa(res),
                  "gercek": [c["msg"] for c in res.get("checks", []) if c["msg"].startswith("GERÇEK")],
                  "kanit": kanit[0]["dosya"] if kanit else None})
    print(f"{ad:24} {'PASS' if gecti else 'RED '} {'✓' if gecti == beklenen else '✗ YANLIŞ'} {sure}s {T.kisa(res)[:120]}")
print(json.dumps(rapor[0], ensure_ascii=False, indent=1))
print("HEPSİ DOĞRU" if all(r["dogru"] for r in rapor) else "SORUN VAR")
