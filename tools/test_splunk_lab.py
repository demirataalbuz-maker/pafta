# -*- coding: utf-8 -*-
"""SPL yolunun gerçek Splunk laboratuvarı (sandbox/splunk_lab.py, py_harness spk_*).

Docker çalışmıyorsa ya da Splunk konteyneri kurulamıyorsa testler atlanır.

    python tools/test_splunk_lab.py
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from engine.runners import for_step, get  # noqa: E402
from sandbox import splunk_lab  # noqa: E402

PROPS = {"meta": {"motor": "splunk", "girdi": "props"}}
ARAMA = {"meta": {"motor": "splunk"}}
VERI = 'veri("2026-10-19 09:01:12,345 ERROR a\\n  devam\\n2026-10-19 09:02:00,001 INFO b\\n", "pafta_t")\n'
KITA = ("[pafta_t]\nSHOULD_LINEMERGE = false\nLINE_BREAKER = ([\\r\\n]+)(?=\\d{4}-)\n"
        "TIME_PREFIX = ^\nTIME_FORMAT = %Y-%m-%d %H:%M:%S,%3N\n")


def setUpModule():
    sorun = splunk_lab.hazirla() if splunk_lab.available() else "Docker yok"
    if sorun:
        raise unittest.SkipTest(sorun)


class Splunk(unittest.TestCase):
    def test_props_girdisi(self):
        r = for_step(get("spl"), PROPS).run(KITA, "", VERI)
        self.assertEqual(r["status"], "ok", r.get("error"))
        satirlar = r["tablolar"][0]["satirlar"]
        self.assertEqual([s[0] for s in satirlar], ["2026-10-19 09:01:12.345", "2026-10-19 09:02:00.001"])
        self.assertIn("devam", satirlar[0][2], "devam satırı ilk olayda kalır")

    def test_props_hatalari(self):
        r = for_step(get("spl"), PROPS).run("[baska]\nTZ = UTC\n", "", VERI)
        self.assertIn("pafta_", r["error"]["msg"])
        r = for_step(get("spl"), PROPS).run("TZ = UTC\n", "", VERI)
        self.assertIn("kıta", r["error"]["msg"])

    def test_arama_ve_test(self):
        adim = dict(ARAMA, setup="props('pafta_t', {'SHOULD_LINEMERGE': 'false'})\n" + VERI,
                    test="eq(sutunlar, ['n'], 'alan')\neq(sonuc, [(3,)], 'üç satır')\n"
                         "eq(dene(\"veri('2026-10-19 10:00:00 x\\\\n', 'pafta_t')\"), [(4,)], 'dene ekler')")
        r = for_step(get("spl"), adim).test(f"index={splunk_lab.DIZIN} | stats count AS n", adim)
        self.assertEqual(r["status"], "pass", (r.get("checks"), r.get("error")))
        r = for_step(get("spl"), ARAMA).run("index=pafta_ders | bilinmeyenkomut", "", "")
        self.assertEqual(r["status"], "error")

    def test_bos_laboratuvar(self):
        r = for_step(get("spl"), ARAMA).run(f"index={splunk_lab.DIZIN} | stats count", "", "")
        self.assertEqual(r["tablolar"][0]["satirlar"], [["0"]], "önceki işin verisi temizlenmiş")


if __name__ == "__main__":
    unittest.main(verbosity=1)
