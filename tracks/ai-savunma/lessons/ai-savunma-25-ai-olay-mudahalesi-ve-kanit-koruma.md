---
id: ai-savunma-25
title: AI Olay Müdahalesi ve Kanıt Koruma
summary: Olayları önceliklendir; kanıt manifestolarını ve devir zincirini doğrulayarak güvenli toparlanma için tekrarlanabilir kayıtlar üret.
timeout: 45
---

::: anlat Müdahale sırası kanıt bütünlüğünü korumalıdır
AI olayında kapsam, etkilenen sistem, olay seviyesi ve korunacak kanıtlar açıkça kaydedilir. Erişimi sınırlama veya önceki model sürümüne dönme gibi adımlar, kanıtların kaynağını ve bütünlüğünü kaybettirmemelidir. Manifestodaki özet değeri, bayt sayısı ve zaman bilgisi sonradan yapılan karşılaştırmaların dayanağıdır.

Bu derste Elastic, SigNoz veya MLflow'a bağlanılmaz; ağ, gerçek model ve gerçek olay verisi kullanılmaz. Bütün olaylar ve kanıtlar deterministik fixture kayıtlarıdır. Dersin listeleri örnek bir müdahale politikasıdır, her kurumun olay planının yerine geçmez.
:::

::: anlat Devir zinciri sıra, zaman ve sahiplik ilişkisini korur
Kanıt her devrinde sıra numarası, zaman, gönderen, alan ve SHA-256 özetiyle kaydedilir. Sıralar her kanıt için sıfırdan başlar ve birer artar. Zaman geriye gidemez; bir adımın alıcısı sonraki adımın göndereni olur. Özet değeri zincir boyunca değişmez.

Sıralama yalnız görünüm için yapılmaz: müdahale planında yüksek seviye önce gelir, kanıt raporunda ise kanıt kimlikleri alfabetik sıralanır. Böylece aynı kayıtlar farklı sırada verilse bile aynı sonuç üretilir.
:::

::: tahmin Sıra ve zaman koşullarını tahmin et
Üç çıktı satırını yaz:

```python
siralar = [0, 1, 2]
zamanlar = [10, 10, 12]
print(siralar == list(range(len(siralar))))
print(all(a <= b for a, b in zip(zamanlar, zamanlar[1:])))
print(all(x == "ab" * 32 for x in ["ab" * 32, "ab" * 32]))
```

???

```cikti
True
True
True
```

Bu koşullar tek başına kanıtın gerçekliğini kanıtlamaz; yalnız fixture zincirinin iç tutarlılığını denetler.
:::

::: gorev 1 · Kanıt manifestosunu doğrula
`kanit_manifestu_dogrula(kayit)` işlevini yaz. Kayıt tam olarak `olay_id`, `kanit_id`, `sha256`, `bayt`, `zaman` alanlarını taşısın. İki kimlik de 1–64 karakterlik, ASCII harf/rakamla başlayan ve yalnız ASCII harf, rakam, alt çizgi veya tire içeren stringdir.

`sha256`, 64 küçük harfli onaltılık karakterden oluşan stringdir. `bayt` ve `zaman`, bool olmayan, sıfır veya pozitif tamsayılardır. Geçersiz veride `ValueError` yükselt. Alanları aynı değerlerle yeni bir sözlükte döndür; girdiyi değiştirme.

```starter
def kanit_manifestu_dogrula(kayit):
    return {}
```

