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
```meta
motor: kusto
timeout: 90
```
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
```meta
motor: kusto
timeout: 90
```
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
SINIR = ("INSERT INTO istekler VALUES ('2026-10-19 10:00','10.0.9.9','GET','/a',500,10,'web03',NULL,'{}'),"
         "('2026-10-19 10:30','10.0.9.9','GET','/a',503,10,'web03',NULL,'{}'),"
         "('2026-10-19 11:40','10.0.9.9','GET','/a',500,10,'web03',NULL,'{}'),"
         "('2026-10-19 11:50','10.0.9.9','GET','/a',502,10,'web03',NULL,'{}');")
eq([(r[0], r[1], str(r[2]).lower()) for r in dene(SINIR)],
   [("2026-10-19 09:00", 0, "false"), ("2026-10-19 09:30", 3, "true"), ("2026-10-19 10:00", 1, "false"),
    ("2026-10-19 10:30", 1, "false"), ("2026-10-19 11:00", 1, "false"), ("2026-10-19 11:30", 0, "false"),
    ("2026-10-19 12:00", 2, "true")],
   "tam 10:00 ve 10:30'daki hata yalnız o anın çalıştırmasında sayılır (pencere sonu dahil, başı hariç); tam 2 hata alarm")
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
```meta
motor: kusto
timeout: 90
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
eq(dene("INSERT INTO istekler VALUES ('2026-10-19 10:10','10.0.9.9','GET','/a',500,10,'web03',NULL,'{}'),"
        "('2026-10-19 10:30','10.0.9.9','GET','/a',503,10,'web03',NULL,'{}');")[3:5],
   [("2026-10-19 10:10", "web03", 0, 2), ("2026-10-19 10:30", "web03", 1, 2)],
   "pencere sınırları: 10:10 olayı 10:30'un 20 dk penceresinin başında (hariç), 10:30 olayı kendi çalıştırmasında (dahil)")
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
```meta
motor: kusto
timeout: 90
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
```meta
motor: kusto
timeout: 90
```
:::

::: anlat Yerel gerçek motorun kanıt sınırı
Bu ders Microsoft'un yerel Kusto Emulator sorgu motorunda çalışır; Azure Sentinel/Defender servisi, ajan alımı veya portal kural önizlemesi değildir. Hazırlık SQL'i yalnız örnek tablo verisini çıkarıp typed datatable/let olarak yollar. Öğrencinin KQL'i gerçek motorda ayrıştırılır ve değerlendirilir; desteklenmeyen ürün fonksiyonu sessiz taklit edilmez. Dersin yerel `_GetWatchlist` yardımcı fonksiyonu yalnız fixture listelerini döndürür; gerçek Sentinel watchlist hizmetine erişildiği iddia edilmez. Üretim kümesindeki izin, connector, ingestion, dcount yaklaşık sayımı ve null/string tür sözleşmesi ayrıca doğrulanmalıdır. Sunucu sorgu sınırı 30 saniye; yanıt sınırı 4 MB. Süre veya boyut aşımı başarı sayılmaz.

