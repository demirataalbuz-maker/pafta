---
id: el18
title: Proje · EQL ile Kanıt Dizisi
summary: Başlık, port, dosya yolu, süre, süreç yaşamı ve sıra makinesini bir sorguda birleştir.
---

::: anlat Süreç yaşamıyla sınırlandırılmış ilişki
İlk sorgu izin verilen iki process adından birinin başlamasını, aynı host/entity altında 443 bağlantısının izlemesini ister. Maxspan ilk başlangıçtan ölçülür; process/end bekleyen adayı iptal eder. İkinci start birinciyi değiştirebilir. Sadece port ve adla ilişki kurmak yerine anahtarları ve süreç yaşamını koru.

Sonuç gerçek kullanıcı niyetini, komut başarısını veya ağ içeriğini kanıtlamaz. Raporda sorguyu, mapping'i, time filter'ı, timestamp ve tiebreaker alanlarını birlikte sakla. Bu tezgâhın id listesi, Elasticsearch `_eql/search` yanıtının tüm shard/timeout/partial-result metadata'sını taklit etmez.

```eql
sequence by host.id, process.entity_id with maxspan=2m
  [process where event.action == "start" and process.name in~ ("cmd.exe", "powershell.exe")]
  [network where destination.port == 443]
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
    "process.entity_id": "keyword",
    "process.name": "keyword",
    "destination.port": "long",
    "file.path": "keyword"
  },
  "documents": [
    {
      "id": "s1",
      "@timestamp": "2026-10-21T00:00:00.000Z",
      "event.category": "process",
      "event.sequence": 1,
      "event.action": "start",
      "host.id": "h1",
      "process.entity_id": "e1",
      "process.name": "PowerShell.Exe"
    },
    {
      "id": "n1",
      "@timestamp": "2026-10-21T00:01:00.000Z",
      "event.category": "network",
      "event.sequence": 2,
      "host.id": "h1",
      "process.entity_id": "e1",
      "destination.port": 443
    },
    {
      "id": "w1",
      "@timestamp": "2026-10-21T00:02:00.000Z",
      "event.category": "file",
      "event.sequence": 3,
      "event.action": "write",
      "host.id": "h1",
      "process.entity_id": "e1",
      "file.path": "C:\\Temp\\a.exe"
    },
    {
      "id": "s2",
      "@timestamp": "2026-10-21T00:03:20.000Z",
      "event.category": "process",
      "event.sequence": 4,
      "event.action": "start",
      "host.id": "h2",
      "process.entity_id": "e2",
      "process.name": "cmd.exe"
    },
    {
      "id": "end2",
      "@timestamp": "2026-10-21T00:03:20.001Z",
      "event.category": "process",
      "event.sequence": 5,
      "event.action": "end",
      "host.id": "h2",
      "process.entity_id": "e2"
    },
    {
      "id": "n2",
      "@timestamp": "2026-10-21T00:03:20.002Z",
      "event.category": "network",
      "event.sequence": 6,
      "host.id": "h2",
      "process.entity_id": "e2",
      "destination.port": 443
    },
    {
      "id": "s3",
      "@timestamp": "2026-10-21T00:05:00.000Z",
      "event.category": "process",
      "event.sequence": 7,
      "event.action": "start",
      "host.id": "h3",
      "process.entity_id": "e3",
      "process.name": "cmd.exe"
    },
    {
      "id": "n3",
      "@timestamp": "2026-10-21T00:07:00.001Z",
      "event.category": "network",
      "event.sequence": 8,
      "host.id": "h3",
      "process.entity_id": "e3",
      "destination.port": 443
    },
    {
      "id": "s4",
      "@timestamp": "2026-10-21T00:08:20.000Z",
      "event.category": "process",
      "event.sequence": 9,
      "event.action": "start",
      "host.id": "h4",
      "process.entity_id": "e4",
      "process.name": "cmd.exe"
    },
    {
      "id": "n4",
      "@timestamp": "2026-10-21T00:08:20.001Z",
      "event.category": "network",
      "event.sequence": 10,
      "host.id": "h4",
      "process.entity_id": "e4",
      "destination.port": 444
    },
    {
      "id": "s5a",
      "@timestamp": "2026-10-21T00:10:00.000Z",
      "event.category": "process",
      "event.sequence": 11,
      "event.action": "start",
      "host.id": "h5",
      "process.entity_id": "e5",
      "process.name": "POWERSHELL.EXE"
    },
    {
      "id": "s5b",
      "@timestamp": "2026-10-21T00:10:00.001Z",
      "event.category": "process",
      "event.sequence": 12,
      "event.action": "start",
      "host.id": "h5",
      "process.entity_id": "e5",
      "process.name": "powershell.exe"
    },
    {
      "id": "n5",
      "@timestamp": "2026-10-21T00:10:00.002Z",
      "event.category": "network",
      "event.sequence": 13,
      "host.id": "h5",
      "process.entity_id": "e5",
      "destination.port": 443
    },
    {
      "id": "w5",
      "@timestamp": "2026-10-21T00:10:00.003Z",
      "event.category": "file",
      "event.sequence": 14,
      "event.action": "write",
      "host.id": "h5",
      "process.entity_id": "e5",
      "file.path": "c:\\temp\\b.EXE"
    }
  ],
  "context": {
    "tiebreaker_field": "event.sequence"
  }
}
```
:::

