---
id: ad24
title: SYSVOL Kanıtı · Güvenlik Şablonu ve Grup Tercihleri
summary: GptTmpl.inf, Groups.xml ve Registry.pol dosyalarını farklı biçimleriyle okumak; dosya içeriği ile etkili GPO sonucunu ayırmak.
---

::: anlat GPO bir dosyadan ibaret değildir
GPO'nun AD nesnesi, SYSVOL dosyaları, bağlantı sırası, güvenlik/WMI filtreleri, devralma, CSE ve uygulama durumu birlikte sonucu belirler. Bir dosyayı bulmak onun belirli bilgisayarda uygulandığını kanıtlamaz; `gpresult /h` veya Resultant Set of Policy ayrı kabul kanıtıdır. Bu ders **çevrimdışı dosya denetimi**; ana makinenin GPO'sunu değiştirmez ve bütün GPO önceliğini taklit etmez.

`Machine/Microsoft/Windows NT/SecEdit/GptTmpl.inf` güvenlik şablonudur. `[Privilege Rights]` kullanıcı hak atamalarını içerir; `SeRemoteInteractiveLogonRight` ile `SeDenyRemoteInteractiveLogonRight` farklı anahtarlardır. SID'in başındaki `*` şablonun SID gösterimidir, LDAP jokeri değildir. Hak verilmesi tek başına oturum açma başarısı değildir; deny, grup üyeliği ve diğer kontroller de gerekir.

`Machine/Preferences/Groups/Groups.xml` XML'dir. Grup Properties kaydındaki `groupSid` yerelleştirilmiş isimden daha sağlam kimliktir: yerleşik Administrators SID'i `S-1-5-32-544`. Member kaydındaki `action='ADD'` ekleme, `REMOVE` çıkarma isteğidir. Silme/yenileme eylemleri, `deleteAllUsers/deleteAllGroups`, disabled ve item-level targeting sonucu etkiler; görev bunları uygulamaz, **inceleme kanıtı** olarak ayırır. Aynı Groups.xml dosyasındaki tarihî **User/Properties** kaydında `cpassword` alanı varsa yalnız varlığını raporla; değeri loga dökme veya şifre çözmeye çalışma.

[MS-GPSB şablon yolu](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-gpsb/f16c4282-9787-483c-a711-d2b1420230ea), [MS-GPPREF XML biçimi](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-gppref/3aa83b78-9629-45d2-8b34-e56a4800d0ac), [Microsoft Groups tercihleri](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-gppref/4b6788a7-c106-4e55-9cfc-1a52bb786e86). Örnekler açıkça üretilmiş eğitim kesitleridir, gerçek şirket çıktısı değildir.
:::

::: tahmin Allow ile deny aynı anahtar mı?
```python
import configparser
p=configparser.ConfigParser(interpolation=None)
p.read_string('[Privilege Rights]\nSeRemoteInteractiveLogonRight = *S-1-5-32-544\nSeDenyRemoteInteractiveLogonRight = *S-1-5-21-1-2-3-1100')
print(len(p['Privilege Rights']))
print(p['Privilege Rights']['SeRemoteInteractiveLogonRight'])
```
???
`2` ve `*S-1-5-32-544`. İki hak tek bir izin listesine birleştirilmez.
```meta
motor: python
dil: python
```
:::

::: gorev UTF-16 güvenlik şablonunu oku
`haklar(raw)` BOM taşıyan UTF-16 baytlarından yalnız `[Privilege Rights]` bölümünü okusun. Anahtarların harflerini koru; virgülle ayrılan değerleri kırp, varsa baştaki tek `*` işaretini kaldır; boşları at, tekrarsız sırala. Boş atamayı boş liste olarak koru. Bölüm yoksa `{}`. Dosya hatalarını temiz rapor sayma.

```starter
def haklar(raw):
    return {}
```

```test
def raw(s): return s.encode('utf-16')
v=haklar(raw('[Unicode]\nUnicode=yes\n[Privilege Rights]\nSeRemoteInteractiveLogonRight=*S-1-5-32-544, *S-1-5-21-1\nSeDenyRemoteInteractiveLogonRight=*S-1-5-21-1\nSeServiceLogonRight=\n'))
eq(v, {'SeRemoteInteractiveLogonRight':['S-1-5-21-1','S-1-5-32-544'],'SeDenyRemoteInteractiveLogonRight':['S-1-5-21-1'],'SeServiceLogonRight':[]},'allow/deny/hizmet ayrı, boş atama korunur')
eq(haklar(raw('[Privilege Rights]\nSeX=*S-1,*S-1, S-2\n')),{'SeX':['S-1','S-2']},'tekrar ve boşluk')
eq(haklar(raw('[Other]\nSeX=*S-1')),{},'başka bölüm hak değildir')
raises(UnicodeError,lambda:haklar(b'odd'),msg='kodlama hatasını yutma')
```

