---
id: ps12
title: Süzmek, Zaman Aralıkları ve Mesajlar
summary: FilterHashtable ile kaynağında süzmek, yarı açık zaman aralıkları, olay mesajından -match ile bilgi çıkarmak ve parametreli günlük araçları.
---

::: anlat Kaynağında süzmek
Gerçek bir makinede günlükte yüz binlerce olay olabilir. `Get-WinEvent | Where-Object ...` hepsini okuyup PowerShell'e taşır, sonra süzer: yavaştır. `-FilterHashtable` ise süzmeyi **olay günlüğü hizmetine** yaptırır; yalnızca eşleşenler gelir:

```powershell
$baslangic = (Get-Date).AddDays(-7)
Get-WinEvent -FilterHashtable @{ LogName = "System"; Level = 1, 2; StartTime = $baslangic } -ErrorAction SilentlyContinue |
    Select-Object -First 5 TimeCreated, Id, ProviderName
```

| Anahtar | Ne süzer |
|---|---|
| `LogName` | günlük adı (zorunlu ya da `ProviderName`) |
| `Id` | olay kimliği, birden çok olabilir: `Id = 6005, 6006` |
| `Level` | önem numarası |
| `StartTime`, `EndTime` | zaman aralığı |
| `ProviderName` | olayı yazan bileşen |

`-ErrorAction SilentlyContinue`, hiç olay bulunamadığında çıkan "eşleşen olay yok" hatasını susturur.

### Zaman aralıkları
Bir günü ya da saati seçerken **yarı açık** aralık kullan: başlangıç dahil, bitiş hariç. Böylece gece yarısındaki bir olay iki güne birden sayılmaz:

```powershell
$olaylar = Get-Content olaylar.json -Raw -Encoding UTF8 | ConvertFrom-Json
$bas = [datetime]"2026-10-16"
$son = $bas.AddDays(1)
$olaylar | Where-Object { $t = [datetime]$_.TimeCreated; $t -ge $bas -and $t -lt $son } |
    ForEach-Object { "$($_.TimeCreated) $($_.Id)" }
```

### Mesajdan bilgi çıkarmak
Olayın asıl ayrıntısı çoğu zaman `Message` metnindedir. `-match` başarılı olunca yakalanan gruplar `$Matches` değişkenine dolar (Regex yolundaki desenler burada işe yarar):

```powershell
$olaylar = Get-Content olaylar.json -Raw -Encoding UTF8 | ConvertFrom-Json
foreach ($o in $olaylar | Where-Object Id -eq 1000) {
    if ($o.Message -match 'adı: (?<uygulama>[^,]+), sürüm: (?<surum>\S+)') {
        "$($Matches.uygulama) $($Matches.surum)"
    }
}
```

> [!TUZAK]
> `$Matches` yalnızca **başarılı** bir `-match`'ten sonra güncellenir. Eşleşmeyen bir satırda önceki eşleşmenin değeri olduğu gibi kalır ve yanlış veri üretirsin. Her zaman `if ($x -match ...) { ... }` içinde kullan.
:::

::: tahmin
Tek sayı:

```powershell
$olaylar = Get-Content olaylar.json -Raw -Encoding UTF8 | ConvertFrom-Json
$bas = [datetime]"2026-10-16"
$son = $bas.AddDays(1)
($olaylar | Where-Object { [datetime]$_.TimeCreated -ge $bas -and [datetime]$_.TimeCreated -lt $son }).Count
```

???

`5`. 16 Ekim'de beş olay var: gece 02:17'de Kernel-Power (41), ardından beklenmedik kapanış kaydı (6008) ve açılış (6005), sabah iki disk uyarısı (153).
:::

::: gorev Çöken uygulamalar
Uygulama çökmesi olaylarının (Id 1000) mesajından uygulama adını çıkar ve her uygulamanın kaç kez çöktüğünü `ad: sayı` biçiminde, çoktan aza yazdır.

```cikti
rapor.exe: 3
tarayici.exe: 1
```

```starter
$olaylar = Get-Content olaylar.json -Raw -Encoding UTF8 | ConvertFrom-Json
$olaylar | Where-Object Id -eq 1000 | ForEach-Object { $_.Message }
```

```test
eq(out, "rapor.exe: 3\ntarayici.exe: 1\n", "uygulama başına çökme sayısı")
ok("-match" in src.lower(), "-match ile mesajdan çıkar")
```

