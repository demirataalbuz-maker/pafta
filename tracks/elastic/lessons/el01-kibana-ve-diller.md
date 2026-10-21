---
id: el01
title: Kibana KQL · İlk Belge Filtren
summary: Kusto ile Kibana KQL farkı; gerçek Lucene alan sorguları, mapping ve dış zaman kapsamıyla iki alan koşulu yaz.
---

::: anlat Aynı kısaltma, ayrı sözdizimleri
Microsoft Kusto'daki `tablo | where ...` ile Kibana Query Language aynı dil değildir. Kibana KQL, `alan: değer` koşullarıyla belge seçer. Lucene query-string ayrı bir arama dilidir; EQL olay dizilerini, ES|QL ise borularla veri işlemeyi ele alır. Bu yolda ilk altı pafta KQL yazdırır; dil seçimini değiştirmek sorgu metnini otomatik çevirmez.

Tezgâha bir **KQL sorgusu** yaz. Pafta'nın sınırlı KQL ayrıştırıcısı alan koşullarını gerçek Apache Lucene sorgularına dönüştürür; metin çözümleme ve eşleşme native Lucene'de çalışır. Bu tezgâh yerel bir Elasticsearch sunucusu değildir. Desteklenmeyen özellik açık hata verir. Görevlerde Python fonksiyonu yazılmaz.

