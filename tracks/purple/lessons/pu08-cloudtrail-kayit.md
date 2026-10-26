---
id: pu08
title: AWS CloudTrail · Kimlik, Kayıt ve Eksik Kanıt
summary: Gerçek CloudTrail kayıt biçimindeki sentetik veriyi normalleştirmek; eventID, API hatası ve rol oturumunu ayrı tutmak.
---

::: anlat Buluttaki iz
CloudTrail AWS API ve hesap etkinliklerinin denetim kaydıdır. Event history son 90 günün bölgesel management olaylarını sunar; bu, bütün S3 obje okuma gibi data olaylarının otomatik aynı kapsamda olduğu anlamına gelmez. Trail/event selector ve saklama politikası kapsama dahil edilmeden “CloudTrail'da yok, yapılmadı” deme. Bu ders tenant/abonelik açmaz; API çağrısı yapmaz, ücretli CloudTrail Lake kullanmaz. Kayıtlar gerçek alan adlarıyla hazırlanmış sentetik fixture'lardır.

`eventTime` UTC olay zamanıdır; dosyanın diske iniş zamanı değildir. `eventID` kayıt kimliği, `requestID` hizmet isteği, `sharedEventID` bazı hesaplar arası ortak olayları bağlamaya yarayan farklı alanlardır. Çoğaltılmış aynı eventID'yi tekrar sayma; iki farklı eventID aynı requestID'yi taşısa da otomatik birleştirme. `eventVersion` major.minor'dır; bu ders major=1 kabul eder ve bilinmeyen major'ı reddeder.

`userIdentity.arn` eylemi yapan kimliği verir; AssumedRole durumunda sessionContext.sessionIssuer.arn rolü gösterir. `recipientAccountId` olayın alıcı hesabı, kimliğin hesabıyla aynı olmak zorunda değildir. `sourceIPAddress` her zaman IP olmak zorunda değil; AWS hizmet adı da olabilir. mfaAuthenticated bilgisi oturum bağlamıdır; bir alanın yokluğu MFA yapılmadı kanıtı değildir.

`errorCode` API hatası kanıtıdır; yokluğunda yalnız “hata kodu kaydedilmemiş” deriz. Örneğin ConsoleLogin ayrıntısı responseElements içinde ayrıca değerlendirilir; bu işlev her API'nin iş sonucunu yorumlamaz. `readOnly` alanının true olması olayın önemsiz olduğunu göstermez; hassas okuma da önemlidir.

[AWS kayıt alanları](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-record-contents.html), [userIdentity ve sessionContext](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-user-identity.html), [Event history ve data/trail ayrımı](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-user-guide.html).
:::

::: tahmin
```python
v={'userIdentity':{'type':'AssumedRole','arn':'arn:aws:sts::111111111111:assumed-role/Audit/session','sessionContext':{'sessionIssuer':{'arn':'arn:aws:iam::111111111111:role/Audit'}}}}
u=v['userIdentity']
print(u['type'])
print(u['arn']==u['sessionContext']['sessionIssuer']['arn'])
```

???
`AssumedRole` ve `False`. Rol oturumu ile rol ARN'si ayrı kimliklerdir.
:::

::: gorev Kayıtları UTC ve eventID ile düzenle
`cloudtrail(doc)` Records listesini eventID ile tekrarsızlasın; aynı id farklı ham kayıt taşıyorsa ValueError. Çıktı sırası UTC zaman, sonra id. Her satır `(id,utc_iso,eventSource,eventName,result)`; utc_iso +00:00 biçiminde. result, dolu errorCode varsa o kod; yoksa no-error-recorded. Major sürüm 1 dışında veya timezone yoksa ValueError. Kaydı uydurma başarıya çevirme.

```starter
def cloudtrail(doc):
    return []
```

