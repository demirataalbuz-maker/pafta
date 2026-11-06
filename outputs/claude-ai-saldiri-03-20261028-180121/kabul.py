import sys
sys.path.insert(0, r"C:\Users\demo12\Documents\Pafta-AI-GercekLab")
sys.path.insert(0, r"C:\Users\demo12\Documents\Pafta-AI-GercekLab\tools")
import test_ai_gercek as T
from engine.lessons import Library

lib = Library()
tid, lid = "ai-saldiri", "ai-saldiri-03"
idx, st = T.adim(lib, tid, lid)
sol = st["solution"]
HATALI = [
    ("tool otorite", 'otorite = {"system": 3, "developer": 2, "user": 1}', 'otorite = {"system": 3, "developer": 2, "user": 1, "tool": 0}'),
    ("yasak önceliği yok", "secilen = yasaklar[-1] if yasaklar else rol_kurallari[-1]", "secilen = rol_kurallari[-1]"),
    ("hatalar paydada", 'gecerli = [k for k in grup if k["hata"] is None]', "gecerli = grup"),
    ("format dışı paydadan atılıyor", 'gecerli = [k for k in grup if k["hata"] is None]',
     'gecerli = [k for k in grup if k["hata"] is None and k["gozlenen"] != "format_disi"]'),
]
kodlar = [("referans", sol), ("başlangıç", st["starter"]), ("boş", ""),
          ("sabit", "def karar_ver(kurallar, eylem, kapsam):\n    return {'karar': 'yasak', 'rol': 'system', 'kural': 'S1'}\n"
                    "def uyum_ozeti(kayitlar):\n    return {'qwen3:4b-instruct-2507-q4_K_M': {'kontrol_uyum': 1.0, 'catisma_uyum': 1.0, 'turler': {}, 'format_disi': 0, 'hata': 0, 'kontrol_tam': True}}\n")]
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
