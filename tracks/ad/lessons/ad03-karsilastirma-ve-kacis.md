---
id: ad03
title: Sıralama Karşılaştırmaları ve Kaçış Karakterleri
summary: RFC 4515'te yalnızca >= ve <= vardır; kesin büyüklüğü olumsuzlama ve varlıkla kurmak, sayısal ve metin karşılaştırması, pwdLastSet=0 tuzağı, \2a \28 \29 \5c kaçışlarıyla özel karakter aramak.
---

::: anlat Yalnızca >= ve <=
RFC 4515'te sıralama için **iki** işleç vardır: `>=` (büyük ya da eşit) ve `<=` (küçük ya da eşit). `>` ve `<` **yoktur**; gerçek sunucu da tezgah da onları içeren filtreyi reddeder:

```ad norun
(badPwdCount>4)
```

Sınırlar **dahildir**:

```ad
(badPwdCount>=5)

(&(badPwdCount>=1)(badPwdCount<=2))
```

### Kesin büyüklük nasıl yazılır?
"4'ten büyük" demek istiyorsan iki yol var:

- Tam sayılarda bir sonraki değeri kullan: `(badPwdCount>=5)`.
- Olumsuzlama: `(!(badPwdCount<=4))`. Ama `!` özniteliği **hiç olmayan** nesneleri de getirir (onlar için `badPwdCount<=4` yanlıştır, olumsuzu doğrudur). Bu yüzden varlıkla birleştir: `(&(badPwdCount=*)(!(badPwdCount<=4)))`.

```ad
(&(objectCategory=person)(objectClass=user)(badPwdCount=*)(!(badPwdCount<=4)))
```

### Sayı mı, metin mi?
Karşılaştırma özniteliğin **sözdizimine** göre yapılır. `badPwdCount`, `logonCount`, `userAccountControl`, `adminCount` ve `pwdLastSet` tam sayıdır, sayısal karşılaştırılır: `(logonCount>=100)`, 95'i dışarıda bırakır, 142'yi alır. Metin öznitelikleri ise sözlük sırasıyla ve büyük-küçük harfe duyarsız karşılaştırılır: `(sAMAccountName>=s)`, `s` ile başlayan ve alfabede ondan sonra gelen adları verir.

```ad
(&(objectCategory=person)(objectClass=user)(sAMAccountName>=svc_s))
```

> [!TUZAK]
> `pwdLastSet` parolanın son değiştiği anı **1601-01-01'den beri geçen 100 nanosaniyelik aralık** (FILETIME) olarak tutar. Değeri **0** ise "bir sonraki oturumda parolasını değiştirmeli" demektir. "Parolası 1 Ocak 2024'ten önce değişmiş hesaplar" için `(pwdLastSet<=133485408000000000)` yazarsan 0 değerli hesaplar da gelir. Onları ayrı ele almak için `(pwdLastSet>=1)` koşulunu ekle.

```ad
(&(objectCategory=person)(objectClass=user)(pwdLastSet>=1)(pwdLastSet<=133485408000000000))
```
:::

::: anlat Özel karakterleri kaçırmak
Filtrenin içinde `*`, `(`, `)` ve `\` özel anlam taşır. Değerin içinde **harfiyen** geçmeleri gerekiyorsa RFC 4515 kaçışıyla yazılırlar: ters bölü ve iki onaltılık basamak.

| Karakter | Kaçış |
|---|---|
| `*` | `\2a` |
| `(` | `\28` |
| `)` | `\29` |
| `\` | `\5c` |
| NUL | `\00` |

Dizinde bunlara örnek var: Ayşe Demir'in açıklaması `Onay: *Tam*`, Zeynep Arslan'ınki `Yol: C:\Araclar\AD`, Ali Kaya'nınki `Vardiya-1 (Merkez)`.

```ad
(description=Onay: \2aTam\2a)

(description=*\28Merkez\29*)

