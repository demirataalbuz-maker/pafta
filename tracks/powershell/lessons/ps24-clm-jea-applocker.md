---
id: ps24
title: Dil Kipleri (CLM), JEA Rol Yetenekleri ve AppLocker Olayları
summary: $ExecutionContext.SessionState.LanguageMode ve dört dil kipi (FullLanguage, ConstrainedLanguage, RestrictedLanguage, NoLanguage), CLM'de çekirdek .NET türleri ve çağrı kısıtları, JEA .psrc/.pssc dosyaları ile rol birleştirme kuralları, AppLocker (8000–8008 ve 8020–8025) olay kimlikleri.
---

::: anlat Dört dil kipi ve Constrained Language Mode (CLM)
Bir PowerShell oturumunun **dil kipi** (*language mode*), o oturumda hangi dil öğelerinin, değişkenlerin ve `.NET` türlerinin kullanılabileceğini belirler. Dil kipi oturumu başlatan uç noktanın (*session configuration*) veya sistemdeki uygulama denetimi ilkesinin bir özelliğidir.

Resmi `about_Language_Modes` belgesine göre PowerShell dört dil kipini destekler:

| Dil Kipi | Ne zaman kullanılır? | Neye izin verir, neyi kısıtlar? |
|---|---|---|
| **`FullLanguage`** | Tüm Windows sürümlerinde varsayılan oturumların varsayılan kipi | Tüm PowerShell dil öğelerine, betik bloklarına ve `.NET` API'lerine kısıtsız izin verir. |
| **`ConstrainedLanguage`** | PowerShell 3.0'da eklendi; sistemde **AppLocker** veya **WDAC** (*Windows Defender Application Control*) ilkesi algılandığında otomatik devreye girer | Cmdlet'lere ve temel dil öğelerine (döngüler, koşullar, metin genişletme, nesne özelliklerine erişim) izin verir; ancak kötüye kullanılabilecek `.NET`, `COM` ve Win32 API çağrılarını yalnızca izinli çekirdek türlerle sınırlar. |
| **`RestrictedLanguage`** | `Import-Module` tarafından yüklenen modül bildirimlerini (`.psd1`) ve `Data` bölümlerini işlerken kullanılır | Komutlar (cmdlet, fonksiyon, CIM komutu) çalışır; fakat betik blokları (`{ ... }`), atama ifadeleri (`=`), özellik erişimi (`.`) ve metot çağrıları yasaktır. Varsayılan olarak yalnız `$PSCulture`, `$PSUICulture`, `$true`, `$false`, `$null` değişkenlerine (modül bildirimlerinde ek olarak `$PSScriptRoot`, `$PSEdition` ve `$env:TEMP` gibi ortam değişkenlerine) ve `-eq`, `-gt`, `-lt` işleçlerine izin verilir. |
| **`NoLanguage`** | **JEA** (*Just Enough Administration*) uç noktalarında varsayılan kip | PowerShell betik dilini tamamen devre dışı bırakır: betik çalıştırılamaz ve değişken kullanılamaz; yalnızca yerleşik komutlar ve cmdlet'ler çağrılabilir. |

Bir `FullLanguage` veya `ConstrainedLanguage` oturumunda etkin kipi `$ExecutionContext.SessionState.LanguageMode` özelliğinden okursun. Buna karşılık `RestrictedLanguage` kipinde nokta (`.`) işleciyle özellik okumak yasak olduğundan aynı ifade `PropertyReferenceNotSupportedInDataSection` ve `VariableReferenceNotSupportedInDataSection` hatalarını döndürür; `NoLanguage` kipinde ise `ScriptsNotAllowed` hatası verir.

**`ConstrainedLanguage` (CLM) sınırları:**
Sistem bir AppLocker ya da WDAC ilkesi altında çalışırken etkileşimli PowerShell oturumu ve ilkenin güvenmediği betikler `ConstrainedLanguage` kipinde çalışır; buna karşılık **ilkenin izin verdiği (imzalı veya beyaz listedeki) betikler ve betik tabanlı modüller kısıtlama olmadan `FullLanguage` kipinde çalışır**. CLM içindeki temel kurallar şunlardır:

- **İzin verilen `.NET` türleri:** Yalnızca izinli listedeki çekirdek türler (`[string]`, `[int]`, `[long]`, `[double]`, `[bool]`, `[datetime]`, `[timespan]`, `[guid]`, `[hashtable]`, `[pscustomobject]`, `[regex]`, `[xml]`, `[uri]`, `[ipaddress]`, `[version]`, `[adsi]`, `[adsisearcher]`, `[wmi]`, `[X509Certificate]` vb.) kullanılabilir. Bu türlere dönüştürme yapmak, özelliklerini okumak/yazmak ve `.NET` metotlarını çağırmak serbesttir.
- **Engellenen `.NET` türleri ve `Add-Type`:** İzinli listede olmayan türlerde (`[System.IO.Path]`, `[System.Convert]`, `[System.Net.WebClient]`, `[System.Diagnostics.Process]` gibi) `New-Object` çağrısı `CannotCreateTypeConstrainedLanguage` hatası, statik/örnek metot çağrısı ise `MethodInvocationNotSupportedInConstrainedLanguage` hatası üretir. `Add-Type` imzalı derlemeleri yükleyebilir ama rastgele C# kodu veya Win32 API'leri derleyemez.
- **COM ve özel durumlar:** Yalnızca `Scripting.Dictionary`, `Scripting.FileSystemObject` ve `VBScript.RegExp` COM nesnelerine izin verilir. `[ordered]@{}` ifadesi serbesttir ve `OrderedDictionary` oluşturur; ancak bu nesne üzerinde metot çağırmak veya türü doğrudan örneklemek yasaktır. `[ref]` türüne dönüştürme (`[ref]`) yapılamaz.

```powershell
$ps = [powershell]::Create()
[void]$ps.AddScript('$ExecutionContext.SessionState.LanguageMode = "ConstrainedLanguage"')
[void]$ps.Invoke()
$ps.Commands.Clear()

[void]$ps.AddScript('
    $kip = $ExecutionContext.SessionState.LanguageMode
    $metin = "pafta".ToUpper()
    $sirali = [ordered]@{ a = 1; b = 2 }
    try { [System.IO.Path]::GetTempPath() } catch { $ioHata = $_.FullyQualifiedErrorId }
    try { New-Object System.Net.WebClient } catch { $newHata = ($_.FullyQualifiedErrorId -split ",")[0] }
    "$kip | metin=$metin | sirali=$($sirali.Count)"
    "io=$ioHata"
    "new=$newHata"
')
$ps.Invoke()
$ps.Dispose()
```

> [!TUZAK] CLM'ye geçiş tek yönlüdür ve bir sonraki ayrıştırmada devreye girer
> Deneme amacıyla `$ExecutionContext.SessionState.LanguageMode = "ConstrainedLanguage"` ataması yaptığında iki tuzağa dikkat et:
> 1. Aynı çalışma alanında (*runspace*) kipi tekrar `"FullLanguage"` yapmaya çalışırsan PowerShell `PropertySetterNotSupportedInConstrainedLanguage` hatası fırlatır; bu yüzden denemeleri ana oturumda değil, `[powershell]::Create()` ile açtığın yalıtılmış bir çalışma alanında yap.
> 2. PowerShell dil kipini betik bloğu **ayrıştırılırken** (*parse* anında) bağlar. `LanguageMode = "ConstrainedLanguage"` satırıyla aynı betik bloğunun içindeki sonraki satırlar hâlâ `FullLanguage` olarak derlenmiştir; kısıtlama ancak o çalışma alanında çalıştırılan **bir sonraki** `AddScript` / komut çağrısında geçerli olur.
:::

