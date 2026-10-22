---
id: ps20
title: CIM, Modüller ve Uzaktan Yönetim
summary: Get-CimInstance ile işletim sistemi sorguları, New-Module ve Export-ModuleMember ile kapsülleme, ScriptBlock ve Invoke-Command kalıbı, Start-Job, Wait-Job, Receive-Job ve Remove-Job ile arka plan işlerinin yaşam döngüsü.
kazanim: AZ040 5.1, AZ040 5.2, AZ040 7.5, AZ040 8.1, AZ040 11.1
---

::: anlat CIM ile makine röntgeni
Windows yönetim altyapısı (WMI / CIM), işletim sisteminin donanımını, süreçlerini, servislerini ve oturumlarını standart sınıflar (`Win32_OperatingSystem`, `Win32_Process`, `Win32_Service`, `Win32_LogicalDisk`) olarak sunar. Modern PowerShell'de eski `Get-WmiObject` yerine WS-Man tabanlı **`Get-CimInstance`** kullanılır:

```powershell
$os = Get-CimInstance -ClassName Win32_OperatingSystem
$os | Select-Object Caption, Version, OSArchitecture
```

CIM sorgularında en önemli kural **sol tarafta süzmektir (Filter Left)**: bütün örnekleri çekip `Where-Object` ile elemek yerine, WQL sözdizimiyle `-Filter` parametresini kullanmak yalnız eşleşen nesneleri getirir:

```powershell
Get-CimInstance -ClassName Win32_Service -Filter "State = 'Running' AND StartMode = 'Auto'" |
    Select-Object -First 3 Name, State, StartMode
```

> [!TUZAK] WQL `-Filter` içinde PowerShell işleçleri kullanılmaz
> `-Filter` parametresi PowerShell'e değil doğrudan CIM sağlayıcısına gider. Bu yüzden içeride `-eq` ve `-and` değil, SQL benzeri `=`, `AND`, `OR` ve `LIKE` (`Name LIKE 'Win%'`) yazılır!
:::

::: anlat Modüller (`New-Module`) ve Uzaktan Yönetim (`ScriptBlock`)
Büyüyen betikleri tek dosyada tutmak yerine yeniden kullanılabilir bir **modül** (`.psm1`) içine alırız. Modül içinde yardımcı fonksiyonlar gizli kalabilir; dışarıya yalnızca `Export-ModuleMember` ile seçilen fonksiyonlar açılır:

```powershell
$m = New-Module -Name PaftaAraclar -ScriptBlock {
    function _IcYardimci($x) { $x.Trim().ToUpper() }
    function Format-Etiket($metin) { "[PAFTA:$(_IcYardimci $metin)]" }
    Export-ModuleMember -Function Format-Etiket
} | Import-Module -PassThru

Format-Etiket "  analiz  "                         #! dışarıya açık fonksiyon
$m.ExportedFunctions.Keys                          #! _IcYardimci dışarıdan görünmez
```

Uzaktan yönetim (`Invoke-Command -ComputerName SRV01 -ScriptBlock { ... }`) ve arka plan işleri (`Start-Job -ScriptBlock { ... }`) kodu bir **`[scriptblock]`** nesnesi olarak taşır. Betik bloğunun içindeki kod uzak makinede (veya ayrı bir süreçte) çalıştığı için yerel değişkenleri doğrudan görmez; değerler `param(...)` ve `-ArgumentList` (ya da `$using:degisken`) ile geçirilir:

```powershell
$blok = {
    param($Esik, $Kayitlar)
    $Kayitlar | Where-Object { $_.Gun -ge $Esik } | Select-Object -ExpandProperty Sunucu
}
$veri = @(
    [pscustomobject]@{ Sunucu = "web01"; Gun = 45 }
    [pscustomobject]@{ Sunucu = "db01";  Gun = 12 }
)
Invoke-Command -ScriptBlock $blok -ArgumentList 30, $veri   #! yerel oturumda aynı kalıpla çalıştır
```

> [!DERİN] Neden `Invoke-Command -ScriptBlock` yerelde de kullanılır?
> Yerel makinede `-ComputerName` vermeden çağrılan `Invoke-Command -ScriptBlock $sb -ArgumentList ...`, uzak sunucularda çalıştıracağın denetim bloğunu ağ bağlantısı açmadan önce birebir aynı parametre sözleşmesiyle test etmeni sağlar.
:::

::: anlat Arka plan işleri: Start-Job'dan Remove-Job'a
Uzun süren bir işi (büyük bir günlüğü taramak, birkaç sunucuyu yoklamak) beklerken oturumu kilitlemek istemezsin. `Start-Job` betik bloğunu **ayrı bir PowerShell sürecinde** başlatır ve hemen bir **iş nesnesi** döndürür. Bir işin yaşam döngüsü dört adımdır:

| Adım | Komut | Ne yapar |
|---|---|---|
| başlat | `Start-Job -ScriptBlock {...} -ArgumentList ...` | işi başlatır, iş nesnesini döndürür (`Id`, `Name`, `State`) |
| bekle | `Wait-Job` | iş ya da işler bitene kadar bekler; `-Timeout` ile saniye sınırı verilebilir |
| sonucu al | `Receive-Job` | işin çıktısını getirir; alınan çıktıyı varsayılan olarak işten **siler** (`-Keep` ile kalır) |
| temizle | `Remove-Job` | iş nesnesini oturumdan kaldırır |

`Get-Job` oturumdaki işleri listeler. `State` alanı `Running`, `Completed`, `Failed` ya da `Stopped` olur. İşler ayrı süreçte çalıştığı için yerel değişkenleri görmez; değerler, `Invoke-Command`'daki gibi `param(...)` ve `-ArgumentList` ile geçer:

```powershell
$isler = foreach ($n in 3, 5) {
    Start-Job -ScriptBlock { param($x) $x * $x } -ArgumentList $n
}
$isler | Wait-Job | Out-Null            #! ikisi de bitene kadar bekle
$isler | ForEach-Object { $_.State }    #! Completed, Completed
$isler | Receive-Job                    #! 9 ve 25: işlerin çıktısı
$isler | Remove-Job                     #! oturumu temizle
(Get-Job).Count                         #! 0
```

Kısa yolu da var: `Start-Job {...} | Receive-Job -Wait -AutoRemoveJob` bekler, sonucu alır ve işi siler.

> [!TUZAK]
> Bir **diziyi** tek argüman olarak geçirmek istiyorsan `-ArgumentList (,$dizi)` yaz. `-ArgumentList $dizi` dizinin elemanlarını ayrı ayrı argümanlara dağıtır: `param([int[]]$Sayilar)` yalnızca ilk elemanı alır.

> [!TUZAK]
> İşin içindeki bir hata **senin oturumunda yükselmez**. İş `Failed` ya da `Completed` olarak biter, hata da `Receive-Job` çağrıldığında hata akışına yazılır. İşlerin `State` değerine bak ve `Receive-Job`'u unutma. `Remove-Job` yazmazsan bitmiş işler ve çıktıları oturum kapanana kadar bellekte kalır.

> [!NOT]
> `Start-Job` her iş için yeni bir `powershell.exe` süreci açar; başlaması zaman alır. Çok kısa işlerde bu bedel kazançtan büyüktür. PowerShell 7'de daha hafif `Start-ThreadJob` ve satır sonuna `&` koyma sözdizimi vardır; Pafta tezgahı Windows PowerShell 5.1 kullanır.
:::

::: tahmin
Üç satır yazar:

```powershell
$m = New-Module -Name SayacModulu -ScriptBlock {
    $script:adim = 10
    function _GizliArtir($n) { $script:adim += $n }
    function Add-Adim($n) { _GizliArtir $n; return $script:adim }
    Export-ModuleMember -Function Add-Adim
} | Import-Module -PassThru

$m.ExportedFunctions.Count
Add-Adim 5
Add-Adim 3
```

???

`1`, `15`, `18`. Modül yalnızca `Add-Adim` fonksiyonunu dışarıya açtığı için `ExportedFunctions.Count` `1`'dir. `$script:adim` modül kapsamında yaşar; ilk çağrı `10 + 5 = 15`, ikinci çağrı `15 + 3 = 18` döndürür.
:::

::: gorev Modül kapsüllemesi
`New-Module` kullanarak şunları yapan bir modül oluşturup içe aktar (`Import-Module`):
- `_Maskele($ip)` adında **gizli** (dışarıya açılmayan) bir fonksiyon IP adresinin son oktetini `xxx` yapsın (`10.20.30.45` → `10.20.30.xxx`).
- `ConvertTo-GuvenliKayit($kullanici, $ip)` adında **dışa açık** (`Export-ModuleMember`) bir fonksiyon `"$kullanici@$(_Maskele $ip)"` metnini döndürsün.
Ardından `$Girdi` satırlarındaki `kullanici,ip` çiftlerini bu fonksiyonla dönüştürüp yazdır.

```stdin
ali,10.0.12.44
ayse,192.168.1.9
```

```starter
$m = New-Module -Name KayitGizleyici -ScriptBlock {
    function _Maskele($ip) {
        # Son okteti xxx yap
    }
    function ConvertTo-GuvenliKayit($kullanici, $ip) {
        "$kullanici@$ip"
    }
    # Yalnız ConvertTo-GuvenliKayit fonksiyonunu dışa aç
} | Import-Module -PassThru

foreach ($s in $Girdi) {
    $k, $ip = $s.Split(",")
    ConvertTo-GuvenliKayit $k $ip
}
```

