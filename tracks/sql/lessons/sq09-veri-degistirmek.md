---
id: sq09
title: Tablo Kurmak ve Veriyi Değiştirmek
summary: CREATE TABLE ve kısıtlar, INSERT/UPDATE/DELETE, işlemler (BEGIN/COMMIT/ROLLBACK), indeksler ve sorgu planı, uygulamadan güvenli sorgu.
---

::: anlat Tablo kurmak
```sql
CREATE TABLE bakimlar (
    id        INTEGER PRIMARY KEY,                           #! her satırın benzersiz kimliği
    sunucu_id INTEGER NOT NULL REFERENCES sunucular(id),     #! var olan bir sunucu olmalı
    tarih     TEXT NOT NULL,
    sure_dk   INTEGER CHECK (sure_dk > 0),                   #! kural: pozitif
    aciklama  TEXT DEFAULT ''
);
INSERT INTO bakimlar (sunucu_id, tarih, sure_dk)
VALUES (4, '2026-10-20', 90),
       (1, '2026-10-21', 30);
SELECT b.id, s.ad, b.tarih, b.sure_dk
FROM bakimlar AS b
JOIN sunucular AS s ON s.id = b.sunucu_id;
```

Kısıtlar veriyi koruyan kurallardır; ihlal eden komut **reddedilir**:

| Kısıt | Anlamı |
|---|---|
| `PRIMARY KEY` | benzersiz kimlik; `INTEGER PRIMARY KEY` verilmezse otomatik artar |
| `NOT NULL` | boş bırakılamaz |
| `UNIQUE` | aynı değer iki kez olamaz (`UNIQUE (a, b)`: ikili benzersiz) |
| `CHECK (koşul)` | koşul doğru olmalı |
| `REFERENCES t(id)` | yabancı anahtar: t'de karşılığı olmalı |

```sql norun
INSERT INTO bakimlar (sunucu_id, tarih, sure_dk) VALUES (99, '2026-10-22', 10);
-- SQLHatası: FOREIGN KEY kısıtı ihlal edildi (99 numaralı sunucu yok)
```

> [!NOT]
> SQLite yabancı anahtar denetimini varsayılan olarak **kapalı** başlatır; `PRAGMA foreign_keys = ON;` ile açılır. Bu tezgahta açık. Kendi uygulamanda her bağlantıda açmayı unutma.
:::

::: anlat Değiştirmek, silmek ve işlemler
```sql
UPDATE sunucular SET ram_gb = 32 WHERE ad = 'yedek01';   #! WHERE: hangi satırlar
DELETE FROM biletler WHERE durum = 'çözüldü' AND kapanis < '2026-10-14';
INSERT INTO ekipler (ad, vardiya) VALUES ('Güvenlik', 'gece');
SELECT * FROM ekipler;
```

> [!TUZAK]
> `WHERE`'siz `UPDATE` ya da `DELETE` **bütün tabloyu** değiştirir. Gerçek bir veritabanında önce aynı WHERE ile bir `SELECT` çalıştırıp etkilenecek satırları gör, sonra değiştir.

**İşlem** (transaction) birden çok komutu tek bir bütün yapar: ya hepsi kalıcı olur (`COMMIT`) ya hiçbiri (`ROLLBACK`). Yarıda kesilen bir işlem veriyi yarım bırakmaz.

```sql
BEGIN;
UPDATE sunucular SET cpu = 0;                          #! WHERE unutuldu!
SELECT COUNT(*) FROM sunucular WHERE cpu = 0;          #! 12
ROLLBACK;                                              #! geri al
SELECT COUNT(*) FROM sunucular WHERE cpu = 0;          #! 0
```

### İndeks ve sorgu planı
İndeks, bir sütunun sıralı bir kopyasıdır; kitabın arkasındaki dizin gibi. İndeks yokken veritabanı koşulu sağlayan satırları bulmak için tablonun **tamamını** okur. Aşağıdaki kodu tezgaha al ve **Plan** düğmesine bas: indeks satırını silince planın `SCAN`'den (tamamını oku) `SEARCH`'e (doğrudan bul) nasıl döndüğüne bak.

