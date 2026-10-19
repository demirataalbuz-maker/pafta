---
id: p46
title: Bağlam Yöneticileri · with
summary: __enter__ ve __exit__, istisnayı yutmak, contextlib.contextmanager, suppress ve ExitStack.
---

::: anlat with'in iç yüzü
P27'de `with open(...)` bloktan çıkarken dosyayı kapattı, hata olsa bile. Bu sihri her sınıf yapabilir. **Bağlam yöneticisi** (context manager) iki dunder'lı bir nesnedir:

- `__enter__(self)`: bloğa girerken çağrılır; döndürdüğü değer `as` hedefine bağlanır
- `__exit__(self, tur, deger, iz)`: bloktan **her nasıl çıkılırsa çıkılsın** çağrılır. Hata yoksa üç argüman da `None`'dır

```python
import time

class Zamanlayici:
    def __enter__(self):
        self.bas = time.perf_counter()
        return self                            #! "as z" buraya bağlanır

    def __exit__(self, tur, deger, iz):
        self.sure = time.perf_counter() - self.bas
        print(f"süre: {self.sure * 1000:.1f} ms", "(hatayla)" if tur else "")
        return False                           #! False/None: hata varsa yayılmaya devam etsin

with Zamanlayici() as z:
    toplam = sum(range(1_000_000))
print(toplam, z.sure > 0)
```

`with A() as x: GÖVDE` aşağı yukarı şunun kısaltmasıdır:

```python norun
yonetici = A()
x = yonetici.__enter__()
try:
    GÖVDE
except BaseException as e:
    if not yonetici.__exit__(type(e), e, e.__traceback__):
        raise                      # __exit__ True döndürmediyse hatayı yay
else:
    yonetici.__exit__(None, None, None)
```

`__exit__` **`True` döndürürse istisna yutulur**. Bunu sadece bilinçli olarak yap.

### Nerede kullanılır?
Bir şeyi **alıp mutlaka geri vermen** gereken her yerde: dosya, ağ bağlantısı, veritabanı işlemi (commit/rollback), kilit (`with threading.Lock():`, P54), geçici klasör, geçici ayar değişikliği.
:::

::: tahmin
Çıktıyı satır satır yaz:

```python
class Ctx:
    def __enter__(self):
        print("gir")
        return 42
    def __exit__(self, tur, deger, iz):
        print("çık", tur.__name__ if tur else None)
        return True

with Ctx() as x:
    print(x)
    1 / 0
    print("buraya gelinmez")
print("devam")
```

???

```cikti
gir
42
çık ZeroDivisionError
devam
```

`__enter__`'ın döndürdüğü 42, `x`'e bağlanır. Bölme hatası bloğun geri kalanını atlar ve `__exit__` hata türüyle çağrılır. `True` döndürdüğü için hata yutulur ve program devam eder.
:::

::: anlat contextlib: üreteçle bağlam yöneticisi
Her seferinde sınıf yazmak yerine `@contextmanager` ile **tek bir `yield`'li üreteç** yazarsın. `yield`'den önceki kısım `__enter__`, sonrası `__exit__` olur:

```python
from contextlib import contextmanager
import os

@contextmanager
def klasorde(yol):
    eski = os.getcwd()
    os.makedirs(yol, exist_ok=True)
    os.chdir(yol)
    try:
        yield yol                        #! with bloğu burada çalışır
    finally:
        os.chdir(eski)                   #! hata olsa bile geri dön

with klasorde("rapor"):
    print("içerideyim:", os.path.basename(os.getcwd()))
print("geri döndüm:", os.path.basename(os.getcwd()) != "rapor")
```

> [!TUZAK]
> `yield`'i `try/finally` içine almazsan, blokta hata çıktığında temizlik kodu **çalışmaz**: istisna `yield` satırından yükselir ve alttaki satırlara hiç gelinmez.

### Hazır araçlar
```python
from contextlib import suppress, redirect_stdout, ExitStack
import io, os

with suppress(FileNotFoundError):          #! bu hatayı bilinçli olarak yut
    os.remove("olmayan.tmp")

tampon = io.StringIO()
with redirect_stdout(tampon):              #! print'leri yakala
    print("gizli çıktı")
print("yakalanan:", tampon.getvalue().strip())

with ExitStack() as yigin:                 #! sayısı bilinmeyen kaynakları tek blokta yönet
    dosyalar = [yigin.enter_context(open(f"p{i}.txt", "w")) for i in range(3)]
    for f in dosyalar:
        f.write("x")
print(all(f.closed for f in dosyalar))
```

> [!DERİN]
> `async with` için de aynı protokolün asenkron versiyonu var: `__aenter__` ve `__aexit__` (ya da `@asynccontextmanager`). Bunları P56'da asyncio ile birlikte göreceksin. `ExitStack`'in içinde bir yığın vardır: kaynakları **ters sırada** kapatır, tıpkı iç içe `with` blokları gibi.
:::

