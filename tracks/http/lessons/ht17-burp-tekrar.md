---
id: ht17
title: Burp — Proxy, History ve Repeater
summary: Kalıcı yerel laboratuvarda oturumlu isteği yakala, tek değişkeni değiştir ve yanıtı yeniden üret.
---

::: anlat Bir isteğin kanıt zinciri
HT14–HT15'te istemciyi yazdın. Şimdi isteği bir tarayıcıdan alıp aynı oturumla tekrar göndereceksin. **Burp gerçek uygulamadır; Pafta onu taklit etmez.** Kalıcı laboratuvarı ayrı terminalde başlat:

```text
python sandbox/http_lab.py --port 8765
```

Terminal açıkken laboratuvar açık kalır. Yazdırılan `url` adresini kullan; kontrol anahtarı her başlatmada değişir. `Ctrl+C` kapatır. `POST /_control/reset` isteğine terminaldeki `X-Lab-Control` değerini eklemek kayıtları ve oturumları sıfırlar. Anahtarsız reset 403 döner.

Kali'deki Burp'u kullanıyorsan sunucuyu **aynı Kali dağıtımında** çalıştır: dosyayı `/tmp/pafta-http-lab.py` konumuna kopyalayıp `python3 /tmp/pafta-http-lab.py --port 8765` çalıştır. Böylece her iki uygulama aynı loopback adresini kullanır. Windows'taki ayrı bir sunucunun Kali'den erişilebilir olduğunu varsayma. Bu dersin sunucusu standart kütüphaneyle çalışır; paket kurulumu gerekmez.

1. Burp'ta geçici proje aç. Proxy → Intercept altında **Open browser** seç. Intercept'i kapat; HTTP history istekleri toplamaya devam eder.
2. Adresi aç, `ayse / pafta-demo` ile oturum aç; **1 numaralı kaydı oku** düğmesine bas.
3. HTTP history'de `GET /items/1` isteğini bul. İstek ve yanıtı birlikte incele: Cookie var mı, yanıt hangi sahibin kaydı?
4. **Send to Repeater** seç. Önce hiç değiştirmeden Send: 200 ve aynı kayıt gelmeli.
5. Yalnız istek hedefindeki `1` değerini `2` yap. Cookie'yi değiştirme. Bu laboratuvarda 403 beklenir. Eski isteğe dönünce yeniden 200 almalısın.
6. Cookie'yi ayrı deneyde kaldır: 401. Başka bir oturum açıp onun Cookie'sini değiştirmek iki değişken olur; ayrı sekmede tut.

History'deki zaman, yöntem, hedef, oturumun **maskelenmiş** kimliği ve yanıtı raporuna yaz. Burp'un sekmelerini aşağıdaki otomatik testler göremez; bunlar isteği değiştirme ve yerel tekrarın davranışını ölçer. GUI adımlarını bu listeyle ayrıca tamamla.

