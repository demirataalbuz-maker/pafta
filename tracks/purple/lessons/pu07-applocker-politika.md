---
id: pu07
title: AppLocker · Politika Tasarımı ve Kabul Kanıtı
summary: Kural koleksiyonlarını, enforcement kipini ve path/publisher/hash koşullarını okuyup güvenli dağıtım kabulünü planlamak.
---

::: anlat Kural XML'i ile etkin uygulama denetimi
AppLocker kural koleksiyonları Exe, Script, Msi, Dll ve Appx gibi ayrı kapsamlar taşır. Exe koleksiyonu tek başına script veya DLL'leri denetlediğini kanıtlamaz. Publisher kuralı imzalayan/ürün/binary/version koşullarıyla, hash kuralı belirli dosya özetiyle, path kuralı dosya yolu ve o yolun yazılabilirliğiyle değerlendirilir. Kullanıcı yazabildiği dizine verilen geniş allow, yönetici tarafından korunmuş bir dizine verilen allow ile aynı güven sınırı değildir.

Koleksiyon kipleri Enabled, AuditOnly, NotConfigured ayrı raporlanır. AuditOnly olay üretir ama engelleme kanıtı değildir. Enabled olması bile bu cihazda çalışan AppID hizmeti, geçerli politika ve doğru kullanıcı bağlamı kontrol edilmeden tam kabul sayılmaz. Kural koleksiyonu içindeki explicit deny allow'dan önce gelir; kural olmayan dosyanın varsayılan reddi de ilgili koleksiyonun gerçekten etkin kuralları varken yorumlanır. Eksik veya boş koleksiyon için “her şey kesin engellenir” çıkarımı yapma.

Bu ders gerçek XML ayrıştırır ama **AppLocker eşleştiricisini taklit etmez**; publisher zinciri, sürüm aralıkları, SID jetonu ve yol değişkenleri bu Python görevinin kapsamı değildir. XML'deki Exceptions da koşul değildir; raporda ayrı tutulur. Gerçek kabulte Get-AppLockerPolicy -Effective ve Test-AppLockerPolicy ile hedef kullanıcı/dosya çiftlerini ölç, audit olayını incele, sonra ayrı pilotta enforcement sonucunu doğrula. Burada ana makineye politika yüklenmez.

[Microsoft koleksiyon ve koşulları](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/app-control-for-business/applocker/working-with-applocker-rules), [deny/allow değerlendirmesi](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/app-control-for-business/applocker/understanding-applocker-allow-and-deny-actions-on-rules), [Test-AppLockerPolicy](https://learn.microsoft.com/en-us/powershell/module/applocker/test-applockerpolicy).
:::

::: tahmin
```python
import xml.etree.ElementTree as ET
r=ET.fromstring('<AppLockerPolicy Version="1"><RuleCollection Type="Exe" EnforcementMode="AuditOnly"/><RuleCollection Type="Script" EnforcementMode="Enabled"/></AppLockerPolicy>')
print([(c.get('Type'),c.get('EnforcementMode')) for c in r])
```

???
`[('Exe', 'AuditOnly'), ('Script', 'Enabled')]`. Script kipini Exe'ye taşımayız.
:::

::: gorev Koşulu ve istisnayı ayrı envanterle
`politika(xml)` her RuleCollection için (Type, EnforcementMode, rules) üçlüsü döndürsün. rules sırası XML sırası; her kural (Id,Action,UserOrGroupSid,Conditions altındaki doğrudan çocuk tag listesi,Exceptions altındaki doğrudan çocuk tag listesi). Eksik kip `NotConfigured`. Kural türleri FilePathRule/FileHashRule/FilePublisherRule. XML hatası yükselsin.

```starter
def politika(xml):
    return []
```

```test
x=r'''<AppLockerPolicy Version="1"><RuleCollection Type="Exe" EnforcementMode="AuditOnly"><FilePathRule Id="p" Action="Allow" UserOrGroupSid="S-1-1-0"><Conditions><FilePathCondition Path="*"/></Conditions><Exceptions><FilePathCondition Path="C:\Temp\*"/></Exceptions></FilePathRule><FileHashRule Id="h" Action="Deny" UserOrGroupSid="S-1-1-0"><Conditions><FileHashCondition/></Conditions></FileHashRule></RuleCollection><RuleCollection Type="Script"/></AppLockerPolicy>'''
eq(politika(x),[('Exe','AuditOnly',[('p','Allow','S-1-1-0',['FilePathCondition'],['FilePathCondition']),('h','Deny','S-1-1-0',['FileHashCondition'],[])]),('Script','NotConfigured',[])],'kapsam, kip, deny ve exception ayrı')
eq(politika(x.replace('AuditOnly','Enabled'))[0][1],'Enabled','kip sabitlenmez')
eq(politika('<AppLockerPolicy/>'),[],'boş politika')
raises(Exception,lambda:politika('<broken>'),msg='XML hatasını gizleme')
```

```solution
import xml.etree.ElementTree as ET

def politika(xml):
    result=[]
    for c in ET.fromstring(xml).findall('RuleCollection'):
        rules=[]
        for r in c:
            if r.tag not in ('FilePathRule','FileHashRule','FilePublisherRule'):continue
            rules.append((r.get('Id'),r.get('Action'),r.get('UserOrGroupSid'),[v.tag for v in r.findall('Conditions/*')],[v.tag for v in r.findall('Exceptions/*')]))
        result.append((c.get('Type'),c.get('EnforcementMode','NotConfigured'),rules))
    return result
```

```hint
Belge, yapılandırma ve gözlenen etkiyi ayrı değerlendir; sınırda eksik kanıtı başarı sayma.
```
:::

::: gorev Önleme iddiası için gerekli kanıtları ayır
`kabul(rows)` kendi eğitim kabul kayıtlarından id listesi döndürsün: mode=Enabled, service_running tam True, effective_policy tam True, expected=Denied ve observed=Denied, tested_user/tested_file boş değil. Audit kaydı ve yalnız benzetim sonucu gerçek enforcement kanıtı değildir; lab_test_kind tam enforcement olmalı. Sıralı tekrarsız id. Bu ürünün iç kararı değil teslim kapısıdır.

```starter
def kabul(rows):
    return [r["id"] for r in rows]
```

```test
base={'id':'a','mode':'Enabled','service_running':True,'effective_policy':True,'expected':'Denied','observed':'Denied','tested_user':'S-1-5-21-1','tested_file':'C:/Lab/x.exe','lab_test_kind':'enforcement'}
eq(kabul([base,base]),['a'],'ölçülen yasak ve tekrar')
for key,value in [('mode','AuditOnly'),('mode','NotConfigured'),('service_running',False),('effective_policy',False),('observed','Allowed'),('expected','Allowed'),('tested_user',''),('tested_file',''),('lab_test_kind','simulation')]:
    eq(kabul([dict(base,**{key:value})]),[],'eksik kabul kanıtı '+key)
eq(kabul([]),[],'boş liste')
```

```solution
def kabul(rows):
    return sorted({r['id'] for r in rows if r.get('mode')=='Enabled' and r.get('service_running') is True and r.get('effective_policy') is True and r.get('expected')=='Denied' and r.get('observed')=='Denied' and bool(r.get('tested_user')) and bool(r.get('tested_file')) and r.get('lab_test_kind')=='enforcement'})
```

```hint
Belge, yapılandırma ve gözlenen etkiyi ayrı değerlendir; sınırda eksik kanıtı başarı sayma.
```
:::
