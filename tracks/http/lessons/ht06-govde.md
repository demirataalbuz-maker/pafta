---
id: ht06
title: Gövde Göndermek
summary: Content-Type ile gövdenin biçimi (form, JSON, multipart, düz metin), Content-Length'in karakter değil bayt sayması, yanlış uzunluğun sonuçları, 201 ve Location, 400/411/413/415/422 ile sunucunun reddetme nedenleri ve gövdeyi sunucuda doğrulamak.
---

::: anlat Gövde ve türü
POST ve PUT gibi istekler bir **gövde** taşır. Sunucu gövdeyi iki başlıkla okur: `Content-Type` biçimini, `Content-Length` kaç **bayt** okuyacağını söyler.

| Tür | Örnek gövde | Nerede |
|---|---|---|
| `application/x-www-form-urlencoded` | `baslik=Disk+dolu&oncelik=y%C3%BCksek` | HTML formlarının varsayılanı (HT11) |
| `application/json` | `{"baslik": "Disk dolu", "oncelik": "yüksek"}` | API'ler |
| `multipart/form-data; boundary=...` | sınır çizgileriyle ayrılmış parçalar | dosya yükleyen formlar |
| `text/plain` | düz metin | nadiren |

Tezgahta `POST /biletler` yeni bir bilet açar. Başarılıysa `201 Created` döner ve yeni biletin adresini `Location` başlığına yazar:

```python
import json
import tezgah

govde = json.dumps({"baslik": "Yedek gecikti", "oncelik": "yüksek"}, ensure_ascii=False).encode("utf-8")
istek = (b"POST /biletler HTTP/1.1\r\nHost: pafta.test\r\nContent-Type: application/json\r\n"
         b"Content-Length: " + str(len(govde)).encode() + b"\r\n\r\n" + govde)
y = tezgah.yanit(istek)
print(y.durum, y.baslik("Location"), y.json())
```

Aynı bilet bir form gövdesiyle de açılabilir: `urlencode` gövdeyi kurar (HT02).

```python
from urllib.parse import urlencode
import tezgah

govde = urlencode({"baslik": "Disk dolu", "oncelik": "kritik"})
y = tezgah.yanit(f"POST /biletler HTTP/1.1\r\nHost: pafta.test\r\nContent-Type: application/x-www-form-urlencoded\r\n"
                 f"Content-Length: {len(govde)}\r\n\r\n{govde}")
print(govde, y.durum, y.baslik("Location"))
```

Sunucunun bir gövdeyi reddetme nedenleri farklı kodlarla söylenir:

| Kod | Neden (tezgahta) |
|---|---|
| `411 Length Required` | gövde var ama `Content-Length` yok |
| `413` | gövde 4096 bayttan büyük |
| `415 Unsupported Media Type` | `Content-Type` JSON ya da form değil |
| `400 Bad Request` | gövde geçerli JSON değil |
| `422 Unprocessable Entity` | biçim doğru ama alanlar geçersiz: başlık 1–80 karakter, öncelik `düşük`/`orta`/`yüksek`/`kritik` |
:::

::: anlat Bayt say, karakter değil
`Content-Length` **bayt** sayısıdır. ASCII'de her karakter bir bayttır, ama UTF-8'de `ğ`, `ş`, `ı`, `ö` ikişer bayttır. `len(metin)` karakter sayar; doğru uzunluk `len(metin.encode("utf-8"))`'tir.

| Uzunluk | Ne olur |
|---|---|
| doğru | sunucu tam gövdeyi okur |
| **kısa** | sunucu gövdenin başını okur, kesik gövde bozuk görünür; arta kalan baytlar bağlantıdaki bir sonraki istek sanılır |
| **uzun** | sunucu gelmeyecek baytları bekler; istek zaman aşımına uğrar |

`json.dumps` varsayılan olarak Türkçe harfleri `ğ` gibi kaçış dizileriyle yazar (`ensure_ascii=True`); o zaman gövde saf ASCII'dir ve bayt sayısı karakter sayısına eşittir. `ensure_ascii=False` daha okunur bir gövde verir ama uzunluğu baytla hesaplamayı zorunlu kılar.

### multipart/form-data
Dosya yükleyen formlar gövdeyi parçalara böler. Her parça bir **sınır** satırıyla başlar (`--` ve `boundary` değeri), kendi başlıklarını taşır ve son sınır `--` ile biter. Tezgah bu türü kabul etmez (415); okuyabilmen yeter:

```text
POST /yukle HTTP/1.1
Host: pafta.test
Content-Type: multipart/form-data; boundary=pafta42

--pafta42
Content-Disposition: form-data; name="baslik"

Disk dolu
--pafta42
Content-Disposition: form-data; name="ek"; filename="df.txt"
Content-Type: text/plain

/dev/sda1 95%
--pafta42--
```

> [!GÜVENLİK]
> Kendi sunucunda istemcinin gönderdiğine güvenme: gövde boyutunu sınırla (413), `Content-Type`'a göre ayrıştır ve beklemediğini reddet (415), alanları tür, uzunluk ve izinli değerler olarak doğrula (422). Yüklenen dosyanın adı ve türü de istemcinin beyanıdır; doğrulamadan kullanma, kendi adınla sakla.
:::

::: tahmin
Aynı gövde, iki farklı `Content-Length`. İki satır:

```python
import json
import tezgah

govde = json.dumps({"baslik": "Ağ yavaş"}, ensure_ascii=False)
for uzunluk in [len(govde), len(govde.encode("utf-8"))]:
    y = tezgah.yanit(f"POST /biletler HTTP/1.1\r\nHost: pafta.test\r\nContent-Type: application/json\r\n"
                     f"Content-Length: {uzunluk}\r\n\r\n{govde}")
    print(uzunluk, y.durum, y.json().get("hata") or y.baslik("Location"), y.kalan_bayt != b"")
```

???

`22 400 gövde geçerli JSON değil True` ve `24 201 /biletler/3 False`. Gövde 22 karakter ama 24 bayttır (`ğ` ve `ş` ikişer bayt). Karakter sayısını yazan istekte sunucu ilk 22 baytı okur; gövde kesildiği için JSON bozuktur: 400. Arta kalan iki bayt bir sonraki istek sanılır ve ona ikinci bir hata yanıtı gelir (`kalan_bayt` boş değil). Bayt sayısıyla gönderilen istek başarılıdır: 201 ve yeni biletin adresi.
:::

::: gorev JSON isteği
`json_istegi(yol, veri)` fonksiyonu `veri` sözlüğünü JSON gövdesi olarak taşıyan ham bir POST isteğini **bayt** olarak döndürsün: `Host: pafta.test`, `Content-Type: application/json` ve doğru `Content-Length`.

```starter
import json

def json_istegi(yol, veri):
    govde = json.dumps(veri, ensure_ascii=False)
    return (f"POST {yol} HTTP/1.1\r\nHost: pafta.test\r\nContent-Type: application/json\r\n"
            f"Content-Length: {len(govde)}\r\n\r\n{govde}").encode("utf-8")
```

```test
import json
import tezgah
need("json_istegi")
ham = json_istegi("/biletler", {"baslik": "Ağ yavaş, şube kesik", "oncelik": "kritik"})
ok(isinstance(ham, bytes), "bayt döndür")
bas, _, govde = ham.partition(b"\r\n\r\n")
basliklar = {s.split(b":", 1)[0].strip().lower(): s.split(b":", 1)[1].strip() for s in bas.split(b"\r\n")[1:]}
eq(int(basliklar[b"content-length"]), len(govde), "Content-Length gövdenin bayt uzunluğu")
eq(json.loads(govde), {"baslik": "Ağ yavaş, şube kesik", "oncelik": "kritik"}, "gövde verinin JSON'u")
y = tezgah.yanit(ham)
eq((y.durum, y.json()["baslik"]), (201, "Ağ yavaş, şube kesik"), "sunucu Türkçe başlığı eksiksiz aldı")
y = tezgah.yanit(json_istegi("/biletler", {}))
eq((y.durum, y.kalan_bayt), (422, b""), "boş nesne: geçerli JSON, eksik alan → 422")
```

```solution
import json


def json_istegi(yol, veri):
    govde = json.dumps(veri, ensure_ascii=False).encode("utf-8")
    bas = (f"POST {yol} HTTP/1.1\r\nHost: pafta.test\r\nContent-Type: application/json\r\n"
           f"Content-Length: {len(govde)}\r\n\r\n")
    return bas.encode("ascii") + govde
```

```hint
Gövdeyi önce baytlara çevir (`.encode("utf-8")`), uzunluğu o baytlardan al, sonra başlık bölümünü ayrıca kodlayıp birleştir.
```
:::

::: gorev Form gönder
`form_istegi(yol, alanlar)` fonksiyonu `alanlar` sözlüğünü `application/x-www-form-urlencoded` gövdesi olarak taşıyan ham bir POST isteğini bayt olarak döndürsün (`Host: pafta.test`, doğru `Content-Length`). Değerlerde boşluk, `&`, `=`, `+`, `%` ve Türkçe harfler olabilir.