::: anlat JEA (Just Enough Administration) ve Rol Yetenekleri (.psrc)
**JEA**, yöneticilere tam yerel yönetici (*Administrator*) yetkisi vermeden, yalnızca görevleri için gereken belirli komutları yükseltilmiş bir uzak oturumda çalıştırma olanağı tanıyan PowerShell özelliğidir. JEA iki yapılandırma dosyasına dayanır:

1. **Rol Yeteneği Dosyası (`.psrc` — *Role Capability*):** Bir modülün `RoleCapabilities` klasöründe duran (`New-PSRoleCapabilityFile` ile üretilen) ve `Import-PowerShellDataFile` ile güvenli biçimde sözlük (*hashtable*) olarak okunabilen bir veri dosyasıdır; bağlanan rolün **ne yapabileceğini** tanımlar.
2. **Oturum Yapılandırma Dosyası (`.pssc` — *Session Configuration*):** `New-PSSessionConfigurationFile` ile üretilen, `Test-PSSessionConfigurationFile` ile doğrulanan ve hangi kullanıcı/grubun hangi role eşleneceğini (`RoleDefinitions`), sanal yönetici hesabını (`RunAsVirtualAccount`) ve oturum türünü (`SessionType = 'RestrictedRemoteServer'`, yani `NoLanguage` kipi) belirleyen dosyadır.

Resmi `JEA Role Capabilities` belgesine göre `.psrc` dosyasındaki temel alanlar:

| `.psrc` Alanı | Görevi ve Güvenlik Kuralı |
|---|---|
| `VisibleCmdlets` / `VisibleFunctions` | İzin verilen cmdlet ve fonksiyonlar. Doğrudan ad (`'Get-Service'`) ya da parametre/değer kısıtı içeren sözlük (`@{ Name = 'Restart-Service'; Parameters = @{ Name = 'Name'; ValidateSet = @('Dns', 'Spooler') } }` veya `ValidatePattern = 'HR_*'`) olarak yazılır. Ortak PowerShell parametreleri (*common parameters*) her zaman serbesttir. Joker karakter (`My-*`, `*-Func`) kullanılması güvenlik açısından önerilmez. |
| `VisibleExternalCommands` | Çalıştırılmasına izin verilen dış `.exe` programlar ve `.ps1` betikleri. Benzer adlı zararlı ikililerin çalışmasını önlemek için **her zaman tam dosya yolu** (`'C:\Windows\System32\whoami.exe'`) belirtilmelidir. |
| `VisibleProviders` | JEA oturumlarında **varsayılan olarak hiçbir PowerShell sağlayıcısı açık değildir**. Yalnız gerektiğinde `'Registry'` veya `'FileSystem'` gibi açıkça eklenir. |
| `FunctionDefinitions` | Karmaşık işlemleri sarmalayan özel fonksiyon tanımları (`@{ Name = 'Get-TopProcess'; ScriptBlock = { ... } }`). Özel fonksiyonun JEA kullanıcısı tarafından çağrılabilmesi için adının **`VisibleFunctions` listesine de eklenmesi zorunludur**. |

> [!GÜVENLİK] JEA'da riskli komutlar ve özel fonksiyonların çalışma kipi
> Microsoft Learn belgesi, kısıtsız açıldığında JEA sınırını aşmaya yol açan iki tehlikeli komut grubunu özellikle vurgular:
> - **Yetki yükseltme (grup/hesap değiştirme):** `Add-LocalGroupMember`, `Add-ADGroupMember`, `net.exe` (ör. `net share` için açılırsa kullanıcı `net group Administrators ... /add` çalıştırabilir; yerine `Get-SmbShare` tercih edilmelidir), `dsadd.exe`.
> - **Rastgele kod çalıştırma:** `Start-Process`, `New-Service`, `Invoke-Item`, `Invoke-WmiMethod`, `Invoke-CimMethod`, `Invoke-Expression`, `Invoke-Command`, `New-ScheduledTask`, `Register-ScheduledJob`.
>
> Ayrıca `FunctionDefinitions` içindeki özel fonksiyonların gövdesi JEA'nın `NoLanguage` kısıtına tabi **değildir**; sistemin varsayılan dil kipinde çalışır ve görünür yapılmamış dosya sistemi/kayıt defteri sağlayıcılarına erişebilir. Bu yüzden parametreler asla doğrudan `Invoke-Expression` gibi komutlara aktarılmamalıdır. JEA oturumlarında `Select-Object` rastgele özellik seçimine izin vermeyen kısıtlı bir vekil (*proxy*) fonksiyondur; özel fonksiyon içinde tam `Select-Object` gerekirse `Microsoft.PowerShell.Utility\Select-Object` tam modül nitelikli adı (FQMN) kullanılır.

**Çoklu rol birleştirme (*Role Capability Merge*) kuralları:**
Bir kullanıcı `.pssc` içinde birden fazla role eşleşirse JEA **en izin verici** (*most permissive*) birleşimi uygular:
- Bir rol komutu parametre kısıtı olmadan açıyor, diğer rol parametre kısıtı koyuyorsa **tüm parametrelere izin verilir**.
- Bir rol parametreyi değer kısıtı olmadan açıyor, diğer rol `ValidateSet` veya `ValidatePattern` koyuyorsa **değer kısıtı yok sayılır**.
- Birden fazla rol aynı parametreye `ValidateSet` tanımlıyorsa **tüm `ValidateSet` değerlerinin birleşimine** izin verilir.
- Bir rol aynı parametreye `ValidateSet`, diğer rol `ValidatePattern` tanımlıyorsa (veya aynı komutta ikisi birden yazılırsa) **`ValidateSet` yok sayılır ve `ValidatePattern` geçerli olur**.
- Bir rol `Remove-Item` cmdlet'ini, başka bir rol ise `FileSystem` sağlayıcısını açıyorsa iki rolün birleşimi kullanıcının diskteki dosyaları silmesine yol açar.

```powershell
$psrcYol = Join-Path $env:TEMP "pafta_rol_$([guid]::NewGuid().ToString('N')).psrc"
New-PSRoleCapabilityFile -Path $psrcYol `
    -VisibleCmdlets 'Get-Service', @{ Name = 'Restart-Service'; Parameters = @{ Name = 'Name'; ValidateSet = 'Dns', 'Spooler' } } `
    -VisibleExternalCommands 'C:\Windows\System32\whoami.exe'

$rol = Import-PowerShellDataFile -Path $psrcYol
Remove-Item $psrcYol -Force

"Komut sayisi: $($rol.VisibleCmdlets.Count)"
$kisitli = $rol.VisibleCmdlets[1]
"$($kisitli.Name) -> $($kisitli.Parameters.Name)=$($kisitli.Parameters.ValidateSet -join ',')"
"Dis komut: $($rol.VisibleExternalCommands[0])"
```
:::

::: anlat AppLocker Olay Kimlikleri (8000–8008 ve 8020–8025)
AppLocker kuralları hangi çalıştırılabilir dosyaların, DLL'lerin, yükleyicilerin ve betiklerin çalışabileceğini belirler ve PowerShell'in otomatik olarak `ConstrainedLanguage` kipine geçmesini tetikler. Olay Görüntüleyicisi'nde `Application and Services Logs\Microsoft\Windows\AppLocker` altında izlenen resmi olay kimlikleri şunlardır:

| Event ID | Seviye | Kanal / Kapsam | Anlamı (Microsoft Learn) |
|---|---|---|---|
| **8000** | Error | İlke (*Policy*) | `AppID policy conversion failed` — AppLocker ilkesi bilgisayara doğru uygulanamadı. |
| **8001** | Information | İlke (*Policy*) | `The AppLocker policy was applied successfully to this computer` — ilke başarıyla uygulandı. |
| **8002** | Information | `EXE and DLL` | `<File name> was allowed to run` — kural `.exe` veya `.dll` dosyasına **izin verdi**. |
| **8003** | Warning | `EXE and DLL` | `<File name> was allowed to run but would have been prevented...` — **Audit only** (*Yalnızca denetle*) kipinde `.exe`/`.dll` çalıştı; `Enforce rules` etkin olsaydı engellenecekti. |
| **8004** | Error | `EXE and DLL` | `<File name> was prevented from running` — **Enforce rules** kipinde `.exe` veya `.dll` **engellendi**. |
| **8005** | Information | `MSI and Script` | `<File name> was allowed to run` — kural betik (`.ps1`, `.bat`, `.vbs`, `.js`) veya `.msi` dosyasına **izin verdi**. |
| **8006** | Warning | `MSI and Script` | `<File name> was allowed to run but would have been prevented...` — **Audit only** kipinde betik veya `.msi` çalıştı; zorlansaydı engellenecekti. |
| **8007** | Error | `MSI and Script` | `<File name> was prevented from running` — **Enforce rules** kipinde betik veya `.msi` **engellendi**. |
| **8008** | Warning | Bileşen | `<File name>: AppLocker component not available on this SKU` — Windows sürümü AppLocker'ı desteklemiyor. |
| **8020–8022** | Info / Warn / Error | `Packaged app-Execution` | Paketlenmiş uygulama (*Packaged app*) çalıştırma: `8020` izin verildi, `8021` denetim uyarısı (*Audit only*), `8022` engellendi (*Enforce*). |
| **8023–8025** | Info / Warn / Error | `Packaged app-Deployment` | Paketlenmiş uygulama kurulumu: `8023` kurulumuna izin verildi, `8024` denetim uyarısı, `8025` kurulum engellendi. |

AppLocker kayıtları olay türüne göre dosya/paket, karar, kural ve kullanıcı bilgileri taşır; her kimliğin aynı XML alanlarını içerdiğini varsayma. Aşağıdaki elle hazırlanmış XML örneğinde FilePathBuffer, RuleNameBuffer ve TargetUser adları kullanılıyor; gerçek kaydın şemasını ToXml ile doğrula:

```powershell
$olayXml = [xml]@'
<Event>
  <System><EventID>8007</EventID><Channel>Microsoft-Windows-AppLocker/MSI and Script</Channel></System>
  <EventData>
    <Data Name="PolicyNameBuffer">SCRIPT</Data>
    <Data Name="RuleNameBuffer">Default Scripts</Data>
    <Data Name="TargetUser">S-1-5-21-1000-2000-3000-1105</Data>
    <Data Name="FilePathBuffer">%OSDRIVE%\USERS\ANALIST\APPDATA\LOCAL\TEMP\TOPLA.PS1</Data>
  </EventData>
</Event>
'@

$veri = @{}
foreach ($d in $olayXml.Event.EventData.Data) { $veri[$d.Name] = $d.'#text' }
$dosya = Split-Path $veri['FilePathBuffer'] -Leaf
"ID=$($olayXml.Event.System.EventID) | Ilke=$($veri['PolicyNameBuffer']) | Dosya=$dosya | Kural=$($veri['RuleNameBuffer'])"
```
:::

::: tahmin
Ne yazar?

```powershell
$ps = [powershell]::Create()
[void]$ps.AddScript('$ExecutionContext.SessionState.LanguageMode = "ConstrainedLanguage"')
[void]$ps.Invoke()
$ps.Commands.Clear()
[void]$ps.AddScript('
    $sayi = [int]"15"
    $sozluk = [ordered]@{ k = 10; m = 20 }
    try {
        [System.Convert]::ToBase64String(@(1, 2))
    } catch {
        $hata = $_.FullyQualifiedErrorId
    }
    "$($ExecutionContext.SessionState.LanguageMode) $sayi $($sozluk.Count) $hata"
')
$ps.Invoke()
$ps.Dispose()

$olaylar = @(
    [pscustomobject]@{ Id = 8002; Dosya = "powershell.exe" }
    [pscustomobject]@{ Id = 8003; Dosya = "rubeus.exe" }
    [pscustomobject]@{ Id = 8004; Dosya = "mimikatz.exe" }
    [pscustomobject]@{ Id = 8006; Dosya = "kesif.ps1" }
    [pscustomobject]@{ Id = 8007; Dosya = "stager.ps1" }
)
"denetim=" + (($olaylar | Where-Object { $_.Id -in 8003, 8006 }).Dosya -join ",")
"engel=" + (($olaylar | Where-Object { $_.Id -in 8004, 8007 }).Dosya -join ",")
```

???

Üç satır yazar:
- `ConstrainedLanguage 15 2 MethodInvocationNotSupportedInConstrainedLanguage`
- `denetim=rubeus.exe,kesif.ps1`
- `engel=mimikatz.exe,stager.ps1`

`[int]` ve `[ordered]@{}` ifadeleri `ConstrainedLanguage` kipinde izinli çekirdek öğelerdir (`15` ve `2` döner); ancak `[System.Convert]` izinli türler listesinde olmadığından `ToBase64String` çağrısı `MethodInvocationNotSupportedInConstrainedLanguage` hatası fırlatır. AppLocker'da `8003` (EXE/DLL) ve `8006` (MSI/Script) *Audit only* (denetim) uyarılarını; `8004` (EXE/DLL) ve `8007` (MSI/Script) ise *Enforce rules* kipinde gerçekten engellenen dosyaları gösterir.
:::

::: gorev JEA rol yeteneği güvenlik denetçisi
`$Girdi`'deki tek satırlık JSON nesnesi bir JEA rol yeteneği özetini ve kabul edilebilir risk eşiğini (`EsikRisk`) içerir:
- `EsikRisk`: tam sayı (`0` veya pozitif)
- `VisibleCmdlets`: metin dizisi (komut adları)
- `VisibleExternalCommands`: metin dizisi (dış komut yolları)
- `VisibleFunctions`: metin dizisi (kullanıcıya açılan fonksiyon adları)
- `FunctionDefinitions`: metin dizisi (`FunctionDefinitions` içinde tanımlanmış özel fonksiyon adları)
- `VisibleProviders`: metin dizisi (açılan sağlayıcı adları)

Aşağıdaki dört kuralı sırayla uygula (listelerdeki boş veya metin olmayan öğeleri yok say):

1. **Tehlikeli cmdlet (`+40` puan):** `VisibleCmdlets` içindeki her komut için, adı şu listedeyse (büyük-küçük harf duyarsız) her biri için risk puanına `40` ekle ve `KOMUT:<komut>` bulgusu üret:
   `Add-LocalGroupMember`, `Add-ADGroupMember`, `Start-Process`, `New-Service`, `Invoke-Item`, `Invoke-WmiMethod`, `Invoke-CimMethod`, `Invoke-Expression`, `Invoke-Command`, `New-ScheduledTask`, `Register-ScheduledJob`
2. **Dış komut riski (`+30` puan):** `VisibleExternalCommands` içindeki her öğe için, tam sürücü yoluyla (`^[A-Za-z]:\\`) başlamıyorsa **veya** dosya adı (`Split-Path -Leaf`) `net.exe` ya da `dsadd.exe` ise her biri için risk puanına `30` ekle ve `DIS:<deger>` bulgusu üret.
3. **Görünmez özel fonksiyon (`+10` puan):** `FunctionDefinitions` içindeki her fonksiyon adı için, `VisibleFunctions` listesinde yer almıyorsa her biri için risk puanına `10` ekle ve `GORUNMEZ:<fonksiyon>` bulgusu üret.
4. **Sağlayıcı ve silme birleşimi (`+50` puan):** `VisibleProviders` içinde `FileSystem` **ve** `VisibleCmdlets` içinde `Remove-Item` varsa risk puanına `50` ekle ve `SAGLAYICI:FileSystem+Remove-Item` bulgusu üret.

Toplam `Risk` puanını `EsikRisk` ile karşılaştır:
- `Risk -gt $esik` ise durum `ENGELLE`
- `Risk -eq $esik` ise durum `SINIRDA`
- `Risk -lt $esik` ise durum `ONAY`

