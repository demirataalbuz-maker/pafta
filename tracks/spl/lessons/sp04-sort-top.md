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
| `head N` | ilk N olay (varsayılan 10) |
| `tail N` | son N olay, **ters sırayla** |
| `dedup alan` | her değer için yalnızca **ilk** olayı tutar |

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
| dedup sunucu_id
| table sunucu_id id baslik
```

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

::: gorev Her sunucunun ilk bileti
Her sunucu için kayıtlardaki **ilk** bileti tut ve `sunucu_id` ile bilet `id`'sini `sunucu_id` sırasıyla getir. Sunucusu olmayan bilet listede olmasın.

```starter
sourcetype=biletler
| sort sunucu_id
| table sunucu_id id
```

```test
eq(sonuc, [(1, 2), (2, 13), (3, 12), (4, 1), (5, 9), (6, 5), (7, 14), (8, 6), (9, 4), (10, 10), (11, 7), (12, 17)], "12 sunucu, her birinin ilk bileti")
ok(kullanir("dedup"), "dedup kullan")
```

```solution
sourcetype=biletler
| dedup sunucu_id
| sort sunucu_id
| table sunucu_id id
```

```hint
`dedup sunucu_id` her sunucu için ilk olayı tutar ve alanı olmayan olayları atar; sonra `sort sunucu_id`.
```
:::
