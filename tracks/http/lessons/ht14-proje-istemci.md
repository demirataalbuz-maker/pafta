---
id: ht14
title: Proje · Kendi HTTP İstemcin
summary: İstek baytlarını kur; parçalı TCP okumalarından nihai HTTP/1.x yanıtını çöz; test edilebilir taşıma katmanıyla yönlendirme ve basit oturum yönetimini birleştir.
---

::: anlat Üç parçalı istemci
HT01–HT13'ü birleştiriyoruz: önce `istek_kur` telde giden baytları üretir, sonra `gonder` soketle gönderip `yanit_coz` ile çözer. Son aşamadaki `Istemci(gonder)` bu tek-istek fonksiyonunu kullanarak yönlendirmeleri ve çerezleri yönetir. Fonksiyonu parametre olarak vermek, bağlantı katmanını değiştirmeden oturum mantığını sınamayı sağlar. Her görevin örnek çözümü kendi başına çalışır; önceki görevin değişkenleri otomatik aktarılmaz.

Bu proje HTTP/1.0–1.1, `Connection: close` ve tek nihai yanıtla sınırlıdır. Soket istemcisi TLS yapmaz; `https` URL'yi HTTP diye göndermez, reddeder. URL önceden yüzde kodlanmış ASCII olmalı; ham Türkçe URL için HT02'deki kodlama gerekir. IPv6 `Host` değeri köşeli parantez taşır. Gövde ise UTF-8 metin veya ham bayt olabilir.

| Katman | Girdi | Çıktı |
|---|---|---|
| İstek kurucu | yöntem, URL, başlık çiftleri, gövde | bayt |
| Tek istek taşıyıcı | aynı bilgiler | `(durum, başlıklar, gövde_bayt)` |
| Oturum | tek istek taşıyıcı fonksiyon | yönlendirmelerden sonraki aynı üçlü ve son URL |

Başlık sözlüğünde küçük harfli adların değerleri **listededir**; birden fazla `Set-Cookie` ayrı kalır. Başlıklar için Latin-1, metin gövdede UTF-8 kullanıyoruz. `Host`, `Connection`, `Content-Length`, `Transfer-Encoding` istek kurucunun yönettiği alanlardır; dışarıdan yinelenmez.
:::

::: anlat Eksik veri başarı değildir
TCP mesaj sınırı taşımaz: tek bir `recv(4096)` çağrısı bütün yanıtı getirmeyebilir. `recv` boş bayt döndürene kadar biriktir; `Connection: close` bu projede sonu belirler. Boy sınırına **eşit** yanıt geçer, bir bayt fazlası reddedilir. Soket zaman aşımı da başarıya çevrilmez.

Yanıtta önce HEAD/204/304 gibi gövdesiz durumları ayır. Diğerlerinde chunked veya Content-Length çerçevesini kontrol et; ikisi de yoksa kapanışa kadarki veri gövdedir. Bu projenin katı politikası yinelenen Content-Length'i (aynı olsa bile), TE+CL birlikteliğini ve chunked dışındaki aktarım kodlamalarını reddeder. RFC aynı değerli bazı CL tekrarlarının birleştirilmesine izin verir; burada bilinçli olarak daha dar davranıyoruz. `1xx` ara yanıtlar, CONNECT tüneli, sıkıştırma açma ve HTTP/2–3 kapsam dışıdır.

Chunk boyu onaltılık, verinin ardından CRLF zorunludur. Sıfır parçadan sonra trailer satırları ve boş satır bulunmalı; trailer'ı atlarız. Bir mesajdan sonraki baytlar gövdeye katılmaz. Başlık ayracı, bildirilen veri veya parça sonu eksikse `ValueError` üret. Tam bir tarayıcı veya üretim HTTP kütüphanesi yazmıyoruz.

