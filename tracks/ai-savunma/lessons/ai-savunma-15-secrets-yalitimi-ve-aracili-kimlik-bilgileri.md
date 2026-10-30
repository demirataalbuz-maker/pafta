---
id: ai-savunma-15
title: Secrets Yalıtımı ve Aracılı Kimlik Bilgileri
summary: Metindeki sırları maskele, kısa ömürlü ve dar kapsamlı kimlik bilgisini doğrula, gerçek sırrı göstermeden broker kullanım kararı üret.
timeout: 45
---

::: anlat Gerçek sır model bağlamına girmez
API anahtarı model istemine, araç çıktısına veya günlüğe açık metin olarak eklenmez. HashiCorp Vault gibi bir sır deposu ile FastAPI üzerindeki broker, kısa ömürlü ve yalnız belirli araç-eylem-kaynak kapsamında kimlik bilgisi üretebilir. Model yalnız opak bir referans veya kullanım kararı görür.

Bu dersteki bütün değerler yapay fixture verisidir. Maskeleme, günlükte yanlışlıkla görünen değeri temizlemek içindir; sırları modele göndermeyi güvenli hale getirme yöntemi değildir. Temel savunma, gerçek sırrı bağlama hiç eklememektir.
:::

::: anlat Çakışan değerlerde en uzun sır önce maskelenir
Bir sır diğerinin başlangıcıysa kısa olanı önce değiştirmek uzun değerin bir bölümünü açıkta bırakabilir. Bu nedenle maskeler uzunluk sırasıyla, en uzun değerden başlanır. Bulunan sayısı her gerçek metin eşleşmesini sayar; aynı sır iki kez geçiyorsa iki bulgu üretir.
:::

::: tahmin Maskeleme sırasını tahmin et
Üç çıktı satırını yaz:

```python
sirlar = sorted(["abc123", "abc12345"], key=len, reverse=True)
metin = "abc12345 ve abc12345"
for sir in sirlar:
    metin = metin.replace(sir, "[GIZLI]")
print(metin)
print(metin.count("[GIZLI]"))
print("abc12345" in metin)
```

???

```cikti
[GIZLI] ve [GIZLI]
2
False
```

Uzun değer önce maskelendiği için kısa değer yalnız bağımsız eşleşmeleri etkiler; açık sır kalmaz.
:::

::: gorev 1 · Metindeki yapay sırları maskele
`sir_maskele(kayitlar)` işlevini yaz. Kayıtlar liste; her kayıt tam olarak `id`, `metin`, `gizliler` alanlarını taşısın. Kimlik 1–64 karakterlik, ASCII harf/rakamla başlayan ve yalnız ASCII harf, rakam, alt çizgi veya tire içeren benzersiz stringdir. Metin string, gizliler liste olmalıdır.

Her gizli değer 4–128 karakterlik, yinelenmeyen ve satır sonu/NUL içermeyen stringdir. Geçersiz veride `ValueError` yükselt. Her kayıtta gizli değerleri uzunluğa göre azalan sırayla bütün eşleşmelerde `[GIZLI]` ile değiştir. Bulgu sayısı yapılan değişiklik değil, maskelenen eşleşme sayısıdır.

Her kayıt için `{"id":ID,"maskeli_metin":METIN,"bulgu":SAYI}` döndür. Kimliğe göre sırala, boş kayıtta boş liste döndür ve girdileri değiştirme.

```starter
def sir_maskele(kayitlar):
    return []
```

