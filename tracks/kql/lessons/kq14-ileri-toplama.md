---
id: kq14
title: İleri Toplama
summary: arg_max ve arg_min ile her varlığın en son ya da en uç kaydını bütün sütunlarıyla almak, percentile ve percentiles ile gecikme dağılımı, ortalamanın neden yanılttığı, oranlar, dcount, make_set ve take_any.
---

::: anlat Her varlığın son durumu: arg_max
SOC'ta ve operasyonda en sık sorulan sorulardan biri şudur: "Her sunucudan (cihazdan, kullanıcıdan) gelen **en son** kayıt ne?" `max(zaman)` yalnızca zamanı verir; o satırın öteki sütunlarını vermez. `arg_max` ise "zamanı en büyük olan **satırı**" verir:

```kql
istekler
| summarize arg_max(zaman, *) by sunucu
| project sunucu, zaman, yol, durum
| sort by sunucu asc
```

| Yazım | Döndürdüğü |
|---|---|
| `arg_max(zaman, *)` | en büyük `zaman`'lı satırın bütün sütunları |
| `arg_max(zaman, yol, durum)` | o satırın yalnızca bu sütunları |
| `arg_min(zaman, *)` | en küçük `zaman`'lı satır: ilk kayıt |

Sonuçta önce `by` sütunları, sonra ölçülen sütun (`zaman`), sonra istenen öteki sütunlar gelir. "Son görülme", "son bilinen IP", "en yavaş istek ve kimin yaptığı" sorularının hepsi `arg_max`'tır.

> [!NOT]
> Gerçek Kusto'da `arg_max` başka toplamalarla aynı `summarize`'da kullanılabilir: `summarize arg_max(zaman, *), adet = count() by sunucu`. Pafta tezgahında `arg_max` tek başına kullanılmalı; başka bir toplama gerekiyorsa ayrı bir sorguyla birleştir.
:::

::: anlat Dağılım: ortalama yalan söyleyebilir
`/api/rapor` isteklerinin ortalama süresi yaklaşık 1500 ms, ama isteklerin yarısı 1200 ms'nin altında bitiyor. Birkaç çok yavaş istek ortalamayı yukarı çekiyor. Gecikme, süre ve boyut gibi değerlerde **yüzdelikler** daha dürüst bir resim verir:

```kql
istekler
| where yol in ("/api/bilet", "/api/rapor")
| summarize istek = count(), p50 = percentile(sure_ms, 50), p95 = percentile(sure_ms, 95) by yol
| sort by yol asc
```

| Ölçü | Sorduğu soru |
|---|---|
| `percentile(x, 50)` | tipik istek ne kadar sürüyor? (medyan) |
| `percentile(x, 95)` | en kötü %5 nerede başlıyor? Kullanıcıların hissettiği yavaşlık |
| `percentiles(x, 50, 95, 99)` | birkaç yüzdelik birden; sütunlar `percentile_x_50`, `percentile_x_95` … |
| `stdev(x)` | değerler ortalama etrafında ne kadar dağınık |

> [!DERİN]
> Kusto büyük veride yüzdelikleri ve `dcount`'u **tahmini** hesaplar (T-Digest ve HyperLogLog): milyarlarca satırda kesin sonuç çok pahalıdır, küçük bir hata payı kabul edilir. Pafta tezgahı küçük veride "en yakın sıra" yöntemini kullanır; sonuç her zaman verideki bir değerdir.

### Oranlar
"Kaç hata?" sorusundan çok "hataların oranı ne?" sorusu önemlidir: 1000 istekte 10 hata ile 20 istekte 10 hata aynı şey değildir:

```kql
istekler
| summarize istek = count(), hata = countif(durum >= 500) by sunucu
| extend oran = round(100.0 * hata / istek, 1)
| sort by oran desc
```

`100.0` ile çarpmak bölmeyi ondalıklı yapar; `100 * hata / istek` tam sayı bölmesine düşüp 27.3 yerine 27 verir.

