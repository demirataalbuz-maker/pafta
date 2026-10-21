---
id: ht05
title: Başlıklar ve Önbellek
summary: Sık kullanılan istek ve yanıt başlıkları, başlık kuralları (büyük-küçük harf, tekrar eden başlıklar), Accept ile içerik pazarlığı ve Vary, Cache-Control, ETag ile If-None-Match ve Last-Modified ile If-Modified-Since → 304, gzip sıkıştırma ve tarayıcıya savunma talimatı veren başlıklar.
---

::: anlat Sık başlıklar
| İstek başlığı | Ne söyler |
|---|---|
| `Host` | hangi site (HT01) |
| `User-Agent` | istemcinin adı ve sürümü |
| `Accept` | hangi biçimleri kabul ediyorum: `application/json`, `text/html` |
| `Accept-Language`, `Accept-Encoding` | dil tercihim; anladığım sıkıştırmalar (`gzip`, `br`) |
| `Content-Type`, `Content-Length` | gönderdiğim gövdenin türü ve bayt uzunluğu (HT06) |
| `Cookie`, `Authorization` | çerezlerim (HT08), kimliğim (HT09) |
| `If-None-Match`, `If-Modified-Since` | koşullu istek: "değiştiyse gönder" (aşağıda) |
| `Referer` | hangi sayfadan geldim (yazım hatası standartta öyle kaldı) |

| Yanıt başlığı | Ne söyler |
|---|---|
| `Content-Type` | gövdenin türü ve karakter kodlaması: `text/html; charset=utf-8` |
| `Content-Length` | gövdenin **bayt** uzunluğu |
| `Location` | yönlendirmenin ya da yeni kaynağın adresi |
| `Set-Cookie` | bir çerez koy (HT08) |
| `Cache-Control`, `ETag`, `Last-Modified`, `Vary` | önbellek kuralları |
| `Content-Encoding` | gövde sıkıştırılmış mı |
| `Allow`, `Retry-After`, `WWW-Authenticate` | izinli yöntemler, ne zaman tekrar, nasıl kimlik doğrulanır |

Kurallar: başlık **adları** büyük-küçük harfe duyarsızdır; başlıkların sırası anlam taşımaz; değerin başındaki ve sonundaki boşluk sayılmaz. Bir başlık **tekrar edebilir**: çoğu başlığın tekrarları virgülle birleştirilebilir, ama `Set-Cookie` birleştirilemez; her çerez kendi satırındadır. Bu yüzden başlıkları "ad → değer listesi" diye tutmak en güvenlisidir.

### İçerik pazarlığı
Aynı adres, `Accept`'e göre farklı biçimde cevap verebilir. `Vary: Accept` başlığı aradaki önbelleklere "bu yanıt `Accept`'e göre değişir, ayrı sakla" der:

```python
import tezgah

for kabul in ["application/json", "text/html"]:
    y = tezgah.yanit(f"GET /sunucular?rol=db HTTP/1.1\r\nHost: pafta.test\r\nAccept: {kabul}\r\n\r\n")
    print(y.baslik("Content-Type"), y.baslik("Vary"), y.govde[:40].replace("\n", " "))
```
:::

::: anlat Önbellek ve koşullu istekler
`Cache-Control` bir yanıtın ne kadar ve nerede saklanabileceğini söyler:

| Değer | Anlamı |
|---|---|
| `max-age=60` | 60 saniye boyunca taze; sormadan kullanılabilir |
| `no-cache` | saklanabilir, ama her kullanımdan önce sunucuya sorulmalı |
| `no-store` | **hiç** saklanmamalı |
| `private` / `public` | yalnızca kullanıcının tarayıcısı / aradaki paylaşılan önbellekler de |

Süresi dolan bir kopyayı yeniden indirmek yerine **sormak** mümkündür. Sunucu yanıta bir sürüm etiketi koyar (`ETag: "v241"`) ya da son değişme zamanını yazar (`Last-Modified`). İstemci sonraki istekte bunu geri gönderir; içerik değişmediyse sunucu gövdesiz bir `304 Not Modified` döner:

| Sunucu verdi | İstemci gönderir | Değişmediyse |
|---|---|---|
| `ETag: "v241"` | `If-None-Match: "v241"` | `304`, gövde yok |
| `Last-Modified: Sun, 18 Oct 2026 22:00:00 GMT` | `If-Modified-Since: <aynı tarih ya da sonrası>` | `304`, gövde yok |

