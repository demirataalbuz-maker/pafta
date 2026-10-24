---
id: sq21
title: Roller ve Etkili Yetkiler (PostgreSQL)
summary: Gerçek PostgreSQL'de uygulama hesaplarını en az yetkiyle kurmak ve denetlemek: CREATE ROLE, LOGIN/NOLOGIN, rol üyeliği ve INHERIT, GRANT/REVOKE, sütun düzeyi yetki, dizi (sequence) yetkisi, PUBLIC; has_table_privilege, has_column_privilege, information_schema.role_table_grants ve relacl ile etkili yetkiyi okumak.
kazanim: 1Z0071 19.1, 1Z0071 19.2, 1Z0071 19.3
---

::: anlat Rol: hem kullanıcı hem grup
Bu dersin sorguları SQLite'ta değil, **gerçek bir PostgreSQL** (18) sunucusunda çalışır: SQLite'ın kullanıcı ve yetki kavramı yoktur. Her çalıştırmada boş bir `pafta_lab` veritabanı kurulur; betiğin `pafta_yonetici` adlı bir rolle çalışır. Bu rol süper kullanıcı değildir, yalnızca rol oluşturabilir (`CREATEROLE`) ve veritabanının sahibidir. İş bitince veritabanı ve oluşturduğun bütün roller silinir.

PostgreSQL'de kullanıcı ile grup aynı şeydir: **rol**. Farkı tek bir özellik yapar:

