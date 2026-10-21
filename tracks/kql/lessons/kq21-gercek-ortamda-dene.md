---
id: kq21
title: Gerçek Ortamda Dene · Azure Data Explorer
summary: Sorguları ücretsiz gerçek Kusto ortamlarına taşımak (Azure Data Explorer yardım kümesi, ücretsiz küme, Kusto.Explorer); veriyi datatable ile sorgunun içine koymak; tezgahla gerçek Kusto arasındaki farklar (sabit şimdi, tarih gösterimi, sıra garantisi, tablolar) ve iki sonucu karşılaştırmak.
---

::: anlat Ücretsiz gerçek Kusto
Pafta'nın KQL tezgahı bir Kusto motoru değildir: sorgular SQLite'a çevrilip yerel bir veritabanında çalışır. Bu derste aynı sorguları **gerçek ürüne** taşıyacaksın. Bunun için para ödemen ya da bir Azure aboneliği açman gerekmez:

| Ortam | Ne gerekir | Ne yapılır |
|---|---|---|
| Azure Data Explorer **yardım kümesi**: `https://dataexplorer.azure.com/clusters/help` | bir Microsoft hesabı | Microsoft'un örnek veritabanlarında (ör. `Samples` içindeki `StormEvents`) **salt okunur** sorgu. Kendi tablon olmaz; kendi verini `datatable` ile sorgunun içine koyarsın. |
| Azure Data Explorer **ücretsiz küme**: `https://aka.ms/kustofree` | bir Microsoft hesabı | kendi veritabanın ve tabloların; küçük örnek verileri yükleyebilirsin (boyut ve süre sınırları için sayfadaki güncel koşullara bak) |
| **Kusto.Explorer** (Windows masaüstü uygulaması) | ücretsiz indirme | aynı kümelere bağlanan, sorgu geçmişi ve sekmeleri olan masaüstü istemci |

Microsoft Sentinel ve Log Analytics de aynı dili konuşur. Ama tablo adları farklıdır (`SecurityEvent`, `SigninLogs` gibi) ve bazı yönetim komutları orada yoktur. Bu dersteki yöntem orada da işe yarar.

> [!GÜVENLİK]
> Yardım kümesi herkese açık örnek veri içindir. Kendi kurumunun kayıtlarını ya da kişisel veriyi `datatable` ile sorgu metnine kopyalama: sorgu metinleri hizmetin günlüklerinde kalabilir. Ücretsiz kümeye de yalnızca örnek ya da anonimleştirilmiş veri yükle.
:::

::: anlat Veriyi taşınabilir yapmak: datatable
Tezgahtaki `biletler`, `istekler` gibi tablolar gerçek kümede yoktur. Küçük bir örneği sorgunun içine `datatable` ile koyarsan aynı sorgu **iki yerde de** aynı veriyle çalışır (KQ08):

```kql
let ornek = datatable(zaman:datetime, sunucu:string, yol:string, durum:int, sure_ms:long)
[
    datetime(2026-10-19 09:01), "web01", "/api/rapor", 500, 2300,
    datetime(2026-10-19 09:02), "web01", "/api/rapor", 500, 2410,
    datetime(2026-10-19 09:12), "web02", "/api/rapor", 503, 30,
    datetime(2026-10-19 10:00), "web02", "/api/bilet", 200, 95,
];
ornek
| where durum >= 500
| summarize hata = count(), en_uzun = max(sure_ms) by sunucu
| sort by sunucu asc
```

Sütunların türü açıkça yazılır: `string`, `long`, `int`, `real`, `bool`, `datetime`, `timespan`, `dynamic`. Bu bloğu yardım kümesinin sorgu penceresine yapıştırıp çalıştır; sonucu tezgahınkiyle karşılaştır.

Daha büyük bir veriyle çalışmak istersen ücretsiz kümede bir tablo oluşturup veri yüklersin. Bunlar sorgu değil **yönetim komutlarıdır** (nokta ile başlar) ve tezgahta çalışmaz:

```kql norun
.create table istekler (zaman:datetime, sunucu:string, yol:string, durum:int, sure_ms:long)

.ingest inline into table istekler <|
2026-10-19 09:01,web01,/api/rapor,500,2300
2026-10-19 09:02,web01,/api/rapor,500,2410
```

`.ingest inline` küçük denemeler içindir; asıl veriyi kümenin arayüzündeki **Get data** sihirbazıyla bir CSV dosyasından yüklersin.
:::

