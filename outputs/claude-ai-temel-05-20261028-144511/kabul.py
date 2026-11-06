import json
import sys
sys.path.insert(0, r"C:\Users\demo12\Documents\Pafta-AI-GercekLab")
sys.path.insert(0, r"C:\Users\demo12\Documents\Pafta-AI-GercekLab\tools")
import test_ai_gercek as T
from engine.lessons import Library

lib = Library()
tid, lid = "ai-temel", "ai-temel-05"
idx, st = T.adim(lib, tid, lid)
sol = st["solution"]
MASKE = '    skor = skor.masked_fill(gelecek, float("-inf"))\n'
HATALI = [
    ("ölçek yok", "skor = q @ k.T / d ** 0.5", "skor = q @ k.T"),
    ("maske yok", MASKE, ""),
    ("softmax sütunda", "torch.softmax(skor, dim=-1)", "torch.softmax(skor, dim=0)"),
    ("maske softmax sonrası", MASKE + "    agirliklar = torch.softmax(skor, dim=-1)",
     "    agirliklar = torch.softmax(skor, dim=-1).masked_fill(gelecek, 0.0)"),
]
kodlar = [("referans", sol), ("başlangıç", st["starter"]), ("boş", ""),
          ("sabit", "import torch\ndef nedensel_dikkat(q, k, v):\n    return {'agirliklar': torch.eye(q.shape[0]), 'baglam': v.double()}\n")]
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
