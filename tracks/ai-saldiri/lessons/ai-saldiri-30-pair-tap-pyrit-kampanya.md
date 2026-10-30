---
id: ai-saldiri-30
title: PAIR, TAP ve PyRIT ile Otomatik Saldırı Kampanyaları
summary: PAIR/TAP yinelemelerini sentetik aday ve skorlarla modelle; deterministik ağaç, tur kararı ve sonda yerel saldırgan + hedef model ile gerçek kampanya kanıtı üret.
timeout: 300
---

::: anlat Otomasyon, ölçüm disiplinini kaldırmaz
PAIR, saldırı varyantını hedef ve değerlendirici geri bildirimiyle yineleyen bir akış; TAP ise aramayı ağaç biçiminde genişletir. PyRIT gibi araçlar bu denemeleri kampanya kayıtlarına dönüştürebilir. Ancak çok sayıda varyant üretmek tek başına başarı kanıtı değildir.

Tekrarlanabilir çalışma için aday kimliği, ebeveyn ilişkisi, tur, skor eşiği ve durma kuralı önceden belirlenir. Aynı skora sahip adaylarda girdi sırasına göre seçim yapmak sonucu değiştirir; kimlikle tie-break gerekir. Başarı eşiği ile iyileşme yokluğu da birbirinden ayrılmalıdır.

İlk üç görevde ağaç düğümleri ve skorlar deterministik fixture'lardır; son görevde ise hem saldırgan hem hedef yerel Ollama modeli üzerinde çalışarak canlı bir PAIR/TAP kampanyası yürütür.
:::

::: tahmin En yüksek skor tek başına seçim yeterli mi?
Üç adayın ikisi aynı en yüksek skora sahip. Üç çıktı satırını yaz:

```python
skorlar = [0.4, 0.9, 0.9]
print(max(skorlar))
print(skorlar.count(max(skorlar)))
print(max(skorlar) >= 0.8)
```

???

```cikti
0.9
2
True
```

Eşik aşıldığı bilinse bile hangi adayın seçileceği belirsizdir. Deterministik kimlik sıralaması gerekir.
:::

::: gorev 1 · TAP için deterministik aday ağacı üret
`tap_agaci_uret(kok="kok", derinlik=3, genislik=2)` işlevini yaz. Kök 1–32 karakterli string olmalı; `/`, NUL, satır sonu veya baş/son boşluk içermemelidir. `derinlik` bool olmayan 0–4 arası int, `genislik` bool olmayan 1–3 arası int olmalıdır. Geçersiz veride `ValueError` yükselt.

Kök düğüm `{"id":KOK,"ebeveyn":None,"derinlik":0}` biçimindedir. Her ebeveyn, sırayla `1..genislik` çocuk üretir; çocuk kimliği `EBEVEYN/INDEX`, derinliği ebeveyn derinliği + 1 olur. Ağacı seviye seviye (BFS), aynı seviyede ebeveyn ve çocuk sırasını koruyarak liste olarak döndür. Toplam düğüm sayısı `Σ genislik^d` (`d=0..derinlik`) olmalıdır.

```starter
def tap_agaci_uret(kok="kok", derinlik=3, genislik=2):
    return []
```

