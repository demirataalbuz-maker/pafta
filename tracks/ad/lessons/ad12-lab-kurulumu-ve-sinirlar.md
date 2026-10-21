---
id: ad12
title: Kendi AD Laboratuvarını Kurmak ve Tezgah Sınırları
summary: Windows Server Evaluation ISO ile kendi etki alanı denetleyicini kurmak, AD DS rolü ve Install-ADDSForest, üye makine eklemek, Pafta tezgahının sınırları (in-memory LDAP motoru, canlı Kerberos/GPO/çoğaltmanın olmaması) ve laboratuvarda ileri güvenlik adımları.
---

::: anlat Neden kendi laboratuvarın?
Pafta'nın Active Directory yolu boyunca RFC 4515 LDAP filtrelerini, `userAccountControl` bayrak matematiğini, `Get-AD*` cmdlet ailesini ve iç içe grup zincirlerini sahte ama gerçeğe sadık bir dizin üzerinde (`DC=pafta,DC=local`) çalıştırdın.

Ancak kurumsal savunmada bir sonraki adım, **canlı bir Active Directory etki alanında** çalışmaktır. Çünkü:
- Grup ilkelerinin (GPO) istemcilerde nasıl işlendiğini görmek,
- Kerberos biletlerini (TGT, TGS, PAC) Wireshark ile yakalayıp paket seviyesinde incelemek,
- Çoklu etki alanı denetleyicileri (DC) arasındaki çoğaltma trafiğini (DRS) gözlemlemek,
- Canlı Active Directory ortamında savunma araçlarını (LAPS, Sysmon, Sentinel Agent, BloodHound) test etmek,
yalnızca gerçek işletim sistemlerinin çalıştığı bir **laboratuvar ortamında** mümkündür.

### Adım Adım: Windows Server Değerlendirme Sürümü ile Kurulum
Microsoft, **Evaluation Center** üzerinden Windows Server'ın 180 günlük yasal değerlendirme ISO kalıplarını ücretsiz sunar (Windows Server 2022 veya 2025).

1. **Sanallaştırma:** Hyper-V (Windows Pro/Enterprise yerleşik), Proxmox, VirtualBox ya da VMware Workstation kur.
2. **Sanal Makine Özellikleri:** En az 2 sanal çekirdek (vCPU), 4 GB RAM, 60 GB disk. Sanal ağ kartını iç ağa (Internal/NAT Network) bağla.
3. **Statik IP ve Sunucu Adı:**
   - Sunucuyu kurduktan sonra adını değiştir: ör. `DC01`.
   - Ağ kartına statik bir IP ver (ör. `192.168.10.10/24`, Ağ Geçidi `192.168.10.1`).
   - Birincil DNS adresi olarak kendisini göster: `127.0.0.1`.
4. **AD DS Rolünün Yüklenmesi:**
   Yönetici PowerShell konsolunda tek komut:
   ```powershell norun
   Install-WindowsFeature -Name AD-Domain-Services -IncludeManagementTools
   ```
5. **Etki Alanının (Ormanın) Kurulması:**
   Sunucuyu bir etki alanı denetleyicisine yükseltmek için:
   ```powershell norun
   Install-ADDSForest -DomainName "pafta.local" -DomainNetbiosName "PAFTA" -InstallDns:$true
   ```
   Kurulum senden DSRM (Directory Services Restore Mode) parolası isteyecek ve tamamlanınca sunucuyu yeniden başlatacaktır.
6. **İstemci Makine Eklemek:**
   Bir Windows 10/11 sanal makinesinin DNS sunucusunu `192.168.10.10` (DC'nin IP'si) yapıp şu komutla etki alanına katabilirsin:
   ```powershell norun
   Add-Computer -DomainName "pafta.local" -Restart
   ```
:::

::: anlat Pafta tezgahının sınırları
Active Directory karmaşık ve çok katmanlı bir ekosistemdir. Tezgah ile gerçek dünya arasındaki farkları bilmek kritik önemdedir:

> [!ÖNEMLİ]
> **Tezgahta neler VAR:**
> - RFC 4515 uyumlu LDAP filtre ayrıştırıcısı ve değerlendiricisi (`&`, `|`, `!`, `=`, `>=`, `<=`, `*` jokeri, varlık filtresi `attr=*`, onaltılık kaçışlar `\2a`, `\28`, `\29`, `\5c`).
> - LDAP bit eşleştirme kuralları (`1.2.840.113556.1.4.803` BIT_AND ve `804` BIT_OR).
> - LDAP geçişli DN zinciri eşleştirme kuralı (`1.2.840.113556.1.4.1941` IN_CHAIN; `memberOf`, `member`, `manager` gibi DN değerli alanlarda).
> - PowerShell `ActiveDirectory` modülünün temel cmdlet'leri (`Get-ADUser`, `Get-ADComputer`, `Get-ADGroup`, `Get-ADGroupMember -Recursive`, `Get-ADObject`, `Get-ADOrganizationalUnit`) ve bunların `-Filter`, `-LDAPFilter`, `-SearchBase`, `-SearchScope` (isim veya `0`/`1`/`2`), `-Properties` parametreleri.
> - Büyük-küçük harf duyarsızlığı ve hesaplanan AD özellikleri (`Enabled`, `PasswordNeverExpires` vb.).

