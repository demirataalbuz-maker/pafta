---
id: el15
title: EQL · Sequence, Kimlik ve Sıra
summary: host.id ve process.entity_id ile olayları bağlamak, timestamp/tiebreaker sırası ve aday dizinin kanıtını okumak.
---

::: anlat Aynı makine, aynı süreç örneği
Bir süreç başladıktan sonra ağ bağlantısı kurmuş mu? `sequence` iki olay koşulunu sırayla arar. İkisi aynı `host.id` ve `process.entity_id` değerlerini taşımalıdır:

```eql norun
sequence by host.id, process.entity_id
  [process where event.type == "start" and process.name == "agent.exe"]
  [network where event.type == "connection"]
```

PID bir makinede süreç bitene kadar ayırt edicidir; sonra tekrar kullanılabilir. İki ayrı süreç aynı `process.pid` değerini taşıyabilir. ECS `process.entity_id`, veri kaynağının süreç örneğini ayırt etmek için ürettiği kimliktir. Bu kimliğin üretildiğini ve olaylara tutarlı taşındığını doğrula. Sadece süreç adını veya PID'yi eşlemek, ilgisiz kayıtları bağlayabilir.

Burada anahtarlar tek değerli keyword alanlardır. `by` alanları opsiyonel yapılmadığından null anahtar aday değildir. Eğitimde eksik kimliği boş bir ortak kimliğe çevirmiyoruz. Gerçek mapping ve veri kaynağı aynı sözleşmeyi sağlamalıdır.
:::

::: anlat Sıra ve sonuç, olay sayısından fazlasıdır
EQL olay zamanını kullanır; Elasticsearch'e geliş sırası aynı şey değildir. Eşit `@timestamp` değerleri için arama isteğinde `tiebreaker_field: "event.sequence"` belirtilebilir. Bu derste bütün zamanlar aynı biçimde UTC milisaniyeli metin, sıra alanı tamsayı ve her `(zaman, sıra)` çifti benzersizdir. Böylece önce/sonra kararı belirsiz kalmaz.

Bir sequence yanıtında `hits.sequences` bulunur. Her dizinin `join_keys` değerleri ve sıralı `events` kanıtları vardır. Olay aramasındaki `hits.events` ile bu listeyi karıştırma.

Elasticsearch, aynı anahtarın bütün olası olay kombinasyonlarını üretmez; bekleyen eşleşmeler için durum tutar. Bu dersin Python görevleri **verilmiş bir aday çiftini** denetler. Geniş akıştan bütün dizileri bulan bir EQL motoru yazmıyorsun. Tahmin verisinde de her anahtar için en çok bir başlangıç ve bir bağlantı vardır; çakışan adaylar özellikle yoktur.

