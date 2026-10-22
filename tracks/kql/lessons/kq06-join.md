---
id: kq06
title: join ile Birleştirmek
summary: join türleri; KQL'in şaşırtıcı varsayılanı innerunique, inner, leftouter, leftanti; anahtarları project ile hazırlamak ve $left/$right.
kazanim: SC200 3.2
---

::: anlat İki tabloyu birleştirmek
`join` soldaki sorgunun her satırını sağdaki sorgunun eşleşen satırlarıyla birleştirir. Sağ taraf parantez içinde kendi borusuyla yazılır; birleştirme sütunu `on` ile verilir:

```kql
biletler
| where durum == "açık"
| join kind=inner (sunucular | project sunucu_id = id, sunucu = ad) on sunucu_id
| project id, baslik, sunucu
```

Sağ tarafta `project` ile anahtarı soldakiyle **aynı ada** getirmek (`sunucu_id = id`) ve yalnızca gereken sütunları almak iyi bir alışkanlıktır. Adlar farklı kalacaksa `on $left.sunucu_id == $right.id` yazılır:

```kql
biletler
| join kind=inner (sunucular) on $left.sunucu_id == $right.id
| project id, ad, rol
| take 3
```

İki tarafta aynı adlı sütunlar varsa sağdakinin adına `1` eklenir (`id1`, `ad1`).

| `kind=` | Sonuç |
|---|---|
| `inner` | iki tarafta da eşleşen satırlar |
| `leftouter` | soldakilerin hepsi; eşi yoksa sağ sütunlar boş |
| `leftanti` | soldakilerden **eşi olmayanlar** (yalnız sol sütunlar) |
| `leftsemi` | soldakilerden eşi olanlar (yalnız sol sütunlar, tekrarsız) |
| *(yazılmazsa)* `innerunique` | sol taraf anahtar başına **tek satıra** indirilip inner yapılır |

> [!TUZAK]
> KQL'de `kind` yazmazsan varsayılan `innerunique`'dir: soldaki tabloda aynı anahtara sahip satırlardan **yalnızca biri** kalır. Yani iki bileti olan bir sunucunun biletlerinden biri sessizce kaybolur. SQL alışkanlığıyla `join` yazıp `kind`'ı unutmak, kayıt analizinde yanlış sayımın en yaygın sebebidir. Kural: **kind'ı her zaman açıkça yaz.**

```kql
personel
| join kind=leftanti (biletler | where isnotnull(atanan_id) | project id = atanan_id) on id
| project ad
```
:::

::: tahmin
İki sorgu, iki sayı:

```kql
biletler
| join (sunucular | project sunucu_id = id, sunucu = ad) on sunucu_id
| count

biletler
| join kind=inner (sunucular | project sunucu_id = id, sunucu = ad) on sunucu_id
| count
```

???

`12`, sonra `19`. İlk sorguda `kind` yazılmadığı için `innerunique` çalışır. Biletler, sunucu başına bir satıra indirilir; biletlerde 12 farklı sunucu geçtiği için sonuç 12 olur. `kind=inner` sunucusu olan 19 biletin hepsini tutar (18 numaralı biletin sunucusu yok).
:::

::: gorev Açık biletler ve sunucuları
Açık her biletin `id`'sini ve sunucusunun adını (`sunucu`) `id` sırasıyla getir. Hiçbir bilet kaybolmamalı.

```starter
biletler
| where durum == "açık"
| join (sunucular | project sunucu_id = id, sunucu = ad) on sunucu_id
| project id, sunucu
| sort by id asc
```

```test
eq(sutunlar, ["id", "sunucu"], "sütunlar: id, sunucu")
eq(sonuc, [(3, "db01"), (5, "dc01"), (9, "db02"), (10, "izleme01"), (12, "web03"), (15, "izleme01"), (17, "test01"), (20, "db01")], "sunucusu olan sekiz açık bilet")
```

```solution
biletler
| where durum == "açık"
| join kind=inner (sunucular | project sunucu_id = id, sunucu = ad) on sunucu_id
| project id, sunucu
| sort by id asc
```

```hint
Başlangıç kodunda `kind` yok: `innerunique` aynı sunucunun ikinci biletini atıyor. `kind=inner` yaz.
```
:::

::: gorev Sorumlusuz sunucu da listede
**Bütün** sunucuların adını (`ad`) ve sorumlusunun adını (`sorumlu`) ada göre artan sırayla getir; sorumlusu olmayan sunucu da listede kalsın.

```starter
sunucular
| join kind=inner (personel | project sorumlu_id = id, sorumlu = ad) on sorumlu_id
| project ad, sorumlu
| sort by ad asc
```

```test
eq(sutunlar, ["ad", "sorumlu"], "sütunlar: ad, sorumlu")
eq(len(sonuc), 12, "12 sunucunun hepsi")
ok(("test01", None) in sonuc, "test01 sorumlusuz olarak listede", got=sonuc[-3:])
eq(sonuc[0], ("cache01", "Zeynep"), "ilk satır cache01 – Zeynep")
```

```solution
sunucular
| join kind=leftouter (personel | project sorumlu_id = id, sorumlu = ad) on sorumlu_id
| project ad, sorumlu
| sort by ad asc
```

```hint
Soldakilerin hepsini tutmak için `kind=leftouter`.
```
:::

::: gorev Kendisine bilet atanmamış çalışanlar
Kendisine **hiç bilet atanmamış** çalışanların adlarını ada göre artan sırayla getir; `leftanti` kullan.

```starter
personel
| project ad
| sort by ad asc
```

```test
eq([r[0] for r in sonuc], ["Burak", "Deniz", "Selin"], "Burak, Deniz, Selin")
ok(kullanir("leftanti"), "kind=leftanti kullan")
```

```solution
personel
| join kind=leftanti (biletler | where isnotnull(atanan_id) | project id = atanan_id) on id
| project ad
| sort by ad asc
```

```hint
Sağ tarafta atanan kişileri `id` adıyla hazırla: `(biletler | project id = atanan_id)`; sonra `join kind=leftanti (...) on id`.
```
:::
