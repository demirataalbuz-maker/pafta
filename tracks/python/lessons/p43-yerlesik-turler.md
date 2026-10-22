---
id: p43
title: Yerleşik Türleri Genişletmek
summary: dict, list ve str'den türetmek; C ile yazılmış hızlı yolların ezilen metotları atlaması, __missing__ kancası, collections.UserDict, UserList ve UserString, değiştirilemez türleri (int, str, tuple) __new__ ile özelleştirmek ve işlemlerin taban türü döndürmesi.
kazanim: PCPP1 1.8
---

::: anlat dict'ten türetmek ve sürprizi
Yerleşik türler de birer sınıftır ve onlardan türetebilirsin. Ama `dict`, `list` ve `str` C ile yazılmıştır ve hız için metotları **birbirini çağırmaz**. Bir metodu ezdiğinde, aynı işi yapan öteki metotlar senin sürümünü atlayabilir:

```python
class BuyukHarfSozluk(dict):
    def __setitem__(self, anahtar, deger):
        super().__setitem__(anahtar.upper(), deger)

d = BuyukHarfSozluk(a=1)        #! yapıcı __setitem__'ı ÇAĞIRMAZ
d["b"] = 2                      #! yalnızca bu satır ezilen metodu kullanır
d.update(c=3)                   #! update de çağırmaz
d.setdefault("d", 4)            #! setdefault da
print(sorted(d))
```

| Ezdiğin | Atlayan |
|---|---|
| `dict.__setitem__` | `dict(...)`, `update`, `setdefault`, `fromkeys` |
| `dict.__getitem__` | `get`, `pop`, `items()`, `values()` |
| `list.append` | `extend`, `insert`, `+=`, dilim ataması |

### __missing__
`dict`'in bilerek açık bıraktığı tek kanca `__missing__`'tir: `d[anahtar]` ile okunan anahtar yoksa `KeyError` yerine bu metot çağrılır. `defaultdict` (P32) bunun üzerine kuruludur:

```python
class Sayac(dict):
    def __missing__(self, anahtar):
        return 0                       #! eklemeden 0 döndür

s = Sayac()
for kelime in "web db web".split():
    s[kelime] += 1                     #! okuma → __missing__ → 0, yazma → normal __setitem__
print(s, s["yok"], len(s))             #! "yok" okundu ama eklenmedi
```

`__missing__` yalnızca `d[k]` ile okumada çalışır; `d.get(k)` ve `k in d` onu çağırmaz.
:::

::: anlat UserDict, UserList, UserString
Davranışı gerçekten değiştirmek istiyorsan `collections` modülündeki **User** sınıflarından türet. Bunlar Python ile yazılmıştır, veriyi `self.data` adlı gerçek bir sözlükte (listede, metinde) tutar ve bütün metotlarını **senin ezdiğin temel metotlar üzerinden** kurar:

```python
from collections import UserDict

class BuyukHarfSozluk(UserDict):
    def __setitem__(self, anahtar, deger):
        super().__setitem__(anahtar.upper(), deger)

e = BuyukHarfSozluk(a=1)       #! yapıcı update'i, update de __setitem__'ı çağırır
e.update(c=3)
e.setdefault("d", 4)
print(sorted(e), e.data)
```

| Ne zaman | Seç |
|---|---|
| yalnızca yeni metot ekliyorsan (davranışı değiştirmiyorsan) | `dict` / `list` / `str`: hızlı |
| okuma ve yazmanın **her yolunu** değiştiriyorsan | `UserDict` / `UserList` / `UserString` |
| yalnızca eksik anahtar davranışı | `dict` + `__missing__` |
| sözlük gibi davranan ama tamamen kendi deposu olan bir sınıf | `collections.abc.MutableMapping` (P42): beş metot yaz, gerisi gelir |

### Değiştirilemez türler: __new__
`int`, `str`, `tuple` ve `frozenset` değiştirilemez: değer, nesne **oluşturulurken** belirlenir. `__init__` çalıştığında iş işten geçmiştir; özelleştirme `__new__`'de yapılır:

```python
class Etiket(str):
    def __new__(cls, deger):
        return super().__new__(cls, deger.strip().lower())

e = Etiket("  Prod ")
print(repr(e), isinstance(e, str), type(e + "x").__name__)
```

> [!TUZAK]
> Yerleşik türlerin işlemleri genellikle **taban türü** döndürür: `Etiket` + metin bir `str`'dir, `int`'ten türeyen bir `Port` ile yapılan toplama düz bir `int` verir. Alt sınıfta kalmasını istiyorsan ilgili metodu (`__add__` gibi) kendin ezmelisin.
:::

::: tahmin
İki satır yazar:

```python
from collections import UserDict

class BuyukHarfSozluk(dict):
    def __setitem__(self, k, v):
        super().__setitem__(k.upper(), v)

d = BuyukHarfSozluk(a=1)
d["b"] = 2
d.update(c=3)
print(sorted(d))

class BuyukHarfSozluk2(UserDict):
    def __setitem__(self, k, v):
        super().__setitem__(k.upper(), v)

e = BuyukHarfSozluk2(a=1)
e.update(c=3)
print(sorted(e))
```

???

`['B', 'a', 'c']` ve `['A', 'C']`. `dict`'ten türeyen sınıfta yapıcı ve `update` ezilen `__setitem__`'ı atlar; yalnızca `d["b"]` büyük harfe çevrilir. Büyük harfler küçüklerden önce sıralanır. `UserDict`'te yapıcı ve `update` `__setitem__` üzerinden çalıştığı için iki anahtar da büyük harftir.
:::

