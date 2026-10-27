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

::: anlat Gerçek EVTX/XML'den Sigma'ya: normalleştirme senin işin
Şimdiye kadarki olaylar Sigma'ya hazır JSON'du. Sahada kanıt çoğunlukla bir **EVTX** dosyası ya da Windows'un ondan ürettiği **XML**'dir. PS27'de `Get-WinEvent -Path` ile okuduğun dosyanın aynısı. Bu görevde laboratuvar sentetik 4688 kayıtlarını Windows'un kendi aracıyla gerçek EVTX'e çevirir (`wevtutil epl`). Sonra Windows'un işlediği XML'i (`wevtutil qe /f:xml`) çalışma klasörüne `guvenlik.xml` olarak yazar. Canlı bir günlük okunmaz.

Bu XML'in üç özelliği normalleştiriciyi belirler:

| Özellik | Bu dosyada | Neden önemli |
|---|---|---|
| `EventData/Data` | **adsız**, sırayla | Eski EVT'den çevrilen kayıtta `Name` özniteliği yoktur. PS27'deki `Properties[n]` erişiminin aynısı. Alan adlarını Microsoft'un 4688 belgesindeki sıradan sen verirsin: `SubjectUserSid`, `SubjectUserName`, … `NewProcessName` (6.), … `CommandLine` (9.), … `ParentProcessName` (14.), `MandatoryLabel` (15.). |
| Boş `<Data></Data>` | mert'in kaydında `CommandLine` | "Include command line in process creation events" ilkesi kapalıyken alan boştur. Boşu atlarsan sonraki bütün alanlar bir sola kayar. |
| XML kaçışı | `&amp;`, `&lt;` | Metni regex'le değil bir XML ayrıştırıcısıyla oku; `ElementTree` kaçışı çözer. |

Sigma tarafı da bir sözleşmedir. `windows-audit` pipeline'ı `process_creation` kuralını Security 4688 alanlarına çevirir (`Image → NewProcessName`, `ParentImage → ParentProcessName`). `splunk_windows` de `EventID`'yi Splunk Windows eklentisinin adıyla `EventCode` yapar ve `source="WinEventLog:Security"` koşulunu ekler. Normalleştirdiğin olayda alan adı `EventID` kalırsa kural hata vermeden **susar**. Bu dersin baştaki "sessiz kural" nedenlerinin gerçek örneğidir.

> [!NOT] Laboratuvar
> Kod bir Python fonksiyonudur: `normalle(xml) -> list[dict]`. Test onun çıktısını gerçek Splunk'a `WinEventLog:Security` kaynağıyla yükler ve hazırlıktaki kuralı gerçek pySigma Splunk backend'iyle (`windows-audit` + `splunk_windows`) çevirip çalıştırır. Sınır: EVT'den gelen kayıtlar sürüm 0'dır ve `Name` taşımaz. Modern bir 4688 kaydında `Data Name="NewProcessName"` bulunur. İyi bir normalleştirici ikisini de okur, ama bu görev yalnız adsız biçimi sınar.

