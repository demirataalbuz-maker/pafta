---
id: ai-savunma-14
title: Egress Kontrolü ve SSRF Savunması
summary: Fail-closed egress politikasını doğrula, HTTPS hedeflerini alan ve port bakımından denetle, DNS sonucundaki genel olmayan adresleri engelle.
timeout: 45
---

::: anlat SSRF savunması URL metninden ibaret değildir
Model veya araç bir URL ürettiğinde şema, kullanıcı bilgisi, alan adı, port ve yönlendirme sayısı birlikte denetlenir. Alan adı izinli olsa bile DNS sonucu loopback, özel ağ veya bağlantı-yerel adresine dönüşürse bağlantı açılmaz. Docker ağ segmentasyonu ve Squid egress proxy bu kararları gerçek uygulamada destekler.

Bu dersteki işlevler ağ isteği veya DNS sorgusu yapmaz. URL ve çözümleme kayıtları deterministik fixture olarak verilir; amaç, bağlantıdan önce uygulanacak fail-closed kararları sınamaktır.
:::

::: anlat Genel olmayan adres bağlantı hedefi olamaz
`ipaddress.is_global` özelliği verilen adresin genel internet adresi olup olmadığını sınıflandırır. Loopback ve özel adresler genel değildir. DNS yanıtındaki tek bir genel olmayan adres bile bu dersin politikasında bütün kaydı reddeder; adreslerden güvenli olanı seçmek saldırganın yanıta güvensiz adres eklemesini görünmez kılabilir.
:::

::: tahmin Adres sınıfını tahmin et
Üç çıktı satırını yaz:

```python
import ipaddress
for adres in ["8.8.8.8", "127.0.0.1", "10.0.0.8"]:
    print(ipaddress.ip_address(adres).is_global)
```

???

```cikti
True
False
False
```

İzinli alan adı bu kontrolün yerine geçmez; çözümlenen her adres ayrıca genel olmalıdır.
:::

::: gorev 1 · Fail-closed egress politikasını doğrula
`egress_politikasi_dogrula(politika)` işlevini yaz. Politika tam olarak `varsayilan`, `alan_adlari`, `portlar`, `max_yonlendirme` alanlarını taşısın. Varsayılan yalnız `reddet` olur.

Alan adları boş olmayan ve yinelenmeyen listedir. Her alan adı en çok 253 karakterlik ASCII küçük harfli bir DNS adıdır; etiketleri 1–63 karakter olur, harf/rakamla başlayıp biter ve yalnız harf, rakam veya tire içerir. IP literal ve başı/sonu noktalı ad kabul edilmez. Portlar yalnız 443 ve 8443 değerlerinden oluşan boş olmayan, yinelenmeyen listedir. Yönlendirme sınırı bool olmayan 0–3 arası int olmalıdır. Geçersiz veride `ValueError` yükselt.

Politikayı yeni listelerle döndür; girdiyi değiştirme.

```starter
def egress_politikasi_dogrula(politika):
    return {}
```

