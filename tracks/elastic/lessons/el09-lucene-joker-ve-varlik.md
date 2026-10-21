---
id: el09
title: Lucene · Jokerler ve İndeksli Varlık
summary: Tek karakteri, değişken uzunluğu ve varlık sorgusunu ayır; keyword/text eşlemesini oku.
---

::: anlat Joker bütün kaynak metni taramak değildir
Tek terimde `?` bir karakteri, `*` sıfır veya daha çok karakteri karşılar. `host.name:web?` web1'i kabul eder, web12'yi etmez. Normalizersız keyword eşlemesinde harf farkı korunur. `text` alanında ise aranan şey ham kaynak cümlesi değil, analyzer'ın ürettiği terimlerdir; aynı joker iki eşlemede farklı sonuç verebilir.

```lucene
(host.name:web?) AND (user.name:*)
```

Baştan jokerle çok geniş arama pahalı olabilir. Önce uygun alanı ve kapsamı seç. Görevde yalnız `*` ve `?` özel karakterdir; köşeli parantez gibi Python fnmatch uzantıları Lucene jokeri diye eklenmez. Kaynaklar: [keyword eşlemesi](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/keyword), [text ve analyzer](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/text).
:::

::: anlat Alanın kaynakta görünmesi ile aranabilir olması farklıdır
`user.name:*` ve `_exists_:user.name`, bu fixture'ın eşlemesi altında alanın indeksli bir değeri olmasını ister. Boş metin indekslenmişse vardır; null veya boş dizi tek başına değer üretmez. `_source` içinde değer görünmesi de yeterli değildir: `ignore_above` gibi eşleme kuralları o değeri indeksten dışlamış olabilir.

Bu yüzden görevler kendi analyzer'ını veya indeksleyicisini uydurmaz. `indexed` sözlüğü önceden hazırlanmış terim listesidir: eksik anahtar ya da boş liste indeksli değer yok, `[""]` ise boş metin terimi var demektir. Böylece kaynağı, mapping'i ve indeks görünümünü ayrı ayrı okuyabilirsin.

Gerçek incelemede mapping, normalizer, null_value ve alanın indeksleme durumunu sunucudan kontrol edersin. Bu derste yalnız açık sözleşmedeki indeks görünümü geçerlidir. Kaynak: [İndeksli varlık ve boş değerler](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-exists-query).
:::

::: tahmin
Aşağıdaki Lucene sorgusunu verilen eşleme, zaman filtresi ve sıralama altında oku. Hangi kimlikler döner? Pafta bu sorguyu Elasticsearch üzerinde çalıştırmaz; cevap, açık veri sözleşmesine göre hazırlanmış okuma cevabıdır.

```lucene
(host.name:web?) AND (user.name:*)
```

```stdin
{
  "mapping": {
    "host.name": "keyword, normalizer yok",
    "user.name": "keyword, null_value yok; ignore_above uygulanmış"
  },
  "time_filter": {
    "gte": "2026-10-21T10:00:00Z",
    "lt": "2026-10-21T11:00:00Z"
  },
  "ordering": "id artan; indexed sözlüğü gerçekten indekslenmiş terimleri verir; _source karar kaynağı değildir",
  "documents": [
    {
      "id": "a",
      "@timestamp": "2026-10-21T10:01:00Z",
      "_source": {
        "user.name": ""
      },
      "indexed": {
        "host.name": [
          "web1"
        ],
        "user.name": [
          ""
        ]
      }
    },
    {
      "id": "b",
      "@timestamp": "2026-10-21T10:02:00Z",
      "_source": {
        "user.name": null
      },
      "indexed": {
        "host.name": [
          "web2"
        ]
      }
    },
    {
      "id": "c",
      "@timestamp": "2026-10-21T10:03:00Z",
      "_source": {
        "user.name": "ali"
      },
      "indexed": {
        "host.name": [
          "web12"
        ],
        "user.name": [
          "ali"
        ]
      }
    },
    {
      "id": "d",
      "@timestamp": "2026-10-21T10:04:00Z",
      "_source": {
        "user.name": "uzun-ve-indeks-disinda"
      },
      "indexed": {
        "host.name": [
          "web3"
        ]
      }
    },
    {
      "id": "e",
      "@timestamp": "2026-10-21T10:05:00Z",
      "_source": {
        "user.name": "can"
      },
      "indexed": {
        "host.name": [
          "Web4"
        ],
        "user.name": [
          "can"
        ]
      }
    },
    {
      "id": "f",
      "@timestamp": "2026-10-21T10:06:00Z",
      "_source": {
        "user.name": [
          "ayse",
          null
        ]
      },
      "indexed": {
        "host.name": [
          "web5"
        ],
        "user.name": [
          "ayse"
        ]
      }
    }
  ]
}
```

```gercek
a
f
```

