import json
import sys
sys.path.insert(0, r"C:\Users\demo12\Documents\Pafta-AI-GercekLab")
sys.path.insert(0, r"C:\Users\demo12\Documents\Pafta-AI-GercekLab\tools")
import test_ai_gercek as T
from engine.lessons import Library

lib = Library()
tid, lid = "ai-temel", "ai-temel-06"
idx, st = T.adim(lib, tid, lid)
sol = st["solution"]
HATALI = [
    ("atlamalı bölme", "dilim = slice(h * d, (h + 1) * d)", "dilim = slice(h, D, kafa_sayisi)"),
    ("maske yok", '.masked_fill(gelecek, float("-inf"))', ""),
    ("√D ölçek", "qh @ kh.T / d ** 0.5", "qh @ kh.T / D ** 0.5"),
    ("ters birleştirme", "torch.cat(baglamlar, dim=1)", "torch.cat(baglamlar[::-1], dim=1)"),
]
kodlar = [("referans", sol), ("başlangıç", st["starter"]), ("boş", ""),
          ("sabit", "import torch\ndef cok_basli_dikkat(q, k, v, kafa_sayisi):\n    T = q.shape[0]\n    return {'agirliklar': torch.ones(kafa_sayisi, T, T) / T, 'baglam': v.double()}\n")]
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
print(rapor[0]["gercek"])
print("HEPSİ DOĞRU" if all(r["dogru"] for r in rapor) else "SORUN VAR")