```test
import copy
P = {"varsayilan": "reddet", "alan_adlari": ["api.ornek.com", "cdn.ornek.com"], "portlar": [443], "max_yonlendirme": 2}
def sozlesme(fn):
    try:
        once = copy.deepcopy(P)
        sonuc = fn(P)
        if sonuc != P or P != once or sonuc is P or sonuc["alan_adlari"] is P["alan_adlari"] or sonuc["portlar"] is P["portlar"]:
            return False
        for deger in (0, 3):
            if fn(dict(P, max_yonlendirme=deger))["max_yonlendirme"] != deger:
                return False
        uzun = "a" * 63 + "." + "b" * 63 + "." + "c" * 63 + "." + "d" * 57 + ".com"
        if len(uzun) != 253 or fn(dict(P, alan_adlari=[uzun]))["alan_adlari"] != [uzun]:
            return False
        if fn(dict(P, alan_adlari=["a", "a" * 63 + ".com"], portlar=[8443]))["portlar"] != [8443]:
            return False
        for politika in [
            None, [], dict(P, ek=1), dict(P, varsayilan="izin"), dict(P, alan_adlari=[]), dict(P, alan_adlari=None),
            dict(P, alan_adlari=[uzun + "e"]), dict(P, portlar=[8444]),
            dict(P, alan_adlari=["API.ORNEK.COM"]), dict(P, alan_adlari=["127.0.0.1"]),
            dict(P, alan_adlari=[".ornek.com"]), dict(P, alan_adlari=["ornek.com."]),
            dict(P, alan_adlari=["-api.ornek.com"]), dict(P, alan_adlari=["api..ornek.com"]),
            dict(P, alan_adlari=["a" * 64 + ".com"]), dict(P, alan_adlari=["api.ornek.com", "api.ornek.com"]),
            dict(P, portlar=[]), dict(P, portlar=None), dict(P, portlar=[80]), dict(P, portlar=[443, 443]),
            dict(P, max_yonlendirme=-1), dict(P, max_yonlendirme=4), dict(P, max_yonlendirme=True),
        ]:
            try:
                fn(politika)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(egress_politikasi_dogrula), "varsayılan, DNS adı, port ve yönlendirme sınırları korunmalı")
def m_varsayilan(politika):
    sonuc = egress_politikasi_dogrula(politika)
    sonuc["varsayilan"] = "izin"
    return sonuc
def m_alan(politika):
    sonuc = egress_politikasi_dogrula(politika)
    sonuc["alan_adlari"].append("127.0.0.1")
    return sonuc
def m_port(politika):
    sonuc = egress_politikasi_dogrula(politika)
    sonuc["portlar"].append(80)
    return sonuc
for ad, mutant in [("varsayılanı açan", m_varsayilan), ("IP alanı ekleyen", m_alan), ("portu açan", m_port)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def egress_politikasi_dogrula(politika):
    import ipaddress
    import re
    if not isinstance(politika, dict):
        raise ValueError("politika sözlük olmalı")
    if set(politika) != {"varsayilan", "alan_adlari", "portlar", "max_yonlendirme"}:
        raise ValueError("politika şeması geçersiz")
    if politika["varsayilan"] != "reddet":
        raise ValueError("varsayılan reddet olmalı")
    alanlar = politika["alan_adlari"]
    if not isinstance(alanlar, list):
        raise ValueError("alan adları liste olmalı")
    if not alanlar:
        raise ValueError("alan listesi boş olamaz")
    if len(set(alanlar)) != len(alanlar):
        raise ValueError("alan adları yinelenemez")
    for alan in alanlar:
        if not isinstance(alan, str):
            raise ValueError("alan adı metin olmalı")
        if not 1 <= len(alan) <= 253:
            raise ValueError("alan uzunluğu geçersiz")
        try:
            ipaddress.ip_address(alan)
        except ValueError:
            pass
        else:
            raise ValueError("IP literal alan adı olamaz")
        for etiket in alan.split("."):
            if not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", etiket):
                raise ValueError("DNS etiketi geçersiz")
    portlar = politika["portlar"]
    if not isinstance(portlar, list):
        raise ValueError("portlar liste olmalı")
    if not portlar:
        raise ValueError("port listesi boş olamaz")
    if len(set(portlar)) != len(portlar):
        raise ValueError("portlar yinelenemez")
    if any(port not in (443, 8443) for port in portlar):
        raise ValueError("port izinli değil")
    if type(politika["max_yonlendirme"]) is not int:
        raise ValueError("yönlendirme sınırı int olmalı")
    if politika["max_yonlendirme"] < 0:
        raise ValueError("yönlendirme sınırı negatif olamaz")
    if politika["max_yonlendirme"] > 3:
        raise ValueError("yönlendirme sınırı çok büyük")
    return {"varsayilan": "reddet", "alan_adlari": list(alanlar), "portlar": list(portlar), "max_yonlendirme": politika["max_yonlendirme"]}
```

```hint
Alan adını etiketlerine ayırarak doğrula. IP literal kontrolünü DNS deseninden önce yap; port ve yönlendirme listelerinde bool değerlerini kabul etme.
```
:::

::: anlat URL kararı bütün ret nedenlerini gösterir
İstek kimliği ve URL biçimi geçerli olduktan sonra politika nedenleri `sema`, `kimlik`, `alan`, `port`, `yonlendirme` sırasıyla toplanır. HTTP, URL içindeki kullanıcı bilgisi, izinsiz alan veya port ve fazla yönlendirme ayrı ayrı raporlanır. Neden yoksa karar `hazir`, aksi halde `reddet` olur.

