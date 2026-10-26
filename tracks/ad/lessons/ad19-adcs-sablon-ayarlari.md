---
id: ad19
title: AD CS Şablon Ayarlarını Çözümlemek
summary: Sertifika şablonunun konu adı, EKU, onay ve imza koşullarını bit alanlarından okumak; sertifika isteği ile kimlik doğrulamayı ayırmak.
---

::: anlat CA, şablon ve kimlik
AD CS bir sertifika yetkilisidir. Enterprise CA, AD'de saklanan şablonlarla hangi amaç ve koşullarda sertifika düzenleneceğini belirleyebilir. Şablon, düzenlenmiş sertifika değildir. Bir şablonun dizinde bulunması, CA tarafından yayımlandığı veya bir hesabın bu şablonla sertifika alabildiği anlamına da gelmez. [Microsoft şablon kavramları](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/certificate-template-concepts).

Üç ayrı soruyu yanıtla: **Kim başvurabilir? Başvuru hangi koşullarda onaylanır? Sertifika hangi kimliğe ve kullanım amacına bağlanır?** Bunlardan birini görmek diğerlerini kanıtlamaz. EKU'da `1.3.6.1.5.5.7.3.2` Client Authentication, `1.3.6.1.5.5.7.3.1` Server Authentication amacıdır. [Microsoft EKU açıklaması](https://learn.microsoft.com/en-us/troubleshoot/windows-server/networking/certificate-requirements-eap-tls-peap).

`msPKI-Certificate-Name-Flag` bitlerinden `0x1`, başvuranın subject bilgisini sağlamasını; `0x10000`, subject alternative name bilgisini sağlamasını ifade eder. Aynı alandaki başka bitler bu bitleri kapatmaz. `msPKI-Enrollment-Flag` içindeki `0x2`, CA yöneticisi onayı gerektiren pending durumunu belirtir. `msPKI-RA-Signature` gerekli imza sayısını taşır. [Konu adı bayrakları](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-crtd/1192823c-d839-4bc3-9b6b-fa8c53507ae1), [pending bayrağı](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-wcce/9cc7ba15-fcbc-48b3-8a3b-121faef3d5ef), [imza sayısı](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-crtd/160d0057-bfa9-46c5-a839-72e7588f0420).
:::

::: anlat Tezgahta neyi ölçüyoruz?
`adcs.json` sentetik, normalize edilmiş bir denetim kesitidir. Ham AD DACL'sini çözmez ve CA gibi sertifika düzenlemez. Bu derste bayrakları ve listeleri okursun; sonraki derste etkili enrollment ve değiştirme izinleriyle birleştirirsin. Boş EKU veya Any Purpose gibi diğer kullanım durumları burada “yalnız clientAuth OID'si var mı?” sorusundan ayrı tutulur. ClientAuth yok demek bütün diğer sertifika kimlik doğrulama ihtimalleri imkânsız demek değildir.

Güncel Windows DC'lerinde sertifika tabanlı kimlik doğrulamayı yalnız UPN/SAN adına indirgeme. Microsoft'un güçlü sertifika eşlemesi değişiklikleri, 9 Eylül 2025 ve sonrası güncellemelerde eski geçiş ayarlarını kaldırır. Sertifikanın kimliğe güçlü biçimde eşlenmesi ayrı kabul koşuludur. [KB5014754](https://support.microsoft.com/en-us/servicing/os/windows-server/2022/05/kb5014754-certificate-based-authentication-changes-on-windows-domain-controllers).
:::

::: tahmin Onay ve EKU aynı şey mi?
İlk üç şablonun yönetici onayı gereksinimini kod hangi satırlarla yazar?

```python
import json
v = json.load(open("adcs.json", encoding="utf-8"))
for t in v["sablonlar"][:3]:
    print(t["ad"], bool(t["enrollment_flags"] & 2))
```

???

`LegacyClient False`, `WebServer False`, `ManagerApproved True`. Bu yalnız pending bayrağıdır; ilk ikisinin aynı EKU'ya sahip olduğu veya her başvuranın sertifika alacağı sonucu çıkmaz.

```meta
motor: python
dil: python
```
:::

::: gorev Bayrak ve kullanım amacı özetini çıkar
`ozet(t)` işlevi `(subject_sunar, san_sunar, yonetici_onayi, imza_sayisi, client_auth)` beşlisini döndürsün. İlk üç alan ilgili bitlerin açık olup olmadığını, son alan EKU listesinde **tam** `1.3.6.1.5.5.7.3.2` bulunmasını göstersin. `ra_signatures` olduğu gibi sayısal kalsın. İşlev bir güvenlik açığı veya başarılı sertifika oturumu kararı vermesin.

```starter
import json
veri = json.load(open("adcs.json", encoding="utf-8"))

def ozet(t):
    return (False, False, False, 0, False)

print(ozet(veri["sablonlar"][0]))
```

```test
import copy
t = veri["sablonlar"][0]
eq(ozet(t), (True, False, False, 0, True), "temel client şablonu")
for flags, expected in [(0, (False, False)), (1, (True, False)), (2, (False, False)), (65536, (False, True)), (65537, (True, True)), (65538, (False, True)), (0x40000001, (True, False))]:
    x = dict(t, name_flags=flags)
    eq(ozet(x)[:2], expected, "ad bayrakları " + str(flags))
for flags, expected in [(0, False), (1, False), (2, True), (3, True), (4, False), (6, True)]:
    eq(ozet(dict(t, enrollment_flags=flags))[2], expected, "pending bit sınırı " + str(flags))
for count in [0, 1, 2]:
    eq(ozet(dict(t, ra_signatures=count))[3], count, "imza sayısı korunmalı")
for eku, expected in [([], False), (["1.3.6.1.5.5.7.3.1"], False), (["1.3.6.1.5.5.7.3.20"], False), (["1.3.6.1.5.5.7.3.2"], True), (["1.3.6.1.5.5.7.3.1", "1.3.6.1.5.5.7.3.2"], True)]:
    eq(ozet(dict(t, eku=eku))[4], expected, "tam EKU eşleşmesi " + str(eku))
```

```solution
import json
veri = json.load(open("adcs.json", encoding="utf-8"))

def ozet(t):
    return (bool(t["name_flags"] & 1),
            bool(t["name_flags"] & 65536),
            bool(t["enrollment_flags"] & 2),
            t["ra_signatures"],
            "1.3.6.1.5.5.7.3.2" in t["eku"])

print(ozet(veri["sablonlar"][0]))
```

```hint
Bayrak değerini `==` ile sınamak yerine bitwise `&` kullan. EKU bir OID listesidir; alt dize araması yapma.
```

```meta
motor: python
dil: python
```
:::
