---
id: ad02
title: Mantık İşleçleri, Joker ve Varlık
summary: RFC 4515'te &, | ve ! önek yazımı, (!) içine tek alt filtre kuralı, * jokeriyle baş/orta/son eşleşmesi, (öznitelik=*) varlık filtresi, eksik özniteliği bulmak ve DN özniteliklerinde jokerin çalışmaması.
---

::: anlat Önek yazımı: &, | ve !
LDAP filtrelerinde mantık işleci **koşulların önüne** yazılır ve koşullar onun arkasına parantez parantez dizilir:

- `(&(A)(B)(C))`: A **ve** B **ve** C
- `(|(A)(B))`: A **veya** B
- `(!(A))`: A **değil**

`&` ve `|` istediğin kadar alt filtre alır; iç içe de yazılabilir. `!` ise **tam olarak bir** alt filtre alır. Birden fazla koşulu olumsuzlamak için önce onları `&` ya da `|` ile tek filtrede topla: `(!(|(A)(B)))`.

```ad
(&(department=SOC)(title=Analist))

(|(department=BT)(department=Yonetim))

(&(objectCategory=person)(objectClass=user)(!(department=Servis)))
```

Uzun filtreleri tezgahta birkaç satıra bölebilirsin; parantezler dengelenene kadar satırlar tek filtre sayılır:

```ad
(&
  (objectCategory=group)
  (|(sAMAccountName=SOC-Liderleri)(sAMAccountName=SOC-Analistleri))
)
```

> [!TUZAK]
> `(!(A)(B))` geçersizdir; tezgah da gerçek sunucu gibi bu filtreyi reddeder. Doğrusu `(!(&(A)(B)))` ya da niyetine göre `(&(!(A))(!(B)))`.
:::

::: anlat Joker ve varlık
`=` karşılaştırmasında `*` **joker**dir ve değerin başında, ortasında ya da sonunda olabilir:

| Filtre | Eşleşir |
|---|---|
| `(sAMAccountName=svc_*)` | `svc_` ile başlayanlar |
| `(description=*eski*)` | içinde `eski` geçenler |
| `(dNSHostName=*.pafta.local)` | `.pafta.local` ile bitenler |
| `(cn=S*Aydin*)` | S ile başlayıp ilerisinde `Aydin` geçenler |

Joker eşleşmesi de büyük-küçük harfe duyarsızdır.

```ad
(description=*eski*)

(&(objectCategory=computer)(sAMAccountName=SRV-*))
```

### Varlık: (öznitelik=*)
Değerin **yalnızca** `*` olduğu filtre özeldir: "bu öznitelik dolu mu?" diye sorar. Değeri olmayan öznitelik dizinde hiç saklanmaz; boş bir dize yoktur, özniteliğin kendisi yoktur. Bu yüzden eksikliği aramak için varlığı olumsuzlarsın:

```ad
(&(objectCategory=person)(objectClass=user)(servicePrincipalName=*))

(&(objectCategory=person)(objectClass=user)(!(mail=*)))
```

> [!TUZAK]
> `!` yalnızca o koşulu tersine çevirir, nesne türünü sınırlamaz. `(!(mail=*))` tek başına e-postası olmayan **her şeyi** getirir: OU'lar, gruplar, bilgisayarlar. Olumsuz filtreyi her zaman bir nesne türü koşuluyla birlikte kullan.

> [!TUZAK]
> **DN özniteliklerinde joker çalışmaz.** `member`, `memberOf`, `distinguishedName`, `manager` ve `objectCategory` gibi DN sözdizimli özniteliklerde `*` alt dize araması desteklenmez. Gerçek AD bu filtreyi reddetmez; yalnızca **hiçbir şey döndürmez**. Bu sessizlik yanıltıcıdır: "SOC gruplarında kimse yok" sanırsın. Grubu tam DN'iyle yaz:

```ad
(memberOf=CN=SOC*)

(memberOf=CN=SOC-Liderleri,OU=Gruplar,DC=pafta,DC=local)
```

İlk satır hiçbir şey yazmaz; ikincisi `ayse.demir`'i bulur. Varlık filtresi `(memberOf=*)` ise DN özniteliklerinde de çalışır.
:::

::: tahmin
Hangi hesaplar listelenir?

```ad
(&(objectCategory=person)(objectClass=user)(!(mail=*))(sAMAccountName=*a*))
```

???

Üç satır: `Administrator`, `burak.sahin`, `svc_rapor`. Önce e-postası olmayan kullanıcı hesapları kalır: Administrator, Guest, krbtgt, burak.sahin ve dört servis hesabı. Sonra adında `a` geçenler süzülür. Joker eşleşmesi büyük-küçük harfe duyarsızdır, Administrator zaten içinde küçük `a` da taşır. Guest, krbtgt, svc_sql, svc_web ve svc_yedek adlarında `a` yoktur. Tedarikci Destek kişisinin e-postası vardır ve zaten `objectClass=user` değildir.
:::

