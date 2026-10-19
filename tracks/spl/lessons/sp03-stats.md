---
id: sp03
title: stats ile Saymak
summary: count, dc, sum, avg, min, max, values; by ile gruplamak, as ile adlandırmak ve by alanı olmayan olayların sessizce düşmesi.
---

::: anlat stats
`stats` olayları gruplara ayırır ve her grup için istatistik hesaplar. Splunk'ta raporların neredeyse hepsi bir `stats` ile biter:

```spl
sourcetype=biletler
| stats count by durum
```

| Fonksiyon | Ne hesaplar | Varsayılan alan adı |
|---|---|---|
| `count` | olay sayısı | `count` |
| `count(alan)` | alanı olan olay sayısı | `count(alan)` |
| `dc(alan)` | farklı değer sayısı | `dc(alan)` |
| `sum`, `avg`, `min`, `max` | toplam, ortalama, en küçük, en büyük | `avg(cpu)` gibi |
| `values(alan)` | farklı değerlerin sıralı listesi | `values(alan)` |

Varsayılan adlar `avg(cpu)` gibi parantezlidir; sonraki komutlarda rahat kullanmak için `as` ile ad ver:

```spl
sourcetype=sunucular
| stats count as adet, avg(cpu) as ort, max(cpu) as en_yuksek by rol
| eval ort = round(ort, 1)
```

`stats` sonucu `by` alanlarına göre **sıralı** gelir. Birden çok `by` alanı yazılabilir: `by sehir, rol`.

```spl
sourcetype=sunucular
| stats dc(sehir) as sehir_sayisi, values(rol) as roller
```

> [!TUZAK]
> `by` alanı **olmayan** olaylar `stats` sonucuna hiç girmez. `stats count by sehir` bulutta çalışan üç sunucuyu sessizce atlar; toplam 9 görünür, 12 değil. Önce `eval sehir = coalesce(sehir, "bulut")` ile boşları doldur.

> [!NOT]
> Aynı kalıp her dilde: SQL'de `GROUP BY`, KQL'de `summarize ... by`, SPL'de `stats ... by`.
:::

::: tahmin
Kaç satır, hangi değerler?

```spl
sourcetype=sunucular
| stats count by sehir
```

???

`Ankara|3`, `İstanbul|4`, `İzmir|2`. Bulutta çalışan üç sunucunun `sehir` alanı yok, sonuca girmez. Satırlar `by` alanına göre sıralı gelir. Karakter kodu sırasıyla `A`, `İ`'den önce, `İstanbul` da `İzmir`'den önce gelir.
:::

::: gorev Duruma göre
Biletleri `durum`'a göre say; alanlar `durum` ve `count`.

```starter
sourcetype=biletler
| table durum
```

```test
eq(sutunlar, ["durum", "count"], "alanlar: durum, count")
eq(sonuc, [("açık", 9), ("çözüldü", 11)], "açık 9, çözüldü 11")
```

```solution
sourcetype=biletler
| stats count by durum
```

```hint
`stats count by durum`.
```
:::

::: gorev Bulut dahil şehirler
Sunucuları şehre göre say; şehri olmayanlar `bulut` olarak sayılsın. Alanlar `sehir` ve `adet`.

```cikti
Ankara|3
bulut|3
İstanbul|4
İzmir|2
```

```starter
sourcetype=sunucular
| stats count as adet by sehir
```

```test
eq(sutunlar, ["sehir", "adet"], "alanlar: sehir, adet")
eq(sonuc, [("Ankara", 3), ("bulut", 3), ("İstanbul", 4), ("İzmir", 2)], "dört grup, bulut dahil")
```

```solution
sourcetype=sunucular
| eval sehir = coalesce(sehir, "bulut")
| stats count as adet by sehir
```

```hint
`stats`'tan önce boş şehirleri doldur: `eval sehir = coalesce(sehir, "bulut")`.
```
:::

::: gorev Rol özeti
Her rol için `adet`, bir ondalığa yuvarlanmış ortalama CPU (`ort`) ve en yüksek CPU (`en_yuksek`) getir. Alanlar: `rol`, `adet`, `ort`, `en_yuksek`.

```starter
sourcetype=sunucular
| stats count by rol
```

```test
eq(sutunlar, ["rol", "adet", "ort", "en_yuksek"], "alanlar: rol, adet, ort, en_yuksek")
eq(sonuc, sorgu("SELECT rol, COUNT(*), round(AVG(cpu), 1), MAX(cpu) FROM sunucular GROUP BY rol ORDER BY rol"), "rol başına değerler")
```

```solution
sourcetype=sunucular
| stats count as adet, avg(cpu) as ort, max(cpu) as en_yuksek by rol
| eval ort = round(ort, 1)
```

```hint
Birden çok toplama yan yana: `stats count as adet, avg(cpu) as ort, max(cpu) as en_yuksek by rol`; yuvarlamayı sonra `eval` ile yap.
```
:::