Kaynaklar: [EQL sequence ve eşleşme davranışı](https://www.elastic.co/docs/reference/query-languages/eql/eql-syntax), [ECS süreç kimliği](https://www.elastic.co/docs/reference/ecs/ecs-process), [arama sırası](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-eql-search).
:::

::: tahmin
Mapping ve sıralama yukarıdaki gibidir; bu fixture için API isteğinde `tiebreaker_field: "event.sequence"` ayarlanmıştır. Kimlikler tüm fixture'da benzersizdir. Aynı anahtarda tek başlangıç ve tek ağ olayı bulunduğundan tamamlanan çiftleri `ilk_id -> ikinci_id` biçiminde, başlangıç sırasıyla yaz.

```eql
sequence by host.id, process.entity_id
  [process where event.type == "start" and process.name == "agent.exe"]
  [network where event.type == "connection"]
```

```stdin
[
  {"event.id":"p1","@timestamp":"2026-10-21T11:00:00.000Z","event.sequence":1,"event.category":"process","event.type":"start","process.name":"agent.exe","host.id":"h1","process.entity_id":"a","process.pid":90},
  {"event.id":"n1","@timestamp":"2026-10-21T11:00:00.000Z","event.sequence":2,"event.category":"network","event.type":"connection","host.id":"h1","process.entity_id":"a","process.pid":90},
  {"event.id":"p2","@timestamp":"2026-10-21T11:00:01.000Z","event.sequence":3,"event.category":"process","event.type":"start","process.name":"agent.exe","host.id":"h2","process.entity_id":"b","process.pid":90},
  {"event.id":"n2","@timestamp":"2026-10-21T11:00:02.000Z","event.sequence":4,"event.category":"network","event.type":"connection","host.id":"h3","process.entity_id":"b","process.pid":90},
  {"event.id":"p3","@timestamp":"2026-10-21T11:00:03.000Z","event.sequence":5,"event.category":"process","event.type":"start","process.name":"agent.exe","host.id":"h4","process.entity_id":"eski","process.pid":90},
  {"event.id":"n3","@timestamp":"2026-10-21T11:00:04.000Z","event.sequence":6,"event.category":"network","event.type":"connection","host.id":"h4","process.entity_id":"yeni","process.pid":90}
]
```

```gercek
p1 -> n1
```

```test
import json, sys
events = json.load(sys.stdin)
for a in events:
    if a.get("event.category") != "process" or a.get("event.type") != "start" or a.get("process.name") != "agent.exe":
        continue
    for b in events:
        if b.get("event.category") != "network" or b.get("event.type") != "connection":
            continue
        if all(a.get(k) is not None and a.get(k) == b.get(k) for k in ("host.id", "process.entity_id")) and (a["@timestamp"], a["event.sequence"]) < (b["@timestamp"], b["event.sequence"]):
            print(a["event.id"] + " -> " + b["event.id"])
```

???

`p1` ile `n1` aynı zaman damgasını taşır; ikinci olayın sıra numarası daha büyüktür. `p2/n2` farklı makinelerdedir. `p3/n3` aynı PID'ye rağmen farklı süreç örnekleridir. Doğrulayıcı yalnız bu tekil aday fixture'ını denetler; bütün olası çiftleri EQL'nin döndüreceği iddiasında bulunmaz.
:::

::: gorev Birleştirme anahtarını çıkar
`zincir_anahtari(olay)` iki alan da mevcut ve null değilse `(host.id, process.entity_id)` demetini, aksi halde `None` döndürsün. PID kullanma. Keyword değerleri bu görevde metindir; boş metin null değildir. Eksik alanı `"bilinmiyor"` gibi ortak bir etikete dönüştürme.

```starter
def zincir_anahtari(olay):
    return olay.get("process.pid")
```

```test
eq(zincir_anahtari({"host.id":"h1", "process.entity_id":"e1", "process.pid":7}), ("h1","e1"), "iki parça")
eq(zincir_anahtari({"host.id":"h2", "process.entity_id":"e1", "process.pid":7}), ("h2","e1"), "PID aynı, makine farklı")
eq(zincir_anahtari({"host.id":"h1", "process.entity_id":"e2", "process.pid":7}), ("h1","e2"), "PID tekrar kullanılmış")
for e in ({}, {"host.id":"h1"}, {"process.entity_id":"e1"}, {"host.id":None,"process.entity_id":"e1"}, {"host.id":"h1","process.entity_id":None}):
    eq(zincir_anahtari(e), None, "null anahtar bağlanmaz")
eq(zincir_anahtari({"host.id":"", "process.entity_id":"e1"}), ("","e1"), "boş metin null değildir")
```

```solution
def zincir_anahtari(olay):
    h, p = olay.get("host.id"), olay.get("process.entity_id")
    return None if h is None or p is None else (h, p)
```

```hint
İki alanı birlikte anahtar yap. if not h yerine h is None, boş metin ile null farkını korur.
```
:::

::: gorev Verilmiş bir aday çifti denetle
`aday_gecerli(a, b)` yukarıdaki iki aşamalı sorgunun **verilen** çiftine uyuluyorsa `True` döndürsün: ilk olay `agent.exe` başlangıcı, ikinci olay ağ bağlantısı; host/entity anahtarları mevcut ve aynı; `(zaman, sıra)` ilk olayda daha küçük. Zamanlar sabit biçimli UTC metinler, sıralar tamsayıdır; bu dört alan eksik/null ise `False`. Başka aday arama veya olayları yeniden sıralama.

```starter
def aday_gecerli(a, b):
    return a.get("process.pid") == b.get("process.pid")
```

```test
def olay(kategori, tip, sira, **ek):
    e = {"event.category":kategori, "event.type":tip, "process.name":"agent.exe", "host.id":"h", "process.entity_id":"e", "process.pid":5, "@timestamp":"2026-10-21T11:00:00.000Z", "event.sequence":sira}
    e.update(ek); return e
a, b = olay("process","start",10), olay("network","connection",11)
eq(aday_gecerli(a,b), True, "eşit zamanda sonraki sıra")
for sira in (9,10,11):
    eq(aday_gecerli(a, dict(b, **{"event.sequence":sira})), sira > 10, f"sıra sınırı {sira}")
eq(aday_gecerli(a, dict(b, **{"@timestamp":"2026-10-21T11:00:00.001Z", "event.sequence":1})), True, "önce zaman karşılaştırılır")
eq(aday_gecerli(a, dict(b, **{"@timestamp":"2026-10-21T10:59:59.999Z"})), False, "geri zaman")
for k, v in (("host.id","diger"), ("process.entity_id","yeniden-kullanilan-pid"), ("event.category","file"), ("event.type","end"), ("host.id",None), ("event.sequence",None)):
    eq(aday_gecerli(a, dict(b, **{k:v})), False, k)
eq(aday_gecerli(dict(a, **{"process.name":"other.exe"}), b), False, "ilk koşul")
eq(aday_gecerli({},b), False, "eksik başlangıç")
```

```solution
def aday_gecerli(a, b):
    if (a.get("event.category"), a.get("event.type"), a.get("process.name")) != ("process", "start", "agent.exe"):
        return False
    if (b.get("event.category"), b.get("event.type")) != ("network", "connection"):
        return False
    if any(a.get(k) is None or a.get(k) != b.get(k) for k in ("host.id", "process.entity_id")):
        return False
    if any(e.get(k) is None for e in (a,b) for k in ("@timestamp", "event.sequence")):
        return False
    return (a["@timestamp"], a["event.sequence"]) < (b["@timestamp"], b["event.sequence"])
```

```hint
Koşulları, anahtarları ve sırayı ayrı denetle. Eşit zaman damgasında karar tamsayı event.sequence alanındadır.
```
:::
