# -*- coding: utf-8 -*-
"""Rota: Pafta, TryHackMe ve HackTheBox Academy yollarının birlikte yürüdüğü sıra.

Pafta'nın ilerlemesi derslerden hesaplanır. THM/HTB ilerlemesi siteden okunup elle
girilir ve %LOCALAPPDATA%\\Pafta\\rota.json'da durur (progress.json'a dokunulmaz).
Yazımlar atomik (geçici dosya + os.replace).
"""
import datetime as _dt
import json
import os
import threading

from engine.progress import data_dir

# Her aşama: THM'de ısın, HTB'de derinleş, Pafta'da platformların atladığı kısmı öğren.
ASAMALAR = [
    {"id": "giris", "ad": "Giriş", "not": "İki tarafın temel kavramları. THM ile ısın, CJCA ile sağlamlaştır.",
     "thm": [("soc1", "SOC Level 1", None), ("jrpt", "Jr Penetration Tester", None)],
     "htb": [("cjca", "Junior Cybersecurity Analyst", "CJCA")],
     "pafta": ["python", "bash", "powershell", "cmd", "http"]},
    {"id": "omurga", "ad": "Omurga · kırmızı + mavi", "not": "CPTS ve CDSA paralel: biri saldırı, biri savunma omurgası.",
     "thm": [("soc2", "SOC Level 2", None), ("webpt", "Web Application Pentesting", None)],
     "htb": [("cpts", "Penetration Tester", "CPTS"), ("cdsa", "SOC Analyst", "CDSA")],
     "pafta": ["sql", "regex", "php", "javascript", "java", "packets", "spl", "elastic", "ids", "yara"]},
    {"id": "windows", "ad": "Windows ve Active Directory", "not": "Purple ekiplerin asıl sahası. Saldırı ve izleri aynı ortamda.",
     "thm": [("winir", "Windows Incident Response & Forensics", None),
             ("endpoint", "Advanced Endpoint Investigations", None)],
     "htb": [("cape", "AD Penetration Tester", "CAPE")],
     "pafta": ["ad", "c", "csharp", "asm"]},
    {"id": "tespit", "ad": "Tespit mühendisliği", "not": "Purple'ın kalbi: saldırıyı bilip tespitini yazmak ve ölçmek.",
     "thm": [("azure", "Defending Azure", None), ("redteam", "Red Teaming", None)],
     "htb": [("cdep", "Detection Engineer", "CDEP")],
     "pafta": ["sigma", "kql", "purple", "bitirme"]},
    {"id": "secmeli", "ad": "İsteğe bağlı", "not": "Purple ile bağı zayıf; vakit kalırsa.",
     "thm": [("webrt", "Web Application Red Teaming", None)],
     "htb": [("wifi", "Wi-Fi Penetration Tester", "CWPE")],
     "pafta": []},
]
# Aşamalardan bağımsız, kendi hızında giden yol
YAN_YOL = {"id": "yan", "ad": "Yan yol · kendi hızında", "not": "Seni diğer adaylardan ayıran yol; aşamaları beklemez.",
           "thm": [], "htb": [("aired", "AI Red Teamer", "COAE")], "pafta": []}

PLATFORM = ("thm", "htb")


class Rota:
    def __init__(self, path=None):
        self.path = path or os.path.join(data_dir(), "rota.json")
        self._lock = threading.Lock()
        try:
            with open(self.path, encoding="utf-8") as f:
                self.data = json.load(f)
        except (OSError, ValueError):
            self.data = {}
        for p in PLATFORM:
            self.data.setdefault(p, {})

    def _save(self):
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=1)
        os.replace(tmp, self.path)

    def guncelle(self, platform, yid, yuzde=None, sertifika=None):
        if platform not in PLATFORM:
            raise ValueError(f"bilinmeyen platform: {platform!r}")
        gecerli = {y[0] for a in ASAMALAR + [YAN_YOL] for y in a[platform]}
        if yid not in gecerli:
            raise ValueError(f"bilinmeyen yol: {yid!r}")
        with self._lock:
            k = self.data[platform].setdefault(yid, {"yuzde": 0, "sertifika": False})
            if yuzde is not None:
                k["yuzde"] = max(0.0, min(100.0, round(float(yuzde), 1)))
            if sertifika is not None:
                k["sertifika"] = bool(sertifika)
            k["tarih"] = _dt.date.today().isoformat()
            self._save()
            return dict(k)

    def gorunum(self, yollar):
        """`yollar`: App.state()['tracks'] listesi; Pafta yüzdeleri buradan hesaplanır."""
        pafta = {t["id"]: t for t in yollar if t.get("status") == "active"}

        def dis(platform, liste):
            return [{"id": i, "ad": ad, "sertifika_adi": s,
                     **{"yuzde": 0, "sertifika": False, "tarih": None}, **self.data[platform].get(i, {})}
                    for i, ad, s in liste]

        def asama(a):
            p = [{"id": tid, "ad": pafta[tid]["name"], "bitti": pafta[tid].get("steps_done", 0),
                  "toplam": pafta[tid].get("steps_total", 0)} for tid in a["pafta"] if tid in pafta]
            return {"id": a["id"], "ad": a["ad"], "not": a["not"], "pafta": p,
                    "thm": dis("thm", a["thm"]), "htb": dis("htb", a["htb"])}

        return {"asamalar": [asama(a) for a in ASAMALAR], "yan": asama(YAN_YOL)}
