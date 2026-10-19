---
id: sq03
title: Sıralamak, Sınırlamak, Dönüştürmek
summary: ORDER BY ve LIMIT/OFFSET, metin ve tarih fonksiyonları, CASE ile koşullu değer.
---

::: anlat ORDER BY ve LIMIT
```sql
SELECT ad, cpu
FROM sunucular
ORDER BY cpu DESC          #! büyükten küçüğe (varsayılan ASC: küçükten büyüğe)
LIMIT 3;                   #! ilk 3 satır
```

Birden çok sıralama anahtarı verebilirsin; ikinci anahtar yalnızca birincide eşitlik olunca devreye girer. `DESC` **yalnızca yazıldığı sütuna** uygulanır:

```sql
SELECT ad, sehir, cpu
FROM sunucular
WHERE sehir IS NOT NULL
ORDER BY sehir, cpu DESC;  #! şehre göre artan, şehir içinde CPU'ya göre azalan
```

Sayfalama için `LIMIT n OFFSET m`: ilk `m` satırı atla, sonraki `n` satırı ver.

> [!TUZAK]
> `ORDER BY` yazmazsan satırların sırası **garanti değildir**. Bugün eklenme sırasıyla geliyor olabilir; bir indeks eklenince ya da veri büyüyünce değişir. Sıra önemliyse her zaman `ORDER BY` yaz.

> [!TUZAK]
> SQLite metinleri **bayt sırasıyla** karşılaştırır, Türk alfabesine göre değil: `'İzmir' < 'Zonguldak'` yanlış çıkar, çünkü `İ` İngilizce harflerden sonra kodlanır. `Ç, Ğ, İ, Ö, Ş, Ü` ile başlayan metinler sıralamada sona düşer.
:::

::: anlat Fonksiyonlar ve CASE
```sql
SELECT ad,
       length(ad) AS uzunluk,
       upper(ad) AS buyuk,
       substr(isletim, 1, 6) AS aile,          #! 1'den başlayarak 6 karakter
       replace(isletim, ' ', '_') AS etiket
FROM sunucular
ORDER BY uzunluk DESC, ad
LIMIT 4;
```

Tarih ve saat fonksiyonları metin biçimindeki zamanlarla çalışır:

```sql
SELECT id,
       date(acilis) AS gun,
       strftime('%H:%M', acilis) AS saat,
       date(acilis, '+7 days') AS bir_hafta_sonra
FROM biletler
LIMIT 3;
```

`CASE` bir değere koşula göre karar verir; ilk doğru `WHEN` kazanır:

```sql
SELECT ad, cpu,
       CASE
           WHEN cpu >= 80 THEN 'yüksek'
           WHEN cpu >= 50 THEN 'orta'
           ELSE 'düşük'
       END AS yuk
FROM sunucular
ORDER BY cpu DESC;
```

`CASE`'in güzel bir kullanımı **özel sıralamadır**: öncelikler alfabetik değil, önem sırasına göre dizilsin:

```sql
SELECT id, oncelik
FROM biletler
WHERE durum = 'açık'
ORDER BY CASE oncelik WHEN 'kritik' THEN 1 WHEN 'yüksek' THEN 2 WHEN 'orta' THEN 3 ELSE 4 END, id;
```

> [!NOT]
> SQLite'ın `upper`/`lower` fonksiyonları da yalnızca İngilizce harfleri çevirir: `upper('veritabanı')` sonucu `VERITABANı` olur.
:::

::: tahmin
Hangi dört ad, hangi sırayla gelir?

```sql
SELECT ad FROM sunucular
WHERE sehir IS NOT NULL
ORDER BY sehir, ad DESC
LIMIT 4;
```

???

`web03`, `vpn01`, `db02`, `web02`. Şehirler artan sırada: önce `Ankara` (web03, db02, vpn01). Bu üçü kendi içinde `ad DESC` ile ters alfabetik dizilir: web03, vpn01, db02. Dördüncü satır sıradaki şehirden, `İstanbul`'dan gelir. Oradaki en büyük ad web02'dir. `DESC` yalnızca `ad` sütununa uygulandı, `sehir` artan kaldı.
:::

::: gorev En yoğun üç sunucu
CPU'su en yüksek **üç** sunucunun `ad` ve `cpu` sütunlarını, en yoğundan başlayarak getir.

```starter
SELECT ad, cpu
FROM sunucular
ORDER BY cpu
LIMIT 3;
```

```test
eq(sonuc, [("db01", 91), ("cache01", 84), ("web01", 72)], "db01, cache01, web01 (bu sırayla)")
```

```solution
SELECT ad, cpu
FROM sunucular
ORDER BY cpu DESC
LIMIT 3;
```

```hint
Varsayılan sıra artandır; büyükten küçüğe için `DESC`.
```
:::

::: gorev Yük sınıfı
Her sunucu için `ad` ve `yuk` sütunlarını getir: CPU 80 ve üstüyse `yüksek`, 50 ve üstüyse `orta`, değilse `düşük`. Sonucu ada göre sırala.

```starter
SELECT ad, 'düşük' AS yuk
FROM sunucular
ORDER BY ad;
```

```test
eq(sutunlar, ["ad", "yuk"], "sütunlar: ad, yuk")
beklenen = sorgu("SELECT ad, CASE WHEN cpu >= 80 THEN 'yüksek' WHEN cpu >= 50 THEN 'orta' ELSE 'düşük' END FROM sunucular ORDER BY ad")
eq(sonuc, beklenen, "sınıflar ve sıra doğru")
```

```solution
SELECT ad,
       CASE
           WHEN cpu >= 80 THEN 'yüksek'
           WHEN cpu >= 50 THEN 'orta'
           ELSE 'düşük'
       END AS yuk
FROM sunucular
ORDER BY ad;
```

```hint
`CASE WHEN koşul THEN değer ... ELSE değer END AS yuk`. Koşulların sırası önemli: önce en yüksek eşik.
```
:::

::: gorev Sabah biletleri
Saat **09:00'dan önce** açılmış biletlerin `id`'sini ve açılış saatini `saat` adıyla (`SS:DD` biçiminde) getir; saate göre sırala.

```starter
SELECT id, acilis
FROM biletler
ORDER BY acilis;
```

```test
eq(sutunlar, ["id", "saat"], "sütunlar: id, saat")
eq(sonuc, [(20, "06:50"), (4, "07:05"), (13, "07:30"), (1, "08:15"), (7, "08:40")], "beş sabah bileti, saate göre")
```

```solution
SELECT id, strftime('%H:%M', acilis) AS saat
FROM biletler
WHERE strftime('%H:%M', acilis) < '09:00'
ORDER BY saat;
```

```hint
`strftime('%H:%M', acilis)` saati metin olarak verir; metin karşılaştırması `< '09:00'` burada doğru çalışır.
```
:::

::: gorev İkinci sayfa
Biletler `id` sırasıyla, sayfa başına **5** bilet gösteriliyor. **İkinci sayfadaki** biletlerin `id` ve `baslik` sütunlarını getir.

```starter
SELECT id, baslik
FROM biletler
ORDER BY id
LIMIT 5;
```

```test
eq([r[0] for r in sonuc], [6, 7, 8, 9, 10], "ikinci sayfa: 6–10")
ok(kullanir("offset"), "OFFSET kullan")
```

```solution
SELECT id, baslik
FROM biletler
ORDER BY id
LIMIT 5 OFFSET 5;
```

```hint
İlk 5'i atla: `LIMIT 5 OFFSET 5`.
```
:::
