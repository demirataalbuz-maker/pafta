---
id: ps22
title: Get-Acl · NTFS ve Kayıt Defteri İzinleri
summary: Bir ACL'yi okumak; ACE alanları, devralma bayrakları, açık Deny'ın Allow'a üstünlüğü ve kanonik sıra, sahiplik, SDDL'in altı alanı ve kayıt defteri anahtarlarında RegistryRights.
kazanim: AZ040 4.2
---

::: anlat Bir ACL neyi söyler
"Bu klasöre kim erişebilir?" sorusunun cevabı dosyanın kendisinde değil, ona iliştirilmiş **güvenlik tanımlayıcısında** (security descriptor) durur. `Get-Acl` onu bir nesne olarak getirir:

| Özellik | Ne tutar |
|---|---|
| `Owner` | Sahibin adı, `DOMAIN\kullanıcı` biçiminde bir metin |
| `Group` | Birincil grup (Windows'ta çoğunlukla önemsizdir) |
| `Access` | **ACE** listesi: izin kayıtlarının kendisi |
| `Sddl` | Tanımlayıcının tamamının metin hâli |
| `AreAccessRulesProtected` | Devralma kesilmiş mi |

Listedeki her kayıt bir **ACE**'dir (Access Control Entry) ve beş şeyi söyler:

```powershell norun
Get-Acl -Path C:\Veri |
    Select-Object -ExpandProperty Access |
    Format-Table IdentityReference, AccessControlType, FileSystemRights, IsInherited, InheritanceFlags
```

| Alan | Anlamı |
|---|---|
| `IdentityReference` | Kime: kullanıcı, grup ya da çözülemediyse ham SID |
| `AccessControlType` | `Allow` ya da `Deny` |
| `FileSystemRights` | Hangi haklar (kayıt defterinde `RegistryRights`) |
| `IsInherited` | Bu kural üst klasörden mi geldi, buraya mı yazıldı |
| `InheritanceFlags` / `PropagationFlags` | Kural alt öğelere nasıl iner |

Hak adları birer **bayrak kümesidir**; sayısal maskeye çevrilirler ve bazıları sessizce başka bitler ekler:

```powershell
foreach ($hak in "Read", "ReadAndExecute", "Modify", "FullControl") {
    $kural = New-Object Security.AccessControl.FileSystemAccessRule("BUILTIN\Users", $hak, "Allow")
    "{0,-15} {1,-38} 0x{2:x}" -f $hak, $kural.FileSystemRights, [int]$kural.FileSystemRights
}
```

> [!TUZAK] `Read` istedin, `Read, Synchronize` aldın
> `Read`, `Write`, `Modify` ve `ReadAndExecute` değerlerinin hepsi `Synchronize` bitini de taşır; yalnız `FullControl` tek başına görünür. Bu yüzden bir ACE'yi "tam olarak `Read` mi?" diye metin karşılaştırmasıyla aramak yanıltır. Hakları **maske üzerinden** karşılaştır.
:::

::: anlat Devralma, kanonik sıra ve Deny'ın üstünlüğü
Bir klasöre yazdığın kural, bayraklarına göre alt öğelere iner:

| Bayrak | Anlamı |
|---|---|
| `ContainerInherit` | Alt **klasörlere** iner |
| `ObjectInherit` | Alt **dosyalara** iner |
| `InheritOnly` (PropagationFlags) | Kural nesnenin kendisine uygulanmaz, yalnız iner |
| `NoPropagateInherit` (PropagationFlags) | Yalnız bir kuşak iner, torunlara geçmez |

Alt öğede o kural `IsInherited = True` görünür ve **oradan silinemez**: devralınan bir kuralı kaldırmanın yolu ya üstte kaldırmak ya da devralmayı kesmektir.

```powershell norun
$acl = Get-Acl -Path .\veri
$acl.SetAccessRuleProtection($true, $true)   # devralmayı kes, mevcutları kopya olarak tut
Set-Acl -Path .\veri -AclObject $acl
```

> [!TUZAK] İkinci argüman `$false` ise ACL boşalır
> `SetAccessRuleProtection($true, $false)` devralmayı keser ve devralınanları **kopyalamaz**: geriye sıfır ACE kalır. Boş bir DACL "herkese kapalı" demektir; klasörü artık okuyamaz, silemez, hatta çoğu durumda ACL'sini `Set-Acl` ile düzeltemezsin (sahibi olsan bile `SeSecurityPrivilege` isteyebilir). Kurtarma yolu yükseltilmiş bir kabukta `icacls <yol> /reset`tir. Denemelerini her zaman yeni oluşturduğun geçici bir klasörde yap.

Windows bir erişim isteğini değerlendirirken ACE'lere **sırayla** bakar ve ilk kesin cevapta durur. Bu yüzden listenin sırası önemlidir; Windows ACL'yi yazarken **kanonik sıraya** sokar:

1. Açık (`IsInherited = False`) `Deny` kuralları
2. Açık `Allow` kuralları
3. Devralınan `Deny` kuralları
4. Devralınan `Allow` kuralları

Sonuç: **açık bir `Deny`, açık bir `Allow`'u ezer**; ama açık bir `Allow`, üstten devralınan bir `Deny`'ı ezer. Hiçbir kural eşleşmezse cevap sessizce "hayır"dır — Windows'ta izin verilmeyen her şey yasaktır.

`Set-Acl` eklediğin kuralı bu sıraya yerleştirir: `Deny`'ı en sona eklesen bile listede başa geçer. Buna karşılık ham bir tanımlayıcıyı (`RawSecurityDescriptor`) elle kurduğunda sıralama **sana** bırakılır.
:::

::: anlat SDDL ve kayıt defteri
`Sddl` özelliği bütün tanımlayıcıyı tek bir metinde taşır: `O:` sahip, `G:` grup, `D:` DACL, `S:` SACL. DACL içindeki her ACE parantez içinde **altı alandır**:

```text
(A;OICIID;0x1200a9;;;WD)
 │ │      │        │││
 │ │      │        ││└─ kim (SID ya da kısaltma: BA yönetciler, BU kullanıcılar, WD herkes)
 │ │      │        ││
 │ │      │        └┴─ nesne türü GUID'leri (dosya ve kayıt defterinde boş)
 │ │      └─ erişim maskesi (FA, FR, KR gibi kısaltma ya da 0x… )
 │ └─ bayraklar (OI nesneye, CI kaba iner, ID devralınmış)
 └─ ACE türü: A = Allow, D = Deny
```

Bu metni koda çevirmek için `RawSecurityDescriptor` yeter; bir dosyaya dokunmadan, makineden bağımsız çalışır:

```powershell
$sd = New-Object Security.AccessControl.RawSecurityDescriptor("O:BAG:BAD:AI(D;;FW;;;BU)(A;ID;FA;;;BA)")
"sahip: " + $sd.Owner.Value
foreach ($ace in $sd.DiscretionaryAcl) {
    "{0,-14} 0x{1:x} bayraklar={2}" -f $ace.AceType, $ace.AccessMask, $ace.AceFlags
}
```

> [!TUZAK] `AceFlags` üzerinde `-band` çalışmaz
> `$ace.AccessMask` bir sayıdır, `-band` ile rahatça bit sınarsın. Ama `$ace.AceFlags` **bayt tabanlı** bir enum'dur ve Windows PowerShell 5.1'de `-band` onu dönüştüremez: `Specified cast is not valid` hatası verir. Bayrak sınamak için `.HasFlag(...)` kullan ya da önce `[int]`'e çevir. Hata `$ErrorActionPreference` varsayılanında betiği durdurmaz; değişken sessizce `$null` kalır ve çıktıda boş bir alan görürsün.

**Kayıt defteri** aynı modeli kullanır; yalnız haklar `FileSystemRights` yerine `RegistryRights`tir (`ReadKey`, `WriteKey`, `FullControl`, `SetValue`, `CreateSubKey`) ve `Get-Acl` bir `RegistryAccessRule` döndürür:

```powershell norun
New-Item -Path "HKCU:\Software\Deneme" -Force | Out-Null
$acl = Get-Acl -Path "HKCU:\Software\Deneme"
$acl.Access | Format-Table IdentityReference, AccessControlType, RegistryRights, IsInherited
Remove-Item -Path "HKCU:\Software\Deneme" -Recurse -Force
```

> [!GÜVENLİK]
> Bir denetimde `Get-Acl`'in söylediği ile gerçekte olan aynı şey değildir. ACL, yetki zincirinin yalnız bir halkasıdır: sahiplik (sahip ACL'yi her zaman yeniden yazabilir), grup üyelikleri, `SeBackupPrivilege` gibi ayrıcalıklar ve paylaşım (share) izinleri sonucu değiştirir. Bulgunu "şu kullanıcı bu dosyayı okuyabiliyor" diye yazacaksan ACL'yi okumakla yetinme, o kimlikle gerçekten dene. Denemeleri kendi oluşturduğun geçici klasör ve `HKCU` anahtarlarında yap; sistem yollarının izinlerini değiştirme.
:::

