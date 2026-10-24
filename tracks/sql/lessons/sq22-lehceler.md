---
id: sq22
title: Lehçeler: Aynı Sorgu, Üç Gerçek Motor
summary: SQLite, PostgreSQL ve MariaDB'de aynı ifadenin farklı sonucu: || ve CONCAT, NULL'la birleştirme, tam sayı bölmesi, büyük-küçük harf karşılaştırması, örtük tür dönüşümü ve uyarılar, çift tırnağın anlamı, bayt ve karakter uzunluğu, sıfıra bölme, tarih aritmetiği; katalog (information_schema) ve sürüm/veritabanı fonksiyonları. Bir sorguyu bir motordan ötekine doğru taşımak.
kazanim: 1Z0071 5.2, 1Z0071 9.2, 1Z0071 14.1, 1Z0071 14.2
---

::: anlat Aynı metin, farklı anlam
Bir web uygulamasını incelerken sorgular çoğu zaman SQLite'ta değil, **PostgreSQL** ya da **MySQL/MariaDB**'de çalışır. SQL bir standarttır ama her motor onu kendi **lehçesiyle** konuşur: aynı metin bir motorda doğru sonucu, ötekinde sessizce yanlış sonucu verir. Bu derste her adım gerçek bir motorda çalışır: SQLite (bu yolun her zamanki tezgahı), Kali'deki **PostgreSQL 18** ve **MariaDB 11.8**. Aşağıdaki tablonun her hücresi o motorda ölçülmüştür:

| İfade | SQLite | PostgreSQL | MariaDB |
|---|---|---|---|
| `'a' \|\| 'b'` | `ab` | `ab` | `0`: `\|\|` mantıksal VEYA'dır |
| `CONCAT('a', NULL, 'b')` | `ab` | `ab` | `NULL` |
| `CONCAT_WS('-', 'a', NULL, 'b')` | `a-b` | `a-b` | `a-b` |
| `7 / 2` | `3` | `3` | `3.5000` (`7 DIV 2` → `3`) |
| `'a' = 'A'` | `0` | `f` | `1`: varsayılan karşılaştırma harfe duyarsız |
| `'abc' + 1` | `1` | hata `22P02` | `1` ve bir **uyarı** (1292) |
| `"x"` | `x` (sütun bulamazsa metin) | hata: `x` diye bir **sütun** arar | `x`: metin |
| `LENGTH('çay')` | `3` | `3` | `4`: **bayt** sayar; karakter için `CHAR_LENGTH` |
| `1 / 0` | `NULL` | hata `22012` | `NULL` |
| `CAST('2026-10-24' AS DATE) + 1` | `2027` | `2026-10-25` | `20261025` |
| `TRUE` | `1` | `t` | `1` |
| `ROUND(2.5)` | `3.0` | `3` | `3` |

Birkaç ders çıkar:

- **Sessiz farklar en tehlikelisidir.** MariaDB'de `ad || ' ' || soyad` hata vermez, her satır için `0` döner. Taşınabilir yol `CONCAT_WS(' ', ad, soyad)`'dır: üçünde de aynı çalışır ve `NULL`'ları atlar.
- **Hata mı, uyarı mı?** PostgreSQL çevrilemeyen bir değeri reddeder; MariaDB çoğu zaman bir değer üretip **uyarı** bırakır (`SHOW WARNINGS`). Uyarıları okumayan bir uygulama yanlış veriyle devam eder.
- **Çift tırnak:** standartta ve PostgreSQL'de çift tırnak bir **ad**dır (`"Büyük Ad"`), metin tek tırnaktır. MariaDB'de çift tırnak varsayılan olarak metindir; adlar ters tırnakla yazılır (`` `tablo` ``).
- **Tarih aritmetiği** lehçeye en çok bağlı alandır: PostgreSQL'de `tarih + 1` bir gündür, MariaDB'de `tarih + INTERVAL 1 DAY` yazılır, SQLite'ta `date(tarih, '+1 day')`.

```sql
SELECT 'a' || 'b' AS veya, CONCAT_WS(' ', 'Ayşe', NULL, 'Kaya') AS ad,
       7 / 2 AS bolum, 7 DIV 2 AS tam_bolum, 'abc' + 1 AS donusum;
SHOW WARNINGS;
```