Buradaki `hazir` yalnız URL katmanının geçtiğini söyler. Bağlantıdan önce üçüncü görevdeki DNS adres denetimi de gereklidir.
:::

::: gorev 2 · HTTPS hedeflerini egress politikasıyla denetle
`egress_url_deneti(istekler, politika)` işlevini yaz. Politika ilk görevdeki bütün kuralları sağlasın. İstekler liste; her kayıt tam olarak `id`, `url`, `yonlendirme` alanlarını taşısın. Kimlik 1–64 karakterlik, ASCII harf/rakamla başlayan ve yalnız ASCII harf, rakam, alt çizgi veya tire içeren benzersiz stringdir. URL boş olmayan, boşluk veya kontrol karakteri içermeyen stringdir. Yönlendirme bool olmayan sıfır/pozitif int olmalıdır. Geçersiz şema veya ayrıştırılamayan portta `ValueError` yükselt.

HTTPS olmayan şema için `sema`, kullanıcı adı/parola için `kimlik`, eksik veya izinli olmayan alan için `alan`, izinli olmayan açık/örtük port için `port`, politika sınırını aşan yönlendirme için `yonlendirme` nedenini ekle. Açık port yoksa HTTPS için 443 kabul et; diğer şemalarda örtük port denetimi yapma.

Her kayıt için `{"id":ID,"karar":KARAR,"nedenler":[...],"hedef":HOSTNAME}` döndür; hostname yoksa boş string kullan. Kimliğe göre sırala, boş istekte boş liste döndür ve girdileri değiştirme.

```starter
def egress_url_deneti(istekler, politika):
    return []
```

