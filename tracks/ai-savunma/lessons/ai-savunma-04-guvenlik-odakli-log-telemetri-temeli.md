---
id: ai-savunma-04
title: Güvenlik Odaklı Log ve Telemetri Temeli
summary: Hassas içeriği dışlayan olay şeması kur, trace zincirlerini ilişkilendir ve sayısal telemetri özeti üret.
timeout: 45
---

::: anlat İzlenebilirlik ham içeriği kaydetmek değildir
Bir AI isteğini izlemek için trace kimliği, olay kimliği, parent ilişkisi, olay türü, zaman ve süre yeterlidir. Prompt, model yanıtı, API anahtarı, Authorization başlığı veya kullanıcı e-postası güvenlik telemetrisine eklenmemelidir. Model adı, HTTP kodu, guardrail kararı ve token sayıları gibi dar alanlar ise ölçüm için kullanılabilir.

Bu derste alan izin listesi fail-closed çalışır: bilinmeyen alan sessizce loglanmaz, olay geçersiz sayılır. Böylece `prompt` veya `yanit` gibi yeni bir alanın şemaya yanlışlıkla eklenmesi engellenir. OpenTelemetry ve SigNoz kavramları standart Python fixture'larıyla temsil edilir; gerçek servis veya model gerekmez.
:::

::: tahmin İzin listesi bilinmeyen alanı görünür kılar
Üç çıktı satırını yaz:

```python
alanlar = {"model": "yerel", "prompt": "gizli"}
print("prompt" in alanlar)
print(sorted(alanlar))
print(len(alanlar) - 1)
```

???

```cikti
True
['model', 'prompt']
1
```

İzin verilen alan sayısını çıkarmak yerine bilinmeyen alanı reddetmek, ham içeriğin loglanmasını önler.
:::

::: gorev 1 · Hassas içeriği dışlayan telemetri olayını doğrula
`guvenli_telemetri_olayi(olay)` işlevini yaz. Olay tam olarak `iz_id`, `olay_id`, `parent_id`, `tur`, `zaman_ms`, `sure_ms`, `alanlar` alanlarını taşısın. İz ve olay kimlikleri baş/son boşluğu olmayan boş olmayan stringlerdir. Parent None veya aynı kurallara uyan ve olay kimliğinden farklı bir stringdir. Tür yalnız `http`, `model`, `guardrail`, `arac`; zaman ve süre bool olmayan, sonlu ve sıfır/pozitif sayılardır.

`alanlar` sözlüğü yalnız şu alanları içerebilir:

- her tür: `durum` (`ok` veya `hata`), `hata_kodu` (boş olmayan string)
- `http`: `http_kod` (bool olmayan 100–599 int), `yontem` (boş olmayan string)
- `model`: `model` (boş olmayan string), `token_in`, `token_out` (bool olmayan sıfır/pozitif int)
- `guardrail`: `karar` (`izin`, `reddet` veya `hata`)
- `arac`: `arac` (boş olmayan string)

Metin alanlarının baş/son boşluğu olamaz. Bilinmeyen alan veya geçersiz veride `ValueError` yükselt. Olayı ve alanlar sözlüğünü kopyalayarak döndür, girdiyi değiştirme.

```starter
def guvenli_telemetri_olayi(olay):
    return {}
```

