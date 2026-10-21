---
id: el06
title: Proje · Aynı Çocukta Nested Koşulları
summary: Nesne dizisinde aynı çocuk ilişkisi; ayrı nested sorguların farkı ve kaynak/zamanla birleştirilmiş inceleme projesi.
---

::: anlat Düz alanlar nesne kimliğini korumayabilir
Bir nesne dizisinde alice adının bir elemanda, admin rolünün başka elemanda bulunması, alice kullanıcısının admin olduğunu göstermez. Elasticsearch object dizilerini düzleştirdiğinde bu ilişki kaybolabilir. Nested mapping, çocuk nesneleri ayrı sorgu kapsamlarında tutar.

`users:{ name: alice AND role: admin }` tek bir users çocuğunda iki koşulu birlikte ister. İçerideki name ve role, users.name ve users.role alanlarına bağlanır. Bu korpusta ikisi de normalizer olmayan keyword'dür. Çocuğun adını dış belgenin diğer alanlarıyla aynı sözlükmüş gibi birleştirme.

Pafta çocuk koşullarını gerçek Lucene'de birlikte çalıştırıp eşleşmeyi sahibine yansıtır. Genel bir Elasticsearch nested API'si veya inner_hits sunmaz. Nested alt alanını dışarıda doğrudan sorgulamak bu tezgâhta açık hata verir; blok kullan. Kaynak: [KQL nested sorguları](https://www.elastic.co/docs/reference/query-languages/kql).

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
    "@timestamp": {
      "type": "date"
    },
    "users": {
      "type": "nested"
    },
    "users.name": {
      "type": "keyword"
    },
    "users.role": {
      "type": "keyword"
    }
  },
  "documents": [
    {
      "id": "a",
      "event.dataset": "auth",
      "@timestamp": "2026-10-21T09:01:00Z",
      "users": [
        {
          "name": "alice",
          "role": "user"
        },
        {
          "name": "bob",
          "role": "admin"
        }
      ]
    },
    {
      "id": "b",
      "event.dataset": "auth",
      "@timestamp": "2026-10-21T09:00:00Z",
      "users": [
        {
          "name": "alice",
          "role": "admin"
        }
      ]
    },
    {
      "id": "c",
      "event.dataset": "auth",
      "@timestamp": "2026-10-21T09:02:00Z",
      "users": [
        {
          "name": "Alice",
          "role": "admin"
        }
      ]
    },
    {
      "id": "d",
      "event.dataset": "auth",
      "@timestamp": "2026-10-21T09:03:00Z"
    },
    {
      "id": "e",
      "event.dataset": "auth",
      "@timestamp": "2026-10-21T09:05:00Z",
      "users": [
        {
          "name": "alice",
          "role": "admin"
        }
      ]
    },
    {
      "id": "f",
      "event.dataset": "web",
      "@timestamp": "2026-10-21T09:04:59Z",
      "users": [
        {
          "name": "alice",
          "role": "admin"
        }
      ]
    },
    {
      "id": "g",
      "event.dataset": "auth",
      "@timestamp": "2026-10-21T09:04:59Z",
      "users": [
        {
          "name": "alice",
          "role": "admin"
        }
      ]
    }
  ],
  "context": {}
}
```

```kibana
users:{ name: alice AND role: admin }
```
:::

::: anlat Ayrı bloklar aynı çocuğu zorlamaz
`users:{ name: alice } AND users:{ role: admin }` iki ayrı nested koşuludur. İlki bir çocukta, ikincisi başka çocukta sağlanabilir. İlişki isteniyorsa koşulları tek bloğa koy. `NOT users:{ ... }` ise eşleşen çocuk bulunan sahip belgeleri dışlar; users eksik veya boşsa negatif koşul sağlanabilir.

Projede dış event.dataset koşulunu, tek çocuk bloğunu ve açık zaman penceresini AND ile birleştir. Başlangıç/bitiş hatalarını gerçek olumlu örneklerle sına: alt uç eşitliği geçmeli, üst uç eşitliği geçmemeli. Farklı veri kümesi, yanlış rol, harf farkı ve ayrı çocuklar diğer koşulları sağlasa bile elenmeli.

Sorgu bir inceleme kümesini tanımlar; admin rolünün meşru olup olmadığını veya bir olayın saldırı olduğunu tek başına kanıtlamaz. Sonraki Lucene bölümünde aynı arama alanının farklı sözdizimini kullanacağız; nested bloğunu Lucene query-string'e taşıyamazsın. Kaynak: [Aynı çocuk kapsamı](https://www.elastic.co/docs/reference/query-languages/kql).

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
    "@timestamp": {
      "type": "date"
    },
    "users": {
      "type": "nested"
    },
    "users.name": {
      "type": "keyword"
    },
    "users.role": {
      "type": "keyword"
    }
  },
  "documents": [
    {
      "id": "a",
      "event.dataset": "auth",
      "@timestamp": "2026-10-21T09:01:00Z",
      "users": [
        {
          "name": "alice",
          "role": "user"
        },
        {
          "name": "bob",
          "role": "admin"
        }
      ]
    },
    {
      "id": "b",
      "event.dataset": "auth",
      "@timestamp": "2026-10-21T09:00:00Z",
      "users": [
        {
          "name": "alice",
          "role": "admin"
        }
      ]
    },
    {
      "id": "c",
      "event.dataset": "auth",
      "@timestamp": "2026-10-21T09:02:00Z",
      "users": [
        {
          "name": "Alice",
          "role": "admin"
        }
      ]
    },
    {
      "id": "d",
      "event.dataset": "auth",
      "@timestamp": "2026-10-21T09:03:00Z"
    },
    {
      "id": "e",
      "event.dataset": "auth",
      "@timestamp": "2026-10-21T09:05:00Z",
      "users": [
        {
          "name": "alice",
          "role": "admin"
        }
      ]
    },
    {
      "id": "f",
      "event.dataset": "web",
      "@timestamp": "2026-10-21T09:04:59Z",
      "users": [
        {
          "name": "alice",
          "role": "admin"
        }
      ]
    },
    {
      "id": "g",
      "event.dataset": "auth",
      "@timestamp": "2026-10-21T09:04:59Z",
      "users": [
        {
          "name": "alice",
          "role": "admin"
        }
      ]
    }
  ],
  "context": {}
}
```

