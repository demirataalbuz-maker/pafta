---
id: el16
title: EQL · Maxspan ve Until
summary: Tam süre eşiğini ve ordinal kullanan iptal olayını gerçek query görevleriyle sınırla.
---

::: anlat Süre ilk olumlu olaydan ölçülür
`with maxspan=5m` tüm olumlu dizinin ilk olayından son olayına kadar geçen süreyi sınırlar. Tam 300000 ms kabul, 300001 ms red; ara aşamadan süreyi yeniden başlatma. Sıra timestamp+tiebreaker ile kesinleştiğinde aynı timestamp'teki farklı olaylar sıfır süreli bir dizi oluşturabilir.

Yerel uygulama bu eşitlik davranışını Elasticsearch v9.2.0 SequenceMatcher'ın `delta > maxspan` reddiyle sınırlar. Bu, motor kaynağından doğrulanmış bir kontrattır; burada `>=` ile red uygulanmaz. Tezgâh corpus tarihleri en fazla milisaniye hassasiyetindedir. maxspan yerel dilde pozitif tamsayı ve açık bir birim ister.

```eql
sequence by host.id, process.entity_id with maxspan=5m
  [process where event.action == "start"]
  [network where event.action == "connect"]
```

```meta
dil: eql
```

```stdin
{
  "dil": "eql",
  "mapping": {
    "id": "keyword",
    "@timestamp": "date",
    "event.category": "keyword",
    "event.sequence": "long",
    "event.action": "keyword",
    "host.id": "keyword",
    "process.entity_id": "keyword"
  },
  "documents": [
    {
      "id": "a1",
      "@timestamp": "2026-10-21T00:00:00.000Z",
      "event.category": "process",
      "event.sequence": 1,
      "event.action": "start",
      "host.id": "h1",
      "process.entity_id": "e"
    },
    {
      "id": "a2",
      "@timestamp": "2026-10-21T00:00:01.000Z",
      "event.category": "process",
      "event.sequence": 2,
      "event.action": "start",
      "host.id": "h2",
      "process.entity_id": "e"
    },
    {
      "id": "a3",
      "@timestamp": "2026-10-21T00:00:02.000Z",
      "event.category": "process",
      "event.sequence": 3,
      "event.action": "start",
      "host.id": "h3",
      "process.entity_id": "e"
    },
    {
      "id": "stop",
      "@timestamp": "2026-10-21T00:00:03.000Z",
      "event.category": "process",
      "event.sequence": 4,
      "event.action": "end",
      "host.id": "h3",
      "process.entity_id": "e"
    },
    {
      "id": "b3",
      "@timestamp": "2026-10-21T00:00:04.000Z",
      "event.category": "network",
      "event.sequence": 5,
      "event.action": "connect",
      "host.id": "h3",
      "process.entity_id": "e"
    },
    {
      "id": "b1",
      "@timestamp": "2026-10-21T00:05:00.000Z",
      "event.category": "network",
      "event.sequence": 6,
      "event.action": "connect",
      "host.id": "h1",
      "process.entity_id": "e"
    },
    {
      "id": "b2",
      "@timestamp": "2026-10-21T00:05:01.001Z",
      "event.category": "network",
      "event.sequence": 7,
      "event.action": "connect",
      "host.id": "h2",
      "process.entity_id": "e"
    }
  ],
  "context": {
    "tiebreaker_field": "event.sequence"
  }
}
```
:::

::: anlat Until zaman damgasından daha ince bir sıraya bakar
`until` aynı join anahtarında bir sonlandırıcı olayla bekleyen diziyi iptal eder; sonlandırıcı çıktıya eklenmez. Native matcher sonlandırıcıyı önceki olumlu ordinal dahil, yeni olumlu ordinal hariç aralığında kontrol eder. Aynı timestamp'te 10=start, 15=end, 20=connect varsa dizi iptal olur; end 21 sırasındaysa tamamlanan diziyi bozmaz.