[Microsoft Kusto Emulator kapsamı](https://learn.microsoft.com/en-us/azure/data-explorer/kusto-emulator-overview). Kurulum README'dedir. Gerçek Sentinel çalışma alanı olmadan portalın **Test with current data** kabulü tamamlanmış sayılmaz.
```meta
motor: kusto
timeout: 90
```
:::


::: anlat Entity mapping bir sütun adı listesinden fazlasıdır
Sentinel kuralındaki `entityMappings`, sorgunun **çıktı sütunlarını** entity identifier'larına bağlar. Account için `Name + UPNSuffix` güçlü tanımlayıcı birleşimlerinden biridir. IP için `Address` alanı vardır; özel adresin bağlamını ve farklı ağlardaki aynı adresleri ayrıca değerlendir. Bu derste IPv4 sözdizimi sınanır; bir IP'nin bir insana ait olduğu iddia edilmez.

Örnek yapılandırma:
```text
{"entityMappings":[
 {"entityType":"Account","fieldMappings":[
   {"identifier":"Name","columnName":"AccountName"},
   {"identifier":"UPNSuffix","columnName":"AccountUPNSuffix"}]},
 {"entityType":"IP","fieldMappings":[
   {"identifier":"Address","columnName":"IPAddress"}]}]}
```
Sorgu `summarize` veya `project` ile bu sütunları kaybederse mapping uygulanabilecek veri kalmaz; alan adını tanımlamak tek başına yeterli değildir. Mapping yapılandırması sorgudaki `pack` ile kendi kendine Sentinel'e kaydedilmez. Son görev mapping'e hazırlanmış **gerçek sorgu çıktısını** ölçer; kuralı yayınlamaz.

**Açık kabul:** Bu makinede Microsoft Sentinel çalışma alanı yok. Portalda Set rule logic → Results simulation → Test with current data, entity mapping seçimi ve Review doğrulaması yapılmadı. Yerel Kusto başarısı bu adımları kapatmaz. Çalışma alanı sağlanınca aynı sorgu ve mapping JSON'u gerçek hizmette yeniden doğrulanmalı; ücretli hizmet onaysız açılmaz.

Kaynaklar: [Entity mapping](https://learn.microsoft.com/en-us/azure/sentinel/map-data-fields-to-entities), [entity identifier'ları](https://learn.microsoft.com/en-us/azure/sentinel/entities-reference), [gerçek kural önizlemesi](https://learn.microsoft.com/en-us/azure/sentinel/detect-threats-custom).
```meta
motor: kusto
timeout: 90
```
:::

::: gorev Mapping'in bağlayacağı gerçek çıktı sütunlarını üret
`entity_girdisi` tablosundan yalnız tam bir @ ayıracı, iki tarafta boş olmayan metin ve geçerli IPv4 IPAddress içeren satırları al. `id,AccountName,AccountUPNSuffix,IPAddress` sütunlarını id sırasında döndür. İsim/suffix harflerini veya adresi değiştirme. Çoklu @, eksik ad/suffix ve hatalı IP dışarıda. Bu ders dar bir UPN parçalayıcısıdır; genel Entra hesap adı doğrulaması değildir. UPN'de whitespace kabulü/normalize etme bu görevde yok; fixture whitespace içermez. Bu çıktı yukarıdaki Account Name/UPNSuffix ve IP Address mapping'ine bağlanır; mapping'i Sentinel'e kaydetme işi ayrıdır.

```meta
motor: kusto
timeout: 90
```

```setup
CREATE TABLE entity_girdisi(id INTEGER,UserPrincipalName TEXT,IPAddress TEXT);
INSERT INTO entity_girdisi VALUES
(1,'Ayse@Pafta.example','198.51.100.9'),(2,'can@pafta.example','203.0.113.5'),
(3,'ad-yok','203.0.113.5'),(4,'@pafta.example','203.0.113.5'),
(5,'ayse@','203.0.113.5'),(6,'a@b@c','203.0.113.5'),
(7,'mert@pafta.example','999.1.1.1'),(8,NULL,'203.0.113.5'),
(9,'z@p.example',NULL),(10,'a@p.example','2001:db8::1');
```

```starter
entity_girdisi | project id,AccountName=UserPrincipalName,AccountUPNSuffix='',IPAddress | sort by id asc
```

```test
eq(sutunlar,['id','AccountName','AccountUPNSuffix','IPAddress'],'mapping JSON sütunları gerçekten çıktıdadır')
eq(sonuc,[(1,'Ayse','Pafta.example','198.51.100.9'),(2,'can','pafta.example','203.0.113.5')],'tek @, boş bileşen ve IPv4 kontrolü')
eq(dene("INSERT INTO entity_girdisi VALUES (11,'Yeni@Baska.example','0.0.0.0'),(12,'Son@p.example','255.255.255.255');")[-2:],[(11,'Yeni','Baska.example','0.0.0.0'),(12,'Son','p.example','255.255.255.255')],'IPv4 sözdizimi uçları; kamuya yönlenebilirlik iddiası değil')
eq(dene("INSERT INTO entity_girdisi VALUES (11,'Yeni@p.example','256.0.0.1');"),sonuc,'IPv4 oktet üst komşusu')
eq(dene('DELETE FROM entity_girdisi;'),[],'boş çıktı; entity uydurma')
```

```solution
entity_girdisi
| extend parts=split(UserPrincipalName,'@')
| where array_length(parts)==2
| extend AccountName=tostring(parts[0]),AccountUPNSuffix=tostring(parts[1])
| where isnotempty(AccountName) and isnotempty(AccountUPNSuffix) and isnotnull(parse_ipv4(IPAddress))
| project id,AccountName,AccountUPNSuffix,IPAddress
| sort by id asc
```

```hint
Sadece ilk @'dan bölmek çoklu @'ı gizler. Identifier ile columnName farklıdır; gerçek çıktı sütun adları mapping JSON'u ile eşleşmeli.
```
:::

::: anlat Kural kaynağı: ürünün doğrulayıcısı neyi kabul etmez
Portalda kaydettiğin kural, Azure'da `Microsoft.SecurityInsights/alertRules` türünde bir kaynaktır. Portal **Export** ile ARM şablonu (JSON) verir, **Import** aynı şablonu geri yükler; kuralı kod olarak saklamanın ve gözden geçirmenin yolu budur. Zamanlanmış kural `kind: "Scheduled"` ile tanımlanır. REST 2025-09-01 tanımında zorunlu alanlar `displayName`, `enabled`, `suppressionEnabled` ve `suppressionDuration`dır. Süreler ISO 8601 biçimindedir: `PT10M`, `PT1H`, `P1D`.

Microsoft Learn'deki belgelenmiş sınırlar:

| Ayar | ARM özelliği | Sınır |
|---|---|---|
| Run query every | `queryFrequency` | 5 dakika – 14 gün |
| Lookup data from the last | `queryPeriod` | 5 dakika – 14 gün; **sıklıktan kısa olamaz** |
| Alert threshold | `triggerOperator` + `triggerThreshold` | `GreaterThan`, `LessThan`, `Equal`, `NotEqual`; eşik her çalıştırmaya ayrı uygulanır |
| Event grouping | `eventGroupingSettings.aggregationKind` | `SingleAlert` (varsayılan) ya da `AlertPerResult`; bir çalıştırma en çok **150** alarm üretir, 150'den fazla sonuçta ilk 149'u tekil, 150. alarm hepsini özetler |
| Suppression | `suppressionEnabled` + `suppressionDuration` | en çok 24 saat; kural bu süre boyunca **hiç çalışmaz** |
| Entity mapping | `entityMappings` | en çok 10 eşleme, eşleme başına en çok 3 identifier; bir alarmda toplam 500 entity (eşlemelere eşit bölünür), Entities alanı 64 KB |
| Rule query | `query` | 1–10.000 karakter, `search *` ve `union *` yok; çıktıda `TimeGenerated` olmalı |

Bu tablonun iki sonucu var. Birincisi: tahmin adımındaki "30 dakikada bir çalışıp 15 dakika geriye bakan" kuralı Sentinel **kaydetmez**; doğrulayıcı sıklığın geriye bakıştan uzun olmasına izin vermez. Pencerelerin arasındaki boşluk yine de oluşabilir, ama bu kez sebebi ayar değil gecikmedir. Sentinel bunun için zamanlanmış kuralları planlanan anlarından **beş dakika sonra** çalıştırır. Kayıt bundan da geç gelirse, Microsoft'un önerdiği çözüm geriye bakışı gecikme kadar uzatmak ve çift sayımı alım zamanıyla kesmektir:

```kql norun
let ingestion_delay = 2min;
let rule_look_back = 5min;
CommonSecurityLog
| where TimeGenerated >= ago(ingestion_delay + rule_look_back)
| where ingestion_time() > ago(rule_look_back)
```

Bu desen 3. görevdeki `alima_gore` sayımının ürün sorgusundaki karşılığıdır. İkinci sonuç: bastırma alarm gürültüsünü değil **kuralın kendisini** durdurur. Bastırma süresince başka bir hesaba yapılan saldırı da görülmez. Aynı olayın tekrar tekrar olay (incident) açmasını istemiyorsan önce olay gruplama (`incidentConfiguration.groupingConfiguration`) düşün.

Entity'nin de kendi kuralları var. Account için `Name` alanı yalnız UPN'in `@` öncesini taşır; `Name + UPNSuffix` güçlü bir birleşimdir, yalnız `Name` zayıftır. Name değeri `ADMIN`, `ADMINISTRATOR`, `SYSTEM`, `ROOT` gibi yerleşik bir hesap adıysa entity alarmdan **düşürülür**: alarm üretilir ama o hesabı taşımaz.

**Bu laboratuvarın sınırı:** Sonraki görevin koşucusu (`motor: sentinel-kural`) kural JSON'unu bu REST şemasına ve sınırlara göre denetler. Sonra sorguyu gerçek Kusto Emulator'da, portalın **Results simulation** penceresi gibi **son 50 planlı çalıştırma** üzerinde koşturur. Her çalıştırma planlanan andan 5 dakika sonra koşar ve yalnız o ana kadar ulaşmış kayıtları görür. Pencere bu dersteki gibi `(plan − queryPeriod, plan]` alınır. Takvim, eşik, gruplama, bastırma ve entity çıkarımı belgelere göre yazılmış yerel bir modeldir. Microsoft pencere uçlarının açık mı kapalı mı olduğunu yazmıyor. Gerçek Sentinel'in **Test with current data** ve **Review and create** doğrulaması bu makinede yapılmadı; kural yayınlanmaz.

Kaynaklar: [zamanlanmış kural ayarları ve sınırları](https://learn.microsoft.com/en-us/azure/sentinel/scheduled-rules-overview), [kural sihirbazı ve sonuç benzetimi](https://learn.microsoft.com/en-us/azure/sentinel/create-analytics-rules), [alım gecikmesi](https://learn.microsoft.com/en-us/azure/sentinel/ingestion-delay), [entity mapping sınırları](https://learn.microsoft.com/en-us/azure/sentinel/map-data-fields-to-entities), [entity identifier'ları](https://learn.microsoft.com/en-us/azure/sentinel/entities-reference), [alertRules REST 2025-09-01](https://learn.microsoft.com/en-us/rest/api/securityinsights/alert-rules/create-or-update?view=rest-securityinsights-2025-09-01).
:::

::: gorev Kuralı kaynak olarak yaz, 50 çalıştırmada sına
`SigninLogs` tablosunda (`TimeGenerated`, `UserPrincipalName`, `IPAddress`, `ResultType`, `AppDisplayName`) parola denemesi arayan zamanlanmış kuralı **ARM şablonu** olarak yaz. Başlangıçtaki şablon Export'tan gelmiş gibi duruyor, ama doğrulamadan geçmiyor ve istenen kuralı da kurmuyor.

İstenen kural:

- **10 dakikada bir** çalışsın, **son 10 dakikaya** baksın.
- Sorgu başarısız girişleri (`ResultType` `"0"` değil) **hesap ve IP çifti başına** saysın. **En az 3** başarısız denemesi olan her çift bir sonuç satırı olsun. Çıktıda `TimeGenerated` (çiftin son denemesi), `AccountName` (UPN'in `@` öncesi), `AccountUPNSuffix` (`@` sonrası), `IPAddress` ve `Basarisiz` (deneme sayısı) bulunsun.
- Kural **0'dan fazla** sonuçta alarm üretsin; **her sonuç ayrı alarm** olsun.
- Account'u `Name` + `UPNSuffix` ile, IP'yi `Address` ile eşle. `Basarisiz` sütununu aynı adla custom detail olarak ekle.
- Alarmdan sonra kural **45 dakika** bastırılsın. Severity `Medium`, taktik `CredentialAccess`, kural açık (`enabled: true`).

Koşucu önce şablonu denetler, sonra sorguyu 2026-10-19 12:00'de biten son 50 planlı çalıştırmada gerçek Kusto'da koşturur. Test hangi çalıştırmanın alarm ürettiğine, hangisinin bastırıldığına ve alarmların hangi entity'leri taşıdığına bakar. Çalıştır düğmesi doğrulama hatalarını ve benzetim özetini gösterir.

```meta
motor: sentinel-kural
son: 2026-10-19 12:00
kosu: 50
pencere: SigninLogs
timeout: 120
```

```setup
CREATE TABLE SigninLogs(TimeGenerated TEXT, alim TEXT, UserPrincipalName TEXT, IPAddress TEXT, ResultType TEXT, AppDisplayName TEXT);
INSERT INTO SigninLogs VALUES
('2026-10-19 10:01','2026-10-19 10:02','derya@pafta.example','203.0.113.20','0','Azure Portal'),
('2026-10-19 10:03','2026-10-19 10:04','derya@pafta.example','203.0.113.20','0','Azure Portal'),
('2026-10-19 10:05','2026-10-19 10:06','derya@pafta.example','203.0.113.20','0','Azure Portal'),
('2026-10-19 10:12','2026-10-19 10:13','berk@pafta.example','203.0.113.50','50126','Azure Portal'),
('2026-10-19 10:14','2026-10-19 10:15','berk@pafta.example','203.0.113.50','50126','Azure Portal'),
('2026-10-19 10:31','2026-10-19 10:32','mert@pafta.example','192.0.2.10','50126','Office 365'),
('2026-10-19 10:33','2026-10-19 10:34','mert@pafta.example','192.0.2.10','50126','Office 365'),
('2026-10-19 10:38','2026-10-19 10:46','mert@pafta.example','192.0.2.10','50126','Office 365'),
('2026-10-19 10:51','2026-10-19 10:52','ayse@pafta.example','203.0.113.7','50126','Office 365'),
('2026-10-19 10:52','2026-10-19 10:53','ece@pafta.example','203.0.113.7','50126','Office 365'),
('2026-10-19 10:53','2026-10-19 10:54','ayse@pafta.example','203.0.113.7','50126','Office 365'),
('2026-10-19 10:54','2026-10-19 10:55','ece@pafta.example','203.0.113.7','50126','Office 365'),
('2026-10-19 10:55','2026-10-19 11:03','ayse@pafta.example','203.0.113.7','50053','Office 365'),
('2026-10-19 10:56','2026-10-19 10:57','ayse@pafta.example','203.0.113.7','0','Office 365'),
('2026-10-19 10:57','2026-10-19 10:58','ece@pafta.example','203.0.113.7','50126','Office 365'),
('2026-10-19 10:58','2026-10-19 10:59','ayse@pafta.example','198.51.100.77','50126','Office 365'),
('2026-10-19 11:21','2026-10-19 11:22','can@pafta.example','198.51.100.4','50126','Azure Portal'),
('2026-10-19 11:22','2026-10-19 11:23','can@pafta.example','198.51.100.4','50126','Azure Portal'),
('2026-10-19 11:24','2026-10-19 11:25','can@pafta.example','198.51.100.4','50126','Azure Portal'),
('2026-10-19 11:52','2026-10-19 11:53','admin@pafta.example','203.0.113.9','50126','Azure Portal'),
('2026-10-19 11:53','2026-10-19 11:54','admin@pafta.example','203.0.113.9','50126','Azure Portal'),
('2026-10-19 11:58','2026-10-19 11:59','admin@pafta.example','203.0.113.9','50126','Azure Portal');
```

```starter
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {"workspace": {"type": "string"}},
  "resources": [{
    "type": "Microsoft.OperationalInsights/workspaces/providers/alertRules",
    "name": "[concat(parameters('workspace'), '/Microsoft.SecurityInsights/pafta-parola-deneme')]",
    "apiVersion": "2025-09-01",
    "kind": "Scheduled",
    "properties": {
      "displayName": "Pafta - parola denemesi",
      "enabled": true,
      "severity": "Medium",
      "tactics": ["CredentialAccess"],
      "query": "SigninLogs | where ResultType == \"50126\" | summarize Basarisiz = count() by UserPrincipalName | where Basarisiz > 3",
      "queryFrequency": "PT10M",
      "queryPeriod": "PT5M",
      "triggerOperator": "GreaterThanOrEqual",
      "triggerThreshold": 1,
      "suppressionEnabled": true,
      "suppressionDuration": "PT48H",
      "eventGroupingSettings": {"aggregationKind": "SingleAlert"},
      "entityMappings": [
        {"entityType": "Account", "fieldMappings": [{"identifier": "FullName", "columnName": "UserPrincipalName"}]}
      ]
    }
  }]
}
```

```test
eq(hatalar, [], 'kural doğrulaması: REST 2025-09-01 şeması ve belgelenmiş sınırlar')
eq(sureler, {'queryFrequency': 10.0, 'queryPeriod': 10.0, 'suppressionDuration': 45.0}, 'sıklık 10 dk, geriye bakış 10 dk, bastırma 45 dk')
eq(((kural.get('eventGroupingSettings') or {}).get('aggregationKind'), kural.get('suppressionEnabled'), kural.get('severity'), kural.get('tactics')),
   ('AlertPerResult', True, 'Medium', ['CredentialAccess']), 'her sonuç ayrı alarm, bastırma açık, Medium, CredentialAccess')
eq(kural.get('customDetails'), {'Basarisiz': 'Basarisiz'}, 'custom detail: ad → sütun')
eq(uyarilar, [], 'Account güçlü identifier birleşimiyle eşlenmeli')
ok({'TimeGenerated', 'AccountName', 'AccountUPNSuffix', 'IPAddress', 'Basarisiz'} <= set(sutunlar), 'sorgu çıktısı mapping ve custom detail sütunlarını taşır', sutunlar)
eq(len(calismalar), 50, 'Results simulation gibi son 50 planlı çalıştırma')
eq([c for c in calismalar if c[3] != 'sessiz'],
   [('2026-10-19 11:00', 2, 2, 'alarm'), ('2026-10-19 11:10', None, 0, 'bastirildi'), ('2026-10-19 11:20', None, 0, 'bastirildi'),
    ('2026-10-19 11:30', None, 0, 'bastirildi'), ('2026-10-19 11:40', None, 0, 'bastirildi'), ('2026-10-19 12:00', 1, 1, 'alarm')],
   "11:00'da iki çift, iki alarm; 45 dk bastırma can'ın 11:30 denemesini gizler; mert'in 8 dk geç gelen kaydı hiçbir pencereye girmez")
ACC = lambda ad: ('Account', (('Name', ad), ('UPNSuffix', 'pafta.example')))
IP = lambda a: ('IP', (('Address', a),))
eq(alarmlar, [('2026-10-19 11:00', (ACC('ayse'), IP('203.0.113.7'))), ('2026-10-19 11:00', (ACC('ece'), IP('203.0.113.7'))),
              ('2026-10-19 12:00', (IP('203.0.113.9'),))],
   "her alarm kendi hesabını taşır; admin yerleşik hesap adı olduğu için Account entity'si düşer, IP kalır")
BERK = "INSERT INTO SigninLogs VALUES ('2026-10-19 10:16','2026-10-19 10:17','berk@pafta.example','203.0.113.50','50126','Azure Portal');"
eq([(a[0], a[1][0]) for a in dene(BERK)[1]], [('2026-10-19 10:20', ACC('berk')), ('2026-10-19 11:30', ACC('can'))],
   "tam 3 deneme alarm üretir; 10:20 alarmının bastırması 11:00'ı, 11:30 alarmınınki 12:00'yi gizler")
IKI_IP = ("INSERT INTO SigninLogs VALUES ('2026-10-19 09:41','2026-10-19 09:42','zeynep@pafta.example','203.0.113.80','50126','Office 365'),"
          "('2026-10-19 09:42','2026-10-19 09:43','zeynep@pafta.example','203.0.113.80','50126','Office 365'),"
          "('2026-10-19 09:43','2026-10-19 09:44','zeynep@pafta.example','203.0.113.81','50126','Office 365'),"
          "('2026-10-19 09:44','2026-10-19 09:45','zeynep@pafta.example','203.0.113.81','50126','Office 365');")
eq(dene(IKI_IP)[1], alarmlar, "iki IP'den ikişer deneme tek çifte toplanmaz")
```

```solution
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {"workspace": {"type": "string"}},
  "resources": [{
    "type": "Microsoft.OperationalInsights/workspaces/providers/alertRules",
    "name": "[concat(parameters('workspace'), '/Microsoft.SecurityInsights/pafta-parola-deneme')]",
    "apiVersion": "2025-09-01",
    "kind": "Scheduled",
    "properties": {
      "displayName": "Pafta - parola denemesi",
      "enabled": true,
      "severity": "Medium",
      "tactics": ["CredentialAccess"],
      "query": "SigninLogs | where ResultType != \"0\" | summarize TimeGenerated = max(TimeGenerated), Basarisiz = count() by UserPrincipalName, IPAddress | where Basarisiz >= 3 | extend AccountName = tostring(split(UserPrincipalName, \"@\")[0]), AccountUPNSuffix = tostring(split(UserPrincipalName, \"@\")[1])",
      "queryFrequency": "PT10M",
      "queryPeriod": "PT10M",
      "triggerOperator": "GreaterThan",
      "triggerThreshold": 0,
      "suppressionEnabled": true,
      "suppressionDuration": "PT45M",
      "eventGroupingSettings": {"aggregationKind": "AlertPerResult"},
      "customDetails": {"Basarisiz": "Basarisiz"},
      "entityMappings": [
        {"entityType": "Account", "fieldMappings": [{"identifier": "Name", "columnName": "AccountName"}, {"identifier": "UPNSuffix", "columnName": "AccountUPNSuffix"}]},
        {"entityType": "IP", "fieldMappings": [{"identifier": "Address", "columnName": "IPAddress"}]}
      ]
    }
  }]
}
```

```hint
Önce Çalıştır'a bas ve doğrulama hatalarını kapat: sıklık geriye bakıştan uzun olamaz, operatör REST enum'undan olmalı (`GreaterThan`, `LessThan`, `Equal`, `NotEqual`), bastırma 24 saati aşamaz. `!` ile başlayan satırlar uyarıdır; `FullName` eşlemede görünür ama entity şemasında yoktur. Hata listesi boşalınca benzetim özeti görünür.
```

```hint
"0'dan fazla sonuçta alarm" `GreaterThan` + `0` demektir. Her çift ayrı alarm olsun diye `aggregationKind` `AlertPerResult` olmalı; 11:00'da iki çift var. Çıktıda `TimeGenerated` yoksa koşucu kuralı reddeder: `summarize TimeGenerated = max(TimeGenerated), ...` ile çiftin son denemesini taşı.
```

```hint
`ResultType == "50126"` yalnız bir hata kodunu sayar; ayse'nin üçüncü denemesi `50053`. Hesap ve IP çifti için `by UserPrincipalName, IPAddress` yaz, `AccountName`/`AccountUPNSuffix` sütunlarını `split(UserPrincipalName, "@")` ile üret.
```
:::

::: anlat Portal kabul defteri: yerel Kusto sonucu ile Sentinel önizlemesini karşılaştır
Bu bölüm mevcut, yetkili Sentinel çalışma alanında uygulanır. Pafta ücretsiz bir Azure/Sentinel hizmeti varmış gibi davranmaz; abonelik, çalışma alanı, veri alımı veya kural yayımı başlatmaz. Çalışma alanın bilinmiyorsa kabul `bekliyor` kalır; yerel Kusto'nun çalışması abonelik varlığını kanıtlamaz.

1. Portalda doğru tenant/çalışma alanını seç. Analytics → Create → Scheduled query rule ekranını aç. Azure portal ile Defender portal düzenleri değişebilir; Microsoft'un aşağıdaki yönergesindeki ilgili görünümü kullan.
2. Önce sorguyu hizmetin gerçek alan adları/verileri üzerinde çalıştır. Yerel `SigninLogs` fixture'ını tenant'ın aynı olayları içerdiği iddiasıyla kullanma. Aynı test verisine erişim yoksa sorgu kabulü ve alarm sayısı eşitliği **karşılaştırılamadı** olarak kaydedilir.
3. Kural mantığında query frequency/period, sonuç eşiği, olay gruplama, bastırma, Account Name + UPNSuffix ve IP Address entity mapping alanlarını ayrı ayrı kaydet. Saat dilimi, veri zaman aralığı ve sorgu metninin SHA-256'sı karşılaştırmanın parçasıdır.
4. Results simulation → Test with current data ile ürünün son 50 planlı çalıştırma grafiğini al. Ayar veya sorgu değişince yeniden çalıştır. Sorgu sonucu sayısını alarm ya da olay sayısıyla eşitleme; gruplama/bastırma etkisini ayrı incele. Gecikmiş alım ve sınırdaki kayıtları gerçek hizmet sonucuyla karşılaştır; yerel `(başlangıç,son]` varsayımı Microsoft'un sınır sözleşmesi diye sunulmaz.
5. Review and create ekranındaki doğrulama sonucunu kaydet; bu kabul için **Create'e basmak gerekmez**. Ekrandaki Validation passed ile kuralın dağıtılmış/çalışan olması farklı durumlardır. Yayım veya gerçek alarm kabulü ayrıca yetkilendirilmelidir.

Kabul kaydı: UTC zaman, tenant/workspace bağlamı (yetkili depoda), API/portal görünümü, query SHA-256, karşılaştırılan veri kapsamı, 50 çalıştırma önizlemesi, entity mapping, Review doğrulaması ve `yayinlandi=false`. Portal, veri eşitliği veya doğrulama görülmediyse her biri ayrı `bekliyor`/`karşılaştırılamadı` olmalı; hazırlanan ARM dosyası bu alanları kendi başına PASS yapmaz.

Kaynak: [Microsoft Scheduled Analytics oluşturma ve önizleme yordamı](https://learn.microsoft.com/en-us/azure/sentinel/detect-threats-custom).
:::
