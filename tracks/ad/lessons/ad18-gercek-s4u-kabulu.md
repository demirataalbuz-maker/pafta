---
id: ad18
title: Gerçek KDC ile S4U Akışını Sınamak
summary: Pafta'nın iki Windows Server konuğu arasında gerçek S4U ve SMB erişimi; klasik/RBCD izinleri ve hassas kullanıcı sınırları.
---

::: anlat Başarı artık gerçek bir hizmet erişimi
Bu derste Pafta `PF-APP01` üye sunucusunda gerçek Windows PowerShell çalıştırır. `Invoke-PaftaS4U` sabit test kullanıcısı `pf_s4u_user` adına Windows'un S4U oturumunu açar ve yalnız laboratuvardaki `\\PF-DC01.pafta.test\PaftaRead\proof.txt` dosyasını okumayı dener. Sonuç gerçek KDC, Windows güvenlik sağlayıcısı ve SMB sunucusundan gelir; AD16–AD17'daki JSON benzetimi kullanılmaz.

WindowsIdentity'nin UPN alan kurucusu Windows'un `KERB_S4U_LOGON` yapısını kullanır. Yardımcı bu işlemi üye sunucunun SYSTEM oturumunda yapar; öğrenci test kullanıcısının parolasını girmez. [Microsoft WindowsIdentity sözleşmesi](https://learn.microsoft.com/en-us/dotnet/api/system.security.principal.windowsidentity.-ctor?view=netframework-4.8.1), [S4U akışı](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-sfu/c920c148-8a9c-42e9-b8e9-db5755cd281b).

Yardımcı her deneyden önce yalnız üye laboratuvar sunucusunun SYSTEM bilet önbelleğini temizler; böylece önceki izinle alınmış bilet yeni deneyi maskelemez. Ayrıca yalnız yönetilen laboratuvardaki iki bilgisayarın devir ayarını değiştirir; her denemeden sonra eski deney ayarlarını temizler. `classic`, ön bilgisayarın hedef listesine CIFS SPN'sini ekler. `rbcd`, hedefin izinli ön hesap listesine üye bilgisayarı ekler. `missing` iki izni de kaldırır. `blocked`, klasik izin varken test kullanıcısını `AccountNotDelegated` yapar. Sonuçtaki `tickets`, gerçek `klist` çıktısıdır. Başarı `ok`, dosyanın beklenen içerikle okunmasıdır. [KCD/RBCD açıklaması](https://learn.microsoft.com/en-us/windows-server/security/kerberos/kerberos-constrained-delegation-overview), [klist](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/klist).
:::

::: tahmin İzin yokken dosya okunur mu?
Kodun tek satırlık sonucunu tahmin et.

```powershell
. C:\Pafta\s4u_probe.ps1
$r=Invoke-PaftaS4U missing
$r.ok
```

???

`False`. Ön hizmet için devir izni bulunmaması, test kullanıcısının arka hizmette erişim hakkı olmasına rağmen devirli dosya erişimini engeller.

```meta
motor: ad-vm
dil: powershell
guest: PF-APP01
timeout: 120
```
:::

::: gorev Gerçek dört deneyi raporla
Girdi `classic`, `rbcd`, `missing` veya `blocked` olur. `Invoke-PaftaS4U` çağrısını bu modla yap ve yalnız gerçek `ok` sonucunu `True`/`False` olarak yaz. Mod adına göre sabit sonuç döndürme. Her deney gerçek bilet ve dosya erişimini dener; bu yüzden ilk başlatma çevrimdışı görevlerden uzun sürer.

```stdin
classic
```

```starter
. C:\Pafta\s4u_probe.ps1
$mode=[Console]::ReadLine().Trim()
'False'
```

```test
if not eq(out.strip(), "True", "klasik devir ile gerçek dosya erişimi"): stop()
if not eq(run("rbcd\n").strip(), "True", "kaynak tabanlı izin"): stop()
if not eq(run("missing\n").strip(), "False", "izinsiz ön hesap"): stop()
if not eq(run("blocked\n").strip(), "False", "hassas kullanıcı"): stop()
prefix=r'''
$__pfPath='\\PF-DC01.pafta.test\C$\Pafta\proof\proof.txt'
$__pfOld=[IO.File]::ReadAllText($__pfPath)
[IO.File]::WriteAllText($__pfPath,'different proof')
try {
'''
suffix=r'''
} finally {[IO.File]::WriteAllText($__pfPath,$__pfOld)}
'''
if not eq(run_code(prefix+src+suffix,"classic\n").strip(), "False", "aynı modda gerçek dosya kanıtı değişince başarı da değişmeli"): stop()
```

```solution
. C:\Pafta\s4u_probe.ps1
$mode=[Console]::ReadLine().Trim()
$result=Invoke-PaftaS4U $mode
$result.ok
```

```hint
Yardımcı sonucu bir nesnedir; `ok` alanını yazdır. Tanılama için serbest çalıştırmada `tickets` ve `error` alanlarını ayrıca inceleyebilirsin.
```

```meta
motor: ad-vm
dil: powershell
guest: PF-APP01
timeout: 240
```
:::


::: anlat DC'deki gerçek 4769 XML kanıtı
Bu kutu da Pafta içinden çalışır; bu adımın konuğu DC'dir. Çıktıyı kullanıcı, hizmet, devreden hizmetler ve zamanla birlikte incele. Aynı test hesabı CA/LDAP deneylerinde de kullanıldığı için her kaydı otomatik S4U diye etiketleme. Bu gerçek laboratuvarda S4U Proxy olayının `TargetUserName` alanı `PF-APP01$` ön hesabını, `TransmittedServices` de ön hizmeti gösterebilir; yalnız `pf_s4u_user` aramak zinciri kaçırır. Kullanıcı adına düzenlenen bileti kendi oturumunun `klist` çıktısıyla birlikte incele. [4769 alanları](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4769).

```powershell
Get-WinEvent -FilterHashtable @{LogName='Security';Id=4769} -MaxEvents 1500 |
    Where-Object {$_.ToXml() -match 'pf_s4u_user|pf-app01\$'} |
    Select-Object -First 12 | ForEach-Object {$_.ToXml()}
```

```meta
motor: ad-vm
dil: powershell
guest: PF-DC01
timeout: 120
```
:::
