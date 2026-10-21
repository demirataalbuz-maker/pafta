---
id: ht01
title: Bir İsteğin Anatomisi
summary: HTTP'nin satır satır bir metin olması; istek satırı, başlıklar, boş satır ve gövde; CRLF satır sonları; yanıtın durum satırı; Host başlığı, HTTP/1.0 ile HTTP/1.1 farkı ve tezgahta ham istek göndermek.
---

::: anlat HTTP bir metindir
Tarayıcıya bir adres yazdığında tarayıcı sunucuya bir TCP bağlantısı açar ve bu bağlantıdan **düz metin** gönderir. Sunucu da metinle cevap verir. Bütün web bu konuşmanın üstüne kuruludur:

```text
GET /durum HTTP/1.1
Host: pafta.test
User-Agent: pafta-ders/1.0
Accept: application/json

```

| Parça | Örnek | Ne söyler |
|---|---|---|
| istek satırı | `GET /durum HTTP/1.1` | **yöntem**, **istek hedefi** (yol ve sorgu) ve **sürüm**, tek boşlukla ayrılmış |
| başlıklar | `Host: pafta.test` | her satırda `Ad: değer`; ad büyük-küçük harfe duyarsızdır |
| boş satır | | başlıkların bittiğini söyler; **zorunludur** |
| gövde | (GET'te çoğu zaman yok) | uzunluğunu `Content-Length` başlığı söyler (HT06) |

Satırlar `\n` ile değil **CRLF** ile, yani `\r\n` ile biter. Python'da yukarıdaki istek şu metindir:

```python
istek = "GET /durum HTTP/1.1\r\nHost: pafta.test\r\nUser-Agent: pafta-ders/1.0\r\nAccept: application/json\r\n\r\n"
print(len(istek), istek.endswith("\r\n\r\n"))
```

### Tezgah
Bu yolda her çalıştırmada arka planda küçük bir demo web uygulaması koşar: **Pafta Bilet Masası** (sunucu listesi, biletler, giriş sayfası). `tezgah` modülü ona ham istek göndermeni sağlar:

| Araç | Ne yapar |
|---|---|
| `tezgah.gonder(istek)` | ham isteği sokete yazar, sunucunun ham yanıtını **metin** olarak döndürür |
| `tezgah.yanit(istek)` | gönderir ve ayrıştırır: `.surum`, `.durum`, `.neden`, `.basliklar`, `.baslik(ad)`, `.govde`, `.json()` |
| `tezgah.SUNUCU` | `http://127.0.0.1:PORT`; `urllib` gibi istemciler için |

```python
import tezgah

istek = "GET /durum HTTP/1.1\r\nHost: pafta.test\r\n\r\n"
for satir in tezgah.gonder(istek).split("\r\n"):
    print(satir)
```

Yanıt da aynı biçimdedir: önce **durum satırı** (`HTTP/1.1 200 OK`: sürüm, durum kodu, neden ifadesi), sonra başlıklar, boş satır ve gövde.

> [!NOT]
> Gerçek dünyada bu konuşma çoğu zaman TLS içinde (HTTPS) şifreli gider; şifre çözüldüğünde içerik aynı metindir. Tarayıcının geliştirici araçları ve web güvenliği test araçları sana tam olarak bu metni gösterir.
:::

::: anlat Host, sürümler ve katı kurallar
Tek bir IP adresinde onlarca site çalışabilir. Sunucu hangi siteyi istediğini **`Host`** başlığından anlar. Bu yüzden HTTP/1.1'de `Host` **zorunludur**; eksikse sunucu `400 Bad Request` döndürür. Eski HTTP/1.0'da zorunlu değildi:

```python
import tezgah

y = tezgah.yanit("GET /durum HTTP/1.1\r\n\r\n")
print(y.durum, y.neden, y.json())
y = tezgah.yanit("GET /durum HTTP/1.0\r\n\r\n")
print(y.durum, y.neden, y.json())
```

| | HTTP/1.0 | HTTP/1.1 |
|---|---|---|
| `Host` | isteğe bağlı | **zorunlu** |
| bağlantı | her istekten sonra kapanır | varsayılan olarak açık kalır (HT13) |

Bir yanıtı okurken **durum koduna** bak, neden ifadesine değil. `OK` ya da `Not Found` yalnızca insanlar içindir; sunucu başka bir ifade yazabilir, HTTP/2 ise hiç göndermez.

> [!TUZAK]
> Yöntem adları **büyük-küçük harfe duyarlıdır**: `GET` bir yöntemdir, `get` değildir. Başlık adları ise duyarsızdır: `host:`, `Host:` ve `HOST:` aynı başlıktır. İstek satırındaki boşluklar da tektir; `GET  /durum` (iki boşluk) bozuk bir istektir.
:::

::: tahmin
Dört istek, dört satır. Hangi kodlar?

```python
import tezgah

for istek in ["GET /durum HTTP/1.1\r\nHost: pafta.test\r\n\r\n",
              "GET /durum HTTP/1.1\r\n\r\n",
              "GET /durum HTTP/1.0\r\n\r\n",
              "GET /yok HTTP/1.1\r\nhost: pafta.test\r\n\r\n"]:
    y = tezgah.yanit(istek)
    print(y.durum, y.neden)
```

???

`200 OK`, `400 Bad Request`, `200 OK` ve `404 Not Found`. İkinci istek HTTP/1.1 olduğu hâlde `Host` taşımıyor: 400. Üçüncüsü aynı isteğin HTTP/1.0 sürümü; orada `Host` zorunlu değil. Dördüncüde başlık adı küçük harfle yazılmış ama bu sorun değil (başlık adları duyarsız); `/yok` diye bir sayfa olmadığı için 404 gelir.
:::

::: gorev Ham istek yaz
`istek_yaz(yontem, yol, host, basliklar=None)` fonksiyonu ham bir HTTP/1.1 isteği döndürsün: önce istek satırı, sonra `Host`, sonra `basliklar` listesindeki `(ad, değer)` çiftleri **verilen sırayla**, en sonda boş satır. Bütün satırlar CRLF ile bitsin; gövde yok.

```starter
def istek_yaz(yontem, yol, host, basliklar=None):
    return f"{yontem} {yol} HTTP/1.1\nHost: {host}\n"
```

```test
import tezgah
need("istek_yaz")
eq(istek_yaz("GET", "/durum", "pafta.test"), "GET /durum HTTP/1.1\r\nHost: pafta.test\r\n\r\n", "en sade istek")
eq(istek_yaz("GET", "/sunucular?rol=web", "pafta.test", [("Accept", "application/json"), ("X-Iz", "a:b")]),
   "GET /sunucular?rol=web HTTP/1.1\r\nHost: pafta.test\r\nAccept: application/json\r\nX-Iz: a:b\r\n\r\n",
   "başlıklar verilen sırayla, değerde : olabilir")
eq(istek_yaz("HEAD", "/", "pafta.test", []), "HEAD / HTTP/1.1\r\nHost: pafta.test\r\n\r\n", "boş başlık listesi")
y = tezgah.yanit(istek_yaz("GET", "/sunucular/web01", "pafta.test"))
eq((y.durum, y.json()["ad"]), (200, "web01"), "sunucu isteği kabul etmeli")
```

```solution
def istek_yaz(yontem, yol, host, basliklar=None):
    satirlar = [f"{yontem} {yol} HTTP/1.1", f"Host: {host}"]
    for ad, deger in basliklar or []:
        satirlar.append(f"{ad}: {deger}")
    return "\r\n".join(satirlar) + "\r\n\r\n"
```

```hint
Satırları bir listede topla ve `"\r\n".join(...)` ile birleştir. Sona bir `"\r\n\r\n"` ekle: biri son başlık satırını bitirir, öteki boş satırdır.
```
:::

::: gorev Yanıtı ayrıştır
`yanit_coz(ham)` fonksiyonu ham bir yanıt metnini şu sözlüğe çevirsin:

```python norun
{"surum": "HTTP/1.1", "durum": 404, "neden": "Not Found",
 "basliklar": {"content-type": "application/json; charset=utf-8", ...}, "govde": "..."}
```

- `durum` bir **tam sayı** olsun; neden ifadesi boşluk içerebilir (`Method Not Allowed`)
- başlık adları **küçük harfe** çevrilsin, değerlerin kenar boşlukları atılsın; değerin içinde `:` olabilir
- gövde, ilk boş satırdan sonraki her şey (yoksa `""`)

```starter
def yanit_coz(ham):
    satirlar = ham.split("\n")
    surum, durum, neden = satirlar[0].split(" ")
    return {"surum": surum, "durum": durum, "neden": neden, "basliklar": {}, "govde": ""}
```

```test
import tezgah
need("yanit_coz")
r = yanit_coz(tezgah.gonder("GET /yok HTTP/1.1\r\nHost: pafta.test\r\n\r\n"))
eq((r["surum"], r["durum"], r["neden"]), ("HTTP/1.1", 404, "Not Found"), "durum satırı; durum bir int")
eq(r["basliklar"]["date"], "Mon, 19 Oct 2026 09:00:00 GMT", "değerde : olan başlık (Date)")
eq(r["basliklar"]["content-type"], "application/json; charset=utf-8", "küçük harfli başlık adı")
eq(r["govde"], '{"hata": "sayfa bulunamadı"}', "gövde")
r = yanit_coz(tezgah.gonder("PATCH /biletler HTTP/1.1\r\nHost: pafta.test\r\n\r\n"))
eq((r["durum"], r["neden"]), (405, "Method Not Allowed"), "neden ifadesi boşluk içerebilir")
r = yanit_coz("HTTP/1.1 204 No Content\r\nServer:   PaftaSunucu/1.0  \r\n\r\n")
eq((r["durum"], r["basliklar"], r["govde"]), (204, {"server": "PaftaSunucu/1.0"}, ""), "gövdesiz yanıt, kırpılmış değer")
```

```solution
def yanit_coz(ham):
    bas, _, govde = ham.partition("\r\n\r\n")
    ilk, *satirlar = bas.split("\r\n")
    surum, durum, neden = ilk.split(" ", 2)
    basliklar = {}
    for satir in satirlar:
        ad, _, deger = satir.partition(":")
        basliklar[ad.strip().lower()] = deger.strip()
    return {"surum": surum, "durum": int(durum), "neden": neden, "basliklar": basliklar, "govde": govde}
```

```hint
`ham.partition("\r\n\r\n")` başlık bölümünü gövdeden ayırır. Durum satırında `split(" ", 2)` en fazla iki kez böler, böylece neden ifadesi bütün kalır.
```

```hint
Başlık satırında `partition(":")` yalnızca **ilk** iki noktadan böler: `Date: Mon, 19 Oct 2026 09:00:00 GMT` doğru ayrılır.
```
:::

::: gorev Geçerli mi?
`gecerli_mi(ham)` fonksiyonu ham bir isteğin başlık bölümüne bakıp sunucunun onu kabul edip etmeyeceğini söylesin (`True` ya da `False`):

- istek satırı **tam üç** parçadır (tek boşlukla ayrılmış)
- yöntem yalnızca **büyük harflerden** oluşur (`GET`, `DELETE`...)
- sürüm `HTTP/1.0` ya da `HTTP/1.1`'dir
- sürüm `HTTP/1.1` ise bir `Host` başlığı vardır (adı büyük-küçük harfe duyarsız) ve değeri boş değildir

```starter
def gecerli_mi(ham):
    return ham.startswith("GET")
```

```test
import tezgah
need("gecerli_mi")
ornekler = [
    ("GET /durum HTTP/1.1\r\nHost: pafta.test\r\n\r\n", True, "geçerli HTTP/1.1"),
    ("GET /durum HTTP/1.1\r\n\r\n", False, "HTTP/1.1'de Host yok"),
    ("GET /durum HTTP/1.0\r\n\r\n", True, "HTTP/1.0'da Host gerekmez"),
    ("HEAD /durum HTTP/1.1\r\nhost: pafta.test\r\n\r\n", True, "küçük harfli başlık adı"),
    ("get /durum HTTP/1.1\r\nHost: pafta.test\r\n\r\n", False, "küçük harfli yöntem"),
    ("GET /durum HTTP/2\r\nHost: pafta.test\r\n\r\n", False, "bilinmeyen sürüm"),
    ("GET  /durum HTTP/1.1\r\nHost: pafta.test\r\n\r\n", False, "çift boşluk: dört parça"),
    ("GET /durum\r\nHost: pafta.test\r\n\r\n", False, "sürüm yok: iki parça"),
    ("GET /durum HTTP/1.1\r\nHost:\r\n\r\n", False, "boş Host değeri"),
    ("GET /durum HTTP/1.1\r\nX-Host: pafta.test\r\n\r\n", False, "X-Host, Host değildir"),
]
for ham, beklenen, ad in ornekler:
    eq(gecerli_mi(ham), beklenen, ad)
for ham, beklenen, ad in ornekler[:5]:
    ok((tezgah.yanit(ham).durum < 400) == beklenen, f"sunucu da aynı kararı veriyor: {ad}")
```

```solution
def gecerli_mi(ham):
    bas = ham.partition("\r\n\r\n")[0]
    ilk, *satirlar = bas.split("\r\n")
    parcalar = ilk.split(" ")
    if len(parcalar) != 3:
        return False
    yontem, _, surum = parcalar
    if not (yontem.isalpha() and yontem.isupper()):
        return False
    if surum == "HTTP/1.0":
        return True
    if surum != "HTTP/1.1":
        return False
    for satir in satirlar:
        ad, _, deger = satir.partition(":")
        if ad.strip().lower() == "host" and deger.strip():
            return True
    return False
```

```hint
`ilk.split(" ")` çift boşlukta boş bir parça üretir; parça sayısı 3 değilse istek bozuktur. `isalpha()` ve `isupper()` birlikte "yalnızca büyük harf" demektir.
```

```hint
Host'u ararken adı `strip().lower()` ile karşılaştır ve değerin boş olmadığına bak.
```
:::
