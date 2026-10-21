---
id: ht13
title: Telin Üstünde · Bağlantı ve Çerçeveleme
summary: Kalıcı bağlantılar ve Connection başlığı, bir bağlantıdaki mesajların sınırını belirleyen Content-Length ve chunked aktarım, art arda gönderilen istekler ve sırayla gelen yanıtlar, belirsiz çerçevelemeye karşı katı ayrıştırma, HTTP/2 ve HTTP/3'ün değiştirdikleri ve CORS'un ne olduğu ve ne olmadığı.
---

::: anlat Bir bağlantı, birçok mesaj
HTTP/1.0'da her istek yeni bir TCP bağlantısı açardı. HTTP/1.1'de bağlantı varsayılan olarak **açık kalır** ve aynı bağlantıdan art arda istekler gider. Kapatmak isteyen taraf `Connection: close` yazar. HTTP/1.0'da tersi geçerliydi: bağlantının açık kalması `Connection: keep-alive` ile istenirdi.

Aynı bağlantıda birden çok mesaj olunca bir soru doğar: **bir mesaj nerede biter?** Buna **çerçeveleme** denir:

| Yol | Nasıl |
|---|---|
| `Content-Length: n` | gövde tam `n` bayttır; sonrası bir sonraki mesajdır |
| `Transfer-Encoding: chunked` | gövde parçalar hâlinde gelir, boyu sıfır olan parça sonu gösterir (aşağıda) |
| ikisi de yok (yanıtta) | gövde bağlantı kapanana kadar sürer; `204` ve `304` gibi yanıtların ise hiç gövdesi yoktur |

İstemci iki isteği **tek seferde** gönderebilir; sunucu yanıtları aynı sırayla, art arda yazar. `tezgah.yanit` ilk yanıtı `Content-Length`'e göre keser ve gerisini `kalan_bayt`'ta tutar:

```python
import tezgah

iki = ("GET /durum HTTP/1.1\r\nHost: pafta.test\r\n\r\n"
       "GET /sunucular/web01 HTTP/1.1\r\nHost: pafta.test\r\n\r\n")
y = tezgah.yanit(iki)
print(y.durum, y.govde)
ikinci = tezgah.Yanit(y.kalan_bayt)
print(ikinci.durum, ikinci.json()["ad"])
```

Bu art arda göndermenin (pipelining) bir zayıflığı var: yavaş bir yanıt arkasındakileri bekletir. Tarayıcılar bu yüzden HTTP/1.1'de onun yerine aynı siteye birkaç bağlantı birden açar.
:::

::: anlat Parça parça: chunked
Sunucu gövdenin uzunluğunu önceden bilmiyorsa (akan bir rapor, üretilmekte olan bir sayfa) `Transfer-Encoding: chunked` kullanır. Her parça, **onaltılık** yazılmış bayt uzunluğu, CRLF, veri ve yine CRLF'dir; uzunluğu `0` olan parça gövdenin bittiğini söyler:

```text
b\r\n
ilk satır\n\r\n
e\r\n
ikinci satır\n\r\n
4\r\n
son\n\r\n
0\r\n
\r\n
```

```python
import tezgah

y = tezgah.yanit("GET /akis HTTP/1.1\r\nHost: pafta.test\r\n\r\n")
print(y.baslik("Transfer-Encoding"), y.baslik("Content-Length"))
print(y.govde_bayt)
```

Uzunluk satırında `;` sonrası parça uzantıları olabilir (`5;ad=deger`); okuyan taraf onları atlar. Verinin içinde CRLF geçebilir: parçayı satır satır değil, **uzunluğuna göre** okumak gerekir.

> [!GÜVENLİK]
> Bir mesaj hem `Content-Length` hem `Transfer-Encoding: chunked` taşırsa kurallar `Transfer-Encoding`'in geçerli olduğunu söyler. Ama araya giren bir vekil ile arkadaki sunucu bunu farklı yorumlarsa mesajların sınırı kayar: biri için gövdenin parçası olan baytlar, öteki için yeni bir istek olur. Savunma, katı ayrıştırmadır: belirsiz ya da çelişkili çerçevelemesi olan mesajları (iki `Content-Length`, ikisi birden, bozuk parça boyu) reddetmek ve vekille arka sunucunun aynı kurallarla ayrıştırmasını sağlamak.
:::

