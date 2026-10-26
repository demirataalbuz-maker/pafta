---
id: ad21
title: Gerçek CA'nın Şablon ve İzin Kanıtını Okumak
summary: Gerçek AD şablon öznitelikleri, CA yayım listesi ve Enrollment GUID'li ACE'leri Pafta içinden denetlemek.
---

::: anlat Gerçek şablon, gerçek CA
Bu tezgah `PF-DC01` üzerindeki Enterprise CA ve AD DS'ye bağlıdır. Altı `Pafta*` şablonu yalnız bu laboratuvarda oluşturuldu. `PaftaClientLegacy`, `PaftaClientPending`, `PaftaClientSigned`, `PaftaServerOnly`, `PaftaClientDraft`, `PaftaClientEditable` farklı ayar/izin sınırlarını gösterir. Öğrenci kodu gerçek `Get-ADObject`, ADSI ve `Get-CATemplate` çağrılarını yapar; sonuç sentetik JSON'dan gelmez.

CA'nın yayımladığı şablonlar ve AD'de saklanan şablonlar ayrı kanıttır. `Get-CATemplate` gerçek CA'nın yayım listesini verir. `msPKI-Enrollment-Flag` ve `msPKI-RA-Signature` başvurunun onay/imza gereksinimlerini taşır. [CA şablonları](https://learn.microsoft.com/en-us/powershell/module/adcsadministration/get-catemplate), [pending işlemi](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-wcce/9cc7ba15-fcbc-48b3-8a3b-121faef3d5ef).

Bu görev bir sertifikanın başka bir hesap olarak oturum açacağını iddia etmez; AD19–AD20'deki güçlü kimlik eşlemesi ayrımı geçerlidir. CA'nın sertifika düzenlemesi ile KDC'nin kimlik doğrulaması farklı kararlardır.
:::

::: tahmin Dizinde var ama CA yayımlıyor mu?
Kodun iki satırını tahmin et.

```powershell
Import-Module ADCSAdministration
$names=@(Get-CATemplate).Name
$names -contains 'PaftaClientLegacy'
$names -contains 'PaftaClientDraft'
```

???

`True`, `False`. Draft AD'de vardır ama bu CA'da yayımlanmamıştır.

```meta
motor: ad-vm
dil: powershell
guest: PF-DC01
timeout: 120
```
:::

::: gorev Canlı şablonun altı alanını raporla
Girdi kutusunda bir `Pafta*` şablon adı var. Gerçek AD'den konu adı, enrollment, imza sayısı ve EKU alanlarını oku; gerçek CA'dan yayım durumunu al. Tek satır şu sırada olsun:

`ad|yayımlanmış|subject_sunar|pending|imza_sayısı|clientAuth`

Bool değerler `True`/`False` yazılsın. Bitleri tam eşitlikle değil `-band` ile sına. Şablon adlarına göre sonuç sabitleme; test canlı şablonun bit alanını değiştirip tekrar sorar.

```stdin
PaftaClientLegacy
```

```starter
Import-Module ActiveDirectory
Import-Module ADCSAdministration
$name=[Console]::ReadLine().Trim()
Write-Output "$name|False|False|False|0|False"
```

```test
if not eq(out.strip(), "PaftaClientLegacy|True|True|False|0|True", "gerçek legacy şablonu"): stop()
if not eq(run("PaftaClientPending\n").strip(), "PaftaClientPending|True|True|True|0|True", "pending bit sınırı"): stop()
if not eq(run("PaftaClientSigned\n").strip(), "PaftaClientSigned|True|True|False|1|True", "bir gerekli imza"): stop()
if not eq(run("PaftaServerOnly\n").strip(), "PaftaServerOnly|True|True|False|0|False", "serverAuth clientAuth değildir"): stop()
if not eq(run("PaftaClientDraft\n").strip(), "PaftaClientDraft|False|True|False|0|True", "dizinde var, yayımlı değil"): stop()
if not eq(run("PaftaClientEditable\n").strip(), "PaftaClientEditable|True|False|False|0|True", "subject dizinden"): stop()
prefix=r'''
Import-Module ActiveDirectory
$__pfBase="CN=Certificate Templates,CN=Public Key Services,CN=Services,$((Get-ADRootDSE).configurationNamingContext)"
$__pfDN="CN=PaftaClientLegacy,$__pfBase"
$__pfOld=(Get-ADObject $__pfDN -Properties msPKI-Enrollment-Flag).'msPKI-Enrollment-Flag'
$__pfOldName=(Get-ADObject $__pfDN -Properties msPKI-Certificate-Name-Flag).'msPKI-Certificate-Name-Flag'
Set-ADObject $__pfDN -Replace @{'msPKI-Enrollment-Flag'=[int]3;'msPKI-Certificate-Name-Flag'=[int]65537}
try {
'''
suffix=r'''
} finally {Set-ADObject $__pfDN -Replace @{'msPKI-Enrollment-Flag'=[int]$__pfOld;'msPKI-Certificate-Name-Flag'=[int]$__pfOldName}}
'''
if not eq(run_code(prefix+src+suffix,"PaftaClientLegacy\n").strip(), "PaftaClientLegacy|True|True|True|0|True", "canlı bit değişikliği ve komşu bit"): stop()
```