::: anlat Üçüncü aşama toplam süreyi yeniden başlatmaz
İkinci sorgu power*.exe başlangıcı, 443 bağlantısı ve C:\Temp\*.exe dosya yazımını sıraya koyar. `:` ASCII harf duyarsız wildcard karşılaştırmasıdır. Raw EQL metninde Windows backslash'ları literal kalır; yıldız ise joker olmaya devam eder. Dosya yolu keyword'dür, text analyzer veya normalizer kullanılmıyor.

İlk-son üç aşamanın tamamı 2 dakika içinde olmalı; bağlantıdan sonra ayrı iki dakikalık pencere açılmaz. Until her ilerlemede aynı anahtarı iptal edebilir. Farklı dillerden pipe/function/array örneklerini ekleyince sessiz yaklaşık sonuç yerine hata alınır. Kaynaklar: [Elastic EQL sequence](https://www.elastic.co/docs/reference/query-languages/eql/eql-syntax), [EQL search API](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-eql-search).

```eql
sequence by host.id, process.entity_id with maxspan=2m
  [process where event.action == "start" and process.name : "power*.exe"]
  [network where destination.port == 443]
  [file where event.action == "write" and file.path : """C:\Temp\*.exe"""]
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
    "process.entity_id": "keyword",
    "process.name": "keyword",
    "destination.port": "long",
    "file.path": "keyword"
  },
  "documents": [
    {
      "id": "s1",
      "@timestamp": "2026-10-21T00:00:00.000Z",
      "event.category": "process",
      "event.sequence": 1,
      "event.action": "start",
      "host.id": "h1",
      "process.entity_id": "e1",
      "process.name": "PowerShell.Exe"
    },
    {
      "id": "n1",
      "@timestamp": "2026-10-21T00:01:00.000Z",
      "event.category": "network",
      "event.sequence": 2,
      "host.id": "h1",
      "process.entity_id": "e1",
      "destination.port": 443
    },
    {
      "id": "w1",
      "@timestamp": "2026-10-21T00:02:00.000Z",
      "event.category": "file",
      "event.sequence": 3,
      "event.action": "write",
      "host.id": "h1",
      "process.entity_id": "e1",
      "file.path": "C:\\Temp\\a.exe"
    },
    {
      "id": "s2",
      "@timestamp": "2026-10-21T00:03:20.000Z",
      "event.category": "process",
      "event.sequence": 4,
      "event.action": "start",
      "host.id": "h2",
      "process.entity_id": "e2",
      "process.name": "cmd.exe"
    },
    {
      "id": "end2",
      "@timestamp": "2026-10-21T00:03:20.001Z",
      "event.category": "process",
      "event.sequence": 5,
      "event.action": "end",
      "host.id": "h2",
      "process.entity_id": "e2"
    },
    {
      "id": "n2",
      "@timestamp": "2026-10-21T00:03:20.002Z",
      "event.category": "network",
      "event.sequence": 6,
      "host.id": "h2",
      "process.entity_id": "e2",
      "destination.port": 443
    },
    {
      "id": "s3",
      "@timestamp": "2026-10-21T00:05:00.000Z",
      "event.category": "process",
      "event.sequence": 7,
      "event.action": "start",
      "host.id": "h3",
      "process.entity_id": "e3",
      "process.name": "cmd.exe"
    },
    {
      "id": "n3",
      "@timestamp": "2026-10-21T00:07:00.001Z",
      "event.category": "network",
      "event.sequence": 8,
      "host.id": "h3",
      "process.entity_id": "e3",
      "destination.port": 443
    },
    {
      "id": "s4",
      "@timestamp": "2026-10-21T00:08:20.000Z",
      "event.category": "process",
      "event.sequence": 9,
      "event.action": "start",
      "host.id": "h4",
      "process.entity_id": "e4",
      "process.name": "cmd.exe"
    },
    {
      "id": "n4",
      "@timestamp": "2026-10-21T00:08:20.001Z",
      "event.category": "network",
      "event.sequence": 10,
      "host.id": "h4",
      "process.entity_id": "e4",
      "destination.port": 444
    },
    {
      "id": "s5a",
      "@timestamp": "2026-10-21T00:10:00.000Z",
      "event.category": "process",
      "event.sequence": 11,
      "event.action": "start",
      "host.id": "h5",
      "process.entity_id": "e5",
      "process.name": "POWERSHELL.EXE"
    },
    {
      "id": "s5b",
      "@timestamp": "2026-10-21T00:10:00.001Z",
      "event.category": "process",
      "event.sequence": 12,
      "event.action": "start",
      "host.id": "h5",
      "process.entity_id": "e5",
      "process.name": "powershell.exe"
    },
    {
      "id": "n5",
      "@timestamp": "2026-10-21T00:10:00.002Z",
      "event.category": "network",
      "event.sequence": 13,
      "host.id": "h5",
      "process.entity_id": "e5",
      "destination.port": 443
    },
    {
      "id": "w5",
      "@timestamp": "2026-10-21T00:10:00.003Z",
      "event.category": "file",
      "event.sequence": 14,
      "event.action": "write",
      "host.id": "h5",
      "process.entity_id": "e5",
      "file.path": "c:\\temp\\b.EXE"
    }
  ],
  "context": {
    "tiebreaker_field": "event.sequence"
  }
}
```
:::

::: tahmin
Girdideki bütün olaylar ve açık mapping verilmiştir. h2 yaşamı sonlandırılıyor, h3 süreyi aşıyor, h4 yanlış porta gidiyor; h5'te iki başlangıç var. Hangi iki olaylı diziler çıkar? Üçüncü file aşaması bu tahmin sorgusunda yoktur.

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
    "process.name": "keyword",
    "destination.port": "long",
    "file.path": "keyword"
  },
  "documents": [
    {
      "id": "s1",
      "@timestamp": "2026-10-21T00:00:00.000Z",
      "event.category": "process",
      "event.sequence": 1,
      "event.action": "start",
      "host.id": "h1",
      "process.entity_id": "e1",
      "process.name": "PowerShell.Exe"
    },
    {
      "id": "n1",
      "@timestamp": "2026-10-21T00:01:00.000Z",
      "event.category": "network",
      "event.sequence": 2,
      "host.id": "h1",
      "process.entity_id": "e1",
      "destination.port": 443
    },
    {
      "id": "w1",
      "@timestamp": "2026-10-21T00:02:00.000Z",
      "event.category": "file",
      "event.sequence": 3,
      "event.action": "write",
      "host.id": "h1",
      "process.entity_id": "e1",
      "file.path": "C:\\Temp\\a.exe"
    },
    {
      "id": "s2",
      "@timestamp": "2026-10-21T00:03:20.000Z",
      "event.category": "process",
      "event.sequence": 4,
      "event.action": "start",
      "host.id": "h2",
      "process.entity_id": "e2",
      "process.name": "cmd.exe"
    },
    {
      "id": "end2",
      "@timestamp": "2026-10-21T00:03:20.001Z",
      "event.category": "process",
      "event.sequence": 5,
      "event.action": "end",
      "host.id": "h2",
      "process.entity_id": "e2"
    },
    {
      "id": "n2",
      "@timestamp": "2026-10-21T00:03:20.002Z",
      "event.category": "network",
      "event.sequence": 6,
      "host.id": "h2",
      "process.entity_id": "e2",
      "destination.port": 443
    },
    {
      "id": "s3",
      "@timestamp": "2026-10-21T00:05:00.000Z",
      "event.category": "process",
      "event.sequence": 7,
      "event.action": "start",
      "host.id": "h3",
      "process.entity_id": "e3",
      "process.name": "cmd.exe"
    },
    {
      "id": "n3",
      "@timestamp": "2026-10-21T00:07:00.001Z",
      "event.category": "network",
      "event.sequence": 8,
      "host.id": "h3",
      "process.entity_id": "e3",
      "destination.port": 443
    },
    {
      "id": "s4",
      "@timestamp": "2026-10-21T00:08:20.000Z",
      "event.category": "process",
      "event.sequence": 9,
      "event.action": "start",
      "host.id": "h4",
      "process.entity_id": "e4",
      "process.name": "cmd.exe"
    },
    {
      "id": "n4",
      "@timestamp": "2026-10-21T00:08:20.001Z",
      "event.category": "network",
      "event.sequence": 10,
      "host.id": "h4",
      "process.entity_id": "e4",
      "destination.port": 444
    },
    {
      "id": "s5a",
      "@timestamp": "2026-10-21T00:10:00.000Z",
      "event.category": "process",
      "event.sequence": 11,
      "event.action": "start",
      "host.id": "h5",
      "process.entity_id": "e5",
      "process.name": "POWERSHELL.EXE"
    },
    {
      "id": "s5b",
      "@timestamp": "2026-10-21T00:10:00.001Z",
      "event.category": "process",
      "event.sequence": 12,
      "event.action": "start",
      "host.id": "h5",
      "process.entity_id": "e5",
      "process.name": "powershell.exe"
    },
    {
      "id": "n5",
      "@timestamp": "2026-10-21T00:10:00.002Z",
      "event.category": "network",
      "event.sequence": 13,
      "host.id": "h5",
      "process.entity_id": "e5",
      "destination.port": 443
    },
    {
      "id": "w5",
      "@timestamp": "2026-10-21T00:10:00.003Z",
      "event.category": "file",
      "event.sequence": 14,
      "event.action": "write",
      "host.id": "h5",
      "process.entity_id": "e5",
      "file.path": "c:\\temp\\b.EXE"
    }
  ],
  "context": {
    "tiebreaker_field": "event.sequence"
  }
}
```

```eql
sequence by host.id, process.entity_id with maxspan=2m
  [process where event.action == "start" and process.name in~ ("cmd.exe", "powershell.exe")]
  [network where destination.port == 443]
