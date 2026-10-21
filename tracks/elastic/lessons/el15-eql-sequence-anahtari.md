---
id: el15
title: EQL · Sequence ve Anahtar
summary: Olayları sıralı ve anahtarlı eşleştir; bütün olası çiftler yerine pending-state davranışını ölç.
---

::: anlat Aynı host ve aynı süreç örneği
`sequence` köşeli parantezli olay koşullarını sırayla ister. `by host.id, process.entity_id` her iki alanın ortak değerini join anahtarı yapar. Aynı PID başka makinede veya sürecin sonraki yaşamında tekrar kullanılabilir; entity_id ile host birlikte daha dar bir ilişki kurar. Bu alanların güvenilirliği yine veri kaynağına bağlıdır.

Tezgâh olayları `@timestamp`, sonra burada açıkça ayarlanmış `event.sequence` tiebreaker'ı ile artan sıraya dizer. Eşit timestamp tek başına sıra değildir. Tam ordinal çiftleri benzersiz olmalıdır; yerel model Elasticsearch'ün gizli shard sırasını taklit etmez. Zorunlu join alanı null ise olay eşleşmeye katılmaz; `?user.id` gibi opsiyonel join alanı null anahtara izin verir.

```eql
sequence by host.id, process.entity_id
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
    "process.entity_id": "keyword",
    "process.pid": "long",
    "user.id": "keyword",
    "file.path": "keyword",
    "process.executable": "keyword"
  },
  "documents": [
    {
      "id": "c1",
      "@timestamp": "2026-10-21T00:00:00.000Z",
      "event.category": "process",
      "event.sequence": 1,
      "event.action": "start",
      "host.id": "h1",
      "process.entity_id": "e1",
      "process.pid": 100
    },
    {
      "id": "c2",
      "@timestamp": "2026-10-21T00:00:01.000Z",
      "event.category": "process",
      "event.sequence": 2,
      "event.action": "start",
      "host.id": "h1",
      "process.entity_id": "e1",
      "process.pid": 100
    },
    {
      "id": "n1",
      "@timestamp": "2026-10-21T00:00:02.000Z",
      "event.category": "network",
      "event.sequence": 3,
      "event.action": "connect",
      "host.id": "h1",
      "process.entity_id": "e1",
      "process.pid": 100
    },
    {
      "id": "n2",
      "@timestamp": "2026-10-21T00:00:03.000Z",
      "event.category": "network",
      "event.sequence": 4,
      "event.action": "connect",
      "host.id": "h1",
      "process.entity_id": "e1",
      "process.pid": 100
    },
    {
      "id": "c3",
      "@timestamp": "2026-10-21T00:00:04.000Z",
      "event.category": "process",
      "event.sequence": 5,
      "event.action": "start",
      "host.id": "h2",
      "process.entity_id": "e1",
      "process.pid": 100
    },
    {
      "id": "n3",
      "@timestamp": "2026-10-21T00:00:05.000Z",
      "event.category": "network",
      "event.sequence": 6,
      "event.action": "connect",
      "host.id": "h1",
      "process.entity_id": "e1",
      "process.pid": 100
    },
    {
      "id": "n4",
      "@timestamp": "2026-10-21T00:00:06.000Z",
      "event.category": "network",
      "event.sequence": 7,
      "event.action": "connect",
      "host.id": "h2",
      "process.entity_id": "e1",
      "process.pid": 100
    },
    {
      "id": "c4",
      "@timestamp": "2026-10-21T00:00:07.000Z",
      "event.category": "process",
      "event.sequence": 8,
      "event.action": "start",
      "host.id": "h1",
      "process.entity_id": "e2",
      "process.pid": 100
    },
    {
      "id": "n5",
      "@timestamp": "2026-10-21T00:00:08.000Z",
      "event.category": "network",
      "event.sequence": 9,
      "event.action": "connect",
      "host.id": "h1",
      "process.entity_id": "e3",
      "process.pid": 100
    },
    {
      "id": "n6",
      "@timestamp": "2026-10-21T00:00:09.000Z",
      "event.category": "network",
      "event.sequence": 10,
      "event.action": "connect",
      "host.id": "h1",
      "process.entity_id": "e2",
      "process.pid": 100
    },
    {
      "id": "f1",
      "@timestamp": "2026-10-21T00:00:10.000Z",
      "event.category": "file",
      "event.sequence": 11,
      "event.action": "create",
      "host.id": "h1",
      "file.path": "C:\\Tools\\x.exe"
    },
    {
      "id": "p1",
      "@timestamp": "2026-10-21T00:00:11.000Z",
      "event.category": "process",
      "event.sequence": 12,
      "event.action": "start",
      "host.id": "h1",
      "process.entity_id": "e4",
      "process.executable": "C:\\Tools\\x.exe"
    }
  ],
  "context": {
    "tiebreaker_field": "event.sequence"
  }
}
```
:::

