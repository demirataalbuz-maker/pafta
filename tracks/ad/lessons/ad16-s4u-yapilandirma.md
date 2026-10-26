---
id: ad16
title: S4U İçin Yapılandırma Kanıtını Okumak
summary: S4U2Self ve S4U2Proxy ayrımı, klasik ve kaynak tabanlı devir ayarlarının yönü; yapılandırma bulgusunu başarılı bilet isteğinden ayırmak.
---

::: anlat Bir hizmet neden kullanıcı adına bilet ister?
AD08 üç devir türünü tanıttı. Şimdi web ön hizmeti ile SQL arka hizmeti arasındaki akışı okuyacağız. **S4U2Self**, ön hizmetin kullanıcı adına *kendi hizmetine* bilet istemesidir. **S4U2Proxy**, kullanıcı adına *başka bir hizmete* bilet istemesidir. Biletteki kullanıcı ile isteği gönderen hizmet hesabını karıştırma. [Microsoft MS-SFU genel bakış](https://learn.microsoft.com/en-us/openspecs/windows_protocols/MS-SFU/36d103d2-61a6-42d5-a725-74de3205cdaf).

Klasik kısıtlı devirde ön hizmetin `msDS-AllowedToDelegateTo` listesi hedef SPN'leri taşır. Kaynak tabanlı kısıtlı devirde hedef hesabın `msDS-AllowedToActOnBehalfOfOtherIdentity` güvenlik tanımlayıcısı hangi ön hizmetlere izin verildiğini belirtir. İkinci alan basit bir SPN veya hesap adı listesi değildir. `PrincipalsAllowedToDelegateToAccount` bunu yönetim için okunabilir hesaplara bağlar. [Microsoft devir açıklaması](https://learn.microsoft.com/en-us/windows-server/security/kerberos/kerberos-constrained-delegation-overview), [Set-ADComputer parametresi](https://learn.microsoft.com/en-us/powershell/module/activedirectory/set-adcomputer#-principalsallowedtodelegatetoaccount).

Klasik S4U2Proxy akışında kanıt biletinin `forwardable` niteliği önemlidir. RBCD'de hassas olmayan bir kullanıcıya ait nonforwardable S4U2Self bileti için protokolde bir istisna vardır; “forwardable kapalıysa her devir başarısızdır” çıkarımı doğru değildir. [MS-SFU koşulları](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-sfu/ddb2cafd-1f01-4834-b52a-d4a5b34cd960).
:::

::: anlat Kanıt dosyasının sınırı
`s4u.json` sentetik ders verisidir. `allowed_to_act` ve `trusted_to_auth_for_delegation` alanları ders için normalize edilmiştir; ham LDAP çıktısı değildir. Bu tezgah KDC çalıştırmaz, bilet üretmez ve bir devir isteğinin kabul edileceğine karar vermez. Yapılandırmanın bulunması yalnızca **inceleme adayı** üretir; kullanıcı koruması, bilet özellikleri, SPN kaydı, güven ilişkisi ve gerçek KDC kararı ayrıca denetlenir.

Kendi AD12 laboratuvarında Windows PowerShell ve ActiveDirectory modülüyle bu okuma komutlarını çalıştırabilirsin:

```powershell norun
Get-ADUser -Filter * -Properties servicePrincipalName,msDS-AllowedToDelegateTo,TrustedToAuthForDelegation,AccountNotDelegated |
    Select-Object SamAccountName,servicePrincipalName,msDS-AllowedToDelegateTo,TrustedToAuthForDelegation,AccountNotDelegated
Get-ADComputer -Filter * -Properties PrincipalsAllowedToDelegateToAccount |
    Select-Object SamAccountName,PrincipalsAllowedToDelegateToAccount
```

Çıktıyı okurken ön hizmetteki klasik izin ile hedefteki RBCD iznini ayrı satıra yaz. [Get-ADUser özellik seçimi](https://learn.microsoft.com/en-us/powershell/module/activedirectory/get-aduser), [Get-ADComputer](https://learn.microsoft.com/en-us/powershell/module/activedirectory/get-adcomputer).
:::

::: tahmin İzin nerede duruyor?
Bu iki satır ne yazar? İkisi aynı hesapta mı tanımlı?

```python
import json
v = json.load(open("s4u.json", encoding="utf-8"))
spn = "MSSQLSvc/sql01.pafta.local:1433"
print(v["hesaplar"]["svc_portal"]["allowed_to_delegate_to"][0])
print(v["kaynaklar"][spn]["allowed_to_act"][0])
```

???

`MSSQLSvc/sql01.pafta.local:1433` ve `svc_on` yazılır. İlki ön hizmet `svc_portal` üzerindeki klasik hedef listesinden; ikincisi SQL kaynağına ait normalize RBCD kanıtından gelir.

```meta
motor: python
dil: python
```
:::

::: gorev Yapılandırma adaylarını iki yönde çıkar
`adaylar(v)` işlevi `(tür, ön_hesap, hedef_spn)` üçlülerini yinelenmeden ve sıralı olarak döndürsün. Tür `klasik` veya `rbcd` olsun. Klasik kenarlar hesapların `allowed_to_delegate_to`, RBCD kenarları kaynakların `allowed_to_act` listelerinden gelir. Ön hesabın `hesaplar` içinde bulunması ve en az bir SPN'inin olması şarttır. Boş SPN'leri atla. `trusted_to_auth_for_delegation` tek başına hedef ilişkisi değildir; kapalı olması da RBCD kaydını ortadan kaldırmaz. Bu işlev başarı tahmini yapmaz.

```starter
import json
veri = json.load(open("s4u.json", encoding="utf-8"))

def adaylar(v):
    return []

print(adaylar(veri))
```

```test
import copy
spn = "MSSQLSvc/sql01.pafta.local:1433"
eq(adaylar(veri), [("klasik", "svc_portal", spn), ("rbcd", "svc_on", spn)], "iki farklı yön")
v = copy.deepcopy(veri)
v["hesaplar"]["svc_portal"]["trusted_to_auth_for_delegation"] = False
eq(adaylar(v), adaylar(veri), "bayrak hedef listesi değildir")
v["hesaplar"]["svc_portal"]["allowed_to_delegate_to"] = []
eq(adaylar(v), [("rbcd", "svc_on", spn)], "klasik liste boşken yalnız RBCD")
v["kaynaklar"][spn]["allowed_to_act"] = []
eq(adaylar(v), [], "iki listede de izin yok")
v = copy.deepcopy(veri)
v["hesaplar"]["svc_portal"]["spn"] = ""
v["kaynaklar"][spn]["allowed_to_act"] = ["olmayan", "svc_on", "svc_on"]
eq(adaylar(v), [("rbcd", "svc_on", spn)], "SPN'siz ve bilinmeyen ön hesap dışarıda; tekrar yok")
v = copy.deepcopy(veri)
v["hesaplar"]["svc_rapor"]["allowed_to_delegate_to"] = ["CIFS/dosya01.pafta.local", "", "CIFS/dosya01.pafta.local"]
eq(adaylar(v), [("klasik", "svc_portal", spn), ("klasik", "svc_rapor", "CIFS/dosya01.pafta.local"), ("rbcd", "svc_on", spn)], "yeni hedef ve tekrar sınırı")
eq(adaylar({"hesaplar": {}, "kaynaklar": {}}), [], "boş dışa aktarım")
```

```solution
import json
veri = json.load(open("s4u.json", encoding="utf-8"))

def adaylar(v):
    sonuc = set()
    hesaplar = v["hesaplar"]
    for ad, hesap in hesaplar.items():
        if hesap["spn"]:
            for spn in hesap["allowed_to_delegate_to"]:
                if spn:
                    sonuc.add(("klasik", ad, spn))
    for spn, kaynak in v["kaynaklar"].items():
        if not spn:
            continue
        for ad in kaynak["allowed_to_act"]:
            if ad in hesaplar and hesaplar[ad]["spn"]:
                sonuc.add(("rbcd", ad, spn))
    return sorted(sonuc)

print(adaylar(veri))
```

```hint
İki bağımsız döngü kur. RBCD'de listenin anahtarı hedef SPN, listedeki değer ön hesaptır. Üçlüleri bir kümeye ekleyip sonunda sırala.
```

```meta
motor: python
dil: python
```
:::