Çıktıyı tek satır olarak yazdır (bulgu yoksa `bulgu=YOK`):
`<DURUM>|risk=<Risk>|bulgu=<bulgular virgülle>`
Girdi boşsa, JSON ayrıştırılamıyorsa veya `EsikRisk` negatif/eksikse tek satır `HATA` yazdır.

```stdin
{"EsikRisk":60,"VisibleCmdlets":["Get-Service","Start-Process"],"VisibleExternalCommands":["C:\\Windows\\System32\\whoami.exe","net.exe"],"VisibleFunctions":["Get-Log"],"FunctionDefinitions":["Get-Log","Reset-App"],"VisibleProviders":["Registry"]}
```

```starter
$ham = ($Girdi | Out-String).Trim()
if (-not $ham) { "HATA"; exit 0 }
# JSON'u ayrıştır, 4 kuralı sırayla uygula ve <DURUM>|risk=<Risk>|bulgu=<...> yazdır
```

```test
eq(out, "ENGELLE|risk=80|bulgu=KOMUT:Start-Process,DIS:net.exe,GORUNMEZ:Reset-App\n",
   "40 + 30 + 10 = 80 > 60 olduğu için ENGELLE")

sinirda = run(stdin='{"EsikRisk":40,"VisibleCmdlets":["Invoke-Expression"],"VisibleExternalCommands":["C:\\\\Windows\\\\System32\\\\whoami.exe"],"VisibleFunctions":[],"FunctionDefinitions":[],"VisibleProviders":[]}\n')
eq(sinirda, "SINIRDA|risk=40|bulgu=KOMUT:Invoke-Expression\n",
   "risk == EsikRisk (40 == 40) olduğunda SINIRDA")

onay_alt = run(stdin='{"EsikRisk":40,"VisibleCmdlets":["Get-Service"],"VisibleExternalCommands":["C:\\\\Windows\\\\System32\\\\ipconfig.exe"],"VisibleFunctions":["Get-Top"],"FunctionDefinitions":["Get-Top","Helper-Fn"],"VisibleProviders":[]}\n')
eq(onay_alt, "ONAY|risk=10|bulgu=GORUNMEZ:Helper-Fn\n",
   "risk < EsikRisk (10 < 40) olduğunda ONAY")

sifir_esik = run(stdin='{"EsikRisk":0,"VisibleCmdlets":["Get-Service"],"VisibleExternalCommands":["C:\\\\Windows\\\\System32\\\\whoami.exe"],"VisibleFunctions":[],"FunctionDefinitions":[],"VisibleProviders":[]}\n')
eq(sifir_esik, "SINIRDA|risk=0|bulgu=YOK\n",
   "EsikRisk=0 geçerli olmalı ve risk=0 olduğunda SINIRDA vermeli")

temiz = run(stdin='{"EsikRisk":10,"VisibleCmdlets":["Get-Service"],"VisibleExternalCommands":["C:\\\\Windows\\\\System32\\\\whoami.exe"],"VisibleFunctions":[],"FunctionDefinitions":[],"VisibleProviders":[]}\n')
eq(temiz, "ONAY|risk=0|bulgu=YOK\n",
   "hiç bulgu yoksa risk=0 ve bulgu=YOK")

saglayici = run(stdin='{"EsikRisk":50,"VisibleCmdlets":["Remove-Item"],"VisibleExternalCommands":[],"VisibleFunctions":[],"FunctionDefinitions":[],"VisibleProviders":["FileSystem"]}\n')
eq(saglayici, "SINIRDA|risk=50|bulgu=SAGLAYICI:FileSystem+Remove-Item\n",
   "FileSystem ve Remove-Item birlikteyse +50 puan")

tek_saglayici = run(stdin='{"EsikRisk":10,"VisibleCmdlets":["Get-Service"],"VisibleExternalCommands":[],"VisibleFunctions":[],"FunctionDefinitions":[],"VisibleProviders":["FileSystem"]}\n')
eq(tek_saglayici, "ONAY|risk=0|bulgu=YOK\n",
   "yalnızca FileSystem varsa Remove-Item olmadan risk eklenmez")

tam_yol_net = run(stdin='{"EsikRisk":30,"VisibleCmdlets":[],"VisibleExternalCommands":["C:\\\\Windows\\\\System32\\\\net.exe","C:\\\\Tools\\\\dsadd.exe"],"VisibleFunctions":[],"FunctionDefinitions":[],"VisibleProviders":[]}\n')
eq(tam_yol_net, "ENGELLE|risk=60|bulgu=DIS:C:\\Windows\\System32\\net.exe,DIS:C:\\Tools\\dsadd.exe\n",
   "tam yol yazılsa bile net.exe ve dsadd.exe risklidir")

bos_ogeler = run(stdin='{"EsikRisk":20,"VisibleCmdlets":["",123,"Add-LocalGroupMember"],"VisibleExternalCommands":["",456],"VisibleFunctions":["",789],"FunctionDefinitions":["",999],"VisibleProviders":["",111]}\n')
eq(bos_ogeler, "ENGELLE|risk=40|bulgu=KOMUT:Add-LocalGroupMember\n",
   "dizi içindeki boş ve metin olmayan öğeler yok sayılmalı")

eq(run(stdin=""), "HATA\n", "boş girdi HATA döndürmeli")
eq(run(stdin="gecersiz json\n"), "HATA\n", "bozuk JSON HATA döndürmeli")
eq(run(stdin='{"EsikRisk":"abc","VisibleCmdlets":[]}\n'), "HATA\n", "metin EsikRisk HATA döndürmeli")
eq(run(stdin='{"EsikRisk":-1,"VisibleCmdlets":[]}\n'), "HATA\n", "negatif EsikRisk HATA döndürmeli")
```

```solution
$ham = ($Girdi | Out-String).Trim()
if (-not $ham) { "HATA"; exit 0 }
try {
    $v = $ham | ConvertFrom-Json -ErrorAction Stop
} catch {
    "HATA"; exit 0
}
if ($v.EsikRisk -isnot [int] -or $v.EsikRisk -lt 0) {
    "HATA"; exit 0
}

$tehlikeli = @(
    "Add-LocalGroupMember", "Add-ADGroupMember", "Start-Process", "New-Service",
    "Invoke-Item", "Invoke-WmiMethod", "Invoke-CimMethod", "Invoke-Expression",
    "Invoke-Command", "New-ScheduledTask", "Register-ScheduledJob"
)

function Temiz-Liste($dizi) {
    @($dizi | Where-Object { $_ -is [string] -and $_.Trim() -ne "" } | ForEach-Object { $_.Trim() })
}

$komutlar = Temiz-Liste $v.VisibleCmdlets
$dislar = Temiz-Liste $v.VisibleExternalCommands
$gorunurFn = Temiz-Liste $v.VisibleFunctions
$tanimliFn = Temiz-Liste $v.FunctionDefinitions
$saglayicilar = Temiz-Liste $v.VisibleProviders

$risk = 0
$bulgular = @()

foreach ($k in $komutlar) {
    if ($k -in $tehlikeli) {
        $risk += 40
        $bulgular += "KOMUT:$k"
    }
}

foreach ($d in $dislar) {
    $yaprak = Split-Path $d -Leaf
    if ($d -notmatch '^[A-Za-z]:\\' -or $yaprak -in @("net.exe", "dsadd.exe")) {
        $risk += 30
        $bulgular += "DIS:$d"
    }
}

foreach ($f in $tanimliFn) {
    if ($f -notin $gorunurFn) {
        $risk += 10
        $bulgular += "GORUNMEZ:$f"
    }
}

if ("FileSystem" -in $saglayicilar -and "Remove-Item" -in $komutlar) {
    $risk += 50
    $bulgular += "SAGLAYICI:FileSystem+Remove-Item"
}

$durum = if ($risk -gt $v.EsikRisk) { "ENGELLE" } elseif ($risk -eq $v.EsikRisk) { "SINIRDA" } else { "ONAY" }
$bulguMetin = if ($bulgular.Count -gt 0) { $bulgular -join "," } else { "YOK" }
"$durum|risk=$risk|bulgu=$bulguMetin"
```