```test
import copy
M = {"olay_id": "o-1", "kanit_id": "k-1", "sha256": "ab" * 32, "bayt": 0, "zaman": 0}
def sozlesme(fn):
    try:
        once = copy.deepcopy(M)
        sonuc = fn(M)
        if sonuc != M or M != once or sonuc is M:
            return False
        if fn(dict(M, olay_id="a" * 64, kanit_id="k" * 64, sha256="0" * 64))["bayt"] != 0:
            return False
        if fn(dict(M, bayt=1024, zaman=99))["zaman"] != 99:
            return False
        for kayit in [
            None, [], dict(M, ek=1), dict(M, olay_id=""), dict(M, olay_id="a b"), dict(M, olay_id="a" * 65),
            dict(M, kanit_id=""), dict(M, kanit_id="a b"), dict(M, kanit_id="a" * 65),
            dict(M, sha256="AB" * 32), dict(M, sha256="a" * 63), dict(M, sha256="g" * 64), dict(M, sha256=1),
            dict(M, bayt=-1), dict(M, bayt=True), dict(M, bayt=1.0),
            dict(M, zaman=-1), dict(M, zaman=False), dict(M, zaman=1.0),
        ]:
            try:
                fn(kayit)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(kanit_manifestu_dogrula), "kimlik, özet, bayt ve zaman kuralları korunmalı")
def m_sha(kayit):
    sonuc = kanit_manifestu_dogrula(kayit)
    sonuc["sha256"] = "0" * 64
    return sonuc
def m_bayt(kayit):
    sonuc = kanit_manifestu_dogrula(kayit)
    sonuc["bayt"] = 1
    return sonuc
def m_zaman(kayit):
    sonuc = kanit_manifestu_dogrula(kayit)
    sonuc["zaman"] = 1
    return sonuc
for ad, mutant in [("özeti değiştiren", m_sha), ("baytı değiştiren", m_bayt), ("zamanı değiştiren", m_zaman)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def kanit_manifestu_dogrula(kayit):
    import re
    if not isinstance(kayit, dict):
        raise ValueError("kayıt sözlük olmalı")
    if set(kayit) != {"olay_id", "kanit_id", "sha256", "bayt", "zaman"}:
        raise ValueError("manifesto şeması geçersiz")
    for alan in ("olay_id", "kanit_id"):
        deger = kayit[alan]
        if not isinstance(deger, str):
            raise ValueError("kimlik string olmalı")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", deger):
            raise ValueError("kimlik geçersiz")
    if not isinstance(kayit["sha256"], str):
        raise ValueError("özet string olmalı")
    if not re.fullmatch(r"[0-9a-f]{64}", kayit["sha256"]):
        raise ValueError("özet geçersiz")
    for alan in ("bayt", "zaman"):
        deger = kayit[alan]
        if isinstance(deger, bool) or not isinstance(deger, int):
            raise ValueError("sayısal alan tamsayı olmalı")
        if deger < 0:
            raise ValueError("sayısal alan negatif olamaz")
    return {"olay_id": kayit["olay_id"], "kanit_id": kayit["kanit_id"], "sha256": kayit["sha256"], "bayt": kayit["bayt"], "zaman": kayit["zaman"]}
```

```hint
Kimlik ve özeti ayrı desenlerle doğrula. Tamsayı alanlarında `bool` değerlerini açıkça reddet; sıfır geçerlidir.
```
:::

::: gorev 2 · Olaylardan öncelikli müdahale planı üret
`mudahale_plani_uret(olaylar)` işlevini yaz. Girdi liste olmalı; her olay tam olarak `id`, `seviye`, `kategori`, `sistem`, `kanit_ids` alanlarını taşısın. Olay kimliği ilk görevdeki desene uyan benzersiz stringdir. Seviye `dusuk`, `orta`, `yuksek`, `kritik`; kategori `sizinti`, `prompt_injection`, `yetkisiz_erisim`, `model_sapmasi` olmalıdır.

Sistem başı/sonu boşluğu olmayan boş olmayan stringdir ve kontrol karakteri içeremez. Kanıt kimlikleri yinelenmeyen listedir; her öğe ilk görevdeki kimlik desenine uyar. Liste boş olabilir. Geçersiz veride `ValueError` yükselt.

Her olay için `{"olay_id":ID,"oncelik":SAYI,"adimlar":[...]}` döndür. Öncelik `kritik=0`, `yuksek=1`, `orta=2`, `dusuk=3` olsun. Adımlar sırasıyla `olayi_kaydet`, `kanitlari_koru`; yüksek veya kritikse `erisimi_sinirla`; kategoriye göre sırasıyla `veri_sizintisini_durdur`, `istekleri_filtrele`, `oturumlari_iptal_et`, `onceki_surume_don`; son olarak `guvenli_toparlanmayi_dogrula` içersin. Sonuçları öncelik, sonra olay kimliğiyle sırala. Boş girdide boş liste döndür ve girdileri değiştirme.

