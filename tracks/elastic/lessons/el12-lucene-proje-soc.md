---
id: el12
title: Proje · Lucene ile SOC Aday Kümesi
summary: Kapsam, indeks semantiği ve bağlamı tek sorguda birleştir; alternatif korpuslarda niyetini koru.
---

::: anlat Önce seçimin sözleşmesini yaz
Bir SOC filtresini yalnız sorgu metniyle teslim etmek eksiktir. Kullanılan dil, alan türleri, analyzer/normalizer, zaman penceresi ve çıktı sırası sonuç üzerinde etkilidir. Bu projede corpus dil:lucene der; keyword alanları normalizersız, message standard text, risk.score long ve @timestamp date'dir. Zaman bağlamı verilmişse önce o pencere, sonra native sorgu uygulanır.

İlk seçim yalnız edge01/edge02 hostlarında authentication olaylarını ister. failure veya unknown kabul edilir; risk en az 70 olmalıdır. svc_ önekli bir kullanıcı değeri varsa belge çıkarılır. Kullanıcı alanı eksik bir belgenin kalması, bu açık sözleşmenin sonucudur; onun insan hesabına ait olduğunu kanıtlamaz.

```lucene
event.category:authentication AND host.name:(edge01 OR edge02) AND event.outcome:(failure OR unknown) AND risk.score:[70 TO *] AND (NOT user.name:svc_*)
```

Bu bir aday filtreleme projesidir. Eşik sayımı, farklı olayları ilişkilendirme, alarm yayınlama veya otomatik engelleme yapmaz. Bulguyu başka bir kaynaktan doğrulama sonraki inceleme adımıdır. [Elastic query_string](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-query-string-query). Kaynaklar 21 Ekim 2026 tarihinde kontrol edildi.

```meta
dil: lucene
```
:::

::: anlat Sınırı ve kapsamı değiştirerek doğrula
Doğru sonuçlu bir korpus tek başına güçlü kanıt değildir. Alt eşikten bir eksik, tam eşik, üst uç, eksik alan, kapsam dışı host ve ters phrase sırası gibi tanıklar yaz. İkinci görev bunları birlikte kullanır: 50 dahil/80 hariç risk, lab01 hostu, process kategorisi ve en fazla bir konum hareketli policy denied phrase.

context.time_filter UTC 10:00 dahil ile 10:05 hariç penceredir. Bu, sorgu metnine eklenmiş gizli bir koşul değildir; veri bağlamında açıkça gösterilir. Sorgun bağlam dışında kalan olayı geri getiremez. Testte alternatif belge listesi verilmesi mapping ve context'i korur. context.sort id artan seçtiği için belgeler giriş sırası karıştırılsa da rapor sırası kararlı kalır.

