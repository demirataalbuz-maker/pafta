---
id: p74
title: requests Session ve Beautiful Soup
summary: Oturumlu HTTP istemcisi: çerezi taşıyan Session, params ve json, timeout, durum kodunu okumak ve sayfalama; HTML'yi regex yerine ağaçtan okumak, eksik öğe None döner, kapanmamış etiket veriyi sessizce birleştirir; form gövdesi (data=), kimlikli vekil ve Via ile kanıtı, kendi CA'nla doğrulama ve iki TLS hatasını ayırmak, kütüphane sürümünü ve yerini kaydetmek; aiohttp ile sınırlı eşzamanlılık.
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

Gerçek bir hedefte eklenen üç şey var: **TLS** (sertifika doğrulaması; `verify=False` yazmak güvenliği kapatır, hata ayıklarken bile alışkanlık yapma; dersin ilerisinde tezgah kendi CA'sıyla HTTPS'te de açılır), **oran sınırı** (`429` ve `Retry-After`), ve **robots.txt ile kullanım koşulları**. Bir siteyi izinsiz taramak teknik değil hukuki bir sorundur.

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

::: anlat Gerçek hedefin dört ayarı: form, vekil, CA ve sürüm
Buraya kadar yalnız JSON gövde gönderdin. Gerçek hedeflerde dört ayar daha karşına çıkar.

**Form gövdesi.** Tarayıcıdaki bir HTML formu veriyi JSON olarak değil, `application/x-www-form-urlencoded` olarak gönderir: `ad=değer&ad2=değer2`. `requests`'te bunu `data={...}` yapar; değerleri **yüzde kodlamasıyla** kodlar (`&` → `%26`, boşluk → `+`, `+` → `%2B`). Tezgahın `/giris-form` ucu yalnız bu biçimi kabul eder; JSON gönderirsen `415` döner. Gövdeyi elle `"kullanici=" + ad + "&parola=" + parola` diye kurarsan, parolada `&` ya da `+` olduğunda sunucu başka bir parola okur. Bu derste ölçüldü: tezgahın özel karakterli parolasıyla elle kurulan gövde `401` aldı, `data=` ile kurulan `200`.

**Vekil (proxy).** Kurumlar dışarı çıkan trafiği bir vekilden geçirir. Burp de bir vekildir (HT17). `proxies` sözlüğünün anahtarı **hedef adresin şemasıdır**, vekilin değil:

```python norun
proxies = {"http": "http://kullanici:parola@127.0.0.1:8080"}   # http:// adreslerine giden istekler bu vekilden geçer
requests.get("http://127.0.0.1:5000/bos", proxies=proxies, timeout=5)
```

| Durum | Sonuç |
|---|---|
| Vekil kimlik ister, sen vermezsin | `407 Proxy Authentication Required` ve `Proxy-Authenticate` başlığı |
| Kimlik adresin içinde (`http://ad:parola@vekil:port`) | `requests` onu `Proxy-Authorization` başlığına çevirir |
| `Session().proxies = {...}` | Oturumdaki bütün istekler vekilden geçer |
| Ortamda `HTTP_PROXY`/`HTTPS_PROXY` tanımlı | `requests` onları **kendiliğinden** kullanır (`trust_env`); `NO_PROXY` hariç tutar |

> [!TUZAK] Yanlış anahtar, vekili sessizce atlar
> `proxies={"https": vekil}` yazıp `http://` bir adrese istek atarsan istek vekile **hiç uğramaz**. Hiçbir hata ya da uyarı yoktur; doğrudan hedefe gider. Bu derste ölçüldü: yanıt geldi, ama vekilin `Via` başlığı yoktu ve vekilin sayacı artmadı. Trafiğin gerçekten vekilden geçtiğini **yanıttaki `Via` başlığından** ya da vekilin kendi kaydından doğrula.

**CA doğrulaması.** HTTPS'te `requests` sunucunun sertifikasını kendi güven deposuyla (`certifi`) doğrular. Kurum içi ya da laboratuvar sunucuları çoğu zaman **kendi CA'larıyla** imzalanır. Doğru çözüm, o CA dosyasını **yalnız o çağrıya** vermektir: `verify="ca.pem"`. `verify=False` doğrulamayı tümden kapatır; araya giren herkesin sertifikasını da kabul eder.

