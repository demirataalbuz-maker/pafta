---
id: ai-saldiri-22
title: SSRF Filtre ve Yönlendirme Atlatma
summary: URL'yi tek bir kanonik origin'e indir, her yönlendirme hedefini yeniden doğrula, DNS cevapları ile gerçek socket hedefi arasındaki sapmaları raporla.
timeout: 45
---

::: anlat Filtrenin okuduğu hedef ile bağlanılan hedef aynı olmalı
SSRF filtresi URL string'ine bakarken HTTP istemcisi ayrıştırıcı, yönlendirme ve DNS katmanlarından geçer. Bu katmanlar farklı hedefler görürse ilk kontrol doğru olsa bile son bağlantı iç servise gidebilir. Özellikle userinfo, eksik port, trailing dot, şema değişimi ve `//host/...` biçimindeki ağ-yolu referansları basit string kontrollerini bozar.

Savunma tek bir kontrol noktasında üç şeyi bağlar: kanonik origin, her redirect sonrası yeniden politika kontrolü ve DNS'de karar verilen IP ile socket'e verilen IP'nin aynılığı. İlk URL'nin izinli olması son hedef için kanıt değildir.

Bu derste mitmproxy, Burp Suite, DNS veya gerçek socket kullanılmaz. URL ve çözümleme kayıtları deterministik fixture'dır; 21. dersteki gerçek loopback laboratuvarı değiştirilmez.
:::

::: tahmin Göreli gibi görünen hedef aynı origin'de mi?
Ağ-yolu referansı `//` ile başlar ve mevcut şemayı koruyarak hostu değiştirir. Üç çıktı satırını yaz:

```python
from urllib.parse import urljoin, urlsplit
ilk = "http://public.test:80/start"
yeni = urljoin(ilk, "//internal.test:80/canary")
print(yeni)
print(urlsplit(ilk).hostname)
print(urlsplit(yeni).hostname)
```

???

```cikti
http://internal.test:80/canary
public.test
internal.test
```

Yeni hedef aynı scheme'i kullansa da origin değişmiştir. Bu nedenle her `Location` çözümlendikten sonra baştan doğrulanmalıdır.
:::

::: gorev 1 · URL'yi dar ve kanonik bir origin'e indir
`url_origin(url)` işlevini yaz. Girdi ASCII 33–126 aralığındaki karakterlerden oluşan string olmalı; boşluk/kontrol, non-ASCII, ters eğik çizgi ve fragment içeremez. Yalnız `http`, açık port ve userinfo'suz URL kabul edilir. Host yalnız ASCII harf, rakam, nokta ve tire içerebilir. Hostu küçük harfe çevir ve sondaki noktaları kaldır; sonuç boşalamaz. IPv6 bu dar fixture politikasının dışındadır. Ayrıştırma, port, şema veya şema dışı tür hatasında `ValueError` yükselt.

Dönüş tam olarak `{"origin":"http://HOST:PORT","host":HOST,"port":PORT}` biçimindedir. Path ve query origin kararını değiştirmez. Gerçek DNS veya ağ erişimi yapma.

```starter
def url_origin(url):
    return {}
```

```test
def sozlesme(fn):
    try:
        if fn("http://public.test:80/a?x=1") != {"origin": "http://public.test:80", "host": "public.test", "port": 80}:
            return False
        if fn("HTTP://PUBLIC.TEST.:8080/x") != {"origin": "http://public.test:8080", "host": "public.test", "port": 8080}:
            return False
        if fn("http://127.0.0.1:65535/")["port"] != 65535:
            return False
        if fn("http://public.test:1/a!b~")["port"] != 1:
            return False
        for url in [
            None, 3, "", "/a", "https://public.test:80/a", "http://public.test/a",
            "http://public.test:/a", "http://public.test:0/a", "http://public.test:65536/a",
            "http://user@public.test:80/a", "http://user:pw@public.test:80/a",
            "http://public.test:80/a#x", "http://public.test:80/a\\b",
            "http://public.test:80/a b", "http://public.test:80/ğ",
            "http://:80/a", "http://...:80/a", "http://[::1]:80/a",
            "http://public_test:80/a", "http://public.test:80/a\tb",
            "http://public.test:80/a\x7fb",
        ]:
            try:
                fn(url)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(url_origin), "şema, userinfo, açık port, kanonik host ve ASCII sınırı korunmalı")
def m_sema(url):
    return url_origin(url.replace("https://", "http://"))
def m_user(url):
    return url_origin(url.replace("user@", ""))
def m_port(url):
    return url_origin(url.replace("http://public.test/", "http://public.test:80/"))
for ad, mutant in [("https'i http'ye çeviren", m_sema), ("userinfo'yu gizleyen", m_user), ("eksik portu tamamlayan", m_port)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def url_origin(url):
    from urllib.parse import urlsplit
    if not isinstance(url, str) or not url or any(ord(c) < 33 or ord(c) > 126 for c in url):
        raise ValueError("URL karakterleri geçersiz")
    if "\\" in url or "#" in url:
        raise ValueError("belirsiz URL")
    try:
        u = urlsplit(url)
        if u.scheme != "http" or not u.hostname or u.username is not None or u.password is not None:
            raise ValueError("URL origin'i geçersiz")
        host = u.hostname.lower().rstrip(".")
        port = u.port
    except (TypeError, ValueError) as exc:
        raise ValueError("URL ayrıştırılamadı") from exc
    if not host or not all(c.isascii() and (c.isalnum() or c in ".-") for c in host):
        raise ValueError("host geçersiz")
    if port is None or port < 1:
        raise ValueError("açık port gerekli")
    return {"origin": "http://" + host + ":" + str(port), "host": host, "port": port}
```

