---
id: ad05
title: Get-ADUser, -Filter ve -Properties
summary: ActiveDirectory modülü, Get-ADUser'ın -Filter dili (-eq, -ne, -like, -notlike, -ge, -le, -gt, -lt, -and, -or, -not), tırnaklama, Enabled gibi hesaplanan özelliklerin LDAP'a çevrilmesi, -ne tuzağı, -Properties, -Identity ve -LDAPFilter.
---

::: anlat ActiveDirectory modülü ve -Filter
Windows'ta AD'yi PowerShell'den sorgulamanın yolu **ActiveDirectory** modülüdür (RSAT'ın parçası; etki alanı denetleyicilerinde hazır gelir). Ana komutlar `Get-ADUser`, `Get-ADComputer`, `Get-ADGroup`, `Get-ADGroupMember`, `Get-ADObject` ve `Get-ADOrganizationalUnit`'tir.

`-Filter` parametresi PowerShell'e benzeyen bir ifade alır; modül onu **LDAP filtresine çevirip** sunucuya gönderir:

| -Filter | LDAP karşılığı |
|---|---|
| `Department -eq "SOC"` | `(Department=SOC)` |
| `Title -like "*Uzman*"` | `(Title=*Uzman*)` |
| `badPwdCount -ge 3` | `(badPwdCount>=3)` |
| `badPwdCount -gt 3` | `(&(badPwdCount>=3)(!(badPwdCount=3)))` |
| `Department -ne "SOC"` | `(!(Department=SOC))` |
| `A -and B` | `(&(A)(B))` |
| `-not A` | `(!(A))` |
| `*` | bütün nesneler |

`A -or B` de aynı mantıkla `|` önekli bir filtreye, `(|(A)(B))`'ye çevrilir.

Get-ADUser bunun önüne kendi sınıf koşulunu ekler: `(&(objectCategory=person)(objectClass=user)...)`. Tezgahtaki **LDAP** düğmesi her komutun etkin filtresini gösterir; bu derste sık sık bak.

```ad
Get-ADUser -Filter 'Department -eq "SOC"'

Get-ADUser -Filter 'Title -like "*Uzman*" -or Department -eq "Yonetim"'
```

### Tırnaklama
Filtreyi **tek tırnakla** ya da `{ }` ile yaz, içindeki metin değerlerini çift tırnakla. Çift tırnaklı bir filtrede PowerShell `$` ile başlayan her şeyi komut çalışmadan **önce** genişletir; bu bazen işe yarar, bazen sessizce yanlış filtre üretir. Tek tırnak, yazdığının modüle olduğu gibi gitmesini sağlar.

```ad
Get-ADUser -Filter {Department -eq "Finans"}
```

### Hesaplanan özellikler
`Enabled`, `PasswordNeverExpires`, `PasswordNotRequired`, `TrustedForDelegation` ve `DoesNotRequirePreAuth` dizinde öznitelik olarak **yoktur**; modül onları `userAccountControl` bitlerinden türetir ve filtrede geri çevirir:

```ad
Get-ADUser -Filter 'Enabled -eq $false'

Get-ADUser -Filter 'PasswordNeverExpires -eq $true -and Enabled -eq $true'
```

LDAP düğmesine basınca ilk komutun `(userAccountControl:1.2.840.113556.1.4.803:=2)` olduğunu görürsün. Aynı nedenle ham LDAP'ta `(Enabled=TRUE)` yazmak hiçbir şey bulmaz: gerçek AD'de böyle bir öznitelik yoktur, tezgah da aynı davranır.

> [!TUZAK]
> `-ne`, `(!(...))`'e çevrilir; özniteliği **hiç olmayan** nesneler de sonuca girer. `Get-ADUser -Filter 'Department -ne "SOC"'` yerleşik Administrator, Guest ve krbtgt hesaplarını da getirir, çünkü onların `department` özniteliği yoktur. "Departmanı dolu ama SOC değil" demek için `Department -like "*" -and Department -ne "SOC"` yaz.
:::

::: anlat -Properties, -Identity ve -LDAPFilter
Get-ADUser varsayılan olarak az sayıda özellik getirir (ad, DN, Enabled, SamAccountName, UserPrincipalName gibi). Başka bir alana bakmak istiyorsan `-Properties` ile iste. Tezgah bu durumda her satırı `sAMAccountName|özellik1|özellik2` biçiminde yazar; çok değerli alanların değerleri `;` ile ayrılır. Gerçek PowerShell'de aynı tabloyu `| Select-Object SamAccountName, badPwdCount` ile alırsın.

```ad
Get-ADUser -Filter 'Department -eq "BT"' -Properties title, badPwdCount

Get-ADUser -Identity svc_sql -Properties servicePrincipalName, PasswordNeverExpires
```

`-Identity` tek bir nesneyi getirir ve **sAMAccountName, DN, GUID ya da SID** kabul eder; görünen adı kabul etmez. Bulamazsa gerçek AD de tezgah da hata verir:

```ad norun
Get-ADUser -Identity "Ali Kaya"
```

`-LDAPFilter` ise doğrudan RFC 4515 filtresi alır; önceki derslerde öğrendiğin her şey burada geçerlidir. Modül yine kendi sınıf koşulunu ekler:

```ad
Get-ADUser -LDAPFilter "(title=*Uzman*)" -Properties title, department
```