Kaynaklar: [RFC 9112 mesaj sınırları](https://www.rfc-editor.org/rfc/rfc9112.html#section-6.3), [chunked](https://www.rfc-editor.org/rfc/rfc9112.html#section-7.1), [RFC 9110 yönlendirme](https://www.rfc-editor.org/rfc/rfc9110.html#section-15.4).
:::

::: tahmin
Yönlendirme sınırını ve bayt uzunluğunu üç satırda oku:

```python
govde = "Ağ".encode("utf-8")
print(len(govde), govde)
for izlenen in (5, 6):
    print(izlenen, "devam" if izlenen <= 5 else "dur")
```

???

`3 b'A\xc4\x9f'`, `5 devam` ve `6 dur`. İki karakter UTF-8'de üç bayttır. Beş yönlendirmeye izin verilir; altıncı hedefe istek gönderilmez. Bir zincirde başlangıç isteği yönlendirme sayılmaz.
:::

::: gorev 1 · İsteği kur
`istek_kur(yontem, url, basliklar=None, govde=None)` bayt döndürsün. Sıra: istek satırı, Host, verilen başlık çiftleri, Connection: close, gövde None değilse Content-Length, boş satır ve gövde. Host'ta varsayılan 80 yazılmaz; diğer portlar 1–65535 arasıdır, IPv6 parantezini koru. Boş yol `/`, sorgu korunur, fragment atılır. Metin gövdeyi UTF-8'e çevirip **bayt say**; None ile boş baytı ayır.

Yöntem yalnız büyük ASCII harfleri; URL kimlik bilgisi taşımayan mutlak `http` ve önceden kodlanmış ASCII olsun. URL'de ham boşluk/kontrol karakteri, başlık adında token dışı karakter veya ayrılan dört başlık, değerde TAB dışı kontrol karakteri varsa ValueError. Desteklenmeyen gövde türü de ValueError. Başlık çiftlerinin sırasını ve tekrarlarını koru.

```starter
def istek_kur(yontem, url, basliklar=None, govde=None):
    return b""
```

```test
need("istek_kur")
from urllib.parse import urlsplit
for url, host, hedef in [
    ("http://pafta.test", "pafta.test", "/"),
    ("http://pafta.test:80/a?x=1#k", "pafta.test", "/a?x=1"),
    ("http://pafta.test:81/a", "pafta.test:81", "/a"),
    ("http://pafta.test:1/", "pafta.test:1", "/"),
    ("http://pafta.test:65535/%C4%B1?q=%26", "pafta.test:65535", "/%C4%B1?q=%26"),
    ("http://[::1]:8080/a#x", "[::1]:8080", "/a"),
    ("http://[::1]:80/", "[::1]", "/")]:
    eq(istek_kur("GET", url), f"GET {hedef} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n".encode(), url)
for govde in (None, b"", b"x", b"\x00\xff", "Ağ", "x" * 80):
    ham = istek_kur("POST", "http://pafta.test/", [("X-A", "1"), ("X-A", "2")], govde)
    veri = govde.encode("utf-8") if isinstance(govde, str) else govde
    cl = b"" if veri is None else f"Content-Length: {len(veri)}\r\n".encode()
    eq(ham, b"POST / HTTP/1.1\r\nHost: pafta.test\r\nX-A: 1\r\nX-A: 2\r\nConnection: close\r\n" + cl + b"\r\n" + (veri or b""), "None/0/1/Unicode/binary gövde")
for url in ("http://pafta.test:0/", "http://pafta.test:65536/", "https://pafta.test/", "/a", "http:///a", "http://ad:sifre@pafta.test/", "http://pafta.test/a b", "http://pafta.test/\r\nx", "http://pafta.test/ışık"):
    raises(ValueError, istek_kur, "GET", url, msg="URL kapsamı: " + repr(url))
for ad, deger in [("HOST", "x"), ("Connection", "close"), ("content-length", "0"), ("Transfer-Encoding", "chunked"), ("X A", "x"), ("X", "a\r\nY: b"), ("X", "\0")]:
    raises(ValueError, istek_kur, "GET", "http://pafta.test/", [(ad,deger)], msg="başlık denetimi")
raises(ValueError, istek_kur, "GET /x", "http://pafta.test/", msg="yöntem jetonu")
import tezgah
y = tezgah.yanit(istek_kur("GET", tezgah.SUNUCU + "/sunucular/db01"))
eq((y.durum, y.json()["ad"]), (200, "db01"), "gerçek sunucu baytları kabul etti")
```

```solution
import re
from urllib.parse import urlsplit


def istek_kur(yontem, url, basliklar=None, govde=None):
    if not re.fullmatch(r"[A-Z]+", yontem):
        raise ValueError("Yöntem büyük ASCII harflerinden oluşmalı")
    if any(ord(c) <= 32 or ord(c) == 127 for c in url):
        raise ValueError("URL boşluk veya kontrol karakteri taşıyamaz")
    u = urlsplit(url)
    if u.scheme != "http" or not u.hostname or u.username is not None or u.password is not None:
        raise ValueError("Kimlik bilgisi taşımayan mutlak http URL gerekli")
    port = u.port
    if port is not None and not 1 <= port <= 65535:
        raise ValueError("Port 1–65535 olmalı")
    host = "[" + u.hostname + "]" if ":" in u.hostname else u.hostname
    if port is not None and port != 80:
        host += ":" + str(port)
    hedef = (u.path or "/") + ("?" + u.query if u.query else "")
    try:
        (hedef + host).encode("ascii")
    except UnicodeEncodeError as exc:
        raise ValueError("URL önceden yüzde kodlanmış ASCII olmalı") from exc
    satirlar = [f"{yontem} {hedef} HTTP/1.1", "Host: " + host]
    ayrilan = {"host", "connection", "content-length", "transfer-encoding"}
    for ad, deger in basliklar or []:
        if not re.fullmatch(r"[!#$%&'*+.^_`|~0-9A-Za-z-]+", ad) or ad.lower() in ayrilan:
            raise ValueError("Geçersiz veya istemcinin yönettiği başlık")
        if any((ord(c) < 32 and c != "\t") or ord(c) == 127 for c in deger):
            raise ValueError("Başlık değeri kontrol karakteri taşıyamaz")
        satirlar.append(f"{ad}: {deger}")
    satirlar.append("Connection: close")
    if isinstance(govde, str):
        govde = govde.encode("utf-8")
    if govde is not None and not isinstance(govde, bytes):
        raise ValueError("Gövde metin, bytes veya None olmalı")
    if govde is not None:
        satirlar.append(f"Content-Length: {len(govde)}")
    return ("\r\n".join(satirlar) + "\r\n\r\n").encode("iso-8859-1") + (govde or b"")
