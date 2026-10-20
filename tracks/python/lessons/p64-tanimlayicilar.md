---
id: p64
title: Tanımlayıcılar · Descriptor
summary: __get__, __set__, __set_name__; property'yi sıfırdan yazmak, metotların bağlanması ve tembel nitelik.
---

::: anlat property'nin arkasındaki mekanizma
P40'da `@property`, P37'da `@classmethod` kullandın; P63'da `__slots__` gördün. Hepsinin altında aynı protokol yatar: **tanımlayıcı** (descriptor). Tanımlayıcı, **sınıf niteliği** olarak duran ve şu metotlardan en az birine sahip bir nesnedir:

- `__get__(self, nesne, sinif)`: okuma (`nesne.x`)
- `__set__(self, nesne, deger)`: yazma (`nesne.x = ...`)
- `__delete__(self, nesne)`: silme
- `__set_name__(self, sinif, ad)`: sınıf oluşturulurken, tanımlayıcıya hangi isme atandığını söyler (3.6+)

```python
class Pozitif:
    def __set_name__(self, sinif, ad):
        self.ad = ad                          #! "port", "zaman_asimi"...
        self.ozel = "_" + ad                  #! gerçek değerin saklanacağı yer

    def __get__(self, nesne, sinif):
        if nesne is None:                     #! sınıf üzerinden erişim: Baglanti.port
            return self
        return getattr(nesne, self.ozel)

    def __set__(self, nesne, deger):
        if not isinstance(deger, (int, float)) or deger <= 0:
            raise ValueError(f"{self.ad} pozitif bir sayı olmalı: {deger!r}")
        setattr(nesne, self.ozel, deger)

class Baglanti:
    port = Pozitif()                          #! aynı doğrulayıcı...
    zaman_asimi = Pozitif()                   #! ...birden çok alanda yeniden kullanılır

    def __init__(self, port, zaman_asimi):
        self.port = port
        self.zaman_asimi = zaman_asimi

b = Baglanti(443, 2.5)
print(b.port, b.zaman_asimi, vars(b))
try:
    b.zaman_asimi = -1
except ValueError as e:
    print(e)
```

`property` ile her alan için ayrı getter/setter yazman gerekirdi. Tanımlayıcı ise doğrulama mantığını **bir kez** yazıp istediğin kadar alanda kullanmanı sağlar. ORM'lerdeki (`Column(Integer)`) ve form kütüphanelerindeki alanlar böyle çalışır.

### Veri ve veri olmayan tanımlayıcı
- **Veri tanımlayıcısı**: `__set__` (ya da `__delete__`) var → nesnenin `__dict__`'inden **önce** gelir (property bu yüzden ezilemez)
- **Veri olmayan tanımlayıcı**: sadece `__get__` var → nesnenin `__dict__`'i **önce** gelir

Bu fark, P63'daki arama sırasının 1. ve 3. adımlarıdır.
:::

::: tahmin
Çıktı tek satır:

```python
class D:
    def __get__(self, nesne, sinif):
        return "nesneden" if nesne is not None else "sınıftan"

class K:
    a = D()

print(K().a, K.a)
```

???

`nesneden sınıftan`. Sınıf üzerinden erişimde `__get__`'in `nesne` argümanı `None` gelir. İyi yazılmış tanımlayıcılar bu durumda genelde kendilerini döndürür.
:::

::: anlat Metotlar nasıl bağlanır?
Fonksiyonlar da **veri olmayan tanımlayıcıdır**: her fonksiyon nesnesinin bir `__get__` metodu vardır. `k.f` yazdığında Python sınıfta `f` fonksiyonunu bulur ve `f.__get__(k, K)` çağırır; bu çağrı `self`'i `k`'ye sabitlenmiş bir **bağlı metot** (bound method) döndürür:

```python
class K:
    def f(self, x):
        return x * 2

k = K()
fonk = K.__dict__["f"]                    #! sınıf sözlüğündeki çıplak fonksiyon
bagli = fonk.__get__(k, K)                #! k.f'nin arkasında olan tam olarak bu
print(bagli(21), bagli.__self__ is k, bagli.__func__ is fonk)
print(K.f is fonk)                        #! sınıf üzerinden: çıplak fonksiyon (Python 3)
```

`self`'in sihri budur: dil sözdiziminde değil, tanımlayıcı protokolündedir.