```test
import copy
O = {"iz_id": "iz-1", "olay_id": "model-1", "parent_id": "http-1", "tur": "model", "zaman_ms": 10, "sure_ms": 2.5, "alanlar": {"token_out": 3, "model": "yerel", "token_in": 5, "durum": "ok"}}
def sozlesme(fn):
    try:
        once = copy.deepcopy(O)
        if fn(O) != O or O != once or fn(O) is O or fn(O)["alanlar"] is O["alanlar"]:
            return False
        sifir = dict(O, zaman_ms=0, sure_ms=0, parent_id=None, alanlar={"token_in": 0, "token_out": 0})
        if fn(sifir)["sure_ms"] != 0:
            return False
        for olay in [
            None, [], dict(O, ek=1), dict(O, iz_id=""), dict(O, iz_id=" x"),
            dict(O, olay_id=None), dict(O, parent_id="model-1"), dict(O, parent_id=1),
            dict(O, parent_id=""), dict(O, parent_id=" x"),
            dict(O, tur="diger"), dict(O, zaman_ms=True), dict(O, sure_ms=-1),
            dict(O, zaman_ms=float("nan")), dict(O, sure_ms=float("inf")),
            dict(O, alanlar=None), dict(O, alanlar={"prompt": "gizli"}),
            dict(O, alanlar={"yanit": "gizli"}), dict(O, alanlar={"api_key": "x"}),
            dict(O, alanlar={"http_kod": 200}), dict(O, alanlar={"token_in": True}),
            dict(O, alanlar={"token_out": -1}), dict(O, alanlar={"model": " x"}),
            dict(O, alanlar={"durum": "bitti"}), dict(O, alanlar={"hata_kodu": ""}),
            dict(O, tur="http", alanlar={"http_kod": 99}),
            dict(O, tur="http", alanlar={"http_kod": 600}),
            dict(O, tur="http", alanlar={"http_kod": True}),
            dict(O, tur="guardrail", alanlar={"karar": "belirsiz"}),
        ]:
            try:
                fn(olay)
                return False
            except ValueError:
                pass
        for kod in (100, 599):
            if fn(dict(O, tur="http", alanlar={"http_kod": kod}))["alanlar"]["http_kod"] != kod:
                return False
        return True
    except Exception:
        return False
ok(sozlesme(guvenli_telemetri_olayi), "izin listesi, sayı sınırları ve kopyalama korunmalı")
def m_prompt(olay):
    sonuc = guvenli_telemetri_olayi(olay)
    sonuc["alanlar"]["prompt"] = "gizli"
    return sonuc
def m_sure(olay):
    sonuc = guvenli_telemetri_olayi(olay)
    sonuc["sure_ms"] += 1
    return sonuc
def m_token(olay):
    sonuc = guvenli_telemetri_olayi(olay)
    sonuc["alanlar"].pop("token_in", None)
    return sonuc
for ad, mutant in [("ham prompt ekleyen", m_prompt), ("süreyi değiştiren", m_sure), ("token kanıtını silen", m_token)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def guvenli_telemetri_olayi(olay):
    import math
    zorunlu = {"iz_id", "olay_id", "parent_id", "tur", "zaman_ms", "sure_ms", "alanlar"}
    if not isinstance(olay, dict):
        raise ValueError("olay geçersiz")
    if set(olay) != zorunlu:
        raise ValueError("olay şeması geçersiz")
    for alan in ("iz_id", "olay_id"):
        deger = olay[alan]
        if not isinstance(deger, str):
            raise ValueError("kimlik geçersiz")
        if not deger or deger != deger.strip():
            raise ValueError("kimlik geçersiz")
    parent = olay["parent_id"]
    if parent is not None:
        if not isinstance(parent, str):
            raise ValueError("parent geçersiz")
        if not parent or parent != parent.strip():
            raise ValueError("parent geçersiz")
        if parent == olay["olay_id"]:
            raise ValueError("olay kendi parentı olamaz")
    tur = olay["tur"]
    if tur not in ("http", "model", "guardrail", "arac"):
        raise ValueError("olay türü geçersiz")
    for alan in ("zaman_ms", "sure_ms"):
        deger = olay[alan]
        if isinstance(deger, bool) or not isinstance(deger, (int, float)):
            raise ValueError("süre geçersiz")
        if not math.isfinite(deger):
            raise ValueError("süre sonlu olmalı")
        if deger < 0:
            raise ValueError("süre negatif olamaz")
    alanlar = olay["alanlar"]
    if not isinstance(alanlar, dict):
        raise ValueError("alanlar geçersiz")
    izinli = {"durum", "hata_kodu"} | {
        "http": {"http_kod", "yontem"}, "model": {"model", "token_in", "token_out"},
        "guardrail": {"karar"}, "arac": {"arac"},
    }[tur]
    if any(alan not in izinli for alan in alanlar):
        raise ValueError("bilinmeyen veya hassas alan")
    for alan in ("hata_kodu", "yontem", "model", "arac"):
        if alan in alanlar:
            deger = alanlar[alan]
            if not isinstance(deger, str) or not deger or deger != deger.strip():
                raise ValueError("metin alanı geçersiz")
    if "durum" in alanlar and alanlar["durum"] not in ("ok", "hata"):
        raise ValueError("durum geçersiz")
    if "karar" in alanlar and alanlar["karar"] not in ("izin", "reddet", "hata"):
        raise ValueError("karar geçersiz")
    if "http_kod" in alanlar:
        kod = alanlar["http_kod"]
        if type(kod) is not int or kod < 100 or kod > 599:
            raise ValueError("HTTP kodu geçersiz")
    for alan in ("token_in", "token_out"):
        if alan in alanlar:
            deger = alanlar[alan]
            if type(deger) is not int or deger < 0:
                raise ValueError("token sayısı geçersiz")
    sonuc = dict(olay)
    sonuc["alanlar"] = {alan: alanlar[alan] for alan in sorted(alanlar)}
    return sonuc
```

