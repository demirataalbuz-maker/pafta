---
id: p74
title: requests Session ve Beautiful Soup
summary: Oturumlu HTTP istemcisi: çerezi taşıyan Session, params ve json, timeout, durum kodunu okumak ve sayfalama; HTML'yi regex yerine ağaçtan okumak, eksik öğe None döner, kapanmamış etiket veriyi sessizce birleştirir.
kazanim: PCPP1 4.4
---

::: anlat Session: çerezi ve bağlantıyı taşıyan istemci
`urllib` ile bir isteği elle kurabilirsin (P56), ama gerçek işlerde tek bir istek nadiren yeter: önce giriş yaparsın, sonra o girişin çerezini taşıyan birkaç istek atarsın. `requests.Session` tam bunun içindir.

```python
import api, requests

oturum = requests.Session()
giris = oturum.post(api.SUNUCU + "/giris",
                    json={"kullanici": api.KULLANICI, "parola": api.PAROLA},
                    timeout=5)
print(giris.status_code, giris.json())        #! 200 ve {'durum': 'açık', ...}
print(oturum.cookies.get("oturum"))           #! Session çerezi sakladı

liste = oturum.get(api.SUNUCU + "/api/biletler", params={"sayfa": 1}, timeout=5)
print(liste.status_code, len(liste.json()["kayitlar"]))   #! çerez kendiliğinden gitti
```

Tek tek `requests.get(...)` çağırsaydın her istek çerezsiz giderdi ve ikincisi `401` alırdı.

| Parça | Ne yapar |
|---|---|
| `Session()` | Çerezleri, varsayılan başlıkları ve TCP bağlantısını istekler arasında taşır |
| `params={"sayfa": 1}` | Sorgu dizesini kodlayarak ekler; elle `?sayfa=1` yazmaktan güvenlidir |
| `json={...}` | Gövdeyi JSON'a çevirir **ve** `Content-Type: application/json` başlığını koyar |
| `data={...}` | Gövdeyi form kodlamasıyla gönderir (`application/x-www-form-urlencoded`) |
| `timeout=5` | Yanıt gelmezse bekleyip kalmaz |
| `.status_code`, `.json()`, `.text`, `.headers` | Yanıtın okunacak yerleri |

> [!TUZAK] `timeout` toplam süre değildir
> `timeout=5` "istek en çok 5 saniye sürer" demek **değildir**. Bağlanma ve iki veri parçası arasında geçen süre için ayrı ayrı 5 saniyedir; yavaş yavaş akan bir yanıt dakikalarca sürebilir. İkisini ayırmak için `timeout=(3, 10)` (bağlanma, okuma) yazılır. `timeout` hiç vermezsen istek **sonsuza kadar** bekleyebilir; betiklerinde her zaman ver.

> [!TUZAK] 404 bir istisna değildir
> `requests` 4xx ve 5xx yanıtlarında istisna fırlatmaz; `y.status_code` 404 olur ve kod akmaya devam eder. Durumu kendin denetle ya da `y.raise_for_status()` çağır — o `HTTPError` fırlatır. İstisna fırlatan şeyler ağ düzeyindedir: bağlanamama, DNS, timeout.
```setup
import os, runpy, sys
_s = next(os.path.dirname(m.__file__) for m in list(sys.modules.values())
          if os.path.basename(getattr(m, "__file__", None) or "") in ("py_harness.py", "wsl_job.py"))
runpy.run_path(os.path.join(_s, "api_tezgah.py"), run_name="__tezgah__")
```
:::

::: anlat Beautiful Soup: HTML'yi ağaç olarak okumak
Bir HTML sayfasından veri çıkarmanın regex'li yolu kırılgandır: öznitelik sırası değişir, boşluk eklenir, etiket kapanmaz ve desen sessizce yanlış şeyi yakalar. Beautiful Soup belgeyi bir ağaca çevirir:

```python
import api, requests
from bs4 import BeautifulSoup

html = requests.get(api.SUNUCU + "/sayfa/biletler", timeout=5).text
corba = BeautifulSoup(html, "html.parser")

print(corba.find(id="baslik").get_text(strip=True))          #! tek öğe, yoksa None
print(len(corba.select("tr.bilet")))                         #! CSS seçici, liste döndürür
print(corba.find("input", {"name": "belirtec"})["value"])    #! öznitelik okumak
print(corba.find(id="olmayan"))                              #! eşleşme yoksa None
```

