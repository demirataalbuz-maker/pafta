---
id: sq13
title: Koşullu Toplama ve Pivot
summary: SUM(CASE ...) ve FILTER ile koşullu sayım, satırları sütuna çeviren pivot tablolar, yüzdeler, sıfıra bölmeye karşı NULLIF ve toplam satırı eklemek.
---

::: anlat Bir sorguda birden çok sayım
Raporların çoğu "her X için, şu koşuldaki Y sayısı" sorusudur. Her koşul için ayrı sorgu yazmak yerine toplama fonksiyonunun içine bir koşul koyulur:

```sql
SELECT oncelik,
       COUNT(*)                                        AS toplam,
       SUM(CASE WHEN durum = 'açık' THEN 1 ELSE 0 END) AS acik,       -- her veritabanında çalışır
       COUNT(*) FILTER (WHERE durum = 'çözüldü')       AS cozulen     -- daha okunur (SQLite, PostgreSQL)
FROM biletler
GROUP BY oncelik;
```

### Pivot: satırları sütuna çevirmek
Bir değerin farklı karşılıklarını **sütun başlıklarına** çevirmek pivottur. SQLite'ta özel bir `PIVOT` komutu yoktur; her sütun bir koşullu toplamadır:

```sql
SELECT s.rol,
       COUNT(*) FILTER (WHERE b.oncelik = 'düşük')  AS dusuk,
       COUNT(*) FILTER (WHERE b.oncelik = 'orta')   AS orta,
       COUNT(*) FILTER (WHERE b.oncelik = 'yüksek') AS yuksek,
       COUNT(*) FILTER (WHERE b.oncelik = 'kritik') AS kritik
FROM biletler AS b
JOIN sunucular AS s ON s.id = b.sunucu_id
GROUP BY s.rol
ORDER BY s.rol;
```

### Yüzdeler ve sıfıra bölme
Tam sayı bölmesine düşmemek için `100.0 *` ile başla. Bölen sıfır olabilecekse `NULLIF(bolen, 0)` sıfırı NULL'a çevirir; sonuç hata yerine NULL olur:

```sql
SELECT rol,
       COUNT(*) AS adet,
       round(100.0 * COUNT(*) / (SELECT COUNT(*) FROM sunucular), 1) AS yuzde,
       round(100.0 * SUM(cpu >= 80) / NULLIF(COUNT(*), 0), 1)         AS yogun_yuzde
FROM sunucular
GROUP BY rol
ORDER BY adet DESC, rol;
```

SQLite'ta karşılaştırmalar 1 ya da 0 döndürdüğü için `SUM(cpu >= 80)` de bir koşullu sayımdır.

### Toplam satırı
Bir rapora en alta "TOPLAM" satırı eklemenin taşınabilir yolu `UNION ALL`'dur; sıralamada toplam satırını sona itmek için bir sıra sütunu kullanılır:

```sql
SELECT rol, adet FROM (
    SELECT rol, COUNT(*) AS adet, 0 AS sira FROM sunucular GROUP BY rol
    UNION ALL
    SELECT 'TOPLAM', COUNT(*), 1 FROM sunucular
)
ORDER BY sira, rol;
```
:::

::: tahmin
Kaç satır, hangi değerler?

```sql
SELECT durum,
       COUNT(*) FILTER (WHERE oncelik = 'kritik') AS kritik,
       COUNT(*) FILTER (WHERE oncelik = 'yüksek') AS yuksek
FROM biletler
GROUP BY durum
ORDER BY durum;
```

???

`açık|0|3` ve `çözüldü|3|3`. Kritik biletlerin üçü de çözülmüş, açıkta kritik yok. Yüksek öncelikli altı biletin üçü açık (5, 9, 20), üçü çözülmüş (1, 7, 13).
:::

::: gorev Öncelik pivotu
Bileti olan her sunucu **rolü** için öncelik dağılımını pivot olarak getir: `rol`, `dusuk`, `orta`, `yuksek`, `kritik`; role göre sıralı. Sunucusu olmayan biletleri sayma.

```starter
SELECT s.rol, b.oncelik, COUNT(*) AS adet
FROM biletler AS b
JOIN sunucular AS s ON s.id = b.sunucu_id
GROUP BY s.rol, b.oncelik;
```

