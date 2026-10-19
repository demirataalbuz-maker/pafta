---
id: p63
title: Bellek Modeli
summary: Referans sayımı, del'in gerçek anlamı, döngüsel çöp toplama, weakref, getsizeof ve tracemalloc.
---

::: anlat Referans sayımı
CPython'da her nesnenin bir **referans sayacı** vardır: o nesneyi gösteren kaç isim, liste elemanı, nitelik... olduğu. Sayaç sıfıra düştüğü **anda** nesne yok edilir ve belleği geri verilir.

```python
import sys

a = [1, 2, 3]
print(sys.getrefcount(a) - 1)       #! getrefcount'un kendi argümanı da geçici bir referanstır
b = a
kutu = [a, a]
print(sys.getrefcount(a) - 1)       #! a, b ve listedeki iki eleman
del b                               #! del İSMİ siler, nesneyi değil
kutu.clear()
print(sys.getrefcount(a) - 1)
```

**`del x` nesneyi silmez**, sadece `x` ismini (bir referansı) kaldırır. Nesne, son referansı gidince yok olur.

```python
class Kaynak:
    def __init__(self, ad):
        self.ad = ad
        print(f"  {ad} oluştu")
    def __del__(self):                       #! nesne yok edilirken çağrılır
        print(f"  {self.ad} yok edildi")

k = Kaynak("bağlantı-1")
k2 = k
del k
print("del k sonrası (k2 hâlâ tutuyor)")
k2 = None                                    #! son referans gitti → hemen yok edilir
print("bitti")
```

> [!TUZAK]
> `__del__`'e kritik temizlik işi (dosya kapatma, kilit bırakma) yükleme: ne zaman çalışacağı garanti değildir (döngüsel referanslarda gecikir, program kapanırken hiç çalışmayabilir) ve içinde oluşan hatalar yutulur. Kaynak yönetimi için `with` (P46) kullan.

### Döngüsel referanslar ve gc
Referans sayımının çözemediği bir durum var: **döngüler**. A, B'yi; B de A'yı gösteriyorsa, dışarıdan hiçbir isim kalmasa bile sayaçlar sıfıra inmez. Bunun için CPython'un ikinci bir mekanizması var: **çöp toplayıcı** (`gc`), periyodik olarak ulaşılamayan döngüleri bulur:

```python
import gc

class Dugum:
    def __init__(self, ad):
        self.ad = ad
        self.komsu = None

a, b = Dugum("a"), Dugum("b")
a.komsu, b.komsu = b, a                      #! döngü
del a, b                                     #! sayaçlar hâlâ 1: döngü kendini tutuyor
print("toplanan nesne:", gc.collect())       #! döngüsel çöpü elle topla
```
:::

::: tahmin
İki satır:

```python
import sys
a = []
b = a
print(sys.getrefcount(a) - 1)
del b
print(sys.getrefcount(a) - 1)
```

???

