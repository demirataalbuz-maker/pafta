---
id: kq19
title: Proje · Hizmet Sağlık Panosu
summary: Web istek günlüğünden saatlik sağlık raporu kurmak; istek hacmi, hata oranı ve p95 gecikme, eşiklere göre durum etiketi ve kimlikleri kalıba indirerek en sorunlu uç noktaları bulmak.
---

::: anlat Proje tanımı
Uygulama ekibi her sabah bir **sağlık panosu** istiyor: saat saat kaç istek geldi, hataların oranı ne, kullanıcılar ne kadar bekledi, hangi saat kırmızı. Bu panoyu üç sorguda kuracaksın. Her biri, gerçek bir Sentinel çalışma kitabında (workbook) ya da Azure Monitor panosunda bir kutucuk olurdu.

| Adım | Soru | Kullanacağın araçlar |
|---|---|---|
| 1 | saat başına hacim, hata oranı, p95 | `bin`, `countif`, `percentile`, oran |
| 2 | hangi saat normal, uyarı, kritik? | `case` ile eşik kuralları |
| 3 | sorun hangi uç noktada? | `replace_regex` ile kalıp, `top` |

### Ölçülerin anlamı
- **Hata oranı**: 500 ve üstü durum kodları sunucu tarafı hatalardır; 4xx ise çoğunlukla istemcinin hatasıdır ve ayrı izlenir.
- **p95**: isteklerin %95'i bu süreden kısa bitti. Ortalamanın gizlediği yavaşlığı gösterir (KQ14).
- **Uç nokta kalıbı**: `/api/bilet/42` ile `/api/bilet/17` aynı uç noktadır. Kimlikleri `{id}` ile değiştirmeden gruplarsan her bilet ayrı bir satır olur ve sorun dağılır.

> [!İPUCU]
> Panoda her kutucuğun eşiğini sorgunun içinde `let` ile tanımla (`let kritik_oran = 20.0;`). Eşik değiştiğinde tek bir satırı değiştirirsin ve eşiğin ne olduğu sorguyu okuyan herkes için görünür olur.
:::

::: tahmin
Tek satır yazar:

```kql
istekler
| summarize hata = countif(durum >= 500), istek = count()
| extend oran = round(100.0 * hata / istek, 1)
```

???

`4|26|15.4`. 26 istekten 4'ü 500 ve üstü durum koduyla bitti: 4 / 26 × 100 = 15.38, bir ondalığa yuvarlanınca 15.4.
:::

::: gorev 1 · Saatlik özet
Her saat için istek sayısını, 500 ve üstü durum kodlu istek sayısını, hata oranını (yüzde, bir ondalık) ve p95 süreyi getir: `saat`, `istek`, `hata`, `hata_orani`, `p95`; saate göre artan.

```starter
istekler
| summarize istek = count() by saat = bin(zaman, 1h)
| sort by saat asc
```

```test
eq(sutunlar, ["saat", "istek", "hata", "hata_orani", "p95"], "sütunlar")
eq(sonuc, [("2026-10-19 08:00", 7, 0, 0.0, 850), ("2026-10-19 09:00", 8, 3, 37.5, 2410),
           ("2026-10-19 10:00", 7, 1, 14.3, 2600), ("2026-10-19 11:00", 4, 0, 0.0, 280)], "dört saat")
```

```solution
istekler
| summarize istek = count(), hata = countif(durum >= 500), p95 = percentile(sure_ms, 95) by saat = bin(zaman, 1h)
| extend hata_orani = round(100.0 * hata / istek, 1)
| project saat, istek, hata, hata_orani, p95
| sort by saat asc
```

```hint
Tek `summarize` içinde üç toplama: `count()`, `countif(durum >= 500)`, `percentile(sure_ms, 95)`; gruplama `by saat = bin(zaman, 1h)`.
```

```hint
Oranı `extend` ile sonra hesapla ve sütunları `project` ile istenen sıraya koy.
```
:::

::: gorev 2 · Durum etiketi
Saatlik özeti şu kurallarla etiketle ve `saat`, `hata_orani`, `p95`, `etiket` sütunlarıyla saate göre artan getir:

- hata oranı %20 ve üstü → `"kritik"`
- değilse, hata oranı %5 ve üstü **ya da** p95 2000 ms ve üstü → `"uyarı"`
- değilse → `"normal"`

```starter
istekler
| summarize istek = count(), hata = countif(durum >= 500), p95 = percentile(sure_ms, 95) by saat = bin(zaman, 1h)
| extend hata_orani = round(100.0 * hata / istek, 1)
| project saat, hata_orani, p95
| sort by saat asc
```

```test
eq(sutunlar, ["saat", "hata_orani", "p95", "etiket"], "sütunlar")
eq([(r[0], r[3]) for r in sonuc], [("2026-10-19 08:00", "normal"), ("2026-10-19 09:00", "kritik"),
                                   ("2026-10-19 10:00", "uyarı"), ("2026-10-19 11:00", "normal")], "etiketler")
ok(kullanir("case"), "kuralları case ile yaz")
```

```solution
istekler
| summarize istek = count(), hata = countif(durum >= 500), p95 = percentile(sure_ms, 95) by saat = bin(zaman, 1h)
| extend hata_orani = round(100.0 * hata / istek, 1)
| extend etiket = case(hata_orani >= 20, "kritik", hata_orani >= 5 or p95 >= 2000, "uyarı", "normal")
| project saat, hata_orani, p95, etiket
| sort by saat asc
```

```hint
`case()` koşulları sırayla dener; ilk doğru olanın değerini verir. Önce en ağır koşulu yaz.
```

```hint
`case(hata_orani >= 20, "kritik", hata_orani >= 5 or p95 >= 2000, "uyarı", "normal")`.
```
:::

::: gorev 3 · En sorunlu uç noktalar
Yollardaki sondaki sayısal kimliği `{id}` ile değiştirerek uç nokta kalıbı (`yol_kalibi`) çıkar. Her kalıp için istek sayısını, **400 ve üstü** durum kodlu istek sayısını (`hata`) ve p95 süreyi hesapla; en çok hatası olan üç kalıbı, eşitlikte p95'i yüksek olan önde gelecek şekilde getir: `yol_kalibi`, `istek`, `hata`, `p95`.

```starter
istekler
| summarize istek = count(), hata = countif(durum >= 400), p95 = percentile(sure_ms, 95) by yol
| top 3 by hata desc
```

```test
eq(sutunlar, ["yol_kalibi", "istek", "hata", "p95"], "sütunlar")
eq(sonuc, [("/api/rapor", 8, 4, 2600), ("/api/bilet/{id}", 3, 1, 180), ("/api/bilet", 8, 0, 310)], "ilk üç kalıp")
```

```solution
istekler
| extend yol_kalibi = replace_regex(yol, @"/\d+$", "/{id}")
| summarize istek = count(), hata = countif(durum >= 400), p95 = percentile(sure_ms, 95) by yol_kalibi
| top 3 by hata desc, p95 desc
```

```hint
Kalıp: `replace_regex(yol, @"/\d+$", "/{id}")`. `/api/bilet/42` ve `/api/bilet/17` aynı satıra düşer.
```

```hint
`top 3 by hata desc, p95 desc`: eşit hatada p95'i yüksek olan önde.
```
:::
