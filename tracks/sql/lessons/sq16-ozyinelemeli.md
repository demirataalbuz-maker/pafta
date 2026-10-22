---
id: sq16
title: Özyinelemeli CTE Ustalığı
summary: WITH RECURSIVE ile sayı ve tarih dizisi üretmek, eksik günleri sıfırla doldurmak, hiyerarşide yol ve derinlik çıkarmak, bütün alt kadroyu saymak ve sonsuz döngüye karşı korunmak.
kazanim: 1Z0071 16.7
---

::: anlat Özyineleme nasıl ilerler
SQ07'da yönetici zincirini gördün. `WITH RECURSIVE` iki parçadan oluşur: bir **başlangıç** sorgusu ve önceki turda eklenen satırlara bakarak yeni satırlar üreten **özyinelemeli** sorgu. Yeni satır üretilmeyince durur:

```sql
WITH RECURSIVE sayi(n) AS (
    SELECT 1                                  -- başlangıç
    UNION ALL
    SELECT n + 1 FROM sayi WHERE n < 5        -- her tur: bir öncekinden üret; koşul durdurur
)
SELECT group_concat(n, ',') FROM sayi;
```

### Takvim üretmek ve boşlukları doldurmak
Gruplama sorguları yalnızca verisi **olan** günleri verir; bilet açılmayan gün sonuçta hiç görünmez. Bir grafik ya da günlük rapor için eksik günler sıfırla doldurulmalıdır. Önce bir takvim üretilir, sonra veri ona `LEFT JOIN` ile bağlanır:

```sql
WITH RECURSIVE takvim(gun) AS (
    SELECT '2026-10-10'
    UNION ALL
    SELECT date(gun, '+1 day') FROM takvim WHERE gun < '2026-10-14'
)
SELECT t.gun, COUNT(b.id) AS bilet
FROM takvim AS t
LEFT JOIN biletler AS b ON date(b.acilis) = t.gun
GROUP BY t.gun
ORDER BY t.gun;
```

### Hiyerarşide yol ve derinlik
Özyinelemeli sorgu her turda bir öncekinin değerlerini taşıyabilir: zincirin yolunu metin olarak biriktirmek ve derinliği saymak:

```sql
WITH RECURSIVE zincir(id, ad, yol, derinlik) AS (
    SELECT id, ad, ad, 0 FROM personel WHERE yonetici_id IS NULL
    UNION ALL
    SELECT p.id, p.ad, z.yol || ' > ' || p.ad, z.derinlik + 1
    FROM personel AS p
    JOIN zincir AS z ON p.yonetici_id = z.id
)
SELECT derinlik, yol FROM zincir ORDER BY yol;
```

> [!TUZAK]
> Veride bir döngü varsa (A'nın yöneticisi B, B'nin yöneticisi A) özyineleme hiç bitmez. Korunmak için ya bir derinlik sınırı koy (`WHERE derinlik < 20`) ya da yolu taşıyıp aynı kimliğe ikinci kez girmeyi engelle: `WHERE z.yol NOT LIKE '%/' || p.id || '/%'`.
:::

::: tahmin
Tek satır yazar:

```sql
WITH RECURSIVE ikilik(n, kuvvet) AS (
    SELECT 0, 1
    UNION ALL
    SELECT n + 1, kuvvet * 2 FROM ikilik WHERE n < 10
)
SELECT COUNT(*), MAX(kuvvet), SUM(kuvvet) FROM ikilik;
```

???

`11|1024|2047`. n 0'dan 10'a kadar 11 satır üretir. Her turda kuvvet ikiye katlanır, en büyüğü 2¹⁰ = 1024 olur. 1 + 2 + … + 1024 toplamı 2¹¹ − 1 = 2047'dir.
:::

::: gorev Eksik günleri doldur
`2026-10-10` ile `2026-10-20` arasındaki (ikisi dahil) **her gün** için açılan bilet sayısını getir; bilet açılmayan günler 0 ile görünsün: `gun`, `bilet`, güne göre sıralı.

```starter
SELECT date(acilis) AS gun, COUNT(*) AS bilet
FROM biletler
GROUP BY gun
ORDER BY gun;
```

