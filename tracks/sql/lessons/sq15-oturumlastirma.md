---
id: sq15
title: Oturumlaştırma ve Olay Dizileri
summary: Zaman damgalı olayları aralarındaki boşluğa göre oturumlara ayırmak; LAG ile ara süre, yeni oturum bayrağı, kümülatif toplamla oturum numarası ve oturum özetleri.
---

::: anlat Olayları oturumlara bölmek
Kayıtlar tek tek olaylardır: bir sayfa açıldı, bir istek geldi, bir bilet açıldı. Çoğu soru ise **olay gruplarıyla** ilgilidir: "Kullanıcı kaç kez oturum açıp çalıştı?", "Arızalar hangi dalgalar halinde geldi?" Ardışık iki olay arasında belirli bir süreden (eşik) uzun bir sessizlik varsa yeni bir oturum başlamış sayılır.

Teknik üç adımdır:

1. `LAG` ile her olayın bir öncekinden ne kadar sonra geldiğini bul.
2. İlk olay ya da eşikten uzun ara için 1, değilse 0 olan bir **yeni oturum bayrağı** üret.
3. Bayrağın **kümülatif toplamı** oturum numarasıdır.

```sql
WITH a AS (
    SELECT id, acilis,
           (julianday(acilis) - julianday(LAG(acilis) OVER (ORDER BY acilis))) * 1440 AS ara_dk
    FROM biletler
),
b AS (
    SELECT id, acilis, ara_dk,
           SUM(CASE WHEN ara_dk IS NULL OR ara_dk > 240 THEN 1 ELSE 0 END)
               OVER (ORDER BY acilis ROWS UNBOUNDED PRECEDING) AS dalga
    FROM a
)
SELECT dalga, MIN(acilis) AS bas, MAX(acilis) AS bit, COUNT(*) AS bilet
FROM b
GROUP BY dalga
HAVING COUNT(*) > 1
ORDER BY dalga;
```

Bu sorgu, aralarında 4 saatten kısa boşluk olan biletleri "dalgalar" halinde toplar ve birden çok bilet içeren dalgaları gösterir.

Kullanıcı başına oturum gibi gruplu sorularda `LAG` ve kümülatif toplam `PARTITION BY kullanici` ile her kullanıcı için ayrı hesaplanır.

> [!NOT]
> Eşiğin seçimi sonucu belirler: 30 dakikalık eşik bir kullanıcının gününü beş oturuma, 2 saatlik eşik iki oturuma bölebilir. Web analitiğinde 30 dakika yaygın bir gelenektir; doğru eşik, sorunun anlamına göre seçilir ve raporda yazılır.
:::

::: tahmin
Her satır için oturum numarası:

```sql
WITH t(zaman) AS (VALUES ('2026-10-19 09:00'), ('2026-10-19 09:20'), ('2026-10-19 10:30'), ('2026-10-19 10:40')),
a AS (SELECT zaman, (julianday(zaman) - julianday(LAG(zaman) OVER (ORDER BY zaman))) * 1440 AS ara FROM t)
SELECT substr(zaman, 12), SUM(CASE WHEN ara IS NULL OR ara > 30 THEN 1 ELSE 0 END) OVER (ORDER BY zaman) AS oturum
FROM a;
```

???

`09:00|1`, `09:20|1`, `10:30|2`, `10:40|2`. İlk olay yeni oturumdur. 20 dakikalık ara eşiğin altında, aynı oturum. 70 dakikalık ara eşiği aşar, ikinci oturum başlar; ardından gelen 10 dakikalık ara yine aynı oturumdur.
:::

