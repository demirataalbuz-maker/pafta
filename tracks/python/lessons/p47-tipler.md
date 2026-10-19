---
id: p47
title: Tip İpuçları
summary: Açıklamalı imzalar, list[int] ve X | None, TypeVar, TypedDict, Literal, Callable ve çalışma anı ipuçları.
---

::: anlat Kod için belgeler, makine için sözleşme
Python dinamik tiplidir; ama büyük projelerde "bu fonksiyon ne alıyor, ne döndürüyor?" sorusu can yakar. **Tip ipuçları** (type hints) bunun cevabını koda yazar:

```python
def baglan(host: str, port: int = 22, zaman_asimi: float | None = None) -> bool:
    return port > 0

hedefler: list[str] = ["web01", "db01"]
portlar: dict[str, int] = {"ssh": 22}
koordinat: tuple[float, float] = (41.0, 29.0)
degiskenler: tuple[int, ...] = (1, 2, 3)          #! herhangi uzunlukta int demeti

print(baglan.__annotations__)
```

**Önemli:** Python ipuçlarını **çalışma anında denetlemez**. `baglan(42, "x")` sorunsuz çalışır. İpuçları üç şeye yarar:

1. **Belge**: imza kendini anlatır
2. **Editör**: otomatik tamamlama ve anlık uyarılar
3. **Statik denetim**: `mypy` ya da `pyright` gibi araçlar kodu **çalıştırmadan** tip hatalarını bulur (`pip install mypy`, sonra `mypy dosya.py`)

