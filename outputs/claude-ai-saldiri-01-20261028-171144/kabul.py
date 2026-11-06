import sys
sys.path.insert(0, r"C:\Users\demo12\Documents\Pafta-AI-GercekLab")
sys.path.insert(0, r"C:\Users\demo12\Documents\Pafta-AI-GercekLab\tools")
import test_ai_gercek as T
from engine.lessons import Library

lib = Library()
tid, lid = "ai-saldiri", "ai-saldiri-01"
idx, st = T.adim(lib, tid, lid)
sol = st["solution"]
HATALI = [
    ("kısa ad anahtar", 'envanter[sid + "/" + ad] = {', "envanter[ad] = {"),
    ("metadata güveni", '"schema": schema, "guven": "guvenilmez"}',
     '"schema": schema, "guven": "guvenilir" if "güvenilir" in tool.get("description", "") else "guvenilmez"}'),
    ("onay kısa adla", "    if ref not in onay:", "    if ref.split(\"/\")[-1] not in {o.split(\"/\")[-1] for o in onay}:"),
    ("bool integer sayılıyor", '"integer": lambda v: isinstance(v, int) and not isinstance(v, bool),', '"integer": lambda v: isinstance(v, int),'),
]
kodlar = [("referans", sol), ("başlangıç", st["starter"]), ("boş", ""),
          ("sabit", "def arac_envanteri(sunucular):\n    return {}\ndef cagri_denetle(cagri, envanter, onay):\n    return False, 'kullanici-onayi-yok'\n")]
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
