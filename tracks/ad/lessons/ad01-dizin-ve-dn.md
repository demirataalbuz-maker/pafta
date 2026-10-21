---
id: ad01
title: Dizin Ağacı, DN ve İlk Filtre
summary: Active Directory'nin ağaç yapısı, distinguishedName'i sağdan sola okumak, OU ile kapsayıcı farkı, sAMAccountName/cn/UPN, ilk RFC 4515 filtresi, büyük-küçük harf duyarsızlığı ve objectClass ile objectCategory farkı.
---

::: anlat Dizin bir ağaçtır
Active Directory (AD), bir kurumdaki kullanıcıları, bilgisayarları ve grupları tutan **dizin hizmetidir**. Bu yolun tezgahında `pafta.local` adlı sahte ama gerçeğe sadık bir etki alanı var. Etki alanının adı dizinde `DC=pafta,DC=local` olarak yazılır ve ağacın köküdür:

```text
DC=pafta,DC=local
├── CN=Users                  (kapsayıcı: Administrator, Guest, krbtgt, Domain Admins)
├── OU=Domain Controllers     (DC01)
├── OU=Merkez
│   ├── OU=SOC                (ali.kaya, ayse.demir, mehmet.yilmaz)
│   ├── OU=BT                 (zeynep.arslan, can.ozkan)
│   ├── OU=Finans             (elif.koc, burak.sahin, Tedarikci Destek kişisi)
│   └── CN=Selin Aydinkaya
├── OU=ServisHesaplari        (svc_sql, svc_web, svc_yedek, svc_rapor)
├── OU=Sunucular              (SRV-SQL01, SRV-WEB01, SRV-ESKI01)
├── OU=Istasyonlar            (PC-SOC01, PC-FIN01)
└── OU=Gruplar                (SOC-Analistleri, Altyapi-Yoneticileri, ...)
```

Her nesnenin ağaçtaki tam adresi **distinguishedName** (DN) özniteliğidir. DN **sağdan sola** okunur: önce etki alanı, sonra üst birim, en solda nesnenin kendi adı.

| DN parçası | Anlamı |
|---|---|
| `DC=` | etki alanı bileşeni (domain component): `pafta.local` → `DC=pafta,DC=local` |
| `OU=` | yapısal birim (organizational unit); yönetimi devretmek ve grup ilkesi bağlamak için |
| `CN=` | ortak ad (common name): kullanıcı, bilgisayar, grup ya da `CN=Users` gibi bir **kapsayıcı** |

`CN=Ali Kaya,OU=SOC,OU=Merkez,DC=pafta,DC=local` şöyle okunur: pafta.local etki alanında, Merkez birimi içindeki SOC biriminde duran **Ali Kaya** nesnesi. En soldaki parça (`CN=Ali Kaya`) göreli addır (RDN).

> [!TUZAK]
> `CN=Users` bir OU **değildir**, bir kapsayıcıdır (`objectClass=container`). Yeni kurulan her etki alanında yerleşik hesaplar ve `Domain Admins` grubu buradadır. Kapsayıcılara grup ilkesi (GPO) bağlanamaz; bu yüzden kurumlar kendi OU'larını açar.

### Bir kullanıcının üç adı
| Öznitelik | Örnek | Nerede kullanılır |
|---|---|---|
| `sAMAccountName` | `ali.kaya` | eski tarz oturum adı (`PAFTA\ali.kaya`), en çok sorgulanan alan |
| `cn` / `name` | `Ali Kaya` | DN'deki görünen ad |
| `userPrincipalName` | `ali.kaya@pafta.local` | e-posta biçimli oturum adı |

Bilgisayar hesaplarının `sAMAccountName` değeri **`$` ile biter**: `SRV-SQL01$`. Kişi (contact) nesnelerinin ise hiç `sAMAccountName`'i yoktur, çünkü oturum açamazlar.

> [!NOT]
> **Tezgahın çıktısı:** her eşleşen nesne için bir satır yazılır: `sAMAccountName` (kişi ve OU nesnelerinde `name`). Sağdaki tablo aynı sonucu sütunlarla gösterir. Gerçek AD sonuçların sırasını garanti etmez; tezgah dizin dosyasındaki sırayı kullanır, böylece tahminlerin her seferinde aynı çıkar.
:::

::: anlat İlk LDAP filtresi
AD'nin konuştuğu dil **LDAP**'tır; arama filtrelerinin yazımı **RFC 4515**'te tanımlıdır. En basit filtre tek bir karşılaştırmadır ve **her zaman parantez içindedir**:

```ad
(department=SOC)
```

Kurallar:

- `(öznitelik=değer)` biçimi; parantezler zorunludur.
- **Öznitelik adları büyük-küçük harfe duyarsızdır**: `department`, `Department` ve `DEPARTMENT` aynı alandır.
- AD'deki metin öznitelikleri (Directory String) **değer karşılaştırmasında da duyarsızdır**: `(department=soc)` ile `(department=SOC)` aynı sonucu verir.
- `=` **değerin tamamını** karşılaştırır: `(title=Analist)`, "Kidemli Analist" unvanını **bulmaz**.

```ad
(department=soc)

(sAMAccountName=ZEYNEP.ARSLAN)
```

### objectClass ve objectCategory
Her nesnenin iki tür bilgisi vardır:

