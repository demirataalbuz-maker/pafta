---
id: el16
title: EQL · Zaman Penceresi ve until
summary: maxspan başlangıçtan son olaya ölçülür; tam sınır dahildir, until ise aradaki sonlanma olayıyla adayı iptal eder.
---

::: anlat Pencere ilk olayda başlar
Beş dakikalık bir dizi, her komşu olay arasına ayrı beş dakika vermez. İlk olumlu olaydan son olumlu olaya kadar geçen toplam süreye bakılır. Örneğin 0, 4 ve 8'inci dakikadaki üç olayın komşu boşlukları küçük olsa da toplamı sekiz dakikadır.

```eql norun
sequence by host.id, process.entity_id with maxspan=5m
  [process where event.type == "start"]
  [network where event.type == "connection"]
```

Bu dersin pozitif iki aşamalı örneklerinde **tam 300000 ms sınır dahildir**: 299999 ve 300000 ms geçer, 300001 ms geçmez. Bu ayrıntı yalnız “beş dakika içinde” sözünden tahmin edilmedi; Elasticsearch'ün `SequenceMatcher` uygulamasında süre ancak `maxspan` değerinden büyükse reddedilir. Kaynak sürümü değiştiğinde veya üretimde başka bir motor kullanıldığında sınır davranışını yeniden doğrula.

Zaman aralığı denetimi ile olay sırası ayrı şeylerdir. Aynı milisaniyede iki olay farklı `event.sequence` değerleriyle sıralanabilir; süreleri sıfırdır. Sıra alanı yoksa bu dersteki Python fonksiyonunun kararı gerçek sorgu sırasının kanıtı olmaz.
:::

::: anlat Diziyi süreden önce bitiren olay
`until`, henüz tamamlanmamış bir adayı sonlandıran olaydır. Bir süreç bitmişse daha sonraki ağ olayını eski başlangıca bağlamak istemeyebilirsin:

```eql norun
sequence by host.id, process.entity_id with maxspan=5m
  [process where event.type == "start"]
  [network where event.type == "connection"]
until [process where event.type == "end"]
```

Aynı anahtardaki `end` başlangıç ile bağlantı arasındaysa aday iptal olur. Bağlantıdan sonra gelmesi tamamlanmış eşleşmeyi geriye dönük kaldırmaz. Başka makinenin veya başka süreç örneğinin sonlanması bu anahtarı kapatmaz. `until` olayı, tamamlanan dizinin normal kanıt listesine üçüncü aşama olarak eklenmez.

Görevlerde zaman, başlangıçtan beri **tamsayı milisaniye**; ikincil sıra tamsayıdır. Adaylar önceden verilmiştir. İkinci görev yalnız kesin açık ordinal aralığındaki gözlemi arayan matematiksel bir yardımcıdır. Gerçek akışta aynı timestamp ve tiebreaker değerini paylaşan farklı kayıtların tam sırası bu iki alanla belirlenemez; yardımcı native motorun ek sıra/tie seçimini taklit etmez. Bütün EQL durum makinesini, çoklu bekleyen başlangıçları veya eksik telemetriyi bu yardımcılarla çözdüğümüzü varsayma.