```

```hint
Önce URL ve gövdeyi normalleştir. IPv6 hostunda : varsa köşeli parantez; port None ile 0 aynı durum değildir.
```

```hint
Gövde uzunluğunu encode sonrasında al. None gövdeye CL eklenmez; b"" için CL: 0 eklenir.
```

:::

::: gorev 2 · Soketten al ve sınırları doğrula
`yanit_coz(ham, yontem="GET") -> (durum, basliklar, govde_bayt)` ve `gonder(yontem, url, govde=None, basliklar=None, azami=1048576)` yaz. Bu göreve önceki isteği kuran fonksiyonunu da koy. `gonder` gerçek `socket.create_connection` ve `sendall` kullansın, bağlantı kapanana kadar recv parçalarını toplasın; en fazla azami **ham yanıt baytını** kabul etsin. Soket her durumda kapansın; azami pozitif tamsayıdır.

`yanit_coz` HTTP/1.0 veya 1.1'in 200–599 nihai durumunu okur. Başlık adları token, küçük harfli sözlük değerleri liste; bozuk başlık reddedilir. HEAD/204/304'te gövde boş. Diğer durumlarda tek sayısal CL'ye göre tam boyu al (fazlayı at), eksikte ValueError; TE varsa yalnız tek chunked kabul et ve CL'yi reddet. Hex boyu, uzantı, veri CRLF'si ve terminal trailer boş satırını doğrula. Hiç uzunluk yoksa EOF gövdesini döndür. Yukarıda belirtilen kapsam dışı yanıtları ValueError ile reddet. Otomatik yönlendirme yapma.

```starter
import socket

def yanit_coz(ham, yontem="GET"):
    return 200, {}, b""

def gonder(yontem, url, govde=None, basliklar=None, azami=1048576):
    return 200, {}, b""
```

```test
need("istek_kur")
from urllib.parse import urlsplit
for url, host, hedef in [
    ("http://pafta.test", "pafta.test", "/"),
    ("http://pafta.test:80/a?x=1#k", "pafta.test", "/a?x=1"),
    ("http://pafta.test:81/a", "pafta.test:81", "/a"),
    ("http://pafta.test:1/", "pafta.test:1", "/"),
    ("http://pafta.test:65535/%C4%B1?q=%26", "pafta.test:65535", "/%C4%B1?q=%26"),
    ("http://[::1]:8080/a#x", "[::1]:8080", "/a"),
    ("http://[::1]:80/", "[::1]", "/")]:
    eq(istek_kur("GET", url), f"GET {hedef} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n".encode(), url)
for govde in (None, b"", b"x", b"\x00\xff", "Ağ", "x" * 80):
    ham = istek_kur("POST", "http://pafta.test/", [("X-A", "1"), ("X-A", "2")], govde)
    veri = govde.encode("utf-8") if isinstance(govde, str) else govde
    cl = b"" if veri is None else f"Content-Length: {len(veri)}\r\n".encode()
    eq(ham, b"POST / HTTP/1.1\r\nHost: pafta.test\r\nX-A: 1\r\nX-A: 2\r\nConnection: close\r\n" + cl + b"\r\n" + (veri or b""), "None/0/1/Unicode/binary gövde")
for url in ("http://pafta.test:0/", "http://pafta.test:65536/", "https://pafta.test/", "/a", "http:///a", "http://ad:sifre@pafta.test/", "http://pafta.test/a b", "http://pafta.test/\r\nx", "http://pafta.test/ışık"):
    raises(ValueError, istek_kur, "GET", url, msg="URL kapsamı: " + repr(url))
