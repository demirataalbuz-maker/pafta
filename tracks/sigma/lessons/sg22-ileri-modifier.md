---
id: sg22
title: İleri Modifier'lar Gerçek Hedefte · base64offset, wide, windash, cidr, fieldref
summary: SG15'te adı geçen ileri değiştiricilerin gerçek Splunk backend'inde neye dönüştüğü ve gerçek Splunk'ta nasıl davrandığı; PowerShell -enc yükünün UTF-16LE base64 olması ve yalnız base64offset'in onu kaçırması, wide|base64offset; windash ile /enc ve tire benzeri karakterler; cidr ile iç ağ dışı bağlantılar; fieldref'in Splunk'ta harfe duyarlı where'e dönüşmesi; cased'in bu backend'de desteklenmemesi. Gerçek pySigma Splunk backend'i ve gerçek Splunk.
---

::: anlat Değiştirici bir söz verir, backend tutar mı?
Bir değiştirici kuralın **ne** aradığını söyler; **nasıl** aranacağını backend belirler. Aynı kural bir SIEM'de doğru, ötekinde eksik çalışabilir. Bu derste her değiştiricinin Splunk backend'inde ürettiği SPL ölçüldü:

| Değiştirici | Splunk'ta (ölçüldü) |
|---|---|
| `\|base64offset\|contains: 'IEX'` | `CommandLine="*SUVY*" OR CommandLine="*lFW*" OR CommandLine="*JRV*"` |
| `\|wide\|base64offset\|contains: 'IEX'` | `CommandLine="*SQBFAFgA*" OR CommandLine="*kARQBYA*" OR CommandLine="*JAEUAWA*"` |
| `\|windash\|contains: ' -enc '` | `-`, `/`, `–` (en dash), `—` (em dash), `―` için beş seçenek |
| `\|cidr: '10.0.0.0/8'` | `DestinationIp="10.0.0.0/8"` (Splunk bunu ağ olarak eşler) |
| `\|re: 'ab+c'` | `\| regex CommandLine="ab+c"` |
| `\|fieldref: ParentUser` | `\| where 'User'='ParentUser'` |
| `\|cased` | **desteklenmiyor**: çeviri `NotImplementedError` verir |

**Neden üç seçenek?** Base64 üç baytı dört karaktere çevirir. Aranan metin kodlanmış verinin içinde hangi konumda başlarsa (0, 1 ya da 2 bayt kaydırmayla) farklı karakterlere dönüşür. `base64offset` üç olasılığı da arar.

> [!TUZAK] PowerShell'in -enc yükü UTF-16LE'dir
> `powershell -EncodedCommand` (kısaca `-enc`) komutu UTF-8 değil **UTF-16LE** metnin base64'üdür: her harfin ardından bir sıfır baytı gelir. Yalnız `base64offset` UTF-8 kodlamayı varsayar ve gerçek PowerShell yüklerini **kaçırır**. `wide` önce metni UTF-16LE'ye çevirir; doğru zincir `|wide|base64offset|contains`. Bu derste ölçüldü: aynı işaret metni için yalnız `base64offset` yalnız UTF-8 kodlanmış tek olayı buldu, `wide|base64offset` gerçek üç PowerShell yükünü buldu.

> [!NOT] Laboratuvar
> İşaret metni zararsızdır (`Write-Output 'pafta egitim'`). Gerçek kural depolarında aynı teknik kodlanmış komutların içinde `IEX` ya da indirme komutları aramak için kullanılır. Kurallar gerçek pySigma Splunk backend'iyle (`sysmon`, `splunk_windows` pipeline'ları) çevrilir ve gerçek Splunk'ta çalışır.
:::

::: tahmin
Sigma'da dize karşılaştırmaları büyük-küçük harfe **duyarsızdır**. Bu kural, sürecin kullanıcısı (`User`) başlatan sürecin kullanıcısından (`ParentUser`) farklı olan olayları arar. pc-mert'te `User` `PAFTA\mert`, `ParentUser` `pafta\MERT`; pc-zeynep'te `User` `PAFTA\zeynep`, `ParentUser` `NT AUTHORITY\SYSTEM`. Kaç satır gelir?

```sigma
title: Süreç başka bir kullanıcı adına başladı
id: 9b1c2d3e-0000-4000-8000-000000000023
logsource: {product: windows, category: process_creation}
detection:
  sel: {EventID: 1}
  ayni: {User|fieldref: ParentUser}
  condition: sel and not ayni
fields: [Computer, User, ParentUser]
```

???

**İki satır; pc-mert de.**

```
pc-zeynep|PAFTA\zeynep|NT AUTHORITY\SYSTEM
pc-mert|PAFTA\mert|pafta\MERT
```

