---
id: ht23
title: WebSocket — 101 ve Maskeli Mesaj
summary: Gerçek TCP bağlantısında el sıkışmasını, oturum/Origin reddini ve UTF-8 çerçevesini oku.
---

::: anlat HTTP yükseltmesi mesajın kendisi değildir
`GET /ws` isteği Upgrade: websocket, Connection: Upgrade, Sec-WebSocket-Version: 13 ve base64 kodlu 16 baytlık rastgele Sec-WebSocket-Key taşır. Başarılı yanıt **101** ve `base64(SHA1(key + GUID))` biçimindeki Sec-WebSocket-Accept değeridir. GUID `258EAFA5-E914-47DA-95CA-C5AB0DC85B11`. SHA1 burada parola saklamak için değil, protokolün el sıkışması için kullanılır; şifreleme sağlamaz.

Laboratuvar geçerli Cookie ve tam izinli Origin ister. Oturumsuz 401, yanlış Origin 403, bozuk key/version 400 verir. Origin tarayıcıdan gelen güven bağlamıdır; özel istemci bunu taklit edebilir, kimliğin yerine geçmez. WebSocket'e klasik Fetch CORS yanıtı denetimi uygulanacağını varsayma.

101'den sonra HTTP gövdesi değil WebSocket çerçeveleri vardır. İstemciden sunucuya çerçeve **maskeli** olmalıdır. Sunucudan istemciye maske yoktur. Bu tezgah yalnız **FIN=1, text, 0..125 bayt, tek mesaj** ve ardından normal kapanış destekler. Uzun/extended frame → 1009; maskesiz veya RSV → 1002; parçalı/binary → 1003; geçersiz UTF-8 → 1007. Ping/pong, fragmentation ve sıkıştırma bu sınırlı sunucuda yoktur; üretim kitaplığı yerine kullanma. Boyutu karakterle değil UTF-8 baytıyla ölç.

