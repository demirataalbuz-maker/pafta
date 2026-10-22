---
id: sq11
title: Pencere Fonksiyonları
summary: Satırları silmeden hesaplamak; ROW_NUMBER, RANK, PARTITION BY, LAG/LEAD, kümülatif toplam ve kayan ortalama, grup başına ilk N.
kazanim: 1Z0071 14.3
---

::: anlat Satırı koru, yanına hesap ekle
`GROUP BY` satırları gruba indirir: her rol için tek satır kalır. **Pencere fonksiyonu** ise her satırı yerinde bırakır ve yanına, o satırın "penceresinden" hesaplanan bir değer ekler. Ayırt edici işareti `OVER (...)`'dır:

```sql
SELECT ad, cpu,
       RANK() OVER (ORDER BY cpu DESC) AS sira,           #! CPU'ya göre kaçıncı
       round(AVG(cpu) OVER (), 1)      AS genel_ort        #! boş pencere = bütün tablo
FROM sunucular
ORDER BY sira;
```

`PARTITION BY` pencereyi gruplara böler; sıralama her grupta baştan başlar:

```sql
SELECT ad, rol, cpu,
       ROW_NUMBER() OVER (PARTITION BY rol ORDER BY cpu DESC) AS rol_sira
FROM sunucular
ORDER BY rol, rol_sira;
```

| Fonksiyon | Ne verir |
|---|---|
| `ROW_NUMBER()` | 1, 2, 3, ... (eşitlikte de farklı numara) |
| `RANK()` | eşitler aynı sırayı alır, sonra atlar: 1, 2, 2, 4 |
| `DENSE_RANK()` | eşitler aynı sırayı alır, atlamaz: 1, 2, 2, 3 |
| `LAG(x)`, `LEAD(x)` | önceki / sonraki satırdaki x |
| `SUM(x) OVER (ORDER BY ...)` | o satıra kadarki kümülatif toplam |

### Zaman serisi: önceki ölçümle fark
```sql
SELECT s.ad, o.zaman, o.cpu,
       o.cpu - LAG(o.cpu) OVER (PARTITION BY o.sunucu_id ORDER BY o.zaman) AS degisim,
       round(AVG(o.cpu) OVER (PARTITION BY o.sunucu_id ORDER BY o.zaman
                              ROWS BETWEEN 1 PRECEDING AND CURRENT ROW), 1) AS kayan_ort
FROM olcumler AS o
JOIN sunucular AS s ON s.id = o.sunucu_id
ORDER BY s.ad, o.zaman;
```

`ROWS BETWEEN 1 PRECEDING AND CURRENT ROW` pencereyi "bu satır ve bir öncesi" ile sınırlar: iki ölçümlük kayan ortalama.

### Grup başına ilk N
Pencere fonksiyonu `WHERE`'de kullanılamaz (WHERE önce çalışır). Bir CTE'de numarala, dışarıda süz:

```sql
WITH sirali AS (
    SELECT rol, ad, cpu,
           ROW_NUMBER() OVER (PARTITION BY rol ORDER BY cpu DESC) AS n
    FROM sunucular
)
SELECT rol, ad, cpu FROM sirali WHERE n = 1 ORDER BY cpu DESC;
```

> [!NOT]
> Log dillerindeki karşılıkları: KQL'de `serialize` sonrası `prev()`, `next()` ve `row_cumsum()`; SPL'de `streamstats`. "Bir önceki olaya göre ne değişti?" sorusu izleme ve kayıt analizinde sürekli sorulur.
:::

::: tahmin
db01'in dört ölçümü için iki sütun yaz (`cpu|fark`):

```sql
SELECT cpu, cpu - LAG(cpu) OVER (ORDER BY zaman) AS fark
FROM olcumler
WHERE sunucu_id = 4
ORDER BY zaman;
```

???

