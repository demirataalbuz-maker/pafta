---
id: ht08
title: Çerezler
summary: HTTP'nin durumsuz olması ve çerezle oturum; Set-Cookie ve öznitelikleri (Expires, Max-Age, Domain, Path, Secure, HttpOnly, SameSite), Cookie başlığı, çerez silmek, istemcideki çerez kavanozu, yol eşleşmesi ve oturum çerezini korumak.
---

::: anlat Sunucu unutur, çerez hatırlatır
HTTP **durumsuzdur**: sunucu her isteği öncekilerden bağımsız görür. "Bu kişi az önce giriş yaptı" bilgisi istekte taşınmalıdır. **Çerez** bunun yoludur: sunucu bir yanıta `Set-Cookie: ad=değer` koyar, istemci aynı siteye giden sonraki isteklere `Cookie: ad=değer` ekler.

```python
import tezgah

govde = "kullanici=ayse&parola=pafta-demo"
y = tezgah.yanit(f"POST /giris HTTP/1.1\r\nHost: pafta.test\r\nContent-Type: application/x-www-form-urlencoded\r\n"
                 f"Content-Length: {len(govde)}\r\n\r\n{govde}")
print(y.durum, y.baslik("Location"), y.baslik("Set-Cookie"))
cerez = y.baslik("Set-Cookie").split(";")[0]                  #! yalnızca ad=değer geri gider
print(tezgah.yanit(f"GET /panel HTTP/1.1\r\nHost: pafta.test\r\nCookie: {cerez}\r\n\r\n").durum)
print(tezgah.yanit("GET /panel HTTP/1.1\r\nHost: pafta.test\r\n\r\n").baslik("Location"))
```

`Set-Cookie`'deki `;` sonrası **öznitelikler**, çerezin ne zaman ve nereye gönderileceğini söyler:

| Öznitelik | Anlamı |
|---|---|
| `Expires=<tarih>` | bu tarihte sil |
| `Max-Age=<saniye>` | bu kadar saniye sonra sil; `Expires` ile birlikteyse geçerli olan budur; `0` ya da eksi → hemen sil |
| (ikisi de yok) | **oturum çerezi**: tarayıcı kapanınca silinir |
| `Domain=pafta.test` | bu alan adına ve alt alanlarına gönder; yoksa yalnızca çerezi koyan host'a |
| `Path=/` | bu yola ve altındaki yollara gönder |
| `Secure` | yalnızca HTTPS bağlantılarında gönder |
| `HttpOnly` | sayfadaki JavaScript çerezi **okuyamaz** |
| `SameSite=Strict` / `Lax` / `None` | isteği başka bir site başlattıysa gönderilsin mi: `Strict` hiç, `Lax` yalnızca bağlantıya tıklayarak gelince, `None` her zaman (`Secure` şart) |

`Cookie` başlığı yalnızca `ad=değer` çiftlerini taşır, `;` ve boşlukla ayrılmış: `Cookie: tema=koyu; oturum=s7f3a-ayse`. Öznitelikler hiçbir zaman geri gönderilmez. Bir çerezi silmek için sunucu aynı adla `Max-Age=0` gönderir; tezgahta `POST /cikis` bunu yapar.
:::

::: anlat Kavanoz ve yol eşleşmesi
İstemci aldığı çerezleri bir **kavanozda** tutar: hangi site, hangi ad, hangi değer, ne zamana kadar. Her yeni istekte kavanoza bakıp o adrese uyan çerezleri `Cookie` başlığına yazar. Bir yanıt **birden çok** `Set-Cookie` taşıyabilir; her biri ayrı bir çerezdir, virgülle birleştirilemez (bir tarihin içinde de virgül vardır).

Çerezin `Path`'i, istek yoluyla RFC 6265'in **yol eşleşmesi** kuralına göre karşılaştırılır. Çerez yolu `/docs` ise:

| İstek yolu | Gönderilir mi | Neden |
|---|---|---|
| `/docs` | evet | aynı yol |
| `/docs/` ve `/docs/web` | evet | çerez yolu önek ve hemen ardından `/` geliyor |
| `/docsx` | hayır | önek ama ardından `/` gelmiyor |
| `/doc` | hayır | önek değil |

Çerez yolu `/` ile bitiyorsa (`/docs/`) önek olması yeter. `/` her yola uyar. Yollar büyük-küçük harfe duyarlıdır.

> [!GÜVENLİK]
> Oturum çerezi bir anahtardır: elinde olan kişi o oturumu kullanabilir. Bu yüzden değeri uzun ve **rastgele** olmalı (tezgahtaki sabit değer yalnızca öğretim içindir), `HttpOnly` (sayfaya sızan bir betik okuyamasın), `Secure` (şifresiz bağlantıda gitmesin) ve `SameSite` (başka sitelerden başlatılan isteklerde gitmesin) taşımalı. Girişte yeni bir oturum kimliği üretilir, sunucu tarafında bir süre sınırı tutulur ve çıkışta oturum sunucuda da geçersiz kılınır.
:::

