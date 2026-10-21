---
id: el04
title: Aralıklar · Sayılar ve Açık Zaman Uçları
summary: Typed sayı karşılaştırması, iki uç ve milisaniye komşuları; açık saat dilimli tarih penceresi yaz.
---

::: anlat İşleci değiştirmek tam sınırdaki belgeyi değiştirir
KQL aralıkları `<`, `<=`, `>` ve `>=` ile kurulur. Tür mapping'den gelir: integer 400, metinsel "400" karşılaştırması değildir. JSON belgelerinde sayı alanına gerçek sayı koy; bu tezgâh otomatik belge tür dönüşümü yapmaz.

`[400,500)` penceresi 400'ü içerir, 500'ü dışlar. Integer için bu, 400–499 kapalı aralığıyla aynı kümedir; 399 ve 500 yakın karşı örneklerdir. `>=` yerine `>` ilk geçerli değeri kaybettirir. `< 500` yerine `<= 500` ilk dış değeri ekler.

Her karşılaştırma bir belge koşuludur. Çok değerli sayı dizisinde `n > 300 AND n < 400`, n=[500,10] için sağlanabilir: ilk koşulu 500, ikincisini 10 sağlar. Aynı dizi elemanını iki koşulla ilişkilendirdiğini varsayma. Kaynak: [KQL aralıkları](https://www.elastic.co/docs/reference/query-languages/kql).

```meta
dil: kibana
```

```stdin
{
  "dil": "kibana",
  "mapping": {
    "http.response.status_code": {
      "type": "integer"
    },
    "@timestamp": {
      "type": "date"
    }
  },
  "documents": [
    {
      "id": "alt",
      "http.response.status_code": 399,
      "@timestamp": "2026-10-21T08:59:59.999Z"
    },
    {
      "id": "ilk",
      "http.response.status_code": 400,
      "@timestamp": "2026-10-21T09:00:00Z"
    },
    {
      "id": "ic",
      "http.response.status_code": 401,
      "@timestamp": "2026-10-21T09:00:00.001Z"
    },
    {
      "id": "son-ic",
      "http.response.status_code": 499,
      "@timestamp": "2026-10-21T09:04:59.999Z"
    },
    {
      "id": "sinir",
      "http.response.status_code": 500,
      "@timestamp": "2026-10-21T09:05:00Z"
    },
    {
      "id": "ust",
      "http.response.status_code": 501,
      "@timestamp": "2026-10-21T09:05:00.001Z"
    },
    {
      "id": "eksik"
    }
  ],
  "context": {}
}
```

```kibana
http.response.status_code >= 400 AND http.response.status_code < 500
```
:::

::: anlat Tarih metnini takvim değeri olarak karşılaştır
Date mapping, ISO metni karakter karakter sıralamak yerine zaman değeriyle karşılaştırır. `09:00Z` ile `12:00+03:00` aynı andır. Saat içindeki iki nokta özel karakter olduğundan tam zaman değerini çift tırnağa al. Tezgâhta açık saat dilimli, en çok milisaniye hassasiyetli ISO zaman kullan; date math, yerel saat tahmini ve kısmi tarih bu sınırlı motorda reddedilir.

Bu görevde sorgunun kendisi başlangıç dahil, bitiş hariç zaman penceresini kurar; dış context zaman filtresi boş. Bir önceki paftadaki bağlam filtresiyle bunu karıştırma. İkisi birlikte verilirse ikisi de uygulanır.

Eksik veya null tarih pozitif aralık koşulunu sağlamaz. Testlerde her ucun hemen altı, tam eşiti ve hemen üstü var; yalnız ortadaki bir olayı denemek sınır hatasını göstermez. Kaynak: [KQL zaman aralıkları](https://www.elastic.co/docs/reference/query-languages/kql).

```meta
dil: kibana
```

```stdin
{
  "dil": "kibana",
  "mapping": {
    "http.response.status_code": {
      "type": "integer"
    },
    "@timestamp": {
      "type": "date"
    }
  },
  "documents": [
    {
      "id": "alt",
      "http.response.status_code": 399,
      "@timestamp": "2026-10-21T08:59:59.999Z"
    },
    {
      "id": "ilk",
      "http.response.status_code": 400,
      "@timestamp": "2026-10-21T09:00:00Z"
    },
    {
      "id": "ic",
      "http.response.status_code": 401,
      "@timestamp": "2026-10-21T09:00:00.001Z"
    },
    {
      "id": "son-ic",
      "http.response.status_code": 499,
      "@timestamp": "2026-10-21T09:04:59.999Z"
    },
    {
      "id": "sinir",
      "http.response.status_code": 500,
      "@timestamp": "2026-10-21T09:05:00Z"
    },
    {
      "id": "ust",
      "http.response.status_code": 501,
      "@timestamp": "2026-10-21T09:05:00.001Z"
    },
    {
      "id": "eksik"
    }
  ],
  "context": {}
}
```

```kibana
@timestamp >= "2026-10-21T09:00:00Z" AND @timestamp < "2026-10-21T09:05:00Z"
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
    "http.response.status_code": {
      "type": "integer"
    },
    "@timestamp": {
      "type": "date"
    }
  },
  "documents": [
    {
      "id": "alt",
      "http.response.status_code": 399,
      "@timestamp": "2026-10-21T08:59:59.999Z"
    },
    {
      "id": "ilk",
      "http.response.status_code": 400,
      "@timestamp": "2026-10-21T09:00:00Z"
    },
    {
      "id": "ic",
      "http.response.status_code": 401,
      "@timestamp": "2026-10-21T09:00:00.001Z"
    },
    {
      "id": "son-ic",
      "http.response.status_code": 499,
      "@timestamp": "2026-10-21T09:04:59.999Z"
    },
    {
      "id": "sinir",
      "http.response.status_code": 500,
      "@timestamp": "2026-10-21T09:05:00Z"
    },
    {
      "id": "ust",
      "http.response.status_code": 501,
      "@timestamp": "2026-10-21T09:05:00.001Z"
    },
    {
      "id": "eksik"
    }
  ],
  "context": {}
}
```

```kibana
http.response.status_code >= 400 AND http.response.status_code < 500
```

???

```text
ilk
ic
son-ic
```

399 alt sınırın altında, 400/401/499 içeride, 500 ve 501 dışarıda. Eksik sayısal alan pozitif karşılaştırmayı sağlamaz.
:::

::: gorev 4xx sayı penceresi

http.response.status_code en az 400, 500’den küçük olsun. Null ve eksik alanlar kalmasın. Durum kodunu metinsel önek veya wildcard ile arama.

```meta
dil: kibana
```

```stdin
{
  "dil": "kibana",
  "mapping": {
    "http.response.status_code": {
      "type": "integer"
    },
    "@timestamp": {
      "type": "date"
    }
  },
  "documents": [
    {
      "id": "alt",
      "http.response.status_code": 399,
      "@timestamp": "2026-10-21T08:59:59.999Z"
    },
    {
      "id": "ilk",
      "http.response.status_code": 400,
      "@timestamp": "2026-10-21T09:00:00Z"
    },
    {
      "id": "ic",
      "http.response.status_code": 401,
      "@timestamp": "2026-10-21T09:00:00.001Z"
    },
    {
      "id": "son-ic",
      "http.response.status_code": 499,
      "@timestamp": "2026-10-21T09:04:59.999Z"
    },
    {
      "id": "sinir",
      "http.response.status_code": 500,
      "@timestamp": "2026-10-21T09:05:00Z"
    },
    {
      "id": "ust",
      "http.response.status_code": 501,
      "@timestamp": "2026-10-21T09:05:00.001Z"
    },
    {
      "id": "eksik"
    }
  ],
  "context": {}
}
```

```starter
http.response.status_code: -999999
```

```test
eq(eslesenler(), ['ilk', 'ic', 'son-ic'], "girdi korpusunun sabit kimlikleri")
eq(referans('http.response.status_code >= 400 AND http.response.status_code < 500'), ['ilk', 'ic', 'son-ic'], "referans sorgunun native sağlaması")
ek = [{'id': '399', 'http.response.status_code': 399}, {'id': '400', 'http.response.status_code': 400}, {'id': '401', 'http.response.status_code': 401}, {'id': '498', 'http.response.status_code': 498}, {'id': '499', 'http.response.status_code': 499}, {'id': '500', 'http.response.status_code': 500}, {'id': '501', 'http.response.status_code': 501}, {'id': 'null', 'http.response.status_code': None}, {'id': 'yok'}]
eq(eslesenler({"documents": ek}), ['400', '401', '498', '499'], "değişen belgeler ve yakın karşı örnekler")
eq(eslesenler({"documents": list(reversed(ek))}), ['499', '498', '401', '400'], "sonuç girdi sırasını izler")
```

```solution
http.response.status_code >= 400 AND http.response.status_code < 500
```

```hint
Aynı sayısal alana >= 400 ve < 500 koşullarını AND ile uygula.
```

:::

::: gorev Sorguda zaman penceresi

@timestamp için 21 Ekim 2026 09:00:00Z dahil, 09:05:00Z hariç pencereyi yaz. Başka saat dilimiyle aynı an gösterildiğinde de aynı sonucu versin; alan date türünde.

```meta
dil: kibana
```

```stdin
{
  "dil": "kibana",
  "mapping": {
    "http.response.status_code": {
      "type": "integer"
    },
    "@timestamp": {
      "type": "date"
    }
  },
  "documents": [
    {
      "id": "alt",
      "http.response.status_code": 399,
      "@timestamp": "2026-10-21T08:59:59.999Z"
    },
    {
      "id": "ilk",
      "http.response.status_code": 400,
      "@timestamp": "2026-10-21T09:00:00Z"
    },
    {
      "id": "ic",
      "http.response.status_code": 401,
      "@timestamp": "2026-10-21T09:00:00.001Z"
    },
    {
      "id": "son-ic",
      "http.response.status_code": 499,
      "@timestamp": "2026-10-21T09:04:59.999Z"
    },
    {
      "id": "sinir",
      "http.response.status_code": 500,
      "@timestamp": "2026-10-21T09:05:00Z"
    },
    {
      "id": "ust",
      "http.response.status_code": 501,
      "@timestamp": "2026-10-21T09:05:00.001Z"
    },
    {
      "id": "eksik"
    }
  ],
  "context": {}
}
```

```starter
http.response.status_code: -999999
```

```test
eq(eslesenler(), ['ilk', 'ic', 'son-ic'], "girdi korpusunun sabit kimlikleri")
eq(referans('@timestamp >= "2026-10-21T09:00:00Z" AND @timestamp < "2026-10-21T09:05:00Z"'), ['ilk', 'ic', 'son-ic'], "referans sorgunun native sağlaması")
ek = [{'id': 'once', '@timestamp': '2026-10-21T08:59:59.999Z'}, {'id': 'esit-alt', '@timestamp': '2026-10-21T09:00:00Z'}, {'id': 'ust-alt', '@timestamp': '2026-10-21T09:00:00.001Z'}, {'id': 'alt-ust', '@timestamp': '2026-10-21T09:04:59.999Z'}, {'id': 'esit-ust', '@timestamp': '2026-10-21T09:05:00Z'}, {'id': 'sonra', '@timestamp': '2026-10-21T09:05:00.001Z'}, {'id': 'offset', '@timestamp': '2026-10-21T12:00:00+03:00'}, {'id': 'null', '@timestamp': None}, {'id': 'yok'}]
eq(eslesenler({"documents": ek}), ['esit-alt', 'ust-alt', 'alt-ust', 'offset'], "değişen belgeler ve yakın karşı örnekler")
eq(eslesenler({"documents": list(reversed(ek))}), ['offset', 'alt-ust', 'ust-alt', 'esit-alt'], "sonuç girdi sırasını izler")
```

```solution
@timestamp >= "2026-10-21T09:00:00Z" AND @timestamp < "2026-10-21T09:05:00Z"
```

```hint
Tam ISO değerlerini tırnakla; alt uç >=, üst uç < olmalı.
```

:::
