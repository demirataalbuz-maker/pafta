---
id: ai-saldiri-10
title: Yapılandırılmış Çıktı ve Ayrıştırıcı Atlatma
summary: Model çıktısındaki JSON'u katı biçimde ayrıştır, yinelenen anahtarları ve özel sayıları reddet, şema doğrulamasından sonra yalnız izinli iç komut üret.
timeout: 45
---

::: anlat JSON'a benzemesi JSON sözleşmesini sağlamaz
Modelden yapılandırılmış çıktı istemek, çıktının her zaman tek bir geçerli JSON belgesi olacağını garanti etmez. Kod çiti, açıklama, ek metin, yinelenen anahtar, yanlış tür veya `NaN` gibi standart dışı değerler görülebilir. Uygulama ile başka bir ayrıştırıcı bunları farklı yorumlarsa **parser differential** oluşur.

Bu derste dar bir sözleşme kullanıyoruz:

1. Girdi tek JSON belgesidir; başında ve sonunda yalnız whitespace olabilir.
2. Yinelenen object anahtarı kabul edilmez; son değeri sessizce kullanmayız.
3. `NaN`, `Infinity`, `-Infinity` kabul edilmez.
4. Ayrıştırmadan sonra alan adları ve türler ayrıca doğrulanır.
5. Doğrulanan eylem adı doğrudan fonksiyon veya araç adı olarak çalıştırılmaz; iç komut allowlist'inden geçer.

```python
import json
metin = '{"eylem":"ozetle","guvence":0.9}'
veri, bitis = json.JSONDecoder().raw_decode(metin)
print(veri["eylem"], bitis == len(metin))
print(json.loads('{"a":1,"a":2}'))
```

Son örnekte standart `json.loads` yinelenen anahtarda son değeri tutar. Bizim katı çözümümüz bunu hata yapacak. Ders gerçek model çağırmaz; saldırı örnekleri zararsız metin fixture'larıdır.
:::

::: tahmin
Katı ayrıştırıcı yinelenen anahtarı ve sondaki ek metni reddediyor. Üç çıktı satırını yaz:

```python
import json
ornekler = [
    '{"a":1}',
    '{"a":1,"a":2}',
    '{"a":1} ek',
]
for metin in ornekler:
    try:
        veri, bitis = json.JSONDecoder().raw_decode(metin)
        print(bitis == len(metin), veri)
    except json.JSONDecodeError:
        print("HATA")
print(json.loads('{"a":1,"a":2}'))
```

???

```cikti
True {'a': 1}
True {'a': 2}
False {'a': 1}
{'a': 2}
```

Standart ayrıştırıcı ikinci örnekte yinelenen anahtarın son değerini tutar; `raw_decode` ise sondaki `ek` metnini kendiliğinden tüketmez. Katı çözüm bu iki durumu ayrıca reddeder.
:::

::: gorev 1 · Tek ve katı JSON belgesi ayrıştır
`kati_json(metin)` işlevini yaz. Girdi string değilse veya boşsa `ValueError` yükselt. Baş ve sondaki whitespace'i kabul et; kod çiti veya başka ek metin kabul etme. `json.JSONDecoder.raw_decode` kullanarak tam belgeyi ayrıştır.

Bütün object düzeylerinde yinelenen anahtarı `ValueError` yap. `NaN`, `Infinity` ve `-Infinity` değerlerini de `ValueError` ile reddet. Geçerli JSON değerini dön; string, liste veya sayı gibi nesne olmayan kök değerler bu görevde kabul edilir. Ayrıştırma hatasını sahte boş değerle gizleme; `ValueError` olarak yükselt.

```starter
def kati_json(metin):
    return None
```

```test
def sozlesme(fn):
    try:
        if fn(' {"a":1,"b":[true,null]} \n') != {"a": 1, "b": [True, None]}:
            return False
        if fn('"Pafta"') != "Pafta" or fn('[1,2]') != [1, 2] or fn('0') != 0:
            return False
        for metin in [
            '', '   ', '```json\n{"a":1}\n```', '{"a":1} ek', '{"a":1}{"b":2}',
            '{"a":1,"a":2}', '{"a":{"b":1,"b":2}}', '{"a":NaN}', '{"a":Infinity}', '{"a":-Infinity}',
            '{"a":}', '[1,2', None, 3,
        ]:
            try:
                fn(metin)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(kati_json), "tam tüketim, yinelenen anahtar, özel sayı ve tür denetimi korunmalı")
def m_loads(metin):
    import json
    return json.loads(metin)
def m_ilk(metin):
    import json
    return json.JSONDecoder().raw_decode(metin.strip())[0]
def m_sondan(metin):
    import json
    return json.loads(metin.split('```')[1])