```kibana
event.dataset: auth AND users:{ name: alice AND role: admin } AND @timestamp >= "2026-10-21T09:00:00Z" AND @timestamp < "2026-10-21T09:05:00Z"
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
    "@timestamp": {
      "type": "date"
    },
    "users": {
      "type": "nested"
    },
    "users.name": {
      "type": "keyword"
    },
    "users.role": {
      "type": "keyword"
    }
  },
  "documents": [
    {
      "id": "a",
      "event.dataset": "auth",
      "@timestamp": "2026-10-21T09:01:00Z",
      "users": [
        {
          "name": "alice",
          "role": "user"
        },
        {
          "name": "bob",
          "role": "admin"
        }
      ]
    },
    {
      "id": "b",
      "event.dataset": "auth",
      "@timestamp": "2026-10-21T09:00:00Z",
      "users": [
        {
          "name": "alice",
          "role": "admin"
        }
      ]
    },
    {
      "id": "c",
      "event.dataset": "auth",
      "@timestamp": "2026-10-21T09:02:00Z",
      "users": [
        {
          "name": "Alice",
          "role": "admin"
        }
      ]
    },
    {
      "id": "d",
      "event.dataset": "auth",
      "@timestamp": "2026-10-21T09:03:00Z"
    },
    {
      "id": "e",
      "event.dataset": "auth",
      "@timestamp": "2026-10-21T09:05:00Z",
      "users": [
        {
          "name": "alice",
          "role": "admin"
        }
      ]
    },
    {
      "id": "f",
      "event.dataset": "web",
      "@timestamp": "2026-10-21T09:04:59Z",
      "users": [
        {
          "name": "alice",
          "role": "admin"
        }
      ]
    },
    {
      "id": "g",
      "event.dataset": "auth",
      "@timestamp": "2026-10-21T09:04:59Z",
      "users": [
        {
          "name": "alice",
          "role": "admin"
        }
      ]
    }
  ],
  "context": {}
}
```

```kibana
users:{ name: alice AND role: admin }
```

???

```text
b
e
f
g
```

Tek çocukta alice+admin bulunan `b`, `e`, `f`, `g` kalır. Bu sorguda dış veri kümesi veya zaman koşulu yoktur. `a` iki ayrı çocuktan parçaları birleştiremez; `c` harf farkıyla, `d` çocuk yokluğuyla elenir.
:::

::: gorev İki koşul aynı çocukta

