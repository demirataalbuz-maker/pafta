---
id: kq22
title: Sorgudan Zamanlanmış Kurala · Sıklık, Geriye Bakış ve Gecikme
summary: Bir avcılık sorgusu ile zamanlanmış bir analitik kuralın farkı: çalışma sıklığı, geriye bakış süresi, eşik, olay gruplama, bastırma ve varlık eşleme; kuralın çalıştırmalarını range ile canlandırmak; geriye bakış sıklıktan kısaysa kaçan, uzunsa iki kez sayılan olaylar; geç gelen (alım zamanı olay zamanından sonra olan) kaydın hiçbir pencereye düşmemesi; çapraz birleştirmede innerunique tuzağı ve hiç olay görmeyen çalıştırmayı sıfır olarak göstermek.
kazanim: SC200 1.3, SC200 3.2
---

::: anlat Sorgu sonucu alarm değildir
KQ19 ve KQ20'de bir sorgu yazdın, çalıştırdın, sonucu okudun. Microsoft Sentinel'de aynı sorguyu **zamanlanmış bir analitik kurala** (scheduled analytics rule) çevirdiğinde onu artık sen çalıştırmazsın; ürün belirli aralıklarla, belirli bir zaman penceresi üzerinde kendisi çalıştırır. Alarmın neyi kapsadığını sorgu kadar bu ayarlar da belirler:

| Ayar | Anlamı | Yanlış ayarlanınca |
|---|---|---|
| **Çalışma sıklığı** (query frequency) | Kural ne sıklıkla çalışır | Seyrekse alarm geç gelir |
| **Geriye bakış** (lookup period, lookback) | Her çalıştırma ne kadar geriye bakar | Sıklıktan kısaysa iki çalıştırma arası **hiç görülmez**; uzunsa aynı olay **iki kez** alarm üretir |
| **Eşik** (alert threshold) | Sonuç sayısı kaça ulaşınca alarm üretilir | Düşükse gürültü, yüksekse kaçırma |
| **Olay gruplama** (event grouping) | Bütün sonuçlar tek alarm mı, her satır ayrı alarm mı | Ayrı alarmda tek bir arıza onlarca kayıt açar |
| **Bastırma** (suppression) | Alarmdan sonra bir süre yeniden üretme | Uzun bastırma, yeni bir olayı da gizler |
| **Varlık eşleme** (entity mapping) | Hangi sütun bir sunucu, hesap, IP | Eşlenmezse alarmlar aynı varlıkta birleşmez |

Sorgu kurala dönüşünce zaman süzgeci de ürüne geçer: her çalıştırma yalnız geriye bakış penceresindeki kayıtları görür. Bu derste ürün yok; kuralın çalıştırmalarını `range` ile **canlandıracağız**. Her çalıştırma anı `calisma`, penceresi `(calisma − geriye bakış, calisma]`: başlangıç hariç, çalıştırma anı dahil. Gerçek ürün sınırları ve gecikme payını kendi zamanlamasıyla uygular; burada önemli olan pencerelerin birbirine göre nasıl dizildiği.

```kql
range calisma from datetime(2026-10-19 09:00) to datetime(2026-10-19 10:30) step 30m
| extend bas = calisma - 30m
```

Her çalıştırmayı her olayla eşlemek için iki tarafa da sabit bir anahtar koyup birleştirirsin (çapraz birleştirme), sonra pencere koşulunu `countif` ile sayarsın:

```kql
range calisma from datetime(2026-10-19 09:00) to datetime(2026-10-19 10:00) step 30m
| extend k = 1
| join kind=inner (istekler | where durum >= 500 | project zaman, k = 1) on k
| summarize hata = countif(zaman > calisma - 30m and zaman <= calisma) by calisma
```

> [!TUZAK] Çapraz birleştirmede `kind`'ı yaz
> KQL'de `join`'in varsayılanı `innerunique`dir: sol taraf **anahtar başına tek satıra** indirilir. Bütün satırların anahtarı `k = 1` olduğu için üç çalıştırmadan yalnız biri kalır. Bu derste ölçüldü: `kind` yazılmayan aynı sorgu tek satır verdi, `09:00 | 4`. Çapraz birleştirmede `kind=inner` ya da `kind=leftouter` yaz.
:::

::: tahmin
Kural 30 dakikada bir çalışıyor ama geriye bakışı **15 dakika**. Ne yazar?

```kql
range calisma from datetime(2026-10-19 09:00) to datetime(2026-10-19 10:00) step 30m
| extend k = 1
| join kind=inner (istekler | where durum >= 500 | project zaman, k = 1) on k
| where zaman > calisma - 15m and zaman <= calisma
| summarize hata = count() by calisma
```

???

**Hiç satır.**

