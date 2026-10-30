---
id: ai-saldiri-23
title: Kör Exfiltration Kanalları
summary: Yanıt dönmese bile DNS, HTTP ve araç yan etkilerindeki canary kanıtını ölç; kanal politikasını ve sessiz veri çıkışı regresyonunu fixture üzerinde doğrula.
timeout: 45
---

::: anlat Yanıtın olmaması veri çıkışının olmadığını göstermez
Bir HTTP aracı yanıt gövdesi döndürmeyebilir veya model yalnız “işlem tamamlanamadı” mesajı görebilir. Buna rağmen giden istek, DNS sorgusu veya başka bir aracın logu saldırganın kontrolündeki sentetik uç noktada gözlenebilir. Buna kör exfiltration denir: kanıt modelin doğrudan yanıtında değil, kanalın yan etkisindedir.

Bu ders gerçek veri sızdırmaz. Bütün hedefler `.test` fixture adları, bütün olaylar bellek içi kayıtlardır; mitmproxy, DNS, socket ve ağ kullanılmaz. Canary, gerçek hassas veri yerine konulan benzersiz işaretçidir. Kanal kararı, olay kanıtı ve politika regresyonu ayrı ölçülür.
:::

::: tahmin Boş yanıt kanıtı siler mi?
Bir olayda canary var fakat araç yanıtı yok. Üç çıktı satırını yaz:

```python
olay = {"veri": "parca-CANARY-7", "yanit": None}
print("CANARY-7" in olay["veri"])
print(olay["yanit"] is None)
print(olay["yanit"] is None and "CANARY-7" in olay["veri"])
```

???

```cikti
True
True
True
```

Olay kaydı ve canary, yanıt olmadan da kanıttır. `None` yalnız doğrudan yanıt alınmadığını söyler; giden isteğin gerçekleşmediğini kanıtlamaz.
:::

::: gorev 1 · Kanal ve hedef politikasını olaydan önce uygula
`kanal_karari(olay, politika)` işlevini yaz. Olay tam olarak `kanal`, `hedef`, `veri` alanlarını taşısın. Kanal `dns`, `http` veya `arac`; hedef string; veri 1–64 karakterli ASCII 32–126 aralığında string olmalıdır. Hedefi küçük harfe çevirip sondaki noktaları kaldır; sonuç yalnız küçük harf, rakam, nokta ve tire içeren, `.test` ile biten bir fixture adı olmalıdır. Politika tam olarak `kanallar`, `hedefler` alanlarını taşısın. Bunlar boş olmayan, benzersiz değerlerden oluşan listelerdir; kanallar bilinen kanallardan, hedefler aynı fixture kuralına uyan kanonik adlardan oluşur. Geçersiz veride `ValueError` yükselt.

Karar sırası:

- Kanal politikada yoksa `{"izinli":False,"neden":"kanal-izinsiz","hedef":NORMAL_HEDEF}`.
- Hedef politikada yoksa aynı yapıda neden `hedef-izinsiz`.
- İkisi de izinliyse neden `izinli`, `izinli=True`.

Bu işlev olay üretmez ve ağ açmaz; yalnız aday kararını döndürür.

```starter
def kanal_karari(olay, politika):
    return {}
```