End ve önceki olumlu olay aynı belge olabilen örtüşen koşullarda alt uç da anlamlıdır. Buradaki start/end eşitlikleri ayrık olduğundan bir olay ikisi birden değildir. PID yeniden kullanımında `until` faydalıdır; entity_id ve host anahtarlarını yine dar tut. Kaynaklar: [EQL maxspan/until](https://www.elastic.co/docs/reference/query-languages/eql/eql-syntax), [v9.2.0 matcher](https://github.com/elastic/elasticsearch/blob/v9.2.0/x-pack/plugin/eql/src/main/java/org/elasticsearch/xpack/eql/execution/sequence/SequenceMatcher.java), [ordinal sınırları](https://github.com/elastic/elasticsearch/blob/v9.2.0/x-pack/plugin/eql/src/main/java/org/elasticsearch/xpack/eql/execution/search/Ordinal.java).

```eql
sequence by host.id, process.entity_id with maxspan=5m
  [process where event.action == "start"]
  [network where event.action == "connect"]
until [process where event.action == "end"]
```

```meta
dil: eql
```

```stdin
{
  "dil": "eql",
  "mapping": {
    "id": "keyword",
    "@timestamp": "date",
    "event.category": "keyword",
    "event.sequence": "long",
    "event.action": "keyword",
    "host.id": "keyword",
    "process.entity_id": "keyword"
  },
  "documents": [
    {
      "id": "a1",
      "@timestamp": "2026-10-21T00:00:00.000Z",
      "event.category": "process",
      "event.sequence": 1,
      "event.action": "start",
      "host.id": "h1",
      "process.entity_id": "e"
    },
    {
      "id": "a2",
      "@timestamp": "2026-10-21T00:00:01.000Z",
      "event.category": "process",
      "event.sequence": 2,
      "event.action": "start",
      "host.id": "h2",
      "process.entity_id": "e"
    },
    {
      "id": "a3",
      "@timestamp": "2026-10-21T00:00:02.000Z",
      "event.category": "process",
      "event.sequence": 3,
      "event.action": "start",
      "host.id": "h3",
      "process.entity_id": "e"
    },
    {
      "id": "stop",
      "@timestamp": "2026-10-21T00:00:03.000Z",
      "event.category": "process",
      "event.sequence": 4,
      "event.action": "end",
      "host.id": "h3",
      "process.entity_id": "e"
    },
    {
      "id": "b3",
      "@timestamp": "2026-10-21T00:00:04.000Z",
      "event.category": "network",
      "event.sequence": 5,
      "event.action": "connect",
      "host.id": "h3",
      "process.entity_id": "e"
    },
    {
      "id": "b1",
      "@timestamp": "2026-10-21T00:05:00.000Z",
      "event.category": "network",
      "event.sequence": 6,
      "event.action": "connect",
      "host.id": "h1",
      "process.entity_id": "e"
    },
    {
      "id": "b2",
      "@timestamp": "2026-10-21T00:05:01.001Z",
      "event.category": "network",
      "event.sequence": 7,
      "event.action": "connect",
      "host.id": "h2",
      "process.entity_id": "e"
    }
  ],
  "context": {
    "tiebreaker_field": "event.sequence"
  }
}
```
:::

::: tahmin
Girdide üç anahtar var. h1 tam beş dakika sürüyor; h2 beş dakika +1 ms; h3'te start ve connect arasında aynı anahtarlı end var. Timestamp ve event.sequence ile sıralayıp süreyi ilk olumlu olaydan ölç.

```meta
dil: eql
```

```stdin
{
  "dil": "eql",
  "mapping": {
    "id": "keyword",
    "@timestamp": "date",
    "event.category": "keyword",
    "event.sequence": "long",
    "event.action": "keyword",
    "host.id": "keyword",
    "process.entity_id": "keyword"
  },
  "documents": [
    {
      "id": "a1",
      "@timestamp": "2026-10-21T00:00:00.000Z",
      "event.category": "process",
      "event.sequence": 1,
      "event.action": "start",
      "host.id": "h1",
      "process.entity_id": "e"
    },
    {
      "id": "a2",
      "@timestamp": "2026-10-21T00:00:01.000Z",
      "event.category": "process",
      "event.sequence": 2,
      "event.action": "start",
      "host.id": "h2",
      "process.entity_id": "e"
    },
    {
      "id": "a3",
      "@timestamp": "2026-10-21T00:00:02.000Z",
      "event.category": "process",
      "event.sequence": 3,
      "event.action": "start",
      "host.id": "h3",
      "process.entity_id": "e"
    },
    {
      "id": "stop",
      "@timestamp": "2026-10-21T00:00:03.000Z",
      "event.category": "process",
      "event.sequence": 4,
      "event.action": "end",
      "host.id": "h3",
      "process.entity_id": "e"
    },
    {
      "id": "b3",
      "@timestamp": "2026-10-21T00:00:04.000Z",
      "event.category": "network",
      "event.sequence": 5,
      "event.action": "connect",
      "host.id": "h3",
      "process.entity_id": "e"
    },
    {
      "id": "b1",
      "@timestamp": "2026-10-21T00:05:00.000Z",
      "event.category": "network",
      "event.sequence": 6,
      "event.action": "connect",
      "host.id": "h1",
      "process.entity_id": "e"
    },
    {
      "id": "b2",
      "@timestamp": "2026-10-21T00:05:01.001Z",
      "event.category": "network",
      "event.sequence": 7,
      "event.action": "connect",
      "host.id": "h2",
      "process.entity_id": "e"
    }
  ],
  "context": {
    "tiebreaker_field": "event.sequence"
  }
}
```

```eql
sequence by host.id, process.entity_id with maxspan=5m
  [process where event.action == "start"]
  [network where event.action == "connect"]
until [process where event.action == "end"]
```

???

h1 a1–b1 tam eşikte kabul edilir. h2 a2–b2 süreyi 1 ms aşar. h3 a3–b3, stop ile iptal olur. Çıktıya stop yazılmaz.

```text
a1 -> b1
```
:::

::: gorev Beş dakikalık kapalı süre sınırı
Aynı host.id ve process.entity_id için process/start ardından network/connect dizisi yaz; ilk-son süre en fazla 5 dakika olsun. Henüz until kullanma: end olayları bu görevde etkisizdir. Tam eşik kabul, 1 ms üstü red; yanlış anahtar veya ters sıra red.

```meta
dil: eql
```

```stdin
{
  "dil": "eql",
  "mapping": {
    "id": "keyword",
    "@timestamp": "date",
    "event.category": "keyword",
    "event.sequence": "long",
    "event.action": "keyword",
    "host.id": "keyword",
    "process.entity_id": "keyword"
  },
  "documents": [
    {
      "id": "a1",
      "@timestamp": "2026-10-21T00:00:00.000Z",
      "event.category": "process",
      "event.sequence": 1,
      "event.action": "start",
      "host.id": "h1",
      "process.entity_id": "e"
    },
    {
      "id": "a2",
      "@timestamp": "2026-10-21T00:00:01.000Z",
      "event.category": "process",
      "event.sequence": 2,
      "event.action": "start",
      "host.id": "h2",
      "process.entity_id": "e"
    },
    {
      "id": "a3",
      "@timestamp": "2026-10-21T00:00:02.000Z",
      "event.category": "process",
      "event.sequence": 3,
      "event.action": "start",
      "host.id": "h3",
      "process.entity_id": "e"
    },
    {
      "id": "stop",
      "@timestamp": "2026-10-21T00:00:03.000Z",
      "event.category": "process",
      "event.sequence": 4,
      "event.action": "end",
      "host.id": "h3",
      "process.entity_id": "e"
    },
    {
      "id": "b3",
      "@timestamp": "2026-10-21T00:00:04.000Z",
      "event.category": "network",
      "event.sequence": 5,
      "event.action": "connect",
      "host.id": "h3",
      "process.entity_id": "e"
    },
    {
      "id": "b1",
      "@timestamp": "2026-10-21T00:05:00.000Z",
      "event.category": "network",
      "event.sequence": 6,
      "event.action": "connect",
      "host.id": "h1",
      "process.entity_id": "e"
    },
    {
      "id": "b2",
      "@timestamp": "2026-10-21T00:05:01.001Z",
      "event.category": "network",
      "event.sequence": 7,
      "event.action": "connect",
      "host.id": "h2",
      "process.entity_id": "e"
    }
  ],
  "context": {
    "tiebreaker_field": "event.sequence"
  }
}
```

```starter
any where false
```

```test
eq(eslesenler(),[["a3","b3"],["a1","b1"]],"dersteki gerçek sorgu sonucu")
eq(eslesenler(veri={"documents":list(reversed(korpus["documents"]))}),[["a3","b3"],["a1","b1"]],"girdi sırası değil timestamp+tiebreaker sırası")
from datetime import datetime, timedelta, timezone
def olay(kimlik,t_ms=0,kategori="process",sira=0,**alanlar):
    zaman=datetime(2026,10,21,tzinfo=timezone.utc)+timedelta(milliseconds=t_ms)
    e={"id":kimlik,"@timestamp":zaman.isoformat(timespec="milliseconds").replace("+00:00","Z"),"event.category":kategori,"event.sequence":sira}
    e.update(alanlar)
    return e
def p(k,t,host="h",entity="e",cat="process",action="start",seq=0):
    return olay(k,t,cat,seq,**{"host.id":host,"process.entity_id":entity,"event.action":action})
for fark,sonuc in ((299999,[["a","b"]]),(300000,[["a","b"]]),(300001,[])):
    eq(eslesenler(veri={"documents":[p("a",0),p("b",fark,cat="network",action="connect")]}),sonuc,"maxspan eşiği "+str(fark))
eq(eslesenler(veri={"documents":[p("a",0,seq=1),p("b",0,cat="network",action="connect",seq=2)]}),[["a","b"]],"sıfır süre doğru ordinalle mümkün")
for b in (p("b",-1,cat="network",action="connect"),p("b",1,host="other",cat="network",action="connect"),p("b",1,entity="other",cat="network",action="connect"),p("b",1,cat="file",action="connect"),p("b",1,cat="network",action="wrong")):
    eq(eslesenler(veri={"documents":[p("a",0),b]}),[],"zaman ve bağımsız ikinci aşama koşulları")
eq(eslesenler(veri={"documents":[p("a",0),p("stop",1,action="end"),p("b",2,cat="network",action="connect")]}),[["a","b"]],"bu görev sonlandırıcı kullanmıyor")

# == ile : arasındaki farkı aşama başına bağımsız büyük harfle sınarız.
# Korpus sorgu metninden türetilmez; her olay aşağıdaki sabit sentetik veridir.
def harf_olay(k, t, kategori, eylem):
    return olay(k, t, kategori, **{"host.id":"case-host", "process.entity_id":"case-entity", "user.id":"case-user", "event.action":eylem, "process.name":"powershell.exe", "destination.port":443, "file.path":"C:\\Temp\\case.exe", "process.executable":"C:\\Temp\\case.exe"})
harf_taban = [harf_olay("case-0", 0, 'process', 'start'), harf_olay("case-1", 2, 'network', 'connect')]
harf_docs = [dict(e) for e in harf_taban]
harf_docs[0]["event.action"] = 'START'
eq(eslesenler(veri={"documents":harf_docs}), [], "1. olumlu aşamada action == harf duyarlıdır")
harf_docs = [dict(e) for e in harf_taban]
harf_docs[1]["event.action"] = 'CONNECT'
eq(eslesenler(veri={"documents":harf_docs}), [], "2. olumlu aşamada action == harf duyarlıdır")
```

```solution
sequence by host.id, process.entity_id with maxspan=5m
  [process where event.action == "start"]
  [network where event.action == "connect"]
```

```hint
sequence by ... with maxspan=5m; süreyi kodla/Python ile hesaplaman gerekmiyor, sorgu ifadesini yaz.
```
:::

::: gorev Süreyi koru, sonlandırıcıyı ekle
Önceki diziyi aynı 5 dakikalık sınırla yaz ve aynı anahtardaki process/end için until ekle. End tam olumlu uç timestamp'inde olsa bile event.sequence sırasını kullan; başka host/entity end'i veya tamamlanmadan sonraki end engellemesin.

```meta
dil: eql
```

```stdin
{
  "dil": "eql",
  "mapping": {
    "id": "keyword",
    "@timestamp": "date",
    "event.category": "keyword",
    "event.sequence": "long",
    "event.action": "keyword",
    "host.id": "keyword",
    "process.entity_id": "keyword"
  },
  "documents": [
    {
      "id": "a1",
      "@timestamp": "2026-10-21T00:00:00.000Z",
      "event.category": "process",
      "event.sequence": 1,
      "event.action": "start",
      "host.id": "h1",
      "process.entity_id": "e"
    },
    {
      "id": "a2",
      "@timestamp": "2026-10-21T00:00:01.000Z",
      "event.category": "process",
      "event.sequence": 2,
      "event.action": "start",
      "host.id": "h2",
      "process.entity_id": "e"
    },
    {
      "id": "a3",
      "@timestamp": "2026-10-21T00:00:02.000Z",
      "event.category": "process",
      "event.sequence": 3,
      "event.action": "start",
      "host.id": "h3",
      "process.entity_id": "e"
    },
    {
      "id": "stop",
      "@timestamp": "2026-10-21T00:00:03.000Z",
      "event.category": "process",
      "event.sequence": 4,
      "event.action": "end",
      "host.id": "h3",
      "process.entity_id": "e"
    },
    {
      "id": "b3",
      "@timestamp": "2026-10-21T00:00:04.000Z",
      "event.category": "network",
      "event.sequence": 5,
      "event.action": "connect",
      "host.id": "h3",
      "process.entity_id": "e"
    },
    {
      "id": "b1",
      "@timestamp": "2026-10-21T00:05:00.000Z",
      "event.category": "network",
      "event.sequence": 6,
      "event.action": "connect",
      "host.id": "h1",
      "process.entity_id": "e"
    },
    {
      "id": "b2",
      "@timestamp": "2026-10-21T00:05:01.001Z",
      "event.category": "network",
      "event.sequence": 7,
      "event.action": "connect",
      "host.id": "h2",
      "process.entity_id": "e"
    }
  ],
  "context": {
    "tiebreaker_field": "event.sequence"
  }
}
```

```starter
any where false
```

```test
eq(eslesenler(),[["a1","b1"]],"dersteki gerçek sorgu sonucu")
eq(eslesenler(veri={"documents":list(reversed(korpus["documents"]))}),[["a1","b1"]],"girdi sırası değil timestamp+tiebreaker sırası")
from datetime import datetime, timedelta, timezone
def olay(kimlik,t_ms=0,kategori="process",sira=0,**alanlar):
    zaman=datetime(2026,10,21,tzinfo=timezone.utc)+timedelta(milliseconds=t_ms)
    e={"id":kimlik,"@timestamp":zaman.isoformat(timespec="milliseconds").replace("+00:00","Z"),"event.category":kategori,"event.sequence":sira}
    e.update(alanlar)
    return e
def p(k,t,host="h",entity="e",cat="process",action="start",seq=0):
    return olay(k,t,cat,seq,**{"host.id":host,"process.entity_id":entity,"event.action":action})
for fark,sonuc in ((299999,[["a","b"]]),(300000,[["a","b"]]),(300001,[])):
    eq(eslesenler(veri={"documents":[p("a",0),p("b",fark,cat="network",action="connect")]}),sonuc,"until süre sınırını kaldırmaz")
for seq,sonuc in ((9,[["a","b"]]),(11,[]),(19,[]),(21,[["a","b"]])):
    eq(eslesenler(veri={"documents":[p("a",0,seq=10),p("stop",0,action="end",seq=seq),p("b",0,cat="network",action="connect",seq=20)]}),sonuc,"aynı timestamp end sırası "+str(seq))
for stop in (p("stop",1,host="other",action="end"),p("stop",1,entity="other",action="end"),p("stop",1,cat="file",action="end"),p("stop",1,action="wrong")):
    eq(eslesenler(veri={"documents":[p("a",0),stop,p("b",2,cat="network",action="connect")]}),[["a","b"]],"until anahtar/category/action ayrı ayrı")

# == ile : arasındaki farkı aşama başına bağımsız büyük harfle sınarız.
# Korpus sorgu metninden türetilmez; her olay aşağıdaki sabit sentetik veridir.
def harf_olay(k, t, kategori, eylem):
    return olay(k, t, kategori, **{"host.id":"case-host", "process.entity_id":"case-entity", "user.id":"case-user", "event.action":eylem, "process.name":"powershell.exe", "destination.port":443, "file.path":"C:\\Temp\\case.exe", "process.executable":"C:\\Temp\\case.exe"})
harf_taban = [harf_olay("case-0", 0, 'process', 'start'), harf_olay("case-1", 2, 'network', 'connect')]
harf_docs = [dict(e) for e in harf_taban]
harf_docs[0]["event.action"] = 'START'
eq(eslesenler(veri={"documents":harf_docs}), [], "1. olumlu aşamada action == harf duyarlıdır")
harf_docs = [dict(e) for e in harf_taban]
harf_docs[1]["event.action"] = 'CONNECT'
eq(eslesenler(veri={"documents":harf_docs}), [], "2. olumlu aşamada action == harf duyarlıdır")
harf_docs = [dict(e) for e in harf_taban]
harf_docs.insert(1, harf_olay("case-negative", 1, 'process', 'END'))
eq(eslesenler(veri={"documents":harf_docs}), [['case-0', 'case-1']], "until action == büyük harfli olayı eşleştirmez")
```

```solution
sequence by host.id, process.entity_id with maxspan=5m
  [process where event.action == "start"]
  [network where event.action == "connect"]
until [process where event.action == "end"]
```

```hint
until [process where event.action == "end"]; ortak by anahtarları sonlandırıcıya da uygulanır.
```
:::
