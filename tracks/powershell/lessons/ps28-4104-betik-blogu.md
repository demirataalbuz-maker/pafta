---
id: ps28
title: PowerShell 4104 · Betik Bloğu Kayıtlarını Birleştirmek
summary: Microsoft-Windows-PowerShell/Operational günlüğündeki 4104 (Script Block Logging) olayının alanları (MessageNumber, MessageTotal, ScriptBlockText, ScriptBlockId, Path), uyarı seviyesindeki otomatik kayıt, 4103 ve 4105 komşuları; uzun bir bloğun parçalara bölünmesi, parçaların karışık ve ters sırada kaydedilmesi, ScriptBlockId ile gruplayıp MessageNumber'a göre sayısal sıralayarak birleştirmek, eksik parçayı fark etmek ve birleşmiş metinde düz (joker ve regex'siz), büyük/küçük harfe duyarsız arama.
kazanim: AZ040 2.3, AZ040 3.2
---

::: anlat 4104: PowerShell'in çalıştırdığı kodun kendisi
PowerShell bir betik bloğunu (bir betik dosyası, konsolda yazılan bir satır, `-Command` ile verilen metin, `Invoke-Expression`'a giden dizgi) derlerken metnini `Microsoft-Windows-PowerShell/Operational` günlüğüne **4104** olayı olarak yazabilir. Saldırgan kodu karıştırsa, şifrelese de PowerShell sonunda **çalıştırdığı metni** görür; olay müdahalesinde 4104 bu yüzden ilk bakılan kayıtlardandır.

| Olay | Ne zaman |
|---|---|
| **4104** | Betik bloğu kaydı (Script Block Logging). İlke açıkken her blok **Level 5** (Verbose) olarak yazılır. İlke kapalıyken de PowerShell şüpheli bulduğu blokları **Level 3** (Warning) olarak kendiliğinden yazar |
| **4103** | Modül kaydı: komut çağrıları ve parametre bağlama |
| **4105** / **4106** | Bir bloğun çalışmaya başlaması ve bitmesi (yalnız çağrı kaydı açıkken) |

4104'ün `EventData` alanları her zaman bu sıradadır:

```powershell norun
<EventData>
  <Data Name='MessageNumber'>1</Data>
  <Data Name='MessageTotal'>3</Data>
  <Data Name='ScriptBlockText'>$istemci = New-Object Net.Web</Data>
  <Data Name='ScriptBlockId'>{6f1e0c2a-0002-4b5c-9d00-5afe00000002}</Data>
  <Data Name='Path'></Data>
</EventData>
```

| Sıra | Alan | Anlamı |
|---|---|---|
| `Properties[0]` | `MessageNumber` | Bu parça kaçıncı |
| `Properties[1]` | `MessageTotal` | Blok kaç parça |
| `Properties[2]` | `ScriptBlockText` | Metnin bu parçası |
| `Properties[3]` | `ScriptBlockId` | Bloğun kimliği: parçaları birleştiren anahtar |
| `Properties[4]` | `Path` | Blok bir dosyadan geldiyse yolu; konsolda yazıldıysa boş |

```setup
import os, runpy, sys
_s = os.path.dirname(next(m.__file__ for m in list(sys.modules.values())
                          if getattr(m, "__file__", None) and os.path.basename(m.__file__) == "py_harness.py"))
runpy.run_path(os.path.join(_s, "ps_evtx_fixtures.py"))["ps28"]()
```

```powershell
Get-WinEvent -Path .\betik.evtx -Oldest -FilterXPath "*[System[EventID=4104]]" -MaxEvents 6 | ForEach-Object {
    $p = $_.Properties
    "{0} L{1} {2}/{3} {4} [{5}]" -f $_.RecordId, $_.Level, $p[0].Value, $p[1].Value,
        $p[3].Value.Substring(30), ($p[2].Value -replace "`n", "⏎")
}
```

> [!DERİN] Bu dersin dosyasındaki iki fark
> `betik.evtx`'i Windows'un kendisi üretir (`wevtutil epl`), ama eski EVT biçiminden çevrildiği için iki şey gerçek kanaldan farklıdır. Birincisi, `Data` öğelerinin `Name` özniteliği yoktur; alanlar yukarıdaki sırayla, `Properties[n]` ile okunur. Gerçek bir dosyada `*[EventData[Data[@Name='ScriptBlockId']='{...}']]` de çalışır. İkincisi, eski biçimde ayrıntı seviyesi yoktur; ilkeyle yazılmış sıradan bloklar burada Level 5 yerine **Level 4** görünür. Uyarı (3) olanlar gerçek kanaldaki gibidir.
:::

::: anlat Parçaları birleştirmek
Uzun bir blok tek bir olaya sığmaz; PowerShell onu parçalara böler ve her parçayı ayrı bir 4104 olayı olarak yazar. Parçalar satır ya da sözcük sınırını gözetmez: `Net.Web` bir parçada, `Client` sonrakinde olabilir. Üstelik:

- Başka blokların kayıtları araya girer.
- Parçalar her zaman sırayla kaydedilmez: dosyada 2. parça 1.'den önce gelebilir.
- Bir parça hiç gelmemiş olabilir (günlük döndü, kayıt silindi, dosya yarım kopyalandı).

Doğru birleştirme: `ScriptBlockId` ile grupla, `MessageNumber`'ı **sayıya çevirip** sırala, `ScriptBlockText` parçalarını **ayırıcısız** (`-join ''`) yapıştır, parça sayısını `MessageTotal` ile karşılaştır.

> [!TUZAK] `"10"` `"2"`'den küçüktür
> `Properties[0].Value` bir **metindir**. `Sort-Object { $_.Properties[0].Value }` on bir parçalı bir bloğu `1, 10, 11, 2, 3 ...` diye dizer. `Sort-Object { [int]$_.Properties[0].Value }` yaz.

Birleşmiş metinde arama yaparken aradığın şeyi **düz metin** olarak ara. `-match "Net.WebClient"` bir düzenli ifadedir: `.` her karakterle eşleşir, `NetXWebClient`'i de bulur; `DownloadString(` gibi parantezli bir desen ise hata verir. `-like "*$k*"` da `*.tmp`'deki `*`'ı joker sayar. Düz ve büyük/küçük harfe duyarsız arama için:

```powershell
$metin = "`$istemci = New-Object Net.WebClient"
$metin.IndexOf("net.webclient", [StringComparison]::OrdinalIgnoreCase) -ge 0
$metin.IndexOf("NetXWebClient", [StringComparison]::OrdinalIgnoreCase) -ge 0
"Write-Output 'NetXWebClient'" -match "Net.WebClient"
```
:::

::: tahmin
`E` bloğu iki parçalı: 1. parça `Get-ChildItem $env:TEMP -Filter *.tmp |` ve satır sonu, 2. parça `    Remove-Item -WhatIf`. Ne yazar?

```setup
import os, runpy, sys
_s = os.path.dirname(next(m.__file__ for m in list(sys.modules.values())
                          if getattr(m, "__file__", None) and os.path.basename(m.__file__) == "py_harness.py"))
runpy.run_path(os.path.join(_s, "ps_evtx_fixtures.py"))["ps28"]()
```

```powershell
$id = "{6f1e0c2a-0005-4b5c-9d00-5afe00000005}"
$parcalar = Get-WinEvent -Path .\betik.evtx -Oldest -FilterXPath "*[System[EventID=4104] and EventData[Data='$id']]"
"[" + (($parcalar | ForEach-Object { $_.Properties[2].Value }) -join "") + "]"
```

???

```text
[    Remove-Item -WhatIfGet-ChildItem $env:TEMP -Filter *.tmp |
]
```

Parçalar ters sırada kaydedilmiş: dosyada önce 2. parça (RecordId 9), sonra 1. parça (RecordId 10) var. `-Oldest` kayıtları **dosya sırasıyla** verir; dosya sırası `MessageNumber` sırası değildir. Sonuçta ikinci satır başa geçti ve metin bir satır sonuyla bitti. `-Oldest`'i kaldırsaydın sonuç bu kez rastlantıyla doğru çıkardı. Kayıt sırasına hiçbir yönde güvenme: `[int]$_.Properties[0].Value` ile sırala.
:::

::: gorev Bloğu yeniden kur
Girdinin ilk satırı bir `ScriptBlockId`'dir (`{xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx}` biçiminde, süslü parantezlerle). `betik.evtx`'teki **4104** olaylarından o bloğun metnini yeniden kur ve yazdır.

- Parçalardan biri eksikse metni yazma: `EKSIK <var olan>/<toplam>: <eksik numaralar, virgülle>` yazdır (`EKSIK 1/2: 2`).
- Bu kimlikte 4104 olayı yoksa `YOK` yazdır.
- Girdi bu biçimde değilse `HATA` yazdır; biçimini denetlemeden sorguya koyma.

Dosyada başka olaylar da var: 4103 ve 4105 olaylarının `Data` değerlerinde de blok kimlikleri geçebilir.

```stdin
{6f1e0c2a-0002-4b5c-9d00-5afe00000002}
```

```setup
import os, runpy, sys
_s = os.path.dirname(next(m.__file__ for m in list(sys.modules.values())
                          if getattr(m, "__file__", None) and os.path.basename(m.__file__) == "py_harness.py"))
runpy.run_path(os.path.join(_s, "ps_evtx_fixtures.py"))["ps28"]()
```

```starter
$id = $Girdi[0]
Get-WinEvent -Path .\betik.evtx -FilterXPath "*[EventData[Data='$id']]" | ForEach-Object { $_.Properties[2].Value }
```

```test
eq(out, "$istemci = New-Object Net.WebClient\n$veri = $istemci.DownloadString('http://rapor.ornek.test/gunluk.txt')\n"
        "Set-Content -Path rapor.txt -Value $veri\n", "üç parça, araya başka kayıtlar girmiş; parçalar ayırıcısız birleşir")
eq(run(stdin="{6f1e0c2a-0005-4b5c-9d00-5afe00000005}\n"),
   "Get-ChildItem $env:TEMP -Filter *.tmp |\n    Remove-Item -WhatIf\n", "parçalar dosyada ters sırada")
eq(run(stdin="{6f1e0c2a-0006-4b5c-9d00-5afe00000006}\n"),
   "".join(f"# satir {i}\n" for i in range(1, 12)), "on bir parça: MessageNumber'ı sayı olarak sırala")
eq(run(stdin="{6f1e0c2a-0001-4b5c-9d00-5afe00000001}\n"),
   "Get-CimInstance Win32_OperatingSystem |\n    Select-Object Caption, Version\n",
   "tek parçalı blok; aynı kimlik bir 4105 olayında da geçiyor")
eq(run(stdin="{6f1e0c2a-0003-4b5c-9d00-5afe00000003}\n"), "EKSIK 1/2: 2\n", "ikinci parça hiç kaydedilmemiş")
eq(run(stdin="{6f1e0c2a-0009-4b5c-9d00-5afe00000009}\n"), "YOK\n", "böyle bir blok yok")
eq(run(stdin="{6f1e0c2a-0002-4b5c-9d00-5afe00000002}' or '1'='1\n"), "HATA\n", "biçime uymayan, XPath parçası içeren girdi")
eq(run(stdin="6f1e0c2a-0002-4b5c-9d00-5afe00000002\n"), "HATA\n", "süslü parantezsiz")
eq(run(stdin=""), "HATA\n", "boş girdi")
```

```solution
$id = if ($Girdi.Count) { $Girdi[0].Trim() } else { "" }
if ($id -notmatch '^\{[0-9a-fA-F]{8}(-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}\}$') { "HATA"; exit 0 }
$sorgu = "*[System[EventID=4104] and EventData[Data='$id']]"
try {
    $parcalar = @(Get-WinEvent -Path .\betik.evtx -FilterXPath $sorgu -ErrorAction Stop)
} catch {
    if ($_.FullyQualifiedErrorId -notlike "NoMatchingEventsFound*") { throw }
    "YOK"
    exit 0
}
$sirali = @($parcalar | Sort-Object { [int]$_.Properties[0].Value })
$toplam = [int]$sirali[0].Properties[1].Value
$var = @($sirali | ForEach-Object { [int]$_.Properties[0].Value })
$eksik = @(1..$toplam | Where-Object { $_ -notin $var })
if ($eksik.Count) {
    "EKSIK {0}/{1}: {2}" -f $var.Count, $toplam, ($eksik -join ",")
    exit 0
}
($sirali | ForEach-Object { $_.Properties[2].Value }) -join ""
```

```hint
Sorguda iki koşul olmalı: `*[System[EventID=4104] and EventData[Data='$id']]`. Yalnız `Data`'ya bakarsan aynı kimliği taşıyan 4105 olayı da gelir; onun `Properties[2]`'si yoktur.
```

```hint
`1..$toplam | Where-Object { $_ -notin $var }` eksik parça numaralarını verir. Metni `-join ""` ile birleştir: parçalar satır sonunu kendileri taşır, araya bir şey ekleme.
```
:::

::: gorev Birleşmiş bloklarda arama
Girdinin her satırı aranacak bir sözcük ya da parçadır (boş satırlar sayılmaz). `betik.evtx`'teki bütün **4104** bloklarını birleştir ve her bloğun metninde bu parçaları **düz metin** olarak, büyük/küçük harfe bakmadan ara.

En az bir parçanın bulunduğu her blok için, blokları ilk kayıtlarının dosya sırasına göre dizerek şu satırı yazdır:

```text
<ScriptBlockId> <Path, boşsa -> <uyari|normal> <bulunan parçalar, girdideki sırayla ve yazıldığı gibi, virgülle>
```

- Bloğun parçalarından biri bile Level 3 ise `uyari`, değilse `normal`.
- Blok eksikse satırın sonuna ` (eksik)` ekle; eksik blokta da eldeki parçalarda ara.
- En sona `toplam <4104 blok sayısı> blok, <eşleşen blok sayısı> eslesme` ekle.
- Hiç arama parçası yoksa `HATA` yazdır.

```stdin
net.webclient
DownloadString(
invoke-webrequest
```

```setup
import os, runpy, sys
_s = os.path.dirname(next(m.__file__ for m in list(sys.modules.values())
                          if getattr(m, "__file__", None) and os.path.basename(m.__file__) == "py_harness.py"))
runpy.run_path(os.path.join(_s, "ps_evtx_fixtures.py"))["ps28"]()
```

```starter
foreach ($olay in Get-WinEvent -Path .\betik.evtx) {
    foreach ($k in $Girdi) {
        if ($olay.Properties[2].Value -match $k) { "$($olay.Properties[3].Value) $k" }
    }
}
```

```test
eq(out, "{6f1e0c2a-0002-4b5c-9d00-5afe00000002} - uyari net.webclient,DownloadString(\n"
        "{6f1e0c2a-0004-4b5c-9d00-5afe00000004} - normal invoke-webrequest\n"
        "toplam 7 blok, 2 eslesme\n",
   "Net.Web|Client iki parçaya bölünmüş; NetXWebClient eşleşmemeli; parantez düz metin")
eq(run(stdin="*.tmp\n"), "{6f1e0c2a-0005-4b5c-9d00-5afe00000005} C:\\Betikler\\temizle.ps1 normal *.tmp\n"
                         "toplam 7 blok, 1 eslesme\n", "* joker değil, düz karakter")
eq(run(stdin="get-*instance\n"), "toplam 7 blok, 0 eslesme\n",
   "Get-CimInstance'ta 'get-*instance' metni geçmez: * ile her şeyi eşleştirme")
eq(run(stdin="compress-archive\n"),
   "{6f1e0c2a-0003-4b5c-9d00-5afe00000003} C:\\Betikler\\yedek.ps1 normal compress-archive (eksik)\n"
   "toplam 7 blok, 1 eslesme\n", "eksik blokta da ara ve işaretle")
eq(run(stdin="satir 10\nWRITE-OUTPUT\n"),
   "{6f1e0c2a-0007-4b5c-9d00-5afe00000007} - normal WRITE-OUTPUT\n"
   "{6f1e0c2a-0006-4b5c-9d00-5afe00000006} C:\\Betikler\\uzun.ps1 normal satir 10\n"
   "toplam 7 blok, 2 eslesme\n", "bloklar kimliğe göre değil, ilk kayıtlarının dosya sırasıyla")
eq(run(stdin="ParameterBinding\n"), "toplam 7 blok, 0 eslesme\n", "yalnız 4104 blokları: 4103'teki metin sayılmaz")
eq(run(stdin="\n\n"), "HATA\n", "yalnız boş satırlar")
eq(run(stdin=""), "HATA\n", "boş girdi")
```

```solution
$parcalar = @($Girdi | ForEach-Object { $_.Trim() } | Where-Object { $_ })
if (-not $parcalar.Count) { "HATA"; exit 0 }
$olaylar = @(Get-WinEvent -Path .\betik.evtx -Oldest -FilterXPath "*[System[EventID=4104]]")
$bloklar = @($olaylar | Group-Object { $_.Properties[3].Value } |
    Sort-Object { ($_.Group | Measure-Object RecordId -Minimum).Minimum })
$eslesen = 0
foreach ($blok in $bloklar) {
    $sirali = @($blok.Group | Sort-Object { [int]$_.Properties[0].Value })
    $metin = ($sirali | ForEach-Object { $_.Properties[2].Value }) -join ""
    $bulunan = @($parcalar | Where-Object { $metin.IndexOf($_, [StringComparison]::OrdinalIgnoreCase) -ge 0 })
    if (-not $bulunan.Count) { continue }
    $eslesen++
    $yol = if ($sirali[0].Properties[4].Value) { $sirali[0].Properties[4].Value } else { "-" }
    $seviye = if (@($blok.Group | Where-Object { $_.Level -eq 3 }).Count) { "uyari" } else { "normal" }
    $satir = "{0} {1} {2} {3}" -f $blok.Name, $yol, $seviye, ($bulunan -join ",")
    if ($sirali.Count -lt [int]$sirali[0].Properties[1].Value) { $satir += " (eksik)" }
    $satir
}
"toplam {0} blok, {1} eslesme" -f $bloklar.Count, $eslesen
```

```hint
Önce bütün 4104'leri `-Oldest` ile al, `Group-Object { $_.Properties[3].Value }` ile blok blok topla. Grupları en küçük `RecordId`'lerine göre sırala; her grubun içini `[int]` parça numarasına göre sıralayıp `-join ""` ile birleştir.
```

```hint
`$metin.IndexOf($k, [StringComparison]::OrdinalIgnoreCase) -ge 0` düz metin ve büyük/küçük harfe duyarsız arar. `-match` (regex) ve `-like` (joker) bu görevin girdilerinde yanılır.
```
:::