for ad, deger in [("HOST", "x"), ("Connection", "close"), ("content-length", "0"), ("Transfer-Encoding", "chunked"), ("X A", "x"), ("X", "a\r\nY: b"), ("X", "\0")]:
    raises(ValueError, istek_kur, "GET", "http://pafta.test/", [(ad,deger)], msg="başlık denetimi")
raises(ValueError, istek_kur, "GET /x", "http://pafta.test/", msg="yöntem jetonu")
import tezgah
y = tezgah.yanit(istek_kur("GET", tezgah.SUNUCU + "/sunucular/db01"))
eq((y.durum, y.json()["ad"]), (200, "db01"), "gerçek sunucu baytları kabul etti")
need("yanit_coz")
need("gonder")
from unittest.mock import patch
def yanit(govde, baslik=b"", kod=b"200 OK"):
    return b"HTTP/1.1 " + kod + b"\r\n" + baslik + b"\r\n" + govde
for veri in (b"", b"x", "Ağ".encode(), b"a\r\nb\x00"):
    h = f"cOnTeNt-LeNgTh: {len(veri)}\r\nX-A: bir\r\nX-A: iki\r\n".encode()
    d, b, g = yanit_coz(yanit(veri + b"SONRAKI", h))
    eq((d,b["x-a"],g), (200,["bir","iki"],veri), "tam bayt sınırı, başlık tekrarları")
eq(yanit_coz(yanit(b"kapanana kadar"))[2], b"kapanana kadar", "uzunluk yoksa EOF")
for kod in (b"204 No Content", b"304 Not Modified"):
    eq(yanit_coz(yanit(b"artakalan", kod=kod))[2], b"", "gövdesiz durum")
eq(yanit_coz(yanit(b"",b"Content-Length: 99\r\n"),"HEAD")[2],b"", "HEAD gövdesizdir")
te = b"Transfer-Encoding: Chunked\r\n"
for chunk, beklenen in [(b"0\r\n\r\n",b""), (b"1\r\nx\r\n0\r\n\r\n",b"x"),
    (b"4;ad=deger\r\na\r\nb\r\nA\r\n0123456789\r\n0\r\nX-End: evet\r\n\r\nARTIK", b"a\r\nb0123456789")]:
    eq(yanit_coz(yanit(chunk,te))[2],beklenen,"chunk sınırı, hex, uzantı ve trailer")
for bas, govde in [(b"Content-Length: 1\r\n",b""), (b"Content-Length: 2\r\n",b"x"),
    (b"Content-Length: -1\r\n",b""), (b"Content-Length: 1, 1\r\n",b"x"),
    (b"Content-Length: 1\r\nContent-Length: 1\r\n",b"x"),
    (te+b"Content-Length: 0\r\n",b"0\r\n\r\n"),
    (b"Transfer-Encoding: xchunked\r\n",b"0\r\n\r\n"),
    (b"Transfer-Encoding: gzip, chunked\r\n",b"0\r\n\r\n")]:
    raises(ValueError,yanit_coz,yanit(govde,bas),msg="eksik/belirsiz/desteklenmeyen çerçeveleme")
for chunk in (b"0\r\n",b"1\r\n",b"1\r\nx",b"1\r\nxXX0\r\n\r\n",b"+1\r\nx\r\n0\r\n\r\n",b"-1\r\n",b"G\r\nx\r\n",b"0\r\nbozuk\r\n\r\n"):
    raises(ValueError,yanit_coz,yanit(chunk,te),msg="bozuk chunk reddedilir")
for ham in (b"",b"HTTP/1.1 200 OK\r\n",b"HTTP/1.1 100 Continue\r\n\r\n",b"HTTP/1.1 200 OK\r\nBozuk\r\n\r\n"):
    raises(ValueError,yanit_coz,ham,msg="bozuk veya kapsam dışı başlık")
class Soket:
    def __init__(self, parcalar): self.parcalar=iter(parcalar); self.giden=[]; self.kapandi=False
    def __enter__(self): return self
    def __exit__(self,*a): self.kapandi=True
    def sendall(self, veri): self.giden.append(veri)
    def recv(self, n): return next(self.parcalar,b"")
ham=yanit("Ağ".encode(),b"Content-Length: 3\r\n")
for bolum in (1,2,len(ham)):
    s=Soket([ham[i:i+bolum] for i in range(0,len(ham),bolum)])
    with patch("socket.create_connection",return_value=s) as baglan:
        eq(gonder("GET","http://127.0.0.1:8770/a?x=1#f",azami=len(ham))[2],"Ağ".encode(),"parçalı recv ve tam boy sınırı")
        eq(baglan.call_args.args[0],("127.0.0.1",8770),"doğru soket adresi")
    eq(s.giden,[b"GET /a?x=1 HTTP/1.1\r\nHost: 127.0.0.1:8770\r\nConnection: close\r\n\r\n"],"sendall: gerçek istek")
    ok(s.kapandi,"soket kapandı")