| Arama | Ne döndürür |
|---|---|
| `find(...)` | İlk eşleşen öğe, yoksa **`None`** |
| `find_all(...)` | Liste, eşleşme yoksa **boş liste** |
| `select("tr.bilet")` | CSS seçicisiyle liste |
| `select_one("...")` | CSS seçicisiyle tek öğe ya da `None` |
| `oge["href"]` | Öznitelik; yoksa `KeyError` (güvenlisi `oge.get("href")`) |
| `oge.get_text(strip=True)` | Öğenin **ve altındaki her şeyin** metni |

> [!TUZAK] `find` `None` döndürür, `.get_text()` patlar
> `corba.find(id="olmayan").get_text()` satırı `AttributeError: 'NoneType' object has no attribute 'get_text'` verir. Bir sayfadan veri çekerken öğenin varlığını her zaman denetle: `oge = corba.find(...)`, sonra `if oge is not None`.

**Bozuk HTML sessizce veri birleştirir.** Ayrıştırıcı kapanmamış bir etiketi kendi kuralına göre kapatır ve bu çoğu zaman beklediğin yer değildir:

```python
import api, requests
from bs4 import BeautifulSoup

corba = BeautifulSoup(requests.get(api.SUNUCU + "/sayfa/bozuk", timeout=5).text, "html.parser")
for li in corba.select("li.kayit"):
    deger = li.find("span", class_="deger")
    print(repr(li.contents[0].strip()), "->", repr(deger.get_text(strip=True) if deger else None))
```

Sayfada üç `li` var ama ilkinin `<span class="deger">` etiketi kapanmamış: ayrıştırıcı onu sonraki satırların sonuna kadar uzatır, bu yüzden ilk değer `'72db0191cache01'` çıkar — üç satırın metni birbirine karışmıştır. İkinci satırın `span`'i düzgün kapandığı için `'91'` doğrudur, üçüncüde `span` hiç yoktur ve `None` gelir. Hiçbiri hata vermez; yanlış veri sessizce akar. Bu yüzden bir ayrıştırmanın sonucunu her zaman **bilinen bir örnekle** doğrula.
```setup
import os, runpy, sys
_s = next(os.path.dirname(m.__file__) for m in list(sys.modules.values())
          if os.path.basename(getattr(m, "__file__", None) or "") in ("py_harness.py", "wsl_job.py"))
runpy.run_path(os.path.join(_s, "api_tezgah.py"), run_name="__tezgah__")
```
:::

::: anlat Tezgahın sınırı ve sıradaki adım
Bu dersteki `api` modülü, hazırlık bloğunun başlattığı yerel bir uygulamadır (`sandbox/api_tezgah.py`): `127.0.0.1`'de boş bir portta çalışır, verisi her çalıştırmada sıfırlanır, `Date` başlığı ve oturum çerezi sabittir. İnternete çıkmaz. Böylece tahminler ve testler her makinede aynı sonucu verir.

Gerçek bir hedefte eklenen üç şey var: **TLS** (sertifika doğrulaması; `verify=False` yazmak güvenliği kapatır, hata ayıklarken bile alışkanlık yapma), **oran sınırı** (`429` ve `Retry-After`), ve **robots.txt ile kullanım koşulları**. Bir siteyi izinsiz taramak teknik değil hukuki bir sorundur.

> [!NOT] Eşzamanlı istemci dersin sonunda
> Bugünkü `requests` kodu sırayla çalışır: yüz istek, yüz gidiş-dönüş demektir. Çok sayıda isteği aynı anda yürüten `aiohttp` bölümü bu dersin **son adımlarındadır** ve gerçek Linux'ta (Kali, WSL) çalışır; aynı tezgah orada da başlatılır. P60 ve P61'deki `asyncio` bilgisi o bölümün temelidir.
:::

::: tahmin
Ne yazar?