```solution
Import-Module ActiveDirectory
Import-Module ADCSAdministration
$name=[Console]::ReadLine().Trim()
$base="CN=Certificate Templates,CN=Public Key Services,CN=Services,$((Get-ADRootDSE).configurationNamingContext)"
$t=Get-ADObject -Identity "CN=$name,$base" -Properties msPKI-Certificate-Name-Flag,msPKI-Enrollment-Flag,msPKI-RA-Signature,pKIExtendedKeyUsage
$published=@(Get-CATemplate).Name -contains $name
$subject=[bool]($t.'msPKI-Certificate-Name-Flag' -band 1)
$pending=[bool]($t.'msPKI-Enrollment-Flag' -band 2)
$signatures=$t.'msPKI-RA-Signature'
$client=@($t.pKIExtendedKeyUsage) -contains '1.3.6.1.5.5.7.3.2'
Write-Output "$name|$published|$subject|$pending|$signatures|$client"
```

```hint
AD'nin Configuration naming context'inden Certificate Templates kapsayıcısını bul. CA listesini `@(Get-CATemplate).Name` ile al; EKU'da tam OID üyeliğini sına.
```

```meta
motor: ad-vm
dil: powershell
guest: PF-DC01
timeout: 240
```
:::

::: anlat Enrollment ACE'sini gerçekten incele
Şablonun security descriptor'ını okumak için ADSI kullanabilirsin. PowerShell'in DirectoryEntry adaptörü bazı özellikleri LDAP özniteliği gibi yorumlayabildiği için `psbase` açıkça seçilir. Bu örnek yalnız okunabilir ACL kanıtını listeler; deny, grup jetonu ve GUID kapsamını çözmeden her allow kaydına “etkili izin” deme. [Enrollment GUID'si](https://learn.microsoft.com/en-us/windows/win32/adschema/r-certificate-enrollment).

```powershell
$dn="CN=PaftaClientLegacy,CN=Certificate Templates,CN=Public Key Services,CN=Services,CN=Configuration,DC=pafta,DC=test"
$e=[DirectoryServices.DirectoryEntry]::new("LDAP://localhost/$dn")
$e.psbase.AuthenticationType=[DirectoryServices.AuthenticationTypes]193
$e.psbase.ObjectSecurity.Access | Select-Object IdentityReference,AccessControlType,ActiveDirectoryRights,ObjectType,IsInherited
$e.psbase.Dispose()
```

```meta
motor: ad-vm
dil: powershell
guest: PF-DC01
timeout: 120
```
:::

::: gorev CA'nın gerçek başvuru kararını oku
`Test-PaftaEnrollment` sabit test kullanıcısı adına gerçek CA'ya bir test CSR'si gönderir; parola istemez. Girdideki şablon için `disposition` değerini yaz: `3` issued, `5` pending, `2` denied. Kararı şablon adına göre üretme. Yardımcı imzalı başvuruyu Windows API'sine iletir ve CA'nın gerçek cevabını döndürür. [Microsoft Submit ve disposition sözleşmesi](https://learn.microsoft.com/en-us/windows/win32/api/certcli/nf-certcli-icertrequest-submit).

`PaftaServerOnly` başvurusu da düzenlenebilir; bu onun Client Authentication EKU'suna sahip olduğu anlamına gelmez. Başvuru başarısı ile sertifikanın kullanım amacını ayrı oku.

```stdin
PaftaClientLegacy
```

```starter
. C:\Pafta\enrollment_probe.ps1
$name=[Console]::ReadLine().Trim()
2
```

```test
if not eq(out.strip(), "3", "gerçek CA issued"): stop()
if not eq(run("PaftaClientPending\n").strip(), "5", "CA pending"): stop()
if not eq(run("PaftaClientSigned\n").strip(), "2", "eksik RA imzası"): stop()
if not eq(run("PaftaServerOnly\n").strip(), "3", "serverAuth da düzenlenebilir"): stop()
if not eq(run("PaftaClientDraft\n").strip(), "2", "yayımlanmayan şablon"): stop()
if not eq(run("PaftaClientEditable\n").strip(), "2", "değiştirme enrollment değildir"): stop()
prefix=r'''
Import-Module ActiveDirectory
$__pfDN="CN=PaftaClientLegacy,CN=Certificate Templates,CN=Public Key Services,CN=Services,$((Get-ADRootDSE).configurationNamingContext)"
$__pfOld=(Get-ADObject $__pfDN -Properties msPKI-Enrollment-Flag).'msPKI-Enrollment-Flag'
Set-ADObject $__pfDN -Replace @{'msPKI-Enrollment-Flag'=[int]2}
Restart-Service CertSvc
try {
'''
suffix=r'''
} finally {
 Set-ADObject $__pfDN -Replace @{'msPKI-Enrollment-Flag'=[int]$__pfOld}
 Restart-Service CertSvc
}
'''
if not eq(run_code(prefix+src+suffix,"PaftaClientLegacy\n").strip(), "5", "gerçek CA politikası değişince karar değişir"): stop()
```

```solution
. C:\Pafta\enrollment_probe.ps1
$name=[Console]::ReadLine().Trim()
$r=Test-PaftaEnrollment $name
$r.disposition
```

```hint
Yardımcı nesnesinin `disposition` alanını yazdır. `message` alanı ayrıntılı CA açıklaması verir; görev çıktısına karıştırma.
```

```meta
motor: ad-vm
dil: powershell
guest: PF-DC01
timeout: 240
```
:::