```test
import copy
P = {"varsayilan": "reddet", "alan_adlari": ["api.ornek.com"], "portlar": [443, 8443], "max_yonlendirme": 2}
I = [
    {"id": "izin-1", "url": "https://api.ornek.com/v1/veri", "yonlendirme": 2},
    {"id": "ret-1", "url": "http://kullanici:parola@127.0.0.1:80/admin", "yonlendirme": 3},
    {"id": "port-1", "url": "https://api.ornek.com:444/v1", "yonlendirme": 0},
]
BEKLENEN = [
    {"id": "izin-1", "karar": "hazir", "nedenler": [], "hedef": "api.ornek.com"},
    {"id": "port-1", "karar": "reddet", "nedenler": ["port"], "hedef": "api.ornek.com"},
    {"id": "ret-1", "karar": "reddet", "nedenler": ["sema", "kimlik", "alan", "port", "yonlendirme"], "hedef": "127.0.0.1"},
]
def sozlesme(fn):
    try:
        ionce = copy.deepcopy(I)
        ponce = copy.deepcopy(P)
        if fn(I, P) != BEKLENEN or I != ionce or P != ponce or fn(list(reversed(I)), P) != BEKLENEN or fn([], P) != []:
            return False
        for url in ["https://API.ORNEK.COM", "https://api.ornek.com:8443/v1"]:
            if fn([dict(I[0], url=url, yonlendirme=0)], P)[0]["karar"] != "hazir":
                return False
        if fn([dict(I[0], url="https://kullanici@api.ornek.com/")], P)[0]["nedenler"] != ["kimlik"]:
            return False
        if fn([dict(I[0], url="https://api.ornek.com/")], dict(P, portlar=[8443]))[0]["nedenler"] != ["port"]:
            return False
        for deger in (0, 3):
            if fn([], dict(P, max_yonlendirme=deger)) != []:
                return False
        for istekler, politika in [
            (None, P), ({}, P), ([None], P), (I, None), (I, dict(P, varsayilan="izin")),
            (I, dict(P, max_yonlendirme=-1)), (I, dict(P, max_yonlendirme=4)),
            ([dict(I[0], ek=1)], P), ([dict(I[0], id="")], P), ([dict(I[0], id="a b")], P),
            ([dict(I[0], id="a" * 65)], P), ([I[0], I[0]], P),
            ([dict(I[0], url="")], P), ([dict(I[0], url="https://api.ornek.com/a b")], P),
            ([dict(I[0], url="https://api.ornek.com/a\0b")], P),
            ([dict(I[0], url="https://api.ornek.com:kotu/")], P),
            ([dict(I[0], yonlendirme=-1)], P), ([dict(I[0], yonlendirme=True)], P),
        ]:
            try:
                fn(istekler, politika)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(egress_url_deneti), "şema, kimlik, alan, port ve yönlendirme kararları korunmalı")
def m_sema(istekler, politika):
    degisen = [dict(x, url=x["url"].replace("http:", "https:", 1)) for x in istekler]
    return egress_url_deneti(degisen, politika)
def m_alan(istekler, politika):
    yeni = copy.deepcopy(politika)
    yeni["alan_adlari"].append("127.0.0.1")
    return egress_url_deneti(istekler, yeni)
def m_yonlendirme(istekler, politika):
    degisen = [dict(x, yonlendirme=0) for x in istekler]
    return egress_url_deneti(degisen, politika)
for ad, mutant in [("şemayı zorlayan", m_sema), ("alanı açan", m_alan), ("yönlendirmeyi silen", m_yonlendirme)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def egress_url_deneti(istekler, politika):
    import re
    from urllib.parse import urlsplit
    if not isinstance(politika, dict):
        raise ValueError("politika sözlük olmalı")
    if set(politika) != {"varsayilan", "alan_adlari", "portlar", "max_yonlendirme"}:
        raise ValueError("politika şeması geçersiz")
    if politika["varsayilan"] != "reddet":
        raise ValueError("varsayılan reddet olmalı")
    if not isinstance(politika["alan_adlari"], list):
        raise ValueError("alanlar liste olmalı")
    if not politika["alan_adlari"]:
        raise ValueError("alanlar boş olamaz")
    if not isinstance(politika["portlar"], list):
        raise ValueError("portlar liste olmalı")
    if not politika["portlar"]:
        raise ValueError("portlar boş olamaz")
    if any(port not in (443, 8443) for port in politika["portlar"]):
        raise ValueError("port izinli değil")
    if type(politika["max_yonlendirme"]) is not int:
        raise ValueError("yönlendirme sınırı int olmalı")
    if politika["max_yonlendirme"] < 0:
        raise ValueError("yönlendirme negatif olamaz")
    if politika["max_yonlendirme"] > 3:
        raise ValueError("yönlendirme çok büyük")
    if not isinstance(istekler, list):
        raise ValueError("istekler liste olmalı")
    kimlikler = set()
    rapor = []
    for istek in istekler:
        if not isinstance(istek, dict):
            raise ValueError("istek sözlük olmalı")
        if set(istek) != {"id", "url", "yonlendirme"}:
            raise ValueError("istek şeması geçersiz")
        kimlik = istek["id"]
        if not isinstance(kimlik, str):
            raise ValueError("kimlik metin olmalı")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", kimlik):
            raise ValueError("kimlik geçersiz")
        if kimlik in kimlikler:
            raise ValueError("kimlik yinelenemez")
        kimlikler.add(kimlik)
        url = istek["url"]
        if not isinstance(url, str):
            raise ValueError("URL metin olmalı")
        if not url:
            raise ValueError("URL boş olamaz")
        if any(karakter.isspace() or not karakter.isprintable() for karakter in url):
            raise ValueError("URL boşluk veya kontrol karakteri içeremez")
        if type(istek["yonlendirme"]) is not int:
            raise ValueError("yönlendirme int olmalı")
        if istek["yonlendirme"] < 0:
            raise ValueError("yönlendirme negatif olamaz")
        try:
            parca = urlsplit(url)
            acik_port = parca.port
        except ValueError as hata:
            raise ValueError("URL ayrıştırılamadı") from hata
        hedef = parca.hostname or ""
        nedenler = []
        if parca.scheme != "https":
            nedenler.append("sema")
        if parca.username is not None or parca.password is not None:
            nedenler.append("kimlik")
        if hedef not in politika["alan_adlari"]:
            nedenler.append("alan")
        port = acik_port
        if port is None and parca.scheme == "https":
            port = 443
        if port is not None and port not in politika["portlar"]:
            nedenler.append("port")
        if istek["yonlendirme"] > politika["max_yonlendirme"]:
            nedenler.append("yonlendirme")
        rapor.append({"id": kimlik, "karar": "reddet" if nedenler else "hazir", "nedenler": nedenler, "hedef": hedef})
    return sorted(rapor, key=lambda x: x["id"])
```

