---
id: p38
title: Dunder Metotlar · Veri Modeli
summary: __repr__, __eq__, __hash__, __lt__, __len__, __getitem__, __iter__, __add__, __call__.
---

::: anlat Python'un işleçleri birer metot çağrısıdır
`a + b` yazdığında Python aslında `a.__add__(b)` çağırır. `len(x)` → `x.__len__()`, `x[i]` → `x.__getitem__(i)`, `print(x)` → `x.__str__()`. Çift alt çizgili (**d**ouble **under**score, kısaca **dunder**) bu metotları kendi sınıfında tanımlarsan, nesnelerin Python'un yerleşik türleri gibi davranır. Buna Python'un **veri modeli** denir.

```python
class Para:
    def __init__(self, kurus):
        self.kurus = kurus

    def __repr__(self):                      #! geliştirici için: belirsizlik yok
        return f"Para({self.kurus})"

    def __str__(self):                       #! kullanıcı için: okunaklı
        return f"{self.kurus // 100},{self.kurus % 100:02d} TL"

    def __add__(self, diger):                #! a + b
        return Para(self.kurus + diger.kurus)

    def __eq__(self, diger):                 #! a == b
        return isinstance(diger, Para) and self.kurus == diger.kurus

    def __lt__(self, diger):                 #! a < b (sorted bunu kullanır)
        return self.kurus < diger.kurus

    def __bool__(self):                      #! if para:
        return self.kurus != 0

a, b = Para(1999), Para(1)
print(a + b, repr(a + b))
print(a == Para(1999), a < b, sorted([a, b]))
print(bool(Para(0)), [a])                    #! listeler elemanları repr ile gösterir
```

| Kural | Dunder |
|---|---|
| `repr(x)`, etkileşimli ekran, listelerin içi | `__repr__` |
| `str(x)`, `print(x)`, f-string | `__str__` (yoksa `__repr__`) |
| `==`, `<`, `<=`... | `__eq__`, `__lt__`, `__le__`... |
| `+`, `-`, `*`, `@` | `__add__`, `__sub__`, `__mul__`, `__matmul__` |
| `hash(x)`, dict anahtarı, set elemanı | `__hash__` |

> [!TUZAK]
> `__eq__` tanımlarsan Python sınıfının `__hash__`'ini **`None` yapar**: nesnelerin artık sözlük anahtarı ya da küme elemanı olamaz. Eşitlik değerden geliyorsa ve nesne değiştirilemezse `__hash__`'i de aynı alanlardan tanımla: `return hash(self.kurus)`. Eşit nesnelerin hash'i **mutlaka** eşit olmalıdır.
:::

::: tahmin
Çıktı tek satır:

```python
class P:
    def __init__(self, x):
        self.x = x
    def __repr__(self):
        return f"P({self.x})"
    def __add__(self, o):
        return P(self.x + o.x)
    def __eq__(self, o):
        return self.x == o.x

print(P(1) + P(2), P(3) == P(3), [P(5)])
```

???

`P(3) True [P(5)]`. `+` işleci `__add__`'i çağırır. `__str__` olmadığı için print `__repr__`'ı kullanır. `__eq__` tanımlandığı için `==` değer karşılaştırması yapar.
:::

::: anlat Kendi koleksiyonun
Birkaç dunder ile kendi sınıfın **gerçek bir koleksiyon** gibi davranır:

```python
class KayitDefteri:
    def __init__(self):
        self._kayitlar = []

    def ekle(self, k):
        self._kayitlar.append(k)

    def __len__(self):                       #! len(defter)
        return len(self._kayitlar)

    def __getitem__(self, i):                #! defter[i], defter[1:3]
        return self._kayitlar[i]

    def __contains__(self, aranan):          #! "x" in defter
        return any(aranan in k for k in self._kayitlar)

    def __iter__(self):                      #! for k in defter
        return iter(self._kayitlar)

    def __call__(self, kelime):              #! defter("FAIL") — nesneyi fonksiyon gibi çağır
        return [k for k in self._kayitlar if kelime in k]

d = KayitDefteri()
for s in ["OK ali", "FAIL root", "FAIL admin"]:
    d.ekle(s)
print(len(d), d[0], d[-2:], "root" in d)
print([k.split()[1] for k in d])
print(d("FAIL"))
```