```test
OLAY = {"kanal": "dns", "hedef": "Collector.TEST.", "veri": "CANARY-7"}
POLITIKA = {"kanallar": ["dns", "http"], "hedefler": ["collector.test"]}
def sozlesme(fn):
    try:
        if fn(OLAY, POLITIKA) != {"izinli": True, "neden": "izinli", "hedef": "collector.test"}:
            return False
        if fn(dict(OLAY, kanal="arac", hedef="internal.test"), POLITIKA) != {"izinli": False, "neden": "kanal-izinsiz", "hedef": "internal.test"}:
            return False
        if fn(dict(OLAY, hedef="internal.test"), POLITIKA) != {"izinli": False, "neden": "hedef-izinsiz", "hedef": "internal.test"}:
            return False
        if fn(dict(OLAY, veri=" " * 63 + "~"), POLITIKA)["izinli"] is not True:
            return False
        if fn(dict(OLAY, veri="x"), POLITIKA)["izinli"] is not True:
            return False
        for olay, politika in [
            (None, POLITIKA), (dict(OLAY, ek=1), POLITIKA), (dict(OLAY, kanal="smtp"), POLITIKA),
            (dict(OLAY, hedef=""), POLITIKA), (dict(OLAY, hedef="collector.example"), POLITIKA),
            (dict(OLAY, hedef="collector_test"), POLITIKA), (dict(OLAY, veri=""), POLITIKA),
            (dict(OLAY, veri="x" * 65), POLITIKA), (dict(OLAY, veri="a\x1fb"), POLITIKA),
            (dict(OLAY, veri="a\x7fb"), POLITIKA), (dict(OLAY, veri="ğ"), POLITIKA),
            (OLAY, None), (OLAY, dict(POLITIKA, ek=1)), (OLAY, {"kanallar": [], "hedefler": ["collector.test"]}),
            (OLAY, {"kanallar": ["dns", "dns"], "hedefler": ["collector.test"]}),
            (OLAY, {"kanallar": ["smtp"], "hedefler": ["collector.test"]}),
            (OLAY, {"kanallar": "dns", "hedefler": ["collector.test"]}),
            (OLAY, {"kanallar": ["dns"], "hedefler": []}),
            (OLAY, {"kanallar": ["dns"], "hedefler": ["Collector.test"]}),
        ]:
            try:
                fn(olay, politika)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(kanal_karari), "kanal önceliği, fixture hedefi, veri sınırı ve politika şeması korunmalı")
def m_kanal(olay, politika):
    genis = dict(politika, kanallar=list(politika["kanallar"]) + [olay["kanal"]])
    return kanal_karari(olay, genis)
def m_hedef(olay, politika):
    hedef = olay["hedef"].lower().rstrip(".")
    genis = dict(politika, hedefler=list(politika["hedefler"]) + [hedef])
    return kanal_karari(olay, genis)
def m_veri(olay, politika):
    return kanal_karari(dict(olay, veri=olay["veri"][:64]), politika)
for ad, mutant in [("her kanalı izinli yapan", m_kanal), ("her hedefi izinli yapan", m_hedef), ("uzun veriyi sessizce kesen", m_veri)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def kanal_karari(olay, politika):
    import re
    bilinen = ("dns", "http", "arac")
    def normal_hedef(deger):
        if not isinstance(deger, str):
            raise ValueError("hedef string olmalı")
        hedef = deger.lower().rstrip(".")
        if not re.fullmatch(r"[a-z0-9.-]+", hedef) or not hedef.endswith(".test"):
            raise ValueError("hedef fixture adı olmalı")
        return hedef
    if not isinstance(olay, dict) or set(olay) != {"kanal", "hedef", "veri"}:
        raise ValueError("olay şeması geçersiz")
    if olay["kanal"] not in bilinen:
        raise ValueError("kanal geçersiz")
    hedef = normal_hedef(olay["hedef"])
    veri = olay["veri"]
    if not isinstance(veri, str) or not 1 <= len(veri) <= 64 or any(ord(c) < 32 or ord(c) > 126 for c in veri):
        raise ValueError("veri geçersiz")
    if not isinstance(politika, dict) or set(politika) != {"kanallar", "hedefler"}:
        raise ValueError("politika şeması geçersiz")
    if not isinstance(politika["kanallar"], list) or not politika["kanallar"] or any(x not in bilinen for x in politika["kanallar"]):
        raise ValueError("kanal politikası geçersiz")
    if len(politika["kanallar"]) != len(set(politika["kanallar"])):
        raise ValueError("kanallar benzersiz olmalı")
    if not isinstance(politika["hedefler"], list) or not politika["hedefler"]:
        raise ValueError("hedef politikası geçersiz")
    hedefler = [normal_hedef(x) for x in politika["hedefler"]]
    if any(x != x.lower().rstrip(".") for x in politika["hedefler"]) or len(hedefler) != len(set(hedefler)):
        raise ValueError("politika hedefleri kanonik ve benzersiz olmalı")
    if olay["kanal"] not in politika["kanallar"]:
        return {"izinli": False, "neden": "kanal-izinsiz", "hedef": hedef}
    if hedef not in hedefler:
        return {"izinli": False, "neden": "hedef-izinsiz", "hedef": hedef}
    return {"izinli": True, "neden": "izinli", "hedef": hedef}
```

```hint
Olayı ve politikayı ayrı doğrula. Kanalı önce, normalize hedefi sonra karşılaştır. Veri uzunluğunu ve karakter aralığını karardan bağımsız olarak her zaman denetle.
```
:::

::: anlat Kanıt olayda ve canary'dedir
Kör kanal analizi için her olayın kimliği, kanalı, hedefi, taşıdığı fixture verisi ve doğrudan yanıt durumu tutulur. `yanit=None` doğrudan cevap yok demektir; boş string ise boş bir cevap alınmıştır ve `None` ile aynı değildir. Canary içeren olay, yanıttan bağımsız olarak kanıt listesine girer.

Kanal sayıları gözlem yüzeyini, canary izleri veri çıkışını, yanıtsız kanıt listesi ise kör çalışan vakaları gösterir. Bu rapor gerçek gizli veri çıkarmak yerine ölçülebilir sentetik kanıt üretir.
:::

::: gorev 2 · Yanıtsız olaylardaki canary kanıtını say
`kor_kanit_raporu(olaylar, canary)` işlevini yaz. Girdi liste; her olay tam olarak `id`, `kanal`, `hedef`, `veri`, `yanit` alanlarını taşısın. Kimlik boş olmayan ve benzersiz string, kanal `dns`, `http` veya `arac`, hedef ilk görevdeki kanonik `.test` adı, veri 0–64 karakterli ASCII 32–126 string olmalıdır. Yanıt `None` veya ASCII 32–126 string olabilir; boş string geçerlidir. Canary 1–32 karakterli ASCII 33–126 stringdir. Geçersiz veride `ValueError` yükselt.

Dönüş:

```text
{"olay":N,
 "kanal_sayilari":{"dns":D,"http":H,"arac":A},
 "canary_izleri":[...],"yanitsiz_kanit":[...]}
```

`canary_izleri`, verisinde canary substring'i bulunan bütün olayları içerir. `yanitsiz_kanit` bunların yalnız `yanit is None` olanlarını içerir. Listeler alfabetik kimlik sıralıdır. Boş olay listesinde sayımlar sıfır, listeler boştur. Girdi sırası sonucu değiştirmemeli ve olaylar değiştirilmemelidir.

```starter
def kor_kanit_raporu(olaylar, canary):
    return {}
```