```test
import json, sys
from datetime import datetime
f = json.load(sys.stdin)
dt = lambda s: datetime.fromisoformat(s.replace("Z", "+00:00"))
bas, son = (dt(f["time_filter"][k]) for k in ("gte", "lt"))
ids = []
for d in f["documents"]:
    terms = d.get("indexed", {})
    host_ok = any(len(t) == 4 and t.startswith("web") for t in terms.get("host.name", []))
    user_exists = len(terms.get("user.name", [])) > 0
    if bas <= dt(d["@timestamp"]) < son and host_ok and user_exists:
        ids.append(d["id"])
for kimlik in sorted(ids):
    print(kimlik)
```

???

`a` ve `f` döner. a için boş metin indekslenmiş bir değerdir; f için en az bir kullanıcı terimi vardır. b/d indeksli kullanıcı içermez; c hostu iki son karakterlidir; e harf farkıyla ayrılır.
:::

::: gorev Yalnız iki joker
`joker_idleri(olaylar, alan, desen)` tek değerli, normalizersız keyword alanını eşleştirsin. Desende yalnız `*` ve `?` özeldir; diğer bütün karakterler literal. Bütün değerin eşleşmesi gerekir. Eksik/null alan elenir; mevcut boş metin `*` ile eşleşir. Kimlikleri artan döndür. Bu sınırlı görev genel Lucene ayrıştırıcısı değildir.

```starter
def joker_idleri(olaylar, alan, desen):
    return []
```

```test
need("joker_idleri")
rows = [{"id": str(i), "host": x} for i, x in enumerate(["web", "web1", "web12", "Web1", "", "xweb1", "web[1]"])] + [{"id": "eksik"}, {"id": "null", "host": None}]
eq(joker_idleri(rows, "host", "web?"), ["1"], "tek karakterin 0/1/2 sınırı")
eq(joker_idleri(rows, "host", "web*"), ["0", "1", "2", "6"], "yıldız sıfır karakteri de kapsar")
eq(joker_idleri(rows, "host", "*"), ["0", "1", "2", "3", "4", "5", "6"], "boş metin var; null yok")
eq(joker_idleri(rows, "host", "web[1]"), ["6"], "fnmatch karakter sınıfı ekleme")
eq(joker_idleri(rows, "host", "web"), ["0"], "tam terim eşleşmesi")
yeni = [{"id": "q", "path": "a.b"}, {"id": "r", "path": "axb"}, {"id": "s", "path": "a..b"}]
eq(joker_idleri(yeni, "path", "a.b"), ["q"], "regex noktası literal")
eq(joker_idleri(yeni, "path", "a?b"), ["q", "r"], "alan ve desen değişti")
```

```solution
import re

def joker_idleri(olaylar, alan, desen):
    regex = "".join(".*" if c == "*" else "." if c == "?" else re.escape(c) for c in desen)
    return sorted(d["id"] for d in olaylar if isinstance(d.get(alan), str)
                  and re.fullmatch(regex, d[alan], flags=re.DOTALL) is not None)
```

```hint
Deseni karakter karakter kur; * ve ? dışında re.escape kullanıp bütün terimi fullmatch ile denetle.
```
:::

::: gorev Kaynağa değil indeks görünümüne bak
`indeksli_idler(olaylar, alan)` her olayın `indexed` sözlüğünde ilgili alanın **en az bir terimi** varsa kimliği döndürsün. Kimlik sırası artan olsun. Terim listeleri yalnız metin içerir; boş metin geçerli terimdir. `_source` alanını karar için kullanma; indeksleme bu görevin dışında hazırlanmıştır.

```starter
def indeksli_idler(olaylar, alan):
    return []
```

```test
need("indeksli_idler")
rows = [{"id": "a", "_source": {"user": ""}, "indexed": {"user": [""]}},
        {"id": "b", "_source": {"user": None}, "indexed": {}},
        {"id": "c", "_source": {"user": []}, "indexed": {"user": []}},
        {"id": "d", "_source": {"user": "ignore_above nedeniyle dışarıda"}, "indexed": {}},
        {"id": "e", "_source": {"user": [None, "ali"]}, "indexed": {"user": ["ali"], "host": ["web1"]}},
        {"id": "f"}]
eq(indeksli_idler(rows, "user"), ["a", "e"], "boş liste ile boş terim farklı")
eq(indeksli_idler(rows, "host"), ["e"], "alan parametresi")
eq(indeksli_idler(rows, "olmayan"), [], "indeksli değer yok")
eq(indeksli_idler([{"id": "degisti", "indexed": {"x": ["bir", "iki"]}}], "x"), ["degisti"], "çok değer ve değişen metin")
eq(indeksli_idler([], "user"), [], "boş korpus")
```

```solution
def indeksli_idler(olaylar, alan):
    return sorted(d["id"] for d in olaylar if len(d.get("indexed", {}).get(alan, [])) > 0)
```

```hint
Listenin içindeki metnin doğruluğunu değil listenin uzunluğunu denetle; [""] dolu listedir.
```
:::
