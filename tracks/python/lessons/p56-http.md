---
id: p56
title: HTTP'yi Elle Kurmak
summary: İstek ve yanıtın anatomisi, urllib.parse, yerel http.server ile küçük bir API ve urllib istemcisi.
kazanim: PCPP1 4.1, PCPP1 4.4
---

::: anlat HTTP bir metin protokolüdür
Web'in dili HTTP, TCP üzerinden giden **düz metindir** (HTTP/1.1 için). Bir istek şuna benzer:

```text
GET /api/kullanici?id=7 HTTP/1.1        ← istek satırı: yöntem, yol, sürüm
Host: ornek.com                         ← başlıklar: Ad: değer
User-Agent: curl/8.0
Accept: application/json
                                        ← boş satır = başlıklar bitti
(gövde: GET'te genelde yok)
```

Yanıt da aynı yapıda:

```text
HTTP/1.1 200 OK                         ← durum satırı
Content-Type: application/json
Content-Length: 27

{"id": 7, "ad": "ayse"}
```

Satırlar `\r\n` ile ayrılır. Başlık adları büyük-küçük harfe duyarsızdır.

```python
istek = "POST /giris HTTP/1.1\r\nHost: ornek.com\r\nContent-Type: application/json\r\nContent-Length: 18\r\n\r\n{\"kullanici\":\"ali\"}"
bas, govde = istek.split("\r\n\r\n", 1)       #! başlık ile gövdeyi boş satırdan ayır
ilk, *basliklar = bas.split("\r\n")
yontem, yol, surum = ilk.split(" ")
alanlar = {}
for b in basliklar:
    ad, deger = b.split(":", 1)
    alanlar[ad.strip().lower()] = deger.strip()
print(yontem, yol, surum)
print(alanlar)
print(govde)
```

### urllib.parse: URL'leri parçala
```python
from urllib.parse import urlparse, parse_qs, urlencode, quote, unquote

u = urlparse("https://ornek.com:8443/ara?q=python+soket&sayfa=2#sonuc")
print(u.scheme, u.hostname, u.port, u.path, u.fragment)
print(parse_qs(u.query))                       #! değerler LİSTE: ?a=1&a=2 olabilir
print(urlencode({"q": "ağ güvenliği", "s": 1})) #! sözlük → sorgu metni
print(quote("rapor 2026/ç.pdf"), unquote("%C3%A7"))
```

> [!GÜVENLİK]
> Web güvenliğinin büyük kısmı bu metinlerin **yanlış yorumlanmasından** doğar: iki farklı sunucu `Content-Length` ile `Transfer-Encoding` başlıklarını farklı yorumlarsa **request smuggling**, kullanıcı girdisi başlığa `\r\n` sokabilirse **header injection** olur. Yol içindeki `%2e%2e%2f` ise P28'deki dizin aşmanın URL kodlanmış halidir. Çözümlemeyi her zaman kendi elle yazdığın kodla değil, test edilmiş kütüphanelerle yap ve gelen veriyi **çözdükten sonra** doğrula.
:::

::: tahmin
Çıktı tek satır:

```python
istek = "GET /admin?x=1 HTTP/1.1\r\nHost: ornek.com\r\nUser-Agent: curl/8.0\r\n\r\n"
ilk, *basliklar = istek.split("\r\n")
yontem, yol, surum = ilk.split()
print(yontem, yol.split("?")[0], len([b for b in basliklar if b]))
```

???

`GET /admin 2`. Sondaki `\r\n\r\n` bölünce iki boş metin üretir; onlar elenince iki başlık kalır.
:::

::: anlat Yerel bir API sunucusu ve istemcisi
Python'un `http.server` modülü küçük sunucular için yeterlidir (üretim için değil). Bir istek işleyici sınıf yazıp `do_GET` / `do_POST` metotlarını doldurursun:

```python
import json, threading, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

class Api(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/durum":
            self.yanit(200, {"durum": "ok", "surum": "1.0"})
        else:
            self.yanit(404, {"hata": "bulunamadı"})

    def yanit(self, kod, veri):
        govde = json.dumps(veri).encode()
        self.send_response(kod)                                  #! durum satırı
        self.send_header("Content-Type", "application/json")     #! başlıklar
        self.send_header("Content-Length", str(len(govde)))
        self.end_headers()                                       #! boş satır
        self.wfile.write(govde)                                  #! gövde

    def log_message(self, *a):                                   #! her isteği stderr'e yazmasın
        pass

sunucu = ThreadingHTTPServer(("127.0.0.1", 0), Api)
threading.Thread(target=sunucu.serve_forever, daemon=True).start()
taban = f"http://127.0.0.1:{sunucu.server_address[1]}"

with urllib.request.urlopen(taban + "/durum", timeout=3) as r:  #! istemci
    print(r.status, r.headers["Content-Type"], json.loads(r.read()))
try:
    urllib.request.urlopen(taban + "/yok", timeout=3)
except urllib.error.HTTPError as e:                              #! 4xx/5xx istisna olarak gelir
    print(e.code, json.loads(e.read()))
sunucu.shutdown()
```