Kaynaklar: [Burp tarayıcısı](https://portswigger.net/burp/documentation/desktop/tools/burps-browser), [Repeater](https://portswigger.net/burp/documentation/desktop/tools/repeater).
:::

::: tahmin
```python
from http_lab import Lab
with Lab() as lab:
    c = lab.login('ayse')
    for cookie, no in ((c, 1), (c, 2), (None, 1)):
        print(lab.request('GET', f'/items/{no}', cookie=cookie)['status'])
```
???
`200`, `403`, `401`. Kimlik doğrulama ve kayda erişim ayrı kararlardır; geçerli oturum başka kullanıcının kaydını açmaz.
:::

::: gorev Tek değişken: yalnız istek hedefi
`hedef_degistir(ham, hedef)` bayt döndürsün. Laboratuvarın dar biçimi: `GET <hedef> HTTP/1.1\r\n` ve ardından başlıklar/boş satır. İlk satırı değiştir, kalan baytları aynen koru. Yeni hedef `/` ile başlamalı, `//` ile başlamamalı; ASCII olmalı, boşluk/kontrol karakteri veya `#` içermemeli. Yanlış biçim, gövde, başka yöntem ve boş başlık sonlandırması için `ValueError` üret. Tam HTTP ayrıştırıcısı değil; HT14'ün genel istemcisinden daha dar bir Repeater yardımcısıdır.
```starter
def hedef_degistir(ham, hedef):
    return ham
```
```test
def hata(ham, hedef):
    try:
        hedef_degistir(ham, hedef)
    except ValueError:
        return
    ok(False, 'gecersiz istek/hedef reddedilmeli')
tail=b'Host: pafta.test\r\nCookie: sid=items/1\r\nUser-Agent: Pafta Lab 1\r\n\r\n'
for eski in ('/items/1','/items/2?x=1'):
    ham=f'GET {eski} HTTP/1.1\r\n'.encode()+tail
    for yeni in ('/items/2','/','/items/1?q=%20'):
        eq(hedef_degistir(ham,yeni),f'GET {yeni} HTTP/1.1\r\n'.encode()+tail,'yalniz hedef')
for hedef in ('','//evil.test/x','/a b','/a\tb','/a\nb','/a\x7fb','/a#b','/a\u011f','https://evil.test/'):
    hata(b'GET / HTTP/1.1\r\n'+tail,hedef)
for ham in (b'POST / HTTP/1.1\r\n'+tail,b'GET / HTTP/1.0\r\n'+tail,b'GET / HTTP/1.1\n'+tail,b'GET / HTTP/1.1\r\nHost: x\r\n',b'GET / HTTP/1.1\r\n'+tail+b'x'):
    hata(ham,'/items/2')
```
```solution
def hedef_degistir(ham, hedef):
    if not isinstance(ham,bytes) or not isinstance(hedef,str):
        raise ValueError('bayt istek ve metin hedef gerekli')
    if not hedef.startswith('/') or hedef.startswith('//') or '#' in hedef or any(ord(c)<=32 or ord(c)>=127 for c in hedef):
        raise ValueError('origin-form ASCII hedef gerekli')
    ilk, ayirac, kalan = ham.partition(b'\r\n')
    p = ilk.split(b' ')
    if not ayirac or len(p)!=3 or p[0]!=b'GET' or p[2]!=b'HTTP/1.1' or not ham.endswith(b'\r\n\r\n') or b'\r\n\r\n' in ham[:-4]:
        raise ValueError('govdesiz tek GET istegi gerekli')
    return b'GET '+hedef.encode('ascii')+b' HTTP/1.1\r\n'+kalan
```
```hint
İlk CRLF'ten sonrasına dokunma. Cookie içindeki benzer metni replace ile değiştirme.
```
:::

::: gorev Aynı oturumla üçlü tekrar
`tekrar(lab, cookie, kendi, baska)` aynı oturumla sırayla kendi kaydını, diğer kaydı ve yeniden kendi kaydını gerçek HTTP üzerinden okusun. `(durum, govde)` çiftlerinin listesini döndür. Sonuçları sabit yazma; lab.request yanıtlarının `status` ve `body` alanlarını kullan. Kayıt numaraları parametredir. Bu deney yazma yapmaz.
```starter
def tekrar(lab, cookie, kendi, baska):
    return []
```
```test
from http_lab import Lab
for user,own,other in (('ayse',1,2),('berk',2,1)):
    with Lab() as lab:
        cookie=lab.login(user); once=lab.snapshot()['items']
        sonuc=tekrar(lab,cookie,own,other)
        eq([x[0] for x in sonuc],[200,403,200],'kabul/red/yeniden kabul')
        eq(sonuc[0][1],once[own],'gercek kayit govdesi')
        eq(sonuc[1][1],{'error':'owner'},'red govdesi')
        eq(sonuc[2][1],once[own],'kontrol deneyi')
        ev=lab.snapshot()['events'][1:]
        eq([(e['method'],e['path'],e['user']) for e in ev],[('GET',f'/items/{n}',user) for n in (own,other,own)],'ayni oturum ve tek hedef degisikligi')
        eq(lab.snapshot()['items'],once,'durum degismedi')
class Tanik:
    def __init__(self): self.calls=[]
    def request(self,m,p,cookie=None):
        self.calls.append((m,p,cookie)); return {'status':418,'body':p}
t=Tanik()
eq(tekrar(t,'sid=abc',7,8),[(418,'/items/7'),(418,'/items/8'),(418,'/items/7')],'yaniti sabitleme')
eq(t.calls,[('GET','/items/7','sid=abc'),('GET','/items/8','sid=abc'),('GET','/items/7','sid=abc')],'parametreleri tasi')
```
```solution
def tekrar(lab, cookie, kendi, baska):
    sonuc=[]
    for no in (kendi,baska,kendi):
        r=lab.request('GET',f'/items/{no}',cookie=cookie)
        sonuc.append((r['status'],r['body']))
    return sonuc
```
```hint
Oturumu yeniden açma; aynı Cookie ile üç çağrı yap. İkinci yanıtın gövdesini de koru.
```
:::
