import sys
sys.path.insert(0, r"C:\Users\demo12\Documents\Pafta-AI-GercekLab")
sys.path.insert(0, r"C:\Users\demo12\Documents\Pafta-AI-GercekLab\tools")
import test_ai_gercek as T
from engine.lessons import Library

lib = Library()
tid, lid = "ai-temel", "ai-temel-21"
idx, st = T.adim(lib, tid, lid)
sol = st["solution"]
HATALI = [
    ("normalize yok", "        return [x / boy for x in v]", "        return list(v)"),
    ("kopya bastırma yok", "        if sade in gorulen:\n            continue\n", ""),
    ("HTML kaçışı yok", "'<kaynak id=\"' + html.escape(parcalar[i][\"id\"]) + '\">' + html.escape(sade)",
     "'<kaynak id=\"' + parcalar[i][\"id\"] + '\">' + sade"),
    ("eşitlikte büyük indeks", "key=lambda i: (-skor[i], i)", "key=lambda i: (-skor[i], -i)"),
]
kodlar = [("referans", sol), ("başlangıç", st["starter"]), ("boş", ""),
          ("sabit", "def rag_baglami(parcalar, parca_vekleri, sorgu_vek, k, butce):\n"
                    "    return {'D': [1.0], 'I': [0], 'baglam': '<kaynak id=\"iade#0\">iade</kaynak>', 'kaynaklar': ['iade#0'], 'token': 1}\n")]
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