::: gorev Eksik anahtarda sıfır
`Sayac` sınıfını `dict`'ten türeterek yaz: olmayan bir anahtar `s[k]` ile okunduğunda `0` döndürsün ama sözlüğe **eklemesin**. Ayrıca `en_cok(n)` metodu, en büyük `n` sayımı `(anahtar, sayı)` çiftleri olarak, sayıya göre azalan (eşitlikte anahtara göre artan) döndürsün.

```starter
class Sayac(dict):
    def en_cok(self, n):
        return []
```

```test
need("Sayac", "sınıf")
s = Sayac()
for k in "web db web cache db web".split():
    s[k] += 1
eq(dict(s), {"web": 3, "db": 2, "cache": 1}, "sayımlar")
eq(s["yok"], 0, "olmayan anahtar 0")
eq(len(s), 3, "okumak anahtarı eklememeli")
eq(s.en_cok(2), [("web", 3), ("db", 2)], "en çok iki")
ok(isinstance(s, dict), "bir dict olmalı")
```

```solution
class Sayac(dict):
    def __missing__(self, anahtar):
        return 0

    def en_cok(self, n):
        return sorted(self.items(), key=lambda c: (-c[1], c[0]))[:n]
```

```hint
`__missing__(self, anahtar)` yalnızca `s[k]` ile okunan anahtar yoksa çağrılır. İçinde `self[anahtar] = 0` yazma; yalnızca `return 0`.
```
:::

::: gorev Harfe duyarsız sözlük
`UserDict`'ten türeyen `KucukHarfSozluk` sınıfını yaz: anahtarlar her zaman küçük harfe çevrilerek saklansın; okuma (`d["WEB"]`), `in`, silme ve `get` de harfe duyarsız çalışsın. Yapıcı ve `update` de bu kurala uymalı.

```starter
class KucukHarfSozluk(dict):
    def __setitem__(self, anahtar, deger):
        super().__setitem__(anahtar.lower(), deger)
```

```test
need("KucukHarfSozluk", "sınıf")
d = KucukHarfSozluk({"Web": 1})
d.update(DB=2)
d["Cache"] = 3
eq(sorted(d), ["cache", "db", "web"], "anahtarlar küçük harf")
eq(d["WEB"], 1, "harfe duyarsız okuma")
ok("dB" in d, "harfe duyarsız in")
eq(d.get("CACHE"), 3, "harfe duyarsız get")
eq(d.get("yok", 0), 0, "get varsayılanı")
del d["DB"]
eq(sorted(d), ["cache", "web"], "harfe duyarsız silme")
```

```solution
from collections import UserDict


class KucukHarfSozluk(UserDict):
    def __setitem__(self, anahtar, deger):
        super().__setitem__(anahtar.lower(), deger)

    def __getitem__(self, anahtar):
        return super().__getitem__(anahtar.lower())

    def __delitem__(self, anahtar):
        super().__delitem__(anahtar.lower())

    def __contains__(self, anahtar):
        return anahtar.lower() in self.data
```

```hint
`dict`'ten türetince yapıcı ve `update` ezilen `__setitem__`'ı atlıyor. `UserDict`'ten türet: öteki metotlar senin temel metotlarını çağırır.
```

```hint
Dört temel metodu ez: `__setitem__`, `__getitem__`, `__delitem__`, `__contains__`. `get` ve `update` bunların üzerinden çalışır. Veri `self.data` sözlüğünde durur.
```
:::

::: gorev Doğrulanmış port
`int`'ten türeyen `Port` sınıfını yaz: oluşturulurken değeri tam sayıya çevirsin (`Port("443")` geçerli), 0–65535 dışındaysa `ValueError` fırlatsın ve `repr`'ı `Port(443)` biçiminde olsun. Değiştirilemez bir tür olduğu için işi `__new__`'de yap.

```starter
class Port(int):
    def __init__(self, deger):
        if not 0 <= int(deger) <= 65535:
            raise ValueError("geçersiz port")
```

```test
need("Port", "sınıf")
p = Port("443")
eq(repr(p), "Port(443)", "repr")
ok(p == 443 and isinstance(p, int), "bir int gibi davranır")
raises(ValueError, Port, 70000, msg="aralık dışı")
raises(ValueError, Port, -1, msg="negatif")
eq((repr(Port(0)), repr(Port(65535))), ("Port(0)", "Port(65535)"), "0 ve 65535 sınırları geçerli")
raises(ValueError, Port, 65536, msg="65536 aralık dışı")
eq(type(p + 1).__name__, "int", "işlemler taban türü döndürür")
eq(sorted([Port(8080), Port(22), Port(443)]), [22, 443, 8080], "sayı gibi sıralanır")
```

```solution
class Port(int):
    def __new__(cls, deger):
        n = int(deger)
        if not 0 <= n <= 65535:
            raise ValueError(f"geçersiz port: {n}")
        return super().__new__(cls, n)

    def __repr__(self):
        return f"Port({int(self)})"
```

```hint
`__init__` çalıştığında değer çoktan oluşturulmuştur ve `Port("443")` metni saklamaya çalışır. `__new__(cls, deger)` içinde önce `int(deger)`, sonra denetim, sonra `super().__new__(cls, n)`.
```

```hint
`__repr__`'da `int(self)` kullan; `repr(self)` yazarsan kendini sonsuza dek çağırır.
```
:::
