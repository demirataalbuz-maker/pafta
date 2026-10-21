---
id: ad04
title: userAccountControl ve Bit Eşleştirme Kuralları
summary: userAccountControl'ü bayraklara ayırmak, (userAccountControl=514) yazmanın neden eksik kaldığı, 1.2.840.113556.1.4.803 (bütün bitler) ve 1.2.840.113556.1.4.804 (herhangi bir bit) kuralları, etkin ve devre dışı hesap filtreleri.
---

::: anlat Bir sayı, bir demet bayrak
`userAccountControl` (UAC) bir hesabın durumunu tek bir tam sayıda tutar. Sayının her biti bir bayraktır:

| Bayrak | Değer | Anlamı |
|---|---|---|
| ACCOUNTDISABLE | 2 | hesap devre dışı |
| PASSWD_NOTREQD | 32 | hesaba boş parola atanabilir |
| NORMAL_ACCOUNT | 512 | sıradan kullanıcı hesabı |
| WORKSTATION_TRUST_ACCOUNT | 4096 | iş istasyonu ya da üye sunucu |
| SERVER_TRUST_ACCOUNT | 8192 | etki alanı denetleyicisi |
| DONT_EXPIRE_PASSWORD | 65536 | parolanın süresi dolmaz |
| TRUSTED_FOR_DELEGATION | 524288 | kısıtsız yetki devri |
| NOT_DELEGATED | 1048576 | hesap devredilemez (hassas hesap) |
| DONT_REQ_PREAUTH | 4194304 | Kerberos ön kimlik doğrulaması istenmez |

Değer, açık bayrakların **toplamıdır**. Dizindeki değerleri çözelim:

| Hesap | UAC | Ayrışım |
|---|---|---|
| ali.kaya | 512 | normal hesap |
| mehmet.yilmaz | 514 | 512 + 2: devre dışı |
| can.ozkan | 66048 | 65536 + 512: parolası dolmaz |
| burak.sahin | 546 | 512 + 32 + 2: devre dışı, parola gerekmez |
| svc_yedek | 66050 | 65536 + 512 + 2: devre dışı, parolası dolmaz |
| Guest | 66082 | 65536 + 512 + 32 + 2: yerleşik Guest hesabının varsayılanı |
| DC01$ | 532480 | 524288 + 8192: etki alanı denetleyicisi |

### `(userAccountControl=514)` neden eksik?
`=` sayının **tamamını** karşılaştırır. 514 yalnızca "normal ve devre dışı, başka hiçbir bayrak yok" demektir. Devre dışı olup başka bir bayrağı da açık olan svc_yedek, burak.sahin ve Guest bu filtreye takılmaz:

```ad
(userAccountControl=514)
```

Bu filtre yalnızca `krbtgt` ve `mehmet.yilmaz`'ı bulur; devre dışı beş hesabın üçü görünmez kalır.

> [!NOT]
> UAC'de 16 değerli bir LOCKOUT bayrağı da tanımlıdır, ama AD bu biti `userAccountControl` içinde güncellemez. Kilitli hesaplar `lockoutTime` özniteliğiyle (`(lockoutTime>=1)`) ya da hesaplanan `msDS-User-Account-Control-Computed` özniteliğiyle bulunur. Tezgahın dizininde kilit verisi yok; kilit eşiği konusunu `badPwdCount` ile çalışıyoruz.
:::

::: anlat Bit eşleştirme kuralları: 803 ve 804
LDAP, sayının **belli bitlerine** bakmak için genişletilmiş eşleştirme kuralları sunar. Yazım `öznitelik:OID:=değer` biçimindedir; değer onluk tabanda yazılır.

| Kural | OID | Doğru olduğu durum |
|---|---|---|
| BIT_AND | `1.2.840.113556.1.4.803` | maskedeki **bütün** bitler açık |
| BIT_OR | `1.2.840.113556.1.4.804` | maskedeki bitlerden **en az biri** açık |