::: tahmin
Giriş yanıtının çerezi. Üç satır:

```python
import tezgah

govde = "kullanici=ayse&parola=pafta-demo"
y = tezgah.yanit(f"POST /giris HTTP/1.1\r\nHost: pafta.test\r\nContent-Type: application/x-www-form-urlencoded\r\n"
                 f"Content-Length: {len(govde)}\r\n\r\n{govde}")
cerez = y.baslik("Set-Cookie")
print(y.durum, cerez.split(";")[0])
print([o.strip() for o in cerez.split(";")[1:]])
ad_deger = cerez.split(";")[0]
print(tezgah.yanit(f"GET /panel HTTP/1.1\r\nHost: pafta.test\r\nCookie: {ad_deger}\r\n\r\n").durum,
      tezgah.yanit("GET /panel HTTP/1.1\r\nHost: pafta.test\r\n\r\n").durum)
```

???

`303 oturum=s7f3a-ayse`, `['Path=/', 'HttpOnly', 'SameSite=Strict']` ve `200 302`. Giriş başarılı olunca sunucu çerezi koyar ve panele yönlendirir (303, PRG). Çerezin değeri `;`'e kadar olan kısımdır; geri kalanı öznitelikler: bütün sitede geçerli, JavaScript'e kapalı, başka sitelerden başlayan isteklerde gönderilmez. Panele çerezle gelen 200 alır, çerezsiz gelen giriş sayfasına yönlendirilir (302).
:::

::: gorev Set-Cookie'yi çöz
`cerez_coz(set_cookie)` fonksiyonu bir `Set-Cookie` değerini `(ad, deger, oznitelikler)` üçlüsüne çevirsin:

- ad ve değer ilk `;`'e kadar olan kısımdan, **ilk** `=`'den bölünerek çıkar (değerin içinde `=` olabilir); kenar boşlukları atılır
- öznitelik adları **küçük harfe** çevrilir; değeri olanlar `{"path": "/"}` gibi, değeri olmayanlar (`HttpOnly`, `Secure`) `True` olarak yazılır

```starter
def cerez_coz(set_cookie):
    parcalar = set_cookie.split(";")
    ad, deger = parcalar[0].split("=")
    return (ad, deger, {})
```

```test
need("cerez_coz")
eq(cerez_coz("oturum=s7f3a-ayse; Path=/; HttpOnly; SameSite=Strict"),
   ("oturum", "s7f3a-ayse", {"path": "/", "httponly": True, "samesite": "Strict"}), "oturum çerezi")
eq(cerez_coz("jeton=YWJj==; max-age=0"), ("jeton", "YWJj==", {"max-age": "0"}), "değerde = olabilir")
eq(cerez_coz("tema=koyu"), ("tema", "koyu", {}), "özniteliksiz")
eq(cerez_coz(" a = 1 ;  Secure ; Expires=Tue, 20 Oct 2026 09:00:00 GMT"),
   ("a", "1", {"secure": True, "expires": "Tue, 20 Oct 2026 09:00:00 GMT"}), "boşluklar ve virgüllü tarih")
eq(cerez_coz("bos=; Path=/a"), ("bos", "", {"path": "/a"}), "boş değer")
```

```solution
def cerez_coz(set_cookie):
    ilk, *oznitelikler = set_cookie.split(";")
    ad, _, deger = ilk.partition("=")
    sozluk = {}
    for o in oznitelikler:
        anahtar, esit, deger_o = o.partition("=")
        sozluk[anahtar.strip().lower()] = deger_o.strip() if esit else True
    return (ad.strip(), deger.strip(), sozluk)
```

```hint
`partition("=")` yalnızca ilk `=`'den böler ve `=` hiç yoksa ortadaki parça boş döner: değeri olmayan öznitelikleri böyle ayırt edersin.
```
:::

::: gorev Çerez kavanozu
Bir `Kavanoz` sınıfı yaz:

- `al(yanit)`: bir `tezgah` yanıtındaki **bütün** `Set-Cookie` başlıklarını (`yanit.hepsi("Set-Cookie")`) işler; çerezi adıyla saklar (aynı ad gelirse değer güncellenir). `Max-Age` sıfır ya da eksiyse o çerezi kavanozdan **siler**
- `cookie()`: `Cookie` başlığına yazılacak metni döndürür: `ad=değer` çiftleri ilk eklenme sırasıyla, `"; "` ile ayrılmış; kavanoz boşsa `""`

```starter
class Kavanoz:
    def __init__(self):
        self.cerezler = {}

    def al(self, yanit):
        pass

    def cookie(self):
        return ""
```

