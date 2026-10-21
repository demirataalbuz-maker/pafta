---
id: el08
title: Lucene · Sayı ve UTC Aralıkları
summary: Açık/kapalı uçları native sayısal noktalarda ve milisaniyelik tarihlerde uygula.
---

::: anlat Köşeli ve süslü parantez ayrı sözleşmelerdir
Sayısal mapping, metin sıralaması yerine gerçek sayısal karşılaştırma sağlar. `event.code:[100 TO 200]` iki ucu da alır; `{100 TO 200}` ikisini dışlar. Karışık `[100 TO 200}` altı dahil, üstü hariçtir. `TO` büyük harfle yazılır. `*` açık uçtur: `event.code:[100 TO *]` 100 ve üstüdür. Mapping keyword olsaydı aralık terimlerin sözlük sırasına göre değerlendirilirdi; aynı metnin türünü değiştirmek sonucu değiştirebilir.

```lucene
event.code:[100 TO 200}
```

Eksik/null sayı koşulu sağlamaz. Sıfır ve negatifler geçerli sayılardır. Bu tezgâhta integer/long belgeleri tamsayı JSON sayısı olmalı; sayı metni sessizce dönüştürülmez. long değerleri 64 bit tamsayı noktalarıyla tutulur; 2^53 civarında kayan nokta yuvarlaması uygulanmaz. Aralık ucu yazarken birimi de bil: byte, saniye veya olay kodu aynı sayı tipinde olabilir ama aynı anlama gelmez. [Elastic aralık söz dizimi](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-query-string-query#query-string-syntax). Kaynaklar 21 Ekim 2026 tarihinde kontrol edildi.

```meta
dil: lucene
```
:::

::: anlat Tarih sorgusu ve bağımsız zaman bağlamı
date alanında tam ISO timestamp ve açık saat dilimi kullan: `"2026-10-21T10:00:00.000Z"`. Sondaki Z UTC'dir; `13:00:00+03:00` aynı anda `10:00:00Z` olur. Belgeler epoch_millis tamsayısı da taşıyabilir. Bu tezgâh tarih metninde en çok üç kesir hanesi kabul eder; kısmi tarih, sayısal tarih metni ve now-15m gibi tarih matematiğini açık hatayla reddeder. Elasticsearch'ün tüm tarih formatları ve yuvarlama seçenekleri burada taklit edilmez.

```lucene
@timestamp:["2026-10-21T10:00:00Z" TO "2026-10-21T10:05:00Z"}
```

Kibana zaman seçimi sorgu çubuğunun dışındadır. Pafta'da context.time_filter önce uygulanır; sorgudaki aralıkla kesişir. context.sort yoksa kimlikler giriş sırasında döner. Bir pencereyi beş dakika diye anlatmak yeterli değildir: başlangıç dahil mi, bitiş hariç mi ve saat dilimi ne, belirt. [Elastic tarih alanı](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/date), [Kibana zaman filtresi](https://www.elastic.co/docs/explore-analyze/query-filter/filtering).

```meta
dil: lucene
```
:::

::: tahmin
Sorguyu çalıştırmadan önce dönecek kimlikleri sırayla tahmin et. Gerçek Lucene motoru kullanılacak. Context sıralaması yoksa belge giriş sırası korunur; bütün veri aşağıdadır.

```lucene
event.code:[100 TO 200}
```

```stdin
{
  "dil": "lucene",
  "mapping": {
    "event.code": {
      "type": "long"
    },
    "@timestamp": {
      "type": "date"
    },
    "host.name": {
      "type": "keyword"
    }
  },
  "documents": [
    {
      "id": "a",
      "event.code": 99
    },
    {
      "id": "b",
      "event.code": 100
    },
    {
      "id": "c",
      "event.code": 199
    },
    {
      "id": "d",
      "event.code": 200
    },
    {
      "id": "e",
      "event.code": -1
    },
    {
      "id": "f"
    }
  ],
  "context": {}
}
```

```meta
dil: lucene
```

???

Çıktı:

```text
b
c
```

100 dahil, 200 hariçtir; 99 alt sınırdan düşer. Eksik alan ve negatif sayı da koşulu sağlamaz.
:::

::: gorev Yarı açık sayısal pencere
event.code için 100 dahil, 200 hariç aralığını yaz. Başka alan kısıtı ekleme.

Editöre yalnız Lucene sorgusu yaz. `stdin` eşlemeyi, belgeleri ve bağımsız zaman/sıralama bağlamını taşır. Testte `eslesenler()` senin sorgunun kimliklerini döndürür; `eslesenler(belge_listesi)` aynı mapping/context ile yeni belgeleri sınar. Python kodu yazman gerekmiyor.

```starter
*:*
```

```stdin
{
  "dil": "lucene",
  "mapping": {
    "event.code": {
      "type": "long"
    },
    "@timestamp": {
      "type": "date"
    },
    "host.name": {
      "type": "keyword"
    }
  },
  "documents": [
    {
      "id": "a",
      "event.code": 99
    },
    {
      "id": "b",
      "event.code": 100
    },
    {
      "id": "c",
      "event.code": 199
    },
    {
      "id": "d",
      "event.code": 200
    },
    {
      "id": "e",
      "event.code": -1
    },
    {
      "id": "f"
    }
  ],
  "context": {}
}
```

```meta
dil: lucene
```

```test
eq(eslesenler(), ['b', 'c'], "ana korpus")
eq(eslesenler([{'id': 'a', 'event.code': 100}, {'id': 'b', 'event.code': 101}, {'id': 'c', 'event.code': 200}, {'id': 'd', 'event.code': 0}, {'id': 'e', 'event.code': -100}]), ['a', 'b'], "değişen korpus 1")
eq(eslesenler([{'id': 'u', 'event.code': 199}, {'id': 'v', 'event.code': [99, 150]}, {'id': 'w', 'event.code': 201}, {'id': 'x', 'event.code': None}]), ['u', 'v'], "değişen korpus 2")
```

```solution
event.code:[100 TO 200}
```

```hint
Karışık köşeli/süslü parantez, tam istenen iki sınırı ifade eder.
```
:::

::: gorev UTC başlangıcı dahil, bitişi hariç
@timestamp alanı 21 Ekim 2026 10:00:00Z dahil ile 10:05:00Z hariç arasında olsun. Başka filtre istemiyoruz. Milisaniye ve +03:00 eşdeğerini doğru ele al.

Editöre yalnız Lucene sorgusu yaz. `stdin` eşlemeyi, belgeleri ve bağımsız zaman/sıralama bağlamını taşır. Testte `eslesenler()` senin sorgunun kimliklerini döndürür; `eslesenler(belge_listesi)` aynı mapping/context ile yeni belgeleri sınar. Python kodu yazman gerekmiyor.

```starter
*:*
```

```stdin
{
  "dil": "lucene",
  "mapping": {
    "event.code": {
      "type": "long"
    },
    "@timestamp": {
      "type": "date"
    },
    "host.name": {
      "type": "keyword"
    }
  },
  "documents": [
    {
      "id": "a",
      "@timestamp": "2026-10-21T09:59:59.999Z"
    },
    {
      "id": "b",
      "@timestamp": "2026-10-21T10:00:00Z"
    },
    {
      "id": "c",
      "@timestamp": "2026-10-21T10:04:59.999Z"
    },
    {
      "id": "d",
      "@timestamp": "2026-10-21T10:05:00Z"
    }
  ],
  "context": {}
}
```

```meta
dil: lucene
```

```test
eq(eslesenler(), ['b', 'c'], "ana korpus")
eq(eslesenler([{'id': 'x', '@timestamp': '2026-10-21T13:00:00+03:00'}, {'id': 'y', '@timestamp': '2026-10-21T13:05:00+03:00'}, {'id': 'z', '@timestamp': '2026-10-21T10:00:00.001Z'}]), ['x', 'z'], "değişen korpus 1")
eq(eslesenler([{'id': 'p', '@timestamp': '2026-10-21T09:59:59.999Z'}, {'id': 'q', '@timestamp': None}, {'id': 'r'}]), [], "değişen korpus 2")
```

```solution
@timestamp:["2026-10-21T10:00:00Z" TO "2026-10-21T10:05:00Z"}
```

```hint
Tarih değerlerini çift tırnakla yaz; alt uç [ ve üst uç } olsun.
```
:::