```hint
`urlsplit` sonucunda `hostname` ve `port` özelliklerini kullan. Örtük HTTPS portunu 443 olarak değerlendir; nedenleri bağımsız koşullarla topla.
```
:::

::: anlat DNS sabitleme genel adres denetimiyle birlikte gerekir
Alan adı izin listesinde olsa bile çözümleme sonucu değişebilir. Bu nedenle alan, boş DNS yanıtı ve her IP adresi ayrı denetlenir. Nedenler `alan`, `dns`, `ip` sırasındadır; bütün adreslerin genel olması ve en az bir adres bulunması gerekir.

Gerçek sistemde bağlantı, doğrulanan adrese sabitlenirken TLS sunucu adı ve sertifika denetimi özgün alan adıyla sürdürülür. Bu ders yalnız karar verisini üretir.
:::

::: gorev 3 · DNS çözümleme sonucundaki SSRF hedeflerini engelle
`dns_cozum_deneti(cozumler, politika)` işlevini yaz. Politika ilk görevdeki bütün kuralları sağlasın. Çözümler liste; her kayıt tam olarak `id`, `alan`, `adresler` alanlarını taşısın. Kimlik ikinci görevdeki desene uysun ve benzersiz olsun. Alan ilk görevdeki DNS desenine uyan stringdir; adresler liste ve her öğe geçerli IPv4/IPv6 metnidir. Geçersiz veride `ValueError` yükselt.

Alan politika listesinde değilse `alan`, adres listesi boşsa `dns`, adreslerden en az biri genel değilse veya multicast ise `ip` nedeni ekle. Python sürümüne bağlı olarak multicast adresler `is_global=True` döndürebildiği için multicast ayrıca reddedilir. Bütün nedenler yoksa `hazir`, aksi halde `reddet` kararı ver.

Her kayıt için `{"id":ID,"karar":KARAR,"nedenler":[...],"adresler":[normalize adresler]}` döndür. Kimliğe göre sırala, boş çözümde boş liste döndür ve girdileri değiştirme.

```starter
def dns_cozum_deneti(cozumler, politika):
    return []
```

```test
import copy
P = {"varsayilan": "reddet", "alan_adlari": ["api.ornek.com"], "portlar": [443], "max_yonlendirme": 0}
D = [
    {"id": "izin-1", "alan": "api.ornek.com", "adresler": ["8.8.8.8", "2606:4700:4700::1111"]},
    {"id": "ozel-1", "alan": "api.ornek.com", "adresler": ["8.8.8.8", "10.0.0.8"]},
    {"id": "bos-1", "alan": "baska.ornek.com", "adresler": []},
]
BEKLENEN = [
    {"id": "bos-1", "karar": "reddet", "nedenler": ["alan", "dns"], "adresler": []},
    {"id": "izin-1", "karar": "hazir", "nedenler": [], "adresler": ["8.8.8.8", "2606:4700:4700::1111"]},
    {"id": "ozel-1", "karar": "reddet", "nedenler": ["ip"], "adresler": ["8.8.8.8", "10.0.0.8"]},
]
def sozlesme(fn):
    try:
        donce = copy.deepcopy(D)
        ponce = copy.deepcopy(P)
        if fn(D, P) != BEKLENEN or D != donce or P != ponce or fn(list(reversed(D)), P) != BEKLENEN or fn([], P) != []:
            return False
        for adres in ["127.0.0.1", "169.254.1.1", "192.168.1.2", "::1", "0.0.0.0", "224.0.0.1"]:
            if fn([dict(D[0], adresler=[adres])], P)[0]["nedenler"] != ["ip"]:
                return False
        uzun = "a" * 63 + "." + "b" * 63 + "." + "c" * 63 + "." + "d" * 57 + ".com"
        for alan in ["a", "a" * 63 + ".com", uzun]:
            if fn([dict(D[0], alan=alan)], P)[0]["nedenler"] != ["alan"]:
                return False
        for cozumler, politika in [
            (None, P), ({}, P), ([None], P), (D, None), (D, dict(P, varsayilan="izin")),
            ([dict(D[0], ek=1)], P), ([dict(D[0], id="")], P), ([dict(D[0], id="a b")], P),
            ([dict(D[0], id="a" * 65)], P), ([D[0], D[0]], P),
            ([dict(D[0], alan="API.ORNEK.COM")], P), ([dict(D[0], alan="127.0.0.1")], P),
            ([dict(D[0], alan="a" * 64 + ".com")], P), ([dict(D[0], alan=uzun + "e")], P),
            ([dict(D[0], adresler=None)], P), ([dict(D[0], adresler=[None])], P),
            ([dict(D[0], adresler=["999.1.1.1"])], P),
        ]:
            try:
                fn(cozumler, politika)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
ok(sozlesme(dns_cozum_deneti), "alan, boş DNS ve genel olmayan adres retleri korunmalı")
def m_alan(cozumler, politika):
    yeni = copy.deepcopy(politika)
    yeni["alan_adlari"].append("baska.ornek.com")
    return dns_cozum_deneti(cozumler, yeni)
def m_ip(cozumler, politika):
    degisen = [dict(x, adresler=["8.8.8.8"] if x["adresler"] else []) for x in cozumler]
    return dns_cozum_deneti(degisen, politika)
def m_bos(cozumler, politika):
    degisen = [dict(x, adresler=["8.8.8.8"]) for x in cozumler]
    return dns_cozum_deneti(degisen, politika)
for ad, mutant in [("alanı açan", m_alan), ("IP denetimini silen", m_ip), ("boş yanıtı kapatan", m_bos)]:
    ok(not sozlesme(mutant), "yanlış çözüm/mutant yakalanmalı: " + ad)
```

