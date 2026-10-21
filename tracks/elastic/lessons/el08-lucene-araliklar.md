---
id: el08
title: Lucene · Sayı ve Zaman Aralıkları
summary: Köşeli ve süslü sınırları ayrı ayrı oku; sayı, tarih ve zaman dilimini birbirine karıştırma.
---

::: anlat İki uç birbirinden bağımsızdır
`status:[400 TO 499]` iki ucu da içerir; `status:{400 TO 499}` ikisini dışlar. Karışık yazım da vardır: `status:[400 TO 500}` alt sınırı içerir, üst sınırı dışlar. `TO` büyük harflidir. Bir açık uç için `*` kullanılabilir; alanın `integer` eşlemesini doğrulamadan sayı gibi sıralama varsayma.

```lucene
(status:[400 TO 500}) AND (@timestamp:["2026-10-21T10:00:00.000Z" TO "2026-10-21T10:00:01.000Z"})
```

Kapalı bir üst sınırı açık yapınca tam uçtaki belge kaybolur. Sınır testleri bu yüzden uçtan bir küçük, tam uç ve bir büyük değerleri ayrı ayrı içerir. Sorgu metni bu tezgahta yürütülmez; Python görevleri verilen aralık sözleşmesini hesaplar. Kaynak: [Lucene aralık yazımı](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-query-string-query).
:::

::: anlat Tarih aralığı ve Kibana zaman filtresi kesişir
Sorgudaki tarih aralığına ek olarak Kibana'nın seçili zaman alanı ve zaman filtresi uygulanabilir. İki pencerenin kesişimini okumadan “neden bu belge gelmedi?” sorusunu yanıtlayamazsın. Burada bütün zamanlar açık UTC ofsetli ISO 8601'dir; fixture tarih hassasiyetini milisaniye olarak bildirir.

`13:00+03:00` ile `10:00Z` aynı andır. Sadece metinleri sözlüksel karşılaştırmak farklı ofsetlerde yanlış sonuç verebilir. Görev çözümü tarihleri ofset bilgili Python `datetime` değerlerine çevirir. Bu, tarih hesaplama alıştırmasıdır; Elasticsearch tarih yuvarlamasını veya `now` değişkenini modellemiyoruz.

Üretimde mapping biçimi, date/date_nanos ayrımı ve `time_zone` ayarı ayrıca incelenmelidir. Bu görevlerin sabit zamanları saat ilerledikçe değişmez. Kaynak: [query_string zaman dilimi ayarı](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-query-string-query).
:::

::: tahmin
Aşağıdaki Lucene sorgusunu verilen eşleme, zaman filtresi ve sıralama altında oku. Hangi kimlikler döner? Pafta bu sorguyu Elasticsearch üzerinde çalıştırmaz; cevap, açık veri sözleşmesine göre hazırlanmış okuma cevabıdır.

```lucene
(status:[400 TO 500}) AND (@timestamp:["2026-10-21T10:00:00.000Z" TO "2026-10-21T10:00:01.000Z"})
```

```stdin
{
  "mapping": {
    "status": "integer",
    "@timestamp": "date, millisecond precision"
  },
  "time_filter": {
    "gte": "2026-10-21T09:00:00.000Z",
    "lt": "2026-10-21T11:00:00.000Z"
  },
  "ordering": "id artan; eksik alan pozitif aralığı sağlamaz; tek değerli alanlar",
  "documents": [
    {
      "id": "a",
      "status": 399,
      "@timestamp": "2026-10-21T10:00:00.000Z"
    },
    {
      "id": "b",
      "status": 400,
      "@timestamp": "2026-10-21T10:00:00.000Z"
    },
    {
      "id": "c",
      "status": 499,
      "@timestamp": "2026-10-21T10:00:00.999Z"
    },
    {
      "id": "d",
      "status": 500,
      "@timestamp": "2026-10-21T10:00:00.500Z"
    },
    {
      "id": "e",
      "status": 401,
      "@timestamp": "2026-10-21T10:00:01.000Z"
    },
    {
      "id": "f",
      "status": 401,
      "@timestamp": "2026-10-21T09:59:59.999Z"
    },
    {
      "id": "g",
      "@timestamp": "2026-10-21T10:00:00.500Z"
    }
  ]
}
```

```gercek
b
c
```

```test
import json, sys
from datetime import datetime
f = json.load(sys.stdin)
dt = lambda s: datetime.fromisoformat(s.replace("Z", "+00:00"))
t0, t1 = (dt(f["time_filter"][k]) for k in ("gte", "lt"))
q0, q1 = dt("2026-10-21T10:00:00.000Z"), dt("2026-10-21T10:00:01.000Z")
ids = []
for d in f["documents"]:
    value = d.get("status")
    stamp = dt(d["@timestamp"])
    if type(value) is int and 400 <= value < 500 and t0 <= stamp < t1 and q0 <= stamp < q1:
        ids.append(d["id"])
for kimlik in sorted(ids):
    print(kimlik)
```

???

`b` alt sınırlarda olduğu için kalır; `c` iki üst sınırın hemen altındadır. d sayısal üst sınırda, e zaman üst sınırında ve f zaman alt sınırının bir milisaniye önündedir.
:::