`2`, sonra `1`. Önce `a` ve `b` isimleri aynı listeyi gösteriyor. `del b` sadece bir ismi kaldırır; liste hâlâ `a` ile yaşar. (`- 1`, getrefcount'a argüman olarak geçerken oluşan geçici referansı düşmek için.)
:::

::: anlat Zayıf referanslar, boyut ve izleme
**Zayıf referans** (weakref) bir nesneyi **sayacı artırmadan** gösterir: nesne başka yerde yaşadığı sürece erişebilirsin, son güçlü referans gidince zayıf referans `None` döner. Önbellekler ve gözlemci listeleri için idealdir, çünkü tuttuğun şeyi sırf sen tuttuğun için ölümsüz yapmazsın:

```python
import weakref

class Oturum:
    def __init__(self, kullanici):
        self.kullanici = kullanici

o = Oturum("ali")
zayif = weakref.ref(o)
print(zayif() is o)                     #! hâlâ yaşıyor
del o
print(zayif())                          #! None: son güçlü referans gitti

onbellek = weakref.WeakValueDictionary()   #! değerleri zayıf tutan sözlük
x = Oturum("veli")
onbellek["veli"] = x
print(list(onbellek))
del x
print(list(onbellek))                   #! nesne ölünce kayıt kendiliğinden düştü
```

### Ne kadar bellek?
```python
import sys, tracemalloc

print(sys.getsizeof(0), sys.getsizeof(2**100))      #! int bile ~28 bayt
print(sys.getsizeof([]), sys.getsizeof([1, 2, 3]))  #! sadece listenin KENDİSİ
print(sys.getsizeof(["x" * 1000]))                   #! içindeki 1000 karakterlik metin dahil DEĞİL!

tracemalloc.start()
veri = [str(i) * 10 for i in range(10000)]
simdi, tepe = tracemalloc.get_traced_memory()
tracemalloc.stop()
print(f"tepe: {tepe / 1024:.0f} KB")
```

`getsizeof` **sığdır**: bir konteynerin içindekileri saymaz. Gerçek ayak izini bulmak için içerideki nesneleri de özyinelemeli toplaman gerekir (bu paftanın ilk görevi).

> [!DERİN]
> CPython küçük nesneler için kendi bellek ayırıcısını kullanır (**pymalloc**: 512 bayta kadar nesneler, "arena → havuz → blok" düzeni). Serbest bırakılan bellek genelde işletim sistemine hemen dönmez, Python tarafından yeniden kullanılmak üzere tutulur. Bu yüzden büyük bir listeyi silince süreç belleği düşmeyebilir. Listeler ayrıca büyürken **fazladan yer ayırır** (over-allocation); `append` bu sayede ortalama O(1)'dir.
:::

::: tahmin
İki satır:

```python
import weakref

class Nesne:
    pass

n = Nesne()
r = weakref.ref(n)
print(r() is n)
del n
print(r())
```

???

`True`, sonra `None`. Zayıf referans nesneyi canlı tutmaz. CPython'da referans sayısı sıfıra indiği **anda** nesne yok edilir, bu yüzden `del n`'den hemen sonra `r()` None döner.
:::

::: gorev Derin boyut
`derin_boyut(x)` bir nesnenin **içindekilerle birlikte** toplam bellek boyutunu (`sys.getsizeof` toplamı) döndürsün:

- `list`, `tuple`, `set`, `frozenset` elemanlarına ve `dict`'in anahtar ve değerlerine özyinelemeli in
- Aynı nesne birden fazla yerden gösteriliyorsa **bir kez** say (`id` ile takip et)
- Kendi kendini içeren yapılarda sonsuz döngüye girme

```starter
import sys

def derin_boyut(x):
    return sys.getsizeof(x)
```

```test
import sys
need("derin_boyut")
eq(derin_boyut(42), sys.getsizeof(42), "düz sayı")
m = "x" * 500
eq(derin_boyut([m]), sys.getsizeof([m]) + sys.getsizeof(m), "liste + içindeki metin")
eq(derin_boyut([m, m]), sys.getsizeof([m, m]) + sys.getsizeof(m), "aynı nesne bir kez sayılır")
d = {"a": [1, 2]}
eq(derin_boyut(d), sys.getsizeof(d) + sys.getsizeof("a") + sys.getsizeof(d["a"]) + sys.getsizeof(1) + sys.getsizeof(2), "sözlük anahtar ve değerleri")
dongu = []
dongu.append(dongu)
eq(derin_boyut(dongu), sys.getsizeof(dongu), "kendini içeren liste sonsuz döngüye girmemeli")
```

```solution
import sys

def derin_boyut(x, _gorulen=None):
    if _gorulen is None:
        _gorulen = set()
    if id(x) in _gorulen:
        return 0
    _gorulen.add(id(x))
    toplam = sys.getsizeof(x)
    if isinstance(x, dict):
        for k, v in x.items():
            toplam += derin_boyut(k, _gorulen) + derin_boyut(v, _gorulen)
    elif isinstance(x, (list, tuple, set, frozenset)):
        for e in x:
            toplam += derin_boyut(e, _gorulen)
    return toplam
```

```hint
Görülen nesnelerin `id`'lerini bir kümede taşı. Kümede varsa 0 döndür; böylece hem tekrarlar hem döngüler çözülür.
```

```hint
Varsayılan argüman olarak `_gorulen=set()` YAZMA (P21'deki tuzak!): `None` ver ve içeride oluştur.
```
:::

::: gorev Zayıf önbellek
`NesneOnbellegi` sınıfı pahalı nesneleri anahtarla saklasın ama onları **canlı tutmasın**:

- `getir(anahtar, fabrika)`: önbellekte canlı bir nesne varsa onu, yoksa `fabrika()` ile yenisini üretip saklayıp döndürsün
- `len(onbellek)`: hâlâ canlı olan nesne sayısı

`weakref.WeakValueDictionary` kullan.

```starter
import weakref

class NesneOnbellegi:
    def __init__(self):
        self._depo = {}

    def getir(self, anahtar, fabrika):
        if anahtar not in self._depo:
            self._depo[anahtar] = fabrika()
        return self._depo[anahtar]

    def __len__(self):
        return len(self._depo)
```

```test
import gc
N = need("NesneOnbellegi", "sınıf")
class Pahali:
    uretilen = 0
    def __init__(self):
        Pahali.uretilen += 1
c = N()
a = c.getir("x", Pahali)
b = c.getir("x", Pahali)
ok(a is b, "canlı nesne yeniden kullanılır")
eq(Pahali.uretilen, 1, "bir kez üretildi")
eq(len(c), 1, "1 canlı nesne")
del a, b
gc.collect()
eq(len(c), 0, "dışarıda referans kalmayınca önbellekten düşmeli")
c.getir("x", Pahali)
eq(Pahali.uretilen, 2, "ölen nesne yeniden üretilir")
```

```solution
import weakref

class NesneOnbellegi:
    def __init__(self):
        self._depo = weakref.WeakValueDictionary()

    def getir(self, anahtar, fabrika):
        nesne = self._depo.get(anahtar)
        if nesne is None:
            nesne = fabrika()
            self._depo[anahtar] = nesne
        return nesne

    def __len__(self):
        return len(self._depo)
```

```hint
`self._depo = weakref.WeakValueDictionary()`. `getir` içinde nesneyi önce **yerel bir değişkene** al: `in` kontrolü ile okuma arasında nesne ölebilir.
```
:::

::: gorev Döngü dedektörü
`dongu_var_mi(x)` iç içe listeler ve sözlüklerden oluşan bir yapı, **kendi atasını** (yolun üzerindeki bir konteyneri) gösteriyorsa `True` döndürsün. Aynı nesnenin iki farklı daldan gösterilmesi döngü **değildir**.

```starter
def dongu_var_mi(x):
    pass
```

```test
need("dongu_var_mi")
a = [1, [2, 3]]
eq(dongu_var_mi(a), False, "döngüsüz liste")
paylasilan = [9]
eq(dongu_var_mi([paylasilan, paylasilan]), False, "paylaşılan alt liste döngü değildir")
b = [1, 2]
b.append(b)
eq(dongu_var_mi(b), True, "kendini içeren liste")
d = {"ad": "kok", "cocuk": {"ad": "alt"}}
d["cocuk"]["ebeveyn"] = d
eq(dongu_var_mi(d), True, "çocuğun ebeveynini göstermesi")
eq(dongu_var_mi({"a": [{"b": []}]}), False, "derin ama döngüsüz")
```

```solution
def dongu_var_mi(x, _yol=None):
    if _yol is None:
        _yol = set()
    if not isinstance(x, (list, dict)):
        return False
    if id(x) in _yol:
        return True
    _yol.add(id(x))
    ogeler = x.values() if isinstance(x, dict) else x
    sonuc = any(dongu_var_mi(o, _yol) for o in ogeler)
    _yol.discard(id(x))
    return sonuc
```

```hint
"Görülenler" yerine "şu anki yol" kümesi tut: bir konteynere girerken ekle, çıkarken çıkar. Yolda olan bir nesneyle tekrar karşılaşmak döngüdür; yolda olmayan ama daha önce görülmüş bir nesne ise sadece paylaşılmıştır.
```
:::
