---
id: sp21
title: Gerçek Splunk'a Veri Almak · Olay Sınırı ve Zaman
summary: Ham bir günlük dosyasının olaylara dönüşmesi; props.conf'ta SHOULD_LINEMERGE, LINE_BREAKER, TIME_PREFIX, TIME_FORMAT, MAX_TIMESTAMP_LOOKAHEAD ve TZ; varsayılan satır birleştirmenin devam satırındaki bir tarihte olayı bölmesi, zaman damgası olmayan satırın önceki olayın zamanını alması, milisaniyenin kaybolması, otomatik zaman tanımanın satırdaki yanlış tarihi yakalaması; bu ayarların dizine alma anında uygulandığı. Görevler Docker'daki gerçek Splunk Enterprise'da çalışır.
kazanim: APU 15.1, APU 15.2
---

::: anlat Dosyadan olaya
Şimdiye kadarki paftalarda veri hazırdı: her satır bir olaydı, `_time` doğruydu. Gerçek bir Splunk'ta bunu sen kurarsın. Bir günlük dosyası Splunk'a ham bir metin akışı olarak gelir; Splunk onu **dizine alırken** iki karar verir:

1. **Olay sınırı:** Akış nerede bölünüp ayrı olaylara ayrılacak? Bir Python hata izi (traceback) beş satırdır ama tek bir olaydır.
2. **Zaman:** Her olayın `_time`'ı metnin neresinden, hangi biçimde ve hangi saat diliminde okunacak?

Bu kararlar sourcetype başına **props.conf** dosyasında verilir:

```ini
[pafta_uygulama]
SHOULD_LINEMERGE = false
LINE_BREAKER = ([\r\n]+)(?=\d{4}-\d{2}-\d{2} \d{2}:)
TIME_PREFIX = ^
TIME_FORMAT = %Y-%m-%d %H:%M:%S,%3N
MAX_TIMESTAMP_LOOKAHEAD = 23
TZ = Europe/Istanbul
```

| Ayar | Anlamı |
|---|---|
| `[pafta_uygulama]` | kıta: bu ayarlar hangi sourcetype'ın |
| `SHOULD_LINEMERGE` | önce satırlara bölüp sonra satırları "tarih görünce yeni olay" kuralıyla birleştir (`true`, varsayılan) ya da yalnız `LINE_BREAKER`'a güven (`false`) |
| `LINE_BREAKER` | akışı nerede böleceğin düzenli ifadesi; **ilk yakalama grubu** iki olay arasındaki ayırıcıdır ve atılır |
| `TIME_PREFIX` | zaman damgasından hemen önce gelen metnin düzenli ifadesi; `^` satır başı |
| `TIME_FORMAT` | damganın `strptime` biçimi; `%3N` milisaniye |
| `MAX_TIMESTAMP_LOOKAHEAD` | `TIME_PREFIX`'ten sonra damgayı en çok kaç karakter içinde arayacağı |
| `TZ` | damga saat dilimi taşımıyorsa hangi dilimde okunacağı |

`(?=...)` bir **ileriye bakış**tır: "ardından bir tarih geliyorsa" der ama tarihi tüketmez; tarih yeni olayın başında kalır. İfade yalnız satır sonu karakterlerinden sonra bir tarih ararsa, satırın **ortasındaki** bir tarih olayı bölmez.

> [!TUZAK] Bu ayarlar dizine alma anındadır
> props.conf'taki olay sınırı ve zaman ayarları veri **dizine alınırken** uygulanır. Ayarı sonradan düzeltirsen dizindeki olaylar değişmez; yalnız yeni gelen veri yeni ayarla bölünür. Yanlış alınmış veriyi düzeltmenin yolu onu silip yeniden almaktır. Bu yüzden yeni bir kaynağı önce bir deneme dizinine al, olayları gözünle kontrol et, sonra asıl dizine yönlendir.

> [!NOT] Bu paftanın laboratuvarı
> Görevler tezgahta değil, bilgisayarındaki Docker'da çalışan **gerçek Splunk Enterprise**'da çalışır (ilk açılış birkaç dakika sürebilir; Docker Desktop açık olmalı). Yazdığın props.conf kıtası Splunk'a uygulanır, görevin günlük dosyası bu ayarla `pafta_ders` dizinine alınır ve sonuç olarak her olayın `zaman` (UTC), `sourcetype` ve `_raw` değeri gösterilir. Gerçek bir kurulumda bu dosya dizinleyicide ya da ağır yönlendiricide bir uygulamanın `local/props.conf` dosyasına yazılır.
:::

::: tahmin
Bir erişim günlüğünün satırları şöyle:

```text
[web01] istek=7f3a gun=2025-12-31 t=19.10.2026 09:01:12 durum=500
[web02] istek=7f3b gun=2025-12-31 t=19.10.2026 09:05:40 durum=200
```

Kıtada hiçbir ayar yok; Splunk zamanı kendisi tanıyacak. `zaman` sütununda ne görürsün?

```spl
[pafta_erisim]
```

???

