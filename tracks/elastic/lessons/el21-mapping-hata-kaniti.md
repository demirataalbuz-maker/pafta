---
id: el21
title: Mapping ve Hata Kanıtı
summary: Simülasyon, strict mapping, taşma ve eksik zamanı birbirinden ayır.
---

::: anlat Gerçek ürün üzerinde çalışma
Bir ingest işlemcisinin başarısı ile indeksleme başarısı ayrı aşamalardır.
`dynamic: strict` bilinmeyen alanı reddeder; sayılarda `coerce: false` metni
kendiliğinden sayıya çevirmeyi kapatır. Bu tezgahın mapping çeviricisi bu
ayarları gerçek indekse yazar. Örneğin yalnız `set n="7"` simülasyonda
başarılı olabilir, fakat integer mapping bunu bulk aşamasında reddeder.

`on_failure` ingest hatasını yakalar; daha sonra oluşan mapping hatasını
yakalamaz. Hatayı sessizce yok etmek yerine ham alanı koruyup bu dersin
başarısız ayrıştırma kaydını `event.outcome: failure` ile işaretle. Başarılı
olaylara bu işareti koyma. Büyük/küçük sayı sınırları gerçek `integer`
aralığıdır. `date` işlemcisi zaman dilimini çözer; iki farklı saat metni aynı
anı gösterebilir. Tarih alanının yokluğu, geçersiz takvim günü ve artık yıl
ayrı test tanıklarıdır. Bu kayıtlar süreç telemetrisi değil ayrıştırma sınırı
için üretilmiş sentetik tanıklardır.

Bu bölüm **gerçek Elasticsearch/Kibana 9.5.5, Basic lisansı** kullanır; önce
[yerel laboratuvar yönergesini](../README.md) uygula. Girdi kutusunda
`backend: elastic` görünür. Önceki Lucene/yerel EQL motoruna sessiz dönüş yoktur.
Her çalıştırma yeni bir geçici indeks kullanır, iş bitince onu siler. Girdideki
`documents` ders tanıklarıdır; sorgu veya pipeline kodu editörde yazılır.
Alan adı, tür, eksik alan ve zaman aralığı sözleşmenin parçasıdır.

