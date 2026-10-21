---
id: ht09
title: Kimlik Doğrulama Başlıkları
summary: 401 ve WWW-Authenticate ile meydan okuma, Authorization: Basic ve base64'ün şifreleme olmaması, 401 ile 403 farkı, Bearer jetonları ve error="invalid_token", çerez ile Authorization başlığının farkı ve kimlik bilgilerini URL'de ve günlüklerde taşımamak.
---

::: anlat 401 ve Basic
Kimlik isteyen bir adrese kimliksiz gelirsen sunucu `401 Unauthorized` döner ve **nasıl** kimlik doğrulanacağını `WWW-Authenticate` başlığında söyler. Buna meydan okuma (challenge) denir. İstemci bir sonraki isteğe `Authorization` başlığını ekler.

**Basic** şemasında değer, `kullanici:parola` metninin UTF-8 baytlarının **base64** hâlidir:

```text
GET /yonetim HTTP/1.1
Host: pafta.test
Authorization: Basic eW9uZXRpY2k6cGFmdGEtZGVtbw==
```

```python
import base64
import tezgah

def yonetim(kimlik=None):
    ek = f"Authorization: Basic {base64.b64encode(kimlik.encode()).decode()}\r\n" if kimlik else ""
    return tezgah.yanit(f"GET /yonetim HTTP/1.1\r\nHost: pafta.test\r\n{ek}\r\n")

for k in [None, "yonetici:yanlis", "ayse:pafta-demo", "yonetici:pafta-demo"]:
    y = yonetim(k)
    print(k, y.durum, y.baslik("WWW-Authenticate"))
```

| Durum | Anlamı |
|---|---|
| `401` + `WWW-Authenticate` | kimlik yok ya da yanlış: "kim olduğunu kanıtla" |
| `403` | kimlik doğru, ama bu kişinin bu kaynağa izni yok; kimliği tekrar göndermek işe yaramaz |

Kullanıcı adı `:` içeremez, parola içerebilir: çözülen metin **ilk** `:`'den bölünür.

> [!TUZAK]
> base64 bir **kodlamadır**, şifreleme değil: herkes geri çözebilir. Basic yalnızca HTTPS ile kullanılır. Tarayıcı Basic kimliğini her istekte yeniden gönderir ve bir "çıkış" düğmesi yoktur; web uygulamaları bu yüzden çoğu zaman çerezli oturum (HT08) ya da jeton kullanır.
:::

::: anlat Bearer jetonları
**Bearer** şemasında istemci bir **jeton** gönderir: bir API anahtarı ya da bir kimlik sunucusunun verdiği erişim jetonu. Adı "taşıyan"dan gelir: jetonu taşıyan herkes onu kullanabilir.

```text
GET /api/rapor HTTP/1.1
Host: pafta.test
Authorization: Bearer demo-jeton-123
```

Jeton eksikse ya da geçersizse yine 401 gelir; `WWW-Authenticate` farkı söyleyebilir:

```python
import tezgah

for jeton in [None, "yanlis", "demo-jeton-123"]:
    ek = f"Authorization: Bearer {jeton}\r\n" if jeton else ""
    y = tezgah.yanit(f"GET /api/rapor HTTP/1.1\r\nHost: pafta.test\r\n{ek}\r\n")
    print(jeton, y.durum, y.baslik("WWW-Authenticate"))
```

| | Çerez (HT08) | `Authorization` başlığı |
|---|---|---|
| kim ekler | tarayıcı, kendiliğinden | uygulama kodu, açıkça |
| başka bir siteden başlayan istekte | `SameSite`'a göre gidebilir | gitmez |
| tipik kullanım | web sayfaları | API'ler, betikler, mobil uygulamalar |

> [!GÜVENLİK]
> Parolaları ve jetonları **URL'ye koyma** (`/api/rapor?jeton=...`): adres sunucu günlüklerine, tarayıcı geçmişine ve bir sonraki sayfanın `Referer` başlığına düşer. Başlıkta taşı, yalnızca HTTPS'te gönder ve kendi günlüklerinde `Authorization` değerini maskele. Jetonun süresi ve yetki kapsamı sınırlı olmalı.
:::

::: tahmin
Bir Basic başlığını çözmek. İki satır:

```python
import base64

baslik = "Basic YXlzZTpzaWZyZTpkZW1v"
tur, kimlik = baslik.split(" ", 1)
cozulmus = base64.b64decode(kimlik).decode()
print(tur, cozulmus)
print(cozulmus.partition(":"))
```

???

`Basic ayse:sifre:demo` ve `('ayse', ':', 'sifre:demo')`. base64'ü çözmek için anahtar gerekmez: kimlik bilgisi düz metin olarak ortaya çıkar. Parolanın içinde `:` var; ilk `:`'den bölünce kullanıcı adı `ayse`, parola `sifre:demo` olur. Son `:`'den bölmek parolayı bozardı.
:::

::: gorev Basic başlığı kur
`basic_baslik(kullanici, parola)` fonksiyonu `Authorization` başlığının değerini döndürsün: `"Basic "` ve `kullanici:parola` metninin UTF-8 baytlarının base64 hâli.

```starter
def basic_baslik(kullanici, parola):
    return f"Basic {kullanici}:{parola}"
```

