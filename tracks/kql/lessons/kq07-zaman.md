---
id: kq07
title: Zamanla Çalışmak
summary: datetime ve ago, zaman aralıkları, bin ile saatlik ve günlük dilimler, datetime_diff ile süre hesabı ve hourofday.
---

::: anlat Zaman her kaydın omurgasıdır
Kayıt sorgularının neredeyse hepsi bir zaman aralığıyla başlar. KQL'de iki temel araç:

| Yazım | Anlamı |
|---|---|
| `datetime(2026-10-12)`, `datetime(2026-10-12 08:00)` | sabit bir an |
| `ago(1d)`, `ago(6h)`, `ago(30m)` | şimdiden bu kadar önce |
| `now()` | şimdi |

```kql
biletler
| where acilis >= datetime(2026-10-18)
| project id, acilis

biletler
| where acilis > ago(1d)
| project id, acilis
```

> [!NOT]
> Bu tezgahta "şimdi" sabittir: **2026-10-19 12:00**. Böylece `ago()` kullanan sorgular her gün aynı sonucu verir. Gerçek Sentinel'de `now()` gerçekten şu andır ve zamanlar UTC'dir; zaman dilimi farkını unutmak sık yapılan bir hatadır.

### bin ile dilimlemek
`bin(zaman, 1h)` zamanı saatin başına, `bin(zaman, 1d)` günün başına yuvarlar. "Saat başına kaç kayıt?" sorusunun cevabı budur:

```kql
biletler
| summarize adet = count() by gun = bin(acilis, 1d)
| sort by gun asc

olcumler
| summarize ort_cpu = round(avg(cpu), 1) by saat = bin(zaman, 1h)
| sort by saat asc
```

### Süreler ve saatler
`datetime_diff('birim', son, ilk)` iki an arasında **geçilen birim sınırlarının** sayısını verir; birim `'year'`, `'month'`, `'week'`, `'day'`, `'hour'`, `'minute'` ya da `'second'` olabilir. Dikkat: bu, geçen süre değildir. `datetime_diff('hour', 09:10, 08:50)` sonucu 1'dir (bir saat sınırı geçildi), `datetime_diff('hour', 08:55, 08:05)` ise 0. `hourofday(zaman)` saati 0–23 arası bir sayı olarak verir:

```kql
biletler
| where isnotnull(kapanis)
| extend dakika = datetime_diff('minute', kapanis, acilis)
| project id, oncelik, dakika
| top 3 by dakika

biletler
| summarize adet = count() by saat = hourofday(acilis)
| sort by saat asc
```

> [!DERİN]
> Zaman aralığını her zaman sorgunun **başına** koy: `where acilis > ago(1d)` ilk adım olsun. Gerçek Kusto verisi zamana göre parçalara bölünmüş halde saklanır. Zaman süzgeci erken gelince motor ilgisiz parçaları hiç okumaz; sorgu hem hızlanır hem ucuzlar.
:::

::: tahmin
Kaç satır, hangi değerler?

```kql
biletler
| where acilis >= ago(2d)
| summarize adet = count() by gun = bin(acilis, 1d)
| sort by gun asc
```

???

`2026-10-17 00:00|1`, `2026-10-18 00:00|2`, `2026-10-19 00:00|1`. "Şimdi" 2026-10-19 12:00 olduğu için `ago(2d)` 2026-10-17 12:00 demektir. 17 Ekim'in sabah 10:00 bileti dışarıda kalır, akşam 18:05 bileti içeride. Ardından 18'inden iki, 19'undan bir bilet gelir.
:::

::: gorev Son 24 saat
Son **1 gün** içinde açılmış biletlerin `id` ve `acilis` sütunlarını getir; `ago` kullan.

```starter
biletler
| where acilis > datetime(2026-10-12)
| project id, acilis
```

```test
eq(sorted(r[0] for r in sonuc), [19, 20], "19 ve 20 numaralı biletler")
ok(kullanir("ago"), "ago kullan")
```

```solution
biletler
| where acilis > ago(1d)
| project id, acilis
```

```hint
`ago(1d)`: şimdiden bir gün önce.
```
:::

::: gorev Önceliğe göre çözüm süresi
Kapanmış biletler için çözüm süresini **saat** olarak hesapla ve her öncelik için ortalamasını bir ondalığa yuvarlayarak `ort_saat` adıyla getir; en uzun süren öncelik en üstte.

```cikti
düşük|22.3
orta|17.5
yüksek|3.0
kritik|1.4
```

```starter
biletler
| summarize adet = count() by oncelik
```

```test
eq(sutunlar, ["oncelik", "ort_saat"], "sütunlar: oncelik, ort_saat")
eq(sonuc, [("düşük", 22.3), ("orta", 17.5), ("yüksek", 3.0), ("kritik", 1.4)], "öncelik başına ortalama çözüm süresi")
```

```solution
biletler
| where isnotnull(kapanis)
| extend saat = datetime_diff('minute', kapanis, acilis) / 60.0
| summarize ort_saat = round(avg(saat), 1) by oncelik
| sort by ort_saat desc
```

```hint
`datetime_diff('hour', ...)` geçen süreyi değil saat sınırlarını sayar: 08:30–09:20 arası 50 dakika 1 saat sayılır. Dakika al, `60.0`'a böl.
```
:::

::: gorev Sabah biletleri
Saat **9'dan önce** açılmış biletlerin `id`'sini ve açılış saatini (`saat`, 0–23 arası sayı) `id` sırasıyla getir.

```starter
biletler
| project id, acilis
```

```test
eq(sutunlar, ["id", "saat"], "sütunlar: id, saat")
eq(sonuc, [(1, 8), (4, 7), (7, 8), (13, 7), (20, 6)], "beş sabah bileti")
```

```solution
biletler
| extend saat = hourofday(acilis)
| where saat < 9
| project id, saat
| sort by id asc
```

```hint
`hourofday(acilis)` saati sayı olarak verir; `extend` ile ekle, `where saat < 9` ile süz.
```
:::
