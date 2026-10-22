---
id: sq12
title: Pencere Çerçeveleri ve Dağılım Fonksiyonları
summary: ROWS ve RANGE çerçeveleri, ORDER BY'lı pencerenin gizli varsayılan çerçevesi, kayan ortalama, FIRST_VALUE ve LAST_VALUE tuzağı, NTILE, PERCENT_RANK, CUME_DIST ve adlandırılmış WINDOW.
kazanim: 1Z0071 14.3
---

::: anlat Pencerenin çerçevesi
SQ11'de pencere fonksiyonlarıyla tanıştın. Her pencere fonksiyonu, o satır için hesaba katılacak satırları belirleyen bir **çerçeveye** bakar:

```sql
SELECT sunucu_id, zaman, cpu,
       round(AVG(cpu) OVER (PARTITION BY sunucu_id ORDER BY zaman
                            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 1) AS kayan3,   -- bu satır ve önceki iki
       SUM(cpu) OVER (PARTITION BY sunucu_id ORDER BY zaman
                      ROWS UNBOUNDED PRECEDING) AS kumulatif                          -- baştan bu satıra
FROM olcumler
WHERE sunucu_id = 4
ORDER BY zaman;
```

| Çerçeve | Anlamı |
|---|---|
| `ROWS BETWEEN 2 PRECEDING AND CURRENT ROW` | bu satır ve fiziksel olarak önceki 2 satır |
| `ROWS UNBOUNDED PRECEDING` | bölümün başından bu satıra |
| `ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING` | bu satırdan bölümün sonuna |
| `RANGE BETWEEN ...` | satır sayısına değil **sıralama değerine** göre; eşit değerli satırlar birlikte girer |

> [!TUZAK]
> `ORDER BY` içeren bir pencerede çerçeve yazmazsan varsayılan `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`'dur: **eşit sıralama değerine sahip bütün satırlar** "şimdiki satır" sayılır. Bu yüzden kümülatif toplam, eşit değerli satırlarda aynı (beklenenden büyük) sonucu verir. İkinci tuzak `LAST_VALUE`'dur: varsayılan çerçeve şimdiki satırda bittiği için `LAST_VALUE(x)` çoğu zaman satırın **kendi** değerini döndürür. Bölümün gerçek son değeri için çerçeveyi sona kadar uzat: `ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING`.

### Dağılım fonksiyonları
| Fonksiyon | Ne verir |
|---|---|
| `NTILE(4) OVER (ORDER BY x)` | satırları 4 eşit dilime böler: 1, 2, 3, 4 |
| `PERCENT_RANK()` | (sıra − 1) / (satır sayısı − 1): 0 ile 1 arası |
| `CUME_DIST()` | bu değere kadar (dahil) olan satırların oranı |
| `FIRST_VALUE(x)`, `LAST_VALUE(x)`, `NTH_VALUE(x, n)` | çerçevenin ilk / son / n. değeri |

Aynı pencere birden çok kez kullanılacaksa `WINDOW` ile adlandırılır:

```sql
SELECT ad, cpu,
       NTILE(4) OVER w AS ceyrek,
       round(PERCENT_RANK() OVER w, 2) AS yuzdelik
FROM sunucular
WINDOW w AS (ORDER BY cpu DESC)
ORDER BY cpu DESC
LIMIT 5;
```
:::

::: tahmin
Dört satır, üç sütun:

```sql
WITH t(x) AS (VALUES (1), (2), (2), (3))
SELECT x,
       SUM(x) OVER (ORDER BY x) AS a,
       SUM(x) OVER (ORDER BY x ROWS UNBOUNDED PRECEDING) AS b
FROM t;
```

???

`1|1|1`, `2|5|3`, `2|5|5`, `3|8|8`. `a` varsayılan RANGE çerçevesini kullanır: iki "2" satırı eşit sıralama değerine sahip olduğu için ikisi de birbirini kapsar ve ikisinde de toplam 1 + 2 + 2 = 5'tir. `b` satır satır ilerler: 1, 3, 5, 8.
:::