`fieldref` Splunk'ta `| where 'User'='ParentUser'` olur ve Splunk'ın `where`'i **harfe duyarlıdır**: `PAFTA\mert` ile `pafta\MERT` farklı sayıldı. Sigma'nın anlamına göre bunlar aynı kullanıcıdır; pc-mert bir yanlış alarmdır. Bir değiştiricinin anlamını backend'in koruyup korumadığını hedefte, harf büyüklüğü farklı bir örnekle sınamadan bilemezsin.

```meta
motor: splunk
pipeline: sysmon,splunk_windows
```

```setup
import json
props("pafta_sysmon", {"INDEXED_EXTRACTIONS": "json", "KV_MODE": "none", "TIMESTAMP_FIELDS": "UtcTime",
                       "TIME_FORMAT": "%Y-%m-%d %H:%M:%S"})
WPS = "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"
ISARET = "VwByAGkAdABlAC0ATwB1AHQAcAB1AHQAIAAnAHAAYQBmAHQAYQAgAGUAZwBpAHQAaQBtACcA"      # Write-Output 'pafta egitim'
BASKA = "RwBlAHQALQBEAGEAdABlADsAIABXAHIAaQB0AGUALQBPAHUAdABwAHUAdAAgACcAdABhAG0AYQBtACcA"   # Get-Date; Write-Output 'tamam'
TARIH = "RwBlAHQALQBEAGEAdABlAA=="                                                            # Get-Date
ASCII = "V3JpdGUtT3V0cHV0ICdwYWZ0YSBlZ2l0aW0n"                                                # Write-Output (UTF-8)
surec = [
    ("09:01:00", "pc-ayse", "powershell.exe -nop -enc " + ISARET, "PAFTA\\ayse", "PAFTA\\ayse"),
    ("09:02:00", "pc-can", "powershell.exe /enc " + BASKA, "PAFTA\\can", "PAFTA\\can"),
    ("09:03:00", "pc-mert", "powershell.exe \u2013enc " + ISARET, "PAFTA\\mert", "pafta\\MERT"),
    ("09:04:00", "pc-zeynep", "powershell.exe -enc " + TARIH, "PAFTA\\zeynep", "NT AUTHORITY\\SYSTEM"),
    ("09:05:00", "pc-ali", "powershell.exe -enc " + ASCII, "PAFTA\\ali", "PAFTA\\ali"),
]
ag = [("09:10:00", "pc-ayse", "10.0.5.10"), ("09:11:00", "pc-ayse", "198.51.100.66"),
      ("09:12:00", "pc-can", "192.168.1.20"), ("09:13:00", "pc-can", "172.16.4.4"),
      ("09:14:00", "pc-mert", "172.32.0.1"), ("09:15:00", "pc-mert", "11.0.0.1")]
olaylar = [{"UtcTime": "2026-10-19 " + z, "EventCode": 1, "Computer": c, "Image": WPS, "CommandLine": k,
            "User": u, "ParentUser": pu} for z, c, k, u, pu in surec]
olaylar += [{"UtcTime": "2026-10-19 " + z, "EventCode": 3, "Computer": c, "Image": WPS, "DestinationIp": d,
             "DestinationPort": 443} for z, c, d in ag]
veri("".join(json.dumps(o) + "\n" for o in olaylar), "pafta_sysmon", "WinEventLog:Microsoft-Windows-Sysmon/Operational")
```
:::

::: gorev 1 · Kodlanmış komutta işaret
Kodlanmış PowerShell komutlarının **içinde** `Write-Output` geçenleri bulan bir kural yaz (`category: process_creation`):