Hata istekleri 09:01, 09:02 ve 09:12'de. Pencereler `(08:45, 09:00]`, `(09:15, 09:30]` ve `(09:45, 10:00]`; üç hatanın hiçbiri bunlara düşmüyor. Geriye bakış sıklıktan kısa olduğu için her yarım saatin ilk on beş dakikası **hiçbir çalıştırmada görülmez**. İkinci ders: `where`'i birleştirmeden sonra koyduğun için olay görmeyen çalıştırmalar da sonuçtan düştü. "Bu çalıştırma sıfır gördü" bilgisi kayboldu. Sıfırları da görmek istiyorsan pencereyi `where` ile değil `countif` ile say.
:::

::: gorev 1 · Kuralın çalıştırmaları
Kural `istekler | where durum >= 500` sorgusunu **30 dakikada bir**, **30 dakika** geriye bakarak çalıştırıyor. İlk çalıştırma 09:00, son çalıştırma 12:00. Pencerede **en az 2** hata isteği varsa alarm üretiyor.

Her çalıştırma için `calisma`, `hata` (penceredeki 500 ve üstü istek sayısı) ve `alarm` (`hata >= 2`) sütunlarını yaz. Hiç hata görmeyen çalıştırmalar da `0` ile listede kalsın. Çalıştırma zamanına göre artan sırala.

```starter
range calisma from datetime(2026-10-19 09:00) to datetime(2026-10-19 12:00) step 30m
| extend k = 1
| join (istekler | where durum >= 500 | project zaman, k = 1) on k
| where zaman > calisma - 30m and zaman <= calisma
| summarize hata = count() by calisma
```

```test
eq(sutunlar, ["calisma", "hata", "alarm"], "sütunlar")
eq(len(sonuc), 7, "09:00'dan 12:00'ye yarım saatte bir yedi çalıştırma, hata görmeyenler dahil")
eq([(r[0], r[1]) for r in sonuc],
   [("2026-10-19 09:00", 0), ("2026-10-19 09:30", 3), ("2026-10-19 10:00", 0), ("2026-10-19 10:30", 0),
    ("2026-10-19 11:00", 1), ("2026-10-19 11:30", 0), ("2026-10-19 12:00", 0)],
   "pencere (calisma − 30m, calisma]; 10:42'deki tek hata 11:00 çalıştırmasında")
eq([str(r[2]).lower() for r in sonuc], ["false", "true", "false", "false", "false", "false", "false"],
   "eşik 2: yalnız 09:30 alarm üretir")
```

```solution
range calisma from datetime(2026-10-19 09:00) to datetime(2026-10-19 12:00) step 30m
| extend k = 1
| join kind=leftouter (istekler | where durum >= 500 | project zaman, k = 1) on k
| summarize hata = countif(zaman > calisma - 30m and zaman <= calisma) by calisma
| extend alarm = hata >= 2
| sort by calisma asc
```

```hint
`kind` yazılmayan birleştirme `innerunique`dir ve sabit anahtarda tek çalıştırma bırakır: `kind=leftouter` ya da `kind=inner` yaz. Pencereyi `where` ile süzersen hata görmeyen çalıştırma kaybolur; `summarize hata = countif(...) by calisma` ile say.
```
:::

::: gorev 2 · Kaçan ve iki kez sayılan olaylar
Aynı kural 09:00'dan 12:00'ye **30 dakikada bir** çalışıyor. İki geriye bakış ayarını karşılaştır: **20 dakika** ve **60 dakika**. Her hata isteği (`durum >= 500`) için kaç çalıştırmanın onu gördüğünü say: `zaman`, `sunucu`, `gorulme_20dk`, `gorulme_60dk`. Zamana göre artan sırala.

`0` hiçbir alarmın o olayı içermediği, `2` aynı olayın iki çalıştırmada yeniden sayıldığı anlamına gelir.

```starter
istekler
| where durum >= 500
| project zaman, sunucu
```

```test
eq(sutunlar, ["zaman", "sunucu", "gorulme_20dk", "gorulme_60dk"], "sütunlar")
eq(sonuc, [("2026-10-19 09:01", "web01", 0, 2), ("2026-10-19 09:02", "web01", 0, 2),
           ("2026-10-19 09:12", "web01", 1, 2), ("2026-10-19 10:42", "web02", 1, 2)],
   "20 dk'da 09:01 ve 09:02 hiçbir pencereye düşmez; 60 dk'da her olay iki kez sayılır")
```

```solution
let calismalar = range calisma from datetime(2026-10-19 09:00) to datetime(2026-10-19 12:00) step 30m | extend k = 1;
istekler
| where durum >= 500
| project zaman, sunucu, k = 1
| join kind=inner calismalar on k
| summarize gorulme_20dk = countif(zaman > calisma - 20m and zaman <= calisma),
            gorulme_60dk = countif(zaman > calisma - 60m and zaman <= calisma) by zaman, sunucu
| sort by zaman asc
```

