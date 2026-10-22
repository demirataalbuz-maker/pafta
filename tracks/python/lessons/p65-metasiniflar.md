---
id: p65
title: Metasınıflar ve __init_subclass__
summary: Sınıfın sınıfı; sınıf oluşturma süreci, kayıt kalıbı, __init_subclass__ ve tekil nesne.
kazanim: PCPP1 1.12
---

::: anlat Sınıfları üreten şey
P62'de gördük: sınıflar `type`'ın örnekleridir. **Metasınıf**, sınıf üreten sınıftır; varsayılanı `type`'tır. `class A(metaclass=M):` yazarak sınıfın **kendisinin** nasıl oluşturulacağını kontrol edersin.

Python bir `class` ifadesini şöyle işler:

1. Metasınıfı belirle (açıkça verilmediyse tabanlardan ya da `type`)
2. `M.__prepare__(ad, tabanlar)` ile gövde için bir isim alanı (sözlük) hazırla
3. Sınıf gövdesini o isim alanında **çalıştır**
4. `M(ad, tabanlar, isim_alani)` çağır: önce `M.__new__`, sonra `M.__init__`
5. Sonucu ada bağla

```python
class Gozlemci(type):
    def __new__(mcs, ad, tabanlar, ns):
        print(f"oluşturuluyor: {ad}, gövdedeki isimler: {[k for k in ns if not k.startswith('__')]}")
        cls = super().__new__(mcs, ad, tabanlar, ns)
        cls.olusturma_sirasi = len(mcs.kayit)
        mcs.kayit.append(cls)
        return cls

Gozlemci.kayit = []

class Taban(metaclass=Gozlemci):
    def calis(self): ...

class Alt(Taban):                       #! metasınıf kalıtımla geçer
    seviye = 3

print([c.__name__ for c in Gozlemci.kayit], Alt.olusturma_sirasi, type(Alt).__name__)
```

Metasınıflar, sınıf **tanımlandığı anda** (nesne oluşturulduğunda değil) devreye girer. Bu yüzden şunlar için kullanılırlar: sınıfları otomatik kaydetmek, sınıf tanımını doğrulamak, sınıfa otomatik metot ya da nitelik eklemek. Django modelleri, SQLAlchemy ve `abc.ABCMeta` metasınıf kullanır.

> [!ZEN]
> Tim Peters'ın meşhur sözü: "Metasınıflar, kullanıcıların %99'unun dert etmemesi gereken derin bir sihirdir. Onlara ihtiyacın olup olmadığını merak ediyorsan, yoktur." Önce sınıf dekoratörü ya da `__init_subclass__` dene.
:::

::: tahmin
Çıktı tek satır:

```python
class Kayit(type):
    siniflar = []
    def __new__(mcs, ad, tabanlar, ns):
        cls = super().__new__(mcs, ad, tabanlar, ns)
        mcs.siniflar.append(ad)
        return cls

class A(metaclass=Kayit):
    pass

class B(A):
    pass

print(Kayit.siniflar, type(B).__name__)
```

???

`['A', 'B'] Kayit`. Metasınıf kalıtımla geçer: B'yi açıkça işaretlemedik ama tabanı A'nın metasınıfı Kayit olduğu için B de onunla oluşturuldu.
:::

::: anlat __init_subclass__: hafif alternatif
Çoğu metasınıf kullanımı aslında "bir alt sınıf tanımlandığında bana haber ver" ihtiyacıdır. Python 3.6 bunun için çok daha basit bir kanca getirdi: taban sınıftaki **`__init_subclass__`** her alt sınıf oluşturulduğunda çağrılır. Sınıf tanımında anahtar sözcüklü argüman bile alabilir:

```python
class Ayristirici:
    turler = {}

    def __init_subclass__(cls, uzanti=None, **kw):
        super().__init_subclass__(**kw)
        if uzanti is None:
            raise TypeError(f"{cls.__name__}: uzanti belirtilmeli")
        Ayristirici.turler[uzanti] = cls

    def ayristir(self, metin):
        raise NotImplementedError

class JsonAyristirici(Ayristirici, uzanti=".json"):
    def ayristir(self, metin):
        import json
        return json.loads(metin)

class CsvAyristirici(Ayristirici, uzanti=".csv"):
    def ayristir(self, metin):
        return [s.split(",") for s in metin.splitlines()]

def ayristir(dosya_adi, metin):
    uzanti = dosya_adi[dosya_adi.rfind("."):]
    return Ayristirici.turler[uzanti]().ayristir(metin)

print(sorted(Ayristirici.turler))
print(ayristir("a.csv", "x,y\n1,2"), ayristir("b.json", '{"k": 1}'))
```

Yeni bir biçim eklemek için tek yapman gereken yeni bir alt sınıf yazmak; kayıt otomatiktir. **Eklenti mimarisinin** en temiz Python kalıbı budur.

> [!DERİN]
> `__init_subclass__` örtük olarak bir `classmethod`'dur. Sınıf oluşturma sırasında tanımlayıcıların `__set_name__`'i (P64) de çağrılır; sıra şöyledir: metasınıfın `__new__`'u sınıfı yaratır → `__set_name__`'ler → tabanın `__init_subclass__`'ı → metasınıfın `__init__`'i. Ayrıca `__class_getitem__` sınıfın `Sinif[int]` gibi indekslenebilmesini sağlar; `list[int]` böyle çalışır.
:::

::: tahmin
Çıktı tek satır:

```python
class Eklenti:
    kayit = {}
    def __init_subclass__(cls, ad=None, **kw):
        super().__init_subclass__(**kw)
        cls.kayit[ad or cls.__name__.lower()] = cls

class Json(Eklenti, ad="json"):
    pass

class Csv(Eklenti):
    pass

print(sorted(Eklenti.kayit), Eklenti.kayit["csv"] is Csv)
```

???

`['csv', 'json'] True`. Json açık bir ad verdi, Csv vermedi ve sınıf adının küçük harfli hali kullanıldı. Taban sınıfın kendisi kaydedilmez: kanca sadece **alt** sınıflar için çalışır.
:::

::: gorev Eklenti kaydı
Bir tespit aracı farklı log biçimleri için ayrıştırıcılar kullanıyor. `Okuyucu` taban sınıfını `__init_subclass__` ile yaz:

- Her alt sınıf bir `bicim` **sınıf niteliği** tanımlamalı (ör. `"syslog"`); tanımlamazsa sınıf oluşturulurken `TypeError` yükselsin
- Alt sınıflar `Okuyucu.kayit` sözlüğüne `bicim → sınıf` olarak eklensin; aynı biçim ikinci kez kaydedilirse `ValueError`
- `okuyucu_bul(bicim)` fonksiyonu ilgili sınıfın **bir örneğini** döndürsün; bilinmeyen biçimde `KeyError`

```starter
class Okuyucu:
    kayit = {}

def okuyucu_bul(bicim):
    pass
```

```test
O = need("Okuyucu", "sınıf"); need("okuyucu_bul")
O.kayit.clear()
class Syslog(O):
    bicim = "syslog"
class Json(O):
    bicim = "json"
eq(sorted(O.kayit), ["json", "syslog"], "iki biçim kaydedildi")
ok(isinstance(okuyucu_bul("json"), Json), "okuyucu_bul örnek döndürmeli")
raises(KeyError, okuyucu_bul, "xml", msg="bilinmeyen biçim → KeyError")
try:
    class Bicimsiz(O):
        pass
    ok(False, "bicim tanımlamayan alt sınıf TypeError vermeli")
except TypeError:
    ok(True, "bicim yoksa TypeError")
try:
    class Kopya(O):
        bicim = "json"
    ok(False, "aynı biçim ikinci kez ValueError vermeli")
except ValueError:
    ok(True, "tekrar kayıt ValueError")
```

