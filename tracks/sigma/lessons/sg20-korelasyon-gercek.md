---
id: sg20
title: Korelasyon Kurallarını Gerçek Hedefte Çalıştırmak
summary: SG16'da anlatılan korelasyonu yazıp gerçekten çalıştırmak; temel kural ve korelasyonun aynı koleksiyonda --- ile birlikte yazılması, name ile başvuru; event_count ve value_count, group-by, timespan ve condition (gte, field); Splunk backend'inin korelasyonu bin _time + stats ile çevirmesi ve bunun kayan pencere değil sabit kutu olması: süreden kısa bir aralıktaki olayların kutu sınırına düştüğü için hiç alarm vermemesi. Gerçek pySigma Splunk backend'i ve gerçek Splunk.
---

::: anlat Temel kural ve korelasyon
SG16'da korelasyonun fikrini gördün: tek bir olay şüphedir, bir zaman penceresinde tekrarlayan olaylar kanıttır. Bir korelasyon kuralı iki parçadan oluşur ve ikisi aynı dosyada `---` ile ayrılır:

```sigma norun
title: Yeni hizmet kuruldu
name: yeni_hizmet
id: 6e2b1c4d-0000-4000-8000-000000007045
logsource: {product: windows, service: system}
detection:
  sel: {EventID: 7045}
  condition: sel
---
title: Kısa sürede çok sayıda hizmet kurulumu
id: 6e2b1c4d-0000-4000-8000-000000007046
correlation:
  type: event_count
  rules: [yeni_hizmet]
  group-by: [Computer]
  timespan: 10m
  condition: {gte: 3}
```

| Alan | Anlamı |
|---|---|
| `name` | temel kuralın adı; korelasyon ona `rules:` ile başvurur |
| `type: event_count` | penceredeki olay sayısı |
| `type: value_count` | penceredeki **farklı değer** sayısı (`condition: {field: ..., gte: ...}`) |
| `group-by` | her değer için ayrı sayaç (ör. her cihaz) |
| `timespan` | pencere uzunluğu |
| `condition` | eşik: `gte`, `gt`, `lte`, `lt`, `eq` |

Splunk backend'i bu kuralı şöyle çevirir (bu derste ölçüldü):

```text
source="WinEventLog:System" EventCode=7045
| bin _time span=10m
| stats count as event_count by _time Computer
| search event_count >= 3
```

> [!TUZAK] Pencere kaymaz, kutulara bölünür
> `bin _time span=10m` zamanı **sabit** on dakikalık kutulara böler: 09:00–09:10, 09:10–09:20... Bir sayaç her kutuda sıfırdan başlar. Üç olay 09:08, 09:09 ve 09:11'de olursa (üç dakika içinde!) ilk kutuda 2, ikincide 1 olay kalır ve kural **alarm vermez**. Bu, bu derste gerçek Splunk'ta ölçüldü. Kayan bir pencere isteyen bir kural için ya pencereyi gerçekte beklenen yayılımdan uzun seçersin ya da hedef SIEM'in kendi kayan pencere yeteneğine (Splunk'ta `streamstats time_window=`) geçersin.

> [!NOT] Laboratuvar
> Kod Sigma kural koleksiyonudur. Pafta onu gerçek pySigma Splunk backend'iyle (`splunk_windows` pipeline'ı: `service: system` → `source="WinEventLog:System"`, `EventID` → `EventCode`) çevirir ve gerçek Splunk laboratuvarında çalıştırır. Sonuç satırları `_time` (kutunun başı), grup alanı ve sayıdır.
:::

::: tahmin
Hazırlıktaki hizmet kurulumları: srv-dosya 09:01, 09:03, 09:05; srv-yedek 09:08, 09:09, 09:11; pc-can 09:20, 09:25. Yukarıdaki kural (10 dakika, en az 3) hangi cihazlarda alarm verir?