| Komut | Ne kurar |
|---|---|
| `CREATE ROLE rapor_app LOGIN PASSWORD '...'` | bağlanabilen bir rol: bir **hesap** |
| `CREATE ROLE okuma NOLOGIN` | bağlanamayan bir rol: bir **grup** (varsayılan NOLOGIN'dir) |
| `GRANT okuma TO rapor_app` ya da `CREATE ROLE rapor_app LOGIN IN ROLE okuma` | `rapor_app`'i `okuma`'nın üyesi yapar |
| `CREATE ROLE tekil LOGIN NOINHERIT` | üye olduğu grupların yetkilerini **kendiliğinden** kullanmaz |

Yetkiler nesnelere verilir:

| Nesne | Yetkiler |
|---|---|
| tablo | `SELECT`, `INSERT`, `UPDATE`, `DELETE`, `TRUNCATE`, `REFERENCES`, `TRIGGER`, `MAINTAIN` |
| tablo sütunu | `SELECT`, `INSERT`, `UPDATE`, `REFERENCES` |
| dizi (`serial` sütununun arkasındaki sayaç) | `USAGE`, `SELECT`, `UPDATE` |
| şema | `USAGE` (içine bakabilmek), `CREATE` |
| veritabanı | `CONNECT`, `CREATE`, `TEMP` |

`GRANT yetki ON nesne TO rol` verir, `REVOKE yetki ON nesne FROM rol` geri alır. Tablonun **sahibi** her şeyi yapabilir; başka hiçbir rol, açıkça verilmedikçe hiçbir şey yapamaz. Tek istisna **`PUBLIC`**'tir: bütün rollerin, şimdikilerin ve gelecektekilerin üye sayıldığı sözde gruptur. Bir veritabanı kurulduğunda `PUBLIC`'e `CONNECT` ve `TEMP` verilmiş olur.

```sql
CREATE TABLE siparisler (id serial PRIMARY KEY, musteri_id int NOT NULL, tutar numeric NOT NULL);
CREATE ROLE okuma NOLOGIN;
CREATE ROLE rapor_app LOGIN IN ROLE okuma;
GRANT SELECT ON siparisler TO okuma;

SELECT rolname, rolcanlogin, rolinherit FROM pg_roles WHERE rolname IN ('okuma', 'rapor_app') ORDER BY rolname;
```

```meta
motor: postgres
```
:::

::: anlat Etkili yetkiyi okumak
Bir hesabın **etkili** yetkisi üç kaynağın toplamıdır: ona doğrudan verilenler, `INHERIT` ile üye olduğu grupların yetkileri ve `PUBLIC`'e verilenler. Denetimde soru "kime ne verdik?" değil, "bu hesap **gerçekte** ne yapabilir?"dir. PostgreSQL bunu fonksiyonlarla yanıtlar:

| Fonksiyon | Sorduğu |
|---|---|
| `has_table_privilege(rol, 'tablo', 'SELECT')` | rol bu tabloda bu yetkiyi **tablo düzeyinde** kullanabilir mi |
| `has_column_privilege(rol, 'tablo', 'sütun', 'SELECT')` | bu sütunda (tablo düzeyindeki yetki de sayılır) |
| `has_any_column_privilege(rol, 'tablo', 'UPDATE')` | en az bir sütunda |
| `has_schema_privilege(rol, 'public', 'CREATE')` | şemada |
| `has_database_privilege(rol, current_database(), 'CONNECT')` | veritabanında |
| `pg_has_role(rol, 'grup', 'USAGE')` | grubun yetkilerini kendiliğinden kullanıyor mu (`MEMBER`: yalnızca üye mi) |

Kimin neyi **verdiğini** görmek için katalog okunur. `information_schema.role_table_grants` standart görünümdür (her `GRANT` bir satır); `pg_class.relacl` ise PostgreSQL'in ham kaydıdır: `okuma=r/pafta_yonetici` "okuma'ya `r` (SELECT), pafta_yonetici verdi" demektir, rol adı boş olan `=r/...` ise `PUBLIC`'tir. Harfler: `a` INSERT, `r` SELECT, `w` UPDATE, `d` DELETE, `D` TRUNCATE, `x` REFERENCES, `t` TRIGGER, `m` MAINTAIN.

İki tuzak denetimde sık kaçırılır:

- **Sütun düzeyi yetki** tablo düzeyinde görünmez. `GRANT UPDATE (durum) ON siparisler TO ...` sonrasında `has_table_privilege(..., 'UPDATE')` **yanlıştır**, `has_column_privilege(..., 'durum', 'UPDATE')` doğrudur. Yalnızca tablo düzeyine bakan bir rapor bu yetkiyi kaçırır.
- **`PUBLIC` her şeyi deler.** `NOINHERIT` bir hesap gruplarının yetkisini kendiliğinden kullanmaz, ama `PUBLIC`'e verilen her şeyi kullanır.

```sql
CREATE TABLE siparisler (id serial PRIMARY KEY, durum text DEFAULT 'yeni');
CREATE ROLE destek_app LOGIN;
GRANT UPDATE (durum) ON siparisler TO destek_app;
GRANT SELECT ON siparisler TO PUBLIC;

SELECT has_table_privilege('destek_app', 'siparisler', 'UPDATE')          AS tablo_update,
       has_column_privilege('destek_app', 'siparisler', 'durum', 'UPDATE') AS durum_update,
       has_table_privilege('destek_app', 'siparisler', 'SELECT')          AS select_public;

SELECT relacl FROM pg_class WHERE relname = 'siparisler';
```

> [!GÜVENLİK]
> En az yetki ilkesinin PostgreSQL'deki kalıbı: yetkiler **NOLOGIN gruplara** verilir, uygulama hesapları yalnızca gruplara üye olur. Hesap değişince yetkiler yeniden yazılmaz, denetim de grup sayısı kadar kısalır. `GRANT ... ON ALL TABLES IN SCHEMA` yalnızca **o an var olan** tablolara uygulanır; sonradan açılan tablolar için `ALTER DEFAULT PRIVILEGES` gerekir. Uygulama hesabına tablo sahipliği verme: sahip, yetkilerini kendine geri verebilir. (PostgreSQL belgeleri, 5.8 Privileges.)

```meta
motor: postgres
```
:::

::: tahmin
Tek satır, dört değer. PostgreSQL mantıksal değerleri `t` ve `f` diye yazar.

```sql
CREATE TABLE kayitlar (id serial PRIMARY KEY, olay text);
CREATE ROLE okuma NOLOGIN;
CREATE ROLE panel LOGIN IN ROLE okuma;
CREATE ROLE tekil LOGIN NOINHERIT IN ROLE okuma;
GRANT SELECT ON kayitlar TO okuma;

SELECT has_table_privilege('panel', 'kayitlar', 'SELECT'),
       has_table_privilege('tekil', 'kayitlar', 'SELECT'),
       has_table_privilege('panel', 'kayitlar', 'INSERT'),
       has_database_privilege('panel', current_database(), 'CONNECT');
```

```meta
motor: postgres
```

???

`t|f|f|t`. `panel` `okuma`'nın üyesidir ve `INHERIT` (varsayılan) olduğu için grubun `SELECT`'ini kendiliğinden kullanır. `tekil` de üyedir ama `NOINHERIT`'tir: yetkiyi ancak `SET ROLE okuma` deyince kullanabilir, `has_table_privilege` bu yüzden yanlış döner. `INSERT` kimseye verilmedi. `CONNECT` hiç verilmediği hâlde doğrudur: veritabanı kurulurken `PUBLIC`'e verilmiştir.
:::

::: gorev Salt okunur rapor hesabı
Raporlama aracı için iki rol kur:

- `rapor_okur`: **bağlanamayan** bir grup. `siparisler` tablosunun tamamını okuyabilir; `musteriler` tablosundan **yalnızca `id` ve `ad`** sütunlarını okuyabilir (`eposta` ve `tc_no` kişisel veridir).
- `rapor_app`: **bağlanabilen** hesap; `rapor_okur`'un üyesidir. Yetkiler ona doğrudan değil, yalnızca grup üzerinden gelir.

Hiçbir yetki `PUBLIC`'e verilmez; hiçbir rol yazamaz.

```setup
CREATE TABLE musteriler (id serial PRIMARY KEY, ad text NOT NULL, eposta text, tc_no char(11));
CREATE TABLE siparisler (id serial PRIMARY KEY, musteri_id int NOT NULL REFERENCES musteriler(id),
                         tutar numeric(10,2) NOT NULL, durum text NOT NULL DEFAULT 'yeni');
INSERT INTO musteriler (ad, eposta, tc_no) VALUES ('Ayşe', 'ayse@ornek.test', '10000000146'), ('Can', NULL, NULL);
INSERT INTO siparisler (musteri_id, tutar, durum) VALUES (1, 250.00, 'teslim'), (2, 99.90, 'yeni');
```

```meta
motor: postgres
```

```starter
CREATE ROLE rapor_app LOGIN;
GRANT SELECT ON siparisler, musteriler TO rapor_app;
```

```test
eq(sorgu("SELECT rolname, rolcanlogin FROM pg_roles WHERE rolname IN ('rapor_app', 'rapor_okur') ORDER BY rolname"),
   [("rapor_app", True), ("rapor_okur", False)], "rapor_app bağlanır, rapor_okur bağlanamaz")
eq(sorgu("SELECT pg_has_role('rapor_app', 'rapor_okur', 'USAGE')"), [(True,)], "rapor_app grubun yetkisini kullanır")
ok(yapabilir("rapor_app", "SELECT * FROM siparisler"), "siparisler okunur")
ok(yapabilir("rapor_app", "SELECT id, ad FROM musteriler"), "musteriler: id ve ad okunur")
ok(not yapabilir("rapor_app", "SELECT eposta FROM musteriler"), "eposta okunamaz")
ok(not yapabilir("rapor_app", "SELECT tc_no FROM musteriler"), "tc_no okunamaz")
ok(not yapabilir("rapor_app", "SELECT * FROM musteriler"), "SELECT * kişisel sütunlara takılır")
ok(not yapabilir("rapor_app", "SELECT count(*) FROM musteriler WHERE eposta IS NULL"), "WHERE içinde de kişisel sütun okunamaz")
ok(not yapabilir("rapor_app", "INSERT INTO siparisler (musteri_id, tutar) VALUES (1, 1)"), "yazamaz")
ok(not yapabilir("rapor_app", "UPDATE siparisler SET durum = 'iptal'"), "güncelleyemez")
ok(not yapabilir("rapor_app", "DELETE FROM siparisler"), "silemez")
eq(sorgu("SELECT count(*) FROM information_schema.role_table_grants WHERE grantee IN ('rapor_app', 'PUBLIC') AND table_schema = 'public'")
   + sorgu("SELECT count(*) FROM information_schema.column_privileges WHERE grantee IN ('rapor_app', 'PUBLIC') AND table_schema = 'public'"),
   [(0,), (0,)], "rapor_app'e ve PUBLIC'e doğrudan hiçbir yetki verilmedi")
```

```solution
CREATE ROLE rapor_okur NOLOGIN;
CREATE ROLE rapor_app LOGIN IN ROLE rapor_okur;
GRANT SELECT ON siparisler TO rapor_okur;
GRANT SELECT (id, ad) ON musteriler TO rapor_okur;
```

```hint
Önce grup: `CREATE ROLE rapor_okur NOLOGIN;`. Hesap gruba üye olarak doğar: `CREATE ROLE rapor_app LOGIN IN ROLE rapor_okur;`.
```

```hint
Sütun düzeyi yetki: `GRANT SELECT (id, ad) ON musteriler TO rapor_okur;`. Tablo düzeyinde `SELECT` verirsen bütün sütunlar açılır.
```
:::

::: gorev Sipariş yazan uygulama
Sipariş servisi `siparis_app` adlı bağlanabilen bir hesapla çalışacak. Bu hesap:

- `siparisler`'e yeni satır **ekleyebilmeli**: `id` sütununu servis vermez, `serial` sayacı verir;
- `siparisler`'i **okuyabilmeli**;
- yalnızca `durum` sütununu **güncelleyebilmeli**; `tutar`'a ya da başka bir sütuna dokunamamalı;
- **silememeli**, tabloyu boşaltamamalı (`TRUNCATE`); `musteriler`'i okuyamamalı.

```setup
CREATE TABLE musteriler (id serial PRIMARY KEY, ad text NOT NULL, eposta text, tc_no char(11));
CREATE TABLE siparisler (id serial PRIMARY KEY, musteri_id int NOT NULL REFERENCES musteriler(id),
                         tutar numeric(10,2) NOT NULL, durum text NOT NULL DEFAULT 'yeni');
INSERT INTO musteriler (ad, eposta, tc_no) VALUES ('Ayşe', 'ayse@ornek.test', '10000000146'), ('Can', NULL, NULL);
INSERT INTO siparisler (musteri_id, tutar, durum) VALUES (1, 250.00, 'teslim'), (2, 99.90, 'yeni');
```

```meta
motor: postgres
```

```starter
CREATE ROLE siparis_app LOGIN;
GRANT SELECT, INSERT, UPDATE ON siparisler TO siparis_app;
```

```test
eq(sorgu("SELECT rolcanlogin FROM pg_roles WHERE rolname = 'siparis_app'"), [(True,)], "siparis_app bağlanabilir")
ok(yapabilir("siparis_app", "INSERT INTO siparisler (musteri_id, tutar) VALUES (1, 10.00)"),
   "id'yi sayaç verince ekleme çalışır (sayacın USAGE yetkisi de gerekir)")
ok(yapabilir("siparis_app", "SELECT id, tutar, durum FROM siparisler"), "okur")
ok(yapabilir("siparis_app", "UPDATE siparisler SET durum = 'hazırlanıyor' WHERE id = 2"), "durumu günceller")
ok(not yapabilir("siparis_app", "UPDATE siparisler SET tutar = 0 WHERE id = 2"), "tutarı güncelleyemez")
ok(not yapabilir("siparis_app", "UPDATE siparisler SET durum = 'iptal', musteri_id = 1 WHERE id = 2"),
   "izinli ve izinsiz sütun birlikte: bütün ifade reddedilir")
ok(not yapabilir("siparis_app", "DELETE FROM siparisler WHERE id = 2"), "silemez")
ok(not yapabilir("siparis_app", "TRUNCATE siparisler"), "tabloyu boşaltamaz")
ok(not yapabilir("siparis_app", "SELECT ad FROM musteriler"), "musteriler'i okuyamaz")
eq(sorgu("SELECT has_table_privilege('siparis_app', 'siparisler', 'UPDATE')"), [(False,)],
   "tablo düzeyinde UPDATE yok: yalnızca sütun düzeyinde")
```

```solution
CREATE ROLE siparis_app LOGIN;
GRANT SELECT, INSERT ON siparisler TO siparis_app;
GRANT UPDATE (durum) ON siparisler TO siparis_app;
GRANT USAGE ON SEQUENCE siparisler_id_seq TO siparis_app;
```

```hint
`GRANT UPDATE (durum) ON siparisler TO siparis_app;` yalnızca bir sütunu açar. Tablo düzeyinde `UPDATE` verirsen bütün sütunlar açılır.
```

```hint
`INSERT` yetkisi olduğu hâlde ekleme `permission denied for sequence siparisler_id_seq` hatası veriyorsa: `serial` sütunu varsayılan değerini `nextval('siparisler_id_seq')` ile alır ve bunun için sayaçta `USAGE` gerekir.
```
:::

::: gorev Etkili yetki raporu
Veritabanında roller ve yetkiler hazır. `destek_app` hesabının `public` şemasındaki **her tablo** için **tablo düzeyinde** etkili yetkisini raporla: `tablo`, `okur` (SELECT), `ekler` (INSERT), `gunceller` (UPDATE), `siler` (DELETE); tablo adına göre sıralı. Etkili yetki doğrudan verilenleri, grup üyeliğinden gelenleri ve `PUBLIC`'e verilenleri kapsar. Tablo listesini ve yetkileri elle yazma: katalogdan oku.

```setup
CREATE TABLE musteriler (id serial PRIMARY KEY, ad text NOT NULL, eposta text);
CREATE TABLE siparisler (id serial PRIMARY KEY, musteri_id int NOT NULL, durum text DEFAULT 'yeni');
CREATE TABLE destek_notlari (id serial PRIMARY KEY, siparis_id int, metin text);
CREATE TABLE duyurular (id serial PRIMARY KEY, metin text);
CREATE TABLE denetim_kaydi (id serial PRIMARY KEY, olay text);
CREATE ROLE okuma NOLOGIN;
CREATE ROLE destek_app LOGIN IN ROLE okuma;
GRANT SELECT ON musteriler, siparisler TO okuma;
GRANT INSERT ON destek_notlari TO destek_app;
GRANT SELECT ON duyurular TO PUBLIC;
```

```meta
motor: postgres
```

```starter
SELECT tablename AS tablo, false AS okur, false AS ekler, false AS gunceller, false AS siler
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablo;
```

```test
temel = [("denetim_kaydi", False, False, False, False), ("destek_notlari", False, True, False, False),
         ("duyurular", True, False, False, False), ("musteriler", True, False, False, False),
         ("siparisler", True, False, False, False)]
eq(sonuc, temel, "beş tablo: grup, doğrudan ve PUBLIC yetkileri")
eq(sutunlar, ["tablo", "okur", "ekler", "gunceller", "siler"], "sütunlar: tablo, okur, ekler, gunceller, siler")
eq(dene("GRANT DELETE ON denetim_kaydi TO PUBLIC;")[0], ("denetim_kaydi", False, False, False, True), "PUBLIC'e verilen silme")
eq([r[1] for r in dene("REVOKE okuma FROM destek_app;")], [False, False, True, False, False], "grup üyeliği kalkınca grup yetkileri gider, PUBLIC kalır")
eq(dene("GRANT UPDATE ON siparisler TO okuma;")[-1], ("siparisler", True, False, True, False), "gruba sonradan verilen güncelleme")
eq(dene("GRANT UPDATE (durum) ON siparisler TO destek_app;")[-1], ("siparisler", True, False, False, False),
   "yalnızca sütun düzeyindeki yetki tablo düzeyi raporda görünmez")
eq(len(dene("CREATE TABLE yeni_tablo (x int);")), 6, "yeni tablo rapora kendiliğinden girer")
eq(dene("CREATE SCHEMA arsiv; CREATE TABLE arsiv.eski (x int); GRANT USAGE ON SCHEMA arsiv TO PUBLIC; GRANT SELECT ON arsiv.eski TO PUBLIC;"),
   temel, "public dışındaki şemalar rapora girmez")
eq(dene("CREATE TABLE \"Büyük Ad\" (x int); GRANT SELECT ON \"Büyük Ad\" TO okuma;")[0], ("Büyük Ad", True, False, False, False),
   "tırnak gerektiren tablo adı da doğru okunur")
```

```solution
SELECT tablename AS tablo,
       has_table_privilege('destek_app', format('%I.%I', schemaname, tablename), 'SELECT') AS okur,
       has_table_privilege('destek_app', format('%I.%I', schemaname, tablename), 'INSERT') AS ekler,
       has_table_privilege('destek_app', format('%I.%I', schemaname, tablename), 'UPDATE') AS gunceller,
       has_table_privilege('destek_app', format('%I.%I', schemaname, tablename), 'DELETE') AS siler
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablo;
```

```hint
`has_table_privilege('destek_app', tablo, 'SELECT')` doğrudan, grup (INHERIT) ve PUBLIC yetkilerinin hepsini hesaba katar. Dört yetki için dört kez çağır.
```

```hint
Tablo adını fonksiyona verirken şemayla ve tırnakla ver: `format('%I.%I', schemaname, tablename)`. `%I` gerekirse adı çift tırnağa alır; `"Büyük Ad"` gibi adlar ancak böyle bulunur.
```
:::