::: anlat Bütün çiftler değil, tüketilen son aday
Aynı anahtarda iki start, sonra bir connect varsa son start bekleyen önceki adayı değiştirir. Tamamlanan aday tüketilir; sonraki connect aynı start'ı yeniden kullanmaz. Ayrı anahtarların makineleri ayrıdır. Bir sonraki aşamaya geçmiş bekleyen dizi ile yeni başlangıç da ayrı aşamalarda tutulur. Bu nedenle `for a in olaylar: for b in olaylar` ile tüm çiftleri toplamak EQL değildir.

Her aşamanın farklı alanını eşitlemek için `] by file.path` ve `] by process.executable` kullanılabilir. Ortak `host.id` buna eklenir; aşama anahtarlarının sayısı/türü uyumlu olmalıdır. Yerel model en fazla 32 aşama, 8 anahtar, skaler alan ve artan sıra destekler. Kaynak: [Elastic sequence eşleştirme davranışı](https://www.elastic.co/docs/reference/query-languages/eql/eql-syntax#eql-sequences).

```eql
sequence by host.id
  [file where event.action == "create"] by file.path
  [process where event.action == "start"] by process.executable
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
    "process.entity_id": "keyword",
    "process.pid": "long",
    "user.id": "keyword",
    "file.path": "keyword",
    "process.executable": "keyword"
  },
  "documents": [
    {
      "id": "c1",
      "@timestamp": "2026-10-21T00:00:00.000Z",
      "event.category": "process",
      "event.sequence": 1,
      "event.action": "start",
      "host.id": "h1",
      "process.entity_id": "e1",
      "process.pid": 100
    },
    {
      "id": "c2",
      "@timestamp": "2026-10-21T00:00:01.000Z",
      "event.category": "process",
      "event.sequence": 2,
      "event.action": "start",
      "host.id": "h1",
      "process.entity_id": "e1",
      "process.pid": 100
    },
    {
      "id": "n1",
      "@timestamp": "2026-10-21T00:00:02.000Z",
      "event.category": "network",
      "event.sequence": 3,
      "event.action": "connect",
      "host.id": "h1",
      "process.entity_id": "e1",
      "process.pid": 100
    },
    {
      "id": "n2",
      "@timestamp": "2026-10-21T00:00:03.000Z",
      "event.category": "network",
      "event.sequence": 4,
      "event.action": "connect",
      "host.id": "h1",
      "process.entity_id": "e1",
      "process.pid": 100
    },
    {
      "id": "c3",
      "@timestamp": "2026-10-21T00:00:04.000Z",
      "event.category": "process",
      "event.sequence": 5,
      "event.action": "start",
      "host.id": "h2",
      "process.entity_id": "e1",
      "process.pid": 100
    },
    {
      "id": "n3",
      "@timestamp": "2026-10-21T00:00:05.000Z",
      "event.category": "network",
      "event.sequence": 6,
      "event.action": "connect",
      "host.id": "h1",
      "process.entity_id": "e1",
      "process.pid": 100
    },
    {
      "id": "n4",
      "@timestamp": "2026-10-21T00:00:06.000Z",
      "event.category": "network",
      "event.sequence": 7,
      "event.action": "connect",
      "host.id": "h2",
      "process.entity_id": "e1",
      "process.pid": 100
    },
    {
      "id": "c4",
      "@timestamp": "2026-10-21T00:00:07.000Z",
      "event.category": "process",
      "event.sequence": 8,
      "event.action": "start",
      "host.id": "h1",
      "process.entity_id": "e2",
      "process.pid": 100
    },
    {
      "id": "n5",
      "@timestamp": "2026-10-21T00:00:08.000Z",
      "event.category": "network",
      "event.sequence": 9,
      "event.action": "connect",
      "host.id": "h1",
      "process.entity_id": "e3",
      "process.pid": 100
    },
    {
      "id": "n6",
      "@timestamp": "2026-10-21T00:00:09.000Z",
      "event.category": "network",
      "event.sequence": 10,
      "event.action": "connect",
      "host.id": "h1",
      "process.entity_id": "e2",
      "process.pid": 100
    },
    {
      "id": "f1",
      "@timestamp": "2026-10-21T00:00:10.000Z",
      "event.category": "file",
      "event.sequence": 11,
      "event.action": "create",
      "host.id": "h1",
      "file.path": "C:\\Tools\\x.exe"
    },
    {
      "id": "p1",
      "@timestamp": "2026-10-21T00:00:11.000Z",
      "event.category": "process",
      "event.sequence": 12,
      "event.action": "start",
      "host.id": "h1",
      "process.entity_id": "e4",
      "process.executable": "C:\\Tools\\x.exe"
    }
  ],
  "context": {
    "tiebreaker_field": "event.sequence"
  }
}
```
:::

::: tahmin
Olayların tamamı girdidedir. `c1` ve `c2` aynı anahtarda iki başlangıçtır; n1/n2/n3 aynı anahtarda bağlantılar taşır. Host ve entity_id'yi, tamamlanan adayın tüketilmesini birlikte izle. Hangi diziler oluşur?

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
    "process.entity_id": "keyword",
    "process.pid": "long",
    "user.id": "keyword",
    "file.path": "keyword",
    "process.executable": "keyword"
  },
  "documents": [
    {
      "id": "c1",
      "@timestamp": "2026-10-21T00:00:00.000Z",
      "event.category": "process",
      "event.sequence": 1,
      "event.action": "start",
      "host.id": "h1",
      "process.entity_id": "e1",
      "process.pid": 100
    },
    {
      "id": "c2",
      "@timestamp": "2026-10-21T00:00:01.000Z",
      "event.category": "process",
      "event.sequence": 2,
      "event.action": "start",
      "host.id": "h1",
      "process.entity_id": "e1",
      "process.pid": 100
    },
    {
      "id": "n1",
      "@timestamp": "2026-10-21T00:00:02.000Z",
      "event.category": "network",
      "event.sequence": 3,
      "event.action": "connect",
      "host.id": "h1",
      "process.entity_id": "e1",
      "process.pid": 100
    },
    {
      "id": "n2",
      "@timestamp": "2026-10-21T00:00:03.000Z",
      "event.category": "network",
      "event.sequence": 4,
      "event.action": "connect",
      "host.id": "h1",
      "process.entity_id": "e1",
      "process.pid": 100
    },
    {
      "id": "c3",
      "@timestamp": "2026-10-21T00:00:04.000Z",
      "event.category": "process",
      "event.sequence": 5,
      "event.action": "start",
      "host.id": "h2",
      "process.entity_id": "e1",
      "process.pid": 100
    },
    {
      "id": "n3",
      "@timestamp": "2026-10-21T00:00:05.000Z",
      "event.category": "network",
      "event.sequence": 6,
      "event.action": "connect",
      "host.id": "h1",
      "process.entity_id": "e1",
      "process.pid": 100
    },
    {
      "id": "n4",
      "@timestamp": "2026-10-21T00:00:06.000Z",
      "event.category": "network",
      "event.sequence": 7,
      "event.action": "connect",
      "host.id": "h2",
      "process.entity_id": "e1",
      "process.pid": 100
    },
    {
      "id": "c4",
      "@timestamp": "2026-10-21T00:00:07.000Z",
      "event.category": "process",
      "event.sequence": 8,
      "event.action": "start",
      "host.id": "h1",
      "process.entity_id": "e2",
      "process.pid": 100
    },
    {
      "id": "n5",
      "@timestamp": "2026-10-21T00:00:08.000Z",
      "event.category": "network",
      "event.sequence": 9,
      "event.action": "connect",
      "host.id": "h1",
      "process.entity_id": "e3",
      "process.pid": 100
    },
    {
      "id": "n6",
      "@timestamp": "2026-10-21T00:00:09.000Z",
      "event.category": "network",
      "event.sequence": 10,
      "event.action": "connect",
      "host.id": "h1",
      "process.entity_id": "e2",
      "process.pid": 100
    },
    {
      "id": "f1",
      "@timestamp": "2026-10-21T00:00:10.000Z",
      "event.category": "file",
      "event.sequence": 11,
      "event.action": "create",
      "host.id": "h1",
      "file.path": "C:\\Tools\\x.exe"
    },
    {
      "id": "p1",
      "@timestamp": "2026-10-21T00:00:11.000Z",
      "event.category": "process",
      "event.sequence": 12,
      "event.action": "start",
      "host.id": "h1",
      "process.entity_id": "e4",
      "process.executable": "C:\\Tools\\x.exe"
    }
  ],
  "context": {
    "tiebreaker_field": "event.sequence"
  }
}
```

```eql
sequence by host.id, process.entity_id
  [process where event.action == "start"]
  [network where event.action == "connect"]