for ad, mutant in [("yinelenen anahtarı ve NaN kabul eden", m_loads), ("sondaki metni yok sayan", m_ilk), ("kod çitini tahmin eden", m_sondan)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
import json

def kati_json(metin):
    if not isinstance(metin, str) or not metin.strip():
        raise ValueError("tek JSON belgesi gerekli")
    def nesne(parcalar):
        sonuc = {}
        for anahtar, deger in parcalar:
            if anahtar in sonuc:
                raise ValueError("yinelenen anahtar")
            sonuc[anahtar] = deger
        return sonuc
    def sabit(deger):
        raise ValueError("standart dışı sayı")
    decoder = json.JSONDecoder(object_pairs_hook=nesne, parse_constant=sabit)
    kaynak = metin.strip()
    try:
        veri, bitis = decoder.raw_decode(kaynak)
    except json.JSONDecodeError as e:
        raise ValueError("geçersiz JSON") from e
    if bitis != len(kaynak):
        raise ValueError("JSON sonrası ek içerik")
    return veri
```

```hint
`object_pairs_hook` her object için anahtar-değer çiftlerini verir; burada tekrar denetlenebilir. `raw_decode` dönüşündeki bitiş konumu temizlenmiş stringin uzunluğuna eşit olmalıdır.
```
:::

::: anlat Ayrıştırma ile yetkilendirme farklı katmanlardır
Geçerli JSON, güvenli komut demek değildir. `{"eylem":"dosya_sil"}` sözdizimsel olarak kusursuz olabilir; uygulama şemasında ve yetki politikasında yoksa reddedilir. Şema doğrulamasında ek alanları sessizce bırakmak da iki katmanın aynı belgeyi farklı görmesine yol açabilir. Bu derste tam anahtar kümesi zorunludur.

Python'da `bool`, `int` alt sınıfıdır. Bu yüzden güvence değeri `True` olduğunda `isinstance(deger, int)` kontrolü onu sayı sanabilir. Açık bool reddi ve sonlu sayı denetimi gerekir. Metin için otomatik `str(...)` dönüşümü, güvence için `float(...)` dönüşümü yapmayız; türü değiştirmek hatayı görünmez kılar.
:::

::: gorev 2 · Karar şemasını türleri bozmadan doğrula
`karar_dogrula(veri)` işlevini yaz. Kök dict olmalı ve tam olarak `eylem`, `metin`, `guvence` anahtarlarını taşımalıdır.

- `eylem`: `ozetle`, `cevir` veya `yoksay`.
- `metin`: 1–120 karakterli string.
- `guvence`: bool olmayan `int` veya `float`; sonlu ve `0 <= guvence <= 1`.

Bütün kurallar sağlanırsa alanları aynı değerlerle taşıyan yeni dict dön; girdiyi değiştirme. Aksi durumda `ValueError` yükselt. Ek alan kabul etme, tür dönüşümü yapma.

```starter
def karar_dogrula(veri):
    return {}
```

```test
import copy
KARAR = {"eylem": "ozetle", "metin": "Pafta", "guvence": 0.8}
def sozlesme(fn):
    try:
        once = copy.deepcopy(KARAR)
        sonuc = fn(KARAR)
        if sonuc != KARAR or sonuc is KARAR or KARAR != once:
            return False
        for deger in [
            {"eylem": "cevir", "metin": "a", "guvence": 0},
            {"eylem": "yoksay", "metin": "b" * 120, "guvence": 1},
        ]:
            if fn(deger) != deger:
                return False
        for deger in [
            None, [], dict(KARAR, ek=1), {"eylem": "ozetle", "metin": "x"},
            dict(KARAR, eylem="dosya_sil"), dict(KARAR, eylem=1),
            dict(KARAR, metin=""), dict(KARAR, metin="x" * 121), dict(KARAR, metin=3),
            dict(KARAR, guvence=True), dict(KARAR, guvence="0.8"),
            dict(KARAR, guvence=-0.1), dict(KARAR, guvence=1.1),
            dict(KARAR, guvence=float("nan")), dict(KARAR, guvence=float("inf")),
        ]:
            try:
                fn(deger)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(karar_dogrula), "tam şema, bool reddi, uzunluk ve sonlu aralık birlikte korunmalı")