```test
eq(out, "ali@10.0.12.xxx\nayse@192.168.1.xxx\n", "maskelenmiş kayıtlar")
ok("Export-ModuleMember" in src, "Export-ModuleMember kullanmalısın")
ek = "\n[bool](Get-Command _Maskele -ErrorAction SilentlyContinue)\n[bool](Get-Command ConvertTo-GuvenliKayit -ErrorAction SilentlyContinue)\n"
son_iki = run_code(src + ek, stdin="veli,172.16.5.200\n").splitlines()
eq(son_iki, ["veli@172.16.5.xxx", "False", "True"], "_Maskele gizli kalmalı, ConvertTo-GuvenliKayit açık olmalı")
```

```solution
$m = New-Module -Name KayitGizleyici -ScriptBlock {
    function _Maskele($ip) {
        $parcalar = $ip.Split(".")
        "$($parcalar[0]).$($parcalar[1]).$($parcalar[2]).xxx"
    }
    function ConvertTo-GuvenliKayit($kullanici, $ip) {
        "$kullanici@$(_Maskele $ip)"
    }
    Export-ModuleMember -Function ConvertTo-GuvenliKayit
} | Import-Module -PassThru

foreach ($s in $Girdi) {
    $k, $ip = $s.Split(",")
    ConvertTo-GuvenliKayit $k $ip
}
```

```hint
`_Maskele` içinde `$ip -replace '\.\d+$', '.xxx'` veya `$ip.Split(".")` kullanabilirsin. Modül sonunda `Export-ModuleMember -Function ConvertTo-GuvenliKayit` yazmayı unutma.
```
:::

::: gorev WQL filtre üreticisi
Uzak sunucularda `Get-CimInstance -ClassName Win32_Service -Filter ...` ile kullanılacak WQL sorgu metnini üreten `New-ServisFiltresi($durum, $baslangic, $onek)` fonksiyonunu yaz. Fonksiyon tam olarak şu biçimde bir WQL metni döndürsün:
`State = '<durum>' AND StartMode = '<baslangic>' AND Name LIKE '<onek>%'`
`$Girdi` içindeki `durum|baslangic|onek` satırları için üretilen filtreleri sırayla yazdır.

```stdin
Running|Auto|Win
Stopped|Manual| Wua
```

```starter
function New-ServisFiltresi($durum, $baslangic, $onek) {
    "State -eq '$durum'"
}

foreach ($satir in $Girdi) {
    $d, $b, $o = $satir.Split("|") | ForEach-Object { $_.Trim() }
    New-ServisFiltresi $d $b $o
}
```

```test
beklenen = (
    "State = 'Running' AND StartMode = 'Auto' AND Name LIKE 'Win%'\n"
    "State = 'Stopped' AND StartMode = 'Manual' AND Name LIKE 'Wua%'\n"
)
eq(out, beklenen, "WQL filtre metinleri")
eq(run(stdin="Running|Disabled|Spool\n"), "State = 'Running' AND StartMode = 'Disabled' AND Name LIKE 'Spool%'\n", "farklı girdide doğru WQL")
```

```solution
function New-ServisFiltresi($durum, $baslangic, $onek) {
    "State = '$durum' AND StartMode = '$baslangic' AND Name LIKE '$onek%'"
}

foreach ($satir in $Girdi) {
    $d, $b, $o = $satir.Split("|") | ForEach-Object { $_.Trim() }
    New-ServisFiltresi $d $b $o
}
```

```hint
WQL içinde eşitlik `=`, mantıksal bağlaç `AND`, önek eşleşmesi ise `LIKE '$onek%'` biçimindedir.
```
:::

::: gorev Denetim ScriptBlock'u
`$DenetimBlok` adında bir `[scriptblock]` tanımla: `param([int]$MinMb, [object[]]$Surecler)` parametrelerini alsın; `Calisma Kümesi (MB)` değeri (`WorkingSetMb`) `$MinMb` değerine **eşit veya büyük** olan süreçleri `WorkingSetMb` değerine göre **çoktan aza** sıralayıp `"$($_.Ad): $($_.WorkingSetMb) MB"` biçiminde döndürsün. Blok `Invoke-Command -ScriptBlock $DenetimBlok -ArgumentList ...` ile çalıştırılıyor.

```stdin
250
sqlservr,640
notdefteri,45
arama,250
tarayici,410
```

```starter
$minMb = [int]$Girdi[0]
$surecler = $Girdi[1..($Girdi.Count - 1)] | ForEach-Object {
    $ad, $mb = $_.Split(",")
    [pscustomobject]@{ Ad = $ad; WorkingSetMb = [int]$mb }
}

$DenetimBlok = {
    param([int]$MinMb, [object[]]$Surecler)
    # Eşikten büyük veya eşit olanları çoktan aza sıralayıp biçimle
}

Invoke-Command -ScriptBlock $DenetimBlok -ArgumentList $minMb, $surecler
```

