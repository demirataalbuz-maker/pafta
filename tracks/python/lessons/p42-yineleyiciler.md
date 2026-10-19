---
id: p42
title: Yineleyici Protokolü
summary: iter ve next, StopIteration, for döngüsünün iç yüzü, yinelenebilir ile yineleyici farkı.
---

::: anlat for döngüsünün sırrı
`for x in dizi:` yazdığında Python perde arkasında iki şey yapar:

1. `iter(dizi)` çağırıp bir **yineleyici** (iterator) alır
2. `next(yineleyici)`'yi tekrar tekrar çağırır; yineleyici `StopIteration` yükselttiğinde döngüyü bitirir

```python
portlar = [22, 80, 443]
it = iter(portlar)            #! listeden bir yineleyici al
print(next(it))               #! 22
print(next(it))               #! 80
print(next(it))               #! 443
try:
    next(it)                  #! bitti
except StopIteration:
    print("StopIteration: eleman kalmadı")

# for döngüsünün elle yazılmış hali:
it = iter(portlar)
while True:
    try:
        p = next(it)
    except StopIteration:
        break
    print("port", p)
```

İki kavramı ayır:

- **Yinelenebilir** (iterable): üzerinde dolaşılabilen şey. `iter()` ile yineleyici üretir. Liste, metin, sözlük, küme, dosya, range...
- **Yineleyici** (iterator): "sıradaki eleman nerede" durumunu tutan nesne. `next()` ile ilerler ve **bir kez tükenir**.

Liste bir yinelenebilirdir: her `for` döngüsü ondan **yeni** bir yineleyici alır, bu yüzden listeyi tekrar tekrar dolaşabilirsin. `zip`, `map`, `enumerate`, `reversed`, `filter` ve açık dosyalar ise **doğrudan yineleyicidir**: bir kez dolaştın mı biterler.
:::

::: tahmin
İki satır:

```python
it = iter([10, 20, 30])
print(next(it), next(it))
print(list(it), list(it))
```

???

`10 20`, sonra `[30] []`. Yineleyici kaldığı yeri hatırlar: ilk `list(it)` kalan tek elemanı alır, ikincisi tükenmiş yineleyiciden hiçbir şey alamaz.
:::

::: anlat Kendi yineleyicin
Yineleyici protokolü iki dunder'dır:

- `__iter__()`: yineleyiciyi döndürür (yineleyicinin kendisi için `return self`)
- `__next__()`: sıradaki elemanı döndürür ya da `StopIteration` yükseltir

```python
class GeriSayim:
    def __init__(self, n):
        self.n = n

    def __iter__(self):
        return self

    def __next__(self):
        if self.n <= 0:
            raise StopIteration
        self.n -= 1
        return self.n + 1

g = GeriSayim(3)
print(list(g))
print(list(g))                 #! bir kez tükendi: []
```

Tekrar tekrar dolaşılabilen bir koleksiyon istiyorsan **yinelenebilir** ile **yineleyiciyi** ayır: koleksiyonun `__iter__`'i her seferinde **yeni** bir yineleyici döndürmeli:

```python
class Aralik:
    def __init__(self, bas, son):
        self.bas, self.son = bas, son

    def __iter__(self):                  #! her çağrıda taze bir yineleyici
        return iter(range(self.bas, self.son))

a = Aralik(1, 4)
print(list(a), list(a))                  #! iki kez de çalışır
```

> [!DERİN]
> `iter()`'in az bilinen iki argümanlı hali: `iter(fonksiyon, durdurucu)`. Fonksiyonu tekrar tekrar çağırır ve durdurucu değer gelince durur. Bir dosyayı 4 KB'lık bloklar halinde okumak için klasik kalıp şudur: `for blok in iter(lambda: f.read(4096), b""):`. Ayrıca bir şey `__iter__` olmadan da yinelenebilir: `__getitem__` 0'dan başlayıp `IndexError` gelene kadar çağrılır (P38'deki fallback).
:::

::: tahmin
Üç satır:

```python
z = zip("ab", [1, 2])
print(list(z))
print(list(z))
e = enumerate([7, 8, 9])
print(next(e), type(e).__name__)
```

???

`[('a', 1), ('b', 2)]`, `[]`, `(0, 7) enumerate`. zip bir yineleyicidir ve ikinci dolaşmada boştur. enumerate da öyledir; `next` ile ilk demeti tek başına alabilirsin.
:::

