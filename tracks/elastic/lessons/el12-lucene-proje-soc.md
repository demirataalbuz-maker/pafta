---
id: el12
title: Proje · Lucene ile SOC İncelemesini Okumak
summary: Sorgu, eşleme, zaman filtresi ve yanıt bütünlüğünü tek inceleme sözleşmesinde birleştir.
---

::: anlat Sorgu çubuğundan API gövdesine
İnceleme amacı: analyst önekli hesapların başarısız kimlik doğrulama olaylarını sabit bir zaman aralığında görmek. Bu sorgu tek olayları seçer; art arda denemeyi veya saldırgan niyetini kanıtlamaz. Davranış korelasyonunu sonraki EQL bölümünde ayrıca okuyacaksın.

```lucene
(event.category:authentication AND event.outcome:failure) AND user.name:analyst*
```

Arama API'sinde sorgu metni `query_string.query` değeridir. Kibana zaman filtresini otomatik var sayma: hazırlanan gövdede `bool.filter` içinde ayrı `range` yaz. Görevde `default_operator` açıkça AND, `lenient` false; fakat gösterilen örnek zaten açık işleçlidir. JSON nesnesi üretmek HTTP isteği göndermek değildir. Bu derste ağ çağrısı yapılmaz. Kaynak: [query_string API](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-query-string-query).
:::

::: anlat Sıralama ve bütünlük bir bulgunun parçasıdır
Aynı damgalı iki olay varsa ikinci bir benzersiz sıralama alanı kullan. Bu fixture event.id keyword alanını bu amaçla tanımlar. Elasticsearch `_id` metadata alanını gelişigüzel sıralama alanı saymıyoruz. Query sonucundaki sıralama ile “ilk saldırı” gibi analitik bir sonuç arasında ayrıca veri kapsamı vardır.

Yanıtta `hits.hits` dönen sayfadır; `hits.total.value` toplam sayısı olabilir ve `relation:gte` yalnız alt sınır bildirebilir. Başarılı, kesin toplamlı bir arama bile size nedeniyle bütün hitleri döndürmemiş olabilir. Zaman aşımı ve başarısız shard varsa kısmi sonuçları “hiç olay yok” diye raporlama.

İlk görev yalnız istek sözlüğü hazırlar. İkinci görev sunucudan geldiği varsayılan bir JSON yanıtının kesin toplam, sayfa ve tamamlanma durumunu okur. Yerel testlerin geçmesi native Elasticsearch sorgusunun doğrulandığı anlamına gelmez. Kaynak: [arama isteği ve yanıtı](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-search).
:::

::: tahmin
Aşağıdaki Lucene sorgusunu verilen eşleme, zaman filtresi ve sıralama altında oku. Hangi kimlikler döner? Pafta bu sorguyu Elasticsearch üzerinde çalıştırmaz; cevap, açık veri sözleşmesine göre hazırlanmış okuma cevabıdır.

```lucene
(event.category:authentication AND event.outcome:failure) AND user.name:analyst*
```

```stdin
{
  "mapping": {
    "event.category": "keyword normalizer yok",
    "event.outcome": "keyword normalizer yok",
    "user.name": "keyword normalizer yok",
    "event.id": "keyword benzersiz",
    "@timestamp": "date UTC"
  },
  "time_filter": {
    "gte": "2026-10-21T10:00:00.000Z",
    "lt": "2026-10-21T10:05:00.000Z"
  },
  "ordering": "@timestamp artan, eşitlikte event.id artan; çıktı event.id",
  "documents": [
    {
      "event.id": "z",
      "@timestamp": "2026-10-21T10:00:00.000Z",
      "event.category": "authentication",
      "event.outcome": "failure",
      "user.name": "analyst1"
    },
    {
      "event.id": "b",
      "@timestamp": "2026-10-21T10:02:00.000Z",
      "event.category": "authentication",
      "event.outcome": "failure",
      "user.name": "analyst2"
    },
    {
      "event.id": "a",
      "@timestamp": "2026-10-21T10:02:00.000Z",
      "event.category": "authentication",
      "event.outcome": "failure",
      "user.name": "analyst"
    },
    {
      "event.id": "c",
      "@timestamp": "2026-10-21T10:03:00.000Z",
      "event.category": "authentication",
      "event.outcome": "success",
      "user.name": "analyst3"
    },
    {
      "event.id": "d",
      "@timestamp": "2026-10-21T10:05:00.000Z",
      "event.category": "authentication",
      "event.outcome": "failure",
      "user.name": "analyst4"
    },
    {
      "event.id": "e",
      "@timestamp": "2026-10-21T10:01:00.000Z",
      "event.category": "authentication",
      "event.outcome": "failure",
      "user.name": "Analyst5"
    },
    {
      "event.id": "f",
      "@timestamp": "2026-10-21T10:01:00.000Z",
      "event.category": "process",
      "event.outcome": "failure",
      "user.name": "analyst6"
    },
    {
      "event.id": "g",
      "@timestamp": "2026-10-21T10:01:00.000Z",
      "event.category": "authentication",
      "event.outcome": "failure"
    }
  ]
}
```