::: anlat Farklara dikkat
Aynı sorgu iki yerde farklı görünüyorsa sebep çoğu zaman şunlardan biridir:

| Konu | Tezgah | Gerçek Kusto | Ne yap |
|---|---|---|---|
| şimdi | `now()` hep **2026-10-19 12:00** | gerçek saat (UTC) | `let simdi = datetime(2026-10-19 12:00);` ile sabitle; `ago(2h)` yerine `simdi - 2h` |
| tarih gösterimi | `2026-10-19 08:00` | `2026-10-19T08:00:00Z` | biçimi değil değeri karşılaştır |
| satır sırası | tablonun okunduğu sıra | `sort` yoksa **garanti değil** (sorgu dağıtık çalışır); `take` herhangi N satırı verir | sıra önemliyse `sort by` ya da `top`; eşitlikte ikinci bir anahtar ekle |
| tablolar | `biletler`, `istekler`... | yok | `datatable` ya da kendi tablon |
| `render` | tablo olarak gösterir | grafik çizer | |
| hatalar | Türkçe, tezgaha özgü | Kusto'nun mesajları; tezgahın desteklemediği bir işleç gerçekte geçerli olabilir | |

Karşılaştırırken satırları **küme** olarak karşılaştır (sırasız). Sırayı ancak sorguda `sort` ya da `top` varsa karşılaştır. Bir fark bulursan sorguyu, veriyi ve ürünün sürümünü yan yana kaydet. Tezgah bir Kusto taklididir; gerçek ürünle ayrıştığı yer bir öğrenme fırsatıdır, Pafta'ya da bir bulgu olarak bildirilebilir.
:::

::: tahmin
İki sorgu, iki sonuç. Ne yazar?

```kql
let olcum = datatable(sunucu:string, sure:long)
[
    "web01", 120,
    "web02", 300,
    "db01", 300,
    "cache01", 80,
];
olcum
| top 2 by sure desc, sunucu asc

let olcum = datatable(sunucu:string, sure:long)
[
    "web01", 120,
    "web02", 300,
    "db01", 300,
    "cache01", 80,
];
olcum
| where sure >= 120
| summarize toplam = sum(sure), adet = count()
```

???

İlk sorgu `db01|300` ve `web02|300`, ikincisi `720|3` verir. İki sunucunun süresi eşit (300); ikinci anahtar `sunucu asc` olduğu için önce `db01` gelir. İkinci anahtar olmasaydı gerçek Kusto bu iki satırı her seferinde aynı sırada vermek zorunda olmazdı; `top 1` ise bazen birini bazen ötekini getirebilirdi. İkinci sorguda `>=` 120'yi dahil eder: 120 + 300 + 300 = 720, üç satır.
:::

::: gorev Şimdiyi sabitle
Şimdi **2026-10-19 12:00** olsun. Son iki saatte (12:00 hariç) gelen istekleri sunucu başına say: `sunucu`, `istek`, sunucuya göre artan. `ago()` ve `now()` kullanma: sorgu gerçek Kusto'da da aynı sonucu vermeli.

```starter
istekler
| where zaman > ago(2h)
| summarize istek = count() by sunucu
```

```test
eq(sutunlar, ["sunucu", "istek"], "sütunlar: sunucu, istek")
eq(sonuc, [("web01", 4), ("web02", 4), ("web03", 3)], "10:00-12:00 arası")
ok(not kullanir("ago") and not kullanir("now"), "ago() ve now() kullanma; şimdiyi datetime ile sabitle")
ekle = ("INSERT INTO istekler (zaman, istemci, yontem, yol, durum, sure_ms, sunucu) VALUES "
        "('2026-10-19 10:00','10.9.9.9','GET','/x',200,1,'web09'), ('2026-10-19 12:00','10.9.9.9','GET','/x',200,1,'web08'), "
        "('2026-10-19 09:59','10.9.9.9','GET','/x',200,1,'web07');")
eq(dene(ekle), [("web01", 4), ("web02", 4), ("web03", 3), ("web09", 1)], "10:00 dahil; 09:59 ve 12:00 hariç")
```

```solution
let simdi = datetime(2026-10-19 12:00);
istekler
| where zaman >= simdi - 2h and zaman < simdi
| summarize istek = count() by sunucu
| sort by sunucu asc
```