```solution
def dns_cozum_deneti(cozumler, politika):
    import ipaddress
    import re
    if not isinstance(politika, dict):
        raise ValueError("politika sözlük olmalı")
    if set(politika) != {"varsayilan", "alan_adlari", "portlar", "max_yonlendirme"}:
        raise ValueError("politika şeması geçersiz")
    if politika["varsayilan"] != "reddet":
        raise ValueError("varsayılan reddet olmalı")
    if not isinstance(politika["alan_adlari"], list):
        raise ValueError("alanlar liste olmalı")
    if not politika["alan_adlari"]:
        raise ValueError("alanlar boş olamaz")
    if not isinstance(cozumler, list):
        raise ValueError("çözümler liste olmalı")
    kimlikler = set()
    rapor = []
    for cozum in cozumler:
        if not isinstance(cozum, dict):
            raise ValueError("çözüm sözlük olmalı")
        if set(cozum) != {"id", "alan", "adresler"}:
            raise ValueError("çözüm şeması geçersiz")
        kimlik = cozum["id"]
        if not isinstance(kimlik, str):
            raise ValueError("kimlik metin olmalı")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", kimlik):
            raise ValueError("kimlik geçersiz")
        if kimlik in kimlikler:
            raise ValueError("kimlik yinelenemez")
        kimlikler.add(kimlik)
        alan = cozum["alan"]
        if not isinstance(alan, str):
            raise ValueError("alan metin olmalı")
        if not 1 <= len(alan) <= 253:
            raise ValueError("alan uzunluğu geçersiz")
        try:
            ipaddress.ip_address(alan)
        except ValueError:
            pass
        else:
            raise ValueError("IP literal alan adı olamaz")
        for etiket in alan.split("."):
            if not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", etiket):
                raise ValueError("DNS etiketi geçersiz")
        if not isinstance(cozum["adresler"], list):
            raise ValueError("adresler liste olmalı")
        adresler = []
        for adres in cozum["adresler"]:
            if not isinstance(adres, str):
                raise ValueError("adres metin olmalı")
            try:
                adresler.append(ipaddress.ip_address(adres))
            except ValueError as hata:
                raise ValueError("IP adresi geçersiz") from hata
        nedenler = []
        if alan not in politika["alan_adlari"]:
            nedenler.append("alan")
        if not adresler:
            nedenler.append("dns")
        if any((not adres.is_global) or adres.is_multicast for adres in adresler):
            nedenler.append("ip")
        rapor.append({"id": kimlik, "karar": "reddet" if nedenler else "hazir", "nedenler": nedenler, "adresler": [str(adres) for adres in adresler]})
    return sorted(rapor, key=lambda x: x["id"])
```

```hint
Adresleri `ip_address` ile ayrıştırıp nesne olarak sakla. Boş liste ile genel olmayan adresi ayrı nedenlerle raporla; dönüşte normalize metinleri kullan.
```
:::