::: gorev Kayan ortalama
`olcumler` tablosunda her sunucu için, her ölçümde **o ölçüm ve önceki iki ölçümün** CPU ortalamasını bir ondalığa yuvarlayarak getir: `sunucu_id`, `zaman`, `ort`; sunucuya sonra zamana göre sıralı.

```starter
SELECT sunucu_id, zaman, cpu AS ort
FROM olcumler
ORDER BY sunucu_id, zaman;
```

```test
eq(sutunlar, ["sunucu_id", "zaman", "ort"], "sütunlar")
eq([r[2] for r in sonuc], [40.0, 49.0, 56.7, 66.3, 62.0, 68.5, 76.0, 84.7, 70.0, 70.5, 75.0, 81.7], "kayan ortalamalar")
eq([r[0] for r in sonuc], [1] * 4 + [4] * 4 + [8] * 4, "sunucu sırası")
```

```solution
SELECT sunucu_id, zaman,
       round(AVG(cpu) OVER (PARTITION BY sunucu_id ORDER BY zaman
                            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 1) AS ort
FROM olcumler
ORDER BY sunucu_id, zaman;
```

```hint
Çerçeve: `ROWS BETWEEN 2 PRECEDING AND CURRENT ROW`; her sunucu ayrı: `PARTITION BY sunucu_id ORDER BY zaman`.
```
:::

::: gorev En üst çeyrek
Sunucuları CPU'ya göre (büyükten küçüğe) **dört dilime** böl ve **ilk dilimdeki** sunucuların `ad` ve `cpu` değerlerini CPU'ya göre azalan getir.

```starter
SELECT ad, cpu
FROM sunucular
ORDER BY cpu DESC
LIMIT 4;
```

```test
eq(sonuc, [("db01", 91), ("cache01", 84), ("web01", 72)], "12 sunucunun ilk çeyreği: 3 sunucu")
ok(kullanir("ntile"), "NTILE kullan")
```

```solution
WITH d AS (
    SELECT ad, cpu, NTILE(4) OVER (ORDER BY cpu DESC) AS dilim
    FROM sunucular
)
SELECT ad, cpu
FROM d
WHERE dilim = 1
ORDER BY cpu DESC;
```

```hint
`NTILE(4) OVER (ORDER BY cpu DESC)` her satıra 1–4 arası bir dilim numarası verir. Pencere fonksiyonu WHERE'de kullanılamadığı için bir CTE'de hesapla.
```
:::

::: gorev İlk ve son ölçüm
`olcumler` tablosundaki her sunucu için ilk ve son ölçümün CPU değerini ve aradaki farkı getir: `sunucu_id`, `ilk`, `son`, `degisim`; sunucuya göre sıralı, sunucu başına **tek satır**.

```starter
SELECT DISTINCT sunucu_id,
       FIRST_VALUE(cpu) OVER (PARTITION BY sunucu_id ORDER BY zaman) AS ilk,
       LAST_VALUE(cpu)  OVER (PARTITION BY sunucu_id ORDER BY zaman) AS son
FROM olcumler
ORDER BY sunucu_id;
```

```test
eq(sutunlar, ["sunucu_id", "ilk", "son", "degisim"], "sütunlar")
eq(sonuc, [(1, 40, 69, 29), (4, 62, 88, 26), (8, 70, 90, 20)], "üç sunucu")
```

```solution
SELECT DISTINCT sunucu_id, ilk, son, son - ilk AS degisim
FROM (
    SELECT sunucu_id,
           FIRST_VALUE(cpu) OVER w AS ilk,
           LAST_VALUE(cpu)  OVER w AS son
    FROM olcumler
    WINDOW w AS (PARTITION BY sunucu_id ORDER BY zaman
                 ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
)
ORDER BY sunucu_id;
```

```hint
Başlangıç kodundaki `LAST_VALUE` varsayılan çerçeve yüzünden her satırın kendi değerini veriyor ve `DISTINCT` birden çok satır bırakıyor. Çerçeveyi bölümün sonuna kadar uzat.
```

```hint
`WINDOW w AS (PARTITION BY sunucu_id ORDER BY zaman ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)`; farkı dıştaki sorguda hesapla.
```
:::