::: gorev Dört aralık türü
`aralik_idleri(olaylar, alan, alt, ust, alt_dahil, ust_dahil)` tek değerli sayısal alanı filtrelesin. `None` verilen uç sınırsızdır. Veri alanı eksik/null ise elensin; diğer mevcut değerler integer'dır. Kimlikleri artan döndür. Bu fonksiyon Lucene metni ayrıştırmaz; köşeli/süslü uçların hesap modelidir.

```starter
def aralik_idleri(olaylar, alan, alt, ust, alt_dahil, ust_dahil):
    return []
```

```test
need("aralik_idleri")
olaylar = [{"id": str(x), "status": x} for x in (9, 10, 11, 12, 13)] + [{"id": "eksik"}, {"id": "null", "status": None}]
for alt_dahil, ust_dahil, beklenen in [(True, True, ["10", "11", "12"]), (False, False, ["11"]), (True, False, ["10", "11"]), (False, True, ["11", "12"])]:
    eq(aralik_idleri(olaylar, "status", 10, 12, alt_dahil, ust_dahil), beklenen, "iki sınır ve ±1 komşuları")
eq(aralik_idleri(olaylar, "status", 11, None, True, False), ["11", "12", "13"], "açık üst uç")
eq(aralik_idleri(olaylar, "status", None, 10, False, False), ["9"], "açık alt uç")
eq(aralik_idleri(olaylar, "status", 11, 11, True, True), ["11"], "tek değerli kapalı aralık")
eq(aralik_idleri(olaylar, "status", 11, 11, True, False), [], "tek değerli yarı açık aralık boş")
yeni = [{"id": "x", "bytes": 20}, {"id": "y", "bytes": 21}, {"id": "z", "bytes": 22}]
eq(aralik_idleri(yeni, "bytes", 20, 22, False, True), ["y", "z"], "alan ve eşikler değişti")
```

```solution
def aralik_idleri(olaylar, alan, alt, ust, alt_dahil, ust_dahil):
    ids = []
    for d in olaylar:
        value = d.get(alan)
        if value is None:
            continue
        alt_ok = alt is None or value > alt or (alt_dahil and value == alt)
        ust_ok = ust is None or value < ust or (ust_dahil and value == ust)
        if alt_ok and ust_ok:
            ids.append(d["id"])
    return sorted(ids)
```

```hint
Alt ve üst uç için ayrı boolean üret; eşitliği yalnız ilgili dahil bayrağı açıksa kabul et.
```
:::

::: gorev Ofsetli zamanı karşılaştır
`zaman_idleri(olaylar, bas, son, bas_dahil=True, son_dahil=False)` @timestamp alanına göre filtrelesin. Bütün mevcut damgalar ve uçlar geçerli, açık ofsetli ISO 8601 zamanlarıdır; eksik/null damga elenir. Ofsetleri tarihe çevirerek karşılaştır, kimlikleri artan döndür. Varsayılan pencere `[bas, son)`.

```starter
def zaman_idleri(olaylar, bas, son, bas_dahil=True, son_dahil=False):
    return []
```

```test
need("zaman_idleri")
bas, son = "2026-10-21T10:00:00.000Z", "2026-10-21T10:00:01.000Z"
zamanlar = ["2026-10-21T09:59:59.999Z", bas, "2026-10-21T10:00:00.001Z", "2026-10-21T10:00:00.999Z", son, "2026-10-21T10:00:01.001Z"]
olaylar = [{"id": str(i), "@timestamp": t} for i, t in enumerate(zamanlar)] + [{"id": "eksik"}, {"id": "null", "@timestamp": None}]
eq(zaman_idleri(olaylar, bas, son), ["1", "2", "3"], "iki ucun tam değeri ve ±1 ms")
eq(zaman_idleri(olaylar, bas, son, False, True), ["2", "3", "4"], "dahil uçlar ters")
eq(zaman_idleri(olaylar, bas, son, True, True), ["1", "2", "3", "4"], "iki uç dahil")
ofsetli = [{"id": "ayni", "@timestamp": "2026-10-21T13:00:00+03:00"}, {"id": "son", "@timestamp": "2026-10-21T13:00:01+03:00"}]
eq(zaman_idleri(ofsetli, bas, son), ["ayni"], "farklı ofset aynı an")
eq(zaman_idleri(olaylar, zamanlar[2], zamanlar[3]), ["2"], "zaman parametreleri değişti")
```

```solution
from datetime import datetime

def zaman_idleri(olaylar, bas, son, bas_dahil=True, son_dahil=False):
    dt = lambda s: datetime.fromisoformat(s.replace("Z", "+00:00"))
    alt, ust = dt(bas), dt(son)
    ids = []
    for d in olaylar:
        if d.get("@timestamp") is None:
            continue
        value = dt(d["@timestamp"])
        if (value > alt or (bas_dahil and value == alt)) and (value < ust or (son_dahil and value == ust)):
            ids.append(d["id"])
    return sorted(ids)
```

```hint
datetime.fromisoformat için Z sonunu +00:00 yap; metin karşılaştırması kullanma.
```
:::