::: tahmin
Ne yazar?

```powershell
$kural = New-Object Security.AccessControl.FileSystemAccessRule("BUILTIN\Users", "Read", "Allow")
"{0} -> {1}" -f $kural.AccessControlType, $kural.FileSystemRights

$sd = New-Object Security.AccessControl.RawSecurityDescriptor("D:(A;;FA;;;BA)(D;;FW;;;BU)")
$sd.DiscretionaryAcl.Count
foreach ($ace in $sd.DiscretionaryAcl) {
    "{0} 0x{1:x}" -f $ace.AceType, $ace.AccessMask
}
```

???

`Allow -> Read, Synchronize`, `2`, `AccessAllowed 0x1f01ff`, `AccessDenied 0x120116`.

İlk satır bu dersin tuzağı: `Read` istedin ama kural `Read, Synchronize` oldu. İkinci bölümde SDDL iki ACE taşır, `Count` 2 verir. `FA` (full access) maskesi `0x1f01ff`, `FW` (file generic write) maskesi `0x120116`'dır. Dikkat: ACE'ler **verdiğin sırada** durur, `Allow` önce gelir — `RawSecurityDescriptor` kanonik sıraya sokmaz. Aynı iki kuralı `Set-Acl` ile gerçek bir dosyaya yazsaydın Windows `Deny`'ı başa alırdı.
:::

