---
id: sq12
title: Metin ve Tarih Fonksiyonları
summary: substr, instr, replace, trim ve printf; LIKE ile GLOB farkı; date, datetime, strftime ve değiştiriciler; julianday ve unixepoch ile süre hesabı; CAST.
---

::: anlat Metinle çalışmak
SQLite'ın metin fonksiyonları küçüktür ama birleştirilince çoğu işi görür:

| Fonksiyon | Ne yapar |
|---|---|
| `substr(s, baş, uz)` | alt metin (1'den sayar; negatif baş sondan sayar) |
| `instr(s, t)` | t'nin ilk konumu (yoksa 0) |
| `replace(s, a, b)` | bütün a'ları b yapar |
| `trim(s)`, `ltrim`, `rtrim` | baştaki/sondaki boşlukları (ya da verilen karakterleri) atar |
| `upper`, `lower`, `length` | harf dönüşümü (yalnızca İngilizce harfler), uzunluk |
| `printf('%05.1f', x)` | C tarzı biçimlendirme |
| `s LIKE 'web%'` | `%` ve `_` joker; İngilizce harflerde büyük-küçük duyarsız |
| `s GLOB 'web[0-9]*'` | kabuk tarzı joker (`*`, `?`, `[...]`); **harfe duyarlı** |

Bir metni ayırıcıdan bölmek için `instr` ile ayırıcının yeri bulunur, `substr` ile iki parça alınır:

```sql
SELECT 'web01.ist.ornek.local' AS fqdn,
       substr('web01.ist.ornek.local', 1, instr('web01.ist.ornek.local', '.') - 1) AS kisa,
       substr('web01.ist.ornek.local', instr('web01.ist.ornek.local', '.') + 1) AS alan;

SELECT ad, printf('%-8s|%3d%%', ad, cpu) AS satir FROM sunucular WHERE ad GLOB 'web0[12]';
```

### Tarih ve saat
SQLite'ta ayrı bir tarih türü yoktur; tarihler `'YYYY-AA-GG SS:DD'` biçiminde metin olarak tutulur ve tarih fonksiyonları bu metinleri anlar. Her fonksiyon, sırayla uygulanan **değiştiriciler** alabilir:

```sql
SELECT date('2026-10-19', '+10 days')                          AS on_gun_sonra,
       date('2026-10-19', 'start of month')                    AS ay_basi,
       date('2026-10-19', 'start of month', '+1 month', '-1 day') AS ay_sonu,
       date('2026-10-19', 'weekday 0')                         AS sonraki_pazar,
       strftime('%w', '2026-10-19')                            AS hafta_gunu,   -- 0 = Pazar
       strftime('%H:%M', '2026-10-19 08:15')                   AS saat;
```

Süre hesabı için iki yol: `julianday` (gün cinsinden ondalık sayı) ya da `unixepoch` (saniye):

```sql
SELECT id,
       round((julianday(kapanis) - julianday(acilis)) * 24, 2) AS saat,
       (unixepoch(kapanis) - unixepoch(acilis)) / 60           AS dakika
FROM biletler
WHERE kapanis IS NOT NULL
LIMIT 3;
```

> [!TUZAK]
> `strftime('%w', ...)` haftanın gününü **Pazar = 0** olarak verir; Türkiye'de hafta Pazartesi başlar. Pazartesiyi 1, Pazarı 7 yapmak için: `(CAST(strftime('%w', t) AS INTEGER) + 6) % 7 + 1`.
:::

::: tahmin
Tek satır, dört sütun:

```sql
SELECT substr('web01.istanbul.local', 1, instr('web01.istanbul.local', '.') - 1),
       replace('2026-10-19', '-', ''),
       strftime('%w', '2026-10-19'),
       date('2026-10-19', 'start of month', '+1 month', '-1 day');
```

???

`web01|20261019|1|2026-10-31`. İlk noktaya kadar olan kısım "web01"dir. Tireler silinir. 19 Ekim 2026 bir Pazartesi; Pazar 0 olduğu için 1 döner. Ayın başına gidip bir ay ekleyip bir gün çıkarmak ayın son gününü verir.
:::

::: gorev Alan adlarını parçala
`kayitlar` tablosundaki her `fqdn` için kısa adı (ilk noktaya kadar) ve alanı (ilk noktadan sonrası) getir: `kisa`, `alan` sütunları, `kisa`'ya göre sıralı.

```setup
CREATE TABLE kayitlar (fqdn TEXT);
INSERT INTO kayitlar VALUES ('web01.ist.ornek.local'), ('db02.ank.ornek.local'), ('yedek01.izm.ornek.local');
```

```starter
SELECT fqdn AS kisa, fqdn AS alan
FROM kayitlar;
```

```test
eq(sutunlar, ["kisa", "alan"], "sütunlar: kisa, alan")
eq(sonuc, [("db02", "ank.ornek.local"), ("web01", "ist.ornek.local"), ("yedek01", "izm.ornek.local")], "üç kayıt")
```

```solution
SELECT substr(fqdn, 1, instr(fqdn, '.') - 1) AS kisa,
       substr(fqdn, instr(fqdn, '.') + 1)    AS alan
FROM kayitlar
ORDER BY kisa;
```

```hint
Noktanın yeri `instr(fqdn, '.')`. Kısa ad 1'den o konumun bir öncesine, alan bir sonrasından sona kadar.
```
:::

::: gorev Haftanın günlerine göre
Biletleri açıldıkları **haftanın gününe** göre say. `gun` sütununda Türkçe gün adı (`Pazartesi` … `Pazar`), `adet` sütununda sayı olsun; Pazartesiden Pazara sıralı.

```cikti
Pazartesi|4
Salı|3
Çarşamba|3
Perşembe|3
Cuma|3
Cumartesi|2
Pazar|2
```

```starter
SELECT strftime('%w', acilis) AS gun, COUNT(*) AS adet
FROM biletler
GROUP BY gun;
```

```test
eq(sutunlar, ["gun", "adet"], "sütunlar: gun, adet")
eq(sonuc, [("Pazartesi", 4), ("Salı", 3), ("Çarşamba", 3), ("Perşembe", 3), ("Cuma", 3), ("Cumartesi", 2), ("Pazar", 2)], "gün dağılımı")
```

```solution
WITH g AS (
    SELECT (CAST(strftime('%w', acilis) AS INTEGER) + 6) % 7 + 1 AS no
    FROM biletler
)
SELECT CASE no WHEN 1 THEN 'Pazartesi' WHEN 2 THEN 'Salı' WHEN 3 THEN 'Çarşamba' WHEN 4 THEN 'Perşembe'
               WHEN 5 THEN 'Cuma' WHEN 6 THEN 'Cumartesi' ELSE 'Pazar' END AS gun,
       COUNT(*) AS adet
FROM g
GROUP BY no
ORDER BY no;
```

```hint
Önce Pazartesi = 1 … Pazar = 7 olacak bir gün numarası üret: `(CAST(strftime('%w', acilis) AS INTEGER) + 6) % 7 + 1`. Bu numaraya göre grupla ve sırala.
```

```hint
Numarayı ada `CASE no WHEN 1 THEN 'Pazartesi' ... END` ile çevir.
```
:::

::: gorev Garantisi bitenler
Sunucuların garantisi devreye alınmalarından **3 yıl** sonra bitiyor. Garantisi `2026-10-19` tarihinden önce bitmiş sunucuların `ad` ve `bitis` tarihini getir; bitiş tarihine göre sıralı.

```starter
SELECT ad, devreye AS bitis
FROM sunucular
ORDER BY bitis;
```

```test
eq(sutunlar, ["ad", "bitis"], "sütunlar: ad, bitis")
eq(sonuc, [("yedek01", "2022-06-30"), ("dc02", "2023-11-11"), ("web03", "2024-05-03"), ("db01", "2025-03-15"),
           ("dc01", "2025-08-20"), ("web01", "2026-01-10"), ("web02", "2026-01-10")], "yedi sunucu")
```

```solution
SELECT ad, date(devreye, '+3 years') AS bitis
FROM sunucular
WHERE date(devreye, '+3 years') < '2026-10-19'
ORDER BY bitis, ad;
```

```hint
`date(devreye, '+3 years')` bitiş tarihini verir. ISO tarihler metin olarak doğru karşılaştırılır.
```
:::