::: anlat HTTP/2, HTTP/3 ve CORS
**HTTP/2** anlamı değiştirmedi: yöntemler, durum kodları ve başlıklar aynıdır. Değişen **tel üzerindeki biçimdir**: metin yerine ikili çerçeveler, tek bağlantıda aynı anda birçok akış (bir yanıt ötekini bekletmez), sıkıştırılmış başlıklar (HPACK). İstek satırının yerini sözde başlıklar alır: `:method`, `:path`, `:scheme`, `:authority` (`Host`'un karşılığı); yanıtta `:status` vardır ama neden ifadesi yoktur, başlık adları hep küçük harftir. **HTTP/3** aynı anlamı UDP üzerinde çalışan QUIC ile taşır. Tarayıcının geliştirici araçları ve web inceleme araçları bu çerçeveleri çoğu zaman bildiğin HTTP/1.1 biçiminde gösterir; bu derslerde öğrendiğin okuma aynen geçerlidir.

**CORS** (kökenler arası kaynak paylaşımı) bir **tarayıcı** kuralıdır. Bir sayfanın betiği başka bir kökene (şema, host ve port üçlüsü) istek attığında tarayıcı isteğe `Origin` başlığını ekler; sunucu yanıtta `Access-Control-Allow-Origin` ile izin vermezse tarayıcı yanıtı betiğe **göstermez**. Bazı istekler için tarayıcı önce bir `OPTIONS` sorusu (preflight) gönderir.

> [!TUZAK]
> CORS sunucuyu korumaz, kullanıcının tarayıcısındaki **okumayı** sınırlar. Aynı isteği bir betik ya da komut satırından gönderen biri CORS'a takılmaz. Sunucudaki yetki denetimi (HT09, HT12) yine şarttır. `Access-Control-Allow-Origin: *`, kimlik bilgisi taşıyan (çerezli) isteklerle birlikte kullanılamaz.
:::

::: tahmin
Parça boylarını elle okumak. İki satır:

```python
import tezgah

govde = tezgah.yanit("GET /akis HTTP/1.1\r\nHost: pafta.test\r\n\r\n").govde_bayt
satirlar = govde.split(b"\r\n")
print(satirlar[0], int(satirlar[0], 16), satirlar[1].decode().strip())
print([int(s, 16) for s in satirlar[0::2] if s])
```

???

`b'b' 11 ilk satır` ve `[11, 14, 4, 0]`. İlk parçanın boyu onaltılık `b`, yani 11 bayttır: "ilk satır" ve satır sonu 10 karakterdir ama `ı` iki bayt olduğu için 11 bayt eder. Çift sıradaki satırlar parça boylarıdır: 11, 14 (`e`), 4 ve sonu gösteren 0. Bu örnekte parçaların içinde CRLF olmadığı için satırlara bölmek işe yaradı; genel bir çözüm parçayı uzunluğuna göre okur.
:::

::: gorev Chunked gövdeyi aç
`chunked_coz(govde)` fonksiyonu `Transfer-Encoding: chunked` ile gelmiş bir gövdeyi (bayt) asıl içeriğe (bayt) çevirsin. Boy satırı onaltılıktır (büyük ya da küçük harf) ve `;` sonrası uzantı taşıyabilir; boyu `0` olan parçada durulur. Parçanın verisi CRLF içerebilir: veriyi **boyuna göre** oku.

```starter
def chunked_coz(govde):
    return b"".join(govde.split(b"\r\n")[1::2])
```

```test
import tezgah
need("chunked_coz")
y = tezgah.yanit("GET /akis HTTP/1.1\r\nHost: pafta.test\r\n\r\n")
eq(chunked_coz(y.govde_bayt), "ilk satır\nikinci satır\nson\n".encode("utf-8"), "tezgahın akışı")
eq(chunked_coz(b"5;ad=deger\r\nmerha\r\nA\r\nba dunya!!\r\n0\r\n\r\n"), b"merhaba dunya!!", "uzantı ve büyük harfli A (10)")
eq(chunked_coz(b"4\r\na\r\nb\r\n1\r\n!\r\n0\r\n\r\n"), b"a\r\nb!", "verinin içinde CRLF: boya göre oku")
eq(chunked_coz(b"0\r\n\r\n"), b"", "boş gövde")
eq(chunked_coz(b"10\r\n" + b"x" * 16 + b"\r\n0\r\n\r\nSONRAKI"), b"x" * 16, "10 onaltılıktır (16); 0'dan sonrası gövde değil")
```

```solution
def chunked_coz(govde):
    sonuc = b""
    i = 0
    while True:
        son = govde.index(b"\r\n", i)
        boy = int(govde[i:son].split(b";")[0], 16)
        if boy == 0:
            return sonuc
        bas = son + 2
        sonuc += govde[bas:bas + boy]
        i = bas + boy + 2
```

```hint
Bir konum değişkeniyle ilerle: boy satırının sonunu `govde.index(b"\r\n", i)` ile bul, `int(..., 16)` ile oku, sonra tam `boy` bayt al ve veriden sonraki CRLF'yi atla.
```
:::

::: gorev Art arda yanıtlar
`yanitlari_ayir(ham)` fonksiyonu tek bir bağlantıdan art arda gelmiş yanıtları (bayt) `(durum_kodu, govde_bayt)` çiftlerinin listesine çevirsin. Her yanıtın gövdesi tam `Content-Length` bayttır; `Content-Length`'i olmayan yanıtın (204 gibi) gövdesi boştur. Başlık adları büyük-küçük harfe duyarsız.

```starter
def yanitlari_ayir(ham):
    parcalar = ham.split(b"HTTP/1.1 ")[1:]
    return [(int(p[:3]), b"") for p in parcalar]
```

```test
import tezgah
need("yanitlari_ayir")
ham = tezgah.gonder_bayt("GET /durum HTTP/1.1\r\nHost: pafta.test\r\n\r\n"
                         "DELETE /biletler/1 HTTP/1.1\r\nHost: pafta.test\r\n\r\n"
                         "GET /sunucular/web01 HTTP/1.1\r\nHost: pafta.test\r\n\r\n")
r = yanitlari_ayir(ham)
eq([d for d, _ in r], [200, 204, 200], "üç yanıt, sırayla")
eq(r[0][1], b'{"durum": "ok", "surum": "2.4.1"}', "ilk gövde")
eq(r[1][1], b"", "204'ün gövdesi yok")
eq(r[2][1], '{"ad": "web01", "rol": "web", "sehir": "İstanbul", "cpu": 72}'.encode("utf-8"), "Türkçe harfli gövde baytla kesilir")
eq(yanitlari_ayir(b"HTTP/1.1 200 OK\r\ncontent-length: 4\r\n\r\nHTTPHTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n"),
   [(200, b"HTTP"), (404, b"")], "gövdede 'HTTP' geçse de; küçük harfli başlık; sıfır uzunluk")
eq(yanitlari_ayir(b""), [], "boş")
```

```solution
def yanitlari_ayir(ham):
    sonuc = []
    while ham:
        bas, _, kalan = ham.partition(b"\r\n\r\n")
        satirlar = bas.decode("iso-8859-1").split("\r\n")
        durum = int(satirlar[0].split(" ")[1])
        uzunluk = 0
        for satir in satirlar[1:]:
            ad, _, deger = satir.partition(":")
            if ad.strip().lower() == "content-length":
                uzunluk = int(deger)
        sonuc.append((durum, kalan[:uzunluk]))
        ham = kalan[uzunluk:]
    return sonuc
```

```hint
Döngüde: başlık bölümünü `partition(b"\r\n\r\n")` ile ayır, `Content-Length`'i bul (yoksa 0), gövdeyi o kadar bayt al, kalanla devam et. Gövdeyi metne çevirmeden **baytla** kes.
```
:::

::: gorev Bağlantı açık kalır mı?
`kalici_mi(surum, connection)` fonksiyonu bir mesajdan sonra bağlantının açık kalıp kalmayacağını söylesin. `connection`, `Connection` başlığının değeridir (yoksa `None`); virgülle ayrılmış, büyük-küçük harfe duyarsız **jetonlardan** oluşur.

- `HTTP/1.1`: `close` jetonu yoksa `True`
- `HTTP/1.0`: yalnızca `keep-alive` jetonu varsa `True`

```starter
def kalici_mi(surum, connection):
    return surum == "HTTP/1.1"
```

```test
need("kalici_mi")
for surum, connection, beklenen in [("HTTP/1.1", None, True), ("HTTP/1.1", "close", False),
                                    ("HTTP/1.1", "Keep-Alive, CLOSE", False), ("HTTP/1.1", "closed", True),
                                    ("HTTP/1.1", "keep-alive", True), ("HTTP/1.0", None, False),
                                    ("HTTP/1.0", "keep-alive", True), ("HTTP/1.0", "Keep-Alive", True),
                                    ("HTTP/1.0", "upgrade,  keep-alive ", True), ("HTTP/1.0", "keep-alive-x", False),
                                    ("HTTP/1.0", "close", False)]:
    eq(kalici_mi(surum, connection), beklenen, f"{surum} · Connection: {connection}")
```

```solution
def kalici_mi(surum, connection):
    jetonlar = [j.strip().lower() for j in (connection or "").split(",")]
    if surum == "HTTP/1.1":
        return "close" not in jetonlar
    return "keep-alive" in jetonlar
```

```hint
Değeri virgüllerden böl, her jetonu `strip().lower()` yap ve **jeton listesinde** ara: `"close" in metin` diye aramak `closed`'u da yakalardı.
```
:::