::: gorev Geri sayım yineleyicisi
`GeriSayim(n)` sınıfını **yineleyici protokolüyle** yaz: n'den 1'e kadar sayıları versin. Üreteç (`yield`) kullanma; `__iter__` ve `__next__` yaz.

```starter
class GeriSayim:
    def __init__(self, n):
        self.n = n
```

```test
G = need("GeriSayim", "sınıf")
eq(list(G(5)), [5, 4, 3, 2, 1], "GeriSayim(5) → 5..1")
eq(list(G(0)), [], "GeriSayim(0) → boş")
g = G(2)
ok(iter(g) is g, "__iter__ self döndürmeli")
eq(next(g), 2, "next → 2")
eq(next(g), 1, "next → 1")
raises(StopIteration, next, g, msg="sonra StopIteration")
ok(not uses("yield"), "yield kullanmadan")
```

```solution
class GeriSayim:
    def __init__(self, n):
        self.n = n

    def __iter__(self):
        return self

    def __next__(self):
        if self.n <= 0:
            raise StopIteration
        self.n -= 1
        return self.n + 1
```

```hint
`__next__` içinde n 0 ya da altındaysa `raise StopIteration`; değilse n'i azalt ve eski değeri döndür.
```
:::

::: gorev Tekrar dolaşılabilen aralık
`Aralik(bas, son, adim=1)` sınıfı bir **yinelenebilir** olsun: her `for` döngüsünde baştan başlasın. `range` kullanmadan, `__iter__` içinde kendi yineleyici mantığını kur (ister yardımcı bir sınıf, ister `yield` kullan). Ayrıca `len()` desteklesin.

```starter
class Aralik:
    def __init__(self, bas, son, adim=1):
        self.bas = bas
        self.son = son
        self.adim = adim
```

```test
A = need("Aralik", "sınıf")
a = A(0, 10, 3)
eq(list(a), [0, 3, 6, 9], "Aralik(0, 10, 3)")
eq(list(a), [0, 3, 6, 9], "ikinci dolaşma da aynı")
eq(len(a), 4, "len 4")
eq(list(A(5, 5)), [], "boş aralık")
eq(len(A(1, 2)), 1, "len 1")
ok(iter(a) is not a, "__iter__ her seferinde yeni yineleyici döndürmeli (self değil)")
ok(not calls("range"), "range kullanmadan")
```

```solution
class Aralik:
    def __init__(self, bas, son, adim=1):
        self.bas = bas
        self.son = son
        self.adim = adim

    def __iter__(self):
        x = self.bas
        while x < self.son:
            yield x
            x += self.adim

    def __len__(self):
        return max(0, (self.son - self.bas + self.adim - 1) // self.adim)
```

```hint
`__iter__` içine `yield` koyarsan her çağrı yeni bir üreteç (yineleyici) döndürür. P43'te bunun nasıl çalıştığını göreceksin.
```

```hint
Uzunluk: `(son - bas + adim - 1) // adim`, negatifse 0.
```
:::

::: gorev Parçalara böl
`parcalar(yinelenebilir, n)` fonksiyonu elemanları n'li **demetler** halinde gruplayıp liste olarak döndürsün; son grup eksik kalabilir. Girdi **tek geçişlik** bir üreteç bile olabilir; `len()` ya da dilimleme kullanma. `iter` ve `itertools.islice` kullan.

```starter
from itertools import islice

def parcalar(yinelenebilir, n):
    pass
```

```test
need("parcalar")
eq(parcalar([1, 2, 3, 4, 5], 2), [(1, 2), (3, 4), (5,)], "[1..5], 2 → üç grup")
eq(parcalar((x for x in range(6)), 3), [(0, 1, 2), (3, 4, 5)], "üreteç girdisi")
eq(parcalar([], 4), [], "boş → []")
eq(parcalar("abcdefg", 3), [("a", "b", "c"), ("d", "e", "f"), ("g",)], "metin")
```

```solution
from itertools import islice

def parcalar(yinelenebilir, n):
    it = iter(yinelenebilir)
    sonuc = []
    while True:
        grup = tuple(islice(it, n))
        if not grup:
            return sonuc
        sonuc.append(grup)
```

```hint
Önce `it = iter(yinelenebilir)`. Sonra döngüde `tuple(islice(it, n))`; aynı yineleyiciden aldığın için her seferinde kaldığı yerden devam eder. Boş demet gelince dur.
```
:::
