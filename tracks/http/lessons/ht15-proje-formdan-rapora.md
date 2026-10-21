---
id: ht15
title: Proje · Formdan Kayda
summary: HTML form kaynağından gönderim planı çıkar, değişen gizli alanları koru, URL-encoded POST ve 303 sonrası JSON kaydıyla akışı doğrula.
---

::: anlat Ekran görüntüsü yerine form sözleşmesini oku
Bu proje HTTP ile HTML okumayı birleştirir: form sayfasını al, `action` ve `method` bilgilerini oku, gönderilecek sabit alanları çıkar, kullanıcı verisini kodla ve oluşturulan kaydı doğrula. Gizli `form_kodu` her sayfada aynı olmak zorunda değildir. Kaynağı okumadan bir kez gördüğün değeri sabitlemek akışı kırar.

Görevlerde sayfanın **ilk formu** seçilir. Etkin `hidden` input ve `readonly` metin inputu değeri taşır; `disabled` input gönderilmez. Boolean HTML niteliğinde varlık önemlidir: `disabled="false"` yine disabled demektir. Aynı adlı iki alanı sözlükle ezmek yerine sıralı `(ad, değer)` çiftleri kullan. Checkbox, textarea, dosya, buton ve kullanıcı tarafından doldurulan normal inputlar bu dar planın sabit alanları değildir. Son iki çifti istemci `baslik` ve `oncelik` olarak ekler.

Bu, tarayıcının bütün form algoritması değildir. Kaynak düzgün kapanan, iç içe form içermeyen basit HTML'dir. Dışarıdan `form=` ile ilişkilendirme, fieldset/optgroup devre dışılığı, `<base>`, JavaScript ve dosya yükleme yoktur. `HTMLParser` bir DOM veya tarayıcı doğrulayıcısı değildir. Kaynaklar: [WHATWG form giriş listesi](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#constructing-the-entry-list), [Python HTMLParser](https://docs.python.org/3/library/html.parser.html).
:::