```python
import api, requests

o = requests.Session()
y1 = o.get(api.SUNUCU + "/api/biletler", timeout=5)
print(y1.status_code, y1.json()["hata"])

o.post(api.SUNUCU + "/giris", json={"kullanici": "analist", "parola": "pafta123"}, timeout=5)
y2 = o.get(api.SUNUCU + "/api/biletler", params={"sayfa": 3}, timeout=5)
d = y2.json()
print(y2.status_code, d["sayfa"], len(d["kayitlar"]), d["sonraki"])
print(o.cookies.get("oturum"))
```

???

`401 oturum`, `200 3 1 None` ve `pafta-oturum-2026`.

İlk istek çerezsizdir: sunucu `401` ve `{"hata": "oturum"}` döner — ama `requests` istisna fırlatmaz, kod akmaya devam eder. Girişten sonra aynı `Session` çerezi taşır, bu yüzden ikinci istek `200` alır. Yedi kaydın sayfa boyu üç olduğu için üçüncü sayfada **bir** kayıt kalır ve son sayfa olduğundan `sonraki` `None`'dır. Çerez `Session` nesnesinde durur; `requests.get(...)` ile atılan bağımsız bir istek onu görmezdi.
```setup
import os, runpy, sys
_s = next(os.path.dirname(m.__file__) for m in list(sys.modules.values())
          if os.path.basename(getattr(m, "__file__", None) or "") in ("py_harness.py", "wsl_job.py"))
runpy.run_path(os.path.join(_s, "api_tezgah.py"), run_name="__tezgah__")
```
:::

::: gorev Sayfaları sonuna kadar gez
Girdi kutusunun ilk satırında bir başlangıç sayfa numarası var. Giriş yap, o sayfadan başlayarak **son sayfaya kadar** bütün kayıtları topla ve her satıra bir bilet numarası yazdır.

Sunucu her sayfada `sonraki` alanını verir: son sayfada `None` olur. Sayfa numarası geçersizse (sunucu `400` döner) ya da satır sayıya çevrilemiyorsa tek satır `HATA` yazdır.

```stdin
1
```

```setup
import os, runpy, sys
_s = next(os.path.dirname(m.__file__) for m in list(sys.modules.values())
          if os.path.basename(getattr(m, "__file__", None) or "") in ("py_harness.py", "wsl_job.py"))
runpy.run_path(os.path.join(_s, "api_tezgah.py"), run_name="__tezgah__")
```

```starter
import api, requests

baslangic = input().strip()
oturum = requests.Session()
oturum.post(api.SUNUCU + "/giris",
            json={"kullanici": api.KULLANICI, "parola": api.PAROLA}, timeout=5)

# sayfa sayfa ilerle, sonraki None olunca dur
```

```test
eq(out, "101\n102\n103\n104\n105\n106\n107\n", "yedi kaydın hepsi, sırayla")
eq(run(stdin="3\n"), "107\n", "son sayfada tek kayıt var ve sonraki None")
eq(run(stdin="2\n"), "104\n105\n106\n107\n", "ortadan başlayınca kalan iki sayfa gelir")
eq(run(stdin="4\n"), "", "aralık dışı sayfa boş döner, hata değildir")
eq(run(stdin="0\n"), "HATA\n", "sunucu 0 için 400 verir")
eq(run(stdin="abc\n"), "HATA\n", "sayıya çevrilemeyen girdi HATA")
ok("sonraki" in src, "son sayfayı sunucunun sonraki alanından anla, sayıyı koda gömme")
```

```solution
import api, requests

baslangic = input().strip()
try:
    sayfa = int(baslangic)
except ValueError:
    print("HATA")
    raise SystemExit

oturum = requests.Session()
oturum.post(api.SUNUCU + "/giris",
            json={"kullanici": api.KULLANICI, "parola": api.PAROLA}, timeout=5)

while sayfa is not None:
    y = oturum.get(api.SUNUCU + "/api/biletler", params={"sayfa": sayfa}, timeout=5)
    if y.status_code != 200:
        print("HATA")
        break
    veri = y.json()
    for kayit in veri["kayitlar"]:
        print(kayit["id"])
    sayfa = veri["sonraki"]
```

