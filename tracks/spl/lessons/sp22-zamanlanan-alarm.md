---
id: sp22
title: Aramadan Zamanlanan Alarma · Pencere, Eşik ve Bastırma
summary: Bir aramayı savedsearches.conf'ta zamanlanmış bir alarma çevirmek; cron_schedule ile dispatch.earliest_time ve dispatch.latest_time'ın birlikte bir pencere dizisi kurması (boşluk ve çakışma), pencerenin başının dahil sonunun hariç olması; counttype, relation ve quantity'nin olayları değil sonuç satırlarını sayması, eşiği aramanın içinde where ile kurmak; tek alarm (digest) ile sonuç başına alarm farkı, alert.suppress.period ve alert.suppress.fields ile bastırma; bastırmanın gerçek saatle sayılması. Görevler Docker'daki gerçek Splunk Enterprise'da çalışır.
kazanim: APU 4.1, APU 15.1
---

::: anlat Bir arama, bir takvim, bir koşul
SP16'da doğru bir arama yazmayı, SP21'de veriyi doğru almayı öğrendin. Bir SOC'ta o aramayı kimse elle çalıştırmaz: Splunk onu bir **takvime** göre kendisi çalıştırır ve sonuç bir **koşulu** sağlarsa alarm üretir. Böyle bir kural `savedsearches.conf`'ta bir kıtadır:

```ini
[pafta_hata_alarmi]
search = index=pafta_ders sourcetype=pafta_istek durum>=500 | stats count by sunucu | where count >= 3
cron_schedule = */15 * * * *
dispatch.earliest_time = -15m
dispatch.latest_time = now
counttype = number of events
relation = greater than
quantity = 0
alert.track = 1
alert.digest_mode = 0
```

| Ayar | Anlamı |
|---|---|
| `search` | kuralın araması |
| `cron_schedule` | ne zaman çalışacağı (dakika saat gün ay haftanın-günü); `*/15 * * * *` her çeyrek saat |
| `dispatch.earliest_time`, `dispatch.latest_time` | her çalıştırmanın penceresi, çalıştırma anına göre; `-15m` ile `now` son on beş dakika |
| `counttype`, `relation`, `quantity` | tetikleme koşulu: "sonuç sayısı 0'dan büyükse" |
| `alert.digest_mode` | `1`: bütün sonuçlar için **tek** alarm; `0`: **her sonuç satırı** için ayrı alarm |
| `alert.track` | tetiklenen alarmı **Triggered Alerts** listesinde tut |

Takvim ile pencere birlikte düşünülür. On beş dakikada bir çalışan kuralın penceresi on beş dakikaysa pencereler uç uca eklenir. Pencere daha kısaysa aradaki olaylar hiçbir çalıştırmada görülmez; daha uzunsa aynı olay iki çalıştırmada sayılır. KQ22'de aynı soruyu KQL ile canlandırmıştın; burada gerçek Splunk çalıştırıyor.

> [!TUZAK] counttype olayları değil sonuç satırlarını sayar
> `counttype = number of events`, aramanın **sonuç satırlarının** sayısıdır, ham olayların değil. `stats count by sunucu`'dan sonra bir satır bir sunucudur. "Bir sunucuda en az üç hata" koşulunu `quantity = 2` ile kurarsan "üçten fazla sunucuda hata" demiş olursun. Eşiği aramanın içine koy (`| where count >= 3`), koşulu "sonuç var mı" diye bırak.

> [!NOT] Bu paftanın laboratuvarı
> Yazdığın kıta gerçek Splunk'a kayıtlı arama olarak kurulur. Ama bir sabah boyunca beklememek için onu Splunk'ın zamanlayıcısı değil, laboratuvar çalıştırır: görevin zaman aralığında `cron_schedule`'ının denk geldiği her anı hesaplar ve kuralı Splunk'ın kendi çalıştırma kapısından (`dispatch.now` ile, alarm eylemleri açık) o anda çalışmış gibi çalıştırır. Laboratuvar takvimin yalnız dakika ve saat alanlarını yorumlar. Splunk geçmiş tarihli çalıştırmaların bastırma kayıtlarını arka planda hemen temizleyebildiği için laboratuvar bu sabahı veriyle birlikte tam gün kaydırıp yarına taşır; çıktıda dersin tarihleri görünür. Her çalıştırma bir satırdır:
>
> `kural | calisma | pencere_bas | pencere_son | sonuc | tetiklenen | bastirilan | teslim`
>
> `sonuc`: aramanın satır sayısı. `tetiklenen`: üretilen alarm sayısı. `bastirilan`: bastırılan sonuç sayısı. `teslim`: alarmla teslim edilen satırlar (alan değerleri `:` ile). Alarm, bastırma ve sayılar Splunk'ın kendi zamanlayıcı ve denetim günlüklerinden okunur.
:::

