---
id: ad20
title: Şablon İzinlerini ve Yayım Durumunu Denetlemek
summary: Enrollment ile şablon değiştirme hakkını ayırmak, çok koşullu bir inceleme listesi üretmek ve CA/DC'de gerçek kabul kanıtını toplamak.
---

::: anlat Enroll, Read ve WriteDacl farklı haklardır
Şablonun görünmesi, başvurabilmek anlamına gelmez. `Certificate-Enrollment` genişletilmiş hakkının GUID'si `0e10c968-78fb-11d2-90d4-00c04f79dc55`'tir. Bunu genel okuma veya şablonun DACL'sini değiştirme hakkıyla karıştırma. Etkili hakkı bulurken AD13'teki özne/grup/deny/devralma ayrımları ve nesneye özgü GUID değerlendirmesi gerekir. [Microsoft Enroll hakkı](https://learn.microsoft.com/en-us/windows/win32/adschema/r-certificate-enrollment).

Bu derste `enroll_effective` **önceden hesaplanmış etkili enrollment iznini**, `edit_effective` ise **önceden doğrulanmış şablon değiştirme yeteneğini** gösterir. İki liste birbirinden bağımsızdır. Şablonu değiştirebilen bir hesap, bugünkü enrollment koşulları kapalı olsa bile ayrı incelenir. Bu alanlar Windows veya LDAP'ın yerleşik öznitelik adları değildir; sentetik ders sözleşmesidir.
:::

::: anlat Gerçek CA'da kabul listesi
AD12 laboratuvarına CA rolü eklendiğinde, şablonları yalnız AD'deki listeden okumakla yetinme. Şablon özelliklerini, şablon DACL'sini ve CA'nın yayımladığı şablonları karşılaştır. [Şablon kavramları](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/certificate-template-concepts).

Windows PowerShell/RSAT bulunan laboratuvarda ham AD şablon ayarlarını şu okuma komutuyla inceleyebilirsin:

```powershell norun
$config = (Get-ADRootDSE).configurationNamingContext
$base = "CN=Certificate Templates,CN=Public Key Services,CN=Services,$config"
Get-ADObject -SearchBase $base -LDAPFilter '(objectClass=pKICertificateTemplate)' -Properties msPKI-Certificate-Name-Flag,msPKI-Enrollment-Flag,msPKI-RA-Signature,pKIExtendedKeyUsage |
    Select-Object Name,DistinguishedName,msPKI-Certificate-Name-Flag,msPKI-Enrollment-Flag,msPKI-RA-Signature,pKIExtendedKeyUsage
```

`certutil -CATemplates` CA şablonlarını, `certutil -Template` şablon bilgisini incelemek için kullanılabilir; CA seçimini kendi laboratuvarına göre yap. Bu komutlar Pafta'nın bellekteki dizinine bağlanmaz. [certutil seçenekleri](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/certutil).

Kabulte yayımlanan/yayımlanmayan, enrollment verilen/verilmeyen, pending açık/kapalı ve gerekli imza sayısı 0/1 olan test şablonlarını karşılaştır. Gerçek başvuru sonucunu CA'nın issued/pending/denied kaydıyla doğrula. Sertifika düzenlenmesini DC'de o kullanıcı olarak oturum açma başarısıyla eşitleme; güçlü kimlik eşlemesi ayrıca sınanır. [Microsoft güçlü eşleme değişiklikleri](https://support.microsoft.com/en-us/servicing/os/windows-server/2022/05/kb5014754-certificate-based-authentication-changes-on-windows-domain-controllers).

Sonraki AD21 dersinde Pafta gerçek CA ve şablonları arka planda kullanır; VM konsoluna girmeden bu ayrımları sınarsın. Canlı CA olmadan bu kabul adımları yapılmış sayılmaz. Aşağıdaki görev yalnız çevrimdışı inceleme listesidir; bütün ESC sınıfları için bir tarayıcı değildir.
:::

::: tahmin Değiştirme ile enrollment izni
`EditableClient` için bu kod ne yazar? Başvuru hakkı olmadığı için şablon değiştirme hakkını göz ardı edebilir miyiz?

```python
import json
v = json.load(open("adcs.json", encoding="utf-8"))
t = next(t for t in v["sablonlar"] if t["ad"] == "EditableClient")
print(bool(t["enroll_effective"]), bool(t["edit_effective"]))
```

???

`False True` yazılır. Enrollment ve şablon değiştirme ayrı haklardır; ikincisi bağımsız bir inceleme bulgusudur.

```meta
motor: python
dil: python
```
:::

::: gorev İki bağımsız inceleme listesi
`bulgular(v, grup)` sıralı ve tekrarsız `(neden, şablon_adı)` çiftleri döndürsün. İki neden var:

- `enrollment`: Şablon yayımlanmış, gruba etkili enrollment izni verilmiş, ClientAuth OID'si var, subject sağlama biti açık, pending biti kapalı ve imza sayısı tam 0.
- `degistirme`: Grup `edit_effective` içinde. Yayımlanma ve bugünkü enrollment ayarlarından bağımsızdır.

Bu yalnız bu koşullar için **inceleme önceliği** çıkarır; “kimlik taklidi başarılı olur” veya “listede olmayan güvenlidir” sonucu üretmez.

```starter
import json
veri = json.load(open("adcs.json", encoding="utf-8"))

def bulgular(v, grup):
    return []

print(bulgular(veri, "Domain Users"))
```

```test
import copy
eq(bulgular(veri, "Domain Users"), [("degistirme", "EditableClient"), ("enrollment", "LegacyClient")], "iki bağımsız bulgu")
eq(bulgular(veri, "BaskaGrup"), [], "başka öznenin izni kullanılmaz")
base = veri["sablonlar"][0]
for alan, deger in [("published", False), ("enroll_effective", []), ("eku", ["1.3.6.1.5.5.7.3.1"]), ("name_flags", 0), ("name_flags", 2), ("enrollment_flags", 2), ("enrollment_flags", 3), ("ra_signatures", 1), ("ra_signatures", 2)]:
    x = copy.deepcopy(base)
    x[alan] = deger
    eq(bulgular({"sablonlar": [x]}, "Domain Users"), [], "eksilen koşul: " + alan + "=" + str(deger))
for alan, deger in [("name_flags", 3), ("enrollment_flags", 1), ("enrollment_flags", 4)]:
    x = dict(base, **{alan: deger})
    eq(bulgular({"sablonlar": [x]}, "Domain Users"), [("enrollment", "LegacyClient")], "komşu bit koşulu bozmaz")
x = copy.deepcopy(veri["sablonlar"][-1])
x["published"] = False
eq(bulgular({"sablonlar": [x]}, "Domain Users"), [("degistirme", "EditableClient")], "yayımlanmayan şablonda da değiştirme incelenir")
x["edit_effective"] = []
eq(bulgular({"sablonlar": [x]}, "Domain Users"), [], "değiştirme izni kaldırılınca bulgu kalkar")
eq(bulgular({"sablonlar": [base, base]}, "Domain Users"), [("enrollment", "LegacyClient")], "tekrarlı veri tek bulgu")
eq(bulgular({"sablonlar": []}, "Domain Users"), [], "boş dizin")
```

```solution
import json
veri = json.load(open("adcs.json", encoding="utf-8"))

def bulgular(v, grup):
    sonuc = set()
    for t in v["sablonlar"]:
        if grup in t["edit_effective"]:
            sonuc.add(("degistirme", t["ad"]))
        if (t["published"] and grup in t["enroll_effective"]
                and "1.3.6.1.5.5.7.3.2" in t["eku"]
                and t["name_flags"] & 1
                and not t["enrollment_flags"] & 2
                and t["ra_signatures"] == 0):
            sonuc.add(("enrollment", t["ad"]))
    return sorted(sonuc)

print(bulgular(veri, "Domain Users"))
```

```hint
Değiştirme koşulunu enrollment için yazdığın `if` bloğunun içine koyma. Bitleri `&` ile, imza sayısını tam eşitlikle sına.
```

```meta
motor: python
dil: python
```
:::
