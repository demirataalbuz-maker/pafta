---
id: p35
title: Zaman, Matematik, İstatistik
summary: datetime ve timedelta, math, kuruş hassasiyeti için decimal ve statistics ile aykırı değer.
kazanim: PCAP 1.2
---

::: anlat Zaman damgaları
Log analizinin yarısı zamandır: "bu iki olay arasında kaç saniye var?", "son 24 saatte ne oldu?". `datetime` modülü bunun için:

```python
from datetime import datetime, date, timedelta, timezone

t = datetime(2026, 10, 19, 8, 15, 30)
print(t, t.year, t.hour)
print(t + timedelta(hours=20))                    #! zaman aritmetiği
fark = datetime(2026, 10, 20, 9, 0) - t           #! iki zaman farkı = timedelta
print(fark, fark.total_seconds())

print(t.strftime("%d.%m.%Y %H:%M"))               #! nesne → metin
g = datetime.strptime("19/Oct/2026:08:02:10", "%d/%b/%Y:%H:%M:%S")   #! metin → nesne (web sunucusu log biçimi)
print(g.isoformat())
print(datetime.fromisoformat("2026-10-19T08:02:10"))
print(date(2026, 10, 19).weekday())               #! 0 = Pazartesi
utc = datetime.now(timezone.utc)                  #! saat dilimli (aware) zaman
print(utc.tzinfo)
```

| Kod | Anlamı | Kod | Anlamı |
|---|---|---|---|
| `%Y` | 2026 | `%H` | 0–23 saat |
| `%m` | 01–12 ay | `%M` | dakika |
| `%d` | 01–31 gün | `%S` | saniye |
| `%b` | Oct (kısa ay adı) | `%z` | +0300 |

> [!TUZAK]
> Saat dilimsiz (*naive*) ve saat dilimli (*aware*) zamanlar karşılaştırılamaz (`TypeError`). Farklı sunuculardan gelen logları birleştirirken her şeyi **UTC**'ye çevir; yerel saat yaz/kış geçişlerinde bir saati iki kez yaşar ya da hiç yaşamaz. Olay zaman çizelgesi kurarken en sık yapılan hata budur.