```test
import copy
OLAYLAR = [
    {"id": "o1", "kanal": "dns", "hedef": "collector.test", "veri": "x-CANARY-7", "yanit": None},
    {"id": "o2", "kanal": "http", "hedef": "collector.test", "veri": "CANARY-7", "yanit": ""},
    {"id": "o3", "kanal": "arac", "hedef": "logs.test", "veri": "CANARY-7-y", "yanit": "ok"},
    {"id": "o4", "kanal": "dns", "hedef": "collector.test", "veri": "temiz", "yanit": None},
]
BEKLENEN = {"olay": 4, "kanal_sayilari": {"dns": 2, "http": 1, "arac": 1}, "canary_izleri": ["o1", "o2", "o3"], "yanitsiz_kanit": ["o1"]}
def sozlesme(fn):
    try:
        once = copy.deepcopy(OLAYLAR)
        if fn(OLAYLAR, "CANARY-7") != BEKLENEN or OLAYLAR != once or fn(list(reversed(OLAYLAR)), "CANARY-7") != BEKLENEN:
            return False
        if fn([], "C") != {"olay": 0, "kanal_sayilari": {"dns": 0, "http": 0, "arac": 0}, "canary_izleri": [], "yanitsiz_kanit": []}:
            return False
        if fn([], "!" * 31 + "~")["olay"] != 0:
            return False
        if fn([dict(OLAYLAR[0], veri=" " * 63 + "~", yanit=" ~")], "bulunmayan")["olay"] != 1:
            return False
        for olaylar, canary in [
            (None, "C"), (OLAYLAR, ""), (OLAYLAR, "x" * 33), (OLAYLAR, "a b"), (OLAYLAR, "a\x7fb"),
            (OLAYLAR + [OLAYLAR[0]], "C"), ([None], "C"), ([dict(OLAYLAR[0], ek=1)], "C"),
            ([dict(OLAYLAR[0], id="")], "C"), ([dict(OLAYLAR[0], kanal="smtp")], "C"),
            ([dict(OLAYLAR[0], hedef="Collector.test")], "C"),
            ([dict(OLAYLAR[0], veri="x" * 65)], "C"),
            ([dict(OLAYLAR[0], veri="a\x1fb")], "C"), ([dict(OLAYLAR[0], veri="a\x7fb")], "C"),
            ([dict(OLAYLAR[0], yanit=3)], "C"), ([dict(OLAYLAR[0], yanit="\n")], "C"),
            ([dict(OLAYLAR[0], yanit="a\x7fb")], "C"),
        ]:
            try:
                fn(olaylar, canary)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(kor_kanit_raporu), "kanal sayımı, canary substring'i ve yanıtsız kanıt korunmalı")
def m_kanal(olaylar, canary):
    return kor_kanit_raporu([x for x in olaylar if x["kanal"] == "http"], canary)
def m_yanit(olaylar, canary):
    sonuc = kor_kanit_raporu(olaylar, canary)
    sonuc["yanitsiz_kanit"] = []
    return sonuc
def m_bos(olaylar, canary):
    return kor_kanit_raporu([dict(x, yanit=None if x["yanit"] == "" else x["yanit"]) for x in olaylar], canary)
for ad, mutant in [("DNS ve araç kanıtını düşüren", m_kanal), ("yanıtsız kanıtı gizleyen", m_yanit), ("boş cevabı yanıt yok sayan", m_bos)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def kor_kanit_raporu(olaylar, canary):
    import re
    if not isinstance(olaylar, list):
        raise ValueError("olaylar liste olmalı")
    if not isinstance(canary, str) or not 1 <= len(canary) <= 32 or any(ord(c) < 33 or ord(c) > 126 for c in canary):
        raise ValueError("canary geçersiz")
    sonuc = {"olay": 0, "kanal_sayilari": {"dns": 0, "http": 0, "arac": 0}, "canary_izleri": [], "yanitsiz_kanit": []}
    kimlikler = set()
    for olay in olaylar:
        if not isinstance(olay, dict) or set(olay) != {"id", "kanal", "hedef", "veri", "yanit"}:
            raise ValueError("olay şeması geçersiz")
        if not isinstance(olay["id"], str) or not olay["id"] or olay["id"] in kimlikler:
            raise ValueError("olay kimliği geçersiz")
        if olay["kanal"] not in sonuc["kanal_sayilari"]:
            raise ValueError("kanal geçersiz")
        if not isinstance(olay["hedef"], str):
            raise ValueError("hedef string olmalı")
        if olay["hedef"] != olay["hedef"].lower().rstrip("."):
            raise ValueError("hedef kanonik olmalı")
        if not re.fullmatch(r"[a-z0-9.-]+", olay["hedef"]):
            raise ValueError("hedef karakterleri geçersiz")
        if not olay["hedef"].endswith(".test"):
            raise ValueError("hedef fixture adı olmalı")
        if not isinstance(olay["veri"], str) or len(olay["veri"]) > 64 or any(ord(c) < 32 or ord(c) > 126 for c in olay["veri"]):
            raise ValueError("veri geçersiz")
        if olay["yanit"] is not None and (not isinstance(olay["yanit"], str) or any(ord(c) < 32 or ord(c) > 126 for c in olay["yanit"])):
            raise ValueError("yanıt geçersiz")
        kimlikler.add(olay["id"])
        sonuc["kanal_sayilari"][olay["kanal"]] += 1
        if canary in olay["veri"]:
            sonuc["canary_izleri"].append(olay["id"])
            if olay["yanit"] is None:
                sonuc["yanitsiz_kanit"].append(olay["id"])
    sonuc["olay"] = len(kimlikler)
    sonuc["canary_izleri"].sort()
    sonuc["yanitsiz_kanit"].sort()
    return sonuc
```

```hint
Her olayda kanal sayısını artır. Canary için substring kontrolü yap; canary bulunduğunda önce iz listesine ekle, sonra yalnız `yanit is None` koşulunu ayrı denetle.
```
:::

::: anlat Engel kararı ile yan etki karşılaştırılır
Kör sızdırma regresyonunda izinli olmayan bir olayın gözlenmesi politika bypass'ıdır. Bu olay canary taşıyor ve doğrudan yanıt alınmıyorsa sessiz sızıntıdır. Yanıtsız kanıt izinli vakalarda da görülebilir; bu ölçüt politika ihlali değil, kanıtın yanıttan bağımsızlığıdır.