```solution
$olaylar = Get-Content olaylar.json -Raw -Encoding UTF8 | ConvertFrom-Json
$olaylar |
    Where-Object Id -eq 1000 |
    ForEach-Object { if ($_.Message -match 'adı: ([^,]+)') { $Matches[1] } } |
    Group-Object |
    Sort-Object @{ Expression = "Count"; Descending = $true }, Name |
    ForEach-Object { "$($_.Name): $($_.Count)" }
```

```hint
Mesaj `Hatalı uygulama adı: rapor.exe, sürüm: 2.4.1` biçiminde. Desen: `'adı: ([^,]+)'`; virgüle kadar olan kısım.
```
:::

::: gorev Güncellemelerin son durumu
Güncelleme olaylarından (Id 19 başarılı, Id 20 başarısız) her KB numarası için **en son** denemenin sonucunu ve deneme sayısını `KB: durum (n deneme)` biçiminde, KB'ye göre sıralı yazdır.

```cikti
KB5031234: başarılı (1 deneme)
KB5031999: başarılı (2 deneme)
```

```starter
$olaylar = Get-Content olaylar.json -Raw -Encoding UTF8 | ConvertFrom-Json
$olaylar | Where-Object { $_.Id -in 19, 20 } | ForEach-Object { $_.Message }
```

```test
eq(out, "KB5031234: başarılı (1 deneme)\nKB5031999: başarılı (2 deneme)\n", "her KB'nin son durumu")
import json
o = json.load(open("olaylar.json", encoding="utf-8"))
o.append({"Id": 20, "Level": 2, "LevelDisplayName": "Hata", "ProviderName": "Microsoft-Windows-WindowsUpdateClient",
          "LogName": "System", "MachineName": "SRV-WEB01", "TimeCreated": "2026-10-19T03:00:00",
          "Message": "Güncelleme yüklenemedi: KB5031999"})
with open("olaylar.json", "w", encoding="utf-8") as f:
    json.dump(o, f, ensure_ascii=False)
eq(run(), "KB5031234: başarılı (1 deneme)\nKB5031999: başarısız (3 deneme)\n", "yeni bir başarısız deneme eklenince son durum değişmeli")
```

```solution
$olaylar = Get-Content olaylar.json -Raw -Encoding UTF8 | ConvertFrom-Json
$olaylar |
    Where-Object { $_.Id -in 19, 20 } |
    ForEach-Object {
        if ($_.Message -match '(KB\d+)') {
            [pscustomobject]@{ KB = $Matches[1]; Zaman = [datetime]$_.TimeCreated; Basarili = $_.Id -eq 19 }
        }
    } |
    Group-Object KB |
    Sort-Object Name |
    ForEach-Object {
        $son = $_.Group | Sort-Object Zaman | Select-Object -Last 1
        $durum = if ($son.Basarili) { "başarılı" } else { "başarısız" }
        "$($_.Name): $durum ($($_.Count) deneme)"
    }
```

```hint
Her olaydan bir `[pscustomobject]` (KB, zaman, başarılı mı) üret, sonra `Group-Object KB`.
```

```hint
Grubun içindeki en son deneme: `$_.Group | Sort-Object Zaman | Select-Object -Last 1`.
```
:::

::: gorev Aralıktaki olaylar
Betik `$Bas` ve `$Son` adlı iki `[datetime]` parametresi alsın ve `[Bas, Son)` aralığındaki (başlangıç dahil, bitiş hariç) olay sayısını `N olay` biçiminde yazdırsın.

```starter
param([datetime]$Bas, [datetime]$Son)
$olaylar = Get-Content olaylar.json -Raw -Encoding UTF8 | ConvertFrom-Json
"$($olaylar.Count) olay"
```

```meta
argv: 2026-10-16 2026-10-17
```

```test
eq(out, "5 olay\n", "16 Ekim: 5 olay")
eq(run(argv=["2026-10-12", "2026-10-13"]), "4 olay\n", "12 Ekim: 4 olay")
eq(run(argv=["2026-10-16 02:00", "2026-10-16 02:18:30"]), "2 olay\n", "bitiş anı hariç: 02:18:30'daki açılış sayılmaz")
eq(run(argv=["2026-10-12", "2026-10-19"]), "23 olay\n", "bütün hafta")
```

```solution
param([datetime]$Bas, [datetime]$Son)
$olaylar = Get-Content olaylar.json -Raw -Encoding UTF8 | ConvertFrom-Json
$sayi = @($olaylar | Where-Object { $t = [datetime]$_.TimeCreated; $t -ge $Bas -and $t -lt $Son }).Count
"$sayi olay"
```

```hint
`$t -ge $Bas -and $t -lt $Son`; hiç olay kalmazsa da çalışması için sonucu `@( ... )` ile diziye sar.
```
:::
