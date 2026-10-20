---
id: kq15
title: Sıralı Satırlar
summary: KQL tablolarının sırasızlığı ve serialize; prev ve next ile komşu satıra bakmak, grup sınırında sıfırlamak, row_number ve row_cumsum'un restart argümanı, durum değişikliklerini yakalamak ve olaylar arasındaki süreyi ölçmek.
---

::: anlat Komşu satıra bakmak
SQ11'de `LAG` ve `LEAD` ile yaptığını KQL'de `prev()` ve `next()` yapar. Bir farkla: KQL tabloları **sırasızdır** ve "önceki satır" ancak satırlar sıralandıktan sonra anlam taşır. Bu yüzden `prev`, `next`, `row_number` ve `row_cumsum` yalnızca **serileştirilmiş** bir girdide çalışır. Girdi `sort by`, `top` ya da `serialize`'dan sonra serileşmiş olur:

```kql
olcumler
| sort by sunucu_id asc, zaman asc
| extend degisim = cpu - prev(cpu)
| project sunucu_id, zaman, cpu, degisim
```

Sıralamayı unutursan sorgu hata verir: `olcumler | extend p = prev(cpu)`.

| Fonksiyon | Döndürdüğü |
|---|---|
| `prev(x)`, `prev(x, 2)` | bir (iki) önceki satırın değeri; yoksa boş |
| `prev(x, 1, 0)` | yoksa 0 |
| `next(x)` | bir sonraki satırın değeri |
| `row_number()` | 1, 2, 3 … |
| `row_cumsum(x)` | baştan bu satıra kadar toplam |

### Grup sınırında sıfırlamak
Yukarıdaki sorguda 4 numaralı sunucunun ilk ölçümü, 1 numaralının **son** ölçümüyle karşılaştırılıyor: −7 anlamsız bir değer. KQL'de `PARTITION BY` yoktur; grup sınırını kendin denetlersin:

```kql
olcumler
| sort by sunucu_id asc, zaman asc
| extend degisim = iff(sunucu_id == prev(sunucu_id), cpu - prev(cpu), int(null))
```

`row_number` ve `row_cumsum` için bunun kısa yolu **restart** argümanıdır: koşul doğru olan satırda sayaç baştan başlar:

```kql
olcumler
| sort by sunucu_id asc, zaman asc
| extend sira = row_number(1, sunucu_id != prev(sunucu_id)),
         toplam = row_cumsum(cpu, sunucu_id != prev(sunucu_id))
```

> [!NOT]
> `int(null)`, `timespan(null)`, `datetime(null)` türü belli boş değerlerdir. `iff`'in iki kolu aynı türde olmalı: `cpu - prev(cpu)` bir sayıdır, öteki kol da sayı türünde bir boşluk olmalı.
:::

::: anlat Değişiklikler ve aralar
Sıralı satırlarla iki güçlü soru sorulur.

**Durum ne zaman değişti?** Her satırı bir öncekiyle karşılaştır, yalnızca farklı olanları tut. Böylece yüzlerce satırlık "hata, hata, hata, tamam, tamam" dizisi birkaç **geçişe** iner:

```kql
istekler
| sort by zaman asc
| extend hatali = durum >= 500
| extend degisti = hatali != prev(hatali)
| where degisti
| project zaman, sunucu, hatali
```

**Bir sonraki olaya kadar ne kadar geçti?** `next(zaman) - zaman` bir süre verir. Bir kullanıcının ardışık istekleri arasındaki en uzun sessizlik, bir cihazın iki sinyali arasındaki boşluk, bir işin iki çalışması arasındaki gecikme hep bu kalıptır:

```kql
istekler
| where kullanici == "can"
| sort by zaman asc
| extend sonraki = next(zaman), ara = next(zaman) - zaman
| project zaman, sonraki, ara
```
:::

::: tahmin
Üç satır yazar:

```kql
datatable(t:int, v:int)[1, 10, 2, 15, 3, 12]
| sort by t asc
| extend d = v - prev(v), c = row_cumsum(v)
| project t, d, c
```

???

`1||10`, `2|5|25`, `3|-3|37`. İlk satırın öncesi olmadığı için `prev(v)` boştur ve fark da boş kalır. Sonra 15 − 10 = 5 ve 12 − 15 = −3. Birikimli toplam 10, 25, 37 diye ilerler.
:::