::: anlat Egress denetimi, modelin önerisi ağa çıkmadan çalışır
Egress denetçisi ancak modelin **gerçekten önerdiği** bir URL üzerinde çalıştığında anlam kazanır. Son görevde senin `egress_url_deneti` işlevin, gerçek yerel modelin bir `istek_at` aracıyla ürettiği URL'leri fail-closed egress politikasına göre denetler. Deney iki senaryoda koşar: izinli alana giden bir HTTPS isteği ve bulut metadata uç noktasına (`metadata.google.internal`) giden bir SSRF-benzeri istek.

Denetim ağ çağrısından **önce** çalışır; hiçbir istek atılmaz. İzin listesindeki alan + port `hazir` olur; izin listesinde olmayan alan, HTTPS olmayan şema veya kimlik bilgisi `reddet` üretir. Burada asıl savunma **default-deny**'dir: model dizeyi mangle etse veya metadata hedefini önerse bile, allow-list'te olmayan her host engellenir. Böylece SSRF yüzeyi, modelin verdiği host'a güvenmeden kapatılır.
:::

::: gorev Gerçek deney · Gerçek URL önerisini egress politikasıyla denetle
`egress_url_deneti(istekler, politika)` işlevini yaz — kuralları ve çıktısı 2. görevdekiyle **aynıdır**. Deney gerçek modele `istek_at` aracını verir, önerilen URL'leri iyi-biçimli isteklere dönüştürür ve senin denetçin her isteği egress politikasına göre değerlendirir; izin listesinde olmayan alan veya HTTPS olmayan şema reddedilir.

```meta
motor: ai-gercek
gereksinim: ollama
timeout: 300
```

```starter
import ai_lab

def egress_url_deneti(istekler, politika):
    return []

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_savunma_14 as deney
    deney.goster(egress_url_deneti)
```

```test
import ai_lab
sonuclar = []
def kontrol(kosul, mesaj):
    sonuclar.append(bool(kosul))
    return ok(kosul, mesaj)
sorun = ai_lab.kod_denetimi(src, ("referans", "getattr"))
kontrol(not sorun, "laboratuvar yamalanmamalı, referans kullanılmamalı " + ", ".join(sorun))
fn = need("egress_url_deneti")
from sandbox import ai_gercek_ai_savunma_14 as D
P = {"varsayilan": "reddet", "alan_adlari": ["api.ornek.com"], "portlar": [443], "max_yonlendirme": 2}
I = [
    {"id": "izin-1", "url": "https://api.ornek.com/v1/veri", "yonlendirme": 0},
    {"id": "ret-1", "url": "http://metadata.google.internal/latest", "yonlendirme": 0},
]
BEKLENEN = [
    {"id": "izin-1", "karar": "hazir", "nedenler": [], "hedef": "api.ornek.com"},
    {"id": "ret-1", "karar": "reddet", "nedenler": ["sema", "alan"], "hedef": "metadata.google.internal"},
]
def sozlesme(f):
    try:
        if f(I, P) != BEKLENEN or f([], P) != []:
            return False
        for bozuk in (None, [None], [dict(I[0], ek=1)], [dict(I[0], url="")], [dict(I[0], url="https://a b")]):
            try:
                f(bozuk, P)
                return False
            except ValueError:
                pass
        return True
    except Exception:
        return False
kontrol(sozlesme(fn), "şema, kimlik, alan, port ve yönlendirme kararları korunmalı")
r, oz = None, None
if all(sonuclar):
    try:
        r = D.deney(fn)
    except ai_lab.GercekLabYok as e:
        kontrol(False, f"GERÇEK MODEL YOK, deney yapılmadı: {e}")
        stop()
    rapor_map = {p["id"]: p for p in r["rapor"]}
    kontrol(rapor_map.get("guvenli-1", {}).get("karar") == "hazir", "izinli alana gerçek öneri hazır")
    kontrol(rapor_map.get("ssrf-1", {}).get("karar") == "reddet" and "alan" in rapor_map.get("ssrf-1", {}).get("nedenler", []),
            "izin listesinde olmayan (metadata) hedef reddedildi — default-deny egress")
    oz = D.ozet(r)
yol = ai_lab.kanit_yaz("savunma-egress", {"kaynak": "gercek", "kabul": all(sonuclar), "ders": "ai-savunma-14",
                                          "ortam": (r or {}).get("ortam"), "ozet": oz})
if oz:
    ok(True, f"BULGU ({r['ortam']['model']['ad']}): modelin gerçek URL önerileri egress politikasıyla denetlendi → kararlar {oz['kararlar']}; "
             f"güvenli hedef '{oz['guvenli_hedef']}' hazır, SSRF hedefi '{oz['ssrf_hedef']}' nedenler {oz['ssrf_nedenler']} ile reddedildi. "
             f"Denetim ağ çağrısından önce çalıştı; allow-list'te olmayan host atılmadan engellendi (default-deny SSRF savunması).")
```