```

???

İlk anahtarda c2, c1'in yerini alır ve n1 ile tamamlanır; n2/n3 için aynı başlangıç yeniden kullanılmaz. h2/e1 c3–n4 olur. h1/e2 yalnız n6 ile tamamlanır; n5 farklı entity'dir. f1 başka kategori; p1'in e4 anahtarında bağlantı yoktur.

```text
c2 -> n1
c3 -> n4
c4 -> n6
```
:::

::: gorev Host ve entity ile süreçten bağlantıya
Aynı `host.id` ve `process.entity_id` için process/start ardından network/connect dizisi yaz. Sadece sıralı olaylar, doğru kategori ve iki dolu anahtar kabul edilsin. Aynı PID'nin eşitliği yetmesin. Aynı anahtardaki son başlangıç ve tüketim native EQL sıra makinesi sözleşmesine uysun.

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
    "process.entity_id": "keyword",
    "process.pid": "long",
    "user.id": "keyword",
    "file.path": "keyword",
    "process.executable": "keyword"
  },
  "documents": [
    {
      "id": "c1",
      "@timestamp": "2026-10-21T00:00:00.000Z",
      "event.category": "process",
      "event.sequence": 1,
      "event.action": "start",
      "host.id": "h1",
      "process.entity_id": "e1",
      "process.pid": 100
    },
    {
      "id": "c2",
      "@timestamp": "2026-10-21T00:00:01.000Z",
      "event.category": "process",
      "event.sequence": 2,
      "event.action": "start",
      "host.id": "h1",
      "process.entity_id": "e1",
      "process.pid": 100
    },
    {
      "id": "n1",
      "@timestamp": "2026-10-21T00:00:02.000Z",
      "event.category": "network",
      "event.sequence": 3,
      "event.action": "connect",
      "host.id": "h1",
      "process.entity_id": "e1",
      "process.pid": 100
    },
    {
      "id": "n2",
      "@timestamp": "2026-10-21T00:00:03.000Z",
      "event.category": "network",
      "event.sequence": 4,
      "event.action": "connect",
      "host.id": "h1",
      "process.entity_id": "e1",
      "process.pid": 100
    },
    {
      "id": "c3",
      "@timestamp": "2026-10-21T00:00:04.000Z",
      "event.category": "process",
      "event.sequence": 5,
      "event.action": "start",
      "host.id": "h2",
      "process.entity_id": "e1",
      "process.pid": 100
    },
    {
      "id": "n3",
      "@timestamp": "2026-10-21T00:00:05.000Z",
      "event.category": "network",
      "event.sequence": 6,
      "event.action": "connect",
      "host.id": "h1",
      "process.entity_id": "e1",
      "process.pid": 100
    },
    {
      "id": "n4",
      "@timestamp": "2026-10-21T00:00:06.000Z",
      "event.category": "network",
      "event.sequence": 7,
      "event.action": "connect",
      "host.id": "h2",
      "process.entity_id": "e1",
      "process.pid": 100
    },
    {
      "id": "c4",
      "@timestamp": "2026-10-21T00:00:07.000Z",
      "event.category": "process",
      "event.sequence": 8,
      "event.action": "start",
      "host.id": "h1",
      "process.entity_id": "e2",
      "process.pid": 100
    },
    {
      "id": "n5",
      "@timestamp": "2026-10-21T00:00:08.000Z",
      "event.category": "network",
      "event.sequence": 9,
      "event.action": "connect",
      "host.id": "h1",
      "process.entity_id": "e3",
      "process.pid": 100
    },
    {
      "id": "n6",
      "@timestamp": "2026-10-21T00:00:09.000Z",
      "event.category": "network",
      "event.sequence": 10,
      "event.action": "connect",
      "host.id": "h1",
      "process.entity_id": "e2",
      "process.pid": 100
    },
    {
      "id": "f1",
      "@timestamp": "2026-10-21T00:00:10.000Z",
      "event.category": "file",
      "event.sequence": 11,
      "event.action": "create",
      "host.id": "h1",
      "file.path": "C:\\Tools\\x.exe"
    },
    {
      "id": "p1",
      "@timestamp": "2026-10-21T00:00:11.000Z",
      "event.category": "process",
      "event.sequence": 12,
      "event.action": "start",
      "host.id": "h1",
      "process.entity_id": "e4",
      "process.executable": "C:\\Tools\\x.exe"
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
eq(eslesenler(),[["c2","n1"],["c3","n4"],["c4","n6"]],"dersteki gerçek sorgu sonucu")
eq(eslesenler(veri={"documents":list(reversed(korpus["documents"]))}),[["c2","n1"],["c3","n4"],["c4","n6"]],"girdi sırası değil timestamp+tiebreaker sırası")
from datetime import datetime, timedelta, timezone
def olay(kimlik,t_ms=0,kategori="process",sira=0,**alanlar):
    zaman=datetime(2026,10,21,tzinfo=timezone.utc)+timedelta(milliseconds=t_ms)
    e={"id":kimlik,"@timestamp":zaman.isoformat(timespec="milliseconds").replace("+00:00","Z"),"event.category":kategori,"event.sequence":sira}
    e.update(alanlar)
    return e
def p(k,t,host="h",entity="e",cat="process",action="start",seq=0):
    return olay(k,t,cat,seq,**{"host.id":host,"process.entity_id":entity,"process.pid":42,"event.action":action})
docs=[p("a1",0),p("a2",1),p("wronghost",2,"other","e","network","connect"),p("wrongentity",3,"h","new","network","connect"),p("b",4,cat="network",action="connect"),p("b2",5,cat="network",action="connect")]
eq(eslesenler(veri={"documents":docs}),[["a2","b"]],"son pending; host/entity bağımsız ve tamamlanan aday tüketilir")
for cat,action in (("file","start"),("process","wrong")):
    eq(eslesenler(veri={"documents":[p("a",0,cat=cat,action=action),p("b",1,cat="network",action="connect")]}),[],"ilk aşama category/action")
for cat,action in (("file","connect"),("network","wrong")):
    eq(eslesenler(veri={"documents":[p("a",0),p("b",1,cat=cat,action=action)]}),[],"ikinci aşama category/action")
eq(eslesenler(veri={"documents":[p("a",0,seq=2),p("b",0,cat="network",action="connect",seq=1)]}),[],"aynı timestamp ters tiebreaker")
eq(eslesenler(veri={"documents":[p("a",0,seq=1),p("b",0,cat="network",action="connect",seq=2)]}),[["a","b"]],"aynı timestamp doğru tiebreaker")
eq(eslesenler(veri={"documents":[p("a",0,entity=None),p("b",1,entity=None,cat="network",action="connect")]}),[],"zorunlu null join anahtarı dışlanır")

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
sequence by host.id, process.entity_id
  [process where event.action == "start"]
  [network where event.action == "connect"]
```