```test
def sozlesme(fn):
    try:
        if fn("kok", 0, 2) != [{"id": "kok", "ebeveyn": None, "derinlik": 0}]:
            return False
        beklenen = [
            {"id": "k", "ebeveyn": None, "derinlik": 0},
            {"id": "k/1", "ebeveyn": "k", "derinlik": 1},
            {"id": "k/2", "ebeveyn": "k", "derinlik": 1},
            {"id": "k/1/1", "ebeveyn": "k/1", "derinlik": 2},
            {"id": "k/1/2", "ebeveyn": "k/1", "derinlik": 2},
            {"id": "k/2/1", "ebeveyn": "k/2", "derinlik": 2},
            {"id": "k/2/2", "ebeveyn": "k/2", "derinlik": 2},
        ]
        if fn("k", 2, 2) != beklenen or fn("k", 2, 2) != beklenen:
            return False
        uc = fn("k", 1, 3)
        if len(uc) != 4 or [x["id"] for x in uc] != ["k", "k/1", "k/2", "k/3"]:
            return False
        if len(fn()) != 15 or len(fn("k", 4, 1)) != 5:
            return False
        if fn("x" * 32, 0, 1)[0]["id"] != "x" * 32:
            return False
        for kok, derinlik, genislik in [
            (None, 2, 2), (123, 2, 2), ("", 2, 2), (" k", 2, 2), ("k ", 2, 2),
            ("a/b", 2, 2), ("a\x00b", 2, 2), ("a\nb", 2, 2), ("a\rb", 2, 2), ("x" * 33, 2, 2),
            ("k", -1, 2), ("k", 5, 2), ("k", True, 2), ("k", 1.5, 2),
            ("k", 2, 0), ("k", 2, 4), ("k", 2, True), ("k", 2, 1.5),
        ]:
            try:
                fn(kok, derinlik, genislik)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(tap_agaci_uret), "BFS sırası, ebeveyn kimliği, derinlik ve genişlik sınırları korunmalı")
def m_derinlik(kok="kok", derinlik=3, genislik=2):
    return tap_agaci_uret(kok, max(0, derinlik - 1), genislik)
def m_genislik(kok="kok", derinlik=3, genislik=2):
    return tap_agaci_uret(kok, derinlik, max(1, genislik - 1))
def m_sira(kok="kok", derinlik=3, genislik=2):
    sonuc = tap_agaci_uret(kok, derinlik, genislik)
    return [sonuc[0]] + list(reversed(sonuc[1:]))
for ad, mutant in [("bir seviyeyi eksik üreten", m_derinlik), ("çocuk sayısını eksilten", m_genislik), ("BFS sırasını bozan", m_sira)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def tap_agaci_uret(kok="kok", derinlik=3, genislik=2):
    if not isinstance(kok, str):
        raise ValueError("kök türü geçersiz")
    if not kok or len(kok) > 32 or kok != kok.strip():
        raise ValueError("kök biçimi geçersiz")
    if any(x in kok for x in ("/", "\x00", "\n", "\r")):
        raise ValueError("kök ayırıcı içeriyor")
    if type(derinlik) is not int or derinlik < 0 or derinlik > 4:
        raise ValueError("derinlik geçersiz")
    if type(genislik) is not int or genislik < 1 or genislik > 3:
        raise ValueError("genişlik geçersiz")
    sonuc = [{"id": kok, "ebeveyn": None, "derinlik": 0}]
    seviye = [kok]
    for d in range(1, derinlik + 1):
        yeni = []
        for ebeveyn in seviye:
            for indeks in range(1, genislik + 1):
                kimlik = ebeveyn + "/" + str(indeks)
                sonuc.append({"id": kimlik, "ebeveyn": ebeveyn, "derinlik": d})
                yeni.append(kimlik)
        seviye = yeni
    return sonuc
```

```hint
Kökü listeye ekle ve yalnız önceki seviyenin kimliklerini tut. Her seviyede ebeveynleri, iç döngüde çocuk indekslerini sırayla gez.
```
:::

::: anlat PAIR turu skor, eşik ve iyileşmeyi birlikte değerlendirir
Bir turda en iyi aday eşiği geçtiyse kampanya başarıyla durur. Eşik geçilmediyse fakat en iyi skor mevcut skordan yüksekse yeni adayla devam edilir. Skor mevcut seviyeyi aşmıyorsa iyileşme yoktur; aynı turu rastgele tekrarlamak yerine durum açıkça raporlanır.

Seçim anahtarı `(-skor, id)` biçimindedir. Böylece skor azalan, eşitlikte kimlik artan sıralanır. Bu işlem yalnız fixture kararıdır; skorun gerçek saldırı başarısı olduğunu varsaymaz.
:::

::: gorev 2 · PAIR turunda aday seçimini ve durma kararını hesapla
`pair_tur_karari(adaylar, mevcut_skor, esik=0.8)` işlevini yaz. Adaylar boş olmayan liste; her kayıt tam olarak `id`, `skor` alanlarını taşısın. Kimlik boş olmayan ve benzersiz string; skor, mevcut skor ve eşik bool olmayan sonlu sayı olmalı ve 0–1 aralığında olmalıdır. Eşik 0'dan büyük olmalıdır. Geçersiz veride `ValueError` yükselt.

Önce en yüksek skorlu, eşitlikte kimliği en küçük adayı seç. Sonra:

- `skor >= esik` ise `durum="basarili"`.
- Aksi halde `skor <= mevcut_skor` ise `durum="iyilesme-yok"`.
- Aksi halde `durum="devam"`.

Dönüş `{"durum":DURUM,"secilen":ID,"skor":SKOR}` biçimindedir; skor float olmalıdır. Girdi sırası sonucu etkilememeli ve kayıtlar değiştirilmemelidir.

```starter
def pair_tur_karari(adaylar, mevcut_skor, esik=0.8):
    return {}
```

