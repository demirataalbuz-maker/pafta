---
id: sq11
title: Küme İşlemleri
summary: UNION ile UNION ALL farkı, INTERSECT ve EXCEPT, sütun uyumu, birleşik sonucun sıralanması ve farklı kaynakları tek zaman çizelgesinde toplamak.
---

::: anlat Sorguları üst üste koymak
JOIN tabloları **yan yana** birleştirir. Küme işlemleri ise iki sorgunun sonucunu **üst üste** koyar:

| İşlem | Sonuç |
|---|---|
| `A UNION B` | ikisindeki satırlar, **tekrarlar atılarak** |
| `A UNION ALL B` | ikisindeki satırlar, tekrarlar dahil (daha hızlı: tekrar aramaz) |
| `A INTERSECT B` | ikisinde de olan satırlar |
| `A EXCEPT B` | A'da olup B'de olmayan satırlar |

İki sorgunun **aynı sayıda** sütun döndürmesi gerekir; sonucun sütun adları ilk sorgudan gelir. `ORDER BY` en sona yazılır ve birleşik sonucun tamamına uygulanır:

```sql
SELECT ad, 'sunucu' AS tur FROM sunucular WHERE cpu > 80
UNION ALL
SELECT ad, 'çalışan' FROM personel WHERE ekip_id IS NULL
ORDER BY ad;
```

Küme işlemlerinin en kullanışlı yanı, **farklı yapıdaki olayları tek bir zaman çizelgesinde** toplamaktır. Biletlerin açılışı ve kapanışı ayrı sütunlarda durur; ikisini satıra çevirip birleştirmek bütün hareketi sırayla gösterir:

```sql
SELECT acilis AS zaman, id, 'açıldı' AS olay FROM biletler
UNION ALL
SELECT kapanis, id, 'kapandı' FROM biletler WHERE kapanis IS NOT NULL
ORDER BY zaman
LIMIT 6;
```

`EXCEPT` "eşi olmayanları bul" sorusunun en okunur cevabıdır:

```sql
SELECT id FROM sunucular
EXCEPT
SELECT sunucu_id FROM biletler WHERE durum = 'açık';
```

> [!TUZAK]
> `UNION` her seferinde tekrarları arar: büyük sonuçlarda gereksiz yere yavaştır ve gerçekten tekrar eden satırları (aynı saatte iki aynı olay) **sessizce siler**. Tekrar olmayacağını biliyorsan ya da tekrarlar anlamlıysa `UNION ALL` kullan.
:::

::: tahmin
İki sorgu, üç satır:

```sql
SELECT sehir FROM sunucular WHERE rol = 'web'
UNION
SELECT sehir FROM sunucular WHERE rol = 'veritabanı'
ORDER BY 1;

SELECT COUNT(*) FROM (
    SELECT sehir FROM sunucular WHERE rol = 'web'
    UNION ALL
    SELECT sehir FROM sunucular WHERE rol = 'veritabanı'
);
```

???

`Ankara`, `İstanbul`, sonra `5`. Web sunucuları İstanbul, İstanbul, Ankara'da; veritabanları İstanbul ve Ankara'da. `UNION` tekrarları atar ve iki şehir kalır. `UNION ALL` beş satırın hepsini tutar.
:::

::: gorev Olay zaman çizelgesi
1–4 numaralı biletlerin açılış ve kapanışlarını tek bir zaman çizelgesinde göster: `zaman`, `id`, `olay` (`açıldı` ya da `kapandı`) sütunları, zamana göre sıralı. Kapanmamış biletin kapanış satırı olmasın.

```starter
SELECT acilis AS zaman, id, 'açıldı' AS olay
FROM biletler
WHERE id <= 4
ORDER BY zaman;
```

```test
eq(sutunlar, ["zaman", "id", "olay"], "sütunlar: zaman, id, olay")
eq(sonuc, [("2026-10-12 08:15", 1, "açıldı"), ("2026-10-12 09:00", 2, "açıldı"), ("2026-10-12 11:45", 1, "kapandı"),
           ("2026-10-12 14:20", 3, "açıldı"), ("2026-10-13 07:05", 4, "açıldı"), ("2026-10-13 09:35", 4, "kapandı"),
           ("2026-10-13 10:00", 2, "kapandı")], "yedi olay, zaman sırasıyla")
ok(kullanir("union all"), "UNION ALL kullan")
```

```solution
SELECT acilis AS zaman, id, 'açıldı' AS olay FROM biletler WHERE id <= 4
UNION ALL
SELECT kapanis, id, 'kapandı' FROM biletler WHERE id <= 4 AND kapanis IS NOT NULL
ORDER BY zaman;
```

```hint
İkinci sorgu kapanışları aynı üç sütun düzeninde versin: `SELECT kapanis, id, 'kapandı' ...`. `ORDER BY` en sonda, birleşik sonuca uygulanır.
```
:::

::: gorev Açık bileti olmayan sunucular
Hiç **açık** bileti olmayan sunucuların adlarını alfabetik getir. `EXCEPT` kullan.

```starter
SELECT ad
FROM sunucular
ORDER BY ad;
```

```test
eq([r[0] for r in sonuc], ["cache01", "dc02", "vpn01", "web01", "web02", "yedek01"], "altı sunucu")
ok(kullanir("except"), "EXCEPT kullan")
```

```solution
SELECT ad
FROM sunucular
WHERE id IN (
    SELECT id FROM sunucular
    EXCEPT
    SELECT sunucu_id FROM biletler WHERE durum = 'açık'
)
ORDER BY ad;
```

```hint
Kimlik kümelerinin farkı: `SELECT id FROM sunucular EXCEPT SELECT sunucu_id FROM biletler WHERE durum = 'açık'`. Adları almak için bunu `WHERE id IN (...)` içinde kullan.
```
:::

::: gorev Hem açan hem çözen
Hem en az bir bilet **açmış** hem de kendisine en az bir bilet **atanmış** çalışanların adlarını alfabetik getir. `INTERSECT` kullan.

```starter
SELECT DISTINCT p.ad
FROM personel AS p
JOIN biletler AS b ON b.acan_id = p.id
ORDER BY p.ad;
```

```test
eq([r[0] for r in sonuc], ["Ayşe", "Can", "Ece", "Elif", "Kerem", "Mert", "Zeynep"], "yedi kişi")
ok(kullanir("intersect"), "INTERSECT kullan")
```

```solution
SELECT ad
FROM personel
WHERE id IN (
    SELECT acan_id FROM biletler
    INTERSECT
    SELECT atanan_id FROM biletler
)
ORDER BY ad;
```

```hint
`SELECT acan_id FROM biletler INTERSECT SELECT atanan_id FROM biletler` iki rolü de üstlenmiş kimlikleri verir.
```
:::