```hint
Önce olayın tam alan kümesini doğrula. Sonra türe özel izin kümesi çıkar; izin dışındaki her anahtarı reddet ve sonuçta yeni bir alan sözlüğü oluştur.
```
:::

::: anlat Trace ilişkisi olayları tek istekte birleştirir
Her olay aynı trace içinde benzersiz bir olay kimliği taşır. Parent kimliği None ise olay köktür; aksi hâlde parent aynı trace içinde bulunmalı ve başlangıç zamanı çocuğun başlangıcından sonra olmamalıdır. Başka trace'e parent vermek veya döngü oluşturmak korelasyonu bozar.

Trace süresi olay sürelerinin toplamı değildir; paralel işlerde süreler çakışabilir. Bu ders `maksimum(zaman + süre) - minimum(zaman)` hesabını kullanır. Olaylar başlangıç zamanı ve kimlikle sıralanır.
:::

::: gorev 2 · Olayları doğrulanmış trace zincirlerine dönüştür
`iz_zinciri_raporu(olaylar)` işlevini yaz. Her olay ilk görevin kurallarını sağlasın. `(iz_id, olay_id)` çifti benzersiz, parent aynı trace içinde kayıtlı ve parent başlangıcı çocuk başlangıcından büyük olmamalıdır. Parent zinciri döngü içeremez. Geçersiz veride `ValueError` yükselt.

Her trace için:

```text
{"iz_id":ID,"kokler":[OLAY_ID,...],"olaylar":[OLAY_ID,...],
 "baslangic_ms":B,"bitis_ms":T,"sure_ms":T-B}
```

Trace'leri iz kimliğine, kökleri ve olayları `(zaman_ms, olay_id)` sırasına göre sırala. Boş girdi için boş liste döndür ve girdiyi değiştirme.

```starter
def iz_zinciri_raporu(olaylar):
    return []
```

