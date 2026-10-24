---
id: sq20
title: JSON Kayıtlarını Sorgulamak
summary: Bir sütunda JSON olarak saklanan olayları SQL'den okumak: json_extract, -> ve ->> ile iç içe alanlar ve dizi elemanları; olmayan anahtar, JSON null ve SQL NULL farkı, json_type ve json_valid; json_each ile diziyi satırlara açıp tabloyla birleştirmek; PostgreSQL jsonb karşılıkları.
kazanim: 1Z0071 3.2, 1Z0071 4.2, 1Z0071 5.2, 1Z0071 14.2, 1Z0071 15.2
---

::: anlat Bir sütunda bir belge
Uygulamalar ve denetim sistemleri olayları çoğu zaman tek bir metin sütununda JSON olarak saklar: her olayın alanları farklıdır, şema her sürümde değişir. Bu derste `olaylar(id, zaman, kayit)` tablosunun `kayit` sütunu böyle bir belgedir:

```json
{"tur": "giris_hata", "sunucu": "db01",
 "kullanici": {"ad": "ayse"}, "kaynak": {"ip": "203.0.113.7"},
 "etiketler": ["auth", "basarisiz", "dis-ag"], "deneme": 3}
```

SQLite (3.38'den beri çekirdekte) bu metni sorgu içinde okur. Bir alana **yol** ile ulaşılır: `$` belgenin kendisi, `.ad` bir anahtar, `[0]` dizinin ilk elemanı, `[#-1]` son elemanı.

| İfade | Ne döner |
|---|---|
| `json_extract(kayit, '$.kullanici.ad')` | SQL değeri: `'ayse'` |
| `kayit ->> '$.kullanici.ad'` | aynısı, kısa yazım |
| `kayit ->> 'tur'` | `->>` ile tek anahtar yolsuz da yazılır |
| `kayit -> '$.kaynak'` | **JSON metni**: `{"ip":"203.0.113.7"}` |
| `kayit -> 'kullanici' ->> 'ad'` | adım adım inmek |
| `kayit ->> '$.etiketler[#-1]'` | dizinin son elemanı: `'dis-ag'` |

```sql
SELECT '{"kullanici": {"ad": "ayse"}, "etiketler": ["auth", "basarisiz", "dis-ag"]}' ->> '$.kullanici.ad' AS ad,
       '{"kullanici": {"ad": "ayse"}, "etiketler": ["auth", "basarisiz", "dis-ag"]}' ->> '$.etiketler[#-1]' AS son_etiket,
       '{"kaynak": {"ip": "203.0.113.7"}}' -> 'kaynak' AS kaynak_json;
```

Fark şudur: `->>` bir **SQL değeri** verir (metin, tam sayı, ondalık; `true` ise 1), `->` her zaman **JSON metni** verir (metin değerler tırnaklı: `"ayse"`). Karşılaştırma ve hesap için `->>`, bir parçayı JSON olarak taşımak için `->` kullanılır.

JSON'daki türler SQL'e olduğu gibi geçer ve tür eğilimi (affinity) yoktur: `{"deneme": 5}` için `kayit ->> 'deneme' = 5` doğrudur, ama `{"deneme": "5"}` için **yanlıştır**, çünkü metin `'5'` sayı 5'e eşit değildir. Uygulama aynı alanı bazen sayı bazen metin yazıyorsa `CAST(kayit ->> 'deneme' AS INTEGER)` ile tek türe çekersin.
:::

::: anlat Üç çeşit boşluk
Bir alanın "boş" olmasının JSON'da üç ayrı anlamı vardır ve olay incelemesinde üçü farklı şey söyler:

| Durum | Örnek `kayit` | `kayit ->> 'kullanici'` | `kayit -> 'kullanici'` | `json_type(kayit, '$.kullanici')` |
|---|---|---|---|---|
| anahtar hiç yok | `{"tur": "giris"}` | `NULL` | `NULL` | `NULL` |
| anahtar var, değeri JSON `null` | `{"kullanici": null}` | `NULL` | `'null'` | `'null'` |
| kaydın kendisi SQL `NULL` | `NULL` | `NULL` | `NULL` | `NULL` |

`->>` üçünü de aynı `NULL`'a çevirir; ayırmak için `json_type` (ya da `->`) gerekir. `json_type` değerin JSON türünü söyler: `'object'`, `'array'`, `'text'`, `'integer'`, `'real'`, `'true'`, `'false'`, `'null'`; anahtar yoksa SQL `NULL`. Kaydın SQL `NULL` olduğunu ise `kayit IS NULL` söyler.

Dördüncü durum **bozuk** kayıttır: yarım yazılmış, kesilmiş bir satır. JSON fonksiyonları bozuk metinde **hata verir** ve bütün sorgu durur (`malformed JSON`). Tek bir bozuk satır raporu düşürmesin diye önce `json_valid(kayit)` ile denetlenir; `json_valid` geçerli JSON'da 1, bozukta 0, `NULL`'da `NULL` döner:

```sql
SELECT json_valid('{"tur": "giris"}'), json_valid('{"tur": "gir'), json_valid(NULL);
```

Bozuk satırı güvenle atlamanın kesin yolu, JSON'a dokunan ifadeyi `CASE WHEN json_valid(kayit) THEN ... END` içine almaktır: `CASE` koşulu yanlışsa dalı hiç değerlendirmez.

> [!GÜVENLİK]
> Olay incelemesinde "kullanıcı alanı boş" ile "kullanıcı alanı hiç yok" aynı şey değildir: ilki uygulamanın bilerek `null` yazdığı (örneğin sistem işi) bir olaydır, ikincisi farklı bir yazılım sürümünden ya da elle üretilmiş bir kayıttan gelebilir. Bunları tek bir `IS NULL` ile birleştiren bir kural, sahte kayıtları gözden kaçırır.
:::

::: anlat Diziyi satırlara açmak
`etiketler` gibi bir dizi tek bir sütuna sığar ama sayılamaz, süzülemez. `json_each(x)` bir **tablo fonksiyonudur**: dizinin her elemanı için bir satır verir. Sütunları `key` (dizide sıra, nesnede anahtar), `value` (SQL değeri) ve `type`'tır (JSON türü). İkinci argüman bir yol olabilir: `json_each(kayit, '$.etiketler')`.

```sql
SELECT key, value, type
FROM json_each('["auth", "basarisiz", "dis-ag"]');
```

Bir tabloyla yan yana yazıldığında her satır için ayrı açılır; sorgu "olay × etiket" satırları üretir:

```sql
WITH olaylar(id, kayit) AS (VALUES
    (1, '{"etiketler": ["auth", "basarili"]}'),
    (2, '{"etiketler": ["auth", "basarisiz", "kritik"]}'),
    (3, '{"etiketler": []}'))
SELECT e.value AS etiket, COUNT(*) AS olay
FROM olaylar AS o, json_each(o.kayit, '$.etiketler') AS e
GROUP BY e.value
ORDER BY olay DESC, etiket;
```

Boş dizi (`[]`), olmayan yol ya da `NULL` kayıt hiç satır vermez: o olay birleşimden düşer. Tersine, `json_group_array(x)` ve `json_group_object(k, v)` satırları yeniden bir JSON dizisine ya da nesnesine toplar.

JSON alanı sıradan bir sütun gibi birleştirmede de kullanılır: `JOIN sunucular AS s ON s.ad = o.kayit ->> 'sunucu'`.

PostgreSQL'de aynı iş **jsonb** türüyle yapılır. Bu tezgah SQLite'tır; aşağıdakiler PostgreSQL'de karşılıklardır, burada çalışmaz:

| İş | SQLite | PostgreSQL (jsonb) |
|---|---|---|
| SQL değeri olarak alan | `kayit ->> 'tur'` | `kayit ->> 'tur'` |
| iç içe yol | `kayit ->> '$.kullanici.ad'` | `kayit #>> '{kullanici,ad}'` |
| JSON olarak parça | `kayit -> 'kaynak'` | `kayit -> 'kaynak'` |
| anahtar var mı | `json_type(kayit, '$.k') IS NOT NULL` | `kayit ? 'k'` |
| JSON türü | `json_type(kayit, '$.k')` | `jsonb_typeof(kayit -> 'k')` |
| diziyi satırlara açmak | `json_each(kayit, '$.etiketler')` | `jsonb_array_elements_text(kayit -> 'etiketler')` |
| dizide eleman var mı | `EXISTS (SELECT 1 FROM json_each(...) WHERE value = 'kritik')` | `kayit -> 'etiketler' ? 'kritik'` |

PostgreSQL'de de `->>` olmayan anahtarda ve JSON `null`'da aynı SQL `NULL`'ı verir; ayrım `?` ya da `jsonb_typeof` ile yapılır. Bir fark: PostgreSQL bozuk JSON'u `jsonb` sütununa **yazarken** reddeder, SQLite'ta ise JSON yalnızca metindir ve bozukluk okurken ortaya çıkar.
:::

::: tahmin
Tek satır, dört değer. Hangileri?

```sql
SELECT json_type('{"kullanici": null}', '$.kullanici'),
       json_type('{"tur": "giris"}', '$.kullanici'),
       '{"kullanici": null}' ->> 'kullanici' IS NULL,
       '{"deneme": "5"}' ->> 'deneme' = 5;
```

???

`null|NULL|1|0`. Anahtar var ve değeri JSON `null` olduğunda `json_type` metin olarak `'null'` döner; anahtar hiç yoksa SQL `NULL` döner (çıktıda büyük harfle `NULL`). `->>` ise JSON `null`'ı da SQL `NULL`'a çevirir: `IS NULL` doğru, 1. Son karşılaştırma yanlıştır, 0: `"5"` JSON'da metindir, `->>` onu metin `'5'` olarak verir ve tür eğilimi olmadığı için sayı 5'e eşit sayılmaz.
:::

::: gorev Kaba kuvvet adayları
`olaylar` tablosunda her satırın `kayit` sütunu bir JSON olayıdır. Türü (`tur`) `giris_hata` olan ve deneme sayısı (`deneme`) **3 ya da daha fazla** olan olayları getir: `id`, kullanıcı adı (`kullanici.ad`, sütun adı `kullanici`), kaynak IP (`kaynak.ip`, sütun adı `ip`) ve olayın sunucusunun `sunucular` tablosundaki `rol`'ü. `id` sırasıyla.

Uygulamanın eski sürümü `deneme`'yi metin olarak (`"4"`) yazıyor; o da sayı gibi değerlendirilsin. `deneme` alanı olmayan olay listeye girmez. Yalnızca `sunucular` tablosunda kayıtlı sunucuların olayları gelir.

```setup
CREATE TABLE olaylar (id INTEGER PRIMARY KEY, zaman TEXT NOT NULL, kayit TEXT);
INSERT INTO olaylar (id, zaman, kayit) VALUES
    (1, '2026-10-19 08:02', '{"tur": "giris", "sunucu": "web01", "kullanici": {"ad": "kerem", "rol": "admin"}, "kaynak": {"ip": "10.0.0.5", "port": 51544}, "etiketler": ["auth", "basarili"]}'),
    (2, '2026-10-19 08:10', '{"tur": "giris_hata", "sunucu": "db01", "kullanici": {"ad": "ayse"}, "kaynak": {"ip": "203.0.113.7"}, "etiketler": ["auth", "basarisiz", "dis-ag"], "deneme": 3}'),
    (3, '2026-10-19 08:11', '{"tur": "giris_hata", "sunucu": "db01", "kullanici": {"ad": "root"}, "kaynak": {"ip": "203.0.113.7"}, "etiketler": ["auth", "basarisiz", "dis-ag", "kritik"], "deneme": 5}'),
    (4, '2026-10-19 09:00', '{"tur": "yedek", "sunucu": "yedek01", "kullanici": null, "etiketler": []}'),
    (5, '2026-10-19 09:30', '{"tur": "yapilandirma", "sunucu": "dc01", "kullanici": {"ad": "selin", "rol": "admin"}, "degisiklik": {"anahtar": "PasswordPolicy", "eski": 12, "yeni": 8}, "etiketler": ["kritik", "politika"]}'),
    (6, '2026-10-19 10:05', '{"tur": "giris", "sunucu": "vpn01", "kaynak": {"ip": "198.51.100.20"}, "etiketler": ["auth", "basarili", "dis-ag"]}'),
    (7, '2026-10-19 10:20', NULL),
    (8, '2026-10-19 11:40', '{"tur": "giris_hata", "sunucu": "web01", "kullanici": {"ad": "kerem"}, "kaynak": {"ip": "10.0.0.5"}, "etiketler": ["auth", "basarisiz"], "deneme": 2}'),
    (9, '2026-10-19 12:15', '{"tur": "giris_hata", "sunucu": "vpn01", "kullanici": {"ad": "admin"}, "kaynak": {"ip": "198.51.100.20"}, "etiketler": ["auth", "basarisiz", "dis-ag"], "deneme": "4"}');
```

```starter
SELECT id, kayit
FROM olaylar
ORDER BY id;
```

```test
def olay(id_, json):
    return "INSERT INTO olaylar (id, zaman, kayit) VALUES (" + str(id_) + ", '2026-10-20 00:00', '" + json + "');"

eq(sonuc, [(2, "ayse", "203.0.113.7", "veritabanı"), (3, "root", "203.0.113.7", "veritabanı"),
           (9, "admin", "198.51.100.20", "ağ geçidi")], "üç aday: 2, 3 ve metin denemeli 9")
eq(sutunlar, ["id", "kullanici", "ip", "rol"], "sütunlar: id, kullanici, ip, rol")
ok(all(r[0] != 8 for r in sonuc), "deneme 2 (eşiğin altı) listede yok")
eq([r[0] for r in dene(olay(20, '{"tur": "giris_hata", "sunucu": "web02", "kullanici": {"ad": "can"}, "kaynak": {"ip": "10.0.0.9"}, "deneme": 3}'))],
   [2, 3, 9, 20], "eşiğe eşit (3) dahil")
eq([r[0] for r in dene(olay(20, '{"tur": "giris_hata", "sunucu": "web02", "kullanici": {"ad": "can"}, "kaynak": {"ip": "10.0.0.9"}, "deneme": "3"}'))],
   [2, 3, 9, 20], "metin olarak \"3\" de eşiğe eşittir")
eq([r[0] for r in dene(olay(20, '{"tur": "giris_hata", "sunucu": "web02", "kullanici": {"ad": "can"}, "kaynak": {"ip": "10.0.0.9"}, "deneme": "2"}'))],
   [2, 3, 9], "metin olarak \"2\" eşiğin altında")
eq([r[0] for r in dene(olay(20, '{"tur": "giris_hata", "sunucu": "web02", "kullanici": {"ad": "can"}, "kaynak": {"ip": "10.0.0.9"}}'))],
   [2, 3, 9], "deneme alanı olmayan olay girmez")
eq([r[0] for r in dene(olay(20, '{"tur": "giris_hata", "sunucu": "mail01", "kullanici": {"ad": "can"}, "kaynak": {"ip": "10.0.0.9"}, "deneme": 7}'))],
   [2, 3, 9], "kayıtlı olmayan sunucunun olayı girmez")
eq(dene(olay(20, '{"tur": "giris_hata", "sunucu": "web02", "deneme": 6}'))[-1], (20, None, None, "web"),
   "kullanıcı ve kaynak yoksa o sütunlar NULL kalır, olay yine listelenir")
eq([r[0] for r in dene(olay(20, '{"tur": "giris", "sunucu": "web02", "deneme": 9}'))], [2, 3, 9], "giris_hata olmayan tür girmez")
```

```solution
SELECT o.id,
       o.kayit ->> '$.kullanici.ad' AS kullanici,
       o.kayit ->> '$.kaynak.ip'    AS ip,
       s.rol
FROM olaylar AS o
JOIN sunucular AS s ON s.ad = o.kayit ->> 'sunucu'
WHERE o.kayit ->> 'tur' = 'giris_hata'
  AND CAST(o.kayit ->> 'deneme' AS INTEGER) >= 3
ORDER BY o.id;
```

```hint
İç içe alan: `kayit ->> '$.kullanici.ad'`. Sunucuyla birleştirme: `JOIN sunucular AS s ON s.ad = o.kayit ->> 'sunucu'`.
```

```hint
`kayit ->> 'deneme' >= 3` metin olarak yazılmış her denemeyi, `"2"`'yi bile, geçirir: SQLite'ta metin her sayıdan büyük sayılır. `CAST(kayit ->> 'deneme' AS INTEGER)` ikisini aynı türe çeker; alan yoksa `NULL` kalır ve koşul geçmez.
```
:::

::: gorev Etiketlerin dağılımı
Her etiketin **kaç farklı olayda** geçtiğini say: `etiket` ve `olay`, olay sayısı büyükten küçüğe, eşitlikte etiket adına göre. Etiket dizisi boş olan, `etiketler` alanı olmayan ya da kaydı `NULL` olan olaylar hiçbir etikete sayılmaz. Bir olay aynı etiketi iki kez yazmışsa o olay bir kez sayılır.

```setup
CREATE TABLE olaylar (id INTEGER PRIMARY KEY, zaman TEXT NOT NULL, kayit TEXT);
INSERT INTO olaylar (id, zaman, kayit) VALUES
    (1, '2026-10-19 08:02', '{"tur": "giris", "sunucu": "web01", "kullanici": {"ad": "kerem", "rol": "admin"}, "kaynak": {"ip": "10.0.0.5", "port": 51544}, "etiketler": ["auth", "basarili"]}'),
    (2, '2026-10-19 08:10', '{"tur": "giris_hata", "sunucu": "db01", "kullanici": {"ad": "ayse"}, "kaynak": {"ip": "203.0.113.7"}, "etiketler": ["auth", "basarisiz", "dis-ag"], "deneme": 3}'),
    (3, '2026-10-19 08:11', '{"tur": "giris_hata", "sunucu": "db01", "kullanici": {"ad": "root"}, "kaynak": {"ip": "203.0.113.7"}, "etiketler": ["auth", "basarisiz", "dis-ag", "kritik"], "deneme": 5}'),
    (4, '2026-10-19 09:00', '{"tur": "yedek", "sunucu": "yedek01", "kullanici": null, "etiketler": []}'),
    (5, '2026-10-19 09:30', '{"tur": "yapilandirma", "sunucu": "dc01", "kullanici": {"ad": "selin", "rol": "admin"}, "degisiklik": {"anahtar": "PasswordPolicy", "eski": 12, "yeni": 8}, "etiketler": ["kritik", "politika"]}'),
    (6, '2026-10-19 10:05', '{"tur": "giris", "sunucu": "vpn01", "kaynak": {"ip": "198.51.100.20"}, "etiketler": ["auth", "basarili", "dis-ag"]}'),
    (7, '2026-10-19 10:20', NULL),
    (8, '2026-10-19 11:40', '{"tur": "giris_hata", "sunucu": "web01", "kullanici": {"ad": "kerem"}, "kaynak": {"ip": "10.0.0.5"}, "etiketler": ["auth", "basarisiz"], "deneme": 2}'),
    (9, '2026-10-19 12:15', '{"tur": "giris_hata", "sunucu": "vpn01", "kullanici": {"ad": "admin"}, "kaynak": {"ip": "198.51.100.20"}, "etiketler": ["auth", "basarisiz", "dis-ag"], "deneme": "4"}');
```

```starter
SELECT kayit ->> '$.etiketler' AS etiket, COUNT(*) AS olay
FROM olaylar
GROUP BY etiket
ORDER BY olay DESC, etiket;
```

```test
def olay(id_, json):
    return "INSERT INTO olaylar (id, zaman, kayit) VALUES (" + str(id_) + ", '2026-10-20 00:00', '" + json + "');"

temel = [("auth", 6), ("basarisiz", 4), ("dis-ag", 4), ("basarili", 2), ("kritik", 2), ("politika", 1)]
eq(sonuc, temel, "altı etiket ve olay sayıları")
eq(sutunlar, ["etiket", "olay"], "sütunlar: etiket, olay")
eq(dene(olay(20, '{"tur": "giris", "etiketler": ["kritik", "kritik", "kritik"]}')),
   [("auth", 6), ("basarisiz", 4), ("dis-ag", 4), ("kritik", 3), ("basarili", 2), ("politika", 1)],
   "aynı olayda üç kez yazılan etiket bir olay sayılır")
eq(dene(olay(20, '{"tur": "giris", "etiketler": []}')), temel, "boş dizi hiçbir etikete sayılmaz")
eq(dene(olay(20, '{"tur": "giris"}')), temel, "etiketler alanı olmayan olay sayılmaz")
eq(dene("INSERT INTO olaylar (id, zaman, kayit) VALUES (20, '2026-10-20 00:00', NULL);"), temel, "NULL kayıt sayılmaz")
eq(dene(olay(20, '{"etiketler": ["yeni"]}'))[-1], ("yeni", 1), "tek olaylı yeni etiket, adına göre sonda")
```

```solution
SELECT e.value AS etiket, COUNT(DISTINCT o.id) AS olay
FROM olaylar AS o, json_each(o.kayit, '$.etiketler') AS e
GROUP BY e.value
ORDER BY olay DESC, etiket;
```

```hint
`FROM olaylar AS o, json_each(o.kayit, '$.etiketler') AS e` her olayı etiketleri kadar satıra açar. Etiket `e.value`'dur.
```

```hint
Aynı olaydaki tekrarlı etiketi bir kez saymak için `COUNT(DISTINCT o.id)`.
```
:::

::: gorev Kullanıcı alanının durumu
Her olay için `kullanici` alanının durumunu raporla: `id` ve `durum`, `id` sırasıyla. Durum şu beş değerden biridir:

| `durum` | Ne zaman |
|---|---|
| `kayit yok` | `kayit` sütunu SQL `NULL` |
| `bozuk` | `kayit` geçerli bir JSON değil |
| `alan yok` | belgede `kullanici` anahtarı hiç yok |
| `json null` | `kullanici` var, değeri JSON `null` |
| `var` | `kullanici` başka herhangi bir değer taşıyor |

Bu tabloda bozuk bir satır var: sorgun onunla karşılaşınca durmamalı.

```setup
CREATE TABLE olaylar (id INTEGER PRIMARY KEY, zaman TEXT NOT NULL, kayit TEXT);
INSERT INTO olaylar (id, zaman, kayit) VALUES
    (1, '2026-10-19 08:02', '{"tur": "giris", "sunucu": "web01", "kullanici": {"ad": "kerem", "rol": "admin"}, "kaynak": {"ip": "10.0.0.5", "port": 51544}, "etiketler": ["auth", "basarili"]}'),
    (2, '2026-10-19 08:10', '{"tur": "giris_hata", "sunucu": "db01", "kullanici": {"ad": "ayse"}, "kaynak": {"ip": "203.0.113.7"}, "etiketler": ["auth", "basarisiz", "dis-ag"], "deneme": 3}'),
    (4, '2026-10-19 09:00', '{"tur": "yedek", "sunucu": "yedek01", "kullanici": null, "etiketler": []}'),
    (6, '2026-10-19 10:05', '{"tur": "giris", "sunucu": "vpn01", "kaynak": {"ip": "198.51.100.20"}, "etiketler": ["auth", "basarili", "dis-ag"]}'),
    (7, '2026-10-19 10:20', NULL),
    (10, '2026-10-19 13:00', '{"tur": "giris", "sunucu": "web02", "kullanici": {"ad": "de');
```

```starter
SELECT id,
       CASE WHEN kayit ->> 'kullanici' IS NULL THEN 'alan yok' ELSE 'var' END AS durum
FROM olaylar
ORDER BY id;
```

```test
def olay(id_, json):
    return "INSERT INTO olaylar (id, zaman, kayit) VALUES (" + str(id_) + ", '2026-10-20 00:00', '" + json + "');"

eq(sonuc, [(1, "var"), (2, "var"), (4, "json null"), (6, "alan yok"), (7, "kayit yok"), (10, "bozuk")],
   "altı olayın beş durumu")
eq(sutunlar, ["id", "durum"], "sütunlar: id, durum")
eq(dene(olay(20, '{"kullanici": "sistem"}'))[-1], (20, "var"), "metin değer de 'var'")
eq(dene(olay(20, '{"kullanici": false}'))[-1], (20, "var"), "false bir değerdir: 'var'")
eq(dene(olay(20, '{"kullanici": ""}'))[-1], (20, "var"), "boş metin de bir değerdir: 'var'")
eq(dene(olay(20, '{"kaynak": {"kullanici": "x"}}'))[-1], (20, "alan yok"), "iç içe başka nesnedeki kullanici sayılmaz")
eq(dene(olay(20, ''))[-1], (20, "bozuk"), "boş metin geçerli JSON değil: 'bozuk'")
eq(dene(olay(20, '[1, 2]'))[-1], (20, "alan yok"), "dizi geçerli JSON ama kullanici anahtarı yok")
```

```solution
SELECT id,
       CASE
         WHEN kayit IS NULL                           THEN 'kayit yok'
         WHEN NOT json_valid(kayit)                   THEN 'bozuk'
         WHEN json_type(kayit, '$.kullanici') IS NULL THEN 'alan yok'
         WHEN json_type(kayit, '$.kullanici') = 'null' THEN 'json null'
         ELSE 'var'
       END AS durum
FROM olaylar
ORDER BY id;
```

```hint
Sıra önemlidir: önce `kayit IS NULL`, sonra `NOT json_valid(kayit)`. JSON'a dokunan ifade ancak bu iki koşul elendikten sonra, aynı `CASE`'in sonraki dallarında çalışır.
```

```hint
`json_type(kayit, '$.kullanici')` anahtar yoksa SQL `NULL`, değer JSON `null` ise `'null'` metni döner. `->>` bu ikisini ayıramaz.
```
:::
