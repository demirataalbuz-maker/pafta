---
id: ad08
title: SPN, Yetki Devri ve Hesap Denetimi
summary: Hizmet asıl adları (servicePrincipalName) ve kullanıcı hesabıyla çalışan hizmetler, krbtgt istisnası, kısıtsız yetki devri (TRUSTED_FOR_DELEGATION) ve etki alanı denetleyicisi ayrımı, eski parolalar ve pwdLastSet, düzenli hesap denetimi listesi.
---

::: anlat Hizmet hesapları ve SPN
Bir hizmet (SQL Server, bir web uygulaması, yedekleme ajanı) Kerberos ile kimlik doğrulayacaksa, istemcinin hangi hesap için bilet isteyeceğini bilmesi gerekir. Bu eşleme **servicePrincipalName** (SPN) özniteliğinde tutulur: `hizmet/sunucu[:port]` biçiminde, çok değerli bir öznitelik.

```ad
Get-ADUser -Identity svc_sql -Properties servicePrincipalName
```

Bilgisayar hesaplarının hepsinde SPN vardır (`HOST/PC-SOC01` gibi); onların parolası makine tarafından otomatik ve uzun üretilir. Denetimde asıl bakılan, SPN'i bir **kullanıcı hesabında** duran hizmetlerdir: o hizmetin bileti, kullanıcı hesabının parolasından türetilen anahtarla korunur. Parola kısa ya da yıllardır değişmemişse risk büyür.

Savunma tarafında yapılacaklar:

- SPN'li kullanıcı hesaplarını düzenli listele; sahibi ve amacı belli olmayanları kaldır.
- Bu hesapların parolalarını uzun (25+ karakter) ve rastgele tut, düzenli değiştir.
- Mümkünse **gMSA**'ya (grup yönetilen hizmet hesabı) geç: parolayı AD kendisi üretir ve değiştirir.
- Ayrıcalıklı gruplara SPN'li kullanıcı hesabı koyma (svc_sql bunu ihlal ediyor: Domain Admins zincirinde).

> [!TUZAK]
> `krbtgt` hesabının da bir SPN'i vardır (`kadmin/changepw`). Bu, Kerberos'un kendi hizmet hesabıdır; devre dışıdır ve düzenli bir hizmet hesabı gibi ele alınmaz. SPN denetim sorgularında onu `(!(sAMAccountName=krbtgt))` ile ayrıca dışarıda bırakmak yaygın bir alışkanlıktır.
:::

::: anlat Yetki devri ve hesap yaşı
**Yetki devri** (delegation), bir hizmetin kullanıcı adına başka bir hizmete bağlanabilmesidir: bir web uygulaması, oturum açan kullanıcı adına veritabanına gider. Üç türü vardır:

| Tür | Nerede görünür | Denetim notu |
|---|---|---|
| Kısıtsız | UAC'de TRUSTED_FOR_DELEGATION (524288) | hizmet, gelen kullanıcı adına **her** hizmete bağlanabilir; DC'ler dışında olmamalı |
| Kısıtlı | `msDS-AllowedToDelegateTo` listesi | yalnızca listedeki hizmetler |
| Kaynak tabanlı kısıtlı | hedefte `msDS-AllowedToActOnBehalfOfOtherIdentity` | izni hedef verir |

Etki alanı denetleyicilerinde kısıtsız devir **varsayılandır** (DC01: 532480 = 524288 + 8192). Denetimde aranan, bu bitin DC **olmayan** hesaplarda açık olmasıdır:

```ad
(&(objectCategory=computer)(userAccountControl:1.2.840.113556.1.4.803:=524288)(!(userAccountControl:1.2.840.113556.1.4.803:=8192)))
```

Ayrıcalıklı kullanıcı hesaplarında NOT_DELEGATED (1048576, "Hesap hassastır ve devredilemez") bayrağını açmak ya da onları **Protected Users** grubuna almak, bu hesapların başka bir hizmet üzerinden kullanılmasını engeller.

### Parola yaşı
`pwdLastSet` parolanın en son ne zaman değiştiğini FILETIME olarak tutar (ad03). Birkaç referans değer:

| Tarih (UTC) | FILETIME |
|---|---|
| 2024-01-01 | 133485408000000000 |
| 2025-01-01 | 133801632000000000 |

0 değeri "bir sonraki oturumda değiştirmeli" demektir; eski parola listesinde ayrıca ele alınır.

```ad
Get-ADUser -Filter 'pwdLastSet -ge 1 -and pwdLastSet -le 133485408000000000' -Properties pwdLastSet
```

> [!İPUCU]
> Düzenli hesap denetiminin kısa listesi: devre dışı ama silinmemiş hesaplar, hiç oturum açmamış hesaplar (`logonCount=0`), parolası dolmayanlar, PASSWD_NOTREQD ve DONT_REQ_PREAUTH bayrakları, SPN'li kullanıcı hesapları, DC dışındaki kısıtsız devirler, ayrıcalıklı grupların zinciri. Proje dersinde (ad11) bunların hepsini tek raporda toplayacaksın.
:::

::: tahmin
Bu filtre hangi hesapları getirir?

```ad
(&(objectCategory=person)(objectClass=user)(servicePrincipalName=*))
```

???

Dört satır: `krbtgt`, `svc_sql`, `svc_web`, `svc_yedek`. Kullanıcı hesaplarından SPN'i dolu olanlar listelenir. krbtgt'nin `kadmin/changepw` SPN'i olduğu için o da gelir; çoğu kişi bunu beklemez. svc_rapor'un SPN'i yoktur. Bilgisayarların SPN'leri vardır ama `objectCategory=person` koşulu onları dışarıda bırakır.
:::

