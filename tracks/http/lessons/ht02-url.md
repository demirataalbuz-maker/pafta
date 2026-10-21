---
id: ht02
title: URL'ler ve Yüzde Kodlama
summary: Bir URL'nin parçaları ve hangisinin isteğe nasıl girdiği, varsayılan portlar, sunucuya hiç gitmeyen parça (#), yüzde kodlama ve UTF-8, yolda %20 ile sorguda +, çift çözme tuzağı ve göreli adresleri urljoin ile çözmek.
---

::: anlat Bir URL'nin parçaları
```text
https://ayse@belgeler.pafta.test:8443/api/biletler?durum=açık&sayfa=2#ozet
```

| Parça | Örnek | Not |
|---|---|---|
| şema | `https` | `http` → varsayılan port 80, `https` → 443 |
| kullanıcı bilgisi | `ayse@` | eski bir biçim; tarayıcılar uyarır, isteğe girmez |
| host | `belgeler.pafta.test` | `Host` başlığına gider |
| port | `8443` | yazılmazsa şemanın varsayılanı |
| yol | `/api/biletler` | |
| sorgu | `durum=açık&sayfa=2` | `?` sonrası, `&` ile ayrılmış `ad=değer` çiftleri |
| parça | `ozet` | `#` sonrası; **sunucuya hiç gönderilmez**, yalnızca tarayıcı kullanır |

Bu URL için tarayıcının göndereceği istek şudur. İstek hedefi yalnızca **yol ve sorgudur**; port varsayılan olmadığı için `Host` başlığına eklenir; Türkçe harfler kodlanır (aşağıda):

```text
GET /api/biletler?durum=a%C3%A7%C4%B1k&sayfa=2 HTTP/1.1
Host: belgeler.pafta.test:8443
```

Python'da `urllib.parse.urlsplit` URL'yi parçalarına ayırır:

```python
from urllib.parse import urlsplit

u = urlsplit("https://ayse@belgeler.pafta.test:8443/api/biletler?durum=açık&sayfa=2#ozet")
print(u.scheme, u.hostname, u.port, u.path)
print(u.query, u.fragment, u.username)
print(urlsplit("http://pafta.test/durum").port)      #! port yazılmadıysa None
```

> [!TUZAK]
> `urlsplit(...).port` port yazılmamışsa `None` döndürür, 80 değil. Varsayılanı şemaya bakarak sen koyarsın. Şema ve host da büyük-küçük harfe duyarsızdır (`hostname` küçük harfe çevrilmiş döner); yol ise duyarlıdır: `/Durum` ile `/durum` iki ayrı adrestir.
:::

::: anlat Yüzde kodlama
Bir URL'de yalnızca ASCII'nin küçük bir kısmı olduğu gibi yazılabilir. Geri kalan her karakter önce **UTF-8 baytlarına** çevrilir, sonra her bayt `%` ve iki onaltılık rakamla yazılır: `ç` iki bayttır (`C3 A7`) ve `%C3%A7` olur.

Anlamı olan karakterler (`/ ? # & = + %` ve boşluk) **veri olarak** geçiyorsa onlar da kodlanır. Yoksa `not=a&b` bir değer değil, iki ayrı parametre olur.

| Yer | Boşluk | Araç |
|---|---|---|
| yol | `%20` | `quote(metin)`: `/` korunur |
| sorgu ve form gövdesi | `+` | `urlencode(sözlük)`, `quote_plus(metin)` |
| geri çözmek | | `unquote`, `unquote_plus`, `parse_qsl` |

```python
from urllib.parse import quote, urlencode, parse_qsl

print(quote("/raporlar/2026 ekim/özet.pdf"))
print(urlencode({"q": "disk dolu", "sehir": "İzmir", "not": "a&b=c"}))
print(parse_qsl("q=disk+dolu&sehir=%C4%B0zmir"))
```

Tezgahtaki `/yanki` adresi, aldığı isteği olduğu gibi geri anlatır. Sunucunun kodlanmış sorguyu nasıl çözdüğünü görmek için ideal:

```python
import tezgah

y = tezgah.yanit("GET /yanki?q=disk+dolu&not=a%26b&sehir=%C4%B0zmir HTTP/1.1\r\nHost: pafta.test\r\n\r\n")
print(y.json()["sorgu"])
```

> [!TUZAK]
> Kodlamayı **bir kez** yap ve **bir kez** çöz. `%2541` bir kez çözülünce `%41`, ikinci kez çözülünce `A` olur. Girdiyi önce denetleyip sonra bir kez daha çözen sunucu, denetlediği değerle kullandığı değerin farklı olmasına yol açar. Kendi kodunda girdiyi tam olarak bir kez çöz ve denetimi çözülmüş değer üzerinde yap.
:::

