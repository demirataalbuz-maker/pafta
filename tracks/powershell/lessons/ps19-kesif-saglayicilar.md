---
id: ps19
title: Keşif ve Sağlayıcılar
summary: Get-Command ve Get-Member ile kendi kendine keşif; PSProvider ve PSDrive mimarisi (Variable:, Env:, Function:, HKLM:).
kazanim: AZ040 1.3, AZ040 4.1, AZ040 4.2
---

::: anlat Ezberleme, kabuğa sor
PowerShell'de binlerce cmdlet vardır; hiçbir sistem yöneticisi veya analist hepsinin parametrelerini ezbere bilmez. Dil, kendi kendini anlatacak şekilde tasarlanmıştır. Üç temel keşif aracı `Get-Command`, `Get-Help` ve `Get-Member`'dır:

```powershell
Get-Command -Verb ConvertTo, ConvertFrom |
    Select-Object Name, Version |
    Sort-Object Name                               #! dönüştürme ailesindeki tüm cmdlet'ler
```

Bir komutun hangi parametre kümelerini (`ParameterSets`) ve hangi parametre türlerini kabul ettiğini doğrudan komut nesnesinden okuyabilirsin:

```powershell
$cmd = Get-Command Get-ChildItem
$cmd.ParameterSets | ForEach-Object { $_.Name }    #! Items ve LiteralItems kümeleri
$cmd.Parameters["Recurse"].SwitchParameter         #! -Recurse bir şalter (switch) parametresidir
```

```powershell norun
Get-Help Get-WinEvent -Examples                    #! yalnız örnekleri göster
Get-Help Get-WinEvent -Parameter FilterHashtable   #! tek parametrenin ayrıntısı
```

> [!İPUCU] `Get-Command -Syntax` kısayolu
> Yardım dosyaları güncellenmemiş bir sunucuda bile `Get-Command Get-WinEvent -Syntax` komutu anında çalışır ve bütün parametre kümelerinin imzasını gösterir.
:::

::: anlat Sağlayıcılar (PSProvider) ve Sürücüler (PSDrive)
PowerShell'de `Get-ChildItem`, `Get-Item` ve `Set-Item` yalnızca dosya sistemi için değildir. **Sağlayıcı (Provider)** mimarisi sayesinde ortam değişkenleri (`Env:`), oturum değişkenleri (`Variable:`), fonksiyonlar (`Function:`) ve Windows Kayıt Defteri (`HKLM:`, `HKCU:`) tıpkı birer klasörmüş gibi gezilir:

```powershell
Get-PSProvider | Select-Object Name, Drives        #! yüklü sağlayıcılar ve sürücü adları
```

```powershell
$sayac = 42
Get-Item Variable:\sayac | Select-Object Name, Value
Set-Item Env:\PAFTA_ORTAM "laboratuvar"
Get-Content Env:\PAFTA_ORTAM                      #! ortam değişkenini dosya gibi oku
```

Kayıt defteri incelemelerinde `HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run` gibi anahtarlar da aynı `Get-ItemProperty` ve `Get-ChildItem` komutlarıyla okunur.

> [!DERİN] `Env:PATH` ile `$env:PATH` aynı sağlayıcıya bakar
> `$env:PAFTA_ORTAM` yazımı aslında `Env:` sağlayıcısının kısayoludur. Değişkenin adını çalışma zamanında bir metin değişkeninden (`$ad = "PAFTA_ORTAM"`) okuyacaksan `Get-Item "Env:\$ad"` veya `(Get-Item "Variable:\$ad").Value` kullanmak, `Invoke-Expression` kullanmaktan çok daha güvenlidir.
:::

::: tahmin
Üç satır yazar:

```powershell
$alfa_1 = 10
$alfa_2 = 25
$beta_1 = 99
$secilen = Get-ChildItem Variable:\alfa_* | Sort-Object Name
$secilen.Count
$secilen[0].Name
($secilen | Measure-Object -Property Value -Sum).Sum
```

???

`2`, `alfa_1`, `35`. `Variable:\alfa_*` deseni adı `alfa_` ile başlayan iki değişkeni (`alfa_1` ve `alfa_2`) getirir. İlk eleman `alfa_1`, değerlerinin toplamı `10 + 25 = 35` olur.
:::

::: gorev Parametre araştırmacısı
`$Girdi` dizisinin ilk satırında verilen cmdlet adının (`Select-Object` gibi) sahip olduğu **Switch (`SwitchParameter` olan)** parametrelerin adlarını alfabetik sırayla, her satıra bir ad gelecek şekilde yazdır. Ancak tüm cmdlet'lerde ortak olan standart parametreleri (`Verbose`, `Debug`, `ErrorAction`, `WarningAction`, `InformationAction`, `ErrorVariable`, `WarningVariable`, `InformationVariable`, `OutVariable`, `OutBuffer`, `PipelineVariable`, `WhatIf`, `Confirm`) dışarıda bırak.

```stdin
Select-Object
```

```starter
$komutAdi = $Girdi[0].Trim()
$cmd = Get-Command $komutAdi
$cmd.Parameters.Keys | Sort-Object
```