```sigma
title: Yeni hizmet kuruldu
name: yeni_hizmet
id: 6e2b1c4d-0000-4000-8000-000000007045
logsource: {product: windows, service: system}
detection:
  sel: {EventID: 7045}
  condition: sel
---
title: Kısa sürede çok sayıda hizmet kurulumu
id: 6e2b1c4d-0000-4000-8000-000000007046
correlation:
  type: event_count
  rules: [yeni_hizmet]
  group-by: [Computer]
  timespan: 10m
  condition: {gte: 3}
```

???

**Yalnız srv-dosya.**

```
2026-10-19T09:00:00.000+00:00|srv-dosya|3
```

srv-yedek'in üç kurulumu üç dakika içinde ama 09:10 sınırının iki yanına düştü: 09:00–09:10 kutusunda 2, 09:10–09:20 kutusunda 1. pc-can'ın iki kurulumu zaten eşiğin altında. Pencereyi 15 dakika yaparsan srv-yedek de 09:00–09:15 kutusuna düşer ve alarm verir.

```meta
motor: splunk
pipeline: splunk_windows
```

```setup
import json
props("pafta_winsys", {"INDEXED_EXTRACTIONS": "json", "KV_MODE": "none", "TIMESTAMP_FIELDS": "TimeCreated",
                       "TIME_FORMAT": "%Y-%m-%d %H:%M:%S"})
hizmet = [("srv-dosya", "09:01:00", "GuncelleyiciA"), ("srv-dosya", "09:03:00", "GuncelleyiciB"),
          ("srv-dosya", "09:05:00", "GuncelleyiciC"),
          ("srv-yedek", "09:08:00", "YedekA"), ("srv-yedek", "09:09:00", "YedekB"), ("srv-yedek", "09:11:00", "YedekC"),
          ("pc-can", "09:20:00", "YaziciSurucu"), ("pc-can", "09:25:00", "YaziciIzleyici")]
veri("".join(json.dumps({"TimeCreated": "2026-10-19 " + z, "EventCode": 7045, "Computer": c, "ServiceName": s,
                         "ImagePath": "C:\\Program Files\\Kurum\\" + s + ".exe"}) + "\n" for c, z, s in hizmet),
     "pafta_winsys", "WinEventLog:System")
```
:::

::: gorev 1 · Hizmet kurulumu fırtınası
Bir **cihazda** 10 dakikalık bir pencerede **en az 3** yeni hizmet kurulumu (Windows System günlüğü, olay kimliği 7045) olursa alarm üreten bir korelasyon yaz: bir temel kural (adı `yeni_hizmet`) ve ona başvuran bir `event_count` korelasyonu, aynı koleksiyonda.

```starter
title: Yeni hizmet kuruldu
id: 6e2b1c4d-0000-4000-8000-000000007045
logsource: {product: windows, service: system}
detection:
  sel: {EventID: 7045}
  condition: sel
```

```test
eq(sutunlar, ["_time", "Computer", "event_count"], "kutu zamanı, cihaz, sayı")
eq([(r[1], r[2]) for r in sonuc], [("srv-dosya", 3)], "10 dakikalık kutuda yalnız srv-dosya üç kuruluma ulaşıyor")
ok(kullanir("event_count") and kullanir("group-by"), "event_count ve group-by")
EK = ('import json\n'
      'ek = [("pc-test", "09:41:00", 7045), ("pc-test", "09:42:00", 7045), ("pc-test", "09:43:00", 7045),\n'
      '      ("pc-iki", "09:41:00", 7045), ("pc-iki", "09:42:00", 7045),\n'
      '      ("pc-baska", "09:41:00", 7036), ("pc-baska", "09:42:00", 7036), ("pc-baska", "09:43:00", 7036)]\n'
      'veri("".join(json.dumps({"TimeCreated": "2026-10-19 " + z, "EventCode": e, "Computer": c, "ServiceName": "s"}) + "\\n"\n'
      '             for c, z, e in ek), "pafta_winsys", "WinEventLog:System")\n')
eq(sorted((r[1], r[2]) for r in dene(EK)), [("pc-test", 3), ("srv-dosya", 3)],
   "tam 3 kurulum eşiğe dahil (gte); 2 kurulum yetmez; başka olay kimliği (7036) sayılmaz; cihazlar ayrı sayılır")
```

