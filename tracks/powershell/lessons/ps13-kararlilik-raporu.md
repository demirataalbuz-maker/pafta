---
id: ps13
title: Proje · Açılış ve Kararlılık Raporu
summary: Olayları zaman çizelgesine dizip her açılışın sebebini bulan, çökme özetini çıkaran bir rapor betiği.
---

::: anlat Proje tanımı
SRV-WEB01 bu hafta birkaç kez yeniden başladı ve bir uygulama ara ara çöküyor. Ekip, olay günlüğünden şu soruların cevabını istiyor:

1. Sunucu **ne zaman** açıldı?
2. Her açılıştan önce ne oldu: **planlı** bir yeniden başlatma mı, **beklenmedik** bir kapanma mı?
3. Haftanın kısa özeti: kaç açılış, kaçı beklenmedik, en çok hangi uygulama çöktü?

Bir olay günlüğünü incelemenin temel tekniği **zaman çizelgesidir**: olayları zamana göre diz ve her önemli olayın öncesine bak. Bu veride açılışı `6005` işaretler. Bir önceki açılışla bu açılış arasındaki olaylar sebebi söyler:

| Aradaki olay | Anlamı |
|---|---|
| `41` ya da `6008` | sistem düzgün kapanmadı: **beklenmedik** |
| `1074` | biri yeniden başlatmayı başlattı: **planlı**, sebebi mesajda |
| önceki açılış kayıtlarda yok | **bilinmiyor** |

```powershell
$olaylar = Get-Content olaylar.json -Raw -Encoding UTF8 | ConvertFrom-Json
$olaylar |
    Where-Object { $_.Id -in 6005, 6006, 6008, 41, 1074 } |
    Sort-Object { [datetime]$_.TimeCreated } |
    ForEach-Object { "{0}  {1,5}  {2}" -f $_.TimeCreated, $_.Id, $_.Message }
```

> [!İPUCU]
> Zaman çizelgesi yöntemi her günlük incelemesinde aynıdır: önce olayları süz ve sırala, sonra "bundan hemen önce ne oldu?" diye sor. Bu ders boyunca aynı kalıbı kullanacaksın: olayları zaman sırasıyla dolaşan tek bir `foreach` ve geçmişi hatırlayan birkaç değişken.
:::

::: gorev 1 · Açılışlar
Sunucunun her açılışını (Id 6005) `yyyy-MM-dd HH:mm` biçiminde, zaman sırasıyla yazdır.

```cikti
2026-10-12 07:00
2026-10-13 03:08
2026-10-16 02:18
2026-10-18 22:03
```

```starter
$olaylar = Get-Content olaylar.json -Raw -Encoding UTF8 | ConvertFrom-Json
$olaylar | Where-Object Id -eq 6006 | ForEach-Object { $_.TimeCreated }
```

```test
eq(out, "2026-10-12 07:00\n2026-10-13 03:08\n2026-10-16 02:18\n2026-10-18 22:03\n", "dört açılış")
```

```solution
$olaylar = Get-Content olaylar.json -Raw -Encoding UTF8 | ConvertFrom-Json
$olaylar |
    Where-Object Id -eq 6005 |
    Sort-Object { [datetime]$_.TimeCreated } |
    ForEach-Object { ([datetime]$_.TimeCreated).ToString("yyyy-MM-dd HH:mm") }
```

```hint
Açılış 6005'tir (6006 kapanıştır). Biçim: `([datetime]$_.TimeCreated).ToString("yyyy-MM-dd HH:mm")`.
```
:::

::: gorev 2 · Açılışın sebebi
Her açılışı sebebiyle birlikte yazdır: `yyyy-MM-dd HH:mm · sebep`. Sebep, önceki açılışla bu açılış arasındaki olaylara göre belirlenir: 41 ya da 6008 varsa `beklenmedik`; yoksa 1074 varsa `planlı: <mesajdaki sebep>`; önceki açılış kayıtlarda yoksa ya da ikisi de yoksa `bilinmiyor`.

```cikti
2026-10-12 07:00 · bilinmiyor
2026-10-13 03:08 · planlı: Windows Update
2026-10-16 02:18 · beklenmedik
2026-10-18 22:03 · planlı: bakım
```

```starter
$olaylar = Get-Content olaylar.json -Raw -Encoding UTF8 | ConvertFrom-Json
$olaylar |
    Where-Object Id -eq 6005 |
    Sort-Object { [datetime]$_.TimeCreated } |
    ForEach-Object { ([datetime]$_.TimeCreated).ToString("yyyy-MM-dd HH:mm") + " · bilinmiyor" }
```