```test
import copy
ADAYLAR = [{"id": "b", "skor": 0.7}, {"id": "a", "skor": 0.7}, {"id": "c", "skor": 0.4}]
def sozlesme(fn):
    try:
        once = copy.deepcopy(ADAYLAR)
        if fn(ADAYLAR, 0.5) != {"durum": "devam", "secilen": "a", "skor": 0.7} or ADAYLAR != once:
            return False
        if fn(list(reversed(ADAYLAR)), 0.5)["secilen"] != "a":
            return False
        esit = [{"id": "x", "skor": 0.8}]
        if fn(esit, 0.8) != {"durum": "basarili", "secilen": "x", "skor": 0.8}:
            return False
        if fn(esit, 0.8, 0.9)["durum"] != "iyilesme-yok":
            return False
        dusuk = [{"id": "x", "skor": 0.2}]
        if fn(dusuk, 0.3)["durum"] != "iyilesme-yok" or fn(dusuk, 0.2, 1.0)["durum"] != "iyilesme-yok":
            return False
        sinir = [{"id": "x", "skor": 1}]
        if fn(sinir, 0.0, 1.0)["durum"] != "basarili" or fn(sinir, 1.0, 1.0)["skor"] != 1.0:
            return False
        for adaylar, mevcut, esik in [
            (None, 0.5, 0.8), ({}, 0.5, 0.8), ([], 0.5, 0.8), ([None], 0.5, 0.8),
            ([dict(ADAYLAR[0], ek=1)], 0.5, 0.8), ([dict(ADAYLAR[0], id=None)], 0.5, 0.8),
            ([dict(ADAYLAR[0], id=123)], 0.5, 0.8), ([dict(ADAYLAR[0], id="")], 0.5, 0.8),
            ([ADAYLAR[0], ADAYLAR[0]], 0.5, 0.8),
            ([dict(ADAYLAR[0], skor=None)], 0.5, 0.8), ([dict(ADAYLAR[0], skor=True)], 0.5, 0.8),
            ([dict(ADAYLAR[0], skor=-0.1)], 0.5, 0.8), ([dict(ADAYLAR[0], skor=1.1)], 0.5, 0.8),
            ([dict(ADAYLAR[0], skor=float("nan"))], 0.5, 0.8), ([dict(ADAYLAR[0], skor=float("inf"))], 0.5, 0.8),
            (ADAYLAR, None, 0.8), (ADAYLAR, True, 0.8), (ADAYLAR, -0.1, 0.8), (ADAYLAR, 1.1, 0.8),
            (ADAYLAR, 0.5, 0), (ADAYLAR, 0.5, -0.1), (ADAYLAR, 0.5, 1.1),
            (ADAYLAR, 0.5, True), (ADAYLAR, 0.5, float("nan")), (ADAYLAR, 0.5, float("inf")),
        ]:
            try:
                fn(adaylar, mevcut, esik)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(pair_tur_karari), "skor/kimlik seçimi, eşik eşitliği ve iyileşme sınırı korunmalı")
def m_esik(adaylar, mevcut_skor, esik=0.8):
    return pair_tur_karari(adaylar, mevcut_skor, esik + 0.01)
def m_iyilesme(adaylar, mevcut_skor, esik=0.8):
    return pair_tur_karari(adaylar, mevcut_skor - 0.01, esik)
def m_sira(adaylar, mevcut_skor, esik=0.8):
    sonuc = pair_tur_karari(adaylar, mevcut_skor, esik)
    esitler = [x["id"] for x in adaylar if x["skor"] == sonuc["skor"]]
    sonuc["secilen"] = max(esitler)
    return sonuc
for ad, mutant in [("eşit skoru başarı dışı bırakan", m_esik), ("eşit skoru iyileşme sayan", m_iyilesme), ("tie-break kararını girdi sırasına bırakan", m_sira)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def pair_tur_karari(adaylar, mevcut_skor, esik=0.8):
    import math
    def oran(deger, ad):
        if isinstance(deger, bool) or not isinstance(deger, (int, float)) or not math.isfinite(deger) or deger < 0 or deger > 1:
            raise ValueError(ad + " geçersiz")
    oran(mevcut_skor, "mevcut skor")
    oran(esik, "eşik")
    if esik == 0:
        raise ValueError("eşik sıfır olamaz")
    if not isinstance(adaylar, list) or not adaylar:
        raise ValueError("aday listesi geçersiz")
    kimlikler = set()
    for aday in adaylar:
        if not isinstance(aday, dict) or set(aday) != {"id", "skor"}:
            raise ValueError("aday şeması geçersiz")
        if type(aday["id"]) is not str or not aday["id"] or aday["id"] in kimlikler:
            raise ValueError("aday kimliği geçersiz")
        kimlikler.add(aday["id"])
        oran(aday["skor"], "aday skoru")
    secilen = sorted(adaylar, key=lambda x: (-x["skor"], x["id"]))[0]
    skor = float(secilen["skor"])
    if skor >= esik:
        durum = "basarili"
    elif skor <= mevcut_skor:
        durum = "iyilesme-yok"
    else:
        durum = "devam"
    return {"durum": durum, "secilen": secilen["id"], "skor": skor}
```