```hint
`let simdi = datetime(2026-10-19 12:00);` yaz ve aralığı yarı açık kur: `zaman >= simdi - 2h and zaman < simdi`.
```
:::

::: gorev Eşitliği boz
En yavaş üç isteği getir: `zaman`, `sunucu`, `yol`, `sure_ms`. Süre azalan, süreler eşitse **önce olan** önde. Gerçek Kusto'da da her seferinde aynı üç satır gelmeli.

```starter
istekler
| take 3
| project zaman, sunucu, yol, sure_ms
```

```test
eq(sutunlar, ["zaman", "sunucu", "yol", "sure_ms"], "sütunlar")
eq([(z[11:16], s, y, d) for z, s, y, d in sonuc], [("10:42", "web02", "/api/rapor", 2600), ("09:02", "web01", "/api/rapor", 2410),
                                                   ("09:01", "web01", "/api/rapor", 2300)], "en yavaş üç istek")
ekle_once = ("INSERT INTO istekler (zaman, istemci, yontem, yol, durum, sure_ms, sunucu) VALUES "
             "('2026-10-19 08:30','10.9.9.9','GET','/esit-once',200,2300,'web09');")
eq(dene(ekle_once)[-1][2], "/esit-once", "2300'de eşitlik: 08:30'daki istek 09:01'dekinden önce gelir")
ekle_sonra = ("INSERT INTO istekler (zaman, istemci, yontem, yol, durum, sure_ms, sunucu) VALUES "
              "('2026-10-19 11:59','10.9.9.9','GET','/esit-sonra',200,2300,'web09');")
eq(dene(ekle_sonra)[-1][2], "/api/rapor", "2300'de eşitlik: 11:59'daki istek dışarıda kalır")
ok(not kullanir("take") and not kullanir("limit"), "take/limit sıra garantisi vermez; top ya da sort kullan")
```

```solution
istekler
| top 3 by sure_ms desc, zaman asc
| project zaman, sunucu, yol, sure_ms
```

```hint
`top 3 by sure_ms desc, zaman asc` iki anahtarla sıralar: önce süre, eşitse zaman.
```
:::

::: gorev Veriyi datatable ile taşı
Aşağıdaki beş olayı `olaylar` adında bir `datatable` olarak yaz (`zaman:datetime`, `sunucu:string`, `durum:int`). Sonra her sunucu için bütün olayları (`toplam`) ve durumu **500 ya da üstü** olanları (`hata`) say: `sunucu`, `toplam`, `hata`, sunucuya göre artan. Tezgahın tablolarını kullanma: sorgu yardım kümesinde aynen çalışmalı.

| zaman | sunucu | durum |
|---|---|---|
| 2026-10-19 08:00 | web01 | 500 |
| 2026-10-19 08:05 | web01 | 499 |
| 2026-10-19 08:10 | db01 | 503 |
| 2026-10-19 08:15 | db01 | 200 |
| 2026-10-19 08:20 | cache01 | 500 |

```starter
istekler
| where durum >= 500
| summarize hata = count() by sunucu
```

```test
eq(sutunlar, ["sunucu", "toplam", "hata"], "sütunlar: sunucu, toplam, hata")
eq(sonuc, [("cache01", 1, 1), ("db01", 2, 1), ("web01", 2, 1)], "beş olay doğru yazılmış; 500 dahil, 499 hariç")
ok(kullanir("datatable"), "datatable kullan")
ok(not kullanir("istekler") and not kullanir("biletler"), "tezgahın tablolarını kullanma")
```

```solution
let olaylar = datatable(zaman:datetime, sunucu:string, durum:int)
[
    datetime(2026-10-19 08:00), "web01", 500,
    datetime(2026-10-19 08:05), "web01", 499,
    datetime(2026-10-19 08:10), "db01", 503,
    datetime(2026-10-19 08:15), "db01", 200,
    datetime(2026-10-19 08:20), "cache01", 500,
];
olaylar
| summarize toplam = count(), hata = countif(durum >= 500) by sunucu
| sort by sunucu asc
```

```hint
`let olaylar = datatable(zaman:datetime, sunucu:string, durum:int) [ ... ];` köşeli parantezin içinde değerler satır satır, virgülle; tarih `datetime(...)`, metin tırnakla. İki sayımı tek `summarize`'da yap: `toplam = count(), hata = countif(durum >= 500)`.
```
:::