```test
import copy
K = [
    {"id": "kayit-1", "metin": "token=sk-live-1234; yedek=sk-live-1234; diger=abcd1234", "gizliler": ["abcd1234", "sk-live-1234"]},
    {"id": "temiz-1", "metin": "sır yok", "gizliler": ["abcd1234"]},
]
BEKLENEN = [
    {"id": "kayit-1", "maskeli_metin": "token=[GIZLI]; yedek=[GIZLI]; diger=[GIZLI]", "bulgu": 3},
    {"id": "temiz-1", "maskeli_metin": "sır yok", "bulgu": 0},
]
def sozlesme(fn):
    try:
        once = copy.deepcopy(K)
        if fn(K) != BEKLENEN or K != once or fn(list(reversed(K))) != BEKLENEN or fn([]) != []:
            return False
        cakisan = [{"id": "c-1", "metin": "abc12345", "gizliler": ["abc123", "abc12345"]}]
        if fn(cakisan) != [{"id": "c-1", "maskeli_metin": "[GIZLI]", "bulgu": 1}]:
            return False
        for uzunluk in (4, 128):
            sir = "a" * uzunluk
            if fn([{"id": "s", "metin": sir, "gizliler": [sir]}])[0]["bulgu"] != 1:
                return False
        if fn([dict(K[0], id="a" * 64)])[0]["id"] != "a" * 64:
            return False
        for kayitlar in [
            None, {}, [None], [dict(K[0], ek=1)], [dict(K[0], id="")], [dict(K[0], id="a b")],
            [dict(K[0], id="a" * 65)], [K[0], K[0]], [dict(K[0], metin=None)], [dict(K[0], gizliler=None)],
            [dict(K[0], gizliler=["abc"])], [dict(K[0], gizliler=["a" * 129])],
            [dict(K[0], gizliler=["abc\n"])], [dict(K[0], gizliler=["abc\0"])],
            [dict(K[0], gizliler=["abcd", "abcd"])],
        ]:
            try:
                fn(kayitlar)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(sir_maskele), "bütün eşleşmeler ve çakışan sırlar maskelenmeli")
def m_sayac(kayitlar):
    sonuc = sir_maskele(kayitlar)
    for kayit in sonuc:
        kayit["bulgu"] = 0
    return sonuc
def m_sira(kayitlar):
    degisen = [dict(x, gizliler=sorted(x["gizliler"], key=len)) for x in kayitlar]
    return sir_maskele(degisen)
def m_metin(kayitlar):
    return sir_maskele([dict(x, metin="") for x in kayitlar])
for ad, mutant in [("sayacı silen", m_sayac), ("sırayı bozan", m_sira), ("metni silen", m_metin)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def sir_maskele(kayitlar):
    import re
    if not isinstance(kayitlar, list):
        raise ValueError("kayıtlar liste olmalı")
    kimlikler = set()
    rapor = []
    for kayit in kayitlar:
        if not isinstance(kayit, dict):
            raise ValueError("kayıt sözlük olmalı")
        if set(kayit) != {"id", "metin", "gizliler"}:
            raise ValueError("kayıt şeması geçersiz")
        kimlik = kayit["id"]
        if not isinstance(kimlik, str):
            raise ValueError("kimlik metin olmalı")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", kimlik):
            raise ValueError("kimlik geçersiz")
        if kimlik in kimlikler:
            raise ValueError("kimlik yinelenemez")
        kimlikler.add(kimlik)
        if not isinstance(kayit["metin"], str):
            raise ValueError("metin string olmalı")
        if not isinstance(kayit["gizliler"], list):
            raise ValueError("gizliler liste olmalı")
        if len(set(kayit["gizliler"])) != len(kayit["gizliler"]):
            raise ValueError("gizliler yinelenemez")
        for sir in kayit["gizliler"]:
            if not isinstance(sir, str):
                raise ValueError("gizli değer metin olmalı")
            if len(sir) < 4:
                raise ValueError("gizli değer çok kısa")
            if len(sir) > 128:
                raise ValueError("gizli değer çok uzun")
            if "\n" in sir or "\r" in sir or "\0" in sir:
                raise ValueError("gizli değer kontrol karakteri içeremez")
        metin = kayit["metin"]
        bulgu = 0
        for sir in sorted(kayit["gizliler"], key=len, reverse=True):
            sayi = metin.count(sir)
            bulgu += sayi
            metin = metin.replace(sir, "[GIZLI]")
        rapor.append({"id": kimlik, "maskeli_metin": metin, "bulgu": bulgu})
    return sorted(rapor, key=lambda x: x["id"])
```