::: gorev SPN'i olan servis hesapları
`sAMAccountName` değeri **svc_** ile başlayan ve en az bir `servicePrincipalName` değeri olan hesapları getir.

```starter
(sAMAccountName=svc_*)
```

```test
eq(sonuc, ["svc_sql", "svc_web", "svc_yedek"], "SPN'i olan üç servis hesabı")
eq(dene(ek=[yeni_kullanici("svc_bos", ou="OU=ServisHesaplari")]), ["svc_sql", "svc_web", "svc_yedek"], "SPN'i olmayan yeni svc_ hesabı gelmemeli")
eq(dene(ek=[yeni_kullanici("SVC_ARSIV", ou="OU=ServisHesaplari", servicePrincipalName=["arsiv/srv-file01.pafta.local"])]), ["svc_sql", "svc_web", "svc_yedek", "SVC_ARSIV"], "SVC_ ile başlayan (büyük harf) SPN'li hesap gelmeli")
eq(dene(ek=[yeni_kullanici("app_svc_x", servicePrincipalName=["app/x.pafta.local"])]), ["svc_sql", "svc_web", "svc_yedek"], "adında svc_ geçen ama onunla başlamayan hesap gelmemeli")
```

```solution
(&(sAMAccountName=svc_*)(servicePrincipalName=*))
```

```hint
"Dolu mu?" sorusu `(servicePrincipalName=*)` ile sorulur. İki koşulu `&` ile birleştir.
```
:::

::: gorev E-postası eksik hesaplar
**Finans** ya da **Servis** departmanındaki kullanıcı hesaplarından e-posta adresi (`mail`) **olmayanları** getir.

```starter
(|(department=Finans)(department=Servis))
```

```test
eq(sonuc, ["burak.sahin", "svc_sql", "svc_web", "svc_yedek", "svc_rapor"], "e-postası olmayan beş hesap")
eq(dene(ek=[yeni_kullanici("fin.yeni", department="Finans", mail="fin.yeni@pafta.local")]), ["burak.sahin", "svc_sql", "svc_web", "svc_yedek", "svc_rapor"], "e-postası olan Finans hesabı gelmemeli")
eq(dene(ek=[yeni_kullanici("svc_yeni", ou="OU=ServisHesaplari", department="Servis")]), ["burak.sahin", "svc_sql", "svc_web", "svc_yedek", "svc_rapor", "svc_yeni"], "e-postası olmayan yeni Servis hesabı gelmeli")
eq(dene(ek=[yeni_kullanici("bt.yeni", department="BT")]), ["burak.sahin", "svc_sql", "svc_web", "svc_yedek", "svc_rapor"], "e-postası olmayan ama BT'de olan hesap gelmemeli")
eq(dene(ek=[yeni_bilgisayar("PC-FIN02", department="Finans")]), ["burak.sahin", "svc_sql", "svc_web", "svc_yedek", "svc_rapor"], "Finans'a yazılmış bir bilgisayar hesabı gelmemeli")
```

```solution
(&
  (objectCategory=person)
  (objectClass=user)
  (|(department=Finans)(department=Servis))
  (!(mail=*))
)
```

```hint
Eksikliği aramak için varlığı olumsuzla: `(!(mail=*))`. Kullanıcı hesabı koşulunu da (`objectCategory=person` ve `objectClass=user`) unutma.
```
:::

::: gorev Grup üyeleri tam DN ile
**SOC-Analistleri** grubunun doğrudan üyelerini `memberOf` üzerinden getir. Başlangıç kodu jokerli yazıldığı için hiçbir şey döndürmüyor.

```starter
(memberOf=CN=SOC-Analistleri*)
```

```test
eq(sonuc, ["ali.kaya", "ayse.demir", "mehmet.yilmaz"], "SOC-Analistleri'nin üç üyesi")
SOC = "CN=SOC-Analistleri,OU=Gruplar,DC=pafta,DC=local"
eq(dene(ek=[yeni_kullanici("yeni.analist", memberOf=[SOC])]), ["ali.kaya", "ayse.demir", "mehmet.yilmaz", "yeni.analist"], "gruba yeni eklenen üye gelmeli")
eq(dene(ek=[yeni_kullanici("eski.analist", memberOf=["CN=SOC-Analistleri-Eski,OU=Gruplar,DC=pafta,DC=local"])]), ["ali.kaya", "ayse.demir", "mehmet.yilmaz"], "adı SOC-Analistleri ile başlayan başka bir grubun üyesi gelmemeli")
```

```solution
(memberOf=CN=SOC-Analistleri,OU=Gruplar,DC=pafta,DC=local)
```

```hint
Grubun DN'i: `CN=SOC-Analistleri,OU=Gruplar,DC=pafta,DC=local`. DN özniteliklerinde joker yok; tamamını yaz.
```
:::