`event.dataset: auth` keyword alanda tam değeri arar. KQL filtreler; toplama, dönüştürme veya sıralama komutunu sorguya eklemezsin. Kaynak: [KQL söz dizimi](https://www.elastic.co/docs/reference/query-languages/kql).

```meta
dil: kibana
```

```stdin
{
  "dil": "kibana",
  "mapping": {
    "event.dataset": {
      "type": "keyword"
    },
    "user.name": {
      "type": "keyword"
    },
    "@timestamp": {
      "type": "date"
    }
  },
  "documents": [
    {
      "id": "a",
      "event.dataset": "auth",
      "user.name": "alice",
      "@timestamp": "2026-10-21T09:00:00Z"
    },
    {
      "id": "b",
      "event.dataset": "auth",
      "user.name": "alice",
      "@timestamp": "2026-10-21T09:05:00Z"
    },
    {
      "id": "c",
      "event.dataset": "auth",
      "user.name": "Alice",
      "@timestamp": "2026-10-21T09:02:00Z"
    },
    {
      "id": "d",
      "event.dataset": "web",
      "user.name": "alice",
      "@timestamp": "2026-10-21T09:01:00Z"
    },
    {
      "id": "e",
      "event.dataset": "auth",
      "user.name": "alice",
      "@timestamp": "2026-10-21T09:04:59Z"
    }
  ],
  "context": {
    "time_filter": {
      "field": "@timestamp",
      "gte": "2026-10-21T09:00:00Z",
      "lt": "2026-10-21T09:05:00Z"
    }
  }
}
```

```kibana
event.dataset: auth
```
:::

::: anlat Sorgu ile dış kapsam birlikte uygulanır
Discover'da doğru data view ve zaman aralığı sorgu kadar önemlidir. Buradaki JSON'un `documents` listesi seçilmiş veri kapsamını temsil eder; gerçek Kibana data view nesnesini taklit etmez. `mapping` alanın nasıl indekslendiğini, `context.time_filter` ise sorgudan önce uygulanacak açık zaman penceresini belirtir. Örnekte başlangıç dahil, bitiş hariçtir: `[09:00,09:05)`.

`user.name` normalizer olmayan keyword olduğundan `alice`, `Alice` ile eşit değildir. İki koşulu `AND` ile birleştirince ikisi de gerekir. Noktalı ECS adları burada alan yollarıdır; belge kimliği `id` ise yalnız sonucu göstermeye yarar, mapping'e eklenmedikçe sorgulanmaz.

Sonuç sırası varsayılan olarak girdi sırasıdır. Gerçek Discover incelemesini yeniden üretirken sorgu, kapsam, zaman alanı/aralığı ve sıralamayı birlikte kaydet. Bu görevlerde bunlar JSON'da görünür. Kaynak: [KQL alan eşleşmesi](https://www.elastic.co/docs/reference/query-languages/kql).

```meta
dil: kibana
```

```stdin
{
  "dil": "kibana",
  "mapping": {
    "event.dataset": {
      "type": "keyword"
    },
    "user.name": {
      "type": "keyword"
    },
    "@timestamp": {
      "type": "date"
    }
  },
  "documents": [
    {
      "id": "a",
      "event.dataset": "auth",
      "user.name": "alice",
      "@timestamp": "2026-10-21T09:00:00Z"
    },
    {
      "id": "b",
      "event.dataset": "auth",
      "user.name": "alice",
      "@timestamp": "2026-10-21T09:05:00Z"
    },
    {
      "id": "c",
      "event.dataset": "auth",
      "user.name": "Alice",
      "@timestamp": "2026-10-21T09:02:00Z"
    },
    {
      "id": "d",
      "event.dataset": "web",
      "user.name": "alice",
      "@timestamp": "2026-10-21T09:01:00Z"
    },
    {
      "id": "e",
      "event.dataset": "auth",
      "user.name": "alice",
      "@timestamp": "2026-10-21T09:04:59Z"
    }
  ],
  "context": {
    "time_filter": {
      "field": "@timestamp",
      "gte": "2026-10-21T09:00:00Z",
      "lt": "2026-10-21T09:05:00Z"
    }
  }
}
```

```kibana
event.dataset: auth AND user.name: alice
```
:::

::: tahmin
JSON içindeki mapping, belgeler ve context birlikte geçerli. Sorgunun döndürdüğü belge kimliklerini girdi sırasıyla tahmin et. `context.sort` verilmemişse alfabetik sıra uygulanmaz.

```meta
dil: kibana
```

```stdin
{
  "dil": "kibana",
  "mapping": {
    "event.dataset": {
      "type": "keyword"
    },
    "user.name": {
      "type": "keyword"
    },
    "@timestamp": {
      "type": "date"
    }
  },
  "documents": [
    {
      "id": "a",
      "event.dataset": "auth",
      "user.name": "alice",
      "@timestamp": "2026-10-21T09:00:00Z"
    },
    {
      "id": "b",
      "event.dataset": "auth",
      "user.name": "alice",
      "@timestamp": "2026-10-21T09:05:00Z"
    },
    {
      "id": "c",
      "event.dataset": "auth",
      "user.name": "Alice",
      "@timestamp": "2026-10-21T09:02:00Z"
    },
    {
      "id": "d",
      "event.dataset": "web",
      "user.name": "alice",
      "@timestamp": "2026-10-21T09:01:00Z"
    },
    {
      "id": "e",
      "event.dataset": "auth",
      "user.name": "alice",
      "@timestamp": "2026-10-21T09:04:59Z"
    }
  ],
  "context": {
    "time_filter": {
      "field": "@timestamp",
      "gte": "2026-10-21T09:00:00Z",
      "lt": "2026-10-21T09:05:00Z"
    }
  }
}
```

```kibana
event.dataset: auth AND user.name: alice
```

???

```text
a
e
```

`a` ve `e` iki keyword koşulunu ve dış zaman penceresini sağlar. `b` bitiş sınırında, `c` harf farkıyla, `d` veri kümesi farkıyla elenir.
:::

::: gorev İstemci adını seç

Yalnız user.name tam alice olan belgeleri seç. JSON içindeki zaman penceresi ayrıca uygulanır; bu görevde event.dataset kısıtı istenmiyor.

```meta
dil: kibana
```

```stdin
{
  "dil": "kibana",
  "mapping": {
    "event.dataset": {
      "type": "keyword"
    },
    "user.name": {
      "type": "keyword"
    },
    "@timestamp": {
      "type": "date"
    }
  },
  "documents": [
    {
      "id": "a",
      "event.dataset": "auth",
      "user.name": "alice",
      "@timestamp": "2026-10-21T09:00:00Z"
    },
    {
      "id": "b",
      "event.dataset": "auth",
      "user.name": "alice",
      "@timestamp": "2026-10-21T09:05:00Z"
    },
    {
      "id": "c",
      "event.dataset": "auth",
      "user.name": "Alice",
      "@timestamp": "2026-10-21T09:02:00Z"
    },
    {
      "id": "d",
      "event.dataset": "web",
      "user.name": "alice",
      "@timestamp": "2026-10-21T09:01:00Z"
    },
    {
      "id": "e",
      "event.dataset": "auth",
      "user.name": "alice",
      "@timestamp": "2026-10-21T09:04:59Z"
    }
  ],
  "context": {
    "time_filter": {
      "field": "@timestamp",
      "gte": "2026-10-21T09:00:00Z",
      "lt": "2026-10-21T09:05:00Z"
    }
  }
}
```

```starter
event.dataset: "__pafta_baslangic__"
```

```test
eq(eslesenler(), ['a', 'd', 'e'], "girdi korpusunun sabit kimlikleri")
eq(referans('user.name: alice'), ['a', 'd', 'e'], "referans sorgunun native sağlaması")
ek = [{'id': 'ilk', 'event.dataset': 'auth', 'user.name': 'alice', '@timestamp': '2026-10-21T09:00:00Z'}, {'id': 'once', 'event.dataset': 'auth', 'user.name': 'alice', '@timestamp': '2026-10-21T08:59:59.999Z'}, {'id': 'web', 'event.dataset': 'web', 'user.name': 'alice', '@timestamp': '2026-10-21T09:01:00Z'}, {'id': 'harf', 'event.dataset': 'auth', 'user.name': 'ALICE', '@timestamp': '2026-10-21T09:01:00Z'}, {'id': 'eksik', 'event.dataset': 'auth', '@timestamp': '2026-10-21T09:01:00Z'}, {'id': 'bos', 'event.dataset': 'auth', 'user.name': '', '@timestamp': '2026-10-21T09:01:00Z'}, {'id': 'son-ic', 'event.dataset': 'auth', 'user.name': 'alice', '@timestamp': '2026-10-21T09:04:59.999Z'}, {'id': 'son', 'event.dataset': 'auth', 'user.name': 'alice', '@timestamp': '2026-10-21T09:05:00Z'}, {'id': 'sonra', 'event.dataset': 'auth', 'user.name': 'alice', '@timestamp': '2026-10-21T09:05:00.001Z'}]
eq(eslesenler({"documents": ek}), ['ilk', 'web', 'son-ic'], "değişen belgeler ve yakın karşı örnekler")
eq(eslesenler({"documents": list(reversed(ek))}), ['son-ic', 'web', 'ilk'], "sonuç girdi sırasını izler")
```

```solution
user.name: alice
```

```hint
Tek keyword alanda tam eşitlik için alan: değer yaz.
```

:::

::: gorev İki alanı birlikte iste

event.dataset tam auth ve user.name tam alice olan belgeleri seç. İki koşul aynı belgede sağlansın. JSON zaman penceresini sorguya kopyalaman gerekmiyor.

```meta
dil: kibana
```

```stdin
{
  "dil": "kibana",
  "mapping": {
    "event.dataset": {
      "type": "keyword"
    },
    "user.name": {
      "type": "keyword"
    },
    "@timestamp": {
      "type": "date"
    }
  },
  "documents": [
    {
      "id": "a",
      "event.dataset": "auth",
      "user.name": "alice",
      "@timestamp": "2026-10-21T09:00:00Z"
    },
    {
      "id": "b",
      "event.dataset": "auth",
      "user.name": "alice",
      "@timestamp": "2026-10-21T09:05:00Z"
    },
    {
      "id": "c",
      "event.dataset": "auth",
      "user.name": "Alice",
      "@timestamp": "2026-10-21T09:02:00Z"
    },
    {
      "id": "d",
      "event.dataset": "web",
      "user.name": "alice",
      "@timestamp": "2026-10-21T09:01:00Z"
    },
    {
      "id": "e",
      "event.dataset": "auth",
      "user.name": "alice",
      "@timestamp": "2026-10-21T09:04:59Z"
    }
  ],
  "context": {
    "time_filter": {
      "field": "@timestamp",
      "gte": "2026-10-21T09:00:00Z",
      "lt": "2026-10-21T09:05:00Z"
    }
  }
}
```

```starter
event.dataset: "__pafta_baslangic__"
```

```test
eq(eslesenler(), ['a', 'e'], "girdi korpusunun sabit kimlikleri")
eq(referans('event.dataset: auth AND user.name: alice'), ['a', 'e'], "referans sorgunun native sağlaması")
ek = [{'id': 'ilk', 'event.dataset': 'auth', 'user.name': 'alice', '@timestamp': '2026-10-21T09:00:00Z'}, {'id': 'once', 'event.dataset': 'auth', 'user.name': 'alice', '@timestamp': '2026-10-21T08:59:59.999Z'}, {'id': 'web', 'event.dataset': 'web', 'user.name': 'alice', '@timestamp': '2026-10-21T09:01:00Z'}, {'id': 'harf', 'event.dataset': 'auth', 'user.name': 'ALICE', '@timestamp': '2026-10-21T09:01:00Z'}, {'id': 'eksik', 'event.dataset': 'auth', '@timestamp': '2026-10-21T09:01:00Z'}, {'id': 'bos', 'event.dataset': 'auth', 'user.name': '', '@timestamp': '2026-10-21T09:01:00Z'}, {'id': 'son-ic', 'event.dataset': 'auth', 'user.name': 'alice', '@timestamp': '2026-10-21T09:04:59.999Z'}, {'id': 'son', 'event.dataset': 'auth', 'user.name': 'alice', '@timestamp': '2026-10-21T09:05:00Z'}, {'id': 'sonra', 'event.dataset': 'auth', 'user.name': 'alice', '@timestamp': '2026-10-21T09:05:00.001Z'}]
eq(eslesenler({"documents": ek}), ['ilk', 'son-ic'], "değişen belgeler ve yakın karşı örnekler")
eq(eslesenler({"documents": list(reversed(ek))}), ['son-ic', 'ilk'], "sonuç girdi sırasını izler")
```

```solution
event.dataset: auth AND user.name: alice
```

```hint
İki alan eşleşmesini AND ile bağla.
```

:::
