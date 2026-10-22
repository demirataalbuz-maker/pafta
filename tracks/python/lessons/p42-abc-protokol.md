---
id: p42
title: Soyut Sınıflar, Protokoller, Ördek Tipleme
summary: Ördek tipleme, abc ile sözleşme, typing.Protocol ve collections.abc hazır arayüzleri.
kazanim: PCPP1 1.3, PCPP1 1.6
---

::: anlat Ördek gibi yürüyorsa...
"Ördek gibi yürüyorsa ve ördek gibi vaklıyorsa, o bir ördektir." Python bir nesnenin **türüne** değil, **yapabildiklerine** bakar. Buna **ördek tipleme** (duck typing) denir:

```python
class Dosya:
    def oku(self):
        return "dosya içeriği"

class Soket:
    def oku(self):
        return "ağdan gelen veri"

class Sahte:                              #! testlerde gerçek kaynağın yerine geçer
    def oku(self):
        return "test verisi"

def isle(kaynak):                         #! tür kontrolü YOK: oku() varsa yeter
    return kaynak.oku().upper()

for k in (Dosya(), Soket(), Sahte()):
    print(isle(k))
```

`isle` fonksiyonu kaynakların ortak bir tabandan türemesini istemez. Bu esneklik Python'un gücüdür; `print`'in `file=` parametresine `write()` metodu olan **her şeyi** verebilmen bu yüzdendir.

Bedeli şu: yanlış bir nesne verirsen hata **çağrı anında**, belki çok geç gelir. Daha kesin bir sözleşme istediğinde iki araç var: **soyut sınıflar** ve **protokoller**.

### abc: zorunlu metotlar
```python
from abc import ABC, abstractmethod

class Denetci(ABC):                       #! soyut taban
    @abstractmethod
    def denetle(self, hedef):             #! alt sınıflar bunu YAZMAK ZORUNDA
        ...

    def rapor(self, hedefler):            #! somut metot: denetle'yi kullanır
        return {h: self.denetle(h) for h in hedefler}

class UzunlukDenetci(Denetci):
    def denetle(self, hedef):
        return len(hedef) <= 253

print(UzunlukDenetci().rapor(["ornek.com", "x" * 300]))
try:
    Denetci()
except TypeError as e:
    print("soyut sınıftan nesne üretilemez:", e)
```

`@abstractmethod` olan bir metodu yazmayan alt sınıftan **nesne üretilemez**. Hata kullanım anında değil, **oluşturma anında** gelir.
:::

::: tahmin
İki satır:

```python
from abc import ABC, abstractmethod

class Denetci(ABC):
    @abstractmethod
    def denetle(self):
        ...

class Eksik(Denetci):
    pass

try:
    Eksik()
except TypeError:
    print("soyut")
print(issubclass(Eksik, Denetci))
```

???

`soyut`, sonra `True`. `Eksik` soyut metodu yazmadığı için hâlâ soyuttur ve nesne üretilemez. Ama Denetci'nin alt sınıfı olduğu doğrudur.
:::

::: anlat Protokol ve collections.abc
**`typing.Protocol`** ördek tiplemenin resmi halidir: "şu metotları olan her şey" der, **kalıtım istemez**. Statik tip denetleyicileri (mypy, P49) bunu kontrol eder. `@runtime_checkable` eklersen `isinstance` ile de çalışır:

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Okunabilir(Protocol):
    def oku(self) -> str: ...

class Dosya:                              #! Okunabilir'den TÜREMİYOR
    def oku(self):
        return "x"

print(isinstance(Dosya(), Okunabilir), isinstance(42, Okunabilir))
```

**`collections.abc`** Python'un kendi arayüzlerini tanımlar: `Iterable`, `Sequence`, `Mapping`, `Callable`... Hem tür kontrolü hem de **hazır metotlar** için kullanılır: `Mapping`'ten türeyip sadece üç dunder (`__getitem__`, `__iter__`, `__len__`) yazarsan `keys()`, `items()`, `get()`, `in` ve `==` bedavaya gelir.

```python
from collections.abc import Iterable, Mapping, Callable

print(isinstance([1, 2], Iterable), isinstance(5, Iterable))
print(isinstance({}, Mapping), isinstance(len, Callable))
```

> [!DERİN]
> `isinstance(Dosya(), Okunabilir)` kalıtım olmadan nasıl `True` döner? `abc.ABCMeta` metasınıfı `__subclasshook__` ve `__instancecheck__` kancaları sunar: `isinstance`, sınıf hiyerarşisine bakmadan önce bu kancaları çağırır. `collections.abc.Iterable` da böyle çalışır: sınıfta `__iter__` varsa yeter. Metasınıfları P65'de açacağız.

> [!NOT]
> Ne zaman hangisi? Kendi kodunda **ortak davranış paylaşan** bir aile kuruyorsan ABC. Başkalarının nesnelerini kabul eden **esnek bir fonksiyon** yazıyorsan Protocol ya da düz ördek tipleme.
:::

::: tahmin
İki satır:

```python
class Ordek:
    def ses(self):
        return "vak"

class Robot:
    def ses(self):
        return "bip"

print([x.ses() for x in (Ordek(), Robot())])
import collections.abc as cabc
print(isinstance([1], cabc.Iterable), isinstance(5, cabc.Iterable))
```

???

`['vak', 'bip']`, sonra `True False`. İki sınıfın hiçbir ortak tabanı yok ama ikisi de `ses()` sunduğu için aynı döngüde kullanılabilirler. Liste yinelenebilir, int değildir.
:::

::: gorev Kural motoru iskeleti
Soyut `Kural` sınıfını yaz:

- soyut metot `eslesir(olay) -> bool`
- somut metot `uygula(olaylar)` → eşleşen olayların listesi

Sonra iki alt sınıf:

- `PortKurali(port)`: `olay["port"] == port` ise eşleşir
- `KullaniciKurali(*adlar)`: `olay["kullanici"]` adlardan biriyse eşleşir

```starter
from abc import ABC, abstractmethod

