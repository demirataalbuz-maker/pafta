---
id: ps21
title: Güvenlik Günlüğü ve Sysmon Telemetrisi
summary: Windows Security (4624, 4625, 4688, 4698, 4720) ve Sysmon (1, 3, 11, 13, 22) olay kimlikleri, LogonType tablosu ve EventData XML köprüsü.
---

::: anlat Windows Security günlüğü ve LogonType
`ps16`–`ps18` derslerinde sunucu sağlığı için `System` ve `Application` günlüklerini inceledik. Mavi takım (SOC ve Olay Müdahale) incelemelerinde ise üçüncü bir temel günlük devreye girer: **`Security`** günlüğü (okumak için Yönetici yetkisi gerekir) ve **`Microsoft-Windows-Sysmon/Operational`** kanalı.

Windows `Security` günlüğünde her analistin ilk bakışta tanıması gereken olay kimlikleri:

| Event ID | Anlamı | Önemli `EventData` Alanları |
|---|---|---|
| **4624** | Başarılı oturum açma | `TargetUserName`, `LogonType`, `IpAddress`, `WorkstationName` |
| **4625** | Başarısız oturum açma | `TargetUserName`, `LogonType`, `IpAddress`, `SubStatus` |
| **4672** | Özel ayrıcalık (admin eşdeğeri) atandı | `SubjectUserName`, `PrivilegeList` |
| **4688** | Yeni süreç oluşturuldu | `NewProcessName`, `ParentProcessName`, `CommandLine` |
| **4698** | Zamanlanmış görev oluşturuldu | `TaskName`, `TaskContent` |
| **4720** | Yeni kullanıcı hesabı oluşturuldu | `TargetUserName`, `SubjectUserName` |
| **7045** *(System)* | Yeni bir Windows servisi kuruldu | `ServiceName`, `ImagePath`, `ServiceType` |

`4624` ve `4625` olaylarında oturumun **nasıl** açıldığını `LogonType` alanı söyler:

| LogonType | Tür | Ne zaman oluşur? |
|---|---|---|
| **2** | Interactive | Fiziksel klavye/ekran başından yerel oturum açma |
| **3** | Network | Ağ üzerinden kimlik doğrulama (SMB dosya paylaşımı, WinRM, RPC) |
| **7** | Unlock | Kilitli ekranın açılması |
| **10** | RemoteInteractive | Uzak Masaüstü (**RDP**) ile grafiksel oturum açma |

```powershell
$oturumlar = @(
    [pscustomobject]@{ Id = 4624; User = "ayse";  LogonType = 2;  Ip = "127.0.0.1" }
    [pscustomobject]@{ Id = 4624; User = "ali";   LogonType = 10; Ip = "10.10.4.25" }
    [pscustomobject]@{ Id = 4625; User = "admin"; LogonType = 3;  Ip = "10.10.9.88" }
)
$oturumlar | Where-Object { $_.LogonType -in 3, 10 } |
    ForEach-Object { "$($_.Id) $($_.User) tip=$($_.LogonType) kaynak=$($_.Ip)" }
```

> [!DERİN] `4688` içinde `CommandLine` neden bazen boş gelir?
> Windows varsayılan olarak `4688` olayını kaydederken yalnız yürütülebilir dosyanın yolunu (`NewProcessName`) yazar; komut satırı argümanlarını (`CommandLine`) gizler. Grup İlkesi'nden *"Include command line in process creation events"* ayarı açıldığında `CommandLine` alanı dolmaya başlar.
:::

::: anlat Sysmon olay kimlikleri ve XML `EventData` köprüsü
Yerleşik Windows günlükleri ağ bağlantılarını, DNS sorgularını veya dosya özetlerini (hash) ayrıntılı kaydetmez. Sysinternals **Sysmon** servisi bu boşluğu doldurur ve **Sigma** ile **KQL** kurallarının ana veri kaynağını üretir:

| Sysmon ID | Kategori (Sigma) | Anlamı ve Temel Alanları |
|---|---|---|
| **1** | `process_creation` | Süreç oluşturma: `ProcessGuid`, `Image`, `CommandLine`, `ParentImage`, `Hashes` |
| **3** | `network_connection` | Ağ bağlantısı: `ProcessGuid`, `Image`, `DestinationIp`, `DestinationPort` |
| **7** | `image_load` | Sürece DLL yüklenmesi: `Image`, `ImageLoaded`, `Signed` |
| **11** | `file_event` | Dosya oluşturulması: `Image`, `TargetFilename` |
| **13** | `registry_set` | Kayıt defteri değer ataması: `TargetObject`, `Details` |
| **22** | `dns_query` | DNS sorgusu: `Image`, `QueryName`, `QueryResults` |

Gerçek bir Windows makinesinde `Get-WinEvent` ile okunan olayın ayrıntı alanları (`Image`, `CommandLine`, `LogonType`) doğrudan özellik olarak durmaz; olayın XML gösterimindeki `<EventData><Data Name="...">` düğümlerinin içindedir. `[xml]` dönüştürücüsüyle bu alanları bir sözlüğe ya da nesneye açmak standart SOC tekniğidir:

```powershell
$hamXml = [xml]@'
<Event>
  <System><EventID>1</EventID><Computer>WS-FIN01</Computer></System>
  <EventData>
    <Data Name="Image">C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe</Data>
    <Data Name="ParentImage">C:\Windows\explorer.exe</Data>
    <Data Name="CommandLine">powershell.exe -File C:\rapor\gunluk.ps1</Data>
  </EventData>
</Event>
'@

$alanlar = @{}
foreach ($d in $hamXml.Event.EventData.Data) {
    $alanlar[$d.Name] = $d.'#text'                 #! Name özniteliği anahtar, iç metin değer
}
"Olay: $($hamXml.Event.System.EventID) · Üst: $($alanlar['ParentImage'])"
"Komut: $($alanlar['CommandLine'])"
```

> [!NOT] Sigma ve KQL ile doğrudan bağlantı
> Yukarıdaki `<Data Name="ParentImage">` ve `<Data Name="CommandLine">` alanları, **Sigma** yolunda yazdığın `ParentImage|endswith` ve `CommandLine|contains` alanlarının birebir kaynağıdır!
:::

::: tahmin
İki satır yazar:

```powershell
$olaylar = @(
    [pscustomobject]@{ EventId = 1;  Guid = "{A1}"; Image = "C:\uyg\guncelleyici.exe" }
    [pscustomobject]@{ EventId = 22; Guid = "{A1}"; QueryName = "update.pafta.local" }
    [pscustomobject]@{ EventId = 3;  Guid = "{A1}"; DestinationPort = 443 }
    [pscustomobject]@{ EventId = 3;  Guid = "{B2}"; DestinationPort = 445 }
)
($olaylar | Where-Object Guid -eq "{A1}").Count
($olaylar | Where-Object { $_.EventId -eq 3 -and $_.DestinationPort -eq 445 }).Guid
```

???

`3` ve `{B2}`. `{A1}` süreç kimliğine (`ProcessGuid`) ait süreç başlatma (`1`), DNS sorgusu (`22`) ve ağ bağlantısı (`3`) olmak üzere `3` olay vardır. `445` numaralı SMB portuna giden ağ bağlantısının (`EventId = 3`) kimliği ise `{B2}`'dir.
:::

::: gorev Uzak oturum denetimi (4624 ve 4625)
JSON satırları (`$Girdi`) olarak verilen Security günlüğü olaylarından yalnızca **Ağ (`LogonType = 3`)** veya **RDP (`LogonType = 10`)** olanları süz. Her olayı şu biçimde yazdır:
`<Durum> | <Tur> | <TargetUserName> | <IpAddress>`
- `<Durum>`: `EventId` `4624` ise `BASARILI`, `4625` ise `BASARISIZ`.
- `<Tur>`: `LogonType` `3` ise `AG`, `10` ise `RDP`.

```stdin
{"EventId":4624,"LogonType":2,"TargetUserName":"demir","IpAddress":"127.0.0.1"}
{"EventId":4624,"LogonType":10,"TargetUserName":"ayse","IpAddress":"10.20.1.15"}
{"EventId":4625,"LogonType":3,"TargetUserName":"svc_yedek","IpAddress":"10.20.8.90"}
{"EventId":4624,"LogonType":7,"TargetUserName":"demir","IpAddress":"127.0.0.1"}
```

