---
id: el11
title: Lucene · Regex, Kaçış ve Hata Okuma
summary: Lucene regexini PCRE sanma; bütün terim eşleşmesi ve JSON kaçış katmanlarını ayır.
---

::: anlat Regex ile joker aynı dil değildir
`process.name:/svc_[0-9]{2}/` iki rakamlı bir terim desenidir. Regexte `?` önceki parçayı isteğe bağlı yapar; Lucene joker sorgusundaki “bir karakter” anlamına gelmez. Lucene regexi indeksli terimin tamamına uygulanır. Text alanı kullanıyorsan bütün kaynak satırı değil, analyzer terimlerini düşündüğünü hatırla.

```lucene
process.name:/svc_[0-9]{2}/
```

Bu motor PCRE değildir: `^`/`$` ankrajlarını ya da lookaround yapılarını alışkanlıkla taşıma. Bütün terimi kapsama zaten modelin parçasıdır. Görevimiz yalnız literal önek + sınırlandırılmış ASCII rakam tekrarı alt kümesini Python fullmatch ile inceler; genel Lucene regex motorunu yeniden kurmaz. Kaynak: [Lucene regex sözdizimi](https://www.elastic.co/docs/reference/query-languages/query-dsl/regexp-syntax).
:::

::: anlat Sorgu katmanı, JSON katmanı, sunucu cevabı
Sorgu dilindeki bir ters eğik çizginin JSON metninde gösterimi ayrıca kaçırılır. Örneğin arama çubuğundaki `message:foo\-bar` dizgesini Python'da bir değer olarak tuttuğunda HTTP gövdesini `json.dumps` ile oluştur; JSON'a elle tırnak veya ters eğik çizgi ekleme. JSON'dan geri çözülen query değeri ilk sorguyla birebir aynı kalmalıdır. JSON kodlamak Lucene sözdizimi hatasını düzeltmez.

Hata geldiğinde tahmin yürütmek yerine yanıtı ayır: parser hatası sorgu yazımını, sayısal dönüştürme hatası eşlemeye uymayan değeri, yetki hatası erişimi işaret edebilir. `timed_out` veya başarısız shard bulunan cevap eksik sonuç içerebilir. Hiç hit gelmemesi bunlardan farklıdır ve başarıyla tamamlanmış boş arama olabilir.

İkinci görev bu kategoriler için **açık bir yerel öncelik politikası** kullanır; bütün Elasticsearch hatalarını tanıdığını iddia etmez. Kaynaklar: [query_string katmanı](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-query-string-query), [arama yanıtı](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-search).
:::

::: tahmin
Aşağıdaki Lucene sorgusunu verilen eşleme, zaman filtresi ve sıralama altında oku. Hangi kimlikler döner? Pafta bu sorguyu Elasticsearch üzerinde çalıştırmaz; cevap, açık veri sözleşmesine göre hazırlanmış okuma cevabıdır.

```lucene
process.name:/svc_[0-9]{2}/
```

```stdin
{
  "mapping": {
    "process.name": "keyword, normalizer yok; tek terim",
    "@timestamp": "date UTC"
  },
  "time_filter": {
    "gte": "2026-10-21T10:00:00Z",
    "lt": "2026-10-21T11:00:00Z"
  },
  "ordering": "id artan; regex bütün indeksli terimi kapsar; yalnız ASCII [0-9]",
  "documents": [
    {
      "id": "a",
      "@timestamp": "2026-10-21T10:01:00Z",
      "process.name": "svc_01"
    },
    {
      "id": "b",
      "@timestamp": "2026-10-21T10:02:00Z",
      "process.name": "xsvc_01"
    },
    {
      "id": "c",
      "@timestamp": "2026-10-21T10:03:00Z",
      "process.name": "svc_012"
    },
    {
      "id": "d",
      "@timestamp": "2026-10-21T10:04:00Z",
      "process.name": "svc_1"
    },
    {
      "id": "e",
      "@timestamp": "2026-10-21T10:05:00Z",
      "process.name": "svc_99"
    },
    {
      "id": "f",
      "@timestamp": "2026-10-21T10:06:00Z",
      "process.name": "SVC_01"
    },
    {
      "id": "g",
      "@timestamp": "2026-10-21T10:07:00Z"
    }
  ]
}
```

```gercek
a
e
```

```test
import json, sys
from datetime import datetime
f = json.load(sys.stdin)
dt = lambda s: datetime.fromisoformat(s.replace("Z", "+00:00"))
bas, son = (dt(f["time_filter"][k]) for k in ("gte", "lt"))
ids = []
for d in f["documents"]:
    value = d.get("process.name")
    uygun = isinstance(value, str) and len(value) == 6 and value.startswith("svc_") and all(c in "0123456789" for c in value[4:])
    if uygun and bas <= dt(d["@timestamp"]) < son:
        ids.append(d["id"])
for kimlik in sorted(ids):
    print(kimlik)
```

???

`a` ve `e` bütün terim desenini sağlar. b fazladan önek, c fazladan rakam, d eksik rakam, f farklı harf içerir; g alanı yoktur.
:::

::: gorev Bütün terim ve tekrar sınırı
`regex_idleri(olaylar, alan, onek, en_az, en_cok)` normalizersız keyword değerin tamamı literal `onek` ve ardından `en_az`–`en_cok` ASCII rakamdan oluşuyorsa seçsin. İki tekrar sınırı dahil. Eksik/null alan elenir; kimlikler artan. Bu yalnız verilen alt kümenin okuma modelidir; onek içindeki regex karakterleri literaldir.

```starter
def regex_idleri(olaylar, alan, onek, en_az, en_cok):
    return []
```

```test
need("regex_idleri")
rows = [{"id": str(n), "p": "svc_" + "1" * n} for n in (1, 2, 3, 4)]
rows += [{"id": "onek", "p": "xsvc_11"}, {"id": "son", "p": "svc_11x"}, {"id": "harf", "p": "SVC_11"}, {"id": "unicode", "p": "svc_١١"}, {"id": "eksik"}, {"id": "null", "p": None}]
eq(regex_idleri(rows, "p", "svc_", 2, 3), ["2", "3"], "iki ucun eşitliği ve komşuları")
eq(regex_idleri(rows, "p", "svc_", 3, 3), ["3"], "tek uzunluk")
yeni = [{"id": "x", "code": "a.b12"}, {"id": "y", "code": "axb12"}, {"id": "z", "code": "a.b1"}]
eq(regex_idleri(yeni, "code", "a.b", 2, 2), ["x"], "literal nokta ve değişen alan")
eq(regex_idleri([], "p", "svc_", 1, 3), [], "boş korpus")
```

```solution
import re

def regex_idleri(olaylar, alan, onek, en_az, en_cok):
    desen = re.escape(onek) + "[0-9]{" + str(en_az) + "," + str(en_cok) + "}"
    return sorted(d["id"] for d in olaylar if isinstance(d.get(alan), str)
                  and re.fullmatch(desen, d[alan]) is not None)
```

```hint
Öneki re.escape ile kaçır; [0-9] kullan ve search yerine fullmatch seç.
```
:::

::: gorev JSON zarfı ve hata triyajı
İki fonksiyon yaz. `istek_jsonu(sorgu)`, `{"query":{"query_string":{"query":sorgu}}}` gövdesini JSON metni olarak döndürsün. Sorguyu değiştirme; yalnız JSON kodla.

`sonuc_durumu(yanit)` şu sırayla karar versin: error varsa, error/root_cause/caused_by içindeki type değerlerinde security_exception → `yetki`, parse_exception veya parsing_exception → `sozdizimi`, number_format_exception → `esleme`, diğer error → `hata`. Error yoksa timed_out → `zaman_asimi`, _shards.failed pozitif → `kismi`, kalan → `tamam`. Tip arama yalnız bu iç içe hata yapısındadır; liste root_cause elemanları da okunur. Bu bir eğitim triyaj politikasıdır; genel hata teşhisi değildir.

```starter
def istek_jsonu(sorgu):
    return "{}"

def sonuc_durumu(yanit):
    return "tamam"
```

```test
import json
need("istek_jsonu")
need("sonuc_durumu")
for query in [r'message:foo\-bar', r'path:"C:\\Lab\\note.txt"', 'user.name:"Ayşe Kaya"', '(status:400 OR status:401)', '']:
    eq(json.loads(istek_jsonu(query)), {"query": {"query_string": {"query": query}}}, "kaçışlar JSON turunda değişmemeli")
eq(sonuc_durumu({"error": {"type": "parsing_exception"}}), "sozdizimi", "doğrudan parser hatası")
eq(sonuc_durumu({"error": {"type": "search_phase_execution_exception", "root_cause": [{"type": "query_shard_exception", "caused_by": {"type": "parse_exception"}}]}}), "sozdizimi", "iç içe parser nedeni")
eq(sonuc_durumu({"error": {"type": "query_shard_exception", "caused_by": {"type": "number_format_exception"}}}), "esleme", "sayısal alanın hata nedeni")
eq(sonuc_durumu({"error": {"type": "security_exception"}, "timed_out": True}), "yetki", "error önceliği")
eq(sonuc_durumu({"error": {"type": "unknown_future_error"}}), "hata", "bilinmeyeni uydurma")
eq(sonuc_durumu({"timed_out": True, "_shards": {"failed": 1}}), "zaman_asimi", "açık öncelik")
eq(sonuc_durumu({"timed_out": False, "_shards": {"failed": 1}}), "kismi", "shard başarısız")
eq(sonuc_durumu({"timed_out": False, "_shards": {"failed": 0}, "hits": {"hits": []}}), "tamam", "boş sonuç hata değildir")
```

```solution
import json

def istek_jsonu(sorgu):
    return json.dumps({"query": {"query_string": {"query": sorgu}}}, ensure_ascii=False)

def sonuc_durumu(yanit):
    if "error" in yanit:
        tipler = set()
        def gez(value):
            if isinstance(value, list):
                for item in value:
                    gez(item)
            elif isinstance(value, dict):
                if isinstance(value.get("type"), str):
                    tipler.add(value["type"])
                for key in ("root_cause", "caused_by"):
                    if key in value:
                        gez(value[key])
        gez(yanit["error"])
        if "security_exception" in tipler:
            return "yetki"
        if tipler & {"parse_exception", "parsing_exception"}:
            return "sozdizimi"
        if "number_format_exception" in tipler:
            return "esleme"
        return "hata"
    if yanit.get("timed_out", False):
        return "zaman_asimi"
    if yanit.get("_shards", {}).get("failed", 0) > 0:
        return "kismi"
    return "tamam"
```

```hint
JSON için json.dumps kullan. Hata type değerlerini root_cause ve caused_by boyunca topla; sadece query_shard_exception adına bakarak parser hatası varsayma.
```
:::
