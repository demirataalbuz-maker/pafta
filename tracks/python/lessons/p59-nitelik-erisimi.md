---
id: p59
title: Nitelik Erişimi ve __slots__
summary: nesne.x arkasındaki arama sırası, __getattr__, __getattribute__, __setattr__ ve __slots__ ile bellek.
---

::: anlat nesne.x yazınca gerçekte ne olur?
`k.x` gibi masum bir ifade, perde arkasında `type(k).__getattribute__(k, "x")` çağrısıdır. Varsayılan `object.__getattribute__` şu sırayla arar:

1. Sınıf (ve MRO'su) içinde `x` adlı bir **veri tanımlayıcısı** (data descriptor: `__get__` ve `__set__` olan bir şey, ör. `property`) varsa onu kullan
2. Yoksa nesnenin kendi `__dict__`'ine bak
3. Yoksa sınıftaki değeri al (normal nitelik ya da metot gibi veri olmayan tanımlayıcı)
4. Hâlâ yoksa ve sınıfta **`__getattr__`** tanımlıysa onu çağır
5. Yoksa `AttributeError`

```python
class Ayar:
    varsayilan_port = 22                    #! sınıf niteliği (adım 3)

    def __init__(self):
        self.host = "web01"                 #! nesne sözlüğü (adım 2)

    def __getattr__(self, ad):              #! SADECE bulunamayanlarda (adım 4)
        if ad.startswith("env_"):
            return f"<{ad[4:].upper()} ortam değişkeni>"
        raise AttributeError(f"{type(self).__name__} nesnesinde '{ad}' yok")

a = Ayar()
print(a.host, a.varsayilan_port, a.env_path)
try:
    a.olmayan
except AttributeError as e:
    print(e)
```

### Atamayı yakalamak: __setattr__
`k.x = 5` → `type(k).__setattr__(k, "x", 5)`. Bunu ezersen **her** atamayı yakalarsın. İçeride sonsuz döngüye düşmemek için gerçek atamayı `super().__setattr__` (ya da `object.__setattr__`) ile yap:

```python
class Izlenen:
    def __setattr__(self, ad, deger):
        print(f"  atama: {ad} = {deger!r}")
        super().__setattr__(ad, deger)      #! self.ad = deger yazsaydın yine buraya gelirdi

i = Izlenen()
i.durum = "aktif"
i.durum = "pasif"
print(vars(i))
```

> [!TUZAK]
> `__getattr__` ile `__getattribute__` farklı şeylerdir. `__getattr__` sadece normal arama **başarısız olunca** çağrılır, güvenlidir. `__getattribute__` **her** nitelik erişiminde çağrılır (metotlar ve `self.__dict__` dahil). İçinde `self.x` yazarsan kendini çağırırsın. Gerçekten gerekmedikçe ezme; gerekirse içeride `object.__getattribute__(self, ad)` kullan.
:::

::: tahmin
Çıktı tek satır:

```python
class K:
    x = 1
    def __getattr__(self, ad):
        return f"<{ad} yok>"

k = K()
k.y = 2
print(k.x, k.y, k.z)
```

???

`1 2 <z yok>`. `x` sınıfta, `y` nesnede bulunur; `__getattr__` onlar için hiç çağrılmaz. Sadece bulunamayan `z` için devreye girer.
:::

::: anlat __slots__: sözlüksüz nesneler
Her nesnenin bir `__dict__` sözlüğü olması esneklik sağlar ama bellek harcar. Milyonlarca küçük nesne (ağ paketleri, log olayları) oluşturuyorsan **`__slots__`** ile niteliklerin listesini sabitleyebilirsin. Python sözlük yerine sabit yuvalar kullanır:

```python
import sys

class Normal:
    def __init__(self, kaynak, hedef, boyut):
        self.kaynak, self.hedef, self.boyut = kaynak, hedef, boyut

class Yuvali:
    __slots__ = ("kaynak", "hedef", "boyut")
    def __init__(self, kaynak, hedef, boyut):
        self.kaynak, self.hedef, self.boyut = kaynak, hedef, boyut

n, y = Normal("a", "b", 1), Yuvali("a", "b", 1)
print(sys.getsizeof(n) + sys.getsizeof(n.__dict__), "bayt (nesne + sözlük)")
print(sys.getsizeof(y), "bayt (yuvalı)")
print(hasattr(y, "__dict__"))
try:
    y.ek_alan = 5
except AttributeError as e:
    print("eklenemez:", e)
```

Kazanımlar: daha az bellek, biraz daha hızlı nitelik erişimi ve yazım hatalarına karşı koruma (`y.boyt = 5` sessizce yeni nitelik yaratmaz, hata verir). Bedeli: sonradan nitelik eklenemez ve kalıtımda alt sınıfların da `__slots__` tanımlaması gerekir.

> [!DERİN]
> `__slots__` aslında P60'ın konusu olan **tanımlayıcıları** kullanır: her yuva adı için sınıfa bir `member_descriptor` eklenir ve nesnenin içindeki sabit konumdaki göstericiye okuma/yazma yapar. `Yuvali.__dict__["kaynak"]` yazarak gör. `@dataclass(slots=True)` (3.10+) aynı şeyi otomatik yapar.
:::

::: tahmin
İki satır:

```python
class P:
    __slots__ = ("x", "y")
    def __init__(self):
        self.x = 1

p = P()
print(hasattr(p, "__dict__"), p.x, hasattr(p, "y"))
try:
    p.z = 3
except AttributeError:
    print("z eklenemez")
```

???

`False 1 False`, sonra `z eklenemez`. Yuvalı nesnenin sözlüğü yoktur. `y` yuvası tanımlı ama değer atanmadığı için boştur ve `hasattr` False döner. `z` yuva listesinde olmadığı için eklenemez.
:::

::: gorev Değişiklik geçmişi
`Gecmisli` sınıfının nesneleri kendilerine yapılan **her nitelik atamasını** `_gecmis` listesine `(ad, değer)` demeti olarak kaydetsin. `_gecmis`'in kendisi kaydedilmesin. `geri_al()` metodu son atamayı geri alsın: nitelik o atamadan önce varsa eski değerine dönsün, yoksa silinsin.

```starter
class Gecmisli:
    pass
```

```test
G = need("Gecmisli", "sınıf")
g = G()
g.durum = "yeni"
g.atanan = "ali"
g.durum = "inceleniyor"
eq(g._gecmis, [("durum", "yeni"), ("atanan", "ali"), ("durum", "inceleniyor")], "geçmiş kaydı")
g.geri_al()
eq(g.durum, "yeni", "geri al → önceki değer")
g.geri_al()
ok(not hasattr(g, "atanan"), "ilk kez atanmış nitelik geri alınınca silinir")
eq(G()._gecmis, [], "her nesnenin ayrı geçmişi")
```

```solution
class Gecmisli:
    def __init__(self):
        object.__setattr__(self, "_gecmis", [])
        object.__setattr__(self, "_onceki", [])

    def __setattr__(self, ad, deger):
        eski = self.__dict__.get(ad, Gecmisli._YOK)
        self._onceki.append((ad, eski))
        self._gecmis.append((ad, deger))
        object.__setattr__(self, ad, deger)

    def geri_al(self):
        ad, eski = self._onceki.pop()
        self._gecmis.pop()
        if eski is Gecmisli._YOK:
            object.__delattr__(self, ad)
        else:
            object.__setattr__(self, ad, eski)

Gecmisli._YOK = object()
```

```hint
`__init__` içinde `self._gecmis = []` yazarsan bu da `__setattr__`'dan geçer! İç nitelikleri `object.__setattr__(self, "_gecmis", [])` ile kur.
```

```hint
Geri alabilmek için her atamada eski değeri de sakla. "Yoktu" durumunu ayırt etmek için `None` değil, benzersiz bir nöbetçi nesne (`_YOK = object()`) kullan.
```
:::

::: gorev Salt okunur yapılandırma
`SaltOkunur(sozluk)` verilen sözlüğü sarmalasın:

- `cfg.port` → `sozluk["port"]`; iç içe sözlükler de `SaltOkunur` olarak dönsün (`cfg.db.host`)
- olmayan anahtar → `AttributeError`
- herhangi bir atama ya da silme → `AttributeError`
- sarmalanan sözlük dışarıdan değişse bile etkilenmesin (kopya al)

```starter
class SaltOkunur:
    def __init__(self, sozluk):
        self.veri = sozluk
```

```test
S = need("SaltOkunur", "sınıf")
kaynak = {"port": 8443, "db": {"host": "10.0.0.6", "ad": "olaylar"}, "hata_ayikla": False}
c = S(kaynak)
eq(c.port, 8443, "c.port")
eq(c.db.host, "10.0.0.6", "iç içe: c.db.host")
eq(c.hata_ayikla, False, "False değer de dönmeli")
raises(AttributeError, getattr, c, "yok", msg="olmayan anahtar → AttributeError")
raises(AttributeError, setattr, c, "port", 1, msg="atama → AttributeError")
raises(AttributeError, delattr, c, "port", msg="silme → AttributeError")
kaynak["port"] = 1
eq(c.port, 8443, "dış sözlük değişince etkilenmemeli")
```

```solution
import copy

class SaltOkunur:
    def __init__(self, sozluk):
        object.__setattr__(self, "_veri", copy.deepcopy(sozluk))

    def __getattr__(self, ad):
        try:
            deger = self._veri[ad]
        except KeyError:
            raise AttributeError(ad) from None
        return SaltOkunur(deger) if isinstance(deger, dict) else deger

    def __setattr__(self, ad, deger):
        raise AttributeError("salt okunur")

    def __delattr__(self, ad):
        raise AttributeError("salt okunur")
```

```hint
Veriyi `object.__setattr__` ile sakla (kendi `__setattr__`'ın her şeyi reddediyor). Okuma için `__getattr__`: KeyError'u AttributeError'a çevir.
```
:::

::: gorev Yuvalı paket
`Paket` sınıfını `__slots__` ile yaz: `kaynak`, `hedef`, `boyut` alanları. `__init__` üçünü alsın, `__repr__` → `Paket(10.0.0.5→10.0.0.6, 1500B)`. Ayrıca `toplam_boyut(paketler)` fonksiyonu boyutların toplamını döndürsün.

```starter
class Paket:
    def __init__(self, kaynak, hedef, boyut):
        self.kaynak = kaynak
        self.hedef = hedef
        self.boyut = boyut
```

```test
P = need("Paket", "sınıf"); need("toplam_boyut")
p = P("10.0.0.5", "10.0.0.6", 1500)
eq(repr(p), "Paket(10.0.0.5→10.0.0.6, 1500B)", "repr")
ok(not hasattr(p, "__dict__"), "__dict__ olmamalı (__slots__)")
raises(AttributeError, setattr, p, "boyt", 1, msg="yazım hatalı alan eklenemez")
eq(toplam_boyut([P("a", "b", 100), P("a", "c", 50)]), 150, "toplam boyut")
eq(set(P.__slots__), {"kaynak", "hedef", "boyut"}, "üç yuva")
```

```solution
class Paket:
    __slots__ = ("kaynak", "hedef", "boyut")

    def __init__(self, kaynak, hedef, boyut):
        self.kaynak = kaynak
        self.hedef = hedef
        self.boyut = boyut

    def __repr__(self):
        return f"Paket({self.kaynak}→{self.hedef}, {self.boyut}B)"


def toplam_boyut(paketler):
    return sum(p.boyut for p in paketler)
```

```hint
Sınıf gövdesine `__slots__ = ("kaynak", "hedef", "boyut")`.
```
:::
