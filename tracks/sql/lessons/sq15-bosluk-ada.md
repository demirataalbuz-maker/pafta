---
id: sq15
title: Boşluklar ve Adalar
summary: Ardışık değer dizilerini (adaları) ROW_NUMBER farkıyla gruplamak, eksik aralıkları (boşlukları) LEAD ile bulmak, aynı tekniği tarihlere uygulamak ve en uzun seriyi seçmek.
---

::: anlat Ardışık olanı gruplamak
"Yedekleme kaç gün üst üste başarısız oldu?", "Hangi fatura numaraları eksik?", "Sunucu hangi zaman aralıklarında yüksek yükteydi?" Bunlar aynı tür sorulardır: sıralı bir dizide **ardışık bloklar** (adalar) ve aralarındaki **eksikler** (boşluklar).

### Boşluklar: LEAD ile
Her değeri bir sonrakiyle karşılaştır; aradaki fark 1'den büyükse orada bir boşluk vardır:

```sql
WITH t(no) AS (VALUES (101), (102), (103), (106), (107), (110)),
s AS (SELECT no, LEAD(no) OVER (ORDER BY no) AS sonraki FROM t)
SELECT no + 1 AS bos_bas, sonraki - 1 AS bos_bit
FROM s
WHERE sonraki > no + 1;
```

### Adalar: ROW_NUMBER farkı
Ardışık bir dizide değer de satır numarası da birer birer artar; ikisinin **farkı sabit** kalır. Dizide bir boşluk olunca fark değişir. Bu sabit fark, adanın kimliği olarak gruplanır:

| değer | ROW_NUMBER | fark |
|---|---|---|
| 1 | 1 | 0 |
| 2 | 2 | 0 |
| 3 | 3 | 0 |
| 7 | 4 | 3 |
| 8 | 5 | 3 |
| 10 | 6 | 4 |

```sql
WITH t(n) AS (VALUES (1), (2), (3), (7), (8), (10)),
g AS (SELECT n, n - ROW_NUMBER() OVER (ORDER BY n) AS ada FROM t)
SELECT MIN(n) AS bas, MAX(n) AS bit, COUNT(*) AS uzunluk
FROM g
GROUP BY ada
ORDER BY bas;
```

### Tarihlerde adalar
Aynı teknik tarihlerde `julianday(gun) - ROW_NUMBER()` ile çalışır. Belirli bir durumdaki ardışık günleri bulmak için **önce süz**, sonra farkı al: süzülen satırların arasındaki eksik günler adaları ayırır:

```sql
WITH t(gun, sonuc) AS (VALUES ('2026-10-01', 'tamam'), ('2026-10-02', 'hata'), ('2026-10-03', 'hata'),
                              ('2026-10-04', 'tamam'), ('2026-10-05', 'hata')),
h AS (SELECT gun, julianday(gun) - ROW_NUMBER() OVER (ORDER BY gun) AS ada FROM t WHERE sonuc = 'hata')
SELECT MIN(gun), MAX(gun), COUNT(*) FROM h GROUP BY ada ORDER BY MIN(gun);
```

> [!İPUCU]
> Bu teknik izleme verilerinde çok işe yarar: "CPU'nun %80'in üstünde kaldığı kesintisiz dönemler", "bir hizmetin art arda başarısız denetimleri". Önce koşula uyan satırları süz, sonra ROW_NUMBER farkıyla grupla.
:::

::: tahmin
Kaç satır, hangi değerler?

```sql
WITH t(n) AS (VALUES (1), (2), (3), (7), (8), (10))
SELECT MIN(n), MAX(n), COUNT(*)
FROM (SELECT n, n - ROW_NUMBER() OVER (ORDER BY n) AS g FROM t)
GROUP BY g
ORDER BY MIN(n);
```

???

`1|3|3`, `7|8|2`, `10|10|1`. Fark 1–3 için 0, 7–8 için 3, 10 için 4'tür; her farklı değer bir adadır.
:::

::: gorev Eksik numaralar
`kayit` tablosundaki `no` dizisindeki eksik aralıkları `bas`, `bit` sütunlarıyla, `bas`'a göre sıralı getir.

```setup
CREATE TABLE kayit (no INTEGER);
INSERT INTO kayit VALUES (101), (102), (103), (106), (107), (110), (111), (112), (114);
```

```starter
SELECT no FROM kayit ORDER BY no;
```

```test
eq(sutunlar, ["bas", "bit"], "sütunlar: bas, bit")
eq(sonuc, [(104, 105), (108, 109), (113, 113)], "üç boşluk")
```