```meta
motor: mariadb
```

> [!NOT]
> **MariaDB, MySQL'in her sürümüyle aynı değildir.** Ortak bir kökten ayrıldılar; JSON türleri, varsayılan `sql_mode` ve karşılaştırma düzenleri sürüme göre farklıdır. Bir sonucu "MySQL'de de böyledir" diye genellemeden önce hedef sürümde dene. SQL Server ise birleştirmede `+` ve satır sınırlamada `TOP` / `OFFSET … FETCH` kullanır; bu tezgahta SQL Server yoktur.
:::

::: anlat Motor kendini anlatır: katalog
Bir veritabanına ilk bağlanışta sorulan "hangi motor, hangi sürüm, hangi tablolar?" sorularının yanıtı da lehçeye göre değişir:

| Soru | SQLite | PostgreSQL | MariaDB |
|---|---|---|---|
| sürüm | `sqlite_version()` | `version()` | `VERSION()` |
| hangi veritabanı | (dosyanın kendisi) | `current_database()` | `DATABASE()` |
| tablolar | `sqlite_master` | `information_schema.tables` | `information_schema.tables` |
| sütunlar | `pragma_table_info('t')` | `information_schema.columns` | `information_schema.columns` |

`information_schema` standarttır, ama içeriği değil yalnız biçimi ortaktır. PostgreSQL'de tablolar şemalara (`public`) ayrılır; MariaDB'de `table_schema` **veritabanının adıdır**. Görünümler de (`VIEW`) `information_schema.columns`'ta sütunlarıyla görünür; yalnız tabloları istiyorsan `information_schema.tables`'ta `table_type = 'BASE TABLE'` olanları al. MariaDB `information_schema` sütun adlarını büyük harfle döndürür (`TABLE_NAME`); takma ad vermek sonucu öngörülebilir kılar.

```sql
CREATE TABLE siparisler (id serial PRIMARY KEY, tutar numeric(10,2));
CREATE VIEW buyukler AS SELECT * FROM siparisler WHERE tutar > 100;
SELECT current_database() LIKE 'pafta%' AS lab, split_part(version(), ' ', 2) AS surum;
SELECT table_name, table_type FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;
```

```meta
motor: postgres
```
:::

::: tahmin MariaDB ne der?
Tek satır, beş değer.

```sql
SELECT 'a' || 'b', CONCAT('a', NULL, 'b'), 7 / 2, 'a' = 'A', LENGTH('çay');
```

```meta
motor: mariadb
```

???

`0|NULL|3.5000|1|4`. MariaDB'de `||` mantıksal VEYA'dır: iki metin sayıya çevrilir (ikisi de 0) ve sonuç 0'dır. `CONCAT` tek bir `NULL` argümanla bütünüyle `NULL` olur. `/` her zaman ondalık böler. Varsayılan karşılaştırma düzeni (`utf8mb4_uca1400_ai_ci`) büyük-küçük harfe duyarsızdır: `'a' = 'A'` doğrudur (1). `LENGTH` bayt sayar; `ç` UTF-8'de iki bayttır, `çay` dört bayt eder.
:::

::: gorev Raporu MariaDB'ye taşı
Bu sorgu SQLite'ta doğru çalışıyordu:

```text
SELECT ad || ' ' || soyad AS tam_ad, gorev_dk / 60 AS saat
FROM personel
WHERE kullanici = 'admin'
ORDER BY id;
```

Aynı **sonucu** MariaDB'de veren sorguyu yaz. Kurallar SQLite'taki anlamla aynı kalmalı:

- `tam_ad`: ad ve soyad arasında bir boşluk; soyad `NULL` ise **yalnız ad** (sonda boşluk yok).
- `saat`: dakikanın 60'a **tam sayı** bölümü (59 dakika → 0, 60 → 1, 119 → 1).
- `kullanici` karşılaştırması **büyük-küçük harfe duyarlı**: `Admin` ya da `ADMIN` gelmez.
- Sütunlar `tam_ad`, `saat`; `id` sırasıyla.