```hint
Döngünün koşulu sayfa sayısı değil, sunucunun verdiği `sonraki` alanıdır: `while sayfa is not None`. Döngünün sonunda `sayfa = veri["sonraki"]` yaz.
```

```hint
`int()` `ValueError` fırlatır; `400` ise istisna değil, `y.status_code` değeridir. İkisini de yakalaman gerekir.
```
:::

::: gorev Bilet oluştur ve hatayı oku
Girdi kutusunun ilk satırı başlık, ikinci satırı önceliktir. Giriş yaptıktan sonra `POST /api/bilet` ile kaydı oluştur.

- Sunucu `201` döndürürse `OLUSTU|<id>|<Location başlığı>` yazdır.
- Başka bir durum kodu gelirse `<kod>|<yanıttaki hata alanı>` yazdır (ör. `400|alan`).
- Girdi iki satır değilse tek satır `HATA` yazdır.

Sunucu üç türlü reddeder: boş alan `400 alan`, listede olmayan öncelik `400 oncelik`, aynı başlıkla ikinci kayıt `409 yinelenen`. Kodunu "400 değilse başarılıdır" diye yazma; **yalnız `201`** oluşturma demektir.

```stdin
yeni kayit
yüksek
```

```setup
import os, runpy, sys
_s = next(os.path.dirname(m.__file__) for m in list(sys.modules.values())
          if os.path.basename(getattr(m, "__file__", None) or "") in ("py_harness.py", "wsl_job.py"))
runpy.run_path(os.path.join(_s, "api_tezgah.py"), run_name="__tezgah__")
```

```starter
import api, requests, sys

satirlar = sys.stdin.read().splitlines()
oturum = requests.Session()
oturum.post(api.SUNUCU + "/giris",
            json={"kullanici": api.KULLANICI, "parola": api.PAROLA}, timeout=5)

# POST /api/bilet · 201 ise OLUSTU, değilse kod ve hata alanı
```

```test
eq(out, "OLUSTU|108|/api/bilet/108\n", "yeni kayıt 108 numarasını alır ve Location başlığı gelir")
eq(run(stdin="\nyüksek\n"), "400|alan\n", "boş başlık reddedilir")
eq(run(stdin="deneme\n\n"), "400|alan\n", "boş öncelik reddedilir")
dusuk = run(stdin="deneme\ndüşük\n").strip()          # aynı sunucuya ikinci kayıt: numara artar
parcalar = dusuk.split("|")
ok(len(parcalar) == 3 and parcalar[0] == "OLUSTU" and parcalar[1].isdigit(),
   "sınırdaki geçerli öncelik düşük de kabul edilir")
ok(parcalar[2] == "/api/bilet/" + parcalar[1], "Location başlığı oluşan kaydın numarasını taşır")
ok(int(parcalar[1]) > 108, "aynı sunucuda ikinci kayıt yeni bir numara alır")
eq(run(stdin="yeni kayit\norta\n"), "409|yinelenen\n", "aynı başlıkla ikinci kayıt 409 verir, 400 değil")
eq(run(stdin="deneme\nYüksek\n"), "400|oncelik\n", "öncelik büyük-küçük harfe duyarlıdır")
eq(run(stdin="deneme\nacil\n"), "400|oncelik\n", "listede olmayan öncelik reddedilir")
eq(run(stdin="yalniz baslik\n"), "HATA\n", "tek satırlık girdi HATA")
```

```solution
import api, requests, sys

satirlar = sys.stdin.read().splitlines()
if len(satirlar) < 2:
    print("HATA")
    raise SystemExit

oturum = requests.Session()
oturum.post(api.SUNUCU + "/giris",
            json={"kullanici": api.KULLANICI, "parola": api.PAROLA}, timeout=5)

y = oturum.post(api.SUNUCU + "/api/bilet",
                json={"baslik": satirlar[0], "oncelik": satirlar[1]}, timeout=5)
if y.status_code == 201:
    print("OLUSTU|{}|{}".format(y.json()["id"], y.headers["Location"]))
else:
    print("{}|{}".format(y.status_code, y.json()["hata"]))
```

```hint
Başarısız yanıtın gövdesi de JSON'dur: `y.json()["hata"]`. Durum kodu 201 değilse istisna beklemeden kodu kendin oku.
```

