---
id: sg21
title: Telemetri Doğrulaması · Kural Sessizse Veri mi Yok, Alan mı?
summary: Bir kuralın sessiz kalmasının üç nedeni: kanal toplanmıyor, olay var ama alanlar çıkarılmıyor, alan toplama ayarı yüzünden hiç yazılmıyor; Splunk'ın varsayılan source::WinEventLog kıtasının KV_MODE=none ile JSON alanlarını arama zamanında gizlemesi ve INDEXED_EXTRACTIONS; Sysmon (Image, ParentImage) ile Security 4688 (NewProcessName, ParentProcessName) alanları; 4688'de CommandLine'ın yalnız denetim ilkesi açıksa yazılması ve bunu exists: false ile bulan bir tanık kuralı. Gerçek pySigma Splunk backend'i ve gerçek Splunk.
---

::: anlat Sessiz kural iyi haber değildir
Bir tespit kuralı haftalardır alarm vermiyorsa iki olasılık vardır: saldırı yoktur ya da kural **göremiyordur**. SG03'te bir kuralın bir telemetri sözleşmesine dayandığını görmüştün. Gerçek bir SIEM'de sözleşme üç yerden bozulur:

| Arıza | Ne olur | Nasıl anlaşılır |
|---|---|---|
| **Kanal toplanmıyor** | Sysmon kurulmamış, Security günlüğü yönlendirilmiyor: olay hiç yok | o kaynak ve olay kimliği için sayım: `source=... EventCode=... \| stats count by host` |
| **Olay var, alan çıkmıyor** | ham olay dizinde, ama arama alanları görmüyor | aynı olayın `_raw`'ında alan var, aramada yok |
| **Alan toplanmıyor** | toplama ayarı alanı hiç yazdırmıyor | olay var, alan yok: `NOT alan=*` |

> [!TUZAK] Splunk'ın kendi WinEventLog kıtası (bu derste ölçüldü)
> Windows olaylarını JSON olarak `source="WinEventLog:Security"` adıyla aldın ve sourcetype'a `KV_MODE = json` yazdın. Kural yine de **sıfır** sonuç verir. Splunk'ın sistem ayarlarında `[source::WinEventLog...]` diye bir kıta vardır ve orada `KV_MODE = none` yazar; kaynak kıtası sourcetype kıtasından önce geldiği için JSON alanları **arama zamanında hiç çıkarılmaz**. Olaylar dizindedir, `_raw`'da her şey görünür, ama `EventCode=4688` hiçbir şeyle eşleşmez. Çözümlerden biri alanları **dizine alırken** çıkarmaktır: `INDEXED_EXTRACTIONS = json`.

Aynı davranış farklı kanallarda farklı adlarla yazılır:

| Bilgi | Sysmon (olay 1) | Security (olay 4688) |
|---|---|---|
| Başlayan süreç | `Image` | `NewProcessName` |
| Başlatan süreç | `ParentImage` | `ParentProcessName` |
| Komut satırı | `CommandLine` (hep) | `CommandLine` (**yalnız** "Include command line in process creation events" ilkesi açıksa) |

Sysmon için yazılmış bir kural, Sysmon'u olmayan bir ortamda hiçbir şey yakalamaz. 4688'e uyarlanmış bir kural da komut satırı denetimi kapalı makinelerde komut satırına bakan her koşulda kör kalır.