```test
eq(out, "2026-10-12 07:00 · bilinmiyor\n2026-10-13 03:08 · planlı: Windows Update\n2026-10-16 02:18 · beklenmedik\n2026-10-18 22:03 · planlı: bakım\n", "dört açılış ve sebepleri")
import json
o = [e for e in json.load(open("olaylar.json", encoding="utf-8")) if e["Id"] not in (41, 6008)]
with open("olaylar.json", "w", encoding="utf-8") as f:
    json.dump(o, f, ensure_ascii=False)
eq(run().splitlines()[2], "2026-10-16 02:18 · bilinmiyor", "41 ve 6008 olmayınca üçüncü açılışın sebebi bilinmiyor olmalı")
```

```solution
$olaylar = Get-Content olaylar.json -Raw -Encoding UTF8 | ConvertFrom-Json
$oncekiAcilisVar = $false
$pencere = @()
foreach ($o in $olaylar | Sort-Object { [datetime]$_.TimeCreated }) {
    if ($o.Id -ne 6005) {
        $pencere += $o
        continue
    }
    $sebep = "bilinmiyor"
    if ($oncekiAcilisVar) {
        $planli = $pencere | Where-Object Id -eq 1074 | Select-Object -Last 1
        if ($pencere | Where-Object { $_.Id -in 41, 6008 }) {
            $sebep = "beklenmedik"
        } elseif ($planli -and $planli.Message -match 'yeniden başlatma: (.+)$') {
            $sebep = "planlı: " + $Matches[1]
        }
    }
    ([datetime]$o.TimeCreated).ToString("yyyy-MM-dd HH:mm") + " · " + $sebep
    $oncekiAcilisVar = $true
    $pencere = @()
}
```

```hint
Olayları zaman sırasıyla tek bir `foreach` ile dolaş. 6005 olmayan olayları bir "pencere" dizisinde biriktir; 6005 gelince pencereye bak, satırı yaz, pencereyi boşalt.
```

```hint
İlk açılıştan önce elimizde kayıt yok: bunu bir `$oncekiAcilisVar` bayrağıyla izle. Sebep metni 1074'ün mesajında: `'yeniden başlatma: (.+)$'`.
```
:::

::: gorev 3 · Haftanın özeti
Üç satırlık bir özet yazdır: toplam açılış sayısı, kaçının beklenmedik olduğu (öncesinde 41 ya da 6008 bulunan açılışlar) ve en çok çöken uygulama (Id 1000) ile çökme sayısı.

```cikti
açılış: 4
beklenmedik: 1
en çok çöken: rapor.exe (3)
```

```starter
$olaylar = Get-Content olaylar.json -Raw -Encoding UTF8 | ConvertFrom-Json
"açılış: " + @($olaylar | Where-Object Id -eq 6005).Count
```

```test
eq(out, "açılış: 4\nbeklenmedik: 1\nen çok çöken: rapor.exe (3)\n", "haftanın özeti")
import json
o = json.load(open("olaylar.json", encoding="utf-8"))
for saat in ("10", "11", "12"):
    o.append({"Id": 1000, "Level": 2, "LevelDisplayName": "Hata", "ProviderName": "Application Error", "LogName": "Application",
              "MachineName": "SRV-WEB01", "TimeCreated": f"2026-10-19T{saat}:00:00", "Message": "Hatalı uygulama adı: tarayici.exe, sürüm: 118.0"})
with open("olaylar.json", "w", encoding="utf-8") as f:
    json.dump(o, f, ensure_ascii=False)
eq(run().splitlines()[2], "en çok çöken: tarayici.exe (4)", "veri değişince en çok çöken uygulama değişmeli")
```

```solution
$olaylar = Get-Content olaylar.json -Raw -Encoding UTF8 | ConvertFrom-Json
$acilis = 0
$beklenmedik = 0
$pencere = @()
foreach ($o in $olaylar | Sort-Object { [datetime]$_.TimeCreated }) {
    if ($o.Id -ne 6005) {
        $pencere += $o
        continue
    }
    $acilis++
    if ($pencere | Where-Object { $_.Id -in 41, 6008 }) { $beklenmedik++ }
    $pencere = @()
}
$enCok = $olaylar |
    Where-Object Id -eq 1000 |
    ForEach-Object { if ($_.Message -match 'adı: ([^,]+)') { $Matches[1] } } |
    Group-Object |
    Sort-Object Count -Descending |
    Select-Object -First 1

"açılış: $acilis"
"beklenmedik: $beklenmedik"
"en çok çöken: $($enCok.Name) ($($enCok.Count))"
```

```hint
Açılış ve beklenmedik sayıları için 2. görevdeki zaman çizelgesi döngüsünü kullan; sebep metni yerine sayaç artır.
```

```hint
En çok çöken uygulama: mesajlardan adları çıkar, `Group-Object`, `Sort-Object Count -Descending`, `Select-Object -First 1`.
```
:::