::: gorev SDDL'yi tabloya çevir
`$Girdi`'nin **ilk satırında** bir SDDL metni, **ikinci satırında** `0x` ile başlayan bir erişim maskesi var. DACL'deki her ACE için sırayla bir satır yazdır:

```text
<AceType>|0x<maske>|<devralindi>|<yeterli>
```

- `devralindi`: ACE'nin bayrakları `Inherited` içeriyorsa `evet`, değilse `hayir`
- `yeterli`: ACE maskesi istenen bitlerin **hepsini** taşıyorsa `evet`, taşımıyorsa `hayir`

SDDL ayrıştırılamıyorsa tek satır `HATA` yazdır ve başka hiçbir şey yazdırma.

```stdin
D:AI(D;;FW;;;BU)(A;ID;FA;;;BA)(A;OICIID;0x1200a9;;;WD)
0x2
```

```starter
$sddl = $Girdi[0].Trim()
$istenen = [Convert]::ToInt32($Girdi[1].Trim(), 16)

$sd = New-Object Security.AccessControl.RawSecurityDescriptor($sddl)
foreach ($ace in $sd.DiscretionaryAcl) {
    # AceType | maske | devralindi | yeterli
}
```

```test
eq(out, "AccessDenied|0x120116|hayir|evet\nAccessAllowed|0x1f01ff|evet|evet\nAccessAllowed|0x1200a9|evet|hayir\n",
   "üç ACE sırayla; FW ve FA yazma bitini taşır, 0x1200a9 taşımaz")

tam = run(stdin="D:(A;;0x1200a9;;;WD)\n0x1200a9\n")
eq(tam, "AccessAllowed|0x1200a9|hayir|evet\n", "maske tam eşitse yeterli")

eksik = run(stdin="D:(A;;0x1200a9;;;WD)\n0x1200ab\n")
eq(eksik, "AccessAllowed|0x1200a9|hayir|hayir\n", "tek bit bile eksikse yeterli değil")

sifir = run(stdin="D:(A;;0x1200a9;;;WD)\n0x0\n")
eq(sifir, "AccessAllowed|0x1200a9|hayir|evet\n", "istenen maske 0 ise her ACE yeterlidir")

bos = run(stdin="D:\n0x2\n")
eq(bos, "", "DACL boşsa hiç satır yazılmaz")

hatali = run(stdin="bu bir sddl degil\n0x2\n")
eq(hatali, "HATA\n", "ayrıştırılamayan SDDL için tek satır HATA")
```

```solution
$sddl = $Girdi[0].Trim()
$istenen = [Convert]::ToInt32($Girdi[1].Trim(), 16)

try {
    $sd = New-Object Security.AccessControl.RawSecurityDescriptor($sddl)
} catch {
    "HATA"
    exit 0
}

foreach ($ace in $sd.DiscretionaryAcl) {
    $devralindi = if ($ace.AceFlags.HasFlag([Security.AccessControl.AceFlags]::Inherited)) { "evet" } else { "hayir" }
    $yeterli = if (($ace.AccessMask -band $istenen) -eq $istenen) { "evet" } else { "hayir" }
    "{0}|0x{1:x}|{2}|{3}" -f $ace.AceType, $ace.AccessMask, $devralindi, $yeterli
}
```

```hint
Bozuk SDDL `RawSecurityDescriptor` kurucusunda istisna fırlatır: `try { ... } catch { "HATA"; exit 0 }`.
```

