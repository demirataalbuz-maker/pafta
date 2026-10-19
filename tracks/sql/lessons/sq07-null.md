---
id: sq07
title: NULL ve Üç Değerli Mantık
summary: NULL'un "bilinmiyor" demek olması, karşılaştırmalarda üçüncü değer, IS ve COALESCE, toplamalarda NULL ve NOT IN tuzağı.
---

::: anlat NULL bir değer değildir
`NULL` "boş" değil, **bilinmiyor** demektir. Bilinmeyen bir şeyle yapılan her karşılaştırmanın sonucu da bilinmiyordur:

```sql
SELECT NULL = NULL,         #! NULL (doğru değil!)
       NULL <> 5,           #! NULL
       NULL IS NULL,        #! 1
       1 + NULL,            #! NULL: aritmetik bulaşır
       'a' || NULL,         #! NULL: birleştirme de
       coalesce(NULL, 'yok'); #! ilk NULL olmayan değer
```

SQL'de mantık **üç değerlidir**: doğru, yanlış ve bilinmiyor. `WHERE` yalnızca **doğru** olan satırları bırakır; bilinmiyor olanlar da elenir. Bu yüzden:

```sql
SELECT COUNT(*) FROM sunucular WHERE sehir <> 'İstanbul';   #! bulut sunucuları sayılmaz!
```

Şehri NULL olan üç sunucu için `sehir <> 'İstanbul'` "bilinmiyor"dur ve elenir.

| Araç | Ne yapar |
|---|---|
| `x IS NULL`, `x IS NOT NULL` | NULL kontrolü (her zaman doğru/yanlış döner) |
| `a IS b`, `a IS NOT b` | NULL'ları da eşit sayan karşılaştırma (SQLite) |
| `coalesce(a, b, ...)` | ilk NULL olmayan değer |
| `ifnull(a, b)` | iki argümanlı coalesce |
| `nullif(a, b)` | a = b ise NULL, değilse a (sıfıra bölmeyi önlemek için: `x / nullif(y, 0)`) |

```sql
SELECT ad, coalesce(sehir, 'bulut') AS konum FROM sunucular ORDER BY konum, ad;
```

### Toplamalarda NULL
`COUNT(*)` satırları sayar; `COUNT(sütun)`, `SUM`, `AVG`, `MIN`, `MAX` NULL'ları **yok sayar**. `AVG(ram_gb)` bilinen 11 değerin ortalamasıdır; NULL'u 0 saymak istiyorsan bunu açıkça yazmalısın: `AVG(coalesce(ram_gb, 0))`. Hangisinin doğru olduğu sorunun anlamına bağlıdır.

> [!TUZAK]
> **NOT IN ve NULL**: alt sorgunun sonucunda tek bir NULL bile varsa `x NOT IN (...)` hiçbir satır döndürmez. `x NOT IN (1, 2, NULL)` demek `x <> 1 AND x <> 2 AND x <> NULL` demektir; son parça her zaman bilinmiyordur. Çözüm: alt sorguda `WHERE sütun IS NOT NULL` yaz ya da `NOT EXISTS` kullan.

```sql
SELECT ad FROM personel
WHERE id NOT IN (SELECT atanan_id FROM biletler);   #! boş döner: atanan_id'lerde NULL var
```
:::

::: tahmin
Üç sorgu, üç sayı:

```sql
SELECT COUNT(*) FROM sunucular WHERE sehir <> 'İstanbul';
SELECT COUNT(*) FROM sunucular WHERE NOT (sehir = 'İstanbul');
SELECT COUNT(*) FROM sunucular WHERE sehir IS NOT 'İstanbul';
```

???

`5`, `5`, `8`. 12 sunucunun 4'ü İstanbul'da, 5'i başka şehirde, 3'ünün şehri NULL. İlk iki sorguda NULL satırlar için koşul "bilinmiyor" çıkar (`NOT` bilinmiyoru da bilinmiyor bırakır), elenirler: 5. `IS NOT` ise NULL'u sıradan bir değer gibi karşılaştırır: NULL, 'İstanbul' değildir, sayılır: 5 + 3 = 8.
:::

::: gorev Konum etiketi
Her sunucunun adını ve `konum` sütununu getir: şehir varsa şehir, yoksa `bulut`. Ada göre sırala.

```starter
SELECT ad, sehir AS konum
FROM sunucular
ORDER BY ad;
```

```test
eq(sutunlar, ["ad", "konum"], "sütunlar: ad, konum")
eq(sonuc, sorgu("SELECT ad, coalesce(sehir, 'bulut') FROM sunucular ORDER BY ad"), "NULL şehirler 'bulut' olmalı")
```

```solution
SELECT ad, coalesce(sehir, 'bulut') AS konum
FROM sunucular
ORDER BY ad;
```

```hint
`coalesce(sehir, 'bulut')`: ilk NULL olmayan değeri verir.
```
:::

::: gorev Sahipsiz biletler
Kimseye **atanmamış** biletlerin `id` ve `baslik` sütunlarını `id` sırasıyla getir.

```starter
SELECT id, baslik
FROM biletler
WHERE atanan_id = NULL
ORDER BY id;
```

```test
eq([r[0] for r in sonuc], [9, 12, 17, 18], "9, 12, 17, 18")
```

```solution
SELECT id, baslik
FROM biletler
WHERE atanan_id IS NULL
ORDER BY id;
```

```hint
`= NULL` her zaman "bilinmiyor"dur, hiçbir satır geçmez. `IS NULL`.
```
:::

::: gorev Hiç bilet atanmamış çalışanlar
Kendisine **hiç bilet atanmamış** çalışanların adlarını ada göre sıralı getir. Başlangıç kodu doğru görünüyor ama boş dönüyor; sebebini bul ve düzelt.

```starter
SELECT ad
FROM personel
WHERE id NOT IN (SELECT atanan_id FROM biletler)
ORDER BY ad;
```

```test
eq([r[0] for r in sonuc], ["Burak", "Deniz", "Selin"], "Burak, Deniz, Selin")
```

```solution
SELECT ad
FROM personel
WHERE id NOT IN (SELECT atanan_id FROM biletler WHERE atanan_id IS NOT NULL)
ORDER BY ad;
```

```hint
Alt sorgunun sonucunda NULL var (atanmamış biletler). `NOT IN` listesinde tek bir NULL her şeyi "bilinmiyor" yapar.
```

```hint
Alt sorguya `WHERE atanan_id IS NOT NULL` ekle ya da `NOT EXISTS (SELECT 1 FROM biletler b WHERE b.atanan_id = personel.id)` kullan.
```
:::

::: gorev Ortalama RAM, iki yoldan
Tek satırda iki sütun getir: `ort_bilinen` (RAM'i bilinen sunucuların ortalaması) ve `ort_sifirli` (RAM'i bilinmeyeni 0 sayan ortalama).

```starter
SELECT AVG(ram_gb) AS ort_bilinen,
       AVG(ram_gb) AS ort_sifirli
FROM sunucular;
```

```test
eq(sutunlar, ["ort_bilinen", "ort_sifirli"], "sütunlar: ort_bilinen, ort_sifirli")
eq(sonuc, [(24.0, 22.0)], "264 / 11 = 24.0 ve 264 / 12 = 22.0")
```

```solution
SELECT AVG(ram_gb) AS ort_bilinen,
       AVG(coalesce(ram_gb, 0)) AS ort_sifirli
FROM sunucular;
```

```hint
`AVG` NULL'u atlar. 0 saydırmak için önce NULL'u 0'a çevir: `AVG(coalesce(ram_gb, 0))`.
```
:::