### Tembel (önbellekli) nitelik
Veri olmayan tanımlayıcı + nesnenin `__dict__`'ine yazmak = ilk erişimde hesapla, sonra bir daha **tanımlayıcıya hiç uğrama**:

```python
class tembel:
    def __init__(self, fonk):
        self.fonk = fonk
        self.ad = fonk.__name__

    def __get__(self, nesne, sinif):
        if nesne is None:
            return self
        deger = self.fonk(nesne)
        nesne.__dict__[self.ad] = deger       #! artık nesne sözlüğünde, sonraki erişim doğrudan oradan
        return deger

class Rapor:
    @tembel
    def ozet(self):
        print("  (pahalı hesap çalıştı)")
        return 42

r = Rapor()
print(r.ozet)
print(r.ozet)                                 #! hesap ikinci kez çalışmaz
```

Standart kütüphanedeki `functools.cached_property` tam olarak budur.

> [!DERİN]
> `classmethod.__get__` fonksiyonu nesneye değil **sınıfa** bağlar, `staticmethod.__get__` ise hiçbir şeye bağlamadan fonksiyonu olduğu gibi döndürür. `super()` da bir tanımlayıcı gibi çalışan bir vekil nesnedir: MRO'da bir sonraki sınıfın tanımlayıcılarını senin nesnene bağlar. Python'un nesne modelinin tamamı aslında üç parçadan ibarettir: `__getattribute__`, tanımlayıcılar ve MRO.
:::

::: tahmin
Çıktı tek satır:

```python
class K:
    def f(self):
        return 1

k = K()
print(K.f is K.__dict__["f"], k.f == k.f, k.f is k.f, k.f.__self__ is k)
```

???

`True True False True`. Sınıf üzerinden erişim çıplak fonksiyonu verir. `k.f` her erişimde **yeni** bir bağlı metot nesnesi üretir: eşittirler (aynı fonksiyon, aynı nesne) ama aynı nesne değildirler.
:::

::: gorev Aralık doğrulayıcı
`Aralikli(en_az, en_cok)` adında yeniden kullanılabilir bir **veri tanımlayıcısı** yaz. `__set_name__` ile adını öğrensin, değeri nesnenin sözlüğünde `_<ad>` altında saklasın, aralık dışı ya da sayı olmayan değerlerde `ValueError` yükseltsin. Sonra şu sınıfı tanımla:

```python
class Sensor:
    sicaklik = Aralikli(-40, 125)
    nem = Aralikli(0, 100)
```

`Sensor(sicaklik, nem)` kurucusu iki değeri atasın.

```starter
class Aralikli:
    pass

class Sensor:
    pass
```

```test
A = need("Aralikli", "sınıf"); S = need("Sensor", "sınıf")
s = S(21.5, 40)
eq((s.sicaklik, s.nem), (21.5, 40), "değerler")
eq(vars(s), {"_sicaklik": 21.5, "_nem": 40}, "değerler _ad altında saklanmalı")
raises(ValueError, setattr, s, "nem", 101, msg="nem 101 → ValueError")
raises(ValueError, setattr, s, "sicaklik", -41, msg="sıcaklık -41 → ValueError")
raises(ValueError, setattr, s, "nem", "yüksek", msg="metin → ValueError")
ok(isinstance(S.__dict__["nem"], A), "nem bir Aralikli tanımlayıcısı olmalı")
ok(isinstance(S.nem, A), "sınıf üzerinden erişim tanımlayıcının kendisini döndürmeli")
s2 = S(0, 0)
eq((s.nem, s2.nem), (40, 0), "her nesnenin kendi değeri")
```

```solution
class Aralikli:
    def __init__(self, en_az, en_cok):
        self.en_az = en_az
        self.en_cok = en_cok

    def __set_name__(self, sinif, ad):
        self.ad = ad
        self.ozel = "_" + ad

    def __get__(self, nesne, sinif):
        if nesne is None:
            return self
        return getattr(nesne, self.ozel)

    def __set__(self, nesne, deger):
        if isinstance(deger, bool) or not isinstance(deger, (int, float)):
            raise ValueError(f"{self.ad} sayı olmalı")
        if not self.en_az <= deger <= self.en_cok:
            raise ValueError(f"{self.ad} {self.en_az}..{self.en_cok} arası olmalı: {deger}")
        setattr(nesne, self.ozel, deger)


class Sensor:
    sicaklik = Aralikli(-40, 125)
    nem = Aralikli(0, 100)

    def __init__(self, sicaklik, nem):
        self.sicaklik = sicaklik
        self.nem = nem
```