> [!TUZAK]
> **Tezgahta neler YOK:**
> 1. **Gerçek Kerberos KDC servisi yoktur:** Port 88 üzerinde çalışan canlı bilet üretimi, oturum açma el sıkışması ve Kerberos şifreleme anahtarları bu tezgahta dönmez.
> 2. **Grup İlkesi (GPO) motoru ve SYSVOL paylaşımı yoktur:** `\\domain\sysvol` paylaşımı, istemcilerin GPO çekmesi, kayıt defteri zorlamaları tezgah sınırları dışındadır.
> 3. **AD Çoğaltma (Replication) yoktur:** Çoklu DC replikasyon mekanizması, USN vektörleri ve DRS RPC çağrıları sanal olarak taklit edilmez.
> 4. **Gerçek RPC / SAMR / LSA protokolleri yoktur:** Canlı ağ üzerinden Mimikatz, Rubeus, BloodHound (SharpHound) gibi araçlar bu tezgaha bağlanamaz; bu araçlar için yukarıda kurduğun Windows Server laboratuvarı şarttır.
> 5. **`-Filter` kapsamı ve belge notu:** `-band`, `-bor`, `-recursivematch` ve `-approx` tezgahta `-Filter` içinde desteklenmez; LDAP karşılıkları `803`, `804`, `1941` ve `~=` ile `-LDAPFilter` kullanılabilir. [Microsoft'un işleç tablosu](https://learn.microsoft.com/en-us/powershell/module/activedirectory/about/about_activedirectory_filter?view=windowsserver2025-ps#supported-operators) `-lt` → `!x >= y`, `-gt` → `!x <= y` verir; tezgah bu tabloyu izler. [Örnek 3'te](https://learn.microsoft.com/en-us/powershell/module/activedirectory/about/about_activedirectory_filter?view=windowsserver2025-ps#example-3---get-entries-with-a-bad-password-count-greater-than-five) `badpwdcount -ge 5` için yazılan `(&(!badpwdcount<=5)(badpwdcount=*))` tabloyla tutarsızdır ve ek varlık koşulu içerir. [LDAP Special Characters tablosuna göre](https://learn.microsoft.com/en-us/powershell/module/activedirectory/about/about_activedirectory_filter?view=windowsserver2025-ps#ldap-special-characters) `-eq '*'` / `-ne '*'` düz yıldızı (`\2a`) karşılaştırır; varlık/yokluk için `-like '*'` / `-notlike '*'` kullanılır. Bu ayrım belgede açıktır.

### Kendi Laboratuvarında İlk Savunma Adımları
Kendi kurduğun laboratuvarda ilk yapman gereken sıkılaştırma (hardening) adımları:
- **LAPS Kurulumu:** Windows LAPS ile yerel `Administrator` parolalarını her makinede farklı yap ve AD'de şifreli sakla.
- **Protected Users Grubu:** Ayrıcalıklı hesapları (Domain Admins üyelerini) `Protected Users` grubuna ekle; böylece NTLM kullanımı, DES/RC4 şifreleme ve zayıf yetki devri otomatik engellenir.
- **gMSA (Group Managed Service Accounts):** Servis hesaplarını parola yönetimi otomatik olan gMSA'ya taşı.
:::

::: tahmin
Kurulan bir etki alanında OU hiyerarşisini kontrol etmek için Get-ADOrganizationalUnit çalıştırılıyor. Bu sorgu dizindeki hangi OU'ları döndürür? `CN=Users` bu listede yer alır mı?

```ad
Get-ADOrganizationalUnit -Filter *
```

???

Dokuz satır yazar: `Domain Controllers`, `Merkez`, `SOC`, `BT`, `Finans`, `ServisHesaplari`, `Sunucular`, `Istasyonlar`, `Gruplar`. `CN=Users` bu listede kesinlikle **yer almaz**; çünkü Users bir OU (organizationalUnit) değil, bir kapsayıcıdır (container nesnesi). Get-ADOrganizationalUnit yalnızca `objectCategory=organizationalUnit` olan nesneleri listeler.
:::

::: gorev Kök etki alanının doğrudan altındaki OU'lar
Laboratuvar mimarisini incelerken, etki alanı kökünün (`DC=pafta,DC=local`) **doğrudan** altındaki ana OU'ları listele. Alt birimler (SOC, BT, Finans gibi) ve kapsayıcılar (CN=Users) sonuçta yer almasın. Get-ADOrganizationalUnit ve `-SearchScope OneLevel` kullan.

```cikti
Domain Controllers
Merkez
ServisHesaplari
Sunucular
Istasyonlar
Gruplar
```

```starter
Get-ADOrganizationalUnit -Filter *
```

```test
eq(sonuc, ["Domain Controllers", "Merkez", "ServisHesaplari", "Sunucular", "Istasyonlar", "Gruplar"], "kök altındaki 6 ana OU")
ok(kullanir("Get-ADOrganizationalUnit"), "Get-ADOrganizationalUnit kullan")
ok(kullanir("OneLevel"), "OneLevel kapsamı kullan")
ok(kullanir("DC=pafta,DC=local"), "SearchBase olarak kök etki alanını ver")
yeni_ou = {"distinguishedName": "OU=TestLab,DC=pafta,DC=local", "name": "TestLab", "ou": "TestLab", "objectCategory": "organizationalUnit", "objectClass": ["top", "organizationalUnit"]}
eq(dene(ek=[yeni_ou]), ["Domain Controllers", "Merkez", "ServisHesaplari", "Sunucular", "Istasyonlar", "Gruplar", "TestLab"], "köke eklenen yeni OU gelmeli")
derin_ou = {"distinguishedName": "OU=AltLab,OU=TestLab,DC=pafta,DC=local", "name": "AltLab", "ou": "AltLab", "objectCategory": "organizationalUnit", "objectClass": ["top", "organizationalUnit"]}
eq(dene(ek=[yeni_ou, derin_ou]), ["Domain Controllers", "Merkez", "ServisHesaplari", "Sunucular", "Istasyonlar", "Gruplar", "TestLab"], "ikinci düzey OU (OneLevel dışı) gelmemeli")
```

```solution
Get-ADOrganizationalUnit -Filter * -SearchBase "DC=pafta,DC=local" -SearchScope OneLevel
```

```hint
`-SearchBase "DC=pafta,DC=local"` ve `-SearchScope OneLevel` parametrelerini ekle.
```
:::

::: gorev Sunucu envanteri ve işletim sistemi doğrulaması
Laboratuvar ortamındaki üye sunucuları listelemek istiyorsun. **OU=Sunucular,DC=pafta,DC=local** altındaki bilgisayar nesnelerini `dNSHostName` ve `OperatingSystem` özellikleriyle birlikte (`sAMAccountName|dNSHostName|OperatingSystem`) Get-ADComputer kullanarak listele.

```cikti
SRV-SQL01$|srv-sql01.pafta.local|Windows Server 2022
SRV-WEB01$|srv-web01.pafta.local|Windows Server 2022
SRV-ESKI01$|srv-eski01.pafta.local|Windows Server 2012 R2
```

```starter
Get-ADComputer -Filter * -Properties dNSHostName, OperatingSystem
```

```test
eq(satirlar, ["SRV-SQL01$|srv-sql01.pafta.local|Windows Server 2022", "SRV-WEB01$|srv-web01.pafta.local|Windows Server 2022", "SRV-ESKI01$|srv-eski01.pafta.local|Windows Server 2012 R2"], "Sunucular OU'sundaki üç makine")
ok(kullanir("Get-ADComputer"), "Get-ADComputer kullan")
ok(kullanir("OU=Sunucular,DC=pafta,DC=local"), "Sunucular OU'sunu sınırla")
eq(dene(ek=[yeni_bilgisayar("SRV-YEDEK01", ou="OU=Sunucular", dNSHostName="srv-yedek01.pafta.local", operatingSystem="Windows Server 2022")], satir_olarak=True), ["SRV-SQL01$|srv-sql01.pafta.local|Windows Server 2022", "SRV-WEB01$|srv-web01.pafta.local|Windows Server 2022", "SRV-ESKI01$|srv-eski01.pafta.local|Windows Server 2012 R2", "SRV-YEDEK01$|srv-yedek01.pafta.local|Windows Server 2022"], "Sunucular OU'suna eklenen yeni sunucu gelmeli")
eq(dene(ek=[yeni_bilgisayar("PC-TEST", ou="OU=Istasyonlar", dNSHostName="pc-test.pafta.local", operatingSystem="Windows 11")], satir_olarak=True), satirlar, "Istasyonlar'a eklenen bilgisayar gelmemeli")
```

```solution
Get-ADComputer -Filter * -SearchBase "OU=Sunucular,DC=pafta,DC=local" -Properties dNSHostName, OperatingSystem
```

```hint
Get-ADComputer komutuna `-SearchBase "OU=Sunucular,DC=pafta,DC=local"` ekle.
```
:::

::: gorev Hardening öncesi: Süresiz parolalı etkin hesaplar
Laboratuvarda parola politikasını sıkılaştırmadan önce, etki alanındaki **etkin** (`Enabled -eq $true`) ve **parolasının süresi asla dolmayan** (`PasswordNeverExpires -eq $true`) kullanıcı hesaplarını listele.

```starter
Get-ADUser -Filter 'PasswordNeverExpires -eq $true'
```

```test
eq(sonuc, ["Administrator", "can.ozkan", "svc_sql"], "etkin ve süresiz parolalı üç hesap")
ok(kullanir("Get-ADUser") and kullanir("-Filter"), "Get-ADUser ve -Filter kullan")
ok(kullanir("Enabled -eq $true") or kullanir("Enabled -eq 1"), "Enabled -eq $true koşulunu kullan")
ok(kullanir("PasswordNeverExpires -eq $true") or kullanir("PasswordNeverExpires -eq 1"), "PasswordNeverExpires -eq $true koşulunu kullan")
eq(dene(ek=[yeni_kullanici("yeni_sureli", userAccountControl=512)]), ["Administrator", "can.ozkan", "svc_sql"], "parolası normal süreli hesap (512) gelmemeli")
eq(dene(ek=[yeni_kullanici("yeni_pasif_suresiz", userAccountControl=66050)]), ["Administrator", "can.ozkan", "svc_sql"], "devre dışı ama süresiz hesap gelmemeli")
eq(dene(ek=[yeni_kullanici("yeni_etkin_suresiz", userAccountControl=66048)]), ["Administrator", "can.ozkan", "svc_sql", "yeni_etkin_suresiz"], "yeni etkin süresiz hesap gelmeli")
```

```solution
Get-ADUser -Filter 'Enabled -eq $true -and PasswordNeverExpires -eq $true'
```

```hint
`-Filter 'Enabled -eq $true -and PasswordNeverExpires -eq $true'` filtresini kullan.
```
:::
