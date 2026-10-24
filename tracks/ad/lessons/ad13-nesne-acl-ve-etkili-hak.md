---
id: ad13
title: Nesne ACL'sinden Etkili Hakkı Okumak
summary: Grup jetonu, owner, sıralı allow/deny ACE ve devralınmış kayıtlardan bir AD nesnesindeki etkili hakkı hesaplamak.
---

::: anlat Bir grup üyeliği tek başına yetki değildir
AD'de her nesnenin güvenlik tanımlayıcısı ve isteğe bağlı DACL'si vardır. DACL, sıralı ACE kayıtları taşır; erişim kontrolü kişinin kendi SID'sini ve grup SID'lerini kullanır. Bir grubun ACL'de bulunması, bütün üyelerinin bütün hakları aldığı anlamına gelmez: hak, hedef nesne ve olası deny kaydı da önemlidir. [Microsoft'un AD erişim modeli](https://learn.microsoft.com/en-us/windows/win32/ad/how-access-control-works-in-active-directory-domain-services), [basit AD erişim denetimi](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-adts/c55e113e-25a2-45eb-abba-bf5a9e521a8f).

Bu dersin `acl.json` dosyası **sentetik ve çevrimdışıdır**. Kodun Python ile bir *kanıt kesitini* yorumlar; Windows AccessCheck, SIDHistory, conditional ACE, özel GUID hakkı, ayrıcalıklar ve gerçek `nTSecurityDescriptor` çözümlemesi değildir. Gerçek ortamda `Get-Acl AD:\...` ile ACE'leri ve owner'ı oku; bir hak için son kararı hedef DC/Windows güvenlik denetimiyle doğrula. [Get-Acl](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.security/get-acl).

İlk ayrım: `WriteDacl` DACL'yi değiştirme hakkıdır; mevcut anda `GenericAll` sahipliği demek değildir. BloodHound iki ilişkiyi ayrı gösterir: [WriteDacl](https://bloodhound.specterops.io/resources/edges/write-dacl), [GenericAll](https://bloodhound.specterops.io/resources/edges/generic-all). Bir nesnenin owner'ı, basit AD erişim denetiminde `ReadControl`, `WriteDacl` ve `WriteOwner` haklarını başlangıçta elde eder. [Microsoft protokol kuralı](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-adts/c55e113e-25a2-45eb-abba-bf5a9e521a8f).
:::

::: anlat ACE sırası ve devralma
Kanıt dosyasında her nesnenin `aces` dizisi, **hedef DACL'de görülen sıradır**. Motor hiçbir ACE'yi yeniden sıralamaz. AD'nin kanonik sıralamasında açık ACE'ler devralınmış ACE'lerden önce, deny kayıtları allow kayıtlarından önce gelir. Fakat erişim denetimi girişleri sırayla değerlendirir; bu nedenle kanıtı sıralamadan okumak gerekir. `inherit_only` kayıt hedef nesnede etkili değildir; devralınmış ve etkili ACE ise hedef DACL'de zaten yer alır. [ACE sırası](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-adts/dbfdc00c-1e4b-4165-939b-974e8ea23733), [AccessCheck](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-adts/c55e113e-25a2-45eb-abba-bf5a9e521a8f).

Şu gerçek komut bir nesnenin ACL'sini incelemek için kullanılabilir; Pafta'nın sentetik `acl.json` dosyasına karşı çalışmaz:

```powershell norun
$dn = 'CN=svc_sql,OU=ServisHesaplari,DC=pafta,DC=local'
$sd = Get-Acl -Path "AD:\$dn"
$sd.Owner
$sd.Access | Select-Object IdentityReference,AccessControlType,ActiveDirectoryRights,ObjectType,IsInherited,InheritanceType
```
:::

::: tahmin ACL kanıtını oku
`svc_sql` üzerindeki ilk iki ACE hangi türdedir ve hangi SID/gruba ilişkindir? Kodun yazacağı iki satırı tahmin et.

```python
import json
veri = json.load(open("acl.json", encoding="utf-8"))
for ace in veri["nesneler"]["svc_sql"]["aces"][:2]:
    print(f'{ace["tur"]}|{ace["kim"]}|{ace["haklar"][0]}')
```

???

`deny|mehmet.yilmaz|WriteDacl` ve `allow|SOC-Analistleri|WriteDacl`. Mehmet gruba üye olsa da kendi açık deny kaydı önce okunur.

```meta
motor: python
dil: python
```
:::

::: gorev Sıralı DACL'den tek hakkı hesapla
`etkili(veri, kisi, hedef, hak)` işlevini yaz. Kişinin geçişli grup üyeliklerini topla; owner ise `ReadControl`, `WriteDacl`, `WriteOwner` başlangıç haklarını dikkate al. Yalnız istenen hak için ACE'leri verildikleri sırada işle: `inherit_only` kayıtlarını atla, ilgili kişiye/gruba ait deny kaydı henüz verilmemiş hakkı engeller; daha önce verilmiş hakkı geriye dönük silmez. `GenericAll` bu dersin dört somut hakkını (`ReadProperty`, `WriteProperty`, `WriteDacl`, `WriteOwner`) kapsar. Olmayan nesne ve boş DACL için `False` döndür.

Gerçek AD'deki nesne türüne bağlı GUID hakları ve özel erişim bitleri burada modellenmez; onları genelleyip `GenericAll` kabul etme.

```starter
import json
veri = json.load(open("acl.json", encoding="utf-8"))

def etkili(veri, kisi, hedef, hak):
    return False

print(etkili(veri, "ali.kaya", "svc_sql", "WriteDacl"))
```

```test
import copy
eq(etkili(veri, "ali.kaya", "svc_sql", "WriteDacl"), True, "gruptan gelen izin")
eq(etkili(veri, "mehmet.yilmaz", "svc_sql", "WriteDacl"), False, "kişisel deny gruptan gelen allow'u keser")
eq(etkili(veri, "ayse.demir", "svc_rapor", "WriteDacl"), True, "owner WriteDacl")
eq(etkili(veri, "ayse.demir", "svc_rapor", "GenericAll"), False, "owner GenericAll değildir")
eq(etkili(veri, "ali.kaya", "svc_rapor", "GenericAll"), False, "inherit-only ACE hedefte etkisiz")
eq(etkili(veri, "ali.kaya", "SRV-SQL01$", "ReadProperty"), True, "hedefte bulunan devralınmış ACE")
eq(etkili(veri, "ali.kaya", "SRV-SQL01$", "WriteProperty"), False, "okuma yazma değildir")
eq(etkili(veri, "ayse.demir", "SRV-SQL01$", "WriteProperty"), True, "ikinci gruptan hak")
eq(etkili(veri, "olmayan", "olmayan", "WriteDacl"), False, "olmayan hedef")
v = copy.deepcopy(veri)
v["gruplar"]["yeni"] = ["ara"]
v["gruplar"]["ara"] = ["SOC-Analistleri", "yeni"]
eq(etkili(v, "yeni", "svc_sql", "WriteDacl"), True, "geçişli üyelik ve döngü")
v = copy.deepcopy(veri)
v["nesneler"]["svc_sql"]["aces"] = []
eq(etkili(v, "ali.kaya", "svc_sql", "WriteDacl"), False, "boş DACL örtük ret")
v = copy.deepcopy(veri)
v["nesneler"]["svc_sql"]["aces"] = [
    {"tur": "allow", "kim": "ali.kaya", "haklar": ["GenericAll"]},
    {"tur": "deny", "kim": "ali.kaya", "haklar": ["WriteDacl"]}]
eq(etkili(v, "ali.kaya", "svc_sql", "WriteDacl"), True, "sıra değişince karar değişir")
v["nesneler"]["svc_sql"]["aces"].reverse()
eq(etkili(v, "ali.kaya", "svc_sql", "WriteDacl"), False, "deny önceyse karar ret")
```

```solution
import json
veri = json.load(open("acl.json", encoding="utf-8"))

def etkili(veri, kisi, hedef, hak):
    nesne = veri["nesneler"].get(hedef)
    if nesne is None:
        return False
    token = {kisi}
    bekleyen = [kisi]
    while bekleyen:
        for grup in veri["gruplar"].get(bekleyen.pop(), []):
            if grup not in token:
                token.add(grup)
                bekleyen.append(grup)

    verildi = kisi == nesne["owner"] and hak in {"ReadControl", "WriteDacl", "WriteOwner"}
    engelli = False
    for ace in nesne["aces"]:
        if ace.get("inherit_only") or ace["kim"] not in token:
            continue
        kapsar = hak in ace["haklar"] or ("GenericAll" in ace["haklar"] and hak in {"ReadProperty", "WriteProperty", "WriteDacl", "WriteOwner", "GenericAll"})
        if not kapsar:
            continue
        if ace["tur"] == "deny" and not verildi:
            engelli = True
        elif ace["tur"] == "allow" and not engelli:
            verildi = True
    return verildi

print(etkili(veri, "ali.kaya", "svc_sql", "WriteDacl"))
```

```hint
Önce token kümesini döngüye dayanıklı biçimde büyüt. Owner'ın başlangıç haklarını ekle. Sonra ACE dizisini asla yeniden sıralamadan tara; `inherit_only` kaydını atla.
```

```meta
motor: python
dil: python
```
:::