::: anlat Göreli adresler
Bir sayfadaki bağlantıların çoğu **göreli** yazılır ve sayfanın kendi adresine göre çözülür. Kuralları `urllib.parse.urljoin` uygular. Sayfa `http://pafta.test/raporlar/haftalik/ozet.html` ise:

| Bağlantı | Sonuç |
|---|---|
| `tablo.csv` | `http://pafta.test/raporlar/haftalik/tablo.csv` (aynı klasör) |
| `../aylik/` | `http://pafta.test/raporlar/aylik/` (bir üst klasör) |
| `/giris` | `http://pafta.test/giris` (sitenin kökünden) |
| `?sayfa=2` | `http://pafta.test/raporlar/haftalik/ozet.html?sayfa=2` |
| `#ozet` | `http://pafta.test/raporlar/haftalik/ozet.html#ozet` (aynı sayfa) |
| `//cdn.pafta.test/site.css` | `http://cdn.pafta.test/site.css` (şemayı devralır) |
| `https://belgeler.pafta.test/` | olduğu gibi (zaten mutlak) |

```python
from urllib.parse import urljoin, urldefrag

taban = "http://pafta.test/raporlar/haftalik/ozet.html"
print(urljoin(taban, "../aylik/"))
print(urljoin(taban, "/giris"))
print(urldefrag(urljoin(taban, "tablo.csv#satir-3")).url)     #! parçayı at
```

Klasörün sonunda `/` olup olmaması sonucu değiştirir: `http://pafta.test/raporlar` adresindeki `ozet.html`, `http://pafta.test/ozet.html` olur; `raporlar` bir dosya adı sayılır.
:::

::: tahmin
Dört satır. Hangileri?

```python
from urllib.parse import urljoin, quote, urlsplit

taban = "http://pafta.test/raporlar/haftalik/ozet.html"
print(urljoin(taban, "../aylik/ekim.html"))
print(urljoin(taban, "giris"))
print(quote("özet 2026.pdf"))
print(urlsplit("http://pafta.test:80/a?b=1#c").port)
```

???

`http://pafta.test/raporlar/aylik/ekim.html`, `http://pafta.test/raporlar/haftalik/giris`, `%C3%B6zet%202026.pdf` ve `80`. `../` bir üst klasöre çıkar. `/` ile başlamayan `giris` sayfanın klasörüne göre çözülür, sitenin köküne göre değil. `quote` `ö`'yü iki UTF-8 baytına (`%C3%B6`), yoldaki boşluğu `%20`'ye çevirir. Port açıkça yazıldığı için `80` döner; yazılmasaydı `None` olurdu.
:::

::: gorev Hedef ve Host
`hedef_ve_host(url)` fonksiyonu bir URL için isteğe yazılacak iki şeyi döndürsün: `(istek_hedefi, host_basligi)`.

- istek hedefi: yol (boşsa `/`), sorgu varsa `?` ile sorgu; parça (`#...`) **atılır**
- `Host` başlığı: host adı; port açıkça yazılmışsa ve şemanın varsayılanı değilse (`http` → 80, `https` → 443) `host:port`

```starter
from urllib.parse import urlsplit

def hedef_ve_host(url):
    u = urlsplit(url)
    return u.path, u.hostname
```

```test
import tezgah
need("hedef_ve_host")
eq(hedef_ve_host("http://pafta.test/durum"), ("/durum", "pafta.test"), "sade adres")
eq(hedef_ve_host("http://pafta.test"), ("/", "pafta.test"), "boş yol → /")
eq(hedef_ve_host("https://pafta.test:443/a?b=1#c"), ("/a?b=1", "pafta.test"), "https'te 443 varsayılan; parça atılır")
eq(hedef_ve_host("http://pafta.test:80/"), ("/", "pafta.test"), "http'de 80 varsayılan")
eq(hedef_ve_host("http://pafta.test:8080/x"), ("/x", "pafta.test:8080"), "varsayılan olmayan port")
eq(hedef_ve_host("https://pafta.test:80/x"), ("/x", "pafta.test:80"), "https'te 80 varsayılan değildir")
eq(hedef_ve_host("http://pafta.test:443/x"), ("/x", "pafta.test:443"), "http'de 443 varsayılan değildir")
eq(hedef_ve_host("http://PAFTA.test/Rapor?Q=1"), ("/Rapor?Q=1", "pafta.test"), "host küçük harf, yol olduğu gibi")
hedef, host = hedef_ve_host(tezgah.SUNUCU + "/sunucular?rol=db#liste")
y = tezgah.yanit(f"GET {hedef} HTTP/1.1\r\nHost: {host}\r\n\r\n")
eq((y.durum, [s["ad"] for s in y.json()]), (200, ["db01"]), "tezgahta: sorgu gider, parça gitmez")
```

