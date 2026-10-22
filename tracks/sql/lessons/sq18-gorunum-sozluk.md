---
id: sq18
title: Görünümler ve Veri Sözlüğü
summary: CREATE VIEW ile bir sorguya ad vermek, görünümün veriyi değil sorguyu saklaması, DROP VIEW ve IF EXISTS; veritabanının kendi yapısını sorgulamak: sqlite_master, PRAGMA table_info ve pragma_table_info, öteki veritabanlarındaki information_schema.
kazanim: 1Z0071 8.4, 1Z0071 9.1, 1Z0071 9.2, 1Z0071 11.2, 1Z0071 18.1
---

::: anlat Görünüm: adı olan bir sorgu
Sık yazılan bir sorguya bir ad verip onu bir tablo gibi kullanabilirsin. Buna **görünüm** (view) denir:

```sql
CREATE VIEW acik_kritikler AS
SELECT id, baslik, acilis
FROM biletler
WHERE durum = 'açık' AND oncelik IN ('yüksek', 'kritik');

SELECT * FROM acik_kritikler ORDER BY acilis;
```

| Komut | Ne yapar |
|---|---|
| `CREATE VIEW ad AS SELECT ...` | sorguyu bu adla kaydeder |
| `CREATE VIEW IF NOT EXISTS ad AS ...` | aynı adda bir görünüm varsa dokunmaz |
| `DROP VIEW ad` / `DROP VIEW IF EXISTS ad` | görünümü siler; alttaki tablolara dokunmaz |

Görünüm **veriyi saklamaz**, sorguyu saklar. Her kullanıldığında sorgu yeniden çalışır: alttaki tablo değişince görünümün sonucu da değişir. Sütun adları görünümün `SELECT`'inden gelir; `AS` ile verdiğin takma adlar görünümün sütun adları olur. Bir görünüm başka bir görünümün üstüne kurulabilir.

SQLite'ta görünümler **salt okunurdur**: bir görünüme `INSERT`, `UPDATE` ya da `DELETE` yazılamaz (bunun için `INSTEAD OF` tetikleyicisi gerekir). Bazı veritabanları sonucu diskte saklayan **somut görünümler** (materialized view) de sunar; onlar hızlıdır ama yenilenene kadar eski veriyi gösterir.

> [!GÜVENLİK]
> Görünümler bir yetki aracı olarak da kullanılır: bir kullanıcıya ya da uygulamaya tablonun kendisi yerine yalnızca gereken satır ve sütunları gösteren bir görünüm açılır (en az yetki ilkesi). Örneğin personel tablosunun telefon sütunu olmadan bir rehber görünümü.
:::

::: anlat Veri sözlüğü: veritabanı kendini anlatır
Bir veritabanı kendi yapısını da tablolarda tutar. Bu bilgiye **veri sözlüğü** (ya da katalog) denir. SQLite'ta ana kayıt `sqlite_master`'dır (3.33 sürümünden beri `sqlite_schema` adıyla da erişilir):

| Sütun | Ne |
|---|---|
| `type` | `table`, `view`, `index` ya da `trigger` |
| `name` | nesnenin adı |
| `tbl_name` | bağlı olduğu tablo (bir indeks için tablonun adı) |
| `sql` | nesneyi oluşturan `CREATE` cümlesi |

```sql
SELECT type, name FROM sqlite_master ORDER BY type, name;
```

`sqlite_autoindex_...` adlı indeksleri SQLite `UNIQUE` ve `PRIMARY KEY` kısıtları için kendisi oluşturur. `sqlite_` ile başlayan adlar SQLite'ın iç nesneleridir.

Bir tablonun sütunlarını `PRAGMA table_info(tablo)` verir: `cid` (sıra), `name`, `type`, `notnull` (1: `NOT NULL`), `dflt_value` (varsayılan) ve `pk` (birincil anahtardaki sırası). Aynı bilgi bir `SELECT` içinde `pragma_table_info('tablo')` tablo fonksiyonuyla da sorgulanır; böylece süzülür, birleştirilir, sayılır:

```sql
PRAGMA table_info(sunucular);

SELECT name, type FROM pragma_table_info('sunucular') WHERE "notnull" = 1 ORDER BY cid;
```

`notnull` SQL'de anahtar bir kelime olduğu için sütun adı çift tırnakla yazılır. `id INTEGER PRIMARY KEY` sütununun `notnull`'u **0**'dır: SQLite'ta bu sütun satırın kimliğidir ve boş bırakılırsa değeri kendiliğinden atanır.

| Veritabanı | Tablolar | Sütunlar |
|---|---|---|
| SQLite | `sqlite_master` | `PRAGMA table_info`, `pragma_table_info` |
| PostgreSQL, MySQL, SQL Server | `information_schema.tables` | `information_schema.columns` |
| Oracle | `all_tables` | `all_tab_columns` |

`information_schema` bir standarttır: `SELECT table_name FROM information_schema.tables` çoğu veritabanında çalışır. Bir veritabanına ilk kez bağlanan bir analistin ilk sorgusu çoğu zaman budur.
:::

::: tahmin
Üç sonuç. Hangileri?

```sql
CREATE VIEW kritikler AS
SELECT id, baslik FROM biletler WHERE oncelik = 'kritik';

SELECT COUNT(*) FROM kritikler;

UPDATE biletler SET oncelik = 'kritik' WHERE id = 1;

SELECT COUNT(*) FROM kritikler;

SELECT type, name FROM sqlite_master WHERE name = 'kritikler';
```