> [!DERİN]
> Python dunder'ları **sınıfta** arar, nesnede değil: `d.__len__ = lambda: 5` diye nesneye atamak `len(d)`'yi değiştirmez. Ayrıca bazı fallback'ler vardır: `__iter__` yoksa `for` döngüsü `__getitem__`'ı 0'dan başlayarak `IndexError` gelene kadar çağırır. `__contains__` yoksa `in` yineleme yapar. `__bool__` yoksa `__len__`'e bakar. `a + b`'de `a.__add__` `NotImplemented` döndürürse Python `b.__radd__(a)`'yı dener; `sum()` bu yüzden `0 + nesne` ile başladığında `__radd__` ister.
:::

::: tahmin
Çıktı tek satır:

```python
class Kume:
    def __init__(self, *e):
        self.e = list(e)
    def __len__(self):
        return len(self.e)
    def __getitem__(self, i):
        return self.e[i]

k = Kume(10, 20, 30)
print(len(k), k[-1], 20 in k, list(k), bool(Kume()))
```

???

`3 30 True [10, 20, 30] False`. Sadece `__len__` ve `__getitem__` tanımlandı ama `in`, `list()` ve `bool()` da çalıştı: `in` ve yineleme `__getitem__` fallback'ini, `bool` ise `__len__`'i kullanır.
:::

::: gorev Vektör
`Vektor(x, y)` sınıfını yaz:

- `repr` → `Vektor(1, 2)`
- `v + w` → bileşen bileşen toplam (yeni Vektor)
- `v * k` → sayıyla çarpım (yeni Vektor)
- `v == w` → bileşenler eşitse True
- `abs(v)` → uzunluk (`math.hypot`)
- Vektörler küme elemanı olabilsin (`__hash__`)

```starter
import math

class Vektor:
    def __init__(self, x, y):
        self.x = x
        self.y = y
```

```test
V = need("Vektor", "sınıf")
eq(repr(V(1, 2)), "Vektor(1, 2)", "repr")
eq(V(1, 2) + V(3, 4), V(4, 6), "toplama")
eq(V(1, 2) * 3, V(3, 6), "sayıyla çarpım")
ok(V(1, 2) != V(2, 1), "farklı vektörler eşit değil")
yakin(abs(V(3, 4)), 5.0, "abs(Vektor(3, 4)) → 5.0")
eq(len({V(1, 1), V(1, 1), V(2, 2)}), 2, "kümede tekrarlar birleşir (__hash__)")
a = V(1, 1); _ = a + V(1, 1)
eq((a.x, a.y), (1, 1), "toplama yeni nesne üretmeli, a değişmemeli")
```

```solution
import math

class Vektor:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Vektor({self.x}, {self.y})"

    def __add__(self, o):
        return Vektor(self.x + o.x, self.y + o.y)

    def __mul__(self, k):
        return Vektor(self.x * k, self.y * k)

    def __eq__(self, o):
        return isinstance(o, Vektor) and (self.x, self.y) == (o.x, o.y)

    def __hash__(self):
        return hash((self.x, self.y))

    def __abs__(self):
        return math.hypot(self.x, self.y)
```

```hint
`__eq__` tanımlayınca `__hash__` de gerekir: `return hash((self.x, self.y))`.
```
:::

::: gorev Sürüm karşılaştırma
Yazılım sürümlerini metin olarak karşılaştırmak yanlıştır: `"1.10.0" < "1.9.0"` metin olarak doğrudur! `Surum("1.10.2")` sınıfı sürümleri **sayısal** karşılaştırsın:

- `==`, `<`, `>`, `<=`, `>=` çalışsın (`functools.total_ordering` ile sadece `__eq__` ve `__lt__` yazman yeter)
- `str(s)` orijinal metni versin
- `sorted` doğru sıralasın

```starter
from functools import total_ordering

class Surum:
    def __init__(self, metin):
        self.metin = metin
```

```test
S = need("Surum", "sınıf")
ok(S("1.10.0") > S("1.9.0"), "1.10.0 > 1.9.0")
ok(S("2.0") == S("2.0"), "2.0 == 2.0")
ok(S("1.2.3") <= S("1.2.3"), "<= eşitlikte doğru")
ok(S("0.9.9") < S("1.0.0"), "0.9.9 < 1.0.0")
eq(str(S("3.1.4")), "3.1.4", "str orijinal metin")
eq([str(x) for x in sorted([S("1.10.0"), S("1.2.0"), S("1.9.1"), S("1.2.10")])], ["1.2.0", "1.2.10", "1.9.1", "1.10.0"], "sayısal sıralama")
ok(S("1.2") != S("1.3"), "!= çalışmalı")
ok(not (S("1.2") < S("1.2")), "aynı sürüm: v < v False")
ok(not (S("1.2") > S("1.2")), "aynı sürüm: v > v False")
```

```solution
from functools import total_ordering

@total_ordering
class Surum:
    def __init__(self, metin):
        self.metin = metin
        self.parcalar = tuple(int(p) for p in metin.split("."))

    def __eq__(self, o):
        return self.parcalar == o.parcalar

    def __lt__(self, o):
        return self.parcalar < o.parcalar

    def __str__(self):
        return self.metin
```

```hint
Sürümü bir int demetine çevir: `tuple(int(p) for p in metin.split("."))`. Demetler zaten sözlük sırasıyla karşılaştırılır.
```

```hint
Sınıfın üstüne `@total_ordering` koyarsan `__eq__` + `__lt__`'den diğer dört karşılaştırma üretilir.
```
:::

::: gorev Olay penceresi
`Pencere` sınıfı, eklenen son **n** olayı tutan sabit boyutlu bir koleksiyon olsun:

- `Pencere(n)`, `ekle(olay)`
- `len(p)`: içindeki olay sayısı (en fazla n)
- `p[i]`: i. olay (0 = en eski; negatif indeks ve dilim de çalışsın)
- `x in p` ve `for olay in p` çalışsın
- `repr(p)` → `Pencere(3/5)` (içindeki/kapasite)

```starter
class Pencere:
    def __init__(self, n):
        self.n = n
```

```test
P = need("Pencere", "sınıf")
p = P(3)
for o in ["a", "b", "c", "d"]:
    p.ekle(o)
eq(len(p), 3, "kapasite 3")
eq(p[0], "b", "en eski 'a' düştü, p[0] = 'b'")
eq(p[-1], "d", "p[-1] = 'd'")
eq(p[0:2], ["b", "c"], "dilim liste döndürür")
ok("c" in p and "a" not in p, "in çalışmalı")
eq(list(p), ["b", "c", "d"], "yineleme")
eq(repr(P(5)), "Pencere(0/5)", "boş pencere repr")
eq(repr(p), "Pencere(3/3)", "dolu pencere repr")
```

```solution
from collections import deque

class Pencere:
    def __init__(self, n):
        self.n = n
        self._q = deque(maxlen=n)

    def ekle(self, olay):
        self._q.append(olay)

    def __len__(self):
        return len(self._q)

    def __getitem__(self, i):
        return list(self._q)[i]

    def __contains__(self, x):
        return x in self._q

    def __iter__(self):
        return iter(self._q)

    def __repr__(self):
        return f"Pencere({len(self)}/{self.n})"
```

```hint
İçeride `deque(maxlen=n)` tut. deque dilimlemeyi desteklemez; `__getitem__` içinde `list(...)` ile çevirip indeksle.
```
:::