def m_ek_alan(veri):
    return {k: veri[k] for k in ("eylem", "metin", "guvence") if k in veri}
def m_donustur(veri):
    return {"eylem": str(veri["eylem"]), "metin": str(veri["metin"]), "guvence": float(veri["guvence"])}
def m_bool(veri):
    sonuc = karar_dogrula(veri)
    return sonuc
for ad, mutant in [("ek alanı ve eksik şemayı kabul eden", m_ek_alan), ("türleri zorla dönüştüren", m_donustur)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
import math

def karar_dogrula(veri):
    if not isinstance(veri, dict) or set(veri) != {"eylem", "metin", "guvence"}:
        raise ValueError("karar şeması geçersiz")
    if veri["eylem"] not in ("ozetle", "cevir", "yoksay"):
        raise ValueError("eylem izinli değil")
    if not isinstance(veri["metin"], str) or not 1 <= len(veri["metin"]) <= 120:
        raise ValueError("metin 1..120 karakter olmalı")
    guvence = veri["guvence"]
    if isinstance(guvence, bool) or not isinstance(guvence, (int, float)):
        raise ValueError("güvence sayı olmalı")
    if not math.isfinite(guvence) or not 0 <= guvence <= 1:
        raise ValueError("güvence 0..1 olmalı")
    return {"eylem": veri["eylem"], "metin": veri["metin"], "guvence": guvence}
```

```hint
Önce dict ve tam anahtar kümesini denetle. `math.isfinite` ile `NaN`/sonsuzluğu ayır; güvence için `isinstance(guvence, bool)` kontrolünü sayı kontrolünden önce yap.
```
:::

::: anlat Modelin verdiği ad çalıştırılabilir adres değildir
`getattr(modul, veri["eylem"])` veya `eval` ile model çıktısını doğrudan çağırmak, şema doğrulamasını yetki sistemi sanmaktır. Uygulamanın desteklediği az sayıdaki iç komut açık eşleştirmeyle seçilir. Güvence eşiğinin altındaki karar da otomatik işlem yerine inceleme yoluna gider.

Bu derste iç komutlar `OZET`, `CEVIR`, `YOKSAY`, `INCELE`; bunlar yalnız veri etiketleridir, araç çağrısı değildir. Eşik `0.75`'tir. Eşik altında `INCELE` döner ve model metni komut kaydına taşınmaz. Bu eşik güvenlik garantisi değildir; yalnız fixture politikasının açık ve test edilebilir kuralıdır.
:::

::: gorev 3 · Doğrulanmış kararı izinli iç komuta çevir
`komut_uret(veri)` işlevini yaz. İkinci görevdeki şemayı bağımsız olarak doğrula. `eylem` eşleşmesi `ozetle → OZET`, `cevir → CEVIR`, `yoksay → YOKSAY` olsun.

`guvence >= 0.75` ise `{"komut": eslesen-komut, "icerik": metin}` dön. Daha düşük güvencede `{"komut": "INCELE", "icerik": ""}` dön. Başka eylem, ek alan, yanlış tür veya geçersiz güvence `ValueError` olmalı. `eval`, `exec`, `getattr` veya dinamik modül çağrısı kullanma; girdiyi değiştirme.

```starter
def komut_uret(veri):
    return {}
```

```test
import copy
def sozlesme(fn):
    try:
        for veri, beklenen in [
            ({"eylem": "ozetle", "metin": "Pafta", "guvence": 0.75}, {"komut": "OZET", "icerik": "Pafta"}),
            ({"eylem": "cevir", "metin": "Merhaba", "guvence": 1}, {"komut": "CEVIR", "icerik": "Merhaba"}),
            ({"eylem": "cevir", "metin": "x", "guvence": 0}, {"komut": "INCELE", "icerik": ""}),
            ({"eylem": "cevir", "metin": "b" * 120, "guvence": 1}, {"komut": "CEVIR", "icerik": "b" * 120}),
            ({"eylem": "yoksay", "metin": "not", "guvence": 0.9}, {"komut": "YOKSAY", "icerik": "not"}),
            ({"eylem": "ozetle", "metin": "gizli", "guvence": 0.74}, {"komut": "INCELE", "icerik": ""}),
        ]:
            once = copy.deepcopy(veri)
            if fn(veri) != beklenen or veri != once:
                return False
        for veri in [
            {"eylem": "eval", "metin": "x", "guvence": 1},
            {"eylem": "ozetle", "metin": "x", "guvence": 1, "arac": "dosya_sil"},
            {"eylem": "ozetle", "metin": "x", "guvence": True},
            {"eylem": "ozetle", "metin": "x", "guvence": 1.1},
            {"eylem": "ozetle", "metin": "x", "guvence": "0.8"},
            {"eylem": "ozetle", "metin": "x", "guvence": float("nan")},
            {"eylem": "ozetle", "metin": "x", "guvence": float("inf")},
            {"eylem": "ozetle", "metin": "", "guvence": 1},
            {"eylem": "ozetle", "metin": "x" * 121, "guvence": 1},
            {"eylem": "ozetle", "metin": 3, "guvence": 1},
        ]:
            try:
                fn(veri)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(komut_uret), "sabit eşleme, eşik sınırı, inceleme yolu ve şema korunmalı")
