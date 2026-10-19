---
id: ps14
title: Gelişmiş Fonksiyonlar II
summary: SupportsShouldProcess ile -WhatIf ve -Confirm, Write-Verbose ve -Verbose, parametre setleri, özelliğe göre boru hattı bağlama, [switch] ve doğrulama öznitelikleri.
---

::: anlat Fonksiyonu cmdlet gibi davrandırmak
PS06'da `[CmdletBinding()]` ile tanıştın. Bu öznitelik fonksiyona, gerçek cmdlet'lerin bütün ortak parametrelerini kazandırır: `-Verbose`, `-ErrorAction`, `-WhatIf`... Bu derste o ortak parametreleri kendi fonksiyonlarında kullanmayı öğreneceksin.

### -WhatIf: "ne yapardın?"
Değişiklik yapan bir fonksiyon `SupportsShouldProcess` bildirir ve her değişiklikten önce `$PSCmdlet.ShouldProcess(hedef, eylem)` diye sorar. `-WhatIf` verilmişse bu çağrı "şunu yapardım" yazar ve `$false` döner; değişiklik yapılmaz:

```powershell
function Remove-GeciciDosya {
    [CmdletBinding(SupportsShouldProcess)]
    param([string]$Klasor = ".")
    Get-ChildItem -Path $Klasor -Filter *.tmp | ForEach-Object {
        if ($PSCmdlet.ShouldProcess($_.Name, "Sil")) {     #! -WhatIf'te false döner
            Remove-Item $_.FullName
            "silindi: $($_.Name)"
        }
    }
}
Set-Content a.tmp "x"
Remove-GeciciDosya -WhatIf
Test-Path a.tmp
```