```hint
Çalıştırmaları `let calismalar = range ... | extend k = 1;` ile bir kez tanımla. Olaylara da `k = 1` ekleyip `kind=inner` ile birleştir; iki ayarı aynı `summarize` içinde iki `countif` ile say.
```
:::

::: gorev 3 · Geç gelen kayıt
Bir kaydın iki zamanı vardır: olayın **olduğu** an (`zaman`, Sentinel'de `TimeGenerated`) ve kaydın çalışma alanına **ulaştığı** an (`alim`, Sentinel'de `ingestion_time()`). Kural bir çalıştırmada yalnız o ana kadar **ulaşmış** kayıtları görebilir.

Kural 09:00'dan 09:50'ye **10 dakikada bir**, **10 dakika** geriye bakarak çalışıyor. Her kayıt için iki sayı hesapla:

- `zamana_gore`: pencereyi `zaman` üzerinden kuran kural. Kaydı görmesi için `zaman` pencerede olmalı **ve** kayıt o çalıştırmaya kadar ulaşmış olmalı (`alim <= calisma`).
- `alima_gore`: pencereyi `alim` üzerinden kuran kural. `alim` pencerede olmalı.

Sütunlar: `zaman`, `alim`, `sunucu`, `zamana_gore`, `alima_gore`; zamana göre artan. Kayıtlar başlangıç sorgusundaki `datatable`'da.

```starter
let olaylar = datatable(zaman: datetime, alim: datetime, sunucu: string) [
    datetime(2026-10-19 09:03), datetime(2026-10-19 09:04), "web01",
    datetime(2026-10-19 09:08), datetime(2026-10-19 09:13), "web01",
    datetime(2026-10-19 09:19), datetime(2026-10-19 09:20), "web02",
    datetime(2026-10-19 09:25), datetime(2026-10-19 09:41), "web02",
    datetime(2026-10-19 09:30), datetime(2026-10-19 09:30), "web01"
];
olaylar
| extend gecikme = alim - zaman
```

```test
eq(sutunlar, ["zaman", "alim", "sunucu", "zamana_gore", "alima_gore"], "sütunlar")
eq(sonuc, [("2026-10-19 09:03", "2026-10-19 09:04", "web01", 1, 1),
           ("2026-10-19 09:08", "2026-10-19 09:13", "web01", 0, 1),
           ("2026-10-19 09:19", "2026-10-19 09:20", "web02", 1, 1),
           ("2026-10-19 09:25", "2026-10-19 09:41", "web02", 0, 1),
           ("2026-10-19 09:30", "2026-10-19 09:30", "web01", 1, 1)],
   "09:08 ve 09:25 kayıtları zamana göre kuran kurala hiç görünmez; alım zamanına göre her kayıt bir kez görülür")
```

```solution
let olaylar = datatable(zaman: datetime, alim: datetime, sunucu: string) [
    datetime(2026-10-19 09:03), datetime(2026-10-19 09:04), "web01",
    datetime(2026-10-19 09:08), datetime(2026-10-19 09:13), "web01",
    datetime(2026-10-19 09:19), datetime(2026-10-19 09:20), "web02",
    datetime(2026-10-19 09:25), datetime(2026-10-19 09:41), "web02",
    datetime(2026-10-19 09:30), datetime(2026-10-19 09:30), "web01"
];
let calismalar = range calisma from datetime(2026-10-19 09:00) to datetime(2026-10-19 09:50) step 10m | extend k = 1;
olaylar
| extend k = 1
| join kind=inner calismalar on k
| summarize zamana_gore = countif(zaman > calisma - 10m and zaman <= calisma and alim <= calisma),
            alima_gore = countif(alim > calisma - 10m and alim <= calisma) by zaman, alim, sunucu
| sort by zaman asc
```

```hint
09:08 kaydı 09:13'te ulaşıyor. 09:10 çalıştırmasında henüz yok; 09:20 çalıştırmasının penceresi `(09:10, 09:20]` ise 09:08'i kapsamıyor. Zamana göre kuran kuralın koşulunda üç parça olmalı: `zaman > calisma - 10m and zaman <= calisma and alim <= calisma`.
```

```hint
Alım zamanına göre kuran kural her kaydı ulaştığı pencerede bir kez görür; bedeli, alarmın olaydan değil kaydın gelişinden sonra üretilmesidir. Gerçek kurallarda geriye bakışı beklenen gecikme kadar uzatıp çift sayımı ayrıca ayıklamak da yaygın bir çözümdür.
```
:::