```hint
sequence by host.id, process.entity_id; sonra process/start ve network/connect köşeli aşamaları.
```
:::

::: gorev Dosya yolunu çalıştırılabilir yoluna bağla
Ortak `host.id` altında file/create olayının `file.path` değeri, sonraki process/start olayının `process.executable` değerine tam eşit olsun. Her aşamanın `by` alanını ayrı yaz. Aynı yol başka hostta, farklı harfle, eksik/null yol veya ters zaman tek başına yetmez.

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
    "process.entity_id": "keyword",
    "process.pid": "long",
    "user.id": "keyword",
    "file.path": "keyword",
    "process.executable": "keyword"
  },
  "documents": [
    {
      "id": "c1",
      "@timestamp": "2026-10-21T00:00:00.000Z",
      "event.category": "process",
      "event.sequence": 1,
      "event.action": "start",
      "host.id": "h1",
      "process.entity_id": "e1",
      "process.pid": 100
    },
    {
      "id": "c2",
      "@timestamp": "2026-10-21T00:00:01.000Z",
      "event.category": "process",
      "event.sequence": 2,
      "event.action": "start",
      "host.id": "h1",
      "process.entity_id": "e1",
      "process.pid": 100
    },
    {
      "id": "n1",
      "@timestamp": "2026-10-21T00:00:02.000Z",
      "event.category": "network",
      "event.sequence": 3,
      "event.action": "connect",
      "host.id": "h1",
      "process.entity_id": "e1",
      "process.pid": 100
    },
    {
      "id": "n2",
      "@timestamp": "2026-10-21T00:00:03.000Z",
      "event.category": "network",
      "event.sequence": 4,
      "event.action": "connect",
      "host.id": "h1",
      "process.entity_id": "e1",
      "process.pid": 100
    },
    {
      "id": "c3",
      "@timestamp": "2026-10-21T00:00:04.000Z",
      "event.category": "process",
      "event.sequence": 5,
      "event.action": "start",
      "host.id": "h2",
      "process.entity_id": "e1",
      "process.pid": 100
    },
    {
      "id": "n3",
      "@timestamp": "2026-10-21T00:00:05.000Z",
      "event.category": "network",
      "event.sequence": 6,
      "event.action": "connect",
      "host.id": "h1",
      "process.entity_id": "e1",
      "process.pid": 100
    },
    {
      "id": "n4",
      "@timestamp": "2026-10-21T00:00:06.000Z",
      "event.category": "network",
      "event.sequence": 7,
      "event.action": "connect",
      "host.id": "h2",
      "process.entity_id": "e1",
      "process.pid": 100
    },
    {
      "id": "c4",
      "@timestamp": "2026-10-21T00:00:07.000Z",
      "event.category": "process",
      "event.sequence": 8,
      "event.action": "start",
      "host.id": "h1",
      "process.entity_id": "e2",
      "process.pid": 100
    },
    {
      "id": "n5",
      "@timestamp": "2026-10-21T00:00:08.000Z",
      "event.category": "network",
      "event.sequence": 9,
      "event.action": "connect",
      "host.id": "h1",
      "process.entity_id": "e3",
      "process.pid": 100
    },
    {
      "id": "n6",
      "@timestamp": "2026-10-21T00:00:09.000Z",
      "event.category": "network",
      "event.sequence": 10,
      "event.action": "connect",
      "host.id": "h1",
      "process.entity_id": "e2",
      "process.pid": 100
    },
    {
      "id": "f1",
      "@timestamp": "2026-10-21T00:00:10.000Z",
      "event.category": "file",
      "event.sequence": 11,
      "event.action": "create",
      "host.id": "h1",
      "file.path": "C:\\Tools\\x.exe"
    },
    {
      "id": "p1",
      "@timestamp": "2026-10-21T00:00:11.000Z",
      "event.category": "process",
      "event.sequence": 12,
      "event.action": "start",
      "host.id": "h1",
      "process.entity_id": "e4",
      "process.executable": "C:\\Tools\\x.exe"
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
eq(eslesenler(),[["f1","p1"]],"dersteki gerçek sorgu sonucu")
eq(eslesenler(veri={"documents":list(reversed(korpus["documents"]))}),[["f1","p1"]],"girdi sırası değil timestamp+tiebreaker sırası")
from datetime import datetime, timedelta, timezone
def olay(kimlik,t_ms=0,kategori="process",sira=0,**alanlar):
    zaman=datetime(2026,10,21,tzinfo=timezone.utc)+timedelta(milliseconds=t_ms)
    e={"id":kimlik,"@timestamp":zaman.isoformat(timespec="milliseconds").replace("+00:00","Z"),"event.category":kategori,"event.sequence":sira}
    e.update(alanlar)
    return e
def f(k,t,host="h",path="C:\\Tools\\x.exe",cat="file",action="create"):
    return olay(k,t,cat,**{"host.id":host,"file.path":path,"event.action":action})
def p(k,t,host="h",path="C:\\Tools\\x.exe",cat="process",action="start"):
    return olay(k,t,cat,**{"host.id":host,"process.executable":path,"event.action":action})
eq(eslesenler(veri={"documents":[f("f",0),p("p",1)]}),[["f","p"]],"farklı alanlarda aynı yol")
for bad in (p("p",1,host="other"),p("p",1,path="C:\\Tools\\X.exe"),p("p",1,path=None),p("p",1,cat="network"),p("p",1,action="wrong"),p("p",-1)):
    eq(eslesenler(veri={"documents":[f("f",0),bad]}),[],"host/yol/category/action/zaman bağımsız")
for bad in (f("f",0,path=None),f("f",0,cat="network"),f("f",0,action="wrong")):
    eq(eslesenler(veri={"documents":[bad,p("p",1)]}),[],"dosya aşaması zorunlu koşulları")

# == ile : arasındaki farkı aşama başına bağımsız büyük harfle sınarız.
# Korpus sorgu metninden türetilmez; her olay aşağıdaki sabit sentetik veridir.
def harf_olay(k, t, kategori, eylem):
    return olay(k, t, kategori, **{"host.id":"case-host", "process.entity_id":"case-entity", "user.id":"case-user", "event.action":eylem, "process.name":"powershell.exe", "destination.port":443, "file.path":"C:\\Temp\\case.exe", "process.executable":"C:\\Temp\\case.exe"})
harf_taban = [harf_olay("case-0", 0, 'file', 'create'), harf_olay("case-1", 2, 'process', 'start')]
harf_docs = [dict(e) for e in harf_taban]
harf_docs[0]["event.action"] = 'CREATE'
eq(eslesenler(veri={"documents":harf_docs}), [], "1. olumlu aşamada action == harf duyarlıdır")
harf_docs = [dict(e) for e in harf_taban]
harf_docs[1]["event.action"] = 'START'
eq(eslesenler(veri={"documents":harf_docs}), [], "2. olumlu aşamada action == harf duyarlıdır")
```

```solution
sequence by host.id
  [file where event.action == "create"] by file.path
  [process where event.action == "start"] by process.executable
```

```hint
sequence by host.id; ilk aşamadan sonra by file.path, ikinciden sonra by process.executable.
```
:::