```hint
`Location` yanıt başlığındadır: `y.headers["Location"]`.
```
:::

::: gorev HTML'den tabloyu çıkar
Girdi kutusunun ilk satırı `tablo`, `bozuk` ya da `yok` olur; başka bir değer için tek satır `HATA` yazdır.

- `tablo`: `/sayfa/biletler` sayfasındaki her `tr.bilet` satırı için `<id>|<başlık>|<öncelik>` yazdır. Numarayı satırın `data-id` özniteliğinden, başlığı bağlantının metninden, önceliği `td.oncelik` hücresinden al.
- `bozuk`: `/sayfa/bozuk` sayfasındaki her `li.kayit` için `<ad>|<değer>` yazdır. Ad, `li`'nin ilk metin parçasıdır; değer `span.deger` metnidir, o `span` yoksa `-` yaz.
- `yok`: `/sayfa/biletler` sayfasında `tr.yoktur` seçicisini dene; hiç eşleşme yoksa tek satır `BOS` yazdır.

```stdin
tablo
```

```setup
import os, runpy, sys
_s = next(os.path.dirname(m.__file__) for m in list(sys.modules.values())
          if os.path.basename(getattr(m, "__file__", None) or "") in ("py_harness.py", "wsl_job.py"))
runpy.run_path(os.path.join(_s, "api_tezgah.py"), run_name="__tezgah__")
```

```starter
import api, requests
from bs4 import BeautifulSoup

ne = input().strip()
# tablo / bozuk / yok
```

```test
eq(out, "101|web01 disk doldu|yüksek\n"
        "102|db01 yedek gecikti|orta\n"
        "104|web02 sertifika süresi|yüksek\n"
        "106|web03 5xx artışı|yüksek\n"
        "107|yedek01 disk testi|düşük\n",
   "sayfada yalnız açık biletler var: 103 ve 105 listelenmez")

eq(run(stdin="bozuk\n"), "web01|72db0191cache01\ndb01|91\ncache01|-\n",
   "kapanmamış span sonraki satırların metnini de yutar; üçüncüde span hiç yok")

eq(run(stdin="yok\n"), "BOS\n", "eşleşmeyen seçici boş liste verir, hata değil")
eq(run(stdin="TABLO\n"), "HATA\n", "tanınmayan değer HATA")
eq(run(stdin="\n"), "HATA\n", "boş girdi HATA")
ok("BeautifulSoup" in src, "HTML'yi regex ile değil ağaçtan oku")
```

```solution
import api, requests
from bs4 import BeautifulSoup

ne = input().strip()
if ne not in ("tablo", "bozuk", "yok"):
    print("HATA")
    raise SystemExit

if ne == "bozuk":
    corba = BeautifulSoup(requests.get(api.SUNUCU + "/sayfa/bozuk", timeout=5).text, "html.parser")
    for li in corba.select("li.kayit"):
        ad = li.contents[0].strip()
        deger = li.find("span", class_="deger")
        print("{}|{}".format(ad, deger.get_text(strip=True) if deger is not None else "-"))
    raise SystemExit

corba = BeautifulSoup(requests.get(api.SUNUCU + "/sayfa/biletler", timeout=5).text, "html.parser")
if ne == "yok":
    satirlar = corba.select("tr.yoktur")
    print("BOS" if not satirlar else len(satirlar))
    raise SystemExit

for tr in corba.select("tr.bilet"):
    baslik = tr.find("a").get_text(strip=True)
    oncelik = tr.find("td", class_="oncelik").get_text(strip=True)
    print("{}|{}|{}".format(tr["data-id"], baslik, oncelik))
```

```hint
`li.contents[0]` metin düğümüdür; `.strip()` ile temizle. `span` yoksa `find` `None` döner, `.get_text()` çağırmadan önce denetle.
```

```hint
`select` eşleşme bulamazsa **boş liste** döndürür, `None` değil: `if not satirlar` ile sınayabilirsin.
```
:::

::: anlat aiohttp: aynı anda birçok istek
Buradan sonraki adımlar **gerçek Linux'ta** (Kali, WSL) çalışır; aynı tezgah Linux işinin içinde başlatılır.