```setup
CREATE TABLE personel (id INT PRIMARY KEY, ad VARCHAR(30) NOT NULL, soyad VARCHAR(30), gorev_dk INT NOT NULL, kullanici VARCHAR(20) NOT NULL);
INSERT INTO personel VALUES
    (1, 'Selin', 'Kaya', 125, 'admin'),
    (2, 'Kerem', NULL, 59, 'admin'),
    (3, 'Ayşe', 'Demir', 60, 'Admin'),
    (4, 'Mert', 'Çelik', 240, 'ADMIN'),
    (5, 'Zeynep', 'Ak', 119, 'admin'),
    (6, 'Can', 'Er', 30, 'operator');
```

```meta
motor: mariadb
```

```starter
SELECT ad || ' ' || soyad AS tam_ad, gorev_dk / 60 AS saat
FROM personel
WHERE kullanici = 'admin'
ORDER BY id;
```

```test
eq(sonuc, [("Selin Kaya", 2), ("Kerem", 0), ("Zeynep Ak", 1)], "üç admin: NULL soyad, 59 ve 119 dakika")
eq(sutunlar, ["tam_ad", "saat"], "sütunlar: tam_ad, saat")
eq(dene("INSERT INTO personel VALUES (7, 'Ece', 'Su', 60, 'admin'), (8, 'Deniz', 'Ay', 0, 'admin');")[-2:],
   [("Ece Su", 1), ("Deniz Ay", 0)], "tam 60 dakika 1 saat; 0 dakika 0")
eq(dene("INSERT INTO personel VALUES (9, 'Elif', '', 61, 'admin');")[-1], ("Elif ", 1),
   "boş metin soyad NULL değildir: arada boşluk kalır")
eq(dene("UPDATE personel SET kullanici = 'admin ' WHERE id = 6;"), sonuc,
   "sondaki boşluk farklı bir kullanıcıdır (PAD SPACE karşılaştırmasına dikkat)")
ok(not any(u[2] == 1292 for u in uyarilar), "çevrilemeyen metin uyarısı yok (|| VEYA olarak kullanılmamış)")
```

```solution
SELECT CONCAT_WS(' ', ad, soyad) AS tam_ad, gorev_dk DIV 60 AS saat
FROM personel
WHERE kullanici = BINARY 'admin'
ORDER BY id;
```

```hint
MariaDB'de `||` birleştirme değil VEYA'dır. `CONCAT_WS(' ', ad, soyad)` ayırıcıyı koyar ve `NULL`'ı atlar. Tam sayı bölümü `DIV`.
```

```hint
Varsayılan karşılaştırma harfe duyarsızdır. Birebir karşılaştırma için bir tarafı ikili karşılaştırmaya çevir: `kullanici = BINARY 'admin'` ya da `COLLATE utf8mb4_bin`. İkili karşılaştırma sondaki boşluğu da önemser.
```
:::

::: gorev Oranı PostgreSQL'e taşı
SQLite'ta yazılmış bu rapor her sunucu için başarılı yedek oranını veriyordu:

```text
SELECT "ad", basarili * 1.0 / toplam AS oran
FROM yedek_ozet
ORDER BY "ad";
```

Aynı raporu PostgreSQL'de yaz:

- `ad` ve `oran` sütunları, ada göre sıralı.
- `oran`: `basarili / toplam`, **iki ondalık basamağa yuvarlanmış** ondalık sayı (`numeric`).
- Hiç yedek alınmamış sunucuda (`toplam = 0`) sorgu **hata vermemeli**; `oran` `NULL` olmalı.
- Tabloda bir sütunun adı büyük harf ve boşluk içeriyor (`"Son Durum"`): onu da üçüncü sütun olarak `son_durum` adıyla getir.

```setup
CREATE TABLE yedek_ozet (ad text PRIMARY KEY, basarili int NOT NULL, toplam int NOT NULL, "Son Durum" text);
INSERT INTO yedek_ozet VALUES ('web01', 29, 30, 'tamam'), ('db01', 2, 3, 'uyarı'), ('test01', 0, 0, NULL), ('dc01', 1, 1, 'tamam');
```

```meta
motor: postgres
```

```starter
SELECT "ad", basarili * 1.0 / toplam AS oran
FROM yedek_ozet
ORDER BY "ad";
```