- `Image` `\powershell.exe` ile biter,
- komut satırında ` -enc ` bayrağı **hangi tire biçimiyle** yazılırsa yazılsın (`/enc`, `–enc` dahil),
- komut satırındaki base64 yükü, çözüldüğünde `Write-Output` içerir (PowerShell'in UTF-16LE kodlamasıyla, metnin yükteki konumundan bağımsız).

`fields: [Computer]`.

```starter
title: Kodlanmış komutta işaret
id: 9b1c2d3e-0000-4000-8000-000000000024
logsource: {product: windows, category: process_creation}
detection:
  sel:
    Image|endswith: '\powershell.exe'
    CommandLine|contains: ' -enc '
    CommandLine|base64offset|contains: 'Write-Output'
  condition: sel
fields: [Computer]
```

```test
eq(sorted(r[0] for r in sonuc), ["pc-ayse", "pc-can", "pc-mert"],
   "üç PowerShell yükü: -enc, /enc ve –enc; işaret yükün başında da ortasında da bulunur")
ok(any("SQBFAFgA" not in q and "VwByAGkAdABlAC0ATwB1AHQAcAB1AHQA" in q for q in spl), "UTF-16LE (wide) biçimi aranıyor")
EK = ('import json\n'
      'WPS = "C:\\\\Windows\\\\System32\\\\WindowsPowerShell\\\\v1.0\\\\powershell.exe"\n'
      'ek = [("pc-uzun", "powershell.exe \\u2014enc " + "VwByAGkAdABlAC0ATwB1AHQAcAB1AHQAIAAnAHAAYQBmAHQAYQAgAGUAZwBpAHQAaQBtACcA"),\n'
      '      ("pc-tarih", "powershell.exe -enc RwBlAHQALQBEAGEAdABlAAo="),\n'
      '      ("pc-duz", "powershell.exe -Command Write-Output pafta")]\n'
      'veri("".join(json.dumps({"UtcTime": "2026-10-19 09:30:00", "EventCode": 1, "Computer": c, "Image": WPS,\n'
      '                         "CommandLine": k}) + "\\n" for c, k in ek), "pafta_sysmon", "WinEventLog:Microsoft-Windows-Sysmon/Operational")\n')
eq(sorted(r[0] for r in dene(EK)), ["pc-ayse", "pc-can", "pc-mert", "pc-uzun"],
   "em dash (—enc) da yakalanır; işaretsiz yük ve kodlanmamış düz komut yakalanmaz")
```

```solution
title: Kodlanmış komutta işaret
id: 9b1c2d3e-0000-4000-8000-000000000024
logsource: {product: windows, category: process_creation}
detection:
  sel:
    Image|endswith: '\powershell.exe'
    CommandLine|windash|contains: ' -enc '
    CommandLine|wide|base64offset|contains: 'Write-Output'
  condition: sel
fields: [Computer]
```

```hint
Tire biçimleri için `CommandLine|windash|contains: ' -enc '`. Yük için değiştirici zinciri sırasıyla: `CommandLine|wide|base64offset|contains: 'Write-Output'` (önce UTF-16LE, sonra base64'ün üç kaydırması, sonra içerir).
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
ISARET = "VwByAGkAdABlAC0ATwB1AHQAcAB1AHQAIAAnAHAAYQBmAHQAYQAgAGUAZwBpAHQAaQBtACcA"      # Write-Output 'pafta egitim'
BASKA = "RwBlAHQALQBEAGEAdABlADsAIABXAHIAaQB0AGUALQBPAHUAdABwAHUAdAAgACcAdABhAG0AYQBtACcA"   # Get-Date; Write-Output 'tamam'
TARIH = "RwBlAHQALQBEAGEAdABlAA=="                                                            # Get-Date
ASCII = "V3JpdGUtT3V0cHV0ICdwYWZ0YSBlZ2l0aW0n"                                                # Write-Output (UTF-8)
surec = [
    ("09:01:00", "pc-ayse", "powershell.exe -nop -enc " + ISARET, "PAFTA\\ayse", "PAFTA\\ayse"),
    ("09:02:00", "pc-can", "powershell.exe /enc " + BASKA, "PAFTA\\can", "PAFTA\\can"),
    ("09:03:00", "pc-mert", "powershell.exe \u2013enc " + ISARET, "PAFTA\\mert", "pafta\\MERT"),
    ("09:04:00", "pc-zeynep", "powershell.exe -enc " + TARIH, "PAFTA\\zeynep", "NT AUTHORITY\\SYSTEM"),
    ("09:05:00", "pc-ali", "powershell.exe -enc " + ASCII, "PAFTA\\ali", "PAFTA\\ali"),
]
ag = [("09:10:00", "pc-ayse", "10.0.5.10"), ("09:11:00", "pc-ayse", "198.51.100.66"),
      ("09:12:00", "pc-can", "192.168.1.20"), ("09:13:00", "pc-can", "172.16.4.4"),
      ("09:14:00", "pc-mert", "172.32.0.1"), ("09:15:00", "pc-mert", "11.0.0.1")]
olaylar = [{"UtcTime": "2026-10-19 " + z, "EventCode": 1, "Computer": c, "Image": WPS, "CommandLine": k,
            "User": u, "ParentUser": pu} for z, c, k, u, pu in surec]
olaylar += [{"UtcTime": "2026-10-19 " + z, "EventCode": 3, "Computer": c, "Image": WPS, "DestinationIp": d,
             "DestinationPort": 443} for z, c, d in ag]
veri("".join(json.dumps(o) + "\n" for o in olaylar), "pafta_sysmon", "WinEventLog:Microsoft-Windows-Sysmon/Operational")
```
:::

::: gorev 2 · İç ağın dışına çıkan PowerShell
PowerShell'in ağ bağlantılarından (`category: network_connection`) hedefi kurumun iç ağlarında **olmayanları** bul. İç ağlar: `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`. `fields: [Computer, DestinationIp]`.

```starter
title: İç ağ dışına PowerShell bağlantısı
id: 9b1c2d3e-0000-4000-8000-000000000025
logsource: {product: windows, category: network_connection}
detection:
  sel:
    Image|endswith: '\powershell.exe'
  ic:
    DestinationIp|startswith: ['10.', '172.16.', '192.168.']
  condition: sel and not ic
fields: [Computer, DestinationIp]
```

```test
eq(sutunlar, ["Computer", "DestinationIp"], "sütunlar")
eq(sorted(r[1] for r in sonuc), ["11.0.0.1", "172.32.0.1", "198.51.100.66"],
   "172.32.0.1 iç ağ değildir (172.16.0.0/12 → 172.16–172.31); 11.0.0.1 de dışarıda")
ok(any("172.16.0.0/12" in q for q in spl), "cidr değiştiricisi")
EK = ('import json\n'
      'WPS = "C:\\\\Windows\\\\System32\\\\WindowsPowerShell\\\\v1.0\\\\powershell.exe"\n'
      'ek = [("pc-x", "172.31.255.254"), ("pc-x", "192.169.0.1"), ("pc-x", "10.255.255.255")]\n'
      'veri("".join(json.dumps({"UtcTime": "2026-10-19 09:40:00", "EventCode": 3, "Computer": c, "Image": WPS,\n'
      '                         "DestinationIp": d}) + "\\n" for c, d in ek), "pafta_sysmon", "WinEventLog:Microsoft-Windows-Sysmon/Operational")\n')
eq(sorted(r[1] for r in dene(EK)), ["11.0.0.1", "172.32.0.1", "192.169.0.1", "198.51.100.66"],
   "ağların son adresleri içeridedir; 192.169.0.1 dışarıdadır")
```

```solution
title: İç ağ dışına PowerShell bağlantısı
id: 9b1c2d3e-0000-4000-8000-000000000025
logsource: {product: windows, category: network_connection}
detection:
  sel:
    Image|endswith: '\powershell.exe'
  ic:
    DestinationIp|cidr: ['10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16']
  condition: sel and not ic
fields: [Computer, DestinationIp]
```

```hint
`startswith: '172.16.'` yalnız 172.16.x'i iç ağ sayar; oysa 172.16.0.0/12 172.16'dan 172.31'e kadardır ve aradakiler dışarıda görünür. Ağ üyeliği için `DestinationIp|cidr: [...]`.
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
ISARET = "VwByAGkAdABlAC0ATwB1AHQAcAB1AHQAIAAnAHAAYQBmAHQAYQAgAGUAZwBpAHQAaQBtACcA"      # Write-Output 'pafta egitim'
BASKA = "RwBlAHQALQBEAGEAdABlADsAIABXAHIAaQB0AGUALQBPAHUAdABwAHUAdAAgACcAdABhAG0AYQBtACcA"   # Get-Date; Write-Output 'tamam'
TARIH = "RwBlAHQALQBEAGEAdABlAA=="                                                            # Get-Date
ASCII = "V3JpdGUtT3V0cHV0ICdwYWZ0YSBlZ2l0aW0n"                                                # Write-Output (UTF-8)
surec = [
    ("09:01:00", "pc-ayse", "powershell.exe -nop -enc " + ISARET, "PAFTA\\ayse", "PAFTA\\ayse"),
    ("09:02:00", "pc-can", "powershell.exe /enc " + BASKA, "PAFTA\\can", "PAFTA\\can"),
    ("09:03:00", "pc-mert", "powershell.exe \u2013enc " + ISARET, "PAFTA\\mert", "pafta\\MERT"),
    ("09:04:00", "pc-zeynep", "powershell.exe -enc " + TARIH, "PAFTA\\zeynep", "NT AUTHORITY\\SYSTEM"),
    ("09:05:00", "pc-ali", "powershell.exe -enc " + ASCII, "PAFTA\\ali", "PAFTA\\ali"),
]
ag = [("09:10:00", "pc-ayse", "10.0.5.10"), ("09:11:00", "pc-ayse", "198.51.100.66"),
      ("09:12:00", "pc-can", "192.168.1.20"), ("09:13:00", "pc-can", "172.16.4.4"),
      ("09:14:00", "pc-mert", "172.32.0.1"), ("09:15:00", "pc-mert", "11.0.0.1")]
olaylar = [{"UtcTime": "2026-10-19 " + z, "EventCode": 1, "Computer": c, "Image": WPS, "CommandLine": k,
            "User": u, "ParentUser": pu} for z, c, k, u, pu in surec]
olaylar += [{"UtcTime": "2026-10-19 " + z, "EventCode": 3, "Computer": c, "Image": WPS, "DestinationIp": d,
             "DestinationPort": 443} for z, c, d in ag]
veri("".join(json.dumps(o) + "\n" for o in olaylar), "pafta_sysmon", "WinEventLog:Microsoft-Windows-Sysmon/Operational")
```
:::