```solution
import configparser

def haklar(raw):
    text = raw.decode('utf-16')
    p=configparser.ConfigParser(interpolation=None)
    p.optionxform=str
    p.read_string(text)
    section=p['Privilege Rights'] if p.has_section('Privilege Rights') else {}
    return {key:sorted({v.strip().removeprefix('*') for v in value.split(',') if v.strip()}) for key,value in section.items()}

```

```hint
Örnek adını ezberleme; dosyanın biçimini ve alanın bağlamını kontrol et.
```

```meta
motor: python
dil: python
```
:::

::: gorev Grup değişiklik isteğini kanıt olarak çıkar
`grup_kaniti(xml)` yalnız hedef SID 544 kayıtları için belirtilen sözlükleri döndürsün. Eylemleri yürütme. disabled/clear_users/clear_groups/targeting bool; action ve members ham niyet kaydı. Parola alanı bu Group görevinin çıktısında yoktur.

```starter
def grup_kaniti(xml):
    return []
```

```test
xml='''<Groups><Group disabled="0"><Properties action="U" groupName="Yerel yoneticiler" groupSid="S-1-5-32-544" deleteAllUsers="1" deleteAllGroups="0"><Members><Member sid="S-1-5-21-1" action="ADD"/><Member sid="S-1-5-21-2" action="REMOVE"/></Members></Properties><Filters/></Group><Group><Properties groupSid="S-1-5-32-545" groupName="Administrators"/></Group></Groups>'''
eq(grup_kaniti(xml),[{'disabled':False,'action':'U','clear_users':True,'clear_groups':False,'targeting':True,'members':[('S-1-5-21-1','ADD'),('S-1-5-21-2','REMOVE')]}],'SID ile hedef; ADD/REMOVE korunur; sır sızmaz')
v=grup_kaniti(xml.replace('disabled="0"','disabled="1"').replace('deleteAllGroups="0"','deleteAllGroups="1"').replace('<Filters/>',''))[0]
eq((v['disabled'],v['clear_groups'],v['targeting']),(True,True,False),'bağımsız bayraklar')
eq(grup_kaniti('<Groups><Group/></Groups>'),[],'Properties yok')
raises(Exception,lambda:grup_kaniti('<Groups>'),msg='bozuk XML hata')
```

```solution
import xml.etree.ElementTree as ET

def grup_kaniti(xml):
    root=ET.fromstring(xml)
    rows=[]
    for group in root.findall('Group'):
        p=group.find('Properties')
        if p is None or p.get('groupSid')!='S-1-5-32-544':
            continue
        rows.append({'disabled':group.get('disabled')=='1','action':p.get('action'),'clear_users':p.get('deleteAllUsers')=='1','clear_groups':p.get('deleteAllGroups')=='1','targeting':group.find('Filters') is not None,'members':[(m.get('sid'),m.get('action')) for m in p.findall('Members/Member')]})
    return rows

```

```hint
Örnek adını ezberleme; dosyanın biçimini ve alanın bağlamını kontrol et.
```

```meta
motor: python
dil: python
```
:::

::: anlat Registry.pol metin aramasıyla çözülmez
İlk sekiz bayt little-endian DWORD imza `0x67655250` (`PReg`) ve sürüm `1` taşır. Gövde `[key;value;type;size;data]` yapısındadır; UTF-16 adlar, ikili tür/boyut alanları ve bayt verisi nedeniyle düz `split(';')` tam ayrıştırıcı değildir. Makine/User dosyasının yeri kök hive'ı belirler; anahtar metninde HKLM/HKCU yoktur. `**Del...` gibi özel silme yönergelerini sıradan değer sayma.

Bu ders yalnız başlık kabulünü ölçer; gövdeyi uygulamaz veya tam Registry.pol çözümlediğini iddia etmez. [Microsoft Registry policy biçimi](https://learn.microsoft.com/en-us/previous-versions/windows/desktop/Policy/registry-policy-file-format).
:::

::: gorev İkili başlığın tam sınırını doğrula
`pol_baslik(raw)` en az 8 bayt, doğru DWORD imza ve sürüm tam 1 ise True döndürsün. Gövde bundan sonra olabilir; gövde doğruluğu bu işlevin kapsamı değil.

```starter
def pol_baslik(raw):
    return raw.startswith(b"PReg")
```

```test
import struct
eq(pol_baslik(b'PReg'+struct.pack('<I',1)),True,'8 bayt yeter')
eq(pol_baslik(b'PReg'+struct.pack('<I',1)+b'body'),True,'gövde bulunabilir')
for b in (b'',b'PReg',b'PReg\x01\0\0',b'PReg'+struct.pack('<I',0),b'PReg'+struct.pack('<I',2),b'PReg'+struct.pack('>I',1),b'XReg'+struct.pack('<I',1)):
    eq(pol_baslik(b),False,'kısa/komşu sürüm/bayt sırası/yanlış imza')
```

```solution
import struct

def pol_baslik(raw):
    return len(raw)>=8 and struct.unpack('<II',raw[:8])==(0x67655250,1)
```

```hint
Örnek adını ezberleme; dosyanın biçimini ve alanın bağlamını kontrol et.
```

```meta
motor: python
dil: python
```
:::