```test
def e(i,t='2026-10-26T00:00:00Z',**kw): return dict(eventID=i,eventTime=t,eventVersion='1.11',eventSource='iam.amazonaws.com',eventName='CreateUser',**kw)
a=e('a');b=e('b','2026-10-26T01:00:00+01:00',errorCode='AccessDenied')
eq(cloudtrail({'Records':[b,a,a]}),[('a','2026-10-26T00:00:00+00:00','iam.amazonaws.com','CreateUser','no-error-recorded'),('b','2026-10-26T00:00:00+00:00','iam.amazonaws.com','CreateUser','AccessDenied')],'UTC eşit zaman, kimlikle sıra ve tekrar')
eq(cloudtrail({'Records':[]}),[],'boş kayıt')
raises(ValueError,lambda:cloudtrail({'Records':[a,dict(a,eventName='DeleteUser')]}),msg='aynı id farklı kayıt çakışması')
raises(ValueError,lambda:cloudtrail({'Records':[dict(a,eventVersion='2.0')]}),msg='bilinmeyen major')
raises(ValueError,lambda:cloudtrail({'Records':[dict(a,eventTime='2026-10-26T00:00:00')]}),msg='belirsiz yerel saat')
eq(cloudtrail({'Records':[dict(a,responseElements={'ConsoleLogin':'Failure'})]})[0][-1],'no-error-recorded','özel payload sonucu uydurulmaz')
```

```solution
from datetime import datetime, timezone

def cloudtrail(doc):
    seen={}
    for row in doc['Records']:
        if row['eventVersion'].split('.')[0]!='1':raise ValueError('Bilinmeyen major')
        key=row['eventID']
        if key in seen and seen[key]!=row:raise ValueError('Kimlik çakışması')
        seen[key]=row
    result=[]
    for key,row in seen.items():
        dt=datetime.fromisoformat(row['eventTime'].replace('Z','+00:00'))
        if dt.tzinfo is None:raise ValueError('Saat dilimi yok')
        result.append((key,dt.astimezone(timezone.utc).isoformat(),row['eventSource'],row['eventName'],row.get('errorCode') or 'no-error-recorded'))
    return sorted(result,key=lambda v:(v[1],v[0]))
```

```hint
Eksik alanı varsayımla doldurma; kimlik, zaman ve sonuç alanları farklı kanıtlardır.
```
:::

::: gorev Oturum ve MFA belirsizliğini koru
`kimlik(event)` actor/issuer/mfa/source alanlarını döndürsün. Actor userIdentity.arn, issuer sessionContext.sessionIssuer.arn; yoksa None. mfa yalnız string "true"→True / "false"→False; yok veya diğer gösterim→None. Source raw sourceIPAddress; IP'ye zorlamadan koru.

```starter
def kimlik(event):
    return {}
```

```test
a={'userIdentity':{'arn':'session','sessionContext':{'sessionIssuer':{'arn':'role'},'attributes':{'mfaAuthenticated':'false'}}},'sourceIPAddress':'ec2.amazonaws.com'}
eq(kimlik(a),{'actor':'session','issuer':'role','mfa':False,'source':'ec2.amazonaws.com'},'rol/oturum/hizmet kaynağı')
a['userIdentity']['sessionContext']['attributes']['mfaAuthenticated']='true'
eq(kimlik(a)['mfa'],True,'true metni')
a['userIdentity']['sessionContext']['attributes']['mfaAuthenticated']='unexpected'
eq(kimlik(a)['mfa'],None,'bilinmeyen başarı veya ret değildir')
eq(kimlik({}),{'actor':None,'issuer':None,'mfa':None,'source':None},'eksik bağlam')
```

```solution
def kimlik(event):
    u=event.get('userIdentity',{})
    c=u.get('sessionContext',{})
    v=c.get('attributes',{}).get('mfaAuthenticated')
    return {'actor':u.get('arn'),'issuer':c.get('sessionIssuer',{}).get('arn'),'mfa':{'true':True,'false':False}.get(v),'source':event.get('sourceIPAddress')}
```

```hint
Eksik alanı varsayımla doldurma; kimlik, zaman ve sonuç alanları farklı kanıtlardır.
```
:::
