---
id: pu09
title: Entra ID · Oturum ve Dizin Değişikliğini İlişkilendirmek
summary: Sign-in ile directoryAudit biçimlerini ayırmak; status, Conditional Access, sabit kullanıcı kimliği ve zaman penceresiyle kanıt toplamak.
---

::: anlat Giriş başarısı ile politika sonucu farklıdır
Entra signIn kaydı oturum etkinliğini, directoryAudit dizindeki değişiklikleri anlatır. Azure Monitor dışa aktarımı ile Microsoft Graph JSON alan adları farklı olabilir; bu ders açıkça **Graph v1.0 biçimini** kullanır. id/userId/createdDateTime/status/conditionalAccessStatus alanlarıyla çalışır; Log Analytics ResultType/TimeGenerated alanlarını bu sözlüğe sessizce karıştırmaz.

Sign-in status.errorCode=0 başarılı giriş sonucudur; hata kodu, Conditional Access sonucu ve risk alanları ayrı tutulur. conditionalAccessStatus=notApplied tek başına “MFA atlatıldı” veya “güvenli” demek değildir. authenticationRequirement bir gereksinimdir; kullanıcının o anda yeni MFA yaptığını tek başına kanıtlamaz. authenticationDetails, kimlik doğrulama adımları ve daha önce karşılanmış claim'ler ayrıca incelenir. Risk bilgisinin saklama/lisans/erişim nedeniyle görünmemesi “risk yok” değildir.

DirectoryAudit `initiatedBy.user.id` değişikliği başlatan kullanıcıyı, `initiatedBy.app` uygulama bağlamını ve targetResources hedefleri gösterir. Hedef kullanıcıyla başlatan kullanıcıyı karıştırma. correlationId iş akışını incelemeye yardım eder ama birbirinden bağımsız sign-in ve audit kayıtlarında her zaman aynı olacağı varsayılmaz. Bu ders sabit userId ve zaman yakınlığıyla **inceleme adayları** üretir; nedensellik veya ele geçirilme kanıtı üretmez.