```python
import tezgah

def iste(*basliklar):
    return tezgah.yanit("GET /durum HTTP/1.1\r\nHost: pafta.test\r\n" + "".join(b + "\r\n" for b in basliklar) + "\r\n")

y = iste()
print(y.durum, y.baslik("ETag"), y.baslik("Cache-Control"))
y = iste('If-None-Match: "v241"')
print(y.durum, repr(y.govde), y.baslik("ETag"))
```

ETag tırnaklarıyla birlikte bir değerdir: `"v241"` ile `v241` aynı etiket değildir. `W/"v241"` biçimindeki etiketler "zayıf"tır: içerik anlamca aynı ama bayt bayt aynı olmayabilir.

### Sıkıştırma
`Accept-Encoding: gzip` gönderen istemciye sunucu gövdeyi sıkıştırıp `Content-Encoding: gzip` ile yollayabilir. O zaman gövde **sıkıştırılmış baytlardır** ve `Content-Length` da sıkıştırılmış uzunluktur:

```python
import gzip
import tezgah

y = tezgah.yanit("GET /sikistirilmis HTTP/1.1\r\nHost: pafta.test\r\nAccept-Encoding: gzip\r\n\r\n")
print(y.baslik("Content-Encoding"), y.baslik("Content-Length"), len(gzip.decompress(y.govde_bayt)))
```

