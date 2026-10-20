---
id: p46
title: Closure ve Dekoratörler I
summary: Fonksiyon döndüren fonksiyon, kapanım hücreleri, @ sözdizimi ve functools.wraps.
---

::: anlat Kapanım: ortamını hatırlayan fonksiyon
P22'de gördük: iç fonksiyon, dıştaki fonksiyonun değişkenlerine erişebilir. Dış fonksiyon **bittikten sonra** bile:

```python
def carpan(n):
    def carp(x):
        return x * n              #! n dış fonksiyondan geliyor
    return carp                   #! fonksiyonu çağırmadan döndür

iki_kat = carpan(2)
uc_kat = carpan(3)
print(iki_kat(10), uc_kat(10))    #! her biri kendi n'ini hatırlıyor
print(iki_kat.__closure__[0].cell_contents)
```

`carpan(2)` döndüğünde yerel `n` normalde yok olurdu. Ama `carp` ona referans verdiği için Python `n`'i bir **hücreye** (cell) koyar ve fonksiyona bağlar. Fonksiyon + yakaladığı ortam = **kapanım** (closure).

### Dekoratör: fonksiyonu saran fonksiyon
**Dekoratör**, bir fonksiyonu alıp onun yerine geçecek **sarmalanmış** bir fonksiyon döndüren fonksiyondur. Asıl fonksiyona dokunmadan ona davranış ekler:

```python
import time

def zamanla(fonk):
    def sarmal(*args, **kwargs):              #! her türlü argümanı kabul et
        bas = time.perf_counter()
        sonuc = fonk(*args, **kwargs)         #! asıl fonksiyonu çağır
        print(f"{fonk.__name__}: {(time.perf_counter() - bas) * 1000:.2f} ms")
        return sonuc                           #! sonucu geri ver
    return sarmal

def yavas_topla(n):
    return sum(range(n))

yavas_topla = zamanla(yavas_topla)            #! elle dekorasyon
print(yavas_topla(1_000_000))

@zamanla                                      #! aynısı, sözdizimi şekeri
def kare_topla(n):
    return sum(i * i for i in range(n))

print(kare_topla(100_000))
```

`@zamanla` satırı tam olarak `kare_topla = zamanla(kare_topla)` demektir; fonksiyon tanımlandıktan hemen sonra çalışır.

> [!NOT]
> Dekoratörler her yerdedir: `@property`, `@classmethod`, `@lru_cache`, `@dataclass`, web çatılarında `@app.route("/")`, testlerde `@pytest.fixture`. Hepsi bu basit fikrin üzerine kurulu.
:::

::: tahmin
Çıktı tek satır:

```python
def carpan(n):
    def f(x):
        return x * n
    return f

iki = carpan(2)
uc = carpan(3)
print(iki(5), uc(5), iki.__closure__[0].cell_contents)
```

???

`10 15 2`. İki kapanım aynı koddan üretildi ama farklı `n` hücreleri taşır. `__closure__` yakalanan değişkenlerin hücreleridir.
:::

::: anlat wraps ve dekoratör sırası
Sarmalanan fonksiyon artık `sarmal`'dır: adı, belgesi ve imzası kaybolur. Bu, hata mesajlarını, `help()`'i ve araçları bozar. Çözüm `functools.wraps`:

```python
from functools import wraps

def kaydet(fonk):
    @wraps(fonk)                       #! adı, belgeyi, __wrapped__'ı kopyala
    def sarmal(*args, **kwargs):
        print(f"→ {fonk.__name__}{args}")
        return fonk(*args, **kwargs)
    return sarmal

@kaydet
def topla(a, b):
    """İki sayıyı toplar."""
    return a + b

print(topla(2, 3), topla.__name__, topla.__doc__)
print(topla.__wrapped__(10, 20))       #! orijinal fonksiyona hâlâ ulaşılabilir
```

**Kural: her dekoratörde `@wraps` kullan.**

Birden fazla dekoratör **alttan yukarı** uygulanır (fonksiyona en yakın olan önce sarar), çalışırken ise **yukarıdan aşağı** girilir:

```python
from functools import wraps

def koseli(f):
    @wraps(f)
    def s(*a):
        return "[" + f(*a) + "]"
    return s

def buyuk(f):
    @wraps(f)
    def s(*a):
        return f(*a).upper()
    return s

@koseli          #! 2) sonra bu sarar
@buyuk           #! 1) önce bu sarar
def selam(ad):
    return "merhaba " + ad

print(selam("ali"))      #! koseli(buyuk(selam))
```

> [!TUZAK]
> Döngüde kapanım oluşturmak klasik bir tuzaktır: `fonklar = [lambda: i for i in range(3)]` listesindeki üç fonksiyonun **üçü de 2 döndürür**. Kapanım değeri değil **değişkeni** yakalar; döngü bittiğinde i 2'dir. Çözüm varsayılan argümanla değeri dondurmaktır: `lambda i=i: i`.
:::