`62|NULL`, `75|13`, `91|16`, `88|-3`. İlk ölçümün öncesi yoktur, `LAG` NULL döner ve NULL ile çıkarma NULL verir. Sonraki her satır bir önceki ölçümle karşılaştırılır.
:::

::: gorev Rol içinde sıra
Her sunucu için `ad`, `rol`, `cpu` ve rolü içindeki CPU sırasını (`rol_sira`, en yüksek CPU 1) getir. Sonucu role, sonra `rol_sira`'ya göre sırala.

```starter
SELECT ad, rol, cpu, 1 AS rol_sira
FROM sunucular
ORDER BY rol;
```

```test
eq(sutunlar, ["ad", "rol", "cpu", "rol_sira"], "sütunlar: ad, rol, cpu, rol_sira")
eq(sonuc, sorgu("SELECT ad, rol, cpu, ROW_NUMBER() OVER (PARTITION BY rol ORDER BY cpu DESC) AS n FROM sunucular ORDER BY rol, n"), "rol içi sıralar")
```

```solution
SELECT ad, rol, cpu,
       ROW_NUMBER() OVER (PARTITION BY rol ORDER BY cpu DESC) AS rol_sira
FROM sunucular
ORDER BY rol, rol_sira;
```

```hint
`ROW_NUMBER() OVER (PARTITION BY rol ORDER BY cpu DESC)`.
```
:::

::: gorev Her rolün en yoğunu
Her rolden **CPU'su en yüksek** sunucuyu getir: `rol`, `ad`, `cpu`; CPU'ya göre azalan sırala. Pencere fonksiyonuyla çöz.

```starter
SELECT rol, ad, cpu
FROM sunucular
ORDER BY cpu DESC;
```

```test
eq(sonuc, [("veritabanı", "db01", 91), ("önbellek", "cache01", 84), ("web", "web01", 72), ("izleme", "izleme01", 55),
           ("ağ geçidi", "vpn01", 38), ("dizin", "dc01", 33), ("yedek", "yedek01", 12), ("test", "test01", 3)], "her rolün en yoğunu")
ok(kullanir("over"), "pencere fonksiyonu (OVER) kullan")
```

```solution
WITH sirali AS (
    SELECT rol, ad, cpu,
           ROW_NUMBER() OVER (PARTITION BY rol ORDER BY cpu DESC) AS n
    FROM sunucular
)
SELECT rol, ad, cpu
FROM sirali
WHERE n = 1
ORDER BY cpu DESC;
```

```hint
Pencere fonksiyonu WHERE'de kullanılamaz. Önce bir CTE'de `ROW_NUMBER()` ile numarala, dıştaki sorguda `WHERE n = 1`.
```
:::

::: gorev Kümülatif bilet sayısı
Her gün için `gun` (`YYYY-AA-GG`), o gün açılan bilet sayısı (`adet`) ve o güne kadarki toplam (`toplam`) sütunlarını gün sırasıyla getir.

```cikti
2026-10-12|3|3
2026-10-13|3|6
...
2026-10-19|1|20
```

```starter
SELECT date(acilis) AS gun, COUNT(*) AS adet
FROM biletler
GROUP BY gun;
```

```test
eq(sutunlar, ["gun", "adet", "toplam"], "sütunlar: gun, adet, toplam")
eq([r[2] for r in sonuc], [3, 6, 9, 12, 15, 17, 19, 20], "kümülatif toplamlar")
eq([r[0] for r in sonuc][:2], ["2026-10-12", "2026-10-13"], "gün sırası")
```

```solution
WITH gunluk AS (
    SELECT date(acilis) AS gun, COUNT(*) AS adet
    FROM biletler
    GROUP BY gun
)
SELECT gun, adet,
       SUM(adet) OVER (ORDER BY gun) AS toplam
FROM gunluk
ORDER BY gun;
```

```hint
Önce günlük sayıları çıkar (GROUP BY), sonra onların üzerinde `SUM(adet) OVER (ORDER BY gun)`.
```
:::
