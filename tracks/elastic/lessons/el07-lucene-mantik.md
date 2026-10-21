---
id: el07
title: Lucene · Gerçek Sorgu ve Mantık Grupları
summary: Native Lucene sorguları yaz; alan grubunu, OR varsayımını ve NOT kapsamını test et.
---

::: anlat Kibana dil seçimi ve gerçek motor
Kibana arama çubuğunda KQL ve Lucene ayrı dillerdir. Bu bölümde editöre **Lucene sorgusu** yazarsın; Pafta sorguyu Apache Lucene 9.12.3 QueryParser ile ayrıştırır ve geçici bellek indeksinde çalıştırır. Elasticsearch sunucusu kurulmaz. Phrase, joker, fuzzy ve regex davranışı gerçek Lucene'den gelir; mapping'e göre sayısal/tarih aralıkları, indekslenmiş değer varlığı ve saf NOT seçimi Pafta adaptörünün açık ekleridir.

Bu tezgâhta varsayılan bağlayıcı OR'dur: `host.name:web01 host.name:web02` iki alternatif demektir. Gerçek Elasticsearch query_string isteğinde `default_operator` ayrıca ayarlanabilir. Dersleri başka ortama taşırken bu ayarı doğrula. Alanı olmayan terim ve alan adına joker burada reddedilir; `*:*` bütün belgeleri seçer. Bilinmeyen alanın sessiz boş sonuç vermesi yerine eşlemeyi düzeltmen istenir.

```lucene
host.name:(web01 OR web02) AND event.outcome:failure
```

