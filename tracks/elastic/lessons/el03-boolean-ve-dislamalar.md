---
id: el03
title: Mantık · Gruplar, Öncelik ve NOT
summary: Kibana bağlamında NOT > AND > OR; alan grupları, diziler ve eksik alanın negatif koşula etkisi.
---

::: anlat Öncelik bir filtre kapsamını değiştirebilir
Kibana sorgu çubuğu bağlamında NOT önce, sonra AND, sonra OR uygulanır. `A OR B AND C`, `A OR (B AND C)` anlamındadır. Parantez, inceleme sorusunu görünür kılar: dış kaynak/kapsam koşulunu iki alternatif dala birden uygulamak için `kapsam AND (dal1 OR dal2)` yaz.

Elasticsearch'ün Query DSL kql bileşeni ve ES|QL KQL fonksiyonu için AND/OR öncelik davranışını Kibana ile aynı varsayma; resmi belgede fark açıklanır. Bu yol **Kibana** önceliğini kullanır. Taşınabilir sorgularda parantez kullanmak niyeti korur.

Boolean sözcükler harf duyarsızdır; alan değerleri ise mapping'e bağlıdır. AND/OR iki yanında, NOT sonrasında boşluk bırak. Bir keyword değeri gerçekten AND ise `"AND"` veya `\AND` yaz. Kaynak: [Birleştirme ve öncelik](https://www.elastic.co/docs/reference/query-languages/kql).

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
    "event.outcome": {
      "type": "keyword"
    },
    "severity": {
      "type": "keyword"
    },
    "user.name": {
      "type": "keyword"
    },
    "tags": {
      "type": "keyword"
    }
  },
  "documents": [
    {
      "id": "a",
      "event.dataset": "auth",
      "event.outcome": "failure",
      "severity": "low",
      "user.name": "alice",
      "tags": [
        "production",
        "blue"
      ]
    },
    {
      "id": "b",
      "event.dataset": "web",
      "event.outcome": "failure",
      "severity": "high",
      "user.name": "bob",
      "tags": [
        "production",
        "deprecated"
      ]
    },
    {
      "id": "c",
      "event.dataset": "auth",
      "event.outcome": "success",
      "severity": "high",
      "user.name": "bob",
      "tags": [
        "blue"
      ]
    },
    {
      "id": "d",
      "event.dataset": "web",
      "event.outcome": "success",
      "severity": "low",
      "user.name": "system",
      "tags": [
        "Production"
      ]
    },
    {
      "id": "e",
      "event.dataset": "auth",
      "event.outcome": "failure",
      "severity": "high",
      "user.name": "system"
    },
    {
      "id": "f",
      "event.dataset": "auth",
      "event.outcome": "failure",
      "severity": "low",
      "tags": [
        "production"
      ]
    },
    {
      "id": "g",
      "event.dataset": "auth",
      "severity": "low"
    }
  ],
  "context": {}
}
```

```kibana
event.dataset: auth AND (event.outcome: failure OR severity: high) AND NOT user.name: system
```
:::

::: anlat Dışlama, alanın var olmasını gerektirmez
`NOT user.name: system`, pozitif system eşleşmesinin tersidir. user.name eksikse pozitif eşleşme başarısız olur ve NOT koşulu sağlanır. Kullanıcı adının ayrıca var olmasını istiyorsan `user.name: * AND NOT user.name: system` eklemelisin. Bu görevde adsız auth olayı, diğer koşulları sağlıyorsa dışlanmaz.

`tags: (production AND NOT deprecated)` alan grubunda iki değer koşulunu aynı alana uygular. Keyword dizisinde production bir elemanda, deprecated başka elemanda olabilir; production bulunup hiçbir eleman deprecated değilse sorgu sağlanır. Dizi boşsa production koşulu sağlanmaz.

Düz skaler dizilerde aynı alanın iki koşulunun aynı elemanla sağlanmasını otomatik bekleme. Nesne dizisindeki aynı çocuk ilişkisi ise nested mapping ve ayrı blok ister; proje paftasında ele alacağız. Kaynak: [Alan grupları](https://www.elastic.co/docs/reference/query-languages/kql).

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
    "event.outcome": {
      "type": "keyword"
    },
    "severity": {
      "type": "keyword"
    },
    "user.name": {
      "type": "keyword"
    },
    "tags": {
      "type": "keyword"
    }
  },
  "documents": [
    {
      "id": "a",
      "event.dataset": "auth",
      "event.outcome": "failure",
      "severity": "low",
      "user.name": "alice",
      "tags": [
        "production",
        "blue"
      ]
    },
    {
      "id": "b",
      "event.dataset": "web",
      "event.outcome": "failure",
      "severity": "high",
      "user.name": "bob",
      "tags": [
        "production",
        "deprecated"
      ]
    },
    {
      "id": "c",
      "event.dataset": "auth",
      "event.outcome": "success",
      "severity": "high",
      "user.name": "bob",
      "tags": [
        "blue"
      ]
    },
    {
      "id": "d",
      "event.dataset": "web",
      "event.outcome": "success",
      "severity": "low",
      "user.name": "system",
      "tags": [
        "Production"
      ]
    },
    {
      "id": "e",
      "event.dataset": "auth",
      "event.outcome": "failure",
      "severity": "high",
      "user.name": "system"
    },
    {
      "id": "f",
      "event.dataset": "auth",
      "event.outcome": "failure",
      "severity": "low",
      "tags": [
        "production"
      ]
    },
    {
      "id": "g",
      "event.dataset": "auth",
      "severity": "low"
    }
  ],
  "context": {}
}
```

