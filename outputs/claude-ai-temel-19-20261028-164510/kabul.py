import sys
sys.path.insert(0, r"C:\Users\demo12\Documents\Pafta-AI-GercekLab")
sys.path.insert(0, r"C:\Users\demo12\Documents\Pafta-AI-GercekLab\tools")
import test_ai_gercek as T
from engine.lessons import Library

lib = Library()
tid, lid = "ai-temel", "ai-temel-19"
idx, st = T.adim(lib, tid, lid)
sol = st["solution"]
HATALI = [
    ("git blob \\0 yok", 's1 = hashlib.sha1(b"blob " + str(boyut).encode() + b"\\0")', 's1 = hashlib.sha1(b"blob " + str(boyut).encode())'),
    ("big-endian", 'n = struct.unpack("<Q", bas)[0]', 'n = struct.unpack(">Q", bas)[0]'),
    ("kapsama denetimi yok", '    if konum != toplam - 8 - n:\n        raise ValueError("veri bölümü uzunluğu başlıkla tutmuyor")\n', ""),
    ("parametre bayt", 'sum(math.prod(t["shape"]) for t in tensorler)', 'sum(t["son"] - t["bas"] for t in tensorler)'),
]
kodlar = [("referans", sol), ("başlangıç", st["starter"]), ("boş", ""),
          ("sabit", "def ozetler(yol):\n    return {'boyut': 0, 'sha256': '', 'git_blob': ''}\n"
                    "def safetensors_baslik(yol):\n    return {'metadata': {'format': 'pt'}, 'tensorler': [], 'parametre': 134515008}\n")]
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
