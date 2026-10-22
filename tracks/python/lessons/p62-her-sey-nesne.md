---
id: p62
title: Her Şey Nesnedir
summary: type ve object ilişkisi, sınıflar da nesne, type() ile çalışma anında sınıf üretmek, iç gözlem.
kazanim: PCAP 4.4, PCPP1 1.1, PCPP1 1.12
---

::: anlat Python'da her şey bir nesnedir
Sayılar, metinler, fonksiyonlar, modüller, sınıflar, hatta `None`... Hepsinin bir **kimliği**, **türü** ve **değeri** vardır. Bunu sadece söylemek yetmez; görelim:

```python
import math

for x in [42, "pafta", [1], len, math, int, None, type]:
    print(f"{type(x).__name__:<22} {repr(x)[:30]}")
```

Son üç satıra dikkat: `int` bir **sınıftır**, ama aynı zamanda bir **nesnedir** ve türü `type`'tır. `type`'ın türü ise yine `type`'tır. Zincir kendi üzerine kapanır.

### type ve object: tavuk ve yumurta
Python nesne modelinin iki temel taşı var:

- **`object`**: bütün sınıfların **atası** (kalıtım zinciri)
- **`type`**: bütün sınıfların **türü** (örnek zinciri; metasınıf)

```python
print(int.__mro__)                    #! int → object
print(type(int), type(object))        #! sınıfların türü type
print(type(type))                     #! type kendisinin örneği
print(issubclass(type, object))       #! type da bir sınıf, object'ten türer
print(isinstance(object, type))       #! object bir sınıf, yani type'ın örneği
```

İki ilişki birbirinden farklıdır ve karıştırılmamalıdır:

| İlişki | Soru | Örnek |
|---|---|---|
| örnek (instance-of) | "bunun türü ne?" | `type(5) is int`, `type(int) is type` |
| alt sınıf (subclass-of) | "bunun atası kim?" | `int.__bases__ == (object,)` |

> [!DERİN]
> `type` ile `object` arasındaki karşılıklı bağımlılık (type, object'ten türer; object, type'ın örneğidir) saf Python'da kurulamaz; CPython bunu C düzeyinde, yorumlayıcı başlarken elle bağlar. Geri kalan her şey bu iki taşın üzerine kurulur. P65'deki metasınıflar, `type` yerine kendi `type` alt sınıfını kullanmaktan ibarettir.
:::

::: tahmin
İki satır:

```python
print(type(42).__name__, type(int).__name__, type(type).__name__)
print(isinstance(int, object), isinstance(object, type), issubclass(type, object))
```

???

`int type type`, sonra `True True True`. 42'nin türü int, int'in türü type, type'ın türü yine type. Her şey (sınıflar dahil) object'in örneğidir. object bir sınıf olduğu için type'ın örneğidir ve type da object'ten türer.
:::

::: anlat Sınıfı çalışma anında üretmek ve iç gözlem
`class` ifadesi aslında bir `type(...)` çağrısının şekerli halidir. Üç argümanlı `type(ad, tabanlar, isim_alani)` yeni bir sınıf üretir:

```python
def selamla(self):
    return f"ben {self.ad}"

Kullanici = type("Kullanici", (object,), {      #! class Kullanici: ... ile aynı
    "rol": "user",
    "__init__": lambda self, ad: setattr(self, "ad", ad),
    "selamla": selamla,
})
k = Kullanici("ayse")
print(k.selamla(), k.rol, type(k).__name__)
```

Sınıflar nesne olduğuna göre çalışma anında değiştirilebilirler. Var olan bir sınıfa sonradan metot eklemeye **maymun yaması** (monkey patching) denir:

```python
class Olay:
    def __init__(self, tur):
        self.tur = tur

Olay.buyuk = lambda self: self.tur.upper()      #! sınıfa yeni metot
print(Olay("giris").buyuk())
```

### İç gözlem (introspection)
Python çalışma anında kendini sorgulamana izin verir:

```python
import inspect

def baglan(host: str, port: int = 22) -> bool:
    """Bağlantı dener."""
    return True

print(callable(baglan), baglan.__name__, baglan.__doc__)
print(inspect.signature(baglan))
print([a for a in dir(baglan) if not a.startswith("_")][:5])
print(baglan.__code__.co_varnames, baglan.__defaults__)
print(inspect.getsource(baglan).splitlines()[0])
print(type(baglan).__mro__)
```

> [!GÜVENLİK]
> Maymun yaması güçlü ama tehlikelidir: bir modül başka bir modülün fonksiyonunu çalışma anında değiştirebilir. Test araçları (`unittest.mock.patch`, P69) bunu meşru biçimde kullanır. Kötü amaçlı bir bağımlılık ise aynı tekniği kullanarak `ssl` doğrulamasını ya da `requests.get`'i sessizce değiştirebilir; tedarik zinciri saldırılarında görülen bir yöntemdir. Bağımlılıklarını sabitle (sürüm + hash) ve denetle.
:::

::: tahmin
Çıktı tek satır:

```python
Nokta = type("Nokta", (), {"x": 0, "kaydir": lambda self, d: self.x + d})
n = Nokta()
print(Nokta.__name__, n.kaydir(5), type(n) is Nokta, Nokta.__bases__[0].__name__)
```

???

`Nokta 5 True object`. type() ile üretilen sınıf `class` ile yazılandan farksızdır. Taban demeti boş verilirse taban otomatik olarak `object` olur.
:::

::: gorev Kayıt sınıfı fabrikası
`kayit_sinifi(ad, alanlar)` fonksiyonu, `type()` ile yeni bir sınıf üretip döndürsün (`class` anahtar kelimesi kullanma):

