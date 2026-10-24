---
id: ht22
title: URL Ayrıştırma, SSRF Sınırı ve Yönlendirmeler
summary: Her yönlendirme hedefini bağlantıdan önce doğrula; 301/302 ve 307 yöntem farkını gerçek HTTP ile ölç.
timeout: 60
---

::: anlat İzin verilen ilk URL zincirin tamamına izin vermez
`RedirectLab` iki **kendi oluşturduğu** loopback hizmeti açar. public ve internal adları laboratuvar rolüdür; ikisi de senin geçici sunucundur. Gerçek iç ağ, bulut metadata veya internet erişimi yapılmaz. `wire` yalnız bu iki portu taşır. Öğrencinin izin politikası daha dardır: yalnız public origin. `/to-internal` internal hizmetin `/secret` adresine 302 verir; hedefe bağlanmadan reddetmelisin.

`/r301`, `/r302`, `/r307` → /echo; `/chain1` → /echo, `/chain2` → /chain1, `/chain3` → /chain2; `/loop` kendisine yönlenir. Bu istemci 301/302'de POST'u GET'e çeviren tarayıcı uyumlu politikayı **açıkça seçer**, gövdeyi atar. 307'de yöntem ve gövde korunur. 301/302'nin her istemcide mutlaka yöntem değiştireceğini varsayma. 303/308 bu görev sözleşmesinde desteklenmez ve hata verir.

DNS rebinding, IP sınıfı listeleri, IDNA ve proxy politikası bu dar loopback deneyiyle çözülmez. Üretimde doğrulanan adresle gerçekten bağlanılan adresin aynı olmasını da güvenceye almak gerekir. urllib.parse bir tarayıcı URL doğrulayıcısı değildir; belirsiz girdileri reddetmek, farklı ayrıştırıcıların aynı şeyi anladığını varsaymaktan daha ölçülebilirdir.