```hint
`urlsplit` sonrasında scheme, hostname, userinfo ve portu ayrı denetle. Dönüş origin'ini girdiden kopyalamak yerine normalize edilmiş host ve doğrulanmış porttan yeniden kur.
```
:::

::: anlat Her Location yeni bir istek adayıdır
`Location: /ok` aynı origin'de kalırken `Location: //internal.test:80/canary` hostu değiştirir. Filtre yalnız başlangıç URL'sine uygulanırsa ikinci istek kontrolden kaçar. Güvenli iz, başlangıç ve her çözümlenmiş hedef için aynı doğrulamayı çalıştırır.

Hop sınırı da politikanın parçasıdır. Sınır aşıldığında yeni hedefi doğrulamadan kabul etmek yerine bütün zincir reddedilir. Bu görev HTTP yanıtı üretmez; yalnız istemcinin sırayla hangi URL'lere istek açacağını hesaplar.
:::

::: gorev 2 · Başlangıç ve her redirect hedefini aynı origin'e bağla
`redirect_originleri(baslangic, locationlar, izinli_origin, max_hop=3)` işlevini yaz. `izinli_origin`, ilk görevin ürettiği kanonik `http://host:port` stringi olmalı; path, query, trailing slash veya farklı yazım kabul edilmez. Başlangıç ve her hedef ilk görevdeki URL kurallarına uymalı ve origin'i birebir izinli origin olmalıdır. `locationlar` string listesidir; her `Location` mevcut URL'ye göre `urljoin` ile çözümlenir. `max_hop` bool olmayan sıfır/pozitif int olmalı ve redirect sayısı bunu aşamaz. Geçersiz veri, origin değişimi veya sınır aşımında `ValueError` yükselt.

Dönüş `{"hop":N,"son_url":SON,"istekler":[BASLANGIC,...]}` biçimindedir. `istekler` başlangıç ve kabul edilmiş bütün hedefleri sırayla içerir; girdi listesinden bağımsızdır. Ağ erişimi yapma.

```starter
def redirect_originleri(baslangic, locationlar, izinli_origin, max_hop=3):
    return {}
```

