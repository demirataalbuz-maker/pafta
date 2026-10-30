# -*- coding: utf-8 -*-
"""ai-savunma-04 gerçek deneyi: güvenli telemetri gerçek trafikten üretilmeli. Deney yerel modele birkaç
gerçek istek atar ve her birinden bir model telemetri olayı kurar: gerçek süre (sure_ms) ve gerçek çıktı
token sayısı (token_out) taşır, ama HAM istem/yanıt içermez (hassas içerik dışlanır). Öğrencinin metrik
raporu bu gerçek olayları toplar; deney ayrıca hiçbir olayda istem metninin sızmadığını doğrular.

İstemler zararsızdır. Model bu deney tarafından yüklendiyse sonunda boşaltılır.
"""
import ai_lab

ISTEMLER = [
    "İki artı iki kaçtır? Kısa yanıt ver.",
    "Türkiye'nin başkenti neresidir? Tek kelime.",
    "Suyun deniz seviyesinde kaynama sıcaklığı kaç derecedir? Kısa yanıt.",
]


def referans_rapor(olaylar):
    """Güvenli telemetri metrik referansı (geçerli olaylar varsayılır)."""
    gruplar, hatali, reddedildi, token_in, token_out = {}, 0, 0, 0, 0
    izler = set()
    for o in olaylar:
        izler.add(o["iz_id"])
        a = o["alanlar"]
        if a.get("durum") == "hata" or "hata_kodu" in a:
            hatali += 1
        if a.get("karar") == "reddet":
            reddedildi += 1
        token_in += a.get("token_in", 0)
        token_out += a.get("token_out", 0)
        gruplar.setdefault(o["tur"], []).append(o["sure_ms"])
    turler = {t: {"sayi": len(v), "ortalama_sure_ms": round(sum(v) / len(v), 3)} for t, v in sorted(gruplar.items())}
    return {"toplam": len(olaylar), "iz_sayisi": len(izler), "hatali": hatali, "reddedildi": reddedildi,
            "token_in": token_in, "token_out": token_out, "turler": turler}


def deney(telemetri_metrik_raporu):
    olaylar = []
    with ai_lab.SohbetOturumu() as oturum:
        for i, istem in enumerate(ISTEMLER):
            c = oturum.sohbet([{"role": "user", "content": istem}], seed=10 + i, sicaklik=0.2, en_fazla=40)
            olaylar.append({"iz_id": f"iz-{i}", "olay_id": f"model-{i}", "parent_id": None, "tur": "model",
                            "zaman_ms": i * 100, "sure_ms": c["sure_ms"],
                            "alanlar": {"model": oturum.model, "token_out": c["eval_count"] or 0, "durum": "ok"}})
        ortam = dict(oturum.kayit)
    ortam["temizlik"] = oturum.kayit.get("temizlik")
    rapor = telemetri_metrik_raporu([dict(o, alanlar=dict(o["alanlar"])) for o in olaylar])
    # mahremiyet: hiçbir olayda ham istem metni geçmemeli
    metin = str(olaylar)
    sizan = [istem for istem in ISTEMLER if istem in metin]
    return {"ortam": ortam, "olaylar": olaylar, "rapor": rapor, "sizan_istem": sizan}


def ozet(r):
    return {"olay": r["rapor"]["toplam"], "iz": r["rapor"]["iz_sayisi"], "token_out": r["rapor"]["token_out"],
            "model_ort_sure_ms": r["rapor"]["turler"].get("model", {}).get("ortalama_sure_ms"),
            "sizan_istem": len(r["sizan_istem"])}


def goster(telemetri_metrik_raporu):
    """Çalıştır düğmesi: gerçek trafikten güvenli telemetri."""
    r = deney(telemetri_metrik_raporu)
    o = r["ortam"]
    print(f"Model: {(o.get('model') or {}).get('ad')} · {len(r['olaylar'])} gerçek istek → telemetri olayı\n")
    for e in r["olaylar"]:
        print(f"   {e['tur']} iz={e['iz_id']} sure={e['sure_ms']}ms alanlar={e['alanlar']}")
    print(f"\nMetrik raporu: {r['rapor']}")
    print(f"Mahremiyet: olaylarda sızan ham istem = {len(r['sizan_istem'])} (0 olmalı — telemetri içerik taşımaz)")
    print("Kanıt:", ai_lab.kanit_yaz("savunma-telemetri-calistir", {"kaynak": "gercek", "kabul": False, "ders": "ai-savunma-04",
                                                                   "ortam": o, "ozet": ozet(r)}))
