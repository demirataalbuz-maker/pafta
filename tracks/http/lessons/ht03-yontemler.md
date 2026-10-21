---
id: ht03
title: Yöntemler
summary: GET, HEAD, POST, PUT, PATCH, DELETE, OPTIONS ve TRACE; güvenli ve idempotent yöntemler ve neden önemli oldukları, HEAD ile gövdesiz bakmak, OPTIONS ve Allow, 405 ile 501 farkı ve durum değiştiren işlemleri GET'e bağlamamak.
---

::: anlat Fiiller
İstek satırının ilk kelimesi **yöntemdir**: sunucuya o adresle ne yapmak istediğini söyler.

| Yöntem | Ne için | Gövde | Güvenli | İdempotent |
|---|---|---|---|---|
| `GET` | bir kaynağı oku | yok | evet | evet |
| `HEAD` | GET'in yalnızca başlıkları | yok | evet | evet |
| `POST` | yeni bir kaynak oluştur ya da bir işlem başlat | var | hayır | hayır |
| `PUT` | kaynağı gönderilenle **tamamen** değiştir | var | hayır | evet |
| `PATCH` | kaynağı **kısmen** değiştir | var | hayır | hayır |
| `DELETE` | kaynağı sil | genelde yok | hayır | evet |
| `OPTIONS` | bu adres hangi yöntemleri destekliyor | yok | evet | evet |
| `TRACE` | isteği geri yansıt (tanılama) | yok | evet | evet |

- **Güvenli** yöntem sunucudaki durumu değiştirmez. Tarayıcılar, önbellekler ve arama motorları bu yüzden onları serbestçe tekrarlar ya da önceden yükler.
- **İdempotent** yöntemi bir ya da on kez göndermek sunucuda **aynı sonucu bırakır**. Bağlantı koptuğunda istemci idempotent bir isteği güvenle yeniden gönderebilir. POST'u yeniden göndermek ise ikinci bir bilet ya da ikinci bir sipariş demektir.

İdempotent olmak her seferinde aynı **yanıtı** almak demek değildir. Bir bileti iki kez silmek sunucuda aynı durumu bırakır (bilet yok) ama ikinci yanıt farklıdır:

```python
import tezgah

def iste(satir):
    return tezgah.yanit(satir + "\r\nHost: pafta.test\r\n\r\n")

print(iste("DELETE /biletler/2 HTTP/1.1").durum)     #! 204: silindi, gövde yok
print(iste("DELETE /biletler/2 HTTP/1.1").durum)     #! 404: zaten yok
print([b["id"] for b in iste("GET /biletler HTTP/1.1").json()])
```
:::

::: anlat HEAD, OPTIONS ve 405
`HEAD`, GET'in vereceği başlıkların **aynısını** verir ama gövdeyi göndermez. `Content-Length`, GET'in göndereceği gövdenin uzunluğudur. Bir sayfanın var olup olmadığını, boyutunu ya da değişip değişmediğini (HT05) gövdeyi indirmeden öğrenmenin yolu budur.

`OPTIONS` bir adresin hangi yöntemleri kabul ettiğini sorar; cevap `Allow` başlığındadır. Desteklenmeyen bir yöntemle gelirsen sunucu `405 Method Not Allowed` döner ve kurallar gereği yine bir `Allow` başlığı ekler. Sunucunun hiç tanımadığı bir yöntem ise `501 Not Implemented` alır.

```python
import tezgah

def iste(satir):
    return tezgah.yanit(satir + "\r\nHost: pafta.test\r\n\r\n")

y = iste("HEAD /sunucular HTTP/1.1")
print(y.durum, y.baslik("Content-Length"), repr(y.govde))
y = iste("OPTIONS /biletler/1 HTTP/1.1")
print(y.durum, y.baslik("Allow"))
y = iste("PUT /sunucular HTTP/1.1")
print(y.durum, y.baslik("Allow"))
```

| Kod | Ne zaman |
|---|---|
| `405 Method Not Allowed` | adres var, ama bu yöntemi kabul etmiyor (`Allow` listeyi verir) |
| `501 Not Implemented` | sunucu bu yöntemi hiç tanımıyor |

> [!GÜVENLİK]
> Durum değiştiren işleri GET'e bağlama (`GET /biletler/2/sil` gibi). Bağlantı önizlemeleri, önbellekler ve tarayıcının ön yüklemesi böyle bir adresi kimse tıklamadan çağırabilir; başka bir sitedeki bir resim etiketi bile onu tetikleyebilir. Durum değiştiren uç noktalar POST, PUT ya da DELETE olmalı ve oturum çerezinin yanında ek bir korumayla (form jetonu, `SameSite` çerezi; HT08) korunmalı. Kullanılmayan yöntemler, özellikle `TRACE`, kapalı tutulur.
:::

::: tahmin
Dört satır. Kod, `Allow` ve gövde boş mu?

```python
import tezgah

def iste(satir):
    return tezgah.yanit(satir + "\r\nHost: pafta.test\r\n\r\n")

for satir in ["HEAD /durum HTTP/1.1", "OPTIONS /cikis HTTP/1.1", "GET /cikis HTTP/1.1", "TRACE / HTTP/1.1"]:
    y = iste(satir)
    print(y.durum, y.baslik("Allow"), y.govde == "")
```

???