Kaynaklar: [EQL maxspan ve until](https://www.elastic.co/docs/reference/query-languages/eql/eql-syntax), [Elastic SequenceMatcher — süre sınırı](https://github.com/elastic/elasticsearch/blob/main/x-pack/plugin/eql/src/main/java/org/elasticsearch/xpack/eql/execution/sequence/SequenceMatcher.java).
:::

::: tahmin
Alanlar tek değerli keyword, zaman alanı date ve `event.sequence` long olarak mapped. API isteğinde `tiebreaker_field: "event.sequence"` ayarlanmıştır; bu fixture'daki bütün `(zaman, sıra)` çiftleri benzersizdir. UTC milisaniye biçimi sabit; aynı anahtarda bir başlangıç ve bir bağlantı var. Tamamlanan çiftleri ilk olay sırasıyla yaz. `h1/a` dizisinin sonlanması bağlantıdan sonradır.

```eql
sequence by host.id, process.entity_id with maxspan=5m
  [process where event.type == "start"]
  [network where event.type == "connection"]
until [process where event.type == "end"]
```

```stdin
[
  {"event.id":"a1","@timestamp":"2026-10-21T12:00:00.000Z","event.sequence":1,"event.category":"process","event.type":"start","host.id":"h1","process.entity_id":"a"},
  {"event.id":"a2","@timestamp":"2026-10-21T12:00:01.000Z","event.sequence":2,"event.category":"process","event.type":"start","host.id":"h2","process.entity_id":"b"},
  {"event.id":"a3","@timestamp":"2026-10-21T12:00:02.000Z","event.sequence":3,"event.category":"process","event.type":"start","host.id":"h3","process.entity_id":"c"},
  {"event.id":"x3","@timestamp":"2026-10-21T12:00:03.000Z","event.sequence":4,"event.category":"process","event.type":"end","host.id":"h3","process.entity_id":"c"},
  {"event.id":"b3","@timestamp":"2026-10-21T12:00:04.000Z","event.sequence":5,"event.category":"network","event.type":"connection","host.id":"h3","process.entity_id":"c"},
  {"event.id":"b1","@timestamp":"2026-10-21T12:05:00.000Z","event.sequence":6,"event.category":"network","event.type":"connection","host.id":"h1","process.entity_id":"a"},
  {"event.id":"x1","@timestamp":"2026-10-21T12:05:00.001Z","event.sequence":7,"event.category":"process","event.type":"end","host.id":"h1","process.entity_id":"a"},
  {"event.id":"b2","@timestamp":"2026-10-21T12:05:01.001Z","event.sequence":8,"event.category":"network","event.type":"connection","host.id":"h2","process.entity_id":"b"}
]
```

```gercek
a1 -> b1
```

```test
import json, sys
from datetime import datetime
events = json.load(sys.stdin)
def ordinal(e):
    return (datetime.fromisoformat(e["@timestamp"].replace("Z", "+00:00")), e["event.sequence"])
def key(e):
    return (e["host.id"], e["process.entity_id"])
for a in events:
    if (a["event.category"], a["event.type"]) != ("process", "start"):
        continue
    for b in events:
        if (b["event.category"], b["event.type"]) != ("network", "connection") or key(a) != key(b):
            continue
        if not ordinal(a) < ordinal(b) or (ordinal(b)[0] - ordinal(a)[0]).total_seconds() > 300:
            continue
        if any(key(x) == key(a) and (x["event.category"],x["event.type"]) == ("process","end") and ordinal(a) < ordinal(x) < ordinal(b) for x in events):
            continue
        print(a["event.id"] + " -> " + b["event.id"])
```

???

`a1/b1` tam beş dakikayla eşleşir; daha sonraki `x1` onu geri almaz. `a2/b2` beş dakikayı bir milisaniye aşar. `a3/b3` kısa sürer ama aradaki `x3` adayı kapatır. Fixture doğrulayıcısı yalnız bu çakışmasız üç zincirin kararını hesaplar.
:::

::: gorev Milisaniye penceresini denetle
`pencereye_sigar(bas_ms, son_ms, max_ms)` süre negatif değil ve verilen pozitif sınırı aşmıyorsa `True` döndürsün. Girdiler tamsayıdır, `max_ms` pozitiftir. Bu fonksiyon yalnız süreyi denetler; olay kategorisini, anahtarı veya ikincil sırayı denetlemez. Sıfır süre, sıraları farklı iki olay için mümkün olduğundan kabul edilir.

```starter
def pencereye_sigar(bas_ms, son_ms, max_ms):
    return son_ms - bas_ms < max_ms
```

```test
for bas in (0, 900000, 1700000000000):
    for fark, beklenen in ((-1,False), (0,True), (1,True), (299999,True), (300000,True), (300001,False)):
        eq(pencereye_sigar(bas, bas + fark, 300000), beklenen, f"başlangıç {bas}, fark {fark}")
for fark, beklenen in ((999,True), (1000,True), (1001,False)):
    eq(pencereye_sigar(5000, 5000 + fark, 1000), beklenen, "sabit beş dakika kodlama")
```

```solution
def pencereye_sigar(bas_ms, son_ms, max_ms):
    fark = son_ms - bas_ms
    return 0 <= fark <= max_ms
```

```hint
İki sınırın da dahil olduğunu ayrı düşün: negatif süre yok, tam max_ms kabul. Başlangıcın 0 olduğunu varsayma.
```
:::

::: gorev until için aradaki olayı bul
`iptal_edilir_mi(bas, son, olaylar)` verilen aday çiftinin **kesin açık ordinal aralığına** aynı `host.id`/`process.entity_id` anahtarıyla bir `process`/`end` gözlemi düşüyorsa `True` döndürsün. Her olayda `t_ms` ve `event.sequence` vardır. Önce zaman, eşitse sıra karşılaştırılır. Bas ve son geçerli, aynı anahtarlı ve sıralıdır; başka kayıtların eksik/null anahtarları eşleşmesin. Bu sınırlı yardımcı uç ordinaline tam eşit girdiyi kabul eder ama arada saymaz: her iki uçta `False`. Bu, belirsiz native tie sırasını çözme iddiası değil, verilen açık aralığı denetleme sözleşmesidir.

```starter
def iptal_edilir_mi(bas, son, olaylar):
    return any(e.get("event.type") == "end" for e in olaylar)
```

```test
def e(t, sira, **ek):
    sonuc = {"host.id":"h", "process.entity_id":"a", "event.category":"process", "event.type":"end", "t_ms":t, "event.sequence":sira}
    sonuc.update(ek); return sonuc
bas, son = e(1000,10), e(2000,20)
for t, beklenen in ((999,False), (1000,True), (1001,True), (1999,True), (2000,True), (2001,False)):
    eq(iptal_edilir_mi(bas, son, [e(t,15)]), beklenen, f"zaman {t}, sıra 15")
eq(iptal_edilir_mi(bas, son, [e(1000,9)]), False, "başlangıçla aynı zaman ama önce")
eq(iptal_edilir_mi(bas, son, [e(1000,10)]), False, "yardımcının açık aralığı: tam başlangıç ordinali")
eq(iptal_edilir_mi(bas, son, [e(2000,19)]), True, "sonla aynı zaman ama önce")
eq(iptal_edilir_mi(bas, son, [e(2000,20)]), False, "yardımcının açık aralığı: tam son ordinali")
eq(iptal_edilir_mi(bas, son, [e(2000,21)]), False, "sondan sonra iptal yok")
for ek in ({"host.id":"baska"}, {"process.entity_id":"baska"}, {"host.id":None}, {"event.category":"file"}, {"event.type":"start"}):
    eq(iptal_edilir_mi(bas, son, [e(1500,15,**ek)]), False, "yalnız ilgili sonlanma")
eq(iptal_edilir_mi(bas, son, []), False, "sonlanma yok")
```

```solution
def iptal_edilir_mi(bas, son, olaylar):
    ilk = (bas["t_ms"], bas["event.sequence"])
    son_sira = (son["t_ms"], son["event.sequence"])
    for olay in olaylar:
        if (olay.get("event.category"), olay.get("event.type")) != ("process", "end"):
            continue
        if any(olay.get(k) is None or olay.get(k) != bas[k] for k in ("host.id", "process.entity_id")):
            continue
        if ilk < (olay["t_ms"], olay["event.sequence"]) < son_sira:
            return True
    return False
```

```hint
Zamanı tek başına değil (t_ms, event.sequence) demetiyle karşılaştır. Yanlış anahtarın end olayını adayın içine katma.
```
:::