En az bir users çocuğunda name tam alice ve role tam admin olan sahip belgeleri seç. İki değerin ayrı çocuklarda bulunması yeterli değil. Dış veri kümesi ve zaman bu görevde kısıtlanmıyor.

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
    "@timestamp": {
      "type": "date"
    },
    "users": {
      "type": "nested"
    },
    "users.name": {
      "type": "keyword"
    },
    "users.role": {
      "type": "keyword"
    }
  },
  "documents": [
    {
      "id": "a",
      "event.dataset": "auth",
      "@timestamp": "2026-10-21T09:01:00Z",
      "users": [
        {
          "name": "alice",
          "role": "user"
        },
        {
          "name": "bob",
          "role": "admin"
        }
      ]
    },
    {
      "id": "b",
      "event.dataset": "auth",
      "@timestamp": "2026-10-21T09:00:00Z",
      "users": [
        {
          "name": "alice",
          "role": "admin"
        }
      ]
    },
    {
      "id": "c",
      "event.dataset": "auth",
      "@timestamp": "2026-10-21T09:02:00Z",
      "users": [
        {
          "name": "Alice",
          "role": "admin"
        }
      ]
    },
    {
      "id": "d",
      "event.dataset": "auth",
      "@timestamp": "2026-10-21T09:03:00Z"
    },
    {
      "id": "e",
      "event.dataset": "auth",
      "@timestamp": "2026-10-21T09:05:00Z",
      "users": [
        {
          "name": "alice",
          "role": "admin"
        }
      ]
    },
    {
      "id": "f",
      "event.dataset": "web",
      "@timestamp": "2026-10-21T09:04:59Z",
      "users": [
        {
          "name": "alice",
          "role": "admin"
        }
      ]
    },
    {
      "id": "g",
      "event.dataset": "auth",
      "@timestamp": "2026-10-21T09:04:59Z",
      "users": [
        {
          "name": "alice",
          "role": "admin"
        }
      ]
    }
  ],
  "context": {}
}
```

```starter
event.dataset: "__pafta_baslangic__"
```

```test
eq(eslesenler(), ['b', 'e', 'f', 'g'], "girdi korpusunun sabit kimlikleri")
eq(referans('users:{ name: alice AND role: admin }'), ['b', 'e', 'f', 'g'], "referans sorgunun native sağlaması")
ek = [{'id': 'ayri', 'users': [{'name': 'alice', 'role': 'user'}, {'name': 'bob', 'role': 'admin'}]}, {'id': 'ayni', 'users': [{'name': 'alice', 'role': 'admin'}]}, {'id': 'nesne', 'users': {'name': 'alice', 'role': 'admin'}}, {'id': 'null', 'users': None}, {'id': 'dizi-bos', 'users': []}, {'id': 'null-cocuk', 'users': [None, {'name': 'alice', 'role': 'admin'}]}, {'id': 'rol', 'users': [{'name': 'alice', 'role': 'reviewer'}]}, {'id': 'harf', 'users': [{'name': 'ALICE', 'role': 'admin'}]}]
eq(eslesenler({"documents": ek}), ['ayni', 'nesne', 'null-cocuk'], "değişen belgeler ve yakın karşı örnekler")
eq(eslesenler({"documents": list(reversed(ek))}), ['null-cocuk', 'nesne', 'ayni'], "sonuç girdi sırasını izler")
```

```solution
users:{ name: alice AND role: admin }
```

```hint
İki çocuk koşulunu users:{ ... } içinde AND ile bağla.
```

:::

::: gorev SOC kapsamını birleştir

Yalnız event.dataset=auth belgelerinde, tek users çocuğu alice+admin olsun. Ayrıca @timestamp 2026-10-21T09:00:00Z dahil, 09:05:00Z hariç pencerede bulunsun. Üç kapsamın tamamını aynı sorguda koru.

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
    "@timestamp": {
      "type": "date"
    },
    "users": {
      "type": "nested"
    },
    "users.name": {
      "type": "keyword"
    },
    "users.role": {
      "type": "keyword"
    }
  },
  "documents": [
    {
      "id": "a",
      "event.dataset": "auth",
      "@timestamp": "2026-10-21T09:01:00Z",
      "users": [
        {
          "name": "alice",
          "role": "user"
        },
        {
          "name": "bob",
          "role": "admin"
        }
      ]
    },
    {
      "id": "b",
      "event.dataset": "auth",
      "@timestamp": "2026-10-21T09:00:00Z",
      "users": [
        {
          "name": "alice",
          "role": "admin"
        }
      ]
    },
    {
      "id": "c",
      "event.dataset": "auth",
      "@timestamp": "2026-10-21T09:02:00Z",
      "users": [
        {
          "name": "Alice",
          "role": "admin"
        }
      ]
    },
    {
      "id": "d",
      "event.dataset": "auth",
      "@timestamp": "2026-10-21T09:03:00Z"
    },
    {
      "id": "e",
      "event.dataset": "auth",
      "@timestamp": "2026-10-21T09:05:00Z",
      "users": [
        {
          "name": "alice",
          "role": "admin"
        }
      ]
    },
    {
      "id": "f",
      "event.dataset": "web",
      "@timestamp": "2026-10-21T09:04:59Z",
      "users": [
        {
          "name": "alice",
          "role": "admin"
        }
      ]
    },
    {
      "id": "g",
      "event.dataset": "auth",
      "@timestamp": "2026-10-21T09:04:59Z",
      "users": [
        {
          "name": "alice",
          "role": "admin"
        }
      ]
    }
  ],
  "context": {}
}
```