```starter
def form_istegi(yol, alanlar):
    govde = "&".join(f"{k}={v}" for k, v in alanlar.items())
    return (f"POST {yol} HTTP/1.1\r\nHost: pafta.test\r\nContent-Type: application/x-www-form-urlencoded\r\n"
            f"Content-Length: {len(govde)}\r\n\r\n{govde}").encode()
```

```test
import tezgah
need("form_istegi")
for baslik in ["Disk dolu & yavaş", "a+b=c %100", "Yedek"]:
    y = tezgah.yanit(form_istegi("/bilet-ac", {"baslik": baslik, "oncelik": "yüksek", "aciklama": ""}))
    eq(y.durum, 303, f"form kabul edildi ({baslik})")
    b = tezgah.yanit(f"GET {y.baslik('Location')} HTTP/1.1\r\nHost: pafta.test\r\n\r\n").json()
    eq((b["baslik"], b["oncelik"]), (baslik, "yüksek"), f"sunucu değeri aynen aldı ({baslik})")
y = tezgah.yanit(form_istegi("/bilet-ac", {"oncelik": "orta"}))
eq(y.durum, 422, "başlık yoksa 422")
```

```solution
from urllib.parse import urlencode


def form_istegi(yol, alanlar):
    govde = urlencode(alanlar).encode("ascii")
    bas = (f"POST {yol} HTTP/1.1\r\nHost: pafta.test\r\nContent-Type: application/x-www-form-urlencoded\r\n"
           f"Content-Length: {len(govde)}\r\n\r\n")
    return bas.encode("ascii") + govde
```

```hint
`urllib.parse.urlencode(alanlar)` her değeri doğru kodlar ve sonuç saf ASCII'dir; uzunluğu o metinden ya da baytlarından alabilirsin.
```
:::

::: gorev Bilet aç
`bilet_ac(baslik, oncelik=None)` fonksiyonu tezgahta JSON ile bir bilet açsın. `oncelik` `None` ise gövdeye hiç konmasın (sunucu `orta` kabul eder). Dönüş:

- `201` → `("tamam", bilet_no)`: `bilet_no`, `Location` başlığındaki numaranın **tam sayı** hâli (`/biletler/7` → `7`)
- başka her durum → `("hata", durum_kodu, gövdedeki "hata" mesajı)`

```starter
import json
import tezgah

def bilet_ac(baslik, oncelik=None):
    return ("tamam", 1)
```

```test
import tezgah
need("bilet_ac")
def getir(no):
    return tezgah.yanit(f"GET /biletler/{no} HTTP/1.1\r\nHost: pafta.test\r\n\r\n").json()
s = bilet_ac("Yazıcı kuyruğu takıldı", "düşük")
eq(s[0], "tamam", "geçerli bilet")
ok(isinstance(s[1], int), "bilet numarası bir int")
eq(getir(s[1]), {"id": s[1], "baslik": "Yazıcı kuyruğu takıldı", "oncelik": "düşük"}, "bilet gerçekten açıldı")
s = bilet_ac("Varsayılan öncelik")
eq(getir(s[1])["oncelik"], "orta", "öncelik verilmezse orta")
eq(bilet_ac("x" * 80)[0], "tamam", "tam 80 karakter kabul")
eq(bilet_ac("x" * 81), ("hata", 422, "başlık 1-80 karakter olmalı"), "81 karakter ret")
eq(bilet_ac("Disk", "acil"), ("hata", 422, "geçersiz öncelik"), "listede olmayan öncelik")
eq(bilet_ac(""), ("hata", 422, "başlık 1-80 karakter olmalı"), "boş başlık")
```

```solution
import json

import tezgah


def bilet_ac(baslik, oncelik=None):
    veri = {"baslik": baslik}
    if oncelik is not None:
        veri["oncelik"] = oncelik
    govde = json.dumps(veri).encode("utf-8")
    y = tezgah.yanit(b"POST /biletler HTTP/1.1\r\nHost: pafta.test\r\nContent-Type: application/json\r\n"
                     b"Content-Length: " + str(len(govde)).encode() + b"\r\n\r\n" + govde)
    if y.durum == 201:
        return ("tamam", int(y.baslik("Location").rsplit("/", 1)[1]))
    return ("hata", y.durum, y.json()["hata"])
```

```hint
`json.dumps(veri)` varsayılan olarak ASCII üretir; yine de uzunluğu bayttan almak alışkanlık olsun. `Location` değerini son `/`'den böl: `rsplit("/", 1)[1]`.
```
:::
