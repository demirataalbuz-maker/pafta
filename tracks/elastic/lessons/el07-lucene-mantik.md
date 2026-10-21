---
id: el07
title: Lucene · Dil Seçimi ve Mantık Grupları
summary: Kibana arama dilini doğrula; alan grubunu, AND/OR/NOT kapsamını açık parantezlerle oku.
---

::: anlat Önce hangi dilde olduğunu bil
Kibana sorgu çubuğunda **KQL ile Lucene ayrı seçimlerdir**. Önce arama menüsündeki dili kontrol et. Bu altı ders Lucene sorgu metnini okutur; sağdaki tezgâh Python ile sınırları belirtilmiş okuma görevlerini çalıştırır. Burada Elasticsearch sunucusu, indeksleme ya da genel bir Lucene ayrıştırıcısı yoktur.

`event.outcome:(failure OR unknown)` iki terimi aynı alana bağlar. `AND`, `OR` ve `NOT` işleçlerini büyük harfle yaz. Boşlukla ayrılmış terimlerin davranışını bağlamdan tahmin etme: API'de `default_operator` ayarı bulunur. Örneklerimiz her ilişkiyi açıkça yazar.

```lucene
(event.category:authentication AND event.outcome:(failure OR unknown)) AND (NOT user.name:svc_backup)
```

