---
id: el18
title: Proje · EQL İncelemesini Hazırla ve Kanıtı Oku
summary: _eql/search isteğini hazırlamak, tam yanıtı ayırt etmek ve verilmiş sequence kanıtında kimlik/sıra/süre tutarlılığını doğrulamak.
---

::: anlat Sorguyla birlikte arama sözleşmesini taşı
Son projede bir eğitim sürecinin başlangıcını ve sonraki bağlantısını araştırıyoruz. Amaç belli bir davranışın kanıtını okumak; sürecin yalnız adına bakıp zararlı olduğuna karar vermek değil. Kullanacağımız sabit sorgu:

```eql norun
sequence by host.id, process.entity_id with maxspan=5m
  [process where event.type == "start" and process.name == "helper.exe"]
  [network where event.type == "connection"]
until [process where event.type == "end"]
```

Bu sorgu `POST /logs-lab-*/_eql/search` gövdesindeki `query` alanına gider. `filter` ise EQL değil **Query DSL** nesnesidir: hangi makinenin, hangi zaman aralığındaki verisinin aramaya gireceğini daraltır. `timestamp_field`, `event_category_field` ve `tiebreaker_field` ile alan sözleşmesi ayrıca yazılabilir. Burada `@timestamp`, `event.category`, `event.sequence` kullanacağız; metinler keyword, sıra long ve zaman date olarak mapped olmalıdır.

Bir aralığın sonunu `lt` seçmek sonu dışarıda bırakır. Arama `09:00–10:00` ise 10:00 olayı girmez; 09:59:59.999 girer. Ayrıca bir sequence başlangıcı arama aralığından önce kaldığında sonraki ağ kaydı tek başına o sequence'i kuramaz. Arama aralığı ile `maxspan` farklı sınırlardır.
:::

::: anlat Sonuç eksikse incelemeyi tamamlandı sayma
EQL yanıtında `is_running`, `is_partial`, `timed_out` ve varsa `shard_failures` alanları okunur. HTTP yanıtının gelmesi bütün aramanın eksiksiz bittiği anlamına gelmez. Bu projede tam yanıt için üç bayrağın da açıkça `false`, shard hatası listesinin boş olmasını isteyeceğiz. İstek örneğinde `allow_partial_search_results: false` seçmek eksik sonuçla devam etmeme niyetini belirtir.

İkinci görev, dönen adayların **iç tutarlılığını** denetler: iki olay, doğru kategoriler, aynı host/entity, doğru sıra ve en fazla beş dakika. `_id` yalnız kendi indeksi içinde benzersiz olduğundan kanıtta `_index` ile birlikte saklanır. Aynı PID'yi taşıyan iki farklı entity tek süreç kabul edilmez. Dizinin `join_keys` sırası sorgudaki alan sırasıyla uyuşmalıdır. Eğitim yanıtındaki `_source` nesneleri noktalı düz ECS anahtarlarına hazırlanmıştır; gerçek API'nin iç içe event/process/host nesneleri önce bu şemaya dönüştürülür. Görev fonksiyonu otomatik düzleştirme yapmaz.

Bu kontrol bütün orijinal telemetriyi görmediği için araya giren bir `until` olayının bulunmadığını tek başına kanıtlayamaz. Gerçek değerlendirme sorguyu Elastic'te çalıştırıp kaynak kayıtları, mapping'i ve veri kalitesini de inceler. Pafta'da yalnız isteği sözlük olarak hazırlayıp **verilmiş** kanıtı okuyoruz; ağ isteği göndermiyor, native arama veya tam bir sequence motoru çalıştırmıyoruz.

