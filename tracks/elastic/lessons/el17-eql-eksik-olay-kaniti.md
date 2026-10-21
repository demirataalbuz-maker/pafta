---
id: el17
title: EQL · Ortadaki Eksik Olay
summary: Maxspan içinde olumlu diziyi kur; ortadaki ![] koşulunu açık timestamp aralığında değerlendir.
---

::: anlat Yokluğu sınırlı bir zaman aralığında sor
`![ ... ]` bir eksik olay koşuludur; EQL'de maxspan zorunludur. Buradaki desteklenen biçim en az iki olumlu aşama arasındaki eksik aşamadır. Önce olumlu sequence makinesi adayını tamamlar; ardından aynı anahtarlı olumsuz olayın iki komşu olumlu timestamp'in **kesin arasında** bulunup bulunmadığı sınanır.

Ortadaki eksik olay, `until` ile aynı ordinal aralığı değildir. Uç timestamp'ine eşit logout, tiebreaker ile uçların arasında dursa bile bu açık timestamp aralığına girmez. Maxspan'ın ilk-son tam eşik kabulü yine geçerlidir. Kaynak: [Elastic eksik olay](https://www.elastic.co/docs/reference/query-languages/eql/eql-syntax), [native aralık hazırlama](https://github.com/elastic/elasticsearch/blob/v9.2.0/x-pack/plugin/eql/src/main/java/org/elasticsearch/xpack/eql/execution/sequence/TumblingWindow.java).

```eql
sequence by host.id, user.id with maxspan=5m
  [authentication where event.action == "login"]
  ![authentication where event.action == "logout"]
  [file where event.action == "read"]
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
    "user.id": "keyword",
    "process.entity_id": "keyword",
    "destination.port": "long"
  },
  "documents": [
    {
      "id": "l1",
      "@timestamp": "2026-10-21T00:00:00.000Z",
      "event.category": "authentication",
      "event.sequence": 1,
      "event.action": "login",
      "host.id": "h1",
      "user.id": "u"
    },
    {
      "id": "l2",
      "@timestamp": "2026-10-21T00:00:00.000Z",
      "event.category": "authentication",
      "event.sequence": 2,
      "event.action": "login",
      "host.id": "h2",
      "user.id": "u"
    },
    {
      "id": "l3",
      "@timestamp": "2026-10-21T00:00:00.000Z",
      "event.category": "authentication",
      "event.sequence": 3,
      "event.action": "login",
      "host.id": "h3",
      "user.id": "u"
    },
    {
      "id": "o3",
      "@timestamp": "2026-10-21T00:00:00.000Z",
      "event.category": "authentication",
      "event.sequence": 4,
      "event.action": "logout",
      "host.id": "h3",
      "user.id": "u"
    },
    {
      "id": "o2",
      "@timestamp": "2026-10-21T00:00:01.000Z",
      "event.category": "authentication",
      "event.sequence": 5,
      "event.action": "logout",
      "host.id": "h2",
      "user.id": "u"
    },
    {
      "id": "r2",
      "@timestamp": "2026-10-21T00:00:02.000Z",
      "event.category": "file",
      "event.sequence": 6,
      "event.action": "read",
      "host.id": "h2",
      "user.id": "u"
    },
    {
      "id": "r3",
      "@timestamp": "2026-10-21T00:00:03.000Z",
      "event.category": "file",
      "event.sequence": 7,
      "event.action": "read",
      "host.id": "h3",
      "user.id": "u"
    },
    {
      "id": "r1",
      "@timestamp": "2026-10-21T00:05:00.000Z",
      "event.category": "file",
      "event.sequence": 8,
      "event.action": "read",
      "host.id": "h1",
      "user.id": "u"
    },
    {
      "id": "s1",
      "@timestamp": "2026-10-21T00:06:40.000Z",
      "event.category": "process",
      "event.sequence": 9,
      "event.action": "start",
      "host.id": "h1",
      "process.entity_id": "e1"
    },
    {
      "id": "w1",
      "@timestamp": "2026-10-21T00:06:50.000Z",
      "event.category": "file",
      "event.sequence": 10,
      "event.action": "write",
      "host.id": "h1",
      "process.entity_id": "e1"
    },
    {
      "id": "s2",
      "@timestamp": "2026-10-21T00:07:00.000Z",
      "event.category": "process",
      "event.sequence": 11,
      "event.action": "start",
      "host.id": "h1",
      "process.entity_id": "e2"
    },
    {
      "id": "tls",
      "@timestamp": "2026-10-21T00:07:05.000Z",
      "event.category": "network",
      "event.sequence": 12,
      "destination.port": 443,
      "host.id": "h1",
      "process.entity_id": "e2"
    },
    {
      "id": "w2",
      "@timestamp": "2026-10-21T00:07:10.000Z",
      "event.category": "file",
      "event.sequence": 13,
      "event.action": "write",
      "host.id": "h1",
      "process.entity_id": "e2"
    }
  ],
  "context": {
    "tiebreaker_field": "event.sequence"
  }
}
```
:::

::: anlat Destek kapsamı ile kanıtın sınırını ayır
Yerel motor orta `![]` koşulunu çalıştırır; başta/sonda eksik aşama, runs, sample, join, pipe, fonksiyon ve regex'i açıkça reddeder. Gerçek Elasticsearch'ün bunların bazılarını desteklemesi, bu tezgâhın hepsini uyguladığı anlamına gelmez. Bu derste onları çalışıyormuş gibi yaklaşık hesaplamıyoruz.

Bir kayıtta logout veya TLS bağlantısı bulunmaması, gerçek dünyada hiç olmadığına tek başına kanıt değildir. Sensör kapsamı, kayıp olay, arama penceresi ve gecikme ayrıca raporlanmalıdır. Tezgâh sentetik corpus'u eksiksiz kabul eder; motor analistin 'telemetri belirsiz' kararını kendi başına üretmez. Aşağıdaki ikinci sorgu sadece bu corpus içinde iki olumlu olay arasında 443 bağlantısı yokluğunu sorar.

```eql
sequence by host.id, process.entity_id with maxspan=10s
  [process where event.action == "start"]
  ![network where destination.port == 443]
  [file where event.action == "write"]
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
    "user.id": "keyword",
    "process.entity_id": "keyword",
    "destination.port": "long"
  },
  "documents": [
    {
      "id": "l1",
      "@timestamp": "2026-10-21T00:00:00.000Z",
      "event.category": "authentication",
      "event.sequence": 1,
      "event.action": "login",
      "host.id": "h1",
      "user.id": "u"
    },
    {
      "id": "l2",
      "@timestamp": "2026-10-21T00:00:00.000Z",
      "event.category": "authentication",
      "event.sequence": 2,
      "event.action": "login",
      "host.id": "h2",
      "user.id": "u"
    },
    {
      "id": "l3",
      "@timestamp": "2026-10-21T00:00:00.000Z",
      "event.category": "authentication",
      "event.sequence": 3,
      "event.action": "login",
      "host.id": "h3",
      "user.id": "u"
    },
    {
      "id": "o3",
      "@timestamp": "2026-10-21T00:00:00.000Z",
      "event.category": "authentication",
      "event.sequence": 4,
      "event.action": "logout",
      "host.id": "h3",
      "user.id": "u"
    },
    {
      "id": "o2",
      "@timestamp": "2026-10-21T00:00:01.000Z",
      "event.category": "authentication",
      "event.sequence": 5,
      "event.action": "logout",
      "host.id": "h2",
      "user.id": "u"
    },
    {
      "id": "r2",
      "@timestamp": "2026-10-21T00:00:02.000Z",
      "event.category": "file",
      "event.sequence": 6,
      "event.action": "read",
      "host.id": "h2",
      "user.id": "u"
    },
    {
      "id": "r3",
      "@timestamp": "2026-10-21T00:00:03.000Z",
      "event.category": "file",
      "event.sequence": 7,
      "event.action": "read",
      "host.id": "h3",
      "user.id": "u"
    },
    {
      "id": "r1",
      "@timestamp": "2026-10-21T00:05:00.000Z",
      "event.category": "file",
      "event.sequence": 8,
      "event.action": "read",
      "host.id": "h1",
      "user.id": "u"
    },
    {
      "id": "s1",
      "@timestamp": "2026-10-21T00:06:40.000Z",
      "event.category": "process",
      "event.sequence": 9,
      "event.action": "start",
      "host.id": "h1",
      "process.entity_id": "e1"
    },
    {
      "id": "w1",
      "@timestamp": "2026-10-21T00:06:50.000Z",
      "event.category": "file",
      "event.sequence": 10,
      "event.action": "write",
      "host.id": "h1",
      "process.entity_id": "e1"
    },
    {
      "id": "s2",
      "@timestamp": "2026-10-21T00:07:00.000Z",
      "event.category": "process",
      "event.sequence": 11,
      "event.action": "start",
      "host.id": "h1",
      "process.entity_id": "e2"
    },
    {
      "id": "tls",
      "@timestamp": "2026-10-21T00:07:05.000Z",
      "event.category": "network",
      "event.sequence": 12,
      "destination.port": 443,
      "host.id": "h1",
      "process.entity_id": "e2"
    },
    {
      "id": "w2",
      "@timestamp": "2026-10-21T00:07:10.000Z",
      "event.category": "file",
      "event.sequence": 13,
      "event.action": "write",
      "host.id": "h1",
      "process.entity_id": "e2"
    }
  ],
  "context": {
    "tiebreaker_field": "event.sequence"
  }
}
```
:::

::: tahmin
Girdide h1/h2/h3 için aynı kullanıcı kimliği var. h1'in süresi tam 5 dakika; h2'nin logout'u kesin arada; h3 logout'u login ile aynı timestamp'te, farklı sıra numarasında. Ortadaki eksik aşama için timestamp ile ordinal ayrımını kullan.

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
    "user.id": "keyword",
    "process.entity_id": "keyword",
    "destination.port": "long"
  },
  "documents": [
    {
      "id": "l1",
      "@timestamp": "2026-10-21T00:00:00.000Z",
      "event.category": "authentication",
      "event.sequence": 1,
      "event.action": "login",
      "host.id": "h1",
      "user.id": "u"
    },
    {
      "id": "l2",
      "@timestamp": "2026-10-21T00:00:00.000Z",
      "event.category": "authentication",
      "event.sequence": 2,
      "event.action": "login",
      "host.id": "h2",
      "user.id": "u"
    },
    {
      "id": "l3",
      "@timestamp": "2026-10-21T00:00:00.000Z",
      "event.category": "authentication",
      "event.sequence": 3,
      "event.action": "login",
      "host.id": "h3",
      "user.id": "u"
    },
    {
      "id": "o3",
      "@timestamp": "2026-10-21T00:00:00.000Z",
      "event.category": "authentication",
      "event.sequence": 4,
      "event.action": "logout",
      "host.id": "h3",
      "user.id": "u"
    },
    {
      "id": "o2",
      "@timestamp": "2026-10-21T00:00:01.000Z",
      "event.category": "authentication",
      "event.sequence": 5,
      "event.action": "logout",
      "host.id": "h2",
      "user.id": "u"
    },
    {
      "id": "r2",
      "@timestamp": "2026-10-21T00:00:02.000Z",
      "event.category": "file",
      "event.sequence": 6,
      "event.action": "read",
      "host.id": "h2",
      "user.id": "u"
    },
    {
      "id": "r3",
      "@timestamp": "2026-10-21T00:00:03.000Z",
      "event.category": "file",
      "event.sequence": 7,
      "event.action": "read",
      "host.id": "h3",
      "user.id": "u"
    },
    {
      "id": "r1",
      "@timestamp": "2026-10-21T00:05:00.000Z",
      "event.category": "file",
      "event.sequence": 8,
      "event.action": "read",
      "host.id": "h1",
      "user.id": "u"
    },
    {
      "id": "s1",
      "@timestamp": "2026-10-21T00:06:40.000Z",
      "event.category": "process",
      "event.sequence": 9,
      "event.action": "start",
      "host.id": "h1",
      "process.entity_id": "e1"
    },
    {
      "id": "w1",
      "@timestamp": "2026-10-21T00:06:50.000Z",
      "event.category": "file",
      "event.sequence": 10,
      "event.action": "write",
      "host.id": "h1",
      "process.entity_id": "e1"
    },
    {
      "id": "s2",
      "@timestamp": "2026-10-21T00:07:00.000Z",
      "event.category": "process",
      "event.sequence": 11,
      "event.action": "start",
      "host.id": "h1",
      "process.entity_id": "e2"
    },
    {
      "id": "tls",
      "@timestamp": "2026-10-21T00:07:05.000Z",
      "event.category": "network",
      "event.sequence": 12,
      "destination.port": 443,
      "host.id": "h1",
      "process.entity_id": "e2"
    },
    {
      "id": "w2",
      "@timestamp": "2026-10-21T00:07:10.000Z",
      "event.category": "file",
      "event.sequence": 13,
      "event.action": "write",
      "host.id": "h1",
      "process.entity_id": "e2"
    }
  ],
  "context": {
    "tiebreaker_field": "event.sequence"
  }
}
```

```eql
sequence by host.id, user.id with maxspan=5m
  [authentication where event.action == "login"]
  ![authentication where event.action == "logout"]
  [file where event.action == "read"]