```gercek
z
a
b
```

```test
import json, sys
from datetime import datetime
f = json.load(sys.stdin)
dt = lambda s: datetime.fromisoformat(s.replace("Z", "+00:00"))
bas, son = (dt(f["time_filter"][k]) for k in ("gte", "lt"))
rows = [d for d in f["documents"] if d.get("event.category") == "authentication"
        and d.get("event.outcome") == "failure"
        and isinstance(d.get("user.name"), str) and d["user.name"].startswith("analyst")
        and bas <= dt(d["@timestamp"]) < son]
for d in sorted(rows, key=lambda d: (dt(d["@timestamp"]), d["event.id"])):
    print(d["event.id"])
```

???

`z`, sonra aynı zamandaki `a` ve `b` döner. analyst* boş son eki de kabul eder. d zaman üst sınırında; e normalizersız eşlemede harf farkıyla elenir. Diğerleri kategori, sonuç veya kullanıcı şartını sağlamaz.
:::

::: gorev İnceleme isteğini hazırla
`arama_istegi(sorgu, bas, son, boyut=100)` bir Python sözlüğü döndürsün; ağ çağrısı yapmasın. `query.bool.filter` listesinde önce `query_string` (query aynen korunmuş, default_operator AND, lenient False), sonra @timestamp için `gte: bas, lt: son` range bulunsun. `sort` sırasıyla `{"@timestamp":"asc"}`, `{"event.id":"asc"}`; `track_total_hits` True; `size` boyut olsun. `_source` listesi @timestamp, event.id, user.name, event.outcome sırasıyla bulunsun.

Boyut integer (bool hariç) ve 1–1000 dahil aralıkta değilse ValueError. Uçlar açık ofsetli ISO 8601 zamanlarıdır; bas >= son ise ValueError. Uçları ofsetli datetime ile denetle ama gövdede özgün metinleri koru. `sorgu` yetkili inceleme metnidir; bu fonksiyon Lucene sözdizimini doğrulamaz.

```starter
def arama_istegi(sorgu, bas, son, boyut=100):
    return {}
```

```test
need("arama_istegi")
bas, son = "2026-10-21T10:00:00Z", "2026-10-21T10:05:00Z"
for boyut in (1, 2, 999, 1000):
    q = 'user.name:"Ayşe Kaya" AND event.outcome:failure'
    got = arama_istegi(q, bas, son, boyut)
    beklenen = {"query": {"bool": {"filter": [{"query_string": {"query": q, "default_operator": "AND", "lenient": False}}, {"range": {"@timestamp": {"gte": bas, "lt": son}}}]}}, "sort": [{"@timestamp": "asc"}, {"event.id": "asc"}], "track_total_hits": True, "size": boyut, "_source": ["@timestamp", "event.id", "user.name", "event.outcome"]}
    eq(got, beklenen, "iki boyut sınırı dahil; bütün istek sözleşmesi")
for boyut in (0, 1001, -1, True, 1.5):
    raises(ValueError, arama_istegi, "status:401", bas, son, boyut, msg="boyut komşuları ve tür")
eq(arama_istegi("status:401", bas, son)["size"], 100, "varsayılan boyut")
raises(ValueError, arama_istegi, "x:y", bas, bas, msg="boş pencere")
raises(ValueError, arama_istegi, "x:y", son, bas, msg="ters pencere")
raises(ValueError, arama_istegi, "x:y", "2026-10-21T13:00:00+03:00", bas, msg="farklı ofset aynı an")
eq(arama_istegi("new:term", "2026-10-21T13:00:00+03:00", son)["query"]["bool"]["filter"][0]["query_string"]["query"], "new:term", "değişen sorgu metni")
```

