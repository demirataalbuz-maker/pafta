---
id: ht12
title: Kaynakta Ne Var?
summary: Sayfanın başka adreslere işaret eden öznitelikleri (href, src, action) ve göreli adreslerin çözülmesi, base etiketi, data-* öznitelikleri, gömülü JSON betikleri, kaynağın açığa vurduğu bilgiler ve istemci tarafı gizlemenin neden yetki denetiminin yerini tutmadığı.
---

::: anlat Bağlantılar ve kaynaklar
Bir sayfa başka adreslere birçok yerden işaret eder:

| Etiket | Öznitelik | Ne |
|---|---|---|
| `<a>` | `href` | bağlantı |
| `<link>` | `href` | stil dosyası, simge, önceden yükleme |
| `<script>` | `src` | betik |
| `<img>`, `<iframe>` | `src` | resim, gömülü sayfa |
| `<form>` | `action` | formun gönderileceği adres (HT11) |

Hepsi **sayfanın adresine göre** çözülür (HT02). Sayfada bir `<base href="...">` etiketi varsa göreli adresler onun adresine göre çözülür. Tezgahın kaynaklar sayfası:

```python
import tezgah

y = tezgah.yanit("GET /kaynaklar HTTP/1.1\r\nHost: pafta.test\r\n\r\n")
print(y.govde)
```

### data-* öznitelikleri ve gömülü JSON
`data-` ile başlayan öznitelikler sayfanın kendi betikleri için saklanan verilerdir: `<li data-sunucu="web01">`'i JavaScript `eleman.dataset.sunucu` diye okur. Birçok sayfa da ayarlarını bir betik etiketinin içine JSON olarak gömer:

```html
<script type="application/json" id="ayarlar">{"api": "/api/rapor", "surum": "2.4.1", "yenileme_sn": 30}</script>
```

`html.parser` bir `<script>`'in içeriğini olduğu gibi `handle_data`'ya verir; içindeki metin etiket diye ayrıştırılmaz.

```python
from html.parser import HTMLParser
import json
import tezgah

class Betikler(HTMLParser):
    def __init__(self):
        super().__init__()
        self.icinde = None
    def handle_starttag(self, etiket, oznitelikler):
        if etiket == "script":
            self.icinde = dict(oznitelikler)
    def handle_data(self, veri):
        if self.icinde is not None and veri.strip():
            print(self.icinde.get("id"), json.loads(veri)["api"])
    def handle_endtag(self, etiket):
        if etiket == "script":
            self.icinde = None

Betikler().feed(tezgah.yanit("GET /kaynaklar HTTP/1.1\r\nHost: pafta.test\r\n\r\n").govde)
```
:::

::: anlat Kaynak herkese açıktır
Bir sayfanın kaynağında görünen her şey, o sayfayı açan herkesin elindedir: yorumlar (HT10), gizli form alanları (HT11), betiklerin çağırdığı API adresleri, gömülü ayarlar, sürüm numaraları. Bir web uygulamasını inceleyen biri işe çoğu zaman buradan başlar: hangi adresler var, sayfa hangi uç noktaları çağırıyor, hangi parametreleri gönderiyor?

> [!GÜVENLİK]
> İstemci tarafında **gizlemek**, yetki denetimi değildir. Bir yönetim bağlantısını kullanıcıdan saklamak, bir düğmeyi devre dışı bırakmak ya da bir alanı JavaScript'le denetlemek yalnızca arayüzü değiştirir; adresi bilen herkes isteği doğrudan gönderebilir. Sunucu **her isteği** kimin gönderdiğine ve onun neye yetkisi olduğuna bakarak değerlendirmeli. Betiklere gömülen anahtarlar ve parolalar da herkese açıktır: gizli kalması gereken bir anahtar istemciye hiç gönderilmez. Başka sitelerden yüklenen betikler için `integrity` özniteliği (alt kaynak bütünlüğü), dosya değiştirilirse tarayıcının onu çalıştırmamasını sağlar.
:::

::: tahmin
Kaynaklar sayfasının bağlantıları, sayfanın adresine göre. Beş satır:

```python
from urllib.parse import urljoin

taban = "http://pafta.test/kaynaklar"
for href in ["/sunucular/web01", "../sunucular/db01", "/static/logo.png", "giris", "#liste"]:
    print(urljoin(taban, href))
```

