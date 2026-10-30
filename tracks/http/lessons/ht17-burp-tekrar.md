---
id: ht17
title: Burp — Proxy, History ve Repeater
summary: Kalıcı yerel laboratuvarda oturumlu isteği yakala, tek değişkeni değiştir ve yanıtı yeniden üret.
---

::: anlat Bir isteğin kanıt zinciri
HT14–HT15'te istemciyi yazdın. Şimdi isteği bir tarayıcıdan alıp aynı oturumla tekrar göndereceksin. **Burp gerçek uygulamadır; Pafta onu taklit etmez.** Kalıcı laboratuvarı ayrı terminalde başlat:

```text
python sandbox/http_lab.py --port 8769
```

Terminal açıkken laboratuvar açık kalır. Yazdırılan `url` adresini kullan; kontrol anahtarı her başlatmada değişir. `Ctrl+C` kapatır. `POST /_control/reset` isteğine terminaldeki `X-Lab-Control` değerini eklemek kayıtları ve oturumları sıfırlar. Anahtarsız reset 403 döner.

Kali'deki Burp'u kullanıyorsan sunucuyu **aynı Kali dağıtımında** çalıştır: dosyayı `/tmp/pafta-http-lab.py` konumuna kopyalayıp `python3 /tmp/pafta-http-lab.py --port 8769` çalıştır. Böylece her iki uygulama aynı loopback adresini kullanır. Windows'taki ayrı bir sunucunun Kali'den erişilebilir olduğunu varsayma. Bu dersin sunucusu standart kütüphaneyle çalışır; paket kurulumu gerekmez.

1. Burp'ta geçici proje aç. Proxy → Intercept altında **Open browser** seç. Intercept'i kapat; HTTP history istekleri toplamaya devam eder.
2. Adresi aç, `ayse / pafta-demo` ile oturum aç; **1 numaralı kaydı oku** düğmesine bas.
3. HTTP history'de `GET /items/1` isteğini bul. İstek ve yanıtı birlikte incele: Cookie var mı, yanıt hangi sahibin kaydı?
4. **Send to Repeater** seç. Önce hiç değiştirmeden Send: 200 ve aynı kayıt gelmeli.
5. Yalnız istek hedefindeki `1` değerini `2` yap. Cookie'yi değiştirme. Bu laboratuvarda 403 beklenir. Eski isteğe dönünce yeniden 200 almalısın.
6. Cookie'yi ayrı deneyde kaldır: 401. Başka bir oturum açıp onun Cookie'sini değiştirmek iki değişken olur; ayrı sekmede tut.

History'deki zaman, yöntem, hedef, oturumun **maskelenmiş** kimliği ve yanıtı raporuna yaz. History satırlarını **Save items**, Repeater yanıtını **Save item** ile XML'e kaydet; **Base64-encode requests and responses** açık olsun. Son görev gerçek Burp dışa aktarımını okur. Otomatik başarı, GUI adımlarını her öğrencinin yaptığına dair kanıt değildir; bu listeyi kendi kaydınla ayrıca tamamla.

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
raises(ValueError,hedef_degistir,None,'/',msg='istek tek başına yanlış tür')
raises(ValueError,hedef_degistir,b'GET / HTTP/1.1\r\nHost: x\r\n\r\n',None,msg='hedef tek başına yanlış tür')
tail=b'Host: pafta.test\r\nCookie: sid=items/1\r\nUser-Agent: Pafta Lab 1\r\n\r\n'
for eski in ('/items/1','/items/2?x=1'):
    ham=f'GET {eski} HTTP/1.1\r\n'.encode()+tail
    for yeni in ('/items/2','/','/items/1?q=%20','/!','/~'):
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


