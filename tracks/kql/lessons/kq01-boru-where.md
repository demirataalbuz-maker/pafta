---
id: kq01
title: Boru Hattı ve where
summary: KQL'in soldan sağa akan boru mantığı; take, count, where, karşılaştırmalar, and/or, in, between ve boş değerler.
---

::: anlat Veri soldan sağa akar
KQL (Kusto Query Language), Microsoft Sentinel, Defender ve Azure Log Analytics'in sorgu dilidir. Yalnızca **okur**; veriyi değiştirmez. Bir sorgu bir **tabloyla** başlar ve `|` (boru) işaretiyle birbirine bağlanan adımlardan geçer. Her adım bir önceki adımın sonucunu alır:

```kql
sunucular                 #! tablo: bütün satırlar
| where cpu > 70          #! süz
| project ad, cpu         #! sütun seç
```

Bu yolda SQL yolunun BT operasyonu veritabanını kullanıyoruz: `ekipler`, `personel`, `sunucular`, `biletler`, `olcumler`. Gerçek bir Sentinel çalışma alanında tablolar `Heartbeat`, `Perf`, `Event` gibi adlar taşır ama mantık aynıdır.

```kql
sunucular
| take 3                  #! herhangi 3 satır: tabloya göz atmak için
```

```kql
biletler
| count                   #! satır sayısı
```

Bir sorguyu SQL ile karşılaştırınca fark görünür: SQL'de `SELECT ... FROM ... WHERE` sırası sabittir, KQL'de adımları istediğin sırada, istediğin kadar art arda eklersin.

> [!NOT]
> Tezgahta birden çok sorguyu **boş bir satırla** ayırarak tek seferde çalıştırabilirsin; her biri ayrı bir tablo verir. Kusto Explorer'da da sorgular boş satırla ayrılır. Bu tezgah KQL'i SQLite'a çevirerek çalıştırır; **SQL** düğmesi her sorgunun SQL karşılığını gösterir.

> [!TUZAK] İki farklı "KQL": Kusto Query Language ve Kibana Query Language
> Siber güvenlikte **KQL** kısaltması birbirinden tamamen farklı iki dil için kullanılır:
> - **Kusto Query Language (bu yol):** Microsoft Sentinel, Microsoft Defender XDR ve Azure Data Explorer'ın boru (`|`) tabanlı analitik sorgu dilidir (`Tablo | where ... | summarize ...`).
> - **Kibana Query Language (Elastic):** Elastic Security / Kibana arama çubuğunda kullanılan tek satırlık filtre dilidir (`source.ip: 10.0.0.1 and event.code: "4625"`). İkisinin sözdizimini birbirine karıştırma.
:::

::: anlat where ile süzmek
| Yazım | Anlamı |
|---|---|
| `==`, `!=` | eşit, eşit değil (metinde büyük-küçük harfe **duyarlı**) |
| `<`, `<=`, `>`, `>=` | büyüklük |
| `and`, `or`, `not(...)` | koşulları birleştir |
| `in ("a", "b")`, `!in (...)` | listede olan / olmayan |
| `between (a .. b)` | a ile b arasında, iki uç dahil |
| `isempty(x)`, `isnotempty(x)` | metin boş mu |
| `isnull(x)`, `isnotnull(x)` | sayı ya da tarih değeri yok mu |

```kql
sunucular
| where rol == "web" and sehir == "İstanbul"
| project ad, cpu

sunucular
| where rol in ("web", "veritabanı") and cpu between (40 .. 80)
| project ad, rol, cpu

sunucular
| where isempty(sehir)
| project ad
```

Metinler çift ya da tek tırnakla yazılır: `"Ankara"` ya da `'Ankara'`. Eşitlik **`==`** ile sınanır; tek `=` yalnızca yeni bir sütuna ad verirken kullanılır.

> [!TUZAK]
> KQL büyük-küçük harfe duyarlıdır: `where` bir işleçtir, `Where` hata verir. Tablo ve sütun adları da öyle: `Sunucular` diye bir tablo yoktur.

> [!DERİN]
> KQL'de metin değerleri hiçbir zaman null olmaz, en fazla **boş** olur. Bu yüzden metinlerde `isnull` değil `isempty` kullanılır. `isnull` sayılar ve tarihler içindir: `where isnull(ram_gb)`.
:::

::: tahmin
Tek bir sayı:

```kql
sunucular
| where rol == "web" or cpu > 80
| count
```

???

`5`. Üç web sunucusu (web01, web02, web03) ve web olmayıp CPU'su 80'i aşan iki sunucu (db01: 91, cache01: 84). `or` iki koşuldan birini sağlayanı alır.
:::

::: gorev İstanbul'daki web sunucuları
İstanbul'da bulunan **web** sunucularının yalnızca adını getir.

```starter
sunucular
| where rol == "web"
| project ad
```

```test
eq(sutunlar, ["ad"], "yalnızca ad sütunu")
eq(sorted(r[0] for r in sonuc), ["web01", "web02"], "web01 ve web02")
```

```solution
sunucular
| where rol == "web" and sehir == "İstanbul"
| project ad
```

```hint
İki koşulu `and` ile bağla: `where rol == "web" and sehir == "İstanbul"`.
```
:::

::: gorev Orta yük
CPU'su 30 ile 60 arasında (iki uç dahil) olan sunucuların `ad` ve `cpu` sütunlarını getir; `between` kullan.

```starter
sunucular
| where cpu > 30
| project ad, cpu
```

```test
eq(sutunlar, ["ad", "cpu"], "sütunlar: ad, cpu")
eq(sorted(sonuc), sorted(sorgu("SELECT ad, cpu FROM sunucular WHERE cpu BETWEEN 30 AND 60")), "30–60 arası sunucular")
ok(kullanir("between"), "between kullan")
```

```solution
sunucular
| where cpu between (30 .. 60)
| project ad, cpu
```

```hint
`between (30 .. 60)`: iki nokta ve parantez KQL'in aralık yazımıdır.
```
:::

::: gorev Acil açık biletler
Durumu `açık` olan ve önceliği `yüksek` ya da `kritik` olan biletleri **say**.

```starter
biletler
| count
```

```test
eq(sutunlar, ["Count"], "count işlecinin sütunu: Count")
eq(sonuc, [(3,)], "3 bilet")
ok(kullanir("in"), "öncelikleri in ile listele")
```

```solution
biletler
| where durum == "açık" and oncelik in ("yüksek", "kritik")
| count
```

```hint
Önce `where` ile süz, sonra `| count`. Birden çok değer için `oncelik in ("yüksek", "kritik")`.
```
:::
