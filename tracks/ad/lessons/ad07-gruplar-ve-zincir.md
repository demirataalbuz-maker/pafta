---
id: ad07
title: Gruplar, İç İçe Üyelik ve Zincir Kuralı
summary: Grup kapsamı ve türü (groupType), member/memberOf bağlantısı, birincil grubun memberOf'ta görünmemesi, Get-ADGroup ve Get-ADGroupMember (-Recursive), 1.2.840.113556.1.4.1941 zincir kuralıyla iç içe üyelikleri çözmek.
---

::: anlat Gruplar ve iki yönlü bağlantı
AD'de yetki çoğunlukla kişilere değil **gruplara** verilir. Bir grubun iki özelliği vardır:

- **Kapsam:** Global (aynı etki alanının üyeleri), Domain Local (izin vermek için, aynı etki alanında kullanılır), Universal (orman genelinde).
- **Tür:** Security (izin verilebilir) ya da Distribution (yalnızca e-posta listesi).

İkisi birlikte `groupType` özniteliğinde bit olarak durur (önceki dersin DERİN notu). ActiveDirectory modülü bunları `GroupScope` ve `GroupCategory` olarak gösterir.

Üyelik **iki yönlüdür**: grubun `member` özniteliği üyelerin DN'lerini tutar; AD her üyenin `memberOf` özniteliğini bundan **otomatik** türetir (geri bağlantı). `memberOf`'a doğrudan yazılmaz.

```ad
Get-ADGroup -Filter * -SearchBase "OU=Gruplar,DC=pafta,DC=local" -Properties member
```

> [!TUZAK]
> `memberOf` yalnızca **doğrudan** üyelikleri gösterir. svc_sql'in `memberOf`'unda yalnızca Sunucu-Operatorleri yazar; oysa bu grup Altyapi-Yoneticileri'nin, o da Domain Admins'in üyesidir. Ayrıca kullanıcının **birincil grubu** (çoğunlukla Domain Users, `primaryGroupID=513`) `memberOf`'ta hiç görünmez.

### Get-ADGroupMember
`Get-ADGroupMember -Identity <grup>` grubun **doğrudan** üyelerini getirir; üye gruplar da listeye girer. `-Recursive` eklenince iç içe grupları açar ve yalnızca **grup olmayan** üyeleri (kullanıcı, bilgisayar) döndürür:

```ad
Get-ADGroupMember -Identity "Altyapi-Yoneticileri"

Get-ADGroupMember -Identity "Altyapi-Yoneticileri" -Recursive
```
:::

::: anlat Zincir kuralı: 1.2.840.113556.1.4.1941
LDAP'ta iç içe üyeliği tek filtrede çözmenin yolu **LDAP_MATCHING_RULE_IN_CHAIN** kuralıdır. Değer olarak **tam DN** verilir (DN özniteliği olduğu için joker yok):

| Filtre | Anlamı |
|---|---|
| `(memberOf:1.2.840.113556.1.4.1941:=<grup DN>)` | o grubun doğrudan ya da dolaylı **bütün üyeleri** (ara gruplar dahil) |
| `(member:1.2.840.113556.1.4.1941:=<nesne DN>)` | o nesnenin doğrudan ya da dolaylı üyesi olduğu **bütün gruplar** |

```ad
(&(objectCategory=person)(memberOf:1.2.840.113556.1.4.1941:=CN=Domain Admins,CN=Users,DC=pafta,DC=local))

(member:1.2.840.113556.1.4.1941:=CN=Ayse Demir,OU=SOC,OU=Merkez,DC=pafta,DC=local)
```

İlk filtre Domain Admins zincirindeki kişileri, ikincisi Ayşe Demir'in bütün gruplarını verir: Domain Admins (SOC-Liderleri üzerinden), SOC-Liderleri ve SOC-Analistleri.

> [!NOT]
> `Get-ADGroupMember -Recursive` gerçekte LDAP yerine AD Web Services üzerinden çalışır, ama sonucu zincir kuralıyla aynıdır; tezgahın LDAP düğmesi onun eşdeğer filtresini gösterir. Zincir kuralı büyük dizinlerde ağır bir sorgudur; gerektiği yerde ve dar bir SearchBase ile kullan.

> [!GÜVENLİK]
> Ayrıcalıklı grupları (Domain Admins, Enterprise Admins, Administrators, Backup Operators...) denetlerken her zaman **zinciri** aç. Doğrudan üye listesi kısa ve temiz görünebilir; asıl kalabalık iç içe gruplardadır.
:::

::: tahmin
İki komut art arda çalışıyor. Çıktı ne?

```ad
Get-ADGroupMember -Identity "Domain Admins"

Get-ADGroupMember -Identity "Domain Admins" -Recursive
```

???

İlk komut üç satır yazar: `Administrator`, `Altyapi-Yoneticileri`, `SOC-Liderleri`. Doğrudan üyeler bunlardır; iki tanesi gruptur. İkinci komut beş satır yazar: `Administrator`, `ayse.demir`, `zeynep.arslan`, `svc_sql`, `SRV-WEB01$`. Gruplar açılır ve listeden çıkar: SOC-Liderleri Ayşe'yi, Altyapi-Yoneticileri Zeynep'i ve Sunucu-Operatorleri'ni, o da svc_sql'i ve SRV-WEB01 bilgisayarını getirir. Bir bilgisayar hesabı da Domain Admins zincirinde olabilir.
:::

::: gorev Bir hesabın bütün grupları
**svc_sql** hesabının doğrudan ya da dolaylı üyesi olduğu **bütün grupları** tek bir LDAP filtresiyle getir.

```starter
(member=CN=svc_sql,OU=ServisHesaplari,DC=pafta,DC=local)
```