```solution
WITH s AS (
    SELECT no, LEAD(no) OVER (ORDER BY no) AS sonraki
    FROM kayit
)
SELECT no + 1 AS bas, sonraki - 1 AS bit
FROM s
WHERE sonraki > no + 1
ORDER BY bas;
```

```hint
`LEAD(no) OVER (ORDER BY no)` bir sonraki numarayı verir; fark 1'den büyükse arada eksik var.
```
:::

::: gorev Başarısız yedek serileri
`yedek_sonuc` tablosunda her günün yedekleme sonucu var. Art arda **başarısız** olan günlerin serilerini `bas`, `bit`, `gun_sayisi` olarak, başlangıca göre sıralı getir.

```setup
CREATE TABLE yedek_sonuc (gun TEXT, sonuc TEXT);
INSERT INTO yedek_sonuc VALUES
 ('2026-10-01','başarılı'), ('2026-10-02','başarılı'), ('2026-10-03','başarısız'), ('2026-10-04','başarısız'),
 ('2026-10-05','başarısız'), ('2026-10-06','başarılı'), ('2026-10-07','başarılı'), ('2026-10-08','başarılı'),
 ('2026-10-09','başarısız'), ('2026-10-10','başarılı'), ('2026-10-11','başarısız'), ('2026-10-12','başarısız'),
 ('2026-10-13','başarılı'), ('2026-10-14','başarılı');
```

```starter
SELECT gun FROM yedek_sonuc WHERE sonuc = 'başarısız';
```

```test
eq(sutunlar, ["bas", "bit", "gun_sayisi"], "sütunlar")
eq(sonuc, [("2026-10-03", "2026-10-05", 3), ("2026-10-09", "2026-10-09", 1), ("2026-10-11", "2026-10-12", 2)], "üç seri")
```

```solution
WITH h AS (
    SELECT gun, julianday(gun) - ROW_NUMBER() OVER (ORDER BY gun) AS ada
    FROM yedek_sonuc
    WHERE sonuc = 'başarısız'
)
SELECT MIN(gun) AS bas, MAX(gun) AS bit, COUNT(*) AS gun_sayisi
FROM h
GROUP BY ada
ORDER BY bas;
```

```hint
Önce yalnızca başarısız günleri süz; sonra `julianday(gun) - ROW_NUMBER() OVER (ORDER BY gun)` her seri için sabittir.
```
:::

::: gorev En uzun başarılı seri
Aynı tablodan **en uzun** art arda başarılı seriyi `bas`, `bit`, `uzunluk` olarak tek satırda getir.

```setup
CREATE TABLE yedek_sonuc (gun TEXT, sonuc TEXT);
INSERT INTO yedek_sonuc VALUES
 ('2026-10-01','başarılı'), ('2026-10-02','başarılı'), ('2026-10-03','başarısız'), ('2026-10-04','başarısız'),
 ('2026-10-05','başarısız'), ('2026-10-06','başarılı'), ('2026-10-07','başarılı'), ('2026-10-08','başarılı'),
 ('2026-10-09','başarısız'), ('2026-10-10','başarılı'), ('2026-10-11','başarısız'), ('2026-10-12','başarısız'),
 ('2026-10-13','başarılı'), ('2026-10-14','başarılı');
```

```starter
SELECT MIN(gun) AS bas, MAX(gun) AS bit, COUNT(*) AS uzunluk
FROM yedek_sonuc
WHERE sonuc = 'başarılı';
```

```test
eq(sonuc, [("2026-10-06", "2026-10-08", 3)], "6–8 Ekim, 3 gün")
eq(dene("UPDATE yedek_sonuc SET sonuc = 'başarılı' WHERE gun = '2026-10-09';"), [("2026-10-06", "2026-10-10", 5)], "veri değişince yeni en uzun seri")
```

```solution
WITH b AS (
    SELECT gun, julianday(gun) - ROW_NUMBER() OVER (ORDER BY gun) AS ada
    FROM yedek_sonuc
    WHERE sonuc = 'başarılı'
),
seriler AS (
    SELECT MIN(gun) AS bas, MAX(gun) AS bit, COUNT(*) AS uzunluk
    FROM b
    GROUP BY ada
)
SELECT bas, bit, uzunluk
FROM seriler
ORDER BY uzunluk DESC, bas
LIMIT 1;
```

```hint
Önceki görevin tekniğiyle başarılı serileri çıkar, sonra uzunluğa göre azalan sıralayıp ilkini al.
```
:::