```

???

h3 l3–r3 tamamlanır: o3 login'in timestamp'ine eşit olduğu için açık aralığa girmez. h1 l1–r1 tam maxspan eşiğinde tamamlanır. h2 o2 ile elenir. Sonuç son olumlu olayın sırasına göre r3, sonra r1 şeklindedir; eksik aşamaya sahte id yazılmaz.

```text
l3 -> r3
l1 -> r1
```
:::

::: gorev Login ile read arasında logout yok
Aynı host.id ve user.id için authentication/login ardından file/read dizisi yaz; ilk-son süre en fazla 5 dakika, arada aynı anahtarlı authentication/logout bulunmasın. Ortadaki `![]` kullan; uç timestamp'ine eşit logout engellemesin. Eksik aşamayı sonuç kimliği olarak uydurma.

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
    "user.id": "keyword",
    "process.entity_id": "keyword",
    "destination.port": "long"
  },
  "documents": [
    {
      "id": "l1",
      "@timestamp": "2026-10-21T00:00:00.000Z",
      "event.category": "authentication",
      "event.sequence": 1,
      "event.action": "login",
      "host.id": "h1",
      "user.id": "u"
    },
    {
      "id": "l2",
      "@timestamp": "2026-10-21T00:00:00.000Z",
      "event.category": "authentication",
      "event.sequence": 2,
      "event.action": "login",
      "host.id": "h2",
      "user.id": "u"
    },
    {
      "id": "l3",
      "@timestamp": "2026-10-21T00:00:00.000Z",
      "event.category": "authentication",
      "event.sequence": 3,
      "event.action": "login",
      "host.id": "h3",
      "user.id": "u"
    },
    {
      "id": "o3",
      "@timestamp": "2026-10-21T00:00:00.000Z",
      "event.category": "authentication",
      "event.sequence": 4,
      "event.action": "logout",
      "host.id": "h3",
      "user.id": "u"
    },
    {
      "id": "o2",
      "@timestamp": "2026-10-21T00:00:01.000Z",
      "event.category": "authentication",
      "event.sequence": 5,
      "event.action": "logout",
      "host.id": "h2",
      "user.id": "u"
    },
    {
      "id": "r2",
      "@timestamp": "2026-10-21T00:00:02.000Z",
      "event.category": "file",
      "event.sequence": 6,
      "event.action": "read",
      "host.id": "h2",
      "user.id": "u"
    },
    {
      "id": "r3",
      "@timestamp": "2026-10-21T00:00:03.000Z",
      "event.category": "file",
      "event.sequence": 7,
      "event.action": "read",
      "host.id": "h3",
      "user.id": "u"
    },
    {
      "id": "r1",
      "@timestamp": "2026-10-21T00:05:00.000Z",
      "event.category": "file",
      "event.sequence": 8,
      "event.action": "read",
      "host.id": "h1",
      "user.id": "u"
    },
    {
      "id": "s1",
      "@timestamp": "2026-10-21T00:06:40.000Z",
      "event.category": "process",
      "event.sequence": 9,
      "event.action": "start",
      "host.id": "h1",
      "process.entity_id": "e1"
    },
    {
      "id": "w1",
      "@timestamp": "2026-10-21T00:06:50.000Z",
      "event.category": "file",
      "event.sequence": 10,
      "event.action": "write",
      "host.id": "h1",
      "process.entity_id": "e1"
    },
    {
      "id": "s2",
      "@timestamp": "2026-10-21T00:07:00.000Z",
      "event.category": "process",
      "event.sequence": 11,
      "event.action": "start",
      "host.id": "h1",
      "process.entity_id": "e2"
    },
    {
      "id": "tls",
      "@timestamp": "2026-10-21T00:07:05.000Z",
      "event.category": "network",
      "event.sequence": 12,
      "destination.port": 443,
      "host.id": "h1",
      "process.entity_id": "e2"
    },
    {
      "id": "w2",
      "@timestamp": "2026-10-21T00:07:10.000Z",
      "event.category": "file",
      "event.sequence": 13,
      "event.action": "write",
      "host.id": "h1",
      "process.entity_id": "e2"
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
eq(eslesenler(),[["l3","r3"],["l1","r1"]],"dersteki gerçek sorgu sonucu")
eq(eslesenler(veri={"documents":list(reversed(korpus["documents"]))}),[["l3","r3"],["l1","r1"]],"girdi sırası değil timestamp+tiebreaker sırası")
from datetime import datetime, timedelta, timezone
def olay(kimlik,t_ms=0,kategori="process",sira=0,**alanlar):
    zaman=datetime(2026,10,21,tzinfo=timezone.utc)+timedelta(milliseconds=t_ms)
    e={"id":kimlik,"@timestamp":zaman.isoformat(timespec="milliseconds").replace("+00:00","Z"),"event.category":kategori,"event.sequence":sira}
    e.update(alanlar)
    return e
def a(k,t,host="h",user="u",cat="authentication",action="login",seq=0):
    return olay(k,t,cat,seq,**{"host.id":host,"user.id":user,"event.action":action})
for zaman,sonuc in ((0,[["l","r"]]),(1,[]),(299999,[]),(300000,[["l","r"]])):
    docs=[a("l",0,seq=1),a("o",zaman,action="logout",seq=2),a("r",300000,cat="file",action="read",seq=3)]
    eq(eslesenler(veri={"documents":docs}),sonuc,"açık timestamp aralığının iki ucu ve iç komşuları "+str(zaman))
for fark,sonuc in ((299999,[["l","r"]]),(300000,[["l","r"]]),(300001,[])):
    eq(eslesenler(veri={"documents":[a("l",0),a("r",fark,cat="file",action="read")]}),sonuc,"maxspan iki komşusu")
for o in (a("o",1,host="other",action="logout"),a("o",1,user="other",action="logout"),a("o",1,cat="process",action="logout"),a("o",1,action="wrong")):
    eq(eslesenler(veri={"documents":[a("l",0),o,a("r",2,cat="file",action="read")]}),[["l","r"]],"olumsuz aşamanın anahtar/category/action koşulları ayrı")
eq(eslesenler(veri={"documents":[a("l1",0),a("l2",1),a("r",2,cat="file",action="read"),a("r2",3,cat="file",action="read")]}),[["l2","r"]],"eksik aşama pozitif pending/tüketim semantiğini değiştirmez")

# == ile : arasındaki farkı aşama başına bağımsız büyük harfle sınarız.
# Korpus sorgu metninden türetilmez; her olay aşağıdaki sabit sentetik veridir.
def harf_olay(k, t, kategori, eylem):
    return olay(k, t, kategori, **{"host.id":"case-host", "process.entity_id":"case-entity", "user.id":"case-user", "event.action":eylem, "process.name":"powershell.exe", "destination.port":443, "file.path":"C:\\Temp\\case.exe", "process.executable":"C:\\Temp\\case.exe"})
harf_taban = [harf_olay("case-0", 0, 'authentication', 'login'), harf_olay("case-1", 2, 'file', 'read')]
harf_docs = [dict(e) for e in harf_taban]
harf_docs[0]["event.action"] = 'LOGIN'
eq(eslesenler(veri={"documents":harf_docs}), [], "1. olumlu aşamada action == harf duyarlıdır")
harf_docs = [dict(e) for e in harf_taban]
harf_docs[1]["event.action"] = 'READ'
eq(eslesenler(veri={"documents":harf_docs}), [], "2. olumlu aşamada action == harf duyarlıdır")
harf_docs = [dict(e) for e in harf_taban]
harf_docs.insert(1, harf_olay("case-negative", 1, 'authentication', 'LOGOUT'))
eq(eslesenler(veri={"documents":harf_docs}), [['case-0', 'case-1']], "missing action == büyük harfli olayı eşleştirmez")
```

