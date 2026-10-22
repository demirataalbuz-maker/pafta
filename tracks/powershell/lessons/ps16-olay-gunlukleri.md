---
id: ps16
title: Olay Günlükleri
summary: Windows olay günlüklerinin yapısı, Get-WinEvent, olay alanları, Level numaraları ve dışa aktarılmış olaylarla çalışmak.
kazanim: AZ040 2.3
---

::: anlat Makinenin günlüğü
Windows, olup biten her önemli şeyi **olay günlüklerine** yazar: hizmet başladı, uygulama çöktü, güncelleme yüklendi, sistem yeniden başladı. En çok bakılan günlükler `System` (işletim sistemi ve sürücüler) ve `Application`'dır (uygulamalar). Bunları okuyan cmdlet `Get-WinEvent`'tir. Aşağıdakiler **senin bilgisayarının** gerçek günlüklerini okur:

```powershell
Get-WinEvent -ListLog System, Application | Select-Object LogName, RecordCount
```

```powershell
Get-WinEvent -LogName System -MaxEvents 5 |
    Select-Object TimeCreated, Id, LevelDisplayName, ProviderName
```

Her olay bir nesnedir; en çok kullanılan özellikleri:

| Özellik | Anlamı |
|---|---|
| `TimeCreated` | olayın zamanı |
| `Id` | olay kimliği: aynı sağlayıcıda aynı tür olay hep aynı numarayı alır |
| `Level` | önem: 1 Kritik, 2 Hata, 3 Uyarı, 4 Bilgi |
| `LevelDisplayName` | önemin **yerelleştirilmiş** adı ("Hata", "Error"...) |
| `ProviderName` | olayı yazan bileşen |
| `Message` | açıklama metni |

> [!DERİN]
> Süzerken `LevelDisplayName` yerine `Level` numarasını kullan: ad, Windows'un diline göre değişir (Türkçe sistemde "Hata", İngilizcede "Error"). Aynı betik başka bir makinede sessizce hiçbir şey bulamaz. Numara her dilde aynıdır.

Günlükleri incelemenin sık yolu, olayları başka bir makineden **dışa aktarılmış** bir dosya üzerinden okumaktır. Bu tezgahta her çalıştırmada hazır bir `olaylar.json` dosyası var: SRV-WEB01 adlı bir sunucunun bir haftalık System ve Application olayları.
:::

::: anlat Dışa aktarılmış olayları okumak
```powershell
$olaylar = Get-Content olaylar.json -Raw -Encoding UTF8 | ConvertFrom-Json
"$($olaylar.Count) olay"
$olaylar | Select-Object -First 3 | ForEach-Object { "$($_.TimeCreated)  $($_.Id)  $($_.ProviderName)" }
```

Bu veride geçen olay kimlikleri:

| Id | Sağlayıcı | Anlamı |
|---|---|---|
| 6005 / 6006 | EventLog | olay günlüğü hizmeti başladı (sistem açıldı) / durdu (düzgün kapandı) |
| 6008 | EventLog | önceki kapanış beklenmedikti |
| 41 | Kernel-Power | sistem düzgün kapatılmadan yeniden başladı |
| 1074 | User32 | bir kullanıcı ya da işlem yeniden başlatmayı başlattı (sebebiyle) |
| 7036 | Service Control Manager | bir hizmetin durumu değişti |
| 1000 | Application Error | bir uygulama çöktü |
| 19 / 20 | WindowsUpdateClient | güncelleme yüklendi / yüklenemedi |
| 153 | disk | disk G/Ç işlemi yeniden denendi |

Zaman metin olarak gelir; karşılaştırmak ya da biçimlemek için `[datetime]`'a çevir:

```powershell
$olaylar = Get-Content olaylar.json -Raw -Encoding UTF8 | ConvertFrom-Json
$ilk = [datetime]$olaylar[0].TimeCreated
$ilk.ToString("yyyy-MM-dd HH:mm")
$ilk.DayOfWeek
```

> [!TUZAK]
> Windows PowerShell 5.1'de `ConvertFrom-Json` bir JSON dizisini boru hattına **tek bir nesne** olarak gönderir: `... | ConvertFrom-Json | Where-Object ...` yazarsan `Where-Object` 23 olayı değil tek bir diziyi görür. Sonucu önce bir değişkene ata, sonra değişkeni boruya ver: `$olaylar | Where-Object ...`. (PowerShell 7'de bu davranış düzeltildi.)
:::

::: tahmin
Üç satır yazar:

```powershell
$olaylar = Get-Content olaylar.json -Raw -Encoding UTF8 | ConvertFrom-Json
$olaylar.Count
($olaylar | Where-Object Level -le 2).Count
($olaylar | Select-Object -ExpandProperty Id -Unique).Count
```

???