```test
def sozlesme(fn):
    try:
        origin = "http://public.test:80"
        beklenen = {"hop": 2, "son_url": "http://public.test:80/a/son", "istekler": ["http://public.test:80/a/basla", "http://public.test:80/a/orta", "http://public.test:80/a/son"]}
        if fn("http://public.test:80/a/basla", ["orta", "son"], origin) != beklenen:
            return False
        if fn("http://public.test:80/a", [], origin, max_hop=0) == {"hop": 0, "son_url": "http://public.test:80/a", "istekler": ["http://public.test:80/a"]}:
            pass
        else:
            return False
        if fn("http://public.test:80/a!~", ["/b!~"], origin, max_hop=1)["son_url"] != "http://public.test:80/b!~":
            return False
        if fn("http://public.test:1/a", [], "http://public.test:1")["hop"] != 0:
            return False
        try:
            fn("http://public.test:80/a", ["/a", "/b", "/c", "/d"], origin)
            return False
        except ValueError:
            pass
        for baslangic, locations, allowed, limit in [
            (3, [], origin, 3),
            ("http://internal.test:80/a", [], origin, 3),
            ("http://public.test:80/a", ["//internal.test:80/canary"], origin, 3),
            ("http://public.test:80/a", ["/orta", "https://public.test:80/son"], origin, 3),
            ("http://public.test:80/a", ["http://user@public.test:80/x"], origin, 3),
            ("http://public.test:80/a", ["http://:80/x"], origin, 3),
            ("http://public.test:80/a", ["http://public.test/x"], origin, 3),
            ("http://public.test:80/a", ["http://public.test:0/x"], origin, 3),
            ("http://public_test:80/a", [], origin, 3),
            ("http://public.test:80/a", ["/x"], "http://public.test:80/", 3),
            ("http://public.test:80/a", ["/x"], "http://public.test:80/path", 3),
            ("http://public.test:80/a", ["/x"], "http://public.test:80?x=1", 3),
            ("http://public.test:80/a", ["/x"], origin, 0),
            ("http://public.test:80/a", [], origin, -1),
            ("http://public.test:80/a", [], origin, True),
            ("http://public.test:80/a", "/x", origin, 3),
            ("http://public.test:80/a", [None], origin, 3),
            ("http://public.test:80/a", ["/a b"], origin, 3),
            ("http://public.test:80/a", ["/a#x"], origin, 3),
            ("http://public.test:80/a", ["/a\x7fb"], origin, 3),
        ]:
            try:
                fn(baslangic, locations, allowed, limit)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(redirect_originleri), "göreli çözümleme, her hop origin kontrolü ve hop sınırı korunmalı")
def m_atla(baslangic, locationlar, izinli_origin, max_hop=3):
    from urllib.parse import urljoin
    sonuc = redirect_originleri(baslangic, [], izinli_origin, max_hop)
    current = baslangic
    for location in locationlar:
        current = urljoin(current, location)
        sonuc["istekler"].append(current)
    sonuc["hop"] = len(locationlar)
    sonuc["son_url"] = current
    return sonuc
def m_limit(baslangic, locationlar, izinli_origin, max_hop=3):
    return redirect_originleri(baslangic, locationlar, izinli_origin, max(max_hop, len(locationlar)))
def m_location(baslangic, locationlar, izinli_origin, max_hop=3):
    return redirect_originleri(baslangic, ["/sabit" for _ in locationlar], izinli_origin, max_hop)
for ad, mutant in [("redirect kontrollerini atlayan", m_atla), ("hop sınırını büyüten", m_limit), ("Location değerini yok sayan", m_location)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def redirect_originleri(baslangic, locationlar, izinli_origin, max_hop=3):
    from urllib.parse import urlsplit, urljoin
    if type(max_hop) is not int or max_hop < 0 or not isinstance(locationlar, list):
        raise ValueError("hop veya Location listesi geçersiz")
    if len(locationlar) > max_hop:
        raise ValueError("hop sınırı aşıldı")
    def origin_denetle(url):
        import re
        from urllib.parse import urlsplit
        if not isinstance(url, str) or not url or any(ord(c) < 33 or ord(c) > 126 for c in url) or "\\" in url or "#" in url:
            raise ValueError("URL geçersiz")
        try:
            u = urlsplit(url)
            host = u.hostname.lower().rstrip(".") if u.hostname else ""
            origin = "http://" + host + ":" + str(u.port)
            if u.scheme != "http":
                raise ValueError("şema geçersiz")
            if not host:
                raise ValueError("host gerekli")
            if u.username is not None:
                raise ValueError("kullanıcı bilgisi geçersiz")
            if u.password is not None:
                raise ValueError("parola geçersiz")
            if u.port is None:
                raise ValueError("port gerekli")
            if u.port < 1:
                raise ValueError("port geçersiz")
            if not re.fullmatch(r"[a-z0-9.-]+", host):
                raise ValueError("host geçersiz")
            return origin
        except (TypeError, ValueError) as exc:
            raise ValueError("URL ayrıştırılamadı") from exc
    if origin_denetle(izinli_origin) != izinli_origin:
        raise ValueError("izinli origin kanonik değil")
    if urlsplit(izinli_origin).path:
        raise ValueError("izinli origin path içeremez")
    if urlsplit(izinli_origin).query:
        raise ValueError("izinli origin query içeremez")
    current = baslangic
    if origin_denetle(current) != izinli_origin:
        raise ValueError("başlangıç origin'i izinsiz")
    istekler = [current]
    for location in locationlar:
        if not isinstance(location, str):
            raise ValueError("Location string olmalı")
        current = urljoin(current, location)
        if origin_denetle(current) != izinli_origin:
            raise ValueError("redirect origin'i izinsiz")
        istekler.append(current)
    return {"hop": len(locationlar), "son_url": current, "istekler": istekler}
```

```hint
Tek bir yerel origin doğrulayıcı yaz ve hem başlangıçta hem her `urljoin` sonrasında çağır. Yeni hedefi listeye eklemeden önce kontrol et; Location sayısını önceden hop sınırıyla karşılaştır.
```
:::

::: anlat DNS kontrolü socket'e sabitlenmeli
Bir hostname politikada bir IP'ye, hemen ardından socket açılırken başka IP'ye çözümlenirse DNS rebinding boşluğu oluşur. Birden fazla çözümleme kaydı tutulduğunda ilk ve son cevabın aynı görünmesi de yeterli değildir; ara cevaplardan biri kısıtlı ağı gösterebilir. Dar fixture politikasında bütün cevaplar izinli IP'ye eşit olmalı ve bağlantı son denetlenen IP'yi kullanmalıdır.

Regresyon dört ayrı sınıf üretir: cevaplar arasında değişim, izinsiz DNS cevabı, socket IP sapması ve bütünüyle temiz vaka. Böylece “DNS kontrolü var” iddiası ile gerçek bağlantı kanıtı birbirinden ayrılır.
:::

::: gorev 3 · DNS rebinding ve socket IP sapmasını raporla
`dns_regresyonu(kayitlar)` işlevini yaz. Girdi liste olmalıdır. Her kayıt tam olarak `vaka_id`, `izinli_ip`, `cozumler`, `baglanti_ip` alanlarını taşısın. Vaka kimliği boş olmayan ve benzersiz string; IP alanları IPv4 stringleri; `cozumler` en az bir IPv4 içeren liste olmalıdır. IP'leri `ipaddress.IPv4Address` ile doğrula. Geçersiz veride `ValueError` yükselt.