::: gorev 1 · Sunucu başına üç hata
`pafta_istek` kaynağında her satır bir istek: `durum` ve `sunucu` alanları var. `[pafta_hata_alarmi]` kuralını yaz:

- **On beş dakikada bir** çalışsın; pencereler ne boşluk bıraksın ne çakışsın.
- Bir pencerede durumu 500 ya da üstü olan **en az üç** isteği olan her sunucu için **ayrı** bir alarm üretsin. Teslim edilen satır `sunucu` ve `count` alanlarını taşısın (`stats count by sunucu`).

Görev kuralı 09:00'dan 10:30'a kadar çalıştırıyor.

```starter
[pafta_hata_alarmi]
search = index=pafta_ders sourcetype=pafta_istek durum>=500 | stats count by sunucu
cron_schedule = */15 * * * *
dispatch.earliest_time = -30m
dispatch.latest_time = now
counttype = number of events
relation = greater than
quantity = 2
alert.track = 1
alert.digest_mode = 1
```

```test
eq(sutunlar, ["kural", "calisma", "pencere_bas", "pencere_son", "sonuc", "tetiklenen", "bastirilan", "teslim"], "sütunlar")
eq([(r[1], r[2], r[3]) for r in sonuc],
   [("2026-10-19 09:00", "2026-10-19 08:45", "2026-10-19 09:00"), ("2026-10-19 09:15", "2026-10-19 09:00", "2026-10-19 09:15"),
    ("2026-10-19 09:30", "2026-10-19 09:15", "2026-10-19 09:30"), ("2026-10-19 09:45", "2026-10-19 09:30", "2026-10-19 09:45"),
    ("2026-10-19 10:00", "2026-10-19 09:45", "2026-10-19 10:00"), ("2026-10-19 10:15", "2026-10-19 10:00", "2026-10-19 10:15"),
    ("2026-10-19 10:30", "2026-10-19 10:15", "2026-10-19 10:30")],
   "yedi çalıştırma, uç uca on beşer dakikalık pencereler")
eq([(r[1][11:], r[5], r[7]) for r in sonuc if r[5]],
   [("09:15", 1, "web01:3"), ("09:30", 1, "web02:3"), ("10:00", 1, "web03:3"), ("10:15", 1, "web01:4")],
   "09:14'teki web02 hatası 09:15 penceresinde, 09:15'teki 09:30 penceresinde: başı dahil, sonu hariç")
EK = 'veri("2026-10-19 10:16 durum=500 sunucu=web04\\n2026-10-19 10:17 durum=500 sunucu=web04\\n2026-10-19 10:18 durum=500 sunucu=web05\\n2026-10-19 10:19 durum=500 sunucu=web05\\n2026-10-19 10:20 durum=500 sunucu=web05\\n2026-10-19 10:21 durum=499 sunucu=web05\\n2026-10-19 10:22 durum=500 sunucu=web07\\n2026-10-19 10:23 durum=504 sunucu=web07\\n2026-10-19 10:24 durum=500 sunucu=web07\\n", "pafta_istek")'
son = dene(EK)[-1]
eq((son[1], son[4], son[5], son[7]), ("2026-10-19 10:30", 2, 2, "web05:3, web07:3"),
   "iki hata eşiğin altında, 499 hata sayılmaz; tam üç hata alarm; aynı pencerede iki sunucu iki ayrı alarm")
```

```solution
[pafta_hata_alarmi]
search = index=pafta_ders sourcetype=pafta_istek durum>=500 | stats count by sunucu | where count >= 3
cron_schedule = */15 * * * *
dispatch.earliest_time = -15m
dispatch.latest_time = now
counttype = number of events
relation = greater than
quantity = 0
alert.track = 1
alert.digest_mode = 0
```

```hint
Pencere takvimle aynı uzunlukta olmalı: `dispatch.earliest_time = -15m`. `-30m` her olayı iki çalıştırmada sayar.
```

```hint
`quantity = 2` "ikiden fazla sonuç satırı" demektir; bir satır bir sunucu. Eşiği aramaya koy (`| where count >= 3`), koşulu `relation = greater than`, `quantity = 0` yap. Her sunucuya ayrı alarm için `alert.digest_mode = 0`.
```

