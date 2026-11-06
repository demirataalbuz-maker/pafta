import os
import sys
import tempfile
sys.path.insert(0, r"C:\Users\demo12\Documents\Pafta-AI-GercekLab")
sys.path.insert(0, r"C:\Users\demo12\Documents\Pafta-AI-GercekLab\tools")
bos = tempfile.mkdtemp(prefix="pafta_bos_hf_")
os.environ["HF_HUB_CACHE"] = bos
os.environ["HF_HOME"] = bos
import test_ai_gercek as T
from engine.lessons import Library
lib = Library()
idx, st = T.adim(lib, "ai-temel", "ai-temel-19")
res, s = T.kos(lib, "ai-temel", st, st["solution"])
print("model dosyası yok:", res.get("status"), T.kisa(res)[:220], "kanıt:", [(k.get("kaynak"), k.get("kabul")) for k in res.get("ai_kanit") or []])
os.rmdir(bos)
