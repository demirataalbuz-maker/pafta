"""Kopya sondası: bir dersin gerçek deney adımına öğrencinin kendi kodu yerine verilen kodu (ör. modüldeki referansı
import eden tek satır) Kontrol'den geçirir. Doğru korunan derste sonuç pass OLMAMALI.
    PAFTA_DATA=<izole klasör> python -X utf8 docs/denetim/araclar/kopya_sonda.py ai-guvence ai-guvence-17 "from sandbox.ai_gercek_ai_guvence_17_20 import ref17 as olc"
Birden çok satır için ';' kullan (ör. "import ai_lab; from sandbox.m import a_ref as a, b_ref as b").
Derste birden çok gerçek deney adımı varsa 4. argüman başlığın bir parçasıdır (ör. "GGUF").
"""
import os
import sys

sys.path.insert(0, os.getcwd())
from engine.lessons import Library  # noqa: E402
from engine.runners import for_step, get  # noqa: E402

tid, lid, kod = sys.argv[1], sys.argv[2], sys.argv[3]
parca = sys.argv[4] if len(sys.argv) > 4 else ""
lib = Library()
track = next(t for t in lib.tracks() if t["id"] == tid)
st = next(s for s in lib.lesson(tid, lid)["steps"] if s["kind"] == "gorev" and s["title"].startswith("Gerçek deney") and parca in s["title"])
r = for_step(get(track.get("runner", tid)), st).test(kod, st)
durum = r.get("status")
print(f"{lid} kopya sondası: {durum} → {'AÇIK (referans import edilince geçiyor)' if durum == 'pass' else 'korunuyor'}")
sys.exit(1 if durum == "pass" else 0)