```hint
Önce gizli değerleri doğrula ve uzunluğa göre azalan sırala. `count` ile eşleşme sayısını topla, ardından `replace` ile bütün eşleşmeleri maskele.
```
:::

::: anlat Kapsam hem yetkiyi hem süreyi sınırlar
Aracılı kimlik bilgisi yalnız belirli araç, eylem ve kaynaklarda kullanılabilir. Modelin gerçek değeri görmesi yasaktır. Ömür bir ile 300 saniye arasındadır; son geçerlilik anı kullanım kararında hâlâ geçerlidir, sonrası süresi dolmuş sayılır.

Kapsam listelerindeki değerler benzersizdir. Böylece aynı yetkinin yinelenmesi denetim raporunu ve politika karşılaştırmasını bulandırmaz.
:::

::: gorev 2 · Kısa ömürlü ve dar kimlik kapsamını doğrula
`kimlik_kapsami_dogrula(kapsam)` işlevini yaz. Kapsam tam olarak `arac`, `eylemler`, `kaynaklar`, `verilis_ms`, `son_gecerlilik_ms`, `model_gorebilir` alanlarını taşısın. Araç `dosya_oku`, `web_getir`, `rapor_yaz`; eylemler `oku`, `yaz`, `getir`; kaynaklar `api.ornek.com`, `cdn.ornek.com`, `yerel/rapor` değerlerinden oluşan boş olmayan ve yinelenmeyen listelerdir.

Zamanlar bool olmayan sıfır/pozitif int olmalı; son geçerlilik verilişten büyük olmalı ve fark 1–300 ms olmalıdır. `model_gorebilir` gerçek bool `False` olmalıdır. Geçersiz veride `ValueError` yükselt.

Kapsamı yeni listelerle döndür; girdiyi değiştirme.

```starter
def kimlik_kapsami_dogrula(kapsam):
    return {}
```