`requests` her isteği bitirmeden sıradakine geçmez. Ağın beklediği sürede işlemci boş durur. `aiohttp` aynı `asyncio` olay döngüsünde birçok isteği **birlikte** bekler (P60):

```python
import asyncio, aiohttp, api

async def dene(sinir):
    kapi = asyncio.Semaphore(sinir)                      #! aynı anda en çok sinir istek
    async with aiohttp.ClientSession() as oturum:
        async def bir(no):
            async with kapi:
                async with oturum.get(api.SUNUCU + "/yavas", params={"ms": 200, "no": no}) as y:
                    return (await y.json())["no"]
        sira = await asyncio.gather(*(bir(i) for i in range(1, 7)))
        async with oturum.get(api.SUNUCU + "/eszamanli") as y:
            return sira, (await y.json())["en_cok"]     #! sunucunun gördüğü en çok eşzamanlı istek

print(asyncio.run(dene(1)))                              #! tek tek: yaklaşık 1,2 sn
print(asyncio.run(dene(6)))                              #! hepsi birden: yaklaşık 0,2 sn
```

`/yavas` her isteği 200 ms bekletir ve sunucu aynı anda kaç isteğin beklediğini sayar. Sınır 1 iken altı istek sırayla gider; sınır 6 iken hepsi aynı anda. Sonuçların **sırası ikisinde de 1'den 6'ya**: `gather` cevapları bitiş sırasıyla değil, verdiğin sırayla döndürür.

| `requests` | `aiohttp` |
|---|---|
| `requests.Session()` | `async with aiohttp.ClientSession() as o:` |
| `y = o.get(url)` | `async with o.get(url) as y:` |
| `y.json()`, `y.text` | `await y.json()`, `await y.text()` (gövde ağdan okunurken beklenir) |
| `y.status_code` | `y.status` |
| `timeout=5` (bağlanma ve okuma ayrı ayrı) | `aiohttp.ClientTimeout(total=5)`: **gerçekten toplam** süre |
| `raise_for_status()` → `HTTPError` | `raise_for_status()` → `aiohttp.ClientResponseError` (`.status`) |

> [!TUZAK] Sınırsız eşzamanlılık bir saldırıdır
> Bin isteği tek seferde `gather` ile göndermek kendi bilgisayarını ve karşı sunucuyu boğar; izinsiz bir hedefte bu bir hizmet engelleme saldırısıdır. Eşzamanlılığı her zaman sınırla: `asyncio.Semaphore(n)` ya da `aiohttp.TCPConnector(limit=n)`. Oran sınırı (`429`) gelirse yavaşla.

> [!TUZAK] Varsayılan çerez kavanozu IP adresinden çerez almaz
> `aiohttp.ClientSession()`'ın çerez kavanozu, adı alan adı değil **IP adresi** olan sunuculardan gelen çerezleri sessizce reddeder. `127.0.0.1`'e giriş yaparsın, yanıt 200 gelir, ama sonraki istek oturumsuz gider. Yerel laboratuvarda kavanozu `aiohttp.CookieJar(unsafe=True)` ile kur; adı "güvensiz" ama yalnızca bu kuralı gevşetir.

```setup
import os, runpy, sys
_s = next(os.path.dirname(m.__file__) for m in list(sys.modules.values())
          if os.path.basename(getattr(m, "__file__", None) or "") in ("py_harness.py", "wsl_job.py"))
runpy.run_path(os.path.join(_s, "api_tezgah.py"), run_name="__tezgah__")
```

```meta
backend: wsl
timeout: 60
```
:::