```test
import copy
O = [
    {"iz_id": "iz-b", "olay_id": "kok", "parent_id": None, "tur": "http", "zaman_ms": 20, "sure_ms": 8, "alanlar": {}},
    {"iz_id": "iz-a", "olay_id": "model", "parent_id": "http", "tur": "model", "zaman_ms": 3, "sure_ms": 5, "alanlar": {}},
    {"iz_id": "iz-a", "olay_id": "http", "parent_id": None, "tur": "http", "zaman_ms": 0, "sure_ms": 12, "alanlar": {}},
    {"iz_id": "iz-a", "olay_id": "arac", "parent_id": "model", "tur": "arac", "zaman_ms": 9, "sure_ms": 4, "alanlar": {}},
]
BEKLENEN = [
    {"iz_id": "iz-a", "kokler": ["http"], "olaylar": ["http", "model", "arac"], "baslangic_ms": 0, "bitis_ms": 13, "sure_ms": 13},
    {"iz_id": "iz-b", "kokler": ["kok"], "olaylar": ["kok"], "baslangic_ms": 20, "bitis_ms": 28, "sure_ms": 8},
]
def sozlesme(fn):
    try:
        once = copy.deepcopy(O)
        if fn(O) != BEKLENEN or O != once or fn(list(reversed(O))) != BEKLENEN or fn([]) != []:
            return False
        es_zamanli = [O[0], dict(O[0], olay_id="cocuk", parent_id="kok", tur="model")]
        if fn(es_zamanli)[0]["olaylar"] != ["cocuk", "kok"]:
            return False
        for olaylar in [
            None, {}, [None], O + [O[0]],
            [dict(O[0], parent_id="yok")],
            [dict(O[1], parent_id="kok")],
            [dict(O[1], zaman_ms=-1)], [dict(O[1], sure_ms=float("nan"))],
            [dict(O[1], zaman_ms=True)], [dict(O[1], sure_ms="x")],
            [dict(O[0], iz_id="")], [dict(O[0], iz_id=" x")], [dict(O[0], olay_id=None)],
            [dict(O[1], alanlar={"prompt": "x"})],
            [dict(O[0], parent_id="kok", olay_id="x")],
            [dict(O[1], parent_id="arac"), dict(O[2], zaman_ms=20)],
            [dict(O[1], parent_id="arac"), dict(O[3], parent_id="model")],
        ]:
            try:
                fn(olaylar)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(iz_zinciri_raporu), "parent kapsamı, döngü, zaman sınırı ve trace süresi korunmalı")
def m_parent(olaylar):
    degisen = [dict(x, parent_id=None) for x in olaylar]
    return iz_zinciri_raporu(degisen)
def m_sure(olaylar):
    sonuc = iz_zinciri_raporu(olaylar)
    for x in sonuc:
        x["sure_ms"] = sum(o["sure_ms"] for o in olaylar if o["iz_id"] == x["iz_id"])
    return sonuc
def m_sira(olaylar):
    sonuc = iz_zinciri_raporu(olaylar)
    for x in sonuc:
        x["olaylar"].sort(reverse=True)
    return sonuc
for ad, mutant in [("parent ilişkisini silen", m_parent), ("süreleri toplayan", m_sure), ("olay sırasını bozan", m_sira)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def iz_zinciri_raporu(olaylar):
    import math
    if not isinstance(olaylar, list):
        raise ValueError("olay listesi geçersiz")
    izler = {}
    kimlikler = set()
    for olay in olaylar:
        if not isinstance(olay, dict):
            raise ValueError("olay geçersiz")
        if set(olay) != {"iz_id", "olay_id", "parent_id", "tur", "zaman_ms", "sure_ms", "alanlar"}:
            raise ValueError("olay şeması geçersiz")
        for alan in ("iz_id", "olay_id"):
            if not isinstance(olay[alan], str) or not olay[alan] or olay[alan] != olay[alan].strip():
                raise ValueError("kimlik geçersiz")
        if olay["tur"] not in ("http", "model", "guardrail", "arac"):
            raise ValueError("olay türü geçersiz")
        for alan in ("zaman_ms", "sure_ms"):
            deger = olay[alan]
            if isinstance(deger, bool) or not isinstance(deger, (int, float)):
                raise ValueError("süre türü geçersiz")
            if not math.isfinite(deger):
                raise ValueError("süre sonlu olmalı")
            if deger < 0:
                raise ValueError("süre negatif olamaz")
        if not isinstance(olay["alanlar"], dict):
            raise ValueError("alanlar geçersiz")
        izinli = {"durum", "hata_kodu"} | {"http": {"http_kod", "yontem"}, "model": {"model", "token_in", "token_out"}, "guardrail": {"karar"}, "arac": {"arac"}}[olay["tur"]]
        if any(a not in izinli for a in olay["alanlar"]):
            raise ValueError("hassas alan")
        kimlik = (olay["iz_id"], olay["olay_id"])
        if kimlik in kimlikler:
            raise ValueError("olay kimliği yinelenemez")
        kimlikler.add(kimlik)
        izler.setdefault(olay["iz_id"], []).append(olay)
    sonuc = []
    for iz_id in sorted(izler):
        kayitlar = izler[iz_id]
        id_map = {x["olay_id"]: x for x in kayitlar}
        for olay in kayitlar:
            parent = olay["parent_id"]
            if parent is None:
                continue
            if not isinstance(parent, str):
                raise ValueError("parent kimliği geçersiz")
            if parent not in id_map:
                raise ValueError("parent aynı trace içinde olmalı")
            if id_map[parent]["zaman_ms"] > olay["zaman_ms"]:
                raise ValueError("parent zamanı geçersiz")
            gorulen = set()
            yuruyen = olay["olay_id"]
            while yuruyen is not None:
                if yuruyen in gorulen:
                    raise ValueError("parent döngüsü")
                gorulen.add(yuruyen)
                yuruyen = id_map[yuruyen]["parent_id"]
        sirali = sorted(kayitlar, key=lambda x: (x["zaman_ms"], x["olay_id"]))
        baslangic = min(x["zaman_ms"] for x in kayitlar)
        bitis = max(x["zaman_ms"] + x["sure_ms"] for x in kayitlar)
        sonuc.append({"iz_id": iz_id, "kokler": [x["olay_id"] for x in sirali if x["parent_id"] is None], "olaylar": [x["olay_id"] for x in sirali], "baslangic_ms": baslangic, "bitis_ms": bitis, "sure_ms": bitis - baslangic})
    return sonuc
```

```hint
Trace'leri önce `iz_id` ile grupla. Her grup içinde olay kimliği haritası kur, parent ve döngüyü bu haritada denetle; süreyi minimum başlangıç ve maksimum bitişten hesapla.
```
:::

