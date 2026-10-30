---
id: ad25
title: LAPS · Görünür Öznitelik ile Okuma Yetkisini Ayırmak
summary: Legacy ve Windows LAPS alanlarını tanımak, FILETIME sınırını okumak ve gizli değeri rapora dökmeden erişim kanıtını sınıflamak.
---

::: anlat Bir isimden yetki çıkmaz
Legacy LAPS `ms-Mcs-AdmPwd` ve `ms-Mcs-AdmPwdExpirationTime` kullanır. Windows LAPS `msLAPS-Password`, `msLAPS-EncryptedPassword` ve `msLAPS-PasswordExpirationTime` gibi farklı şema alanları kullanır. İki aileyi eş anlamlı veya aynı kodlama sanma. `msLAPS-Password` JSON metnidir: n hesap, t güncelleme zamanının hex FILETIME değeri, p açık paroladır. Parolayı rapora yazmak gereksiz ifşadır. EncryptedPassword bir bayt alanıdır; JSON diye açılmaz. Parola okuma ile şifreli parolayı çözme yetkisi farklı kontroller olabilir.

PasswordExpirationTime planlanan sona erme FILETIME'ıdır; genel bir Unix saniyesi değildir. FILETIME 1601-01-01 UTC'den 100 ns birimlerle sayılır. Güncelleme zamanı ile sona erme aynı alan değildir. Süreye gelinmiş olması döndürmenin gerçekleştiği anlamına gelmez; istemci işlemi ayrıca doğrulanır. [Windows LAPS şema/JSON sözleşmesi](https://learn.microsoft.com/en-us/windows-server/identity/laps/laps-technical-reference), [FILETIME](https://learn.microsoft.com/en-us/windows/win32/api/minwinbase/ns-minwinbase-filetime), [LAPS mimarisi ve ACL/şifreleme](https://learn.microsoft.com/en-us/windows-server/identity/laps/laps-concepts-overview).

Boş veya görünmeyen bir öznitelik “LAPS kurulu değil” veya “kimse okuyamaz” kanıtı değildir. AD'nin şeması, istemci politikası, yetki jetonu, confidential öznitelik izinleri ve sorgu sonucu ayrı incelenir. `Find-LapsADExtendedRights` fazla genişletilmiş hakları bulmak için yardımcıdır; bir ACL satırı tek başına her parola/şifre çözme yetkisinin tam kararı değildir. [Cmdlet sözleşmesi](https://learn.microsoft.com/en-us/windows-server/identity/laps/laps-scenarios-windows-server-active-directory).

Bu ders normalize edilmiş, **sentetik** okuma sonucu kesitleriyle çalışır. Ana makineye veya önceki AD VM'lerine LAPS politikası yüklemez; şema değişikliği/parola döndürme yapmaz. `permission` alanı dersin önceden doğrulanmış okuma denemesidir, ham LDAP özniteliği değildir. Gerçek kabul için test hesabıyla parola değerini kaydetmeden erişim denemesi ve LAPS operational olayları birlikte incelenir.
:::

::: tahmin Aynı güncelleme, farklı sona erme
```python
import json
v=json.loads('{"n":"Administrator","t":"1d0000000000000","p":"EGITIM-VERISI"}')
print(sorted(v))
print(v['n'])
```
???
`['n', 'p', 't']` ve `Administrator`. Kod parola değerini yazdırmaz; t güncelleme zamanıdır, expiration değildir.
```meta
motor: python
dil: python
```
:::

::: gorev Sır içermeyen zaman raporu üret
`laps_meta(text, expiry, now)` Windows LAPS JSON'undan account ve updated (hex t → int), verilen decimal FILETIME expiry/now üzerinden due döndürsün. Tam sona erme anı due=True. Yalnız bu üç anahtar döndür.

```starter
def laps_meta(text, expiry, now):
    return {}
```

```test
import json
raw=json.dumps({'n':'Administrator','t':'10','p':'NEVER-LOG-THIS'})
eq(laps_meta(raw,32,32),{'account':'Administrator','updated':16,'due':True},'tam son tarih dahil')
eq(laps_meta(raw,33,32)['due'],False,'son tarihten önce')
eq(laps_meta(raw,31,32)['due'],True,'son tarihi geçmiş')
v=laps_meta(json.dumps({'n':'YerelYonetici','t':'100','p':'SECRET'}),'1000','999')
eq(v,{'account':'YerelYonetici','updated':256,'due':False},'hex update ile decimal expiration farklı')
ok('p' not in v and 'SECRET' not in repr(v),'parola taşınmaz')
raises(Exception,lambda:laps_meta('bad',1,1),msg='JSON hatasını yutma')
```

```solution
import json

def laps_meta(text, expiry, now):
    v=json.loads(text)
    return {'account':v['n'],'updated':int(v['t'],16),'due':int(expiry)<=int(now)}

```

```hint
Örnek adını ezberleme; dosyanın biçimini ve alanın bağlamını kontrol et.
```

```meta
motor: python
dil: python
```
:::

::: gorev Erişim kanıtının sınırını koru
`okuma_kaniti(row)` aşağıdaki sıralı sözleşmeyi uygulasın: denied → erisim-reddi; allowed dışı → belirsiz; allowed iken encrypted_present → sifreli-veri-goruldu; sonra clear_present → acik-veri-goruldu; ikisi yok → izinli-ama-deger-yok. Bunlar gözlem etiketleridir, tüm AD yetki motoru değil.

```starter
def okuma_kaniti(row):
    return "belirsiz"
```

```test
eq(okuma_kaniti({'permission':'denied','clear_present':True}),'erisim-reddi','ret önce gelir, eski değerle izin çıkarma')
eq(okuma_kaniti({}),'belirsiz','öznitelik yokluğundan yetki çıkarma')
eq(okuma_kaniti({'permission':'unknown','encrypted_present':True}),'belirsiz','başka bağlamdan değer kanıt sayılmaz')
eq(okuma_kaniti({'permission':'allowed'}),'izinli-ama-deger-yok','okuma izni ile değer ayrı')
eq(okuma_kaniti({'permission':'allowed','clear_present':True}),'acik-veri-goruldu','açık değer')
eq(okuma_kaniti({'permission':'allowed','encrypted_present':True}),'sifreli-veri-goruldu','şifre çözme yetkisi iddiası yok')
eq(okuma_kaniti({'permission':'allowed','clear_present':True,'encrypted_present':True}),'sifreli-veri-goruldu','sözleşmede şifreli alan öncelikli')
```

```solution
def okuma_kaniti(row):
    if row.get('permission')=='denied':
        return 'erisim-reddi'
    if row.get('permission')!='allowed':
        return 'belirsiz'
    if row.get('encrypted_present'):
        return 'sifreli-veri-goruldu'
    if row.get('clear_present'):
        return 'acik-veri-goruldu'
    return 'izinli-ama-deger-yok'

```

```hint
Örnek adını ezberleme; dosyanın biçimini ve alanın bağlamını kontrol et.
```

```meta
motor: python
dil: python
```
:::
