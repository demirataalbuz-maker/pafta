# -*- coding: utf-8 -*-
"""ai-savunma-25 gerçek deneyi: kanıt manifestosu gerçek bir kanıt dosyasının ASIL özetiyle doğrulanır.

Deney gerçek yerel modelle bir özetleme etkileşimi yapar ve ai_lab.kanit_yaz ile GERÇEK bir kanıt
JSON dosyası yazar. Dosyanın bayt içeriğinden gerçek SHA-256 ve bayt uzunluğu hesaplanır; bu değerlerle
bir kanıt manifestosu kurulur. Öğrencinin `kanit_manifestu_dogrula` işlevi manifestonun şemasını
doğrular.

Kritik ölçüm: doğru manifesto hem şemadan hem de gerçek dosyanın yeniden-hash'inden geçer (bütünlük
korunmuş). Sahte bir manifesto (özeti sıfırlanmış) şema olarak GEÇERLİ olsa bile, dosya yeniden
hash'lendiğinde özet uyuşmaz — yani şema geçerliliği kanıt bütünlüğünü kanıtlamaz; devir zincirinde
yeniden-hash şarttır. Böylece kanıt koruma gerçek bir artefakt üzerinde gösterilir.

Kanıt dosyası bu deneyin kendi çıktısıdır; gizli veri içermez. Model bu deney tarafından yüklendiyse
boşaltılır.
"""
import hashlib
import json

import ai_lab

BELGE = "Pafta yerel modellerle calisan bir guvenlik egitimidir; kurulum birkac komutla biter."
SIFIR_SHA = "0" * 64


def _dosya_sha_bayt(yol):
    with open(yol, "rb") as f:
        veri = f.read()
    return hashlib.sha256(veri).hexdigest(), len(veri)


def deney(kanit_manifestu_dogrula):
    with ai_lab.SohbetOturumu() as oturum:
        c = oturum.sohbet([{"role": "system", "content": "Sen bir asistanisin; kisa ozetle."},
                           {"role": "user", "content": "Belgeyi ozetle.\n---\n" + BELGE + "\n---"}],
                          seed=5, sicaklik=0.0, en_fazla=80)
        ortam = dict(oturum.kayit)
        ozet_metni = (c["icerik"] or "")[:200]
    # GERÇEK bir kanıt dosyası yaz (olay müdahalesi kanıtı)
    yol = ai_lab.kanit_yaz("savunma-olay-kaniti", {"kaynak": "gercek", "kabul": False, "ders": "ai-savunma-25",
                                                   "olay": "ornek-ozetleme", "ozet": ozet_metni, "ortam": ortam})
    gercek_sha, gercek_bayt = _dosya_sha_bayt(yol)

    dogru = {"olay_id": "olay-1", "kanit_id": "kanit-1", "sha256": gercek_sha, "bayt": gercek_bayt, "zaman": 0}
    sahte = {"olay_id": "olay-1", "kanit_id": "kanit-2", "sha256": SIFIR_SHA, "bayt": gercek_bayt, "zaman": 0}

    dogru_dogrulandi = kanit_manifestu_dogrula(dict(dogru))      # şema doğrulaması (öğrenci)
    sahte_dogrulandi = kanit_manifestu_dogrula(dict(sahte))      # şema olarak da geçerli (64 hex)
    # Gerçek bütünlük: dosyayı yeniden hash'le, manifestoyla karşılaştır
    yeniden_sha, _ = _dosya_sha_bayt(yol)
    dogru_butunluk = yeniden_sha == dogru_dogrulandi["sha256"]
    sahte_butunluk = yeniden_sha == sahte_dogrulandi["sha256"]
    return {"ortam": ortam, "yol": yol, "gercek_sha": gercek_sha, "gercek_bayt": gercek_bayt,
            "dogru": dogru_dogrulandi, "sahte": sahte_dogrulandi,
            "dogru_sema_gecerli": dogru_dogrulandi == dogru, "sahte_sema_gecerli": sahte_dogrulandi == sahte,
            "dogru_butunluk": dogru_butunluk, "sahte_butunluk": sahte_butunluk}


def ozet(r):
    return {"gercek_sha_onek": r["gercek_sha"][:12] + "…", "gercek_bayt": r["gercek_bayt"],
            "dogru_sema_gecerli": r["dogru_sema_gecerli"], "sahte_sema_gecerli": r["sahte_sema_gecerli"],
            "dogru_butunluk": r["dogru_butunluk"], "sahte_butunluk": r["sahte_butunluk"]}


def goster(kanit_manifestu_dogrula):
    """Çalıştır düğmesi: gerçek kanıt dosyasının manifestosunu doğrula ve yeniden-hash'le."""
    r = deney(kanit_manifestu_dogrula)
    o = r["ortam"]
    print(f"Model: {(o.get('model') or {}).get('ad')}\n")
    print(f"   Gerçek kanıt dosyası yazıldı · SHA-256: {r['gercek_sha'][:16]}… · {r['gercek_bayt']} bayt")
    oz = ozet(r)
    print(f"\n   Doğru manifesto: şema geçerli={oz['dogru_sema_gecerli']} · yeniden-hash bütünlük={oz['dogru_butunluk']}")
    print(f"   Sahte manifesto (özet sıfırlı): şema geçerli={oz['sahte_sema_gecerli']} · yeniden-hash bütünlük={oz['sahte_butunluk']}")
    print("Not: sahte manifesto şema olarak geçerli ama dosya yeniden hash'lendiğinde özet uyuşmadı — şema geçerliliği kanıt bütünlüğünü kanıtlamaz, yeniden-hash şarttır.")
    print("Kanıt:", ai_lab.kanit_yaz("savunma-olay-calistir", {"kaynak": "gercek", "kabul": False,
                                                              "ders": "ai-savunma-25", "ortam": o, "ozet": oz}))