| Toplama | Döndürdüğü |
|---|---|
| `dcount(x)` | farklı değer sayısı |
| `dcountif(x, koşul)`, `sumif(x, koşul)` | koşullu sürümleri |
| `make_set(x)`, `make_list(x)` | değerlerin dizisi (tekrarsız / tekrarlı) |
| `take_any(x)` | gruptan herhangi bir değer: örnek görmek için |
:::

::: tahmin
Tek satır yazar:

```kql
istekler
| summarize arg_max(sure_ms, yol, kullanici)
```

???

`2600|/api/rapor|can`. `by` olmadığı için bütün tablo tek bir gruptur. En yavaş istek 2600 ms'dir ve `arg_max` o satırın `yol` ve `kullanici` değerlerini de getirir: can'ın `/api/rapor` isteği.
:::

::: gorev Her sunucunun son isteği
Her sunucuya gelen **en son** isteğin `zaman`, `yol` ve `durum` değerlerini getir: `sunucu`, `zaman`, `yol`, `durum`; sunucuya göre artan.

```starter
istekler
| summarize zaman = max(zaman) by sunucu
| sort by sunucu asc
```

```test
eq(sutunlar, ["sunucu", "zaman", "yol", "durum"], "sütunlar")
eq(sonuc, [("web01", "2026-10-19 11:47", "/api/bilet", 200), ("web02", "2026-10-19 11:20", "/api/bilet", 201),
           ("web03", "2026-10-19 11:31", "/api/durum", 200)], "üç sunucunun son isteği")
ok(kullanir("arg_max"), "arg_max kullan")
```

```solution
istekler
| summarize arg_max(zaman, *) by sunucu
| project sunucu, zaman, yol, durum
| sort by sunucu asc
```

```hint
`max(zaman)` satırın öteki sütunlarını getirmez. `summarize arg_max(zaman, *) by sunucu` en son satırın tamamını getirir.
```
:::

::: gorev Gecikme yüzdelikleri
`/api/bilet` ve `/api/rapor` yolları için istek sayısını, medyan (`p50`) ve 95. yüzdelik (`p95`) süreyi getir: `yol`, `istek`, `p50`, `p95`; yola göre artan.

```starter
istekler
| where yol in ("/api/bilet", "/api/rapor")
| summarize istek = count(), ort = avg(sure_ms) by yol
| sort by yol asc
```

```test
eq(sutunlar, ["yol", "istek", "p50", "p95"], "sütunlar")
eq(sonuc, [("/api/bilet", 8, 120, 310), ("/api/rapor", 8, 1200, 2600)], "iki yolun yüzdelikleri")
```

```solution
istekler
| where yol in ("/api/bilet", "/api/rapor")
| summarize istek = count(), p50 = percentile(sure_ms, 50), p95 = percentile(sure_ms, 95) by yol
| sort by yol asc
```

```hint
`percentile(sure_ms, 50)` ve `percentile(sure_ms, 95)`; adlarını `p50 = ...` biçiminde ver.
```
:::

::: gorev Sunucu başına hata oranı
Her sunucu için istek sayısını, 500 ve üstü durum kodlu istek sayısını ve hata oranını (yüzde, bir ondalık) getir: `sunucu`, `istek`, `hata`, `oran`; orana göre azalan.

```starter
istekler
| where durum >= 500
| summarize hata = count() by sunucu
```

```test
eq(sutunlar, ["sunucu", "istek", "hata", "oran"], "sütunlar")
eq(sonuc, [("web01", 11, 3, 27.3), ("web02", 9, 1, 11.1), ("web03", 6, 0, 0.0)], "üç sunucu, hatasız olan da")
```

```solution
istekler
| summarize istek = count(), hata = countif(durum >= 500) by sunucu
| extend oran = round(100.0 * hata / istek, 1)
| sort by oran desc
```

```hint
Başlangıç kodundaki `where` hatasız sunucuyu (web03) sonuçtan atıyor. Süzme; hatayı `countif(durum >= 500)` ile say.
```

```hint
Oran: `round(100.0 * hata / istek, 1)`. `100.0` bölmeyi ondalıklı yapar.
```
:::
