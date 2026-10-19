---
id: kq04
title: summarize ile Özetlemek
summary: count, countif, dcount, avg, sum, min, max; by ile gruplamak, varsayılan sütun adları ve bin ile aralıklara bölmek.
---

::: anlat summarize
`summarize` satırları gruplara ayırır ve her grup için toplama fonksiyonlarını hesaplar. Log analizinin büyük kısmı bu tek işleçtir:

```kql
biletler
| summarize adet = count() by durum
```

| Fonksiyon | Ne hesaplar |
|---|---|
| `count()` | satır sayısı |
| `countif(koşul)` | koşulu sağlayan satır sayısı |
| `dcount(x)` | farklı değer sayısı (boşları saymaz) |
| `sum(x)`, `avg(x)`, `min(x)`, `max(x)` | toplam, ortalama, en küçük, en büyük |
| `make_set(x)` | farklı değerlerin listesi |

Birden çok toplama ve birden çok grup sütunu yan yana yazılır. Sonuçta önce `by` sütunları, sonra toplamalar gelir:

```kql
sunucular
| summarize adet = count(), ort_cpu = round(avg(cpu), 1), en_yuksek = max(cpu) by rol
| sort by adet desc
```

Toplamaya ad vermezsen KQL kendisi verir: `count()` → `count_`, `avg(cpu)` → `avg_cpu`, `dcount(sehir)` → `dcount_sehir`:

```kql
sunucular
| summarize count(), avg(cpu) by sehir
```

`by` olmadan bütün tablo tek grup olur:

```kql
biletler
| summarize toplam = count(), acik = countif(durum == "açık"), sunucu = dcount(sunucu_id)
```

### bin: aralıklara bölmek
`bin(x, boyut)` bir değeri aralığının başına yuvarlar; sayılarla da zamanla da çalışır:

```kql
sunucular
| summarize adet = count() by aralik = bin(cpu, 25)
| sort by aralik asc
```

> [!NOT]
> Aynı kalıp her yerde: SQL'de `SELECT rol, COUNT(*) ... GROUP BY rol`, KQL'de `summarize count() by rol`, Splunk'ta `stats count by rol`. Bir dilde öğrendiğin özetleme düşüncesi diğerlerine olduğu gibi taşınır.
:::

::: tahmin
Tek satır, üç sayı:

```kql
biletler
| summarize toplam = count(), acik = countif(durum == "açık"), kisi = dcount(atanan_id)
```

???

`20|9|7`. 20 bilet var, 9'u açık. `dcount` atanan kişilerin farklı değerlerini sayar ve boşları (atanmamış 4 bileti) atlar: 2, 3, 4, 5, 6, 7 ve 10 numaralı çalışanlar, yani 7 kişi.
:::

::: gorev Rol başına sunucu
Her rol için sunucu sayısını getir: `rol` ve `adet` sütunları.

```starter
sunucular
| project rol
```

```test
eq(sutunlar, ["rol", "adet"], "sütunlar: rol, adet")
eq(sorted(sonuc), sorted(sorgu("SELECT rol, COUNT(*) FROM sunucular GROUP BY rol")), "rol başına sayılar")
```

```solution
sunucular
| summarize adet = count() by rol
```

```hint
`summarize adet = count() by rol`.
```
:::

::: gorev Şehir ortalaması
Şehri bilinen sunucular için her şehrin ortalama CPU'sunu bir ondalığa yuvarlayarak `ort` adıyla getir; en yüksek ortalama en üstte.

```cikti
İstanbul|65.3
Ankara|34.3
İzmir|20.5
```

```starter
sunucular
| summarize ort = avg(cpu) by sehir
```

```test
eq(sutunlar, ["sehir", "ort"], "sütunlar: sehir, ort")
eq(sonuc, [("İstanbul", 65.3), ("Ankara", 34.3), ("İzmir", 20.5)], "şehir ortalamaları, büyükten küçüğe")
```

```solution
sunucular
| where isnotempty(sehir)
| summarize ort = round(avg(cpu), 1) by sehir
| sort by ort desc
```

```hint
Bulut sunucularını `where isnotempty(sehir)` ile önce at; `round(avg(cpu), 1)`; sonra `sort by ort desc`.
```
:::

::: gorev Açık biletlerin öncelikleri
Yalnızca **açık** biletleri önceliğe göre say: `oncelik` ve `adet`.

```starter
biletler
| summarize adet = count() by oncelik
```

```test
eq(sutunlar, ["oncelik", "adet"], "sütunlar: oncelik, adet")
eq(sorted(sonuc), [("düşük", 4), ("orta", 2), ("yüksek", 3)], "açık biletlerin öncelik dağılımı")
```

```solution
biletler
| where durum == "açık"
| summarize adet = count() by oncelik
```

```hint
Süzmeyi özetlemeden **önce** yap: `where durum == "açık"` sonra `summarize`.
```
:::
