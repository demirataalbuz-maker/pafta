import sys
sys.path.insert(0, r"C:\Users\demo12\Documents\Pafta-AI-GercekLab")
sys.path.insert(0, r"C:\Users\demo12\Documents\Pafta-AI-GercekLab\tools")
import test_ai_gercek as T
from engine.lessons import Library

lib = Library()
tid, lid = "ai-temel", "ai-temel-16"
idx, st = T.adim(lib, tid, lid)
sol = st["solution"]
HATALI = [
    ("maskeleme yok", 'secili = {a: DESEN.sub("[GIZLI]", kayit[a]) for a in alanlar}', "secili = {a: kayit[a] for a in alanlar}"),
    ("token seçilebiliyor", 'if any(a not in ("id", "soru", "not") for a in alanlar):', 'if any(a not in ("id", "soru", "not", "token") for a in alanlar):'),
    ("beşinci karakter maskeleniyor", 'DESEN = re.compile(r"TOKEN-[A-Z0-9]{4}(?![A-Z0-9])")', 'DESEN = re.compile(r"TOKEN-[A-Z0-9]{4}")'),
    ("tam kayıt", "return json.dumps(secili, ensure_ascii=False)", "return json.dumps(kayit, ensure_ascii=False)"),
]
kodlar = [("referans", sol), ("başlangıç", st["starter"]), ("boş", ""),
          ("sabit", 'def baglam_hazirla(kayit, alanlar):\n    return \'{"id": "m1"}\'\n')]
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
