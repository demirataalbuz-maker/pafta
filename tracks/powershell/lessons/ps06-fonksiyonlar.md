---
id: ps06
title: Fonksiyonlar
summary: Fiil-İsim fonksiyonlar, her çıktının dönüş değeri olması, doğrulama öznitelikleri ve boru hattından girdi.
kazanim: AZ040 7.5
---

::: anlat Fonksiyon tanımlamak
```powershell
function Get-Kare {
    param([int]$Sayi)
    $Sayi * $Sayi                    #! çıktıya yazılan değer = dönüş değeri
}
Get-Kare -Sayi 7                     #! isimli
Get-Kare 9                           #! konumsal
$sonuc = Get-Kare 4
"sonuç: $sonuc"
```

Adlandırmada da `Fiil-İsim` geleneğine uy ve onaylı fiilleri kullan (`Get-Verb` listeyi verir): `Get-`, `Set-`, `New-`, `Remove-`, `Test-`, `Invoke-`...

### Her çıktı dönüş değeridir
PowerShell'in en şaşırtıcı kuralı: fonksiyonun içinde boru hattına yazılan **her şey** dönüş değerine eklenir; sadece `return`'deki değil:

```powershell
function Topla($a, $b) {
    "hesaplanıyor..."                #! bu da dönüş değerine girer!
    return $a + $b
}
$s = Topla 2 3
$s.Count                             #! 2: bir metin + bir sayı
$s[1]
```

Teşhis mesajı yazmak istiyorsan `Write-Verbose`, `Write-Host` ya da `Write-Warning` kullan; bunlar dönüş değerine karışmaz. Bir komutun çıktısını yutmak için `$null = komut` ya da `komut | Out-Null`.

### Gelişmiş fonksiyonlar
`[CmdletBinding()]` ve parametre öznitelikleri fonksiyonu gerçek bir cmdlet gibi yapar: doğrulama, zorunlu parametre, boru hattından girdi:

```powershell
function Test-Port {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][ValidateRange(1, 65535)][int]$Port,
        [ValidateSet("tcp", "udp")][string]$Protokol = "tcp"
    )
    "$Protokol/$Port geçerli"
}
Test-Port -Port 443
try { Test-Port -Port 70000 } catch { "reddedildi: aralık dışı" }
```

### Boru hattından girdi: process {}
```powershell
function Add-Onek {
    param([Parameter(ValueFromPipeline)][string]$Metin, [string]$Onek = "> ")
    begin   { $n = 0 }                     #! bir kez, başta
    process { $n++; "$Onek$n $Metin" }     #! her nesne için
    end     { "toplam $n" }                #! bir kez, sonda
}
"alfa", "beta" | Add-Onek
```
:::

::: tahmin
Çıktıyı satır satır yaz:

```powershell
function Topla($a, $b) {
    "hesaplanıyor"
    return $a + $b
}
$sonuc = Topla 2 3
$sonuc.Count
$sonuc[1]
```

???

`2`, sonra `5`. Fonksiyon iki şey çıktıladı: `"hesaplanıyor"` metni ve `return` ile 5. İkisi de dönüş değerine girdi ve `$sonuc` iki elemanlı bir dizi oldu.
:::

::: gorev Kare fonksiyonu
`Get-Kare` adında, `[int]$Sayi` parametresi alan ve karesini **döndüren** (başka hiçbir şey çıktılamayan) bir fonksiyon yaz. Betik `Get-Kare 7` sonucunu yazdırsın.

```starter
function Get-Kare {
    param([int]$Sayi)
    "kare hesaplanıyor"
    $Sayi * $Sayi
}
Get-Kare 7
```

```test
eq(out, "49\n", "Get-Kare 7 → 49 (başka çıktı yok)")
ok("function get-kare" in src.lower(), "Get-Kare fonksiyonunu tanımla")
```

```solution
function Get-Kare {
    param([int]$Sayi)
    $Sayi * $Sayi
}
Get-Kare 7
```

```hint
Fonksiyonun içindeki fazladan metin satırı da dönüş değerine giriyor; onu sil ya da `Write-Verbose` yap.
```
:::

::: gorev Port sınıfı
`Get-PortSinifi` fonksiyonunu yaz: `[ValidateRange(0, 65535)][int]$Port` parametresi alsın ve `sistem` (0–1023), `kayıtlı` (1024–49151) ya da `dinamik` (49152–65535) döndürsün. Betik `$Girdi`'nin her satırı için sonucu yazdırsın; aralık dışı ya da sayı olmayan satırlarda `geçersiz` yazsın (doğrulama hatasını `try/catch` ile yakala).

```starter
function Get-PortSinifi {
    param([int]$Port)
    "sistem"
}
foreach ($satir in $Girdi) { Get-PortSinifi $satir }
```

```stdin
22
8080
```

```test
eq(run("22\n8080\n50000\n70000\nabc\n1023\n").splitlines(), ["sistem", "kayıtlı", "dinamik", "geçersiz", "geçersiz", "sistem"], "sınıflar")
ok("validaterange" in src.lower(), "ValidateRange kullan")
```

```solution
function Get-PortSinifi {
    param([ValidateRange(0, 65535)][int]$Port)
    if ($Port -le 1023) { "sistem" }
    elseif ($Port -le 49151) { "kayıtlı" }
    else { "dinamik" }
}
foreach ($satir in $Girdi) {
    try {
        Get-PortSinifi $satir
    } catch {
        "geçersiz"
    }
}
```

```hint
Doğrulama ya da tür dönüşümü başarısız olunca parametre bağlama hatası yükselir; çağrıyı `try { ... } catch { "geçersiz" }` içine al.
```
:::

::: gorev Boru hattı fonksiyonu
`Add-SatirNo` adında, boru hattından metin alan bir fonksiyon yaz: her satırın başına `N: ` eklesin (1'den başlayarak). Betik `$Girdi | Add-SatirNo` çıktısını versin.

```starter
function Add-SatirNo {
    param([string]$Metin)
    "1: $Metin"
}
$Girdi | Add-SatirNo
```

```stdin
alfa
beta
gama
```

```test
eq(run("alfa\nbeta\ngama\n"), "1: alfa\n2: beta\n3: gama\n", "numaralı satırlar")
eq(run("tek\n"), "1: tek\n", "tek satır")
ok("process" in src.lower(), "process bloğu kullan")
```

```solution
function Add-SatirNo {
    param([Parameter(ValueFromPipeline)][string]$Metin)
    begin { $n = 0 }
    process {
        $n++
        "${n}: $Metin"
    }
}
$Girdi | Add-SatirNo
```

```hint
Parametreye `[Parameter(ValueFromPipeline)]` ekle; sayaç için `begin { $n = 0 }`, her satır için `process { ... }`.
```
:::