```hint
Devralma bayrağı bir bayrak kümesidir, eşitlikle bakma: `$ace.AceFlags.HasFlag([Security.AccessControl.AceFlags]::Inherited)`. `AceFlags` bayt tabanlı olduğu için `-band` işlecini doğrudan uygulayamazsın. Maskenin bütün bitleri için `($maske -band $istenen) -eq $istenen`; `AccessMask` sayıdır, orada `-band` çalışır.
```
:::

::: gorev Etkin yetkiyi hesapla
`$Girdi`'nin ilk satırı sorudur: `KIMLIK 0xMASKE`. Kalan satırların her biri bir ACE'dir:

```text
<Allow|Deny>;<evet|hayir devralındı>;<KIMLIK>;0x<maske>
```

Windows'un kanonik sırasını uygula: önce **açık Deny**, sonra **açık Allow**, sonra **devralınan Deny**, en sonra **devralınan Allow**. Her grubun içinde girdi sırasını koru. Kimliği soruyla aynı olan ilk ACE'de karar ver:

- `Deny` ise ve maskesi istenen bitlerden **en az birini** içeriyorsa karar `RET`
- `Allow` ise ve maskesi istenen bitlerin **hepsini** içeriyorsa karar `IZIN`
- ikisi de değilse o ACE karar vermez, sıradakine bak

Tek satır yazdır: `IZIN|<numara>` ya da `RET|<numara>`; numara ACE'nin **girdideki** 1'den başlayan sırasıdır. Hiçbir ACE karar vermezse `RET|-` yazdır (eşleşmeyen istek reddedilir). Bir ACE satırı dört alandan oluşmuyorsa tek satır `HATA` yazdır.

```stdin
ALICE 0x2
Allow;hayir;ALICE;0x120089
Deny;evet;ALICE;0x4
Allow;hayir;BOB;0x1f01ff
Allow;evet;ALICE;0x1f01ff
```

```starter
$parcalar = $Girdi[0].Trim() -split "\s+"
$kimlik = $parcalar[0]
$istenen = [Convert]::ToInt32($parcalar[1], 16)

# ACE satırlarını oku, kanonik sıraya diz, ilk karar veren ACE'yi bul
```

```test
eq(out, "IZIN|4\n", "açık Allow 0x2'yi kapsamıyor, devralınan Deny 0x4 ile çakışmıyor; karar devralınan Allow'da")

cakisan_deny = run(stdin="ALICE 0x2\nAllow;hayir;ALICE;0x120089\nDeny;evet;ALICE;0x2\nAllow;evet;ALICE;0x1f01ff\n")
eq(cakisan_deny, "RET|2\n", "devralınan Deny çakışırsa devralınan Allow'dan önce karar verir")

acik_deny = run(stdin="ALICE 0x2\nAllow;hayir;ALICE;0x1f01ff\nDeny;hayir;ALICE;0x2\n")
eq(acik_deny, "RET|2\n", "açık Deny açık Allow'u ezer, sırası sonra olsa bile")

devralinan_deny = run(stdin="ALICE 0x2\nDeny;evet;ALICE;0x1f01ff\nAllow;hayir;ALICE;0x2\n")
eq(devralinan_deny, "IZIN|2\n", "açık Allow devralınan Deny'ı ezer")

tam = run(stdin="ALICE 0x3\nAllow;hayir;ALICE;0x3\n")
eq(tam, "IZIN|1\n", "maske tam eşitse izin")

eksik = run(stdin="ALICE 0x3\nAllow;hayir;ALICE;0x1\n")
eq(eksik, "RET|-\n", "Allow bitlerin hepsini kapsamıyorsa karar vermez")

fazla = run(stdin="ALICE 0x3\nAllow;hayir;ALICE;0x1f01ff\n")
eq(fazla, "IZIN|1\n", "Allow istenenden fazlasını kapsıyorsa izin")

kismi_deny = run(stdin="ALICE 0x3\nDeny;hayir;ALICE;0x1\n")
eq(kismi_deny, "RET|1\n", "Deny tek ortak bitte bile reddeder")

baska = run(stdin="ALICE 0x2\nAllow;hayir;BOB;0x1f01ff\n")
eq(baska, "RET|-\n", "başka kimliğin kuralı karar vermez")

bos = run(stdin="ALICE 0x2\n")
eq(bos, "RET|-\n", "hiç ACE yoksa istek reddedilir")

hatali = run(stdin="ALICE 0x2\nAllow;hayir;ALICE\n")
eq(hatali, "HATA\n", "dört alanı olmayan satır HATA")

for metin,expected in [('ALICE 0x2\nAllow;evet;ALICE;0x2\nDeny;evet;ALICE;0x2\n','RET|2\n'),('ALICE 0x2\nAllow;evet;ALICE;0x2\n','IZIN|1\n'),('ALICE 0x2\nDeny;evet;ALICE;0x4\nAllow;evet;ALICE;0x2\n','IZIN|2\n')]:
    r=calis(stdin=metin)
    eq((r['kod'],r['cikti'],r['hata']),(0,expected,''),'son iki kanonik grup ve temiz stderr')


r=calis(stdin='ALICE 0x2\nAllow;evet;ALICE;0x2\nDeny;hayir;BOB;0x1\n')
eq((r['kod'],r['cikti'],r['hata']),(0,'IZIN|1\n',''),'devralınan Allow var, diğer kimliğin açık Deny kaydı karar vermez')

```