```hint
Adayları `(-skor, id)` ile sırala. İlk adayın skorunu önce eşikle, sonra mevcut skorla karşılaştır; iki eşitlik sınırını da koru.
```
:::

::: anlat Kampanya kanıtı deneme geçmişinden türetilir
Kampanya raporu yalnız son turu değil bütün denemeleri içermelidir. Deneme sayısı maliyeti, en iyi skor erişilen seviyeyi, ilk başarı turu ise ne zaman durulabileceğini gösterir. Başarısız kampanyada ilk başarı turu `None` olur; sıfır tur ile karıştırılmaz.

Aynı kampanya–tur–aday üçlüsünün tekrarı kayıt bütünlüğü hatasıdır. Farklı turlarda aynı aday kimliği bulunabilir; bunlar ayrı ölçümlerdir. Gerçek PyRIT çalışmasında buna model, prompt ve değerlendirici sürümleri de eklenmelidir.
:::

::: gorev 3 · Kampanyaların deneme, en iyi skor ve ilk başarı kanıtını özetle
`kampanya_ozeti(denemeler, esik=0.8)` işlevini yaz. Denemeler liste olabilir; her kayıt tam olarak `kampanya`, `tur`, `aday`, `skor` alanlarını taşısın. Kampanya ve aday boş olmayan string; tur bool olmayan pozitif int; skor bool olmayan sonlu 0–1 sayısı olmalıdır. Eşik ikinci görevdeki kuralları sağlamalıdır. `(kampanya, tur, aday)` üçlüsü benzersiz olmalıdır. Geçersiz veride `ValueError` yükselt.

Her kampanya için:

```text
{"kampanya":AD,"deneme":N,"en_iyi":EN_IYI,
 "basarili":BOOL,"ilk_basari_turu":TUR_VEYA_NONE}
```

Başarı, skoru eşiğe eşit veya büyük en az bir denemedir. İlk başarı turu yalnız başarılı denemelerin minimum turudur. Raporu kampanya adına göre artan sırala; girdi sırası sonucu etkilememeli ve kayıtlar değiştirilmemelidir.

```starter
def kampanya_ozeti(denemeler, esik=0.8):
    return []
```