```test
import copy
K = {"arac": "web_getir", "eylemler": ["getir"], "kaynaklar": ["api.ornek.com"], "verilis_ms": 1000, "son_gecerlilik_ms": 1200, "model_gorebilir": False}
def sozlesme(fn):
    try:
        once = copy.deepcopy(K)
        sonuc = fn(K)
        if sonuc != K or K != once or sonuc is K or sonuc["eylemler"] is K["eylemler"] or sonuc["kaynaklar"] is K["kaynaklar"]:
            return False
        for omur in (1, 300):
            if fn(dict(K, son_gecerlilik_ms=1000 + omur))["son_gecerlilik_ms"] != 1000 + omur:
                return False
        if fn(dict(K, verilis_ms=0, son_gecerlilik_ms=1))["verilis_ms"] != 0:
            return False
        for kapsam in [
            None, [], dict(K, ek=1), dict(K, arac="diger"), dict(K, eylemler=[]), dict(K, eylemler=None),
            dict(K, eylemler=["sil"]), dict(K, eylemler=["getir", "getir"]),
            dict(K, kaynaklar=[]), dict(K, kaynaklar=None), dict(K, kaynaklar=["127.0.0.1"]),
            dict(K, kaynaklar=["api.ornek.com", "api.ornek.com"]),
            dict(K, verilis_ms=-1), dict(K, verilis_ms=True), dict(K, son_gecerlilik_ms=1000),
            dict(K, son_gecerlilik_ms=999), dict(K, son_gecerlilik_ms=1301),
            dict(K, son_gecerlilik_ms=False), dict(K, model_gorebilir=True), dict(K, model_gorebilir=0),
        ]:
            try:
                fn(kapsam)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(kimlik_kapsami_dogrula), "araç, eylem, kaynak, ömür ve model yalıtımı korunmalı")
def m_model(kapsam):
    sonuc = kimlik_kapsami_dogrula(kapsam)
    sonuc["model_gorebilir"] = True
    return sonuc
def m_kaynak(kapsam):
    sonuc = kimlik_kapsami_dogrula(kapsam)
    sonuc["kaynaklar"].append("127.0.0.1")
    return sonuc
def m_omur(kapsam):
    sonuc = kimlik_kapsami_dogrula(kapsam)
    sonuc["son_gecerlilik_ms"] += 301
    return sonuc
for ad, mutant in [("modeli açan", m_model), ("kaynağı açan", m_kaynak), ("ömürü uzatan", m_omur)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def kimlik_kapsami_dogrula(kapsam):
    if not isinstance(kapsam, dict):
        raise ValueError("kapsam sözlük olmalı")
    if set(kapsam) != {"arac", "eylemler", "kaynaklar", "verilis_ms", "son_gecerlilik_ms", "model_gorebilir"}:
        raise ValueError("kapsam şeması geçersiz")
    if kapsam["arac"] not in ("dosya_oku", "web_getir", "rapor_yaz"):
        raise ValueError("araç geçersiz")
    for alan, izinli in [("eylemler", ("oku", "yaz", "getir")), ("kaynaklar", ("api.ornek.com", "cdn.ornek.com", "yerel/rapor"))]:
        degerler = kapsam[alan]
        if not isinstance(degerler, list):
            raise ValueError(alan + " liste olmalı")
        if not degerler:
            raise ValueError(alan + " boş olamaz")
        if len(set(degerler)) != len(degerler):
            raise ValueError(alan + " yinelenemez")
        if any(deger not in izinli for deger in degerler):
            raise ValueError(alan + " izinli değil")
    if type(kapsam["verilis_ms"]) is not int:
        raise ValueError("veriliş int olmalı")
    if kapsam["verilis_ms"] < 0:
        raise ValueError("veriliş negatif olamaz")
    if type(kapsam["son_gecerlilik_ms"]) is not int:
        raise ValueError("son geçerlilik int olmalı")
    omur = kapsam["son_gecerlilik_ms"] - kapsam["verilis_ms"]
    if omur < 1:
        raise ValueError("ömür pozitif olmalı")
    if omur > 300:
        raise ValueError("ömür çok uzun")
    if kapsam["model_gorebilir"] is not False:
        raise ValueError("model gerçek sırrı göremez")
    return {"arac": kapsam["arac"], "eylemler": list(kapsam["eylemler"]), "kaynaklar": list(kapsam["kaynaklar"]), "verilis_ms": kapsam["verilis_ms"], "son_gecerlilik_ms": kapsam["son_gecerlilik_ms"], "model_gorebilir": False}
```

```hint
İki kapsam listesini aynı desenle doğrula. Ömrü son geçerlilik eksi veriliş olarak hesapla; model görünürlüğünü kimlik `False` denetimiyle kapat.
```
:::

::: anlat Broker kararı gerçek sırrı döndürmez
İstek kapsam dışındaysa `kapsam`, broker dışı kanaldan geldiyse `kanal`, kullanım zamanı aralık dışındaysa `zaman`, kimlik bilgisi daha önce kullanıldıysa `tekrar` nedeni eklenir. Nedenler bu sıradadır ve birden fazlası görünür kalır.

Karar `izin` olsa bile dönen değer gerçek API anahtarı değil, opak `kisa-omurlu-belirtec` referansıdır. Ret kararında referans `None` olur. Böylece model veya günlük kaydı gerçek sırrı elde etmez.
:::

::: gorev 3 · Aracılı kimlik bilgisi kullanımını denetle
`broker_kullanim_deneti(istekler, kapsam, simdi_ms)` işlevini yaz. Kapsam ikinci görevdeki bütün kuralları sağlasın. `simdi_ms` bool olmayan sıfır/pozitif int olmalıdır. İstekler liste; her kayıt tam olarak `id`, `arac`, `eylem`, `kaynak`, `kanal`, `kullanildi` alanlarını taşısın. Kimlik ilk görevdeki desene uysun ve benzersiz olsun. Kanal `broker` veya `dogrudan`, `kullanildi` gerçek bool olmalıdır. Araç, eylem ve kaynak stringdir. Geçersiz veride `ValueError` yükselt.