`23`, `7`, `10`. Dosyada 23 olay var. Level 2 ve altı (Kritik ya da Hata) yedi tane: dört uygulama çökmesi (1000), bir başarısız güncelleme (20), bir Kernel-Power (41) ve bir beklenmedik kapanış (6008). Farklı olay kimliği sayısı 10'dur.
:::

::: gorev Hatalar ve kritikler
Önemi **Hata ya da Kritik** olan olayları zaman sırasıyla, her biri bir satırda `yyyy-MM-dd HH:mm Id ProviderName` biçiminde yazdır.

```cikti
2026-10-12 10:15 1000 Application Error
2026-10-14 09:40 1000 Application Error
...
```

```starter
$olaylar = Get-Content olaylar.json -Raw -Encoding UTF8 | ConvertFrom-Json
$olaylar | ForEach-Object { "$($_.TimeCreated) $($_.Id) $($_.ProviderName)" }
```

```test
import json
o = json.load(open("olaylar.json", encoding="utf-8"))
beklenen = "".join(f"{e['TimeCreated'][:10]} {e['TimeCreated'][11:16]} {e['Id']} {e['ProviderName']}\n"
                   for e in sorted(o, key=lambda e: e["TimeCreated"]) if e["Level"] <= 2)
eq(out, beklenen, "yedi olay, zaman sırasıyla, istenen biçimde")
ok("level" in src.lower(), "Level numarasıyla süz")
```

```solution
$olaylar = Get-Content olaylar.json -Raw -Encoding UTF8 | ConvertFrom-Json
$olaylar |
    Where-Object Level -le 2 |
    Sort-Object { [datetime]$_.TimeCreated } |
    ForEach-Object { "{0} {1} {2}" -f ([datetime]$_.TimeCreated).ToString("yyyy-MM-dd HH:mm"), $_.Id, $_.ProviderName }
```

```hint
`Where-Object Level -le 2` ile süz; zamanı biçimlemek için `([datetime]$_.TimeCreated).ToString("yyyy-MM-dd HH:mm")`.
```
:::

::: gorev Sağlayıcıya göre
Olayları `ProviderName`'e göre grupla ve `Ad: Sayı` biçiminde, **çoktan aza**, eşitlikte ada göre artan sırayla yazdır.

```starter
$olaylar = Get-Content olaylar.json -Raw -Encoding UTF8 | ConvertFrom-Json
$olaylar | Group-Object ProviderName | ForEach-Object { "$($_.Name): $($_.Count)" }
```

```test
import json
from collections import Counter
o = json.load(open("olaylar.json", encoding="utf-8"))
sayim = sorted(Counter(e["ProviderName"] for e in o).items(), key=lambda kv: (-kv[1], kv[0].lower()))
eq(out, "".join(f"{ad}: {n}\n" for ad, n in sayim), "çoktan aza, eşitlikte ada göre")
```

```solution
$olaylar = Get-Content olaylar.json -Raw -Encoding UTF8 | ConvertFrom-Json
$olaylar |
    Group-Object ProviderName |
    Sort-Object @{ Expression = "Count"; Descending = $true }, Name |
    ForEach-Object { "$($_.Name): $($_.Count)" }
```

```hint
`Sort-Object Count, Name -Descending` ikisini de azalan sıralar. Yönleri ayrı vermek için hashtable: `Sort-Object @{ Expression = "Count"; Descending = $true }, Name`.
```
:::

::: gorev Günlük uyarı sayısı
Önemi **Uyarı ya da daha ciddi** (Level 3 ve altı) olan olayları güne göre say; `yyyy-MM-dd: sayı` biçiminde gün sırasıyla yazdır.

```starter
$olaylar = Get-Content olaylar.json -Raw -Encoding UTF8 | ConvertFrom-Json
$olaylar | Where-Object Level -le 3 | Measure-Object | Select-Object -ExpandProperty Count
```

```test
import json
from collections import Counter
o = json.load(open("olaylar.json", encoding="utf-8"))
gunler = sorted(Counter(e["TimeCreated"][:10] for e in o if e["Level"] <= 3).items())
eq(out, "".join(f"{g}: {n}\n" for g, n in gunler), "günlere göre sayılar")
```

```solution
$olaylar = Get-Content olaylar.json -Raw -Encoding UTF8 | ConvertFrom-Json
$olaylar |
    Where-Object Level -le 3 |
    Group-Object { ([datetime]$_.TimeCreated).ToString("yyyy-MM-dd") } |
    Sort-Object Name |
    ForEach-Object { "$($_.Name): $($_.Count)" }
```

```hint
`Group-Object`'e bir özellik adı yerine bir betik bloğu da verebilirsin: `Group-Object { ([datetime]$_.TimeCreated).ToString("yyyy-MM-dd") }`.
```
:::