**`2025-12-31 09:01:12.000` ve `2025-12-31 09:05:40.000`:**

```
2025-12-31 09:01:12.000|pafta_erisim|[web01] istek=7f3a gun=2025-12-31 t=19.10.2026 09:01:12 durum=500
2025-12-31 09:05:40.000|pafta_erisim|[web02] istek=7f3b gun=2025-12-31 t=19.10.2026 09:05:40 durum=200
```

Splunk'ın otomatik zaman tanıması satırda gördüğü ilk tarih benzeri metni yakaladı: `gun=2025-12-31`. Saati ise ondan sonra gelen `09:01:12`'den aldı. Sonuç iki parçadan birleşmiş, gerçekte hiç olmamış bir an. Bir hata yok, bir uyarı yok; olaylar yalnız yanlış güne düşer ve "son 24 saat" aramasında hiç görünmez. Damganın yerini `TIME_PREFIX` ile, biçimini `TIME_FORMAT` ile söylemek bu yüzden gereklidir.

```meta
motor: splunk
girdi: props
```

```setup
veri("""[web01] istek=7f3a gun=2025-12-31 t=19.10.2026 09:01:12 durum=500
[web02] istek=7f3b gun=2025-12-31 t=19.10.2026 09:05:40 durum=200
""", "pafta_erisim", "erisim.log")
```
:::

::: gorev 1 · Hata izini tek olay yap
Uygulamanın günlüğü (`uygulama.log`) her olaya `2026-10-19 09:01:12,345` biçiminde bir zaman damgasıyla başlıyor; bazı olayların altında girintili devam satırları var. `[pafta_uygulama]` kıtasını yaz:

- Her olay **satır başındaki** bir zaman damgasıyla başlasın; devam satırları (hata izi, `hedef=`, `son deneme ...`) kendi olaylarında kalsın. Satır birleştirmeyi kapat, sınırı `LINE_BREAKER` ile ver.
- `_time` satır başındaki damgadan **milisaniyesiyle** okunsun. Damga UTC.

Başlangıç kıtası yalnız satır birleştirmeyi kapatıyor: her satır ayrı bir olay oluyor ve damgası olmayan satırlar bir önceki olayın zamanını alıyor.

```starter
[pafta_uygulama]
SHOULD_LINEMERGE = false
```

```test
eq(len(sonuc), 5, "beş olay: hata izi, devam satırları ve 'son deneme' satırındaki tarih yeni olay başlatmaz")
eq([r[0] for r in sonuc], ["2026-10-19 09:01:12.345", "2026-10-19 09:02:00.001", "2026-10-19 09:02:00.950",
                           "2026-10-19 09:03:30.000", "2026-10-19 09:04:00.000"], "zamanlar milisaniyesiyle")
satirlar = [len(r[2].strip().split("\n")) for r in sonuc]
eq(satirlar, [4, 1, 1, 3, 1], "satır sayıları: hata izi 4, bağlantı hatası 3 satır")
ok(sonuc[3][2].strip().endswith("son deneme 2026-10-19 09:03:35 basarisiz"),
   "satırın ortasındaki tarih olayı bölmez")
EK = ("2026-10-19 09:06:00,900 INFO ikinci\n"
      "2026-10-19 09:06:00,100 INFO birinci\n"
      "    2026-10-19 09:07:00,000 girintili satir\n")
yeni = dene("veri(%r, 'pafta_uygulama', 'uygulama2.log')" % EK)
eq([(r[0], r[2].strip().split("\n")[0][24:]) for r in yeni[5:]],
   [("2026-10-19 09:06:00.100", "INFO birinci"), ("2026-10-19 09:06:00.900", "INFO ikinci")],
   "aynı saniyedeki iki olay milisaniyeyle sıralanır; girintiyle başlayan tarihli satır yeni olay değildir")
```

```solution
[pafta_uygulama]
SHOULD_LINEMERGE = false
LINE_BREAKER = ([\r\n]+)(?=\d{4}-\d{2}-\d{2} \d{2}:)
TIME_PREFIX = ^
TIME_FORMAT = %Y-%m-%d %H:%M:%S,%3N
MAX_TIMESTAMP_LOOKAHEAD = 23
TZ = UTC
```

```hint
`LINE_BREAKER = ([\r\n]+)(?=\d{4}-\d{2}-\d{2} \d{2}:)`: satır sonu karakterleri ayırıcıdır (atılır), ardından bir tarih ve saat geliyorsa orada yeni olay başlar. İleriye bakışın içine boşluk ya da başka bir şey koyma: girintili satırdaki tarih de yeni olay başlatır.
```

```hint
Zaman için `TIME_PREFIX = ^`, `TIME_FORMAT = %Y-%m-%d %H:%M:%S,%3N`. `%3N` yazılmazsa aynı saniyedeki olaylar `.000` olur ve sıraları kaybolur. `2026-10-19 09:01:12,345` 23 karakterdir: `MAX_TIMESTAMP_LOOKAHEAD = 23`.
```

```meta
motor: splunk
girdi: props
```