Devre dışı kullanıcı hesapları, UAC'nin geri kalanı ne olursa olsun:

```ad
(&(objectCategory=person)(objectClass=user)(userAccountControl:1.2.840.113556.1.4.803:=2))
```

Etkin hesaplar için aynı koşulu olumsuzla:

```ad
(&(objectCategory=person)(objectClass=user)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))
```

### Birden fazla bit
Maske, bayrakların toplamıdır. 65538 = 65536 + 2:

- `:803:=65538`: devre dışı **ve** parolası dolmaz (iki bit birden açık).
- `:804:=65538`: devre dışı **veya** parolası dolmaz (en az biri açık).

```ad
(&(objectCategory=person)(objectClass=user)(userAccountControl:1.2.840.113556.1.4.804:=65538))
```

> [!İPUCU]
> Aynı işi iki ayrı 803 koşuluyla da yapabilirsin: `(|(userAccountControl:1.2.840.113556.1.4.803:=2)(userAccountControl:1.2.840.113556.1.4.803:=65536))`, tek bir 804 koşuluyla aynı sonucu verir. Uzun ama okuması kolaydır.

> [!DERİN]
> Bu kurallar yalnızca UAC için değildir; her tam sayı özniteliğinde çalışır. Örneğin grupların `groupType` özniteliği de bir bayrak demetidir (2 global, 4 etki alanı yerel, 8 evrensel, 2147483648 güvenlik grubu). Değer işaretli 32 bitlik tam sayı olarak saklandığı için güvenlik grupları dizinde eksi görünür: global güvenlik grubu `-2147483646`. Bit kuralı bu sayıyla da doğru çalışır.
:::

::: tahmin
İki filtre art arda çalışıyor. Çıktı ne?

```ad
(userAccountControl=66050)

(&(objectCategory=person)(objectClass=user)(userAccountControl:1.2.840.113556.1.4.803:=65538))
```

???

Önce `svc_yedek`, sonra `Guest` ve yine `svc_yedek`. İlk filtre sayıyı bütün olarak karşılaştırır; tam olarak 66050 olan tek hesap svc_yedek'tir. İkinci filtre yalnızca iki bite bakar: 2 (devre dışı) ve 65536 (parolası dolmaz) birlikte açık mı? Guest'in 66082 değeri bu iki biti içerir, fazladan 32 biti de açıktır; BIT_AND fazlalığa bakmaz. Mehmet (514) ve krbtgt (514) devre dışıdır ama 65536 bitleri kapalıdır; Can (66048) ve Administrator (66048) parolası dolmayan hesaplardır ama etkindir.
:::

::: gorev Devre dışı kullanıcı hesapları
Devre dışı bütün **kullanıcı hesaplarını** getir; UAC'nin başka bitleri ne olursa olsun. Bilgisayar hesapları gelmesin.

```starter
(userAccountControl=514)
```

```test
eq(sonuc, ["Guest", "krbtgt", "mehmet.yilmaz", "burak.sahin", "svc_yedek"], "devre dışı beş kullanıcı hesabı")
eq(dene(ek=[yeni_kullanici("pasif.hassas", userAccountControl=1049090)]), ["Guest", "krbtgt", "mehmet.yilmaz", "burak.sahin", "svc_yedek", "pasif.hassas"], "1049090 (devre dışı + NOT_DELEGATED) gelmeli")
eq(dene(ek=[yeni_kullanici("etkin.hassas", userAccountControl=1049088)]), ["Guest", "krbtgt", "mehmet.yilmaz", "burak.sahin", "svc_yedek"], "1049088 (etkin + NOT_DELEGATED) gelmemeli")
eq(dene(ek=[yeni_bilgisayar("PC-PASIF", userAccountControl=4098)]), ["Guest", "krbtgt", "mehmet.yilmaz", "burak.sahin", "svc_yedek"], "devre dışı bilgisayar gelmemeli")
```