Kayıtlar sentetiktir; tenant'a bağlanma, Graph token'ı, P1/P2 aboneliği veya ücretli hizmet kurulumu yoktur. Graph sign-in indirme lisans/izin gereksinimleri gerçek kullanımda ayrıca karşılanır. [Graph signIn](https://learn.microsoft.com/en-us/graph/api/resources/signin?view=graph-rest-1.0), [signInStatus](https://learn.microsoft.com/en-us/graph/api/resources/signinstatus?view=graph-rest-1.0), [directoryAudit](https://learn.microsoft.com/en-us/graph/api/resources/directoryaudit?view=graph-rest-1.0), [sign-in ve audit günlüklerinin ayrımı](https://learn.microsoft.com/en-us/entra/identity/monitoring-health/concept-sign-ins).
:::

::: tahmin
```python
v={'status':{'errorCode':0},'conditionalAccessStatus':'notApplied'}
print(v['status']['errorCode']==0)
print(v['conditionalAccessStatus']=='success')
```

???
`True` ve `False`. Başarılı giriş, Conditional Access uygulanmış demek değildir.
:::

::: gorev Başarı ve eksik sonucu ayır
`giris(v)` (sonuc,ca) döndürsün. sonuc status.errorCode tam int 0→success; başka tam int→failure; eksik/None/yanlış tür→unknown (bool kabul edilmez). ca alanı varsa raw değer, yoksa unknown. CA'dan giriş sonucu türetme.

```starter
def giris(v):
    return ("success", "success")
```

```test
eq(giris({'status':{'errorCode':0},'conditionalAccessStatus':'notApplied'}),('success','notApplied'),'CA farklı alan')
eq(giris({'status':{'errorCode':50076},'conditionalAccessStatus':'failure'}),('failure','failure'),'MFA gereksinimi hatası')
eq(giris({}),('unknown','unknown'),'eksik başarı değil')
for code in (None,'0',False):
    eq(giris({'status':{'errorCode':code}})[0],'unknown','gösterim tipi')
eq(giris({'status':{'errorCode':-1}})[0],'failure','sıfır dışı kod')
```

```solution
def giris(v):
    code=v.get('status',{}).get('errorCode')
    outcome='unknown' if type(code) is not int else ('success' if code==0 else 'failure')
    return outcome,v.get('conditionalAccessStatus','unknown')
```

```hint
Eksik alanı varsayımla doldurma; kimlik, zaman ve sonuç alanları farklı kanıtlardır.
```
:::

::: gorev Dizin değişikliğini doğru kullanıcı ve pencereyle bağla
`adaylar(signins,audits,span)` yalnız status.errorCode tam int 0 olan girişleri, başarılı (`result="success"`) audit değişiklikleriyle bağlasın. Giriş userId ile audit initiatedBy.user.id eşit ve boş değil; 0<=audit_time-signin_time<=span saniye. span>=0; negatif span ValueError. UTC offsetli zamanlar zorunlu. Sonuç sıralı tekrarsız (signIn.id,audit.id) çiftleri. Hedefe göre veya app.id ile bağlama; nedensellik iddiası yok.

```starter
def adaylar(signins, audits, span):
    return []
```

```test
s=[{'id':'s','userId':'u1','createdDateTime':'2026-10-26T00:00:00Z','status':{'errorCode':0}}]
def a(i,t,user='u1',result='success'):return {'id':i,'activityDateTime':t,'result':result,'initiatedBy':{'user':{'id':user}},'targetResources':[{'id':'u1'}]}
r=[a('zero','2026-10-26T00:00:00Z'),a('edge','2026-10-26T01:05:00+01:00'),a('after','2026-10-26T00:05:01Z'),a('before','2026-10-25T23:59:59Z'),a('other','2026-10-26T00:01:00Z','u2'),a('failed','2026-10-26T00:01:00Z',result='failure')]
eq(adaylar(s,r+r,300),[('s','edge'),('s','zero')],'iki eşit sınır ve tekrar; hedef değil başlatan')
eq(adaylar([dict(s[0],status={'errorCode':1})],r,300),[],'başarısız giriş')
eq(adaylar([dict(s[0],status={})],r,300),[],'eksik status')
eq(adaylar(s,[{'id':'app','activityDateTime':'2026-10-26T00:01:00Z','result':'success','initiatedBy':{'app':{'servicePrincipalId':'u1'}}}],300),[],'uygulama kullanıcı kimliği değildir')
eq(adaylar(s,r,0),[('s','zero')],'sıfır pencere yalnız aynı an')
raises(ValueError,lambda:adaylar(s,r,-1),msg='negatif pencere')
eq(adaylar([dict(s[0],userId='')],r,300),[],'boş kullanıcı')
eq(adaylar([dict(s[0],status={'errorCode':False})],r,300),[],'bool başarı kodu değil')
raises(ValueError,lambda:adaylar([dict(s[0],createdDateTime='2026-10-26T00:00:00')],r,300),msg='naif giriş zamanı')
raises(ValueError,lambda:adaylar(s,[a('naive','2026-10-26T00:00:00')],300),msg='naif audit zamanı')
```

```solution
from datetime import datetime

def adaylar(signins,audits,span):
    if span<0:raise ValueError('Negatif pencere')
    def instant(value):
        t=datetime.fromisoformat(value.replace('Z','+00:00'))
        if t.tzinfo is None:raise ValueError('Saat dilimi yok')
        return t
    result=set()
    for s in signins:
        code=s.get('status',{}).get('errorCode')
        if type(code) is not int or code!=0 or not s.get('userId'):continue
        st=instant(s['createdDateTime'])
        for a in audits:
            actor=a.get('initiatedBy',{}).get('user',{}).get('id')
            if a.get('result')!='success' or actor!=s['userId']:continue
            delta=(instant(a['activityDateTime'])-st).total_seconds()
            if 0<=delta<=span:result.add((s['id'],a['id']))
    return sorted(result)
```

```hint
Eksik alanı varsayımla doldurma; kimlik, zaman ve sonuç alanları farklı kanıtlardır.
```
:::
