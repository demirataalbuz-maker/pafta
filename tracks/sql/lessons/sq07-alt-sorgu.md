---
id: sq07
title: Alt Sorgular ve CTE
summary: Sorgunun içinde sorgu; skaler alt sorgu, IN ve EXISTS, FROM'da türetilmiş tablo, WITH ile okunabilir adımlar ve özyinelemeli CTE.
kazanim: 1Z0071 16.1, 1Z0071 16.2, 1Z0071 16.3, 1Z0071 16.4, 1Z0071 16.6, 1Z0071 16.7, 1Z0071 16.8
---

::: anlat Sorgunun içinde sorgu
Bir sorgunun sonucunu başka bir sorgunun içinde kullanabilirsin. **Skaler** alt sorgu tek bir değer döndürür:

```sql
SELECT ad, cpu
FROM sunucular
WHERE cpu > (SELECT AVG(cpu) FROM sunucular);   #! önce ortalama hesaplanır
```

`IN` ile bir **liste** döndüren alt sorgu:

```sql
SELECT ad
FROM personel
WHERE id IN (SELECT atanan_id FROM biletler WHERE oncelik = 'kritik');
```

`EXISTS` "en az bir eşleşen satır var mı?" diye sorar. Bu alt sorgu dıştaki satıra (`s.id`) bağlıdır; her sunucu için yeniden değerlendirilir (**ilişkili alt sorgu**):

```sql
SELECT s.ad
FROM sunucular AS s
WHERE EXISTS (SELECT 1 FROM biletler AS b
              WHERE b.sunucu_id = s.id AND b.durum = 'açık');
```

`JOIN` ile aynı soruyu sorsaydın, iki açık bileti olan sunucu iki kez gelirdi. `EXISTS` ve `IN` tekrar üretmez.

### WITH: adım adım sorgu
Uzun sorguları okunur adımlara bölmenin yolu **CTE**'dir (Common Table Expression). Her adımın bir adı olur, sonraki adımlar onu tablo gibi kullanır:

```sql
WITH acik AS (
    SELECT * FROM biletler WHERE durum = 'açık'
),
sayim AS (
    SELECT oncelik, COUNT(*) AS adet FROM acik GROUP BY oncelik
)
SELECT oncelik, adet
FROM sayim
ORDER BY adet DESC, oncelik;
```

> [!DERİN]
> `WITH RECURSIVE` bir CTE'nin kendisine başvurmasına izin verir. Ağaç yapılarını (yönetici zinciri, klasör hiyerarşisi) dolaşmanın SQL'deki yolu budur: önce başlangıç satırları seçilir, sonra her turda bir öncekine bağlananlar eklenir, yeni satır kalmayınca durur.

```sql
WITH RECURSIVE zincir (id, ad, seviye) AS (
    SELECT id, ad, 0 FROM personel WHERE yonetici_id IS NULL   #! başlangıç: en üst yönetici
    UNION ALL
    SELECT p.id, p.ad, z.seviye + 1                            #! her tur: bir alt kademe
    FROM personel AS p
    JOIN zincir AS z ON p.yonetici_id = z.id
)
SELECT seviye, ad FROM zincir ORDER BY seviye, ad;
```
:::

::: tahmin
Hangi sunucular, hangi sırayla?

```sql
SELECT ad FROM sunucular
WHERE cpu > (SELECT AVG(cpu) FROM sunucular)
ORDER BY cpu DESC;
```

???

`db01`, `cache01`, `web01`, `web02`, `izleme01`, `db02`. 12 sunucunun CPU toplamı 547, ortalaması yaklaşık 45,6. Bunun üstünde kalan altı sunucu CPU'ya göre azalan sırada geliyor: 91, 84, 72, 65, 55, 47.
:::

::: gorev Ortalamanın üstünde RAM
RAM'i (`ram_gb`), RAM'i bilinen sunucuların **ortalamasından büyük** olan sunucuların adlarını ada göre sıralı getir. Ortalamayı elle yazma; veri değişince sorgun yine doğru çalışmalı.

```starter
SELECT ad
FROM sunucular
ORDER BY ad;
```

```test
eq([r[0] for r in sonuc], ["cache01", "db01", "db02", "dc01"], "ortalama 24 GB; üstündekiler")
eq([r[0] for r in dene("UPDATE sunucular SET ram_gb = 4 WHERE ram_gb = 64;")],
   ["cache01", "dc01", "dc02", "web01", "web02"], "veri değişince yeni ortalamaya göre çalışmalı")
```

```solution
SELECT ad
FROM sunucular
WHERE ram_gb > (SELECT AVG(ram_gb) FROM sunucular)
ORDER BY ad;
```

```hint
Ortalamayı bir alt sorguyla hesapla: `WHERE ram_gb > (SELECT AVG(ram_gb) FROM sunucular)`. `AVG` NULL'ları zaten atlar.
```
:::

::: gorev Açık bileti olan sunucular
En az bir **açık** bileti olan sunucuların adlarını, her biri **bir kez** görünecek şekilde, ada göre sıralı getir.

```starter
SELECT s.ad
FROM sunucular AS s
JOIN biletler AS b ON b.sunucu_id = s.id
WHERE b.durum = 'açık'
ORDER BY s.ad;
```

```test
eq([r[0] for r in sonuc], ["db01", "db02", "dc01", "izleme01", "test01", "web03"], "altı sunucu, tekrarsız")
```

```solution
SELECT s.ad
FROM sunucular AS s
WHERE EXISTS (
    SELECT 1
    FROM biletler AS b
    WHERE b.sunucu_id = s.id
      AND b.durum = 'açık'
)
ORDER BY s.ad;
```

```hint
JOIN, iki açık bileti olan sunucuyu iki kez getirir. `WHERE EXISTS (SELECT 1 FROM biletler b WHERE b.sunucu_id = s.id AND ...)` kullan.
```
:::

::: gorev Önceliğe göre çözüm süresi
Çözülmüş (kapanış zamanı olan) biletlerin çözüm süresini **saat** olarak hesapla ve her öncelik için ortalamasını bir ondalığa yuvarlayarak getir: `oncelik` ve `ort_saat`, en uzun süren öncelik en üstte. Çözümü `WITH` ile iki adımda yaz.

```cikti
düşük|22.3
orta|17.5
yüksek|3.0
kritik|1.4
```

```starter
SELECT oncelik, COUNT(*)
FROM biletler
GROUP BY oncelik;
```

```test
eq(sutunlar, ["oncelik", "ort_saat"], "sütunlar: oncelik, ort_saat")
eq(sonuc, [("düşük", 22.3), ("orta", 17.5), ("yüksek", 3.0), ("kritik", 1.4)], "öncelik başına ortalama çözüm süresi")
ok(kullanir("with"), "WITH ile adımlara böl")
```

```solution
WITH cozulen AS (
    SELECT oncelik,
           (julianday(kapanis) - julianday(acilis)) * 24 AS saat
    FROM biletler
    WHERE kapanis IS NOT NULL
)
SELECT oncelik, round(AVG(saat), 1) AS ort_saat
FROM cozulen
GROUP BY oncelik
ORDER BY ort_saat DESC;
```

```hint
`julianday()` bir zamanı gün cinsinden sayıya çevirir; iki zamanın farkı × 24 = saat.
```

```hint
İlk adımda (`WITH cozulen AS (...)`) her bilet için süreyi hesapla, ikinci adımda o tablo üzerinden `GROUP BY oncelik`.
```
:::
