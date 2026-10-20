---
id: p70
title: Proje · Erişim Logu İstatistikleri
summary: Web sunucusu erişim loglarını ayrıştırıp trafik, durum kodu, gecikme ve yoğunluk raporu üreten araç.
---

::: anlat Proje tanımı
Bir web sunucusunun erişim logu elinde. Ekip senden sabah toplantısı için birkaç sorunun cevabını istiyor: **dün kaç istek geldi, ne kadarı hata verdi, en çok hangi sayfalar istendi, site ne kadar hızlıydı, en yoğun saat hangisiydi?**

Bu projede, önceki paftalarda öğrendiklerini birleştiren küçük bir **raporlama aracı** yazacaksın:

| Aşama | İş | Kullandığın paftalar |
|---|---|---|
| 1. Ayrıştır | Satırı yapılandırılmış kayda çevir | P34 regex, P35 datetime |
| 2. Özetle | Durum sınıfları, en çok istenen yollar, toplam trafik | P16, P32 Counter |
| 3. Gecikme | Yüzdelikler ve en yavaş uç nokta | P13 sıralama, P35 istatistik |
| 4. Yoğunluk | Saatlik dağılım ve en yoğun saat | P10, P13 |

Log satırları, yaygın "combined" biçimin sadeleştirilmiş bir hali; sonda isteğin kaç saniyede yanıtlandığı var:

```text
10.0.0.5 - - [19/Oct/2026:08:15:02 +0300] "GET /index.html HTTP/1.1" 200 5120 0.042
10.0.0.8 - - [19/Oct/2026:08:15:09 +0300] "POST /api/siparis HTTP/1.1" 201 312 0.180
10.0.0.5 - - [19/Oct/2026:09:01:44 +0300] "GET /resim/logo.png HTTP/1.1" 304 - 0.003
```

Alanlar sırasıyla: istemci adresi, iki boş alan (`-`), köşeli parantez içinde zaman, tırnak içinde istek satırı (yöntem, yol, sürüm), durum kodu, yanıt boyutu (bayt; içerik yoksa `-`) ve yanıt süresi.

Her görev kendi başına çalışır. Görev 2–4, görev 1'in ürettiği kayıt biçimini kullanır:

```python norun
{"ip": "10.0.0.5", "zaman": datetime(2026, 10, 19, 8, 15, 2, tzinfo=...), "yontem": "GET",
 "yol": "/index.html", "durum": 200, "bayt": 5120, "sure": 0.042}
```

> [!NOT]
> Gerçek dünyada bu iş için hazır araçlar (GoAccess, ELK, Grafana Loki) vardır. Ama hepsinin çekirdeği bu projedeki dört adımdır. Kendin yazınca, hazır aracın sana gösterdiği bir sayının nereden geldiğini de bilirsin.
:::

::: gorev 1 · Satır ayrıştırıcı
`ayristir(satir)` fonksiyonunu yaz: yukarıdaki biçimdeki bir satırı kayıt sözlüğüne çevirsin, biçime uymayan satırlarda `None` döndürsün.

- `zaman`: saat dilimli `datetime` (`%d/%b/%Y:%H:%M:%S %z`)
- `durum`: int, `bayt`: int (`-` ise 0), `sure`: float
- Sorgu metnini yoldan **ayırma**; yol olduğu gibi kalsın

```starter
import re
from datetime import datetime

def ayristir(satir):
    pass
```

```test
from datetime import datetime, timezone, timedelta
need("ayristir")
k = ayristir('10.0.0.5 - - [19/Oct/2026:08:15:02 +0300] "GET /index.html HTTP/1.1" 200 5120 0.042')
eq(k, {"ip": "10.0.0.5", "zaman": datetime(2026, 10, 19, 8, 15, 2, tzinfo=timezone(timedelta(hours=3))),
       "yontem": "GET", "yol": "/index.html", "durum": 200, "bayt": 5120, "sure": 0.042}, "tam kayıt")
k2 = ayristir('10.0.0.5 - - [19/Oct/2026:09:01:44 +0300] "GET /ara?q=kitap HTTP/1.1" 304 - 0.003')
eq((k2["yol"], k2["bayt"], k2["durum"]), ("/ara?q=kitap", 0, 304), "boyut '-' → 0, sorgu yolda kalır")
eq(ayristir("bozuk satır"), None, "biçim dışı → None")
eq(ayristir(""), None, "boş satır → None")
```

