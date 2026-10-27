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

::: anlat sigma-cli: aynı çeviri komut satırından
Bu derse kadar çeviriyi Pafta, pySigma kütüphanesini çağırarak yaptı. Sahada kural deposunu bir CI hattında ya da elle **sigma-cli** ile çevirirsin. Bu ders `.deps` içindeki gerçek sigma-cli 3.1.0'ı (pySigma 1.5.1, Splunk backend 2.1.0) çalıştırır:

```text
sigma convert -t splunk -p sysmon -p kurum-edr.yml -f default kurallar/
```

| Seçenek | Anlamı | Bu sürümde ölçülen |
|---|---|---|
| `-t splunk` | hedef backend | `sigma list targets`: `splunk`, `splunk_spl2` |
| `-p ad` / `-p dosya.yml` | pipeline; birden çok verilebilir, `priority` değerine göre birleşir | hazır: `sysmon`, `windows-logsources`, `windows-audit`, `splunk_windows`, `splunk_cim`, `splunk_sysmon_acceleration` |
| `-f` | çıktı biçimi | `default` (düz SPL), `savedsearches` (conf dosyası), `data_model` (`tstats`) |
| `-s` | çevrilemeyen kuralı atla, sonda "Ignored errors" altında yaz | yalnız pySigma'nın kendi hata türlerini atlar |
| `--without-pipeline` | pipeline'sız çevirmeye zorla | Splunk backend'i pipeline ister; vermezsen **çıkış kodu 2** |

Ölçülen üç tuzak:

- Pipeline vermeden `sigma convert -t splunk kural.yml` çalıştırınca komut "Processing pipeline required by backend" der ve **2** ile çıkar. `--without-pipeline` hatayı susturur ama alan adları Sysmon'da kalır.
- Klasör çevirirken tek bir kural bütün işi durdurabilir. Tanımlanmamış bir yer tutucu (`|expand: '%yonetici_makineleri%'`) `-s` ile atlanır ve stderr'de nedeni yazılır. Ama `-s` her şeyi atlamaz: `|cased` değiştiricili bir kural bu sürümde `-s`'ye rağmen çeviriyi **1** ile durdurdu. Hata pySigma'nın hata türü olarak değil genel bir istisna olarak yükseliyor. CI'da çıkış koduna bak.
- `-p splunk_cim -f data_model` kuralı ham olaylara değil **CIM veri modeline** çevirir: `| tstats ... from datamodel=Endpoint.Processes where Processes.process_path=... by Processes.dest ...`. Alan eşlemesi `Image→Processes.process_path`, `CommandLine→Processes.process`, `ParentImage→Processes.parent_process_path`. Sorgu yalnız modele giren (etiketli, SP23'teki gibi) olayları görür. Model dışında kalan bir kaynak, alan adları aynı olsa bile sonuçta görünmez.

> [!NOT] Laboratuvar
> Bu görevlerde kod bir **komut satırıdır**. Pafta komutu hazırlığın dosyalarıyla geçici bir klasörde gerçek sigma-cli'ye verir; stdout'taki her satır bir sorgudur, son sorgu gerçek Splunk'ta çalışır (`tstats` ile başlıyorsa olduğu gibi, değilse laboratuvar dizininde). Hedef yalnız `splunk`, biçim yalnız çalıştırılabilir olanlar (`default`, `data_model`); dosya yazan (`-o`) ya da başka hedef seçen seçenekler reddedilir. Komut sıfırdan farklı bir kodla biterse görev hata verir ve sigma-cli'nin mesajı gösterilir.

Kaynaklar: [sigma-cli](https://github.com/SigmaHQ/sigma-cli), [pySigma Splunk backend ve splunk_cim](https://github.com/SigmaHQ/pySigma-backend-splunk), [Sigma değiştiricileri](https://sigmahq.io/docs/basics/modifiers.html).
:::

::: gorev 2 · Kural klasörünü kendi pipeline'ınla çevir
Hazırlıkta `kurallar/` klasöründe üç kural ve birinci görevdeki pipeline `kurum-edr.yml` dosyası var. Kurallardan biri (`b_yonetici_disi.yml`) kurumun henüz tanımlamadığı bir yer tutucu (`%yonetici_makineleri%`) kullanıyor.

sigma-cli ile **bütün klasörü** Splunk'a çevir. Kurumun alan adları için `kurum-edr.yml` pipeline'ını kullan, çevrilemeyen kural işi durdurmasın. Sonuçta iki sorgu çıkmalı ve ikisi de kurumun verisinde çalışmalı.

```meta
motor: splunk
girdi: komut
```

```setup
import json
props("pafta_edr", {"INDEXED_EXTRACTIONS": "json", "KV_MODE": "none", "TIMESTAMP_FIELDS": "zaman",
                    "TIME_FORMAT": "%Y-%m-%d %H:%M:%S"})
WPS = "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"
WORD = "C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE"
olaylar = [
    {"zaman": "2026-10-19 09:01:00", "device": "pc-ayse", "process_path": WPS,
     "process_cmdline": "powershell.exe -nop -w hidden -enc SQBFAFgA", "parent_path": WORD},
    {"zaman": "2026-10-19 09:02:00", "device": "pc-can", "process_path": WPS,
     "process_cmdline": "powershell.exe -File yedek.ps1", "parent_path": "C:\\Windows\\explorer.exe"},
    {"zaman": "2026-10-19 09:04:00", "device": "pc-zeynep", "process_path": WPS,
     "process_cmdline": "powershell.exe -ENC JABhAD0A", "parent_path": "C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE"},
    {"zaman": "2026-10-19 09:05:00", "device": "pc-ayse", "process_path": "C:\\Windows\\System32\\cmd.exe",
     "process_cmdline": "cmd.exe /c whoami", "parent_path": WORD},
    {"zaman": "2026-10-19 09:06:00", "device": "pc-mert", "process_path": "C:\\Windows\\System32\\cmd.exe",
     "process_cmdline": "cmd.exe /c dir", "parent_path": "C:\\Windows\\explorer.exe"},
]
veri("".join(json.dumps(o) + "\n" for o in olaylar), "pafta_edr", "edr:surec")
dosya("kurum-edr.yml", """name: kurum-edr
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
""")
dosya("kurallar/a_ofis_powershell.yml", r"""title: Office'ten başlatılan kodlanmış PowerShell
id: 5d1a8f2e-7c3b-4e9a-a1d2-0b6c4f8e9a10
status: experimental
logsource: {product: windows, category: process_creation}
detection:
  sel:
    Image|endswith: '\powershell.exe'
    CommandLine|contains: ' -enc '
    ParentImage|endswith: ['\winword.exe', '\excel.exe']
  condition: sel
level: high
""")
dosya("kurallar/b_yonetici_disi.yml", r"""title: Yönetici makinesi dışında PowerShell
id: 8a4d1b5c-0f6e-4bcd-94a5-3e9f7c1bcd43
status: experimental
logsource: {product: windows, category: process_creation}
detection:
  sel:
    Image|endswith: '\powershell.exe'
  yonetici:
    Computer|expand: '%yonetici_makineleri%'
  condition: sel and not yonetici
level: medium
""")
dosya("kurallar/c_ofis_cmd.yml", r"""title: Office'ten başlatılan komut satırı
id: 9b5e2c6d-1a7f-4cde-a5b6-4fa08d2cde54
status: experimental
logsource: {product: windows, category: process_creation}
detection:
  sel:
    Image|endswith: '\cmd.exe'
    ParentImage|endswith: ['\winword.exe', '\excel.exe']
  condition: sel
level: medium
""")
```

```starter
sigma convert -t splunk -p sysmon kurallar
```

```test
eq(len(spl), 2, "üç kuraldan ikisi çevrilir; yer tutuculu kural atlanır, işi durdurmaz")
ok(all('sourcetype="pafta_edr"' in q and "Image" not in q and "EventID" not in q for q in spl),
   "iki sorgu da kurumun pipeline'ıyla: pafta_edr kaynağı, kurumun alan adları", spl)
eq(sorted(r[0] for r in ara("search index=" + DIZIN + " " + spl[1] + " | table device")), ["pc-ayse"],
   "ikinci sorgu (c_ofis_cmd): Word'den başlatılan cmd.exe")
eq(sorted(r[0] for r in ara("search index=" + DIZIN + " " + spl[0] + " | table device")), ["pc-ayse", "pc-zeynep"],
   "ilk sorgu (a_ofis_powershell): Word ve Excel'den kodlanmış PowerShell")
```

```solution
sigma convert -t splunk -p kurum-edr.yml -s kurallar
```

```hint
Pipeline'ı dosya adıyla verebilirsin: `-p kurum-edr.yml`. `-p sysmon` alanları Sysmon'da bırakır ve `EventID=1` ekler; kurumun verisinde ikisi de yok.
```

```hint
Yer tutucu `%yonetici_makineleri%` tanımlı değil; `-s` (`--skip-unsupported`) bu kuralı atlar ve nedenini "Ignored errors" altında yazar. Girdi olarak klasörün adını ver: `kurallar`.
```
:::

::: gorev 3 · Aynı kuralı CIM veri modeline çevir
Bu kez kurumun EDR olayları `pafta_edr_cim` kaynağında ve SP23'teki gibi CIM'e uyarlanmış: `device → dest`, `process_cmdline → process`, `parent_path → parent_process_path` takma adları ve `process` + `report` etiketleri hazırlıkta kurulu. Kuralı ham olaylara değil Splunk'ın **Endpoint.Processes** veri modeline çeviren sigma-cli komutunu yaz. Sonuç modelden `tstats` ile gelmeli.

```meta
motor: splunk
girdi: komut
```

```setup
import json
CIM = {"INDEXED_EXTRACTIONS": "json", "KV_MODE": "none", "TIMESTAMP_FIELDS": "zaman", "TIME_FORMAT": "%Y-%m-%d %H:%M:%S",
       "FIELDALIAS-cim": "device AS dest process_cmdline AS process parent_path AS parent_process_path"}
props("pafta_edr_cim", CIM)
olay_turu("pafta_edr_surec", "sourcetype=pafta_edr_cim")
etiket("eventtype=pafta_edr_surec", {"process": "enabled", "report": "enabled"})
WPS = "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"
olaylar = [
    {"zaman": "2026-10-19 09:01:00", "device": "pc-ayse", "process_path": WPS,
     "process_cmdline": "powershell.exe -nop -w hidden -enc SQBFAFgA", "parent_path": "C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE"},
    {"zaman": "2026-10-19 09:02:00", "device": "pc-can", "process_path": WPS,
     "process_cmdline": "powershell.exe -File yedek.ps1", "parent_path": "C:\\Windows\\explorer.exe"},
    {"zaman": "2026-10-19 09:04:00", "device": "pc-zeynep", "process_path": WPS,
     "process_cmdline": "powershell.exe -ENC JABhAD0A", "parent_path": "C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE"},
]
veri("".join(json.dumps(o) + "\n" for o in olaylar), "pafta_edr_cim", "edr:surec")
dosya("kurallar/ofis_powershell.yml", r"""title: Office'ten başlatılan kodlanmış PowerShell
id: 5d1a8f2e-7c3b-4e9a-a1d2-0b6c4f8e9a10
status: experimental
logsource: {product: windows, category: process_creation}
detection:
  sel:
    Image|endswith: '\powershell.exe'
    CommandLine|contains: ' -enc '
    ParentImage|endswith: ['\winword.exe', '\excel.exe']
  condition: sel
level: high
""")
```

```starter
sigma convert -t splunk -p splunk_cim kurallar/ofis_powershell.yml
```

```test
ok(spl[-1].startswith("| tstats") and "datamodel=Endpoint.Processes" in spl[-1], "sorgu veri modelinden tstats ile okur", spl)
ok("Processes.process_path" in spl[-1] and "Processes.parent_process_path" in spl[-1], "Sigma alanları CIM model alanlarına eşlenir")
ok({"dest", "process", "count", "firstTime", "lastTime"} <= set(sutunlar), "drop_dm_object_name: model öneki atılmış sütunlar", sutunlar)
eq(sorted(r[sutunlar.index("dest")] for r in sonuc), ["pc-ayse", "pc-zeynep"], "modele giren iki eşleşme")
EK = ('import json\n'
      'props("pafta_edr_baska", CIM)\n'
      'veri(json.dumps({"zaman": "2026-10-19 09:10:00", "device": "pc-etiketsiz", "process_path": WPS, '
      '"process_cmdline": "powershell -enc AAA", "parent_path": "C:\\\\o\\\\WINWORD.EXE"}) + "\\n", "pafta_edr_baska", "edr:surec")\n')
eq(sorted(r[sutunlar.index("dest")] for r in dene(EK)), ["pc-ayse", "pc-zeynep"],
   "aynı takma adlara sahip ama etiketsiz kaynak modele girmez")
```

```solution
sigma convert -t splunk -p splunk_cim -f data_model kurallar/ofis_powershell.yml
```

```hint
`-p splunk_cim` alan adlarını CIM'e çevirir ama `-f` vermezsen çıktı yine ham olaylarda arayan düz SPL olur. Veri modeli için biçim `data_model`.
```
:::

::: anlat Aynı kural, üç ürün: Defender'ın Kusto'su ve Elastic'in EQL'i
Splunk tek hedef değildir. Bu bilgisayarda kurulu sigma-cli artık Kusto backend'i (1.0.1) ve Elasticsearch backend'i (2.1.1) ile de çalışır: `sigma list targets` çıktısında `kusto`, `eql`, `lucene`, `esql` görünür. Her hedefin kendi pipeline'ı vardır ve pipeline yalnız alan adını değil **tabloyu ya da indeks eşlemesini** de belirler (bu derste ölçüldü):

| Komut | Çıktı | Neye dayanır |
|---|---|---|
| `-t kusto -p microsoft_xdr` | `DeviceProcessEvents \| where FolderPath endswith ... and ProcessCommandLine contains ...` | Defender XDR'ın gelişmiş avcılık tablosu ve alan adları |
| `-t kusto -p sentinel_asim` | `imProcessCreate \| where TargetProcessName ...` | Sentinel'deki ASIM ayrıştırıcı fonksiyonu; çalışma alanında tanımlı olmalı |
| `-t kusto` (pipeline'sız) | yalnız `Image endswith ...`; tablo yok | Kusto backend pipeline istemez ama çıktısı tek başına sorgu değildir |
| `-t eql -p ecs_windows` | `any where process.executable.caseless:"*\\powershell.exe" ...` | ECS alanları ve indekste `.caseless` normalizer'lı alt alan |
| `-t esql -p ecs_windows` | **ret**: pipeline bu hedefe uygun değil | sigma-cli pipeline/hedef uyumunu denetler |

İki tuzak: `.caseless` alt alanı olmayan bir indekste EQL sorgusu eşleşmez ya da alan hatası verir. Bu yüzden indeks eşlemesi kuralın parçasıdır. Kusto'da `contains` ve `endswith` harfe duyarsızdır, Elastic EQL'de `:` ve `like~` da öyle. Splunk'taki `where 'A'='B'` ise harfe duyarlıdır (SG22). Aynı kural her üründe aynı olayları bulmalı; bunu ancak hepsinde aynı olaylarla sınayarak bilirsin.

> [!NOT] Laboratuvar
> Kod satır başına bir `sigma convert` komutudur (`motor: sigma-hedef`). `kusto` çıktısı gerçek Kusto Emulator'da hazırlığın `DeviceProcessEvents` tablosunda, `eql` çıktısı gerçek Elasticsearch 9.5.5'te hazırlığın ECS belgelerinde çalışır. Tablolar ders verisidir; Defender ya da Sentinel servisi değildir.

Kaynaklar: [pySigma Kusto backend](https://github.com/AttackIQ/pySigma-backend-kusto), [pySigma Elasticsearch backend](https://github.com/SigmaHQ/pySigma-backend-elasticsearch), [DeviceProcessEvents](https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-deviceprocessevents-table), [ECS process alanları](https://www.elastic.co/docs/reference/ecs/ecs-process).
:::

::: gorev 4 · Aynı kuralı Defender (Kusto) ve Elastic (EQL) için çevir
Hazırlıktaki `kurallar/ofis_powershell.yml` kuralını iki ürün için çeviren iki `sigma convert` satırı yaz:

- **Defender XDR**: Kusto hedefi, Defender'ın `DeviceProcessEvents` tablosu ve alan adları.
- **Elastic**: EQL hedefi, ECS Windows alanları.

İki çıktı da gerçek motorlarda aynı beş süreç olayının kendi şemalarındaki kopyasında koşar. İkisinin de aynı iki cihazı bulması beklenir.

```meta
motor: sigma-hedef
timeout: 180
```

```setup
{"dosyalar": {"kurallar/ofis_powershell.yml": "title: Office'ten başlatılan kodlanmış PowerShell\nid: 5d1a8f2e-7c3b-4e9a-a1d2-0b6c4f8e9a10\nstatus: experimental\nlogsource: {product: windows, category: process_creation}\ndetection:\n  sel:\n    Image|endswith: '\\powershell.exe'\n    CommandLine|contains: ' -enc '\n    ParentImage|endswith: ['\\winword.exe', '\\excel.exe']\n  condition: sel\nlevel: high\n"}, "kusto_anahtar": "DeviceName", "kusto": {"DeviceProcessEvents": {"sutunlar": [["Timestamp", "datetime"], ["DeviceName", "string"], ["AccountName", "string"], ["FolderPath", "string"], ["ProcessCommandLine", "string"], ["InitiatingProcessFolderPath", "string"]], "satirlar": [["2026-10-19T09:01:00Z", "pc-ayse", "ayse", "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe", "powershell.exe -nop -w hidden -enc SQBFAFgA", "C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE"], ["2026-10-19T09:02:00Z", "pc-can", "can", "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe", "powershell.exe -File yedek.ps1", "C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE"], ["2026-10-19T09:03:00Z", "pc-mert", "mert", "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe", "powershell.exe -enc ZQBjAGgAbwA=", "C:\\Windows\\explorer.exe"], ["2026-10-19T09:04:00Z", "pc-zeynep", "zeynep", "C:\\WINDOWS\\SYSTEM32\\WINDOWSPOWERSHELL\\V1.0\\POWERSHELL.EXE", "POWERSHELL.EXE -ENC JABhAD0A", "C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE"], ["2026-10-19T09:05:00Z", "pc-ali", "ali", "C:\\Windows\\System32\\cmd.exe", "cmd.exe /c echo -enc", "C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE"]]}}, "elastic": {"mapping": {"@timestamp": "date", "event.category": "keyword", "host.name": "keyword", "user.name": "keyword", "process.executable": {"type": "keyword", "fields": {"caseless": {"type": "keyword", "normalizer": "lowercase"}}}, "process.command_line": "keyword", "process.parent.executable": {"type": "keyword", "fields": {"caseless": {"type": "keyword", "normalizer": "lowercase"}}}}, "documents": [{"id": "pc-ayse", "@timestamp": "2026-10-19T09:01:00Z", "event": {"category": "process"}, "host": {"name": "pc-ayse"}, "user": {"name": "ayse"}, "process": {"executable": "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe", "command_line": "powershell.exe -nop -w hidden -enc SQBFAFgA", "parent": {"executable": "C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE"}}}, {"id": "pc-can", "@timestamp": "2026-10-19T09:02:00Z", "event": {"category": "process"}, "host": {"name": "pc-can"}, "user": {"name": "can"}, "process": {"executable": "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe", "command_line": "powershell.exe -File yedek.ps1", "parent": {"executable": "C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE"}}}, {"id": "pc-mert", "@timestamp": "2026-10-19T09:03:00Z", "event": {"category": "process"}, "host": {"name": "pc-mert"}, "user": {"name": "mert"}, "process": {"executable": "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe", "command_line": "powershell.exe -enc ZQBjAGgAbwA=", "parent": {"executable": "C:\\Windows\\explorer.exe"}}}, {"id": "pc-zeynep", "@timestamp": "2026-10-19T09:04:00Z", "event": {"category": "process"}, "host": {"name": "pc-zeynep"}, "user": {"name": "zeynep"}, "process": {"executable": "C:\\WINDOWS\\SYSTEM32\\WINDOWSPOWERSHELL\\V1.0\\POWERSHELL.EXE", "command_line": "POWERSHELL.EXE -ENC JABhAD0A", "parent": {"executable": "C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE"}}}, {"id": "pc-ali", "@timestamp": "2026-10-19T09:05:00Z", "event": {"category": "process"}, "host": {"name": "pc-ali"}, "user": {"name": "ali"}, "process": {"executable": "C:\\Windows\\System32\\cmd.exe", "command_line": "cmd.exe /c echo -enc", "parent": {"executable": "C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE"}}}]}}
```

```starter
sigma convert -t kusto kurallar/ofis_powershell.yml
sigma convert -t eql kurallar/ofis_powershell.yml
```

```test
eq(sorted(hedefler), ["eql", "kusto"], "iki hedef de çevrildi")
ok(hedefler["kusto"]["sorgu"].startswith("DeviceProcessEvents"), "Kusto sorgusu Defender tablosundan başlar", hedefler["kusto"]["sorgu"])
ok("ProcessCommandLine" in hedefler["kusto"]["sorgu"] and "InitiatingProcessFolderPath" in hedefler["kusto"]["sorgu"],
   "Defender alan adları: ProcessCommandLine, InitiatingProcessFolderPath")
ok("process.parent.executable" in hedefler["eql"]["sorgu"] and "process.command_line" in hedefler["eql"]["sorgu"], "ECS alanları")
eq(hedefler["kusto"]["eslesen"], ["pc-ayse", "pc-zeynep"], "gerçek Kusto: Word ve Excel'den kodlanmış PowerShell (büyük harfli yol dahil)")
eq(hedefler["eql"]["eslesen"], ["pc-ayse", "pc-zeynep"], "gerçek Elasticsearch EQL: aynı iki cihaz")
eq(hedefler["kusto"]["eslesen"], hedefler["eql"]["eslesen"], "iki ürün aynı olaylarda aynı sonucu verir")
```

```solution
sigma convert -t kusto -p microsoft_xdr kurallar/ofis_powershell.yml
sigma convert -t eql -p ecs_windows kurallar/ofis_powershell.yml
```

```hint
Kusto backend pipeline istemez ama pipeline'sız çıktı bir tabloyla başlamaz; Defender tabloları için `-p microsoft_xdr`. EQL backend pipeline ister; ECS alanları için `-p ecs_windows`.
```
:::