```hint
Dış komutlarda hem `$d -notmatch '^[A-Za-z]:\\'` (tam yol değil) hem de `(Split-Path $d -Leaf) -in @("net.exe", "dsadd.exe")` durumunu kontrol et; ikisinden biri bile doğruysa `+30` puan ve `DIS:<deger>` eklenir.
```
:::

::: gorev JEA çoklu rol birleştirme (Merge) motoru
Bir kullanıcı JEA oturumunda aynı anda iki role (`RolA` ve `RolB`) sahipse JEA kuralları en izin verici şekilde birleştirir. `$Girdi`'deki JSON nesnesi şu alanları içerir:
- `MinSeviye`: komutu çalıştırmak için gereken asgari yetki seviyesi (tam sayı, `1` veya üstü)
- `RolA` ve `RolB`: her biri komut kuralları listesidir. Her kural:
  - `Name`: komut adı
  - `Kisitli`: `$false` ise komut parametre kısıtı olmadan açılmıştır; `$true` ise `Param` parametresi kısıtlanmıştır (`ValidateSet` dizisi veya `ValidatePattern` düzenli ifadesiyle).
- `Istekler`: sınanacak çağrılar listesi (`Name`, `Deger`, `Seviye`).

Microsoft Learn JEA birleştirme kurallarını her istek için uygula:
1. İstek yapılan `Name` ne `RolA` ne de `RolB` içinde varsa (veya kullanıcının `Seviye` değeri `MinSeviye` değerinden **küçükse**, `Seviye -lt $min`) sonuç `RET`'tir.
2. Komut rollerden **en az birinde** `Kisitli = $false` olarak tanımlanmışsa parametre kısıtı kalkar (`KISITSIZ`) ve her `Deger` kabul edilir.
3. Komut her görünür olduğu rolde `Kisitli = $true` ise:
   - Rollerden **en az birinde** `ValidatePattern` tanımlıysa tüm `ValidateSet` listeleri **yok sayılır**; `Deger` tanımlı `ValidatePattern` desenlerinden en az biriyle tam eşleşiyorsa (`$deger -match "^(?:$desen)$"`) kabul edilir (`DESEN`), eşleşmiyorsa `RET`.
   - Hiçbir rolde `ValidatePattern` yoksa, rollerdeki tüm `ValidateSet` dizilerinin **birleşimi** alınır; `Deger` bu birleşimde varsa kabul edilir (`KUME`), yoksa `RET`.

Kabul edilen bir istekte `Seviye -eq $min` ise `ONAY_SINIR`, `Seviye -gt $min` ise `ONAY_TAM` yazdır. Çıktı biçimi:
- Kabul: `<Name>:<Deger>-><ONAY_SINIR|ONAY_TAM>:<KISITSIZ|DESEN|KUME>`
- Ret: `<Name>:<Deger>->RET`

Girdi boş veya bozuk JSON ise tek satır `HATA` yazdır.

```stdin
{"MinSeviye":3,"RolA":[{"Name":"Get-Service","Kisitli":false},{"Name":"Restart-Service","Kisitli":true,"ValidateSet":["Dns","Spooler"]},{"Name":"Start-Website","Kisitli":true,"ValidateSet":["Portal"]}],"RolB":[{"Name":"Get-Service","Kisitli":true,"ValidatePattern":"DNS.*"},{"Name":"Restart-Service","Kisitli":true,"ValidateSet":["W3SVC"]},{"Name":"Start-Website","Kisitli":true,"ValidatePattern":"HR_.*"}],"Istekler":[{"Name":"Get-Service","Deger":"WinRM","Seviye":4},{"Name":"Restart-Service","Deger":"W3SVC","Seviye":3},{"Name":"Start-Website","Deger":"Portal","Seviye":5},{"Name":"Start-Website","Deger":"HR_Intranet","Seviye":5},{"Name":"Restart-Service","Deger":"Dns","Seviye":2}]}
```

```starter
$ham = ($Girdi | Out-String).Trim()
if (-not $ham) { "HATA"; exit 0 }
# RolA ve RolB kurallarını birleştirip Istekler listesini değerlendir
```

```test
beklenen = (
    "Get-Service:WinRM->ONAY_TAM:KISITSIZ\n"
    "Restart-Service:W3SVC->ONAY_SINIR:KUME\n"
    "Start-Website:Portal->RET\n"
    "Start-Website:HR_Intranet->ONAY_TAM:DESEN\n"
    "Restart-Service:Dns->RET\n"
)
eq(out, beklenen, "KISITSIZ, KUME birleşimi, DESEN'in ValidateSet'i ezmesi ve Seviye < MinSeviye reddi")

olmayan = run(stdin='{"MinSeviye":1,"RolA":[{"Name":"Get-Process","Kisitli":false}],"RolB":[],"Istekler":[{"Name":"Stop-Process","Deger":"1","Seviye":5},{"Name":"Get-Process","Deger":"lsass","Seviye":1}]}\n')
eq(olmayan, "Stop-Process:1->RET\nGet-Process:lsass->ONAY_SINIR:KISITSIZ\n",
   "hiçbir rolde olmayan komut RET, Seviye == MinSeviye ONAY_SINIR")

kume_ret = run(stdin='{"MinSeviye":2,"RolA":[{"Name":"Restart-Service","Kisitli":true,"ValidateSet":["Dns"]}],"RolB":[],"Istekler":[{"Name":"Restart-Service","Deger":"Spooler","Seviye":3}]}\n')
eq(kume_ret, "Restart-Service:Spooler->RET\n",
   "ValidateSet birleşiminde olmayan değer RET")

eq(run(stdin=""), "HATA\n", "boş girdi HATA")
eq(run(stdin="{bozuk"), "HATA\n", "bozuk JSON HATA")
eq(run(stdin='{"MinSeviye":"abc","RolA":[],"RolB":[],"Istekler":[]}\n'), "HATA\n", "metin MinSeviye HATA")
eq(run(stdin='{"MinSeviye":0,"RolA":[],"RolB":[],"Istekler":[]}\n'), "HATA\n", "MinSeviye < 1 ise HATA")
```

```solution
$ham = ($Girdi | Out-String).Trim()
if (-not $ham) { "HATA"; exit 0 }
try {
    $v = $ham | ConvertFrom-Json -ErrorAction Stop
} catch {
    "HATA"; exit 0
}
if ($v.MinSeviye -isnot [int] -or $v.MinSeviye -lt 1) {
    "HATA"; exit 0
}

$tumKurallar = @(@($v.RolA) + @($v.RolB) | Where-Object { $_.Name })

foreach ($istek in @($v.Istekler)) {
    $ad = $istek.Name
    $deger = [string]$istek.Deger
    $seviye = [int]$istek.Seviye
    $eslesen = @($tumKurallar | Where-Object { $_.Name -eq $ad })

    if ($eslesen.Count -eq 0 -or $seviye -lt $v.MinSeviye) {
        "${ad}:${deger}->RET"
        continue
    }

    $onayEtiket = if ($seviye -eq $v.MinSeviye) { "ONAY_SINIR" } else { "ONAY_TAM" }

    if (@($eslesen | Where-Object { -not $_.Kisitli }).Count -gt 0) {
        "${ad}:${deger}->${onayEtiket}:KISITSIZ"
        continue
    }

    $desenler = @($eslesen | Where-Object { $_.ValidatePattern } | ForEach-Object { [string]$_.ValidatePattern })
    if ($desenler.Count -gt 0) {
        $uydu = $false
        foreach ($d in $desenler) {
            if ($deger -match "^(?:$d)$") { $uydu = $true; break }
        }
        if ($uydu) { "${ad}:${deger}->${onayEtiket}:DESEN" } else { "${ad}:${deger}->RET" }
        continue
    }

    $kumeler = @($eslesen | Where-Object { $_.ValidateSet } | ForEach-Object { @($_.ValidateSet) })
    if ($deger -in $kumeler) {
        "${ad}:${deger}->${onayEtiket}:KUME"
    } else {
        "${ad}:${deger}->RET"
    }
}
```