Kaynaklar: [OWASP SSRF savunması](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html), [WHATWG host ayrıştırma](https://url.spec.whatwg.org/#host-parsing), [RFC 9110 yönlendirme](https://www.rfc-editor.org/rfc/rfc9110.html#section-15.4).
:::

::: tahmin
```python
from urllib.parse import urlsplit
from http_browser_lab import browser_run
urls=['http://127.1/x', 'http://good.test\\@other.test/x']
r=browser_run({'mode':'url','urls':urls})
for u,v in zip(urls,r['results']):
    print(urlsplit(u).hostname,v['host'])
```
???
`127.1 127.0.0.1` ve `other.test good.test`. Sağdaki gerçek Chromium URL API'sinden gelir; örnek adreslere bağlantı yapılmaz. URL içindeki kullanıcı bilgisi, ters eğik çizgi ve sayısal host biçimlerini basit alt-dize kontrolüyle izinli sayma.
:::

::: gorev Dar ve açık bir URL izin politikası
`izinli(url, origin)` bool döndürsün. Bu laboratuvarda origin güvenilir `http://127.0.0.1:PORT` biçimindedir. url ASCII olmalı; boşluk/kontrol, DEL, ters eğik çizgi ve fragment içermemeli; userinfo olmamalı; şema http, hostname tam 127.0.0.1 ve port origin ile eşit olmalı. Port açıkça 1..65535 olmalı. Ayrıştırma hatasını False yap. `/echo?x=%20` geçerlidir; path'teki kodlanmış boşluk host kontrolünü değiştirmez. Bu genel SSRF filtresi değildir.
```starter
def izinli(url, origin):
    return True
```
```test
for port in (1,65535):
    base=f'http://127.0.0.1:{port}'
    for suffix in ('','/','/echo?x=%20'):
        eq(izinli(base+suffix,base),True,'izinli origin')
    for u in (f'http://127.0.0.1:{port}/#x',f'http://x@127.0.0.1:{port}/',f'http://127.1:{port}/',f'http://2130706433:{port}/',f'http://127.0.0.1.evil.test:{port}/',f'https://127.0.0.1:{port}/',f'http://127.0.0.1:{port}/a b',f'http://127.0.0.1:{port}/a\tb',f'http://127.0.0.1:{port}/a\\b',f'http://127.0.0.1:{port}/\u011f','http://127.0.0.1:0/','http://127.0.0.1:65536/','http://127.0.0.1:/','http://[oops','/echo'):
        eq(izinli(u,base),False,'belirsiz veya farkli hedef')
eq(izinli('http://127.0.0.1:81/','http://127.0.0.1:80'),False,'port origin parcasi')
```
```solution
from urllib.parse import urlsplit
def izinli(url, origin):
    if not isinstance(url,str) or any(ord(c)<=32 or ord(c)>=127 for c in url) or '\\' in url or '#' in url:
        return False
    try:
        u=urlsplit(url); o=urlsplit(origin)
        return u.scheme=='http' and u.hostname=='127.0.0.1' and u.username is None and u.password is None and u.port is not None and 1<=u.port<=65535 and u.port==o.port
    except ValueError:
        return False
```
```hint
Hostname equality ile prefix/contains aynı şey değildir. .port erişimi de ValueError verebilir.
```
:::

::: gorev Her hop'ta doğrula, yöntemi bilinçli taşı
`takip(wire,url,kontrol,method='GET',body=None,max_redirects=3)` her URL için önce kontrol(url) çağırsın; kontrol izin vermezse ValueError yükseltir. Sonra wire(method,url,body) gerçek yanıtını al. 301/302/307'yi takip et; Location eksik/boş veya ASCII boşluk/kontrol içeriyorsa ValueError. Göreli adresi mevcut URL'ye göre çöz. 301/302 POST'u GET ve body=None yapar; 307 korur. Diğer 3xx hata; diğer durumlarda tam yanıtı döndür. max_redirects bool olmayan, sıfır veya pozitif int olmalı; başlangıç isteği hop sayılmaz. Sınırı aşan yeni hedefe istek gönderme.
```starter
def takip(wire,url,kontrol,method='GET',body=None,max_redirects=3):
    return wire(method,url,body)
```
```test
from http_redirect_lab import RedirectLab
from urllib.parse import urlsplit
with RedirectLab() as lab:
    checked=[]
    def guard(u):
        checked.append(u)
        if urlsplit(u).netloc!=urlsplit(lab.base).netloc: raise ValueError('origin')
    for code,expected in ((301,'GET'),(302,'GET'),(307,'POST')):
        sent=[]
        def wire_tanik(method,url,body=None):
            sent.append((method,url,body))
            return lab.wire(method,url,body)
        r=takip(wire_tanik,lab.base+f'/r{code}',guard,'POST',{'x':1})
        eq(r['body'],{'method':expected,'data':{'x':1} if code==307 else None},'yontem/govde gercek echo')
        eq(sent,[('POST',lab.base+f'/r{code}',{'x':1}),(expected,lab.base+'/echo',{'x':1} if code==307 else None)],'GET govdesi gercekten atildi; 307 korundu')
    eq(takip(lab.wire,lab.base+'/chain3',guard,max_redirects=3)['status'],200,'tam uc hop')
    eq(takip(lab.wire,lab.base+'/echo',guard,max_redirects=0)['status'],200,'sifir hopta dogrudan istek')
    for path,limit in (('/chain1',0),('/chain3',2),('/loop',3),('/to-internal',3)):
        before=len(lab.public.snapshot()['events'])
        try: takip(lab.wire,lab.base+path,guard,max_redirects=limit)
        except ValueError: pass
        else: ok(False,'sinir/izin reddi')
        if path=='/chain1': eq(len(lab.public.snapshot()['events'])-before,1,'yeni hedefe gitme')
    eq(lab.internal.snapshot()['events'],[],'ic hedefe hic baglanilmadi')
    ok(lab.base+'/echo' in checked,'son hedef de kontrol edildi')
for limit in (-1,True,1.5):
    try: takip(lambda *a:None,'x',lambda u:None,max_redirects=limit)
    except ValueError: pass
    else: ok(False,'limit tipi')
for response in ({'status':302,'headers':{}},{'status':302,'headers':{'location':''}},{'status':302,'headers':{'location':'/a\tb'}},{'status':303,'headers':{'location':'/x'}},{'status':308,'headers':{'location':'/x'}}):
    try: takip(lambda *a:response,'http://127.0.0.1:1/x',lambda u:None)
    except ValueError: pass
    else: ok(False,'desteksiz/bozuk yonlendirme')
calls=[]
def deny(u): calls.append(u); raise ValueError('deny')
try: takip(lambda *a:ok(False,'guard oncesi ag'),'http://127.0.0.1:1/',deny)
except ValueError: pass
eq(len(calls),1,'ilk URL de dogrulanir')
```
```solution
from urllib.parse import urljoin
def takip(wire,url,kontrol,method='GET',body=None,max_redirects=3):
    if type(max_redirects) is not int or max_redirects<0: raise ValueError('limit')
    hops=0
    while True:
        kontrol(url)
        r=wire(method,url,body)
        status=r['status']
        if not 300<=status<=399: return r
        if status not in (301,302,307) or hops>=max_redirects: raise ValueError('yonlendirme siniri/turu')
        location=r['headers'].get('location')
        if not location or any(ord(c)<=32 or ord(c)==127 for c in location): raise ValueError('Location')
        url=urljoin(url,location)
        if status in (301,302) and method=='POST': method,body='GET',None
        hops+=1
```
```hint
Yalnız ilk URL'yi doğrulayan istemci /to-internal sınırını kaçırır. Kontrolü while döngüsünün başına koy.
```
:::