class Kural:
    pass
```

```test
from abc import ABC
K = need("Kural", "sınıf"); P = need("PortKurali", "sınıf"); U = need("KullaniciKurali", "sınıf")
raises(TypeError, K, msg="Kural soyut olmalı (nesne üretilemez)")
olaylar = [{"port": 22, "kullanici": "root"}, {"port": 443, "kullanici": "ali"},
           {"port": 22, "kullanici": "ali"}, {"port": 3389, "kullanici": "admin"}]
eq(P(22).uygula(olaylar), [olaylar[0], olaylar[2]], "port 22 olayları")
eq(U("root", "admin").uygula(olaylar), [olaylar[0], olaylar[3]], "root ve admin olayları")
eq(P(8080).uygula(olaylar), [], "eşleşme yok")
class Eksik(K):
    pass
raises(TypeError, Eksik, msg="eslesir yazmayan alt sınıf da soyut kalmalı")
```

```solution
from abc import ABC, abstractmethod

class Kural(ABC):
    @abstractmethod
    def eslesir(self, olay):
        ...

    def uygula(self, olaylar):
        return [o for o in olaylar if self.eslesir(o)]


class PortKurali(Kural):
    def __init__(self, port):
        self.port = port

    def eslesir(self, olay):
        return olay["port"] == self.port


class KullaniciKurali(Kural):
    def __init__(self, *adlar):
        self.adlar = set(adlar)

    def eslesir(self, olay):
        return olay["kullanici"] in self.adlar
```

```hint
`class Kural(ABC):` ve `eslesir` üstüne `@abstractmethod`. `uygula` tabanda, `eslesir`'i çağırır.
```
:::

::: gorev Ördek tipli toplam
`toplam_boyut(nesneler)` fonksiyonu, `boyut()` metodu **olan** her nesnenin `boyut()` sonucunu toplasın; metodu olmayanları sessizce atlasın. Tür kontrolü (`isinstance`) yapma.

```starter
def toplam_boyut(nesneler):
    pass
```

```test
need("toplam_boyut")
class Dosya:
    def __init__(self, n): self.n = n
    def boyut(self): return self.n
class Klasor:
    def __init__(self, *ic): self.ic = ic
    def boyut(self): return sum(x.boyut() for x in self.ic)
class Kisayol:
    pass
eq(toplam_boyut([Dosya(10), Klasor(Dosya(5), Dosya(7)), Kisayol(), 42]), 22, "boyut() olanlar toplanır, diğerleri atlanır")
eq(toplam_boyut([]), 0, "boş → 0")
ok(not calls("isinstance"), "isinstance kullanmadan (ördek tipleme)")
```

```solution
def toplam_boyut(nesneler):
    toplam = 0
    for n in nesneler:
        try:
            boyut = n.boyut
        except AttributeError:
            continue
        toplam += boyut()
    return toplam
```

```hint
EAFP: `n.boyut`'u oku, `AttributeError` gelirse atla. Ya da `hasattr(n, "boyut")`.
```

```hint
`try` bloğuna sadece nitelik okumayı koy, `boyut()` çağrısını koyma; yoksa metodun **içindeki** bir AttributeError'u da yanlışlıkla yutarsın.
```
:::

::: gorev Salt okunur envanter
`Envanter` sınıfını `collections.abc.Mapping`'ten türet. `Envanter(sozluk)` verilen sözlüğün bir **kopyasını** içeride saklasın. Sadece `__getitem__`, `__iter__` ve `__len__` yaz; `keys`, `items`, `get` ve `in` kendiliğinden çalışmalı. Sınıf atamaya izin vermemeli (`env["x"] = 1` → `TypeError`).

```starter
from collections.abc import Mapping

class Envanter:
    pass
```

```test
from collections.abc import Mapping
E = need("Envanter", "sınıf")
kaynak = {"web01": "10.0.0.5", "db01": "10.0.0.6"}
e = E(kaynak)
ok(isinstance(e, Mapping), "Mapping'ten türemeli")
eq(e["web01"], "10.0.0.5", "e['web01']")
eq(len(e), 2, "len 2")
eq(sorted(e.keys()), ["db01", "web01"], "keys() bedava gelmeli")
eq(e.get("yok", "-"), "-", "get() bedava gelmeli")
ok("db01" in e, "in çalışmalı")
kaynak["yeni"] = "x"
ok("yeni" not in e, "kaynak sözlük değişince envanter etkilenmemeli (kopya)")
try:
    e["x"] = 1
    ok(False, "atama TypeError vermeli")
except TypeError:
    ok(True, "atama TypeError veriyor")
```

```solution
from collections.abc import Mapping

class Envanter(Mapping):
    def __init__(self, sozluk):
        self._veri = dict(sozluk)

    def __getitem__(self, anahtar):
        return self._veri[anahtar]

    def __iter__(self):
        return iter(self._veri)

    def __len__(self):
        return len(self._veri)
```

```hint
`class Envanter(Mapping):` ve içeride `self._veri = dict(sozluk)`. Üç dunder `self._veri`'ye yönlensin.
```

```hint
Mapping'in `__setitem__`'ı yoktur; bu yüzden `e["x"] = 1` kendiliğinden TypeError verir.
```
:::