::: anlat Burp çıktısını baytları koruyarak oku
Tezgahtaki `burp/history.xml` ve `burp/repeater.xml`, **Burp Community 2026.8'in kendi XML çıktılarıdır**. History'ye dört yerel istek Python istemcisiyle gerçek Burp Proxy üzerinden gönderildi: 200/403/200/401. İlk satır GUI'de Repeater'a taşınıp Send ile yeniden gönderildi, 200 yanıtı ayrıca dışa aktarıldı. Bu kayıt tarayıcıyla oluşturulmuş gibi sunulmaz. Tekrar üretim ve hash'ler `tracks/http/fixtures/ht17_burp` içindedir. Kayıttaki oturum yalnız kapanabilen yerel ders laboratuvarına aittir; kendi gerçek oturum çerezini rapora basma.

Burp XML'i istek ve yanıtı aynı `item` altında tutar; yöntem/hedef/status gibi metadata ayrıca bulunur. Base64 seçeneği ikili gövdeyi ve CRLF'yi XML metin normalleştirmesinden korur. Örnek XML'in dahili DTD'sinde ELEMENT/ATTLIST bildirimleri vardır; bütün DOCTYPE bildirimlerini reddetmek gerçek örneği de reddeder. Bu küçük okuyucu ENTITY bildirimlerini ve SYSTEM/PUBLIC dış kaynak bildirimlerini reddeder; dosya, URL veya komut açmaz. Genel amaçlı güvenli XML ürününün yerini almaz.

Destek sınırı: UTF-8 XML, Base64 işaretli HTTP/1.0 veya HTTP/1.1 çiftleri ve en fazla 65536 bayt. HTTP/2, Base64 kapalı kayıt, bozuk çift ve daha büyük dosya açık hatadır; desteklenmiş gibi sessiz atlanmaz. Metadata ile ham ilk satırın uyumu kontrol edilir; tam HTTP çerçeveleme, chunked ayrıştırma veya dışa aktarımın yazarlığını doğrulama bu görevin konusu değildir. `burpVersion` alanı ve zaman metni kaynağın kriptografik kanıtı değildir.

