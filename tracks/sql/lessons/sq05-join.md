---
id: sq05
title: JOIN ile Birleştirmek
summary: Tabloları ilişkiden birleştirmek; INNER ve LEFT JOIN, takma adlar, tablonun kendisiyle birleşmesi ve LEFT JOIN'in WHERE tuzağı.
---

::: anlat İlişkiler ve JOIN
Veritabanı bilgiyi tekrar etmemek için tablolara böler. `sunucular` tablosunda sorumlunun adı değil, **kimliği** (`sorumlu_id`) yazar; ad `personel` tablosundadır. İkisini `JOIN` ile birleştirirsin:

```sql
SELECT s.ad, p.ad AS sorumlu
FROM sunucular AS s                       #! s ve p: tablo takma adları
JOIN personel AS p ON p.id = s.sorumlu_id; #! hangi satır hangisiyle eşleşir
```

`JOIN` (tam adıyla `INNER JOIN`) yalnızca **eşleşen** satırları bırakır: sorumlusu olmayan test01 sonuçta yok.

`LEFT JOIN` soldaki tablonun **bütün** satırlarını tutar; eşleşme yoksa sağdaki sütunlar `NULL` olur:

```sql
SELECT s.ad, p.ad AS sorumlu
FROM sunucular AS s
LEFT JOIN personel AS p ON p.id = s.sorumlu_id
ORDER BY s.ad;
```

Bu, "eşi olmayanları bul" kalıbını da verir:

```sql
SELECT s.ad
FROM sunucular AS s
LEFT JOIN personel AS p ON p.id = s.sorumlu_id
WHERE p.id IS NULL;
```

### Tablonun kendisiyle birleşmesi
`personel.yonetici_id` yine `personel` tablosunu gösterir. Aynı tabloyu iki farklı takma adla iki kez kullanırsın:

```sql
SELECT c.ad AS calisan, y.ad AS yonetici
FROM personel AS c
LEFT JOIN personel AS y ON y.id = c.yonetici_id;
```

### Zincirleme birleştirme
```sql
SELECT b.id, s.ad AS sunucu, a.ad AS atanan, e.ad AS ekip
FROM biletler AS b
JOIN sunucular AS s ON s.id = b.sunucu_id
JOIN personel AS a ON a.id = b.atanan_id
JOIN ekipler AS e ON e.id = a.ekip_id
WHERE b.durum = 'açık';
```

> [!TUZAK]
> `LEFT JOIN`'den sonra **sağdaki** tabloya `WHERE` koşulu koymak onu gizlice `INNER JOIN`'e çevirir: eşleşmeyen satırlarda sağ taraf NULL'dır ve `WHERE p.unvan = 'Stajyer'` NULL için doğru olmaz, satır elenir. Sağ tablo üzerindeki koşulu `ON`'a yaz: `LEFT JOIN personel p ON p.id = s.sorumlu_id AND p.unvan = 'Stajyer'`.

> [!TUZAK]
> `ON` koşulunu unutursan (ya da yanlış yazarsan) her satır her satırla eşleşir: 12 sunucu × 10 çalışan = 120 satır. Sonuç beklenenden çok büyükse ilk bakılacak yer burasıdır.
:::

::: tahmin
Üç sorgu, üç sayı:

```sql
SELECT COUNT(*) FROM personel JOIN ekipler ON ekipler.id = personel.ekip_id;
SELECT COUNT(*) FROM personel LEFT JOIN ekipler ON ekipler.id = personel.ekip_id;
SELECT COUNT(*) FROM ekipler LEFT JOIN personel ON personel.ekip_id = ekipler.id;
```

???

`9`, `10`, `10`. Burak'ın ekibi yok (`ekip_id` NULL): INNER JOIN onu atar (9), personelden başlayan LEFT JOIN tutar (10). Üçüncü sorgu ekiplerden başlar. Dört ekibin 9 çalışanı var, hiç çalışanı olmayan Arşiv ekibi de NULL'larla bir satır olarak kalır: yine 10. Aynı sayı, bambaşka sebeple.
:::

::: gorev Sunucu ve sorumlusu
**Bütün** sunucuların adını (`sunucu`) ve sorumlusunun adını (`sorumlu`) getir; sorumlusu olmayan sunucu da listede olsun. Sunucu adına göre sırala.

```starter
SELECT s.ad AS sunucu, p.ad AS sorumlu
FROM sunucular AS s
JOIN personel AS p ON p.id = s.sorumlu_id
ORDER BY s.ad;
```