```test
eq(sutunlar, ["rol", "dusuk", "orta", "yuksek", "kritik"], "pivot sütunları")
beklenen = sorgu("""SELECT s.rol, SUM(b.oncelik = 'düşük'), SUM(b.oncelik = 'orta'), SUM(b.oncelik = 'yüksek'), SUM(b.oncelik = 'kritik')
                    FROM biletler b JOIN sunucular s ON s.id = b.sunucu_id GROUP BY s.rol ORDER BY s.rol""")
eq(sonuc, beklenen, "rol başına öncelik sayıları")
eq(len(sonuc), 8, "bileti olan sekiz rol")
```

```solution
SELECT s.rol,
       COUNT(*) FILTER (WHERE b.oncelik = 'düşük')  AS dusuk,
       COUNT(*) FILTER (WHERE b.oncelik = 'orta')   AS orta,
       COUNT(*) FILTER (WHERE b.oncelik = 'yüksek') AS yuksek,
       COUNT(*) FILTER (WHERE b.oncelik = 'kritik') AS kritik
FROM biletler AS b
JOIN sunucular AS s ON s.id = b.sunucu_id
GROUP BY s.rol
ORDER BY s.rol;
```

```hint
Her öncelik bir sütun: `COUNT(*) FILTER (WHERE b.oncelik = 'düşük') AS dusuk` ve diğerleri. Gruplama yalnızca role göre.
```
:::

::: gorev Çözülme oranı
Her öncelik için `toplam`, `cozulen` ve çözülme yüzdesini (`oran`, bir ondalık) getir; oranı yüksek olan en üstte.

```cikti
kritik|3|3|100.0
orta|5|3|60.0
yüksek|6|3|50.0
düşük|6|2|33.3
```

```starter
SELECT oncelik, COUNT(*) AS toplam
FROM biletler
GROUP BY oncelik;
```

```test
eq(sutunlar, ["oncelik", "toplam", "cozulen", "oran"], "sütunlar")
eq(sonuc, [("kritik", 3, 3, 100.0), ("orta", 5, 3, 60.0), ("yüksek", 6, 3, 50.0), ("düşük", 6, 2, 33.3)], "öncelik başına oran")
```

```solution
SELECT oncelik,
       COUNT(*) AS toplam,
       COUNT(*) FILTER (WHERE durum = 'çözüldü') AS cozulen,
       round(100.0 * COUNT(*) FILTER (WHERE durum = 'çözüldü') / COUNT(*), 1) AS oran
FROM biletler
GROUP BY oncelik
ORDER BY oran DESC;
```

```hint
Yüzde: `round(100.0 * cozulen_sayisi / COUNT(*), 1)`. `100.0` ile başlamazsan tam sayı bölmesi küsuratı atar.
```
:::

::: gorev Toplam satırlı rapor
Her ekip için çalışan sayısını (`ekip`, `adet`) getir ve en alta `TOPLAM` satırı ekle. Ekipler alfabetik, `TOPLAM` en sonda olsun. Çalışanı olmayan ekip 0 ile görünsün; ekibi olmayan çalışan yalnızca toplamda sayılsın.

```starter
SELECT e.ad AS ekip, COUNT(*) AS adet
FROM personel AS p
JOIN ekipler AS e ON e.id = p.ekip_id
GROUP BY e.ad;
```

```test
eq(sutunlar, ["ekip", "adet"], "sütunlar: ekip, adet")
eq(sonuc, [("Altyapı", 3), ("Arşiv", 0), ("Ağ", 2), ("Uygulama", 2), ("Veritabanı", 2), ("TOPLAM", 10)], "beş ekip ve toplam")
```

```solution
SELECT ekip, adet FROM (
    SELECT e.ad AS ekip, COUNT(p.id) AS adet, 0 AS sira
    FROM ekipler AS e
    LEFT JOIN personel AS p ON p.ekip_id = e.id
    GROUP BY e.id
    UNION ALL
    SELECT 'TOPLAM', COUNT(*), 1 FROM personel
)
ORDER BY sira, ekip;
```

```hint
Çalışanı olmayan ekip için `ekipler LEFT JOIN personel` ve `COUNT(p.id)` (NULL'ları saymaz). Toplam satırı ayrı bir sorgu: `SELECT 'TOPLAM', COUNT(*), 1 FROM personel`.
```

```hint
`UNION ALL` sonucunu bir alt sorguya al ve `ORDER BY sira, ekip` ile sırala; dışarıda yalnızca `ekip, adet` seç.
```
:::
