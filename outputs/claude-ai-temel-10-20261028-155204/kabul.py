import sys
sys.path.insert(0, r"C:\Users\demo12\Documents\Pafta-AI-GercekLab")
sys.path.insert(0, r"C:\Users\demo12\Documents\Pafta-AI-GercekLab\tools")
import test_ai_gercek as T
from engine.lessons import Library

lib = Library()
tid, lid = "ai-temel", "ai-temel-10"
idx, st = T.adim(lib, tid, lid)
sol = st["solution"]
HATALI = [
    ("ölçek alfa", "self.olcek = alfa / rank", "self.olcek = alfa"),
    ("B rastgele", "torch.zeros(temel.out_features, rank)", "torch.randn(temel.out_features, rank) * 0.01"),
    ("temel dondurulmuyor", "            p.requires_grad_(False)\n", "            pass\n"),
    ("yerinde birleştirme", "        return self.temel.weight.detach() + self.olcek * (self.B @ self.A).detach()",
     "        with torch.no_grad():\n            self.temel.weight += self.olcek * (self.B @ self.A)\n        return self.temel.weight.detach()"),
]
kodlar = [("referans", sol), ("başlangıç", st["starter"]), ("boş", ""),
          ("sabit", "import torch\nclass LoraDogrusal(torch.nn.Module):\n    def __init__(self, temel, rank, alfa):\n        super().__init__()\n        self.temel = temel\n        self.olcek = 2.0\n    def forward(self, x):\n        return self.temel(x)\n    def birlestir(self):\n        return self.temel.weight\n")]
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
                  "gercek": [c["msg"] for c in res.get("checks", []) if c["msg"].startswith("GERÇEK")]})
    print(f"{ad:24} {'PASS' if gecti else 'RED '} {'✓' if gecti == beklenen else '✗ YANLIŞ'} {sure}s {T.kisa(res)[:120]}")
print(rapor[0]["gercek"])
print("HEPSİ DOĞRU" if all(r["dogru"] for r in rapor) else "SORUN VAR")