```test
import tezgah
need("Kavanoz", "sınıf")
k = Kavanoz()
eq(k.cookie(), "", "boş kavanoz")
def iste(satir, govde=None):
    ek = f"Cookie: {k.cookie()}\r\n" if k.cookie() else ""
    if govde is None:
        return tezgah.yanit(f"{satir}\r\nHost: pafta.test\r\n{ek}\r\n")
    return tezgah.yanit(f"{satir}\r\nHost: pafta.test\r\n{ek}Content-Type: application/x-www-form-urlencoded\r\n"
                        f"Content-Length: {len(govde)}\r\n\r\n{govde}")
k.al(iste("POST /giris HTTP/1.1", "kullanici=ayse&parola=pafta-demo"))
eq(k.cookie(), "oturum=s7f3a-ayse", "girişten sonra oturum çerezi")
eq(iste("GET /panel HTTP/1.1").durum, 200, "kavanozla panel açılıyor")
k.al(iste("GET /tercih?tema=koyu HTTP/1.1"))
eq(k.cookie(), "oturum=s7f3a-ayse; tema=koyu", "ikinci çerez eklenme sırasıyla")
k.al(iste("GET /tercih?tema=acik HTTP/1.1"))
eq(k.cookie(), "oturum=s7f3a-ayse; tema=acik", "aynı ad: değer güncellenir, sıra korunur")
k.al(iste("POST /cikis HTTP/1.1", ""))
eq(k.cookie(), "tema=acik", "çıkışta Max-Age=0: oturum silinir")
eq(iste("GET /panel HTTP/1.1").durum, 302, "çerezsiz panel giriş sayfasına yönlendirir")
k2 = Kavanoz()
k2.al(tezgah.Yanit(b"HTTP/1.1 200 OK\r\nSet-Cookie: a=1; Max-Age=1\r\nSet-Cookie: b=2; Max-Age=-1\r\nSet-Cookie: c=3=4\r\n\r\n"))
eq(k2.cookie(), "a=1; c=3=4", "Max-Age=1 kalır, -1 silinir; aynı yanıtta birden çok çerez")
```

```solution
class Kavanoz:
    def __init__(self):
        self.cerezler = {}

    def al(self, yanit):
        for set_cookie in yanit.hepsi("Set-Cookie"):
            ilk, *oznitelikler = set_cookie.split(";")
            ad, _, deger = ilk.partition("=")
            ad = ad.strip()
            omur = None
            for o in oznitelikler:
                anahtar, _, d = o.partition("=")
                if anahtar.strip().lower() == "max-age":
                    omur = int(d.strip())
            if omur is not None and omur <= 0:
                self.cerezler.pop(ad, None)
            else:
                self.cerezler[ad] = deger.strip()

    def cookie(self):
        return "; ".join(f"{ad}={deger}" for ad, deger in self.cerezler.items())
```

```hint
Python sözlükleri ekleme sırasını korur ve var olan bir anahtarın değerini güncellemek sırayı değiştirmez. Silmek için `pop(ad, None)`.
```

```hint
`Max-Age`'i bulmak için öznitelikleri dolaş, adını küçük harfle karşılaştır, değerini `int` yap: `0` ya da eksi ise sil.
```
:::

::: gorev Yol eşleşmesi
`gonderilir_mi(cerez_yolu, istek_yolu)` fonksiyonu RFC 6265'in yol eşleşmesi kuralını uygulasın: yollar aynıysa ya da çerez yolu istek yolunun öneki olup (a) `/` ile bitiyorsa ya da (b) istek yolunda önekten hemen sonra `/` geliyorsa `True`; değilse `False`. Karşılaştırma büyük-küçük harfe duyarlı.

```starter
def gonderilir_mi(cerez_yolu, istek_yolu):
    return istek_yolu.startswith(cerez_yolu)
```

```test
need("gonderilir_mi")
for cerez_yolu, istek_yolu, beklenen in [("/", "/panel", True), ("/", "/", True), ("/docs", "/docs", True),
                                        ("/docs", "/docs/", True), ("/docs", "/docs/web", True),
                                        ("/docs", "/docsx", False), ("/docs", "/doc", False),
                                        ("/docs/", "/docs/a", True), ("/docs/", "/docs", False),
                                        ("/Docs", "/docs", False), ("/docs", "/", False), ("/a/b", "/a/bc/d", False)]:
    eq(gonderilir_mi(cerez_yolu, istek_yolu), beklenen, f"{cerez_yolu} ↔ {istek_yolu}")
```

```solution
def gonderilir_mi(cerez_yolu, istek_yolu):
    if istek_yolu == cerez_yolu:
        return True
    if not istek_yolu.startswith(cerez_yolu):
        return False
    return cerez_yolu.endswith("/") or istek_yolu[len(cerez_yolu)] == "/"
```

```hint
Önce eşitliğe, sonra öneke bak. Önekse ve çerez yolu `/` ile bitmiyorsa, istek yolunun `len(cerez_yolu)` konumundaki karakter `/` olmalı.
```
:::
