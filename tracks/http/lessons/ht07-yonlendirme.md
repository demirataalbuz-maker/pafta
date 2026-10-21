---
id: ht07
title: Yönlendirmeler
summary: 301, 302, 303, 307 ve 308; kalıcı ile geçici, yönlendirmede yöntemin ve gövdenin ne olduğu, göreli Location'ı çözmek, Post/Redirect/Get kalıbı, yönlendirme zincirleri, döngüler ve sınırlar, açık yönlendirmeye karşı izin listesi.
---

::: anlat Başka yere bak
Bir `3xx` yanıtı ve `Location` başlığı "aradığın şey başka bir adreste" der. İstemci o adrese yeni bir istek gönderir.

| Kod | Kalıcı mı | Sonraki istekte yöntem | Ne için |
|---|---|---|---|
| `301 Moved Permanently` | kalıcı | GET aynı kalır; POST tarihsel olarak GET'e döner | adres taşındı; arama motorları yeni adresi öğrenir |
| `302 Found` | geçici | GET aynı kalır; POST tarihsel olarak GET'e döner | geçici yönlendirme, ör. giriş sayfasına gönderme |
| `303 See Other` | geçici | **her zaman GET** | POST'un sonucunu gösteren sayfaya |
| `307 Temporary Redirect` | geçici | **aynı yöntem, aynı gövde** | |
| `308 Permanent Redirect` | kalıcı | **aynı yöntem, aynı gövde** | |

301 ve 302'nin POST'u GET'e çevirmesi standardın değil tarayıcıların alışkanlığıydı; 307 ve 308 bu belirsizliği gidermek için eklendi. `304 Not Modified` bir yönlendirme değildir: `Location` taşımaz (HT05).

`Location` göreli olabilir ve **o anki adrese göre** çözülür (HT02). Tarayıcılar ve `urllib` yönlendirmeleri kendiliğinden izler; ham istekle her adımı görebilirsin:

```python
import tezgah

yol = "/eski-panel"
for _ in range(5):
    y = tezgah.yanit(f"GET {yol} HTTP/1.1\r\nHost: pafta.test\r\n\r\n")
    print(yol, y.durum, y.baslik("Location"))
    if y.durum not in (301, 302, 303, 307, 308):
        break
    yol = y.baslik("Location")
```

Eski panel adresi kalıcı olarak `/panel`'e taşınmış (301); panel oturum açmamış birini geçici olarak giriş sayfasına gönderiyor (302); giriş sayfası kendisi 200.
:::

::: anlat Post/Redirect/Get, zincirler ve döngüler
Bir form POST ile gönderildikten sonra sunucu sonucu doğrudan göstermek yerine `303` ile sonucun adresine yönlendirir; tarayıcı oraya GET ile gider. Kullanıcı sayfayı yenilerse formu değil sonuç sayfasını yeniden ister: aynı bilet ikinci kez açılmaz. Bu kalıbın adı **Post/Redirect/Get**'tir (PRG); tezgahta `POST /bilet-ac` böyle çalışır.

Yönlendirmeler zincir olabilir (A → B → C) ve yanlış yapılandırılmış bir site kendine yönlendirerek **döngüye** girebilir. İstemciler bu yüzden bir sınır koyar: tarayıcılar yaklaşık 20 adımda, `urllib` 10 adımda (ve aynı adrese tekrar tekrar dönüldüğünü görünce daha erken) durur:

```python
import urllib.error
import urllib.request

import tezgah

with urllib.request.urlopen(tezgah.SUNUCU + "/zincir/3") as r:
    print(r.status, r.url.endswith("/zincir/0"), r.read().decode().strip())
try:
    urllib.request.urlopen(tezgah.SUNUCU + "/dongu")
except urllib.error.HTTPError as e:
    print(e.code, e.reason.splitlines()[0])
```

> [!GÜVENLİK]
> Kullanıcının verdiği bir adrese yönlendiren uç noktalar (`/git?adres=...`) bir **izin listesiyle** sınırlanmalı. Yoksa güvenilir alan adının bir bağlantısı ziyaretçiyi bambaşka bir siteye taşımakta kullanılabilir (açık yönlendirme). En güvenlisi `Location`'ı sitenin kendi göreli yollarıyla sınırlamaktır. Bir siteyi HTTP'den HTTPS'ye taşımak da bir 301 ve `Strict-Transport-Security` başlığıyla yapılır.
:::