```solution
import re
from datetime import datetime

DESEN = re.compile(
    r'(?P<ip>\S+) \S+ \S+ \[(?P<zaman>[^\]]+)\] "(?P<yontem>[A-Z]+) (?P<yol>\S+) [^"]*" '
    r'(?P<durum>\d{3}) (?P<bayt>\d+|-) (?P<sure>[\d.]+)'
)

def ayristir(satir):
    m = DESEN.match(satir)
    if not m:
        return None
    d = m.groupdict()
    return {
        "ip": d["ip"],
        "zaman": datetime.strptime(d["zaman"], "%d/%b/%Y:%H:%M:%S %z"),
        "yontem": d["yontem"],
        "yol": d["yol"],
        "durum": int(d["durum"]),
        "bayt": 0 if d["bayt"] == "-" else int(d["bayt"]),
        "sure": float(d["sure"]),
    }
```

```hint
Adlı gruplarla tek bir desen yaz: `\[(?P<zaman>[^\]]+)\]` köşeli parantezin içini, `"(?P<yontem>[A-Z]+) (?P<yol>\S+) [^"]*"` istek satırını yakalar.
```

```hint
Saat dilimli zaman: `datetime.strptime(metin, "%d/%b/%Y:%H:%M:%S %z")`.
```
:::

::: gorev 2 · Trafik özeti
`ozet(kayitlar)` fonksiyonu kayıt listesinden şu sözlüğü üretsin:

```python
{"toplam": 6,
 "durum_siniflari": {"2xx": 3, "3xx": 1, "4xx": 1, "5xx": 1},
 "toplam_bayt": 12345,
 "en_cok_yol": [("/index.html", 3), ("/api/siparis", 2), ("/hakkinda", 1)]}
```

- `durum_siniflari` dört sınıfı **her zaman** içersin (yoksa 0)
- `en_cok_yol`: en çok istenen en fazla 3 yol, çoktan aza; eşitlikte yol adına göre alfabetik

```starter
from collections import Counter

def ozet(kayitlar):
    pass
```

```test
need("ozet")
def k(yol, durum, bayt):
    return {"ip": "x", "zaman": None, "yontem": "GET", "yol": yol, "durum": durum, "bayt": bayt, "sure": 0.1}
kayitlar = [k("/index.html", 200, 5000), k("/api/siparis", 201, 300), k("/index.html", 200, 5000),
            k("/hakkinda", 404, 120), k("/index.html", 304, 0), k("/api/siparis", 500, 90)]
eq(ozet(kayitlar), {"toplam": 6, "durum_siniflari": {"2xx": 3, "3xx": 1, "4xx": 1, "5xx": 1},
                    "toplam_bayt": 10510,
                    "en_cok_yol": [("/index.html", 3), ("/api/siparis", 2), ("/hakkinda", 1)]}, "örnek özet")
eq(ozet([]), {"toplam": 0, "durum_siniflari": {"2xx": 0, "3xx": 0, "4xx": 0, "5xx": 0},
              "toplam_bayt": 0, "en_cok_yol": []}, "boş liste")
eq(ozet([k("/b", 200, 1), k("/a", 200, 1)])["en_cok_yol"], [("/a", 1), ("/b", 1)], "eşitlikte alfabetik")
```

```solution
from collections import Counter

def ozet(kayitlar):
    siniflar = {"2xx": 0, "3xx": 0, "4xx": 0, "5xx": 0}
    for k in kayitlar:
        sinif = f"{k['durum'] // 100}xx"
        if sinif in siniflar:
            siniflar[sinif] += 1
    yollar = Counter(k["yol"] for k in kayitlar)
    en_cok = sorted(yollar.items(), key=lambda yv: (-yv[1], yv[0]))[:3]
    return {
        "toplam": len(kayitlar),
        "durum_siniflari": siniflar,
        "toplam_bayt": sum(k["bayt"] for k in kayitlar),
        "en_cok_yol": en_cok,
    }