```test
from decimal import Decimal
eq(sonuc, [("db01", Decimal("0.67"), "uyarı"), ("dc01", Decimal("1.00"), "tamam"),
           ("test01", None, None), ("web01", Decimal("0.97"), "tamam")], "dört sunucu; toplamı 0 olan NULL, hata yok")
eq(sutunlar, ["ad", "oran", "son_durum"], "sütunlar: ad, oran, son_durum")
eq(dene("INSERT INTO yedek_ozet VALUES ('a01', 1, 8, 'x'), ('b01', 5, 8, 'y');")[:2],
   [("a01", Decimal("0.13"), "x"), ("b01", Decimal("0.63"), "y")], "0.125 → 0.13 ve 0.625 → 0.63: numeric yuvarlama yarımı yukarı")
eq(dene("INSERT INTO yedek_ozet VALUES ('z01', 7, 7, NULL);")[-1], ("z01", Decimal("1.00"), None), "tam oran 1.00")
eq(sorgu("SELECT pg_typeof(round(1::numeric / 3, 2))::text"), [("numeric",)], "ölçüm: round(numeric, 2) numeric döner")
```

```solution
SELECT ad,
       round(basarili::numeric / NULLIF(toplam, 0), 2) AS oran,
       "Son Durum" AS son_durum
FROM yedek_ozet
ORDER BY ad;
```

```hint
PostgreSQL'de `int / int` tam sayı böler (2/3 → 0). Birini `numeric`'e çevir: `basarili::numeric / toplam`. `round(x, 2)` yalnız `numeric` alır.
```

```hint
Sıfıra bölme PostgreSQL'de hatadır. `NULLIF(toplam, 0)` 0'ı `NULL`'a çevirir; `NULL`'a bölmek `NULL` verir. Boşluklu ad çift tırnakla yazılır: `"Son Durum"`.
```
:::

::: gorev MariaDB'de şema raporu
MariaDB'de bu çalıştırmanın veritabanındaki **tabloları** ve her tablonun sütun sayısını, tablo adına göre sıralı getir: `tablo`, `sutun`. Görünümler rapora girmez. Veritabanının adını elle yazma: her çalıştırmada değişir; `DATABASE()` ile al.

```setup
CREATE TABLE sunucular (id INT PRIMARY KEY, ad VARCHAR(20), rol VARCHAR(20), cpu INT);
CREATE TABLE olaylar (id INT PRIMARY KEY, sunucu_id INT, kayit JSON);
CREATE VIEW yuksek_cpu AS SELECT ad, cpu FROM sunucular WHERE cpu > 80;
```

```meta
motor: mariadb
```

```starter
SELECT table_name, COUNT(*)
FROM information_schema.columns
GROUP BY table_name;
```

```test
eq(sonuc, [("olaylar", 3), ("sunucular", 4)], "iki tablo; görünüm yok")
eq(sutunlar, ["tablo", "sutun"], "sütunlar: tablo, sutun")
eq(dene("CREATE TABLE ayarlar (anahtar VARCHAR(20) PRIMARY KEY, deger TEXT);"),
   [("ayarlar", 2), ("olaylar", 3), ("sunucular", 4)], "yeni tablo ada göre yerine girer")
eq(dene("CREATE VIEW tum AS SELECT * FROM sunucular;"), sonuc, "yeni görünüm de girmez")
eq(dene("ALTER TABLE olaylar ADD COLUMN zaman DATETIME;"), [("olaylar", 4), ("sunucular", 4)], "sütun sayısı güncel")
```

```solution
SELECT c.table_name AS tablo, COUNT(*) AS sutun
FROM information_schema.columns AS c
JOIN information_schema.tables AS t
  ON t.table_schema = c.table_schema AND t.table_name = c.table_name
WHERE c.table_schema = DATABASE() AND t.table_type = 'BASE TABLE'
GROUP BY c.table_name
ORDER BY c.table_name;
```

```hint
`information_schema.columns`'ı `table_schema = DATABASE()` ile bu veritabanına daralt; yoksa sunucudaki sistem tabloları da gelir.
```

```hint
Görünümleri ayırmak için `information_schema.tables` ile birleştir ve `table_type = 'BASE TABLE'` olanları al. Sütun adları MariaDB'de büyük harfle döner; `AS tablo`, `AS sutun` ver.
```
:::