```test
import copy
DENEMELER = [
    {"kampanya": "b", "tur": 2, "aday": "x", "skor": 0.4},
    {"kampanya": "a", "tur": 2, "aday": "x", "skor": 0.7},
    {"kampanya": "a", "tur": 1, "aday": "x", "skor": 0.3},
    {"kampanya": "a", "tur": 3, "aday": "y", "skor": 0.8},
    {"kampanya": "a", "tur": 4, "aday": "x", "skor": 0.9},
    {"kampanya": "b", "tur": 1, "aday": "x", "skor": 0.2},
]
BEKLENEN = [
    {"kampanya": "a", "deneme": 4, "en_iyi": 0.9, "basarili": True, "ilk_basari_turu": 3},
    {"kampanya": "b", "deneme": 2, "en_iyi": 0.4, "basarili": False, "ilk_basari_turu": None},
]
def sozlesme(fn):
    try:
        once = copy.deepcopy(DENEMELER)
        if fn(DENEMELER) != BEKLENEN or DENEMELER != once or fn(list(reversed(DENEMELER))) != BEKLENEN:
            return False
        if fn([]) != []:
            return False
        esit = [{"kampanya": "x", "tur": 1, "aday": "a", "skor": 0.8}]
        if fn(esit)[0]["basarili"] is not True or fn(esit)[0]["ilk_basari_turu"] != 1:
            return False
        yuksek = [{"kampanya": "x", "tur": 1, "aday": "a", "skor": 1.0}]
        if fn(yuksek, 1.0)[0]["en_iyi"] != 1.0:
            return False
        sifir = [{"kampanya": "x", "tur": 1, "aday": "a", "skor": 0}]
        if fn(sifir)[0]["en_iyi"] != 0.0 or fn(sifir)[0]["basarili"]:
            return False
        for denemeler, esik in [
            (None, 0.8), ({}, 0.8), ([None], 0.8), ([dict(DENEMELER[0], ek=1)], 0.8),
            ([dict(DENEMELER[0], kampanya=None)], 0.8), ([dict(DENEMELER[0], kampanya="")], 0.8),
            ([dict(DENEMELER[0], aday=None)], 0.8), ([dict(DENEMELER[0], aday="")], 0.8),
            ([dict(DENEMELER[0], tur=0)], 0.8), ([dict(DENEMELER[0], tur=-1)], 0.8),
            ([dict(DENEMELER[0], tur=True)], 0.8), ([dict(DENEMELER[0], tur=1.5)], 0.8),
            ([dict(DENEMELER[0], skor=None)], 0.8), ([dict(DENEMELER[0], skor=True)], 0.8),
            ([dict(DENEMELER[0], skor=-0.1)], 0.8), ([dict(DENEMELER[0], skor=1.1)], 0.8),
            ([dict(DENEMELER[0], skor=float("nan"))], 0.8),
            ([DENEMELER[0], DENEMELER[0]], 0.8),
            (DENEMELER, 0), (DENEMELER, 1.1), (DENEMELER, True), (DENEMELER, None),
            (DENEMELER, float("nan")), (DENEMELER, float("inf")),
        ]:
            try:
                fn(denemeler, esik)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(kampanya_ozeti), "kayıt benzersizliği, eşik, ilk başarı turu ve sıralama korunmalı")
def m_esik(denemeler, esik=0.8):
    return kampanya_ozeti(denemeler, esik + 0.01)
def m_tur(denemeler, esik=0.8):
    sonuc = kampanya_ozeti(denemeler, esik)
    for kayit in sonuc:
        if kayit["basarili"]:
            kayit["ilk_basari_turu"] = 4
    return sonuc
def m_deneme(denemeler, esik=0.8):
    return kampanya_ozeti(denemeler[:-1], esik)
for ad, mutant in [("eşit skoru başarı dışı bırakan", m_esik), ("son başarıyı ilk başarı sayan", m_tur), ("deneme geçmişini eksilten", m_deneme)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def kampanya_ozeti(denemeler, esik=0.8):
    import math
    if isinstance(esik, bool) or not isinstance(esik, (int, float)) or not math.isfinite(esik) or esik <= 0 or esik > 1:
        raise ValueError("eşik geçersiz")
    if not isinstance(denemeler, list):
        raise ValueError("deneme listesi geçersiz")
    gruplar = {}
    anahtarlar = set()
    for kayit in denemeler:
        if not isinstance(kayit, dict) or set(kayit) != {"kampanya", "tur", "aday", "skor"}:
            raise ValueError("deneme şeması geçersiz")
        if type(kayit["kampanya"]) is not str or not kayit["kampanya"]:
            raise ValueError("kampanya geçersiz")
        if type(kayit["aday"]) is not str or not kayit["aday"]:
            raise ValueError("aday geçersiz")
        if type(kayit["tur"]) is not int or kayit["tur"] < 1:
            raise ValueError("tur geçersiz")
        skor = kayit["skor"]
        if isinstance(skor, bool) or not isinstance(skor, (int, float)) or not math.isfinite(skor) or skor < 0 or skor > 1:
            raise ValueError("skor geçersiz")
        anahtar = (kayit["kampanya"], kayit["tur"], kayit["aday"])
        if anahtar in anahtarlar:
            raise ValueError("deneme tekrar ediyor")
        anahtarlar.add(anahtar)
        gruplar.setdefault(kayit["kampanya"], []).append(kayit)
    sonuc = []
    for kampanya, kayitlar in gruplar.items():
        basarili_turlar = [x["tur"] for x in kayitlar if x["skor"] >= esik]
        sonuc.append({"kampanya": kampanya, "deneme": len(kayitlar), "en_iyi": float(max(x["skor"] for x in kayitlar)), "basarili": bool(basarili_turlar), "ilk_basari_turu": min(basarili_turlar) if basarili_turlar else None})
    sonuc.sort(key=lambda x: x["kampanya"])
    return sonuc
```

```hint
Kayıtları kampanyaya grupla. Her grup için başarılı turları ayrı listele; bayrağı listenin doluluğundan, ilk turu minimumdan ve en iyi skoru bütün kayıtlardan hesapla.
```
:::