(description=*C:\5cAraclar\5cAD*)
```

İlk filtrede kaçışsız `*` yazsaydın joker olurdu: `(description=Onay: *Tam*)` "Onay: ile başlayıp Tam içeren" her açıklamayı arardı. Kaçışsız `(` ya da `)` ise filtreyi bozar; tezgah gerçek sunucu gibi reddeder:

```ad norun
(description=Vardiya-1 (Merkez))
```

> [!GÜVENLİK]
> Bir uygulama kullanıcıdan aldığı metni kaçırmadan LDAP filtresine eklerse, kullanıcı `*` ya da `)(` yazarak filtrenin anlamını değiştirebilir. Bu, SQL'deki enjeksiyonun LDAP'taki karşılığıdır (LDAP injection). Savunması aynıdır: girdideki özel karakterleri her zaman bu tabloyla kaçır ya da kütüphanenin kaçış fonksiyonunu kullan.
:::

::: tahmin
İki filtre art arda çalışıyor. Ne yazdırır?

```ad
(&(badPwdCount>=3)(badPwdCount<=4))

(description=*\28*)
```

???

Önce `zeynep.arslan`, `can.ozkan`, `burak.sahin`, sonra `ali.kaya`, `svc_web`, `svc_rapor`, `Tedarikci Destek`. İlk filtrede iki sınır da dahildir: 3 (Zeynep, Burak) ve 4 (Can) gelir, 5 (Mehmet) ve 6 (svc_yedek) gelmez. İkinci filtre açıklamasında harfiyen `(` geçen **her** nesneyi arar: "Vardiya-1 (Merkez)", "Portal web uygulamasi (*uretim*)", "Eski raporlama betigi (C:\Rapor)" ve kişi nesnesinin "Dis tedarikci destek adresi (kisi nesnesi, hesap degil)" açıklaması. Nesne türü koşulu olmadığı için kişi de listeye girer.
:::

::: gorev Kilitlenme eşiğine yaklaşanlar
Kurumun kilitleme eşiği 5 hatalı parola. Eşiğe **bir adım kalmış ya da eşiği geçmiş** kullanıcı hesaplarını, yani `badPwdCount` değeri **4 ya da daha fazla** olanları getir. Bilgisayar hesapları sonuçta olmasın.

```starter
(badPwdCount>4)
```

```test
eq(sonuc, ["mehmet.yilmaz", "can.ozkan", "svc_yedek"], "badPwdCount 4, 5 ve 6 olan üç hesap")
eq(dene(ek=[yeni_kullanici("sinir.uc", badPwdCount=3)]), ["mehmet.yilmaz", "can.ozkan", "svc_yedek"], "badPwdCount=3 gelmemeli")
eq(dene(ek=[yeni_kullanici("sinir.dort", badPwdCount=4)]), ["mehmet.yilmaz", "can.ozkan", "svc_yedek", "sinir.dort"], "badPwdCount=4 gelmeli (sınır dahil)")
eq(dene(ek=[yeni_bilgisayar("PC-HATALI", badPwdCount=9)]), ["mehmet.yilmaz", "can.ozkan", "svc_yedek"], "bilgisayar hesabı gelmemeli")
```

```solution
(&(objectCategory=person)(objectClass=user)(badPwdCount>=4))
```

```hint
`>` yok; "4 ya da daha fazla" zaten `>=4` demek. Kullanıcı hesabı koşulunu da ekle.
```
:::

::: gorev Kesin büyüklük
`logonCount` değeri **300'den büyük** (300 dahil değil) kullanıcı hesaplarını getir. `logonCount` özniteliği hiç olmayan bir hesap da sonuçta olmamalı.

```starter
(&(objectCategory=person)(objectClass=user)(logonCount>300))
```

```test
eq(sonuc, ["svc_sql", "svc_web"], "logonCount 500 ve 310 olan iki hesap")
eq(dene(ek=[yeni_kullanici("sinir.300", logonCount=300)]), ["svc_sql", "svc_web"], "logonCount=300 gelmemeli (kesin büyük)")
eq(dene(ek=[yeni_kullanici("sinir.301", logonCount=301)]), ["svc_sql", "svc_web", "sinir.301"], "logonCount=301 gelmeli")
eq(dene(ek=[yeni_kullanici("hic.girmedi")]), ["svc_sql", "svc_web"], "logonCount özniteliği olmayan hesap gelmemeli")
```

```solution
(&(objectCategory=person)(objectClass=user)(logonCount>=301))
```

```hint
Tam sayıda "300'den büyük", "301 ya da daha büyük" demektir. `(!(logonCount<=300))` yazarsan özniteliği olmayanlar da gelir; o yolu seçersen `(logonCount=*)` ekle.
```
:::

::: gorev Harfiyen yıldız
Açıklamasında (`description`) **harfiyen bir `*` karakteri** geçen nesneleri getir.

```starter
(description=*)
```

```test
eq(sonuc, ["ayse.demir", "svc_web"], "açıklamasında * geçen iki nesne")
eq(dene(ek=[yeni_kullanici("yildizsiz", description="Siradan aciklama")]), ["ayse.demir", "svc_web"], "yıldızsız açıklama gelmemeli")
eq(dene(ek=[yeni_kullanici("sonda.yildiz", description="Not*")]), ["ayse.demir", "svc_web", "sonda.yildiz"], "sonunda * olan açıklama gelmeli")
```

```solution
(description=*\2a*)
```

```hint
Kaçışsız `*` jokerdir. Harfiyen yıldız `\2a` yazılır; çevresine joker koy: `*\2a*`.
```
:::

::: gorev Ters bölülü yol
Açıklamasında **`C:\`** geçen nesneleri getir (büyük-küçük harf fark etmesin).

```starter
(description=*C:*)
```

```test
eq(sonuc, ["zeynep.arslan", "svc_rapor"], "açıklamasında C:\\ geçen iki nesne")
eq(dene(ek=[yeni_kullanici("egik.cizgi", description="Yol: C:/temp")]), ["zeynep.arslan", "svc_rapor"], "C:/ (eğik çizgi) gelmemeli")
eq(dene(ek=[yeni_kullanici("kucuk.harf", description="betik c:\\temp\\a.ps1")]), ["zeynep.arslan", "svc_rapor", "kucuk.harf"], "küçük harfli c:\\ de gelmeli")
```

```solution
(description=*C:\5c*)
```

```hint
`\` filtrede kaçış başlatır; harfiyen ters bölü `\5c` yazılır.
```
:::
