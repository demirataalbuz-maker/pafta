# -*- coding: utf-8 -*-
"""ai-savunma-19 gerçek deneyi: kiracı yalıtımı, çapraz kiracı kaydı en benzer olsa bile getirmez.

Deney GERÇEK gömme modeliyle (all-minilm:22m) bir kiracı-a sorgusu ile vektör kayıtları arasındaki
kosinüs benzerliğini (gerçek `skor`) hesaplar. Kayıtların biri kiracı-b'ye aittir ve sorguya en
benzer olandır. Öğrencinin `yetkili_vektorleri_getir` işlevi yalnız aynı kiracının (a) ve skor eşiğini
geçen kayıtlarını getirir.

Kritik ölçüm: en yüksek gerçek embedding skoruna sahip kayıt kiracı-b'den geliyorsa sonuca GİRMEZ;
getirilen bütün kayıtlar kiracı-a'dır. Böylece benzerlik sıralaması kiracı sınırını aşamaz — çapraz
kiracı sızıntısı olmaz.

Kayıtlar sentetiktir. Gömme modeli bu deney tarafından yüklendiyse boşaltılır (kullanıcınınkine
dokunulmaz).
"""
import json
import math
import urllib.error
import urllib.request

import ai_lab

GOMME_MODELI = "all-minilm:22m"
SORGU_METNI = "İade süresi kaç gündür?"
POLITIKA = {"izinli_kiracilar": ["a", "b"], "min_skor": 0.3, "max_top_k": 5,
            "filtre_zorunlu": True, "capraz_kiraci": False}
SORGU = {"id": "q-1", "kiraci": "a", "filtre_kiraci": "a", "top_k": 3}
# (id, kiraci, metin) — b-iade kiracı-b'ye ait ve sorguya en benzer
KAYIT_TANIM = [
    ("a-iade", "a", "İade süresi teslimattan sonra 14 gündür."),
    ("b-iade", "b", "İade süresi kaç gündür? İade süresi 30 gündür."),
    ("a-kargo", "a", "140 TL üzeri siparişlerde kargo ücretsizdir."),
]


def _istek(adres, yol, govde, sure=120):
    req = urllib.request.Request(adres + yol, json.dumps(govde).encode(), {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=sure) as r:
        return json.loads(r.read())


class _Gomucu:
    def __init__(self, adres):
        self.adres = adres
        try:
            bilgi = _istek(adres, "/api/show", {"model": GOMME_MODELI}, sure=30)
        except Exception as e:
            raise ai_lab.GercekLabYok(f"gömme modeli {GOMME_MODELI} kurulu değil ({type(e).__name__}). "
                                      f"Kurulum: ollama pull {GOMME_MODELI}") from e
        with urllib.request.urlopen(adres + "/api/ps", timeout=30) as r:
            yuklu = [m["name"] for m in json.loads(r.read())["models"]]
        self.once_yukluydu = GOMME_MODELI in yuklu
        det = bilgi.get("details", {})
        self.kayit = {"model": GOMME_MODELI, "parametre": det.get("parameter_size"), "once_yukluydu": self.once_yukluydu}

    def __call__(self, metinler):
        govde = {"model": GOMME_MODELI, "input": metinler}
        if not self.once_yukluydu:
            govde["keep_alive"] = 0
        try:
            return _istek(self.adres, "/api/embed", govde)["embeddings"]
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"Ollama /api/embed HTTP {e.code}") from e


def _birim(v):
    boy = math.sqrt(sum(x * x for x in v))
    return [x / boy for x in v] if boy else list(v)


def _kosinus(a, b):
    ua, ub = _birim(a), _birim(b)
    return sum(x * y for x, y in zip(ua, ub))


def deney(yetkili_vektorleri_getir):
    metinler = [t[2] for t in KAYIT_TANIM]
    with ai_lab.SohbetOturumu() as oturum:
        gom = _Gomucu(oturum.adres)
        sorgu_vek = gom([SORGU_METNI])[0]
        kayit_vek = gom(metinler)
        ortam = dict(oturum.kayit)
    ortam["gomme"] = gom.kayit
    kayitlar = []
    for (kid, kiraci, metin), vek in zip(KAYIT_TANIM, kayit_vek):
        skor = max(0.0, min(1.0, round(_kosinus(sorgu_vek, vek), 6)))
        kayitlar.append({"id": kid, "kiraci": kiraci, "skor": skor, "metin": metin})
    sonuc = yetkili_vektorleri_getir([dict(k) for k in kayitlar], dict(SORGU), dict(POLITIKA))
    en_yuksek = max(kayitlar, key=lambda k: k["skor"])
    sonuc_idler = [s["id"] for s in sonuc]
    sonuc_kiracilar = sorted({s["kiraci"] for s in sonuc})
    return {"ortam": ortam, "sorgu_metni": SORGU_METNI, "kayitlar": kayitlar, "sonuc": sonuc,
            "sonuc_idler": sonuc_idler, "sonuc_kiracilar": sonuc_kiracilar,
            "en_yuksek_id": en_yuksek["id"], "en_yuksek_kiraci": en_yuksek["kiraci"],
            "en_yuksek_dislandi": en_yuksek["id"] not in sonuc_idler and en_yuksek["kiraci"] != SORGU["kiraci"],
            "capraz_sizinti": any(s["kiraci"] != SORGU["kiraci"] for s in sonuc)}


def ozet(r):
    return {"kayit": len(r["kayitlar"]), "sonuc_idler": r["sonuc_idler"], "sonuc_kiracilar": r["sonuc_kiracilar"],
            "en_yuksek_id": r["en_yuksek_id"], "en_yuksek_kiraci": r["en_yuksek_kiraci"],
            "en_yuksek_dislandi": r["en_yuksek_dislandi"], "capraz_sizinti": r["capraz_sizinti"],
            "skorlar": {k["id"]: k["skor"] for k in r["kayitlar"]}}


def goster(yetkili_vektorleri_getir):
    """Çalıştır düğmesi: gerçek embedding skoru + kiracı yalıtımı."""
    r = deney(yetkili_vektorleri_getir)
    o = r["ortam"]
    print(f"Gömme: {o['gomme']['model']} ({o['gomme']['parametre']}) · sorgu kiracısı: {SORGU['kiraci']!r} · sorgu: {r['sorgu_metni']!r}\n")
    for k in sorted(r["kayitlar"], key=lambda x: -x["skor"]):
        print(f"   {k['id']}: kiracı={k['kiraci']} skor={k['skor']:.4f} metin={k['metin'][:36]!r}")
    oz = ozet(r)
    print(f"\nEn yüksek embedding skoru: {oz['en_yuksek_id']} (kiracı {oz['en_yuksek_kiraci']})")
    print(f"Getirilen kayıtlar: {oz['sonuc_idler']} · kiracılar: {oz['sonuc_kiracilar']} · çapraz kiracı sızıntısı: {oz['capraz_sizinti']}")
    print("Not: en benzer kayıt kiracı-b'den geldiği için yüksek skora rağmen getirilmedi — benzerlik sıralaması kiracı sınırını aşamaz.")
    print("Kanıt:", ai_lab.kanit_yaz("savunma-kiraci-calistir", {"kaynak": "gercek", "kabul": False,
                                                               "ders": "ai-savunma-19", "ortam": o, "ozet": oz}))