```solution
title: Yeni hizmet kuruldu
name: yeni_hizmet
id: 6e2b1c4d-0000-4000-8000-000000007045
logsource: {product: windows, service: system}
detection:
  sel: {EventID: 7045}
  condition: sel
---
title: Kısa sürede çok sayıda hizmet kurulumu
id: 6e2b1c4d-0000-4000-8000-000000007046
correlation:
  type: event_count
  rules: [yeni_hizmet]
  group-by: [Computer]
  timespan: 10m
  condition: {gte: 3}
```

```hint
Temel kurala `name: yeni_hizmet` ekle; sonra `---` ile ikinci bir belge başlat ve `correlation:` altında `type: event_count`, `rules: [yeni_hizmet]`, `group-by: [Computer]`, `timespan: 10m`, `condition: {gte: 3}` yaz. İkinci belgenin de kendi `title` ve `id`'si olmalı.
```

```meta
motor: splunk
pipeline: splunk_windows
```

```setup
import json
props("pafta_winsys", {"INDEXED_EXTRACTIONS": "json", "KV_MODE": "none", "TIMESTAMP_FIELDS": "TimeCreated",
                       "TIME_FORMAT": "%Y-%m-%d %H:%M:%S"})
hizmet = [("srv-dosya", "09:01:00", "GuncelleyiciA"), ("srv-dosya", "09:03:00", "GuncelleyiciB"),
          ("srv-dosya", "09:05:00", "GuncelleyiciC"),
          ("srv-yedek", "09:08:00", "YedekA"), ("srv-yedek", "09:09:00", "YedekB"), ("srv-yedek", "09:11:00", "YedekC"),
          ("pc-can", "09:20:00", "YaziciSurucu"), ("pc-can", "09:25:00", "YaziciIzleyici")]
veri("".join(json.dumps({"TimeCreated": "2026-10-19 " + z, "EventCode": 7045, "Computer": c, "ServiceName": s,
                         "ImagePath": "C:\\Program Files\\Kurum\\" + s + ".exe"}) + "\n" for c, z, s in hizmet),
     "pafta_winsys", "WinEventLog:System")
```
:::

::: gorev 2 · Kısa sürede çok sayıda farklı hedef
PowerShell'in (`Image` `\powershell.exe` ile biter) bir **cihazda** 5 dakikalık bir pencerede **en az 4 farklı** hedef adrese (`DestinationIp`) bağlanması şüphelidir: bir tarayıcı aynı sunucuya defalarca bağlanır, bir betik ise art arda farklı adresleri dener. Temel kural (Sysmon ağ bağlantısı, `category: network_connection`, adı `ps_baglanti`) ve bir `value_count` korelasyonu yaz.

```starter
title: PowerShell ağ bağlantısı
name: ps_baglanti
id: 7f3c2d5e-0000-4000-8000-000000000003
logsource: {product: windows, category: network_connection}
detection:
  sel: {Image|endswith: '\powershell.exe'}
  condition: sel
---
title: PowerShell kısa sürede çok sayıda bağlantı kuruyor
id: 7f3c2d5e-0000-4000-8000-000000000004
correlation:
  type: event_count
  rules: [ps_baglanti]
  group-by: [Computer]
  timespan: 5m
  condition: {gte: 4}
```