```solution
$parcalar = $Girdi[0].Trim() -split "\s+"
$kimlik = $parcalar[0]
$istenen = [Convert]::ToInt32($parcalar[1], 16)

$aceler = @()
for ($i = 1; $i -lt $Girdi.Count; $i++) {
    $satir = $Girdi[$i].Trim()
    if (-not $satir) { continue }
    $alan = $satir -split ";"
    if ($alan.Count -ne 4) { "HATA"; exit 0 }
    $aceler += [pscustomobject]@{
        No = $i
        Tur = $alan[0].Trim()
        Devralindi = ($alan[1].Trim() -eq "evet")
        Kimlik = $alan[2].Trim()
        Maske = [Convert]::ToInt32($alan[3].Trim(), 16)
    }
}

$sirali = @($aceler | Where-Object { -not $_.Devralindi -and $_.Tur -eq "Deny" }) +
          @($aceler | Where-Object { -not $_.Devralindi -and $_.Tur -eq "Allow" }) +
          @($aceler | Where-Object { $_.Devralindi -and $_.Tur -eq "Deny" }) +
          @($aceler | Where-Object { $_.Devralindi -and $_.Tur -eq "Allow" })

foreach ($ace in $sirali) {
    if ($ace.Kimlik -ne $kimlik) { continue }
    if ($ace.Tur -eq "Deny" -and ($ace.Maske -band $istenen) -ne 0) { "RET|" + $ace.No; exit 0 }
    if ($ace.Tur -eq "Allow" -and ($ace.Maske -band $istenen) -eq $istenen) { "IZIN|" + $ace.No; exit 0 }
}
"RET|-"
```

```hint
Dört listeyi ayrı ayrı süzüp `+` ile birleştirmek kanonik sırayı kurmanın en okunur yoludur; `Where-Object` girdi sırasını korur.
```

```hint
Deny ile Allow'un eşik kuralı **farklıdır**: Deny için `-band` sonucu sıfırdan farklı olmalı (tek ortak bit yeter), Allow için `-band` sonucu istenenin **tamamına** eşit olmalı.
```
:::

::: gorev Gerçek ACL raporu
Şimdi gerçek nesnelerle çalış. `$Girdi`'nin ilk satırı `klasor`, `anahtar` ya da `ikisi` olur; başka bir değer (boş satır dâhil) için tek satır `HATA` yazdır.

İstenen her kaynak için:

- **klasor**: çalışma klasöründe `acl_deneme` adlı bir klasör oluştur, geçerli kullanıcıya `ReadAndExecute` hakkını `ContainerInherit, ObjectInherit` bayraklarıyla **açık** bir `Allow` kuralı olarak ekle, sonra klasörün **açık** (devralınmamış) kurallarını yazdır.
- **anahtar**: `HKCU:\Software\PaftaAclGecici` anahtarını oluştur, geçerli kullanıcıya `ReadKey` hakkını `ContainerInherit` bayrağıyla açık bir `Allow` kuralı olarak ekle, sonra açık kurallarını yazdır.

Satır biçimi (`ikisi` için önce klasör, sonra anahtar):

```text
KLASOR|<AccessControlType>|<FileSystemRights>|<InheritanceFlags>
ANAHTAR|<AccessControlType>|<RegistryRights>|<InheritanceFlags>
```

Sonunda kayıt defteri anahtarını **sil** ve anahtar gerçekten yoksa son satıra `TEMIZ` yazdır. Geçerli kullanıcının adını `[Security.Principal.WindowsIdentity]::GetCurrent().Name` ile al; makineye özel bir ad yazma.

```stdin
ikisi
```

```starter
$ne = $Girdi[0].Trim()
$ben = [Security.Principal.WindowsIdentity]::GetCurrent().Name
$anahtar = "HKCU:\Software\PaftaAclGecici"

# klasor / anahtar / ikisi
```