```starter
def mudahale_plani_uret(olaylar):
    return []
```

```test
import copy
O = [
    {"id": "o-dusuk", "seviye": "dusuk", "kategori": "model_sapmasi", "sistem": "AI API", "kanit_ids": []},
    {"id": "o-kritik", "seviye": "kritik", "kategori": "sizinti", "sistem": "sohbet", "kanit_ids": ["k-1", "k-2"]},
    {"id": "o-yuksek", "seviye": "yuksek", "kategori": "prompt_injection", "sistem": "yardim", "kanit_ids": ["k-3"]},
]
BEKLENEN = [
    {"olay_id": "o-kritik", "oncelik": 0, "adimlar": ["olayi_kaydet", "kanitlari_koru", "erisimi_sinirla", "veri_sizintisini_durdur", "guvenli_toparlanmayi_dogrula"]},
    {"olay_id": "o-yuksek", "oncelik": 1, "adimlar": ["olayi_kaydet", "kanitlari_koru", "erisimi_sinirla", "istekleri_filtrele", "guvenli_toparlanmayi_dogrula"]},
    {"olay_id": "o-dusuk", "oncelik": 3, "adimlar": ["olayi_kaydet", "kanitlari_koru", "onceki_surume_don", "guvenli_toparlanmayi_dogrula"]},
]
def sozlesme(fn):
    try:
        once = copy.deepcopy(O)
        if fn(O) != BEKLENEN or O != once or fn(list(reversed(O))) != BEKLENEN or fn([]) != []:
            return False
        if fn([dict(O[0], id="a" * 64, seviye="orta")])[0]["oncelik"] != 2:
            return False
        yetki = fn([dict(O[0], id="o-yetki", kategori="yetkisiz_erisim")])
        if yetki[0]["adimlar"][-2] != "oturumlari_iptal_et":
            return False
        if fn([dict(O[0], kanit_ids=["a" * 64])])[0]["olay_id"] != "o-dusuk":
            return False
        for olaylar in [
            None, {}, [None], [dict(O[0], ek=1)], [dict(O[0], id="a b")], [dict(O[0], id="a" * 65)],
            [O[0], O[0]], [dict(O[0], seviye="bilinmeyen")], [dict(O[0], kategori="diger")],
            [dict(O[0], sistem="")], [dict(O[0], sistem=" x")], [dict(O[0], sistem="a\0b")],
            [dict(O[0], kanit_ids=None)], [dict(O[0], kanit_ids="k-1")], [dict(O[0], kanit_ids=["a b"])],
            [dict(O[0], kanit_ids=["a" * 65])], [dict(O[0], kanit_ids=["k-1", "k-1"])],
        ]:
            try:
                fn(olaylar)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(mudahale_plani_uret), "öncelik, kategori adımı ve kanıt kimlikleri korunmalı")
def m_seviye(olaylar):
    return mudahale_plani_uret([dict(x, seviye="dusuk") for x in olaylar])
def m_kategori(olaylar):
    return mudahale_plani_uret([dict(x, kategori="model_sapmasi") for x in olaylar])
def m_sistem(olaylar):
    return mudahale_plani_uret([dict(x, sistem=" " + x["sistem"]) for x in olaylar])
for ad, mutant in [("seviyeyi düşüren", m_seviye), ("kategoriyi değiştiren", m_kategori), ("sistemi bozan", m_sistem)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def mudahale_plani_uret(olaylar):
    import re
    if not isinstance(olaylar, list):
        raise ValueError("olaylar liste olmalı")
    oncelikler = {"kritik": 0, "yuksek": 1, "orta": 2, "dusuk": 3}
    kategori_adimlari = {
        "sizinti": "veri_sizintisini_durdur",
        "prompt_injection": "istekleri_filtrele",
        "yetkisiz_erisim": "oturumlari_iptal_et",
        "model_sapmasi": "onceki_surume_don",
    }
    gorulen = set()
    for olay in olaylar:
        if not isinstance(olay, dict):
            raise ValueError("olay sözlük olmalı")
        if set(olay) != {"id", "seviye", "kategori", "sistem", "kanit_ids"}:
            raise ValueError("olay şeması geçersiz")
        if not isinstance(olay["id"], str):
            raise ValueError("olay kimliği string olmalı")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", olay["id"]):
            raise ValueError("olay kimliği geçersiz")
        if olay["id"] in gorulen:
            raise ValueError("olay kimliği yinelenemez")
        gorulen.add(olay["id"])
        if olay["seviye"] not in oncelikler:
            raise ValueError("seviye geçersiz")
        if olay["kategori"] not in kategori_adimlari:
            raise ValueError("kategori geçersiz")
        sistem = olay["sistem"]
        if not isinstance(sistem, str):
            raise ValueError("sistem string olmalı")
        if not sistem or sistem != sistem.strip():
            raise ValueError("sistem boşluk biçimi geçersiz")
        if any(ord(k) < 32 for k in sistem):
            raise ValueError("sistem kontrol karakteri içeremez")
        kanit_ids = olay["kanit_ids"]
        if not isinstance(kanit_ids, list):
            raise ValueError("kanıt kimlikleri liste olmalı")
        if len(set(kanit_ids)) != len(kanit_ids):
            raise ValueError("kanıt kimlikleri yinelenemez")
        for kanit_id in kanit_ids:
            if not isinstance(kanit_id, str):
                raise ValueError("kanıt kimliği string olmalı")
            if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", kanit_id):
                raise ValueError("kanıt kimliği geçersiz")
    sonuc = []
    for olay in olaylar:
        adimlar = ["olayi_kaydet", "kanitlari_koru"]
        if olay["seviye"] in ("kritik", "yuksek"):
            adimlar.append("erisimi_sinirla")
        adimlar.append(kategori_adimlari[olay["kategori"]])
        adimlar.append("guvenli_toparlanmayi_dogrula")
        sonuc.append({"olay_id": olay["id"], "oncelik": oncelikler[olay["seviye"]], "adimlar": adimlar})
    return sorted(sonuc, key=lambda x: (x["oncelik"], x["olay_id"]))
```

