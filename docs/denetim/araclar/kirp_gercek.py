"""Mutasyon için anlık görüntü: projeyi <hedef>'e kopyalar ve derslerdeki `::: gorev Gerçek deney` adımlarını çıkarır
(gerçek deneyler mutasyonda koşmaz; kalan görevler sınanır).
    python -X utf8 docs/denetim/araclar/kirp_gercek.py <hedef klasör>
    python -X utf8 docs/denetim/araclar/mutasyon.py <hedef klasör> --en-cok 1000 <ders...>
"""
import pathlib
import shutil
import sys

KOK = pathlib.Path(__file__).resolve().parents[3]
hedef = pathlib.Path(sys.argv[1]).resolve()
if hedef.exists():
    shutil.rmtree(hedef)
for ad in ("engine", "sandbox", "web", "tracks"):
    shutil.copytree(KOK / ad, hedef / ad, ignore=shutil.ignore_patterns("__pycache__"))
shutil.copytree(KOK / "docs/denetim/araclar", hedef / "docs/denetim/araclar")
(hedef / "tools").mkdir()
shutil.copy2(KOK / "tools/validate.py", hedef / "tools/validate.py")
n = 0
for md in hedef.glob("tracks/*/lessons/*.md"):
    out, atla = [], False
    for s in md.read_text(encoding="utf-8").split("\n"):
        if not atla and s.startswith("::: gorev Gerçek deney"):
            atla, n = True, n + 1
            continue
        if atla:
            atla = s.strip() != ":::"
            continue
        out.append(s)
    md.write_text("\n".join(out), encoding="utf-8")
print(f"{hedef} · kırpılan gerçek deney adımı: {n}")