::: gorev Oturum numaraları
`etkinlik` tablosunda bir iç uygulamada kullanıcıların işlem zamanları var. Aralarında **30 dakikadan uzun** boşluk olan işlemler ayrı oturum sayılır. Her işlem için `kullanici`, `zaman`, `oturum` (kullanıcı başına 1'den başlayan numara) getir; kullanıcıya sonra zamana göre sıralı.

```setup
CREATE TABLE etkinlik (kullanici TEXT, zaman TEXT);
INSERT INTO etkinlik VALUES
 ('ece','2026-10-19 09:00'), ('ece','2026-10-19 09:10'), ('ece','2026-10-19 09:25'), ('ece','2026-10-19 11:00'),
 ('ece','2026-10-19 11:05'), ('ece','2026-10-19 15:30'), ('can','2026-10-19 09:05'), ('can','2026-10-19 09:50'),
 ('can','2026-10-19 10:15'), ('can','2026-10-19 10:20'), ('mert','2026-10-19 14:00');
```

```starter
SELECT kullanici, zaman, 1 AS oturum
FROM etkinlik
ORDER BY kullanici, zaman;
```

```test
eq(sutunlar, ["kullanici", "zaman", "oturum"], "sütunlar")
eq([(r[0], r[2]) for r in sonuc], [("can", 1), ("can", 2), ("can", 2), ("can", 2), ("ece", 1), ("ece", 1), ("ece", 1),
                                    ("ece", 2), ("ece", 2), ("ece", 3), ("mert", 1)], "oturum numaraları")
```

```solution
WITH a AS (
    SELECT kullanici, zaman,
           (julianday(zaman) - julianday(LAG(zaman) OVER (PARTITION BY kullanici ORDER BY zaman))) * 1440 AS ara
    FROM etkinlik
)
SELECT kullanici, zaman,
       SUM(CASE WHEN ara IS NULL OR ara > 30 THEN 1 ELSE 0 END)
           OVER (PARTITION BY kullanici ORDER BY zaman ROWS UNBOUNDED PRECEDING) AS oturum
FROM a
ORDER BY kullanici, zaman;
```

```hint
Her kullanıcı için ayrı: `LAG(zaman) OVER (PARTITION BY kullanici ORDER BY zaman)`. Ara dakika = julianday farkı × 1440.
```

```hint
Yeni oturum bayrağının kümülatif toplamı: `SUM(CASE WHEN ara IS NULL OR ara > 30 THEN 1 ELSE 0 END) OVER (PARTITION BY kullanici ORDER BY zaman ROWS UNBOUNDED PRECEDING)`.
```
:::

::: gorev Oturum özeti
Aynı tablo ve 30 dakikalık eşikle her oturumu özetle: `kullanici`, `oturum`, `bas` (ilk işlemin saati, `SS:DD`), `bit` (son işlemin saati), `islem` (sayı), `sure_dk` (ilk ve son işlem arası dakika); kullanıcıya sonra oturuma göre sıralı.

```setup
CREATE TABLE etkinlik (kullanici TEXT, zaman TEXT);
INSERT INTO etkinlik VALUES
 ('ece','2026-10-19 09:00'), ('ece','2026-10-19 09:10'), ('ece','2026-10-19 09:25'), ('ece','2026-10-19 11:00'),
 ('ece','2026-10-19 11:05'), ('ece','2026-10-19 15:30'), ('can','2026-10-19 09:05'), ('can','2026-10-19 09:50'),
 ('can','2026-10-19 10:15'), ('can','2026-10-19 10:20'), ('mert','2026-10-19 14:00');
```

```starter
SELECT kullanici, COUNT(*) AS islem
FROM etkinlik
GROUP BY kullanici;
```

```test
eq(sutunlar, ["kullanici", "oturum", "bas", "bit", "islem", "sure_dk"], "sütunlar")
eq(sonuc, [("can", 1, "09:05", "09:05", 1, 0), ("can", 2, "09:50", "10:20", 3, 30),
           ("ece", 1, "09:00", "09:25", 3, 25), ("ece", 2, "11:00", "11:05", 2, 5), ("ece", 3, "15:30", "15:30", 1, 0),
           ("mert", 1, "14:00", "14:00", 1, 0)], "altı oturum")
```

```solution
WITH a AS (
    SELECT kullanici, zaman,
           (julianday(zaman) - julianday(LAG(zaman) OVER (PARTITION BY kullanici ORDER BY zaman))) * 1440 AS ara
    FROM etkinlik
),
b AS (
    SELECT kullanici, zaman,
           SUM(CASE WHEN ara IS NULL OR ara > 30 THEN 1 ELSE 0 END)
               OVER (PARTITION BY kullanici ORDER BY zaman ROWS UNBOUNDED PRECEDING) AS oturum
    FROM a
)
SELECT kullanici, oturum,
       strftime('%H:%M', MIN(zaman)) AS bas,
       strftime('%H:%M', MAX(zaman)) AS bit,
       COUNT(*) AS islem,
       CAST(round((julianday(MAX(zaman)) - julianday(MIN(zaman))) * 1440) AS INTEGER) AS sure_dk
FROM b
GROUP BY kullanici, oturum
ORDER BY kullanici, oturum;
```

```hint
Önceki görevin sorgusunu bir CTE'ye al ve `GROUP BY kullanici, oturum` ile özetle.
```

```hint
Süreyi tam sayı dakikaya çevirirken kayan nokta hatasını yuvarlayarak gider: `CAST(round(... * 1440) AS INTEGER)`.
```
:::

::: gorev Eşiğin etkisi
Aynı tabloda eşiği **60 dakika** yapıp her kullanıcının **oturum sayısını** getir: `kullanici`, `oturum_sayisi`; kullanıcıya göre sıralı.

```setup
CREATE TABLE etkinlik (kullanici TEXT, zaman TEXT);
INSERT INTO etkinlik VALUES
 ('ece','2026-10-19 09:00'), ('ece','2026-10-19 09:10'), ('ece','2026-10-19 09:25'), ('ece','2026-10-19 11:00'),
 ('ece','2026-10-19 11:05'), ('ece','2026-10-19 15:30'), ('can','2026-10-19 09:05'), ('can','2026-10-19 09:50'),
 ('can','2026-10-19 10:15'), ('can','2026-10-19 10:20'), ('mert','2026-10-19 14:00');
```

```starter
SELECT kullanici, COUNT(*) AS oturum_sayisi
FROM etkinlik
GROUP BY kullanici;
```

```test
eq(sutunlar, ["kullanici", "oturum_sayisi"], "sütunlar")
eq(sonuc, [("can", 1), ("ece", 3), ("mert", 1)], "60 dakikalık eşikle")
```

```solution
WITH a AS (
    SELECT kullanici,
           (julianday(zaman) - julianday(LAG(zaman) OVER (PARTITION BY kullanici ORDER BY zaman))) * 1440 AS ara
    FROM etkinlik
)
SELECT kullanici,
       SUM(CASE WHEN ara IS NULL OR ara > 60 THEN 1 ELSE 0 END) AS oturum_sayisi
FROM a
GROUP BY kullanici
ORDER BY kullanici;
```

```hint
Oturum sayısı, yeni oturum bayraklarının toplamıdır: kümülatif toplama gerek yok, `GROUP BY kullanici` ile düz `SUM` yeter.
```
:::