Dönüş:

```text
{"vaka":N,"rebinding":[...],"yetkisiz_dns":[...],
 "socket_sapmasi":[...],"temiz":[...]}
```

- `rebinding`: `cozumler` içinde birden fazla farklı IP var.
- `yetkisiz_dns`: herhangi bir çözüm `izinli_ip`den farklı.
- `socket_sapmasi`: `baglanti_ip != cozumler[-1]`.
- `temiz`: bütün çözümler izinli ve birbirine eşit, socket son çözümle aynı.

Listeler alfabetik vaka kimliği sıralıdır. Bir vaka birden fazla sorun listesine girebilir. Boş girdi için boş rapor dön; girdi sırası sonucu etkilememeli ve girdi değişmemelidir.

```starter
def dns_regresyonu(kayitlar):
    return {}
```

```test
import copy
KAYITLAR = [
    {"vaka_id": "v1", "izinli_ip": "203.0.113.10", "cozumler": ["203.0.113.10", "203.0.113.10"], "baglanti_ip": "203.0.113.10"},
    {"vaka_id": "v2", "izinli_ip": "203.0.113.10", "cozumler": ["203.0.113.10", "127.0.0.1"], "baglanti_ip": "127.0.0.1"},
    {"vaka_id": "v3", "izinli_ip": "203.0.113.10", "cozumler": ["127.0.0.1"], "baglanti_ip": "203.0.113.10"},
    {"vaka_id": "v4", "izinli_ip": "203.0.113.10", "cozumler": ["203.0.113.10"], "baglanti_ip": "127.0.0.1"},
    {"vaka_id": "v5", "izinli_ip": "203.0.113.10", "cozumler": ["203.0.113.10", "127.0.0.1", "203.0.113.10"], "baglanti_ip": "203.0.113.10"},
    {"vaka_id": "v6", "izinli_ip": "203.0.113.10", "cozumler": ["127.0.0.1"], "baglanti_ip": "127.0.0.1"},
]
BEKLENEN = {"vaka": 6, "rebinding": ["v2", "v5"], "yetkisiz_dns": ["v2", "v3", "v5", "v6"], "socket_sapmasi": ["v3", "v4"], "temiz": ["v1"]}
def sozlesme(fn):
    try:
        once = copy.deepcopy(KAYITLAR)
        if fn(KAYITLAR) != BEKLENEN or KAYITLAR != once or fn(list(reversed(KAYITLAR))) != BEKLENEN:
            return False
        if fn([]) != {"vaka": 0, "rebinding": [], "yetkisiz_dns": [], "socket_sapmasi": [], "temiz": []}:
            return False
        for kayitlar in [
            None, {}, [None], KAYITLAR + [KAYITLAR[0]], [dict(KAYITLAR[0], ek=1)],
            [dict(KAYITLAR[0], vaka_id="")], [dict(KAYITLAR[0], izinli_ip="::1")],
            [dict(KAYITLAR[0], cozumler=[])], [dict(KAYITLAR[0], cozumler="203.0.113.10")],
            [dict(KAYITLAR[0], cozumler=["999.1.1.1"])], [dict(KAYITLAR[0], baglanti_ip=None)],
        ]:
            try:
                fn(kayitlar)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(dns_regresyonu), "rebinding, izinsiz DNS, socket sapması ve temizlik ayrımı korunmalı")
def m_rebinding(kayitlar):
    sonuc = dns_regresyonu(kayitlar)
    sonuc["rebinding"] = sorted(x["vaka_id"] for x in kayitlar if x["cozumler"][0] != x["cozumler"][-1])
    return sonuc
def m_dns(kayitlar):
    sonuc = dns_regresyonu(kayitlar)
    sonuc["yetkisiz_dns"] = sorted(x["vaka_id"] for x in kayitlar if x["cozumler"][-1] != x["izinli_ip"])
    return sonuc
def m_temiz(kayitlar):
    sonuc = dns_regresyonu(kayitlar)
    sonuc["temiz"] = sorted(x["vaka_id"] for x in kayitlar if x["baglanti_ip"] == x["izinli_ip"])
    return sonuc
for ad, mutant in [("ara DNS değişimini kaçıran", m_rebinding), ("yalnız son DNS cevabını denetleyen", m_dns), ("temizliği yalnız socket'e indirgeyen", m_temiz)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def dns_regresyonu(kayitlar):
    import ipaddress
    if not isinstance(kayitlar, list):
        raise ValueError("kayıtlar liste olmalı")
    def ipv4(deger):
        if not isinstance(deger, str):
            raise ValueError("IP string olmalı")
        try:
            return str(ipaddress.IPv4Address(deger))
        except ipaddress.AddressValueError as exc:
            raise ValueError("IPv4 geçersiz") from exc
    sonuc = {"vaka": 0, "rebinding": [], "yetkisiz_dns": [], "socket_sapmasi": [], "temiz": []}
    vakalar = set()
    for kayit in kayitlar:
        if not isinstance(kayit, dict) or set(kayit) != {"vaka_id", "izinli_ip", "cozumler", "baglanti_ip"}:
            raise ValueError("kayıt şeması geçersiz")
        if not isinstance(kayit["vaka_id"], str) or not kayit["vaka_id"] or kayit["vaka_id"] in vakalar:
            raise ValueError("vaka kimliği geçersiz")
        izinli = ipv4(kayit["izinli_ip"])
        socket = ipv4(kayit["baglanti_ip"])
        if not isinstance(kayit["cozumler"], list) or not kayit["cozumler"]:
            raise ValueError("DNS cevabı listesi geçersiz")
        cozumler = [ipv4(x) for x in kayit["cozumler"]]
        vakalar.add(kayit["vaka_id"])
        rebinding = len(set(cozumler)) > 1
        yetkisiz = any(x != izinli for x in cozumler)
        sapma = socket != cozumler[-1]
        if rebinding:
            sonuc["rebinding"].append(kayit["vaka_id"])
        if yetkisiz:
            sonuc["yetkisiz_dns"].append(kayit["vaka_id"])
        if sapma:
            sonuc["socket_sapmasi"].append(kayit["vaka_id"])
        if not rebinding and not yetkisiz and not sapma:
            sonuc["temiz"].append(kayit["vaka_id"])
    sonuc["vaka"] = len(vakalar)
    for alan in ("rebinding", "yetkisiz_dns", "socket_sapmasi", "temiz"):
        sonuc[alan].sort()
    return sonuc
```