```meta
motor: splunk
girdi: alarm
```

```setup
props("pafta_istek", {"SHOULD_LINEMERGE": "false", "TIME_PREFIX": "^", "TIME_FORMAT": "%Y-%m-%d %H:%M",
                      "MAX_TIMESTAMP_LOOKAHEAD": "16"})
veri("""2026-10-19 09:01 durum=500 sunucu=web01
2026-10-19 09:04 durum=500 sunucu=web01
2026-10-19 09:09 durum=503 sunucu=web01
2026-10-19 09:14 durum=500 sunucu=web02
2026-10-19 09:15 durum=500 sunucu=web02
2026-10-19 09:20 durum=502 sunucu=web02
2026-10-19 09:29 durum=500 sunucu=web02
2026-10-19 09:31 durum=200 sunucu=web01
2026-10-19 09:44 durum=500 sunucu=web01
2026-10-19 09:52 durum=500 sunucu=web03
2026-10-19 09:53 durum=500 sunucu=web03
2026-10-19 09:58 durum=500 sunucu=web03
2026-10-19 10:10 durum=500 sunucu=web01
2026-10-19 10:12 durum=500 sunucu=web01
2026-10-19 10:13 durum=500 sunucu=web01
2026-10-19 10:14 durum=500 sunucu=web01
""", "pafta_istek", "istek.log")
aralik("2026-10-19 09:00", "2026-10-19 10:30")
```
:::

::: anlat Bastırma
Bir sunucu yarım saat boyunca hata verirse sonuç başına bir kural her çalıştırmada yeniden alarm üretir; nöbetçinin önüne aynı olay için on alarm düşer. **Bastırma** (throttling), bir alarmdan sonra belirli bir süre aynı alarmı yeniden üretmemektir:

```ini
alert.suppress = 1
alert.suppress.period = 3h
alert.suppress.fields = sunucu
```

- `alert.suppress.period`: alarmdan sonra ne kadar süre susulacağı.
- `alert.suppress.fields`: bastırmanın hangi alanın **değerine** göre yapılacağı. `sunucu` verilirse web01'in alarmı yalnız web01'i susturur; web02 hâlâ alarm üretebilir. Tek alarm modunda alan verilmezse alarmın tamamı susar (aşağıdaki tahmin). Sonuç başına modda alan vermezsen Splunk bastırma anahtarını kendisi seçer; bu laboratuvarda `sunucu` vermişsin gibi davrandı, ama bu belgelenmiş bir sözleşme değil. Hangi alana göre susturulacağını her zaman açıkça yaz.

Bastırılan sonuç teslim edilmez; zamanlayıcı günlüğüne `suppressed` olarak yazılır.

> [!TUZAK] Bastırma gerçek saatle sayılır
> Splunk bastırma süresini çalıştırmanın **gerçek** saatine göre sayar. Bu laboratuvar bir sabahın çalıştırmalarını birkaç saniye içinde yapar; yani gerçek saatle bastırma süresi bu derste dolmaz. Bu yüzden görevlerde süre, canlandırılan aralığın tamamını (09:00–10:30) kapsayacak kadar uzun seçildi; böylece laboratuvar ile gerçek kural aynı sonucu verir. Sürenin dolmasını aşağıdaki ikinci tahminde gerçek saniyelerle göreceksin.
:::

::: tahmin
Gorev 1'deki kural bu kez **tek alarm** modunda ve alan vermeden üç saat bastırıyor. 09:15'te web01, 09:30'da web02, 10:00'da web03, 10:15'te yeniden web01 eşiği aşıyor. Kaç alarm üretilir?

```spl
[pafta_hata_alarmi]
search = index=pafta_ders sourcetype=pafta_istek durum>=500 | stats count by sunucu | where count >= 3
cron_schedule = */15 * * * *
dispatch.earliest_time = -15m
dispatch.latest_time = now
counttype = number of events
relation = greater than
quantity = 0
alert.track = 1
alert.digest_mode = 1
alert.suppress = 1
alert.suppress.period = 3h
```

???

**Tek alarm, 09:15'te.**

```
pafta_hata_alarmi|2026-10-19 09:00|2026-10-19 08:45|2026-10-19 09:00|0|0|0|
pafta_hata_alarmi|2026-10-19 09:15|2026-10-19 09:00|2026-10-19 09:15|1|1|0|web01:3
pafta_hata_alarmi|2026-10-19 09:30|2026-10-19 09:15|2026-10-19 09:30|1|0|1|
pafta_hata_alarmi|2026-10-19 09:45|2026-10-19 09:30|2026-10-19 09:45|0|0|0|
pafta_hata_alarmi|2026-10-19 10:00|2026-10-19 09:45|2026-10-19 10:00|1|0|1|
pafta_hata_alarmi|2026-10-19 10:15|2026-10-19 10:00|2026-10-19 10:15|1|0|1|
pafta_hata_alarmi|2026-10-19 10:30|2026-10-19 10:15|2026-10-19 10:30|0|0|0|
```