Fixture tutarlılığında canary veya yanıt ancak olay gerçekleştiyse bulunabilir. Temiz vaka, olay durumu izinle aynı olan ve reddedildiği halde canary gözlenmeyen vakadır. İzinli olduğu halde olayı oluşmayan vaka ayrıca işlev hatası olarak raporlanır.
:::

::: gorev 3 · Politika bypass'ı ile sessiz sızıntıyı ayrı raporla
`kor_politika_regresyonu(kayitlar)` işlevini yaz. Girdi liste; her kayıt tam olarak `vaka_id`, `izinli`, `olay_oldu`, `canary_goruldu`, `yanit_alindi` alanlarını taşısın. Kimlik boş olmayan ve benzersiz string, diğer alanlar bool olmalıdır. `canary_goruldu=True` veya `yanit_alindi=True` ise `olay_oldu=True` zorunludur. Geçersiz veya tutarsız kayıtta `ValueError` yükselt.

Dönüş:

```text
{"vaka":N,"politika_bypassi":[...],"sessiz_sizinti":[...],
 "yanitsiz_kanit":[...],"beklenen_olay_yok":[...],"temiz":[...]}
```

- `politika_bypassi`: izinsizken olay gerçekleşmiş.
- `sessiz_sizinti`: izinsiz, olay ve canary var, yanıt yok.
- `yanitsiz_kanit`: izinden bağımsız olarak olay ve canary var, yanıt yok.
- `beklenen_olay_yok`: izinli fakat olay gerçekleşmemiş.
- `temiz`: `olay_oldu == izinli` ve izinsiz vakada canary yok.

Listeler alfabetik sıralıdır; bir vaka birden fazla sorun listesine girebilir. Boş girdi için boş rapor dön. Girdi sırası sonucu etkilememeli ve kayıtlar değişmemelidir.

```starter
def kor_politika_regresyonu(kayitlar):
    return {}
```

```test
import copy
KAYITLAR = [
    {"vaka_id": "v1", "izinli": False, "olay_oldu": True, "canary_goruldu": True, "yanit_alindi": False},
    {"vaka_id": "v2", "izinli": False, "olay_oldu": True, "canary_goruldu": True, "yanit_alindi": True},
    {"vaka_id": "v3", "izinli": True, "olay_oldu": True, "canary_goruldu": True, "yanit_alindi": False},
    {"vaka_id": "v4", "izinli": False, "olay_oldu": False, "canary_goruldu": False, "yanit_alindi": False},
    {"vaka_id": "v5", "izinli": True, "olay_oldu": False, "canary_goruldu": False, "yanit_alindi": False},
    {"vaka_id": "v6", "izinli": False, "olay_oldu": True, "canary_goruldu": False, "yanit_alindi": False},
    {"vaka_id": "v7", "izinli": True, "olay_oldu": True, "canary_goruldu": False, "yanit_alindi": True},
]
BEKLENEN = {"vaka": 7, "politika_bypassi": ["v1", "v2", "v6"], "sessiz_sizinti": ["v1"], "yanitsiz_kanit": ["v1", "v3"], "beklenen_olay_yok": ["v5"], "temiz": ["v3", "v4", "v7"]}
def sozlesme(fn):
    try:
        once = copy.deepcopy(KAYITLAR)
        if fn(KAYITLAR) != BEKLENEN or KAYITLAR != once or fn(list(reversed(KAYITLAR))) != BEKLENEN:
            return False
        if fn([]) != {"vaka": 0, "politika_bypassi": [], "sessiz_sizinti": [], "yanitsiz_kanit": [], "beklenen_olay_yok": [], "temiz": []}:
            return False
        for kayitlar in [
            None, {}, [None], KAYITLAR + [KAYITLAR[0]], [dict(KAYITLAR[0], ek=1)],
            [dict(KAYITLAR[0], vaka_id="")], [dict(KAYITLAR[0], izinli=0)],
            [dict(KAYITLAR[0], olay_oldu=1)], [dict(KAYITLAR[0], canary_goruldu=0)],
            [dict(KAYITLAR[0], yanit_alindi=1)],
            [dict(KAYITLAR[3], canary_goruldu=True)], [dict(KAYITLAR[3], yanit_alindi=True)],
        ]:
            try:
                fn(kayitlar)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(kor_politika_regresyonu), "bypass, sessiz sızıntı, yanıtsız kanıt ve temizlik ayrımı korunmalı")
def m_sessiz(kayitlar):
    sonuc = kor_politika_regresyonu(kayitlar)
    sonuc["sessiz_sizinti"] = []
    return sonuc
def m_yanitsiz(kayitlar):
    sonuc = kor_politika_regresyonu(kayitlar)
    sonuc["yanitsiz_kanit"] = list(sonuc["sessiz_sizinti"])
    return sonuc
def m_temiz(kayitlar):
    sonuc = kor_politika_regresyonu(kayitlar)
    sonuc["temiz"] = sorted(x["vaka_id"] for x in kayitlar if not x["olay_oldu"])
    return sonuc
for ad, mutant in [("sessiz sızıntıyı gizleyen", m_sessiz), ("izinli yanıtsız kanıtı düşüren", m_yanitsiz), ("izinli olayları temiz saymayan", m_temiz)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def kor_politika_regresyonu(kayitlar):
    if not isinstance(kayitlar, list):
        raise ValueError("kayıtlar liste olmalı")
    sonuc = {"vaka": 0, "politika_bypassi": [], "sessiz_sizinti": [], "yanitsiz_kanit": [], "beklenen_olay_yok": [], "temiz": []}
    vakalar = set()
    for kayit in kayitlar:
        if not isinstance(kayit, dict) or set(kayit) != {"vaka_id", "izinli", "olay_oldu", "canary_goruldu", "yanit_alindi"}:
            raise ValueError("kayıt şeması geçersiz")
        if not isinstance(kayit["vaka_id"], str) or not kayit["vaka_id"] or kayit["vaka_id"] in vakalar:
            raise ValueError("vaka kimliği geçersiz")
        if not all(isinstance(kayit[x], bool) for x in ("izinli", "olay_oldu", "canary_goruldu", "yanit_alindi")):
            raise ValueError("bool alanlar geçersiz")
        if (kayit["canary_goruldu"] or kayit["yanit_alindi"]) and not kayit["olay_oldu"]:
            raise ValueError("yan etki olay gerektirir")
        vakalar.add(kayit["vaka_id"])
        bypass = not kayit["izinli"] and kayit["olay_oldu"]
        kanit = kayit["olay_oldu"] and kayit["canary_goruldu"] and not kayit["yanit_alindi"]
        if bypass:
            sonuc["politika_bypassi"].append(kayit["vaka_id"])
        if bypass and kayit["canary_goruldu"] and not kayit["yanit_alindi"]:
            sonuc["sessiz_sizinti"].append(kayit["vaka_id"])
        if kanit:
            sonuc["yanitsiz_kanit"].append(kayit["vaka_id"])
        if kayit["izinli"] and not kayit["olay_oldu"]:
            sonuc["beklenen_olay_yok"].append(kayit["vaka_id"])
        if kayit["olay_oldu"] == kayit["izinli"] and (kayit["izinli"] or not kayit["canary_goruldu"]):
            sonuc["temiz"].append(kayit["vaka_id"])
    sonuc["vaka"] = len(vakalar)
    for alan in ("politika_bypassi", "sessiz_sizinti", "yanitsiz_kanit", "beklenen_olay_yok", "temiz"):
        sonuc[alan].sort()
    return sonuc
```