```test
eq(out, "KLASOR|Allow|ReadAndExecute, Synchronize|ContainerInherit, ObjectInherit\n"
        "ANAHTAR|Allow|ReadKey|ContainerInherit\n"
        "TEMIZ\n",
   "iki kaynak da açık kuralıyla listelenir, anahtar silinir")

yalniz_klasor = run(stdin="klasor\n")
eq(yalniz_klasor, "KLASOR|Allow|ReadAndExecute, Synchronize|ContainerInherit, ObjectInherit\nTEMIZ\n",
   "yalnız klasör istendiğinde anahtar satırı yazılmaz")

yalniz_anahtar = run(stdin="anahtar\n")
eq(yalniz_anahtar, "ANAHTAR|Allow|ReadKey|ContainerInherit\nTEMIZ\n",
   "yalnız anahtar istendiğinde klasör satırı yazılmaz")

tekrar = run(stdin="ikisi\n")
ok(tekrar.strip().endswith("TEMIZ"), "temizlik yapıldığı için ikinci çalıştırma da aynı sonucu verir")

bos = run(stdin="\n")
eq(bos, "HATA\n", "boş girdi HATA")

gecersiz = run(stdin="hepsi\n")
eq(gecersiz, "HATA\n", "tanınmayan değer HATA")

ok("GetCurrent" in src, "geçerli kullanıcıyı çalışma anında al, adı koda yazma")

for value in ('ikisi','klasor','anahtar','hepsi',''):
    r=calis(stdin=value+'\n')
    eq(r['hata'],'','başarı ve geçersiz girdide stderr temizliği')

```

```solution
$ne = $Girdi[0].Trim()
$ben = [Security.Principal.WindowsIdentity]::GetCurrent().Name
$anahtar = "HKCU:\Software\PaftaAclGecici"

if ($ne -notin @("klasor", "anahtar", "ikisi")) { "HATA"; exit 0 }

if ($ne -in @("klasor", "ikisi")) {
    $klasor = Join-Path (Get-Location) "acl_deneme"
    New-Item -ItemType Directory -Path $klasor -Force | Out-Null
    $acl = Get-Acl -Path $klasor
    $acl.AddAccessRule((New-Object Security.AccessControl.FileSystemAccessRule(
        $ben, "ReadAndExecute", "ContainerInherit, ObjectInherit", "None", "Allow")))
    Set-Acl -Path $klasor -AclObject $acl
    foreach ($a in (Get-Acl -Path $klasor).Access | Where-Object { -not $_.IsInherited }) {
        "KLASOR|{0}|{1}|{2}" -f $a.AccessControlType, $a.FileSystemRights, $a.InheritanceFlags
    }
}

if ($ne -in @("anahtar", "ikisi")) {
    Remove-Item -Path $anahtar -Recurse -Force -ErrorAction SilentlyContinue
    New-Item -Path $anahtar -Force | Out-Null
    $racl = Get-Acl -Path $anahtar
    $racl.AddAccessRule((New-Object Security.AccessControl.RegistryAccessRule(
        $ben, "ReadKey", "ContainerInherit", "None", "Allow")))
    Set-Acl -Path $anahtar -AclObject $racl
    foreach ($a in (Get-Acl -Path $anahtar).Access | Where-Object { -not $_.IsInherited }) {
        "ANAHTAR|{0}|{1}|{2}" -f $a.AccessControlType, $a.RegistryRights, $a.InheritanceFlags
    }
}

Remove-Item -Path $anahtar -Recurse -Force -ErrorAction SilentlyContinue
if (-not (Test-Path -Path $anahtar)) { "TEMIZ" }
```

```hint
Yeni bir klasörün bütün kuralları devralınmıştır; eklediğin kural tek "açık" kural olur. Süzgeç: `Where-Object { -not $_.IsInherited }`.
```

```hint
Dosya sisteminde `FileSystemAccessRule` ve `FileSystemRights`, kayıt defterinde `RegistryAccessRule` ve `RegistryRights` kullanılır. Kurucunun beş argümanlı biçimi: kimlik, haklar, InheritanceFlags, PropagationFlags, tür.
```

```hint
Anahtarı en sonda, `klasor` seçilmiş olsa bile sil: `Remove-Item ... -ErrorAction SilentlyContinue` yoksa da hata vermez. `TEMIZ` satırını `Test-Path` sonucuna bak yazdır.
```
:::