```test
ortak = {"Verbose", "Debug", "ErrorAction", "WarningAction", "InformationAction",
         "ErrorVariable", "WarningVariable", "InformationVariable", "OutVariable",
         "OutBuffer", "PipelineVariable", "WhatIf", "Confirm"}
satirlar = [s.strip() for s in out.splitlines() if s.strip()]
ok("Unique" in satirlar and "First" not in satirlar, "Select-Object için Unique switch'tir, First değildir")
ok(not (set(satirlar) & ortak), "ortak parametreler (Verbose vb.) elenmeli")
ok(satirlar == sorted(satirlar), "alfabetik sıralı olmalı")
ikinci = [s.strip() for s in run(stdin="Sort-Object\n").splitlines() if s.strip()]
ok("Descending" in ikinci and "Unique" in ikinci and "Property" not in ikinci, "Sort-Object için Descending ve Unique switch olmalı")
```

```solution
$ortak = @(
    "Verbose", "Debug", "ErrorAction", "WarningAction", "InformationAction",
    "ErrorVariable", "WarningVariable", "InformationVariable", "OutVariable",
    "OutBuffer", "PipelineVariable", "WhatIf", "Confirm"
)
$komutAdi = $Girdi[0].Trim()
$cmd = Get-Command $komutAdi
$cmd.Parameters.Values |
    Where-Object { $_.SwitchParameter -and ($_.Name -notin $ortak) } |
    Select-Object -ExpandProperty Name |
    Sort-Object
```

```hint
`$cmd.Parameters.Values` içindeki her parametre nesnesinin `$_.SwitchParameter` özelliği `$true` ise o parametre bir şalterdir.
```
:::

::: gorev Değişken sürücüsü denetimi
Betiğin başında tanımlanan `$ayar_*` değişkenlerini `Variable:` sürücüsü üzerinden bul. Değeri tam sayı (`[int]`) olanları ada göre sırala ve `ad=değer` biçiminde yazdır.

```starter
$ayar_port = 8080
$ayar_ad = "srv-01"
$ayar_zaman_asimi = 30
$ayar_aktif = $true
$ayar_deneme = 3

# Variable: sürücüsünden $ayar_* değişkenlerini süz
```

```test
eq(out, "ayar_deneme=3\nayar_port=8080\nayar_zaman_asimi=30\n", "yalnızca [int] değerindeki ayar_* değişkenleri")
ok("variable:" in src.lower(), "Variable: sağlayıcısını kullanmalısın")
kod2 = src.replace("$ayar_port = 8080", "$ayar_port = 9090\n$ayar_pencere = 15")
eq(run_code(kod2), "ayar_deneme=3\nayar_pencere=15\nayar_port=9090\nayar_zaman_asimi=30\n", "yeni değişken eklendiğinde sonuç güncellenmeli")
```

```solution
$ayar_port = 8080
$ayar_ad = "srv-01"
$ayar_zaman_asimi = 30
$ayar_aktif = $true
$ayar_deneme = 3

Get-ChildItem Variable:\ayar_* |
    Where-Object { $_.Value -is [int] } |
    Sort-Object Name |
    ForEach-Object { "$($_.Name)=$($_.Value)" }
```

```hint
`Get-ChildItem Variable:\ayar_*` ile değişkenleri al; `Where-Object { $_.Value -is [int] }` ile yalnızca tam sayı olanları süz.
```
:::

::: gorev Ortam yapılandırma raporu
`$Girdi` satırlarında `ANAHTAR=DEĞER` biçiminde verilen çiftleri `Env:` sürücüsüne (`Set-Item "Env:\$anahtar" $deger`) kaydet. Ardından `Env:` sürücüsünde adı `PAFTA_` ile başlayan tüm ortam değişkenlerini ada göre sıralayarak `ANAHTAR: DEĞER` biçiminde yazdır.

```stdin
PAFTA_MOD=koruma
PAFTA_BOLGE=eu-west
DIGER_DEGISKEN=gecici
PAFTA_ADIM=3
```

Yalnız bu girdide atanan `PAFTA_` anahtarlarını raporla; üst süreçten gelen Pafta kurulum ayarlarını rapora katma.

```starter
foreach ($satir in $Girdi) {
    # Satırı = işaretinden böl ve Env: sürücüsüne yaz
}
```

```test
eq(out, "PAFTA_ADIM: 3\nPAFTA_BOLGE: eu-west\nPAFTA_MOD: koruma\n", "PAFTA_ ortam değişkenleri sıralı")
ok("env:" in src.lower(), "Env: sürücüsü kullanılmalı")
eq(run(stdin="PAFTA_SUNUCU=web09\nTEST_YOK=1\n"), "PAFTA_SUNUCU: web09\n", "farklı girdide doğru çalışmalı")
```

```solution
$gelen = @()
foreach ($satir in $Girdi) {
    if ($satir -match '^([^=]+)=(.*)$') {
        $gelen += $Matches[1]
        Set-Item "Env:\$($Matches[1])" $Matches[2]
    }
}
Get-ChildItem Env:\PAFTA_* |
    Where-Object { $_.Name -in $gelen } |
    Sort-Object Name |
    ForEach-Object { "$($_.Name): $($_.Value)" }
```

```hint
`$satir.Split("=", 2)` ya da `-match '^([^=]+)=(.*)$'` ile anahtar ve değeri ayırıp `Set-Item "Env:\$anahtar" $deger` ile kaydet; sonra `Get-ChildItem Env:\PAFTA_*` ile oku.
```
:::