```hint
Her vakada üç koşulu bağımsız hesapla: `set(cozumler)` birden büyük mü, herhangi bir cevap izinsiz mi, socket son cevaptan farklı mı? Temizlik üçünün de false olmasını gerektirir.
```
:::


::: anlat URL kapısını gerçek bağlantıya, raporu gerçek peer'e bağla
Ham sentetik örnek aynı Pafta sunucusunda `/data/ai-saldiri-22-url-vakalari.txt` adresinde açılır. Mevcut Markdownrenderer bağlantıları tıklanabilir yapmaz; sunucuadresine bu yolu yaz. Çalıştır ayrı kalıcı `calisma/ai-saldiri-22/url-vakalari.json` kopyasının yolunu/içeriğini gösterir; dış editör/Python ile değiştirip yeniden Çalıştır, düzenlemeler korunur. Test ayrı dosya kullanır.

Öğrencinin `redirect_originleri` planı başlangıçta ve her yeni gerçek Location sonrası, sonraki bağlantıdan **önce** çalışır. `url_origin` son hedefin origin'ini denetler; yalnız izinli origin devam eder. Yerel modelin ham URLseçimi de bu kapıya girer. Her istek gerçek HTTP/TCPdir; kanıtta gerçek peer ve sunucuolayı vardır. Normal doğrudan ve iki hoplu okuma çalışmalı, iç origin/yanlışport/userinfo/fragment ve cross-originredirect engellenmelidir. Yalnız deneyin kendi iki sunucusuna bağlantı açılabilir;21'in sınırlandırılmış HTTPsınıfı yeniden kullanılır.

Virtualtesthostname'ler localhosta eşlenir. OS'nin gerçek localhost çözümü ve bağlantının gerçek TCPpeer'i raporlanır. Rebinding ve peerdrift negatifleri **ayrı sentetik DNS kayıtlarıdır**; gerçek DNS sunucusuna saldırı yapıldığı söylenmez. Modelin saldırıya uyması geçme şartı değildir. Kendi sunucuları kapanır, kullanıcının servislerine dokunulmaz.
:::

::: gorev Gerçek deney · Kanonik origin ve DNS raporunu gerçek HTTPye bağla
Önceki `url_origin`, `redirect_originleri`, `dns_regresyonu` işlevlerini birleştir. Çalıştır gerçek ham URL/Location/TCPpeer ve ayrı sentetik DNSraporunu gösterir. Kontrol Et saf sözleşmelerden sonra gerçek kapı/etkiyi sınar.

```meta
motor: ai-gercek
gereksinim: ollama
timeout: 300
```

```starter
import ai_lab

def url_origin(url):return {}

def redirect_originleri(baslangic,locationlar,izinli_origin,max_hop=3):return {}

def dns_regresyonu(kayitlar):return {}

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_saldiri_22 as deney
    deney.goster(url_origin,redirect_originleri,dns_regresyonu)

```

