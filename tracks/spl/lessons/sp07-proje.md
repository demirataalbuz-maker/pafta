---
id: sp07
title: Proje · Haftalık Operasyon Raporu
summary: SQL ve KQL yollarındaki haftalık raporu Splunk ile kurmak; eval ile bayraklar, stats sum ile koşullu sayım, iki join ve sıralı ilk N.
---

::: anlat Proje tanımı
Aynı rapor, üçüncü dil: **12–18 Ekim 2026** haftasının bilet özeti. SQL'de `COUNT(*) FILTER`, KQL'de `countif` kullanmıştın. Splunk'ta yaygın kalıp, her olaya `eval` ile 0/1 **bayraklar** koymak ve `stats sum()` ile toplamaktır:

```spl
sourcetype=biletler
| eval kritik = if(oncelik="kritik", 1, 0), acik = if(durum="açık", 1, 0)
| stats count as toplam, sum(kritik) as kritik, sum(acik) as acik
```

Zaman alanları metin olduğu için hafta aralığını `where` içinde metin karşılaştırmasıyla, **yarı açık** yazabilirsin: `acilis>="2026-10-12" AND acilis<"2026-10-19"`.

Üç bölüm:

1. **Haftanın özeti**: açılan, çözülen, hafta sonunda açık kalan
2. **Ekip yükü**: bilet atanmış ekiplerin açık ve hafta içinde çözülen bilet sayıları
3. **Sıcak noktalar**: hafta içinde en çok bilet açılan beş sunucu

> [!İPUCU]
> Splunk'ta uzun aramaları komut başına bir satıra böl. Bir aramanın hangi adımda bozulduğunu bulmak için sondan komut silip ara sonuçlara bak; kayıt sorgulayan her dilde aynı yöntem işe yarar.
:::

::: gorev 1 · Haftanın özeti
Tek satırda üç alan getir: `acilan` (hafta içinde açılan), `cozulen` (hafta içinde kapanan), `acik_kalan` (hafta içinde açılmış ama hafta bittiğinde hâlâ kapanmamış: hiç kapanmamış ya da hafta bittikten sonra kapanmış).

```cikti
19|10|9
```

```starter
sourcetype=biletler
| stats count as acilan
```

```test
eq(sutunlar, ["acilan", "cozulen", "acik_kalan"], "alanlar: acilan, cozulen, acik_kalan")
eq(sonuc, [(19, 10, 9)], "19 açılan, 10 çözülen, 9 açık kalan")
eq(dene("DELETE FROM biletler WHERE id IN (1, 19);"), [(17, 9, 8)], "veri değişince de doğru saymalı (sabit sayı yazma)")
```

```solution
sourcetype=biletler
| eval acilan = if(acilis>="2026-10-12" AND acilis<"2026-10-19", 1, 0),
       cozulen = if(kapanis>="2026-10-12" AND kapanis<"2026-10-19", 1, 0),
       acik_kalan = if(acilan=1 AND (isnull(kapanis) OR kapanis>="2026-10-19"), 1, 0)
| stats sum(acilan) as acilan, sum(cozulen) as cozulen, sum(acik_kalan) as acik_kalan
```

```hint
Her olaya üç bayrak koy (`eval ... = if(koşul, 1, 0)`), sonra `stats sum(...) as ...` ile topla.
```

```hint
Bir `eval` içinde az önce tanımladığın alanı kullanabilirsin: `acik_kalan = if(acilan=1 AND (isnull(kapanis) OR kapanis>="2026-10-19"), 1, 0)`.
```
:::

::: gorev 2 · Ekip yükü
Biletleri atandıkları kişinin ekibine bağla; her ekip için `acik` (şu anda açık) ve `cozulen_hafta` (hafta içinde kapanan) sayılarını getir. Sıralama: `cozulen_hafta` azalan, eşitlikte `ekip` artan.

```cikti
Altyapı|1|7
Ağ|2|1
Uygulama|0|1
Veritabanı|2|1
```

```starter
sourcetype=biletler
| stats count by atanan_id
```

```test
eq(sutunlar, ["ekip", "acik", "cozulen_hafta"], "alanlar: ekip, acik, cozulen_hafta")
eq(sonuc, [("Altyapı", 1, 7), ("Ağ", 2, 1), ("Uygulama", 0, 1), ("Veritabanı", 2, 1)], "ekiplere göre sayılar")
```

```solution
sourcetype=biletler
| join atanan_id [search sourcetype=personel | rename id AS atanan_id | fields atanan_id ekip_id]
| join ekip_id [search sourcetype=ekipler | rename id AS ekip_id, ad AS ekip | fields ekip_id ekip]
| eval acik = if(durum="açık", 1, 0),
       coz = if(kapanis>="2026-10-12" AND kapanis<"2026-10-19", 1, 0)
| stats sum(acik) as acik, sum(coz) as cozulen_hafta by ekip
| sort -cozulen_hafta, ekip
```

```hint
İki join: bilet → kişi (`personel`, ortak alan `atanan_id`), kişi → ekip (`ekipler`, ortak alan `ekip_id`).
```

```hint
Bayraklar için `eval`, toplamak için `stats sum(...) by ekip`, sonra `sort -cozulen_hafta, ekip`.
```
:::

::: gorev 3 · Sıcak noktalar
Hafta içinde açılan biletleri sunucuya göre say; en çok bileti olan **beş** sunucunun adını (`ad`) ve bilet sayısını (`bilet`) getir. Eşitlikte ada göre artan. Sunucusu olmayan biletleri sayma.

```cikti
db01|3
dc01|2
izleme01|2
web01|2
web02|2
```

```starter
sourcetype=biletler
| top limit=5 sunucu_id
```

```test
eq(sutunlar, ["ad", "bilet"], "alanlar: ad, bilet")
eq(sonuc, [("db01", 3), ("dc01", 2), ("izleme01", 2), ("web01", 2), ("web02", 2)], "sıcak noktalar")
```

```solution
sourcetype=biletler
| where acilis>="2026-10-12" AND acilis<"2026-10-19"
| stats count as bilet by sunucu_id
| join sunucu_id [search sourcetype=sunucular | rename id AS sunucu_id | fields sunucu_id ad]
| sort -bilet, ad
| head 5
| table ad bilet
```

```hint
Zaman aralığını `where` ile süz, `stats count as bilet by sunucu_id` ile say (sunucusu olmayanlar `by` alanı olmadığı için zaten düşer), sonra adı `join` ile getir.
```
:::