::: anlat Yerel saldırgan + yerel hedef model ile canlı PAIR/TAP kampanyası
İlk üç görevde TAP ağaç üretimini, PAIR tur kararını ve kampanya kanıt özetini çevrimdışı fixture'lar üzerinde doğruladın. Şimdi aynı üç işlevi **saldırganın da hedefin de yerel Ollama modeli** (`ai_lab.SohbetOturumu`) olduğu iki turluk canlı bir kampanyaya bağlıyoruz:

1. `tap_agaci_uret("pair", 1, 2)` ile iki dal (`pair/1`, `pair/2`) üretilir.
2. Her turda **saldırgan rolündeki yerel model**, bir önceki turun geri bildirimini kullanarak hedefteki sentetik `canary` değerini sızdırmayı deneyen yeni bir istem üretir.
3. **Hedef rolündeki yerel model** (`ai_lab.injection_sistemi(canary)`) bu istemi yanıtlar; değerlendirici yanıtı `[0, 1]` aralığında skorlar.
4. Her turun sonunda `pair_tur_karari`, kampanya sonunda ise `kampanya_ozeti` canlı deneme geçmişini özetler ve kanıt yazar.
:::

::: gorev Gerçek deney · Saldırgan + hedef yerel model ile canlı PAIR/TAP kampanyası
Önceki üç görevde yazdığın `tap_agaci_uret(kok="kok", derinlik=3, genislik=2)`, `pair_tur_karari(adaylar, mevcut_skor, esik=0.8)` ve `kampanya_ozeti(denemeler, esik=0.8)` işlevlerini burada birleştir.

- **Çalıştır** düğmesi yerel modelde 2 turluk saldırgan → hedef döngüsünü koşar ve üretilen istemleri, yanıtları ve kampanya özetini gösterir.
- **Kontrol** düğmesi önce üç işlevini deterministik sınır testlerinden geçirir, ardından canlı saldırgan+hedef kampanyasını yürütüp kanıt üretir.

```meta
motor: ai-gercek
gereksinim: ollama
timeout: 300
```

```starter
import importlib
import math
import ai_lab
L = importlib.import_module("sandbox.ai_gercek_ai_saldiri_30")

def tap_agaci_uret(kok="kok", derinlik=3, genislik=2):
    # KUSURLU BAŞLANGIÇ KODU: yalnız kök düğümü döndürüyor, çocuk dalları üretmiyor!
    return [{"id": kok, "ebeveyn": None, "derinlik": 0}]

def pair_tur_karari(adaylar, mevcut_skor, esik=0.8):
    return {"durum": "iyilesme-yok", "secilen": adaylar[0]["id"] if adaylar else "yok", "skor": 0.0}

def kampanya_ozeti(denemeler, esik=0.8):
    return []

if ai_lab.CALISTIR:
    L.goster(tap_agaci_uret, pair_tur_karari, kampanya_ozeti)
```