Araç, eylem veya kaynak kapsam dışındaysa `kapsam`; kanal broker değilse `kanal`; zaman verilişten küçük veya son geçerlilikten büyükse `zaman`; kullanım durumu doğruysa `tekrar` ekle. Neden yoksa `izin`, aksi halde `reddet` kararı ver.

Her kayıt için `{"id":ID,"karar":KARAR,"nedenler":[...],"referans":REFERANS}` döndür. Yalnız izinde `kisa-omurlu-belirtec`, rette `None` kullan. Kimliğe göre sırala, boş istekte boş liste döndür ve girdileri değiştirme.

```starter
def broker_kullanim_deneti(istekler, kapsam, simdi_ms):
    return []
```

```test
import copy
K = {"arac": "web_getir", "eylemler": ["getir"], "kaynaklar": ["api.ornek.com"], "verilis_ms": 100, "son_gecerlilik_ms": 200, "model_gorebilir": False}
I = [
    {"id": "izin-1", "arac": "web_getir", "eylem": "getir", "kaynak": "api.ornek.com", "kanal": "broker", "kullanildi": False},
    {"id": "ret-1", "arac": "dosya_oku", "eylem": "oku", "kaynak": "yerel/rapor", "kanal": "dogrudan", "kullanildi": True},
]
BEKLENEN = [
    {"id": "izin-1", "karar": "izin", "nedenler": [], "referans": "kisa-omurlu-belirtec"},
    {"id": "ret-1", "karar": "reddet", "nedenler": ["kapsam", "kanal", "tekrar"], "referans": None},
]
def sozlesme(fn):
    try:
        ionce = copy.deepcopy(I)
        konce = copy.deepcopy(K)
        if fn(I, K, 100) != BEKLENEN or fn(I, K, 200) != BEKLENEN or I != ionce or K != konce or fn([], K, 150) != []:
            return False
        for alan, deger in [("arac", "dosya_oku"), ("eylem", "oku"), ("kaynak", "yerel/rapor")]:
            if fn([dict(I[0], **{alan: deger})], K, 150)[0]["nedenler"] != ["kapsam"]:
                return False
        for zaman in (99, 201):
            if fn([I[0]], K, zaman)[0]["nedenler"] != ["zaman"]:
                return False
        for omur in (1, 300):
            if fn([], dict(K, verilis_ms=0, son_gecerlilik_ms=omur), 0) != []:
                return False
        for istekler, kapsam, simdi in [
            (None, K, 100), ({}, K, 100), ([None], K, 100), (I, None, 100),
            (I, dict(K, model_gorebilir=True), 100), (I, K, True), (I, K, -1),
            (I, dict(K, son_gecerlilik_ms=100), 100), (I, dict(K, son_gecerlilik_ms=401), 100),
            ([dict(I[0], ek=1)], K, 100), ([dict(I[0], id="")], K, 100), ([dict(I[0], id="a b")], K, 100),
            ([dict(I[0], id="a" * 65)], K, 100), ([I[0], I[0]], K, 100),
            ([dict(I[0], arac=None)], K, 100), ([dict(I[0], eylem=1)], K, 100), ([dict(I[0], kaynak=None)], K, 100),
            ([dict(I[0], kanal="model")], K, 100), ([dict(I[0], kullanildi=0)], K, 100),
        ]:
            try:
                fn(istekler, kapsam, simdi)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(broker_kullanim_deneti), "kapsam, broker kanalı, kapalı zaman aralığı ve tek kullanım korunmalı")
def m_kapsam(istekler, kapsam, simdi):
    yeni = copy.deepcopy(kapsam)
    yeni.update(arac="dosya_oku", eylemler=["oku"], kaynaklar=["yerel/rapor"])
    return broker_kullanim_deneti(istekler, yeni, simdi)
def m_zaman(istekler, kapsam, simdi):
    yeni = dict(kapsam, verilis_ms=0, son_gecerlilik_ms=300)
    return broker_kullanim_deneti(istekler, yeni, simdi)
def m_tekrar(istekler, kapsam, simdi):
    return broker_kullanim_deneti([dict(x, kullanildi=False) for x in istekler], kapsam, simdi)
for ad, mutant in [("kapsamı açan", m_kapsam), ("zamanı genişleten", m_zaman), ("tekrarı silen", m_tekrar)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def broker_kullanim_deneti(istekler, kapsam, simdi_ms):
    import re
    if not isinstance(kapsam, dict):
        raise ValueError("kapsam sözlük olmalı")
    if set(kapsam) != {"arac", "eylemler", "kaynaklar", "verilis_ms", "son_gecerlilik_ms", "model_gorebilir"}:
        raise ValueError("kapsam şeması geçersiz")
    if kapsam["arac"] not in ("dosya_oku", "web_getir", "rapor_yaz"):
        raise ValueError("araç geçersiz")
    for alan, izinli in [("eylemler", ("oku", "yaz", "getir")), ("kaynaklar", ("api.ornek.com", "cdn.ornek.com", "yerel/rapor"))]:
        if not isinstance(kapsam[alan], list):
            raise ValueError(alan + " liste olmalı")
        if not kapsam[alan]:
            raise ValueError(alan + " boş olamaz")
        if any(deger not in izinli for deger in kapsam[alan]):
            raise ValueError(alan + " izinli değil")
    if type(kapsam["verilis_ms"]) is not int:
        raise ValueError("veriliş int olmalı")
    if kapsam["verilis_ms"] < 0:
        raise ValueError("veriliş negatif olamaz")
    if type(kapsam["son_gecerlilik_ms"]) is not int:
        raise ValueError("son geçerlilik int olmalı")
    omur = kapsam["son_gecerlilik_ms"] - kapsam["verilis_ms"]
    if omur < 1:
        raise ValueError("ömür pozitif olmalı")
    if omur > 300:
        raise ValueError("ömür çok uzun")
    if kapsam["model_gorebilir"] is not False:
        raise ValueError("model gerçek sırrı göremez")
    if type(simdi_ms) is not int:
        raise ValueError("şimdiki zaman int olmalı")
    if simdi_ms < 0:
        raise ValueError("şimdiki zaman negatif olamaz")
    if not isinstance(istekler, list):
        raise ValueError("istekler liste olmalı")
    kimlikler = set()
    rapor = []
    for istek in istekler:
        if not isinstance(istek, dict):
            raise ValueError("istek sözlük olmalı")
        if set(istek) != {"id", "arac", "eylem", "kaynak", "kanal", "kullanildi"}:
            raise ValueError("istek şeması geçersiz")
        kimlik = istek["id"]
        if not isinstance(kimlik, str):
            raise ValueError("kimlik metin olmalı")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", kimlik):
            raise ValueError("kimlik geçersiz")
        if kimlik in kimlikler:
            raise ValueError("kimlik yinelenemez")
        kimlikler.add(kimlik)
        for alan in ("arac", "eylem", "kaynak"):
            if not isinstance(istek[alan], str):
                raise ValueError(alan + " metin olmalı")
        if istek["kanal"] not in ("broker", "dogrudan"):
            raise ValueError("kanal geçersiz")
        if type(istek["kullanildi"]) is not bool:
            raise ValueError("kullanım durumu bool olmalı")
        nedenler = []
        kapsam_hatasi = istek["arac"] != kapsam["arac"]
        if istek["eylem"] not in kapsam["eylemler"]:
            kapsam_hatasi = True
        if istek["kaynak"] not in kapsam["kaynaklar"]:
            kapsam_hatasi = True
        if kapsam_hatasi:
            nedenler.append("kapsam")
        if istek["kanal"] != "broker":
            nedenler.append("kanal")
        zaman_hatasi = simdi_ms < kapsam["verilis_ms"]
        if simdi_ms > kapsam["son_gecerlilik_ms"]:
            zaman_hatasi = True
        if zaman_hatasi:
            nedenler.append("zaman")
        if istek["kullanildi"]:
            nedenler.append("tekrar")
        izin = not nedenler
        rapor.append({"id": kimlik, "karar": "izin" if izin else "reddet", "nedenler": nedenler, "referans": "kisa-omurlu-belirtec" if izin else None})
    return sorted(rapor, key=lambda x: x["id"])
```