```sql
CREATE INDEX ix_biletler_atanan ON biletler(atanan_id);
SELECT id, baslik FROM biletler WHERE atanan_id = 6;
```

İndeksler okumayı hızlandırır, yazmayı biraz yavaşlatır ve yer kaplar: sık süzülen ve birleştirilen sütunlara koyulur.

> [!GÜVENLİK]
> Uygulama kodundan sorgu çalıştırırken kullanıcıdan gelen değeri SQL metnine **asla** birleştirerek ekleme; değeri her zaman **parametre** olarak geçir. Böylece değer ne içerirse içersin veri olarak kalır, sorgunun parçası olmaz:
>
> ```python
> cur.execute("SELECT id, baslik FROM biletler WHERE atanan_id = ?", (kullanici_id,))
> ```
:::

::: tahmin
İki sayı:

```sql
BEGIN;
DELETE FROM biletler WHERE durum = 'çözüldü';
SELECT COUNT(*) FROM biletler;
ROLLBACK;
SELECT COUNT(*) FROM biletler;
```

???

`9`, sonra `20`. İşlemin içinde 11 çözülmüş bilet silinir ve 9 kalır; `ROLLBACK` silmeyi geri alır, tablo eski haline (20) döner.
:::

::: gorev Yama tablosu
`yamalar` tablosunu kur: `id` (tam sayı birincil anahtar), `sunucu_id` (boş olamaz, `sunucular`'a yabancı anahtar), `kod` (metin, boş olamaz), `tarih` (metin, boş olamaz). Aynı sunucuya aynı yama **iki kez** kaydedilememeli. Sonra üç kayıt ekle: db01 (`id` 4) için `KB-1001` (`2026-10-15`) ve `KB-1002` (`2026-10-18`), web01 (`id` 1) için `KB-1001` (`2026-10-16`).

```starter
CREATE TABLE yamalar (
    id INTEGER,
    sunucu_id INTEGER,
    kod TEXT,
    tarih TEXT
);
```

```test
eq(sorgu("SELECT sunucu_id, kod, tarih FROM yamalar ORDER BY tarih"),
   [(4, "KB-1001", "2026-10-15"), (1, "KB-1001", "2026-10-16"), (4, "KB-1002", "2026-10-18")], "üç kayıt")
def reddedilir(sql):
    try:
        sorgu(sql)
    except Exception:
        return True
    return False
ok(reddedilir("INSERT INTO yamalar (sunucu_id, kod, tarih) VALUES (4, 'KB-1001', '2026-10-19')"), "aynı sunucuya aynı yama ikinci kez eklenememeli (UNIQUE)")
ok(reddedilir("INSERT INTO yamalar (sunucu_id, kod, tarih) VALUES (99, 'KB-9', '2026-10-19')"), "olmayan sunucuya yama eklenememeli (REFERENCES)")
ok(reddedilir("INSERT INTO yamalar (sunucu_id, tarih) VALUES (4, '2026-10-19')"), "kod boş bırakılamamalı (NOT NULL)")
```

```solution
CREATE TABLE yamalar (
    id        INTEGER PRIMARY KEY,
    sunucu_id INTEGER NOT NULL REFERENCES sunucular(id),
    kod       TEXT NOT NULL,
    tarih     TEXT NOT NULL,
    UNIQUE (sunucu_id, kod)
);
INSERT INTO yamalar (sunucu_id, kod, tarih)
VALUES (4, 'KB-1001', '2026-10-15'),
       (1, 'KB-1001', '2026-10-16'),
       (4, 'KB-1002', '2026-10-18');
```

```hint
İkili benzersizlik tablo düzeyinde bir kısıttır: sütunlardan sonra `UNIQUE (sunucu_id, kod)`.
```
:::

::: gorev Hedefli güncelleme
İki değişiklik yap: test01'in sorumlusunu Can (`id` 6) yap ve 17 numaralı bileti çöz (`durum` = `çözüldü`, `kapanis` = `2026-10-19 12:00`). Başka hiçbir satır değişmemeli.

```starter
UPDATE biletler SET durum = 'çözüldü';
```

```test
eq(sorgu("SELECT sorumlu_id FROM sunucular WHERE ad = 'test01'"), [(6,)], "test01'in sorumlusu 6")
eq(sorgu("SELECT durum, kapanis FROM biletler WHERE id = 17"), [("çözüldü", "2026-10-19 12:00")], "17 çözüldü")
eq(sorgu("SELECT COUNT(*) FROM biletler WHERE durum = 'çözüldü'"), [(12,)], "yalnızca bir bilet daha çözüldü (11 → 12)")
eq(sorgu("SELECT COUNT(*) FROM sunucular WHERE sorumlu_id = 6"), [(4,)], "Can'ın sunucu sayısı 3 → 4")
```

```solution
UPDATE sunucular
SET sorumlu_id = 6
WHERE ad = 'test01';

UPDATE biletler
SET durum = 'çözüldü',
    kapanis = '2026-10-19 12:00'
WHERE id = 17;
```

```hint
Her UPDATE'in bir WHERE'i olmalı. Birden çok sütun: `SET a = 1, b = 2`.
```
:::

::: gorev Arşivle
Çözülmüş biletleri `arsiv` adlı yeni bir tabloya taşı: `arsiv` tablosunu çözülmüş biletlerle oluştur, sonra onları `biletler`'den sil. İki adımı **tek bir işlem** içinde yap.

```starter
CREATE TABLE arsiv AS
SELECT * FROM biletler WHERE durum = 'çözüldü';
```

```test
eq(sorgu("SELECT COUNT(*) FROM arsiv"), [(11,)], "arşivde 11 bilet")
eq(sorgu("SELECT COUNT(*) FROM biletler"), [(9,)], "biletler'de 9 açık bilet kaldı")
eq(sorgu("SELECT COUNT(*) FROM biletler WHERE durum = 'çözüldü'"), [(0,)], "biletler'de çözülmüş kalmadı")
ok(kullanir("begin") and kullanir("commit"), "BEGIN ... COMMIT ile tek işlem")
```

```solution
BEGIN;
CREATE TABLE arsiv AS
SELECT * FROM biletler WHERE durum = 'çözüldü';
DELETE FROM biletler WHERE durum = 'çözüldü';
COMMIT;
```

```hint
`CREATE TABLE ... AS SELECT ...` sorgu sonucundan tablo kurar. İkisini `BEGIN;` ve `COMMIT;` arasına al.
```
:::

::: gorev İndeksle arama
Aşağıdaki sorgu `biletler` tablosunu baştan sona tarıyor. Planı `SEARCH ... USING INDEX` olacak şekilde bir indeks oluştur (sorguyu değiştirme). Plan düğmesiyle kontrol edebilirsin.

```starter
-- indeksi burada oluştur

SELECT id, baslik FROM biletler WHERE atanan_id = 3;
```

```test
plan = " ".join(r[3] for r in sorgu("EXPLAIN QUERY PLAN SELECT id, baslik FROM biletler WHERE atanan_id = 3"))
ok("USING INDEX" in plan, "sorgu indeksle aranıyor olmalı", got=plan)
eq(sorted(r[0] for r in sonuc), [1, 3, 20], "sorgu sonucu değişmedi: 1, 3, 20")
```

```solution
CREATE INDEX ix_biletler_atanan ON biletler(atanan_id);

SELECT id, baslik FROM biletler WHERE atanan_id = 3;
```

```hint
`CREATE INDEX ad ON tablo(sütun);` WHERE'de süzülen sütun: `atanan_id`.
```
:::