```test
def sozlesme(fn):
    try:
        if fn("http://public.test:80/a?x=1") != {"origin": "http://public.test:80", "host": "public.test", "port": 80}:
            return False
        if fn("HTTP://PUBLIC.TEST.:8080/x") != {"origin": "http://public.test:8080", "host": "public.test", "port": 8080}:
            return False
        if fn("http://127.0.0.1:65535/")["port"] != 65535:
            return False
        if fn("http://public.test:1/a!b~")["port"] != 1:
            return False
        for url in [
            None, 3, "", "/a", "https://public.test:80/a", "http://public.test/a",
            "http://public.test:/a", "http://public.test:0/a", "http://public.test:65536/a",
            "http://user@public.test:80/a", "http://user:pw@public.test:80/a",
            "http://public.test:80/a#x", "http://public.test:80/a\\b",
            "http://public.test:80/a b", "http://public.test:80/ğ",
            "http://:80/a", "http://...:80/a", "http://[::1]:80/a",
            "http://public_test:80/a", "http://public.test:80/a\tb",
            "http://public.test:80/a\x7fb",
        ]:
            try:
                fn(url)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(url_origin), "şema, userinfo, açık port, kanonik host ve ASCII sınırı korunmalı")
def m_sema(url):
    return url_origin(url.replace("https://", "http://"))
def m_user(url):
    return url_origin(url.replace("user@", ""))
def m_port(url):
    return url_origin(url.replace("http://public.test/", "http://public.test:80/"))
for ad, mutant in [("https'i http'ye çeviren", m_sema), ("userinfo'yu gizleyen", m_user), ("eksik portu tamamlayan", m_port)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)

def sozlesme(fn):
    try:
        origin = "http://public.test:80"
        beklenen = {"hop": 2, "son_url": "http://public.test:80/a/son", "istekler": ["http://public.test:80/a/basla", "http://public.test:80/a/orta", "http://public.test:80/a/son"]}
        if fn("http://public.test:80/a/basla", ["orta", "son"], origin) != beklenen:
            return False
        if fn("http://public.test:80/a", [], origin, max_hop=0) == {"hop": 0, "son_url": "http://public.test:80/a", "istekler": ["http://public.test:80/a"]}:
            pass
        else:
            return False
        if fn("http://public.test:80/a!~", ["/b!~"], origin, max_hop=1)["son_url"] != "http://public.test:80/b!~":
            return False
        if fn("http://public.test:1/a", [], "http://public.test:1")["hop"] != 0:
            return False
        try:
            fn("http://public.test:80/a", ["/a", "/b", "/c", "/d"], origin)
            return False
        except ValueError:
            pass
        for baslangic, locations, allowed, limit in [
            (3, [], origin, 3),
            ("http://internal.test:80/a", [], origin, 3),
            ("http://public.test:80/a", ["//internal.test:80/canary"], origin, 3),
            ("http://public.test:80/a", ["/orta", "https://public.test:80/son"], origin, 3),
            ("http://public.test:80/a", ["http://user@public.test:80/x"], origin, 3),
            ("http://public.test:80/a", ["http://:80/x"], origin, 3),
            ("http://public.test:80/a", ["http://public.test/x"], origin, 3),
            ("http://public.test:80/a", ["http://public.test:0/x"], origin, 3),
            ("http://public_test:80/a", [], origin, 3),
            ("http://public.test:80/a", ["/x"], "http://public.test:80/", 3),
            ("http://public.test:80/a", ["/x"], "http://public.test:80/path", 3),
            ("http://public.test:80/a", ["/x"], "http://public.test:80?x=1", 3),
            ("http://public.test:80/a", ["/x"], origin, 0),
            ("http://public.test:80/a", [], origin, -1),
            ("http://public.test:80/a", [], origin, True),
            ("http://public.test:80/a", "/x", origin, 3),
            ("http://public.test:80/a", [None], origin, 3),
            ("http://public.test:80/a", ["/a b"], origin, 3),
            ("http://public.test:80/a", ["/a#x"], origin, 3),
            ("http://public.test:80/a", ["/a\x7fb"], origin, 3),
        ]:
            try:
                fn(baslangic, locations, allowed, limit)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(redirect_originleri), "göreli çözümleme, her hop origin kontrolü ve hop sınırı korunmalı")
def m_atla(baslangic, locationlar, izinli_origin, max_hop=3):
    from urllib.parse import urljoin
    sonuc = redirect_originleri(baslangic, [], izinli_origin, max_hop)
    current = baslangic
    for location in locationlar:
        current = urljoin(current, location)
        sonuc["istekler"].append(current)
    sonuc["hop"] = len(locationlar)
    sonuc["son_url"] = current
    return sonuc
def m_limit(baslangic, locationlar, izinli_origin, max_hop=3):
    return redirect_originleri(baslangic, locationlar, izinli_origin, max(max_hop, len(locationlar)))
def m_location(baslangic, locationlar, izinli_origin, max_hop=3):
    return redirect_originleri(baslangic, ["/sabit" for _ in locationlar], izinli_origin, max_hop)
for ad, mutant in [("redirect kontrollerini atlayan", m_atla), ("hop sınırını büyüten", m_limit), ("Location değerini yok sayan", m_location)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)

import copy
KAYITLAR = [
    {"vaka_id": "v1", "izinli_ip": "203.0.113.10", "cozumler": ["203.0.113.10", "203.0.113.10"], "baglanti_ip": "203.0.113.10"},
    {"vaka_id": "v2", "izinli_ip": "203.0.113.10", "cozumler": ["203.0.113.10", "127.0.0.1"], "baglanti_ip": "127.0.0.1"},
    {"vaka_id": "v3", "izinli_ip": "203.0.113.10", "cozumler": ["127.0.0.1"], "baglanti_ip": "203.0.113.10"},
    {"vaka_id": "v4", "izinli_ip": "203.0.113.10", "cozumler": ["203.0.113.10"], "baglanti_ip": "127.0.0.1"},
    {"vaka_id": "v5", "izinli_ip": "203.0.113.10", "cozumler": ["203.0.113.10", "127.0.0.1", "203.0.113.10"], "baglanti_ip": "203.0.113.10"},
    {"vaka_id": "v6", "izinli_ip": "203.0.113.10", "cozumler": ["127.0.0.1"], "baglanti_ip": "127.0.0.1"},
]
BEKLENEN = {"vaka": 6, "rebinding": ["v2", "v5"], "yetkisiz_dns": ["v2", "v3", "v5", "v6"], "socket_sapmasi": ["v3", "v4"], "temiz": ["v1"]}
def sozlesme(fn):
    try:
        once = copy.deepcopy(KAYITLAR)
        if fn(KAYITLAR) != BEKLENEN or KAYITLAR != once or fn(list(reversed(KAYITLAR))) != BEKLENEN:
            return False
        if fn([]) != {"vaka": 0, "rebinding": [], "yetkisiz_dns": [], "socket_sapmasi": [], "temiz": []}:
            return False
        for kayitlar in [
            None, {}, [None], KAYITLAR + [KAYITLAR[0]], [dict(KAYITLAR[0], ek=1)],
            [dict(KAYITLAR[0], vaka_id="")], [dict(KAYITLAR[0], izinli_ip="::1")],
            [dict(KAYITLAR[0], cozumler=[])], [dict(KAYITLAR[0], cozumler="203.0.113.10")],
            [dict(KAYITLAR[0], cozumler=["999.1.1.1"])], [dict(KAYITLAR[0], baglanti_ip=None)],
        ]:
            try:
                fn(kayitlar)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(dns_regresyonu), "rebinding, izinsiz DNS, socket sapması ve temizlik ayrımı korunmalı")
def m_rebinding(kayitlar):
    sonuc = dns_regresyonu(kayitlar)
    sonuc["rebinding"] = sorted(x["vaka_id"] for x in kayitlar if x["cozumler"][0] != x["cozumler"][-1])
    return sonuc
def m_dns(kayitlar):
    sonuc = dns_regresyonu(kayitlar)
    sonuc["yetkisiz_dns"] = sorted(x["vaka_id"] for x in kayitlar if x["cozumler"][-1] != x["izinli_ip"])
    return sonuc
def m_temiz(kayitlar):
    sonuc = dns_regresyonu(kayitlar)
    sonuc["temiz"] = sorted(x["vaka_id"] for x in kayitlar if x["baglanti_ip"] == x["izinli_ip"])
    return sonuc
for ad, mutant in [("ara DNS değişimini kaçıran", m_rebinding), ("yalnız son DNS cevabını denetleyen", m_dns), ("temizliği yalnız socket'e indirgeyen", m_temiz)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)

from sandbox import ai_gercek_ai_saldiri_22 as deney
import tempfile
from pathlib import Path
if not ok(not ai_lab.kod_denetimi(src,('dns_ref',)), 'laboratuvar/gerçek ölçüm yamalanmamalı'):stop()
with tempfile.TemporaryDirectory(prefix='pafta_origin22_') as tmp:
    p=Path(tmp)/'vaka.json';p.write_text(deney.ORNEK.read_text(encoding='utf-8'),encoding='utf-8')
    r=deney.deney(url_origin,redirect_originleri,dns_regresyonu,p,Path(tmp)/'deney')
    for k,v in r['kontroller'].items():ok(v,'gerçek deney: '+k)
    accepted=all(r['kontroller'].values());ai_lab.kanit_yaz('saldiri-22-origin',dict(r,kabul=accepted));ok(accepted,'origin/Location kapısı gerçekHTTPönünde ve gerçekDNSpeer raporu; saldırıbaşarısı şart değil')

```