```hint
Öncelik ve kategori adımlarını sözlüklerde tut. Erişim sınırlama adımını yalnız yüksek ve kritik olaylarda ekle.
```
:::

::: gorev 3 · Kanıt devir zincirini doğrula ve özetle
`kanit_zinciri_dogrula(kayitlar)` işlevini yaz. Girdi liste olmalı; her kayıt tam olarak `kanit_id`, `sira`, `zaman`, `gonderen`, `alan`, `sha256` alanlarını taşısın. Kimlik ve özet ilk görevdeki kuralları sağlasın. Sıra ve zaman bool olmayan, sıfır veya pozitif tamsayılardır. Gönderen ve alan başı/sonu boşluğu olmayan boş olmayan stringdir ve kontrol karakteri içeremez.

Her kanıtın sıraları sıfırdan başlamalı ve birer artmalı, zamanları geriye gitmemeli, SHA-256 özeti değişmemelidir. Sıfırdan büyük adımın göndereni, önceki adımın alanıyla aynı olmalıdır. Aynı kanıt ve sıra numarası yinelenemez. Geçersiz veride `ValueError` yükselt.

Her kanıt için `{"kanit_id":ID,"adim_sayisi":N,"son_zaman":ZAMAN,"son_sahip":ALAN,"sha256":OZET}` döndür. Kanıt kimliğine göre sırala; girdi sırasından bağımsız çalış. Boş girdide boş liste döndür ve girdileri değiştirme.

```starter
def kanit_zinciri_dogrula(kayitlar):
    return []
```