::: anlat Telemetri özeti içerik yerine ölçüm taşır
Sayısal özet; olay, trace, hata, ret ve token sayılarını toplar. Tür bazında ortalama süre, hangi aşamanın yavaşladığını gösterir. Hata, `durum = hata` veya `hata_kodu` bulunmasıyla belirlenir. Guardrail'in `reddet` kararı teknik hata değildir ve ayrı sayılır.

Ortalama süre üç ondalık basamağa yuvarlanır. Çıktı yalnız sabit ölçüm alanları ve olay türü anahtarları içerir; kullanıcı kimliği, model girdisi veya serbest metin taşımaz.
:::

::: gorev 3 · Tür bazında güvenli telemetri metrikleri hesapla
`telemetri_metrik_raporu(olaylar)` işlevini yaz. Olaylar ilk görevdeki bütün şema, tür ve alan kurallarını sağlasın; olay kimliklerinin trace içinde yinelenmediğini de doğrula. Geçersiz veride `ValueError` yükselt.

Dönüş:

```text
{"toplam":N,"iz_sayisi":N,"hatali":N,"reddedildi":N,
 "token_in":N,"token_out":N,
 "turler":{TUR:{"sayi":N,"ortalama_sure_ms":ORT},...}}
```

`hatali`, durumu `hata` olan veya `hata_kodu` taşıyan olay sayısıdır; aynı olay iki koşulda da bir kez sayılır. `reddedildi`, `karar = reddet` olaylarıdır. Token alanları bulunmadığında sıfır kabul edilir. Türleri alfabetik sıralı sözlükte, her ortalama süreyi üç ondalığa yuvarlanmış şekilde döndür. Boş girdi için türler boş, sayaçlar sıfır olur. Girdiyi değiştirme.

```starter
def telemetri_metrik_raporu(olaylar):
    return {}
```