```

```hint
Durum sınıfı: `f"{durum // 100}xx"`. Yollar için `Counter`; eşitlik kuralı için `sorted(..., key=lambda yv: (-yv[1], yv[0]))`.
```
:::

::: gorev 3 · Gecikme raporu
Ortalama gecikme yanıltıcıdır: kullanıcıların çoğu hızlı yanıt alırken birkaç çok yavaş istek ortalamayı bozar. Bu yüzden ekipler **yüzdelik** (percentile) kullanır: p95 = isteklerin %95'i bu süreden hızlı.

İki fonksiyon yaz:

- `yuzdelik(degerler, p)`: **en yakın sıra** yöntemiyle p. yüzdelik. Değerleri sırala, sıra = `ceil(p / 100 * n)` (en az 1), sonuç = sıralı listenin `sıra - 1`'inci elemanı. Boş listede `None`.
- `gecikme_raporu(kayitlar)`: `{"p50": ..., "p95": ..., "en_yavas_yol": ...}`; en yavaş yol, ortalama süresi en yüksek olan yoldur. Kayıt yoksa üçü de `None`.

```starter
import math

def yuzdelik(degerler, p):
    pass

def gecikme_raporu(kayitlar):
    pass
```

```test
need("yuzdelik"); need("gecikme_raporu")
d = [0.05, 0.01, 0.30, 0.02, 0.04, 0.03, 0.02, 0.06, 0.02, 1.50]
eq(yuzdelik(d, 50), 0.03, "p50")
eq(yuzdelik(d, 95), 1.50, "p95 (10 değerde 10. sıra)")
eq(yuzdelik(d, 90), 0.30, "p90")
eq(yuzdelik(d, 0), 0.01, "p0 → en küçük")
eq(yuzdelik([], 50), None, "boş → None")
def k(yol, sure):
    return {"ip": "x", "zaman": None, "yontem": "GET", "yol": yol, "durum": 200, "bayt": 0, "sure": sure}
kayitlar = [k("/a", 0.02), k("/a", 0.04), k("/rapor", 0.9), k("/rapor", 1.1), k("/b", 0.05)]
eq(gecikme_raporu(kayitlar), {"p50": 0.05, "p95": 1.1, "en_yavas_yol": "/rapor"}, "rapor")
eq(gecikme_raporu([]), {"p50": None, "p95": None, "en_yavas_yol": None}, "boş rapor")
```

```solution
import math

def yuzdelik(degerler, p):
    if not degerler:
        return None
    sirali = sorted(degerler)
    sira = max(1, math.ceil(p / 100 * len(sirali)))
    return sirali[sira - 1]

def gecikme_raporu(kayitlar):
    if not kayitlar:
        return {"p50": None, "p95": None, "en_yavas_yol": None}
    sureler = [k["sure"] for k in kayitlar]
    gruplar = {}
    for k in kayitlar:
        gruplar.setdefault(k["yol"], []).append(k["sure"])
    en_yavas = max(gruplar, key=lambda y: sum(gruplar[y]) / len(gruplar[y]))
    return {"p50": yuzdelik(sureler, 50), "p95": yuzdelik(sureler, 95), "en_yavas_yol": en_yavas}
```

```hint
En yakın sıra: `sira = max(1, math.ceil(p / 100 * n))`, sonuç `sirali[sira - 1]`.
```

```hint
Yollara göre süreleri grupla (`setdefault(yol, []).append(sure)`), sonra `max(gruplar, key=ortalama)`.
```
:::

::: gorev 4 · Saatlik yoğunluk
İki fonksiyon yaz:

- `saatlik(kayitlar)`: 24 elemanlı bir liste; i. eleman, saati i olan (kaydın kendi saat diliminde) istek sayısı
- `en_yogun_saat(kayitlar)`: en çok isteğin geldiği saati `"08:00-09:00"` biçiminde döndür; eşitlikte erken saat; kayıt yoksa `None`

Son olarak, `ornek.log` dosyasını görev 1'deki biçimde okuyan (bozuk satırları atlayan) ve en yoğun saati yazdıran kısa bir program bölümü ekle. Ayrıştırıcı aşağıda hazır.

```setup
satirlar = [
    '10.0.0.5 - - [19/Oct/2026:08:15:02 +0300] "GET / HTTP/1.1" 200 512 0.04',
    '10.0.0.6 - - [19/Oct/2026:08:47:10 +0300] "GET /urun/7 HTTP/1.1" 200 2048 0.11',
    'bu satır bozuk',
    '10.0.0.7 - - [19/Oct/2026:14:02:00 +0300] "GET / HTTP/1.1" 200 512 0.05',
    '10.0.0.5 - - [19/Oct/2026:08:59:59 +0300] "POST /sepet HTTP/1.1" 201 90 0.20',
    '10.0.0.9 - - [19/Oct/2026:23:30:00 +0300] "GET /iletisim HTTP/1.1" 404 120 0.02',
]
with open("ornek.log", "w", encoding="utf-8") as f:
    f.write("\n".join(satirlar) + "\n")