def m_dinamik(veri):
    return {"komut": veri["eylem"].upper(), "icerik": veri["metin"]}
def m_esik(veri):
    sonuc = komut_uret(veri)
    if sonuc["komut"] == "INCELE":
        sonuc = {"komut": "OZET", "icerik": veri["metin"]}
    return sonuc
def m_ek(veri):
    return {"komut": "OZET", "icerik": veri["metin"]}
for ad, mutant in [("model adını komut yapan", m_dinamik), ("düşük güvenceyi çalıştıran", m_esik), ("şemayı atlayan", m_ek)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
import math

def komut_uret(veri):
    if not isinstance(veri, dict) or set(veri) != {"eylem", "metin", "guvence"}:
        raise ValueError("karar şeması geçersiz")
    esleme = {"ozetle": "OZET", "cevir": "CEVIR", "yoksay": "YOKSAY"}
    if veri["eylem"] not in esleme:
        raise ValueError("eylem izinli değil")
    if not isinstance(veri["metin"], str) or not 1 <= len(veri["metin"]) <= 120:
        raise ValueError("metin geçersiz")
    guvence = veri["guvence"]
    if isinstance(guvence, bool) or not isinstance(guvence, (int, float)) or not math.isfinite(guvence) or not 0 <= guvence <= 1:
        raise ValueError("güvence geçersiz")
    if guvence < 0.75:
        return {"komut": "INCELE", "icerik": ""}
    return {"komut": esleme[veri["eylem"]], "icerik": veri["metin"]}
```

```hint
İç komutları literal dict ile eşle. Eşik altını erken `INCELE` dönüşüyle ayır; modelden gelen eylem adını çıktı komutuna doğrudan büyük harfle çevirme.
```
:::


::: anlat Gerçek JSON'un diskteki iş etkisini incele
[Sentetik ham JSON karar örneklerini aç](/data/ai-saldiri-10-json.txt). Dış dosya bir JSON listesidir; her `ham` alanının içindeki metin ayrı ayrıştırılacak model yanıtını temsil eder. Yinelenen anahtar ve `NaN` örnekleri eğitim için yazılmıştır, canlı model çıktısı değildir. Çalıştır ayrı kalıcı `calisma/ai-saldiri-10/kararlar.json` öğrenci kopyasını ve tam yolunu gösterir. Dış editör veya Python ile değiştirip tekrar çalıştır; sıfırlanmaz. 1–10 benzersiz `id` ve en çok 2000 karakterli `ham` kaydı kullan; en az bir izinli ve bir düşük güvenceli inceleme örneğini koru.

Yeni bölüm iki gerçek yerel model yanıtını da aynı ayrıştırma/şema/komut hattından geçirir. Model bozuk örneği düzeltirse veya kod çiti eklerse gözlenen gerçek çıktı kaydedilir; beklenen sabit cümle dayatılmaz. Doğru reddedilen canlı çıktı kabulü bozmaz, taşıma/yarım üretim hatası bozar.

İç komut bu kez yalnız sözlükte kalmaz: izinli iş gerçek SQLite `isler` kuyruğuna, düşük güvence `inceleme` kuyruğuna boş içerikle yazılır. Reddedilen girdinin hiçbir kuyruğa yazmaması ölçülür. Bağlantı kapanıp yeni bağlantıyla disk tekrar okunur. Bu, kuyruk adaptörü deneyidir; gerçek çeviri/özet üretildiği veya keyfi model komutlarının çalıştırıldığı iddiası yoktur. `dosya_sil` örneği hiçbir gerçek silme işlemi yapmaz. SQLite dosyası öğrenci alanında korunur; mevcut veriler silinmez. Test örnek dosyanı değiştirmekten bağımsız yeni veriler kullanır.
:::

::: gorev Gerçek deney · Katı JSON'dan gerçek iş kuyruğuna
Önceki üç işlevi birleştir: `kati_json`, `karar_dogrula`, `komut_uret`. Çalıştır, sentetik ve canlı ham kayıtları ayrı gösterir; her vaka için reddi/komutu ve SQLite değişim sayısını raporlar. Kontrol Et meşru akışın çalışmasını, düşük güvencenin incelemeye gitmesini ve geçersiz JSON'un sıfır kuyruk etkisi üretmesini doğrular. Modelin saldırı denemesine uyması şart değildir.

```meta
motor: ai-gercek
gereksinim: ollama
timeout: 300
```

```starter
import ai_lab

def kati_json(metin):return None

def karar_dogrula(veri):return {}

def komut_uret(veri):return {}

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_saldiri_10 as deney
    deney.goster(kati_json,karar_dogrula,komut_uret)

```

```test
def sozlesme(fn):
    try:
        if fn(' {"a":1,"b":[true,null]} \n') != {"a": 1, "b": [True, None]}:
            return False
        if fn('"Pafta"') != "Pafta" or fn('[1,2]') != [1, 2] or fn('0') != 0:
            return False
        for metin in [
            '', '   ', '```json\n{"a":1}\n```', '{"a":1} ek', '{"a":1}{"b":2}',
            '{"a":1,"a":2}', '{"a":{"b":1,"b":2}}', '{"a":NaN}', '{"a":Infinity}', '{"a":-Infinity}',
            '{"a":}', '[1,2', None, 3,
        ]:
            try:
                fn(metin)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(kati_json), "tam tüketim, yinelenen anahtar, özel sayı ve tür denetimi korunmalı")