`200 None True`, `204 POST, OPTIONS True`, `405 POST, OPTIONS False` ve `405 GET, HEAD, OPTIONS False`. HEAD başarılıdır ama gövde gelmez; `Allow` yalnızca OPTIONS ve 405 yanıtlarında vardır. `/cikis` yalnızca POST kabul eder: OPTIONS `204 No Content` ile listeyi verir, GET ise 405 ve hatayı anlatan bir JSON gövdesi alır. Ana sayfa `TRACE`'i desteklemez: yine 405 ve sayfanın kabul ettiği yöntemler.
:::

::: gorev İzin verilen yöntemler
`izinli_yontemler(yol)` fonksiyonu tezgaha o yol için bir **OPTIONS** isteği göndersin ve `Allow` başlığındaki yöntemleri, sırasını koruyarak bir liste olarak döndürsün. Yanıtta `Allow` yoksa (ör. adres bulunamadı) boş liste döndürsün.

```starter
import tezgah

def izinli_yontemler(yol):
    return ["GET"]
```

```test
need("izinli_yontemler")
ok("OPTIONS" in src, "OPTIONS isteği gönder")
eq(izinli_yontemler("/biletler"), ["GET", "POST", "HEAD", "OPTIONS"], "/biletler")
eq(izinli_yontemler("/biletler/1"), ["GET", "PUT", "DELETE", "HEAD", "OPTIONS"], "/biletler/1")
eq(izinli_yontemler("/cikis"), ["POST", "OPTIONS"], "/cikis: yalnızca POST")
eq(izinli_yontemler("/yok"), [], "bulunamayan adres: Allow yok")
```

```solution
import tezgah


def izinli_yontemler(yol):
    y = tezgah.yanit(f"OPTIONS {yol} HTTP/1.1\r\nHost: pafta.test\r\n\r\n")
    allow = y.baslik("Allow")
    if not allow:
        return []
    return [parca.strip() for parca in allow.split(",")]
```

```hint
`tezgah.yanit(f"OPTIONS {yol} HTTP/1.1\r\nHost: pafta.test\r\n\r\n")` ve `y.baslik("Allow")`. Değeri virgüllerden böl ve her parçanın boşluğunu at.
```
:::

::: gorev Güvenli mi, idempotent mi?
`ozellik(yontem)` fonksiyonu bir yöntem adı için `(guvenli, idempotent)` ikilisini döndürsün (anlatımdaki tabloya göre). Tanımadığı bir ad için, **küçük harfle yazılmış** standart yöntemler dahil, `ValueError` yükseltsin.

```starter
def ozellik(yontem):
    return (yontem == "GET", yontem == "GET")
```

```test
need("ozellik")
beklenen = {"GET": (True, True), "HEAD": (True, True), "OPTIONS": (True, True), "TRACE": (True, True),
            "PUT": (False, True), "DELETE": (False, True), "POST": (False, False), "PATCH": (False, False)}
for yontem, ikili in beklenen.items():
    eq(ozellik(yontem), ikili, yontem)
raises(ValueError, ozellik, "get", msg="küçük harfli get bir yöntem değildir")
raises(ValueError, ozellik, "FOO", msg="bilinmeyen yöntem")
raises(ValueError, ozellik, "", msg="boş ad")
```

```solution
GUVENLI = {"GET", "HEAD", "OPTIONS", "TRACE"}
IDEMPOTENT = GUVENLI | {"PUT", "DELETE"}
BILINEN = IDEMPOTENT | {"POST", "PATCH"}


def ozellik(yontem):
    if yontem not in BILINEN:
        raise ValueError(f"bilinmeyen yöntem: {yontem!r}")
    return (yontem in GUVENLI, yontem in IDEMPOTENT)
```

```hint
Üç küme yeter: güvenliler, idempotentler (güvenliler + PUT, DELETE) ve bilinenler (idempotentler + POST, PATCH). Karşılaştırmayı olduğu gibi yap: yöntem adları büyük-küçük harfe duyarlıdır.
```
:::

::: gorev HEAD ile boyut
`boyutlar(yollar)` fonksiyonu her yol için tezgaha bir **HEAD** isteği göndersin ve `{yol: boyut}` sözlüğü döndürsün. Boyut `Content-Length` başlığının **tam sayı** değeridir; başlık yoksa `None`.

```starter
import tezgah

def boyutlar(yollar):
    return {yol: 0 for yol in yollar}
```

```test
import tezgah
need("boyutlar")
ok("HEAD" in src, "HEAD isteği gönder")
yollar = ["/", "/sunucular", "/durum", "/yok"]
b = boyutlar(yollar)
for yol in yollar:
    g = tezgah.yanit(f"GET {yol} HTTP/1.1\r\nHost: pafta.test\r\n\r\n")
    eq(b[yol], len(g.govde_bayt), f"{yol}: GET'in gövdesiyle aynı uzunluk")
eq(boyutlar(["/akis"]), {"/akis": None}, "Content-Length yok (chunked) → None")
eq(boyutlar([]), {}, "boş liste")
```

```solution
import tezgah


def boyutlar(yollar):
    sonuc = {}
    for yol in yollar:
        y = tezgah.yanit(f"HEAD {yol} HTTP/1.1\r\nHost: pafta.test\r\n\r\n")
        uzunluk = y.baslik("Content-Length")
        sonuc[yol] = int(uzunluk) if uzunluk is not None else None
    return sonuc
```

```hint
HEAD yanıtında gövde yoktur ama `Content-Length` vardır: `int(y.baslik("Content-Length"))`. `/akis` parça parça (chunked) gönderildiği için uzunluğunu önceden bildirmez.
```
:::