```solution
import ai_lab
def url_origin(url):
    from urllib.parse import urlsplit
    if not isinstance(url, str) or not url or any(ord(c) < 33 or ord(c) > 126 for c in url):
        raise ValueError("URL karakterleri geçersiz")
    if "\\" in url or "#" in url:
        raise ValueError("belirsiz URL")
    try:
        u = urlsplit(url)
        if u.scheme != "http" or not u.hostname or u.username is not None or u.password is not None:
            raise ValueError("URL origin'i geçersiz")
        host = u.hostname.lower().rstrip(".")
        port = u.port
    except (TypeError, ValueError) as exc:
        raise ValueError("URL ayrıştırılamadı") from exc
    if not host or not all(c.isascii() and (c.isalnum() or c in ".-") for c in host):
        raise ValueError("host geçersiz")
    if port is None or port < 1:
        raise ValueError("açık port gerekli")
    return {"origin": "http://" + host + ":" + str(port), "host": host, "port": port}

def redirect_originleri(baslangic, locationlar, izinli_origin, max_hop=3):
    from urllib.parse import urlsplit, urljoin
    if type(max_hop) is not int or max_hop < 0 or not isinstance(locationlar, list):
        raise ValueError("hop veya Location listesi geçersiz")
    if len(locationlar) > max_hop:
        raise ValueError("hop sınırı aşıldı")
    def origin_denetle(url):
        import re
        from urllib.parse import urlsplit
        if not isinstance(url, str) or not url or any(ord(c) < 33 or ord(c) > 126 for c in url) or "\\" in url or "#" in url:
            raise ValueError("URL geçersiz")
        try:
            u = urlsplit(url)
            host = u.hostname.lower().rstrip(".") if u.hostname else ""
            origin = "http://" + host + ":" + str(u.port)
            if u.scheme != "http":
                raise ValueError("şema geçersiz")
            if not host:
                raise ValueError("host gerekli")
            if u.username is not None:
                raise ValueError("kullanıcı bilgisi geçersiz")
            if u.password is not None:
                raise ValueError("parola geçersiz")
            if u.port is None:
                raise ValueError("port gerekli")
            if u.port < 1:
                raise ValueError("port geçersiz")
            if not re.fullmatch(r"[a-z0-9.-]+", host):
                raise ValueError("host geçersiz")
            return origin
        except (TypeError, ValueError) as exc:
            raise ValueError("URL ayrıştırılamadı") from exc
    if origin_denetle(izinli_origin) != izinli_origin:
        raise ValueError("izinli origin kanonik değil")
    if urlsplit(izinli_origin).path:
        raise ValueError("izinli origin path içeremez")
    if urlsplit(izinli_origin).query:
        raise ValueError("izinli origin query içeremez")
    current = baslangic
    if origin_denetle(current) != izinli_origin:
        raise ValueError("başlangıç origin'i izinsiz")
    istekler = [current]
    for location in locationlar:
        if not isinstance(location, str):
            raise ValueError("Location string olmalı")
        current = urljoin(current, location)
        if origin_denetle(current) != izinli_origin:
            raise ValueError("redirect origin'i izinsiz")
        istekler.append(current)
    return {"hop": len(locationlar), "son_url": current, "istekler": istekler}

def dns_regresyonu(kayitlar):
    import ipaddress
    if not isinstance(kayitlar, list):
        raise ValueError("kayıtlar liste olmalı")
    def ipv4(deger):
        if not isinstance(deger, str):
            raise ValueError("IP string olmalı")
        try:
            return str(ipaddress.IPv4Address(deger))
        except ipaddress.AddressValueError as exc:
            raise ValueError("IPv4 geçersiz") from exc
    sonuc = {"vaka": 0, "rebinding": [], "yetkisiz_dns": [], "socket_sapmasi": [], "temiz": []}
    vakalar = set()
    for kayit in kayitlar:
        if not isinstance(kayit, dict) or set(kayit) != {"vaka_id", "izinli_ip", "cozumler", "baglanti_ip"}:
            raise ValueError("kayıt şeması geçersiz")
        if not isinstance(kayit["vaka_id"], str) or not kayit["vaka_id"] or kayit["vaka_id"] in vakalar:
            raise ValueError("vaka kimliği geçersiz")
        izinli = ipv4(kayit["izinli_ip"])
        socket = ipv4(kayit["baglanti_ip"])
        if not isinstance(kayit["cozumler"], list) or not kayit["cozumler"]:
            raise ValueError("DNS cevabı listesi geçersiz")
        cozumler = [ipv4(x) for x in kayit["cozumler"]]
        vakalar.add(kayit["vaka_id"])
        rebinding = len(set(cozumler)) > 1
        yetkisiz = any(x != izinli for x in cozumler)
        sapma = socket != cozumler[-1]
        if rebinding:
            sonuc["rebinding"].append(kayit["vaka_id"])
        if yetkisiz:
            sonuc["yetkisiz_dns"].append(kayit["vaka_id"])
        if sapma:
            sonuc["socket_sapmasi"].append(kayit["vaka_id"])
        if not rebinding and not yetkisiz and not sapma:
            sonuc["temiz"].append(kayit["vaka_id"])
    sonuc["vaka"] = len(vakalar)
    for alan in ("rebinding", "yetkisiz_dns", "socket_sapmasi", "temiz"):
        sonuc[alan].sort()
    return sonuc
if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_saldiri_22 as deney
    deney.goster(url_origin,redirect_originleri,dns_regresyonu)

```

```hint
İlk URLyi doğrulamak yetmez; her Location yeni adaydır. Host,şema ve port beraber denetlenmeli. DNSraporunda çözüm cevabı ile gerçek socketpeer farkını ayrı ölç; negatif sentetik DNSkaydını canlı çıktı gibi etiketleme.
```
:::