```test
import copy
Z = [
    {"kanit_id": "k-b", "sira": 0, "zaman": 0, "gonderen": "olay muhafizi", "alan": "adli laboratuvar", "sha256": "ab" * 32},
    {"kanit_id": "k-b", "sira": 1, "zaman": 5, "gonderen": "adli laboratuvar", "alan": "kanit arsivi", "sha256": "ab" * 32},
    {"kanit_id": "k-a", "sira": 0, "zaman": 0, "gonderen": "saha eki", "alan": "adli laboratuvar", "sha256": "0" * 64},
]
BEKLENEN = [
    {"kanit_id": "k-a", "adim_sayisi": 1, "son_zaman": 0, "son_sahip": "adli laboratuvar", "sha256": "0" * 64},
    {"kanit_id": "k-b", "adim_sayisi": 2, "son_zaman": 5, "son_sahip": "kanit arsivi", "sha256": "ab" * 32},
]
def sozlesme(fn):
    try:
        once = copy.deepcopy(Z)
        if fn(Z) != BEKLENEN or Z != once or fn(list(reversed(Z))) != BEKLENEN or fn([]) != []:
            return False
        if fn([dict(Z[0], kanit_id="a" * 64)])[0]["adim_sayisi"] != 1:
            return False
        esit_zaman = [Z[0], dict(Z[1], zaman=0)]
        if fn(esit_zaman)[0]["son_zaman"] != 0:
            return False
        for kayitlar in [
            None, {}, [None], [dict(Z[0], ek=1)], [dict(Z[0], kanit_id="a b")], [dict(Z[0], kanit_id="a" * 65)],
            [dict(Z[0], sira=-1)], [dict(Z[0], sira=True)], [dict(Z[0], sira=1.0)],
            [dict(Z[0], zaman=-1)], [dict(Z[0], zaman=False)], [dict(Z[0], zaman=1.0)],
            [dict(Z[0], gonderen="")], [dict(Z[0], gonderen=" x")], [dict(Z[0], gonderen="a\0b")],
            [dict(Z[0], alan="")], [dict(Z[0], alan="x ")], [dict(Z[0], sha256="AB" * 32)],
            [Z[0], Z[0]], [dict(Z[0], sira=1)], [Z[0], dict(Z[1], sira=2)],
            [Z[0], dict(Z[1], zaman=-1)], [Z[0], dict(Z[1], sha256="0" * 64)],
            [Z[0], dict(Z[1], gonderen="baska ekip")],
        ]:
            try:
                fn(kayitlar)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(kanit_zinciri_dogrula), "sıra, zaman, devir ve özet bütünlüğü korunmalı")
def m_zaman(kayitlar):
    return kanit_zinciri_dogrula([dict(x, zaman=99) for x in kayitlar])
def m_sira(kayitlar):
    return kanit_zinciri_dogrula([dict(x, sira=0) for x in kayitlar])
def m_alan(kayitlar):
    return kanit_zinciri_dogrula([dict(x, alan="baska ekip") for x in kayitlar])
for ad, mutant in [("zamanı değiştiren", m_zaman), ("sırayı bozan", m_sira), ("devri bozan", m_alan)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def kanit_zinciri_dogrula(kayitlar):
    import re
    if not isinstance(kayitlar, list):
        raise ValueError("kayıtlar liste olmalı")
    gorulen = set()
    for kayit in kayitlar:
        if not isinstance(kayit, dict):
            raise ValueError("kayıt sözlük olmalı")
        if set(kayit) != {"kanit_id", "sira", "zaman", "gonderen", "alan", "sha256"}:
            raise ValueError("zincir şeması geçersiz")
        if not isinstance(kayit["kanit_id"], str):
            raise ValueError("kanıt kimliği string olmalı")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", kayit["kanit_id"]):
            raise ValueError("kanıt kimliği geçersiz")
        for alan in ("sira", "zaman"):
            deger = kayit[alan]
            if isinstance(deger, bool) or not isinstance(deger, int):
                raise ValueError("sıra ve zaman tamsayı olmalı")
            if deger < 0:
                raise ValueError("sıra ve zaman negatif olamaz")
        for alan in ("gonderen", "alan"):
            deger = kayit[alan]
            if not isinstance(deger, str):
                raise ValueError("sahip string olmalı")
            if not deger or deger != deger.strip():
                raise ValueError("sahip boşluk biçimi geçersiz")
            if any(ord(k) < 32 for k in deger):
                raise ValueError("sahip kontrol karakteri içeremez")
        if not isinstance(kayit["sha256"], str):
            raise ValueError("özet string olmalı")
        if not re.fullmatch(r"[0-9a-f]{64}", kayit["sha256"]):
            raise ValueError("özet geçersiz")
        anahtar = (kayit["kanit_id"], kayit["sira"])
        if anahtar in gorulen:
            raise ValueError("kanıt ve sıra yinelenemez")
        gorulen.add(anahtar)
    gruplar = {}
    for kayit in kayitlar:
        gruplar.setdefault(kayit["kanit_id"], []).append(kayit)
    sonuc = []
    for kanit_id in sorted(gruplar):
        zincir = sorted(gruplar[kanit_id], key=lambda x: x["sira"])
        for indeks, kayit in enumerate(zincir):
            if kayit["sira"] != indeks:
                raise ValueError("sıralar kesintisiz olmalı")
            if indeks:
                onceki = zincir[indeks - 1]
                if kayit["zaman"] < onceki["zaman"]:
                    raise ValueError("zaman geriye gidemez")
                if kayit["gonderen"] != onceki["alan"]:
                    raise ValueError("devir sahipleri uyuşmalı")
                if kayit["sha256"] != onceki["sha256"]:
                    raise ValueError("özet zincirde değişemez")
        son = zincir[-1]
        sonuc.append({"kanit_id": kanit_id, "adim_sayisi": len(zincir), "son_zaman": son["zaman"], "son_sahip": son["alan"], "sha256": son["sha256"]})
    return sonuc
```

