---
id: ps02
title: Girdi ve Parametreler
summary: param() bloğu, türlü ve varsayılan parametreler, isimli argümanlar, [switch] ve tezgahtaki $Girdi.
---

::: anlat param(): betiğin imzası
PowerShell betikleri ve fonksiyonları girdilerini en başta bir **`param()` bloğuyla** tanımlar. Bu, betiği bir cmdlet gibi kullanılabilir yapar:

```powershell
param(
    [string]$Hedef = "localhost",          #! tür + varsayılan değer
    [int]$Port = 22,
    [switch]$Ayrintili                     #! bayrak: varsa $true
)
"Hedef: ${Hedef}:${Port}"
if ($Ayrintili) { "ayrıntılı mod açık" }
```

Böyle bir betik şu yollarla çağrılabilir:

```powershell norun
.\tara.ps1                                 # varsayılanlar
.\tara.ps1 web01 443                       # konumsal
.\tara.ps1 -Port 8443 -Hedef db01          # isimli: sıra serbest
.\tara.ps1 web01 -Ayrintili                # bayrak
```

İsimli argümanlar okunabilirliği artırır ve sırayı önemsiz kılar. Tür belirtmek (`[int]$Port`) PowerShell'in gelen metni dönüştürmesini ve dönüşemiyorsa açık bir hata vermesini sağlar.

> [!NOT]
> `param()` betiğin **ilk** ifadesi olmalıdır (yorumlar ve boş satırlar hariç). Ondan önce başka bir satır yazarsan parametreler tanınmaz.

### Tezgahta girdi: $Girdi
Gerçek hayatta veri boru hattından, dosyadan (`Get-Content`) ya da parametrelerden gelir; etkileşimli soru için `Read-Host` kullanılır. Tezgahta ise alttaki **Girdi** kutusunun satırları senin için hazır bir dizide durur: **`$Girdi`**.

```powershell
"Kaç satır geldi: $($Girdi.Count)"
foreach ($satir in $Girdi) { "> $satir" }
```

Bu örneği tezgaha al, Girdi kutusuna birkaç satır yaz ve çalıştır.
:::

::: tahmin
Betik argümansız çalıştırılırsa ne yazar?

```powershell
param([string]$Ad = "dünya", [int]$Tekrar = 2)
1..$Tekrar | ForEach-Object { "Merhaba $Ad #$_" }
```

???

`Merhaba dünya #1`, sonra `Merhaba dünya #2`. Varsayılanlar devreye girer. `1..2` bir aralıktır, `ForEach-Object` her eleman için bloğu çalıştırır ve `$_` o anki elemandır (PS05).
:::

::: gorev Selamla
`$Girdi`'nin ilk satırındaki adı kullanarak `Merhaba, <ad>!` yazdır.

```starter
# $Girdi[0] ilk satırdır

```

```stdin
Ali
```

```test
eq(run("Ali\n"), "Merhaba, Ali!\n", "Ali")
eq(run("Ayşe Yılmaz\n"), "Merhaba, Ayşe Yılmaz!\n", "boşluklu ad")
```

```solution
$ad = $Girdi[0]
"Merhaba, $ad!"
```

```hint
`$Girdi[0]` ilk satır. Çift tırnak içinde `"Merhaba, $ad!"`.
```
:::

::: gorev Varsayılan hedef
Betik `Hedef` adında bir parametre alsın, varsayılanı `localhost` olsun ve `Hedef: <hedef>` yazdırsın. Hem konumsal (`web01`) hem isimli (`-Hedef db01`) çağrı çalışmalı.

```starter
$Hedef = $args[0]
"Hedef: $Hedef"
```

```test
eq(run(), "Hedef: localhost\n", "argümansız → localhost")
eq(run(argv=["web01"]), "Hedef: web01\n", "konumsal")
eq(run(argv=["-Hedef", "db01"]), "Hedef: db01\n", "isimli")
ok("param" in src.lower(), "param() bloğu kullan")
```

```solution
param([string]$Hedef = "localhost")
"Hedef: $Hedef"
```

```hint
`param([string]$Hedef = "localhost")` betiğin ilk satırı olmalı.
```
:::

::: gorev Ayrıntılı bayrak
Betik `[switch]` türünde `-Ayrintili` bayrağı alsın: bayrak yoksa `kısa rapor`, varsa `ayrıntılı rapor` yazdırsın. Ayrıca `[int]` türünde `-Satir` parametresi (varsayılan 3) alsın ve ikinci satıra `satır: N` yazdırsın.

```starter
"kısa rapor"
```

```test
eq(run(), "kısa rapor\nsatır: 3\n", "varsayılanlar")
eq(run(argv=["-Ayrintili"]), "ayrıntılı rapor\nsatır: 3\n", "bayrakla")
eq(run(argv=["-Satir", "10", "-Ayrintili"]), "ayrıntılı rapor\nsatır: 10\n", "isimli parametre + bayrak")
```

```solution
param([switch]$Ayrintili, [int]$Satir = 3)
if ($Ayrintili) { "ayrıntılı rapor" } else { "kısa rapor" }
"satır: $Satir"
```

```hint
`param([switch]$Ayrintili, [int]$Satir = 3)`. Bayrak `if ($Ayrintili)` ile sınanır.
```
:::