def m_loads(metin):
    import json
    return json.loads(metin)
def m_ilk(metin):
    import json
    return json.JSONDecoder().raw_decode(metin.strip())[0]
def m_sondan(metin):
    import json
    return json.loads(metin.split('```')[1])
for ad, mutant in [("yinelenen anahtarı ve NaN kabul eden", m_loads), ("sondaki metni yok sayan", m_ilk), ("kod çitini tahmin eden", m_sondan)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)

import copy
KARAR = {"eylem": "ozetle", "metin": "Pafta", "guvence": 0.8}
def sozlesme(fn):
    try:
        once = copy.deepcopy(KARAR)
        sonuc = fn(KARAR)
        if sonuc != KARAR or sonuc is KARAR or KARAR != once:
            return False
        for deger in [
            {"eylem": "cevir", "metin": "a", "guvence": 0},
            {"eylem": "yoksay", "metin": "b" * 120, "guvence": 1},
        ]:
            if fn(deger) != deger:
                return False
        for deger in [
            None, [], dict(KARAR, ek=1), {"eylem": "ozetle", "metin": "x"},
            dict(KARAR, eylem="dosya_sil"), dict(KARAR, eylem=1),
            dict(KARAR, metin=""), dict(KARAR, metin="x" * 121), dict(KARAR, metin=3),
            dict(KARAR, guvence=True), dict(KARAR, guvence="0.8"),
            dict(KARAR, guvence=-0.1), dict(KARAR, guvence=1.1),
            dict(KARAR, guvence=float("nan")), dict(KARAR, guvence=float("inf")),
        ]:
            try:
                fn(deger)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(karar_dogrula), "tam şema, bool reddi, uzunluk ve sonlu aralık birlikte korunmalı")
