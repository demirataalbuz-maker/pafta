---
id: sp04
title: sort, head, tail, top ve dedup
summary: Varsayılanı artan olan sort, head ve ters sıralı tail, count ve percent üreten top/rare, ilk olayı tutan dedup.
---

::: anlat Sıralamak ve kesmek
```spl
sourcetype=sunucular
| sort -cpu                #! - azalan, + ya da işaretsiz artan
| head 3
| table ad cpu
```

| Komut | Ne yapar |
|---|---|
| `sort alan`, `sort -alan` | artan / azalan (Splunk'ta varsayılan **artan**; KQL'in tersi) |
| `sort 5 -alan` | sıralayıp ilk 5'i tutar |
| `sort rol, -cpu` | önce role göre artan, rol içinde CPU'ya göre azalan |
| `head N` | gelen ilk N olay (varsayılan 10) |
| `tail N` | son N olay, **ters sırayla** |
| `dedup alan` | her değer için yalnızca **ilk gelen** olayı tutar |

### top ve rare
`top alan` en sık değerleri, `rare alan` en seyreklerini verir; sonuçta `count` ve `percent` alanları gelir. Varsayılan sınır 10'dur, `limit=N` ile değişir:

```spl
sourcetype=biletler durum=açık
| top oncelik

sourcetype=biletler
| top limit=3 acan_id
```

`top alan` aslında `stats count by alan | sort -count | head 10` kalıbının kısaltmasıdır, üstüne bir yüzde sütunu ekler.

```spl
sourcetype=biletler
| sort acilis                #! önce sırayı kur
| dedup sunucu_id            #! her sunucunun ilk gelen, yani en eski bileti
| table sunucu_id id baslik
```

> [!TUZAK]
> `head`, `tail` ve `dedup` olayların **geliş sırasına** bağlıdır. Gerçek Splunk olayları **en yeniden eskiye** getirir: orada `head 3` en yeni üç olayı, sıralamasız bir `dedup sunucu_id` her sunucunun **en yeni** olayını verir. Pafta tezgahı tabloları eskiden yeniye okur; aynı arama burada en eski olayı tutar. Sonuç sıraya bağlıysa sırayı `sort` ile kendin kur: `sort acilis | dedup sunucu_id` iki yerde de en eskiyi, `sort -acilis | dedup sunucu_id` iki yerde de en yeniyi verir.

> [!TUZAK]
> `tail` son N olayı **ters sırayla** verir. `sort -cpu | tail 2` en düşük iki CPU'yu küçükten büyüğe değil, en sondan başlayarak gösterir. Sırayı korumak istiyorsan tersine sırala ve `head` kullan.
:::

::: tahmin
Hangi iki ad, hangi sırayla?

```spl
sourcetype=sunucular
| sort -cpu
| tail 2
| table ad
```

???

`test01`, sonra `yedek01`. Azalan sıralamada en sondaki iki sunucu yedek01 (12) ve test01 (3)'tür. `tail` sondan başlayarak verdiği için önce test01 gelir.
:::

::: gorev En yoğun üç sunucu
CPU'su en yüksek **üç** sunucunun `ad` ve `cpu` alanlarını en yoğundan başlayarak getir.

```starter
sourcetype=sunucular
| sort cpu
| head 3
| table ad cpu
```

```test
eq(sonuc, [("db01", 91), ("cache01", 84), ("web01", 72)], "db01, cache01, web01")
```

```solution
sourcetype=sunucular
| sort -cpu
| head 3
| table ad cpu
```

```hint
Splunk'ta varsayılan sıralama artandır; azalan için alanın önüne `-`: `sort -cpu`.
```
:::

::: gorev Açık biletlerde en sık öncelikler
Açık biletlerde önceliklerin sıklığını `top` ile getir.

```starter
sourcetype=biletler
| top oncelik
```

```test
eq(sutunlar, ["oncelik", "count", "percent"], "top'un alanları: oncelik, count, percent")
eq([(r[0], r[1]) for r in sonuc], [("düşük", 4), ("yüksek", 3), ("orta", 2)], "açık biletler: düşük 4, yüksek 3, orta 2")
```

```solution
sourcetype=biletler durum=açık
| top oncelik
```

```hint
Önce aramada süz: `sourcetype=biletler durum=açık`, sonra `| top oncelik`.
```
:::

::: gorev Her sunucunun en eski bileti
Her sunucu için **açılışı en eski** (`acilis` alanı) bileti tut ve `sunucu_id` ile bilet `id`'sini `sunucu_id` sırasıyla getir. Sunucusu olmayan bilet listede olmasın. Sonuç olayların geliş sırasına bağlı kalmasın: aynı arama gerçek Splunk'ta da aynı biletleri vermeli.

```starter
sourcetype=biletler
| sort sunucu_id
| table sunucu_id id
```

```test
import re
eq(sonuc, [(1, 2), (2, 13), (3, 12), (4, 1), (5, 9), (6, 5), (7, 14), (8, 6), (9, 4), (10, 10), (11, 7), (12, 17)], "12 sunucu, her birinin en eski bileti")
ok(kullanir("dedup"), "dedup kullan")
ok(re.search(r"\bsort\b[^|]*\bacilis\b[^|]*\|\s*dedup\b", src), "dedup'tan hemen önce acilis'e göre sırala: gerçek Splunk en yeniden eskiye getirir")
```

```solution
sourcetype=biletler
| sort acilis
| dedup sunucu_id
| sort sunucu_id
| table sunucu_id id
```

```hint
`dedup` ilk gelen olayı tutar; hangisinin ilk geleceğini sen belirle: önce `sort acilis`. Sonra `dedup sunucu_id` (alanı olmayan olayları da atar) ve sonuç için `sort sunucu_id`.
```
:::