### -Verbose: teşhis mesajları
`Write-Verbose` mesajları varsayılan olarak görünmez; kullanıcı `-Verbose` verdiğinde `VERBOSE:` önekiyle görünür. Fonksiyonun dönüş değerine karışmazlar (PS06'daki "her çıktı dönüş değeridir" tuzağının ilacı):

```powershell
function Get-Toplam {
    [CmdletBinding()]
    param([int[]]$Sayilar)
    Write-Verbose "$($Sayilar.Count) sayı toplanıyor"
    ($Sayilar | Measure-Object -Sum).Sum
}
Get-Toplam 1, 2, 3
Get-Toplam 1, 2, 3 -Verbose
```

### Parametre setleri
Bir fonksiyon birbirini dışlayan farklı çağrılma biçimleri sunabilir: ya adıyla ya rolüyle. Her parametre bir **sete** konur; PowerShell verilen parametrelere bakarak hangi setin kullanıldığını anlar ve iki seti karıştıran çağrıyı reddeder:

```powershell
function Find-Sunucu {
    [CmdletBinding(DefaultParameterSetName = "Ad")]
    param(
        [Parameter(ParameterSetName = "Ad", Mandatory)][string]$Ad,
        [Parameter(ParameterSetName = "Rol", Mandatory)][string]$Rol
    )
    "kullanılan set: $($PSCmdlet.ParameterSetName)"
}
Find-Sunucu -Ad web01
Find-Sunucu -Rol web
```

### Özelliğe göre boru hattı bağlama
`ValueFromPipelineByPropertyName`, boru hattından gelen nesnenin **aynı adlı özelliğini** parametreye bağlar. Böylece `Import-Csv`'den gelen satırlar doğrudan fonksiyona akar:

```powershell
function Show-Kayit {
    param([Parameter(ValueFromPipelineByPropertyName)][string]$Ad,
          [Parameter(ValueFromPipelineByPropertyName)][int]$Cpu)
    process { "{0,-8} {1,3}" -f $Ad, $Cpu }
}
@"
Ad,Cpu,Rol
web01,72,web
db01,91,db
"@ | ConvertFrom-Csv | Show-Kayit
```

| Öznitelik | Ne denetler |
|---|---|
| `[ValidateNotNullOrEmpty()]` | boş olamaz |
| `[ValidatePattern('^web\d+$')]` | düzenli ifadeye uymalı |
| `[ValidateScript({ Test-Path $_ })]` | betik bloğu `$true` döndürmeli |
| `[switch]$Zorla` | değersiz bayrak: verilirse `$true` |

> [!NOT]
> Bir fonksiyon değişiklik yapıyorsa (siler, yazar, durdurur) `SupportsShouldProcess` bildirmek iyi bir PowerShell vatandaşlığıdır: kullanıcı onu `-WhatIf` ile önce güvenle deneyebilir.
:::

::: tahmin
İki satır yazar:

```powershell
function Test-Bag {
    param([Parameter(ValueFromPipelineByPropertyName)][string]$Ad,
          [Parameter(ValueFromPipelineByPropertyName)][int]$Cpu)
    process { "$Ad=$Cpu" }
}
[pscustomobject]@{ Ad = "web01"; Cpu = 72; Rol = "web" },
[pscustomobject]@{ Ad = "db01"; Cpu = 91 } | Test-Bag
```

???

`web01=72` ve `db01=91`. Her nesnenin `Ad` ve `Cpu` özellikleri aynı adlı parametrelere bağlanır; fazladan `Rol` özelliği yok sayılır. `process` bloğu her nesne için bir kez çalışır.
:::

::: gorev -WhatIf destekli temizlik
`Remove-GeciciDosya` fonksiyonunu tamamla: çalışma klasöründeki `.tmp` dosyalarını silsin, her biri için `silindi: ad` döndürsün ve **-WhatIf** desteklesin. Betik `-Deneme` anahtarıyla çağrılırsa fonksiyonu `-WhatIf` ile çalıştırsın.

```setup
for ad in ["a.tmp", "b.tmp", "kalsin.txt"]:
    open(ad, "w", newline="\n").write("x")
```

```starter
param([switch]$Deneme)
function Remove-GeciciDosya {
    Get-ChildItem -Filter *.tmp | Sort-Object Name | ForEach-Object {
        Remove-Item $_.FullName
        "silindi: $($_.Name)"
    }
}
Remove-GeciciDosya
```

```meta
argv: -Deneme
```

```test
import os
ok(os.path.exists("a.tmp") and os.path.exists("b.tmp"), "-WhatIf ile hiçbir dosya silinmemeli")
ok("silindi" not in out, "-WhatIf ile 'silindi' satırı çıkmamalı", got=out)
eq(run(), "silindi: a.tmp\nsilindi: b.tmp\n", "gerçek çalıştırma")
ok(not os.path.exists("a.tmp") and os.path.exists("kalsin.txt"), "yalnızca .tmp dosyaları silindi")
ok("SupportsShouldProcess" in src, "SupportsShouldProcess kullan")
```

```solution
param([switch]$Deneme)
function Remove-GeciciDosya {
    [CmdletBinding(SupportsShouldProcess)]
    param()
    Get-ChildItem -Filter *.tmp | Sort-Object Name | ForEach-Object {
        if ($PSCmdlet.ShouldProcess($_.Name, "Sil")) {
            Remove-Item $_.FullName
            "silindi: $($_.Name)"
        }
    }
}
Remove-GeciciDosya -WhatIf:$Deneme
```

```hint
`[CmdletBinding(SupportsShouldProcess)]` ve `param()` ekle; silmeyi `if ($PSCmdlet.ShouldProcess($_.Name, "Sil")) { ... }` içine al.
```

```hint
Anahtarı ortak parametreye aktarmak: `Remove-GeciciDosya -WhatIf:$Deneme`.
```
:::

::: gorev Parametre setleri
`Find-Sunucu` fonksiyonu ya `-Ad` ya `-Rol` ile çağrılsın (ikisi birden **olmasın**). `-Ad` ile o sunucunun rolünü, `-Rol` ile o roldeki sunucuların adlarını (virgülle, alfabetik) döndürsün. Betiğin sonundaki üç çağrı aynen kalmalı.

```starter
$sunucular = @{ web01 = "web"; web02 = "web"; db01 = "db" }
function Find-Sunucu {
    param([string]$Ad, [string]$Rol)
    if ($Ad) { $sunucular[$Ad] }
    else { ($sunucular.Keys | Where-Object { $sunucular[$_] -eq $Rol } | Sort-Object) -join "," }
}
Find-Sunucu -Ad db01
Find-Sunucu -Rol web
try { Find-Sunucu -Ad db01 -Rol web -ErrorAction Stop; "kabul edildi" } catch { "reddedildi" }
```

```test
eq(out, "db\nweb01,web02\nreddedildi\n", "iki geçerli çağrı ve reddedilen karışık çağrı")
ok("ParameterSetName" in src, "parametre setleri kullan")
```

```solution
$sunucular = @{ web01 = "web"; web02 = "web"; db01 = "db" }
function Find-Sunucu {
    [CmdletBinding(DefaultParameterSetName = "Ad")]
    param(
        [Parameter(ParameterSetName = "Ad", Mandatory)][string]$Ad,
        [Parameter(ParameterSetName = "Rol", Mandatory)][string]$Rol
    )
    if ($PSCmdlet.ParameterSetName -eq "Ad") { $sunucular[$Ad] }
    else { ($sunucular.Keys | Where-Object { $sunucular[$_] -eq $Rol } | Sort-Object) -join "," }
}
Find-Sunucu -Ad db01
Find-Sunucu -Rol web
try { Find-Sunucu -Ad db01 -Rol web -ErrorAction Stop; "kabul edildi" } catch { "reddedildi" }
```

```hint
Her parametreyi ayrı bir sete koy: `[Parameter(ParameterSetName = "Ad", Mandatory)]`. İki seti birden kullanan çağrıyı PowerShell kendisi reddeder.
```
:::

::: gorev Ayrıntılı kip
`Get-Ortalama` fonksiyonu sayıların ortalamasını döndürsün; `Write-Verbose` ile `N sayı işleniyor` mesajı versin. Betik `-Ayrintili` anahtarıyla çağrılırsa fonksiyonu `-Verbose` ile çalıştırsın. Mesaj, dönüş değerine karışmamalı.

```starter
param([switch]$Ayrintili)
function Get-Ortalama {
    param([double[]]$Sayilar)
    "$($Sayilar.Count) sayı işleniyor"
    ($Sayilar | Measure-Object -Average).Average
}
$sonuc = Get-Ortalama 2, 4, 9
"ortalama: $sonuc"
```

```test
eq(out, "ortalama: 5\n", "ayrıntısız")
cikti = run(argv=["-Ayrintili"])
ok("VERBOSE: 3 sayı işleniyor" in cikti, "ayrıntılı kipte VERBOSE mesajı", got=cikti)
ok(cikti.rstrip().endswith("ortalama: 5"), "dönüş değeri temiz kalmalı", got=cikti)
```

```solution
param([switch]$Ayrintili)
function Get-Ortalama {
    [CmdletBinding()]
    param([double[]]$Sayilar)
    Write-Verbose "$($Sayilar.Count) sayı işleniyor"
    ($Sayilar | Measure-Object -Average).Average
}
$sonuc = Get-Ortalama 2, 4, 9 -Verbose:$Ayrintili
"ortalama: $sonuc"
```

```hint
Düz metin satırı dönüş değerine karışıyor. `Write-Verbose` kullan ve fonksiyona `[CmdletBinding()]` ekle ki `-Verbose` parametresini tanısın.
```
:::