::: tahmin
Üç satır:

```python
from contextlib import contextmanager

@contextmanager
def etiket(ad):
    print(f"<{ad}>")
    try:
        yield ad.upper()
    finally:
        print(f"</{ad}>")

with etiket("b") as e:
    print(e)
```

???

`<b>`, `B`, `</b>`. yield'den önceki kısım girişte çalışır, yield edilen değer `as e`'ye bağlanır, blok bitince `finally` çalışır.
:::

::: gorev Zamanlayıcı
`Zamanlayici` sınıfını bir bağlam yöneticisi olarak yaz: `as` ile kendisini versin, çıkışta geçen süreyi saniye cinsinden `sure` niteliğine yazsın. Blokta hata olursa da `sure` ayarlansın ve hata **yayılsın**.

```starter
import time

class Zamanlayici:
    pass
```

```test
import time
Z = need("Zamanlayici", "sınıf")
with Z() as z:
    time.sleep(0.05)
ok(isinstance(z, Z), "as ile kendisini vermeli")
ok(0.04 <= z.sure < 1.0, "sure ~0.05 sn olmalı", got=getattr(z, "sure", None))
z2 = Z()
try:
    with z2:
        raise KeyError("x")
    ok(False, "hata yutulmamalı")
except KeyError:
    ok(True, "hata yayıldı")
ok(hasattr(z2, "sure"), "hatada da sure ayarlanmalı")
```

```solution
import time

class Zamanlayici:
    def __enter__(self):
        self._bas = time.perf_counter()
        return self

    def __exit__(self, tur, deger, iz):
        self.sure = time.perf_counter() - self._bas
        return False
```

```hint
`__enter__` başlangıç zamanını kaydedip `self` döndürür; `__exit__` süreyi hesaplar ve `False` döndürür.
```
:::

::: gorev Geçici klasör değişikliği
`@contextmanager` ile `klasorde(yol)` yaz: yoksa klasörü oluştursun, içine geçsin (`os.chdir`), blok bitince **her durumda** eski klasöre dönsün. Bloğa çözülmüş mutlak yolu versin.

```starter
import os
from contextlib import contextmanager

def klasorde(yol):
    pass
```

```test
import os
need("klasorde")
bas = os.getcwd()
with klasorde("a/b") as y:
    ok(os.getcwd() == y and y.endswith(os.path.join("a", "b")), "a/b içindeyiz ve yol veriliyor", got=y)
eq(os.getcwd(), bas, "çıkınca geri dönüldü")
try:
    with klasorde("c"):
        raise RuntimeError("patladı")
except RuntimeError:
    pass
eq(os.getcwd(), bas, "hatadan sonra da geri dönüldü")
ok(os.path.isdir("a/b") and os.path.isdir("c"), "klasörler oluşturuldu")
```

```solution
import os
from contextlib import contextmanager

@contextmanager
def klasorde(yol):
    eski = os.getcwd()
    os.makedirs(yol, exist_ok=True)
    os.chdir(yol)
    try:
        yield os.getcwd()
    finally:
        os.chdir(eski)
```

```hint
`yield os.getcwd()`'i `try/finally` içine al; `finally`'de `os.chdir(eski)`.
```
:::

::: gorev Geri alınabilir işlem
`Islem(sozluk)` bağlam yöneticisi bir sözlük üzerinde **işlem** (transaction) gibi çalışsın: girişte sözlüğün bir **kopyasını** alsın. Blokta hata olursa sözlüğü **yerinde** eski haline döndürsün (aynı nesne kalmalı) ve hatayı yaysın. Hata yoksa değişiklikler kalsın.

```starter
class Islem:
    def __init__(self, sozluk):
        self.sozluk = sozluk
```

```test
I = need("Islem", "sınıf")
d = {"bakiye": 100}
with I(d):
    d["bakiye"] -= 30
eq(d, {"bakiye": 70}, "başarılı işlem kalıcı")
ref = d
try:
    with I(d):
        d["bakiye"] -= 500
        d["kilit"] = True
        raise ValueError("yetersiz bakiye")
except ValueError:
    ok(True, "hata yayıldı")
eq(d, {"bakiye": 70}, "hata sonrası geri alındı")
ok(d is ref, "aynı sözlük nesnesi yerinde geri yüklenmeli")
```

```solution
class Islem:
    def __init__(self, sozluk):
        self.sozluk = sozluk

    def __enter__(self):
        self._yedek = dict(self.sozluk)
        return self.sozluk

    def __exit__(self, tur, deger, iz):
        if tur is not None:
            self.sozluk.clear()
            self.sozluk.update(self._yedek)
        return False
```

```hint
Girişte `self._yedek = dict(self.sozluk)`. Hata varsa `self.sozluk.clear()` ve `self.sozluk.update(self._yedek)`: yeni sözlük atamak yerine yerinde değiştir.
```
:::
