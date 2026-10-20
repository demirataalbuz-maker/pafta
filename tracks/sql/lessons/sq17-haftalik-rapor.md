---
id: sq17
title: Proje · Haftalık Operasyon Raporu
summary: Öğrendiklerini birleştirerek bir haftanın bilet raporunu çıkarmak; yarı açık tarih aralıkları, koşullu sayım, LEFT JOIN ile eksiksiz liste ve RANK.
---

::: anlat Proje tanımı
BT müdürü Selin her pazartesi geçen haftanın raporunu istiyor. Rapor haftası **12–18 Ekim 2026** (pazartesi–pazar). Raporun üç bölümü var; her görev bir bölüm:

1. **Haftanın özeti**: açılan, çözülen ve hafta sonunda açık kalan bilet sayısı
2. **Ekip yükü**: her ekibin şu anki açık biletleri ve hafta içinde çözdükleri, hiç işi olmayan ekip dahil
3. **Sıcak noktalar**: hafta içinde en çok bilet açılan sunucular, sıra numarasıyla

### Tarih aralığı: yarı açık yaz
"Hafta içinde" koşulunu `BETWEEN '2026-10-12' AND '2026-10-18'` diye yazmak bir tuzaktır: zamanlar `'2026-10-18 22:00'` gibi saat de içerir ve `'2026-10-18 22:00' > '2026-10-18'` olduğu için pazar akşamı açılan bilet dışarıda kalır. Doğrusu **yarı açık aralıktır**: başlangıç dahil, bitiş hariç.

```sql
SELECT COUNT(*) FROM biletler WHERE acilis BETWEEN '2026-10-12' AND '2026-10-18';     #! 17: pazar kaçtı
SELECT COUNT(*) FROM biletler WHERE acilis >= '2026-10-12' AND acilis < '2026-10-19'; #! 19: doğru
```

### Koşullu sayım
Tek sorguda birden çok sayım için `COUNT(*) FILTER (WHERE ...)` ya da her veritabanında çalışan `SUM(CASE WHEN ... THEN 1 ELSE 0 END)`:

```sql
SELECT COUNT(*) FILTER (WHERE oncelik = 'kritik')            AS kritik,
       SUM(CASE WHEN oncelik = 'yüksek' THEN 1 ELSE 0 END)   AS yuksek,
       COUNT(*)                                              AS toplam
FROM biletler;
```

> [!İPUCU]
> Okunabilir SQL için: her yan tümce (`SELECT`, `FROM`, `WHERE`...) kendi satırında, uzun sorgular `WITH` adımlarıyla, tablolar kısa ama anlamlı takma adlarla. Altı ay sonra raporu güncelleyecek kişi büyük ihtimalle sensin.
:::

::: gorev 1 · Haftanın özeti
Tek satırda üç sütun getir:

- `acilan`: hafta içinde **açılan** bilet sayısı
- `cozulen`: hafta içinde **kapanan** bilet sayısı (açılış tarihi ne olursa olsun)
- `acik_kalan`: hafta içinde açılmış olup hafta bittiğinde hâlâ kapanmamış olanlar (hiç kapanmamış ya da hafta bittikten sonra kapanmış)

```cikti
19|10|9
```

```starter
SELECT COUNT(*) AS acilan
FROM biletler;
```

```test
eq(sutunlar, ["acilan", "cozulen", "acik_kalan"], "sütunlar: acilan, cozulen, acik_kalan")
eq(sonuc, [(19, 10, 9)], "19 açılan, 10 çözülen, 9 açık kalan")
eq(dene("DELETE FROM biletler WHERE id IN (1, 19);"), [(17, 9, 8)], "veri değişince de doğru saymalı (sabit sayı yazma)")
```

```solution
SELECT
    COUNT(*) FILTER (WHERE acilis >= '2026-10-12' AND acilis < '2026-10-19') AS acilan,
    COUNT(*) FILTER (WHERE kapanis >= '2026-10-12' AND kapanis < '2026-10-19') AS cozulen,
    COUNT(*) FILTER (WHERE acilis >= '2026-10-12' AND acilis < '2026-10-19'
                       AND (kapanis IS NULL OR kapanis >= '2026-10-19')) AS acik_kalan
FROM biletler;
```

```hint
Üç sayımı tek sorguda: `COUNT(*) FILTER (WHERE ...)` ya da `SUM(CASE WHEN ... THEN 1 ELSE 0 END)`.
```