- Sınıfın adı `ad` olsun
- `__init__` anahtar sözcüklü argümanlarla her alanı nitelik olarak atasın; eksik alan varsa `TypeError` yükseltsin
- `__repr__` → `Ad(alan1=..., alan2=...)` (değerler repr ile)
- `alanlar` sınıf niteliği olarak alanların demeti dursun

```starter
def kayit_sinifi(ad, alanlar):
    pass
```

```test
need("kayit_sinifi")
Olay = kayit_sinifi("Olay", ["ip", "port"])
ok(isinstance(Olay, type), "bir sınıf döndürmeli")
eq(Olay.__name__, "Olay", "sınıf adı")
o = Olay(ip="10.0.0.7", port=22)
eq((o.ip, o.port), ("10.0.0.7", 22), "nitelikler")
eq(repr(o), "Olay(ip='10.0.0.7', port=22)", "repr")
eq(Olay.alanlar, ("ip", "port"), "alanlar demeti")
raises(TypeError, Olay, ip="x", msg="eksik alan → TypeError")
ok(not uses("class"), "class anahtar kelimesi kullanmadan, type() ile")
```

```solution
def kayit_sinifi(ad, alanlar):
    alanlar = tuple(alanlar)

    def __init__(self, **kw):
        eksik = [a for a in alanlar if a not in kw]
        if eksik:
            raise TypeError(f"eksik alan: {', '.join(eksik)}")
        for a in alanlar:
            setattr(self, a, kw[a])

    def __repr__(self):
        icerik = ", ".join(f"{a}={getattr(self, a)!r}" for a in alanlar)
        return f"{ad}({icerik})"

    return type(ad, (), {"__init__": __init__, "__repr__": __repr__, "alanlar": alanlar})
```

```hint
Önce `__init__` ve `__repr__` fonksiyonlarını normal `def` ile tanımla (kapanım olarak `alanlar`'ı görürler), sonra `type(ad, (), {...})`.
```
:::

::: gorev Nesne künyesi
`kunye(x)` fonksiyonu herhangi bir nesne için şu sözlüğü döndürsün:

```python
{"tur": <tür adı>, "modul": <türün tanımlandığı modül>, "cagrilabilir": <bool>,
 "sinif_mi": <x bir sınıf mı>, "ata_sayisi": <türün MRO uzunluğu>}
```

```starter
def kunye(x):
    pass
```

```test
import json
need("kunye")
eq(kunye(42), {"tur": "int", "modul": "builtins", "cagrilabilir": False, "sinif_mi": False, "ata_sayisi": 2}, "42")
eq(kunye(int), {"tur": "type", "modul": "builtins", "cagrilabilir": True, "sinif_mi": True, "ata_sayisi": 2}, "int sınıfı")
eq(kunye(json.dumps)["tur"], "function", "fonksiyon türü")
eq(kunye(json.dumps)["cagrilabilir"], True, "fonksiyon çağrılabilir")
eq(kunye(True)["ata_sayisi"], 3, "bool → int → object")
eq(kunye(json)["tur"], "module", "modül")
```

```solution
def kunye(x):
    t = type(x)
    return {
        "tur": t.__name__,
        "modul": t.__module__,
        "cagrilabilir": callable(x),
        "sinif_mi": isinstance(x, type),
        "ata_sayisi": len(t.__mro__),
    }
```

```hint
Her şey `type(x)` üzerinden: `__name__`, `__module__`, `__mro__`. Sınıf kontrolü: `isinstance(x, type)`.
```
:::

::: gorev Maymun yaması
`yama_uygula(sinif)` fonksiyonu verilen sınıfa **dışarıdan** iki şey eklesin:

- `ozet(self)` metodu → `"<tur>@<kaynak>"`
- `olusturulan` sınıf niteliği: o andan sonra oluşturulan nesne sayısını tutsun. Bunun için sınıfın mevcut `__init__`'ini sarmala (orijinal davranış korunmalı).

```starter
def yama_uygula(sinif):
    pass
```

```test
need("yama_uygula")
class Olay:
    def __init__(self, tur, kaynak):
        self.tur, self.kaynak = tur, kaynak
yama_uygula(Olay)
a = Olay("giris", "10.0.0.7")
b = Olay("cikis", "10.0.0.8")
eq(a.ozet(), "giris@10.0.0.7", "ozet metodu")
eq(Olay.olusturulan, 2, "iki nesne sayıldı")
eq((b.tur, b.kaynak), ("cikis", "10.0.0.8"), "orijinal __init__ çalışmaya devam etmeli")
class Baska:
    def __init__(self, tur, kaynak, ek=0):
        self.tur, self.kaynak, self.ek = tur, kaynak, ek
yama_uygula(Baska)
eq(Baska("x", "y", ek=5).ek, 5, "anahtar sözcüklü argümanlar da aktarılmalı")
eq(Baska.olusturulan, 1, "her sınıfın kendi sayacı")
```

```solution
def yama_uygula(sinif):
    orijinal = sinif.__init__

    def yeni_init(self, *args, **kwargs):
        orijinal(self, *args, **kwargs)
        sinif.olusturulan += 1

    def ozet(self):
        return f"{self.tur}@{self.kaynak}"

    sinif.olusturulan = 0
    sinif.__init__ = yeni_init
    sinif.ozet = ozet
```

```hint
Orijinal `__init__`'i bir değişkende sakla, yeni bir `__init__` yaz: önce orijinali çağırır, sonra sayacı artırır. Sonra `sinif.__init__ = yeni_init`.
```
:::