`alert.suppress.fields` verilmediği için bastırma kuralın **tamamını** susturdu: 09:30'da web02, 10:00'da web03 eşiği aştı ama ikisi de 09:15'teki web01 alarmının gölgesinde kaldı. Bir kuralı gürültüden korurken başka sunuculardaki yeni olayları da gizlemiş olursun.

```meta
motor: splunk
girdi: alarm
```

```setup
props("pafta_istek", {"SHOULD_LINEMERGE": "false", "TIME_PREFIX": "^", "TIME_FORMAT": "%Y-%m-%d %H:%M",
                      "MAX_TIMESTAMP_LOOKAHEAD": "16"})
veri("""2026-10-19 09:01 durum=500 sunucu=web01
2026-10-19 09:04 durum=500 sunucu=web01
2026-10-19 09:09 durum=503 sunucu=web01
2026-10-19 09:14 durum=500 sunucu=web02
2026-10-19 09:15 durum=500 sunucu=web02
2026-10-19 09:20 durum=502 sunucu=web02
2026-10-19 09:29 durum=500 sunucu=web02
2026-10-19 09:31 durum=200 sunucu=web01
2026-10-19 09:44 durum=500 sunucu=web01
2026-10-19 09:52 durum=500 sunucu=web03
2026-10-19 09:53 durum=500 sunucu=web03
2026-10-19 09:58 durum=500 sunucu=web03
2026-10-19 10:10 durum=500 sunucu=web01
2026-10-19 10:12 durum=500 sunucu=web01
2026-10-19 10:13 durum=500 sunucu=web01
2026-10-19 10:14 durum=500 sunucu=web01
""", "pafta_istek", "istek.log")
aralik("2026-10-19 09:00", "2026-10-19 10:30")
```
:::

::: gorev 2 · Sunucu başına bastırma
Gorev 1'in kuralına bastırma ekle: bir sunucu alarm ürettikten sonra **üç saat** boyunca **aynı sunucu** için yeniden alarm üretilmesin; başka sunucuların alarmları etkilenmesin. Her sunucu yine ayrı alarm.

```starter
[pafta_hata_alarmi]
search = index=pafta_ders sourcetype=pafta_istek durum>=500 | stats count by sunucu | where count >= 3
cron_schedule = */15 * * * *
dispatch.earliest_time = -15m
dispatch.latest_time = now
counttype = number of events
relation = greater than
quantity = 0
alert.track = 1
alert.digest_mode = 0
```

```test
eq([(r[1][11:], r[4], r[5], r[6], r[7]) for r in sonuc if r[4]],
   [("09:15", 1, 1, 0, "web01:3"), ("09:30", 1, 1, 0, "web02:3"), ("10:00", 1, 1, 0, "web03:3"),
    ("10:15", 1, 0, 1, "")],
   "web02 ve web03 kendi alarmlarını üretir; 10:15'te web01 bastırılır")
EK = 'veri("2026-10-19 10:01 durum=500 sunucu=web02\\n2026-10-19 10:02 durum=500 sunucu=web02\\n2026-10-19 10:03 durum=500 sunucu=web02\\n2026-10-19 10:04 durum=500 sunucu=web06\\n2026-10-19 10:05 durum=500 sunucu=web06\\n2026-10-19 10:06 durum=500 sunucu=web06\\n", "pafta_istek")'
satir = [r for r in dene(EK) if r[1] == "2026-10-19 10:15"][0]
eq((satir[4], satir[5], satir[6], satir[7]), (3, 1, 2, "web06:3"),
   "aynı pencerede web01 ve web02 bastırılır, ilk kez görülen web06 alarm üretir")
```

```solution
[pafta_hata_alarmi]
search = index=pafta_ders sourcetype=pafta_istek durum>=500 | stats count by sunucu | where count >= 3
cron_schedule = */15 * * * *
dispatch.earliest_time = -15m
dispatch.latest_time = now
counttype = number of events
relation = greater than
quantity = 0
alert.track = 1
alert.digest_mode = 0
alert.suppress = 1
alert.suppress.period = 3h
alert.suppress.fields = sunucu
```