```kibana
tags: (production AND NOT deprecated)
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
    "event.outcome": {
      "type": "keyword"
    },
    "severity": {
      "type": "keyword"
    },
    "user.name": {
      "type": "keyword"
    },
    "tags": {
      "type": "keyword"
    }
  },
  "documents": [
    {
      "id": "a",
      "event.dataset": "auth",
      "event.outcome": "failure",
      "severity": "low",
      "user.name": "alice",
      "tags": [
        "production",
        "blue"
      ]
    },
    {
      "id": "b",
      "event.dataset": "web",
      "event.outcome": "failure",
      "severity": "high",
      "user.name": "bob",
      "tags": [
        "production",
        "deprecated"
      ]
    },
    {
      "id": "c",
      "event.dataset": "auth",
      "event.outcome": "success",
      "severity": "high",
      "user.name": "bob",
      "tags": [
        "blue"
      ]
    },
    {
      "id": "d",
      "event.dataset": "web",
      "event.outcome": "success",
      "severity": "low",
      "user.name": "system",
      "tags": [
        "Production"
      ]
    },
    {
      "id": "e",
      "event.dataset": "auth",
      "event.outcome": "failure",
      "severity": "high",
      "user.name": "system"
    },
    {
      "id": "f",
      "event.dataset": "auth",
      "event.outcome": "failure",
      "severity": "low",
      "tags": [
        "production"
      ]
    },
    {
      "id": "g",
      "event.dataset": "auth",
      "severity": "low"
    }
  ],
  "context": {}
}
```

```kibana
event.dataset: auth OR severity: high AND NOT user.name: system
```

???

```text
a
b
c
e
f
g
```

Önce high AND NOT system dalı kurulur; sonra auth dalıyla OR uygulanır. Auth olan `e`, system olsa da ilk dal sayesinde kalır. `f`/`g` için eksik kullanıcı adı NOT sonucunu değiştirebilir; sorgu bir varlık şartı içermiyor.
:::

::: gorev Kapsamı iki dala da uygula