```test
eq(out, "sqlservr: 640 MB\ntarayici: 410 MB\narama: 250 MB\n", "tam 250 MB sınır değer dahil, çoktan aza sıralı")
ok("Invoke-Command" in src and "-ScriptBlock" in src, "Invoke-Command -ScriptBlock kullanılmalı")
girdi2 = "500\nsqlservr,640\ntarayici,500\nyedek,499\n"
eq(run(stdin=girdi2), "sqlservr: 640 MB\ntarayici: 500 MB\n", "500 MB sınırında 500 dahil, 499 hariç")
```

```solution
$minMb = [int]$Girdi[0]
$surecler = $Girdi[1..($Girdi.Count - 1)] | ForEach-Object {
    $ad, $mb = $_.Split(",")
    [pscustomobject]@{ Ad = $ad; WorkingSetMb = [int]$mb }
}

$DenetimBlok = {
    param([int]$MinMb, [object[]]$Surecler)
    $Surecler |
        Where-Object { $_.WorkingSetMb -ge $MinMb } |
        Sort-Object WorkingSetMb -Descending |
        ForEach-Object { "$($_.Ad): $($_.WorkingSetMb) MB" }
}

Invoke-Command -ScriptBlock $DenetimBlok -ArgumentList $minMb, $surecler
```

```hint
Betik bloğu içinde `$Surecler | Where-Object { $_.WorkingSetMb -ge $MinMb } | Sort-Object WorkingSetMb -Descending` borusunu kur.
```
:::

::: gorev İşlerle paralel toplam
`$Girdi`'nin ilk satırı bir eşik, kalan satırlar `ad:sayı,sayı,...` biçiminde. Her satır için bir **arka plan işi** başlat: iş, sayıları `-ArgumentList` ile alsın ve toplamlarını döndürsün. Bütün işleri bekle (`Wait-Job`), sonuçları **girdideki sırayla** al (`Receive-Job`) ve her satır için `ad toplam` yazdır; toplam eşiğe **eşit ya da büyükse** satırın sonuna ` !` ekle. Sonunda bütün işleri kaldır (`Remove-Job`).

```stdin
20
web01:3,5,9
db01:10,10
cache01:4,4,4
```

```starter
$esik = [int]$Girdi[0]
$satirlar = $Girdi[1..($Girdi.Count - 1)]
foreach ($satir in $satirlar) {
    $ad, $liste = $satir.Split(":")
    $sayilar = [int[]]$liste.Split(",")
    # Burada toplamı hesaplayan bir iş başlat
}
```

```test
eq(out, "web01 17\ndb01 20 !\ncache01 12\n", "girdideki sırayla toplamlar; tam 20 eşiğe dahil")
for komut in ("Start-Job", "Wait-Job", "Receive-Job", "Remove-Job"):
    ok(komut in src, f"{komut} kullanmalısın")
eq(run(stdin="10\na:9\nb:10\nc:4,7\n"), "a 9\nb 10 !\nc 11 !\n", "eşik 10: 9 hariç, 10 ve 11 dahil")
son = run_code(src + "\n(Get-Job).Count\n", stdin="5\nx:1,2\n").splitlines()
eq(son, ["x 3", "0"], "tek işte de çalışmalı ve bitince oturumda iş kalmamalı")
```

```solution
$esik = [int]$Girdi[0]
$satirlar = $Girdi[1..($Girdi.Count - 1)]
$isler = foreach ($satir in $satirlar) {
    $ad, $liste = $satir.Split(":")
    $sayilar = [int[]]$liste.Split(",")
    Start-Job -ScriptBlock {
        param([int[]]$Sayilar)
        ($Sayilar | Measure-Object -Sum).Sum
    } -ArgumentList (,$sayilar)
}
$isler | Wait-Job | Out-Null
for ($i = 0; $i -lt $satirlar.Count; $i++) {
    $ad = $satirlar[$i].Split(":")[0]
    $toplam = Receive-Job -Job @($isler)[$i]
    $isaret = if ($toplam -ge $esik) { " !" } else { "" }
    "$ad $toplam$isaret"
}
$isler | Remove-Job
```

```hint
`Start-Job -ScriptBlock { param([int[]]$Sayilar) ... } -ArgumentList (,$sayilar)`: diziyi tek argüman olarak geçirmek için başına virgül koy. İşleri bir değişkende topla (`$isler = foreach (...) { Start-Job ... }`).
```

```hint
Sırayı korumak için işleri girdideki sırayla `Receive-Job -Job @($isler)[$i]` ile al. `@(...)` tek iş olduğunda da diziyle çalışmanı sağlar. Sonda `$isler | Remove-Job`.
```
:::