::: gorev Sunucu içinde saatlik değişim
Her ölçümün bir önceki saate göre CPU değişimini `degisim` sütununda hesapla; değişim yalnızca **aynı sunucunun** önceki ölçümüne göre hesaplansın, her sunucunun ilk ölçümünde boş kalsın: `sunucu_id`, `zaman`, `cpu`, `degisim`; sunucuya sonra zamana göre artan.

```starter
olcumler
| sort by sunucu_id asc, zaman asc
| extend degisim = cpu - prev(cpu)
| project sunucu_id, zaman, cpu, degisim
```

```test
eq(sutunlar, ["sunucu_id", "zaman", "cpu", "degisim"], "sütunlar")
eq([r[3] for r in sonuc], [None, 18, 14, -3, None, 13, 16, -3, None, 1, 13, 6], "grup sınırında boş")
eq([r[0] for r in sonuc], [1] * 4 + [4] * 4 + [8] * 4, "sıra")
```

```solution
olcumler
| sort by sunucu_id asc, zaman asc
| extend degisim = iff(sunucu_id == prev(sunucu_id), cpu - prev(cpu), int(null))
| project sunucu_id, zaman, cpu, degisim
```

```hint
Başlangıç kodunda 4 ve 8 numaralı sunucuların ilk ölçümü, önceki sunucunun son ölçümüyle karşılaştırılıyor.
```

```hint
`iff(sunucu_id == prev(sunucu_id), cpu - prev(cpu), int(null))`.
```
:::

::: gorev 200 sınırını aşan saat
Her sunucunun CPU değerlerini saat saat biriktir (sunucu değişince toplam sıfırdan başlasın) ve birikimli toplamın **ilk kez 200'ü aştığı** ölçümü getir: `sunucu_id`, `zaman`, `toplam`; sunucuya göre artan.

```starter
olcumler
| sort by sunucu_id asc, zaman asc
| extend toplam = row_cumsum(cpu)
| where toplam > 200
```

```test
eq(sutunlar, ["sunucu_id", "zaman", "toplam"], "sütunlar")
eq(sonuc, [(1, "2026-10-19 11:00", 239), (4, "2026-10-19 10:00", 228), (8, "2026-10-19 10:00", 225)], "her sunucu için bir satır")
```

```solution
olcumler
| sort by sunucu_id asc, zaman asc
| extend toplam = row_cumsum(cpu, sunucu_id != prev(sunucu_id))
| where toplam > 200
| summarize arg_min(zaman, toplam) by sunucu_id
| sort by sunucu_id asc
```

```hint
Toplamın her sunucuda sıfırdan başlaması için restart: `row_cumsum(cpu, sunucu_id != prev(sunucu_id))`.
```

```hint
200'ü aşan satırlardan her sunucunun **ilkini** almak için KQ14'teki `arg_min(zaman, toplam) by sunucu_id`.
```
:::

::: gorev En uzun sessizlik
Her kullanıcının (boş kullanıcılar hariç) **ardışık iki isteği arasındaki en uzun süreyi** getir: `kullanici`, `en_uzun` (süre); en uzundan kısaya. Tek isteği olan kullanıcı listede olmasın.

```starter
istekler
| where isnotempty(kullanici)
| summarize ilk = min(zaman), son = max(zaman) by kullanici
```

```test
eq(sutunlar, ["kullanici", "en_uzun"], "sütunlar")
eq(sonuc, [("zeynep", "02:27:00"), ("can", "01:27:00"), ("ayse", "01:02:00"), ("mert", "01:00:00")], "dört kullanıcı")
ok(kullanir("next") or kullanir("prev"), "komşu satıra next ya da prev ile bak")
```

```solution
istekler
| where isnotempty(kullanici)
| sort by kullanici asc, zaman asc
| extend ara = iff(next(kullanici) == kullanici, next(zaman) - zaman, timespan(null))
| where isnotnull(ara)
| summarize en_uzun = max(ara) by kullanici
| sort by en_uzun desc
```

```hint
Kullanıcıya sonra zamana göre sırala; ara `next(zaman) - zaman`, ama yalnızca sonraki satır aynı kullanıcınınsa: `iff(next(kullanici) == kullanici, ..., timespan(null))`.
```

```hint
Boş araları at, sonra `summarize en_uzun = max(ara) by kullanici`.
```
:::