s=Soket([ham])
with patch("socket.create_connection",return_value=s):
    raises(ValueError,gonder,"GET","http://127.0.0.1/",azami=len(ham)-1,msg="bir bayt fazla")
raises(ValueError,gonder,"GET","http://127.0.0.1/",azami=0,msg="sıfır limit")
import tezgah
eq(gonder("GET",tezgah.SUNUCU+"/durum")[0],200,"gerçek TCP")
eq(gonder("GET",tezgah.SUNUCU+"/akis")[2],"ilk satır\nikinci satır\nson\n".encode(),"gerçek chunked TCP")
eq(gonder("HEAD",tezgah.SUNUCU+"/durum")[2],b"","gerçek HEAD")
eq(gonder("GET",tezgah.SUNUCU+"/yok")[0],404,"HTTP hata yanıtı da çözümlenir")
```

```solution
import re
from urllib.parse import urlsplit


def istek_kur(yontem, url, basliklar=None, govde=None):
    if not re.fullmatch(r"[A-Z]+", yontem):
        raise ValueError("Yöntem büyük ASCII harflerinden oluşmalı")
    if any(ord(c) <= 32 or ord(c) == 127 for c in url):
        raise ValueError("URL boşluk veya kontrol karakteri taşıyamaz")
    u = urlsplit(url)
    if u.scheme != "http" or not u.hostname or u.username is not None or u.password is not None:
        raise ValueError("Kimlik bilgisi taşımayan mutlak http URL gerekli")
    port = u.port
    if port is not None and not 1 <= port <= 65535:
        raise ValueError("Port 1–65535 olmalı")
    host = "[" + u.hostname + "]" if ":" in u.hostname else u.hostname
    if port is not None and port != 80:
        host += ":" + str(port)
    hedef = (u.path or "/") + ("?" + u.query if u.query else "")
    try:
        (hedef + host).encode("ascii")
    except UnicodeEncodeError as exc:
        raise ValueError("URL önceden yüzde kodlanmış ASCII olmalı") from exc
    satirlar = [f"{yontem} {hedef} HTTP/1.1", "Host: " + host]
    ayrilan = {"host", "connection", "content-length", "transfer-encoding"}
    for ad, deger in basliklar or []:
        if not re.fullmatch(r"[!#$%&'*+.^_`|~0-9A-Za-z-]+", ad) or ad.lower() in ayrilan:
            raise ValueError("Geçersiz veya istemcinin yönettiği başlık")
        if any((ord(c) < 32 and c != "\t") or ord(c) == 127 for c in deger):
            raise ValueError("Başlık değeri kontrol karakteri taşıyamaz")
        satirlar.append(f"{ad}: {deger}")
    satirlar.append("Connection: close")
    if isinstance(govde, str):
        govde = govde.encode("utf-8")
    if govde is not None and not isinstance(govde, bytes):
        raise ValueError("Gövde metin, bytes veya None olmalı")
    if govde is not None:
        satirlar.append(f"Content-Length: {len(govde)}")
    return ("\r\n".join(satirlar) + "\r\n\r\n").encode("iso-8859-1") + (govde or b"")


import socket


def yanit_coz(ham, yontem="GET"):
    bas, ayirici, govde = ham.partition(b"\r\n\r\n")
    if not ayirici:
        raise ValueError("Başlık bölümü eksik")
    satirlar = bas.decode("iso-8859-1").split("\r\n")
    m = re.fullmatch(r"HTTP/1\.[01] ([2-5][0-9]{2})(?: .*)?", satirlar[0])
    if not m:
        raise ValueError("Bu projede yalnız nihai HTTP/1.x yanıtları var")
    durum = int(m[1])
    tablo = {}
    for satir in satirlar[1:]:
        ad, sep, deger = satir.partition(":")
        if not sep or not re.fullmatch(r"[!#$%&'*+.^_`|~0-9A-Za-z-]+", ad):
            raise ValueError("Bozuk başlık")
        if any((ord(c) < 32 and c != "\t") or ord(c) == 127 for c in deger):
            raise ValueError("Bozuk başlık değeri")
        tablo.setdefault(ad.lower(), []).append(deger.strip(" \t"))
    if yontem == "HEAD" or durum in (204, 304):
        return durum, tablo, b""
    if "transfer-encoding" in tablo:
        if "content-length" in tablo or [v.lower() for v in tablo["transfer-encoding"]] != ["chunked"]:
            raise ValueError("Belirsiz veya desteklenmeyen aktarım kodlaması")
        i, parcalar = 0, []
        while True:
            son = govde.find(b"\r\n", i)
            if son < 0:
                raise ValueError("Parça boy satırı eksik")
            boy_metin = govde[i:son].split(b";", 1)[0]
            if not re.fullmatch(rb"[0-9a-fA-F]+", boy_metin):
                raise ValueError("Bozuk parça boyu")
            boy = int(boy_metin, 16)
            i = son + 2
            if boy == 0:
                while True:
                    son = govde.find(b"\r\n", i)
                    if son < 0:
                        raise ValueError("Trailer sonu eksik")
                    trailer = govde[i:son]
                    i = son + 2
                    if not trailer:
                        return durum, tablo, b"".join(parcalar)
                    ad, sep, _ = trailer.partition(b":")
                    if not sep or not re.fullmatch(rb"[!#$%&'*+.^_`|~0-9A-Za-z-]+", ad):
                        raise ValueError("Bozuk trailer")
            if len(govde) < i + boy + 2 or govde[i + boy:i + boy + 2] != b"\r\n":
                raise ValueError("Eksik parça veya CRLF")
            parcalar.append(govde[i:i + boy])
            i += boy + 2
    if "content-length" in tablo:
        degerler = tablo["content-length"]
        if len(degerler) != 1 or not re.fullmatch(r"[0-9]+", degerler[0]):
            raise ValueError("Tek ve negatif olmayan Content-Length gerekli")
        boy = int(degerler[0])
        if len(govde) < boy:
            raise ValueError("Gövde belirtilen uzunluktan kısa")
        govde = govde[:boy]
    return durum, tablo, govde