Kaynaklar: [RFC 6455 el sıkışması](https://datatracker.ietf.org/doc/html/rfc6455#section-4), [çerçeveleme](https://datatracker.ietf.org/doc/html/rfc6455#section-5), [Origin](https://datatracker.ietf.org/doc/html/rfc6455#section-10.2).
:::

::: tahmin
```python
from http_lab import Lab
from http_ws_lab import exchange
with Lab() as lab:
    c=lab.login('ayse')
    r=exchange(lab,c,text='Ağ')
    print(r['status'],r['text'])
    print(exchange(lab,None)['status'])
    print(exchange(lab,c,origin='http://other.test')['status'])
```
???
`101 Ağ`, `401`, `403`. İlk satır gerçek maskeli istemci mesajının sunucudan geri dönmesidir; yalnız 101 üreten bir sahte yanıt değildir.
:::

::: gorev Kısa maskeli text çerçevesi
`text_frame(text,mask)` bytes döndürsün. mask tam 4 baytlık bytes, text str olmalı; UTF-8 uzunluğu 0..125. İhlalde ValueError. Başlık 0x81 ve 0x80|uzunluk; ardından mask ve her veri baytı için `bayt XOR mask[i%4]`. Üretim istemcisi her mesajda yeni rastgele maske üretir; burada ölçüm için maskeyi parametre alıyoruz.
```starter
def text_frame(text,mask):
    return b''
```
```test
from http_lab import Lab
from http_ws_lab import exchange
for text in ('','a','x'*125,'\u011f'*62+'x'):
    for mask in (b'\0\0\0\0',b'abcd',b'\xff\x01\x02\x03'):
        data=text.encode('utf-8'); f=text_frame(text,mask)
        eq(f[:2],bytes([129,128|len(data)]),'FIN opcode mask ve bayt uzunlugu')
        eq(f[2:6],mask,'mask aynen korunur')
        eq(f[6:],bytes(b^mask[i%4] for i,b in enumerate(data)),'XOR')
for text,mask in [('x'*126,b'abcd'),('\u011f'*63,b'abcd'),('x',b''),('x',b'abc'),('x',b'abcde'),('x','abcd'),(b'x',b'abcd')]:
    try: text_frame(text,mask)
    except ValueError: pass
    else: ok(False,'boyut ve tur')
with Lab() as lab:
    c=lab.login('ayse')
    for text in ('','A\u011f','x'*125):
        r=exchange(lab,c,frame=text_frame(text,b'Paft'))
        eq((r['opcode'],r['text']),(1,text),'gercek sunucuda cozuldu')
```
```solution
def text_frame(text,mask):
    if not isinstance(text,str) or not isinstance(mask,bytes) or len(mask)!=4: raise ValueError('text/mask')
    data=text.encode('utf-8')
    if len(data)>125: raise ValueError('kisa cerceve siniri')
    return bytes([0x81,0x80|len(data)])+mask+bytes(v^mask[i%4] for i,v in enumerate(data))
```
```hint
Türkçe karakterler birden fazla bayt olabilir. len(text) yerine len(text.encode('utf-8')) kullan.
```
:::

::: gorev 101 yanıtının protokol kanıtı
`handshake_ok(status,headers,key)` bool döndürsün. status 101, büyük/küçük harften bağımsız header adlarıyla Upgrade websocket, Connection virgülle ayrılmış token'larında upgrade ve doğru Sec-WebSocket-Accept aranır. Key strict base64 ile 16 bayta çözülmeli; bozuksa False. Eksik alan False. Cookie/Origin sunucunun ayrı kontrolleridir; burada yanıtın protokol tutarlılığını doğruluyoruz.
```starter
def handshake_ok(status,headers,key):
    return status==101
```
```test
from http_ws_lab import accept_value,exchange
from http_lab import Lab
key='dGhlIHNhbXBsZSBub25jZQ=='
eq(accept_value(key),'s3pPLMBiTxaQ9kYGzzhZRbK+xOo=','RFC ornegi')
h={'Upgrade':'WebSocket','Connection':'keep-alive, Upgrade','Sec-WebSocket-Accept':accept_value(key)}
eq(handshake_ok(101,h,key),True,'tokenlar ve buyuk/kucuk harf')
for status,field,value in [(100,'Upgrade','websocket'),(102,'Upgrade','websocket'),(200,'Upgrade','websocket'),(101,'Upgrade','h2c'),(101,'Connection','x-upgrade'),(101,'Sec-WebSocket-Accept','bad')]:
    hh=dict(h); hh[field]=value
    eq(handshake_ok(status,hh,key),False,'gercek kanit gerekli')
for field in h:
    hh=dict(h); hh.pop(field); eq(handshake_ok(101,hh,key),False,'eksik baslik')
for key2 in ('','!!!','YQ==','dGhlIHNhbXBsZSBub25jZQ==\n'):
    eq(handshake_ok(101,h,key2),False,'strict 16 bayt key')
with Lab() as lab:
    c=lab.login('berk'); r=exchange(lab,c)
    eq(handshake_ok(r['status'],r['headers'],r['key']),True,'gercek TCP el sikismasi')
```
```solution
import base64,hashlib
def handshake_ok(status,headers,key):
    try:
        if len(base64.b64decode(key,validate=True))!=16: return False
        expected=base64.b64encode(hashlib.sha1((key+'258EAFA5-E914-47DA-95CA-C5AB0DC85B11').encode('ascii')).digest()).decode('ascii')
    except (ValueError,UnicodeError,TypeError):
        return False
    h={k.lower():v for k,v in headers.items()}
    return status==101 and h.get('upgrade','').lower()=='websocket' and 'upgrade' in {v.strip().lower() for v in h.get('connection','').split(',')} and h.get('sec-websocket-accept')==expected
```
```hint
Connection alanında substring aramak x-upgrade'i yanlış kabul eder; virgülden böl ve token eşitliği kullan.
```
:::