```solution
class Okuyucu:
    kayit = {}

    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        bicim = cls.__dict__.get("bicim")
        if bicim is None:
            raise TypeError(f"{cls.__name__}: 'bicim' tanımlanmalı")
        if bicim in Okuyucu.kayit:
            raise ValueError(f"'{bicim}' zaten kayıtlı")
        Okuyucu.kayit[bicim] = cls


def okuyucu_bul(bicim):
    return Okuyucu.kayit[bicim]()
```

```hint
`__init_subclass__(cls, **kw)` içinde `cls.__dict__.get("bicim")`: tabandan miras gelen değeri değil, alt sınıfın **kendi** tanımını kontrol eder.
```
:::

::: gorev Sabit adı denetleyicisi
`SabitDenetci` adında bir **metasınıf** yaz: bu metasınıfla oluşturulan bir sınıfın gövdesindeki, `_` ile başlamayan ve **çağrılabilir olmayan** her sınıf niteliğinin adı **tamamen büyük harf** (`MAKS_DENEME`) olmalı. Kurala uymayan bir ad varsa sınıf oluşturulurken `TypeError` yükselt. Metotlar ve `_` ile başlayanlar serbest.

```starter
class SabitDenetci(type):
    pass
```

```test
M = need("SabitDenetci", "sınıf")
ok(issubclass(M, type), "type'tan türeyen bir metasınıf olmalı")
class Ayarlar(metaclass=M):
    MAKS_DENEME = 5
    ZAMAN_ASIMI = 2.5
    _ic = "serbest"
    def yukle(self):
        return self.MAKS_DENEME
eq(Ayarlar().yukle(), 5, "geçerli sınıf normal çalışır")
try:
    class Kotu(metaclass=M):
        MAKS = 1
        varsayilan_port = 22
    ok(False, "küçük harfli sabit TypeError vermeli")
except TypeError as e:
    ok("varsayilan_port" in str(e), "hata mesajı kural dışı adı içermeli", got=str(e))
class Alt(Ayarlar):
    YENI = 1
ok(type(Alt) is M, "metasınıf alt sınıflara geçer")
```

```solution
class SabitDenetci(type):
    def __new__(mcs, ad, tabanlar, ns):
        for anahtar, deger in ns.items():
            if anahtar.startswith("_") or callable(deger):
                continue
            if anahtar != anahtar.upper():
                raise TypeError(f"{ad}.{anahtar}: sabit adları büyük harf olmalı")
        return super().__new__(mcs, ad, tabanlar, ns)
```

```hint
`__new__(mcs, ad, tabanlar, ns)` içinde `ns` sınıf gövdesindeki isimlerin sözlüğüdür. Denetimden sonra `super().__new__(...)` ile sınıfı oluştur.
```
:::

::: gorev Tekil nesne
`Tekil` adında bir metasınıf yaz: bu metasınıfı kullanan her sınıfın **yalnızca bir** örneği olsun. `Sinif()` her çağrıldığında aynı nesne dönsün; ilk çağrıdaki argümanlarla oluşturulsun. Her sınıfın kendi tekil nesnesi olmalı.

```starter
class Tekil(type):
    pass
```

```test
T = need("Tekil", "sınıf")
class Yapilandirma(metaclass=T):
    def __init__(self, yol="varsayilan.ini"):
        self.yol = yol
class Baglanti(metaclass=T):
    pass
a = Yapilandirma("ozel.ini")
b = Yapilandirma("baska.ini")
ok(a is b, "aynı nesne dönmeli")
eq(b.yol, "ozel.ini", "ilk çağrının argümanları geçerli")
ok(Baglanti() is Baglanti(), "ikinci sınıf da tekil")
ok(Baglanti() is not a, "her sınıfın kendi tekili")
```

```solution
class Tekil(type):
    _ornekler = {}

    def __call__(cls, *args, **kwargs):
        if cls not in Tekil._ornekler:
            Tekil._ornekler[cls] = super().__call__(*args, **kwargs)
        return Tekil._ornekler[cls]
```

```hint
`Sinif()` çağrısı aslında metasınıfın `__call__`'ıdır. Onu ez: sınıf için kayıtlı bir örnek yoksa `super().__call__(*args, **kwargs)` ile oluştur ve sakla.
```
:::