Kaynak: [PortSwigger message editor — Save item](https://portswigger.net/burp/documentation/desktop/tools/message-editor), [Save items](https://portswigger.net/burp/documentation/desktop/tools/context-menu).
:::

::: gorev Gerçek Burp XML çiftlerini doğrula
`burp_oku(veri)` yaz. Girdi bytes ve uzunluğu 1..65536 olmalı; UTF-8/XML hatası ValueError olsun. ENTITY, SYSTEM/PUBLIC dış kaynak bildirimi reddedilsin. Kök `items`, dolu `burpVersion`; bütün doğrudan çocuklar `item` olmalı. Her item tam birer url/method/path/status/request/response taşımalı. İlk üçü boş olmayan metin; status üç ASCII rakam ve 100..599. request/response `base64="true"` taşımalı; Base64 içindeki satır/beyaz boşlukları kaldırıp strict çöz. Her ikisinde CRLF CRLF ayracı olmalı. Request ilk satırı tam `method path HTTP/1.0` veya `HTTP/1.1`; response ilk satırı `HTTP/1.0` veya `HTTP/1.1`, üç rakamlı durum ve ardından boşluk veya CRLF taşımalı. Ham durum XML status ile aynı olmalı. Her uyumsuzluk ValueError; kısmi başarı döndürme.

XML sırasıyla `{'url':str,'method':str,'path':str,'status':int,'request':bytes,'response':bytes}` sözlükleri döndür; boş items için `[]`. Ham HTTP baytlarını, tekrarlanan kayıtları ve sıralamayı koru. Metadata'daki diğer alanları bu dar rapora alma.

```starter
def burp_oku(veri):
    return []
```

```test
from pathlib import Path
import base64,copy,xml.etree.ElementTree as ET
need('burp_oku')
ham=Path('burp/history.xml').read_bytes()
r=burp_oku(ham)
eq([x['status'] for x in r],[200,403,200,401],'gerçek Proxy sırası ve tekrarlar')
eq([x['path'] for x in r],['/items/1','/items/2','/items/1','/items/1'],'hedef değişikliği metadata ile birlikte')
eq([x['method'] for x in r],['GET']*4,'yöntemler korunur')
eq([x['url'] for x in r],['http://127.0.0.1:18769'+x['path'] for x in r],'URL metni korunur')
root=ET.fromstring(ham)
for x,item in zip(r,root):
    for alan in ('request','response'):
        eq(x[alan],base64.b64decode(item.find(alan).text,validate=True),'ham baytlar birebir: '+alan)
repeater=burp_oku(Path('burp/repeater.xml').read_bytes())
eq(len(repeater),1,'gerçek Repeater dışa aktarımı')
eq(repeater[0]['request'],r[0]['request'],'aynı istek yeniden gönderilmiş')
eq(repeater[0]['status'],200,'gerçek Repeater yanıtı')
eq(repeater[0]['response'].split(b'\r\n\r\n',1)[1],r[0]['response'].split(b'\r\n\r\n',1)[1],'kontrol deneyinde aynı kayıt gövdesi')
def xml(x): return ET.tostring(x,encoding='utf-8')
eq(burp_oku(b'<items burpVersion="future"/>'),[],'boş ve farklı ürün sürümü')
x=copy.deepcopy(root);x[:]=list(reversed(list(x)))
eq([z['status'] for z in burp_oku(xml(x))],[401,200,403,200],'kayıtlar sıralanıp tekilleştirilmez')
x=copy.deepcopy(root)
binary=b'HTTP/1.1 200 OK\r\nX-Test: a\r\n\r\n\x00\xff\xc3\xa7'
x[0].find('response').text=base64.b64encode(binary).decode()
eq(burp_oku(xml(x))[0]['response'],binary,'ikili gövde metne dönüştürülmez')
x[0].find('response').text='\n '+x[0].find('response').text[:12]+'\n'+x[0].find('response').text[12:]+'\t'
eq(burp_oku(xml(x))[0]['response'],binary,'Base64 satırları açılır')
for n in (100,599):
    x=copy.deepcopy(root);x[0].find('status').text=str(n)
    x[0].find('response').text=base64.b64encode(f'HTTP/1.1 {n} Test\r\n\r\n'.encode()).decode()
    eq(burp_oku(xml(x))[0]['status'],n,'iki geçerli durum sınırı')
# Boyut üst ucunu gerçek, geçerli XML ile ölç; bir bayt üstü ayrı reddedilir.
small=b'<items burpVersion="x"></items>'
limit=small[:-8]+b' '*(65536-len(small))+small[-8:]
eq(len(limit),65536,'tam boyut fixture')
eq(burp_oku(limit),[],'65536 dahil')
raises(ValueError,burp_oku,limit+b' ',msg='65537 hariç')
for bad in (b'',None,'<items/>',b'\xff',b'<items',b'<wrong burpVersion="x"/>',b'<items/>',b'<items burpVersion="x"><other/></items>',b'<!DOCTYPE items [<!ENTITY x "y">]><items burpVersion="x"/>',b'<!DOCTYPE items SYSTEM "file:///does-not-exist"><items burpVersion="x"/>'):
    raises(ValueError,burp_oku,bad,msg='bozuk veya destek dışı XML')
for field in ('url','method','path','status','request','response'):
    x=copy.deepcopy(root);x[0].remove(x[0].find(field))
    raises(ValueError,burp_oku,xml(x),msg='eksik alan: '+field)
    x=copy.deepcopy(root);x[0].append(copy.deepcopy(x[0].find(field)))
    raises(ValueError,burp_oku,xml(x),msg='çift alan belirsiz: '+field)
for field in ('url','method','path'):
    x=copy.deepcopy(root);x[0].find(field).text=''
    raises(ValueError,burp_oku,xml(x),msg='boş alan: '+field)
for n in ('99','600','2xx','0200','２００'):
    x=copy.deepcopy(root);x[0].find('status').text=n
    x[0].find('response').text=base64.b64encode(('HTTP/1.1 '+n+' Test\r\n\r\n').encode('utf-8')).decode()
    raises(ValueError,burp_oku,xml(x),msg='geçersiz durum '+n)
for field in ('request','response'):
    for kind in ('flag','missing-flag','alphabet','trailing','delimiter','version'):
        x=copy.deepcopy(root);node=x[0].find(field)
        if kind=='flag':node.set('base64','false')
        elif kind=='missing-flag':node.attrib.clear()
        elif kind=='alphabet':node.text='!!!'
        elif kind=='trailing':node.text+='!'
        else:
            data=base64.b64decode(node.text)
            data=data.replace(b'\r\n',b'\n') if kind=='delimiter' else data.replace(b'HTTP/1.1',b'HTTP/2')
            node.text=base64.b64encode(data).decode()
        raises(ValueError,burp_oku,xml(x),msg='geçersiz '+field+': '+kind)
for field,value in (('method','POST'),('path','/items/999'),('status','201')):
    x=copy.deepcopy(root);x[0].find(field).text=value
    raises(ValueError,burp_oku,xml(x),msg='metadata ham ilk satırla uyuşmaz: '+field)
```

```solution
import base64,binascii,re,xml.etree.ElementTree as ET

def burp_oku(veri):
    if not isinstance(veri,bytes) or not 1<=len(veri)<=65536:
        raise ValueError('1..65536 bayt XML gerekli')
    try:
        text=veri.decode('utf-8')
        if re.search(r"""<!ENTITY|\b(?:SYSTEM|PUBLIC)\s+["']""",text,re.I):
            raise ValueError('Dış kaynak veya entity desteklenmiyor')
        root=ET.fromstring(text)
    except (UnicodeError,ET.ParseError) as e:
        raise ValueError('UTF-8 XML gerekli') from e
    if root.tag!='items' or not root.get('burpVersion'):
        raise ValueError('Burp items kökü gerekli')
    result=[]
    for item in root:
        if item.tag!='item':raise ValueError('Bilinmeyen kayıt')
        fields={}
        for name in ('url','method','path','status','request','response'):
            nodes=item.findall(name)
            if len(nodes)!=1:raise ValueError('Eksik veya tekrarlı alan')
            fields[name]=nodes[0]
        row={name:fields[name].text or '' for name in ('url','method','path')}
        if not all(row.values()):raise ValueError('Boş metadata')
        status=fields['status'].text or ''
        if not re.fullmatch(r'[0-9]{3}',status) or not 100<=int(status)<=599:
            raise ValueError('Geçersiz durum')
        row['status']=int(status)
        for name in ('request','response'):
            node=fields[name]
            if node.get('base64')!='true':raise ValueError('Base64 açık olmalı')
            try:
                row[name]=base64.b64decode(''.join((node.text or '').split()),validate=True)
            except (ValueError,binascii.Error) as e:
                raise ValueError('Bozuk Base64') from e
            if b'\r\n\r\n' not in row[name]:raise ValueError('CRLF ayraç yok')
        try:
            prefix=(row['method']+' '+row['path']).encode('ascii')
        except UnicodeError as e:raise ValueError('ASCII ilk satır gerekli') from e
        if row['request'].split(b'\r\n',1)[0] not in (prefix+b' HTTP/1.0',prefix+b' HTTP/1.1'):
            raise ValueError('İstek metadata uyumsuz')
        match=re.match(rb'HTTP/1\.[01] ([0-9]{3})(?: |\r\n)',row['response'])
        if match is None or int(match.group(1))!=row['status']:
            raise ValueError('Yanıt metadata uyumsuz')
        result.append(row)
    return result

from pathlib import Path
print([r['status'] for r in burp_oku(Path('burp/history.xml').read_bytes())])
```

```hint
Burp'ün kendi DTD'sini ENTITY/dış kaynak tanımından ayır. XML'de tekrar eden alanı find ile sessiz seçme; findall sayısını ölç. Base64'ü strict çöz, ham HTTP'yi metne dönüştürme.
```

```setup
import sys
from pathlib import Path
sys.path.insert(0,str(Path(sys.modules['__main__'].__file__).resolve().parent))
from burp_export_lab import hazirla
hazirla()
```
:::