```starter
$kayitlar = $Girdi | Where-Object { $_ } | ForEach-Object { $_ | ConvertFrom-Json }
foreach ($k in $kayitlar) {
    "$($k.EventId) | $($k.LogonType) | $($k.TargetUserName) | $($k.IpAddress)"
}
```

```test
beklenen = (
    "BASARILI | RDP | ayse | 10.20.1.15\n"
    "BASARISIZ | AG | svc_yedek | 10.20.8.90\n"
)
eq(out, beklenen, "yalnız LogonType 3 ve 10 biçimlendirilerek listelenmeli")
girdi2 = (
    '{"EventId":4625,"LogonType":10,"TargetUserName":"ali","IpAddress":"192.168.1.50"}\n'
    '{"EventId":4624,"LogonType":3,"TargetUserName":"web_app","IpAddress":"10.0.0.8"}\n'
    '{"EventId":4624,"LogonType":2,"TargetUserName":"yerel","IpAddress":"127.0.0.1"}\n'
)
eq(run(stdin=girdi2), "BASARISIZ | RDP | ali | 192.168.1.50\nBASARILI | AG | web_app | 10.0.0.8\n", "4625 RDP ve 4624 AG doğru eşlenmeli")
```

```solution
$kayitlar = $Girdi | Where-Object { $_ } | ForEach-Object { $_ | ConvertFrom-Json }
foreach ($k in $kayitlar | Where-Object { $_.LogonType -in 3, 10 }) {
    $durum = if ($k.EventId -eq 4624) { "BASARILI" } else { "BASARISIZ" }
    $tur = if ($k.LogonType -eq 10) { "RDP" } else { "AG" }
    "$durum | $tur | $($k.TargetUserName) | $($k.IpAddress)"
}
```

```hint
`Where-Object { $_.LogonType -in 3, 10 }` ile yerel (`2`) ve ekran kilidi (`7`) olaylarını ele; sonra `4624`/`4625` ve `10`/`3` karşılıklarını metne çevir.
```
:::

::: gorev Sysmon süreç ve ağ korelasyonu (Event ID 1 ve 3)
`$Girdi` içindeki JSON satırları Sysmon `EventId = 1` (süreç oluşturma) ve `EventId = 3` (ağ bağlantısı) olaylarını içerir. Her iki olay türünde ortak anahtar `ProcessGuid` alanıdır.
Her `EventId = 3` ağ bağlantısı için, onu başlatan süreci (`EventId = 1`) `ProcessGuid` ile bul; yürütülebilir dosya adlarının yalnızca **son parçasını** (`Split-Path -Leaf`) alarak şu biçimde yazdır:
`<ParentLeaf> -> <ImageLeaf> => <DestinationIp>:<DestinationPort>`

```stdin
{"EventId":1,"ProcessGuid":"{P-10}","ParentImage":"C:\\Windows\\explorer.exe","Image":"C:\\Program Files\\App\\istemci.exe"}
{"EventId":1,"ProcessGuid":"{P-20}","ParentImage":"C:\\Windows\\System32\\services.exe","Image":"C:\\Windows\\System32\\svchost.exe"}
{"EventId":3,"ProcessGuid":"{P-10}","DestinationIp":"198.51.100.12","DestinationPort":8443}
{"EventId":3,"ProcessGuid":"{P-20}","DestinationIp":"10.0.0.53","DestinationPort":53}
```

```starter
$olaylar = $Girdi | Where-Object { $_ } | ForEach-Object { $_ | ConvertFrom-Json }
# EventId 1 olanları ProcessGuid tablosuna kaydet, EventId 3 olanları eşleştir
```