Yalnız auth belgeleri içinde outcome=failure veya severity=high olanları seç; user.name tam system ise dışla. Kullanıcı adı eksik olması tek başına dışlama sebebi değil.

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
    "event.outcome": {
      "type": "keyword"
    },
    "severity": {
      "type": "keyword"
    },
    "user.name": {
      "type": "keyword"
    },
    "tags": {
      "type": "keyword"
    }
  },
  "documents": [
    {
      "id": "a",
      "event.dataset": "auth",
      "event.outcome": "failure",
      "severity": "low",
      "user.name": "alice",
      "tags": [
        "production",
        "blue"
      ]
    },
    {
      "id": "b",
      "event.dataset": "web",
      "event.outcome": "failure",
      "severity": "high",
      "user.name": "bob",
      "tags": [
        "production",
        "deprecated"
      ]
    },
    {
      "id": "c",
      "event.dataset": "auth",
      "event.outcome": "success",
      "severity": "high",
      "user.name": "bob",
      "tags": [
        "blue"
      ]
    },
    {
      "id": "d",
      "event.dataset": "web",
      "event.outcome": "success",
      "severity": "low",
      "user.name": "system",
      "tags": [
        "Production"
      ]
    },
    {
      "id": "e",
      "event.dataset": "auth",
      "event.outcome": "failure",
      "severity": "high",
      "user.name": "system"
    },
    {
      "id": "f",
      "event.dataset": "auth",
      "event.outcome": "failure",
      "severity": "low",
      "tags": [
        "production"
      ]
    },
    {
      "id": "g",
      "event.dataset": "auth",
      "severity": "low"
    }
  ],
  "context": {}
}
```

```starter
event.dataset: "__pafta_baslangic__"
```

```test
eq(eslesenler(), ['a', 'c', 'f'], "girdi korpusunun sabit kimlikleri")
eq(referans('event.dataset: auth AND (event.outcome: failure OR severity: high) AND NOT user.name: system'), ['a', 'c', 'f'], "referans sorgunun native sağlaması")
ek = [{'id': 'hata', 'event.dataset': 'auth', 'event.outcome': 'failure', 'severity': 'low', 'user.name': 'eva'}, {'id': 'yuksek', 'event.dataset': 'auth', 'event.outcome': 'success', 'severity': 'high', 'user.name': 'eva'}, {'id': 'web', 'event.dataset': 'web', 'event.outcome': 'failure', 'severity': 'high', 'user.name': 'eva'}, {'id': 'sistem', 'event.dataset': 'auth', 'event.outcome': 'failure', 'severity': 'high', 'user.name': 'system'}, {'id': 'dusuk', 'event.dataset': 'auth', 'event.outcome': 'success', 'severity': 'low', 'user.name': 'eva'}, {'id': 'adsiz', 'event.dataset': 'auth', 'event.outcome': 'failure', 'severity': 'low'}, {'id': 'bos-dal', 'event.dataset': 'auth', 'user.name': 'eva'}]
eq(eslesenler({"documents": ek}), ['hata', 'yuksek', 'adsiz'], "değişen belgeler ve yakın karşı örnekler")
eq(eslesenler({"documents": list(reversed(ek))}), ['adsiz', 'yuksek', 'hata'], "sonuç girdi sırasını izler")
```

```solution
event.dataset: auth AND (event.outcome: failure OR severity: high) AND NOT user.name: system
```

```hint
Auth koşulunu AND ile dışarıda tut; iki alternatif koşulu parantez içinde OR ile bağla.
```

:::

::: gorev Dizide olumlu ve olumsuz üyelik

tags alanında production değeri bulunan ve hiçbir tags değeri deprecated olmayan belgeleri seç. Harf duyarlı keyword eşleşmesini koru; boş ve eksik dizi yeterli değil.

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
    "event.outcome": {
      "type": "keyword"
    },
    "severity": {
      "type": "keyword"
    },
    "user.name": {
      "type": "keyword"
    },
    "tags": {
      "type": "keyword"
    }
  },
  "documents": [
    {
      "id": "a",
      "event.dataset": "auth",
      "event.outcome": "failure",
      "severity": "low",
      "user.name": "alice",
      "tags": [
        "production",
        "blue"
      ]
    },
    {
      "id": "b",
      "event.dataset": "web",
      "event.outcome": "failure",
      "severity": "high",
      "user.name": "bob",
      "tags": [
        "production",
        "deprecated"
      ]
    },
    {
      "id": "c",
      "event.dataset": "auth",
      "event.outcome": "success",
      "severity": "high",
      "user.name": "bob",
      "tags": [
        "blue"
      ]
    },
    {
      "id": "d",
      "event.dataset": "web",
      "event.outcome": "success",
      "severity": "low",
      "user.name": "system",
      "tags": [
        "Production"
      ]
    },
    {
      "id": "e",
      "event.dataset": "auth",
      "event.outcome": "failure",
      "severity": "high",
      "user.name": "system"
    },
    {
      "id": "f",
      "event.dataset": "auth",
      "event.outcome": "failure",
      "severity": "low",
      "tags": [
        "production"
      ]
    },
    {
      "id": "g",
      "event.dataset": "auth",
      "severity": "low"
    }
  ],
  "context": {}
}
```

```starter
event.dataset: "__pafta_baslangic__"
```

```test
eq(eslesenler(), ['a', 'f'], "girdi korpusunun sabit kimlikleri")
eq(referans('tags: (production AND NOT deprecated)'), ['a', 'f'], "referans sorgunun native sağlaması")
ek = [{'id': 'tek', 'tags': 'production'}, {'id': 'ikisi', 'tags': ['production', 'deprecated']}, {'id': 'karisik', 'tags': ['blue', 'production']}, {'id': 'harf', 'tags': ['Production']}, {'id': 'bos', 'tags': []}, {'id': 'yok'}]
eq(eslesenler({"documents": ek}), ['tek', 'karisik'], "değişen belgeler ve yakın karşı örnekler")
eq(eslesenler({"documents": list(reversed(ek))}), ['karisik', 'tek'], "sonuç girdi sırasını izler")
```

```solution
tags: (production AND NOT deprecated)
```

```hint
Alan grubunda production AND NOT deprecated yazabilirsin.
```

:::