::: tahmin
Çıktı tek satır:

```python
def yildiz(f):
    def sar(*a):
        return "*" + f(*a) + "*"
    return sar

def alt(f):
    def sar(*a):
        return "_" + f(*a) + "_"
    return sar

@yildiz
@alt
def selam(ad):
    return ad

print(selam("ali"), selam.__name__)
```

???

`*_ali_* sar`. Önce `alt` sarar, sonra `yildiz`; çağrıldığında dıştaki (yildiz) içteki (alt) sonucu sarar. `wraps` kullanılmadığı için ad `sar` olarak görünür.
:::

::: gorev Çağrı sayacı
`cagri_say` adında bir dekoratör yaz. Sarmalanan fonksiyon her çağrıldığında sarmalın `sayac` niteliğini bir artırsın. `functools.wraps` kullan (ad korunmalı). Her dekore edilen fonksiyonun kendi sayacı olmalı.

```starter
from functools import wraps

def cagri_say(fonk):
    pass
```

```test
need("cagri_say")
@cagri_say
def kare(x):
    """kare alır"""
    return x * x
@cagri_say
def selam():
    return "hi"
eq(kare.sayac, 0, "başta 0")
eq(kare(4), 16, "sonuç korunmalı")
kare(1); kare(2)
eq(kare.sayac, 3, "3 çağrı → 3")
selam()
eq(selam.sayac, 1, "her fonksiyonun ayrı sayacı")
eq(kare.__name__, "kare", "wraps ile ad korunmalı")
eq(kare.__doc__, "kare alır", "wraps ile belge korunmalı")
```

```solution
from functools import wraps

def cagri_say(fonk):
    @wraps(fonk)
    def sarmal(*args, **kwargs):
        sarmal.sayac += 1
        return fonk(*args, **kwargs)
    sarmal.sayac = 0
    return sarmal
```

```hint
Fonksiyonlar nesnedir, nitelik taşıyabilirler: `sarmal.sayac = 0` ve sarmalın içinde `sarmal.sayac += 1`.
```
:::

::: gorev Denetim kaydı
`denetle` adında bir dekoratör yaz. Her çağrıda global `KAYITLAR` listesine `(fonksiyon_adı, args, sonuç)` demetini eklesin. Fonksiyon hata verirse sonuç yerine `"HATA: <istisna türü>"` metnini kaydetsin ve istisnayı **yeniden yükseltsin**.

```starter
from functools import wraps

KAYITLAR = []

def denetle(fonk):
    pass
```

```test
need("denetle")
KAYITLAR.clear()
@denetle
def bol(a, b):
    return a / b
eq(bol(6, 3), 2.0, "sonuç korunur")
raises(ZeroDivisionError, bol, 1, 0, msg="hata yeniden yükseltilmeli")
eq(KAYITLAR, [("bol", (6, 3), 2.0), ("bol", (1, 0), "HATA: ZeroDivisionError")], "iki kayıt")
eq(bol.__name__, "bol", "wraps")
```

```solution
from functools import wraps

KAYITLAR = []

def denetle(fonk):
    @wraps(fonk)
    def sarmal(*args, **kwargs):
        try:
            sonuc = fonk(*args, **kwargs)
        except Exception as e:
            KAYITLAR.append((fonk.__name__, args, f"HATA: {type(e).__name__}"))
            raise
        KAYITLAR.append((fonk.__name__, args, sonuc))
        return sonuc
    return sarmal
```

```hint
Sarmalın içinde `try/except Exception as e:` kullan, kaydı ekle ve çıplak `raise` ile yeniden yükselt.
```
:::

::: gorev Kayan ortalama
`ortalama_tutucu()` fonksiyonu bir **kapanım** döndürsün: döndürülen fonksiyon her çağrıda bir sayı alsın ve şimdiye kadar verilen **tüm** sayıların ortalamasını döndürsün. Global değişken ve sınıf kullanma.

```starter
def ortalama_tutucu():
    pass
```

```test
need("ortalama_tutucu")
ort = ortalama_tutucu()
eq(ort(10), 10.0, "10 → 10.0")
eq(ort(20), 15.0, "10, 20 → 15.0")
eq(ort(0), 10.0, "10, 20, 0 → 10.0")
ort2 = ortalama_tutucu()
eq(ort2(4), 4.0, "ikinci tutucu bağımsız")
ok(ort.__closure__ is not None, "bir kapanım olmalı")
ok(not uses("global") and not uses("class"), "global ve sınıf kullanmadan")
```

```solution
def ortalama_tutucu():
    toplam = 0
    adet = 0
    def ekle(x):
        nonlocal toplam, adet
        toplam += x
        adet += 1
        return toplam / adet
    return ekle
```

```hint
Dış fonksiyonda `toplam` ve `adet`; içte `nonlocal toplam, adet`.
```

```hint
Alternatif: dışta bir liste tut ve `append` et; listeyi değiştirmek (atamak değil) `nonlocal` gerektirmez.
```
:::