```

```starter
import re
from datetime import datetime

DESEN = re.compile(
    r'(?P<ip>\S+) \S+ \S+ \[(?P<zaman>[^\]]+)\] "(?P<yontem>[A-Z]+) (?P<yol>\S+) [^"]*" '
    r'(?P<durum>\d{3}) (?P<bayt>\d+|-) (?P<sure>[\d.]+)'
)

def ayristir(satir):
    m = DESEN.match(satir)
    if not m:
        return None
    d = m.groupdict()
    return {"ip": d["ip"], "zaman": datetime.strptime(d["zaman"], "%d/%b/%Y:%H:%M:%S %z"),
            "yontem": d["yontem"], "yol": d["yol"], "durum": int(d["durum"]),
            "bayt": 0 if d["bayt"] == "-" else int(d["bayt"]), "sure": float(d["sure"])}

def saatlik(kayitlar):
    pass

def en_yogun_saat(kayitlar):
    pass

# ornek.log'u oku ve en yoğun saati yazdır

```

```test
from datetime import datetime
need("saatlik"); need("en_yogun_saat")
def k(saat):
    return {"ip": "x", "zaman": datetime(2026, 10, 19, saat, 0), "yontem": "GET", "yol": "/", "durum": 200, "bayt": 0, "sure": 0.1}
s = saatlik([k(8), k(8), k(14), k(23)])
eq(len(s), 24, "24 elemanlı liste")
eq((s[8], s[14], s[23], sum(s)), (2, 1, 1, 4), "saat sayıları")
eq(en_yogun_saat([k(9), k(9), k(21), k(21), k(3)]), "09:00-10:00", "eşitlikte erken saat")
eq(en_yogun_saat([k(23)]), "23:00-24:00", "son saat dilimi")
eq(en_yogun_saat([]), None, "kayıt yok → None")
eq(out.strip(), "08:00-09:00", "ornek.log'un en yoğun saati yazdırılmalı")
```

```solution
import re
from datetime import datetime

DESEN = re.compile(
    r'(?P<ip>\S+) \S+ \S+ \[(?P<zaman>[^\]]+)\] "(?P<yontem>[A-Z]+) (?P<yol>\S+) [^"]*" '
    r'(?P<durum>\d{3}) (?P<bayt>\d+|-) (?P<sure>[\d.]+)'
)

def ayristir(satir):
    m = DESEN.match(satir)
    if not m:
        return None
    d = m.groupdict()
    return {"ip": d["ip"], "zaman": datetime.strptime(d["zaman"], "%d/%b/%Y:%H:%M:%S %z"),
            "yontem": d["yontem"], "yol": d["yol"], "durum": int(d["durum"]),
            "bayt": 0 if d["bayt"] == "-" else int(d["bayt"]), "sure": float(d["sure"])}

def saatlik(kayitlar):
    sayim = [0] * 24
    for k in kayitlar:
        sayim[k["zaman"].hour] += 1
    return sayim

def en_yogun_saat(kayitlar):
    if not kayitlar:
        return None
    sayim = saatlik(kayitlar)
    saat = sayim.index(max(sayim))
    return f"{saat:02d}:00-{saat + 1:02d}:00"

with open("ornek.log", encoding="utf-8") as f:
    kayitlar = [k for k in (ayristir(s.strip()) for s in f) if k]
print(en_yogun_saat(kayitlar))
```

```hint
`sayim = [0] * 24` ve her kayıt için `sayim[k["zaman"].hour] += 1`. `sayim.index(max(sayim))` eşitlikte ilk (en erken) saati verir.
```
:::