```test
eq(sutunlar, ["sunucu", "sorumlu"], "sütunlar: sunucu, sorumlu")
eq(len(sonuc), 12, "12 sunucunun hepsi")
ok(("test01", None) in sonuc, "test01 sorumlusuz (NULL) olarak listede", got=sonuc[-3:])
eq(sonuc, sorgu("SELECT s.ad, p.ad FROM sunucular s LEFT JOIN personel p ON p.id = s.sorumlu_id ORDER BY s.ad"), "eşleşmeler ve sıra")
```

```solution
SELECT s.ad AS sunucu, p.ad AS sorumlu
FROM sunucular AS s
LEFT JOIN personel AS p ON p.id = s.sorumlu_id
ORDER BY s.ad;
```

```hint
INNER JOIN eşleşmeyeni atar. Soldaki tablonun hepsini tutmak için `LEFT JOIN`.
```
:::

::: gorev Ekip başına açık bilet
Açık biletleri, **atandıkları kişinin ekibine** göre say: `ekip` ve `adet` sütunları; çoktan aza, eşitlikte ekip adına göre sırala. Kimseye atanmamış biletleri sayma.

```cikti
Ağ|2
Veritabanı|2
Altyapı|1
```

```starter
SELECT atanan_id, COUNT(*)
FROM biletler
WHERE durum = 'açık'
GROUP BY atanan_id;
```

```test
eq(sutunlar, ["ekip", "adet"], "sütunlar: ekip, adet")
eq(sonuc, [("Ağ", 2), ("Veritabanı", 2), ("Altyapı", 1)], "ekiplere göre açık bilet sayıları")
```

```solution
SELECT e.ad AS ekip, COUNT(*) AS adet
FROM biletler AS b
JOIN personel AS p ON p.id = b.atanan_id
JOIN ekipler AS e ON e.id = p.ekip_id
WHERE b.durum = 'açık'
GROUP BY e.ad
ORDER BY adet DESC, ekip;
```

```hint
Bilet → atanan kişi (`personel`) → ekip (`ekipler`): iki JOIN. Sonra `GROUP BY e.ad`.
```
:::

::: gorev Yönetici başına ekip
Her yöneticinin adını (`yonetici`) ve doğrudan bağlı çalışan sayısını (`bagli`) getir; çoktan aza, eşitlikte ada göre sırala.

```starter
SELECT yonetici_id, COUNT(*)
FROM personel
GROUP BY yonetici_id;
```

```test
eq(sutunlar, ["yonetici", "bagli"], "sütunlar: yonetici, bagli")
eq(sonuc, [("Selin", 4), ("Kerem", 2), ("Ayşe", 1), ("Mert", 1), ("Zeynep", 1)], "yöneticiler ve bağlı sayıları")
```

```solution
SELECT y.ad AS yonetici, COUNT(*) AS bagli
FROM personel AS c
JOIN personel AS y ON y.id = c.yonetici_id
GROUP BY y.id
ORDER BY bagli DESC, yonetici;
```

```hint
`personel` tablosunu iki kez kullan: çalışanlar (`c`) ve yöneticileri (`y`), `ON y.id = c.yonetici_id`.
```
:::

::: gorev Düşük öncelikli biletler
Önceliği `düşük` olan biletlerin `id`'sini ve ilgili sunucunun adını (`sunucu`) getir; bir sunucuyla ilgili olmayan bilet de listede olsun. `id`'ye göre sırala.

```starter
SELECT b.id, s.ad AS sunucu
FROM biletler AS b
JOIN sunucular AS s ON s.id = b.sunucu_id
WHERE b.oncelik = 'düşük'
ORDER BY b.id;
```

```test
eq(sonuc, [(6, "cache01"), (10, "izleme01"), (11, "dc01"), (15, "izleme01"), (17, "test01"), (18, None)], "altı düşük öncelikli bilet; 18'in sunucusu yok")
```

```solution
SELECT b.id, s.ad AS sunucu
FROM biletler AS b
LEFT JOIN sunucular AS s ON s.id = b.sunucu_id
WHERE b.oncelik = 'düşük'
ORDER BY b.id;
```

```hint
18 numaralı biletin `sunucu_id`'si NULL; INNER JOIN onu atar. Buradaki WHERE soldaki tabloya (`b`) ait olduğu için LEFT JOIN'i bozmaz.
```
:::