Kaynaklar: [EQL arama API'si ve yanıt alanları](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-eql-search), [EQL sequence sözleşmesi](https://www.elastic.co/docs/reference/query-languages/eql/eql-syntax).
:::

::: tahmin
Mapping ve UTC zaman biçimi yukarıdaki gibidir; API isteğinde `tiebreaker_field: "event.sequence"` ayarlanmıştır. Fixture'da her anahtar için tek başlangıç/bağlantı ve hiçbir end olayı yoktur. Query DSL arama aralığı bütün bu olayları içerir. Tamamlanan çiftlerin kimliklerini başlangıç sırasıyla yaz; PID'nin aynı olması tek başına yeterli değildir.

```eql
sequence by host.id, process.entity_id with maxspan=5m
  [process where event.type == "start" and process.name == "helper.exe"]
  [network where event.type == "connection"]
until [process where event.type == "end"]
```

```stdin
[
  {"event.id":"s1","@timestamp":"2026-10-21T14:00:00.000Z","event.sequence":1,"event.category":"process","event.type":"start","process.name":"helper.exe","host.id":"h1","process.entity_id":"e1","process.pid":44},
  {"event.id":"s2","@timestamp":"2026-10-21T14:00:01.000Z","event.sequence":2,"event.category":"process","event.type":"start","process.name":"helper.exe","host.id":"h2","process.entity_id":"eski","process.pid":44},
  {"event.id":"s3","@timestamp":"2026-10-21T14:00:02.000Z","event.sequence":3,"event.category":"process","event.type":"start","process.name":"helper.exe","host.id":"h3","process.entity_id":"e3","process.pid":44},
  {"event.id":"n2","@timestamp":"2026-10-21T14:00:03.000Z","event.sequence":4,"event.category":"network","event.type":"connection","host.id":"h2","process.entity_id":"yeni","process.pid":44},
  {"event.id":"n3","@timestamp":"2026-10-21T14:00:04.000Z","event.sequence":5,"event.category":"network","event.type":"connection","host.id":"h4","process.entity_id":"e3","process.pid":44},
  {"event.id":"n1","@timestamp":"2026-10-21T14:05:00.000Z","event.sequence":6,"event.category":"network","event.type":"connection","host.id":"h1","process.entity_id":"e1","process.pid":44}
]
```

```gercek
s1 -> n1
```

```test
import json, sys
from datetime import datetime
events = json.load(sys.stdin)
def order(e):
    return (datetime.fromisoformat(e["@timestamp"].replace("Z", "+00:00")),e["event.sequence"])
for a in events:
    if (a["event.category"],a["event.type"],a.get("process.name")) != ("process","start","helper.exe"):
        continue
    for b in events:
        if (b["event.category"],b["event.type"]) != ("network","connection"):
            continue
        if all(a[k] == b[k] for k in ("host.id","process.entity_id")) and order(a) < order(b) and (order(b)[0] - order(a)[0]).total_seconds() <= 300:
            print(a["event.id"] + " -> " + b["event.id"])
```

???

`s1/n1` tam 300000 ms ile sınırın içindedir. `s2/n2` PID tekrar kullanımı yüzünden farklı entity'lerdir. `s3/n3` farklı makinelerdedir. Bu fixture'da alternatif başlangıçlar ve sonlandırma olayı bulunmadığından yanıt tekildir; Python doğrulayıcı genel EQL keşfi yapmaz.
:::

::: gorev Gönderilmeye hazır arama nesnesi
`istek_hazirla(host, bas, bit, adet)` şu nesneyi döndürsün; ağ isteği gönderme. `method` POST, `path` `/logs-lab-*/_eql/search` olsun. `body.query` başlangıç kodundaki sabit `EQL_QUERY`; `size` adet; `timestamp_field` `@timestamp`, `event_category_field` `event.category`, `tiebreaker_field` `event.sequence`, `allow_partial_search_results` `False`. Filter nesnesi `{"bool":{"filter":[{"term":{"host.id":host}}, {"range":{"@timestamp":{"gte":bas,"lt":bit}}}]}}` olsun.

Host boş olmayan bir metin, adet 1–100 arasında tamsayı (`bool` değil) olmalı. Bas ve bit geçerli, aynı biçimli UTC milisaniye metinlerdir; bas kesin olarak bit'ten küçük olmalı. Bu kontroller sağlanmıyorsa `ValueError` yükselt. Tarih sözdizimi doğrulayıcısı veya EQL üreticisi yazma; verilen sorguyu ve aralık sözleşmesini isteğe yerleştir.

```starter
EQL_QUERY = '''sequence by host.id, process.entity_id with maxspan=5m
  [process where event.type == "start" and process.name == "helper.exe"]
  [network where event.type == "connection"]
until [process where event.type == "end"]'''

def istek_hazirla(host, bas, bit, adet):
    return {"method":"POST", "path":"/logs-lab-*/_eql/search", "body":{"query":EQL_QUERY}}
```

```test
beklenen_sorgu = '''sequence by host.id, process.entity_id with maxspan=5m
  [process where event.type == "start" and process.name == "helper.exe"]
  [network where event.type == "connection"]
until [process where event.type == "end"]'''
bas, bit = "2026-10-21T09:00:00.000Z", "2026-10-21T10:00:00.000Z"
for host, adet in (("h1",1), ("h2",99), ("sunucu-üç",100)):
    r = istek_hazirla(host,bas,bit,adet)
    eq(r, {"method":"POST", "path":"/logs-lab-*/_eql/search", "body":{
        "query":beklenen_sorgu, "size":adet, "timestamp_field":"@timestamp", "event_category_field":"event.category",
        "tiebreaker_field":"event.sequence", "allow_partial_search_results":False,
        "filter":{"bool":{"filter":[{"term":{"host.id":host}}, {"range":{"@timestamp":{"gte":bas,"lt":bit}}}]}}}}, "gövde sözleşmesi")
for adet in (0,101,True,1.0):
    raises(ValueError, istek_hazirla, "h",bas,bit,adet)
for host in ("", None, 7):
    raises(ValueError, istek_hazirla, host,bas,bit,10)
for son in ("2026-10-21T08:59:59.999Z", bas):
    raises(ValueError, istek_hazirla, "h",bas,son,10)
eq(istek_hazirla("h",bas,"2026-10-21T09:00:00.001Z",10)["body"]["filter"]["bool"]["filter"][1]["range"]["@timestamp"]["lt"], "2026-10-21T09:00:00.001Z", "bir milisaniyelik aralık")
```

```solution
EQL_QUERY = '''sequence by host.id, process.entity_id with maxspan=5m
  [process where event.type == "start" and process.name == "helper.exe"]
  [network where event.type == "connection"]
until [process where event.type == "end"]'''

def istek_hazirla(host, bas, bit, adet):
    if not isinstance(host, str) or not host:
        raise ValueError("host gerekli")
    if type(adet) is not int or not 1 <= adet <= 100:
        raise ValueError("adet 1–100 arasında tamsayı olmalı")
    if bas >= bit:
        raise ValueError("başlangıç bitişten önce olmalı")
    return {"method":"POST", "path":"/logs-lab-*/_eql/search", "body":{
        "query":EQL_QUERY, "size":adet, "timestamp_field":"@timestamp", "event_category_field":"event.category",
        "tiebreaker_field":"event.sequence", "allow_partial_search_results":False,
        "filter":{"bool":{"filter":[{"term":{"host.id":host}}, {"range":{"@timestamp":{"gte":bas,"lt":bit}}}]}}}}
```

```hint
Sorgu metni, Query DSL filter nesnesi ve HTTP yolu ayrı alanlarda. Aynı UTC biçimindeki tarih metinleri bu sınırlı görevde sıralanabilir.
```
:::

::: gorev Dönen çiftin kanıtını doğrula
`kanit_kontrol(yanit)` tam yanıt değilse `ValueError` yükseltsin: `is_running`, `is_partial`, `timed_out` açıkça `False` olmalı; `shard_failures` yok veya boş olmalı. Sonra `hits.sequences` içindeki adayları giriş sırasında denetle. Her geçerli aday için `(ilk_index + "/" + ilk_id, son_index + "/" + son_id)` demetini listeye ekle.

Geçerli aday tam iki **gözlenmiş** olay içermeli; ikisinde `_index`, `_id`, `_source` bulunmalı. `_source` bu alıştırma için noktalı düz ECS anahtarlarına hazırlanmıştır; gerçek iç içe `_source` önce bu şemaya dönüştürülür. İlk olay helper.exe/process/start, ikinci network/connection olmalı. Dolu host/entity anahtarları aynı ve `join_keys` bu sırayla eşit olmalı. `_source` zamanları aynı UTC biçiminde, `event.sequence` tamsayı; `(zaman, sıra)` kesin artmalı ve süre en fazla 300000 ms olmalı. Aynı indeks/id çifti iki kez kullanılmışsa reddet. Eksik anahtar, eksik sıra, `missing: true`, yanlış uzunluk veya bozuk aday atlanır. Bu, adayın iç tutarlılığıdır; dönmeyen bir until olayını buradan keşfedemezsin.

```starter
def kanit_kontrol(yanit):
    return []
```

```test
from copy import deepcopy
from datetime import datetime, timedelta, timezone
def zaman(ms):
    return (datetime(2026,10,21,tzinfo=timezone.utc)+timedelta(milliseconds=ms)).isoformat(timespec="milliseconds").replace("+00:00","Z")
def aday(fark=300000):
    return {"join_keys":["h","e"], "events":[
        {"_index":"logs-1", "_id":"p", "_source":{"@timestamp":zaman(1000), "event.sequence":10,"event.category":"process","event.type":"start","process.name":"helper.exe","host.id":"h","process.entity_id":"e","process.pid":9}},
        {"_index":"logs-1", "_id":"n", "_source":{"@timestamp":zaman(1000+fark), "event.sequence":11,"event.category":"network","event.type":"connection","host.id":"h","process.entity_id":"e","process.pid":9}}]}
def yanit(*diziler):
    return {"is_running":False,"is_partial":False,"timed_out":False,"hits":{"sequences":list(diziler)}}
for fark, kabul in ((-1,False),(0,True),(299999,True),(300000,True),(300001,False)):
    eq(kanit_kontrol(yanit(aday(fark))), [("logs-1/p","logs-1/n")] if kabul else [], f"süre sınırı {fark}")
for sira, kabul in ((9,False),(10,False),(11,True)):
    d = aday(0); d["events"][1]["_source"]["event.sequence"] = sira
    eq(kanit_kontrol(yanit(d)), [("logs-1/p","logs-1/n")] if kabul else [], f"eşit zamanda sıra {sira}")
for alan,deger in (("host.id","baska"),("process.entity_id","yeni-pid-ornegi"),("event.category","file"),("event.type","end"),("host.id",None),("event.sequence",None)):
    d = aday(); d["events"][1]["_source"][alan] = deger
    eq(kanit_kontrol(yanit(d)), [], alan)
for alan in ("host.id","process.entity_id"):
    for deger in (None, ""):
        d = aday()
        for e in d["events"]:
            e["_source"][alan] = deger
        d["join_keys"] = [d["events"][0]["_source"].get("host.id"), d["events"][0]["_source"].get("process.entity_id")]
        eq(kanit_kontrol(yanit(d)), [], "iki uçta da geçersiz anahtar")
for alan in ("_index","_id"):
    for konum in (0,1):
        d = aday(); d["events"][konum][alan] = ""
        eq(kanit_kontrol(yanit(d)), [], "eksik kanıt kimliği")
for adet in (1,3):
    d = aday(); d["events"] = (d["events"] * 2)[:adet]
    eq(kanit_kontrol(yanit(d)), [], "tam iki aşama")
for degistir in (lambda d: d.update(join_keys=["e","h"]),
                 lambda d: d["events"][1].update(missing=True),
                 lambda d: d["events"][1].update(_id="p"),
                 lambda d: d["events"][0]["_source"].update({"process.name":"other.exe"}),
                 lambda d: d["events"][1].pop("_source")):
    d = aday(); degistir(d); eq(kanit_kontrol(yanit(d)), [], "kanıt tutarsızlığı")
d = aday(); d["events"][1].update(_id="p", _index="logs-2")
eq(kanit_kontrol(yanit(d)), [("logs-1/p","logs-2/p")], "_id yalnız indeksinde benzersiz")
eq(kanit_kontrol(yanit(aday(300001),aday(1))), [("logs-1/p","logs-1/n")], "geçersizi atla, geçerliyi koru")
for alan in ("is_running","is_partial","timed_out"):
    r = yanit(aday()); r[alan] = True
    raises(ValueError, kanit_kontrol, r)
    r = yanit(); r.pop(alan)
    raises(ValueError, kanit_kontrol, r)
r = yanit(); r["shard_failures"] = [{"reason":"unavailable"}]
raises(ValueError, kanit_kontrol, r)
eq(kanit_kontrol(yanit()), [], "tam ama eşleşmesiz")
```

```solution
from datetime import datetime

def kanit_kontrol(yanit):
    if any(yanit.get(k) is not False for k in ("is_running","is_partial","timed_out")) or yanit.get("shard_failures"):
        raise ValueError("arama tamamlanmış ve eksiksiz değil")
    sonuc = []
    for dizi in yanit.get("hits", {}).get("sequences", []):
        olaylar = dizi.get("events", [])
        if len(olaylar) != 2 or any(e.get("missing") is True for e in olaylar):
            continue
        try:
            a, b = [e["_source"] for e in olaylar]
            if (a["event.category"],a["event.type"],a.get("process.name")) != ("process","start","helper.exe"):
                continue
            if (b["event.category"],b["event.type"]) != ("network","connection"):
                continue
            anahtar = [a.get("host.id"),a.get("process.entity_id")]
            if any(k is None or k == "" for k in anahtar):
                continue
            if anahtar != [b.get("host.id"),b.get("process.entity_id")] or dizi.get("join_keys") != anahtar:
                continue
            ta, tb = [datetime.fromisoformat(e["@timestamp"].replace("Z","+00:00")) for e in (a,b)]
            if any(type(e.get("event.sequence")) is not int for e in (a,b)):
                continue
            if not (ta,a["event.sequence"]) < (tb,b["event.sequence"]):
                continue
            if (tb - ta).total_seconds() > 300:
                continue
            ids = [(e["_index"],e["_id"]) for e in olaylar]
            if any(not indeks or not kimlik for indeks,kimlik in ids) or ids[0] == ids[1]:
                continue
            sonuc.append(tuple(indeks + "/" + kimlik for indeks,kimlik in ids))
        except (KeyError, TypeError, ValueError):
            continue
    return sonuc
```

```hint
Kalite hatası bütün yanıtı durdurur; bozuk bir aday ise yalnız kendisi atlanır. Sıra için (datetime, event.sequence) demeti, süre için ilk ve son datetime farkı gerekir.
```
:::
