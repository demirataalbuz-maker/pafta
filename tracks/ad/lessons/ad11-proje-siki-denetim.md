---
id: ad11
title: Proje: Sıkı Active Directory Denetimi
summary: Uçtan uca kurumsal Active Directory denetim projesi; ayrıcalıklı grup zincirindeki hizmet hesapları, etkin hesaplardaki kritik UAC bayrakları, unutulmuş devre dışı hesaplar ve parola politikası ihlalleri.
---

::: anlat Kurumsal denetim masası
Bu paftada öğrendiğin araçları (RFC 4515 LDAP filtreleri, bit eşleştirme kuralları, Get-AD* cmdlet'leri ve iç içe grup zincirleri) birleştirerek `pafta.local` etki alanının kapsamlı bir **güvenlik denetimini** gerçekleştireceksin.

Bir etki alanı denetiminde öncelikli incelenen dört ana eksen şunlardır:

1. **Ayrıcalık Hiyerarşisi:** Domain Admins ve korumalı grupların zincirinde kimler var? Bir hizmet hesabı ya da üye sunucu yanlışlıkla bu zincire girmiş mi?
2. **Kritik UAC Bayrakları:** Parolasız oturum açma (PASSWD_NOTREQD), Kerberos ön kimlik doğrulamasının kapatılması (DONT_REQ_PREAUTH) veya etki alanı denetleyicisi olmayan makinelerde kısıtsız yetki devri (TRUSTED_FOR_DELEGATION) var mı?
3. **Parola ve Yaşam Döngüsü:** Parolası asla dolmayan hesaplar, eski parola yaşları, hiç oturum açmamış stajyer/geçici hesaplar.
4. **Kalıntılar:** Devre dışı bırakıldığı halde parolası süresiz kalan veya `adminCount=1` damgası üzerinde unutulmuş hesaplar.

```ad
Get-ADGroupMember -Identity "Domain Admins" -Recursive

Get-ADUser -Filter 'Enabled -eq $true -and PasswordNeverExpires -eq $true' -Properties pwdLastSet
```

> [!İPUCU]
> Denetim raporu hazırlarken hem doğrudan PowerShell `-Filter` hem de gerekirse doğrudan LDAP filtresi kullanabilirsin. Sonuçları her zaman nesne adı ve ilgili kritik özelliklerle birlikte listelemek raporun kanıt değerini artırır.
:::

::: tahmin
Denetçi, devre dışı bırakılmış olmasına rağmen parola hatası sayacı sıfırdan büyük olan hesapları inceliyor. Hangi hesaplar ve sayaç değerleri listelenir?

```ad
Get-ADUser -Filter 'Enabled -eq $false -and badPwdCount -gt 0' -Properties badPwdCount
```

???

Üç satır yazar: `mehmet.yilmaz|5`, `burak.sahin|3`, `svc_yedek|6`. Filtre devre dışı olan (`Enabled -eq $false`) ve sayacı sıfırdan kesin büyük (`badPwdCount -gt 0`) kullanıcıları arar. Guest ve krbtgt devre dışıdır ama `badPwdCount` değerleri 0'dır, bu yüzden gelmezler. Mehmet, Burak ve svc_yedek'in hatalı parola sayaçları sırasıyla 5, 3 ve 6'dır.
:::

::: gorev Denetim 1: Domain Admins zincirindeki hizmet hesapları
Domain Admins grubunun doğrudan ya da dolaylı **zincirinde yer alan** ve en az bir `servicePrincipalName` (SPN) taşıyan **kullanıcı hesaplarını** tek bir LDAP filtresiyle tespit et. Hizmet hesaplarının etki alanı yöneticisi haklarına sahip olması büyük bir risk bulgusudur.

```starter
(&(objectCategory=person)(objectClass=user)(servicePrincipalName=*))
```

```test
eq(sonuc, ["svc_sql"], "Domain Admins zincirindeki tek SPN'li kullanıcı")
ok(kullanir("servicePrincipalName=*"), "SPN varlık filtresi kullan")
ok(kullanir("1.2.840.113556.1.4.1941"), "zincir kuralını kullan")
eq(dene(ek=[yeni_kullanici("svc_yeni_da", memberOf=["CN=Sunucu-Operatorleri,OU=Gruplar,DC=pafta,DC=local"], servicePrincipalName=["app/da.pafta.local"])]), ["svc_sql", "svc_yeni_da"], "zincirdeki gruba eklenen yeni SPN'li hesap gelmeli")
eq(dene(ek=[yeni_kullanici("da_kullanici", memberOf=["CN=Domain Admins,CN=Users,DC=pafta,DC=local"])]), ["svc_sql"], "Domain Admins'te olup SPN'i olmayan sıradan kullanıcı gelmemeli")
eq(dene(ek=[yeni_kullanici("svc_baska", memberOf=["CN=Ag-Ekibi,OU=Gruplar,DC=pafta,DC=local"], servicePrincipalName=["test/a"])]), ["svc_sql"], "zincir dışındaki SPN'li hesap gelmemeli")
```

```solution
(&
  (objectCategory=person)
  (objectClass=user)
  (servicePrincipalName=*)
  (memberOf:1.2.840.113556.1.4.1941:=CN=Domain Admins,CN=Users,DC=pafta,DC=local)
)
```

```hint
Kullanıcı filtresine `(servicePrincipalName=*)` ve `(memberOf:1.2.840.113556.1.4.1941:=CN=Domain Admins,CN=Users,DC=pafta,DC=local)` ekle.
```
:::

::: gorev Denetim 2: Etkin hesaplarda kritik UAC ayarları
**Etkin** kullanıcı hesapları arasında PASSWD_NOTREQD (32), TRUSTED_FOR_DELEGATION (524288) ya da DONT_REQ_PREAUTH (4194304) bayraklarından **en az biri** açık olan kullanıcı hesaplarını getir.

```starter
(&(objectCategory=person)(objectClass=user)(userAccountControl:1.2.840.113556.1.4.803:=2))
```

```test
eq(sonuc, ["svc_web", "svc_rapor"], "etkin olup bu bayrakları taşıyan iki hesap")
ok(kullanir("1.2.840.113556.1.4.804"), "en az biri için BIT_OR (804) kuralını kullan")
eq(dene(ek=[yeni_kullanici("uac.32", userAccountControl=544)]), ["svc_web", "svc_rapor", "uac.32"], "32 biti açık etkin hesap gelmeli")
eq(dene(ek=[yeni_kullanici("uac.pasif", userAccountControl=546)]), ["svc_web", "svc_rapor"], "aynı biti taşıyan devre dışı hesap gelmemeli")
eq(dene(ek=[yeni_kullanici("uac.temiz", userAccountControl=512)]), ["svc_web", "svc_rapor"], "sıradan 512 gelmemeli")
```

```solution
(&
  (objectCategory=person)
  (objectClass=user)
  (!(userAccountControl:1.2.840.113556.1.4.803:=2))
  (userAccountControl:1.2.840.113556.1.4.804:=4718624)
)
```

```hint
Maske: 32 + 524288 + 4194304 = 4718624. BIT_OR kuralı: `1.2.840.113556.1.4.804:=4718624`. Etkinlik için `(!(...803:=2))` ekle.
```
:::

::: gorev Denetim 3: Devre dışı ama süresiz parolalı hesaplar
Devre dışı bırakıldığı halde `PasswordNeverExpires` bayrağı açık kalmış kullanıcı hesaplarını `userAccountControl` ve `description` özellikleriyle birlikte (`sAMAccountName|userAccountControl|description`) listele. Get-ADUser ve `-Filter` kullan.

```cikti
Guest|66082|Built-in account for guest access to the computer/domain
svc_yedek|66050|Eski yedekleme ajani
```

```starter
Get-ADUser -Filter 'Enabled -eq $false' -Properties userAccountControl, description
```

```test
eq(satirlar, ["Guest|66082|Built-in account for guest access to the computer/domain", "svc_yedek|66050|Eski yedekleme ajani"], "iki devre dışı ve süresiz parolalı hesap")
ok(kullanir("Get-ADUser") and kullanir("-Filter"), "Get-ADUser ve -Filter kullan")
ok(kullanir("PasswordNeverExpires"), "PasswordNeverExpires özelliğini filtrele")
eq(dene(ek=[yeni_kullanici("eski.unuttuk", userAccountControl=66050, description="Unutulan hesap")], satir_olarak=True), ["Guest|66082|Built-in account for guest access to the computer/domain", "svc_yedek|66050|Eski yedekleme ajani", "eski.unuttuk|66050|Unutulan hesap"], "yeni devre dışı ve 65536'lı hesap gelmeli")
eq(dene(ek=[yeni_kullanici("eski.normal", userAccountControl=514, description="Normal pasif")], satir_olarak=True), satirlar, "parolası dolabilen pasif hesap (514) gelmemeli")
```

```solution
Get-ADUser -Filter 'Enabled -eq $false -and PasswordNeverExpires -eq $true' -Properties userAccountControl, description
```

```hint
`-Filter 'Enabled -eq $false -and PasswordNeverExpires -eq $true'` koşulunu yaz ve `-Properties userAccountControl, description` ekle.
```
:::
