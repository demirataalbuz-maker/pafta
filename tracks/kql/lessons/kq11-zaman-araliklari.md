---
id: kq11
title: Süreler, Pencereler ve Takvim
summary: datetime ile timespan türleri; tarihleri çıkarıp süre bulmak, süreyi 1h ya da 1m'ye bölüp sayıya çevirmek, datetime_diff'in sınır sayması, range ile takvim kurup boş saatleri sıfırla doldurmak ve bir olaydan sonraki zaman penceresinde ilişkilendirme.
---

::: anlat İki tür: an ve süre
KQL'de zamanla ilgili iki ayrı tür vardır:

| Tür | Ne | Örnek |
|---|---|---|
| `datetime` | bir **an** | `datetime(2026-10-19 08:45)`, `now()`, `ago(1h)` |
| `timespan` | bir **süre** | `30m`, `2h`, `1d`, `90s`, `500ms` |

İkisi arasındaki aritmetik kuralları:

| İşlem | Sonuç | Örnek |
|---|---|---|
| an − an | süre | `kapanis - acilis` → `1.01:00:00` |
| an ± süre | an | `zaman + 30m` |
| süre / süre | sayı | `(kapanis - acilis) / 1h` → `1.5` |
| süre karşılaştırma | bool | `sure > 1d` |

Süreler `[gün.]sa:dk:sn` biçiminde görünür: `1.01:00:00` bir gün bir saattir. Bir süreyi sayıya çevirmenin KQL deyimi, **birimine bölmektir**: dakika için `/ 1m`, saat için `/ 1h`.

```kql
biletler
| where isnotnull(kapanis)
| extend sure = kapanis - acilis
| where sure > 1d
| project id, oncelik, sure
| sort by sure desc
```

### datetime_diff başka bir şey sayar
`datetime_diff('hour', son, ilk)` aradaki süreyi değil, **geçilen saat sınırlarını** sayar. 08:45'ten 10:15'e 1,5 saat geçer ama iki saat sınırı (09:00 ve 10:00) aşılır:

```kql
print gecen = datetime(2026-10-19 10:15) - datetime(2026-10-19 08:45),
      saat = (datetime(2026-10-19 10:15) - datetime(2026-10-19 08:45)) / 1h,
      sinir = datetime_diff('hour', datetime(2026-10-19 10:15), datetime(2026-10-19 08:45))
```

Ne istediğine göre seç: **geçen süre** için çıkar ve böl; "kaç farklı güne yayıldı" gibi **takvim** soruları için `datetime_diff`.

### Takvim fonksiyonları
| Fonksiyon | Sonuç |
|---|---|
| `startofday(t)`, `startofweek(t)`, `startofmonth(t)` | günün, haftanın (pazar), ayın başı |
| `bin(t, 1h)` | saatin başına yuvarlar |
| `dayofweek(t) / 1d` | 0 = pazar … 6 = cumartesi (`dayofweek` bir süre döndürür) |
| `format_datetime(t, "dd.MM.yyyy HH:mm")` | metne biçimler |
:::

::: anlat Boş saatleri doldurmak ve zaman pencereleri
`summarize ... by bin(zaman, 1h)` yalnızca kaydı **olan** saatleri verir; hata olmayan saat sonuçta hiç görünmez. Grafikte o saat sıfır değil "yok" olur ve eğri yanıltır. Çözüm SQ17'dekiyle aynıdır: önce bir takvim kur, veriyi ona bağla. KQL'de takvimi `range` üretir:

```kql
let saatler = range saat from datetime(2026-10-19 08:00) to datetime(2026-10-19 11:00) step 1h;
let hatalar = istekler | where durum >= 500 | summarize hata = count() by saat = bin(zaman, 1h);
saatler
| join kind=leftouter hatalar on saat
| project saat, hata = coalesce(hata, 0)
| sort by saat asc
```

> [!NOT]
> Gerçek Kusto'da bu işin kısa yolu `make-series` işlecidir: `istekler | make-series hata = countif(durum >= 500) default=0 on zaman from ... to ... step 1h`. Sonucu dizi olarak verir ve anomali fonksiyonlarına (`series_decompose_anomalies`) girdi olur. Pafta tezgahında `make-series` yok; `range` ile kurduğun takvim aynı fikri açıkça gösterir.

### Bir olaydan sonraki pencere
"Her dağıtımdan sonraki 30 dakikada ne oldu?" sorusu iki adımdır: olayları anahtarla birleştir, sonra zamanı **pencereyle** süz:

```kql
dagitimlar
| join kind=inner (istekler | project istek_zamani = zaman, sunucu, durum) on sunucu
| where istek_zamani between (zaman .. zaman + 30m)
```

> [!TUZAK]
> Burada `kind=inner` şart. Varsayılan `innerunique` sol tabloyu anahtar başına **tek satıra** indirir (KQ06). web01'e iki dağıtım yapıldığı için biri sessizce kaybolur.
:::

::: tahmin
Tek satır, üç değer:

