---
id: kq05
title: sort, top ve take
summary: KQL'de varsayılan sıralama yönünün azalan olması, birden çok anahtarla sıralama, top ile ilk N ve take'in neden rastgele olduğu.
kazanim: SC200 1.6
---

::: anlat Sıralamak
```kql
sunucular
| sort by cpu              #! DİKKAT: varsayılan yön AZALAN (desc)
| project ad, cpu
```

KQL'de `sort by` (eş anlamlısı `order by`) varsayılan olarak **büyükten küçüğe** sıralar; SQL'in tam tersi. Artan sıra istiyorsan `asc` yazmalısın. Yön, her anahtar için **ayrı ayrı** belirlenir:

```kql
sunucular
| where isnotempty(sehir)
| sort by sehir asc, cpu desc
| project sehir, ad, cpu
```

### top ve take
| İşleç | Ne yapar |
|---|---|
| `top 5 by cpu` | CPU'ya göre (varsayılan azalan) sıralayıp ilk 5'i alır |
| `take 5` (ya da `limit 5`) | **herhangi** 5 satırı alır; sıra garanti değildir |
| `sort by ... \| take 5` | `top` ile aynı sonucu verir |

```kql
sunucular
| top 3 by cpu
| project ad, cpu

sunucular
| top 3 by cpu asc
| project ad, cpu
```

> [!TUZAK]
> `take`, sıralama içermez: büyük bir tabloda her çalıştırmada farklı satırlar dönebilir. Tabloya göz atmak için idealdir; "en yüksek", "en son" gibi sorular için `top` ya da `sort by ... | take` kullan.

> [!TUZAK]
> Metinler karakter koduna göre sıralanır: `İ`, `Ç`, `Ö`, `Ş`, `Ü` ile başlayan değerler İngilizce harflerin **sonuna** düşer. `sort by sehir asc` İstanbul'u Ankara'dan sonra getirir (doğru), ama İzmir'i Zonguldak'tan da sonra getirirdi.
:::

::: tahmin
Hangi dört ad, hangi sırayla?

```kql
sunucular
| where isnotempty(sehir)
| sort by sehir asc, cpu
| take 4
| project ad
```

???

`db02`, `vpn01`, `web03`, `db01`. Şehir artan sırada önce Ankara gelir. Ama `cpu` için yön yazılmadığından o anahtar **azalan** sıralanır: db02 (47), vpn01 (38), web03 (18). Dördüncü satır sıradaki şehirden, İstanbul'dan gelir; orada en yüksek CPU db01'de (91).
:::

::: gorev En sakin üç sunucu
CPU'su **en düşük** üç sunucunun `ad` ve `cpu` sütunlarını, en düşükten başlayarak getir.

```starter
sunucular
| top 3 by cpu
| project ad, cpu
```

```test
eq(sonuc, [("test01", 3), ("yedek01", 12), ("web03", 18)], "test01, yedek01, web03 (bu sırayla)")
```

```solution
sunucular
| top 3 by cpu asc
| project ad, cpu
```

```hint
`top` da varsayılan olarak azalan sıralar; `top 3 by cpu asc`.
```
:::

::: gorev Son açılan biletler
En son açılan **üç** biletin `id` ve `baslik` sütunlarını, en yeniden başlayarak getir.

```starter
biletler
| take 3
| project id, baslik
```

```test
eq([r[0] for r in sonuc], [20, 19, 18], "20, 19, 18")
```

```solution
biletler
| sort by acilis desc
| take 3
| project id, baslik
```

```hint
`take` tek başına "son"u bilmez. Önce açılış zamanına göre sırala: `sort by acilis desc`, sonra `take 3`. Ya da `top 3 by acilis`.
```
:::

::: gorev Role göre, rol içinde CPU'ya göre
Sunucuları önce role göre **artan**, rol içinde CPU'ya göre **azalan** sırala; `rol` ve `ad` sütunlarını getir.

```starter
sunucular
| sort by rol, cpu
| project rol, ad
```

```test
eq(sutunlar, ["rol", "ad"], "sütunlar: rol, ad")
eq(sonuc, sorgu("SELECT rol, ad FROM sunucular ORDER BY rol ASC, cpu DESC"), "sıralama doğru")
```

```solution
sunucular
| sort by rol asc, cpu desc
| project rol, ad
```

```hint
Yön her anahtar için ayrı: `sort by rol asc, cpu desc`.
```
:::