::: tahmin
Üç yönlendirme. Üç satır:

```python
from urllib.parse import urljoin
import tezgah

y = tezgah.yanit("GET /goreli HTTP/1.1\r\nHost: pafta.test\r\n\r\n")
print(y.durum, y.baslik("Location"), urljoin("http://pafta.test/goreli", y.baslik("Location")))
y = tezgah.yanit("POST /tasindi HTTP/1.1\r\nHost: pafta.test\r\nContent-Length: 0\r\n\r\n")
print(y.durum, y.baslik("Location"))
y = tezgah.yanit("GET /zincir/2 HTTP/1.1\r\nHost: pafta.test\r\n\r\n")
print(y.durum, y.baslik("Location"))
```

???

`302 sunucular?rol=web http://pafta.test/sunucular?rol=web`, `307 /biletler` ve `302 /zincir/1`. İlk `Location` göreli ve `/` ile başlamıyor; `/goreli` adresinin klasörü kök olduğu için `http://pafta.test/sunucular?rol=web` olur. `/tasindi` 307 döner: istemci bir sonraki isteği **yine POST** olarak ve aynı gövdeyle `/biletler`'e göndermeli. Zincir her adımda bir azalır; sıfıra varınca 200 gelecek.
:::

::: gorev Sonraki yöntem
`sonraki_yontem(yontem, kod)` fonksiyonu bir yönlendirmeden sonra gönderilecek isteğin yöntemini döndürsün. Kod bir yönlendirme değilse (`301`, `302`, `303`, `307`, `308` dışındaki her kod) `None` döndürsün.

| Kod | Kural |
|---|---|
| `303` | `HEAD` ise `HEAD`, değilse `GET` |
| `301`, `302` | `POST` ise `GET`, değilse aynı yöntem |
| `307`, `308` | aynı yöntem |

```starter
def sonraki_yontem(yontem, kod):
    if kod in (301, 302, 303, 307, 308):
        return "GET"
    return None
```

```test
need("sonraki_yontem")
for yontem, kod, beklenen in [("POST", 303, "GET"), ("PUT", 303, "GET"), ("GET", 303, "GET"), ("HEAD", 303, "HEAD"),
                              ("POST", 301, "GET"), ("POST", 302, "GET"), ("PUT", 302, "PUT"), ("GET", 301, "GET"),
                              ("DELETE", 301, "DELETE"), ("POST", 307, "POST"), ("POST", 308, "POST"),
                              ("PUT", 307, "PUT"), ("HEAD", 308, "HEAD")]:
    eq(sonraki_yontem(yontem, kod), beklenen, f"{yontem} + {kod}")
for kod in (200, 300, 304, 305, 306, 309, 404):
    eq(sonraki_yontem("GET", kod), None, f"{kod} bir yönlendirme değil")
```

```solution
def sonraki_yontem(yontem, kod):
    if kod == 303:
        return "HEAD" if yontem == "HEAD" else "GET"
    if kod in (301, 302):
        return "GET" if yontem == "POST" else yontem
    if kod in (307, 308):
        return yontem
    return None
```

```hint
Üç grup var: 303, (301, 302) ve (307, 308). Her grubu ayrı bir `if` ile ele al; hiçbirine girmeyen kod için `None`.
```
:::

::: gorev Zinciri izle
`takip_et(yol, sinir=5)` fonksiyonu tezgahta `yol`'a bir GET göndersin ve yönlendirmeleri **en fazla** `sinir` kez izlesin. `Location` göreli olabilir: o anki adrese göre çöz (`http://pafta.test` + o anki yol) ve bir sonraki isteğe yolu ve varsa sorguyu yaz. Dönüş `(son_durum, gidilen_yollar)` olsun; `gidilen_yollar` başlangıç yolu dahil her istenen yolu sırasıyla içersin. `sinir` aşılacaksa `RuntimeError` yükseltsin.

```starter
import tezgah

def takip_et(yol, sinir=5):
    y = tezgah.yanit(f"GET {yol} HTTP/1.1\r\nHost: pafta.test\r\n\r\n")
    return (y.durum, [yol])
```