```test
import copy
O = [
    {"iz_id": "a", "olay_id": "h1", "parent_id": None, "tur": "http", "zaman_ms": 0, "sure_ms": 10, "alanlar": {"http_kod": 200}},
    {"iz_id": "a", "olay_id": "m1", "parent_id": "h1", "tur": "model", "zaman_ms": 1, "sure_ms": 1, "alanlar": {"token_in": 3, "token_out": 2, "durum": "hata"}},
    {"iz_id": "b", "olay_id": "m2", "parent_id": None, "tur": "model", "zaman_ms": 0, "sure_ms": 2, "alanlar": {"token_in": 4, "hata_kodu": "E1"}},
    {"iz_id": "b", "olay_id": "g1", "parent_id": "m2", "tur": "guardrail", "zaman_ms": 2, "sure_ms": 2, "alanlar": {"karar": "reddet", "durum": "hata", "hata_kodu": "E2"}},
]
BEKLENEN = {"toplam": 4, "iz_sayisi": 2, "hatali": 3, "reddedildi": 1, "token_in": 7, "token_out": 2, "turler": {"guardrail": {"sayi": 1, "ortalama_sure_ms": 2.0}, "http": {"sayi": 1, "ortalama_sure_ms": 10.0}, "model": {"sayi": 2, "ortalama_sure_ms": 1.5}}}
def sozlesme(fn):
    try:
        once = copy.deepcopy(O)
        if fn(O) != BEKLENEN or O != once or fn(list(reversed(O))) != BEKLENEN:
            return False
        if fn([]) != {"toplam": 0, "iz_sayisi": 0, "hatali": 0, "reddedildi": 0, "token_in": 0, "token_out": 0, "turler": {}}:
            return False
        uc = [dict(O[0], olay_id=str(i), sure_ms=x) for i, x in enumerate((1, 2, 2))]
        if fn(uc)["turler"]["http"]["ortalama_sure_ms"] != 1.667:
            return False
        if fn([dict(O[0], sure_ms=0)])["turler"]["http"]["ortalama_sure_ms"] != 0.0:
            return False
        for kod in (100, 599):
            if fn([dict(O[0], alanlar={"http_kod": kod})])["toplam"] != 1:
                return False
        sifir_token = fn([dict(O[1], alanlar={"token_in": 0, "token_out": 0})])
        if sifir_token["token_in"] != 0 or sifir_token["token_out"] != 0 or sifir_token["hatali"] != 0:
            return False
        for olaylar in [
            None, {}, [None], O + [O[0]], [dict(O[0], ek=1)],
            [dict(O[0], zaman_ms=True)], [dict(O[0], sure_ms=float("nan"))],
            [dict(O[0], iz_id="")], [dict(O[0], iz_id=" x")], [dict(O[0], olay_id=None)],
            [dict(O[0], alanlar={"prompt": "x"})],
            [dict(O[1], alanlar={"token_in": True})],
            [dict(O[0], alanlar={"http_kod": 99})],
            [dict(O[0], alanlar={"http_kod": 600})],
        ]:
            try:
                fn(olaylar)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(telemetri_metrik_raporu), "hata ve ret ayrımı, token toplamları ve yuvarlanmış ortalamalar korunmalı")
def m_hata(olaylar):
    sonuc = telemetri_metrik_raporu(olaylar)
    sonuc["hatali"] = sum(1 for o in olaylar if o["alanlar"].get("durum") == "hata")
    return sonuc
def m_ret(olaylar):
    sonuc = telemetri_metrik_raporu(olaylar)
    sonuc["reddedildi"] = sonuc["hatali"]
    return sonuc
def m_ortalama(olaylar):
    sonuc = telemetri_metrik_raporu(olaylar)
    for x in sonuc["turler"].values():
        x["ortalama_sure_ms"] += 1
    return sonuc
for ad, mutant in [("hata kodunu saymayan", m_hata), ("ret sayısını hataya eşitleyen", m_ret), ("ortalama süreyi bozan", m_ortalama)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def telemetri_metrik_raporu(olaylar):
    import math
    if not isinstance(olaylar, list):
        raise ValueError("olay listesi geçersiz")
    kimlikler = set()
    gruplar = {}
    hatali = 0
    reddedildi = 0
    token_in = 0
    token_out = 0
    for olay in olaylar:
        if not isinstance(olay, dict) or set(olay) != {"iz_id", "olay_id", "parent_id", "tur", "zaman_ms", "sure_ms", "alanlar"}:
            raise ValueError("olay şeması geçersiz")
        for alan in ("iz_id", "olay_id"):
            if not isinstance(olay[alan], str) or not olay[alan] or olay[alan] != olay[alan].strip():
                raise ValueError("kimlik geçersiz")
        anahtar = (olay["iz_id"], olay["olay_id"])
        if anahtar in kimlikler:
            raise ValueError("olay kimliği yinelenemez")
        kimlikler.add(anahtar)
        tur = olay["tur"]
        if tur not in ("http", "model", "guardrail", "arac"):
            raise ValueError("olay türü geçersiz")
        for alan in ("zaman_ms", "sure_ms"):
            deger = olay[alan]
            if isinstance(deger, bool) or not isinstance(deger, (int, float)):
                raise ValueError("süre türü geçersiz")
            if not math.isfinite(deger):
                raise ValueError("süre sonlu olmalı")
            if deger < 0:
                raise ValueError("süre negatif olamaz")
        alanlar = olay["alanlar"]
        if not isinstance(alanlar, dict):
            raise ValueError("alanlar geçersiz")
        izinli = {"durum", "hata_kodu"} | {"http": {"http_kod", "yontem"}, "model": {"model", "token_in", "token_out"}, "guardrail": {"karar"}, "arac": {"arac"}}[tur]
        if any(a not in izinli for a in alanlar):
            raise ValueError("hassas alan")
        if "durum" in alanlar and alanlar["durum"] not in ("ok", "hata"):
            raise ValueError("durum geçersiz")
        if "karar" in alanlar and alanlar["karar"] not in ("izin", "reddet", "hata"):
            raise ValueError("karar geçersiz")
        if "http_kod" in alanlar:
            kod = alanlar["http_kod"]
            if type(kod) is not int:
                raise ValueError("HTTP kodu türü geçersiz")
            if kod < 100:
                raise ValueError("HTTP kodu küçük")
            if kod > 599:
                raise ValueError("HTTP kodu büyük")
        for alan in ("token_in", "token_out"):
            if alan in alanlar:
                deger = alanlar[alan]
                if type(deger) is not int:
                    raise ValueError("token sayısı türü geçersiz")
                if deger < 0:
                    raise ValueError("token sayısı negatif olamaz")
        if alanlar.get("durum") == "hata":
            hatali += 1
        elif "hata_kodu" in alanlar:
            hatali += 1
        if alanlar.get("karar") == "reddet":
            reddedildi += 1
        token_in += alanlar.get("token_in", 0)
        token_out += alanlar.get("token_out", 0)
        gruplar.setdefault(tur, []).append(olay["sure_ms"])
    turler = {}
    for tur in sorted(gruplar):
        sureler = gruplar[tur]
        turler[tur] = {"sayi": len(sureler), "ortalama_sure_ms": round(sum(sureler) / len(sureler), 3)}
    return {"toplam": len(olaylar), "iz_sayisi": len({x["iz_id"] for x in olaylar}), "hatali": hatali, "reddedildi": reddedildi, "token_in": token_in, "token_out": token_out, "turler": turler}
```