```solution
from urllib.parse import urlsplit

VARSAYILAN = {"http": 80, "https": 443}


def hedef_ve_host(url):
    u = urlsplit(url)
    hedef = u.path or "/"
    if u.query:
        hedef += "?" + u.query
    host = u.hostname
    if u.port is not None and u.port != VARSAYILAN.get(u.scheme):
        host += f":{u.port}"
    return hedef, host
```

```hint
`u.path or "/"` boş yolu düzeltir. Parçayı (`u.fragment`) hiç kullanma.
```

```hint
Varsayılan portları bir sözlükte tut: `{"http": 80, "https": 443}`. `u.port` `None` değilse ve şemanın varsayılanına eşit değilse `Host`'a ekle.
```
:::

::: gorev Sorgulu yol
`sorgulu_yol(yol, parametreler)` fonksiyonu bir yola, `parametreler` sözlüğünü doğru kodlanmış bir sorgu olarak eklesin. Sözlük boşsa `?` de eklenmesin. Sunucu sorguyu çözdüğünde aynı sözlüğü bulmalı: boşluk, `&`, `=`, `+` ve Türkçe harfler dahil.

```starter
def sorgulu_yol(yol, parametreler):
    return yol + "?" + "&".join(f"{k}={v}" for k, v in parametreler.items())
```

```test
import tezgah
need("sorgulu_yol")
eq(sorgulu_yol("/sunucular", {}), "/sunucular", "boş sözlük: ? yok")
eq(sorgulu_yol("/sunucular", {"rol": "web"}), "/sunucular?rol=web", "tek parametre")
for p in [{"q": "disk dolu", "not": "a&b=c"}, {"sehir": "İzmir", "x": "1+1"}, {"bos": "", "y": "%41"}]:
    y = tezgah.yanit(f"GET {sorgulu_yol('/yanki', p)} HTTP/1.1\r\nHost: pafta.test\r\n\r\n")
    eq(y.json()["sorgu"], p, f"sunucu aynı değerleri buluyor: {p}")
```

```solution
from urllib.parse import urlencode


def sorgulu_yol(yol, parametreler):
    if not parametreler:
        return yol
    return yol + "?" + urlencode(parametreler)
```

```hint
`urllib.parse.urlencode` her anahtarı ve değeri UTF-8 ve yüzde kodlamasıyla yazar, boşluğu `+`, `+`'yı `%2B` yapar.
```
:::

::: gorev Mutlak adres
`mutlak(sayfa_url, href)` fonksiyonu bir sayfadaki bağlantıyı, parçası atılmış mutlak bir adrese çevirsin. Şu durumlarda `None` döndürsün:

- `href` boşsa ya da yalnızca bir parçaysa (`#...`): aynı sayfa, yeni bir istek yok
- çözülen adresin şeması `http` ya da `https` değilse (`mailto:`, `javascript:`, `tel:`)

```starter
def mutlak(sayfa_url, href):
    return sayfa_url + href
```

```test
need("mutlak")
s = "http://pafta.test/raporlar/haftalik/ozet.html"
eq(mutlak(s, "tablo.csv"), "http://pafta.test/raporlar/haftalik/tablo.csv", "aynı klasör")
eq(mutlak(s, "../aylik/ekim.html#ust"), "http://pafta.test/raporlar/aylik/ekim.html", "üst klasör, parça atılır")
eq(mutlak(s, "/giris"), "http://pafta.test/giris", "kökten")
eq(mutlak(s, "?sayfa=2"), "http://pafta.test/raporlar/haftalik/ozet.html?sayfa=2", "yalnızca sorgu")
eq(mutlak(s, "//cdn.pafta.test/site.css"), "http://cdn.pafta.test/site.css", "şemayı devralır")
eq(mutlak(s, "https://belgeler.pafta.test/api"), "https://belgeler.pafta.test/api", "zaten mutlak")
eq(mutlak(s, "#ozet"), None, "yalnızca parça")
eq(mutlak(s, ""), None, "boş bağlantı")
eq(mutlak(s, "mailto:ekip@pafta.test"), None, "mailto")
eq(mutlak(s, "JavaScript:void(0)"), None, "javascript (büyük harfle)")
eq(mutlak(s, "HTTP://Pafta.test/A"), "http://Pafta.test/A", "büyük harfli http şeması da geçerli")
```

```solution
from urllib.parse import urldefrag, urljoin, urlsplit


def mutlak(sayfa_url, href):
    if not href or href.startswith("#"):
        return None
    adres = urldefrag(urljoin(sayfa_url, href)).url
    if urlsplit(adres).scheme not in ("http", "https"):
        return None
    return adres
```

```hint
`urljoin(sayfa_url, href)` göreli adresi çözer, `urldefrag(...).url` parçayı atar. `urlsplit(...).scheme` şemayı küçük harfle verir.
```
:::
