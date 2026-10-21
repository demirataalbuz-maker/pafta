---
id: ht04
title: Durum Kodları
summary: Beş sınıf (1xx–5xx) ve kimin hatası olduğu; 200, 201, 204, 400, 401, 403, 404, 405, 409, 410, 411, 413, 415, 422, 429, 500, 502, 503, 504; hangi hataların tekrar denenebileceği, Retry-After ve geri çekilme, hata yanıtlarında iç ayrıntı vermemek.
---

::: anlat Beş sınıf
Durum kodunun **ilk rakamı** neyin olduğunu söyler; ayrıntıyı geri kalanı verir:

| Sınıf | Anlamı | Örnekler |
|---|---|---|
| `1xx` | bilgi: istek alındı, sürüyor | `100 Continue`, `101 Switching Protocols` |
| `2xx` | başarı | `200 OK`, `201 Created` (yeni kaynağın adresi `Location`'da), `204 No Content` |
| `3xx` | yönlendirme ya da "değişmedi" | `301`, `302`, `303`, `307`, `308` (HT07), `304 Not Modified` (HT05) |
| `4xx` | **istemcinin** hatası: isteği düzelt | aşağıda |
| `5xx` | **sunucunun** hatası: istek doğru olabilir, sunucu yapamadı | aşağıda |

| Kod | Ne demek | Ne yapılır |
|---|---|---|
| `400 Bad Request` | istek bozuk | isteği düzelt |
| `401 Unauthorized` | kimlik bilgisi yok ya da yanlış (adı yanıltıcıdır: "kimliği doğrulanmadı") | kimlik bilgisi gönder (HT09) |
| `403 Forbidden` | kim olduğun belli, ama izin yok | aynı kimlikle tekrar denemek işe yaramaz |
| `404 Not Found` | böyle bir kaynak yok | |
| `405 Method Not Allowed` | adres var, yöntem desteklenmiyor | `Allow`'a bak |
| `409 Conflict` | kaynağın şu anki durumuyla çakışıyor (aynı ad, eski sürüm) | |
| `410 Gone` | **kalıcı** olarak kaldırıldı | bağlantıyı sil |
| `411 Length Required` | gövde var ama `Content-Length` yok | |
| `413` | gövde çok büyük (RFC 9110'daki adı `Content Too Large`; Python'da hâlâ `Request Entity Too Large`) | |
| `415 Unsupported Media Type` | gövdenin türü (`Content-Type`) kabul edilmiyor | |
| `422 Unprocessable Entity` | biçim doğru, içerik geçersiz (doğrulama hatası) | |
| `429 Too Many Requests` | hız sınırı aşıldı | `Retry-After` kadar bekle |
| `500 Internal Server Error` | sunucuda beklenmeyen bir hata | |
| `502 Bad Gateway` | aradaki sunucu (vekil, yük dengeleyici) arkadakinden geçersiz bir yanıt aldı | |
| `503 Service Unavailable` | hizmet **geçici** olarak yok (bakım, aşırı yük) | `Retry-After` |
| `504 Gateway Timeout` | aradaki sunucu arkadakini bekledi, yanıt gelmedi | |

```python
import tezgah

for yol in ["/biletler/1", "/biletler/99", "/v1/durum", "/hata", "/bakim"]:
    y = tezgah.yanit(f"GET {yol} HTTP/1.1\r\nHost: pafta.test\r\n\r\n")
    print(yol, y.durum, y.neden, y.baslik("Retry-After"))
```

> [!TUZAK]
> `404` ile `410` farklı şeyler söyler: 404 "şu an burada yok" (belki hiç olmadı, belki geri gelir), 410 "vardı, bilerek kaldırıldı". `401` ile `403` de farklıdır: 401 "seni tanımıyorum", 403 "seni tanıyorum, izin yok". Bazı sunucular, var olduğunu bile söylemek istemedikleri kaynaklara bilerek 404 döner.
:::

::: anlat Tekrar denemek
Bir hata aldığında ilk soru şudur: **aynı isteği yeniden göndermek işe yarar mı?**

| Durum | Tekrar dene? |
|---|---|
| `408` (istek zaman aşımı), `429`, `502`, `503`, `504` | **evet**, bekleyerek: sorun geçici olabilir |
| diğer `4xx` | **hayır**: önce isteği düzelt; aynı istek aynı hatayı alır |
| `500`, `501` | hayır ya da bir kez: sunucu tarafında bir hata; bildirmek gerekir |

`Retry-After` başlığı ne kadar bekleneceğini söyler: saniye (`120`) ya da bir HTTP tarihi. Başlık yoksa istemciler **üstel geri çekilme** kullanır: 1, 2, 4, 8 saniye... ve bir üst sınır. Yalnızca idempotent istekler (HT03) kendiliğinden yeniden denenir; bir POST'u körü körüne tekrarlamak işi iki kez yaptırabilir.

Tezgahtaki `/sinir` bir hız sınırıdır: bir çalıştırmada ilk üç isteği geçirir, sonra `429` döner. Kalan hakkı `X-Kalan-Hak` başlığında söyler.

> [!GÜVENLİK]
> Hata yanıtları iç ayrıntı taşımamalı: yığın izi, kütüphane sürümü, SQL sorgusu ya da dosya yolu kullanıcıya değil sunucu günlüğüne gider. Kullanıcı genel bir mesaj ve gerekiyorsa bir hata kimliği görür (`{"hata": "beklenmeyen bir sorun oluştu"}`). Hız sınırları da tek bir istemcinin hizmeti herkes için yavaşlatmasını önleyen bir savunmadır.
:::

::: tahmin
Aynı adrese dört istek. Dört satır:

```python
import tezgah

for _ in range(4):
    y = tezgah.yanit("GET /sinir HTTP/1.1\r\nHost: pafta.test\r\n\r\n")
    print(y.durum, y.baslik("X-Kalan-Hak"), y.baslik("Retry-After"))
```

???

`200 2 None`, `200 1 None`, `200 0 None` ve `429 None 30`. İlk üç istek geçer ve her biri kalan hakkı bir azaltır. Dördüncüsü hız sınırına takılır: `429 Too Many Requests`, kalan hak başlığı yok, `Retry-After: 30` istemciye otuz saniye beklemesini söyler.
:::

::: gorev Sınıf adı
`sinif(kod)` fonksiyonu bir durum kodunun sınıfını döndürsün: `"bilgi"`, `"başarı"`, `"yönlendirme"`, `"istemci hatası"` ya da `"sunucu hatası"`. Kod 100 ile 599 arasında değilse `ValueError` yükseltsin.

```starter
def sinif(kod):
    if kod < 400:
        return "başarı"
    return "istemci hatası"
```

```test
need("sinif")
for kod, ad in [(100, "bilgi"), (199, "bilgi"), (200, "başarı"), (204, "başarı"), (299, "başarı"),
                (300, "yönlendirme"), (304, "yönlendirme"), (399, "yönlendirme"), (400, "istemci hatası"),
                (499, "istemci hatası"), (500, "sunucu hatası"), (599, "sunucu hatası")]:
    eq(sinif(kod), ad, f"{kod}")
raises(ValueError, sinif, 99, msg="99 geçersiz")
raises(ValueError, sinif, 600, msg="600 geçersiz")
raises(ValueError, sinif, 0, msg="0 geçersiz")
```

```solution
ADLAR = ["bilgi", "başarı", "yönlendirme", "istemci hatası", "sunucu hatası"]


def sinif(kod):
    if not 100 <= kod <= 599:
        raise ValueError(f"geçersiz durum kodu: {kod}")
    return ADLAR[kod // 100 - 1]
```

```hint
Sınıf ilk rakamdır: `kod // 100`. Önce aralığı denetle: `100 <= kod <= 599`.
```
:::

::: gorev Ne yapmalı?
`ne_yapmali(y)` fonksiyonu bir `tezgah` yanıtına (`y.durum`, `y.baslik(...)`) bakıp ne yapılacağını söylesin:

| Durum | Dönüş |
|---|---|
| `2xx`, `3xx` | `("tamam", None)` |
| `408`, `429`, `502`, `503`, `504` | `("bekle", saniye)`: `Retry-After` varsa onun tam sayı değeri, yoksa `1` |
| diğer `4xx` | `("düzelt", None)` |
| diğer `5xx` | `("bildir", None)` |

```starter
def ne_yapmali(y):
    if y.durum == 200:
        return ("tamam", None)
    return ("düzelt", None)
```

```test
import tezgah
need("ne_yapmali")
def iste(satir):
    return tezgah.yanit(satir + "\r\nHost: pafta.test\r\n\r\n")
eq(ne_yapmali(iste("GET /durum HTTP/1.1")), ("tamam", None), "200")
eq(ne_yapmali(iste("GET /kisa/w1 HTTP/1.1")), ("tamam", None), "302 yönlendirme")
eq(ne_yapmali(iste("GET /yok HTTP/1.1")), ("düzelt", None), "404")
eq(ne_yapmali(iste("GET /bakim HTTP/1.1")), ("bekle", 120), "503 + Retry-After: 120")
eq(ne_yapmali(iste("GET /hata HTTP/1.1")), ("bildir", None), "500")
eq(ne_yapmali(iste("FOO / HTTP/1.1")), ("bildir", None), "501")
for _ in range(4):
    y = iste("GET /sinir HTTP/1.1")
eq(ne_yapmali(y), ("bekle", 30), "429 + Retry-After: 30")
sahte = lambda satir: tezgah.Yanit(satir.encode() + b"\r\n\r\n")
eq(ne_yapmali(sahte("HTTP/1.1 503 Service Unavailable")), ("bekle", 1), "Retry-After yok → 1")
eq(ne_yapmali(sahte("HTTP/1.1 408 Request Timeout")), ("bekle", 1), "408")
eq(ne_yapmali(sahte("HTTP/1.1 504 Gateway Timeout\r\nRetry-After: 5")), ("bekle", 5), "504 + Retry-After: 5")
eq(ne_yapmali(sahte("HTTP/1.1 502 Bad Gateway")), ("bekle", 1), "502")
eq(ne_yapmali(sahte("HTTP/1.1 399 Sinir")), ("tamam", None), "399 hâlâ 3xx")
eq(ne_yapmali(sahte("HTTP/1.1 400 Bad Request")), ("düzelt", None), "400 ilk istemci hatası")
eq(ne_yapmali(sahte("HTTP/1.1 499 Sinir")), ("düzelt", None), "499 son istemci hatası")
eq(ne_yapmali(sahte("HTTP/1.1 599 Sinir")), ("bildir", None), "599 sunucu hatası")
```

```solution
TEKRAR = {408, 429, 502, 503, 504}


def ne_yapmali(y):
    if y.durum in TEKRAR:
        bekle = y.baslik("Retry-After")
        return ("bekle", int(bekle) if bekle else 1)
    if y.durum < 400:
        return ("tamam", None)
    if y.durum < 500:
        return ("düzelt", None)
    return ("bildir", None)
```

```hint
Önce tekrar denenebilir kodları bir kümede ara; sonra sınıfa bak: 400'ün altı tamam, 500'ün altı düzelt, gerisi bildir.
```
:::

::: gorev Sınıra saygı
`hakki_kullan(n)` fonksiyonu tezgahın `/sinir` adresine **en fazla** `n` GET isteği göndersin, ama ilk `429`'da dursun. `(basarili_istek_sayisi, bekleme)` döndürsün: `bekleme` 429 alındıysa `Retry-After`'ın tam sayı değeri, alınmadıysa `None`. Sınır bir çalıştırma boyunca sayılır: önceki çağrılar hakkı tüketir.

```starter
import tezgah

def hakki_kullan(n):
    for _ in range(n):
        tezgah.yanit("GET /sinir HTTP/1.1\r\nHost: pafta.test\r\n\r\n")
    return (n, None)
```

```test
import tezgah
need("hakki_kullan")
eq(hakki_kullan(0), (0, None), "hiç istek yok")
eq(hakki_kullan(2), (2, None), "ilk iki istek geçer")
eq(hakki_kullan(5), (1, 30), "üçüncü geçer, dördüncüde 429: dur")
eq(hakki_kullan(5), (0, 30), "hak bitti: ilk istekte 429")
```

```solution
import tezgah


def hakki_kullan(n):
    basarili = 0
    for _ in range(n):
        y = tezgah.yanit("GET /sinir HTTP/1.1\r\nHost: pafta.test\r\n\r\n")
        if y.durum == 429:
            return (basarili, int(y.baslik("Retry-After")))
        basarili += 1
    return (basarili, None)
```

```hint
Döngüde her yanıta bak: `y.durum == 429` ise hemen dön ve `Retry-After`'ı `int` yap; değilse sayacı artır.
```
:::