```hint
Değeri tanımlayıcının içinde (`self.deger = ...`) saklama: tanımlayıcı **sınıfa** aittir ve bütün nesneler onu paylaşır. Değeri nesnenin kendisinde sakla: `setattr(nesne, "_" + ad, deger)`.
```
:::

::: gorev Kendi property'n
`ozellik` adında, `property`'nin minik bir klonunu yaz:

- `@ozellik` ile getter tanımlanır
- `@x.setter` ile setter eklenir (yeni bir `ozellik` döndürmeli)
- setter yoksa atama `AttributeError` versin
- sınıf üzerinden erişimde kendisini döndürsün

`property`'yi kullanmak yok.

```starter
class ozellik:
    pass
```

```test
O = need("ozellik", "sınıf")
class Hesap:
    def __init__(self):
        self._b = 0
    @O
    def bakiye(self):
        return self._b
    @bakiye.setter
    def bakiye(self, d):
        if d < 0:
            raise ValueError("negatif")
        self._b = d
    @O
    def durum(self):
        return "aktif"
h = Hesap()
h.bakiye = 50
eq(h.bakiye, 50, "getter/setter")
raises(ValueError, setattr, h, "bakiye", -1, msg="setter doğrulaması çalışmalı")
eq(h.durum, "aktif", "sadece getter")
raises(AttributeError, setattr, h, "durum", "x", msg="setter yoksa AttributeError")
ok(isinstance(Hesap.bakiye, O), "sınıftan erişim kendisini döndürmeli")
ok("bakiye" not in vars(h), "değer nesne sözlüğüne 'bakiye' olarak yazılmamalı")
ok("property" not in src, "property kullanmadan")
```

```solution
class ozellik:
    def __init__(self, getter, setter=None):
        self.getter = getter
        self.setter_fonk = setter

    def __get__(self, nesne, sinif):
        if nesne is None:
            return self
        return self.getter(nesne)

    def __set__(self, nesne, deger):
        if self.setter_fonk is None:
            raise AttributeError("salt okunur")
        self.setter_fonk(nesne, deger)

    def setter(self, fonk):
        return ozellik(self.getter, fonk)
```

```hint
`__init__(self, getter, setter=None)`. `setter` metodu yeni bir `ozellik(self.getter, fonk)` döndürür; sınıf gövdesinde aynı ada atandığı için eskisinin yerini alır.
```

```hint
`__set__` tanımlı olduğu için bu bir **veri** tanımlayıcısıdır: setter yokken bile atama `__set__`'e gelir ve orada reddedilir.
```
:::

::: gorev Tembel nitelik
`tembel` adında bir dekoratör-tanımlayıcı yaz: süslediği metodu ilk erişimde çalıştırıp sonucu **nesnenin sözlüğüne** yazsın; sonraki erişimler tanımlayıcıya hiç uğramasın. `functools.cached_property` kullanmak yok.

```starter
class tembel:
    pass
```

```test
T = need("tembel", "sınıf")
cagri = []
class Rapor:
    def __init__(self, n):
        self.n = n
    @T
    def agir(self):
        cagri.append(self.n)
        return self.n * 100
a, b = Rapor(1), Rapor(2)
eq((a.agir, a.agir, b.agir), (100, 100, 200), "değerler")
eq(cagri, [1, 2], "her nesne için bir kez hesaplanmalı")
ok(vars(a).get("agir") == 100, "sonuç nesne sözlüğüne yazılmalı")
del a.agir
eq(a.agir, 100, "silinince yeniden hesaplanır")
eq(cagri, [1, 2, 1], "silindikten sonra bir kez daha")
ok("cached_property" not in src, "cached_property kullanmadan")
ok(not hasattr(T, "__set__"), "veri olmayan tanımlayıcı olmalı (__set__ yok)")
```

```solution
class tembel:
    def __init__(self, fonk):
        self.fonk = fonk
        self.ad = fonk.__name__

    def __get__(self, nesne, sinif):
        if nesne is None:
            return self
        deger = self.fonk(nesne)
        nesne.__dict__[self.ad] = deger
        return deger
```

```hint
Sadece `__get__` yaz. Sonucu `nesne.__dict__[self.ad]`'a koy; veri olmayan tanımlayıcılarda nesne sözlüğü öncelikli olduğu için sonraki erişim oradan gelir.
```
:::