```test
eq(sutunlar, ["gun", "bilet"], "sütunlar: gun, bilet")
eq(sonuc, [("2026-10-10", 0), ("2026-10-11", 0), ("2026-10-12", 3), ("2026-10-13", 3), ("2026-10-14", 3),
           ("2026-10-15", 3), ("2026-10-16", 3), ("2026-10-17", 2), ("2026-10-18", 2), ("2026-10-19", 1),
           ("2026-10-20", 0)], "11 gün, boşlar sıfırla")
ok(kullanir("recursive"), "WITH RECURSIVE ile takvim üret")
```

```solution
WITH RECURSIVE takvim(gun) AS (
    SELECT '2026-10-10'
    UNION ALL
    SELECT date(gun, '+1 day') FROM takvim WHERE gun < '2026-10-20'
)
SELECT t.gun, COUNT(b.id) AS bilet
FROM takvim AS t
LEFT JOIN biletler AS b ON date(b.acilis) = t.gun
GROUP BY t.gun
ORDER BY t.gun;
```

```hint
Takvim: `SELECT '2026-10-10' UNION ALL SELECT date(gun, '+1 day') FROM takvim WHERE gun < '2026-10-20'`.
```

```hint
Takvimi `LEFT JOIN biletler ON date(b.acilis) = t.gun` ile bağla ve `COUNT(b.id)` say: eşleşme yoksa 0 olur.
```
:::

::: gorev Yönetim zinciri
Her çalışan için en üstteki yöneticiden kendisine kadar olan yolu `Selin > Kerem > Can` biçiminde getir: tek sütun `yol`, alfabetik sıralı.

```starter
SELECT ad AS yol FROM personel ORDER BY yol;
```

```test
eq(sutunlar, ["yol"], "tek sütun: yol")
eq([r[0] for r in sonuc], ["Selin", "Selin > Ayşe", "Selin > Ayşe > Ece", "Selin > Kerem", "Selin > Kerem > Burak",
                           "Selin > Kerem > Can", "Selin > Mert", "Selin > Mert > Elif", "Selin > Zeynep",
                           "Selin > Zeynep > Deniz"], "on yol")
```

```solution
WITH RECURSIVE zincir(id, yol) AS (
    SELECT id, ad FROM personel WHERE yonetici_id IS NULL
    UNION ALL
    SELECT p.id, z.yol || ' > ' || p.ad
    FROM personel AS p
    JOIN zincir AS z ON p.yonetici_id = z.id
)
SELECT yol FROM zincir ORDER BY yol;
```

```hint
Başlangıç: yöneticisi olmayan kişi, yol = kendi adı. Her tur: `z.yol || ' > ' || p.ad`.
```
:::

::: gorev Bütün alt kadro
Her yöneticinin **doğrudan ve dolaylı** bütün alt kadrosunun sayısını getir: `yonetici`, `alt_kadro`; çoktan aza, eşitlikte ada göre. Alt kadrosu olmayanlar listede olmasın.

```starter
SELECT y.ad AS yonetici, COUNT(*) AS alt_kadro
FROM personel AS c
JOIN personel AS y ON y.id = c.yonetici_id
GROUP BY y.id
ORDER BY alt_kadro DESC, yonetici;
```

```test
eq(sutunlar, ["yonetici", "alt_kadro"], "sütunlar")
eq(sonuc, [("Selin", 9), ("Kerem", 2), ("Ayşe", 1), ("Mert", 1), ("Zeynep", 1)], "dolaylılar dahil")
```

```solution
WITH RECURSIVE bag(yonetici_id, calisan_id) AS (
    SELECT yonetici_id, id FROM personel WHERE yonetici_id IS NOT NULL
    UNION ALL
    SELECT b.yonetici_id, p.id
    FROM bag AS b
    JOIN personel AS p ON p.yonetici_id = b.calisan_id
)
SELECT y.ad AS yonetici, COUNT(*) AS alt_kadro
FROM bag
JOIN personel AS y ON y.id = bag.yonetici_id
GROUP BY y.id
ORDER BY alt_kadro DESC, yonetici;
```

```hint
Başlangıç kodu yalnızca doğrudan bağlıları sayıyor (Selin için 4). Bütün (yönetici, alt çalışan) çiftlerini üreten bir özyineleme kur: başlangıç doğrudan bağlar, her tur bir kademe aşağı.
```

```hint
`bag(yonetici_id, calisan_id)`: başlangıç `SELECT yonetici_id, id FROM personel WHERE yonetici_id IS NOT NULL`; özyineleme `JOIN personel p ON p.yonetici_id = b.calisan_id` ve `SELECT b.yonetici_id, p.id`.
```
:::