Kaynaklar: [Convert](https://www.elastic.co/docs/reference/enrich-processor/convert-processor), [Date](https://www.elastic.co/docs/reference/enrich-processor/date-processor), [Dynamic mapping](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/dynamic).
:::

::: tahmin Önce çıktıyı düşün
Taşan sayı ve sözcük on_failure ile neye dönüşür?

```meta
dil: ingest
timeout: 60
```

```ingest
{
  "processors": [
    {
      "convert": {
        "field": "raw",
        "target_field": "n",
        "type": "integer"
      }
    }
  ],
  "on_failure": [
    {
      "set": {
        "field": "event.outcome",
        "value": "failure"
      }
    }
  ]
}
```

```stdin
{"backend":"elastic","dil":"ingest","mapping":{"raw":"keyword","n":"integer","event.outcome":"keyword"},"documents":[{"id":"a","raw":"-2147483648"},{"id":"b","raw":"2147483647"},{"id":"c","raw":"2147483648"},{"id":"d","raw":"oops"}]}
```

???
Gerçek API ile doğrulanmış çıktı:

```text
{"documents":[{"id":"a","n":-2147483648,"raw":"-2147483648"},{"id":"b","n":2147483647,"raw":"2147483647"},{"event":{"outcome":"failure"},"id":"c","raw":"2147483648"},{"event":{"outcome":"failure"},"id":"d","raw":"oops"}],"items":[{"error":null,"id":"a","status":201},{"error":null,"id":"b","status":201},{"error":null,"id":"c","status":201},{"error":null,"id":"d","status":201}],"simulation":[{"source":{"id":"a","n":-2147483648,"raw":"-2147483648"}},{"source":{"id":"b","n":2147483647,"raw":"2147483647"}},{"source":{"event":{"outcome":"failure"},"id":"c","raw":"2147483648"}},{"source":{"event":{"outcome":"failure"},"id":"d","raw":"oops"}}]}
```

:::

::: gorev 32 bit sayı ve hata izi
raw metnini integer n alanına çevir; raw kalsın. Çevrilemeyenlerde n olmasın ve event.outcome failure olsun; geçerli sayı hataya işaretlenmesin.

```meta
dil: ingest
timeout: 60
```

```stdin
{"backend":"elastic","dil":"ingest","mapping":{"raw":"keyword","n":"integer","event.outcome":"keyword"},"documents":[{"id":"a","raw":"-2147483648"},{"id":"b","raw":"2147483647"},{"id":"c","raw":"2147483648"},{"id":"d","raw":"oops"}]}
```

```starter
{
  "processors": []
}
```

```test
r=sonuc()
eq([i['status'] for i in r['items']], [201]*4, 'on_failure ile bozuk girdi de izlenebilir')
eq([d.get('n') for d in r['documents']], [-2147483648,2147483647,None,None], 'integer iki ucu, taşma ve sözcük')
eq([alan(d,'event.outcome') for d in r['documents']], [None,None,'failure','failure'], 'yalnız hatalı girdiye failure')
eq([d['raw'] for d in r['documents']], ['-2147483648','2147483647','2147483648','oops'], 'ham kanıt korunur')
aday=[{'id':str(i),'raw':str(v)} for i,v in enumerate([-2147483649,-1,0,1,2147483646])]
r=sonuc(aday)
eq([d.get('n') for d in r['documents']], [None,-1,0,1,2147483646], 'alt taşma ve sıfır sınırı')
eq([alan(d,'event.outcome') for d in r['documents']], ['failure',None,None,None,None], 'başarı hataya karışmaz')
```

```solution
{
  "processors": [
    {
      "convert": {
        "field": "raw",
        "target_field": "n",
        "type": "integer"
      }
    }
  ],
  "on_failure": [
    {
      "set": {
        "field": "event.outcome",
        "value": "failure"
      }
    }
  ]
}
```

```hint
convert integer; pipeline on_failure içinde set.
```

:::

::: gorev Zaman dilimi ve tarih hatası
raw tarihini UTC @timestamp alanına ISO8601 olarak dönüştür. Çıktı yyyy-MM-ddTHH:mm:ss.SSSZ biçiminde olsun. Eksik/geçersiz tarihte event.outcome failure ve @timestamp yok; raw korunur.

```meta
dil: ingest
timeout: 60
```

```stdin
{"backend":"elastic","dil":"ingest","mapping":{"raw":"keyword","@timestamp":"date","event.outcome":"keyword"},"documents":[{"id":"a","raw":"2026-01-01T00:00:00Z"},{"id":"b","raw":"2026-01-01T03:00:00+03:00"},{"id":"c","raw":"2026-02-30T00:00:00Z"},{"id":"d"}]}
```

```starter
{
  "processors": []
}
```

```test
r=sonuc()
eq([i['status'] for i in r['items']], [201]*4, 'hatalı tarih kaydı kaybolmaz')
eq([d.get('@timestamp') for d in r['documents']], ['2026-01-01T00:00:00.000Z','2026-01-01T00:00:00.000Z',None,None], 'aynı an, geçersiz gün, alan yokluğu')
eq([alan(d,'event.outcome') for d in r['documents']], [None,None,'failure','failure'], 'başarıya yanlış failure verilmez')
r=sonuc([{'id':'a','raw':'2024-02-29T00:00:00Z'},{'id':'b','raw':'2025-02-29T00:00:00Z'},{'id':'c','raw':'2026-01-01T00:00:00.001Z'}])
eq([d.get('@timestamp') for d in r['documents']], ['2024-02-29T00:00:00.000Z',None,'2026-01-01T00:00:00.001Z'], 'artık yıl ve milisaniye')
```

```solution
{
  "processors": [
    {
      "date": {
        "field": "raw",
        "target_field": "@timestamp",
        "formats": [
          "ISO8601"
        ],
        "output_format": "yyyy-MM-dd'T'HH:mm:ss.SSSXXX"
      }
    }
  ],
  "on_failure": [
    {
      "set": {
        "field": "event.outcome",
        "value": "failure"
      }
    }
  ]
}
```

```hint
date formats [ISO8601], target_field @timestamp, on_failure set.
```

:::
