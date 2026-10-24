---
id: sg19
title: Processing Pipeline · Paylaşılan Kuralı Kendi Verine Uydurmak
summary: Bir Sigma kuralının alan adlarının (Image, CommandLine, ParentImage) kurumun verisindeki adlarla aynı olmadığı durum; pySigma processing pipeline'ı: field_name_mapping, add_condition ve rule_conditions ile dönüşümün yalnız ilgili kurallara uygulanması; eşlemesi unutulan alanın ve yanlış kategoriye bağlanan dönüşümün kuralı sessizce susturması; bilinmeyen dönüşüm türünün hata vermesi. Kural gerçek pySigma Splunk backend'iyle çevrilir ve gerçek Splunk'ta aynı olaylarda çalışır.
---

::: anlat Kural ortak, veri senin
SigmaHQ deposundaki bir kural Sysmon'un alan adlarıyla yazılır: `Image`, `CommandLine`, `ParentImage`. Senin kurumun uç nokta ajanı (EDR) ise aynı bilgiyi kendi adlarıyla gönderiyor olabilir: `process_path`, `process_cmdline`, `parent_path`, `device`. SG15'te bunu elle düzeltmiştin. Yüzlerce kuralda elle düzeltmek sürdürülemez; Sigma'nın çözümü **processing pipeline**'dır: kuralı değiştirmeden, çeviri sırasında uygulanan bir dönüşüm listesi.

```sigma norun
name: kurum-edr
priority: 100
transformations:
  - id: alanlar
    type: field_name_mapping
    mapping:
      Image: process_path
      CommandLine: process_cmdline
    rule_conditions:
      - type: logsource
        category: process_creation
  - id: kaynak
    type: add_condition
    conditions:
      sourcetype: pafta_edr
    rule_conditions:
      - type: logsource
        category: process_creation
```

| Parça | Anlamı |
|---|---|
| `field_name_mapping` | kuraldaki alan adını hedefteki adla değiştirir |
| `add_condition` | sorguya bir koşul ekler; burada verinin nerede olduğunu (`sourcetype`) |
| `rule_conditions` | dönüşüm **yalnız** bu koşula uyan kurallara uygulanır (ör. `process_creation` kategorisi) |
| `priority` | birden çok pipeline birleşince sıralama |

Bu pipeline ile kural şu SPL'e dönüşür (bu derste ölçüldü):

```text
sourcetype="pafta_edr" process_path="*\\powershell.exe" process_cmdline="* -enc *"
```

> [!TUZAK] Unutulan eşleme hata vermez
> Eşlemede bir alanı unutursan pySigma onu olduğu gibi bırakır: sorguda `Image="*\\powershell.exe"` kalır. Kurumun verisinde `Image` diye bir alan olmadığı için Splunk **hata vermeden sıfır sonuç** döner. Kural çalışıyor görünür, hiçbir şey yakalamaz. `rule_conditions` yanlış kategoriye bağlanırsa da aynı şey olur: dönüşüm hiç uygulanmaz. Bir pipeline'ı mutlaka **yakalaması gereken bir olayla** sına.

> [!TUZAK] Splunk'ın kendi alan adları
> Bir kaynağın alanı Splunk'ın meta alanlarından biriyle aynı adı taşıyorsa (`host`, `source`, `sourcetype`, `index`) Splunk'ınki kazanır. Bu derste ölçüldü: EDR olaylarındaki `"host": "pc-ayse"` alanı aramada `host=pafta-splunk` olarak, yani olayı alan sunucunun adıyla geldi. Kurumun cihaz adı alanı bu yüzden burada `device`.