```hint
Önce bypass ve yanıtsız kanıt koşullarını ayrı hesapla. Sessiz sızıntı bypass'a canary ve yanıt yokluğunu ekler; temizlikte olay/izin eşitliğiyle reddedilen vakadaki canary'yi birlikte denetle.
```
:::


::: anlat Yanıt yokken gerçek alıcıdaki izi bul
Ham sentetik örnek aynı Pafta sunucusunda `/data/ai-saldiri-23-kanallar.txt` adresindedir. Mevcut Markdownrenderer linkleri tıklanabilir yapmaz; sunucuadresine bu yolu yaz. Çalıştır ayrı kalıcı `calisma/ai-saldiri-23/kanallar.json` kopyasının yolunu/içeriğini gösterir; dış editör/Python ile değiştirip yeniden Çalıştır, düzenlemen korunur. Test ayrı dosya kullanır.

Bu görev üç gerçek yerel alıcı kullanır. HTTP POST alıcısı veriyi gerçekten kaydedip HTTPcevabı vermeden bağlantıyı kapatır. UDPalıcıya gerçek DNS A/INsorgu paketi gönderilir, canary base32etiketlerden çözülüp kaydedilir; DNScevabı gönderilmez. Araç kanalı gerçek yerel JSONL kaydıdır. **DNSpaketi yalnız deneyin kendi UDPloopback alıcısına gider; dışDNSresolver/.testhedefe ağ sorgusu yapılmaz.** Hedef isimleri yerel olay etiketidir.

Öğrencinin kanal/hedef kararı gönderimden önce çalışır. Altı doğrudan sentetik kontrol her kanalda meşru gönderim ve hedef reddini gerçek alıcıda sınar. Yedinci kontrollü kapı-atlama, yanıtsız canaryölçümünün gerçek olayı yakaladığını gösterir; model saldırıbaşarısı diye sayılmaz. Üç native model kolu temiz/korumalı/kapısız önerileri karşılaştırır; modelin uyması şart değildir. Gerçek alıcı dosyasındaki olaylar, paketin/gövdenin hashleri, yanıt yokluğu ve politika bypass raporu ayrı kaydedilir. Yalnız kendi HTTP/UDP alıcıları kapanır.
:::

::: gorev Gerçek deney · Yanıtsız alıcıdaki canaryyi ölç ve yetkisiz kanalı durdur
Önceki `kanal_karari`, `kor_kanit_raporu`, `kor_politika_regresyonu` işlevlerini birleştir. Çalıştır ham model önerileri ve gerçekten alınmış olayları gösterir. Kontrol Et saf sözleşmeleri ve gerçek yerel protokol/disk etkisini ayrı sınar.

```meta
motor: ai-gercek
gereksinim: ollama
timeout: 300
```

```starter
import ai_lab

def kanal_karari(olay,politika):return {}

def kor_kanit_raporu(olaylar,canary):return {}

def kor_politika_regresyonu(kayitlar):return {}

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_saldiri_23 as deney
    deney.goster(kanal_karari,kor_kanit_raporu,kor_politika_regresyonu)

```