::: anlat ACL satırı ile gerçek dosya açılışı farklı kanıtlardır
Açık bir ReadData Deny kuralı geçerli kullanıcının dosya baytlarını normal açışını engeller. WriteData Deny ise aynı okuma denemesini engellemez. Kullanıcı/SID ve işlem türünü söylemeden yalnız Deny var demek eksik bir bulgudur. Bu bölüm geçerli Windows token'ıyla gerçek File.ReadAllBytes çağırır; yedekleme semantiği, farklı hesap/SMB paylaşımı veya bütün etkin erişim haklarının genel hesaplaması değildir.

PowerShell 5.1'de .NET statik yöntem hatası MethodInvocationException içinde UnauthorizedAccessException olarak gelebilir. InnerException zincirinde bu türü ara; her hatayı erişim reddi diye etiketleme. Aynı dosyada önce oku, sonra Deny ekleyip tekrar oku, özgün ACL'yi finally ile geri yükleyip üçüncü kez oku. Deny yalnız ReadData/WriteData bitine uygulanır; ACL okuma/değiştirme veya Delete reddedilmez. Boş DACL/FullControl Deny kullanma; geçici klasörü kilitleme.

Sahiplik, ACL'yi değiştirme imkânı ve dosyayı o an okuma kararı aynı şey değildir. Burada sahibi olan kullanıcı da normal dosya açılışında ReadData Deny yüzünden reddedildi; sonra özgün ACL geri yüklendi. Yalnız çalışma klasöründeki görev dosyaları değiştirilir. Kaynak: [FileSystemRights](https://learn.microsoft.com/en-us/dotnet/api/system.security.accesscontrol.filesystemrights?view=net-9.0), [File.ReadAllBytes ve UnauthorizedAccessException](https://learn.microsoft.com/en-us/dotnet/api/system.io.file.readallbytes?view=net-9.0).
:::

::: gorev Deny sonrası gerçek okumayı karşılaştır ve geri yükle
Girdide dosya adı ve ReadData veya WriteData var. Yalnız okuma.bin, boşluklu dosya.bin ve bos.bin görev dosyaları kabul edilir; başka yol/hak veya eksik girdi HATA. Bu dosyalar çalışma klasöründe hazırdır. Hazırlık, yalnız geçici görev dosyalarında Set-Acl ile devralma kontrol bayrağını bir kez normalleştirir. Bu başlangıçtan sonra özgün SDDL birebir geri gelmelidir. Dosyanın özgün Get-Acl nesnesini sakla; geçerli kullanıcının SID'sine yalnız istenen bit için açık Deny ekle ve Set-Acl ile uygula. Yeni kurallı ACL ile aslı birbirinden ayrı Get-Acl nesneleri olsun.

Gerçek File.ReadAllBytes ile önce, Deny uygulanmışken ve özgün ACL finally içinde geri yüklendikten sonra okuma yap. Başarıyı OK:<bayt sayısı>, zincirdeki gerçek UnauthorizedAccessException'ı DENIED olarak raporla; diğer hataları throw et. Dört satır: before=<sonuç>, during=<sonuç>, after=<sonuç>, restored=<özgün SDDL ile son SDDL eşitliği>. Normal raporda son değer True; WriteData Deny okumayı engellememeli. Dosya içeriğini değiştirme. Set-Acl sonrasında bir hata çıksa bile finally özgün ACL'yi geri yüklemeli; hata gizlenmemeli.