```hint
Her olayı doğrularken sayaçları ve türe göre süre listelerini biriktir. Hata için iki koşulu tek bir karar olarak ele al; aynı olayı iki kez artırma.
```
:::

::: anlat Telemetri gerçek trafikten üretilir, içerik taşımaz
Buraya kadar telemetri olayları sentetik fixture'dı. Gerçekte bu olaylar canlı trafikten üretilir: her model çağrısı bir gecikme (sure_ms) ve token sayısı (token_out) bırakır — ama güvenli telemetri bu ölçüleri alır, istem ve yanıt **metnini** almaz. Son görevde senin `telemetri_metrik_raporu` işlevin, yerel modele yapılan **gerçek isteklerden** üretilmiş telemetri olaylarını toplar: süreler ve tokenlar gerçektir, hiçbir olay ham istem içermez. Deney ayrıca olaylarda istem metninin sızmadığını doğrular — telemetrinin kendisi bir sızıntı yüzeyi olmamalıdır.
:::

::: gorev Gerçek deney · Gerçek trafikten güvenli telemetri metrikleri
`telemetri_metrik_raporu(olaylar)` işlevini yaz — kuralları ve çıktısı 3. görevdekiyle **aynıdır**. Deney yerel modele birkaç gerçek istek atar, her birinden gerçek süre ve çıktı token sayısı taşıyan (ham istem/yanıt taşımayan) bir model telemetri olayı kurar ve senin raporun bunları toplar.

```meta
motor: ai-gercek
gereksinim: ollama
timeout: 300
```

```starter
import ai_lab

def telemetri_metrik_raporu(olaylar):
    return {}

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_savunma_04 as deney
    deney.goster(telemetri_metrik_raporu)
```

```test
import ai_lab
sonuclar = []
def kontrol(kosul, mesaj):
    sonuclar.append(bool(kosul))
    return ok(kosul, mesaj)
sorun = ai_lab.kod_denetimi(src, ("referans", "referans_rapor", "getattr"))
kontrol(not sorun, "laboratuvar yamalanmamalı, referans kullanılmamalı " + ", ".join(sorun))
fn = need("telemetri_metrik_raporu")
from sandbox import ai_gercek_ai_savunma_04 as D
ornek = [{"iz_id": "a", "olay_id": "m1", "parent_id": None, "tur": "model", "zaman_ms": 0, "sure_ms": 12.0, "alanlar": {"model": "yerel", "token_out": 5, "durum": "ok"}},
         {"iz_id": "a", "olay_id": "g1", "parent_id": "m1", "tur": "guardrail", "zaman_ms": 1, "sure_ms": 2, "alanlar": {"karar": "reddet"}}]
def sozlesme(f):
    try:
        if f([dict(o, alanlar=dict(o["alanlar"])) for o in ornek]) != D.referans_rapor(ornek) or f([]) != {"toplam": 0, "iz_sayisi": 0, "hatali": 0, "reddedildi": 0, "token_in": 0, "token_out": 0, "turler": {}}:
            return False
        for ol in [None, [None], ornek + [ornek[0]], [dict(ornek[0], ek=1)], [dict(ornek[0], alanlar={"prompt": "x"})],
                   [dict(ornek[0], sure_ms=-1)], [dict(ornek[0], iz_id="")], [dict(ornek[0], alanlar={"token_out": True, "model": "y"})]]:
            try:
                f(ol)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
kontrol(sozlesme(fn), "güvenli telemetri metrikleri doğru; hassas alan ve geçersiz girdi reddedilmeli")
r, oz = None, None
if all(sonuclar):
    try:
        r = D.deney(fn)
    except ai_lab.GercekLabYok as e:
        kontrol(False, f"GERÇEK MODEL YOK, deney yapılmadı: {e}")
        stop()
    kontrol(r["rapor"] == D.referans_rapor(r["olaylar"]), "gerçek telemetri metrikleri bağımsız hesapla aynı")
    kontrol(not r["sizan_istem"], f"telemetri olaylarında ham istem sızmadı (sızan: {r['sizan_istem'] or 'yok'})")
    oz = D.ozet(r)
    kontrol(oz["token_out"] > 0 and oz["olay"] > 0, f"gerçek token/süre ölçüldü: {oz['olay']} olay, token_out {oz['token_out']}, ort süre {oz['model_ort_sure_ms']} ms")
yol = ai_lab.kanit_yaz("savunma-telemetri", {"kaynak": "gercek", "kabul": all(sonuclar), "ders": "ai-savunma-04",
                                             "ortam": (r or {}).get("ortam"), "ozet": oz})
if oz:
    ok(True, f"BULGU ({r['ortam']['model']['ad']}): {oz['olay']} gerçek istekten telemetri — token_out {oz['token_out']}, model ort süre {oz['model_ort_sure_ms']} ms; "
             f"sızan ham istem: {oz['sizan_istem']}. Telemetri gerçek ölçüleri taşır ama içerik taşımaz.")
```