def gonder(yontem, url, govde=None, basliklar=None, azami=1048576):
    if not isinstance(azami, int) or azami < 1:
        raise ValueError("azami pozitif bayt sayısı olmalı")
    istek = istek_kur(yontem, url, basliklar, govde)
    u = urlsplit(url)
    parcalar, toplam = [], 0
    with socket.create_connection((u.hostname, u.port or 80), timeout=3) as soket:
        soket.sendall(istek)
        while True:
            parca = soket.recv(4096)
            if not parca:
                break
            toplam += len(parca)
            if toplam > azami:
                raise ValueError("Yanıt boy sınırını aştı")
            parcalar.append(parca)
    return yanit_coz(b"".join(parcalar), yontem)
```

```hint
recv parçalarının sınırları başlık veya gövde sınırlarıyla örtüşmek zorunda değildir; önce baytları biriktir.
```

```hint
Chunk uzunluğundan sonra veri tam boyda ve ardından CRLF olmalı. 0 parçasından sonra boş trailer satırına kadar ilerle.
```

:::

::: anlat Taşıma bağımlılığını değiştir, oturum kuralını koru
Son görevde taşıyıcıyı `Istemci(gonder)` ile dışarıdan veriyoruz. İkinci görevin `gonder` fonksiyonunu bağladığında gerçek TCP çalışır; testte aynı sözleşmeli küçük fonksiyon yöntem, URL, gövde ve başlıkları kaydeder. Test taşıyıcı `(durum, {küçük_ad: [değerler]}, bayt)` döndürür. Bu sayede 301/302/303/307/308 ve sınırda zincirler, sunucuya yeni uç nokta eklemeden sınanır.

Bu sınıf ilk isteğin kökenine bağlıdır: şema, host, etkin port değişirse **yeni hedefi çağırmadan** ValueError verir; sonraki isteklerde de aynı kural geçerlidir. `:80` ile portsuz http aynı kökendir. Çerezler bu dar laboratuvarda yalnız ad/değer ve Max-Age silme kuralıyla saklanır; Path/Domain/Secure/SameSite, son kullanma saatleri ve tam tarayıcı çerez kavanozu uygulanmaz. Testler Max-Age için -1/0/1'i ayırır; pozitif değerde süreyi ölçmez.

303'te HEAD korunur, diğer yöntemler GET'e döner. POST için 301/302'de GET'e dönmek yaygın istemci davranışıdır; RFC izin verir. 307/308'de yöntem/gövde korunur. Yöntem GET'e dönünce gövde ve gövde başlıkları kaldırılır. Location taşımayan yanıtı olduğu gibi döndür; bir Location olması her durum kodunu yönlendirme yapmaz.
:::

::: gorev 3 · Oturum ve yönlendirme motoru
`Istemci(gonder)` sınıfı yaz. `istek(yontem,url,govde=None,basliklar=None)` sonunda `(durum,basliklar,govde_bayt,son_url)` döndürsün. Metni UTF-8 bayta çevir; taşıyıcı her çağrıda `(yöntem, URL, gövde, başlık çiftleri listesi)` alır.

- Her yanıttan (yönlendirme dahil) Set-Cookie listesini al; ilk ad=değer çiftini sakla, değerdeki sonraki = karakterlerini koru. Max-Age adını harften bağımsız oku; <=0 siler, pozitif/yoksa saklar. `cerezler` sözlüğü görünür olsun. Sonraki isteğe tek Cookie başlığında ekle. Girişteki çerez satırlarının biçiminin geçerli olduğunu ve Path=/ olduğunu varsayabilirsin; çağıran Cookie başlığı vermiyor.
- Yalnız 301/302/303/307/308 + Location varken izle. Location'ı mevcut URL'ye göre çöz, fragment'i at. Anlatımdaki yöntem kurallarını uygula; dönüşümde Content-Type, Content-Length, Transfer-Encoding başlıklarını adın harf durumuna bakmadan sil, diğerlerini koru.
- En fazla 5 yönlendirme izle. 6. yönlendirme yanıtı gelince hedefe gitmeden RuntimeError. İlk kökenin dışına hiçbir çağrı gönderme; http dışını, URL kimlik bilgisini ve geçersiz portu ValueError ile reddet. Başlangıç isteği sayılmaz.

```starter
class Istemci:
    def __init__(self, gonder):
        self.gonder = gonder
        self.cerezler = {}

    def istek(self, yontem, url, govde=None, basliklar=None):
        return 200, {}, b"", url