???

`3`, `4` ve `view|kritikler`. Görünüm oluşturulduğunda üç kritik bilet var. Görünüm sonucu saklamadığı için 1 numaralı bilet kritik yapıldıktan sonra aynı görünüm dört satır verir. Görünüm de veri sözlüğüne bir kayıt olarak girer: türü `view`.
:::

::: gorev Açık bilet görünümü
Durumu `açık` olan biletlerin `id`, `baslik` ve `oncelik` sütunlarını veren `acik_biletler` adında bir görünüm oluştur. Sonra görünümden bütün satırları `id` sırasıyla getir.

```starter
SELECT id, baslik, oncelik FROM biletler WHERE durum = 'açık';
```

```test
eq(sutunlar, ["id", "baslik", "oncelik"], "sütunlar: id, baslik, oncelik")
eq([r[0] for r in sonuc], [3, 5, 9, 10, 12, 15, 17, 18, 20], "açık biletler, id sırasıyla")
eq(sorgu("SELECT type FROM sqlite_master WHERE name = 'acik_biletler'"), [("view",)], "acik_biletler bir görünüm")
eq([r[0] for r in dene("UPDATE biletler SET durum = 'açık' WHERE id = 1; UPDATE biletler SET durum = 'çözüldü' WHERE id = 20;")],
   [1, 3, 5, 9, 10, 12, 15, 17, 18], "görünüm her seferinde güncel veriyi verir (sabit liste yazma)")
ok(kullanir("create view"), "CREATE VIEW kullan")
```

```solution
CREATE VIEW acik_biletler AS
SELECT id, baslik, oncelik
FROM biletler
WHERE durum = 'açık';

SELECT * FROM acik_biletler ORDER BY id;
```

```hint
`CREATE VIEW acik_biletler AS SELECT ...;` sonra `SELECT * FROM acik_biletler ORDER BY id;`. İki cümleyi `;` ile ayır.
```
:::

::: gorev Zorunlu sütunlar
`sunucular` tablosunun `NOT NULL` olan (`notnull` değeri 1) sütunlarının adlarını, tablodaki sıralarıyla getir. Sütun listesini kendin yazma: veri sözlüğünden oku.

```starter
SELECT 'ad', 'rol';
```

```test
eq(sonuc, [("ad",), ("rol",), ("isletim",), ("cpu",), ("devreye",)], "beş zorunlu sütun, tablodaki sırayla")
eq(dene("ALTER TABLE sunucular ADD COLUMN etiket TEXT NOT NULL DEFAULT 'yok'; ALTER TABLE sunucular ADD COLUMN notu TEXT;"),
   [("ad",), ("rol",), ("isletim",), ("cpu",), ("devreye",), ("etiket",)],
   "tablo değişince sonuç da değişir: yeni NOT NULL sütun eklenir, NULL olabilen eklenmez")
ok(kullanir("pragma_table_info") or kullanir("table_info"), "veri sözlüğünü kullan")
```

```solution
SELECT name
FROM pragma_table_info('sunucular')
WHERE "notnull" = 1
ORDER BY cid;
```

```hint
`pragma_table_info('sunucular')` bir tablo gibi sorgulanır. `notnull` sütununu çift tırnakla yaz ve `cid` ile sırala.
```
:::

::: gorev Şema raporu
Veritabanındaki her **tablonun** adını ve kaç sütunu olduğunu, ada göre sıralı getir: `name` ve `sutun`. Görünümler, indeksler ve SQLite'ın iç tabloları (`sqlite_` ile başlayanlar) rapora girmez.

```starter
SELECT name, 0 AS sutun FROM sqlite_master ORDER BY name;
```

```test
eq(sonuc, [("biletler", 9), ("ekipler", 3), ("isler", 7), ("olcumler", 3), ("personel", 6), ("sla", 2), ("sunucular", 9)],
   "yedi tablo ve sütun sayıları")
eq(sutunlar, ["name", "sutun"], "sütunlar: name, sutun")
eq(dene("CREATE VIEW v AS SELECT 1 AS a;"), sonuc, "görünümler rapora girmez")
eq(dene("CREATE TABLE yeni (a, b, c);"), sonuc + [("yeni", 3)], "yeni tablo ada göre yerine girer")
eq(dene("CREATE TABLE kayit (id INTEGER PRIMARY KEY AUTOINCREMENT, x); INSERT INTO kayit (x) VALUES (1);"),
   sonuc[:3] + [("kayit", 2)] + sonuc[3:], "AUTOINCREMENT'in açtığı sqlite_sequence iç tablodur, rapora girmez")
```

```solution
SELECT m.name, COUNT(p.cid) AS sutun
FROM sqlite_master AS m
JOIN pragma_table_info(m.name) AS p
WHERE m.type = 'table' AND m.name NOT LIKE 'sqlite_%'
GROUP BY m.name
ORDER BY m.name;
```

```hint
`sqlite_master`'ı `pragma_table_info(m.name)` ile birleştir: her tablo için sütunları kadar satır gelir. `GROUP BY m.name` ve `COUNT(p.cid)` ile say.
```

```hint
Yalnızca `type = 'table'` olanları al ve `name NOT LIKE 'sqlite_%'` ile iç tabloları dışarıda bırak.
```
:::