def m_ek_alan(veri):
    return {k: veri[k] for k in ("eylem", "metin", "guvence") if k in veri}
def m_donustur(veri):
    return {"eylem": str(veri["eylem"]), "metin": str(veri["metin"]), "guvence": float(veri["guvence"])}
def m_bool(veri):
    sonuc = karar_dogrula(veri)
    return sonuc
for ad, mutant in [("ek alanı ve eksik şemayı kabul eden", m_ek_alan), ("türleri zorla dönüştüren", m_donustur)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)

import copy
def sozlesme(fn):
    try:
        for veri, beklenen in [
            ({"eylem": "ozetle", "metin": "Pafta", "guvence": 0.75}, {"komut": "OZET", "icerik": "Pafta"}),
            ({"eylem": "cevir", "metin": "Merhaba", "guvence": 1}, {"komut": "CEVIR", "icerik": "Merhaba"}),
            ({"eylem": "cevir", "metin": "x", "guvence": 0}, {"komut": "INCELE", "icerik": ""}),
            ({"eylem": "cevir", "metin": "b" * 120, "guvence": 1}, {"komut": "CEVIR", "icerik": "b" * 120}),
            ({"eylem": "yoksay", "metin": "not", "guvence": 0.9}, {"komut": "YOKSAY", "icerik": "not"}),
            ({"eylem": "ozetle", "metin": "gizli", "guvence": 0.74}, {"komut": "INCELE", "icerik": ""}),
        ]:
            once = copy.deepcopy(veri)
            if fn(veri) != beklenen or veri != once:
                return False
        for veri in [
            {"eylem": "eval", "metin": "x", "guvence": 1},
            {"eylem": "ozetle", "metin": "x", "guvence": 1, "arac": "dosya_sil"},
            {"eylem": "ozetle", "metin": "x", "guvence": True},
            {"eylem": "ozetle", "metin": "x", "guvence": 1.1},
            {"eylem": "ozetle", "metin": "x", "guvence": "0.8"},
            {"eylem": "ozetle", "metin": "x", "guvence": float("nan")},
            {"eylem": "ozetle", "metin": "x", "guvence": float("inf")},
            {"eylem": "ozetle", "metin": "", "guvence": 1},
            {"eylem": "ozetle", "metin": "x" * 121, "guvence": 1},
            {"eylem": "ozetle", "metin": 3, "guvence": 1},
        ]:
            try:
                fn(veri)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(komut_uret), "sabit eşleme, eşik sınırı, inceleme yolu ve şema korunmalı")
def m_dinamik(veri):
    return {"komut": veri["eylem"].upper(), "icerik": veri["metin"]}
def m_esik(veri):
    sonuc = komut_uret(veri)
    if sonuc["komut"] == "INCELE":
        sonuc = {"komut": "OZET", "icerik": veri["metin"]}
    return sonuc
def m_ek(veri):
    return {"komut": "OZET", "icerik": veri["metin"]}
for ad, mutant in [("model adını komut yapan", m_dinamik), ("düşük güvenceyi çalıştıran", m_esik), ("şemayı atlayan", m_ek)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)

from sandbox import ai_gercek_ai_saldiri_10 as deney
import json,secrets,tempfile
from pathlib import Path
if not ok(not ai_lab.kod_denetimi(src,('pipeline_referans','_pipeline','_isle','eval','exec','getattr')), 'dinamik çağrı ve laboratuvar yaması olmamalı'):stop()
for i in range(4):
    marker='NOT-'+secrets.token_hex(4)
    valid=json.dumps(dict(eylem='ozetle',metin=marker,guvence=.75),ensure_ascii=False)
    if not ok(komut_uret(karar_dogrula(kati_json(valid)))==dict(komut='OZET',icerik=marker),'yeni geçerli JSON eşik sınırında iş üretmeli'):stop()
    for raw in [valid+' EK','{"x":1,"x":2}', '{"ic":{"x":1,"x":2}}']:
        rejected=False
        try:kati_json(raw)
        except ValueError:rejected=True
        if not ok(rejected,'yeni bozuk JSON ek metin/yinelenen anahtar reddi'):stop()