```hint
Kayıtları kanıt kimliğiyle grupla ve her grubu sıra numarasına göre sırala. Beklenen sıra, grup içindeki indekse eşit olmalıdır.
```
:::

::: anlat Kanıt bütünlüğü gerçek bir artefakt üzerinde doğrulanır
Olay müdahalesinde manifestonun şema olarak geçerli olması yetmez; manifestodaki özet, kanıt dosyasının **gerçek** içeriğiyle eşleşmelidir. Son görevde senin `kanit_manifestu_dogrula` işlevin, gerçek yerel modelle yapılan bir etkileşimden `ai_lab.kanit_yaz` ile yazılan GERÇEK bir kanıt dosyasının manifestosunu doğrular. Sandbox dosyanın bayt içeriğinden gerçek SHA-256 ve bayt uzunluğunu hesaplar.

Deney şunu gösterir: doğru manifesto hem şemadan hem dosyanın yeniden-hash'inden geçer; özeti sıfırlanmış sahte bir manifesto şema olarak GEÇERLİ olsa bile yeniden-hash'te uyuşmaz. Yani şema geçerliliği kanıt bütünlüğünü kanıtlamaz; devir zincirinde artefaktı yeniden hash'lemek şarttır. Böylece kanıt koruma, uydurma bir kayıt değil gerçek bir dosya üzerinde test edilir.
:::

::: gorev Gerçek deney · Gerçek kanıt dosyasının manifestosunu doğrula
`kanit_manifestu_dogrula(kayit)` işlevini yaz — kuralları ve çıktısı 1. görevdekiyle **aynıdır**. Deney gerçek bir kanıt dosyası yazar, dosyanın gerçek SHA-256 ve bayt değerleriyle manifesto kurar; senin işlevin manifestoyu doğrular, deney ise dosyayı yeniden hash'leyerek bütünlüğü teyit eder.

```meta
motor: ai-gercek
gereksinim: ollama
timeout: 300
```

```starter
import ai_lab

def kanit_manifestu_dogrula(kayit):
    return {}

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_savunma_25 as deney
    deney.goster(kanit_manifestu_dogrula)
```

