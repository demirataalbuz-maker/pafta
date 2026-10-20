---
id: sp18
title: Proje · Web Erişim Panosu
summary: Web istek günlüğünden bir Splunk panosu kurmak; saatlik hacim, hata oranı ve ortalama süre, kimlikleri kalıba indirip en sorunlu uç noktaları bulmak ve append ile streamstats kullanarak her isteği kendisinden önceki son dağıtıma bağlamak.
---

::: anlat Proje tanımı
Uygulama ekibi için bir Splunk panosu (dashboard) kuruyorsun. Her panel bir aramadır:

| Panel | Soru | Araçlar |
|---|---|---|
| 1 | saat saat hacim, hata oranı, ortalama süre | `timechart` + `eval` |
| 2 | sorun hangi uç noktada? | `replace` ile kalıp, `count(eval())`, `sort` |
| 3 | dağıtımlardan sonra ne oldu? | `append`, `sort`, `streamstats`, pencere |

### Üçüncü panelin fikri
KQL'de (KQ11) dağıtımları isteklerle `join` edip bir zaman penceresiyle süzmüştün. Splunk'ta pahalı `join` yerine sık kullanılan bir kalıp vardır: iki kaynağı **alt alta** koy, zamana göre sırala ve her olaya "bu sunucuya yapılan **son dağıtımın** zamanını" taşı. Taşımayı `streamstats max()` yapar: dağıtım olaylarında dolu, isteklerde boş olan bir alanın birikimli en büyüğü, her zaman en son dağıtımdır.

```spl
sourcetype=istekler
| append [search sourcetype=dagitimlar | eval dagitim=_time]
| sort sunucu _time
| streamstats max(dagitim) as son_dagitim by sunucu
| eval dk=round((_time-son_dagitim)/60, 0)
| table sunucu zaman dagitim son_dagitim dk
| head 8
```

Böylece her isteğin yanında "son dağıtımdan kaç dakika sonra geldi" bilgisi durur; gerisi bir `where` ve bir `stats`'tır.
:::

::: tahmin
Tek bir sayı:

```spl
sourcetype=dagitimlar
| stats dc(sunucu) as sunucu
```

???

`2`. Üç dağıtım yapılmış ama ikisi aynı sunucuya (web01); farklı sunucu sayısı 2.
:::

::: gorev 1 · Saatlik sağlık paneli
Saat başına istek sayısını (`istek`), 500 ve üstü durum kodlu istek sayısını (`hata`) ve ortalama süreyi (`ort`, tam sayıya yuvarlanmış) tek bir `timechart` ile hesapla; ardından hata oranını (`hata_orani`, yüzde, bir ondalık) ekle.

```starter
sourcetype=istekler
| timechart span=1h count as istek
```

```test
eq(sutunlar, ["_time", "istek", "hata", "ort", "hata_orani"], "sütunlar")
eq(sonuc, [("2026-10-19 08:00", 7, 0, 230, 0.0), ("2026-10-19 09:00", 8, 3, 870, 37.5),
           ("2026-10-19 10:00", 7, 1, 673, 14.3), ("2026-10-19 11:00", 4, 0, 121, 0.0)], "dört saat")
```

```solution
sourcetype=istekler
| timechart span=1h count as istek, count(eval(durum>=500)) as hata, avg(sure_ms) as ort
| eval hata_orani=round(100*hata/istek, 1), ort=round(ort, 0)
```

```hint
Bölme olmadan `timechart` birden çok toplama alabilir: `count as istek, count(eval(durum>=500)) as hata, avg(sure_ms) as ort`.
```
:::

::: gorev 2 · En sorunlu uç noktalar
Yollardaki sondaki sayısal kimliği `{id}` ile değiştirip `yol_kalibi` alanını kur. Her kalıp için istek sayısını (`istek`), 400 ve üstü durum kodlu istek sayısını (`hata`) ve en uzun süreyi (`en_yavas`) hesapla; en çok hatası olan üç kalıbı, eşitlikte en yavaşı önde olacak şekilde getir.

```starter
sourcetype=istekler
| stats count as istek by yol
| sort -istek
| head 3
```

```test
eq(sutunlar, ["yol_kalibi", "istek", "hata", "en_yavas"], "sütunlar")
eq(sonuc, [("/api/rapor", 8, 4, 2600), ("/api/bilet/{id}", 3, 1, 180), ("/api/bilet", 8, 0, 310)], "ilk üç kalıp")
```

```solution
sourcetype=istekler
| eval yol_kalibi=replace(yol, "/\d+$", "/{id}")
| stats count as istek, count(eval(durum>=400)) as hata, max(sure_ms) as en_yavas by yol_kalibi
| sort -hata -en_yavas
| head 3
```

```hint
`replace(yol, "/\d+$", "/{id}")`: sondaki `/sayı` kısmı `/{id}` olur.
```

```hint
İki anahtarlı sıralama: `sort -hata -en_yavas`.
```
:::

::: gorev 3 · Dağıtımdan sonraki 30 dakika
Her isteği, aynı sunucuya kendisinden önce yapılan **son dağıtıma** bağla ve dağıtımdan sonraki **30 dakika** içinde (1800 saniye, sınır dahil) gelen istekleri dağıtım başına say: `dagitim_zamani` (`%Y-%m-%d %H:%M` biçiminde), `sunucu`, `istek`, `hata` (500 ve üstü); dağıtım zamanına göre artan. `join` kullanma.

```starter
sourcetype=istekler
| append [search sourcetype=dagitimlar | eval dagitim=_time]
| sort sunucu _time
| table sunucu zaman dagitim
```

```test
eq(sutunlar, ["dagitim_zamani", "sunucu", "istek", "hata"], "sütunlar")
eq(sonuc, [("2026-10-19 08:55", "web01", 4, 3), ("2026-10-19 10:40", "web02", 2, 1), ("2026-10-19 11:40", "web01", 1, 0)],
   "üç dağıtım")
ok(not kullanir("join"), "join kullanma")
ok(kullanir("streamstats"), "son dağıtımı streamstats ile taşı")
```

```solution
sourcetype=istekler
| append [search sourcetype=dagitimlar | eval dagitim=_time]
| sort sunucu _time
| streamstats max(dagitim) as son_dagitim by sunucu
| where isnull(dagitim) AND _time-son_dagitim<=1800
| stats count as istek, count(eval(durum>=500)) as hata by sunucu son_dagitim
| eval dagitim_zamani=strftime(son_dagitim, "%Y-%m-%d %H:%M")
| sort dagitim_zamani
| table dagitim_zamani sunucu istek hata
```

```hint
Son dağıtımı taşı: `streamstats max(dagitim) as son_dagitim by sunucu`. Dağıtım olaylarını at ve pencereyi uygula: `where isnull(dagitim) AND _time-son_dagitim<=1800`.
```

```hint
`stats count as istek, count(eval(durum>=500)) as hata by sunucu son_dagitim`, sonra `strftime(son_dagitim, "%Y-%m-%d %H:%M")` ile biçimle ve sırala.
```
:::