```setup
veri("""2026-10-19 09:01:12,345 ERROR rapor uretilemedi
Traceback (most recent call last):
  File "rapor.py", line 10, in uret
ValueError: bos sablon
2026-10-19 09:02:00,001 INFO istek tamam sure=120
2026-10-19 09:02:00,950 WARN yavas istek sure=2300
2026-10-19 09:03:30,000 ERROR baglanti koptu
  hedef=db01:5432
  son deneme 2026-10-19 09:03:35 basarisiz
2026-10-19 09:04:00,000 INFO yeniden baglandi
""", "pafta_uygulama", "uygulama.log")
```
:::

::: anlat Varsayılanlar neden yetmez
Kıtayı boş bıraksaydın Splunk varsayılanlarla çalışırdı: satırlara böl (`LINE_BREAKER = ([\r\n]+)`), sonra `SHOULD_LINEMERGE = true` ile **tarih içeren her satırdan önce** yeni olay başlat. Bu, gorev 1'in günlüğünde neredeyse doğru sonuç verir; tek fark `  son deneme 2026-10-19 09:03:35 basarisiz` satırıdır. O satır bir tarih taşıdığı için kendi olayı olur ve zamanı `09:03:35` sayılır. Bu derste ölçüldü: boş kıtayla altı olay çıktı.

Satır birleştirme ayrıca yavaştır: Splunk önce her satırı ayrı ele alıp sonra yeniden birleştirir. Büyük kurulumlarda bu yüzden yeni her sourcetype için olay sınırı ve zaman ayarlarının hep birlikte yazılması önerilir: `SHOULD_LINEMERGE = false` ile bir `LINE_BREAKER`, `TIME_PREFIX`, `TIME_FORMAT`, `MAX_TIMESTAMP_LOOKAHEAD`; ayrıca olay boyu sınırı `TRUNCATE` (varsayılan 10000 bayt). Böylece Splunk tahmin etmez, söyleneni yapar.

Zaman damgası saat dilimi taşımıyorsa Splunk onu **dizinleyicinin** saat diliminde okur. Bu laboratuvarın Splunk'ı UTC'de çalışıyor; İstanbul'da yazılmış `09:01` damgası `TZ` verilmezse `09:01 UTC` sayılır, yani gerçekte olduğundan üç saat sonraya düşer.
:::

::: gorev 2 · Damganın yeri ve saat dilimi
Erişim günlüğü (`erisim.log`) İstanbul'daki sunuculardan geliyor; damgalar yerel saatte ve dilim bilgisi taşımıyor. Her satırda başka tarihler de var. `[pafta_erisim]` kıtasını yaz:

- Her satır bir olay.
- `_time`, ` t=` alanındaki `19.10.2026 09:01:12` biçimli damgadan, **İstanbul saatiyle** okunsun. Sonuç UTC gösterildiği için `09:01:12` damgası `06:01:12` görünmeli.

```starter
[pafta_erisim]
SHOULD_LINEMERGE = false
TIME_FORMAT = %d.%m.%Y %H:%M:%S
```

```test
eq(len(sonuc), 3, "üç satır, üç olay")
eq([r[0] for r in sonuc], ["2026-10-19 06:01:12.000", "2026-10-19 06:05:40.000", "2026-10-19 07:00:00.000"],
   "damga t= alanından, İstanbul saati (UTC+3) olarak")
EK = "[web04] istek=7f3d ext=01.01.2026 00:00:00 t=19.10.2026 10:30:00 durum=200\n"
yeni = dene("veri(%r, 'pafta_erisim', 'erisim2.log')" % EK)
eq(yeni[-1][0], "2026-10-19 07:30:00.000",
   "ext= alanındaki damga yakalanmaz: önek t= alanının başını, önündeki boşlukla birlikte tarif etmeli")
```

```solution
[pafta_erisim]
SHOULD_LINEMERGE = false
LINE_BREAKER = ([\r\n]+)
TIME_PREFIX = \st=
TIME_FORMAT = %d.%m.%Y %H:%M:%S
MAX_TIMESTAMP_LOOKAHEAD = 19
TZ = Europe/Istanbul
```

```hint
`TIME_FORMAT` tek başına yetmez: Splunk damgayı yine satırın başından aramaya başlar ve önce `gun=2025-12-31`'e takılır. `TIME_PREFIX` ile damganın önündeki metni söyle.
```

```hint
`TIME_PREFIX = t=` yazarsan `ext=` içindeki `t=` de eşleşir. Önündeki boşluğu da iste: `TIME_PREFIX = \st=`. Saat dilimi için `TZ = Europe/Istanbul`.
```

```meta
motor: splunk
girdi: props
```

```setup
veri("""[web01] istek=7f3a gun=2025-12-31 t=19.10.2026 09:01:12 durum=500
[web02] istek=7f3b gun=2025-12-31 t=19.10.2026 09:05:40 durum=200
[web03] istek=7f3c gun=2026-01-15 t=19.10.2026 10:00:00 durum=404
""", "pafta_erisim", "erisim.log")
```
:::