### Temel yazım
| Yazım | Anlamı |
|---|---|
| `list[int]`, `set[str]`, `dict[str, float]` | içerik tipiyle koleksiyon (3.9+) |
| `int \| None` | int ya da None (3.10+; eskisi `Optional[int]`) |
| `int \| str` | ikisinden biri (eskisi `Union[int, str]`) |
| `Any` | denetimi kapat |
| `Callable[[int, str], bool]` | (int, str) alıp bool döndüren fonksiyon |
| `Iterable[str]`, `Sequence[int]`, `Mapping[str, int]` | soyut arayüzler (`collections.abc`'den) |
| `Literal["r", "w"]` | sadece bu değerlerden biri |

> [!NOT]
> Parametreleri **soyut**, dönüşü **somut** yaz: `def say(kelimeler: Iterable[str]) -> dict[str, int]`. Böylece fonksiyon liste, küme, üreteç kabul eder ama ne döndürdüğü kesindir.
:::

::: tahmin
Çıktı tek satır:

```python
def topla(a: int, b: int) -> int:
    return a + b

print(topla("ab", "cd"), topla.__annotations__["return"].__name__)
```

???

`abcd int`. İpuçları çalışma anında **uygulanmaz**: metinler sorunsuz birleştirildi. `__annotations__` sözlüğü ipuçlarını saklar ama Python onlara bakmaz.
:::

::: anlat Generic'ler, TypedDict ve çalışma anında ipuçları
**TypeVar** "giren türle çıkan tür aynı" demeyi sağlar:

```python
from typing import TypeVar, Sequence

T = TypeVar("T")

def ilk(dizi: Sequence[T]) -> T | None:      #! list[int] gelirse int döner, list[str] gelirse str
    return dizi[0] if dizi else None

print(ilk([3, 1]), ilk("abc"), ilk([]))
```

Python 3.12+ bunu daha kısa yazar: `def ilk[T](dizi: Sequence[T]) -> T | None`. Burada 3.11 kullandığımız için `TypeVar` yazımı geçerli.

**TypedDict**, JSON benzeri sözlüklerin şemasını tanımlar. **Literal** izin verilen sabit değerleri sınırlar:

```python
from typing import TypedDict, Literal, NotRequired

class Olay(TypedDict):
    ip: str
    port: int
    seviye: Literal["dusuk", "orta", "yuksek"]
    notlar: NotRequired[str]                  #! zorunlu olmayan anahtar

o: Olay = {"ip": "10.0.0.7", "port": 22, "seviye": "orta"}
print(o["ip"], type(o).__name__)              #! çalışırken hâlâ sıradan bir dict
```

Çalışma anında ipuçlarına `typing.get_type_hints()` ve `inspect.signature()` ile erişebilirsin. Pydantic gibi kütüphaneler ipuçlarını okuyup **gerçek doğrulama** yapar; bu paftanın bir görevinde onun minik bir versiyonunu yazacaksın.

```python
import inspect, typing

def kaydet(ad: str, yas: int, aktif: bool = True) -> None: ...

print(typing.get_type_hints(kaydet))
for p in inspect.signature(kaydet).parameters.values():
    print(p.name, p.annotation.__name__, p.default)
```

> [!DERİN]
> `from __future__ import annotations` yazılırsa (ya da gelecekteki Python'larda varsayılan olarak) ipuçları değerlendirilmez, **metin** olarak saklanır; `get_type_hints` bunları gerektiğinde çözer. Bu, henüz tanımlanmamış bir sınıfa atıf yapmayı (`def ebeveyn(self) -> Dugum:`) ve içe aktarma döngülerinden kaçmayı kolaylaştırır. Ayrıca `typing.TYPE_CHECKING` sabiti sadece statik denetleyici için `True`'dur: ağır import'ları çalışma anında atlamak için kullanılır.
:::

::: tahmin
Çıktı tek satır:

```python
from typing import TypedDict

class Olay(TypedDict):
    ip: str
    port: int

o: Olay = {"ip": "10.0.0.1", "port": "22"}
print(type(o).__name__, o["port"] * 2)
```

???

`dict 2222`. TypedDict çalışma anında sıradan bir sözlüktür ve `"22"` metni hiç denetlenmez; metin çarpımı `"2222"` üretir. Bu hatayı mypy yakalardı, Python yakalamaz.
:::

::: gorev İpuçlu imza
`ortalama` fonksiyonunu **tam tip ipuçlarıyla** yaz: `degerler` parametresi `list[float]`, dönüş tipi `float | None`. Liste boşsa `None` döndür.

```starter
def ortalama(degerler):
    if not degerler:
        return None
    return sum(degerler) / len(degerler)
```

```test
import typing
need("ortalama")
ipucu = typing.get_type_hints(ortalama)
eq(ipucu.get("degerler"), list[float], "degerler: list[float]")
eq(ipucu.get("return"), float | None, "dönüş: float | None")
eq(ortalama([1.0, 2.0]), 1.5, "ortalama çalışıyor")
eq(ortalama([]), None, "boş → None")
```

```solution
def ortalama(degerler: list[float]) -> float | None:
    if not degerler:
        return None
    return sum(degerler) / len(degerler)
```

```hint
`def ortalama(degerler: list[float]) -> float | None:`
```
:::

::: gorev Mini çalışma anı doğrulayıcı
`tip_denetle` adında bir **dekoratör** yaz: sarmalanan fonksiyon çağrıldığında, ipucu **basit bir sınıf** olan (int, str, float, bool, list, dict gibi) her argümanı `isinstance` ile denetlesin; uymayanlarda `TypeError` yükseltsin. İpucu olmayan parametreleri atla. Varsayılan değerler de bağlanmalı (`inspect.signature(...).bind`).

```starter
import inspect
from functools import wraps

def tip_denetle(fonk):
    pass
```

```test
need("tip_denetle")
@tip_denetle
def kayit(ad: str, yas: int, etiket=None, puan: float = 0.0):
    return f"{ad}:{yas}:{puan}"
eq(kayit("ali", 30), "ali:30:0.0", "doğru tipler geçer")
eq(kayit("ali", 30, etiket=5, puan=1.5), "ali:30:1.5", "ipucusuz parametre denetlenmez")
raises(TypeError, kayit, "ali", "otuz", msg="yas metin → TypeError")
raises(TypeError, kayit, 42, 30, msg="ad sayı → TypeError")
raises(TypeError, kayit, "ali", 30, puan="yuksek", msg="anahtar sözcüklü argüman da denetlenir")
eq(kayit.__name__, "kayit", "wraps")
```

```solution
import inspect
from functools import wraps

def tip_denetle(fonk):
    imza = inspect.signature(fonk)

    @wraps(fonk)
    def sarmal(*args, **kwargs):
        bagli = imza.bind(*args, **kwargs)
        bagli.apply_defaults()
        for ad, deger in bagli.arguments.items():
            tip = imza.parameters[ad].annotation
            if tip is not inspect.Parameter.empty and isinstance(tip, type) and not isinstance(deger, tip):
                raise TypeError(f"{ad}: {tip.__name__} bekleniyordu, {type(deger).__name__} geldi")
        return fonk(*args, **kwargs)
    return sarmal
```

```hint
`imza = inspect.signature(fonk)`, çağrıda `bagli = imza.bind(*args, **kwargs)` ve `bagli.arguments` (ad → değer).
```

```hint
İpucu yoksa `annotation` değeri `inspect.Parameter.empty`'dir; o da bir sınıf olduğu için ayrıca ele: `tip is not inspect.Parameter.empty`. `isinstance(tip, type)` ise `list[int]` gibi generic'leri eler.
```
:::

::: gorev Generic ilk eleman
`T = TypeVar("T")` tanımla ve `ilk_uyan(dizi, kosul)` fonksiyonunu yaz: `dizi: Iterable[T]`, `kosul: Callable[[T], bool]`, dönüş `T | None`. Koşulu sağlayan ilk elemanı döndürsün, yoksa `None`.

```starter
from typing import TypeVar, Iterable, Callable

def ilk_uyan(dizi, kosul):
    pass
```

```test
import typing
need("ilk_uyan")
eq(ilk_uyan([3, 8, 12], lambda x: x > 5), 8, "ilk 5'ten büyük → 8")
eq(ilk_uyan(["ssh", "rdp"], lambda s: s.startswith("r")), "rdp", "metinler")
eq(ilk_uyan(iter([]), lambda x: True), None, "boş → None")
h = typing.get_type_hints(ilk_uyan)
ok(isinstance(kullanici.get("T"), typing.TypeVar), "T bir TypeVar olmalı")
ok("dizi" in h and "kosul" in h and "return" in h, "tüm parametreler ve dönüş ipuçlu olmalı")
ok(typing.get_origin(h.get("kosul")) is not None and "Callable" in str(h.get("kosul")), "kosul: Callable[[T], bool]")
```

```solution
from typing import TypeVar, Iterable, Callable

T = TypeVar("T")

def ilk_uyan(dizi: Iterable[T], kosul: Callable[[T], bool]) -> T | None:
    for x in dizi:
        if kosul(x):
            return x
    return None
```

```hint
İmza: `def ilk_uyan(dizi: Iterable[T], kosul: Callable[[T], bool]) -> T | None:`
```
:::
