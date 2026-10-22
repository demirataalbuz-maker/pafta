---
id: sq02
title: WHERE ile Süzmek
summary: Karşılaştırmalar, AND/OR önceliği, IN, BETWEEN, LIKE, IS NULL ve tarihlerin metin olarak karşılaştırılması.
kazanim: 1Z0071 3.2
---

::: anlat Koşul yazmak
`WHERE` yalnızca koşulu **doğru** olan satırları bırakır:

```sql
SELECT ad, cpu FROM sunucular WHERE cpu > 70;
```

| İşleç | Anlamı |
|---|---|
| `=`, `<>` (ya da `!=`) | eşit, eşit değil |
| `<`, `<=`, `>`, `>=` | büyüklük |
| `AND`, `OR`, `NOT` | koşulları birleştir |
| `IN (a, b, c)` | listedekilerden biri |
| `BETWEEN a AND b` | a ile b arasında (**iki uç dahil**) |
| `LIKE 'kalıp'` | `%` = herhangi sayıda karakter, `_` = tek karakter |
| `IS NULL`, `IS NOT NULL` | değer yok / var |

Metinler **tek tırnakla** yazılır: `'Ankara'`. Çift tırnak sütun adları içindir.

```sql
SELECT ad, sehir FROM sunucular WHERE sehir = 'Ankara' AND rol = 'web';
SELECT ad, rol FROM sunucular WHERE rol IN ('web', 'veritabanı');
SELECT ad, devreye FROM sunucular WHERE devreye BETWEEN '2023-01-01' AND '2024-12-31';
SELECT id, baslik FROM biletler WHERE baslik LIKE '%disk%';
SELECT ad FROM sunucular WHERE sehir IS NULL;
```

> [!DERİN]
> Tarihler bu veritabanında `'YYYY-AA-GG'` biçiminde **metin** olarak durur. Bu biçimin güzelliği, metin olarak karşılaştırıldığında kronolojik sırayla aynı sonucu vermesidir: `'2024-02-01' < '2024-11-30'`. `'01.02.2024'` gibi gün önde biçimlerde bu bozulur; tarihleri her zaman ISO biçiminde sakla.

> [!TUZAK]
> **AND, OR'dan önce gelir.** `rol = 'web' OR rol = 'veritabanı' AND cpu > 80` aslında `rol = 'web' OR (rol = 'veritabanı' AND cpu > 80)` demektir. Niyetin farklıysa parantez kullan; ikisi karışınca her zaman parantez kullan.

> [!TUZAK]
> SQLite'ta `LIKE` büyük-küçük harfe yalnızca **İngilizce harflerde** duyarsızdır: `'Disk' LIKE 'disk'` doğru, ama `'İzmir' LIKE 'i%'` yanlıştır. Türkçe metinlerde `İ/i`, `I/ı` ayrımına dikkat et.
:::

::: tahmin
Hangi sunucuların adları, hangi sırayla gelir?

```sql
SELECT ad FROM sunucular
WHERE rol = 'web' OR rol = 'veritabanı' AND cpu > 80;
```

???

`web01`, `web02`, `web03`, `db01`. `AND` önce bağlandığı için koşul "web olanlar **ya da** (veritabanı olup CPU'su 80'i aşanlar)" oldu: üç web sunucusunun hepsi geldi, veritabanlarından yalnızca db01 (91). Niyet "web ya da veritabanı olup CPU'su 80'i aşanlar" ise `(rol = 'web' OR rol = 'veritabanı') AND cpu > 80` yazılmalı; o zaman yalnızca db01 gelir.
:::

::: gorev Acil açık biletler
Durumu `açık` olan ve önceliği `yüksek` ya da `kritik` olan biletlerin `id` ve `baslik` sütunlarını getir.

```starter
SELECT id, baslik
FROM biletler
WHERE durum = 'açık';
```

```test
eq(sutunlar, ["id", "baslik"], "sütunlar: id, baslik")
eq(sorted(r[0] for r in sonuc), [5, 9, 20], "açık ve yüksek/kritik biletler: 5, 9, 20")
```

```solution
SELECT id, baslik
FROM biletler
WHERE durum = 'açık'
  AND oncelik IN ('yüksek', 'kritik');
```

```hint
İki koşulu `AND` ile bağla; öncelik için `IN ('yüksek', 'kritik')`.
```
:::

::: gorev Yeni ve sakin
2024'te ya da daha sonra devreye alınmış (`devreye`) **ve** CPU'su 50'nin altında olan sunucuların adlarını getir.

```starter
SELECT ad
FROM sunucular
WHERE cpu < 50;
```

```test
eq(sorted(r[0] for r in sonuc), ["db02", "test01", "vpn01"], "db02, test01, vpn01")
```

```solution
SELECT ad
FROM sunucular
WHERE devreye >= '2024-01-01'
  AND cpu < 50;
```

```hint
Tarihler ISO biçiminde metin; `devreye >= '2024-01-01'` doğru karşılaştırır.
```
:::

::: gorev Disk biletleri
Başlığında "disk" kelimesi geçen biletlerin `id` ve `durum` sütunlarını getir. Başlıklarda kelime büyük harfle başlıyor olabilir.

```starter
SELECT id, durum
FROM biletler
WHERE baslik = 'disk';
```

```test
eq(sorted(sonuc), [(1, "çözüldü"), (13, "çözüldü"), (20, "açık")], "1, 13 ve 20 numaralı biletler")
ok(kullanir("like"), "LIKE kullan")
```

```solution
SELECT id, durum
FROM biletler
WHERE baslik LIKE '%disk%';
```

```hint
`=` tam eşitlik ister. Metnin içinde aramak için `LIKE '%disk%'`.
```
:::

::: gorev Buluttakiler
Şehir bilgisi olmayan (bulutta çalışan) sunucuların adlarını getir.

```starter
SELECT ad
FROM sunucular
WHERE sehir = NULL;
```

```test
eq(sorted(r[0] for r in sonuc), ["cache01", "izleme01", "test01"], "cache01, izleme01, test01")
```

```solution
SELECT ad
FROM sunucular
WHERE sehir IS NULL;
```

```hint
`NULL` bir değer değil, "bilinmiyor" demektir; `= NULL` hiçbir zaman doğru olmaz. `IS NULL` kullan.
```
:::