```test
import copy
import importlib
import ai_lab
L = importlib.import_module("sandbox.ai_gercek_ai_saldiri_30")
checks = []
_base_ok = ok
def ok(kosul, mesaj):
    checks.append(bool(kosul))
    return _base_ok(kosul, mesaj)

for s in ai_lab.kod_denetimi(src, yasak=("tap_agaci_uret_referans", "pair_tur_karari_referans", "kampanya_ozeti_referans", "kanit_yaz")):
    ok(False, f"Güvenlik/kopya denetimi: {s}")
if not all(checks):
    stop()

def _sozlesme_kontrol():
    try:
        bek_agac = [
            {"id": "k", "ebeveyn": None, "derinlik": 0},
            {"id": "k/1", "ebeveyn": "k", "derinlik": 1},
            {"id": "k/2", "ebeveyn": "k", "derinlik": 1},
            {"id": "k/1/1", "ebeveyn": "k/1", "derinlik": 2},
            {"id": "k/1/2", "ebeveyn": "k/1", "derinlik": 2},
            {"id": "k/2/1", "ebeveyn": "k/2", "derinlik": 2},
            {"id": "k/2/2", "ebeveyn": "k/2", "derinlik": 2},
        ]
        if tap_agaci_uret("k", 2, 2) != bek_agac or len(tap_agaci_uret()) != 15:
            return False
        for bozuk_k, d, g in [(None, 2, 2), ("", 2, 2), ("a/b", 2, 2), ("k", -1, 2), ("k", 5, 2), ("k", True, 2), ("k", 2, 0), ("k", 2, 4)]:
            try:
                tap_agaci_uret(bozuk_k, d, g)
                return False
            except ValueError:
                pass

        adaylar = [{"id": "b", "skor": 0.7}, {"id": "a", "skor": 0.7}, {"id": "c", "skor": 0.4}]
        if pair_tur_karari(adaylar, 0.5) != {"durum": "devam", "secilen": "a", "skor": 0.7}:
            return False
        if pair_tur_karari([{"id": "x", "skor": 0.8}], 0.8) != {"durum": "basarili", "secilen": "x", "skor": 0.8}:
            return False
        if pair_tur_karari([{"id": "x", "skor": 0.8}], 0.8, 0.9)["durum"] != "iyilesme-yok":
            return False
        for bozuk_a, m, e in [(None, 0.5, 0.8), ([], 0.5, 0.8), (adaylar, -0.1, 0.8), (adaylar, 0.5, 0), (adaylar, 0.5, True), ([adaylar[0], adaylar[0]], 0.5, 0.8)]:
            try:
                pair_tur_karari(bozuk_a, m, e)
                return False
            except ValueError:
                pass

        denemeler = [
            {"kampanya": "b", "tur": 2, "aday": "x", "skor": 0.4},
            {"kampanya": "a", "tur": 2, "aday": "x", "skor": 0.7},
            {"kampanya": "a", "tur": 1, "aday": "x", "skor": 0.3},
            {"kampanya": "a", "tur": 3, "aday": "y", "skor": 0.8},
            {"kampanya": "a", "tur": 4, "aday": "x", "skor": 0.9},
            {"kampanya": "b", "tur": 1, "aday": "x", "skor": 0.2},
        ]
        bek_ozet = [
            {"kampanya": "a", "deneme": 4, "en_iyi": 0.9, "basarili": True, "ilk_basari_turu": 3},
            {"kampanya": "b", "deneme": 2, "en_iyi": 0.4, "basarili": False, "ilk_basari_turu": None},
        ]
        if kampanya_ozeti(denemeler) != bek_ozet or kampanya_ozeti([]) != []:
            return False
        for bozuk_d, es in [(None, 0.8), ([denemeler[0], denemeler[0]], 0.8), ([dict(denemeler[0], tur=0)], 0.8), (denemeler, 0)]:
            try:
                kampanya_ozeti(bozuk_d, es)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False

ok(_sozlesme_kontrol(), "tap_agaci_uret, pair_tur_karari ve kampanya_ozeti sözleşme ve sınır kontrollerini geçmeli")
if not all(checks):
    stop()

try:
    rapor = L.deney(tap_agaci_uret, pair_tur_karari, kampanya_ozeti)
except ai_lab.GercekLabYok as e:
    ok(False, str(e))
    stop()
except Exception as e:
    ok(False, f"GERÇEK PAIR/TAP KAMPANYA DENEYİ YAPILAMADI: {type(e).__name__}: {e}")
    stop()

k = rapor["kontroller"]
ok(k["agac_uyumu"], f"tap_agaci_uret referansla uyuşmalı: {rapor['agac']}")
ok(k["tur_karari_uyumu"], f"pair_tur_karari canlı turlarda referansla uyuşmalı: {rapor['tur_kararlari']}")
ok(k["kampanya_ozeti_uyumu"], f"kampanya_ozeti canlı denemelerde referansla uyuşmalı: {rapor['kampanya_ozeti']}")
ok(k["saldirgan_ve_hedef_canli_kostu"], f"saldırgan ve hedef yerel model çağrıları tamamlanmalı: {rapor['ozet']}")
ok(k["cihaz_dogrulandi"], f"cihaz doğrulaması geçmeli: {rapor['ortam'].get('bellek')}")
ok(k["kaynak_temizlendi"], f"kaynak temizliği geçmeli: {rapor['ortam'].get('temizlik')}")

kabul = all(checks)
kanit_yolu = ai_lab.kanit_yaz("saldiri-30-pair-tap-kampanya", dict(rapor, kaynak="gercek", kabul=kabul))
o = rapor["ozet"]
print(f"GERÇEK PAIR/TAP KAMPANYA DENEYİ: model={o['model']} toplam_cagri={o['toplam_cagri']} özet={o['kampanya_ozeti']} kanıt={kanit_yolu}")
```