> [!NOT]
> Gerçek projelerde istemci tarafında `requests` ya da `httpx` kütüphaneleri (`pip install`), sunucu tarafında Flask/FastAPI kullanılır. Ama ikisinin de altında bu paftadaki satırlar vardır. `urllib` standart kütüphanede olduğu için kurulum gerektirmez; bir sunucuda pip kurulamıyorsa hayat kurtarır.

> [!DERİN]
> `urllib.request` sistemin vekil sunucu (proxy) ayarlarını otomatik kullanır. Kurumsal ağlarda `127.0.0.1` isteklerinin bile vekile gitmesi bu yüzden "bende çalışıyor" türü sorunlara yol açar. Vekili kapatmak için: `urllib.request.build_opener(urllib.request.ProxyHandler({}))`. Bu paftanın testleri bunu kullanıyor.
:::

::: tahmin
İki satır:

```python
from urllib.parse import urlparse, parse_qs, quote
u = urlparse("https://ornek.com:8443/ara?q=python&sayfa=2#sonuc")
print(u.hostname, u.port, u.path, parse_qs(u.query)["sayfa"])
print(quote("a b/ç"))
```

???

`ornek.com 8443 /ara ['2']`, sonra `a%20b/%C3%A7`. parse_qs değerleri her zaman liste olarak verir. `quote` varsayılan olarak `/` karakterini kodlamaz; "ç" UTF-8'in iki baytı olarak kodlanır.
:::

::: gorev İstek ayrıştırıcı
`istek_coz(ham)` fonksiyonu ham bir HTTP isteğini (metin) ayrıştırıp şu sözlüğü döndürsün:

```python
{"yontem": "POST", "yol": "/giris", "sorgu": {"a": "1"}, "surum": "HTTP/1.1",
 "basliklar": {"host": "ornek.com", ...}, "govde": "..."}
```

- Başlık adları **küçük harfe** çevrilsin, değerlerin kenar boşlukları temizlensin
- `sorgu`: yoldaki `?` sonrası; her anahtarın **ilk** değeri (yoksa boş sözlük). `yol` sorgusuz olsun
- Boş satırdan sonraki her şey gövde; yoksa `""`

```starter
from urllib.parse import parse_qs

def istek_coz(ham):
    pass
```

```test
need("istek_coz")
h = "POST /giris?dil=tr&dil=en&x=1 HTTP/1.1\r\nHost: ornek.com\r\nContent-Type:  application/json \r\nX-Iz: a:b\r\n\r\n{\"k\": 1}"
r = istek_coz(h)
eq(r["yontem"], "POST", "yöntem")
eq(r["yol"], "/giris", "sorgusuz yol")
eq(r["sorgu"], {"dil": "tr", "x": "1"}, "sorgu (ilk değerler)")
eq(r["surum"], "HTTP/1.1", "sürüm")
eq(r["basliklar"], {"host": "ornek.com", "content-type": "application/json", "x-iz": "a:b"}, "başlıklar (değerde : olabilir)")
eq(r["govde"], '{"k": 1}', "gövde")
r2 = istek_coz("GET / HTTP/1.0\r\n\r\n")
eq((r2["yol"], r2["sorgu"], r2["basliklar"], r2["govde"]), ("/", {}, {}, ""), "en sade istek")
```

```solution
from urllib.parse import parse_qs

def istek_coz(ham):
    bas, _, govde = ham.partition("\r\n\r\n")
    ilk, *satirlar = bas.split("\r\n")
    yontem, tam_yol, surum = ilk.split(" ")
    yol, _, sorgu_metni = tam_yol.partition("?")
    sorgu = {k: v[0] for k, v in parse_qs(sorgu_metni).items()}
    basliklar = {}
    for s in satirlar:
        if not s:
            continue
        ad, deger = s.split(":", 1)
        basliklar[ad.strip().lower()] = deger.strip()
    return {"yontem": yontem, "yol": yol, "sorgu": sorgu, "surum": surum,
            "basliklar": basliklar, "govde": govde}
```

```hint
`ham.partition("\r\n\r\n")` başlık bölümünü ve gövdeyi ayırır (boş satır yoksa gövde `""` olur).
```

```hint
Başlıkta değerin içinde de `:` olabilir: `split(":", 1)`. Sorgu için `tam_yol.partition("?")` ve `parse_qs`.
```
:::