```kql
print a = datetime(2026-10-19 10:15) - datetime(2026-10-19 08:45),
      b = (datetime(2026-10-19 10:15) - datetime(2026-10-19 08:45)) / 1h,
      c = datetime_diff('hour', datetime(2026-10-19 10:15), datetime(2026-10-19 08:45))
```

???

`01:30:00|1.5|2`. İki anın farkı bir süredir: 1 saat 30 dakika. Süreyi `1h`'ye bölmek onu saat cinsinden sayıya çevirir: 1.5. `datetime_diff('hour', ...)` ise geçilen saat sınırlarını sayar: 09:00 ve 10:00, yani 2.
:::

::: gorev Bir günden uzun sürenler
Kapanmış biletlerden çözümü **bir günden uzun** sürenleri `id`, `oncelik`, `sure` (süre türünde: `kapanis - acilis`) sütunlarıyla, en uzun süren en üstte olacak şekilde getir.

```starter
biletler
| where isnotnull(kapanis)
| extend sure = datetime_diff('day', kapanis, acilis)
| where sure > 1
| project id, oncelik, sure
```

```test
eq(sutunlar, ["id", "oncelik", "sure"], "sütunlar")
eq(sonuc, [(6, "düşük", "1.20:00:00"), (2, "orta", "1.01:00:00")], "iki bilet, süre biçiminde")
```

```solution
biletler
| where isnotnull(kapanis)
| extend sure = kapanis - acilis
| where sure > 1d
| project id, oncelik, sure
| sort by sure desc
```

```hint
`datetime_diff('day', ...)` gün sınırlarını sayar ve bir sayı döndürür. Süre için iki anı doğrudan çıkar: `kapanis - acilis`.
```

```hint
Süreyi bir süre sabitiyle karşılaştır: `where sure > 1d`.
```
:::

::: gorev Saatlik hata takvimi
`2026-10-19 08:00` ile `11:00` arasındaki her saat için 500 ve üstü durum kodlu istek sayısını getir; hata olmayan saatler **0** ile görünsün: `saat`, `hata`; saate göre artan.

```starter
istekler
| where durum >= 500
| summarize hata = count() by saat = bin(zaman, 1h)
| sort by saat asc
```

```test
eq(sutunlar, ["saat", "hata"], "sütunlar")
eq(sonuc, [("2026-10-19 08:00", 0), ("2026-10-19 09:00", 3), ("2026-10-19 10:00", 1), ("2026-10-19 11:00", 0)],
   "dört saat, boşlar sıfırla")
ok(kullanir("range"), "takvimi range ile kur")
```

```solution
let saatler = range saat from datetime(2026-10-19 08:00) to datetime(2026-10-19 11:00) step 1h;
let hatalar = istekler | where durum >= 500 | summarize hata = count() by saat = bin(zaman, 1h);
saatler
| join kind=leftouter hatalar on saat
| project saat, hata = coalesce(hata, 0)
| sort by saat asc
```

```hint
Takvim: `range saat from datetime(2026-10-19 08:00) to datetime(2026-10-19 11:00) step 1h`. Başlangıç kodundaki sorguyu bir `let`'e al.
```

```hint
Takvimi `join kind=leftouter` ile hatalara bağla ve boşları `coalesce(hata, 0)` ile doldur.
```
:::

::: gorev Dağıtım sonrası 30 dakika
Her dağıtım için, aynı sunucuya dağıtım anından itibaren **30 dakika içinde** (sınırlar dahil) gelen istek sayısını ve bunların kaçının 500 ve üstü durum kodlu olduğunu getir: `dagitim` (dağıtım zamanı), `sunucu`, `surum`, `istek`, `hata`; dağıtım zamanına göre artan.

```starter
dagitimlar
| join (istekler | project istek_zamani = zaman, sunucu, durum) on sunucu
| where istek_zamani between (zaman .. zaman + 30m)
| summarize istek = count(), hata = countif(durum >= 500) by dagitim = zaman, sunucu, surum
| sort by dagitim asc
```

```test
eq(sutunlar, ["dagitim", "sunucu", "surum", "istek", "hata"], "sütunlar")
eq(sonuc, [("2026-10-19 08:55", "web01", "2.5.0", 4, 3), ("2026-10-19 10:40", "web02", "2.5.0", 2, 1),
           ("2026-10-19 11:40", "web01", "2.5.1", 1, 0)], "üç dağıtımın üçü de")
```

```solution
dagitimlar
| join kind=inner (istekler | project istek_zamani = zaman, sunucu, durum) on sunucu
| where istek_zamani between (zaman .. zaman + 30m)
| summarize istek = count(), hata = countif(durum >= 500) by dagitim = zaman, sunucu, surum
| sort by dagitim asc
```

```hint
Başlangıç kodu iki satır döndürüyor: web01'in ikinci dağıtımı kayıp. `join`'in varsayılan türünü hatırla.
```

```hint
`join kind=inner` yaz: varsayılan `innerunique` sol tablodaki web01 satırlarından yalnızca birini tutar.
```
:::