::: anlat İki ayrı kodlama, üç HTTP adımı
HTML içindeki `&amp;` ayrıştırılınca `&` olur. Bu değer form gövdesine taşınırken yeniden `application/x-www-form-urlencoded` kodlaması ister: literal `&`, `=`, `+` ayraç olmamalıdır. `urlencode` sıralı çiftleri UTF-8 ile yüzde kodlar; çıktı ASCII baytlarıdır. `Content-Length` gerekiyorsa bu son baytların uzunluğu alınır. Kaynak: [URL-encoded serileştirme](https://url.spec.whatwg.org/#application/x-www-form-urlencoded).

Akış `GET form → POST action → 303 Location → GET kayıt` biçimindedir. 303 sonrasında form gövdesi tekrar gönderilmez. Başarı yalnız bir yönlendirme sayısı değildir: son yanıt 200, MIME türü JSON, gövde doğru başlık/öncelik ve pozitif kayıt kimliği taşımalıdır. HTML ve JSON MIME türlerinin parametrelerini medya türünden ayıracağız. Kaynak: [RFC 9110, 303](https://www.rfc-editor.org/rfc/rfc9110.html#section-15.4.4).

Testler hem yerel tezgâhla hem değişken cevap veren `istek` fonksiyonuyla çalışır. İkinci yöntem başlık, gövde, sıra ve hata davranışını görünür kılar. Aynı origin kontrolü bu projenin sınırıdır; tam çerezli tarayıcı veya genel yönlendirme istemcisi yazmıyoruz. Varsayılan taşıma yalnız yerel tezgâha gider; TLS ve internette başka sunucular bu proje kapsamında değildir.
:::

::: tahmin
HTML varlık kodlaması ile form kodlaması aynı mı? Çiftler korunursa iki değer nasıl görünür?

```python
from html.parser import HTMLParser
from urllib.parse import urlencode, parse_qsl

class Oku(HTMLParser):
    def __init__(self):
        super().__init__()
        self.alanlar = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "input" and a.get("name") and "disabled" not in a:
            self.alanlar.append((a["name"], a.get("value", "")))

p = Oku()
p.feed('<input name="kod" value="A&amp;B"><input name="kod" value="x+y"><input disabled="false" name="yok" value="z">')
govde = urlencode(p.alanlar).encode("ascii")
print(govde.decode("ascii"))
print(parse_qsl(govde.decode("ascii")))
```

???

İlk satır `kod=A%26B&kod=x%2By`, ikinci satır `[('kod', 'A&B'), ('kod', 'x+y')]` olur. Aynı adlı iki çift kaybolmaz; literal artı `%2B` olur. `disabled="false"` niteliği hâlâ vardır ve alan dışlanır.
:::

::: gorev HTML'den dar gönderim planı çıkar
`form_plani(kaynak, sayfa_url)` şu sözlüğü döndürsün:

- `url`: ilk formun action'ı sayfa URL'sine göre çözülmüş, fragment çıkarılmış adres; eksik/boş action aynı sayfadır.
- `sabitler`: kaynak sırasıyla, boş olmayan `name` taşıyan, disabled olmayan `type=hidden` veya `type=text` (varsayılan text) ve readonly input çiftleri. Eksik value boş metindir. Yinelenen adlar korunur. `baslik`/`oncelik` sabit alan adı olamaz.
- `oncelikler`: ilk formdaki `name=oncelik` olan tek etkin select'in, açık value'su dolu ve disabled olmayan option değerleri; sırayla ve tekrarsız.
- `varsayilan`: etkin selected option; yoksa ilk etkin option. Birden çok etkin selected geçersizdir.

Form method'u büyük/küçük harf duyarsız `post`, enctype eksik veya `application/x-www-form-urlencoded` olmalı. Sayfa ve action aynı HTTP origin'inde olmalı (scheme, küçük harf host ve etkin port); userinfo, ham ASCII boşluk/kontrol karakterli URL, boş host ve 0 port reddedilsin. URL içindeki boşluk önceden `%20` kodlanmış olmalıdır. Form/select/etkin option yoksa veya belirtilen sözleşme bozulursa `ValueError`. Sonraki formları ve ilk form dışındaki kontrolleri alma. Dar HTML altkümesi anlatımdaki gibidir; seçeneklerde metinden value türetme yoktur.

```starter
def form_plani(kaynak, sayfa_url):
    return {"url": sayfa_url, "sabitler": [], "oncelikler": ["orta"], "varsayilan": "orta"}
```

```test
need('form_plani')
sayfa='http://pafta.test:8080/form/yeni?eski=1'
def html(kod='A&amp;B', action='../kaydet?x=1&amp;y=2#son', method='POST'):
    return f'''<input type="hidden" name="dis" value="alma"><form action="{action}" method="{method}">
<input type="hidden" name="kod" value="{kod}"><input readonly name="kaynak" value="web">
<input type="hidden" disabled="false" name="gizli" value="alma"><input readonly name="kod" value="x+y">
<input type="hidden" disabled name="kapali" value="alma"><input readonly disabled="" name="kapali_salt" value="alma">
<input name="normal" value="alma"><input type="checkbox" checked name="secim" value="alma">
<input type="hidden" value="adsız"><input type="hidden" name="bos">
<select name="oncelik"><option disabled value="kapali" selected>Kapalı</option><option value="düşük">D</option><option value="orta" selected>O</option><option value="yüksek">Y</option></select>
</form><form method="post"><input type="hidden" name="sonraki" value="alma"></form>'''
eq(form_plani(html(),sayfa),{'url':'http://pafta.test:8080/kaydet?x=1&y=2','sabitler':[('kod','A&B'),('kaynak','web'),('kod','x+y'),('bos','')],'oncelikler':['düşük','orta','yüksek'],'varsayilan':'orta'},'sıra, nitelikler ve göreli action')
for kod in ('başka','0','x&amp;y=1+2','Türkçe'):
    eq(form_plani(html(kod),sayfa)['sabitler'][0],('kod',kod.replace('&amp;','&')),'gizli değer kaynaktan')
eq(form_plani(html(action=''),sayfa)['url'],sayfa,'boş action aynı sayfa')
eq(form_plani(html(action='http://PAFTA.test:8080/x'),sayfa)['url'],'http://PAFTA.test:8080/x','host origin karşılaştırması harf duyarsız')
duz='<FORM METHOD="post"><INPUT TYPE="HIDDEN" NAME="k" VALUE="v"/><SELECT NAME="oncelik"><OPTION VALUE="a">A</OPTION><OPTION VALUE="b">B</OPTION></SELECT></FORM>'
eq(form_plani(duz,'http://pafta.test:80/a')['varsayilan'],'a','selected yoksa ilk')
eq(form_plani(html(action='http://pafta.test/kaydet'),'http://pafta.test:80/form')['url'],'http://pafta.test/kaydet','örtük port80 aynı origin')
for port in (1,65535):
    url=f'http://pafta.test:{port}/form/yeni'
    eq(form_plani(html(action='../kaydet'),url)['url'],f'http://pafta.test:{port}/kaydet','portun iki geçerli ucu')
iki_select=html().replace('</select>','</select><select name="oncelik"><option value="ek">Ek</option></select>',1)
for bozuk in ('<p>form yok</p>',html(method='get'),html().replace('method="POST"','method="POST" enctype="multipart/form-data"'),html().replace('name="oncelik"','name="baska"'),html().replace('<select name="oncelik">','<select disabled name="oncelik">'),html().replace('value="yüksek"','value="orta"'),html().replace('value="yüksek"','value="yüksek" selected'),html().replace('name="kod"','name="baslik"'),'<form method="post"><select name="oncelik"><option value="">boş</option></select></form>',iki_select):
    raises(ValueError,form_plani,bozuk,sayfa,msg='geçersiz plan')
for action in ('http://other.test/x','https://pafta.test:8080/x','http://pafta.test:8081/x','http://u:p@pafta.test:8080/x','http://pafta.test:0/x','http://pafta.test:65536/x','/a b','/a\r\nb','/a\tb','/a\x1fb','/a\x7fb'):
    raises(ValueError,form_plani,html(action=action),sayfa,msg='origin veya URL hatası')
for url in ('/goreli','https://pafta.test/x','http://u@pafta.test/x','http://pafta.test:0/x','http://pafta.test:65536/x','http://pafta.test/a b','http://pafta.test/a\r\nb','http://pafta.test/a\x1fb','http://pafta.test/a\x7fb'):
    raises(ValueError,form_plani,html(),url,msg='sayfa URL sözleşmesi')
```

```solution
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit, urldefrag

def _origin(url):
    if not isinstance(url,str) or any(ord(c)<=32 or ord(c)==127 for c in url):
        raise ValueError('URL geçersiz')
    u=urlsplit(url)
    if u.scheme!='http' or not u.hostname or u.username is not None or u.password is not None or u.port==0:
        raise ValueError('yalnız userinfo içermeyen HTTP URL')
    return (u.scheme,u.hostname.lower(),u.port or 80)

class _FormOku(HTMLParser):
    def __init__(self):
        super().__init__()
        self.goruldu=False; self.ic=False; self.form=None
        self.sabitler=[]; self.secim=False; self.select_sayisi=0; self.secenekler=[]; self.secilenler=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='form':
            if not self.goruldu:
                self.goruldu=True; self.ic=True; self.form=a
            return
        if not self.ic:
            return
        if tag=='input' and a.get('name') and 'disabled' not in a:
            tur=(a.get('type') or 'text').lower()
            if tur=='hidden' or (tur=='text' and 'readonly' in a):
                if a['name'] in ('baslik','oncelik'):
                    raise ValueError('kullanıcı alanı sabit olamaz')
                self.sabitler.append((a['name'],a.get('value') or ''))
        if tag=='select' and a.get('name')=='oncelik' and 'disabled' not in a:
            self.select_sayisi+=1; self.secim=True
        if tag=='option' and self.secim and 'disabled' not in a:
            deger=a.get('value')
            if not deger or deger in self.secenekler:
                raise ValueError('option value eksik veya yinelenmiş')
            self.secenekler.append(deger)
            if 'selected' in a:
                self.secilenler.append(deger)
    def handle_endtag(self,tag):
        if tag=='form':
            self.ic=False
        if tag=='select':
            self.secim=False

def form_plani(kaynak,sayfa_url):
    origin=_origin(sayfa_url)
    p=_FormOku(); p.feed(kaynak); p.close()
    if p.form is None or (p.form.get('method') or 'get').lower()!='post':
        raise ValueError('POST form gerekli')
    if (p.form.get('enctype') or 'application/x-www-form-urlencoded').lower()!='application/x-www-form-urlencoded':
        raise ValueError('enctype desteklenmiyor')
    if p.select_sayisi!=1 or not p.secenekler or len(p.secilenler)>1:
        raise ValueError('öncelik seçenekleri geçersiz')
    action=p.form.get('action') or sayfa_url
    if any(ord(c)<=32 or ord(c)==127 for c in action):
        raise ValueError('action geçersiz')
    url=urldefrag(urljoin(sayfa_url,action))[0]
    if _origin(url)!=origin:
        raise ValueError('action origin değiştiremez')
    return {'url':url,'sabitler':p.sabitler,'oncelikler':p.secenekler,'varsayilan':p.secilenler[0] if p.secilenler else p.secenekler[0]}
```

```hint
HTMLParser etiket/nitelik adlarını küçültür ve attribute içindeki &amp; değerini açar. Boolean disabled için a.get(...) değil, anahtarın varlığına bak. Sıralı çiftleri sözlüğe dönüştürme.
```
:::

::: gorev Formdan oluşturulan kayda ulaş
`bilet_ac(baslik, oncelik='orta', istek=None, sayfa_url=None)` oluşturulan kayıt sözlüğünü döndürsün. Önce başlığı strip et; 1–80 Unicode karakteri olmalı, CR/LF/NUL içermemeli. Başlık metin değilse veya sınır dışındaysa ağ çağrısından önce `ValueError`. Öncelik metin veya `None`; `None`, HTML planının varsayılanını seçer, diğer değer planın seçeneklerinde bulunmalı.

`sayfa_url=None` ise `tezgah.SUNUCU+'/bilet-ac'`. `istek` verilirse `(yontem,url,govde=None,basliklar=None) -> (durum,tablo,govde_bayt)` sözleşmesindedir; tablo küçük harfli başlık adlarını değer listelerine eşler. Otomatik yönlendirme yapmaz. Verilmezse yerel tezgâh için kendi küçük taşıma adaptörünü kullanabilirsin; burada `tezgah.yanit` serbesttir. Görev ham HTTP ayrıştırmasını HT14'ten tekrar istemez.

1. Sayfayı GET al: durum 200, tek Content-Type medya türü `text/html`, UTF-8 gövde gerekli. İlk görevdeki `form_plani` sözleşmesini bu çözümde de uygula.
2. Planın sabit çiftleri, ardından `('baslik',temiz_baslik)` ve `('oncelik',secim)` sırasıyla URL-encode edilip ASCII bayt olarak POST gönderilsin. Content-Type tam `application/x-www-form-urlencoded` olsun.
3. POST tam 303 ve tek dolu Location döndürmeli. Adresi **POST action URL'sine göre** çöz, fragmenti çıkar; aynı HTTP origin'inde kalmalı. Sonra gövdesiz GET gönder.
4. Son yanıt 200 ve medya türü `application/json` olmalı. UTF-8 JSON nesnesinde `id` bool olmayan pozitif int, `baslik` ve `oncelik` gönderilen değerlerle aynı olmalı; nesnenin tamamını döndür. Uyuşmayan durum/MIME/başlık/JSON/kayıtta `ValueError`.

Her adım doğrulanmadan sonraki çağrı yapılmasın. Content-Type parametreleri kabul edilir. Sayfa ve Location URL kontrolleri ilk görevle aynıdır. Normal dosya/mime dışı yanıtlar desteklenmez; `<base>`, otomatik login veya genel redirect döngüsü yoktur. Görevler bağımsızdır: `form_plani` ve yardımcılarını bu çözümüne de ekle.

```starter
def bilet_ac(baslik,oncelik='orta',istek=None,sayfa_url=None):
    return {'id':1,'baslik':baslik,'oncelik':oncelik}
```

```test
import json
from urllib.parse import parse_qsl, urlsplit
import tezgah
need('bilet_ac')
# Gerçek yerel GET form / POST / 303 / GET JSON.
for baslik,oncelik in [('A','orta'),('ğ'*80,'yüksek'),('  Ağ & disk=1+2  ','düşük')]:
    b=bilet_ac(baslik,oncelik)
    ok(type(b['id']) is int and b['id']>0,'gerçek kayıt kimliği')
    eq((b['baslik'],b['oncelik']),(baslik.strip(),oncelik),'tezgâhta oluşan kayıt')
# Callback, değişken gizli ve readonly alanları ile tüm gönderim baytlarını ölçer.
base='http://pafta.test:8123/form/yeni'
def kaynak(kod='A&amp;B',action='../gonder?tur=bilet'):
    return f'''<form method="post" action="{action}"><input type="hidden" name="kod" value="{kod}"><input name="kaynak" value="salt+okunur" readonly><input type="hidden" name="kod" value="ikinci"><input type="hidden" name="alma" value="x" disabled><input readonly disabled="" name="alma_salt" value="x"><select name="oncelik"><option value="düşük">D</option><option value="orta">O</option><option selected value="yüksek">Y</option></select></form>'''
def deneme(yanitlar,baslik='A & B=1+2',oncelik=None):
    cagri=[]
    def iste(m,u,g=None,b=None):
        cagri.append((m,u,g,b))
        return yanitlar[len(cagri)-1]
    sonuc=bilet_ac(baslik,oncelik,iste,base)
    return sonuc,cagri
for kod in ('A&amp;B','başka','0','x+y=2'):
    veri={'id':7,'baslik':'A & B=1+2','oncelik':'yüksek','ek':'koru'}
    sonuc,c=deneme([(200,{'content-type':['Text/HTML; charset=UTF-8']},kaynak(kod).encode()),(303,{'location':['kayit/7#son']},b''),(200,{'content-type':['application/json; charset=utf-8']},json.dumps(veri,ensure_ascii=False).encode())])
    eq(sonuc,veri,'JSON nesnesinin tamamı')
    eq([(x[0],x[1]) for x in c],[('GET',base),('POST','http://pafta.test:8123/gonder?tur=bilet'),('GET','http://pafta.test:8123/kayit/7')],'GET POST GET ve relative Location action tabanlı')
    eq(c[0][2],None,'ilk GET gövdesiz')
    eq(c[2][2],None,'303 sonrası GET gövdesiz')
    ok(isinstance(c[1][2],bytes),'POST gövdesi bayt')
    eq(parse_qsl(c[1][2].decode('ascii'),keep_blank_values=True),[('kod',kod.replace('&amp;','&')),('kaynak','salt+okunur'),('kod','ikinci'),('baslik','A & B=1+2'),('oncelik','yüksek')],'gizli ve readonly kaynak değerleri; tekrar ve özel karakterler')
    eq(c[1][3],[('Content-Type','application/x-www-form-urlencoded')],'form MIME')
def asla(*a,**k):
    raise AssertionError('geçersiz başlıkta istek yapılmamalı')
for baslik in ('',' ','x'*81,'ğ'*81,'a\nb','a\rb','a\0b',None):
    raises(ValueError,bilet_ac,baslik,'orta',asla,base,msg='başlık 0/81/kontrol/metin sınırı')
for url in ('https://pafta.test/a','http://u@pafta.test/a','http://pafta.test:0/a','http://pafta.test:65536/a','http://pafta.test/a b','http://pafta.test/a\x1fb','http://pafta.test/a\x7fb'):
    raises(ValueError,bilet_ac,'başlık','orta',asla,url,msg='URL doğrulaması ağdan önce')
for uzunluk in (1,80):
    veri={'id':uzunluk,'baslik':'ğ'*uzunluk,'oncelik':'orta'}
    sonuc,c=deneme([(200,{'content-type':['text/html']},kaynak().encode()),(303,{'location':['/kayit']},b''),(200,{'content-type':['application/json']},json.dumps(veri,ensure_ascii=False).encode())],veri['baslik'],'orta')
    eq(sonuc,veri,'1/80 Unicode karakteri')
def hata_akisi(cevaplar,beklenen_cagri=1,oncelik='orta'):
    c=[]
    def iste(*args):
        c.append(args)
        return cevaplar[len(c)-1]
    raises(ValueError,bilet_ac,'başlık',oncelik,iste,base,msg='bozuk akış reddedildi')
    eq(len(c),beklenen_cagri,'hata sonrası yeni istek yok')
iyi=(200,{'content-type':['text/html']},kaynak().encode())
port_cagri=[]
port_json={'id':1,'baslik':'başlık','oncelik':'orta'}
port_yanitlar=[(200,{'content-type':['text/html']},kaynak(action='http://pafta.test/gonder').encode()),(303,{'location':['http://pafta.test:80/kayit']},b''),(200,{'content-type':['application/json']},json.dumps(port_json,ensure_ascii=False).encode())]
def port_iste(*args):
    port_cagri.append(args)
    return port_yanitlar[len(port_cagri)-1]
eq(bilet_ac('başlık','orta',port_iste,'http://pafta.test:80/form/yeni'),port_json,'açık ve örtük port80 aynı origin')
for r in ((404,{'content-type':['text/html']},b''),(200,{},b''),(200,{'content-type':['application/json']},b'{}'),(200,{'content-type':['text/html','text/html']},b''),(200,{'content-type':['text/html']},b'\xff')):
    hata_akisi([r])
hata_akisi([iyi],oncelik='kritik')
for h in (kaynak().replace('method="post"','method="get"'),kaynak().replace('name="oncelik"','name="baska"'),kaynak().replace('value="yüksek"','value="düşük"'),kaynak().replace('value="düşük"','value=""'),kaynak().replace('value="orta"','value="orta" selected'),kaynak(action='/a b'),kaynak(action='/a\x1fb'),kaynak(action='/a\x7fb'),kaynak(action='/a\tb'),kaynak(action='/a\r\nb')):
    hata_akisi([(200,{'content-type':['text/html']},h.encode())])
for r in ((201,{},b'{}'),(302,{'location':['/kayit']},b''),(303,{},b''),(303,{'location':['']},b''),(303,{'location':['/a','/b']},b''),(303,{'location':['http://other.test/x']},b''),(303,{'location':['https://pafta.test:8123/x']},b''),(303,{'location':['/a b']},b''),(303,{'location':['/a\x1fb']},b''),(303,{'location':['/a\x7fb']},b''),(303,{'location':['/a\tb']},b''),(303,{'location':['/a\r\nb']},b'')):
    hata_akisi([iyi,r],2)
yon=(303,{'location':['/kayit']},b'')
for r in ((404,{'content-type':['application/json']},b'{}'),(200,{},b'{}'),(200,{'content-type':['text/html']},b'{}'),(200,{'content-type':['application/json']},b'bozuk')):
    hata_akisi([iyi,yon,r],3)
for veri in ([],{'id':0,'baslik':'başlık','oncelik':'orta'},{'id':True,'baslik':'başlık','oncelik':'orta'},{'id':1,'baslik':'başka','oncelik':'orta'},{'id':1,'baslik':'başlık','oncelik':'yüksek'}):
    hata_akisi([iyi,yon,(200,{'content-type':['application/json']},json.dumps(veri,ensure_ascii=False).encode())],3)
```

```solution
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit, urldefrag, urlencode
import json

def _origin(url):
    if not isinstance(url,str) or any(ord(c)<=32 or ord(c)==127 for c in url):
        raise ValueError('URL geçersiz')
    u=urlsplit(url)
    if u.scheme!='http' or not u.hostname or u.username is not None or u.password is not None or u.port==0:
        raise ValueError('yalnız userinfo içermeyen HTTP URL')
    return (u.scheme,u.hostname.lower(),u.port or 80)

class _FormOku(HTMLParser):
    def __init__(self):
        super().__init__()
        self.goruldu=False; self.ic=False; self.form=None
        self.sabitler=[]; self.secim=False; self.select_sayisi=0; self.secenekler=[]; self.secilenler=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='form':
            if not self.goruldu:
                self.goruldu=True; self.ic=True; self.form=a
            return
        if not self.ic:
            return
        if tag=='input' and a.get('name') and 'disabled' not in a:
            tur=(a.get('type') or 'text').lower()
            if tur=='hidden' or (tur=='text' and 'readonly' in a):
                if a['name'] in ('baslik','oncelik'):
                    raise ValueError('kullanıcı alanı sabit olamaz')
                self.sabitler.append((a['name'],a.get('value') or ''))
        if tag=='select' and a.get('name')=='oncelik' and 'disabled' not in a:
            self.select_sayisi+=1; self.secim=True
        if tag=='option' and self.secim and 'disabled' not in a:
            deger=a.get('value')
            if not deger or deger in self.secenekler:
                raise ValueError('option value eksik veya yinelenmiş')
            self.secenekler.append(deger)
            if 'selected' in a:
                self.secilenler.append(deger)
    def handle_endtag(self,tag):
        if tag=='form':
            self.ic=False
        if tag=='select':
            self.secim=False

def form_plani(kaynak,sayfa_url):
    origin=_origin(sayfa_url)
    p=_FormOku(); p.feed(kaynak); p.close()
    if p.form is None or (p.form.get('method') or 'get').lower()!='post':
        raise ValueError('POST form gerekli')
    if (p.form.get('enctype') or 'application/x-www-form-urlencoded').lower()!='application/x-www-form-urlencoded':
        raise ValueError('enctype desteklenmiyor')
    if p.select_sayisi!=1 or not p.secenekler or len(p.secilenler)>1:
        raise ValueError('öncelik seçenekleri geçersiz')
    action=p.form.get('action') or sayfa_url
    if any(ord(c)<=32 or ord(c)==127 for c in action):
        raise ValueError('action geçersiz')
    url=urldefrag(urljoin(sayfa_url,action))[0]
    if _origin(url)!=origin:
        raise ValueError('action origin değiştiremez')
    return {'url':url,'sabitler':p.sabitler,'oncelikler':p.secenekler,'varsayilan':p.secilenler[0] if p.secilenler else p.secenekler[0]}

def _yerel_istek(yontem,url,govde=None,basliklar=None):
    import tezgah
    if _origin(url)!=_origin(tezgah.SUNUCU):
        raise ValueError('varsayılan taşıma yalnız yerel tezgâha gider')
    u=urlsplit(url)
    hedef=(u.path or '/')+('?' + u.query if u.query else '')
    satirlar=[f'{yontem} {hedef} HTTP/1.1',f'Host: {u.netloc}','Connection: close']
    satirlar += [f'{a}: {d}' for a,d in (basliklar or [])]
    if govde is not None:
        satirlar.append(f'Content-Length: {len(govde)}')
    y=tezgah.yanit(('\r\n'.join(satirlar)+'\r\n\r\n').encode('ascii')+(govde or b''))
    tablo={}
    for a,d in y.basliklar:
        tablo.setdefault(a.lower(),[]).append(d)
    return y.durum,tablo,y.govde_bayt

def _medya(tablo,tur):
    degerler=tablo.get('content-type',[])
    if len(degerler)!=1 or degerler[0].split(';',1)[0].strip().lower()!=tur:
        raise ValueError('Content-Type uyuşmuyor')

def bilet_ac(baslik,oncelik='orta',istek=None,sayfa_url=None):
    if not isinstance(baslik,str) or any(c in baslik for c in '\r\n\0'):
        raise ValueError('başlık geçersiz')
    baslik=baslik.strip()
    if not 1<=len(baslik)<=80 or (oncelik is not None and not isinstance(oncelik,str)):
        raise ValueError('başlık veya öncelik geçersiz')
    if sayfa_url is None:
        import tezgah
        sayfa_url=tezgah.SUNUCU+'/bilet-ac'
    _origin(sayfa_url)
    istek=istek or _yerel_istek
    durum,tablo,govde=istek('GET',sayfa_url,None,None)
    if durum!=200:
        raise ValueError('form alınamadı')
    _medya(tablo,'text/html')
    plan=form_plani(govde.decode('utf-8'),sayfa_url)
    secim=plan['varsayilan'] if oncelik is None else oncelik
    if secim not in plan['oncelikler']:
        raise ValueError('öncelik formda yok')
    alanlar=plan['sabitler']+[('baslik',baslik),('oncelik',secim)]
    veri=urlencode(alanlar,encoding='utf-8').encode('ascii')
    durum,tablo,govde=istek('POST',plan['url'],veri,[('Content-Type','application/x-www-form-urlencoded')])
    yerler=tablo.get('location',[])
    if durum!=303 or len(yerler)!=1 or not yerler[0].strip():
        raise ValueError('303 ve tek Location gerekli')
    if any(ord(c)<=32 or ord(c)==127 for c in yerler[0]):
        raise ValueError('Location geçersiz')
    son=urldefrag(urljoin(plan['url'],yerler[0]))[0]
    if _origin(son)!=_origin(sayfa_url):
        raise ValueError('Location origin değiştiremez')
    durum,tablo,govde=istek('GET',son,None,None)
    if durum!=200:
        raise ValueError('kayıt alınamadı')
    _medya(tablo,'application/json')
    sonuc=json.loads(govde.decode('utf-8'))
    if not isinstance(sonuc,dict) or type(sonuc.get('id')) is not int or sonuc['id']<=0 or sonuc.get('baslik')!=baslik or sonuc.get('oncelik')!=secim:
        raise ValueError('kayıt yanıtı uyuşmuyor')
    return sonuc
```

```hint
İlk görevin planlayıcısını yeniden kullan. urlencode'a sözlük yerine çift listesi ver. Location'ı sayfanın değil, POST'un gerçek action adresine göre çöz. Her HTTP adımının durumunu ve MIME'ını ilerlemeden doğrula.
```
:::