```solution
sequence by host.id, user.id with maxspan=5m
  [authentication where event.action == "login"]
  ![authentication where event.action == "logout"]
  [file where event.action == "read"]
```

```hint
İki olumlu aşamanın arasına ![authentication where event.action == "logout"] koy; by ve maxspan'ı koru.
```
:::

::: gorev Süreçten dosyaya, arada 443 yok
Aynı host.id ve process.entity_id için process/start ardından file/write dizisi yaz. En fazla 10 saniye içinde tamamlanmalı; kesin aradaki aynı anahtarlı network olayının destination.port'u 443 ise aday elensin. Port 442/444, yanlış kategori veya yanlış anahtar engellemesin. Uç timestamp'ine eşit network olayı arada sayılmaz.

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
    "user.id": "keyword",
    "process.entity_id": "keyword",
    "destination.port": "long"
  },
  "documents": [
    {
      "id": "l1",
      "@timestamp": "2026-10-21T00:00:00.000Z",
      "event.category": "authentication",
      "event.sequence": 1,
      "event.action": "login",
      "host.id": "h1",
      "user.id": "u"
    },
    {
      "id": "l2",
      "@timestamp": "2026-10-21T00:00:00.000Z",
      "event.category": "authentication",
      "event.sequence": 2,
      "event.action": "login",
      "host.id": "h2",
      "user.id": "u"
    },
    {
      "id": "l3",
      "@timestamp": "2026-10-21T00:00:00.000Z",
      "event.category": "authentication",
      "event.sequence": 3,
      "event.action": "login",
      "host.id": "h3",
      "user.id": "u"
    },
    {
      "id": "o3",
      "@timestamp": "2026-10-21T00:00:00.000Z",
      "event.category": "authentication",
      "event.sequence": 4,
      "event.action": "logout",
      "host.id": "h3",
      "user.id": "u"
    },
    {
      "id": "o2",
      "@timestamp": "2026-10-21T00:00:01.000Z",
      "event.category": "authentication",
      "event.sequence": 5,
      "event.action": "logout",
      "host.id": "h2",
      "user.id": "u"
    },
    {
      "id": "r2",
      "@timestamp": "2026-10-21T00:00:02.000Z",
      "event.category": "file",
      "event.sequence": 6,
      "event.action": "read",
      "host.id": "h2",
      "user.id": "u"
    },
    {
      "id": "r3",
      "@timestamp": "2026-10-21T00:00:03.000Z",
      "event.category": "file",
      "event.sequence": 7,
      "event.action": "read",
      "host.id": "h3",
      "user.id": "u"
    },
    {
      "id": "r1",
      "@timestamp": "2026-10-21T00:05:00.000Z",
      "event.category": "file",
      "event.sequence": 8,
      "event.action": "read",
      "host.id": "h1",
      "user.id": "u"
    },
    {
      "id": "s1",
      "@timestamp": "2026-10-21T00:06:40.000Z",
      "event.category": "process",
      "event.sequence": 9,
      "event.action": "start",
      "host.id": "h1",
      "process.entity_id": "e1"
    },
    {
      "id": "w1",
      "@timestamp": "2026-10-21T00:06:50.000Z",
      "event.category": "file",
      "event.sequence": 10,
      "event.action": "write",
      "host.id": "h1",
      "process.entity_id": "e1"
    },
    {
      "id": "s2",
      "@timestamp": "2026-10-21T00:07:00.000Z",
      "event.category": "process",
      "event.sequence": 11,
      "event.action": "start",
      "host.id": "h1",
      "process.entity_id": "e2"
    },
    {
      "id": "tls",
      "@timestamp": "2026-10-21T00:07:05.000Z",
      "event.category": "network",
      "event.sequence": 12,
      "destination.port": 443,
      "host.id": "h1",
      "process.entity_id": "e2"
    },
    {
      "id": "w2",
      "@timestamp": "2026-10-21T00:07:10.000Z",
      "event.category": "file",
      "event.sequence": 13,
      "event.action": "write",
      "host.id": "h1",
      "process.entity_id": "e2"
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
eq(eslesenler(),[["s1","w1"]],"dersteki gerçek sorgu sonucu")
eq(eslesenler(veri={"documents":list(reversed(korpus["documents"]))}),[["s1","w1"]],"girdi sırası değil timestamp+tiebreaker sırası")
from datetime import datetime, timedelta, timezone
def olay(kimlik,t_ms=0,kategori="process",sira=0,**alanlar):
    zaman=datetime(2026,10,21,tzinfo=timezone.utc)+timedelta(milliseconds=t_ms)
    e={"id":kimlik,"@timestamp":zaman.isoformat(timespec="milliseconds").replace("+00:00","Z"),"event.category":kategori,"event.sequence":sira}
    e.update(alanlar)
    return e
def p(k,t,host="h",entity="e",cat="process",action="start",port=None,seq=0):
    alanlar={"host.id":host,"process.entity_id":entity,"event.action":action}
    if port is not None: alanlar["destination.port"]=port
    return olay(k,t,cat,seq,**alanlar)
for port,sonuc in ((442,[["s","w"]]),(443,[]),(444,[["s","w"]])):
    eq(eslesenler(veri={"documents":[p("s",0),p("n",5000,cat="network",port=port),p("w",10000,cat="file",action="write")]}),sonuc,"olumsuz port eşiği "+str(port))
for t,sonuc in ((0,[["s","w"]]),(1,[]),(9999,[]),(10000,[["s","w"]])):
    eq(eslesenler(veri={"documents":[p("s",0,seq=1),p("n",t,cat="network",port=443,seq=2),p("w",10000,cat="file",action="write",seq=3)]}),sonuc,"orta eksik olay açık zaman aralığı")
for n in (p("n",1,host="other",cat="network",port=443),p("n",1,entity="other",cat="network",port=443),p("n",1,cat="file",port=443)):
    eq(eslesenler(veri={"documents":[p("s",0),n,p("w",2,cat="file",action="write")]}),[["s","w"]],"olumsuz kategori ve iki anahtar")
for fark,sonuc in ((9999,[["s","w"]]),(10000,[["s","w"]]),(10001,[])):
    eq(eslesenler(veri={"documents":[p("s",0),p("w",fark,cat="file",action="write")]}),sonuc,"10 saniye iki komşusu")

# == ile : arasındaki farkı aşama başına bağımsız büyük harfle sınarız.
# Korpus sorgu metninden türetilmez; her olay aşağıdaki sabit sentetik veridir.
def harf_olay(k, t, kategori, eylem):
    return olay(k, t, kategori, **{"host.id":"case-host", "process.entity_id":"case-entity", "user.id":"case-user", "event.action":eylem, "process.name":"powershell.exe", "destination.port":443, "file.path":"C:\\Temp\\case.exe", "process.executable":"C:\\Temp\\case.exe"})
harf_taban = [harf_olay("case-0", 0, 'process', 'start'), harf_olay("case-1", 2, 'file', 'write')]
harf_docs = [dict(e) for e in harf_taban]
harf_docs[0]["event.action"] = 'START'
eq(eslesenler(veri={"documents":harf_docs}), [], "1. olumlu aşamada action == harf duyarlıdır")
harf_docs = [dict(e) for e in harf_taban]
harf_docs[1]["event.action"] = 'WRITE'
eq(eslesenler(veri={"documents":harf_docs}), [], "2. olumlu aşamada action == harf duyarlıdır")
```

```solution
sequence by host.id, process.entity_id with maxspan=10s
  [process where event.action == "start"]
  ![network where destination.port == 443]
  [file where event.action == "write"]
```

```hint
sequence ... maxspan=10s; ortada ![network where destination.port == 443].
```
:::
