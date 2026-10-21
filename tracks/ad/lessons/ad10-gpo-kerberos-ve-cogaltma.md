---
id: ad10
title: GPO, Kerberos, AdminSDHolder ve Çoğaltma
summary: GPO'nun iki ayağı (GPC ve SYSVOL GPT), Kerberos biletleri ve PAC, AdminSDHolder ile SDProp süreci, adminCount=1 kalıntısı ve yetki devralmanın bozulması, etki alanı denetleyicileri ve AD çoğaltma kavramları.
---

::: anlat Dizin arkasındaki görünmeyen çarklar
Active Directory yalnızca nesne aranan bir veritabanı değildir; etki alanının güvenliğini ve yönetimini sağlayan arka plan mekanizmalarıyla yaşar:

### 1. Grup İlkesi (GPO)
Bir GPO tek bir yerde durmaz, iki ayrı parçadan oluşur:
- **GPC (Group Policy Container):** Dizinde `CN=Policies,CN=System,DC=pafta,DC=local` altında duran LDAP nesnesidir. İlkenin adı, sürüm numarası ve durumunu tutar.
- **GPT (Group Policy Template):** Dosya paylaşımında (`\\pafta.local\sysvol\pafta.local\Policies\{GUID}`) duran dosya ve klasörlerdir. Betikler, kayıt defteri ayarları burada saklanır.

İstemciler ilkeyi **LSDOU** sırasıyla (Local, Site, Domain, OU) uygular. Aynı ilke çakışırsa en son uygulanan (OU) kazanır (Enforced ilkesi yoksa).

### 2. Kerberos Kimlik Doğrulama ve PAC
Kullanıcı etki alanında oturum açtığında KDC'den (Key Distribution Center - etki alanı denetleyicisi) bir **TGT** (bilet verme bileti) alır. Bir hizmete giderken bu TGT ile KDC'ye başvurup o hizmet için bir **TGS** bileti ister.
- Biletin içinde **PAC (Privilege Attribute Certificate)** bulunur. PAC kullanıcının SID'sini ve üye olduğu grupların SID'lerini taşır.
- PAC, KDC ve hizmet anahtarlarıyla imzalanır.

### 3. AdminSDHolder ve SDProp: Ayrıcalıklı Hesap Koruması
Domain Admins, Administrators, Backup Operators gibi kritik grupların üyeleri saldırıya karşı özel korunur. Her 60 dakikada bir **SDProp** (Security Descriptor Propagator) adlı arka plan işlemi çalışır:
1. `CN=AdminSDHolder,CN=System,DC=...` nesnesinin ACL'ini alır.
2. Korunan grupların ve üyelerinin üzerine bu ACL'i damgalar.
3. Nesnelerin üst OU'dan **izin devralmasını (inheritance) kapatır**.
4. Nesnenin `adminCount` özniteliğini **1** yapar.

> [!TUZAK]
> **adminCount=1 kalıntısı (orphaned adminCount):** Bir kullanıcı Domain Admins grubundan çıkarıldığında, Active Directory onun `adminCount` değerini kendiliğinden **0 yapmaz** ve kapanan **izin devralmasını geri açmaz**! Hesap artık yönetici olmadığı halde `adminCount=1` olarak kalır ve üst OU'daki delegasyonlardan yararlanamaz. Denetimde `adminCount=1` olup korumalı gruplarda olmayan bu hesaplar bulunur ve elle düzeltilir.

### 4. AD Çoğaltma (Replication)
Bütün etki alanı denetleyicileri dizinin birer kopyasını tutar. Değişiklikler **USN** (Update Sequence Number) ile izlenir ve DC'ler arasında çoğaltılır. Silinen nesneler hemen yok edilmez; **tombstone** (veya AD Recycle Bin) durumuna geçer ve 180 gün boyunca saklanır.

> [!NOT]
> **Tezgahın sınırları:** Bu tezgahta canlı bir Kerberos KDC servisi, ağ üzerinde çalışan bir SYSVOL dosya paylaşımı, GPO işleme motoru ya da DC çoğaltma protokolü (DRS RPC) **yoktur**. Tezgah, bellek içi bir LDAP dizini (`dizin.json`) ve RFC 4515 motoru ile çalışır. Bu mekanizmaların dizindeki nesne karşılıklarını, bayraklarını ve kalıntılarını sorgularsın. Canlı Kerberos biletleme ve GPO işleyişini incelemek için ad12'de kendi laboratuvarını kuracaksın.
:::

::: anlat adminCount=1 ve Denetleyici Sorguları
`adminCount=1` olan kullanıcıları doğrudan sorgulayabilirsin:

```ad
Get-ADUser -Filter 'adminCount -eq 1' -Properties adminCount
```

Bir nesnenin gerçekten etki alanı denetleyicisi olup olmadığını anlamak için `userAccountControl`'deki **8192** (SERVER_TRUST_ACCOUNT) bitine bakılır:

