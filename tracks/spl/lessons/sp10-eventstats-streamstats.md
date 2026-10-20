---
id: sp10
title: eventstats ve streamstats
summary: Olayları kaybetmeden özet eklemek; eventstats ile toplamdaki pay ve grup ortalamasından sapma, streamstats ile birikimli sayım, kayan ortalama (window), bir önceki olaya bakmak (current=f window=1) ve by ile grup başına akış.
---

::: anlat Olayları kaybetmeden özet
`stats` olayları **yok eder**: 26 istek, sunucu başına 3 satıra iner. Çoğu zaman ise her olayın yanında bir özet görmek istersin: "Bu istek, yolunun ortalamasından ne kadar yavaş?" `eventstats` aynı toplamaları hesaplar ama sonucu **her olaya yeni bir alan olarak** ekler; hiçbir olay kaybolmaz:

```spl
sourcetype=istekler
| eventstats avg(sure_ms) as yol_ort by yol
| where sure_ms > 1.5*yol_ort
| table zaman yol sure_ms
```

| Komut | Olaylar | Sonuç |
|---|---|---|
| `stats avg(x) by g` | yok olur | grup başına bir satır |
| `eventstats avg(x) by g` | kalır | her olaya grubunun ortalaması eklenir |
| `streamstats count` | kalır | her olaya **o ana kadar** olan sayım eklenir |

Toplamdaki payı bulmak da `eventstats`'in klasik işidir: önce bütün olayların sayısını her olaya yaz, sonra grupla:

```spl
sourcetype=istekler
| eventstats count as toplam
| stats count as istek, max(toplam) as toplam by sunucu
| eval pay=round(100*istek/toplam, 1)
```
:::

::: anlat streamstats: akış boyunca
`streamstats` olayları sırayla işler ve her olaya **o ana kadarki** toplamı yazar. Sıra önemlidir; önce `sort` ile istediğin sırayı kur. Gerçek Splunk olayları en yeniden eskiye getirir, bu yüzden zamanla ilerleyen bir akış için `sort _time` yazmak alışkanlık olmalı.

| Yazım | Anlamı |
|---|---|
| `streamstats count as sira` | 1, 2, 3 … |
| `streamstats sum(x) as toplam` | birikimli toplam |
| `streamstats window=3 avg(x) as kayan` | bu olay ve önceki iki olay: kayan ortalama |
| `streamstats current=f window=1 max(x) as onceki` | **yalnızca bir önceki** olay: önceki değer |
| `... by g` | her grup için ayrı akış |

```spl
sourcetype=olcumler
| sort sunucu_id zaman
| streamstats window=3 avg(cpu) as kayan by sunucu_id
| eval kayan=round(kayan, 1)
| table sunucu_id zaman cpu kayan
```

`current=f window=1` kalıbı KQL'deki `prev()`'in karşılığıdır: pencere bir olay, ama şimdiki olay hariç. `by` ile birlikte kullanıldığında grup sınırında kendiliğinden boş kalır:

```spl
sourcetype=olcumler
| sort sunucu_id zaman
| streamstats current=f window=1 max(cpu) as onceki by sunucu_id
| eval degisim=cpu-onceki
| table sunucu_id zaman cpu degisim
```
:::

::: tahmin
Dört satır yazar:

```spl
| makeresults count=4
| streamstats count as n
| eval x=n*10
| streamstats sum(x) as toplam
| table n toplam
```

???

`1|10`, `2|30`, `3|60`, `4|100`. `makeresults` dört boş olay üretir; ilk `streamstats` onları 1'den 4'e numaralar. `x` 10, 20, 30, 40 olur ve ikinci `streamstats` bunların birikimli toplamını yazar.
:::

::: gorev Sunucuların payı
Her sunucunun istek sayısını ve bütün isteklerin içindeki payını (yüzde, bir ondalık) getir: `sunucu`, `istek`, `pay`. Toplamı `eventstats` ile hesapla.

```starter
sourcetype=istekler
| stats count as istek by sunucu
```

```test
eq(sutunlar, ["sunucu", "istek", "pay"], "sütunlar")
eq(sonuc, [("web01", 11, 42.3), ("web02", 9, 34.6), ("web03", 6, 23.1)], "üç sunucu")
ok(kullanir("eventstats"), "toplamı eventstats ile hesapla")
```

```solution
sourcetype=istekler
| eventstats count as toplam
| stats count as istek, max(toplam) as toplam by sunucu
| eval pay=round(100*istek/toplam, 1)
| table sunucu istek pay
```

```hint
`eventstats count as toplam` her olaya bütün olayların sayısını yazar. `stats` sonrası bu alanı kaybetmemek için `max(toplam) as toplam` ile taşı.
```
:::

::: gorev Yolunun ortalamasından yavaş
Süresi, **kendi yolunun** ortalama süresinin 1,5 katını aşan istekleri `zaman`, `yol`, `sure_ms` alanlarıyla getir.

```starter
sourcetype=istekler
| eventstats avg(sure_ms) as ort
| where sure_ms > 1.5*ort
| table zaman yol sure_ms
```

```test
eq(sutunlar, ["zaman", "yol", "sure_ms"], "sütunlar")
eq(sonuc, [("2026-10-19 08:12", "/api/bilet", 310), ("2026-10-19 09:01", "/api/rapor", 2300),
           ("2026-10-19 09:02", "/api/rapor", 2410), ("2026-10-19 10:42", "/api/rapor", 2600),
           ("2026-10-19 11:20", "/api/bilet", 280)], "beş yavaş istek")
```

```solution
sourcetype=istekler
| eventstats avg(sure_ms) as yol_ort by yol
| where sure_ms > 1.5*yol_ort
| table zaman yol sure_ms
```

```hint
Başlangıç kodu bütün isteklerin ortalamasına bakıyor; hızlı bir yolun yavaş isteği bu yüzden görünmüyor. Ortalamayı yol başına hesapla: `eventstats ... by yol`.
```
:::

::: gorev En uzun sessizlik
Kullanıcısı olan istekleri kullanıcıya ve zamana göre sırala, her isteğin aynı kullanıcının **bir önceki** isteğinden kaç dakika sonra geldiğini hesapla ve her kullanıcının en uzun arasını getir: `kullanici`, `en_uzun` (dakika); büyükten küçüğe. Tek isteği olan kullanıcı listede olmasın.

```starter
sourcetype=istekler kullanici=*
| stats min(_time) as ilk, max(_time) as son by kullanici
```

```test
eq(sutunlar, ["kullanici", "en_uzun"], "sütunlar")
eq(sonuc, [("zeynep", 147), ("can", 87), ("ayse", 62), ("mert", 60)], "dört kullanıcı")
ok(kullanir("streamstats"), "streamstats kullan")
```

```solution
sourcetype=istekler kullanici=*
| sort kullanici _time
| streamstats current=f window=1 max(_time) as onceki by kullanici
| eval ara_dk=(_time-onceki)/60
| where isnotnull(ara_dk)
| stats max(ara_dk) as en_uzun by kullanici
| sort -en_uzun
```

```hint
Bir önceki isteğin zamanı: `streamstats current=f window=1 max(_time) as onceki by kullanici`. Ara: `(_time-onceki)/60`.
```

```hint
Her kullanıcının ilk isteğinde önceki yoktur; `where isnotnull(ara_dk)` ile at, sonra `stats max(ara_dk) as en_uzun by kullanici` ve `sort -en_uzun`.
```
:::