**Süre ölçmek** için `time.perf_counter()` kullan: duvar saatinden bağımsız, yüksek çözünürlüklü bir sayaçtır. `time.time()` ise Unix zaman damgasını verir (1970'ten beri geçen saniye).
:::

::: tahmin
İki satır:

```python
from datetime import datetime, timedelta
t = datetime(2026, 10, 19, 23, 30)
print((t + timedelta(minutes=45)).strftime("%Y-%m-%d %H:%M"))
print((datetime(2026, 12, 31) - datetime(2026, 10, 19)).days)
```

???

`2026-10-20 00:15`, sonra `73`. 45 dakika gece yarısını aşıp tarihi değiştirir. Ekim'in kalan 12 günü + Kasım'ın 30 günü + Aralık'ın 31 günü = 73.
:::

::: anlat math, decimal, statistics
### math
```python
import math

print(math.floor(3.7), math.ceil(3.2), math.trunc(-3.7))   #! aşağı, yukarı, sıfıra doğru
print(math.gcd(84, 36), math.lcm(4, 6))                    #! EBOB, EKOK
print(math.sqrt(2), math.isqrt(17))                        #! karekök, tam sayı karekök
print(math.log2(1024), math.log10(1000), math.log(math.e))
print(math.comb(10, 3), math.factorial(5))                 #! kombinasyon, faktöriyel
print(math.isclose(0.1 + 0.2, 0.3))                        #! P03'teki tuzağın doğru çözümü
print(math.inf > 10**100, math.pi)
```

### decimal: kuruş hassasiyeti
P03'te float'ın para için uygun olmadığını söylemiştik. `decimal.Decimal` onluk tabanda **tam** hesap yapar:

```python
from decimal import Decimal, ROUND_HALF_UP

print(0.1 + 0.2)                                   #! 0.30000000000000004
print(Decimal("0.1") + Decimal("0.2"))             #! 0.3 — tam
fiyat = Decimal("19.995")
print(fiyat.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))   #! 20.00
print(Decimal(0.1))                                #! float'tan yaratma: hatayı da taşır!
```

> [!TUZAK]
> `Decimal(0.1)` yazma, `Decimal("0.1")` yaz. Float'tan oluşturursan float'ın ikilik yaklaşım hatası da Decimal'e geçer.

### statistics
```python
import statistics as st

yanit_ms = [120, 135, 128, 990, 131, 125, 140]
print(st.mean(yanit_ms), st.median(yanit_ms))      #! ortalama aykırı değere duyarlı, medyan değil
print(round(st.pstdev(yanit_ms), 1))               #! standart sapma
print(st.mode([22, 80, 22, 443]))                  #! en sık değer
print(st.quantiles(yanit_ms, n=4))                 #! çeyrekler
```

Ortalama ile medyan arasındaki fark tek başına bir sinyaldir: 990 ms'lik tek bir yavaş istek ortalamayı ~253'e çeker, medyan ise 131'de kalır.

> [!GÜVENLİK]
> Anomali tespitinin en basit hali istatistiktir: bir kullanıcının günlük indirdiği veri, giriş saatleri ya da istek sayısı **kendi ortalamasından** kaç standart sapma uzakta? Kullanıcı ve varlık davranış analitiği (UEBA) ürünlerinin çekirdeğinde bu fikir vardır. Bu paftanın son görevinde basit bir sürümünü yazacaksın.
:::

::: tahmin
İki satır:

```python
import math
from decimal import Decimal
print(math.ceil(7 / 2), math.floor(-3.5), math.gcd(12, 18), math.log2(1024))
print(Decimal("1.10") + Decimal("2.20"))
```

???

`4 -4 6 10.0`, sonra `3.30`. `floor(-3.5)` aşağı yuvarlar, yani `-4` olur. `log2` her zaman float döndürür. Decimal ise ondalık basamak sayısını korur: `1.10 + 2.20 = 3.30`.
:::

::: gorev Oturum süresi
`oturum_dakika(giris, cikis)` fonksiyonu `"2026-10-19 08:15:00"` biçimindeki iki zaman damgası arasındaki farkı **tam dakika** (aşağı yuvarlanmış int) olarak döndürsün. Gece yarısını aşan oturumlar da doğru hesaplanmalı.

```starter
from datetime import datetime

def oturum_dakika(giris, cikis):
    pass
```

```test
need("oturum_dakika")
eq(oturum_dakika("2026-10-19 08:15:00", "2026-10-19 09:00:30"), 45, "08:15:00 → 09:00:30 = 45 dk")
eq(oturum_dakika("2026-10-19 23:50:00", "2026-10-20 00:20:00"), 30, "gece yarısını aşan → 30 dk")
eq(oturum_dakika("2026-10-19 10:00:00", "2026-10-21 10:00:00"), 2880, "iki gün → 2880 dk")
eq(oturum_dakika("2026-10-19 10:00:00", "2026-10-19 10:00:59"), 0, "59 sn → 0 dk")
ok(calls("strptime") or calls("fromisoformat"), "strptime ya da fromisoformat ile ayrıştır")
```

```solution
from datetime import datetime

BICIM = "%Y-%m-%d %H:%M:%S"

def oturum_dakika(giris, cikis):
    fark = datetime.strptime(cikis, BICIM) - datetime.strptime(giris, BICIM)
    return int(fark.total_seconds() // 60)
```

```hint
`datetime.strptime(metin, "%Y-%m-%d %H:%M:%S")`. İki datetime'ın farkı timedelta'dır; `total_seconds()` ile saniyeye çevir.
```
:::

::: gorev Fatura toplamı
`fatura_toplam(kalemler)` fonksiyonu `["19.99", "0.10", "0.20"]` gibi **metin** fiyat listesini alsın, `Decimal` ile toplasın ve sonucu 2 ondalığa yuvarlanmış (`ROUND_HALF_UP`) bir **Decimal** olarak döndürsün.

```starter
from decimal import Decimal, ROUND_HALF_UP

def fatura_toplam(kalemler):
    return round(sum(float(k) for k in kalemler), 2)
```

```test
from decimal import Decimal
need("fatura_toplam")
s = fatura_toplam(["19.99", "0.10", "0.20"])
ok(isinstance(s, Decimal), "sonuç Decimal olmalı", got=type(s).__name__)
eq(s, Decimal("20.29"), "19.99 + 0.10 + 0.20 = 20.29")
eq(str(fatura_toplam(["0.1"] * 10)), "1.00", "on kez 0.1 → tam 1.00")
eq(str(fatura_toplam(["1.005"])), "1.01", "1.005 → 1.01 (yarım yukarı)")
eq(str(fatura_toplam([])), "0.00", "boş fatura → 0.00")
```

```solution
from decimal import Decimal, ROUND_HALF_UP

def fatura_toplam(kalemler):
    toplam = sum((Decimal(k) for k in kalemler), Decimal("0"))
    return toplam.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
```

```hint
Her kalemi `Decimal(k)` yap (metinden!). `sum(..., Decimal("0"))` başlangıç değeriyle topla.
```

```hint
Yuvarlama: `toplam.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`
```
:::

::: gorev Aykırı değer dedektörü
`aykirilar(degerler, k=2)` fonksiyonu ortalamadan **k popülasyon standart sapmasından** (`statistics.pstdev`) daha uzak olan değerleri, **listedeki sırasıyla** döndürsün. Standart sapma 0 ise boş liste döndür.

```starter
import statistics

def aykirilar(degerler, k=2):
    pass
```

```test
need("aykirilar")
gunluk_mb = [210, 190, 205, 198, 220, 2400, 201, 195]
eq(aykirilar(gunluk_mb), [2400], "günlük indirmede 2400 MB aykırı")
eq(aykirilar([5, 5, 5, 5]), [], "sapma 0 → []")
eq(aykirilar([1, 2, 3, 4, 100, -90], k=1), [100, -90], "k=1 ile iki uç değer")
eq(aykirilar([0, 2], k=1), [], "tam k·σ uzaklık (ortalama 1, σ 1) aykırı sayılmaz")
ok(calls("pstdev"), "statistics.pstdev kullan")
```

```solution
import statistics

def aykirilar(degerler, k=2):
    ort = statistics.mean(degerler)
    sapma = statistics.pstdev(degerler)
    if sapma == 0:
        return []
    return [d for d in degerler if abs(d - ort) > k * sapma]
```

```hint
Ortalama `statistics.mean`, sapma `statistics.pstdev`. Koşul: `abs(d - ort) > k * sapma`.
```
:::