Kaynak: [4688 olay XML'i ve alan sırası](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4688).
:::

::: gorev 3 · Windows'un XML'ini Sigma'ya hazırla
Çalışma klasöründeki `guvenlik.xml`, `<Events>` kökü altında altı adet 4688 olayı içeriyor. `normalle(xml)` fonksiyonunu yaz. Fonksiyon her olay için bir sözlük döndürsün:

- `EventCode`: olay kimliği, **tamsayı**;
- `TimeCreated`: `SystemTime` özniteliği, olduğu gibi;
- `Computer`;
- 15 `EventData` alanı, 4688 belgesindeki sırayla adlandırılmış (adlar `from sigma_evtx_lab import ALANLAR_4688` ile gelir). Boş alan `""` olsun.

Olayların sırası dosyadaki sıra olsun. Test çıktını gerçek Splunk'a yükleyip "Office'ten başlatılan kodlanmış PowerShell" kuralını çalıştırır.

```meta
motor: python
timeout: 120
```

```setup
import os, sys
_s = os.path.dirname(next(m.__file__ for m in list(sys.modules.values())
                          if getattr(m, "__file__", None) and os.path.basename(m.__file__) == "py_harness.py"))
sys.path.insert(0, _s)
import sigma_evtx_lab
sigma_evtx_lab.ornek(".")
```

```starter
import re

def normalle(xml):
    olaylar = []
    for parca in xml.split("<Event ")[1:]:
        o = {"EventID": int(re.search(r"<EventID[^>]*>(\d+)<", parca).group(1))}
        for ad, deger in re.findall(r"<Data Name='(\w+)'>([^<]*)</Data>", parca):
            o[ad] = deger
        olaylar.append(o)
    return olaylar
```

```test
import sigma_evtx_lab as L
need("normalle")
xml = open("guvenlik.xml", encoding="utf-8").read()
n = normalle(xml)
eq(len(n), 6, "altı 4688 olayı")
eq([sorted(o) for o in n], [sorted(["EventCode", "TimeCreated", "Computer", *L.ALANLAR_4688])] * 6, "her olayda aynı 18 alan")
eq([o["EventCode"] for o in n], [4688] * 6, "EventCode tamsayı; splunk_windows EventID'yi EventCode'a çevirir")
eq([o["TimeCreated"] for o in n][:2], ["2026-01-01T09:00:05.0000000Z", "2026-01-01T09:00:12.0000000Z"], "SystemTime olduğu gibi, dosya sırasıyla")
eq({o["Computer"] for o in n}, {"PAFTA-LAB"}, "Computer System bölümünden")
eq([o["SubjectUserName"] for o in n], ["ayse", "berk", "can", "zeynep", "mert", "ece"], "2. Data alanı")
eq(n[4]["CommandLine"], "", "boş Data yerini korur")
eq((n[4]["TargetLogonId"], n[4]["ParentProcessName"], n[4]["MandatoryLabel"]),
   ("0x0", L.WORD, "S-1-16-8192"), "boş komut satırından sonraki alanlar kaymaz")
eq(n[5]["CommandLine"], "cmd.exe /c echo a & b <x> -enc", "XML kaçışı çözülür")
tek = xml.replace("ayse", "ayse2", 1).split("</Event>")[0] + "</Event></Events>"
eq([o["SubjectUserName"] for o in normalle(tek)], ["ayse2"], "dosyaya değil verilen XML metnine bakar")
spl, sutun, satir = L.splunkta(n)
eq(sorted(r[sutun.index("SubjectUserName")] for r in satir), ["ayse", "zeynep"],
   "gerçek Splunk: Word/Excel'den kodlanmış PowerShell; mert'in boş komut satırı kör nokta, can'ın üst süreci Explorer")
```

```solution
import xml.etree.ElementTree as ET
from sigma_evtx_lab import ALANLAR_4688

NS = {"e": "http://schemas.microsoft.com/win/2004/08/events/event"}

def normalle(xml):
    olaylar = []
    for olay in ET.fromstring(xml).findall("e:Event", NS):
        sistem = olay.find("e:System", NS)
        degerler = [d.text or "" for d in olay.findall("e:EventData/e:Data", NS)]
        o = {"EventCode": int(sistem.find("e:EventID", NS).text),
             "TimeCreated": sistem.find("e:TimeCreated", NS).get("SystemTime"),
             "Computer": sistem.find("e:Computer", NS).text}
        o.update(zip(ALANLAR_4688, degerler))
        olaylar.append(o)
    return olaylar
```

```hint
Başlangıç `Data Name='...'` arıyor; bu dosyada `Name` yok, bu yüzden hiçbir alan bulunmuyor. `xml.etree.ElementTree` ile `<Events>` kökünü ayrıştır. Olaylar `http://schemas.microsoft.com/win/2004/08/events/event` ad alanındadır: `findall("e:Event", NS)`.
```

```hint
`[d.text or "" for d in olay.findall("e:EventData/e:Data", NS)]` boş `Data`'yı `""` yapar ve sırayı korur; sonra `zip(ALANLAR_4688, degerler)`. Olay kimliğinin anahtarı `EventCode` olmalı, değeri `int(...)`.
```
:::