Pafta'nın bellek indeksi sorgu üyeliğini doğrular. Gerçek dağıtık Elasticsearch indeksinin performansını, shard davranışını, puanını veya Kibana saved-search API'sini ölçmez. Gerçek ortamda aynı analyzer ve alan seçeneklerini doğrulayıp kontrollü bir veri kümesiyle sorguyu tekrar sınamalısın. [Kibana filtreleme ve zaman seçimi](https://www.elastic.co/docs/explore-analyze/query-filter/filtering), [Lucene QueryParser](https://lucene.apache.org/core/9_12_3/queryparser/org/apache/lucene/queryparser/classic/QueryParser.html).

```meta
dil: lucene
```
:::

::: tahmin
Sorguyu çalıştırmadan önce dönecek kimlikleri sırayla tahmin et. Gerçek Lucene motoru kullanılacak. Context sıralaması yoksa belge giriş sırası korunur; bütün veri aşağıdadır.

```lucene
event.category:authentication AND host.name:(edge01 OR edge02) AND event.outcome:(failure OR unknown) AND risk.score:[70 TO *] AND (NOT user.name:svc_*)
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
    "host.name": {
      "type": "keyword"
    },
    "user.name": {
      "type": "keyword"
    },
    "message": {
      "type": "text"
    },
    "risk.score": {
      "type": "long"
    },
    "@timestamp": {
      "type": "date"
    }
  },
  "documents": [
    {
      "id": "a",
      "event.category": "authentication",
      "event.outcome": "failure",
      "host.name": "edge01",
      "user.name": "alice",
      "risk.score": 70
    },
    {
      "id": "b",
      "event.category": "authentication",
      "event.outcome": "unknown",
      "host.name": "edge02",
      "risk.score": 90
    },
    {
      "id": "c",
      "event.category": "authentication",
      "event.outcome": "failure",
      "host.name": "edge03",
      "risk.score": 90
    },
    {
      "id": "d",
      "event.category": "authentication",
      "event.outcome": "failure",
      "host.name": "edge01",
      "user.name": "svc_job",
      "risk.score": 99
    },
    {
      "id": "e",
      "event.category": "process",
      "event.outcome": "failure",
      "host.name": "edge01",
      "risk.score": 90
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
b
```

70 alt sınırı dahildir. b kullanıcı alanı eksik olduğu için svc_ terimine eşleşmez. c host kapsamı, d dışlama, e kategori nedeniyle elenir.
:::

::: gorev İnceleme için kimlik doğrulama adayları
Authentication kategorisi, edge01 veya edge02 hostu, failure veya unknown sonucu ve en az 70 risk iste. svc_ ile başlayan herhangi bir kullanıcı değeri varsa belgeyi çıkar. Başka kısıt ekleme.

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
    "host.name": {
      "type": "keyword"
    },
    "user.name": {
      "type": "keyword"
    },
    "message": {
      "type": "text"
    },
    "risk.score": {
      "type": "long"
    },
    "@timestamp": {
      "type": "date"
    }
  },
  "documents": [
    {
      "id": "a",
      "event.category": "authentication",
      "event.outcome": "failure",
      "host.name": "edge01",
      "user.name": "alice",
      "risk.score": 70
    },
    {
      "id": "b",
      "event.category": "authentication",
      "event.outcome": "unknown",
      "host.name": "edge02",
      "risk.score": 90
    },
    {
      "id": "c",
      "event.category": "authentication",
      "event.outcome": "failure",
      "host.name": "edge03",
      "risk.score": 90
    },
    {
      "id": "d",
      "event.category": "authentication",
      "event.outcome": "failure",
      "host.name": "edge01",
      "user.name": "svc_job",
      "risk.score": 99
    },
    {
      "id": "e",
      "event.category": "process",
      "event.outcome": "failure",
      "host.name": "edge01",
      "risk.score": 90
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
eq(eslesenler([{'id': 'x', 'event.category': 'authentication', 'host.name': 'edge01', 'event.outcome': 'failure', 'risk.score': 69}, {'id': 'y', 'event.category': 'authentication', 'host.name': 'edge02', 'event.outcome': 'unknown', 'risk.score': 70}, {'id': 'z', 'event.category': 'authentication', 'host.name': 'other', 'event.outcome': 'failure', 'risk.score': 100}, {'id': 'w', 'event.category': 'authentication', 'host.name': 'edge01', 'event.outcome': 'success', 'risk.score': 100}]), ['y'], "değişen korpus 1")
eq(eslesenler([{'id': 'p', 'event.category': 'authentication', 'host.name': 'edge01', 'event.outcome': 'failure', 'risk.score': 71, 'user.name': ['alice', 'svc_x']}, {'id': 'q', 'event.category': 'authentication', 'host.name': 'edge01', 'event.outcome': 'failure', 'risk.score': 71}, {'id': 'r', 'event.category': 'authentication', 'host.name': 'edge01', 'event.outcome': 'failure'}]), ['q'], "değişen korpus 2")
```

```solution
event.category:authentication AND host.name:(edge01 OR edge02) AND event.outcome:(failure OR unknown) AND risk.score:[70 TO *] AND (NOT user.name:svc_*)
```

```hint
Beş ana grubu AND ile birleştir. Host ve sonuç için OR alan grubu, risk için açık üst uç kullan.
```
:::

::: gorev Proje: zaman bağlamında metinli süreç adayları
Verilen context zaman filtresi ve id artan sıralamasını koruyarak process kategorisini ve lab01 hostunu seç. message içinde policy denied phrase slop1 olsun; risk.score 50 dahil/80 hariç olsun; svc_ kullanıcılarını çıkar. Eksik kullanıcı kalabilir. Zaman koşulunu ayrıca sorguya kopyalaman gerekmiyor.

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
    "host.name": {
      "type": "keyword"
    },
    "user.name": {
      "type": "keyword"
    },
    "message": {
      "type": "text"
    },
    "risk.score": {
      "type": "long"
    },
    "@timestamp": {
      "type": "date"
    }
  },
  "documents": [
    {
      "id": "a",
      "@timestamp": "2026-10-21T10:00:00Z",
      "event.category": "process",
      "host.name": "lab01",
      "message": "policy denied",
      "risk.score": 50
    },
    {
      "id": "b",
      "@timestamp": "2026-10-21T10:04:59.999Z",
      "event.category": "process",
      "host.name": "lab01",
      "message": "policy remotely denied",
      "risk.score": 79
    },
    {
      "id": "c",
      "@timestamp": "2026-10-21T10:05:00Z",
      "event.category": "process",
      "host.name": "lab01",
      "message": "policy denied",
      "risk.score": 60
    },
    {
      "id": "d",
      "@timestamp": "2026-10-21T10:01:00Z",
      "event.category": "process",
      "host.name": "lab01",
      "message": "denied policy",
      "risk.score": 60
    },
    {
      "id": "e",
      "@timestamp": "2026-10-21T10:01:00Z",
      "event.category": "process",
      "host.name": "lab02",
      "message": "policy denied",
      "risk.score": 60
    }
  ],
  "context": {
    "time_filter": {
      "field": "@timestamp",
      "gte": "2026-10-21T10:00:00Z",
      "lt": "2026-10-21T10:05:00Z"
    },
    "sort": [
      [
        "id",
        "asc"
      ]
    ]
  }
}
```

```meta
dil: lucene
```

```test
eq(eslesenler(), ['a', 'b'], "ana korpus")
eq(eslesenler([{'id': 'z', '@timestamp': '2026-10-21T10:04:59.999Z', 'event.category': 'process', 'host.name': 'lab01', 'message': 'policy denied', 'risk.score': 79}, {'id': 'a', '@timestamp': '2026-10-21T10:00:00Z', 'event.category': 'process', 'host.name': 'lab01', 'message': 'policy remote denied', 'risk.score': 50}, {'id': 'b', '@timestamp': '2026-10-21T10:00:00Z', 'event.category': 'process', 'host.name': 'lab01', 'message': 'policy denied', 'risk.score': 80}, {'id': 'c', '@timestamp': '2026-10-21T09:59:59.999Z', 'event.category': 'process', 'host.name': 'lab01', 'message': 'policy denied', 'risk.score': 60}]), ['a', 'z'], "değişen korpus 1")
eq(eslesenler([{'id': 'p', '@timestamp': '2026-10-21T10:01:00Z', 'event.category': 'process', 'host.name': 'lab01', 'message': 'policy denied', 'risk.score': 49}, {'id': 'q', '@timestamp': '2026-10-21T10:01:00Z', 'event.category': 'process', 'host.name': 'lab01', 'message': 'policy denied', 'risk.score': 51, 'user.name': 'svc_job'}, {'id': 'r', '@timestamp': '2026-10-21T10:01:00Z', 'event.category': 'process', 'host.name': 'lab01', 'message': ['policy', 'denied'], 'risk.score': 51}, {'id': 's', '@timestamp': '2026-10-21T10:01:00Z', 'event.category': 'network', 'host.name': 'lab01', 'message': 'policy denied', 'risk.score': 51}]), [], "değişen korpus 2")
```

```solution
event.category:process AND host.name:lab01 AND message:"policy denied"~1 AND risk.score:[50 TO 80} AND (NOT user.name:svc_*)
```

```hint
Phrase ~1, risk [50 TO 80} ve NOT svc_* koşullarını iki kapsam koşuluyla AND yap.
```
:::