until [process where event.action == "end"]
```

???

s1–n1 doğru anahtar, ad ve portla 60 saniyede tamamlanır. h5'te son bekleyen başlangıç s5b'dir; n5 ile tamamlanır. end2 h2'yi iptal eder, h3 120001 ms sürer, h4 port 444'tür. w1/w5 bu iki aşamalı sorguya dahil değildir.

```text
s1 -> n1
s5b -> n5
```
:::

::: gorev İzinli süreçten 443 bağlantısına
Aynı host.id ve process.entity_id altında process/start adının ASCII harf duyarsız cmd.exe veya powershell.exe olmasını, ardından network destination.port 443 gelmesini iste. En fazla 2 dakika; aynı anahtarlı process/end until ile iptal etsin. Adlar tam listedir; cmd.exe.bak veya power*.exe literal değeri listeye eşit değildir.

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
    "process.name": "keyword",
    "destination.port": "long",
    "file.path": "keyword"
  },
  "documents": [
    {
      "id": "s1",
      "@timestamp": "2026-10-21T00:00:00.000Z",
      "event.category": "process",
      "event.sequence": 1,
      "event.action": "start",
      "host.id": "h1",
      "process.entity_id": "e1",
      "process.name": "PowerShell.Exe"
    },
    {
      "id": "n1",
      "@timestamp": "2026-10-21T00:01:00.000Z",
      "event.category": "network",
      "event.sequence": 2,
      "host.id": "h1",
      "process.entity_id": "e1",
      "destination.port": 443
    },
    {
      "id": "w1",
      "@timestamp": "2026-10-21T00:02:00.000Z",
      "event.category": "file",
      "event.sequence": 3,
      "event.action": "write",
      "host.id": "h1",
      "process.entity_id": "e1",
      "file.path": "C:\\Temp\\a.exe"
    },
    {
      "id": "s2",
      "@timestamp": "2026-10-21T00:03:20.000Z",
      "event.category": "process",
      "event.sequence": 4,
      "event.action": "start",
      "host.id": "h2",
      "process.entity_id": "e2",
      "process.name": "cmd.exe"
    },
    {
      "id": "end2",
      "@timestamp": "2026-10-21T00:03:20.001Z",
      "event.category": "process",
      "event.sequence": 5,
      "event.action": "end",
      "host.id": "h2",
      "process.entity_id": "e2"
    },
    {
      "id": "n2",
      "@timestamp": "2026-10-21T00:03:20.002Z",
      "event.category": "network",
      "event.sequence": 6,
      "host.id": "h2",
      "process.entity_id": "e2",
      "destination.port": 443
    },
    {
      "id": "s3",
      "@timestamp": "2026-10-21T00:05:00.000Z",
      "event.category": "process",
      "event.sequence": 7,
      "event.action": "start",
      "host.id": "h3",
      "process.entity_id": "e3",
      "process.name": "cmd.exe"
    },
    {
      "id": "n3",
      "@timestamp": "2026-10-21T00:07:00.001Z",
      "event.category": "network",
      "event.sequence": 8,
      "host.id": "h3",
      "process.entity_id": "e3",
      "destination.port": 443
    },
    {
      "id": "s4",
      "@timestamp": "2026-10-21T00:08:20.000Z",
      "event.category": "process",
      "event.sequence": 9,
      "event.action": "start",
      "host.id": "h4",
      "process.entity_id": "e4",
      "process.name": "cmd.exe"
    },
    {
      "id": "n4",
      "@timestamp": "2026-10-21T00:08:20.001Z",
      "event.category": "network",
      "event.sequence": 10,
      "host.id": "h4",
      "process.entity_id": "e4",
      "destination.port": 444
    },
    {
      "id": "s5a",
      "@timestamp": "2026-10-21T00:10:00.000Z",
      "event.category": "process",
      "event.sequence": 11,
      "event.action": "start",
      "host.id": "h5",
      "process.entity_id": "e5",
      "process.name": "POWERSHELL.EXE"
    },
    {
      "id": "s5b",
      "@timestamp": "2026-10-21T00:10:00.001Z",
      "event.category": "process",
      "event.sequence": 12,
      "event.action": "start",
      "host.id": "h5",
      "process.entity_id": "e5",
      "process.name": "powershell.exe"
    },
    {
      "id": "n5",
      "@timestamp": "2026-10-21T00:10:00.002Z",
      "event.category": "network",
      "event.sequence": 13,
      "host.id": "h5",
      "process.entity_id": "e5",
      "destination.port": 443
    },
    {
      "id": "w5",
      "@timestamp": "2026-10-21T00:10:00.003Z",
      "event.category": "file",
      "event.sequence": 14,
      "event.action": "write",
      "host.id": "h5",
      "process.entity_id": "e5",
      "file.path": "c:\\temp\\b.EXE"
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
eq(eslesenler(),[["s1","n1"],["s5b","n5"]],"dersteki gerçek sorgu sonucu")
eq(eslesenler(veri={"documents":list(reversed(korpus["documents"]))}),[["s1","n1"],["s5b","n5"]],"girdi sırası değil timestamp+tiebreaker sırası")
from datetime import datetime, timedelta, timezone
def olay(kimlik,t_ms=0,kategori="process",sira=0,**alanlar):
    zaman=datetime(2026,10,21,tzinfo=timezone.utc)+timedelta(milliseconds=t_ms)
    e={"id":kimlik,"@timestamp":zaman.isoformat(timespec="milliseconds").replace("+00:00","Z"),"event.category":kategori,"event.sequence":sira}
    e.update(alanlar)
    return e
def p(k,t,host="h",entity="e",cat="process",action="start",name="cmd.exe",port=None,seq=0):
    alanlar={"host.id":host,"process.entity_id":entity,"event.action":action,"process.name":name}
    if port is not None: alanlar["destination.port"]=port
    return olay(k,t,cat,seq,**alanlar)
for ad,sonuc in (("cmd.exe",[["s","n"]]),("CMD.EXE",[["s","n"]]),("PowerShell.Exe",[["s","n"]]),("cmd.exe.bak",[]),("power*.exe",[])):
    eq(eslesenler(veri={"documents":[p("s",0,name=ad),p("n",1,cat="network",port=443)]}),sonuc,"tam ASCII ad listesi "+ad)
for fark,sonuc in ((119999,[["s","n"]]),(120000,[["s","n"]]),(120001,[])):
    eq(eslesenler(veri={"documents":[p("s",0),p("n",fark,cat="network",port=443)]}),sonuc,"2 dakika eşiği")
for n in (p("n",1,host="other",cat="network",port=443),p("n",1,entity="other",cat="network",port=443),p("n",1,cat="file",port=443),p("n",1,cat="network",port=442),p("n",1,cat="network",port=444)):
    eq(eslesenler(veri={"documents":[p("s",0),n]}),[],"ikinci aşamanın bağımsız alanları")
eq(eslesenler(veri={"documents":[p("s",0),p("end",1,action="end"),p("n",2,cat="network",port=443)]}),[],"until süreç yaşamını bitirir")
eq(eslesenler(veri={"documents":[p("s1",0),p("s2",1),p("n1",2,cat="network",port=443),p("n2",3,cat="network",port=443)]}),[["s2","n1"]],"son pending ve tüketim")
eq(eslesenler(veri={"documents":[p("s",0,cat="file"),p("n",1,cat="network",port=443)]}),[],"başlangıç kategorisi")
eq(eslesenler(veri={"documents":[p("s",0,action="wrong"),p("n",1,cat="network",port=443)]}),[],"başlangıç action")

# == ile : arasındaki farkı aşama başına bağımsız büyük harfle sınarız.
# Korpus sorgu metninden türetilmez; her olay aşağıdaki sabit sentetik veridir.
def harf_olay(k, t, kategori, eylem):
    return olay(k, t, kategori, **{"host.id":"case-host", "process.entity_id":"case-entity", "user.id":"case-user", "event.action":eylem, "process.name":"powershell.exe", "destination.port":443, "file.path":"C:\\Temp\\case.exe", "process.executable":"C:\\Temp\\case.exe"})
harf_taban = [harf_olay("case-0", 0, 'process', 'start'), harf_olay("case-1", 2, 'network', 'connect')]
harf_docs = [dict(e) for e in harf_taban]
harf_docs[0]["event.action"] = 'START'
eq(eslesenler(veri={"documents":harf_docs}), [], "1. olumlu aşamada action == harf duyarlıdır")
harf_docs = [dict(e) for e in harf_taban]
harf_docs.insert(1, harf_olay("case-negative", 1, 'process', 'END'))
eq(eslesenler(veri={"documents":harf_docs}), [['case-0', 'case-1']], "until action == büyük harfli olayı eşleştirmez")
```