::: tahmin Çerez kavanozu
Ne yazar? (Linux'ta çalışır.)

```python
import asyncio, aiohttp, api

async def dene(guvensiz):
    kavanoz = aiohttp.CookieJar(unsafe=guvensiz)
    async with aiohttp.ClientSession(cookie_jar=kavanoz) as o:
        async with o.post(api.SUNUCU + "/giris", json={"kullanici": "analist", "parola": "pafta123"}) as y:
            giris = y.status
        async with o.get(api.SUNUCU + "/api/biletler") as y:
            print(giris, y.status, len(kavanoz))

asyncio.run(dene(False))
asyncio.run(dene(True))
```

???

`200 401 0` ve `200 200 1`.

Giriş iki denemede de başarılıdır: sunucu 200 ve `Set-Cookie` döner. Ama varsayılan kavanoz, adresi `127.0.0.1` gibi bir IP olan sunucunun çerezini **saklamaz**: kavanozda 0 çerez kalır ve liste isteği oturumsuz gider, `401` alır. Hiçbir hata, hiçbir uyarı yoktur. `unsafe=True` ile çerez saklanır, kavanozda 1 çerez olur ve ikinci istek 200 alır. `requests.Session` bu ayrımı yapmaz; bu yüzden P74'ün ilk görevleri aynı sunucuda sorunsuz çalışıyordu.

```setup
import os, runpy, sys
_s = next(os.path.dirname(m.__file__) for m in list(sys.modules.values())
          if os.path.basename(getattr(m, "__file__", None) or "") in ("py_harness.py", "wsl_job.py"))
runpy.run_path(os.path.join(_s, "api_tezgah.py"), run_name="__tezgah__")
```

```meta
backend: wsl
timeout: 60
```
:::

::: gorev Sınırlı eşzamanlı istek
Girdi kutusunun ilk satırı eşzamanlılık sınırıdır. `aiohttp` ile `/yavas` ucuna **altı** istek gönder: `i` 1'den 6'ya, her biri `no=i` ve `ms=300-40*i` parametreleriyle (ilk istek en uzun bekler, sonuncusu en kısa). Aynı anda en çok "sınır" kadar istek uçuşsun.

İki satır yazdır: dönen `no` değerlerini **istek sırasıyla**, aralarında birer boşlukla; sonra `/eszamanli` ucunun verdiği değeri `en_cok <değer>` biçiminde. Sınır 1'den küçükse ya da tam sayı değilse tek satır `HATA` yazdır.

```stdin
3
```

```setup
import os, runpy, sys
_s = next(os.path.dirname(m.__file__) for m in list(sys.modules.values())
          if os.path.basename(getattr(m, "__file__", None) or "") in ("py_harness.py", "wsl_job.py"))
runpy.run_path(os.path.join(_s, "api_tezgah.py"), run_name="__tezgah__")
```

```meta
backend: wsl
timeout: 90
```

```starter
import asyncio, aiohttp, api

satir = input().strip()

async def calis(sinir):
    async with aiohttp.ClientSession() as oturum:
        for i in range(1, 7):
            async with oturum.get(api.SUNUCU + "/yavas", params={"ms": 300 - 40 * i, "no": i}) as y:
                print((await y.json())["no"])

asyncio.run(calis(int(satir)))
```

```test
eq(out, "1 2 3 4 5 6\nen_cok 3\n", "sınır 3: aynı anda en çok 3 istek, sonuçlar istek sırasıyla")
eq(run(stdin="1\n"), "1 2 3 4 5 6\nen_cok 1\n", "sınır 1: istekler tek tek")
eq(run(stdin="6\n"), "1 2 3 4 5 6\nen_cok 6\n", "sınır istek sayısına eşit: hepsi aynı anda")
eq(run(stdin="10\n"), "1 2 3 4 5 6\nen_cok 6\n", "sınır istek sayısının üstünde: en çok 6 olabilir")
eq(run(stdin="0\n"), "HATA\n", "sınır 0 olamaz")
eq(run(stdin="-2\n"), "HATA\n", "eksi sınır HATA")
eq(run(stdin="üç\n"), "HATA\n", "sayı olmayan girdi HATA")
eq(run(stdin="\n"), "HATA\n", "boş girdi HATA")
ok("aiohttp" in src, "istekleri aiohttp ile gönder")
```

```solution
import asyncio, aiohttp, api

satir = input().strip()

async def calis(sinir):
    kapi = asyncio.Semaphore(sinir)
    async with aiohttp.ClientSession() as oturum:
        async def bir(no):
            async with kapi:
                async with oturum.get(api.SUNUCU + "/yavas", params={"ms": 300 - 40 * no, "no": no}) as y:
                    return (await y.json())["no"]
        sira = await asyncio.gather(*(bir(i) for i in range(1, 7)))
        async with oturum.get(api.SUNUCU + "/eszamanli") as y:
            en_cok = (await y.json())["en_cok"]
    print(" ".join(str(n) for n in sira))
    print("en_cok", en_cok)

if satir.isdigit() and int(satir) >= 1:
    asyncio.run(calis(int(satir)))
else:
    print("HATA")
```

```hint
`asyncio.Semaphore(sinir)` bir kapıdır: `async with kapi:` bloğuna aynı anda en çok `sinir` görev girer. İsteği bu bloğun içinde gönder.
```

```hint
Son istek ilk biter. Sonuçları bitiş sırasıyla toplarsan sıra `6 5 4 3 2 1` olur; `asyncio.gather` ise verdiğin sırayı korur.
```
:::

::: gorev Oturumla eşzamanlı ayrıntı
Girdi kutusunun ilk satırında boşlukla ayrılmış bilet numaraları var. `aiohttp` ile giriş yap, sonra bütün biletleri `/api/bilet/<no>` ucundan **aynı anda** iste ve girdideki sırayla `<no>|<başlık>` yazdır. Bilet yoksa (`404`) `<no>|YOK` yaz.

Satır boşsa ya da numaralardan biri tam sayı değilse tek satır `HATA` yazdır.

```stdin
101 104 107
```

```setup
import os, runpy, sys
_s = next(os.path.dirname(m.__file__) for m in list(sys.modules.values())
          if os.path.basename(getattr(m, "__file__", None) or "") in ("py_harness.py", "wsl_job.py"))
runpy.run_path(os.path.join(_s, "api_tezgah.py"), run_name="__tezgah__")
```

```meta
backend: wsl
timeout: 90
```

```starter
import asyncio, aiohttp, api

parcalar = input().split()

async def calis(nolar):
    async with aiohttp.ClientSession() as oturum:
        await oturum.post(api.SUNUCU + "/giris", json={"kullanici": api.KULLANICI, "parola": api.PAROLA})
        # biletleri aynı anda iste

asyncio.run(calis([int(p) for p in parcalar]))
```

```test
eq(out, "101|web01 disk doldu\n104|web02 sertifika süresi\n107|yedek01 disk testi\n",
   "üç bilet, girdideki sırayla")
eq(run(stdin="107 101\n"), "107|yedek01 disk testi\n101|web01 disk doldu\n", "girdinin sırası korunur")
eq(run(stdin="999\n"), "999|YOK\n", "olmayan bilet 404: YOK")
eq(run(stdin="101 999 103\n"), "101|web01 disk doldu\n999|YOK\n103|cache01 yeniden başladı\n",
   "bulunan ve bulunmayan karışık")
eq(run(stdin="101 x\n"), "HATA\n", "sayı olmayan numara HATA")
eq(run(stdin="\n"), "HATA\n", "boş girdi HATA")
ok("gather" in src or "TaskGroup" in src or "create_task" in src, "biletleri aynı anda iste")
```

```solution
import asyncio, aiohttp, api

parcalar = input().split()

async def calis(nolar):
    kavanoz = aiohttp.CookieJar(unsafe=True)
    async with aiohttp.ClientSession(cookie_jar=kavanoz) as oturum:
        async with oturum.post(api.SUNUCU + "/giris",
                               json={"kullanici": api.KULLANICI, "parola": api.PAROLA}) as y:
            y.raise_for_status()

        async def bir(no):
            async with oturum.get(f"{api.SUNUCU}/api/bilet/{no}") as y:
                if y.status == 404:
                    return f"{no}|YOK"
                y.raise_for_status()
                return f"{no}|{(await y.json())['baslik']}"

        for satir in await asyncio.gather(*(bir(n) for n in nolar)):
            print(satir)

if parcalar and all(p.isdigit() for p in parcalar):
    asyncio.run(calis([int(p) for p in parcalar]))
else:
    print("HATA")
```

```hint
Girişten sonra liste istekleri `401` alıyorsa sebep çerez kavanozudur: `aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar(unsafe=True))`.
```

```hint
`404` bir istisna değildir; `y.status`'a bak. Beklenmedik başka bir kod için `y.raise_for_status()` çağır ki sessizce yanlış veri yazmasın.
```
:::