with tempfile.TemporaryDirectory(prefix='pafta_json10_') as tmp:
    samples=deney.ornekleri_oku(deney.ORNEK)
    samples[0]['ham']=json.dumps(dict(eylem='ozetle',metin=secrets.token_hex(4),guvence=.9))
    result=deney.deney(kati_json,karar_dogrula,komut_uret,samples,Path(tmp)/'kuyruk.sqlite3')
    for key,value in result['kontroller'].items():ok(value,'gerçek deney: '+key)
    accepted=all(result['kontroller'].values())
    ai_lab.kanit_yaz('saldiri-10-json',dict(result,kabul=accepted))
    ok(accepted,'gerçek SQLite kuyruk etkisi ve iki canlı yanıt; modelin belirli bozuk JSON üretmesi şart değil')

```

```solution
import ai_lab

import json

def kati_json(metin):
    if not isinstance(metin, str) or not metin.strip():
        raise ValueError("tek JSON belgesi gerekli")
    def nesne(parcalar):
        sonuc = {}
        for anahtar, deger in parcalar:
            if anahtar in sonuc:
                raise ValueError("yinelenen anahtar")
            sonuc[anahtar] = deger
        return sonuc
    def sabit(deger):
        raise ValueError("standart dışı sayı")
    decoder = json.JSONDecoder(object_pairs_hook=nesne, parse_constant=sabit)
    kaynak = metin.strip()
    try:
        veri, bitis = decoder.raw_decode(kaynak)
    except json.JSONDecodeError as e:
        raise ValueError("geçersiz JSON") from e
    if bitis != len(kaynak):
        raise ValueError("JSON sonrası ek içerik")
    return veri

import math

def karar_dogrula(veri):
    if not isinstance(veri, dict) or set(veri) != {"eylem", "metin", "guvence"}:
        raise ValueError("karar şeması geçersiz")
    if veri["eylem"] not in ("ozetle", "cevir", "yoksay"):
        raise ValueError("eylem izinli değil")
    if not isinstance(veri["metin"], str) or not 1 <= len(veri["metin"]) <= 120:
        raise ValueError("metin 1..120 karakter olmalı")
    guvence = veri["guvence"]
    if isinstance(guvence, bool) or not isinstance(guvence, (int, float)):
        raise ValueError("güvence sayı olmalı")
    if not math.isfinite(guvence) or not 0 <= guvence <= 1:
        raise ValueError("güvence 0..1 olmalı")
    return {"eylem": veri["eylem"], "metin": veri["metin"], "guvence": guvence}

import math

def komut_uret(veri):
    if not isinstance(veri, dict) or set(veri) != {"eylem", "metin", "guvence"}:
        raise ValueError("karar şeması geçersiz")
    esleme = {"ozetle": "OZET", "cevir": "CEVIR", "yoksay": "YOKSAY"}
    if veri["eylem"] not in esleme:
        raise ValueError("eylem izinli değil")
    if not isinstance(veri["metin"], str) or not 1 <= len(veri["metin"]) <= 120:
        raise ValueError("metin geçersiz")
    guvence = veri["guvence"]
    if isinstance(guvence, bool) or not isinstance(guvence, (int, float)) or not math.isfinite(guvence) or not 0 <= guvence <= 1:
        raise ValueError("güvence geçersiz")
    if guvence < 0.75:
        return {"komut": "INCELE", "icerik": ""}
    return {"komut": esleme[veri["eylem"]], "icerik": veri["metin"]}
if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_saldiri_10 as deney
    deney.goster(kati_json,karar_dogrula,komut_uret)

```

```hint
Katı parser bütün belgeyi tüketsin ve nesne kancası her düzeyde yineleneni reddetsin. Şema ile komut yetkisini ayır; bool güvence değildir. Eşik altında içerik boş kalsın. Reddedilen kayıt için SQL eklemesi oluşmamalı.
```
:::
