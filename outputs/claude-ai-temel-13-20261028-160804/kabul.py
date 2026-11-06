import sys
sys.path.insert(0, r"C:\Users\demo12\Documents\Pafta-AI-GercekLab")
sys.path.insert(0, r"C:\Users\demo12\Documents\Pafta-AI-GercekLab\tools")
import test_ai_gercek as T
from engine.lessons import Library

lib = Library()
tid, lid = "ai-temel", "ai-temel-13"
idx, st = T.adim(lib, tid, lid)
sol = st["solution"]
HATALI = [
    ("kaçış yok", 'kacisli = belge.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")', "kacisli = belge"),
    ("kaçış sırası yanlış (& en son)", 'kacisli = belge.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")',
     'kacisli = belge.replace("<", "&lt;").replace(">", "&gt;").replace("&", "&amp;")'),
    ("hatalar paydada", "gecerli = [k for k in grup if k[\"hata\"] is None]", "gecerli = grup"),
    ("kontrol ASR'de", "saldiri = [k for k in gecerli if k[\"tur\"] == \"saldiri\"]", "saldiri = gecerli"),
]
kodlar = [("referans", sol), ("başlangıç", st["starter"]), ("boş", ""),
          ("sabit", "def mesajlari_kur(talimat, belge, yontem):\n    return [{'role': 'user', 'content': belge}]\n"
                    "def deney_ozeti(kayitlar):\n    return {'birlesik': {'asr': 0.0, 'kontrol_sizinti': 0, 'fayda': 1.0, 'hata': 0}, "
                    "'ayrik': {'asr': 0.0, 'kontrol_sizinti': 0, 'fayda': 1.0, 'hata': 0}}\n")]
for ad, eski, yeni in HATALI:
    assert eski in sol, ad
    kodlar.append((ad, sol.replace(eski, yeni, 1)))
rapor = []
for ad, kod in kodlar:
    res, sure = T.kos(lib, tid, st, kod)
    kanit = [k for k in (res.get("ai_kanit") or []) if k.get("kaynak") == "gercek" and k.get("kabul")]
    gecti = res.get("status") == "pass" and bool(kanit)
    beklenen = ad == "referans"
    rapor.append({"ad": ad, "gecti": gecti, "dogru": gecti == beklenen,
                  "gercek": [c["msg"] for c in res.get("checks", []) if c["msg"].startswith(("GERÇEK", "BULGU"))]})
    print(f"{ad:30} {'PASS' if gecti else 'RED '} {'✓' if gecti == beklenen else '✗ YANLIŞ'} {sure}s {T.kisa(res)[:110]}")
print(rapor[0]["gercek"])
print("HEPSİ DOĞRU" if all(r["dogru"] for r in rapor) else "SORUN VAR")