```test
eq(sutunlar, ["_time", "Computer", "value_count"], "kutu zamanı, cihaz, farklı değer sayısı")
eq([(r[1], r[2]) for r in sonuc], [("pc-ayse", 4)], "pc-ayse dört farklı adrese bağlandı; pc-can üçte kaldı")
EK = ('import json\n'
      'WPS = "C:\\\\Windows\\\\System32\\\\WindowsPowerShell\\\\v1.0\\\\powershell.exe"\n'
      'EDGE = "C:\\\\Program Files (x86)\\\\Microsoft\\\\Edge\\\\Application\\\\msedge.exe"\n'
      'ek = [("pc-can", WPS, "09:33:30", "198.51.100.23")]\n'
      'ek += [("pc-tekrar", WPS, "09:31:%02d" % (i * 10), "198.51.100.99") for i in range(6)]\n'
      'ek += [("pc-tarayici", EDGE, "09:31:%02d" % (i * 10), "198.51.100.%d" % (50 + i)) for i in range(5)]\n'
      'veri("".join(json.dumps({"UtcTime": "2026-10-19 " + z, "EventCode": 3, "Computer": c, "Image": im,\n'
      '                         "DestinationIp": d, "DestinationPort": 443}) + "\\n" for c, im, z, d in ek),\n'
      '     "pafta_sysmon", "WinEventLog:Microsoft-Windows-Sysmon/Operational")\n')
eq(sorted((r[1], r[2]) for r in dene(EK)), [("pc-ayse", 4), ("pc-can", 4)],
   "pc-can'ın dördüncü farklı hedefi eşiği doldurur; aynı adrese altı bağlantı sayılmaz; tarayıcının bağlantıları temel kurala girmez")
```

```solution
title: PowerShell ağ bağlantısı
name: ps_baglanti
id: 7f3c2d5e-0000-4000-8000-000000000003
logsource: {product: windows, category: network_connection}
detection:
  sel: {Image|endswith: '\powershell.exe'}
  condition: sel
---
title: PowerShell kısa sürede çok sayıda farklı hedefe bağlanıyor
id: 7f3c2d5e-0000-4000-8000-000000000004
correlation:
  type: value_count
  rules: [ps_baglanti]
  group-by: [Computer]
  timespan: 5m
  condition: {field: DestinationIp, gte: 4}
```

```hint
`event_count` her bağlantıyı sayar; aynı adrese altı bağlantı da eşiği aşar. Farklı adresleri saymak için `type: value_count` ve koşula sayılacak alanı yaz: `condition: {field: DestinationIp, gte: 4}`.
```

```meta
motor: splunk
pipeline: sysmon,splunk_windows
```

```setup
import json
props("pafta_sysmon", {"INDEXED_EXTRACTIONS": "json", "KV_MODE": "none", "TIMESTAMP_FIELDS": "UtcTime",
                       "TIME_FORMAT": "%Y-%m-%d %H:%M:%S"})
WPS = "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"
EDGE = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
baglanti = [("pc-ayse", WPS, "09:31:00", "198.51.100.10"), ("pc-ayse", WPS, "09:31:30", "198.51.100.11"),
            ("pc-ayse", WPS, "09:32:00", "198.51.100.12"), ("pc-ayse", WPS, "09:32:30", "198.51.100.13"),
            ("pc-mert", EDGE, "09:31:00", "203.0.113.5"), ("pc-mert", EDGE, "09:31:10", "203.0.113.5"),
            ("pc-mert", EDGE, "09:31:20", "203.0.113.5"), ("pc-mert", EDGE, "09:31:30", "203.0.113.5"),
            ("pc-mert", EDGE, "09:31:40", "203.0.113.5"),
            ("pc-can", WPS, "09:33:00", "198.51.100.20"), ("pc-can", WPS, "09:33:10", "198.51.100.21"),
            ("pc-can", WPS, "09:33:20", "198.51.100.22")]
veri("".join(json.dumps({"UtcTime": "2026-10-19 " + z, "EventCode": 3, "Computer": c, "Image": i,
                         "DestinationIp": d, "DestinationPort": 443}) + "\n" for c, i, z, d in baglanti),
     "pafta_sysmon", "WinEventLog:Microsoft-Windows-Sysmon/Operational")
```
:::