```solution
import math
import ai_lab

def telemetri_metrik_raporu(olaylar):
    if not isinstance(olaylar, list):
        raise ValueError("olay listesi geçersiz")
    kimlikler, gruplar = set(), {}
    hatali = reddedildi = token_in = token_out = 0
    for olay in olaylar:
        if not isinstance(olay, dict) or set(olay) != {"iz_id", "olay_id", "parent_id", "tur", "zaman_ms", "sure_ms", "alanlar"}:
            raise ValueError("olay şeması geçersiz")
        for alan in ("iz_id", "olay_id"):
            if not isinstance(olay[alan], str) or not olay[alan] or olay[alan] != olay[alan].strip():
                raise ValueError("kimlik geçersiz")
        anahtar = (olay["iz_id"], olay["olay_id"])
        if anahtar in kimlikler:
            raise ValueError("olay kimliği yinelenemez")
        kimlikler.add(anahtar)
        tur = olay["tur"]
        if tur not in ("http", "model", "guardrail", "arac"):
            raise ValueError("olay türü geçersiz")
        for alan in ("zaman_ms", "sure_ms"):
            d = olay[alan]
            if isinstance(d, bool) or not isinstance(d, (int, float)) or not math.isfinite(d) or d < 0:
                raise ValueError("süre geçersiz")
        alanlar = olay["alanlar"]
        if not isinstance(alanlar, dict):
            raise ValueError("alanlar geçersiz")
        izinli = {"durum", "hata_kodu"} | {"http": {"http_kod", "yontem"}, "model": {"model", "token_in", "token_out"}, "guardrail": {"karar"}, "arac": {"arac"}}[tur]
        if any(a not in izinli for a in alanlar):
            raise ValueError("hassas alan")
        if "durum" in alanlar and alanlar["durum"] not in ("ok", "hata"):
            raise ValueError("durum geçersiz")
        if "hata_kodu" in alanlar and (not isinstance(alanlar["hata_kodu"], str) or not alanlar["hata_kodu"]):
            raise ValueError("hata kodu geçersiz")
        if "karar" in alanlar and alanlar["karar"] not in ("izin", "reddet", "hata"):
            raise ValueError("karar geçersiz")
        if "http_kod" in alanlar and (type(alanlar["http_kod"]) is not int or not 100 <= alanlar["http_kod"] <= 599):
            raise ValueError("HTTP kodu geçersiz")
        for alan in ("token_in", "token_out"):
            if alan in alanlar and (type(alanlar[alan]) is not int or alanlar[alan] < 0):
                raise ValueError("token sayısı geçersiz")
        if alanlar.get("durum") == "hata" or "hata_kodu" in alanlar:
            hatali += 1
        if alanlar.get("karar") == "reddet":
            reddedildi += 1
        token_in += alanlar.get("token_in", 0)
        token_out += alanlar.get("token_out", 0)
        gruplar.setdefault(tur, []).append(olay["sure_ms"])
    turler = {t: {"sayi": len(v), "ortalama_sure_ms": round(sum(v) / len(v), 3)} for t, v in sorted(gruplar.items())}
    return {"toplam": len(olaylar), "iz_sayisi": len({x["iz_id"] for x in olaylar}), "hatali": hatali,
            "reddedildi": reddedildi, "token_in": token_in, "token_out": token_out, "turler": turler}

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_savunma_04 as deney
    deney.goster(telemetri_metrik_raporu)
```

```hint
Bu işlev 3. görevdeki `telemetri_metrik_raporu` ile birebir aynıdır; tek fark, olayların gerçek model çağrılarından gelmesidir. Her olayı doğrula, hassas alanı reddet; türe göre süreleri biriktir ve ortalamayı 3 ondalığa yuvarla. Hata sayısında durum=hata ve hata_kodu'nu tek karar olarak ele al.
```
:::
