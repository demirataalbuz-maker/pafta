---
id: kq11
title: Proje · Haftalık Operasyon Özeti
summary: SQL yolundaki haftalık raporu KQL ile yeniden kurmak; countif ile koşullu sayım, zincirleme join ve sıralı ilk N.
---

::: anlat Proje tanımı
SQL yolunun son projesindeki haftalık raporu hatırla: **12–18 Ekim 2026** haftası için bilet özeti. Aynı soruları bu kez KQL ile cevaplayacaksın. Gerçek hayatta bu rapor büyük ihtimalle bir Sentinel çalışma kitabında (workbook) ya da zamanlanmış bir sorguda yaşar.

Üç bölüm:

1. **Haftanın özeti**: açılan, çözülen ve hafta sonunda açık kalan bilet sayısı
2. **Ekip yükü**: bilet atanmış ekiplerin açık ve hafta içinde çözülen bilet sayıları
3. **Sıcak noktalar**: hafta içinde en çok bilet açılan beş sunucu

Hafta aralığını SQL'deki gibi **yarı açık** yaz: başlangıç dahil, bitiş hariç.

```kql
biletler
| where acilis >= datetime(2026-10-12) and acilis < datetime(2026-10-19)
| count
```

`countif` ile tek bir `summarize` içinde birden çok koşullu sayım yapılır:

```kql
biletler
| summarize kritik = countif(oncelik == "kritik"), yuksek = countif(oncelik == "yüksek"), toplam = count()
```

> [!İPUCU]
> Uzun KQL sorgularında her `|` adımını ayrı satıra yaz ve adımların arasına `//` ile kısa notlar düş. Bir sorgunun hangi adımda yanlış sonuç verdiğini bulmanın en hızlı yolu, sondan adım silerek ara sonuçlara bakmaktır.
:::

::: gorev 1 · Haftanın özeti
Tek satırda üç sütun getir: `acilan` (hafta içinde açılan), `cozulen` (hafta içinde kapanan), `acik_kalan` (hafta içinde açılmış ama hafta bittiğinde hâlâ kapanmamış olan: hiç kapanmamış ya da hafta bittikten sonra kapanmış).

```cikti
19|10|9
```

```starter
biletler
| count
```

```test
eq(sutunlar, ["acilan", "cozulen", "acik_kalan"], "sütunlar: acilan, cozulen, acik_kalan")
eq(sonuc, [(19, 10, 9)], "19 açılan, 10 çözülen, 9 açık kalan")
eq(dene("DELETE FROM biletler WHERE id IN (1, 19);"), [(17, 9, 8)], "veri değişince de doğru saymalı (sabit sayı yazma)")
```

```solution
biletler
| summarize
    acilan = countif(acilis >= datetime(2026-10-12) and acilis < datetime(2026-10-19)),
    cozulen = countif(kapanis >= datetime(2026-10-12) and kapanis < datetime(2026-10-19)),
    acik_kalan = countif(acilis >= datetime(2026-10-12) and acilis < datetime(2026-10-19)
                         and (isnull(kapanis) or kapanis >= datetime(2026-10-19)))
```

```hint
Üç sayım tek `summarize` içinde: `acilan = countif(...)`, `cozulen = countif(...)`, `acik_kalan = countif(...)`.
```

```hint
Açık kalan: hafta içinde açılmış **ve** (`isnull(kapanis)` **ya da** `kapanis >= datetime(2026-10-19)`). Parantezleri unutma.
```
:::

::: gorev 2 · Ekip yükü
Biletleri atandıkları kişinin ekibine bağla ve her ekip için `acik` (şu anda açık) ve `cozulen_hafta` (hafta içinde kapanan) sayılarını getir. Sıralama: `cozulen_hafta` azalan, eşitlikte `ekip` artan.

```cikti
Altyapı|1|7
Ağ|2|1
Uygulama|0|1
Veritabanı|2|1
```

```starter
biletler
| summarize adet = count() by atanan_id
```

```test
eq(sutunlar, ["ekip", "acik", "cozulen_hafta"], "sütunlar: ekip, acik, cozulen_hafta")
eq(sonuc, [("Altyapı", 1, 7), ("Ağ", 2, 1), ("Uygulama", 0, 1), ("Veritabanı", 2, 1)], "ekiplere göre sayılar")
```

```solution
biletler
| join kind=inner (personel | project atanan_id = id, ekip_id) on atanan_id
| join kind=inner (ekipler | project ekip_id = id, ekip = ad) on ekip_id
| summarize acik = countif(durum == "açık"),
            cozulen_hafta = countif(kapanis >= datetime(2026-10-12) and kapanis < datetime(2026-10-19))
            by ekip
| sort by cozulen_hafta desc, ekip asc
```

```hint
İki join: bilet → kişi (`personel`, anahtar `atanan_id`), kişi → ekip (`ekipler`, anahtar `ekip_id`). Sağ tarafları `project` ile anahtar adına getir.
```

```hint
Sıralamada yönleri ayrı ayrı yaz: `sort by cozulen_hafta desc, ekip asc`.
```
:::

::: gorev 3 · Sıcak noktalar
Hafta içinde açılan biletleri sunucuya göre say; en çok bileti olan **beş** sunucunun adını (`ad`) ve bilet sayısını (`bilet`) getir. Eşitlikte ada göre artan sırala. Sunucusu olmayan biletleri sayma.

```cikti
db01|3
dc01|2
izleme01|2
web01|2
web02|2
```

```starter
biletler
| summarize bilet = count() by sunucu_id
| take 5
```

```test
eq(sutunlar, ["ad", "bilet"], "sütunlar: ad, bilet")
eq(sonuc, [("db01", 3), ("dc01", 2), ("izleme01", 2), ("web01", 2), ("web02", 2)], "sıcak noktalar")
```

```solution
biletler
| where acilis >= datetime(2026-10-12) and acilis < datetime(2026-10-19)
| where isnotnull(sunucu_id)
| summarize bilet = count() by sunucu_id
| join kind=inner (sunucular | project sunucu_id = id, ad) on sunucu_id
| sort by bilet desc, ad asc
| take 5
| project ad, bilet
```

```hint
Önce zaman aralığı, sonra `summarize ... by sunucu_id`, sonra sunucu adını almak için `join kind=inner`.
```

```hint
Eşitlikleri bozmak için iki anahtarla sırala: `sort by bilet desc, ad asc`, ardından `take 5`.
```
:::