> [!NOT] Laboratuvar
> Bu paftada kod bir **pipeline**'dır; kural görevin hazırlığında hazırdır. Pafta pipeline'ını gerçek pySigma (1.5.1) ve resmi Splunk backend'iyle (2.1.0) kurar, kuralı çevirir, üretilen SPL'i gösterir ve gerçek Splunk laboratuvarında (SP21–SP23'teki) hazırlığın olaylarında çalıştırır. Sonuç satırları Splunk'tan gelir.
:::

::: tahmin
Bu pipeline'da dönüşümler `network_connection` kategorisine bağlanmış. Kural `process_creation` kategorisinde. Kaç sonuç gelir?

```sigma
name: kurum-edr
priority: 100
transformations:
  - id: alanlar
    type: field_name_mapping
    mapping:
      Image: process_path
      CommandLine: process_cmdline
      ParentImage: parent_path
      Computer: device
    rule_conditions:
      - type: logsource
        category: network_connection
  - id: kaynak
    type: add_condition
    conditions:
      sourcetype: pafta_edr
```

???

**Hiç satır.**

`add_condition` koşulsuz olduğu için `sourcetype="pafta_edr"` eklendi, ama alan eşlemesi `network_connection` kurallarına bağlı olduğu için bu kurala **uygulanmadı**. Üretilen SPL `sourcetype="pafta_edr" Image="*\\powershell.exe" ...` olur; kurumun verisinde `Image` alanı olmadığından Splunk hata vermeden sıfır satır döndürür. Pipeline'ı denerken her zaman üretilen SPL'e de bak.

```meta
motor: splunk
girdi: pipeline
```

```setup
import json
props("pafta_edr", {"INDEXED_EXTRACTIONS": "json", "KV_MODE": "none", "TIMESTAMP_FIELDS": "zaman",
                    "TIME_FORMAT": "%Y-%m-%d %H:%M:%S"})
WPS = "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"
olaylar = [
    {"zaman": "2026-10-19 09:01:00", "device": "pc-ayse", "process_path": WPS,
     "process_cmdline": "powershell.exe -nop -w hidden -enc SQBFAFgA", "parent_path": "C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE"},
    {"zaman": "2026-10-19 09:02:00", "device": "pc-can", "process_path": WPS,
     "process_cmdline": "powershell.exe -File yedek.ps1", "parent_path": "C:\\Windows\\explorer.exe"},
    {"zaman": "2026-10-19 09:03:00", "device": "pc-mert", "process_path": WPS,
     "process_cmdline": "powershell.exe -enc ZQBjAGgAbwA=", "parent_path": "C:\\Windows\\explorer.exe"},
    {"zaman": "2026-10-19 09:04:00", "device": "pc-zeynep", "process_path": WPS,
     "process_cmdline": "powershell.exe -ENC JABhAD0A", "parent_path": "C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE"},
    {"zaman": "2026-10-19 09:05:00", "device": "pc-ayse", "process_path": "C:\\Windows\\System32\\cmd.exe",
     "process_cmdline": "cmd.exe /c echo -enc", "parent_path": "C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE"},
]
veri("".join(json.dumps(o) + "\n" for o in olaylar), "pafta_edr", "edr:surec")
kural(r"""title: Office'ten başlatılan kodlanmış PowerShell
id: 5d1a8f2e-7c3b-4e9a-a1d2-0b6c4f8e9a10
status: experimental
logsource:
  product: windows
  category: process_creation
detection:
  sel:
    Image|endswith: '\powershell.exe'
    CommandLine|contains: ' -enc '
    ParentImage|endswith:
      - '\winword.exe'
      - '\excel.exe'
  condition: sel
fields:
  - Computer
  - CommandLine
level: high
""")
```
:::

::: gorev 1 · Kurumun EDR alanlarına çevir
Kurumun EDR'ı süreç olaylarını `pafta_edr` sourcetype'ında şu alanlarla gönderiyor: `device`, `process_path`, `process_cmdline`, `parent_path`. Hazırlıktaki kural ("Office'ten başlatılan kodlanmış PowerShell") Sysmon adlarıyla yazılmış: `Computer`, `Image`, `CommandLine`, `ParentImage`.

Kuralı değiştirmeden bu verinde çalıştıran bir pipeline yaz:

- dört alanı eşle,
- sorguyu `pafta_edr` sourcetype'ına sınırla,
- iki dönüşüm de yalnız `process_creation` kurallarına uygulansın.

```starter
name: kurum-edr
priority: 100
transformations:
  - id: alanlar
    type: field_name_mapping
    mapping:
      Image: process_path
      CommandLine: process_cmdline
```

```test
eq(sutunlar, ["device", "process_cmdline"], "kuralın fields listesi de eşlenir: Computer → device, CommandLine → process_cmdline")
eq(sorted(r[0] for r in sonuc), ["pc-ayse", "pc-zeynep"], "Word ve Excel'den başlayan iki kodlanmış PowerShell")
ok('sourcetype="pafta_edr"' in spl[0], "sorgu pafta_edr ile sınırlı")
ok("Image" not in spl[0] and "ParentImage" not in spl[0], "Sysmon alan adı sorguda kalmadı")
EK = ('import json\n'
      'veri(json.dumps({"zaman": "2026-10-19 09:20:00", "device": "pc-baska", "process_path": "C:\\\\x\\\\powershell.exe", '
      '"process_cmdline": "powershell -enc AAA", "parent_path": "C:\\\\o\\\\WINWORD.EXE"}) + "\\n", "pafta_baska", "edr:surec")\n')
eq(sorted(r[0] for r in dene(EK)), ["pc-ayse", "pc-zeynep"], "aynı alan adlarıyla başka bir sourcetype'taki olay sonuca girmez")
ag = cevir("""title: ag
id: 99999999-0000-0000-0000-000000000001
logsource: {product: windows, category: network_connection}
detection:
  sel: {Image|endswith: '\\\\powershell.exe'}
  condition: sel
""")
ok("pafta_edr" not in ag[0] and "process_path" not in ag[0], "dönüşümler başka kategorideki bir kurala uygulanmaz")
```

```solution
name: kurum-edr
priority: 100
transformations:
  - id: alanlar
    type: field_name_mapping
    mapping:
      Image: process_path
      CommandLine: process_cmdline
      ParentImage: parent_path
      Computer: device
    rule_conditions:
      - type: logsource
        category: process_creation
  - id: kaynak
    type: add_condition
    conditions:
      sourcetype: pafta_edr
    rule_conditions:
      - type: logsource
        category: process_creation
```

```hint
Başlangıçta `ParentImage` ve `Computer` eşlenmemiş; sorguda Sysmon adıyla kalırlar ve kurumun verisinde karşılıkları olmadığı için hiçbir şey eşleşmez.
```

```hint
İkinci dönüşüm `type: add_condition` ve `conditions: {sourcetype: pafta_edr}`. İkisine de aynı `rule_conditions` bloğunu koy: `- type: logsource` / `category: process_creation`.
```

```meta
motor: splunk
girdi: pipeline
```

```setup
import json
props("pafta_edr", {"INDEXED_EXTRACTIONS": "json", "KV_MODE": "none", "TIMESTAMP_FIELDS": "zaman",
                    "TIME_FORMAT": "%Y-%m-%d %H:%M:%S"})
WPS = "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"
olaylar = [
    {"zaman": "2026-10-19 09:01:00", "device": "pc-ayse", "process_path": WPS,
     "process_cmdline": "powershell.exe -nop -w hidden -enc SQBFAFgA", "parent_path": "C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE"},
    {"zaman": "2026-10-19 09:02:00", "device": "pc-can", "process_path": WPS,
     "process_cmdline": "powershell.exe -File yedek.ps1", "parent_path": "C:\\Windows\\explorer.exe"},
    {"zaman": "2026-10-19 09:03:00", "device": "pc-mert", "process_path": WPS,
     "process_cmdline": "powershell.exe -enc ZQBjAGgAbwA=", "parent_path": "C:\\Windows\\explorer.exe"},
    {"zaman": "2026-10-19 09:04:00", "device": "pc-zeynep", "process_path": WPS,
     "process_cmdline": "powershell.exe -ENC JABhAD0A", "parent_path": "C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE"},
    {"zaman": "2026-10-19 09:05:00", "device": "pc-ayse", "process_path": "C:\\Windows\\System32\\cmd.exe",
     "process_cmdline": "cmd.exe /c echo -enc", "parent_path": "C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE"},
]
veri("".join(json.dumps(o) + "\n" for o in olaylar), "pafta_edr", "edr:surec")
kural(r"""title: Office'ten başlatılan kodlanmış PowerShell
id: 5d1a8f2e-7c3b-4e9a-a1d2-0b6c4f8e9a10
status: experimental
logsource:
  product: windows
  category: process_creation
detection:
  sel:
    Image|endswith: '\powershell.exe'
    CommandLine|contains: ' -enc '
    ParentImage|endswith:
      - '\winword.exe'
      - '\excel.exe'
  condition: sel
fields:
  - Computer
  - CommandLine
level: high
""")
```
:::