```solution
sequence by host.id, process.entity_id with maxspan=2m
  [process where event.action == "start" and process.name in~ ("cmd.exe", "powershell.exe")]
  [network where destination.port == 443]
until [process where event.action == "end"]
```

```hint
sequence by host.id, process.entity_id with maxspan=2m; başlangıçta in~, ağ aşamasında 443, sonda until end.
```
:::

::: gorev Ağ ve dosya aşamasıyla üçlü kanıt
Aynı host.id ve process.entity_id için sırasıyla process/start adı `power*.exe`, network hedef portu 443, file/write yolu raw `C:\Temp\*.exe` kalıbına uysun. İki kalıp da ASCII harf duyarsızdır. İlk-son toplam süre en fazla 2 dakika ve process/end until iptal koşulu olsun. Ara network olayından süreyi yeniden başlatma.

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
    "process.name": "keyword",
    "destination.port": "long",
    "file.path": "keyword"
  },
  "documents": [
    {
      "id": "s1",
      "@timestamp": "2026-10-21T00:00:00.000Z",
      "event.category": "process",
      "event.sequence": 1,
      "event.action": "start",
      "host.id": "h1",
      "process.entity_id": "e1",
      "process.name": "PowerShell.Exe"
    },
    {
      "id": "n1",
      "@timestamp": "2026-10-21T00:01:00.000Z",
      "event.category": "network",
      "event.sequence": 2,
      "host.id": "h1",
      "process.entity_id": "e1",
      "destination.port": 443
    },
    {
      "id": "w1",
      "@timestamp": "2026-10-21T00:02:00.000Z",
      "event.category": "file",
      "event.sequence": 3,
      "event.action": "write",
      "host.id": "h1",
      "process.entity_id": "e1",
      "file.path": "C:\\Temp\\a.exe"
    },
    {
      "id": "s2",
      "@timestamp": "2026-10-21T00:03:20.000Z",
      "event.category": "process",
      "event.sequence": 4,
      "event.action": "start",
      "host.id": "h2",
      "process.entity_id": "e2",
      "process.name": "cmd.exe"
    },
    {
      "id": "end2",
      "@timestamp": "2026-10-21T00:03:20.001Z",
      "event.category": "process",
      "event.sequence": 5,
      "event.action": "end",
      "host.id": "h2",
      "process.entity_id": "e2"
    },
    {
      "id": "n2",
      "@timestamp": "2026-10-21T00:03:20.002Z",
      "event.category": "network",
      "event.sequence": 6,
      "host.id": "h2",
      "process.entity_id": "e2",
      "destination.port": 443
    },
    {
      "id": "s3",
      "@timestamp": "2026-10-21T00:05:00.000Z",
      "event.category": "process",
      "event.sequence": 7,
      "event.action": "start",
      "host.id": "h3",
      "process.entity_id": "e3",
      "process.name": "cmd.exe"
    },
    {
      "id": "n3",
      "@timestamp": "2026-10-21T00:07:00.001Z",
      "event.category": "network",
      "event.sequence": 8,
      "host.id": "h3",
      "process.entity_id": "e3",
      "destination.port": 443
    },
    {
      "id": "s4",
      "@timestamp": "2026-10-21T00:08:20.000Z",
      "event.category": "process",
      "event.sequence": 9,
      "event.action": "start",
      "host.id": "h4",
      "process.entity_id": "e4",
      "process.name": "cmd.exe"
    },
    {
      "id": "n4",
      "@timestamp": "2026-10-21T00:08:20.001Z",
      "event.category": "network",
      "event.sequence": 10,
      "host.id": "h4",
      "process.entity_id": "e4",
      "destination.port": 444
    },
    {
      "id": "s5a",
      "@timestamp": "2026-10-21T00:10:00.000Z",
      "event.category": "process",
      "event.sequence": 11,
      "event.action": "start",
      "host.id": "h5",
      "process.entity_id": "e5",
      "process.name": "POWERSHELL.EXE"
    },
    {
      "id": "s5b",
      "@timestamp": "2026-10-21T00:10:00.001Z",
      "event.category": "process",
      "event.sequence": 12,
      "event.action": "start",
      "host.id": "h5",
      "process.entity_id": "e5",
      "process.name": "powershell.exe"
    },
    {
      "id": "n5",
      "@timestamp": "2026-10-21T00:10:00.002Z",
      "event.category": "network",
      "event.sequence": 13,
      "host.id": "h5",
      "process.entity_id": "e5",
      "destination.port": 443
    },
    {
      "id": "w5",
      "@timestamp": "2026-10-21T00:10:00.003Z",
      "event.category": "file",
      "event.sequence": 14,
      "event.action": "write",
      "host.id": "h5",
      "process.entity_id": "e5",
      "file.path": "c:\\temp\\b.EXE"
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
eq(eslesenler(),[["s1","n1","w1"],["s5b","n5","w5"]],"dersteki gerçek sorgu sonucu")
eq(eslesenler(veri={"documents":list(reversed(korpus["documents"]))}),[["s1","n1","w1"],["s5b","n5","w5"]],"girdi sırası değil timestamp+tiebreaker sırası")
from datetime import datetime, timedelta, timezone
def olay(kimlik,t_ms=0,kategori="process",sira=0,**alanlar):
    zaman=datetime(2026,10,21,tzinfo=timezone.utc)+timedelta(milliseconds=t_ms)
    e={"id":kimlik,"@timestamp":zaman.isoformat(timespec="milliseconds").replace("+00:00","Z"),"event.category":kategori,"event.sequence":sira}
    e.update(alanlar)
    return e
def p(k,t,cat="process",host="h",entity="e",action="start",name="PowerShell.Exe",port=443,path="C:\\Temp\\a.exe",seq=0):
    return olay(k,t,cat,seq,**{"host.id":host,"process.entity_id":entity,"event.action":action,"process.name":name,"destination.port":port,"file.path":path})
def zincir(son=120000):
    return [p("s",0),p("n",60000,"network"),p("w",son,"file",action="write")]
for son,sonuc in ((119999,[["s","n","w"]]),(120000,[["s","n","w"]]),(120001,[])):
    eq(eslesenler(veri={"documents":zincir(son)}),sonuc,"toplam süre ilk olaydan "+str(son))
for ad,sonuc in (("POWER.EXE",[["s","n","w"]]),("powershell.exe",[["s","n","w"]]),("cmd.exe",[]),("powershell.exe.bak",[])):
    docs=zincir(); docs[0]["process.name"]=ad
    eq(eslesenler(veri={"documents":docs}),sonuc,"başlangıç wildcard sıfır/çok karakter ve tam kapsam")
for yol,sonuc in (("c:\\temp\\A.EXE",[["s","n","w"]]),("C:\\Temp\\.exe",[["s","n","w"]]),("C:\\Other\\a.exe",[]),("C:\\Temp\\a.exe.bak",[])):
    docs=zincir(); docs[-1]["file.path"]=yol
    eq(eslesenler(veri={"documents":docs}),sonuc,"dosya kalıbı ve harf")
for index,alan,deger in ((0,"event.category","file"),(0,"event.action","wrong"),(1,"event.category","file"),(1,"destination.port",442),(1,"destination.port",444),(1,"host.id","other"),(1,"process.entity_id","other"),(2,"event.category","network"),(2,"event.action","wrong"),(2,"host.id","other"),(2,"process.entity_id","other")):
    docs=zincir(); docs[index][alan]=deger
    eq(eslesenler(veri={"documents":docs}),[],"üç aşamanın bağımsız koşulları")
docs=zincir(); docs.insert(2,p("end",90000,action="end"))
eq(eslesenler(veri={"documents":docs}),[],"son aşamadan önce until")
docs=zincir(); docs[-1]["@timestamp"]=docs[1]["@timestamp"]; docs[-1]["event.sequence"]=1; docs[1]["event.sequence"]=2
eq(eslesenler(veri={"documents":docs}),[],"son iki aşamanın ters ordinali")

# == ile : arasındaki farkı aşama başına bağımsız büyük harfle sınarız.
# Korpus sorgu metninden türetilmez; her olay aşağıdaki sabit sentetik veridir.
def harf_olay(k, t, kategori, eylem):
    return olay(k, t, kategori, **{"host.id":"case-host", "process.entity_id":"case-entity", "user.id":"case-user", "event.action":eylem, "process.name":"powershell.exe", "destination.port":443, "file.path":"C:\\Temp\\case.exe", "process.executable":"C:\\Temp\\case.exe"})
harf_taban = [harf_olay("case-0", 0, 'process', 'start'), harf_olay("case-1", 2, 'network', 'connect'), harf_olay("case-2", 4, 'file', 'write')]
harf_docs = [dict(e) for e in harf_taban]
harf_docs[0]["event.action"] = 'START'
eq(eslesenler(veri={"documents":harf_docs}), [], "1. olumlu aşamada action == harf duyarlıdır")
harf_docs = [dict(e) for e in harf_taban]
harf_docs[2]["event.action"] = 'WRITE'
eq(eslesenler(veri={"documents":harf_docs}), [], "3. olumlu aşamada action == harf duyarlıdır")
harf_docs = [dict(e) for e in harf_taban]
harf_docs.insert(1, harf_olay("case-negative", 1, 'process', 'END'))
eq(eslesenler(veri={"documents":harf_docs}), [['case-0', 'case-1', 'case-2']], "until action == büyük harfli olayı eşleştirmez")
```

```solution
sequence by host.id, process.entity_id with maxspan=2m
  [process where event.action == "start" and process.name : "power*.exe"]
  [network where destination.port == 443]
  [file where event.action == "write" and file.path : """C:\Temp\*.exe"""]
until [process where event.action == "end"]
```

```hint
Üç köşeli olumlu aşama; ilk-son için tek maxspan. Raw triple quote Windows yolu string kaçışını sadeleştirir, yıldız yine joker.
```
:::