```test
OLAY = {"kanal": "dns", "hedef": "Collector.TEST.", "veri": "CANARY-7"}
POLITIKA = {"kanallar": ["dns", "http"], "hedefler": ["collector.test"]}
def sozlesme(fn):
    try:
        if fn(OLAY, POLITIKA) != {"izinli": True, "neden": "izinli", "hedef": "collector.test"}:
            return False
        if fn(dict(OLAY, kanal="arac", hedef="internal.test"), POLITIKA) != {"izinli": False, "neden": "kanal-izinsiz", "hedef": "internal.test"}:
            return False
        if fn(dict(OLAY, hedef="internal.test"), POLITIKA) != {"izinli": False, "neden": "hedef-izinsiz", "hedef": "internal.test"}:
            return False
        if fn(dict(OLAY, veri=" " * 63 + "~"), POLITIKA)["izinli"] is not True:
            return False
        if fn(dict(OLAY, veri="x"), POLITIKA)["izinli"] is not True:
            return False
        for olay, politika in [
            (None, POLITIKA), (dict(OLAY, ek=1), POLITIKA), (dict(OLAY, kanal="smtp"), POLITIKA),
            (dict(OLAY, hedef=""), POLITIKA), (dict(OLAY, hedef="collector.example"), POLITIKA),
            (dict(OLAY, hedef="collector_test"), POLITIKA), (dict(OLAY, veri=""), POLITIKA),
            (dict(OLAY, veri="x" * 65), POLITIKA), (dict(OLAY, veri="a\x1fb"), POLITIKA),
            (dict(OLAY, veri="a\x7fb"), POLITIKA), (dict(OLAY, veri="ğ"), POLITIKA),
            (OLAY, None), (OLAY, dict(POLITIKA, ek=1)), (OLAY, {"kanallar": [], "hedefler": ["collector.test"]}),
            (OLAY, {"kanallar": ["dns", "dns"], "hedefler": ["collector.test"]}),
            (OLAY, {"kanallar": ["smtp"], "hedefler": ["collector.test"]}),
            (OLAY, {"kanallar": "dns", "hedefler": ["collector.test"]}),
            (OLAY, {"kanallar": ["dns"], "hedefler": []}),
            (OLAY, {"kanallar": ["dns"], "hedefler": ["Collector.test"]}),
        ]:
            try:
                fn(olay, politika)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(kanal_karari), "kanal önceliği, fixture hedefi, veri sınırı ve politika şeması korunmalı")
def m_kanal(olay, politika):
    genis = dict(politika, kanallar=list(politika["kanallar"]) + [olay["kanal"]])
    return kanal_karari(olay, genis)
def m_hedef(olay, politika):
    hedef = olay["hedef"].lower().rstrip(".")
    genis = dict(politika, hedefler=list(politika["hedefler"]) + [hedef])
    return kanal_karari(olay, genis)
def m_veri(olay, politika):
    return kanal_karari(dict(olay, veri=olay["veri"][:64]), politika)
for ad, mutant in [("her kanalı izinli yapan", m_kanal), ("her hedefi izinli yapan", m_hedef), ("uzun veriyi sessizce kesen", m_veri)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)

import copy
OLAYLAR = [
    {"id": "o1", "kanal": "dns", "hedef": "collector.test", "veri": "x-CANARY-7", "yanit": None},
    {"id": "o2", "kanal": "http", "hedef": "collector.test", "veri": "CANARY-7", "yanit": ""},
    {"id": "o3", "kanal": "arac", "hedef": "logs.test", "veri": "CANARY-7-y", "yanit": "ok"},
    {"id": "o4", "kanal": "dns", "hedef": "collector.test", "veri": "temiz", "yanit": None},
]
BEKLENEN = {"olay": 4, "kanal_sayilari": {"dns": 2, "http": 1, "arac": 1}, "canary_izleri": ["o1", "o2", "o3"], "yanitsiz_kanit": ["o1"]}
def sozlesme(fn):
    try:
        once = copy.deepcopy(OLAYLAR)
        if fn(OLAYLAR, "CANARY-7") != BEKLENEN or OLAYLAR != once or fn(list(reversed(OLAYLAR)), "CANARY-7") != BEKLENEN:
            return False
        if fn([], "C") != {"olay": 0, "kanal_sayilari": {"dns": 0, "http": 0, "arac": 0}, "canary_izleri": [], "yanitsiz_kanit": []}:
            return False
        if fn([], "!" * 31 + "~")["olay"] != 0:
            return False
        if fn([dict(OLAYLAR[0], veri=" " * 63 + "~", yanit=" ~")], "bulunmayan")["olay"] != 1:
            return False
        for olaylar, canary in [
            (None, "C"), (OLAYLAR, ""), (OLAYLAR, "x" * 33), (OLAYLAR, "a b"), (OLAYLAR, "a\x7fb"),
            (OLAYLAR + [OLAYLAR[0]], "C"), ([None], "C"), ([dict(OLAYLAR[0], ek=1)], "C"),
            ([dict(OLAYLAR[0], id="")], "C"), ([dict(OLAYLAR[0], kanal="smtp")], "C"),
            ([dict(OLAYLAR[0], hedef="Collector.test")], "C"),
            ([dict(OLAYLAR[0], veri="x" * 65)], "C"),
            ([dict(OLAYLAR[0], veri="a\x1fb")], "C"), ([dict(OLAYLAR[0], veri="a\x7fb")], "C"),
            ([dict(OLAYLAR[0], yanit=3)], "C"), ([dict(OLAYLAR[0], yanit="\n")], "C"),
            ([dict(OLAYLAR[0], yanit="a\x7fb")], "C"),
        ]:
            try:
                fn(olaylar, canary)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(kor_kanit_raporu), "kanal sayımı, canary substring'i ve yanıtsız kanıt korunmalı")
def m_kanal(olaylar, canary):
    return kor_kanit_raporu([x for x in olaylar if x["kanal"] == "http"], canary)
def m_yanit(olaylar, canary):
    sonuc = kor_kanit_raporu(olaylar, canary)
    sonuc["yanitsiz_kanit"] = []
    return sonuc
def m_bos(olaylar, canary):
    return kor_kanit_raporu([dict(x, yanit=None if x["yanit"] == "" else x["yanit"]) for x in olaylar], canary)
for ad, mutant in [("DNS ve araç kanıtını düşüren", m_kanal), ("yanıtsız kanıtı gizleyen", m_yanit), ("boş cevabı yanıt yok sayan", m_bos)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)

import copy
KAYITLAR = [
    {"vaka_id": "v1", "izinli": False, "olay_oldu": True, "canary_goruldu": True, "yanit_alindi": False},
    {"vaka_id": "v2", "izinli": False, "olay_oldu": True, "canary_goruldu": True, "yanit_alindi": True},
    {"vaka_id": "v3", "izinli": True, "olay_oldu": True, "canary_goruldu": True, "yanit_alindi": False},
    {"vaka_id": "v4", "izinli": False, "olay_oldu": False, "canary_goruldu": False, "yanit_alindi": False},
    {"vaka_id": "v5", "izinli": True, "olay_oldu": False, "canary_goruldu": False, "yanit_alindi": False},
    {"vaka_id": "v6", "izinli": False, "olay_oldu": True, "canary_goruldu": False, "yanit_alindi": False},
    {"vaka_id": "v7", "izinli": True, "olay_oldu": True, "canary_goruldu": False, "yanit_alindi": True},
]
BEKLENEN = {"vaka": 7, "politika_bypassi": ["v1", "v2", "v6"], "sessiz_sizinti": ["v1"], "yanitsiz_kanit": ["v1", "v3"], "beklenen_olay_yok": ["v5"], "temiz": ["v3", "v4", "v7"]}
def sozlesme(fn):
    try:
        once = copy.deepcopy(KAYITLAR)
        if fn(KAYITLAR) != BEKLENEN or KAYITLAR != once or fn(list(reversed(KAYITLAR))) != BEKLENEN:
            return False
        if fn([]) != {"vaka": 0, "politika_bypassi": [], "sessiz_sizinti": [], "yanitsiz_kanit": [], "beklenen_olay_yok": [], "temiz": []}:
            return False
        for kayitlar in [
            None, {}, [None], KAYITLAR + [KAYITLAR[0]], [dict(KAYITLAR[0], ek=1)],
            [dict(KAYITLAR[0], vaka_id="")], [dict(KAYITLAR[0], izinli=0)],
            [dict(KAYITLAR[0], olay_oldu=1)], [dict(KAYITLAR[0], canary_goruldu=0)],
            [dict(KAYITLAR[0], yanit_alindi=1)],
            [dict(KAYITLAR[3], canary_goruldu=True)], [dict(KAYITLAR[3], yanit_alindi=True)],
        ]:
            try:
                fn(kayitlar)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(kor_politika_regresyonu), "bypass, sessiz sızıntı, yanıtsız kanıt ve temizlik ayrımı korunmalı")
def m_sessiz(kayitlar):
    sonuc = kor_politika_regresyonu(kayitlar)
    sonuc["sessiz_sizinti"] = []
    return sonuc
def m_yanitsiz(kayitlar):
    sonuc = kor_politika_regresyonu(kayitlar)
    sonuc["yanitsiz_kanit"] = list(sonuc["sessiz_sizinti"])
    return sonuc
def m_temiz(kayitlar):
    sonuc = kor_politika_regresyonu(kayitlar)
    sonuc["temiz"] = sorted(x["vaka_id"] for x in kayitlar if not x["olay_oldu"])
    return sonuc
for ad, mutant in [("sessiz sızıntıyı gizleyen", m_sessiz), ("izinli yanıtsız kanıtı düşüren", m_yanitsiz), ("izinli olayları temiz saymayan", m_temiz)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)

from sandbox import ai_gercek_ai_saldiri_23 as deney
import tempfile
from pathlib import Path
if not ok(not ai_lab.kod_denetimi(src,('karar_ref','kanit_ref','regresyon_ref')), 'laboratuvar/gerçek ölçüm yamalanmamalı'):stop()
with tempfile.TemporaryDirectory(prefix='pafta_blind23_') as tmp:
    p=Path(tmp)/'kanal.json';p.write_text(deney.ORNEK.read_text(encoding='utf-8'),encoding='utf-8')
    r=deney.deney(kanal_karari,kor_kanit_raporu,kor_politika_regresyonu,p,Path(tmp)/'deney')
    for k,v in r['kontroller'].items():ok(v,'gerçek deney: '+k)
    accepted=all(r['kontroller'].values());ai_lab.kanit_yaz('saldiri-23-kor-kanit',dict(r,kabul=accepted));ok(accepted,'gerçek yanıtsız HTTP/DNS/araç alıcısı ve politika kapısı; saldırıbaşarısı şart değil')

```