> [!NOT] Laboratuvar
> Olaylar Windows olaylarının alanlarıyla (EventData adları) JSON'a çevrilmiş sentetik kayıtlardır; gerçek bir EVTX dosyası değildir. Kurallar gerçek pySigma Splunk backend'iyle (`splunk_windows` pipeline'ı: `service: security` → `source="WinEventLog:Security"`) çevrilir ve gerçek Splunk'ta çalışır.
:::

::: tahmin
Hazırlıkta dört 4688 olayı `source="WinEventLog:Security"` adıyla dizine alındı; sourcetype'ta `KV_MODE = json` var. Bu kural kaç satır döndürür?

```sigma
title: Süreç oluşturma olayları
id: 8a1b2c3d-0000-4000-8000-000000004688
logsource: {product: windows, service: security}
detection:
  sel: {EventID: 4688}
  condition: sel
fields: [Computer]
```

???

**Hiç satır.**

Üretilen SPL doğru: `source="WinEventLog:Security" EventCode=4688 | table Computer`. Olaylar da dizinde. Ama Splunk'ın `[source::WinEventLog...]` kıtasındaki `KV_MODE = none`, sourcetype'taki `KV_MODE = json`'ı geçersiz kılar; `EventCode` alanı arama zamanında hiç oluşmaz. Aynı olaylar `INDEXED_EXTRACTIONS = json` ile alınsaydı kural dört satır döndürürdü. Bir kuralı devreye almadan önce, yakalaması gereken bir olayla sınamanın nedeni budur.

```meta
motor: splunk
pipeline: splunk_windows
```

```setup
import json
props("pafta_winsec", {"KV_MODE": "json", "SHOULD_LINEMERGE": "false", "TIME_PREFIX": '"TimeCreated": "',
                       "TIME_FORMAT": "%Y-%m-%d %H:%M:%S", "MAX_TIMESTAMP_LOOKAHEAD": "19"})
WPS = "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"
WORD = "C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE"
olaylar = [
    {"TimeCreated": "2026-10-19 09:01:00", "EventCode": 4688, "Computer": "pc-ayse", "SubjectUserName": "ayse",
     "NewProcessName": WPS, "ParentProcessName": WORD, "CommandLine": "powershell.exe -nop -enc SQBFAFgA"},
    {"TimeCreated": "2026-10-19 09:02:00", "EventCode": 4688, "Computer": "pc-can", "SubjectUserName": "can",
     "NewProcessName": WPS, "ParentProcessName": "C:\\Windows\\explorer.exe", "CommandLine": "powershell.exe -File yedek.ps1"},
    {"TimeCreated": "2026-10-19 09:03:00", "EventCode": 4688, "Computer": "pc-eski", "SubjectUserName": "mert",
     "NewProcessName": WPS, "ParentProcessName": WORD},
    {"TimeCreated": "2026-10-19 09:04:00", "EventCode": 4688, "Computer": "pc-eski", "SubjectUserName": "mert",
     "NewProcessName": "C:\\Windows\\System32\\notepad.exe", "ParentProcessName": "C:\\Windows\\explorer.exe"},
    {"TimeCreated": "2026-10-19 09:05:00", "EventCode": 4624, "Computer": "pc-yeni", "SubjectUserName": "zeynep"},
]
veri("".join(json.dumps(o) + "\n" for o in olaylar), "pafta_winsec", "WinEventLog:Security")
```
:::

::: gorev 1 · Sysmon kuralını 4688'e uyarla
Kurumda Sysmon yok; süreç olayları yalnız Security günlüğünden (olay 4688) geliyor. Başlangıç kuralı Sysmon alan adlarıyla yazılmış ve hiçbir şey yakalamıyor. Aynı tespiti 4688'in alanlarıyla yaz: başlayan süreç `\powershell.exe` ile biter, başlatan süreç `\winword.exe` ya da `\excel.exe` ile biter, komut satırı ` -enc ` içerir. `fields: [Computer, CommandLine]`.

```starter
title: Office'ten kodlanmış PowerShell
id: 8a1b2c3d-0000-4000-8000-000000004690
logsource: {product: windows, service: security}
detection:
  sel:
    EventID: 4688
    Image|endswith: '\powershell.exe'
    ParentImage|endswith: ['\winword.exe', '\excel.exe']
    CommandLine|contains: ' -enc '
  condition: sel
fields: [Computer, CommandLine]
```

```test
eq(sutunlar, ["Computer", "CommandLine"], "sütunlar")
eq(sonuc, [("pc-ayse", "powershell.exe -nop -enc SQBFAFgA")],
   "yalnız pc-ayse; pc-eski'de de Word'den PowerShell var ama komut satırı toplanmıyor, bu kural onu göremez")
EK = ('import json\n'
      'WPS = "C:\\\\Windows\\\\System32\\\\WindowsPowerShell\\\\v1.0\\\\powershell.exe"\n'
      'ek = [{"TimeCreated": "2026-10-19 09:20:00", "EventCode": 4688, "Computer": "pc-x", "NewProcessName": WPS,\n'
      '       "ParentProcessName": "C:\\\\Office\\\\EXCEL.EXE", "CommandLine": "powershell -ENC AAA"},\n'
      '      {"TimeCreated": "2026-10-19 09:21:00", "EventCode": 4688, "Computer": "pc-y", "NewProcessName": WPS,\n'
      '       "ParentProcessName": "C:\\\\Windows\\\\explorer.exe", "CommandLine": "powershell -enc AAA"}]\n'
      'veri("".join(json.dumps(o) + "\\n" for o in ek), "pafta_winsec", "WinEventLog:Security")\n')
eq(sorted(r[0] for r in dene(EK)), ["pc-ayse", "pc-x"], "Excel ve büyük harfli -ENC yakalanır; Explorer'dan başlayan değil")
```

```solution
title: Office'ten kodlanmış PowerShell
id: 8a1b2c3d-0000-4000-8000-000000004690
logsource: {product: windows, service: security}
detection:
  sel:
    EventID: 4688
    NewProcessName|endswith: '\powershell.exe'
    ParentProcessName|endswith: ['\winword.exe', '\excel.exe']
    CommandLine|contains: ' -enc '
  condition: sel
fields: [Computer, CommandLine]
```

```hint
4688'de başlayan sürecin alanı `NewProcessName`, başlatanınki `ParentProcessName`. `CommandLine` aynı adı taşır.
```

```meta
motor: splunk
pipeline: splunk_windows
```

```setup
import json
props("pafta_winsec", {"INDEXED_EXTRACTIONS": "json", "KV_MODE": "none", "TIMESTAMP_FIELDS": "TimeCreated",
                       "TIME_FORMAT": "%Y-%m-%d %H:%M:%S"})
WPS = "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"
WORD = "C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE"
olaylar = [
    {"TimeCreated": "2026-10-19 09:01:00", "EventCode": 4688, "Computer": "pc-ayse", "SubjectUserName": "ayse",
     "NewProcessName": WPS, "ParentProcessName": WORD, "CommandLine": "powershell.exe -nop -enc SQBFAFgA"},
    {"TimeCreated": "2026-10-19 09:02:00", "EventCode": 4688, "Computer": "pc-can", "SubjectUserName": "can",
     "NewProcessName": WPS, "ParentProcessName": "C:\\Windows\\explorer.exe", "CommandLine": "powershell.exe -File yedek.ps1"},
    {"TimeCreated": "2026-10-19 09:03:00", "EventCode": 4688, "Computer": "pc-eski", "SubjectUserName": "mert",
     "NewProcessName": WPS, "ParentProcessName": WORD},
    {"TimeCreated": "2026-10-19 09:04:00", "EventCode": 4688, "Computer": "pc-eski", "SubjectUserName": "mert",
     "NewProcessName": "C:\\Windows\\System32\\notepad.exe", "ParentProcessName": "C:\\Windows\\explorer.exe"},
    {"TimeCreated": "2026-10-19 09:05:00", "EventCode": 4624, "Computer": "pc-yeni", "SubjectUserName": "zeynep"},
]
veri("".join(json.dumps(o) + "\n" for o in olaylar), "pafta_winsec", "WinEventLog:Security")
```
:::

::: gorev 2 · Kör noktayı bulan tanık kuralı
Görev 1'in kuralı pc-eski'deki olayı göremedi, çünkü orada komut satırı yazılmıyor. Böyle makineleri bulan bir **telemetri tanığı** yaz: `CommandLine` alanı **olmayan** 4688 olayları. `fields: [Computer, NewProcessName]`. Bu kural bir saldırıyı değil, bir **toplama açığını** bulur.

```starter
title: Komut satırı denetimi kapalı
id: 8a1b2c3d-0000-4000-8000-000000004689
logsource: {product: windows, service: security}
detection:
  sel: {EventID: 4688}
  condition: sel
fields: [Computer, NewProcessName]
```

```test
eq(sutunlar, ["Computer", "NewProcessName"], "sütunlar")
eq(sorted(r[0] for r in sonuc), ["pc-eski", "pc-eski"], "pc-eski'nin iki 4688 olayında komut satırı yok")
ok(any("NOT CommandLine=*" in q for q in spl), "alan yokluğu: NOT CommandLine=*")
EK = ('import json\n'
      'ek = [{"TimeCreated": "2026-10-19 09:30:00", "EventCode": 4688, "Computer": "srv-yeni", "NewProcessName": "C:\\\\a.exe"},\n'
      '      {"TimeCreated": "2026-10-19 09:31:00", "EventCode": 4688, "Computer": "srv-bos", "NewProcessName": "C:\\\\b.exe", "CommandLine": ""},\n'
      '      {"TimeCreated": "2026-10-19 09:32:00", "EventCode": 4624, "Computer": "srv-giris"}]\n'
      'veri("".join(json.dumps(o) + "\\n" for o in ek), "pafta_winsec", "WinEventLog:Security")\n')
eq(sorted(set(r[0] for r in dene(EK))), ["pc-eski", "srv-yeni"],
   "yeni bir kör makine çıkar; boş komut satırı alan sayılır; 4688 olmayan olay (4624) sayılmaz")
```

```solution
title: Komut satırı denetimi kapalı
id: 8a1b2c3d-0000-4000-8000-000000004689
logsource: {product: windows, service: security}
detection:
  sel: {EventID: 4688}
  filtre: {CommandLine|exists: true}
  condition: sel and not filtre
fields: [Computer, NewProcessName]
```

```hint
Alanın varlığı `exists` değiştiricisiyle sorulur: bir seçim `filtre: {CommandLine|exists: true}`, koşul `sel and not filtre`. Splunk'ta bu `NOT CommandLine=*` olur.
```

```meta
motor: splunk
pipeline: splunk_windows
```

```setup
import json
props("pafta_winsec", {"INDEXED_EXTRACTIONS": "json", "KV_MODE": "none", "TIMESTAMP_FIELDS": "TimeCreated",
                       "TIME_FORMAT": "%Y-%m-%d %H:%M:%S"})
WPS = "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"
WORD = "C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE"
olaylar = [
    {"TimeCreated": "2026-10-19 09:01:00", "EventCode": 4688, "Computer": "pc-ayse", "SubjectUserName": "ayse",
     "NewProcessName": WPS, "ParentProcessName": WORD, "CommandLine": "powershell.exe -nop -enc SQBFAFgA"},
    {"TimeCreated": "2026-10-19 09:02:00", "EventCode": 4688, "Computer": "pc-can", "SubjectUserName": "can",
     "NewProcessName": WPS, "ParentProcessName": "C:\\Windows\\explorer.exe", "CommandLine": "powershell.exe -File yedek.ps1"},
    {"TimeCreated": "2026-10-19 09:03:00", "EventCode": 4688, "Computer": "pc-eski", "SubjectUserName": "mert",
     "NewProcessName": WPS, "ParentProcessName": WORD},
    {"TimeCreated": "2026-10-19 09:04:00", "EventCode": 4688, "Computer": "pc-eski", "SubjectUserName": "mert",
     "NewProcessName": "C:\\Windows\\System32\\notepad.exe", "ParentProcessName": "C:\\Windows\\explorer.exe"},
    {"TimeCreated": "2026-10-19 09:05:00", "EventCode": 4624, "Computer": "pc-yeni", "SubjectUserName": "zeynep"},
]
veri("".join(json.dumps(o) + "\n" for o in olaylar), "pafta_winsec", "WinEventLog:Security")
```
:::