```test
import ai_lab
sonuclar = []
def kontrol(kosul, mesaj):
    sonuclar.append(bool(kosul))
    return ok(kosul, mesaj)
sorun = ai_lab.kod_denetimi(src, ("referans", "getattr"))
kontrol(not sorun, "laboratuvar yamalanmamalı, referans kullanılmamalı " + ", ".join(sorun))
fn = need("kanit_manifestu_dogrula")
from sandbox import ai_gercek_ai_savunma_25 as D
M = {"olay_id": "o-1", "kanit_id": "k-1", "sha256": "ab" * 32, "bayt": 10, "zaman": 5}
def sozlesme(f):
    try:
        if f(dict(M)) != M or f(dict(M)) is M:
            return False
        for bozuk in (None, dict(M, ek=1), dict(M, sha256="AB" * 32), dict(M, sha256="a" * 63), dict(M, bayt=-1), dict(M, bayt=True), dict(M, olay_id="a b")):
            try:
                f(bozuk)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
kontrol(sozlesme(fn), "kimlik, özet, bayt ve zaman kuralları korunmalı")
r, oz = None, None
if all(sonuclar):
    try:
        r = D.deney(fn)
    except ai_lab.GercekLabYok as e:
        kontrol(False, f"GERÇEK MODEL YOK, deney yapılmadı: {e}")
        stop()
    kontrol(r["dogru_sema_gecerli"] and r["dogru_butunluk"],
            "doğru manifesto hem şemadan hem gerçek dosyanın yeniden-hash'inden geçti")
    kontrol(r["sahte_sema_gecerli"] and not r["sahte_butunluk"],
            "sahte manifesto şema olarak geçerli ama yeniden-hash'te bütünlük bozuk (yakalandı)")
    oz = D.ozet(r)
yol = ai_lab.kanit_yaz("savunma-olay", {"kaynak": "gercek", "kabul": all(sonuclar), "ders": "ai-savunma-25",
                                        "ortam": (r or {}).get("ortam"), "ozet": oz})
if oz:
    ok(True, f"BULGU ({r['ortam']['model']['ad']}): gerçek kanıt dosyası SHA-256 {oz['gercek_sha_onek']} ({oz['gercek_bayt']} bayt); "
             f"doğru manifesto şema+bütünlük {oz['dogru_sema_gecerli']}/{oz['dogru_butunluk']}, sahte manifesto şema {oz['sahte_sema_gecerli']} ama bütünlük {oz['sahte_butunluk']}. "
             f"Şema geçerliliği kanıt bütünlüğünü kanıtlamaz; yeniden-hash şart.")
```

```solution
import ai_lab

def kanit_manifestu_dogrula(kayit):
    import re
    if not isinstance(kayit, dict):
        raise ValueError("kayıt sözlük olmalı")
    if set(kayit) != {"olay_id", "kanit_id", "sha256", "bayt", "zaman"}:
        raise ValueError("manifesto şeması geçersiz")
    for alan in ("olay_id", "kanit_id"):
        deger = kayit[alan]
        if not isinstance(deger, str):
            raise ValueError("kimlik string olmalı")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", deger):
            raise ValueError("kimlik geçersiz")
    if not isinstance(kayit["sha256"], str):
        raise ValueError("özet string olmalı")
    if not re.fullmatch(r"[0-9a-f]{64}", kayit["sha256"]):
        raise ValueError("özet geçersiz")
    for alan in ("bayt", "zaman"):
        deger = kayit[alan]
        if isinstance(deger, bool) or not isinstance(deger, int):
            raise ValueError("sayısal alan tamsayı olmalı")
        if deger < 0:
            raise ValueError("sayısal alan negatif olamaz")
    return {"olay_id": kayit["olay_id"], "kanit_id": kayit["kanit_id"], "sha256": kayit["sha256"], "bayt": kayit["bayt"], "zaman": kayit["zaman"]}

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_savunma_25 as deney
    deney.goster(kanit_manifestu_dogrula)
```

```hint
Bu işlev 1. görevdeki `kanit_manifestu_dogrula` ile birebir aynıdır; tek fark, manifestonun gerçek bir kanıt dosyasından kurulmasıdır. Kimlik ve özeti ayrı desenlerle doğrula; tamsayı alanlarında `bool`'u reddet.
```
:::