::: gorev Sağlık kontrolü uç noktası
`SaglikIsleyici` adında bir `BaseHTTPRequestHandler` alt sınıfı yaz:

- `GET /saglik` → **200**, gövde JSON `{"durum": "ok"}`
- başka her yol → **404**, gövde JSON `{"hata": "bulunamadı"}`
- Her yanıtta `Content-Type: application/json` ve `X-Content-Type-Options: nosniff` başlıkları olsun
- `log_message`'ı sustur

Testler sınıfını yerel bir sunucuda başlatıp istek atacak.

```starter
import json
from http.server import BaseHTTPRequestHandler

class SaglikIsleyici(BaseHTTPRequestHandler):
    pass
```

```meta
timeout: 15
```

```test
import json, threading, urllib.request, urllib.error
from http.server import ThreadingHTTPServer
I = need("SaglikIsleyici", "sınıf")
sunucu = ThreadingHTTPServer(("127.0.0.1", 0), I)
threading.Thread(target=sunucu.serve_forever, daemon=True).start()
taban = f"http://127.0.0.1:{sunucu.server_address[1]}"
acici = urllib.request.build_opener(urllib.request.ProxyHandler({}))
try:
    with acici.open(taban + "/saglik", timeout=3) as r:
        eq(r.status, 200, "/saglik → 200")
        eq(json.loads(r.read()), {"durum": "ok"}, "gövde {'durum': 'ok'}")
        eq(r.headers.get("Content-Type"), "application/json", "Content-Type")
        eq(r.headers.get("X-Content-Type-Options"), "nosniff", "nosniff başlığı")
    try:
        acici.open(taban + "/admin", timeout=3)
        ok(False, "/admin 404 vermeli")
    except urllib.error.HTTPError as e:
        eq(e.code, 404, "/admin → 404")
        eq(json.loads(e.read()), {"hata": "bulunamadı"}, "404 gövdesi")
        eq(e.headers.get("X-Content-Type-Options"), "nosniff", "404'te de nosniff")
finally:
    sunucu.shutdown()
```

```solution
import json
from http.server import BaseHTTPRequestHandler

class SaglikIsleyici(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/saglik":
            self._yanit(200, {"durum": "ok"})
        else:
            self._yanit(404, {"hata": "bulunamadı"})

    def _yanit(self, kod, veri):
        govde = json.dumps(veri, ensure_ascii=False).encode("utf-8")
        self.send_response(kod)
        self.send_header("Content-Type", "application/json")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(govde)))
        self.end_headers()
        self.wfile.write(govde)

    def log_message(self, *args):
        pass
```

```hint
Sıra önemli: `send_response`, sonra `send_header`'lar, sonra `end_headers`, en son `self.wfile.write(govde)`.
```
:::

::: gorev JSON istemcisi
`json_getir(url)` fonksiyonu verilen adrese GET isteği atsın (3 saniye zaman aşımı, vekil kullanmadan), yanıt gövdesini JSON olarak çözüp döndürsün. Sunucu 4xx/5xx dönerse `RuntimeError(f"HTTP {kod}")` yükseltsin.

```starter
import json, urllib.request, urllib.error

def json_getir(url):
    pass
```

```meta
timeout: 15
```

```test
import json, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
need("json_getir")
class H(BaseHTTPRequestHandler):
    def do_GET(self):
        kod, veri = (200, {"liste": [1, 2], "ad": "ağ"}) if self.path == "/veri" else (503, {"hata": "bakım"})
        g = json.dumps(veri).encode()
        self.send_response(kod); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(g))); self.end_headers(); self.wfile.write(g)
    def log_message(self, *a):
        pass
s = ThreadingHTTPServer(("127.0.0.1", 0), H)
threading.Thread(target=s.serve_forever, daemon=True).start()
taban = f"http://127.0.0.1:{s.server_address[1]}"
try:
    eq(json_getir(taban + "/veri"), {"liste": [1, 2], "ad": "ağ"}, "JSON gövdesi çözülmeli")
    try:
        json_getir(taban + "/bakim")
        ok(False, "503 → RuntimeError")
    except RuntimeError as e:
        eq(str(e), "HTTP 503", "mesaj 'HTTP 503'")
finally:
    s.shutdown()
```

```solution
import json, urllib.request, urllib.error

def json_getir(url):
    acici = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with acici.open(url, timeout=3) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}") from e
```

```hint
`urllib.request.build_opener(urllib.request.ProxyHandler({}))` vekilsiz bir açıcı verir; `acici.open(url, timeout=3)`.
```

```hint
4xx/5xx yanıtlar `urllib.error.HTTPError` olarak yükselir; `e.code` durum kodudur.
```
:::