```test
need("takip_et")
eq(takip_et("/durum"), (200, ["/durum"]), "yönlendirme yok")
eq(takip_et("/goreli"), (200, ["/goreli", "/sunucular?rol=web"]), "göreli Location ve sorgu")
eq(takip_et("/eski-panel"), (200, ["/eski-panel", "/panel", "/giris"]), "iki adımlı zincir")
eq(takip_et("/son-rapor"), (200, ["/son-rapor", "/rapor.csv"]), "303")
eq(takip_et("/tasindi"), (200, ["/tasindi", "/biletler"]), "307")
eq(takip_et("/kalici"), (200, ["/kalici", "/biletler"]), "308")
eq(takip_et("/zincir/5"), (200, [f"/zincir/{n}" for n in range(5, -1, -1)]), "tam 5 yönlendirme: sınırın içinde")
eq(takip_et("/zincir/2", sinir=2), (200, ["/zincir/2", "/zincir/1", "/zincir/0"]), "sinir=2, iki yönlendirme")
raises(RuntimeError, takip_et, "/zincir/6", msg="6 yönlendirme, sınır 5 → RuntimeError")
raises(RuntimeError, takip_et, "/zincir/3", 2, msg="3 yönlendirme, sınır 2 → RuntimeError")
raises(RuntimeError, takip_et, "/dongu", msg="döngü")
eq(takip_et("/kisa/yok"), (404, ["/kisa/yok"]), "yönlendirme olmayan hata")
```

```solution
from urllib.parse import urljoin, urlsplit

import tezgah

YONLENDIRME = {301, 302, 303, 307, 308}


def takip_et(yol, sinir=5):
    yollar = [yol]
    while True:
        y = tezgah.yanit(f"GET {yol} HTTP/1.1\r\nHost: pafta.test\r\n\r\n")
        if y.durum not in YONLENDIRME:
            return (y.durum, yollar)
        if len(yollar) > sinir:
            raise RuntimeError("çok fazla yönlendirme")
        u = urlsplit(urljoin("http://pafta.test" + yol, y.baslik("Location")))
        yol = u.path + ("?" + u.query if u.query else "")
        yollar.append(yol)
```

```hint
Şimdiye kadar izlenen yönlendirme sayısı `len(yollar) - 1`'dir. Yeni bir yönlendirmeyi izlemeden önce bu sayı `sinir`'e ulaştıysa dur.
```

```hint
`urljoin("http://pafta.test" + yol, location)` göreli adresi çözer; `urlsplit` ile yolu ve sorguyu alıp yeniden birleştir.
```
:::

::: gorev Post/Redirect/Get
`formla_ac(baslik)` fonksiyonu tezgahın `/bilet-ac` adresine `baslik` alanlı bir form POST'u göndersin. Yanıt `303` ise `Location`'daki adrese **GET** ile gidip gelen biletin sözlüğünü (`json()`) döndürsün; başka bir yanıtta `None` döndürsün.

```starter
from urllib.parse import urlencode
import tezgah

def formla_ac(baslik):
    govde = urlencode({"baslik": baslik})
    y = tezgah.yanit(f"POST /bilet-ac HTTP/1.1\r\nHost: pafta.test\r\nContent-Type: application/x-www-form-urlencoded\r\n"
                     f"Content-Length: {len(govde)}\r\n\r\n{govde}")
    return y.json()
```

```test
import tezgah
need("formla_ac")
b = formla_ac("Sertifika süresi doluyor")
ok(isinstance(b, dict), "bilet sözlüğü döndü")
eq((b["baslik"], b["oncelik"]), ("Sertifika süresi doluyor", "orta"), "biletin içeriği")
eq(tezgah.yanit(f"GET /biletler/{b['id']} HTTP/1.1\r\nHost: pafta.test\r\n\r\n").json(), b, "bilet gerçekten açıldı")
eq(formla_ac(""), None, "geçersiz form (422): None")
eq(formla_ac("x" * 81), None, "81 karakter (422): None")
```

```solution
from urllib.parse import urlencode

import tezgah


def formla_ac(baslik):
    govde = urlencode({"baslik": baslik})
    y = tezgah.yanit(f"POST /bilet-ac HTTP/1.1\r\nHost: pafta.test\r\nContent-Type: application/x-www-form-urlencoded\r\n"
                     f"Content-Length: {len(govde)}\r\n\r\n{govde}")
    if y.durum != 303:
        return None
    sonuc = tezgah.yanit(f"GET {y.baslik('Location')} HTTP/1.1\r\nHost: pafta.test\r\n\r\n")
    return sonuc.json()
```

```hint
303'ten sonra yöntem her zaman GET'tir ve gövde gönderilmez: `GET {Location} HTTP/1.1`.
```
:::