```hint
Üç satır ekle: `alert.suppress = 1`, `alert.suppress.period = 3h` ve bastırmayı sunucunun değerine bağlayan `alert.suppress.fields = sunucu`.
```

```meta
motor: splunk
girdi: alarm
```

```setup
props("pafta_istek", {"SHOULD_LINEMERGE": "false", "TIME_PREFIX": "^", "TIME_FORMAT": "%Y-%m-%d %H:%M",
                      "MAX_TIMESTAMP_LOOKAHEAD": "16"})
veri("""2026-10-19 09:01 durum=500 sunucu=web01
2026-10-19 09:04 durum=500 sunucu=web01
2026-10-19 09:09 durum=503 sunucu=web01
2026-10-19 09:14 durum=500 sunucu=web02
2026-10-19 09:15 durum=500 sunucu=web02
2026-10-19 09:20 durum=502 sunucu=web02
2026-10-19 09:29 durum=500 sunucu=web02
2026-10-19 09:31 durum=200 sunucu=web01
2026-10-19 09:44 durum=500 sunucu=web01
2026-10-19 09:52 durum=500 sunucu=web03
2026-10-19 09:53 durum=500 sunucu=web03
2026-10-19 09:58 durum=500 sunucu=web03
2026-10-19 10:10 durum=500 sunucu=web01
2026-10-19 10:12 durum=500 sunucu=web01
2026-10-19 10:13 durum=500 sunucu=web01
2026-10-19 10:14 durum=500 sunucu=web01
""", "pafta_istek", "istek.log")
aralik("2026-10-19 09:00", "2026-10-19 10:30")
```
:::

::: tahmin
Bastırma süresinin dolmasını görmek için bu adımda laboratuvar üç çalıştırmayı **gerçekten 12 saniye arayla** yapıyor; bastırma süresi **20 saniye**. web01 her üç pencerede de eşiği aşıyor. Hangi çalıştırmalar alarm üretir?

```spl
[pafta_hata_alarmi]
search = index=pafta_ders sourcetype=pafta_istek durum>=500 | stats count by sunucu | where count >= 3
cron_schedule = */15 * * * *
dispatch.earliest_time = -15m
dispatch.latest_time = now
counttype = number of events
relation = greater than
quantity = 0
alert.track = 1
alert.digest_mode = 0
alert.suppress = 1
alert.suppress.period = 20s
alert.suppress.fields = sunucu
```

???

**Birinci ve üçüncü.**

```
pafta_hata_alarmi|2026-10-19 10:15|2026-10-19 10:00|2026-10-19 10:15|1|1|0|web01:3
pafta_hata_alarmi|2026-10-19 10:30|2026-10-19 10:15|2026-10-19 10:30|1|0|1|
pafta_hata_alarmi|2026-10-19 10:45|2026-10-19 10:30|2026-10-19 10:45|1|1|0|web01:3
```

İkinci çalıştırma ilk alarmdan 12 saniye sonra: bastırma sürüyor. Üçüncüsü 24 saniye sonra: 20 saniye dolmuş, web01 yeniden alarm üretir. Pencere zamanları (`10:15`, `10:30`) bastırmayı etkilemedi; Splunk süreyi çalıştırmanın gerçek saatiyle saydı. Gerçek bir kuralda süre, olayın nöbetçi tarafından ele alınması için gereken zaman kadar seçilir: kısa süre gürültüyü geri getirir, uzun süre aynı sunucudaki yeni bir olayı gizler.

```meta
motor: splunk
girdi: alarm
```

```setup
props("pafta_istek", {"SHOULD_LINEMERGE": "false", "TIME_PREFIX": "^", "TIME_FORMAT": "%Y-%m-%d %H:%M",
                      "MAX_TIMESTAMP_LOOKAHEAD": "16"})
veri("""2026-10-19 10:01 durum=500 sunucu=web01
2026-10-19 10:02 durum=500 sunucu=web01
2026-10-19 10:03 durum=500 sunucu=web01
2026-10-19 10:16 durum=500 sunucu=web01
2026-10-19 10:17 durum=500 sunucu=web01
2026-10-19 10:18 durum=500 sunucu=web01
2026-10-19 10:31 durum=500 sunucu=web01
2026-10-19 10:32 durum=500 sunucu=web01
2026-10-19 10:33 durum=500 sunucu=web01
""", "pafta_istek", "istek.log")
calistir("2026-10-19 10:15", "2026-10-19 10:30", "2026-10-19 10:45", ara=12)
```
:::