> [!GÜVENLİK]
> Kişisel veri gösteren sayfalara `Cache-Control: no-store` konur: ortak bilgisayarlarda ve aradaki önbelleklerde kopyası kalmasın. `Server` başlığında ayrıntılı sürüm yazmamak, yazılımın eski bir sürümünü arayanlara bilgi vermemektir. Bazı başlıklar da tarayıcıya savunma talimatı verir: `Strict-Transport-Security` (bu siteye yalnızca HTTPS ile gel), `Content-Security-Policy` (hangi kaynaktan betik yüklenebilir), `X-Content-Type-Options: nosniff` (`Content-Type`'a uy, tahmin yürütme).
:::

::: tahmin
Dört koşullu istek. Kod ve gövde boş mu?

```python
import tezgah

for etiket in ['"v241"', 'v241', '"v240", "v241"', '*']:
    y = tezgah.yanit(f"GET /durum HTTP/1.1\r\nHost: pafta.test\r\nIf-None-Match: {etiket}\r\n\r\n")
    print(y.durum, y.govde == "")
```

???

`304 True`, `200 False`, `304 True` ve `304 True`. Etiket tırnaklarıyla eşleşir: `"v241"` tutar, tırnaksız `v241` tutmaz ve tam yanıt (200, gövdeli) gelir. `If-None-Match` virgülle ayrılmış birden çok etiket alabilir; biri tutması yeter. `*` "herhangi bir sürümün varsa" demektir ve kaynak var olduğu için 304 döner.
:::

::: gorev Başlık tablosu
`baslik_tablosu(ham)` fonksiyonu ham bir yanıtın başlıklarını `{küçük_harfli_ad: [değer, değer, ...]}` sözlüğüne çevirsin. Aynı başlık birden çok kez geçiyorsa bütün değerleri **geliş sırasıyla** listede dursun. Değerlerin kenar boşlukları atılsın; değerin içinde `:` olabilir. Durum satırı ve gövde tabloya girmez.

```starter
def baslik_tablosu(ham):
    tablo = {}
    for satir in ham.split("\r\n")[1:]:
        ad, deger = satir.split(":")
        tablo[ad] = deger
    return tablo
```

```test
import tezgah
need("baslik_tablosu")
ham = ("HTTP/1.1 200 OK\r\nSet-Cookie: a=1; Path=/\r\nVary: Accept\r\nset-cookie: b=2\r\n"
       "vary:Accept-Encoding\r\nDate: Mon, 19 Oct 2026 09:00:00 GMT\r\n\r\nX: gövdedeki satır başlık değildir")
eq(baslik_tablosu(ham), {"set-cookie": ["a=1; Path=/", "b=2"], "vary": ["Accept", "Accept-Encoding"],
                         "date": ["Mon, 19 Oct 2026 09:00:00 GMT"]}, "tekrar eden başlıklar, : içeren değer")
eq(baslik_tablosu("HTTP/1.1 204 No Content\r\n\r\n"), {}, "başlıksız yanıt")
t = baslik_tablosu(tezgah.gonder("GET /durum HTTP/1.1\r\nHost: pafta.test\r\n\r\n"))
eq((t["etag"], t["content-length"]), (['"v241"'], ["33"]), "tezgahın gerçek yanıtı")
```

```solution
def baslik_tablosu(ham):
    bas = ham.partition("\r\n\r\n")[0]
    tablo = {}
    for satir in bas.split("\r\n")[1:]:
        ad, _, deger = satir.partition(":")
        tablo.setdefault(ad.strip().lower(), []).append(deger.strip())
    return tablo
```

```hint
Önce gövdeyi ayır (`partition("\r\n\r\n")`), sonra durum satırını atla. `tablo.setdefault(ad, []).append(deger)` aynı adın değerlerini bir listede toplar.
```
:::

::: gorev Değiştiyse getir
`durum_getir(onceki_etag=None)` fonksiyonu tezgahın `/durum` adresine bir GET göndersin; `onceki_etag` verilmişse isteğe `If-None-Match` başlığı olarak eklesin. Dönüş `(degisti_mi, etag, veri)` olsun:

- `200` → `(True, yanıttaki ETag, gövdenin JSON'u)`
- `304` → `(False, yanıttaki ETag, None)`

```starter
import tezgah

def durum_getir(onceki_etag=None):
    y = tezgah.yanit("GET /durum HTTP/1.1\r\nHost: pafta.test\r\n\r\n")
    return (True, y.baslik("ETag"), y.json())
```

```test
need("durum_getir")
ok("If-None-Match" in src, "koşullu istek için If-None-Match kullan")
ilk = durum_getir()
eq(ilk, (True, '"v241"', {"durum": "ok", "surum": "2.4.1"}), "ilk istek: tam yanıt")
eq(durum_getir(ilk[1]), (False, '"v241"', None), "aynı etiket: 304, veri yok")
eq(durum_getir('"v240"'), (True, '"v241"', {"durum": "ok", "surum": "2.4.1"}), "eski etiket: tam yanıt")
```

```solution
import tezgah


def durum_getir(onceki_etag=None):
    istek = "GET /durum HTTP/1.1\r\nHost: pafta.test\r\n"
    if onceki_etag:
        istek += f"If-None-Match: {onceki_etag}\r\n"
    y = tezgah.yanit(istek + "\r\n")
    if y.durum == 304:
        return (False, y.baslik("ETag"), None)
    return (True, y.baslik("ETag"), y.json())
```

```hint
İsteği parça parça kur: önce istek satırı ve `Host`, etiket varsa `If-None-Match: <etiket>` satırı, en sonda boş satır. 304'te gövde yoktur; `json()` çağırma.
```
:::

::: gorev Sıkıştırmayı aç
`getir(yol)` fonksiyonu tezgaha `Accept-Encoding: gzip` başlıklı bir GET göndersin ve gövdeyi **metin** olarak döndürsün. Yanıtta `Content-Encoding: gzip` varsa (değeri büyük-küçük harfe duyarsız) gövdeyi `gzip.decompress` ile açsın; yoksa gövdeyi olduğu gibi UTF-8 olarak çözsün.

```starter
import tezgah

def getir(yol):
    return tezgah.yanit(f"GET {yol} HTTP/1.1\r\nHost: pafta.test\r\n\r\n").govde
```

```test
import tezgah
need("getir")
ok("gzip" in src, "Accept-Encoding: gzip gönder")
eq(getir("/sikistirilmis"), "Pafta Bilet Masası haftalık özeti. " * 8, "sıkıştırılmış gövde açılır")
eq(getir("/durum"), '{"durum": "ok", "surum": "2.4.1"}', "sıkıştırılmamış gövde olduğu gibi")
y = tezgah.yanit("GET /sikistirilmis HTTP/1.1\r\nHost: pafta.test\r\nAccept-Encoding: gzip\r\n\r\n")
ok(y.baslik("Content-Encoding") == "gzip", "sunucu gzip'li gönderiyor (kontrol)")
```

```solution
import gzip

import tezgah


def getir(yol):
    y = tezgah.yanit(f"GET {yol} HTTP/1.1\r\nHost: pafta.test\r\nAccept-Encoding: gzip\r\n\r\n")
    kodlama = y.baslik("Content-Encoding")
    if kodlama and kodlama.lower() == "gzip":
        return gzip.decompress(y.govde_bayt).decode("utf-8")
    return y.govde_bayt.decode("utf-8")
```

```hint
Sıkıştırılmış gövde metin değil bayttır: `y.govde_bayt` kullan. `gzip.decompress(...)` açılmış baytları verir, `.decode("utf-8")` metne çevirir.
```
:::