```

```test
need("Istemci","sınıf")
from urllib.parse import urlsplit
def yol(url): return urlsplit(url).path
S="http://pafta.test:8080"
for n in (0,1,4,5,6):
    iz=[]
    def zincir(y,u,g,b):
        iz.append(u); kalan=int(yol(u).rsplit("/",1)[1])
        return (302,{"location":[str(kalan-1)]},b"") if kalan else (200,{},b"son")
    i=Istemci(zincir)
    if n<=5:
        eq(i.istek("GET",S+f"/z/{n}")[:3],(200,{},b"son"),"0–5 yönlendirme")
    else:
        raises(RuntimeError,i.istek,"GET",S+f"/z/{n}",msg="6. yönlendirmeyi izleme")
    eq(len(iz),min(n+1,6),"sınırda istek sayısı")
for durum in (301,302,303,307,308):
    for yontem in ("POST","PUT","HEAD"):
        iz=[]
        def yonlendir(y,u,g,b):
            iz.append((y,u,g,list(b)))
            return (durum,{"location":["../son?x=1#parca"]},b"") if len(iz)==1 else (200,{},b"son")
        i=Istemci(yonlendir)
        sonuc=i.istek(yontem,S+"/a/b", "Ağ",[("cOnTeNt-TyPe","text/plain"),("Content-Length","3"),("X-Kalsin","1")])
        degisti=(durum==303 and yontem!="HEAD") or (durum in(301,302) and yontem=="POST")
        eq(iz[1][0],"GET" if degisti else yontem,"yöntem kuralı")
        eq(iz[1][2],None if degisti else "Ağ".encode(),"gövde kuralı")
        eq(iz[1][3],[("X-Kalsin","1")] if degisti else [("cOnTeNt-TyPe","text/plain"),("Content-Length","3"),("X-Kalsin","1")],"gövde başlıkları yalnız GET dönüşümünde silinir")
        eq(sonuc[3],S+"/son?x=1","göreli Location, fragment gönderilmez")
for kod in (200,300,304,305,306,309,404):
    iz=[]
    def dur(y,u,g,b): iz.append(u); return kod,{"location":["/son"]},b"x"
    eq(Istemci(dur).istek("GET",S+"/")[0],kod,"yönlendirme olmayan kod")
    eq(len(iz),1,"fazladan istek yok")
def konumsuz(y,u,g,b): return 302,{},b"yer yok"
eq(Istemci(konumsuz).istek("GET",S+"/")[2],b"yer yok","Location yoksa yanıtı döndür")
for omur in (-1,0,1):
    iz=[]
    def cerez(y,u,g,b):
        iz.append(list(b))
        if len(iz)==1: return 303,{"set-cookie":["oturum=a=b; Path=/", "tema=koyu; Max-Age=1"],"location":["/iki"]},b""
        if len(iz)==2: return 200,{"set-cookie":[f"oturum=son; mAx-AgE={omur}"]},b"ok"
        return 200,{},b"ok"
    i=Istemci(cerez); i.istek("GET",S+"/bir"); i.istek("GET",S+"/uc")
    eq(iz[1],[("Cookie","oturum=a=b; tema=koyu")],"303'teki iki Set-Cookie taşınır, = korunur")
    eq(i.cerezler,{"tema":"koyu"} if omur<=0 else {"oturum":"son","tema":"koyu"},"Max-Age eksi/sıfır/bir")
    eq(iz[2],[("Cookie","tema=koyu" if omur<=0 else "oturum=son; tema=koyu")],"silme sonraki istekte görünür")
