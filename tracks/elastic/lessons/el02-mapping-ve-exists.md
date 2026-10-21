---
id: el02
title: Mapping · Keyword, Text ve Varlık
summary: Keyword tam değer, text native analiz/OR ve tırnaklı ifade; indexed-value exists ile null/boş/ignore_above farkı.
---

::: anlat Aynı metin iki alanda farklı aranabilir
Keyword alan bütün değeri tek terim olarak tutar. Normalizer yoksa harf ve noktalama korunur; lowercase normalizer varsa indeksleme ve sorgu aynı normalizasyondan geçer. Text alanı ise mapping'deki analyzer ile terimlere ayrılır. Bu tezgâhta text analyzer yalnız **standard**, keyword normalizer isteğe bağlı **lowercase** olabilir; özel analiz zinciri varsayılmaz.

Tırnaksız `message: access denied`, standard text alanda iki analyzed terim için **OR** davranır: yalnız access veya yalnız denied içeren belge de eşleşir. İki terimin ikisini zorlamak için `message:(access AND denied)` yaz. Bu, tek tırnaksız değerin varsayılanını AND sanmaktan farklıdır.

Tırnaklı `message: "access denied"` ise native phrase sorgusudur: analyzed terimlerin bu sırada, yan yana bulunmasını ister. Mesajın tamamının yalnız bu iki sözcükten oluşması gerekmez. Kaynaklar: [KQL](https://www.elastic.co/docs/reference/query-languages/kql), [match varsayılan OR](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-match-query).

```meta
dil: kibana
```

```stdin
{
  "dil": "kibana",
  "mapping": {
    "user.name": {
      "type": "keyword",
      "ignore_above": 8
    },
    "message": {
      "type": "text",
      "analyzer": "standard"
    }
  },
  "documents": [
    {
      "id": "a",
      "user.name": "alice",
      "message": "access denied"
    },
    {
      "id": "b",
      "user.name": null,
      "message": "denied access"
    },
    {
      "id": "c",
      "message": "access only"
    },
    {
      "id": "d",
      "user.name": "",
      "message": "denied only"
    },
    {
      "id": "e",
      "user.name": [
        null,
        "bob"
      ],
      "message": "other"
    },
    {
      "id": "f",
      "user.name": [],
      "message": null
    },
    {
      "id": "g",
      "user.name": "toolongname",
      "message": ""
    },
    {
      "id": "h",
      "user.name": "null"
    },
    {
      "id": "i",
      "user.name": [
        "toolongname",
        "eve"
      ]
    }
  ],
  "context": {}
}
```

```kibana
message: access denied
```
:::

::: anlat Exists, JSON anahtarını saymak değildir
`user.name: *`, alanda **indekslenmiş bir değer** arar. Anahtarın bulunması yeterli değildir: null, boş dizi ve yalnız null içeren dizi normalde indekslenmiş değer üretmez. Keyword `""` ise boş metin olsa da değerdir. Bir dizide en az bir indekslenebilir değer bulunması yeterlidir.

Bu korpusta user.name için `ignore_above: 8` var. Sekiz karakterlik keyword indekslenir; dokuz karakterlik değer _source'ta görünmesine rağmen bu alanın aramasına katılmaz. `null_value` tanımlanırsa açık null yerine belirtilen keyword indekslenebilir; eksik anahtar için kendiliğinden eklenmez. Görevde null_value tanımlı değil.

`user.name: "*"` ve `user.name: \*` literal yıldız arar; exists değildir. `NOT user.name: *`, indekslenmiş değeri olmayan belgeleri seçebilir. index:false alan sorguları bu tezgâhta açıkça reddedilir; Elasticsearch doc_values seçeneklerini burada varsayma. Kaynak: [exists ve indekslenmiş değer](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-exists-query).

```meta
dil: kibana
```

```stdin
{
  "dil": "kibana",
  "mapping": {
    "user.name": {
      "type": "keyword",
      "ignore_above": 8
    },
    "message": {
      "type": "text",
      "analyzer": "standard"
    }
  },
  "documents": [
    {
      "id": "a",
      "user.name": "alice",
      "message": "access denied"
    },
    {
      "id": "b",
      "user.name": null,
      "message": "denied access"
    },
    {
      "id": "c",
      "message": "access only"
    },
    {
      "id": "d",
      "user.name": "",
      "message": "denied only"
    },
    {
      "id": "e",
      "user.name": [
        null,
        "bob"
      ],
      "message": "other"
    },
    {
      "id": "f",
      "user.name": [],
      "message": null
    },
    {
      "id": "g",
      "user.name": "toolongname",
      "message": ""
    },
    {
      "id": "h",
      "user.name": "null"
    },
    {
      "id": "i",
      "user.name": [
        "toolongname",
        "eve"
      ]
    }
  ],
  "context": {}
}
```

```kibana
user.name: *
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
    "user.name": {
      "type": "keyword",
      "ignore_above": 8
    },
    "message": {
      "type": "text",
      "analyzer": "standard"
    }
  },
  "documents": [
    {
      "id": "a",
      "user.name": "alice",
      "message": "access denied"
    },
    {
      "id": "b",
      "user.name": null,
      "message": "denied access"
    },
    {
      "id": "c",
      "message": "access only"
    },
    {
      "id": "d",
      "user.name": "",
      "message": "denied only"
    },
    {
      "id": "e",
      "user.name": [
        null,
        "bob"
      ],
      "message": "other"
    },
    {
      "id": "f",
      "user.name": [],
      "message": null
    },
    {
      "id": "g",
      "user.name": "toolongname",
      "message": ""
    },
    {
      "id": "h",
      "user.name": "null"
    },
    {
      "id": "i",
      "user.name": [
        "toolongname",
        "eve"
      ]
    }
  ],
  "context": {}
}
```

```kibana
message: access denied
```

???

```text
a
b
c
d
```

Tırnaksız text değeri OR ile aranır: `a`/`b` iki terimi, `c` yalnız access ve `d` yalnız denied içerir. Sıra şartı ve ikisini birden bulma şartı bu sorguda yoktur.
:::

::: gorev İndekslenmiş kullanıcı değeri

user.name için indekslenmiş bir değeri bulunan belgeleri seç. Boş keyword metni dahil; eksik/null/boş dizi/yalnız null dışarıda. ignore_above=8 etkisini koru.

```meta
dil: kibana
```

```stdin
{
  "dil": "kibana",
  "mapping": {
    "user.name": {
      "type": "keyword",
      "ignore_above": 8
    },
    "message": {
      "type": "text",
      "analyzer": "standard"
    }
  },
  "documents": [
    {
      "id": "a",
      "user.name": "alice",
      "message": "access denied"
    },
    {
      "id": "b",
      "user.name": null,
      "message": "denied access"
    },
    {
      "id": "c",
      "message": "access only"
    },
    {
      "id": "d",
      "user.name": "",
      "message": "denied only"
    },
    {
      "id": "e",
      "user.name": [
        null,
        "bob"
      ],
      "message": "other"
    },
    {
      "id": "f",
      "user.name": [],
      "message": null
    },
    {
      "id": "g",
      "user.name": "toolongname",
      "message": ""
    },
    {
      "id": "h",
      "user.name": "null"
    },
    {
      "id": "i",
      "user.name": [
        "toolongname",
        "eve"
      ]
    }
  ],
  "context": {}
}
```

```starter
user.name: "__pafta_baslangic__"
```

```test
eq(eslesenler(), ['a', 'd', 'e', 'h', 'i'], "girdi korpusunun sabit kimlikleri")
eq(referans('user.name: *'), ['a', 'd', 'e', 'h', 'i'], "referans sorgunun native sağlaması")
ek = [{'id': 'sekiz', 'user.name': 'eight888'}, {'id': 'dokuz', 'user.name': 'nine99999'}, {'id': 'null', 'user.name': None}, {'id': 'dizi-null', 'user.name': [None]}, {'id': 'dizi-bos', 'user.name': []}, {'id': 'bos-metin', 'user.name': ''}, {'id': 'yok'}]
eq(eslesenler({"documents": ek}), ['sekiz', 'bos-metin'], "değişen belgeler ve yakın karşı örnekler")
eq(eslesenler({"documents": list(reversed(ek))}), ['bos-metin', 'sekiz'], "sonuç girdi sırasını izler")
```

```solution
user.name: *
```

```hint
Değer yerinde tırnaksız tek yıldız exists sorgusudur.
```

:::

::: gorev Yan yana iki terim

Standard text message alanında analyzed access ve denied terimleri tam bu sırada yan yana bulunsun. Ters sıra, araya sözcük girmesi veya terimlerin ayrı dizi değerlerine dağılması yeterli değil.

```meta
dil: kibana
```

```stdin
{
  "dil": "kibana",
  "mapping": {
    "user.name": {
      "type": "keyword",
      "ignore_above": 8
    },
    "message": {
      "type": "text",
      "analyzer": "standard"
    }
  },
  "documents": [
    {
      "id": "a",
      "user.name": "alice",
      "message": "access denied"
    },
    {
      "id": "b",
      "user.name": null,
      "message": "denied access"
    },
    {
      "id": "c",
      "message": "access only"
    },
    {
      "id": "d",
      "user.name": "",
      "message": "denied only"
    },
    {
      "id": "e",
      "user.name": [
        null,
        "bob"
      ],
      "message": "other"
    },
    {
      "id": "f",
      "user.name": [],
      "message": null
    },
    {
      "id": "g",
      "user.name": "toolongname",
      "message": ""
    },
    {
      "id": "h",
      "user.name": "null"
    },
    {
      "id": "i",
      "user.name": [
        "toolongname",
        "eve"
      ]
    }
  ],
  "context": {}
}
```

```starter
user.name: "__pafta_baslangic__"
```

```test
eq(eslesenler(), ['a'], "girdi korpusunun sabit kimlikleri")
eq(referans('message: "access denied"'), ['a'], "referans sorgunun native sağlaması")
ek = [{'id': 'buyuk', 'message': 'ACCESS denied'}, {'id': 'ters', 'message': 'denied access'}, {'id': 'aralik', 'message': 'access strongly denied'}, {'id': 'devam', 'message': 'access denied later'}, {'id': 'dizi-ayri', 'message': ['access', 'denied']}, {'id': 'dizi-ic', 'message': ['other', 'access denied']}, {'id': 'null', 'message': None}, {'id': 'bos', 'message': ''}]
eq(eslesenler({"documents": ek}), ['buyuk', 'devam', 'dizi-ic'], "değişen belgeler ve yakın karşı örnekler")
eq(eslesenler({"documents": list(reversed(ek))}), ['dizi-ic', 'devam', 'buyuk'], "sonuç girdi sırasını izler")
```

```solution
message: "access denied"
```

```hint
KQL değerini çift tırnağa al; phrase sorgusu oluşur.
```

:::