```stdin
okuma.bin
ReadData
```
```setup
from pathlib import Path
Path('okuma.bin').write_bytes(bytes(range(256)))
Path('boşluklu dosya.bin').write_bytes(b'abc\x00\xff')
Path('bos.bin').write_bytes(b'')

import os, subprocess
ps=Path(os.environ['SystemRoot'])/'System32/WindowsPowerShell/v1.0/powershell.exe'
env=dict(os.environ);env['PSModulePath']=str(ps.parent/'Modules')
script=Path('normalize-fixture-acl.ps1')
script.write_text("$ErrorActionPreference='Stop'\nGet-ChildItem -LiteralPath . -Filter *.bin | ForEach-Object { $a=Get-Acl -LiteralPath $_.FullName; Set-Acl -LiteralPath $_.FullName -AclObject $a }\n",encoding='utf-8-sig')
subprocess.run([str(ps),'-NoProfile','-NonInteractive','-ExecutionPolicy','Bypass','-File',str(script.resolve())],env=env,check=True,capture_output=True)
```
```starter
'before=OK:256'
'during=DENIED'
'after=OK:256'
'restored=True'
```
```test
import json,pathlib
files={'okuma.bin':bytes(range(256)),'boşluklu dosya.bin':b'abc\x00\xff','bos.bin':b''}
eq(out,'before=OK:256\nduring=DENIED\nafter=OK:256\nrestored=True\n','aynı token ile gerçek okuma kararı')
for name,data in files.items():
    for right in ('ReadData','WriteData'):
        during='DENIED' if right=='ReadData' else 'OK:'+str(len(data))
        eq(run(stdin=name+'\n'+right+'\n'),f'before=OK:{len(data)}\nduring={during}\nafter=OK:{len(data)}\nrestored=True\n','dosya, sıfır bayt ve işlem biti')
        eq(pathlib.Path(name).read_bytes(),data,'sonraki gerçek Python açılışı ve içerik korunması')
for body in ('okuma.bin\nFullControl\n','../okuma.bin\nReadData\n','yok.bin\nReadData\n',''):
    eq(run(stdin=body),'HATA\n','yalnız görev dosyası ve dar hak listesi')

# Sarmalayıcı gerçek Microsoft cmdlet'ini çağırır ve bağımsız .NET açılışı yapar.
wrapper=r'''
$script:AclCalls=0
function Set-Acl {
    [CmdletBinding()]param([string]$LiteralPath,[Security.AccessControl.FileSystemSecurity]$AclObject)
    Microsoft.PowerShell.Security\Set-Acl -LiteralPath $LiteralPath -AclObject $AclObject -ErrorAction Stop
    $script:AclCalls++
    $state='OK'
    try { $null=[IO.File]::ReadAllBytes($LiteralPath) }
    catch {
        $err=$_.Exception
        while ($err.InnerException) { $err=$err.InnerException }
        if ($err -is [UnauthorizedAccessException]) { $state='DENIED' } else { throw }
    }
    $sddl=(Get-Acl -LiteralPath $LiteralPath).Sddl
    [pscustomobject]@{call=$script:AclCalls;state=$state;sddl=$sddl} | ConvertTo-Json -Compress | Add-Content -LiteralPath acl-observed.jsonl -Encoding UTF8
    if ($script:AclCalls -eq 1 -and $script:InjectAclFault) { throw 'PAFTA_ACL_INJECTED_FAULT' }
}
'''
log=pathlib.Path('acl-observed.jsonl')
for inject in (False,True):
    log.unlink(missing_ok=True)
    prefix=wrapper+('\n$script:InjectAclFault=$true\n' if inject else '\n$script:InjectAclFault=$false\n')
    code=prefix+"\n$initial=(Get-Acl -LiteralPath okuma.bin).Sddl\ntry { & {\n"+src+"\n} } catch { if ($_.Exception.Message -notlike '*PAFTA_ACL_INJECTED_FAULT*') { throw }; 'FAULT_OBSERVED' }\nif ((Get-Acl -LiteralPath okuma.bin).Sddl -ne $initial) { throw 'ORIGINAL_ACL_NOT_RESTORED' }\n"
    output=run_code(code,stdin='okuma.bin\nReadData\n')
    records=[json.loads(line) for line in log.read_text(encoding='utf-8-sig').splitlines()] if log.exists() else []
    eq([r['state'] for r in records],['DENIED','OK'],'bağımsız gerçek açılış: Deny uygulandı ve geri yüklendi')
    if inject:ok('FAULT_OBSERVED' in output,'uygulama sonrası hata gizlenmedi')
    eq(pathlib.Path('okuma.bin').read_bytes(),files['okuma.bin'],'finally hata yolunda da geri yükledi')
```
```solution
if ($Girdi.Count -lt 2 -or $Girdi[0] -notin @('okuma.bin','boşluklu dosya.bin','bos.bin') -or $Girdi[1] -notin @('ReadData','WriteData')) { 'HATA'; exit 0 }
$ErrorActionPreference='Stop'
$path=Join-Path $PWD $Girdi[0]
$original=Get-Acl -LiteralPath $path
$changed=Get-Acl -LiteralPath $path
$sid=[Security.Principal.WindowsIdentity]::GetCurrent().User
$rule=New-Object Security.AccessControl.FileSystemAccessRule($sid,$Girdi[1],'Deny')
$changed.AddAccessRule($rule)
function Read-State([string]$File) {
    try { 'OK:'+([IO.File]::ReadAllBytes($File).Length) }
    catch {
        $err=$_.Exception
        while ($err.InnerException) { $err=$err.InnerException }
        if ($err -is [UnauthorizedAccessException]) { 'DENIED' } else { throw }
    }
}
'before='+(Read-State $path)
try {
    Set-Acl -LiteralPath $path -AclObject $changed
    'during='+(Read-State $path)
} finally {
    Set-Acl -LiteralPath $path -AclObject $original
}
'after='+(Read-State $path)
'restored='+((Get-Acl -LiteralPath $path).Sddl -eq $original.Sddl)
```
:::