for adres in ("http://diger.test/", "http://pafta.test:8081/", "https://pafta.test:8080/"):
    iz=[]
    def disari(y,u,g,b): iz.append(u); return 302,{"location":[adres]},b""
    raises(ValueError,Istemci(disari).istek,"GET",S+"/",msg="köken dışına gitme")
    eq(iz,[S+"/"],"diğer kökene callback çağrılmaz")
iz=[]
def kaydet(y,u,g,b): iz.append(u); return 200,{},b""
i=Istemci(kaydet); i.istek("GET","http://pafta.test/")
i.istek("GET","http://pafta.test:80/a")
eq(len(iz),2,"varsayılan port aynı kökendir")
raises(ValueError,i.istek,"GET","http://diger.test/",msg="yeni çağrıda da aynı köken")
import tezgah, json
def gercek(y,u,g,b):
    p=urlsplit(u); hedef=(p.path or "/")+("?"+p.query if p.query else "")
    satirlar=[f"{y} {hedef} HTTP/1.1",f"Host: {p.netloc}","Connection: close"]+[f"{a}: {d}" for a,d in b]
    if g is not None: satirlar.append(f"Content-Length: {len(g)}")
    ham=("\r\n".join(satirlar)+"\r\n\r\n").encode()+ (g or b"")
    r=tezgah.yanit(ham)
    tablo={}
    for ad,deger in r.basliklar:
        tablo.setdefault(ad.lower(),[]).append(deger)
    return r.durum,tablo,r.govde_bayt
i=Istemci(gercek); s=tezgah.SUNUCU
d,b,g,u=i.istek("POST",s+"/giris","kullanici=ayse&parola=pafta-demo",[("Content-Type","application/x-www-form-urlencoded")])
eq((d,u),(200,s+"/panel"),"gerçek giriş ve 303 çerezi")
ok("Hoş geldin, ayse" in g.decode(),"panel")
i.istek("POST",s+"/cikis",b"")
eq(i.istek("GET",s+"/panel")[3],s+"/giris","gerçek Max-Age=0 çıkışı")
```

```solution
from urllib.parse import urldefrag, urljoin, urlsplit


class Istemci:
    def __init__(self, gonder):
        self.gonder = gonder
        self.cerezler = {}
        self.koken = None

    def istek(self, yontem, url, govde=None, basliklar=None):
        if isinstance(govde, str):
            govde = govde.encode("utf-8")
        basliklar = list(basliklar or [])
        sayac = 0
        url = urldefrag(url).url
        while True:
            u = urlsplit(url)
            if u.scheme != "http" or not u.hostname or u.username is not None or u.password is not None:
                raise ValueError("Kimlik bilgisi taşımayan http URL gerekli")
            port = u.port if u.port is not None else 80
            if not 1 <= port <= 65535:
                raise ValueError("Geçersiz port")
            koken = (u.scheme, u.hostname, port)
            if self.koken is None:
                self.koken = koken
            if koken != self.koken:
                raise ValueError("Bu eğitim istemcisi tek kökenlidir")
            giden = list(basliklar)
            if self.cerezler:
                giden.append(("Cookie", "; ".join(f"{ad}={deger}" for ad, deger in self.cerezler.items())))
            durum, tablo, sonuc = self.gonder(yontem, url, govde, giden)
            for satir in tablo.get("set-cookie", []):
                ilk, *oznitelikler = satir.split(";")
                ad, _, deger = ilk.partition("=")
                ad = ad.strip()
                omur = None
                for oz in oznitelikler:
                    anahtar, sep, deger_oz = oz.strip().partition("=")
                    if anahtar.lower() == "max-age" and sep:
                        omur = int(deger_oz)
                if omur is not None and omur <= 0:
                    self.cerezler.pop(ad, None)
                else:
                    self.cerezler[ad] = deger.strip()
            if durum not in {301, 302, 303, 307, 308} or not tablo.get("location"):
                return durum, tablo, sonuc, url
            if sayac >= 5:
                raise RuntimeError("En fazla beş yönlendirme izlenir")
            sayac += 1
            if (durum == 303 and yontem != "HEAD") or (durum in (301, 302) and yontem == "POST"):
                yontem, govde = "GET", None
                basliklar = [(ad, deger) for ad, deger in basliklar
                             if ad.lower() not in {"content-type", "content-length", "transfer-encoding"}]
            url = urldefrag(urljoin(url, tablo["location"][-1])).url
```

```hint
Tek isteği callback yapar. Sınıfın görevi döngü, çerez ve yöntem politikasıdır; gövdeyi ikinci kez encode etme.
```

```hint
5 yönlendirme 6 istek demektir. Sayaç 5 iken yeni bir yönlendirme gelirse hedefe gitmeden dur.
```

```hint
303 yanıtındaki Set-Cookie önce alınır; sonra sonraki isteğin Cookie başlığı hazırlanır.
```

:::