???

`http://pafta.test/sunucular/web01`, `http://pafta.test/sunucular/db01`, `http://pafta.test/static/logo.png`, `http://pafta.test/giris` ve `http://pafta.test/kaynaklar#liste`. `/kaynaklar` sitenin kökündeki bir sayfadır; klasörü köktür. `../` kökten yukarı çıkamaz ve olduğu yerde kalır, bu yüzden `../sunucular/db01` de `/sunucular/db01` olur. `giris` kök klasöre göre çözülür. `#liste` aynı sayfanın bir parçasıdır.
:::

::: gorev Kaynak adresleri
`kaynak_adresleri(html, sayfa_url)` fonksiyonu sayfanın işaret ettiği bütün adresleri, mutlak ve parçası atılmış olarak, **tekrarsız ve sıralı** bir liste hâlinde döndürsün. Bakılacak öznitelikler: `a`, `link` → `href`; `script`, `img`, `iframe` → `src`; `form` → `action`. Boş değerleri, yalnızca parça olanları (`#...`) ve şeması `http`/`https` olmayanları (`mailto:`, `javascript:`, `data:`) atla.

```starter
def kaynak_adresleri(html, sayfa_url):
    return []
```

```test
import tezgah
need("kaynak_adresleri")
def sayfa(yol):
    return tezgah.yanit(f"GET {yol} HTTP/1.1\r\nHost: pafta.test\r\n\r\n").govde
eq(kaynak_adresleri(sayfa("/"), "http://pafta.test/"),
   ["http://pafta.test/bilet-ac", "http://pafta.test/giris", "http://pafta.test/static/site.css",
    "http://pafta.test/sunucular", "https://belgeler.pafta.test/api"], "ana sayfa: göreli 'giris' de çözülür")
eq(kaynak_adresleri(sayfa("/kaynaklar"), "http://pafta.test/kaynaklar"),
   ["http://pafta.test/static/logo.png", "http://pafta.test/static/uygulama.js",
    "http://pafta.test/sunucular/db01", "http://pafta.test/sunucular/web01"], "kaynaklar sayfası")
ornek = """<A HREF="rapor.html#ozet">r</A><a href="rapor.html">r</a><a href="#ust">üst</a><a name="cizgi">x</a>
<a href="mailto:ekip@pafta.test">e</a><a href="JavaScript:void(0)">j</a><img src="data:image/png;base64,AAA">
<form action="ara"></form><iframe src="//cdn.pafta.test/harita"></iframe><div data-href="/gizli">d</div><a href="">boş</a>"""
eq(kaynak_adresleri(ornek, "http://pafta.test/belge/"),
   ["http://cdn.pafta.test/harita", "http://pafta.test/belge/ara", "http://pafta.test/belge/rapor.html"],
   "tekrar ve parça atılır; mailto, javascript, data, boş ve yalnızca parça atlanır; data-href bakılan bir öznitelik değil")
```

```solution
from html.parser import HTMLParser
from urllib.parse import urldefrag, urljoin, urlsplit

BAKILAN = {"a": "href", "link": "href", "script": "src", "img": "src", "iframe": "src", "form": "action"}


class _Adresler(HTMLParser):
    def __init__(self, sayfa_url):
        super().__init__()
        self.sayfa_url = sayfa_url
        self.adresler = set()

    def handle_starttag(self, etiket, oznitelikler):
        if etiket not in BAKILAN:
            return
        deger = dict(oznitelikler).get(BAKILAN[etiket])
        if not deger or deger.startswith("#"):
            return
        adres = urldefrag(urljoin(self.sayfa_url, deger)).url
        if urlsplit(adres).scheme in ("http", "https"):
            self.adresler.add(adres)


def kaynak_adresleri(html, sayfa_url):
    p = _Adresler(sayfa_url)
    p.feed(html)
    return sorted(p.adresler)
```

```hint
Hangi etikette hangi özniteliğe bakılacağını bir sözlükte tut: `{"a": "href", "img": "src", ...}`. Adresleri bir kümede topla, sonunda `sorted(...)`.
```
:::

::: gorev data-* öznitelikleri
`veri_oznitelikleri(html)` fonksiyonu en az bir `data-` özniteliği olan her öğe için `(etiket, sozluk)` çifti döndürsün, belgedeki sırayla. Sözlükte anahtarlar `data-` öneki atılmış adlar (küçük harf), değerler öznitelik değerleri; değeri olmayan bir `data-` özniteliğinin değeri `""`. Adı tam olarak `data` olan (tiresiz) öznitelik sayılmaz.