```test
import tezgah
need("basic_baslik")
eq(basic_baslik("yonetici", "pafta-demo"), "Basic eW9uZXRpY2k6cGFmdGEtZGVtbw==", "bilinen değer")
eq(basic_baslik("ayşe", "şifre"), "Basic YXnFn2U6xZ9pZnJl", "Türkçe harfler UTF-8 ile")
eq(basic_baslik("ayse", "sifre:demo"), "Basic YXlzZTpzaWZyZTpkZW1v", "parolada : olabilir")
y = tezgah.yanit(f"GET /yonetim HTTP/1.1\r\nHost: pafta.test\r\nAuthorization: {basic_baslik('yonetici', 'pafta-demo')}\r\n\r\n")
eq(y.durum, 200, "tezgah yöneticiyi kabul ediyor")
y = tezgah.yanit(f"GET /yonetim HTTP/1.1\r\nHost: pafta.test\r\nAuthorization: {basic_baslik('ayse', 'pafta-demo')}\r\n\r\n")
eq(y.durum, 403, "ayse'nin kimliği doğru ama yetkisi yok")
```

```solution
import base64


def basic_baslik(kullanici, parola):
    kimlik = f"{kullanici}:{parola}".encode("utf-8")
    return "Basic " + base64.b64encode(kimlik).decode("ascii")
```

```hint
`base64.b64encode` bayt alır ve bayt döndürür: önce `.encode("utf-8")`, sonra sonucu `.decode("ascii")` ile metne çevir.
```
:::

::: gorev Basic başlığını çöz
`basic_coz(deger)` fonksiyonu bir `Authorization` değerinden `(kullanici, parola)` çıkarsın. Şema adı büyük-küçük harfe duyarsızdır (`basic`, `BASIC`). Şu durumlarda `ValueError` yükseltsin: şema Basic değilse, base64 geçersizse, çözülen metinde `:` yoksa.

```starter
import base64

def basic_coz(deger):
    return tuple(base64.b64decode(deger[6:]).decode().split(":"))
```

```test
need("basic_coz")
eq(basic_coz("Basic eW9uZXRpY2k6cGFmdGEtZGVtbw=="), ("yonetici", "pafta-demo"), "sade")
eq(basic_coz("basic YXlzZTpzaWZyZTpkZW1v"), ("ayse", "sifre:demo"), "küçük harfli şema, parolada :")
eq(basic_coz("BASIC YXnFn2U6xZ9pZnJl"), ("ayşe", "şifre"), "UTF-8")
eq(basic_coz("Basic OnBhcm9sYQ=="), ("", "parola"), "boş kullanıcı adı (':parola')")
raises(ValueError, basic_coz, "Bearer demo-jeton-123", msg="başka şema")
raises(ValueError, basic_coz, "Digest eW9uZXRpY2k6cGFmdGEtZGVtbw==", msg="geçerli base64 olsa da şema Basic değil")
raises(ValueError, basic_coz, "Basic eW9uZXRpY2k=", msg="':' yok")
raises(ValueError, basic_coz, "Basic !!!", msg="geçersiz base64")
raises(ValueError, basic_coz, "Basic", msg="değer yok")
```

```solution
import base64
import binascii


def basic_coz(deger):
    sema, _, kimlik = deger.partition(" ")
    if sema.lower() != "basic" or not kimlik:
        raise ValueError("Basic değil")
    try:
        metin = base64.b64decode(kimlik, validate=True).decode("utf-8")
    except (binascii.Error, UnicodeDecodeError):
        raise ValueError("geçersiz base64")
    kullanici, iki_nokta, parola = metin.partition(":")
    if not iki_nokta:
        raise ValueError("':' yok")
    return (kullanici, parola)
```

```hint
`b64decode(..., validate=True)` geçersiz karakterlerde `binascii.Error` yükseltir (o da bir `ValueError`'dır). `partition(":")` ortadaki parçası boşsa `:` yok demektir.
```
:::

::: gorev Jetonla rapor
`rapor_al(jeton)` fonksiyonu tezgahın `/api/rapor` adresine bir GET göndersin. `jeton` doluysa `Authorization: Bearer <jeton>` başlığını eklesin, boşsa (`None` ya da `""`) hiç eklemesin. Dönüş:

- `200` → `("tamam", gövdedeki acik_bilet)`
- `401` ve `WWW-Authenticate` değeri `error="invalid_token"` içeriyor → `("geçersiz", None)`
- diğer `401` → `("eksik", None)`

```starter
import tezgah

def rapor_al(jeton):
    y = tezgah.yanit(f"GET /api/rapor?jeton={jeton} HTTP/1.1\r\nHost: pafta.test\r\n\r\n")
    return ("tamam", y.json().get("acik_bilet"))
```

```test
import tezgah
need("rapor_al")
ok("?jeton" not in src, "jetonu URL'ye koyma")
acik = len(tezgah.yanit("GET /biletler HTTP/1.1\r\nHost: pafta.test\r\n\r\n").json())
eq(rapor_al("demo-jeton-123"), ("tamam", acik), "geçerli jeton")
eq(rapor_al("yanlis"), ("geçersiz", None), "geçersiz jeton")
eq(rapor_al(None), ("eksik", None), "jeton yok")
eq(rapor_al(""), ("eksik", None), "boş jeton: başlık gönderilmez")
```

```solution
import tezgah


def rapor_al(jeton):
    ek = f"Authorization: Bearer {jeton}\r\n" if jeton else ""
    y = tezgah.yanit(f"GET /api/rapor HTTP/1.1\r\nHost: pafta.test\r\n{ek}\r\n")
    if y.durum == 200:
        return ("tamam", y.json()["acik_bilet"])
    if 'error="invalid_token"' in (y.baslik("WWW-Authenticate") or ""):
        return ("geçersiz", None)
    return ("eksik", None)
```

```hint
`WWW-Authenticate` değerinde `error="invalid_token"` geçip geçmediğine bak; başlık hiç yoksa `None` döner, `or ""` ile metne çevir.
```
:::