Sorgu bir belge kümesi seçer. Olay sayısı, zaman sırası ve nedensellik üretmez. [Elastic Lucene arama dili](https://www.elastic.co/docs/explore-analyze/query-filter/languages/lucene-query-syntax), [query_string ayarları](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-query-string-query). Kaynaklar 21 Ekim 2026 tarihinde kontrol edildi.

```meta
dil: lucene
```
:::

::: anlat Parantez ve eksik alanın etkisi
`AND`, `OR`, `NOT` büyük harfle yazılır. `event.outcome:(failure OR unknown)` iki terimi aynı alana bağlar. Bütün hostlarda başarısızlık istemek ile yalnız iki hostta başarısızlık/yüksek seviye istemek farklıdır: host koşulunu alternatiflerin dışına bağla.

Classic QueryParser, AND/OR karışımında programlama dillerinden beklediğin önceliği sağlamaz. Örneğin `A AND B OR C` ifadesini SQL önceliğiyle okuma; `(A AND B) OR C` niyetini açıkça yaz. Testler değişen belge kümelerinde yanlış gruplanan dalları yakalar.

Normalizersız keyword alanı büyük/küçük harfe duyarlıdır. Eksik user.name pozitif kullanıcı terimini sağlamaz; fakat `NOT user.name:svc_backup` dışlamasından geçer. Kullanıcı varlığı da gerekiyorsa `user.name:*` ekle. Saf NOT bu tezgâhta tüm belgelerden çıkarma olarak desteklenir; bu, Lucene çekirdeğinin saf negatif BooleanQuery'sine uygulanan açık adaptör davranışıdır. [Lucene QueryParser söz dizimi](https://lucene.apache.org/core/9_12_3/queryparser/org/apache/lucene/queryparser/classic/package-summary.html).

```meta
dil: lucene
```
:::

::: tahmin
Sorguyu çalıştırmadan önce dönecek kimlikleri sırayla tahmin et. Gerçek Lucene motoru kullanılacak. Context sıralaması yoksa belge giriş sırası korunur; bütün veri aşağıdadır.

```lucene
event.category:authentication AND event.outcome:(failure OR unknown) AND (NOT user.name:svc_backup)
```

```stdin
{
  "dil": "lucene",
  "mapping": {
    "event.category": {
      "type": "keyword"
    },
    "event.outcome": {
      "type": "keyword"
    },
    "user.name": {
      "type": "keyword"
    },
    "host.name": {
      "type": "keyword"
    },
    "alert.level": {
      "type": "keyword"
    }
  },
  "documents": [
    {
      "id": "a",
      "event.category": "authentication",
      "event.outcome": "failure",
      "user.name": "alice"
    },
    {
      "id": "b",
      "event.category": "authentication",
      "event.outcome": "unknown",
      "user.name": "svc_backup"
    },
    {
      "id": "c",
      "event.category": "authentication",
      "event.outcome": "success"
    },
    {
      "id": "d",
      "event.category": "process",
      "event.outcome": "failure"
    },
    {
      "id": "e",
      "event.category": "authentication",
      "event.outcome": "unknown"
    },
    {
      "id": "f",
      "event.category": "authentication"
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
a
e
```

e kullanıcı alanı eksik olsa da dışlanan kullanıcıya eşleşmez. b dışlamaya, c sonuç grubuna, d kategoriye, f eksik sonuca takılır.
:::

::: gorev Kimlik doğrulama adaylarını seç
Yalnız authentication kategorisinde failure veya unknown sonucu olanları seç. svc_backup kullanıcısını çıkar; kullanıcı alanı eksik aday kalabilir.

Editöre yalnız Lucene sorgusu yaz. `stdin` eşlemeyi, belgeleri ve bağımsız zaman/sıralama bağlamını taşır. Testte `eslesenler()` senin sorgunun kimliklerini döndürür; `eslesenler(belge_listesi)` aynı mapping/context ile yeni belgeleri sınar. Python kodu yazman gerekmiyor.

```starter
*:*
```

```stdin
{
  "dil": "lucene",
  "mapping": {
    "event.category": {
      "type": "keyword"
    },
    "event.outcome": {
      "type": "keyword"
    },
    "user.name": {
      "type": "keyword"
    },
    "host.name": {
      "type": "keyword"
    },
    "alert.level": {
      "type": "keyword"
    }
  },
  "documents": [
    {
      "id": "a",
      "event.category": "authentication",
      "event.outcome": "failure",
      "user.name": "alice"
    },
    {
      "id": "b",
      "event.category": "authentication",
      "event.outcome": "unknown",
      "user.name": "svc_backup"
    },
    {
      "id": "c",
      "event.category": "authentication",
      "event.outcome": "success"
    },
    {
      "id": "d",
      "event.category": "process",
      "event.outcome": "failure"
    },
    {
      "id": "e",
      "event.category": "authentication",
      "event.outcome": "unknown"
    },
    {
      "id": "f",
      "event.category": "authentication"
    }
  ],
  "context": {}
}
```

```meta
dil: lucene
```

```test
eq(eslesenler(), ['a', 'e'], "ana korpus")
eq(eslesenler([{'id': 'g', 'event.category': 'authentication', 'event.outcome': 'unknown', 'user.name': 'other'}, {'id': 'h', 'event.category': 'authentication', 'event.outcome': 'failure', 'user.name': 'svc_backup'}, {'id': 'i', 'event.category': 'Authentication', 'event.outcome': 'failure'}, {'id': 'j', 'event.outcome': 'unknown'}]), ['g'], "değişen korpus 1")
eq(eslesenler([{'id': 'z', 'event.category': 'authentication', 'event.outcome': ['success', 'failure']}, {'id': 'y', 'event.category': 'authentication', 'event.outcome': 'success'}]), ['z'], "değişen korpus 2")
```

```solution
event.category:authentication AND event.outcome:(failure OR unknown) AND (NOT user.name:svc_backup)
```

```hint
Kategori AND sonuç grubu AND parantezli NOT yaz. Keyword dizisinin herhangi bir değeri terimi sağlayabilir.
```
:::

::: gorev Host kısıtını iki dala uygula
Yalnız web01 veya web02 hostlarını al. Bu kapsam içinde event.outcome failure VEYA alert.level high yeterli olsun. Kapsam dışındaki high olayını alma. Eksik host da kapsam dışıdır.

Editöre yalnız Lucene sorgusu yaz. `stdin` eşlemeyi, belgeleri ve bağımsız zaman/sıralama bağlamını taşır. Testte `eslesenler()` senin sorgunun kimliklerini döndürür; `eslesenler(belge_listesi)` aynı mapping/context ile yeni belgeleri sınar. Python kodu yazman gerekmiyor.

```starter
*:*
```

```stdin
{
  "dil": "lucene",
  "mapping": {
    "event.category": {
      "type": "keyword"
    },
    "event.outcome": {
      "type": "keyword"
    },
    "user.name": {
      "type": "keyword"
    },
    "host.name": {
      "type": "keyword"
    },
    "alert.level": {
      "type": "keyword"
    }
  },
  "documents": [
    {
      "id": "a",
      "host.name": "web01",
      "event.outcome": "failure"
    },
    {
      "id": "b",
      "host.name": "web02",
      "alert.level": "high"
    },
    {
      "id": "c",
      "host.name": "db01",
      "alert.level": "high"
    },
    {
      "id": "d",
      "host.name": "web01",
      "alert.level": "low"
    },
    {
      "id": "e",
      "alert.level": "high"
    }
  ],
  "context": {}
}
```

```meta
dil: lucene
```

```test
eq(eslesenler(), ['a', 'b'], "ana korpus")
eq(eslesenler([{'id': 'x', 'host.name': 'web02', 'event.outcome': 'success', 'alert.level': 'high'}, {'id': 'y', 'host.name': 'other', 'event.outcome': 'failure'}, {'id': 'z', 'host.name': 'web01', 'event.outcome': 'Failure'}]), ['x'], "değişen korpus 1")
eq(eslesenler([{'id': 'n', 'host.name': ['db01', 'web01'], 'event.outcome': 'failure'}, {'id': 'm', 'host.name': 'WEB01', 'alert.level': 'high'}]), ['n'], "değişen korpus 2")
```

```solution
host.name:(web01 OR web02) AND (event.outcome:failure OR alert.level:high)
```

```hint
Host grubunu AND ile bütün alternatif parantezine bağla.
```
:::