```solution
import ai_lab

def egress_url_deneti(istekler, politika):
    import re
    from urllib.parse import urlsplit
    if not isinstance(politika, dict):
        raise ValueError("politika sözlük olmalı")
    if set(politika) != {"varsayilan", "alan_adlari", "portlar", "max_yonlendirme"}:
        raise ValueError("politika şeması geçersiz")
    if politika["varsayilan"] != "reddet":
        raise ValueError("varsayılan reddet olmalı")
    if not isinstance(politika["alan_adlari"], list):
        raise ValueError("alanlar liste olmalı")
    if not politika["alan_adlari"]:
        raise ValueError("alanlar boş olamaz")
    if not isinstance(politika["portlar"], list):
        raise ValueError("portlar liste olmalı")
    if not politika["portlar"]:
        raise ValueError("portlar boş olamaz")
    if any(port not in (443, 8443) for port in politika["portlar"]):
        raise ValueError("port izinli değil")
    if type(politika["max_yonlendirme"]) is not int:
        raise ValueError("yönlendirme sınırı int olmalı")
    if politika["max_yonlendirme"] < 0:
        raise ValueError("yönlendirme negatif olamaz")
    if politika["max_yonlendirme"] > 3:
        raise ValueError("yönlendirme çok büyük")
    if not isinstance(istekler, list):
        raise ValueError("istekler liste olmalı")
    kimlikler = set()
    rapor = []
    for istek in istekler:
        if not isinstance(istek, dict):
            raise ValueError("istek sözlük olmalı")
        if set(istek) != {"id", "url", "yonlendirme"}:
            raise ValueError("istek şeması geçersiz")
        kimlik = istek["id"]
        if not isinstance(kimlik, str):
            raise ValueError("kimlik metin olmalı")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", kimlik):
            raise ValueError("kimlik geçersiz")
        if kimlik in kimlikler:
            raise ValueError("kimlik yinelenemez")
        kimlikler.add(kimlik)
        url = istek["url"]
        if not isinstance(url, str):
            raise ValueError("URL metin olmalı")
        if not url:
            raise ValueError("URL boş olamaz")
        if any(karakter.isspace() or not karakter.isprintable() for karakter in url):
            raise ValueError("URL boşluk veya kontrol karakteri içeremez")
        if type(istek["yonlendirme"]) is not int:
            raise ValueError("yönlendirme int olmalı")
        if istek["yonlendirme"] < 0:
            raise ValueError("yönlendirme negatif olamaz")
        try:
            parca = urlsplit(url)
            acik_port = parca.port
        except ValueError as hata:
            raise ValueError("URL ayrıştırılamadı") from hata
        hedef = parca.hostname or ""
        nedenler = []
        if parca.scheme != "https":
            nedenler.append("sema")
        if parca.username is not None or parca.password is not None:
            nedenler.append("kimlik")
        if hedef not in politika["alan_adlari"]:
            nedenler.append("alan")
        port = acik_port
        if port is None and parca.scheme == "https":
            port = 443
        if port is not None and port not in politika["portlar"]:
            nedenler.append("port")
        if istek["yonlendirme"] > politika["max_yonlendirme"]:
            nedenler.append("yonlendirme")
        rapor.append({"id": kimlik, "karar": "reddet" if nedenler else "hazir", "nedenler": nedenler, "hedef": hedef})
    return sorted(rapor, key=lambda x: x["id"])

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_savunma_14 as deney
    deney.goster(egress_url_deneti)
```

```hint
Bu işlev 2. görevdeki `egress_url_deneti` ile birebir aynıdır; tek fark, URL'lerin gerçek model önerilerinden gelmesidir. `urlsplit` ile host ve portu al; örtük HTTPS portunu 443 say ve nedenleri bağımsız topla.
```
:::