```solution
(&(objectCategory=person)(objectClass=user)(userAccountControl:1.2.840.113556.1.4.803:=2))
```

```hint
Yalnızca 2 bitine bak: `(userAccountControl:1.2.840.113556.1.4.803:=2)`. Kullanıcı hesabı koşulunu ekle.
```
:::

::: gorev Etkin ve parolası dolmayan
**Etkin** olup parolasının süresi **hiç dolmayan** kullanıcı hesaplarını getir. Bu hesaplar parola politikasının dışında kalır; denetimde ilk bakılan listedir.

```starter
(&(objectCategory=person)(objectClass=user)(userAccountControl=66048))
```

```test
eq(sonuc, ["Administrator", "can.ozkan", "svc_sql"], "etkin ve parolası dolmayan üç hesap")
eq(dene(ek=[yeni_kullanici("ndp.etkin", userAccountControl=1114624)]), ["Administrator", "can.ozkan", "svc_sql", "ndp.etkin"], "1114624 (65536 + 512 + NOT_DELEGATED) gelmeli")
eq(dene(ek=[yeni_kullanici("ndp.pasif", userAccountControl=66050)]), ["Administrator", "can.ozkan", "svc_sql"], "devre dışı 66050 gelmemeli")
eq(dene(ek=[yeni_kullanici("normal", userAccountControl=512)]), ["Administrator", "can.ozkan", "svc_sql"], "parolası dolan 512 gelmemeli")
```

```solution
(&
  (objectCategory=person)
  (objectClass=user)
  (userAccountControl:1.2.840.113556.1.4.803:=65536)
  (!(userAccountControl:1.2.840.113556.1.4.803:=2))
)
```

```hint
İki ayrı bit koşulu: 65536 açık olmalı, 2 açık olmamalı. İkincisini `(!(...))` ile olumsuzla.
```
:::

::: gorev Zayıf kimlik doğrulama ayarı
**Etkin** kullanıcı hesaplarından PASSWD_NOTREQD (32) **ya da** DONT_REQ_PREAUTH (4194304) bayraklarından **en az biri** açık olanları getir. İkisi de güvenlik taramalarında düzeltilmesi istenen ayarlardır.

```starter
(&(objectCategory=person)(objectClass=user)(userAccountControl:1.2.840.113556.1.4.803:=4194336))
```

```test
eq(sonuc, ["svc_rapor"], "etkin hesaplardan yalnızca svc_rapor (4194816)")
eq(dene(ek=[yeni_kullanici("parolasiz", userAccountControl=544)]), ["svc_rapor", "parolasiz"], "yalnızca 32 biti açık etkin hesap (544) gelmeli")
eq(dene(ek=[yeni_kullanici("ikisi.de", userAccountControl=4194848)]), ["svc_rapor", "ikisi.de"], "iki biti de açık etkin hesap gelmeli")
eq(dene(ek=[yeni_kullanici("pasif.parolasiz", userAccountControl=546)]), ["svc_rapor"], "devre dışı 546 gelmemeli")
eq(dene(ek=[yeni_kullanici("temiz", userAccountControl=66048)]), ["svc_rapor"], "iki biti de kapalı hesap gelmemeli")
eq(dene(ek=[yeni_kullanici("komsu.bitler", userAccountControl=513)]), ["svc_rapor"], "SCRIPT (1) gibi komşu bitleri açık hesap (513) gelmemeli")
```

```solution
(&
  (objectCategory=person)
  (objectClass=user)
  (userAccountControl:1.2.840.113556.1.4.804:=4194336)
  (!(userAccountControl:1.2.840.113556.1.4.803:=2))
)
```

```hint
"En az biri" BIT_OR'dur: `1.2.840.113556.1.4.804`, maske 32 + 4194304 = 4194336. Burak Sahin ve Guest bu bayrağı taşır ama devre dışıdır; etkinlik koşulunu ekle.
```
:::