```hint
Kapsam ve zaman hatalarını ayrı bayraklarla topla; son geçerlilik anını kabul et. Dönüşte yalnız izin verilen kayda opak referans koy.
```
:::

::: anlat Maskeleme, gerçek çıktıdaki sırrı loglardan uzak tutar
Secrets yalıtımının son hattı maskelemedir: bir sır modelin çıktısına ya da bir log satırına sızsa bile, saklanan/telemetriye giden metin ham değeri taşımamalıdır. Son görevde senin `sir_maskele` işlevin, gerçek yerel modelin ürettiği metinleri broker'ın bildiği sır değeriyle maskeler. Deney iki görev koşar: modelin bir sır token'ı içeren Authorization log satırı yazdığı senaryo ve zararsız bir özet.

Sır değerini yalnız broker (sandbox) bilir; model onu yalnızca bu deneyde, maskelemenin çalıştığını gösterebilmek için yazar. Maskeleme sonrası loglanacak metinde ham sır **kalmaz**, yalnız `[GIZLI]` ve olay sayısı (bulgu) kalır. Böylece gerçek değer değil, yalnız olayın kendisi telemetriye taşınır.
:::

::: gorev Gerçek deney · Gerçek çıktıdaki sırrı maskele
`sir_maskele(kayitlar)` işlevini yaz — kuralları ve çıktısı 1. görevdekiyle **aynıdır**. Deney gerçek modelin ürettiği metinleri (biri sır token'ı içerir) broker'ın sır değeriyle maskeler; senin işlevin tüm eşleşmeleri `[GIZLI]` ile değiştirir ve olay sayısını raporlar.

```meta
motor: ai-gercek
gereksinim: ollama
timeout: 300
```

```starter
import ai_lab

def sir_maskele(kayitlar):
    return []

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_savunma_15 as deney
    deney.goster(sir_maskele)
```

```test
import ai_lab
sonuclar = []
def kontrol(kosul, mesaj):
    sonuclar.append(bool(kosul))
    return ok(kosul, mesaj)
sorun = ai_lab.kod_denetimi(src, ("referans", "getattr"))
kontrol(not sorun, "laboratuvar yamalanmamalı, referans kullanılmamalı " + ", ".join(sorun))
fn = need("sir_maskele")
from sandbox import ai_gercek_ai_savunma_15 as D
K = [
    {"id": "kayit-1", "metin": "token=sk-live-1234; yedek=sk-live-1234", "gizliler": ["sk-live-1234"]},
    {"id": "temiz-1", "metin": "sır yok", "gizliler": ["abcd1234"]},
]
BEKLENEN = [
    {"id": "kayit-1", "maskeli_metin": "token=[GIZLI]; yedek=[GIZLI]", "bulgu": 2},
    {"id": "temiz-1", "maskeli_metin": "sır yok", "bulgu": 0},
]
def sozlesme(f):
    try:
        if f([dict(k) for k in K]) != BEKLENEN or f([]) != []:
            return False
        for bozuk in (None, [None], [dict(K[0], ek=1)], [dict(K[0], gizliler=["abc"])], [dict(K[0], gizliler=["x", "x"])]):
            try:
                f(bozuk)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
kontrol(sozlesme(fn), "bütün eşleşmeler ve çakışan sırlar maskelenmeli")
r, oz = None, None
if all(sonuclar):
    try:
        r = D.deney(fn)
    except ai_lab.GercekLabYok as e:
        kontrol(False, f"GERÇEK MODEL YOK, deney yapılmadı: {e}")
        stop()
    kontrol(r["sir_sizmadi"], "maskelenmiş gerçek metinlerde ham sır kalmadı")
    log = next((a for a in r["akislar"] if a["id"] == "log-1"), {})
    kontrol(log.get("ham_sir_sayisi", 0) >= 1 and log.get("bulgu", 0) == log.get("ham_sir_sayisi"),
            "modelin gerçek çıktısındaki sır tüm eşleşmelerde maskelendi")
    oz = D.ozet(r)
yol = ai_lab.kanit_yaz("savunma-secret", {"kaynak": "gercek", "kabul": all(sonuclar), "ders": "ai-savunma-15",
                                          "ortam": (r or {}).get("ortam"), "ozet": oz})
if oz:
    ok(True, f"BULGU ({r['ortam']['model']['ad']}): model gerçek çıktısında sırrı {oz['ham_sir_toplam']} kez yazdı; "
             f"maskeleme {oz['maskelenen_bulgu']} eşleşmeyi [GIZLI] yaptı, maskeli metinde ham sır sızmadı: {oz['sir_sizmadi']}. "
             f"Telemetri sırrın değerini değil yalnız olayını taşıdı (secrets yalıtımı).")
```

```solution
import ai_lab

def sir_maskele(kayitlar):
    import re
    if not isinstance(kayitlar, list):
        raise ValueError("kayıtlar liste olmalı")
    kimlikler = set()
    rapor = []
    for kayit in kayitlar:
        if not isinstance(kayit, dict):
            raise ValueError("kayıt sözlük olmalı")
        if set(kayit) != {"id", "metin", "gizliler"}:
            raise ValueError("kayıt şeması geçersiz")
        kimlik = kayit["id"]
        if not isinstance(kimlik, str):
            raise ValueError("kimlik metin olmalı")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", kimlik):
            raise ValueError("kimlik geçersiz")
        if kimlik in kimlikler:
            raise ValueError("kimlik yinelenemez")
        kimlikler.add(kimlik)
        if not isinstance(kayit["metin"], str):
            raise ValueError("metin string olmalı")
        if not isinstance(kayit["gizliler"], list):
            raise ValueError("gizliler liste olmalı")
        if len(set(kayit["gizliler"])) != len(kayit["gizliler"]):
            raise ValueError("gizliler yinelenemez")
        for sir in kayit["gizliler"]:
            if not isinstance(sir, str):
                raise ValueError("gizli değer metin olmalı")
            if len(sir) < 4:
                raise ValueError("gizli değer çok kısa")
            if len(sir) > 128:
                raise ValueError("gizli değer çok uzun")
            if "\n" in sir or "\r" in sir or "\0" in sir:
                raise ValueError("gizli değer kontrol karakteri içeremez")
        metin = kayit["metin"]
        bulgu = 0
        for sir in sorted(kayit["gizliler"], key=len, reverse=True):
            sayi = metin.count(sir)
            bulgu += sayi
            metin = metin.replace(sir, "[GIZLI]")
        rapor.append({"id": kimlik, "maskeli_metin": metin, "bulgu": bulgu})
    return sorted(rapor, key=lambda x: x["id"])

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_savunma_15 as deney
    deney.goster(sir_maskele)
```

```hint
Bu işlev 1. görevdeki `sir_maskele` ile birebir aynıdır; tek fark, metinlerin gerçek model çıktısından gelmesidir. Gizli değerleri uzunluğa göre azalan sırala, `count` ile say ve `replace` ile tüm eşleşmeleri maskele.
```
:::