- **`objectClass`** çok değerlidir; sınıf zincirinin tamamını tutar. Bir kullanıcı: `top, person, organizationalPerson, user`. Bir bilgisayar: `top, person, organizationalPerson, user, computer`. Yani **bilgisayar da bir `user`'dır**.
- **`objectCategory`** tek değerlidir ve dizinde indekslidir. Kullanıcılarda ve kişilerde (contact) `person`, bilgisayarlarda `computer`, gruplarda `group`'tur.

Çok değerli bir öznitelikte filtre, **değerlerden herhangi biri** eşleşirse doğrudur. Bu yüzden `(objectClass=user)` bilgisayarları da getirir:

```ad
(objectClass=computer)

(objectClass=contact)
```

Gerçek kullanıcı hesaplarını getirmenin yerleşik deyimi iki koşulu birlikte istemektir. `&` "ve" demektir (bir sonraki derste ayrıntısıyla); koşullar onun arkasına parantez parantez dizilir:

```ad
(&(objectCategory=person)(objectClass=user))
```

`objectCategory=person` bilgisayarları dışarıda bırakır; `objectClass=user` ise kişi nesnelerini (Tedarikci Destek) dışarıda bırakır.

> [!DERİN]
> Gerçek AD'de `objectCategory`'nin değeri aslında bir DN'dir: `CN=Person,CN=Schema,CN=Configuration,DC=pafta,DC=local`. `(objectCategory=person)` kısa yazımı çalışır, çünkü sunucu sınıf adını şemadaki **defaultObjectCategory** değerine çevirir. Bu çevirinin bir yan etkisi var: `user` ve `contact` sınıflarının ikisinin de varsayılan kategorisi `Person`'dır, yani `(objectCategory=user)` yazmak `(objectCategory=person)` yazmakla aynıdır ve kişileri de getirir. Tezgah bu davranışı aynen taklit eder.
:::

::: tahmin
Bu iki filtre hangi satırları yazar?

```ad
(TITLE=analist)

(department=FINANS)
```

???

Çıktı üç satırdır: `mehmet.yilmaz`, sonra `elif.koc` ve `burak.sahin`. İlk filtrede öznitelik adı da değer de büyük-küçük harfe duyarsız karşılaştırılır, ama `=` değerin **tamamını** ister: Ali Kaya'nın unvanı "Kidemli Analist", Ayşe Demir'inki "SOC Takim Lideri" olduğu için yalnızca unvanı tam olarak "Analist" olan Mehmet Yılmaz eşleşir. İkinci filtrede `FINANS` ile `Finans` aynıdır. Finans OU'sundaki Tedarikci Destek kişisinin `department` özniteliği hiç olmadığı için o eşleşmez.
:::

::: gorev BT departmanı
`department` değeri **BT** olan nesneleri getiren bir LDAP filtresi yaz.

```starter
(department=SOC)
```

```test
eq(sonuc, ["zeynep.arslan", "can.ozkan"], "BT departmanındaki iki kişi")
eq(dene(ek=[yeni_kullanici("deneme.bt", ou="OU=BT,OU=Merkez", department="bt")]), ["zeynep.arslan", "can.ozkan", "deneme.bt"], "değer karşılaştırması büyük-küçük harfe duyarsızdır: 'bt' de eşleşmeli")
eq(dene(ek=[yeni_kullanici("deneme.btd", department="BT Destek")]), ["zeynep.arslan", "can.ozkan"], "'BT Destek' eşleşmemeli: = değerin tamamını karşılaştırır")
```

```solution
(department=BT)
```

```hint
Tek bir karşılaştırma yeter: `(öznitelik=değer)`.
```
:::

::: gorev Yalnızca kullanıcı hesapları
Dizindeki bütün **kullanıcı hesaplarını** getir: bilgisayar hesapları da, kişi (contact) nesneleri de sonuçta olmasın.

```starter
(objectClass=user)
```

```test
KULLANICILAR = ["Administrator", "Guest", "krbtgt", "ali.kaya", "ayse.demir", "mehmet.yilmaz", "zeynep.arslan", "can.ozkan", "elif.koc", "burak.sahin", "selin.aydinkaya", "svc_sql", "svc_web", "svc_yedek", "svc_rapor"]
eq(sonuc, KULLANICILAR, "15 kullanıcı hesabı; bilgisayar ve kişi yok")
eq(dene(ek=[yeni_bilgisayar("PC-YENI01")]), KULLANICILAR, "yeni bir bilgisayar hesabı (objectClass'ında user da var) gelmemeli")
kisi = {"distinguishedName": "CN=Yeni Kisi,OU=Finans,OU=Merkez,DC=pafta,DC=local", "cn": "Yeni Kisi", "name": "Yeni Kisi", "objectCategory": "person", "objectClass": ["top", "person", "organizationalPerson", "contact"]}
eq(dene(ek=[kisi]), KULLANICILAR, "yeni bir kişi nesnesi (objectCategory=person) gelmemeli")
eq(dene(ek=[yeni_kullanici("yeni.kullanici")]), KULLANICILAR + ["yeni.kullanici"], "yeni bir kullanıcı gelmeli")
```

```solution
(&(objectCategory=person)(objectClass=user))
```

```hint
`objectClass=user` bilgisayarları da kapsar; `objectCategory=person` kişileri de kapsar. İkisini `(&(...)(...))` ile birlikte iste.
```
:::