Bu sorgu bir olay seçer; zaman sırası veya eşik sayımı yapmaz. Kibana zaman filtresi ayrıca uygulanır. Kaynak: [Kibana Lucene seçimi](https://www.elastic.co/docs/explore-analyze/query-filter/languages/lucene-query-syntax).
:::

::: anlat Parantez bir okuma sözleşmesidir
`(A AND B) OR C` ile `A AND (B OR C)` farklı kümeler üretir. Özellikle bir host kısıtını bütün dallara uygulamak istiyorsan host grubunu dışta `AND` ile bağla. Karışık boolean ifadelerde alıştığın programlama dilinin önceliğini Lucene'e taşıma; parantezlerle niyetini yaz.

Bu derste tüm alanlar tek değerli, `keyword` ve normalizersızdır. Dolayısıyla `failure` ile `Failure` farklıdır. Eksik alan bir pozitif terimi sağlamaz. Fakat `NOT user.name:svc_backup` ifadesi, kullanıcı alanı eksik belgeyi kendi başına dışlamaz; pozitif kısıtlar sağlanıyorsa o belge kalabilir. Kullanıcının varlığı da gerekliyse bunu ayrı koşulla istemelisin.

Görevlerde JSON sözlüklerindeki düz ECS alan adlarını okuyacaksın. Bu, yalnızca anlatılan boolean seçim modelidir; analyzer, nested alan, puan veya sorgu ayrıştırma taklidi değildir. Kaynak: [Gruplar ve query_string ayarları](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-query-string-query).
:::

::: tahmin
Aşağıdaki Lucene sorgusunu verilen eşleme, zaman filtresi ve sıralama altında oku. Hangi kimlikler döner? Pafta bu sorguyu Elasticsearch üzerinde çalıştırmaz; cevap, açık veri sözleşmesine göre hazırlanmış okuma cevabıdır.

```lucene
(event.category:authentication AND event.outcome:(failure OR unknown)) AND (NOT user.name:svc_backup)
```

```stdin
{
  "mapping": {
    "event.category": "keyword, normalizer yok",
    "event.outcome": "keyword, normalizer yok",
    "user.name": "keyword, normalizer yok",
    "@timestamp": "date UTC"
  },
  "time_filter": {
    "gte": "2026-10-21T10:00:00Z",
    "lt": "2026-10-21T10:05:00Z"
  },
  "ordering": "id artan; alanlar tek değerli; eksik alan ilgili terimi eşleştirmez",
  "documents": [
    {
      "id": "a",
      "@timestamp": "2026-10-21T10:00:00Z",
      "event.category": "authentication",
      "event.outcome": "failure",
      "user.name": "alice"
    },
    {
      "id": "b",
      "@timestamp": "2026-10-21T10:01:00Z",
      "event.category": "authentication",
      "event.outcome": "unknown",
      "user.name": "svc_backup"
    },
    {
      "id": "c",
      "@timestamp": "2026-10-21T10:02:00Z",
      "event.category": "authentication",
      "event.outcome": "success",
      "user.name": "alice"
    },
    {
      "id": "d",
      "@timestamp": "2026-10-21T10:05:00Z",
      "event.category": "authentication",
      "event.outcome": "failure",
      "user.name": "alice"
    },
    {
      "id": "e",
      "@timestamp": "2026-10-21T10:03:00Z",
      "event.category": "process",
      "event.outcome": "failure"
    },
    {
      "id": "f",
      "@timestamp": "2026-10-21T10:04:00Z",
      "event.category": "authentication"
    },
    {
      "id": "g",
      "@timestamp": "2026-10-21T10:04:30Z",
      "event.category": "authentication",
      "event.outcome": "unknown"
    }
  ]
}
```

```gercek
a
g
```

```test
import json, sys
from datetime import datetime
f = json.load(sys.stdin)
dt = lambda s: datetime.fromisoformat(s.replace("Z", "+00:00"))
bas, son = (dt(f["time_filter"][k]) for k in ("gte", "lt"))
secilen = [d["id"] for d in f["documents"]
           if bas <= dt(d["@timestamp"]) < son
           and d.get("event.category") == "authentication"
           and d.get("event.outcome") in ("failure", "unknown")
           and d.get("user.name") != "svc_backup"]
for kimlik in sorted(secilen):
    print(kimlik)
```

???

`a` ve `g` döner. g kullanıcı alanı eksik olsa da NOT filtresini ihlal etmez. b dışlanmış kullanıcıdır; d zamanın açık üst sınırındadır. Diğerleri pozitif gruplardan birini sağlamaz.
:::

::: gorev Kimlik doğrulama adaylarını oku
`aday_idleri(olaylar, kategori, sonuclar, haric_kullanici)` fonksiyonu kategori eşitliği **ve** izin verilen sonuçlardan birini **ve** dışlanan kullanıcıdan farklı olmayı istesin. Kimlikleri artan döndür. Alanlar tek değerli keyword; eksik kategori/sonuç elenir, eksik kullanıcı dışlamadan geçer. `sonuclar` boşsa sonuç boştur. Zaman filtresi bu göreve dahil değildir.

```starter
def aday_idleri(olaylar, kategori, sonuclar, haric_kullanici):
    return []
```

```test
need("aday_idleri")
olaylar = [
    {"id": "z", "event.category": "auth", "event.outcome": "fail", "user.name": "ali"},
    {"id": "a", "event.category": "auth", "event.outcome": "unknown"},
    {"id": "b", "event.category": "auth", "event.outcome": "fail", "user.name": "yedek"},
    {"id": "c", "event.category": "process", "event.outcome": "fail"},
    {"id": "d", "event.category": "auth", "event.outcome": "success"},
    {"id": "e", "event.category": "auth"},
    {"id": "f", "event.outcome": "fail"},
]
eq(aday_idleri(olaylar, "auth", ["fail", "unknown"], "yedek"), ["a", "z"], "gruplar ve NOT")
eq(aday_idleri(olaylar, "process", ["fail"], "yedek"), ["c"], "kategori parametresi değişti")
eq(aday_idleri(olaylar, "auth", ["success"], "ali"), ["d"], "sonuç parametresi değişti")
eq(aday_idleri(olaylar, "auth", [], "yedek"), [], "boş OR grubu")
eq(aday_idleri([], "auth", ["fail"], "yedek"), [], "boş korpus")
yeni = [{"id": "yeni", "event.category": "vpn", "event.outcome": "blocked", "user.name": "can"}]
eq(aday_idleri(yeni, "vpn", ["blocked"], "svc"), ["yeni"], "sabit cevap yok")
```

```solution
def aday_idleri(olaylar, kategori, sonuclar, haric_kullanici):
    return sorted(d["id"] for d in olaylar
                  if d.get("event.category") == kategori
                  and d.get("event.outcome") in sonuclar
                  and d.get("user.name") != haric_kullanici)
```

```hint
Üç koşulu and ile bağla; sonuç grubu için in, kullanıcı dışlaması için != kullan.
```
:::

::: gorev Host kısıtı bütün dallarda
`host_kapsami(olaylar, hostlar, sonuc, seviye)` şu açık grubu okusun: `(host.name:(izinli hostlar)) AND ((event.outcome:sonuc) OR (alert.level:seviye))`. Kimlikleri artan döndür. Yüksek seviyeli fakat hostu kapsam dışında olay dönmemeli. Bütün alanlar tek değerli keyword; eksikler ilgili terimi sağlamaz.

```starter
def host_kapsami(olaylar, hostlar, sonuc, seviye):
    return []
```

```test
need("host_kapsami")
olaylar = [{"id": "a", "host.name": "web01", "event.outcome": "failure"},
           {"id": "b", "host.name": "web02", "event.outcome": "success", "alert.level": "high"},
           {"id": "c", "host.name": "db01", "alert.level": "high"},
           {"id": "d", "alert.level": "high"},
           {"id": "e", "host.name": "web01", "event.outcome": "success", "alert.level": "low"},
           {"id": "f", "host.name": "web01"}]
eq(host_kapsami(olaylar, ["web01", "web02"], "failure", "high"), ["a", "b"], "host dışındaki OR sızmamalı")
eq(host_kapsami(olaylar, ["db01"], "failure", "high"), ["c"], "host kümesi değişebilir")
eq(host_kapsami(olaylar, ["web01"], "success", "low"), ["e"], "iki dalın parametreleri")
eq(host_kapsami(olaylar, [], "failure", "high"), [], "boş host kapsamı")
eq(host_kapsami([{"id": "r", "host.name": "edge", "alert.level": "critical"}], ["edge"], "denied", "critical"), ["r"], "yeni terimler")
```

```solution
def host_kapsami(olaylar, hostlar, sonuc, seviye):
    return sorted(d["id"] for d in olaylar
                  if d.get("host.name") in hostlar
                  and (d.get("event.outcome") == sonuc or d.get("alert.level") == seviye))
```

```hint
Önce host koşulunu yaz, sonra iki alternatifin tamamını tek parantez içinde tut.
```
:::