::: gorev Gözden geçirilecek hizmet hesapları
SPN'i olan **etkin** kullanıcı hesaplarını getir; `krbtgt` sonuçta olmasın.

```starter
(&(objectCategory=person)(objectClass=user)(servicePrincipalName=*))
```

```test
eq(sonuc, ["svc_sql", "svc_web"], "SPN'li iki etkin hizmet hesabı")
eq(dene(guncelle={"krbtgt": {"userAccountControl": 512}}), ["svc_sql", "svc_web"], "krbtgt etkin görünse bile gelmemeli")
eq(dene(ek=[yeni_kullanici("svc_mail", ou="OU=ServisHesaplari", servicePrincipalName=["SMTP/srv-mail01.pafta.local"])]), ["svc_sql", "svc_web", "svc_mail"], "SPN'li yeni etkin hesap gelmeli")
eq(dene(ek=[yeni_kullanici("svc_pasif", ou="OU=ServisHesaplari", userAccountControl=66050, servicePrincipalName=["x/srv.pafta.local"])]), ["svc_sql", "svc_web"], "devre dışı SPN'li hesap gelmemeli")
eq(dene(ek=[yeni_kullanici("svc_spnsiz", ou="OU=ServisHesaplari")]), ["svc_sql", "svc_web"], "SPN'siz hesap gelmemeli")
```

```solution
(&
  (objectCategory=person)
  (objectClass=user)
  (servicePrincipalName=*)
  (!(userAccountControl:1.2.840.113556.1.4.803:=2))
  (!(sAMAccountName=krbtgt))
)
```

```hint
Üç koşul ekle: SPN dolu, devre dışı değil (`(!(...803:=2))`), adı krbtgt değil.
```
:::

::: gorev DC dışındaki kısıtsız yetki devri
UAC'sinde TRUSTED_FOR_DELEGATION (524288) biti açık olan, ama etki alanı denetleyicisi (SERVER_TRUST_ACCOUNT, 8192) **olmayan** bütün hesapları getir: kullanıcılar da bilgisayarlar da.

```starter
(userAccountControl:1.2.840.113556.1.4.803:=524288)
```

```test
eq(sonuc, ["svc_web", "SRV-WEB01$"], "bir kullanıcı ve bir bilgisayar")
eq(dene(ek=[yeni_bilgisayar("DC02", ou="OU=Domain Controllers", userAccountControl=532480)]), ["svc_web", "SRV-WEB01$"], "yeni bir DC (532480) gelmemeli")
eq(dene(ek=[yeni_bilgisayar("SRV-APP01", ou="OU=Sunucular", userAccountControl=528384)]), ["svc_web", "SRV-WEB01$", "SRV-APP01$"], "kısıtsız devirli yeni üye sunucu (528384) gelmeli")
eq(dene(ek=[yeni_kullanici("svc_devir", ou="OU=ServisHesaplari", userAccountControl=524800)]), ["svc_web", "SRV-WEB01$", "svc_devir"], "kısıtsız devirli yeni kullanıcı (524800) gelmeli")
eq(dene(ek=[yeni_bilgisayar("SRV-NORMAL", ou="OU=Sunucular", userAccountControl=4096)]), ["svc_web", "SRV-WEB01$"], "devirsiz sunucu gelmemeli")
```

```solution
(&
  (userAccountControl:1.2.840.113556.1.4.803:=524288)
  (!(userAccountControl:1.2.840.113556.1.4.803:=8192))
)
```

```hint
524288 açık olsun, 8192 açık olmasın. İki BIT_AND koşulu; ikincisi olumsuzlanmış.
```
:::

::: gorev Eski parolalı etkin hesaplar
Parolası **2024-01-01 (133485408000000000) ya da öncesinde** değişmiş **etkin** kullanıcıları, `pwdLastSet` değeriyle listele. `pwdLastSet=0` olan hesaplar bu listeye girmesin. Get-ADUser ve `-Filter` kullan.

```cikti
Administrator|133000000000000000
```

```starter
Get-ADUser -Filter 'pwdLastSet -le 133485408000000000' -Properties pwdLastSet
```

```test
eq(satirlar, ["Administrator|133000000000000000"], "yalnızca Administrator")
ok(kullanir("Get-ADUser") and kullanir("-Filter"), "Get-ADUser -Filter kullan")
eq(dene(ek=[yeni_kullanici("sinir.tam", pwdLastSet=133485408000000000)], satir_olarak=True), ["Administrator|133000000000000000", "sinir.tam|133485408000000000"], "tam sınır değeri gelmeli")
eq(dene(ek=[yeni_kullanici("sinir.sonra", pwdLastSet=133485408000000001)], satir_olarak=True), ["Administrator|133000000000000000"], "sınırdan bir sonra gelmemeli")
eq(dene(ek=[yeni_kullanici("degismeli", pwdLastSet=0)], satir_olarak=True), ["Administrator|133000000000000000"], "pwdLastSet=0 gelmemeli")
eq(dene(ek=[yeni_kullanici("bir", pwdLastSet=1)], satir_olarak=True), ["Administrator|133000000000000000", "bir|1"], "pwdLastSet=1 gelmeli (0 dışındaki en küçük değer)")
eq(dene(ek=[yeni_kullanici("eski.pasif", userAccountControl=514, pwdLastSet=130000000000000000)], satir_olarak=True), ["Administrator|133000000000000000"], "devre dışı eski hesap gelmemeli")
```

```solution
Get-ADUser -Filter 'Enabled -eq $true -and pwdLastSet -ge 1 -and pwdLastSet -le 133485408000000000' -Properties pwdLastSet
```

```hint
Üç koşulu `-and` ile bağla: `Enabled -eq $true`, `pwdLastSet -ge 1`, `pwdLastSet -le 133485408000000000`.
```
:::
