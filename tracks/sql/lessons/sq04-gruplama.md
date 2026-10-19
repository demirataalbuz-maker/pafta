---
id: sq04
title: Toplama ve GROUP BY
summary: COUNT, SUM, AVG, MIN, MAX; GROUP BY ile gruplamak, HAVING ile grupları süzmek ve sorgunun gerçek yürütülme sırası.
---

::: anlat Satırları özetlemek
**Toplama fonksiyonları** birçok satırı tek bir değere indirir:

```sql
SELECT COUNT(*)              AS toplam,        #! satır sayısı
       COUNT(ram_gb)         AS ram_bilinen,   #! NULL olmayan değer sayısı
       COUNT(DISTINCT sehir) AS sehir_sayisi,  #! farklı değer sayısı
       MIN(cpu), MAX(cpu),
       round(AVG(cpu), 1)    AS ort_cpu
FROM sunucular;
```

`GROUP BY` satırları gruplara ayırır ve toplama fonksiyonunu **her grup için ayrı** hesaplar:

```sql
SELECT rol, COUNT(*) AS adet, round(AVG(cpu), 1) AS ort_cpu
FROM sunucular
GROUP BY rol
ORDER BY adet DESC, rol;
```

`HAVING` grupları süzer. `WHERE` gruplamadan **önce** satırlara, `HAVING` gruplamadan **sonra** gruplara uygulanır:

```sql
SELECT sehir, COUNT(*) AS adet
FROM sunucular
WHERE sehir IS NOT NULL      #! önce satırlar süzülür
GROUP BY sehir
HAVING COUNT(*) >= 3;        #! sonra gruplar
```

`group_concat` bir grubun değerlerini tek metne toplar:

```sql
SELECT rol, group_concat(ad, ', ') AS sunucular
FROM sunucular
GROUP BY rol;
```

> [!DERİN]
> SQL'i yazdığın sıra ile veritabanının yürüttüğü sıra farklıdır:
> `FROM` → `WHERE` → `GROUP BY` → `HAVING` → `SELECT` → `ORDER BY` → `LIMIT`.
> Bu yüzden `WHERE COUNT(*) > 2` yazamazsın (gruplar henüz yok) ve SELECT'te verdiğin takma adı WHERE'de kullanamazsın (SELECT henüz çalışmadı). ORDER BY ise en sonda çalıştığı için takma adları görür.

> [!TUZAK]
> SQLite, `SELECT rol, ad, COUNT(*) ... GROUP BY rol` gibi gruplanmamış bir sütunu (`ad`) sessizce kabul eder ve gruptan **rastgele bir satırın** değerini koyar. PostgreSQL ve SQL Server bu sorguyu hata vererek reddeder. Kural: SELECT'teki her sütun ya GROUP BY'da olmalı ya da bir toplama fonksiyonunun içinde.

> [!NOT]
> KQL'de `biletler | summarize count() by oncelik`, SPL'de `... | stats count by oncelik`. Log analizinin büyük kısmı bu tek kalıptır: süz, grupla, say.
:::

::: tahmin
Tek satır, üç sayı:

```sql
SELECT COUNT(*), COUNT(atanan_id), COUNT(DISTINCT atanan_id)
FROM biletler;
```

???

`20|16|7`. 20 bilet var. 4'ünde `atanan_id` NULL (9, 12, 17, 18); `COUNT(sütun)` NULL'ları saymaz, 16 kalır. Bu 16 bilet 7 farklı kişiye atanmış: 2, 3, 4, 5, 6, 7 ve 10 numaralı çalışanlar.
:::

::: gorev Duruma göre
Biletleri `durum`'a göre grupla; her durumun adını ve bilet sayısını `adet` adıyla getir.

```starter
SELECT durum
FROM biletler;
```

```test
eq(sutunlar, ["durum", "adet"], "sütunlar: durum, adet")
eq(sorted(sonuc), [("açık", 9), ("çözüldü", 11)], "açık 9, çözüldü 11")
```

```solution
SELECT durum, COUNT(*) AS adet
FROM biletler
GROUP BY durum;
```

```hint
`COUNT(*)` ve `GROUP BY durum`.
```
:::

::: gorev Şehir başına ortalama CPU
Şehri bilinen sunucular için her şehrin adını ve ortalama CPU'sunu (bir ondalığa yuvarlanmış, `ort` adıyla) getir. En yüksek ortalama en üstte olsun.

```cikti
İstanbul|65.3
Ankara|34.3
İzmir|20.5
```

```starter
SELECT sehir, AVG(cpu)
FROM sunucular
GROUP BY sehir;
```

```test
eq(sutunlar, ["sehir", "ort"], "sütunlar: sehir, ort")
eq(sonuc, [("İstanbul", 65.3), ("Ankara", 34.3), ("İzmir", 20.5)], "şehir ortalamaları, büyükten küçüğe")
```

```solution
SELECT sehir, round(AVG(cpu), 1) AS ort
FROM sunucular
WHERE sehir IS NOT NULL
GROUP BY sehir
ORDER BY ort DESC;
```

```hint
Bulut sunucularını (`sehir IS NULL`) WHERE ile gruplamadan önce at. Yuvarlamak için `round(AVG(cpu), 1)`.
```
:::

::: gorev Yoğun sorumlular
En az **3** sunucunun sorumlusu olan çalışanların `sorumlu_id` değerini ve kaç sunucudan sorumlu olduklarını getir.

```starter
SELECT sorumlu_id, COUNT(*)
FROM sunucular
GROUP BY sorumlu_id;
```

```test
eq(sorted(sonuc), [(2, 3), (6, 3)], "2 ve 6 numaralı çalışanlar, 3'er sunucu")
ok(kullanir("having"), "grupları HAVING ile süz")
```

```solution
SELECT sorumlu_id, COUNT(*) AS sunucu_sayisi
FROM sunucular
GROUP BY sorumlu_id
HAVING COUNT(*) >= 3;
```

```hint
Grup sayısına koşul `WHERE`'e yazılamaz; `HAVING COUNT(*) >= 3`.
```
:::