```solution
from datetime import datetime

def arama_istegi(sorgu, bas, son, boyut=100):
    if type(boyut) is not int or not 1 <= boyut <= 1000:
        raise ValueError("boyut 1..1000 integer olmalı")
    dt = lambda s: datetime.fromisoformat(s.replace("Z", "+00:00"))
    if dt(bas) >= dt(son):
        raise ValueError("başlangıç bitişten önce olmalı")
    return {"query": {"bool": {"filter": [
                {"query_string": {"query": sorgu, "default_operator": "AND", "lenient": False}},
                {"range": {"@timestamp": {"gte": bas, "lt": son}}}
            ]}},
            "sort": [{"@timestamp": "asc"}, {"event.id": "asc"}],
            "track_total_hits": True, "size": boyut,
            "_source": ["@timestamp", "event.id", "user.name", "event.outcome"]}
```

```hint
İstek bir sözlüktür; bas/son metnini koru. Tarih ve boyut kontrollerini gövdeyi kurmadan yap.
```
:::

::: gorev Sayfa ile bütün aramayı ayır
`raporu_oku(yanit)` error anahtarı varsa ValueError yükseltsin. Başarılı yanıt sözleşmesi: hits.total `{value: integer, relation: eq|gte}`, hits.hits içinde `_id` metinleri vardır; timed_out ve _shards.failed verilmezse false/0 kabul edilir.

Fonksiyon şu sözlüğü döndürsün: `idler` dönen hitlerin mevcut sırasıyla _id listesi; `bulunan` total.value; `kesin_toplam` relation eq mi; `arama_tamam` zaman aşımı yok ve failed sıfır mı; `tum_hitler` yalnız arama_tamam, kesin_toplam ve dönen hit sayısı total.value'ya eşitse True. Sorgu çalıştırma veya hitleri yeniden filtreleme; yalnız yanıt oku.

```starter
def raporu_oku(yanit):
    return {}
```

```test
need("raporu_oku")
def yanit(ids, value, relation="eq", timeout=False, failed=0):
    return {"hits": {"hits": [{"_id": x} for x in ids], "total": {"value": value, "relation": relation}}, "timed_out": timeout, "_shards": {"failed": failed}}
for sayi in (1, 2, 3):
    idler = ["z", "a"][:sayi]
    got = raporu_oku(yanit(idler, sayi))
    eq(got, {"idler": idler, "bulunan": sayi, "kesin_toplam": True, "arama_tamam": True, "tum_hitler": sayi <= 2}, "iki kayıtlık sayfanın altı/tamı/üstü; sıralamayı koru")
eq(raporu_oku(yanit([], 0))["tum_hitler"], True, "tamamlanmış kesin boş arama")
eq(raporu_oku(yanit(["q"], 1, "gte"))["tum_hitler"], False, "alt sınır kesin toplam değildir")
eq(raporu_oku(yanit(["q"], 1, "gte"))["kesin_toplam"], False, "gte bilgisi korunmalı")
for timeout, failed in [(True, 0), (False, 1), (True, 1)]:
    got = raporu_oku(yanit(["r"], 1, timeout=timeout, failed=failed))
    eq(got["arama_tamam"], False, "zaman aşımı veya shard başarısızlığı")
    eq(got["tum_hitler"], False, "kısmi yanıt tam sayfa gibi raporlanmaz")
eq(raporu_oku({"hits": {"hits": [{"_id": "yeni"}], "total": {"value": 7, "relation": "eq"}}})["idler"], ["yeni"], "opsiyonel durum alanları ve yeni kimlik")
raises(ValueError, raporu_oku, {"error": {"type": "parsing_exception"}}, msg="hata boş arama değildir")
```

```solution
def raporu_oku(yanit):
    if "error" in yanit:
        raise ValueError("sunucu hata döndürdü")
    hits = yanit["hits"]
    ids = [hit["_id"] for hit in hits["hits"]]
    value = hits["total"]["value"]
    kesin = hits["total"]["relation"] == "eq"
    tamam = not yanit.get("timed_out", False) and yanit.get("_shards", {}).get("failed", 0) == 0
    return {"idler": ids, "bulunan": value, "kesin_toplam": kesin,
            "arama_tamam": tamam, "tum_hitler": tamam and kesin and len(ids) == value}
```

```hint
Toplamın kesinliği, aramanın tamamlanması ve bütün hitlerin dönmesi üç ayrı boolean bilgidir.
```
:::