> [!İPUCU]
> `-Filter`, `-LDAPFilter` ve `-Identity` aynı komutta birlikte kullanılamaz; birini seç. Bit kuralları ve DN zincirleri gibi incelikler için `-LDAPFilter`, okunaklı günlük sorgular için `-Filter` daha rahattır.
:::

::: tahmin
Bu komut hangi satırları yazar?

```ad
Get-ADUser -Filter 'Department -eq "BT" -or Title -like "*Lider*"' -Properties Title
```

???

Üç satır: `ayse.demir|SOC Takim Lideri`, `zeynep.arslan|Sistem Yoneticisi`, `can.ozkan|Ag Uzmani`. Filtre `(|(Department=BT)(Title=*Lider*))` olur. Ayşe BT'de değildir ama unvanında "Lider" geçer; Zeynep ve Can BT'dedir. Sıra dizindeki sıradır: SOC OU'su BT'den önce gelir. `-Properties Title` istendiği için her satıra unvan eklenir.
:::

::: gorev Etkin SOC personeli
Get-ADUser ve `-Filter` ile departmanı **SOC** olan **etkin** kullanıcıları getir.

```starter
Get-ADUser -Filter 'Department -eq "SOC"'
```

```test
eq(sonuc, ["ali.kaya", "ayse.demir"], "etkin iki SOC çalışanı")
ok(kullanir("Get-ADUser") and kullanir("-Filter"), "Get-ADUser -Filter kullan")
eq(dene(guncelle={"ali.kaya": {"userAccountControl": 66050}}), ["ayse.demir"], "Ali devre dışı bırakılınca (66050) gelmemeli")
eq(dene(ek=[yeni_kullanici("soc.yeni", department="SOC", userAccountControl=66048)]), ["ali.kaya", "ayse.demir", "soc.yeni"], "parolası dolmayan ama etkin (66048) yeni SOC hesabı gelmeli")
```

```solution
Get-ADUser -Filter 'Enabled -eq $true -and Department -eq "SOC"'
```

```hint
`Enabled -eq $true` koşulunu `-and` ile ekle; filtreyi tek tırnak içinde tut.
```
:::

::: gorev Hatalı parola sayacı
`badPwdCount` değeri **3 ya da daha fazla** olan kullanıcıları, sayaç değeriyle birlikte (`sAMAccountName|badPwdCount`) listele.

```cikti
mehmet.yilmaz|5
zeynep.arslan|3
can.ozkan|4
burak.sahin|3
svc_yedek|6
```

```starter
Get-ADUser -Filter 'badPwdCount -gt 3' -Properties badPwdCount
```

```test
eq(satirlar, ["mehmet.yilmaz|5", "zeynep.arslan|3", "can.ozkan|4", "burak.sahin|3", "svc_yedek|6"], "beş satır, sayaçlarıyla")
eq(dene(ek=[yeni_kullanici("iki.hata", badPwdCount=2)], satir_olarak=True)[-1], "svc_yedek|6", "badPwdCount=2 gelmemeli")
eq(dene(ek=[yeni_kullanici("uc.hata", badPwdCount=3)], satir_olarak=True)[-1], "uc.hata|3", "badPwdCount=3 gelmeli (sınır dahil)")
```

```solution
Get-ADUser -Filter 'badPwdCount -ge 3' -Properties badPwdCount
```

```hint
`-gt` kesin büyüktür, 3'leri dışarıda bırakır. "3 ya da daha fazla" `-ge`'dir.
```
:::

::: gorev Departmanı dolu ama SOC değil
**OU=Merkez** altında departmanı **dolu** olup SOC **olmayan** kullanıcıları getir. Departman özniteliği hiç olmayan bir hesap sonuçta olmamalı.

```starter
Get-ADUser -Filter 'Department -ne "SOC"' -SearchBase "OU=Merkez,DC=pafta,DC=local"
```

```test
eq(sonuc, ["zeynep.arslan", "can.ozkan", "elif.koc", "burak.sahin", "selin.aydinkaya"], "Merkez'de SOC dışındaki beş kişi")
eq(dene(ek=[yeni_kullanici("departmansiz", ou="OU=BT,OU=Merkez")]), ["zeynep.arslan", "can.ozkan", "elif.koc", "burak.sahin", "selin.aydinkaya"], "department özniteliği olmayan hesap gelmemeli")
eq(dene(ek=[yeni_kullanici("soc.kucuk", ou="OU=SOC,OU=Merkez", department="soc")]), ["zeynep.arslan", "can.ozkan", "elif.koc", "burak.sahin", "selin.aydinkaya"], "'soc' (küçük harf) de SOC sayılmalı")
eq(dene(ek=[yeni_kullanici("bt.yeni", ou="OU=BT,OU=Merkez", department="BT")]), ["zeynep.arslan", "can.ozkan", "elif.koc", "burak.sahin", "selin.aydinkaya", "bt.yeni"], "departmanı BT olan yeni hesap gelmeli")
ok(kullanir("-SearchBase"), "aramayı OU=Merkez ile sınırla")
```

```solution
Get-ADUser -Filter 'Department -like "*" -and Department -ne "SOC"' -SearchBase "OU=Merkez,DC=pafta,DC=local"
```

```hint
`-ne` özniteliği olmayanları da getirir. Önce `Department -like "*"` ile "dolu" koşulunu koy.
```
:::