```ad
Get-ADComputer -LDAPFilter "(userAccountControl:1.2.840.113556.1.4.803:=8192)" -Properties dNSHostName, OperatingSystem
```

> [!GÜVENLİK]
> Etki alanı denetleyicileri yalnızca `OU=Domain Controllers` altında durmalıdır. Farklı bir OU'da duran ya da sıradan bilgisayarlar gibi yönetilen bir DC ciddi bir yapılandırma hatasıdır.
:::

::: tahmin
Bu komut dizinde `adminCount -eq 1` olan etkin kullanıcıları listeliyor. Hangi hesaplar gelir?

```ad
Get-ADUser -Filter 'adminCount -eq 1 -and Enabled -eq $true'
```

???

Beş satır yazar: `Administrator`, `ali.kaya`, `ayse.demir`, `zeynep.arslan`, `svc_sql`. `adminCount=1` olan hesaplardan `krbtgt` devre dışıdır (Enabled=$false) bu yüzden gelmez. Geriye kalan beş hesap etkindir. Dikkat: Ali Kaya şu an yalnızca SOC-Analistleri grubundadır, Domain Admins zincirinde değildir; fakat geçmişte yetkilendirilmiş ve `adminCount=1` kalıntısı üzerinde kalmıştır.
:::

::: gorev adminCount=1 kalıntısı (Orphaned adminCount)
Dizinde `adminCount` değeri **1** olan, ancak **Domain Admins zincirinde olmayan** ve `krbtgt` **olmayan** kullanıcı hesabını getir. Bu hesap yetkisi alındığı halde izin devralması kapalı kalmış hesaptır.

```starter
(&(objectCategory=person)(objectClass=user)(adminCount=1))
```

```test
eq(sonuc, ["ali.kaya"], "Domain Admins zincirinde olmayan adminCount=1 hesabı")
ok(kullanir("adminCount=1"), "adminCount=1 filtresi kullan")
ok(kullanir("1.2.840.113556.1.4.1941"), "Domain Admins zincir kuralını olumsuzla")
eq(dene(ek=[yeni_kullanici("eski.admin", adminCount=1)]), ["ali.kaya", "eski.admin"], "yeni eklenen zincir dışı adminCount=1 hesabı gelmeli")
eq(dene(ek=[yeni_kullanici("da.yeni", adminCount=1, memberOf=["CN=Domain Admins,CN=Users,DC=pafta,DC=local"])]), ["ali.kaya"], "Domain Admins'e üye yeni adminCount=1 hesabı gelmemeli")
```

```solution
(&
  (objectCategory=person)
  (objectClass=user)
  (adminCount=1)
  (!(sAMAccountName=krbtgt))
  (!(memberOf:1.2.840.113556.1.4.1941:=CN=Domain Admins,CN=Users,DC=pafta,DC=local))
)
```

```hint
Kullanıcı hesabı koşuluna `(adminCount=1)`, `(!(sAMAccountName=krbtgt))` ve `(!(memberOf:1.2.840.113556.1.4.1941:=CN=Domain Admins,CN=Users,DC=pafta,DC=local))` ekle.
```
:::

::: gorev Etki alanı denetleyicilerini tespit etmek
`userAccountControl` özniteliğindeki **SERVER_TRUST_ACCOUNT (8192)** bitini kontrol ederek dizindeki etki alanı denetleyicisini ve özelliklerini (`sAMAccountName|dNSHostName|OperatingSystem`) Get-ADComputer ve `-LDAPFilter` ile listele.

```cikti
DC01$|dc01.pafta.local|Windows Server 2022
```

```starter
Get-ADComputer -Filter * -Properties dNSHostName, OperatingSystem
```

```test
eq(satirlar, ["DC01$|dc01.pafta.local|Windows Server 2022"], "yalnızca DC01")
ok(kullanir("Get-ADComputer") and kullanir("-LDAPFilter"), "Get-ADComputer ve -LDAPFilter kullan")
ok(kullanir("8192"), "8192 bit maskesini kullan")
eq(dene(ek=[yeni_bilgisayar("DC02", userAccountControl=532480, dNSHostName="dc02.pafta.local", operatingSystem="Windows Server 2022")], satir_olarak=True), ["DC01$|dc01.pafta.local|Windows Server 2022", "DC02$|dc02.pafta.local|Windows Server 2022"], "yeni DC de gelmeli")
eq(dene(ek=[yeni_bilgisayar("SRV-APP", userAccountControl=4096)], satir_olarak=True), satirlar, "sıradan sunucu (4096) gelmemeli")
```

```solution
Get-ADComputer -LDAPFilter "(userAccountControl:1.2.840.113556.1.4.803:=8192)" -Properties dNSHostName, OperatingSystem
```

```hint
`1.2.840.113556.1.4.803:=8192` eşleştirme kuralını Get-ADComputer'ın `-LDAPFilter` parametresine ver.
```
:::