| Deneme | Sonuç (bu derste ölçüldü) |
|---|---|
| `verify=api.CA`, `https://127.0.0.1:...` | doğrulama geçer; durum kodu ne olursa olsun bir **HTTP yanıtı** gelir (204, 404...) |
| CA verilmez (varsayılan `certifi`) | `SSLError`: `unable to get local issuer certificate` |
| `verify=api.CA`, `https://localhost:...` | `SSLError`: `Hostname mismatch, certificate is not valid for 'localhost'` |

İkinci ve üçüncü satır aynı istisna sınıfıdır (`requests.exceptions.SSLError`), ama anlamları farklıdır: biri "bu imzacıyı tanımıyorum", öteki "imzacı tamam, sertifika bu ada verilmemiş". Sertifika yalnız `127.0.0.1` IP adına verildiği için `localhost` başka bir addır, aynı makine olsa bile. Bir `404` ise TLS hatası **değildir**: el sıkışma başarılı olmuş, sunucu HTTP düzeyinde "yok" demiştir.

**Sürüm kaydı.** Bir betiğin sonucunu raporlarken hangi kütüphane sürümüyle ve **hangi klasörden** yüklendiğini de yaz. Aynı makinede bir paketin iki kopyası olabilir (P75'te `.deps` örneği). `requests.__version__` modülün kendi söylediği sürümdür; `importlib.metadata.version("requests")` kurulu dağıtımın kayıtlı sürümüdür. Modülün gerçek yeri `requests.__file__`'dır.
:::

::: gorev Formla giriş
Girdi kutusunun ilk satırı kullanıcı adı, ikinci satırı paroladır. Bir `Session` ile `/giris-form` ucuna **form gövdesiyle** giriş yap, sonra aynı oturumla `/api/biletler`'i iste.

- Giriş `200` ise `200|<toplam>` yazdır; toplamı liste yanıtının `toplam` alanından al.
- Değilse `<giriş kodu>|-` yazdır.
- Girdi iki satır değilse tek satır `HATA` yazdır.

Tezgahta iki hesap var: `api.KULLANICI` / `api.PAROLA` ve özel karakterli `api.FORM_KULLANICI` / `api.FORM_PAROLA`.

```stdin
nöbetçi analist
a&b=c d+%
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
govde = "kullanici=" + satirlar[0] + "&parola=" + satirlar[1]
y = oturum.post(api.SUNUCU + "/giris-form", data=govde, timeout=5)
print(y.status_code)
```

```test
eq(out, "200|7\n", "özel karakterli parola form kodlamasıyla doğru gider")
eq(run(stdin="analist\npafta123\n"), "200|7\n", "ikinci hesap")
eq(run(stdin="analist\nyanlis\n"), "401|-\n", "yanlış parola: liste istenmez")
eq(run(stdin="nöbetçi analist\na&b=c d\n"), "401|-\n", "parolanın bir kısmı yetmez")
eq(run(stdin="yalniz\n"), "HATA\n", "tek satır HATA")
ok("data=" in src and "json=" not in src, "form gövdesi data= ile gönderilir")
```

```solution
import api, requests, sys

satirlar = sys.stdin.read().splitlines()
if len(satirlar) != 2:
    print("HATA")
    raise SystemExit

oturum = requests.Session()
y = oturum.post(api.SUNUCU + "/giris-form",
                data={"kullanici": satirlar[0], "parola": satirlar[1]}, timeout=5)
if y.status_code != 200:
    print(f"{y.status_code}|-")
else:
    liste = oturum.get(api.SUNUCU + "/api/biletler", timeout=5)
    print(f"200|{liste.json()['toplam']}")
```

```hint
Gövdeyi metin olarak kurma; sözlük ver: `data={"kullanici": ..., "parola": ...}`. `requests` `&`, `=`, `+` ve boşluğu kendisi kodlar ve `Content-Type` başlığını koyar.
```

```hint
`json=` gönderirsen sunucu `415` döner: `/giris-form` yalnız form biçimini kabul eder.
```
:::

::: gorev Vekilden geçtiğini kanıtla
`api.vekil_kur()` kimlik isteyen bir vekil başlatır ve adresini döndürür. Girdi kutusunun ilk satırı vekil kimliğidir: `ad:parola`. Satır boşsa kimliksiz dene.

Vekili kullanan bir `Session` kur, giriş yap (`/giris`, JSON) ve `/api/bilet/101`'i iste. Tek satır yazdır:

- Bilet geldiyse `<durum kodu>|<Via başlığı>|<başlık>`.
- Vekil reddettiyse (`407`) `407|-|-`.
- Yanıtta `Via` başlığı **yoksa**, yani istek vekilden geçmediyse, sonuç ne olursa olsun `VEKILSIZ` yazdır.

```stdin
vekil:pafta-vekil-2026
```

```setup
import os, runpy, sys
_s = next(os.path.dirname(m.__file__) for m in list(sys.modules.values())
          if os.path.basename(getattr(m, "__file__", None) or "") in ("py_harness.py", "wsl_job.py"))
runpy.run_path(os.path.join(_s, "api_tezgah.py"), run_name="__tezgah__")
import api
api.vekil_kur()
```

```starter
import api, requests

kimlik = input().strip()
oturum = requests.Session()
oturum.proxies = {"https": api.VEKIL}
oturum.post(api.SUNUCU + "/giris", json={"kullanici": api.KULLANICI, "parola": api.PAROLA}, timeout=5)
y = oturum.get(api.SUNUCU + "/api/bilet/101", timeout=5)
print(y.status_code, y.json()["baslik"])
```

```test
import api
eq(out, "200|1.1 pafta-vekil|web01 disk doldu\n", "kimlikli vekil: giriş ve bilet vekilden geçti")
once = api.vekil_sayac()
eq(run(stdin="vekil:pafta-vekil-2026\n"), "200|1.1 pafta-vekil|web01 disk doldu\n", "ikinci çalıştırma")
ok(api.vekil_sayac() - once >= 2, "vekil hem girişi hem bilet isteğini gördü", got=api.vekil_sayac() - once)
eq(run(stdin="vekil:yanlis\n"), "407|-|-\n", "yanlış vekil parolası 407")
eq(run(stdin="\n"), "407|-|-\n", "kimliksiz istek 407")
eq(run(stdin="baska:pafta-vekil-2026\n"), "407|-|-\n", "yanlış vekil kullanıcısı 407")
yanlis_anahtar = src.replace('"http"', '"https"').replace("'http'", "'https'")
if yanlis_anahtar != src:
    eq(run_code(yanlis_anahtar, stdin="vekil:pafta-vekil-2026\n"), "VEKILSIZ\n",
       "proxies anahtarı https olursa istek vekili atlar; bunu Via başlığından yakalarsın")
ok("Via" in src, "vekilden geçtiğini yanıttaki Via başlığıyla doğrula")
```

```solution
import api, requests

kimlik = input().strip()
vekil = api.VEKIL.replace("http://", f"http://{kimlik}@") if kimlik else api.VEKIL
oturum = requests.Session()
oturum.proxies = {"http": vekil}
oturum.post(api.SUNUCU + "/giris", json={"kullanici": api.KULLANICI, "parola": api.PAROLA}, timeout=5)
y = oturum.get(api.SUNUCU + "/api/bilet/101", timeout=5)
via = y.headers.get("Via")
if y.status_code == 407:
    print("407|-|-")
elif via is None:
    print("VEKILSIZ")
else:
    print(f"{y.status_code}|{via}|{y.json()['baslik']}")
```

```hint
`proxies` sözlüğünün anahtarı **hedefin** şemasıdır. Tezgah `http://` olduğu için anahtar `"http"` olmalı. Kimliği vekil adresine göm: `http://ad:parola@127.0.0.1:PORT`.
```

```hint
Vekilin reddi `407` durum kodudur, istisna değildir. Önce `407`'yi, sonra `Via` başlığının yokluğunu denetle: `y.headers.get("Via")` başlık yoksa `None` verir.
```
:::

::: gorev Kendi CA'nla doğrula
`api.tls_kur()` uygulamayı HTTPS'te de başlatır: `api.HTTPS_SUNUCU`, ders CA'sı `api.CA` ve port `api.HTTPS_PORT`. Girdi kutusunun ilk satırı bir deneme adıdır:

| Deneme | İstek |
|---|---|
| `ca` | `api.HTTPS_SUNUCU + "/bos"`, CA olarak `api.CA` |
| `ca-yok` | `api.HTTPS_SUNUCU + "/yok"`, CA olarak `api.CA` |
| `sistem` | `api.HTTPS_SUNUCU + "/bos"`, varsayılan doğrulama (CA verme) |
| `ad` | `https://localhost:<api.HTTPS_PORT>/bos`, CA olarak `api.CA` |

Tek satır yazdır: HTTP yanıtı geldiyse `HTTP|<durum kodu>`; imzacı tanınmadıysa `TANINMAYAN_CA`; sertifika bu ada verilmemişse `AD_UYUSMAZ`. Tanınmayan deneme adı için `HATA`. **Doğrulamayı hiçbir denemede kapatma.**

```stdin
ca
```

```setup
import os, runpy, sys
_s = next(os.path.dirname(m.__file__) for m in list(sys.modules.values())
          if os.path.basename(getattr(m, "__file__", None) or "") in ("py_harness.py", "wsl_job.py"))
runpy.run_path(os.path.join(_s, "api_tezgah.py"), run_name="__tezgah__")
import api
api.tls_kur()
```

```starter
import api, requests

deneme = input().strip()
y = requests.get(api.HTTPS_SUNUCU + "/bos", verify=False, timeout=5)
print("HTTP|" + str(y.status_code))
```

```test
eq(out, "HTTP|204\n", "ders CA'sıyla doğrulama geçer")
eq(run(stdin="ca-yok\n"), "HTTP|404\n", "404 bir TLS hatası değildir: el sıkışma başarılı, sunucu HTTP'de yok dedi")
eq(run(stdin="sistem\n"), "TANINMAYAN_CA\n", "varsayılan güven deposu ders CA'sını tanımaz")
eq(run(stdin="ad\n"), "AD_UYUSMAZ\n", "sertifika 127.0.0.1'e verildi; localhost başka bir addır")
eq(run(stdin="baska\n"), "HATA\n", "tanınmayan deneme")
ok("verify=False" not in src.replace(" ", ""), "verify=False doğrulamayı kapatır; kullanma")
ok("api.CA" in src, "CA yalnız o çağrıya verilir: verify=api.CA")
```

```solution
import api, requests

deneme = input().strip()
istekler = {
    "ca": (api.HTTPS_SUNUCU + "/bos", api.CA),
    "ca-yok": (api.HTTPS_SUNUCU + "/yok", api.CA),
    "sistem": (api.HTTPS_SUNUCU + "/bos", True),
    "ad": (f"https://localhost:{api.HTTPS_PORT}/bos", api.CA),
}
if deneme not in istekler:
    print("HATA")
    raise SystemExit

adres, dogrula = istekler[deneme]
try:
    y = requests.get(adres, verify=dogrula, timeout=5)
except requests.exceptions.SSLError as e:
    print("AD_UYUSMAZ" if "Hostname mismatch" in str(e) else "TANINMAYAN_CA")
else:
    print(f"HTTP|{y.status_code}")
```

```hint
`verify` hem `True`/`False` hem bir dosya yolu alır: `verify=api.CA`. Varsayılan (`True`) `requests`'in kendi güven deposudur.
```

```hint
İki doğrulama hatası da `requests.exceptions.SSLError`'dır. Ayırmak için mesajın içine bak: ad uyuşmazlığında `Hostname mismatch` geçer, tanınmayan imzacıda `unable to get local issuer certificate`.
```
:::

::: gorev Hangi kütüphaneyle çalıştın?
Raporuna eklenecek üç satırı yazdır:

```text
python <büyük.küçük.yama>
requests <sürüm> <yüklendiği klasör>
urllib3 <sürüm> <yüklendiği klasör>
```

Klasör, modülü içeren paket klasörünün **bir üstüdür** (`requests/__init__.py` için `.../site-packages` gibi). Sürümü **o klasördeki dağıtım kaydından** al: `importlib.metadata.distributions(path=[klasör])`. Modülün kendi `__version__` değeri kayıttaki sürümle uyuşmuyorsa o satırın sonuna ` UYUSMAZ` ekle.

```setup
import os, runpy, sys
_s = next(os.path.dirname(m.__file__) for m in list(sys.modules.values())
          if os.path.basename(getattr(m, "__file__", None) or "") in ("py_harness.py", "wsl_job.py"))
runpy.run_path(os.path.join(_s, "api_tezgah.py"), run_name="__tezgah__")
```

```starter
import requests, urllib3

print("requests", requests.__version__)
print("urllib3", urllib3.__version__)
```

```test
import importlib.metadata as md, os, sys
satirlar = out.splitlines()
eq(len(satirlar), 3, "üç satır")
eq(satirlar[0] if satirlar else "", "python " + ".".join(str(x) for x in sys.version_info[:3]), "yorumlayıcı sürümü")
for satir, ad in zip(satirlar[1:], ("requests", "urllib3")):
    p = satir.split(" ")
    ok(len(p) >= 3 and p[0] == ad, ad + " satırı", got=satir)
    if len(p) < 3:
        continue
    klasor = " ".join(p[2:]).removesuffix(" UYUSMAZ")
    ok(os.path.isfile(os.path.join(klasor, ad, "__init__.py")), ad + " gerçekten bu klasörden yüklenebilir", got=klasor)
    kayit = [d.version for d in md.distributions(path=[klasor]) if d.metadata["Name"].lower() == ad]
    eq(p[1], kayit[0] if kayit else None, ad + " sürümü o klasördeki dağıtım kaydıyla aynı")
    modul = sys.modules.get(ad)
    ok(modul is not None and os.path.dirname(os.path.dirname(modul.__file__)) == klasor,
       ad + " klasörü gerçekten yüklenen kopyanın klasörü")
    if modul is not None:
        eq(satir.endswith(" UYUSMAZ"), modul.__version__ != p[1],
           ad + ": UYUSMAZ yalnız __version__ kayıttan farklıysa eklenir")
import requests
gercek = requests.__version__
requests.__version__ = "0.0.0"
try:
    bozuk = run_code(src).splitlines()
finally:
    requests.__version__ = gercek
ok(len(bozuk) == 3 and bozuk[1].endswith(" UYUSMAZ") and not bozuk[2].endswith(" UYUSMAZ"),
   "modülün __version__'ı kayıttan farklıysa yalnız o satıra UYUSMAZ eklenir", got=bozuk[1:])
ok("distributions" in src, "sürümü yüklenen klasördeki dağıtım kaydından al")
```

```solution
import importlib.metadata as md, os, sys
import requests, urllib3

print("python", ".".join(str(x) for x in sys.version_info[:3]))
for modul in (requests, urllib3):
    ad = modul.__name__
    klasor = os.path.dirname(os.path.dirname(modul.__file__))
    surum = next(d.version for d in md.distributions(path=[klasor]) if d.metadata["Name"].lower() == ad)
    print(ad, surum, klasor + ("" if modul.__version__ == surum else " UYUSMAZ"))
```

```hint
`os.path.dirname(requests.__file__)` paketin kendi klasörüdür (`.../requests`); bir kez daha `dirname` alınca paketin bulunduğu yer çıkar.
```

```hint
`importlib.metadata.version("requests")` kısa yoldur, ama `sys.path`'te **ilk bulduğu** kaydı okur. Bir paketin iki kopyası varsa bu kayıt yüklenen kopyanınki olmayabilir. Klasörü `__file__`'dan al, kaydı o klasörde ara: `[d for d in md.distributions(path=[klasor]) if d.metadata["Name"].lower() == "requests"]`.
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
