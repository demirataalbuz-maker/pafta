---
id: ad15
title: Gerçek AD Nesnesinde ACL Kararını Doğrulamak
summary: Pafta'nın yönettiği Windows Server laboratuvarında gerçek nTSecurityDescriptor ve gerçek kullanıcı jetonuyla WriteDacl kontrolü.
---

::: anlat Çevrimdışı kanıttan gerçek nesneye
AD13–AD14 çevrimdışı veriyle çalıştı. Bu derste **Çalıştır** gerçek Windows Server'da PowerShell çalıştırır. Etki alanı `pafta.test`, nesneler `OU=PaftaLab` altındadır; önceki bellek içi `pafta.local` dizininden ayrıdır. Pafta gerekli VM'yi arka planda başlatır; ders sırasında VM konsolunu açman gerekmez. İlk kurulum ve gereksinimler README'de açıklanır.

`Test-PaftaWriteDacl`, gerçek `svc_sql` nesnesinin güvenlik tanımlayıcısını ADSI ile okur, seçilen test kullanıcısı için gerçek Windows jetonu alır ve Windows **AccessCheck** API'sine `WRITE_DAC` (`0x40000`) sorar. Sonuç Python ACL modelinden gelmez. Bu yardımcı yalnız bu standart hakkı ölçer; nesne GUID'sine bağlı extended right'lar için genel bir `AccessCheckByType` aracı değildir. [Microsoft AccessCheck sözleşmesi](https://learn.microsoft.com/en-us/windows/win32/api/securitybaseapi/nf-securitybaseapi-accesscheck).

Laboratuvarda `SOC-Analistleri` grubuna WriteDacl allow, `mehmet.yilmaz` hesabına açık deny verildi. Ali ve Mehmet aynı grubun üyesidir. Kontrolü oturum açmış Domain Admin için yaparsan bu iki kullanıcıyı ölçmüş olmazsın; yardımcıya doğru kullanıcıyı vermen gerekir.
:::

::: tahmin Aynı grup, farklı karar
İki satır ne yazar?

```powershell
. C:\Pafta\acl_probe.ps1
Test-PaftaWriteDacl 'ali.kaya'
Test-PaftaWriteDacl 'mehmet.yilmaz'
```

???

`True` ve `False`. Grup allow kaydı Ali'ye hakkı verir; Mehmet'in kişisel deny kaydı kendi jetonu için bu hakkı engeller. Bunlar gerçek laboratuvar jetonları üzerinde API sonuçlarıdır.

```meta
motor: ad-vm
dil: powershell
guest: PF-DC01
```
:::

::: gorev Kullanıcının etkili WriteDacl sonucunu raporla
Girdi kutusundan bir kullanıcı adı oku: `ali.kaya`, `mehmet.yilmaz` veya `pf_s4u_user`. Gerçek `Test-PaftaWriteDacl` sonucuna göre yalnız `izin` veya `ret` yaz. Kullanıcı adına bakarak sonucu sabitleme; testler gerçek nesnenin ACL'sini değiştirip tekrar sorar. Bu görev ACL'yi değiştirmez, yalnız raporlar.

```stdin
ali.kaya
```

```starter
. C:\Pafta\acl_probe.ps1
$kisi=[Console]::ReadLine().Trim()
'ret'
```

```test
if not eq(out.strip(), "izin", "Ali'nin etkili hakkı var"): stop()
if not eq(run("mehmet.yilmaz\n").strip(), "ret", "kişisel deny"): stop()
if not eq(run("pf_s4u_user\n").strip(), "ret", "başlangıçta hakkı olmayan kullanıcı"): stop()
def degistir(kisi, tur):
    return r'''
Import-Module ActiveDirectory
$__pfDN=(Get-ADUser svc_sql).DistinguishedName
$__pfEntry=[DirectoryServices.DirectoryEntry]::new("LDAP://localhost/$__pfDN")
$__pfEntry.psbase.AuthenticationType=[DirectoryServices.AuthenticationTypes]193
$__pfEntry.get_Options().SecurityMasks=[DirectoryServices.SecurityMasks]::Dacl
$__pfSD=$__pfEntry.psbase.ObjectSecurity
$__pfBytes=$__pfSD.GetSecurityDescriptorBinaryForm()
$__pfSID=(Get-ADUser 'KISI').SID
$__pfRule=[DirectoryServices.ActiveDirectoryAccessRule]::new($__pfSID,[DirectoryServices.ActiveDirectoryRights]::WriteDacl,[Security.AccessControl.AccessControlType]::TUR)
$__pfSD.AddAccessRule($__pfRule)
$__pfEntry.psbase.ObjectSecurity=$__pfSD
$__pfEntry.psbase.CommitChanges()
try {
'''.replace('KISI',kisi).replace('TUR',tur)+src+r'''
} finally {
 $__pfRestore=[DirectoryServices.ActiveDirectorySecurity]::new()
 $__pfRestore.SetSecurityDescriptorBinaryForm($__pfBytes)
 $__pfEntry.psbase.ObjectSecurity=$__pfRestore
 $__pfEntry.psbase.CommitChanges()
 $__pfEntry.psbase.Dispose()
}
'''
if not eq(run_code(degistir("pf_s4u_user","Allow"), "pf_s4u_user\n").strip(), "izin", "gerçek allow eklenince karar değişmeli"): stop()
if not eq(run_code(degistir("ali.kaya","Deny"), "ali.kaya\n").strip(), "ret", "gerçek deny eklenince karar değişmeli"): stop()
```

```solution
. C:\Pafta\acl_probe.ps1
$kisi=[Console]::ReadLine().Trim()
if(Test-PaftaWriteDacl $kisi){'izin'}else{'ret'}
```

```hint
Girdi adını yardımcıya geçir. Bool sonuca göre çıktı üret; testteki izin değişiklikleri gerçek AD nesnesinde uygulanıp geri alınır.
```

```meta
motor: ad-vm
dil: powershell
guest: PF-DC01
timeout: 240
```
:::