```hint
Bir komut için eşleşen kurallardan herhangi birinde `Kisitli` `$false` ise diğer roldeki kısıtlamalar yok sayılır (`KISITSIZ`). Aksi durumda en az bir kuralda `ValidatePattern` varsa tüm `ValidateSet` listeleri devre dışı kalır.
```
:::

::: gorev AppLocker olay korelasyonu (8002–8007)
`$Girdi`'nin **ilk satırı** ihlal eşik sayısıdır (`EsikSayi`, `1` veya üstü tam sayı). Kalan satırların her biri tek satırlık bir AppLocker XML olayıdır (`<Event><System><EventID>...</EventID></System><EventData>...</EventData></Event>`).

1. Yalnızca `8002`, `8003`, `8004`, `8005`, `8006` ve `8007` olay kimliklerini işle (`8001` gibi ilke olaylarını atla):
   - `8002`: `EXE_DLL` ve `IZIN`
   - `8003`: `EXE_DLL` ve `DENETIM`
   - `8004`: `EXE_DLL` ve `ENGEL`
   - `8005`: `MSI_SCRIPT` ve `IZIN`
   - `8006`: `MSI_SCRIPT` ve `DENETIM`
   - `8007`: `MSI_SCRIPT` ve `ENGEL`
2. Yalnızca **ihlal** olaylarını (`DENETIM` veya `ENGEL`, yani `8003`, `8004`, `8006`, `8007`) girdi sırasıyla şu biçimde yazdır (`FilePathBuffer` alanının yalnızca son dosya adını `Split-Path -Leaf` ile al):
   `OLAY|<TargetUser>|<EXE_DLL|MSI_SCRIPT>|<DENETIM|ENGEL>|<DosyaYaprak>`
3. Ardından, en az bir olayda (`IZIN` dahil) görünen her `TargetUser` için (ilk görülme sırasıyla) toplam **ihlal** (`DENETIM` + `ENGEL`) sayısını `EsikSayi` ile karşılaştırarak özet satırı yazdır:
   - `IhlalSayisi -gt $esik` ise `KRITIK`
   - `IhlalSayisi -eq $esik` ise `UYARI`
   - `IhlalSayisi -lt $esik` ise `NORMAL`
   Biçim: `OZET|<TargetUser>|ihlal=<IhlalSayisi>|<KRITIK|UYARI|NORMAL>`

İlk satır geçerli bir pozitif tam sayı değilse veya herhangi bir XML satırı ayrıştırılamıyorsa yalnız tek satır `HATA` yazdır.

```stdin
2
<Event><System><EventID>8001</EventID></System><EventData></EventData></Event>
<Event><System><EventID>8002</EventID></System><EventData><Data Name="TargetUser">S-1-5-21-1001</Data><Data Name="FilePathBuffer">%SYSTEM32%\WINDOWSPOWERSHELL\V1.0\POWERSHELL.EXE</Data></EventData></Event>
<Event><System><EventID>8003</EventID></System><EventData><Data Name="TargetUser">S-1-5-21-1001</Data><Data Name="FilePathBuffer">%OSDRIVE%\TOOLS\RUBEUS.EXE</Data></EventData></Event>
<Event><System><EventID>8006</EventID></System><EventData><Data Name="TargetUser">S-1-5-21-1001</Data><Data Name="FilePathBuffer">%OSDRIVE%\TEMP\KESIF.PS1</Data></EventData></Event>
<Event><System><EventID>8007</EventID></System><EventData><Data Name="TargetUser">S-1-5-21-1001</Data><Data Name="FilePathBuffer">%OSDRIVE%\TEMP\PAYLOAD.PS1</Data></EventData></Event>
<Event><System><EventID>8004</EventID></System><EventData><Data Name="TargetUser">S-1-5-21-1002</Data><Data Name="FilePathBuffer">%OSDRIVE%\TEMP\MIMIKATZ.EXE</Data></EventData></Event>
<Event><System><EventID>8005</EventID></System><EventData><Data Name="TargetUser">S-1-5-21-1003</Data><Data Name="FilePathBuffer">%PROGRAMFILES%\ADMIN\BAKIM.PS1</Data></EventData></Event>
```

```starter
$satirlar = @($Girdi | Where-Object { ([string]$_).Trim() -ne "" })
if ($satirlar.Count -eq 0) { "HATA"; exit 0 }
# İlk satırdan EsikSayi değerini al, XML olaylarını ayrıştır, OLAY ve OZET satırlarını yazdır
```

```test
beklenen = (
    "OLAY|S-1-5-21-1001|EXE_DLL|DENETIM|RUBEUS.EXE\n"
    "OLAY|S-1-5-21-1001|MSI_SCRIPT|DENETIM|KESIF.PS1\n"
    "OLAY|S-1-5-21-1001|MSI_SCRIPT|ENGEL|PAYLOAD.PS1\n"
    "OLAY|S-1-5-21-1002|EXE_DLL|ENGEL|MIMIKATZ.EXE\n"
    "OZET|S-1-5-21-1001|ihlal=3|KRITIK\n"
    "OZET|S-1-5-21-1002|ihlal=1|NORMAL\n"
    "OZET|S-1-5-21-1003|ihlal=0|NORMAL\n"
)
eq(out, beklenen, "8003/8004/8006/8007 ihlalleri ve 3 > 2 KRITIK, 1 < 2 NORMAL, 0 < 2 NORMAL özeti")

uyari_esit = run(stdin=(
    "1\n"
    '<Event><System><EventID>8004</EventID></System><EventData><Data Name="TargetUser">S-1-5-21-99</Data><Data Name="FilePathBuffer">C:\\Temp\\a.exe</Data></EventData></Event>\n'
))
eq(uyari_esit,
   "OLAY|S-1-5-21-99|EXE_DLL|ENGEL|a.exe\nOZET|S-1-5-21-99|ihlal=1|UYARI\n",
   "EsikSayi=1 geçerli olmalı ve ihlal == EsikSayi (1 == 1) olduğunda UYARI vermeli")

eq(run(stdin="0\n"), "HATA\n", "EsikSayi < 1 ise HATA")
eq(run(stdin="abc\n"), "HATA\n", "sayı olmayan EsikSayi HATA")
eq(run(stdin="1\n<bozuk xml\n"), "HATA\n", "bozuk XML satırı HATA")
eq(run(stdin="1\n<Event><System></System></Event>\n"), "HATA\n", "EventID olmayan XML satırı HATA")
```

