---
id: ht20
title: Oturuma Bağlı CSRF ve Gerçek SameSite
summary: Oturumlar arasında taşınamayan jetonla yazma yap; farklı sitelerde çerezlerin gönderilmesini gözle.
timeout: 60
---

::: anlat Kimlik, niyet ve tarayıcının çerezi
HT11'in sabit form jetonu doğrulama yapmıyordu. Yeni laboratuvarda `POST /session` rastgele oturum, `GET /csrf` o oturuma bağlı rastgele jeton üretir. `POST /change` hem Cookie'yi hem `X-CSRF-Token` değerini doğrular. Eksik/yanlış/başka oturumun jetonu 403 verir ve revision değişmez; oturumsuz istek 401'dir. Reset eski oturumları iptal eder. Jetonları URL'ye veya rapora yazma.

Bu laboratuvar **synchronizer token** modelidir; üretim oturum süresi, logout, XSS savunması ve dağıtık depolama kapsam dışıdır. JSON API'nin /items uç noktaları yetkilendirme deneyi içindir; /change jeton deneyinin ayrı uç noktasıdır.

`samesite_report()` gerçek tarayıcıda `app.pafta.test` ve `evil.other.test` kullanır: farklı portlardan farklı olarak bunlar farklı sitelerdir. DNS yalnız bu tarayıcı sürecinin resolver ayarıyla loopback'e çevrilir; hosts dosyası değiştirilmez. Uygulama açıkça SameSite=Lax ve Strict çerezleri koyar; diğer siteden uygulamaya üst düzey GET ve POST form navigasyonları yapılır. GET'te Lax gönderilir, Strict gönderilmez; POST'ta ikisi de gönderilmez. Bu deney HTTP'de açıkça Lax/Strict çerezleri içindir; Secure/None, üçüncü taraf çerez izinleri ve varsayılan-Lax iki dakikalık istisnası sınanmaz.

Kaynaklar: [OWASP synchronizer token](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html#synchronizer-token-pattern), [SameSite uygulaması](https://web.dev/articles/samesite-cookies-explained).
:::

::: tahmin
```python
from http_browser_lab import samesite_report
r=samesite_report()
for x in r['results']:
    print(x['method'],repr(x['cookie']))
```
???
`GET 'lax=L'` ve `POST ''`. Bu gerçek navigasyonların sonucudur; site ayrımını yalnız port değiştirerek göstermiyoruz.
:::

::: gorev CSRF jetonunu aynı oturumda kullan
`guvenli_degistir(lab,cookie,title)` önce GET /csrf'yi verilen cookie ile alsın. Yanıt 200 değilse ValueError; token'ı X-CSRF-Token ile aynı cookie kullanarak POST /change'e JSON `{'title':title}` gönderip tam yanıt sözlüğünü döndürsün. Sunucunun yazma doğrulamasını istemcide taklit etme.
```starter
def guvenli_degistir(lab,cookie,title):
    return {}
```
```test
from http_lab import Lab
with Lab() as lab:
    for user in ('ayse','berk'):
        c=lab.login(user)
        for title in ('a','x'*80,'',' '*2,'x'*81):
            n=lab.snapshot()['revision']; r=guvenli_degistir(lab,c,title)
            accepted=1<=len(title.strip())<=80
            eq(r['status'],200 if accepted else 422,'1..80 siniri')
            eq(lab.snapshot()['revision'],n+int(accepted),'gercek yazma')
        a,b=lab.snapshot()['events'][-2:]
        eq([(a['method'],a['path'],a['user']),(b['method'],b['path'],b['user'])],[('GET','/csrf',user),('POST','/change',user)],'ayni oturum')
    try: guvenli_degistir(lab,None,'x')
    except ValueError: pass
    else: ok(False,'oturumsuz token kullanilmaz')
class Tanik:
    def __init__(self): self.calls=[]
    def request(self,m,p,data=None,cookie=None,headers=None):
        self.calls.append((m,p,data,cookie,headers))
        return {'status':200,'body':{'token':'degisen-token'}} if m=='GET' else {'status':209,'body':'tanik'}
t=Tanik(); eq(guvenli_degistir(t,'sid=s','baslik'),{'status':209,'body':'tanik'},'yaniti koru')
eq(t.calls,[('GET','/csrf',None,'sid=s',None),('POST','/change',{'title':'baslik'},'sid=s',{'X-CSRF-Token':'degisen-token'})],'tokeni ve cookieyi tasi')
```
```solution
def guvenli_degistir(lab,cookie,title):
    r=lab.request('GET','/csrf',cookie=cookie)
    if r['status']!=200:
        raise ValueError('csrf alinamadi')
    return lab.request('POST','/change',{'title':title},cookie=cookie,headers={'X-CSRF-Token':r['body']['token']})
```
```hint
Giriş yapıp cookieyi değiştirme. Çağıranın oturumunu hem GET hem POST'ta taşı.
```
:::

::: gorev Red deneyi gerçekten yazmayı durdurdu mu?
`csrf_redleri(lab, a, b)` iki geçerli farklı oturum cookie'si alır. GET /csrf ile **b** jetonunu oku. Ardından **a** oturumunda sırasıyla eksik jeton, yanlış `yanlis` jetonu ve b'nin jetonuyla title='x' POST /change yap. Üç yanıtın status listesini ve lab.snapshot revision değerinin önce/sonra farkını `(liste,fark)` olarak döndür. Sonucu sabitleme.
```starter
def csrf_redleri(lab,a,b):
    return ([],0)
```
```test
from http_lab import Lab
with Lab() as lab:
    a=lab.login('ayse'); b=lab.login('berk')
    eq(csrf_redleri(lab,a,b),([403,403,403],0),'3 red ve sifir yazma')
    ev=lab.snapshot()['events'][-4:]
    eq([e['user'] for e in ev],['berk','ayse','ayse','ayse'],'oturum degistirme')
    token=lab.request('GET','/csrf',cookie=a)['body']['token']
    lab.reset()
    eq(lab.request('POST','/change',{'title':'x'},cookie=a,headers={'X-CSRF-Token':token})['status'],401,'reset eski oturumu iptal eder')
class Tanik:
    def __init__(self): self.n=7; self.tokens=[]
    def snapshot(self): return {'revision':self.n}
    def request(self,m,p,data=None,cookie=None,headers=None):
        if m=='GET':
            eq(cookie,'B','b tokeni'); return {'status':200,'body':{'token':'B-token'}}
        eq((m,p,data,cookie),('POST','/change',{'title':'x'},'A'),'a oturumunda yazma deneyi')
        self.tokens.append((headers or {}).get('X-CSRF-Token'))
        self.n+=1
        return {'status':410+len(self.tokens)}
t=Tanik(); eq(csrf_redleri(t,'A','B'),([411,412,413],3),'olculen durum/fark')
eq(t.tokens,[None,'yanlis','B-token'],'eksik/yanlis/baska oturum')
```
```solution
def csrf_redleri(lab,a,b):
    token=lab.request('GET','/csrf',cookie=b)['body']['token']
    once=lab.snapshot()['revision']
    durumlar=[]
    for headers in ({},{'X-CSRF-Token':'yanlis'},{'X-CSRF-Token':token}):
        r=lab.request('POST','/change',{'title':'x'},cookie=a,headers=headers)
        durumlar.append(r['status'])
    return durumlar, lab.snapshot()['revision']-once
```
```hint
Sunucudaki revision sayacı kabul edilen yazmada artar. 403 görmek yetmez; önce/sonra farkını ölç.
```
:::