```hint
19 numaralı bilet pazar 22:00'de açıldı, pazartesi 01:30'da kapandı: hafta içinde açıldı ama hafta bittiğinde açıktı. Yarı açık aralık kullan: `>= '2026-10-12' AND < '2026-10-19'`.
```
:::

::: gorev 2 · Ekip yükü
**Bütün** ekipler için (işi olmayan dahil) şu sütunları getir; biletler atandıkları kişinin ekibine sayılır:

- `ekip`: ekip adı
- `acik`: ekibe atanmış ve şu anda açık olan bilet sayısı
- `cozulen_hafta`: ekibin hafta içinde kapattığı bilet sayısı

`cozulen_hafta`'ya göre çoktan aza, eşitlikte ekip adına göre sırala.

```cikti
Altyapı|1|7
Ağ|2|1
Uygulama|0|1
Veritabanı|2|1
Arşiv|0|0
```

```starter
SELECT e.ad AS ekip
FROM ekipler AS e;
```

```test
eq(sutunlar, ["ekip", "acik", "cozulen_hafta"], "sütunlar: ekip, acik, cozulen_hafta")
eq(sonuc, [("Altyapı", 1, 7), ("Ağ", 2, 1), ("Uygulama", 0, 1), ("Veritabanı", 2, 1), ("Arşiv", 0, 0)], "beş ekibin hepsi, doğru sayılarla")
```

```solution
SELECT e.ad AS ekip,
       SUM(CASE WHEN b.durum = 'açık' THEN 1 ELSE 0 END) AS acik,
       SUM(CASE WHEN b.kapanis >= '2026-10-12' AND b.kapanis < '2026-10-19' THEN 1 ELSE 0 END) AS cozulen_hafta
FROM ekipler AS e
LEFT JOIN personel AS p ON p.ekip_id = e.id
LEFT JOIN biletler AS b ON b.atanan_id = p.id
GROUP BY e.id
ORDER BY cozulen_hafta DESC, ekip;
```

```hint
Ekiplerden başla ve `LEFT JOIN` ile personele, oradan biletlere in: böylece çalışanı ya da bileti olmayan ekip de kalır.
```

```hint
Hiç bileti olmayan ekipte `b.durum` NULL'dur; `COUNT(*)` o satırı 1 sayar. `SUM(CASE WHEN ... THEN 1 ELSE 0 END)` ise 0 verir.
```
:::

::: gorev 3 · Sıcak noktalar
Hafta içinde açılan biletleri sunucuya göre say ve sunuculara bilet sayısına göre `RANK` ver (en çok bilet 1; eşitler aynı sırayı alır). Sırası **2 ya da daha iyi** olan sunucuları `sira`, `ad`, `bilet` sütunlarıyla, önce sıraya sonra ada göre sıralı getir. Bir sunucuyla ilgili olmayan biletleri sayma.

```cikti
1|db01|3
2|dc01|2
2|izleme01|2
2|web01|2
2|web02|2
```

```starter
SELECT s.ad, COUNT(*) AS bilet
FROM biletler AS b
JOIN sunucular AS s ON s.id = b.sunucu_id
GROUP BY s.ad
ORDER BY bilet DESC
LIMIT 3;
```

```test
eq(sutunlar, ["sira", "ad", "bilet"], "sütunlar: sira, ad, bilet")
eq(sonuc, [(1, "db01", 3), (2, "dc01", 2), (2, "izleme01", 2), (2, "web01", 2), (2, "web02", 2)], "sıcak noktalar")
ok(kullanir("rank"), "RANK kullan")
```

```solution
WITH haftalik AS (
    SELECT s.ad, COUNT(*) AS bilet
    FROM biletler AS b
    JOIN sunucular AS s ON s.id = b.sunucu_id
    WHERE b.acilis >= '2026-10-12' AND b.acilis < '2026-10-19'
    GROUP BY s.id
),
sirali AS (
    SELECT RANK() OVER (ORDER BY bilet DESC) AS sira, ad, bilet
    FROM haftalik
)
SELECT sira, ad, bilet
FROM sirali
WHERE sira <= 2
ORDER BY sira, ad;
```

```hint
Üç adım: hafta içi sayım (`GROUP BY`), sıralama (`RANK() OVER (ORDER BY bilet DESC)`), süzme (`WHERE sira <= 2`). Pencere fonksiyonu WHERE'de kullanılamadığı için sıralamayı bir CTE'de yap.
```
:::