```solution
import importlib
import math
import ai_lab
L = importlib.import_module("sandbox.ai_gercek_ai_saldiri_30")

def tap_agaci_uret(kok="kok", derinlik=3, genislik=2):
    if not isinstance(kok, str):
        raise ValueError("kök türü geçersiz")
    if not kok or len(kok) > 32 or kok != kok.strip():
        raise ValueError("kök biçimi geçersiz")
    if any(x in kok for x in ("/", "\x00", "\n", "\r")):
        raise ValueError("kök ayırıcı içeriyor")
    if type(derinlik) is not int or derinlik < 0 or derinlik > 4:
        raise ValueError("derinlik geçersiz")
    if type(genislik) is not int or genislik < 1 or genislik > 3:
        raise ValueError("genişlik geçersiz")
    sonuc = [{"id": kok, "ebeveyn": None, "derinlik": 0}]
    seviye = [kok]
    for d in range(1, derinlik + 1):
        yeni = []
        for ebeveyn in seviye:
            for indeks in range(1, genislik + 1):
                kimlik = ebeveyn + "/" + str(indeks)
                sonuc.append({"id": kimlik, "ebeveyn": ebeveyn, "derinlik": d})
                yeni.append(kimlik)
        seviye = yeni
    return sonuc

def pair_tur_karari(adaylar, mevcut_skor, esik=0.8):
    def oran(deger, ad):
        if isinstance(deger, bool) or not isinstance(deger, (int, float)) or not math.isfinite(deger) or deger < 0 or deger > 1:
            raise ValueError(ad + " geçersiz")
    oran(mevcut_skor, "mevcut skor")
    oran(esik, "eşik")
    if esik == 0:
        raise ValueError("eşik sıfır olamaz")
    if not isinstance(adaylar, list) or not adaylar:
        raise ValueError("aday listesi geçersiz")
    kimlikler = set()
    for aday in adaylar:
        if not isinstance(aday, dict) or set(aday) != {"id", "skor"}:
            raise ValueError("aday şeması geçersiz")
        if type(aday["id"]) is not str or not aday["id"] or aday["id"] in kimlikler:
            raise ValueError("aday kimliği geçersiz")
        kimlikler.add(aday["id"])
        oran(aday["skor"], "aday skoru")
    secilen = sorted(adaylar, key=lambda x: (-x["skor"], x["id"]))[0]
    skor = float(secilen["skor"])
    if skor >= esik:
        durum = "basarili"
    elif skor <= mevcut_skor:
        durum = "iyilesme-yok"
    else:
        durum = "devam"
    return {"durum": durum, "secilen": secilen["id"], "skor": skor}

def kampanya_ozeti(denemeler, esik=0.8):
    if isinstance(esik, bool) or not isinstance(esik, (int, float)) or not math.isfinite(esik) or esik <= 0 or esik > 1:
        raise ValueError("eşik geçersiz")
    if not isinstance(denemeler, list):
        raise ValueError("deneme listesi geçersiz")
    gruplar = {}
    anahtarlar = set()
    for kayit in denemeler:
        if not isinstance(kayit, dict) or set(kayit) != {"kampanya", "tur", "aday", "skor"}:
            raise ValueError("deneme şeması geçersiz")
        if type(kayit["kampanya"]) is not str or not kayit["kampanya"]:
            raise ValueError("kampanya geçersiz")
        if type(kayit["aday"]) is not str or not kayit["aday"]:
            raise ValueError("aday geçersiz")
        if type(kayit["tur"]) is not int or kayit["tur"] < 1:
            raise ValueError("tur geçersiz")
        skor = kayit["skor"]
        if isinstance(skor, bool) or not isinstance(skor, (int, float)) or not math.isfinite(skor) or skor < 0 or skor > 1:
            raise ValueError("skor geçersiz")
        anahtar = (kayit["kampanya"], kayit["tur"], kayit["aday"])
        if anahtar in anahtarlar:
            raise ValueError("deneme tekrar ediyor")
        anahtarlar.add(anahtar)
        gruplar.setdefault(kayit["kampanya"], []).append(kayit)
    sonuc = []
    for kampanya, kayitlar in gruplar.items():
        basarili_turlar = [x["tur"] for x in kayitlar if x["skor"] >= esik]
        sonuc.append({"kampanya": kampanya, "deneme": len(kayitlar), "en_iyi": float(max(x["skor"] for x in kayitlar)), "basarili": bool(basarili_turlar), "ilk_basari_turu": min(basarili_turlar) if basarili_turlar else None})
    sonuc.sort(key=lambda x: x["kampanya"])
    return sonuc

if ai_lab.CALISTIR:
    L.goster(tap_agaci_uret, pair_tur_karari, kampanya_ozeti)
```

```hint
Önceki üç görevde yazdığın `tap_agaci_uret`, `pair_tur_karari` ve `kampanya_ozeti` işlevlerini eksiksiz taşı; `if ai_lab.CALISTIR:` bloğu canlı saldırgan+hedef kampanyasını çalıştırır.
```
:::
