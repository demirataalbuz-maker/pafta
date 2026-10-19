---
id: kq02
title: project, extend ve Hesaplanan Sütunlar
summary: Sütun seçmek, atmak ve yeniden adlandırmak; extend ile yeni sütun; iff, case, strcat ve print.
---

::: anlat Sütunlarla çalışmak
| İşleç | Ne yapar |
|---|---|
| `project a, b, c = ifade` | yalnızca bu sütunlar kalır (SQL'deki SELECT listesi) |
| `project-away a, b` | bu sütunlar atılır, gerisi kalır |
| `project-rename yeni = eski` | yeniden adlandırır |
| `extend c = ifade` | **var olan bütün sütunlar** kalır, yanına yenisi eklenir |

```kql
sunucular
| extend bos = 100 - cpu, ram_mb = ram_gb * 1024   #! iki yeni sütun
| project ad, cpu, bos, ram_mb
| take 4
```

`extend`'in gücü, sütun listesini baştan yazmadan bir hesap ekleyebilmendir. Bir `extend` içinde az önce tanımladığın sütunu hemen kullanabilirsin:

```kql
sunucular
| extend bos = 100 - cpu, durum = iff(bos < 20, "dolu", "rahat")
| project ad, bos, durum
```

### Koşullu değerler
`iff(koşul, doğruysa, yanlışsa)` iki seçenekli, `case(koşul1, değer1, koşul2, değer2, ..., varsayılan)` çok seçeneklidir:

```kql
sunucular
| extend yuk = case(cpu >= 80, "yüksek", cpu >= 50, "orta", "düşük")
| project ad, cpu, yuk
```

`strcat` metinleri birleştirir (KQL'de `+` metin birleştirmez):

```kql
sunucular
| project etiket = strcat(ad, " @ ", rol)
| take 3
```

### print: tablosuz hesap
`print` tek satırlık bir sonuç üretir; bir ifadeyi denemek için idealdir:

```kql
print toplam = 2 + 3 * 4, metin = strcat("KQL", "!"), uzunluk = strlen("Sentinel")
```

> [!TUZAK]
> İki tam sayının bölümü tam sayıdır: `7 / 2` sonucu `3`. Ondalık için bir tarafı ondalık yaz: `7 / 2.0`. Yüzde hesaplarında `100.0 * a / b` alışkanlığı edin.
:::

::: tahmin
Tek satır, dört sütun:

```kql
print a = 7 / 2, b = 7 / 2.0, c = strcat("SQL", "+", "KQL"), d = iff(3 > 2, "evet", "hayır")
```

???

`3|3.5|SQL+KQL|evet`. Tam sayı bölmesi küsuratı atar, `2.0` olunca sonuç ondalık olur. `strcat` parçaları yan yana koyar. 3 > 2 doğru olduğu için `iff` ilk değeri verir.
:::

::: gorev Boş kapasite
Her sunucunun adını ve CPU'da kalan boş yüzdeyi `bos` adıyla getir.

```starter
sunucular
| project ad, cpu
```

```test
eq(sutunlar, ["ad", "bos"], "sütunlar: ad, bos")
eq(sorted(sonuc), sorted(sorgu("SELECT ad, 100 - cpu FROM sunucular")), "bos = 100 - cpu")
```

```solution
sunucular
| extend bos = 100 - cpu
| project ad, bos
```

```hint
`extend bos = 100 - cpu` ile ekle, sonra `project ad, bos`. Ya da tek adımda: `project ad, bos = 100 - cpu`.
```
:::

::: gorev Yük sınıfı
Her sunucu için `ad` ve `yuk` sütunlarını getir: CPU 80 ve üstüyse `yüksek`, 50 ve üstüyse `orta`, değilse `düşük`.

```starter
sunucular
| extend yuk = "düşük"
| project ad, yuk
```

```test
eq(sutunlar, ["ad", "yuk"], "sütunlar: ad, yuk")
beklenen = sorgu("SELECT ad, CASE WHEN cpu >= 80 THEN 'yüksek' WHEN cpu >= 50 THEN 'orta' ELSE 'düşük' END FROM sunucular")
eq(sorted(sonuc), sorted(beklenen), "sınıflar doğru")
```

```solution
sunucular
| extend yuk = case(cpu >= 80, "yüksek", cpu >= 50, "orta", "düşük")
| project ad, yuk
```

```hint
`case(cpu >= 80, "yüksek", cpu >= 50, "orta", "düşük")`: koşullar sırayla denenir, son değer varsayılandır.
```
:::

::: gorev Etiketler
Ankara'daki sunucular için `ad (rol)` biçiminde tek bir `etiket` sütunu getir; ör. `web03 (web)`.

```starter
sunucular
| where sehir == "Ankara"
| project ad
```

```test
eq(sutunlar, ["etiket"], "tek sütun: etiket")
eq(sorted(r[0] for r in sonuc), ["db02 (veritabanı)", "vpn01 (ağ geçidi)", "web03 (web)"], "üç etiket")
```

```solution
sunucular
| where sehir == "Ankara"
| project etiket = strcat(ad, " (", rol, ")")
```

```hint
`strcat(ad, " (", rol, ")")`: boşluk ve parantezler de birer parça.
```
:::
