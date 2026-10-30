---
id: pu06
title: Sertleştirme · ASR ve Ölçülebilir Pilot
summary: ASR eylemlerini okuyup audit ile block farkını korumak; LAPS ve diğer önleme katmanlarını ayrı kabul kanıtlarıyla değerlendirmek.
---

::: anlat Tespit ile önleme arasındaki boşluk
Bir alarm kuralı davranışı gördüğünü söyler; önleme politikası aynı davranışın yürütülmesini engellemeyi hedefler. Audit gözlem toplar, Block engeller; Warn ise kullanıcıya aşma olanağı tanıyabilen farklı bir kip olduğu için Block diye raporlanmaz. Kural GUID'si, desteklenen OS/Defender durumu, merkezi politikanın kaynağı, istisnalar ve gerçek sonucun hepsi gerekir. Yalnız registry ayarı görmek yeterli değildir.

ASR, Exploit Guard ailesinin davranış odaklı bölümüdür; Network Protection, Controlled Folder Access ve Exploit Protection aynı şey değildir. AppLocker da farklı bir uygulama denetimi katmanıdır. LAPS parolayı yönetir, yazılım allowlist'i yerine geçmez. LAPS'in parola saklama/okuma yetkisi ve süre kanıtını AD25'te öğrendin; burada dağıtım planına bir kabul kapısı olarak bağlarız.

`Get-MpPreference` çıktısındaki AttackSurfaceReductionRules_Ids ve Actions paralel dizilerdir. Eylemler bu dersin kapsamındaki 0 Disabled, 1 Block, 2 Audit, 5 NotConfigured, 6 Warn değerleridir; bilinmeyen değeri Block diye yorumlama. Liste boyları farklıysa zip'in sessiz kırpmasına izin verme. Aynı GUID tekrarlanırsa hangi politikanın etkin olduğunu tahmin etmek yerine hata ver.

Bu tezgah sentetik envanter ve açık pilot kriterlerini değerlendirir. Defender ayarını, LAPS'i, servisleri veya gerçek cihazı değiştirmez. Audit→pilot→kademeli Block geçişi, istisna sahibi/son tarihi, uyumluluk testi, geri dönüş planı ve aynı sensörün testten önce/sonra kayıtları birlikte tutulur. Sayısal pilot eşikleri **Pafta'nın örnek değişiklik politikasıdır**, Microsoft'un ürün varsayılanı değildir.

[ASR eylem değerleri](https://learn.microsoft.com/en-us/defender-endpoint/attack-surface-reduction-rules-configure), [Microsoft ASR referansı](https://learn.microsoft.com/en-us/defender-endpoint/attack-surface-reduction-rules-reference), [audit sonrası pilot geçiş](https://learn.microsoft.com/en-us/defender-endpoint/attack-surface-reduction-rules-deployment-implement), [Exploit Guard katmanları](https://www.microsoft.com/en-us/security/blog/?p=75468), [Windows LAPS mimarisi](https://learn.microsoft.com/en-us/windows-server/identity/laps/laps-concepts-overview).
:::

::: tahmin
```python
actions={0:'Disabled',1:'Block',2:'Audit',5:'NotConfigured',6:'Warn'}
print([actions[i] for i in (2,1,6)])
```

???
`['Audit', 'Block', 'Warn']`. Warn ve Audit, Block sayılmaz.
:::

::: gorev Paralel ASR dizilerini kayıpsız eşle
`asr(ids,actions)` GUID metnini lower yapıp `(guid,kip)` çiftlerini GUID'ye göre sıralasın. Kip sözlüğü Disabled/Block/Audit/NotConfigured/Warn; boy farkı, tekrar GUID ve diğer eylem ValueError. Bu görev GUID sözdizimi doğrulayıcısı değildir.

```starter
def asr(ids, actions):
    return []
```

```test
eq(asr(['B','A','C','D'],[2,1,6,0]),[('a','Block'),('b','Audit'),('c','Warn'),('d','Disabled')],'dört kip ayrı')
eq(asr([],[]),[],'boş politika')
eq(asr(['A'],[5]),[('a','NotConfigured')],'yapılandırılmamış kip block değil')
raises(ValueError,lambda:asr(['A','B'],[1]),msg='zip kırpmasın')
raises(ValueError,lambda:asr(['A','a'],[1,2]),msg='GUID harf durumuyla çoğalmasın')
raises(ValueError,lambda:asr(['A'],[3]),msg='komşu bilinmeyen değer')
```

```solution
def asr(ids,actions):
    modes={0:'Disabled',1:'Block',2:'Audit',5:'NotConfigured',6:'Warn'}
    if len(ids)!=len(actions):raise ValueError('Dizi boyları farklı')
    result={}
    for key,value in zip(ids,actions):
        key=key.lower()
        if key in result or value not in modes:raise ValueError('Tekrar veya bilinmeyen kip')
        result[key]=modes[value]
    return sorted(result.items())
```

```hint
Belge, yapılandırma ve gözlenen etkiyi ayrı değerlendir; sınırda eksik kanıtı başarı sayma.
```
:::

::: gorev Pilotun geçiş kapısını değerlendir
`pilot(v)` yalnız şu **ders politikasında** True: telemetri güncelliği en fazla 24 saat (age_hours 0..24), en az 100 örnek (samples), sıfır yüksek etkili uyumluluk hatası (critical), owner ve rollback_plan boş değil, laps_verified ve exceptions_reviewed tam True. Eksik sayısal kanıt geçişi kapatır. Bu değişikliği uygulamaz.

```starter
def pilot(v):
    return True
```

```test
base={'age_hours':24,'samples':100,'critical':0,'owner':'SOC','rollback_plan':'geri-al-v1','laps_verified':True,'exceptions_reviewed':True}
eq(pilot(base),True,'eşit kapılar dahil')
for key,value in [('age_hours',24.01),('age_hours',-1),('samples',99),('critical',1),('owner',''),('rollback_plan',''),('laps_verified',False),('exceptions_reviewed',False)]:
    eq(pilot(dict(base,**{key:value})),False,'bağımsız kapı '+key)
eq(pilot({}),False,'kanıt yok')
eq(pilot(dict(base,age_hours=0)),True,'0 saatlik taze kanıt alt sınırda dahil')
for key in ('age_hours','critical'):
    eq(pilot({k:v for k,v in base.items() if k!=key}),False,'eksik '+key+' geçiş vermez')
```

```solution
def pilot(v):
    return (0<=v.get('age_hours',25)<=24 and v.get('samples',0)>=100 and v.get('critical',1)==0 and bool(v.get('owner')) and bool(v.get('rollback_plan')) and v.get('laps_verified') is True and v.get('exceptions_reviewed') is True)
```

```hint
Belge, yapılandırma ve gözlenen etkiyi ayrı değerlendir; sınırda eksik kanıtı başarı sayma.
```
:::