```test
beklenen = (
    "explorer.exe -> istemci.exe => 198.51.100.12:8443\n"
    "services.exe -> svchost.exe => 10.0.0.53:53\n"
)
eq(out, beklenen, "Parent -> Image => IP:Port korelasyonu")
girdi2 = (
    r'{"EventId":1,"ProcessGuid":"{G-1}","ParentImage":"C:\\Windows\\System32\\cmd.exe","Image":"C:\\Tools\\curl.exe"}' + "\n" +
    r'{"EventId":3,"ProcessGuid":"{G-1}","DestinationIp":"192.0.2.99","DestinationPort":443}' + "\n"
)
eq(run(stdin=girdi2), "cmd.exe -> curl.exe => 192.0.2.99:443\n", "farklı süreç zincirinde doğru çalışmalı")
```

```solution
$olaylar = $Girdi | Where-Object { $_ } | ForEach-Object { $_ | ConvertFrom-Json }
$surecler = @{}
foreach ($o in $olaylar | Where-Object EventId -eq 1) {
    $surecler[$o.ProcessGuid] = $o
}
foreach ($ag in $olaylar | Where-Object EventId -eq 3) {
    $s = $surecler[$ag.ProcessGuid]
    if ($s) {
        $ust = Split-Path $s.ParentImage -Leaf
        $ad = Split-Path $s.Image -Leaf
        "$ust -> $ad => $($ag.DestinationIp):$($ag.DestinationPort)"
    }
}
```

```hint
Önce `EventId -eq 1` olaylarını `$surecler[$o.ProcessGuid] = $o` sözlüğüne yerleştir; sonra `EventId -eq 3` olaylarını gezip `Split-Path ... -Leaf` ile dosya adlarını çıkar.
```
:::

::: gorev EventData XML ayrıştırıcı
`$Girdi` içindeki tek satırlık Windows Event XML kayıtlarını `[xml]` olarak ayrıştır. Her olay için `<System><EventID>` değerini ve `<EventData>` içindeki `SubjectUserName`, `TargetUserName` veya `ServiceName`, `ImagePath` alanlarını kullanarak şu özeti yazdır:
- `EventID` `4720` ise: `4720 hesap-acildi: <SubjectUserName> -> <TargetUserName>`
- `EventID` `7045` ise: `7045 servis-kuruldu: <ServiceName> (<ImagePath>)`

```stdin
<Event><System><EventID>4720</EventID></System><EventData><Data Name="SubjectUserName">admin_efe</Data><Data Name="TargetUserName">stajyer_01</Data></EventData></Event>
<Event><System><EventID>7045</EventID></System><EventData><Data Name="ServiceName">PaftaAjan</Data><Data Name="ImagePath">C:\Program Files\Pafta\ajan.exe</Data></EventData></Event>
```

```starter
foreach ($satir in $Girdi | Where-Object { $_ }) {
    $x = [xml]$satir
    $id = [int]$x.Event.System.EventID
    # EventData.Data düğümlerini sözlüğe çevirip 4720 ve 7045 satırlarını biçimle
}
```

```test
beklenen = (
    "4720 hesap-acildi: admin_efe -> stajyer_01\n"
    "7045 servis-kuruldu: PaftaAjan (C:\\Program Files\\Pafta\\ajan.exe)\n"
)
eq(out, beklenen, "4720 ve 7045 XML olayları ayrıştırılmalı")
girdi2 = '<Event><System><EventID>4720</EventID></System><EventData><Data Name="SubjectUserName">ik_sistem</Data><Data Name="TargetUserName">analist_zeynep</Data></EventData></Event>' + "\n"
eq(run(stdin=girdi2), "4720 hesap-acildi: ik_sistem -> analist_zeynep\n", "farklı XML girdisinde doğru çalışmalı")
```

```solution
foreach ($satir in $Girdi | Where-Object { $_ }) {
    $x = [xml]$satir
    $id = [int]$x.Event.System.EventID
    $veri = @{}
    foreach ($d in $x.Event.EventData.Data) {
        $veri[$d.Name] = $d.'#text'
    }
    if ($id -eq 4720) {
        "4720 hesap-acildi: $($veri['SubjectUserName']) -> $($veri['TargetUserName'])"
    } elseif ($id -eq 7045) {
        "7045 servis-kuruldu: $($veri['ServiceName']) ($($veri['ImagePath']))"
    }
}
```

```hint
`$x.Event.EventData.Data` içindeki her düğümün adı `$d.Name`, metin değeri ise `$d.'#text'` özelliğindedir.
```
:::