```starter
def veri_oznitelikleri(html):
    return []
```

```test
import tezgah
need("veri_oznitelikleri")
html = tezgah.yanit("GET /kaynaklar HTTP/1.1\r\nHost: pafta.test\r\n\r\n").govde
eq(veri_oznitelikleri(html), [("ul", {"sayfa": "1", "sayfa-boyu": "20"}), ("li", {"sunucu": "web01"}),
                              ("li", {"sunucu": "db01"})], "kaynaklar sayfası")
eq(veri_oznitelikleri('<p data-x data-y="2" id="a">a</p><span data="eski">b</span><DIV DATA-Z="3"></DIV>'),
   [("p", {"x": "", "y": "2"}), ("div", {"z": "3"})], "değersiz öznitelik, tiresiz data sayılmaz, büyük harf")
eq(veri_oznitelikleri("<p id='a'>yok</p>"), [], "hiç yok")
```

```solution
from html.parser import HTMLParser


class _Veri(HTMLParser):
    def __init__(self):
        super().__init__()
        self.bulunan = []

    def handle_starttag(self, etiket, oznitelikler):
        veri = {ad[5:]: (deger if deger is not None else "") for ad, deger in oznitelikler if ad.startswith("data-")}
        if veri:
            self.bulunan.append((etiket, veri))


def veri_oznitelikleri(html):
    p = _Veri()
    p.feed(html)
    return p.bulunan
```

```hint
`html.parser` öznitelik adlarını küçük harfle verir. `ad.startswith("data-")` tiresiz `data`'yı dışarıda bırakır; `ad[5:]` öneki atar.
```
:::

::: gorev Gömülü JSON
`gomulu_json(html, kimlik)` fonksiyonu `type="application/json"` ve `id` özniteliği `kimlik` olan `<script>` öğesinin içeriğini JSON olarak çözüp döndürsün. Böyle bir öğe yoksa (yanlış `id` ya da başka bir `type`) `None` döndürsün. `type` değeri büyük-küçük harfe duyarsız.

```starter
import json

def gomulu_json(html, kimlik):
    return None
```

```test
import tezgah
need("gomulu_json")
html = tezgah.yanit("GET /kaynaklar HTTP/1.1\r\nHost: pafta.test\r\n\r\n").govde
eq(gomulu_json(html, "ayarlar"), {"api": "/api/rapor", "surum": "2.4.1", "yenileme_sn": 30}, "kaynaklar sayfasındaki ayarlar")
eq(gomulu_json(html, "yok"), None, "olmayan id")
ornek = ('<script id="v" type="text/javascript">var x = 1;</script>'
         '<script type="Application/JSON" id="a">{"n": 1}</script>'
         '<script type="application/json" id="v2">[1, 2, "<b>"]</script>')
eq(gomulu_json(ornek, "v"), None, "id tutuyor ama tür JSON değil")
eq(gomulu_json(ornek, "a"), {"n": 1}, "tür büyük-küçük harfe duyarsız")
eq(gomulu_json(ornek, "v2"), [1, 2, "<b>"], "içerikteki < etiket sayılmaz")
```

```solution
import json
from html.parser import HTMLParser


class _Gomulu(HTMLParser):
    def __init__(self, kimlik):
        super().__init__()
        self.kimlik = kimlik
        self.icinde = False
        self.metin = None

    def handle_starttag(self, etiket, oznitelikler):
        oz = dict(oznitelikler)
        if etiket == "script" and oz.get("id") == self.kimlik and (oz.get("type") or "").lower() == "application/json":
            self.icinde = True
            self.metin = ""

    def handle_data(self, veri):
        if self.icinde:
            self.metin += veri

    def handle_endtag(self, etiket):
        if etiket == "script":
            self.icinde = False


def gomulu_json(html, kimlik):
    p = _Gomulu(kimlik)
    p.feed(html)
    return None if p.metin is None else json.loads(p.metin)
```

```hint
Doğru `<script>` başladığında bir bayrak aç ve `handle_data`'da metni biriktir; `</script>`'te kapat. Bulamadıysan metin `None` kalır.
```
:::