```starter
event.dataset: "__pafta_baslangic__"
```

```test
eq(eslesenler(), ['b', 'g'], "girdi korpusunun sabit kimlikleri")
eq(referans('event.dataset: auth AND users:{ name: alice AND role: admin } AND @timestamp >= "2026-10-21T09:00:00Z" AND @timestamp < "2026-10-21T09:05:00Z"'), ['b', 'g'], "referans sorgunun native sağlaması")
ek = [{'id': 'once', 'event.dataset': 'auth', '@timestamp': '2026-10-21T08:59:59.999Z', 'users': [{'name': 'alice', 'role': 'admin'}]}, {'id': 'ilk', 'event.dataset': 'auth', '@timestamp': '2026-10-21T09:00:00Z', 'users': [{'name': 'alice', 'role': 'admin'}]}, {'id': 'ust-ilk', 'event.dataset': 'auth', '@timestamp': '2026-10-21T09:00:00.001Z', 'users': [{'name': 'alice', 'role': 'admin'}]}, {'id': 'alt-son', 'event.dataset': 'auth', '@timestamp': '2026-10-21T09:04:59.999Z', 'users': [{'name': 'alice', 'role': 'admin'}]}, {'id': 'son', 'event.dataset': 'auth', '@timestamp': '2026-10-21T09:05:00Z', 'users': [{'name': 'alice', 'role': 'admin'}]}, {'id': 'sonra', 'event.dataset': 'auth', '@timestamp': '2026-10-21T09:05:00.001Z', 'users': [{'name': 'alice', 'role': 'admin'}]}, {'id': 'ayri', 'event.dataset': 'auth', '@timestamp': '2026-10-21T09:03:00Z', 'users': [{'name': 'alice', 'role': 'user'}, {'name': 'bob', 'role': 'admin'}]}, {'id': 'web', 'event.dataset': 'web', '@timestamp': '2026-10-21T09:03:00Z', 'users': [{'name': 'alice', 'role': 'admin'}]}, {'id': 'harf', 'event.dataset': 'auth', '@timestamp': '2026-10-21T09:03:00Z', 'users': [{'name': 'Alice', 'role': 'admin'}]}, {'id': 'rol', 'event.dataset': 'auth', '@timestamp': '2026-10-21T09:03:00Z', 'users': [{'name': 'alice', 'role': 'reviewer'}]}, {'id': 'yok', 'event.dataset': 'auth', '@timestamp': '2026-10-21T09:03:00Z', 'users': None}, {'id': 'zaman-yok', 'event.dataset': 'auth', 'users': [{'name': 'alice', 'role': 'admin'}]}]
eq(eslesenler({"documents": ek}), ['ilk', 'ust-ilk', 'alt-son'], "değişen belgeler ve yakın karşı örnekler")
eq(eslesenler({"documents": list(reversed(ek))}), ['alt-son', 'ust-ilk', 'ilk'], "sonuç girdi sırasını izler")
```

```solution
event.dataset: auth AND users:{ name: alice AND role: admin } AND @timestamp >= "2026-10-21T09:00:00Z" AND @timestamp < "2026-10-21T09:05:00Z"
```

```hint
Dış koşulları AND ile birleştir; name/role tek nested blokta, tarih uçları >= ve < olsun.
```

:::