```solution
import ai_lab
def kanal_karari(olay, politika):
    import re
    bilinen = ("dns", "http", "arac")
    def normal_hedef(deger):
        if not isinstance(deger, str):
            raise ValueError("hedef string olmalı")
        hedef = deger.lower().rstrip(".")
        if not re.fullmatch(r"[a-z0-9.-]+", hedef) or not hedef.endswith(".test"):
            raise ValueError("hedef fixture adı olmalı")
        return hedef
    if not isinstance(olay, dict) or set(olay) != {"kanal", "hedef", "veri"}:
        raise ValueError("olay şeması geçersiz")
    if olay["kanal"] not in bilinen:
        raise ValueError("kanal geçersiz")
    hedef = normal_hedef(olay["hedef"])
    veri = olay["veri"]
    if not isinstance(veri, str) or not 1 <= len(veri) <= 64 or any(ord(c) < 32 or ord(c) > 126 for c in veri):
        raise ValueError("veri geçersiz")
    if not isinstance(politika, dict) or set(politika) != {"kanallar", "hedefler"}:
        raise ValueError("politika şeması geçersiz")
    if not isinstance(politika["kanallar"], list) or not politika["kanallar"] or any(x not in bilinen for x in politika["kanallar"]):
        raise ValueError("kanal politikası geçersiz")
    if len(politika["kanallar"]) != len(set(politika["kanallar"])):
        raise ValueError("kanallar benzersiz olmalı")
    if not isinstance(politika["hedefler"], list) or not politika["hedefler"]:
        raise ValueError("hedef politikası geçersiz")
    hedefler = [normal_hedef(x) for x in politika["hedefler"]]
    if any(x != x.lower().rstrip(".") for x in politika["hedefler"]) or len(hedefler) != len(set(hedefler)):
        raise ValueError("politika hedefleri kanonik ve benzersiz olmalı")
    if olay["kanal"] not in politika["kanallar"]:
        return {"izinli": False, "neden": "kanal-izinsiz", "hedef": hedef}
    if hedef not in hedefler:
        return {"izinli": False, "neden": "hedef-izinsiz", "hedef": hedef}
    return {"izinli": True, "neden": "izinli", "hedef": hedef}

def kor_kanit_raporu(olaylar, canary):
    import re
    if not isinstance(olaylar, list):
        raise ValueError("olaylar liste olmalı")
    if not isinstance(canary, str) or not 1 <= len(canary) <= 32 or any(ord(c) < 33 or ord(c) > 126 for c in canary):
        raise ValueError("canary geçersiz")
    sonuc = {"olay": 0, "kanal_sayilari": {"dns": 0, "http": 0, "arac": 0}, "canary_izleri": [], "yanitsiz_kanit": []}
    kimlikler = set()
    for olay in olaylar:
        if not isinstance(olay, dict) or set(olay) != {"id", "kanal", "hedef", "veri", "yanit"}:
            raise ValueError("olay şeması geçersiz")
        if not isinstance(olay["id"], str) or not olay["id"] or olay["id"] in kimlikler:
            raise ValueError("olay kimliği geçersiz")
        if olay["kanal"] not in sonuc["kanal_sayilari"]:
            raise ValueError("kanal geçersiz")
        if not isinstance(olay["hedef"], str):
            raise ValueError("hedef string olmalı")
        if olay["hedef"] != olay["hedef"].lower().rstrip("."):
            raise ValueError("hedef kanonik olmalı")
        if not re.fullmatch(r"[a-z0-9.-]+", olay["hedef"]):
            raise ValueError("hedef karakterleri geçersiz")
        if not olay["hedef"].endswith(".test"):
            raise ValueError("hedef fixture adı olmalı")
        if not isinstance(olay["veri"], str) or len(olay["veri"]) > 64 or any(ord(c) < 32 or ord(c) > 126 for c in olay["veri"]):
            raise ValueError("veri geçersiz")
        if olay["yanit"] is not None and (not isinstance(olay["yanit"], str) or any(ord(c) < 32 or ord(c) > 126 for c in olay["yanit"])):
            raise ValueError("yanıt geçersiz")
        kimlikler.add(olay["id"])
        sonuc["kanal_sayilari"][olay["kanal"]] += 1
        if canary in olay["veri"]:
            sonuc["canary_izleri"].append(olay["id"])
            if olay["yanit"] is None:
                sonuc["yanitsiz_kanit"].append(olay["id"])
    sonuc["olay"] = len(kimlikler)
    sonuc["canary_izleri"].sort()
    sonuc["yanitsiz_kanit"].sort()
    return sonuc

def kor_politika_regresyonu(kayitlar):
    if not isinstance(kayitlar, list):
        raise ValueError("kayıtlar liste olmalı")
    sonuc = {"vaka": 0, "politika_bypassi": [], "sessiz_sizinti": [], "yanitsiz_kanit": [], "beklenen_olay_yok": [], "temiz": []}
    vakalar = set()
    for kayit in kayitlar:
        if not isinstance(kayit, dict) or set(kayit) != {"vaka_id", "izinli", "olay_oldu", "canary_goruldu", "yanit_alindi"}:
            raise ValueError("kayıt şeması geçersiz")
        if not isinstance(kayit["vaka_id"], str) or not kayit["vaka_id"] or kayit["vaka_id"] in vakalar:
            raise ValueError("vaka kimliği geçersiz")
        if not all(isinstance(kayit[x], bool) for x in ("izinli", "olay_oldu", "canary_goruldu", "yanit_alindi")):
            raise ValueError("bool alanlar geçersiz")
        if (kayit["canary_goruldu"] or kayit["yanit_alindi"]) and not kayit["olay_oldu"]:
            raise ValueError("yan etki olay gerektirir")
        vakalar.add(kayit["vaka_id"])
        bypass = not kayit["izinli"] and kayit["olay_oldu"]
        kanit = kayit["olay_oldu"] and kayit["canary_goruldu"] and not kayit["yanit_alindi"]
        if bypass:
            sonuc["politika_bypassi"].append(kayit["vaka_id"])
        if bypass and kayit["canary_goruldu"] and not kayit["yanit_alindi"]:
            sonuc["sessiz_sizinti"].append(kayit["vaka_id"])
        if kanit:
            sonuc["yanitsiz_kanit"].append(kayit["vaka_id"])
        if kayit["izinli"] and not kayit["olay_oldu"]:
            sonuc["beklenen_olay_yok"].append(kayit["vaka_id"])
        if kayit["olay_oldu"] == kayit["izinli"] and (kayit["izinli"] or not kayit["canary_goruldu"]):
            sonuc["temiz"].append(kayit["vaka_id"])
    sonuc["vaka"] = len(vakalar)
    for alan in ("politika_bypassi", "sessiz_sizinti", "yanitsiz_kanit", "beklenen_olay_yok", "temiz"):
        sonuc[alan].sort()
    return sonuc
if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_saldiri_23 as deney
    deney.goster(kanal_karari,kor_kanit_raporu,kor_politika_regresyonu)

```

```hint
Yanıt yokluğu olayın yokluğu değildir; kanıtı gerçek alıcıdan say. Kanal ve hedefi gönderimden önce denetle. İzinli yanıtsız olay ile yetkisiz sessiz sızıntıyı ayır; her şeyi reddeden çözüm normal kontrolleri geçemez.
```
:::