```solution
$satirlar = @($Girdi | Where-Object { ([string]$_).Trim() -ne "" })
if ($satirlar.Count -eq 0) { "HATA"; exit 0 }

$esik = 0
if (-not [int]::TryParse($satirlar[0].Trim(), [ref]$esik) -or $esik -lt 1) {
    "HATA"; exit 0
}

$tablo = @{
    8002 = @{ Kanal = "EXE_DLL";    Karar = "IZIN" }
    8003 = @{ Kanal = "EXE_DLL";    Karar = "DENETIM" }
    8004 = @{ Kanal = "EXE_DLL";    Karar = "ENGEL" }
    8005 = @{ Kanal = "MSI_SCRIPT"; Karar = "IZIN" }
    8006 = @{ Kanal = "MSI_SCRIPT"; Karar = "DENETIM" }
    8007 = @{ Kanal = "MSI_SCRIPT"; Karar = "ENGEL" }
}

$olayCikti = @()
$kullaniciSirasi = @()
$ihlalSayilari = @{}

for ($i = 1; $i -lt $satirlar.Count; $i++) {
    try {
        $x = [xml]$satirlar[$i]
    } catch {
        "HATA"; exit 0
    }
    if (-not $x.Event.System.EventID) {
        "HATA"; exit 0
    }
    $id = [int]$x.Event.System.EventID
    if (-not $tablo.ContainsKey($id)) { continue }

    $veri = @{}
    foreach ($d in $x.Event.EventData.Data) {
        if ($d.Name) { $veri[$d.Name] = $d.'#text' }
    }
    $kullanici = $veri['TargetUser']
    $dosya = Split-Path $veri['FilePathBuffer'] -Leaf
    $bilgi = $tablo[$id]

    if ($kullanici -notin $kullaniciSirasi) {
        $kullaniciSirasi += $kullanici
        $ihlalSayilari[$kullanici] = 0
    }

    if ($bilgi.Karar -in @("DENETIM", "ENGEL")) {
        $ihlalSayilari[$kullanici] += 1
        $olayCikti += "OLAY|$kullanici|$($bilgi.Kanal)|$($bilgi.Karar)|$dosya"
    }
}

foreach ($s in $olayCikti) { $s }
foreach ($k in $kullaniciSirasi) {
    $sayi = $ihlalSayilari[$k]
    $seviye = if ($sayi -gt $esik) { "KRITIK" } elseif ($sayi -eq $esik) { "UYARI" } else { "NORMAL" }
    "OZET|$k|ihlal=$sayi|$seviye"
}
```

```hint
Önce tüm XML satırlarını doğrulayıp `OLAY|...` satırlarını bir dizide biriktir; bozuk bir XML satırı varsa hiçbir şey yazdırmadan `HATA` döndürebilmek için çıktıyı döngü bittikten sonra yazdır.
```
:::


::: anlat Dosya köprüsü: gerçek okuyucu, üretilmiş olay verisi
Bu ek bölümün applocker.evtx dosyası metin XML değildir: PS27/28'in EVT hazırlayıcısıyla üretilen eğitim kayıtlarını Windows wevtutil gerçek EVTX'e dönüştürür; Get-WinEvent dosyayı gerçek okuyucuyla açar. **Olay içeriği sentetiktir.** Bu dosya gerçek bir AppLocker ilkesinin dosyayı engellediğinin kanıtı değildir. Host ilkesi, canlı günlük ve servis değiştirilmez. Manifest AppLocker kaydının şeması taklit edilmez: klasik EVT'den geldiği için Data öğeleri adsızdır, burada sözleşme [ilke, dosya, kural, SID] sırasıdır. Gerçek vaka kaydında ToXml ile EventData/UserData ve alan adlarını ayrıca kontrol et.

JEA dosyaları ise New-PSRoleCapabilityFile ve New-PSSessionConfigurationFile ile yerel geçici klasörde gerçekten üretilir. Test-PSSessionConfigurationFile sözdizimini doğrular; endpoint kayıt veya kimlik doğrulama kabulü değildir. Import-PowerShellDataFile veri okur, dosyayı komut olarak çalıştırmaz. Bu görev seçilen RoleDefinitions anahtarının bildirdiği dosyaları envantere alır; AD grup üyeliği çözmez, kullanıcı için etkin rol birleşimi hesaplamaz, JEA endpoint'i açmaz. Rol kısıtını görmek ile o endpoint'in çalıştığını ispatlamak ayrı kabullerdir.