```test
eq(sonuc, ["Domain Admins", "Altyapi-Yoneticileri", "Sunucu-Operatorleri"], "üç grup: doğrudan bir, dolaylı iki")
ok(kullanir("1.2.840.113556.1.4.1941"), "zincir kuralını kullan")
ust = {"distinguishedName": "CN=Kritik-Erisim,OU=Gruplar,DC=pafta,DC=local", "sAMAccountName": "Kritik-Erisim", "cn": "Kritik-Erisim", "name": "Kritik-Erisim", "objectCategory": "group", "objectClass": ["top", "group"], "groupType": -2147483646, "member": ["CN=Domain Admins,CN=Users,DC=pafta,DC=local"]}
eq(dene(ek=[ust]), ["Domain Admins", "Altyapi-Yoneticileri", "Sunucu-Operatorleri", "Kritik-Erisim"], "Domain Admins'i içeren yeni bir üst grup da gelmeli (dördüncü basamak)")
yan = {"distinguishedName": "CN=Yan-Grup,OU=Gruplar,DC=pafta,DC=local", "sAMAccountName": "Yan-Grup", "cn": "Yan-Grup", "name": "Yan-Grup", "objectCategory": "group", "objectClass": ["top", "group"], "groupType": -2147483646, "member": ["CN=SOC-Liderleri,OU=Gruplar,DC=pafta,DC=local"]}
eq(dene(ek=[yan]), ["Domain Admins", "Altyapi-Yoneticileri", "Sunucu-Operatorleri"], "svc_sql'in zincirinde olmayan grup gelmemeli")
```

```solution
(member:1.2.840.113556.1.4.1941:=CN=svc_sql,OU=ServisHesaplari,DC=pafta,DC=local)
```

```hint
`member` özniteliğine zincir kuralını uygula: `(member:1.2.840.113556.1.4.1941:=<svc_sql'in DN'i>)`.
```
:::

::: gorev Domain Admins zincirindeki etkin kullanıcılar
Domain Admins grubunun doğrudan ya da dolaylı üyesi olan **etkin kullanıcı hesaplarını** getir; bilgisayarlar ve gruplar gelmesin.

```starter
(&(objectCategory=person)(objectClass=user)(memberOf=CN=Domain Admins,CN=Users,DC=pafta,DC=local))
```

```test
eq(sonuc, ["Administrator", "ayse.demir", "zeynep.arslan", "svc_sql"], "zincirdeki dört etkin kullanıcı")
eq(dene(guncelle={"zeynep.arslan": {"userAccountControl": 514}}), ["Administrator", "ayse.demir", "svc_sql"], "devre dışı bırakılan Zeynep gelmemeli")
eq(dene(ek=[yeni_kullanici("op.yeni", ou="OU=ServisHesaplari", memberOf=["CN=Sunucu-Operatorleri,OU=Gruplar,DC=pafta,DC=local"])]), ["Administrator", "ayse.demir", "zeynep.arslan", "svc_sql", "op.yeni"], "Sunucu-Operatorleri'ne eklenen hesap (üç basamak aşağıda) gelmeli")
eq(dene(ek=[yeni_kullanici("analist.yeni", memberOf=["CN=SOC-Analistleri,OU=Gruplar,DC=pafta,DC=local"])]), ["Administrator", "ayse.demir", "zeynep.arslan", "svc_sql"], "zincir dışındaki gruba eklenen hesap gelmemeli")
```

```solution
(&
  (objectCategory=person)
  (objectClass=user)
  (!(userAccountControl:1.2.840.113556.1.4.803:=2))
  (memberOf:1.2.840.113556.1.4.1941:=CN=Domain Admins,CN=Users,DC=pafta,DC=local)
)
```

```hint
`memberOf` yalnızca doğrudan üyeleri bulur; zincir kuralı `memberOf:1.2.840.113556.1.4.1941:=` olur. Etkinlik koşulu: `(!(userAccountControl:1.2.840.113556.1.4.803:=2))`.
```
:::

::: gorev Etki alanı yerel güvenlik grupları
`groupType` üzerinden **etki alanı yerel (4)** ve **güvenlik (2147483648)** bitlerinin **ikisi birden** açık olan grupları getir. Get-ADGroup ve `-LDAPFilter` kullan.

```starter
Get-ADGroup -LDAPFilter "(groupType:1.2.840.113556.1.4.803:=4)"
```

```test
eq(sonuc, ["Yedekleme-Operatorleri"], "tek etki alanı yerel güvenlik grubu")
ok(kullanir("Get-ADGroup") and kullanir("-LDAPFilter"), "Get-ADGroup -LDAPFilter kullan")
def grup(ad, gt):
    return {"distinguishedName": f"CN={ad},OU=Gruplar,DC=pafta,DC=local", "sAMAccountName": ad, "cn": ad, "name": ad, "objectCategory": "group", "objectClass": ["top", "group"], "groupType": gt}
eq(dene(ek=[grup("Dagitim-Yerel", 4)]), ["Yedekleme-Operatorleri"], "etki alanı yerel DAĞITIM grubu (4) gelmemeli")
eq(dene(ek=[grup("Izin-Yerel", -2147483644)]), ["Yedekleme-Operatorleri", "Izin-Yerel"], "yeni etki alanı yerel güvenlik grubu (-2147483644) gelmeli")
eq(dene(ek=[grup("Evrensel-Guvenlik", -2147483640)]), ["Yedekleme-Operatorleri"], "evrensel güvenlik grubu (-2147483640) gelmemeli")
```

```solution
Get-ADGroup -LDAPFilter "(groupType:1.2.840.113556.1.4.803:=2147483652)"
```

```hint
İki biti birden istemek BIT_AND'dir; maske 4 + 2147483648 = 2147483652.
```
:::