Kaynak: [AppLocker olayları](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/app-control-for-business/applocker/using-event-viewer-with-applocker), [JEA rol yetenekleri](https://learn.microsoft.com/en-us/powershell/scripting/security/remoting/jea/role-capabilities), [Import-PowerShellDataFile](https://learn.microsoft.com/powershell/module/microsoft.powershell.utility/import-powershelldatafile).
:::

::: gorev EVTX'te izin, denetim ve engeli ayır
İlk girdi EVTX dosya yolu, ikinci girdi 0–5 dahil en yüksek Level olsun. Geçersiz girdi veya dosya yoksa HATA. Gerçek Get-WinEvent ile yalnız Microsoft-Windows-AppLocker sağlayıcısının 8002–8007 dahil olaylarını ve Level <= eşik olanları dosya sırasıyla oku. Bu kimlikleri karar olarak eşle: 8002/8005 ALLOW, 8003/8006 AUDIT, 8004/8007 BLOCK. Audit, engel değildir.

Her kayıt için record/id/decision/file/rule/sid alanlı nesne üret; veri dizisinde tam dört öğe [ilke, dosya, kural, SID] yoksa throw. JSON listesi yaz; tek kayıt ve boş sonuç da liste olmalı. Bozuk EVTX'i veya eksik alanı boş sonuç diye gizleme. Yerelleştirilmiş Message metnini ayrıştırma. Yalnız verilen dosyayı oku; canlı kanal kullanma.

```stdin
applocker.evtx
2
```
```setup
import os,runpy,sys
_s=os.path.dirname(next(m.__file__ for m in list(sys.modules.values()) if os.path.basename(getattr(m,'__file__',None) or '')=='py_harness.py'))
runpy.run_path(os.path.join(_s,'ps24_file_fixtures.py'),run_name='__tezgah__')
```
```starter
'[]'
```
```test
import json
all_rows=[{'record':i+1,'id':eid,'decision':('ALLOW','AUDIT','BLOCK')[i%3],'file':rf'C:\Pafta\file {eid}.exe','rule':f'Rule-{eid}','sid':'S-1-5-21-1000-2000-3000-1105'} for i,eid in enumerate(range(8002,8008))]
eq(json.loads(out),[all_rows[2],all_rows[5]],'Level 2 dahil; EXE ve SCRIPT blokları')
eq(json.loads(run(stdin='applocker.evtx\n3\n')),[row for i,row in enumerate(all_rows) if i%3 in (1,2)],'audit BLOCK diye etiketlenmez')
eq(json.loads(run(stdin='applocker.evtx\n4\n')),all_rows,'8002/8007 uçları, sağlayıcı ve kayıt sırası')
eq(json.loads(run(stdin='applocker.evtx\n0\n')),[],'alt Level ucu ve eşleşme yok')
eq(json.loads(run(stdin='empty.evtx\n5\n')),[],'üst Level ucu ve boş dosya')
eq(json.loads(run(stdin='alternate.evtx\n2\n')),[{'record':1,'id':8004,'decision':'BLOCK','file':r'C:\Different\changed.dll','rule':'Changed Rule','sid':'S-1-5-18'}],'dosya, kural ve SID sabit değildir')
for body in ('applocker.evtx\n-1\n','applocker.evtx\n6\n','applocker.evtx\nx\n','missing.evtx\n2\n',''):
    eq(run(stdin=body),'HATA\n','dosya ve eşik girdi denetimi')
for name in ('corrupt.evtx','missing-fields.evtx'):
    r=calis(stdin=name+'\n2\n');ok(r['kod']!=0,'bozuk dosya/alan hata vermeli')
```
```solution
$level=0
if ($Girdi.Count -lt 2 -or -not [int]::TryParse($Girdi[1],[ref]$level) -or $level -lt 0 -or $level -gt 5 -or -not (Test-Path -LiteralPath $Girdi[0] -PathType Leaf)) { 'HATA'; exit 0 }
$query="*[System[Provider[@Name='Microsoft-Windows-AppLocker'] and (EventID>=8002 and EventID<=8007) and Level<=$level]]"
try { $events=@(Get-WinEvent -Path $Girdi[0] -FilterXPath $query -Oldest -ErrorAction Stop) }
catch { if ($_.FullyQualifiedErrorId -notlike 'NoMatchingEventsFound*') { throw }; $events=@() }
try {
    $result=@(foreach($event in $events) {
        if ($event.Properties.Count -ne 4) { throw 'Beklenmeyen egitim kaydi semasi' }
        $decision=switch($event.Id) {8002 {'ALLOW'} 8005 {'ALLOW'} 8003 {'AUDIT'} 8006 {'AUDIT'} 8004 {'BLOCK'} 8007 {'BLOCK'}}
        [pscustomobject]@{record=[int]$event.RecordId;id=[int]$event.Id;decision=$decision;file=[string]$event.Properties[1].Value;rule=[string]$event.Properties[2].Value;sid=[string]$event.Properties[3].Value}
    })
    ConvertTo-Json -InputObject $result -Compress -Depth 5
} finally { foreach($event in $events) { $event.Dispose() } }
```
:::

::: gorev Gerçek PSSC ve PSRC dosyalarındaki rol kapsamını oku
İlk girdi .pssc dosyası, ikinci girdi RoleDefinitions içindeki tam grup anahtarı. Import-PowerShellDataFile ile oturum ve RoleCapabilities/<rol>.psrc dosyalarını veri olarak oku. Seçilen anahtar yoksa, rol dosyası eksikse, rol adı ^[A-Za-z][A-Za-z0-9_-]*$ biçiminde değilse veya veri dosyası bozuk/dinamikse HATA. SessionType yalnız Default/RestrictedRemoteServer/Empty; RunAsVirtualAccount varsa gerçek boolean olmalı (metin 'false' kabul edilmez). Dosyayı dot-source/Invoke-Expression ile çalıştırma. Tam anahtar üzerinden envanter isteniyor; grup üyeliği sorgulama.

JSON nesnesi: session_type (SessionType), virtual_account (RunAsVirtualAccount bool; yoksa false), roles (bildirim sıralı liste). Her rol name, cmdlets (VisibleCmdlets değerleri; string/hashtable ve Parameters kısıtları korunur), external_commands (VisibleExternalCommands), providers (VisibleProviders) alanlarını taşısın. Eksik listeler [] olmalı. Rol kısıtlarının yürürlükte olduğunu değil, dosyada ne bildirildiğini raporla. Get-Service gibi cmdlet'leri ve harici komutları bu envanter için çalıştırma.

```stdin
limited.pssc
PAFTA\Analistler
```
```setup
import os,runpy,sys
_s=os.path.dirname(next(m.__file__ for m in list(sys.modules.values()) if os.path.basename(getattr(m,'__file__',None) or '')=='py_harness.py'))
runpy.run_path(os.path.join(_s,'ps24_file_fixtures.py'),run_name='__tezgah__')
```
```starter
'{}'
```
```test
import json,pathlib
reader={'name':'Reader','cmdlets':['Get-Service',{'Name':'Restart-Service','Parameters':{'Name':'Name','ValidateSet':['Dns','Spooler']}}],'external_commands':[r'C:\Windows\System32\whoami.exe'],'providers':[]}
inventory={'name':'Inventory','cmdlets':['Get-Process'],'external_commands':[],'providers':['FileSystem']}
eq(json.loads(out),{'session_type':'RestrictedRemoteServer','virtual_account':True,'roles':[reader,inventory]},'gerçek üretilmiş PSSC/PSRC, iki rol ve parametre kısıtı')
eq(json.loads(run(stdin='limited.pssc\nPAFTA\\SaltOku\n')),{'session_type':'RestrictedRemoteServer','virtual_account':True,'roles':[inventory]},'seçilen grup anahtarı')
eq(json.loads(run(stdin='alternate.pssc\nPAFTA\\Analistler\n')),{'session_type':'Default','virtual_account':False,'roles':[inventory]},'oturum türü ve varsayılan false sabit değildir')
for body in ('limited.pssc\nPAFTA\\Yok\n','missing.pssc\nPAFTA\\Analistler\n','dynamic.pssc\nPAFTA\\Analistler\n',''):
    eq(run(stdin=body),'HATA\n','eksik/bozuk/dinamik veri ve grup yok')
ok(not pathlib.Path('executed.txt').exists(),'veri dosyasındaki ifade çalıştırılmadı')
role=pathlib.Path('RoleCapabilities/Inventory.psrc');saved=role.read_bytes()
try:
    role.unlink()
    eq(run(stdin='limited.pssc\nPAFTA\\SaltOku\n'),'HATA\n','bağlı rol dosyası yok')
finally:role.write_bytes(saved)
# Rol dosyasının gerçek kısıtı değişince rapor da değişmeli.
role=pathlib.Path('RoleCapabilities/Reader.psrc');saved=role.read_text(encoding='utf-8-sig')
try:
    role.write_text(saved.replace("'Spooler'","'W3SVC'"),encoding='utf-8-sig')
    changed=json.loads(run(stdin='limited.pssc\nPAFTA\\Analistler\n'))
    eq(changed['roles'][0]['cmdlets'][1]['Parameters']['ValidateSet'],['Dns','W3SVC'],'dosyadaki değişen kısıt okunur')
finally:role.write_text(saved,encoding='utf-8-sig')
pathlib.Path('bad-role.pssc').write_text("@{SessionType='Default';RoleDefinitions=@{'PAFTA\\Analistler'=@{RoleCapabilities=@('../Reader')}}}",encoding='utf-8-sig')
eq(run(stdin='bad-role.pssc\nPAFTA\\Analistler\n'),'HATA\n','rol adından üst klasöre çıkılmaz')
pathlib.Path('bad-type.pssc').write_text("@{SessionType='Default';RunAsVirtualAccount='false';RoleDefinitions=@{'PAFTA\\Analistler'=@{RoleCapabilities=@('Inventory')}}}",encoding='utf-8-sig')
eq(run(stdin='bad-type.pssc\nPAFTA\\Analistler\n'),'HATA\n','metin false gerçek boolean değildir')
```
```solution
$ErrorActionPreference='Stop'
if ($Girdi.Count -lt 2) { 'HATA'; exit 0 }
try {
    $configuration=Import-PowerShellDataFile -LiteralPath $Girdi[0]
    if ($configuration -isnot [hashtable] -or $configuration.RoleDefinitions -isnot [hashtable] -or $configuration.SessionType -notin @('Default','RestrictedRemoteServer','Empty')) { throw 'Oturum verisi gecersiz' }
    if ($configuration.ContainsKey('RunAsVirtualAccount') -and $configuration.RunAsVirtualAccount -isnot [bool]) { throw 'Sanal hesap degeri boolean olmali' }
    $group=$Girdi[1]
    if (-not $configuration.RoleDefinitions.ContainsKey($group)) { throw 'Grup yok' }
    $roles=@(foreach($name in @($configuration.RoleDefinitions[$group].RoleCapabilities)) {
        if ($name -cnotmatch '^[A-Za-z][A-Za-z0-9_-]*$') { throw 'Rol adi kapsam disi' }
        $rolePath=Join-Path (Split-Path (Resolve-Path -LiteralPath $Girdi[0]).Path -Parent) "RoleCapabilities/$name.psrc"
        if (-not (Test-Path -LiteralPath $rolePath -PathType Leaf)) { throw 'Rol dosyasi yok' }
        $role=Import-PowerShellDataFile -LiteralPath $rolePath
        if ($role -isnot [hashtable]) { throw 'Rol verisi gecersiz' }
        [pscustomobject]@{name=$name;cmdlets=@($role.VisibleCmdlets | Where-Object { $null -ne $_ });external_commands=@($role.VisibleExternalCommands | Where-Object { $null -ne $_ });providers=@($role.VisibleProviders | Where-Object { $null -ne $_ })}
    })
    [pscustomobject]@{session_type=$configuration.SessionType;virtual_account=[bool]$configuration.RunAsVirtualAccount;roles=$roles} | ConvertTo-Json -Depth 10 -Compress
} catch { 'HATA' }
```
:::
