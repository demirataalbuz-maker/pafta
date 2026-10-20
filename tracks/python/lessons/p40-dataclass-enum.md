---
id: p40
title: dataclass ve enum
summary: Kalıp kodu yazmadan veri sınıfları; field, frozen, __post_init__; Enum, IntEnum ve Flag.
---

::: anlat @dataclass: kalıp kod fabrikası
Veri taşıyan sınıflar için hep aynı şeyi yazarsın: `__init__` içinde `self.x = x`, okunaklı bir `__repr__`, alanları karşılaştıran bir `__eq__`. `@dataclass` bunları **tip ipuçlarından** otomatik üretir:

```python
from dataclasses import dataclass, field, asdict

@dataclass
class Bulgu:
    baslik: str                                  #! alan: ad ve tip ipucu
    seviye: int = 3                              #! varsayılan değer
    etiketler: list = field(default_factory=list)   #! değiştirilebilir varsayılan: fabrika!

    def kritik_mi(self):                         #! normal metotlar da eklenebilir
        return self.seviye >= 4

b = Bulgu("Varsayılan parola", 5, ["auth"])
print(b)                                         #! otomatik __repr__
print(b == Bulgu("Varsayılan parola", 5, ["auth"]))   #! otomatik __eq__
print(b.kritik_mi(), asdict(b))                  #! asdict: JSON'a hazır sözlük
```

> [!TUZAK]
> `etiketler: list = []` yazarsan dataclass **hata verir** (`ValueError: mutable default`). P21'deki tuzağı bildiği için seni korur. `field(default_factory=list)` her nesne için yeni bir liste üretir.

### Seçenekler
```python
from dataclasses import dataclass

@dataclass(frozen=True, order=True)              #! değiştirilemez + karşılaştırılabilir
class Surum:
    ana: int
    ara: int
    yama: int = 0

    def __post_init__(self):                     #! otomatik __init__'ten sonra çalışır: doğrulama yeri
        if min(self.ana, self.ara, self.yama) < 0:
            raise ValueError("negatif sürüm parçası")

s = Surum(1, 10)
print(sorted([Surum(1, 9, 3), s, Surum(0, 99)]))  #! order=True: alan sırasıyla karşılaştırır
print({s, Surum(1, 10)})                          #! frozen → hash'lenebilir
```

`frozen=True` atamayı yasaklar (`FrozenInstanceError`) ve `__hash__` üretir. `order=True` ise `<`, `<=` gibi karşılaştırmaları alanların **tanım sırasına** göre ekler. Python 3.10+ `slots=True` daha az bellek kullanan ve hızlı nitelik erişimi sağlayan bir sınıf üretir (P59).

> [!DERİN]
> `@dataclass` sihir değil, sınıf üzerinde çalışan bir fonksiyondur: sınıfın `__annotations__` sözlüğünü okur, `__init__`'in **kaynak kodunu metin olarak üretir**, `exec` ile derler ve sınıfa ekler. Tip ipuçları çalışma anında **doğrulanmaz**: `Bulgu(42, "x")` yine çalışır. Tip denetimi için P47'deki mypy ya da `__post_init__` gerekir.
:::

::: tahmin
İki satırlık değil, tek satırlık çıktı:

```python
from dataclasses import dataclass, field

@dataclass
class Olay:
    ip: str
    port: int = 22
    etiketler: list = field(default_factory=list)

a = Olay("10.0.0.7")
b = Olay("10.0.0.7")
a.etiketler.append("ssh")
print(a == b, b)
```

???

`False Olay(ip='10.0.0.7', port=22, etiketler=[])`. `default_factory` sayesinde her nesnenin kendi listesi var; a'nın listesi değişince eşitlik bozulur ama b'ninki boş kalır.
:::

::: anlat Enum: sabit seçenekler kümesi
Sihirli metinler ve sayılar (`"yuksek"`, `3`) yazım hatasına açıktır: `"yuskek"` yazsan kimse uyarmaz. **Enum** sabit seçenekleri isimli sabitlere dönüştürür:

```python
from enum import Enum, IntEnum, Flag, auto

class Durum(Enum):
    ACIK = "open"
    KAPALI = "closed"
    FILTRELI = "filtered"

print(Durum.ACIK, Durum.ACIK.name, Durum.ACIK.value)
print(Durum("closed"))                       #! değerden üye bul
print(Durum["FILTRELI"])                     #! addan üye bul
print([d.name for d in Durum])               #! üyeler üzerinde döngü
print(Durum.ACIK == "open")                  #! False: Enum metinle eşit değildir

class Seviye(IntEnum):                       #! IntEnum: sayı gibi karşılaştırılır
    DUSUK = 1
    ORTA = 2
    YUKSEK = 3

print(Seviye.YUKSEK > Seviye.ORTA, max(Seviye))
```

### Flag: bit bayrakları
Unix dosya izinleri (`rwx`) gibi **birleştirilebilir** seçenekler için `Flag`:

```python
from enum import Flag, auto

class Izin(Flag):
    OKU = auto()          #! 1
    YAZ = auto()          #! 2
    CALISTIR = auto()     #! 4

kullanici = Izin.OKU | Izin.YAZ              #! birleştir: bitwise OR
print(kullanici, Izin.YAZ in kullanici, Izin.CALISTIR in kullanici)
print(kullanici.value)
```

> [!GÜVENLİK]
> Unix'te `chmod 754`'teki her rakam 3 bitlik bir bayraktır: 4 = oku, 2 = yaz, 1 = çalıştır. `7 = 4|2|1`. Herkese yazma izni (`o+w`, `chmod 777`) gibi yanlış yapılandırmaları denetleyen bir araç yazarken bu bitlerle konuşursun. P48'de bit işleçlerini doğrudan kullanacaksın.
:::

::: tahmin
Çıktı tek satır:

```python
from enum import Flag, auto

class Izin(Flag):
    OKU = auto()
    YAZ = auto()
    CALISTIR = auto()

i = Izin.OKU | Izin.YAZ
print(Izin.YAZ in i, Izin.CALISTIR in i, i.value)
```

???

`True False 3`. `auto()` 1, 2, 4 değerlerini verir. OKU|YAZ = 1|2 = 3.
:::

::: gorev Doğrulayan bulgu
`Bulgu` adında bir **dataclass** yaz: `baslik: str`, `seviye: int`, `etiketler: list` (varsayılan boş liste). `__post_init__` içinde seviye 1–5 dışındaysa `ValueError` yükselt ve başlığın kenar boşluklarını temizle. `kritik_mi()` metodu seviye 4 ve üstündeyse `True` döndürsün.

```starter
from dataclasses import dataclass, field

class Bulgu:
    pass
```

```test
import dataclasses
B = need("Bulgu", "sınıf")
ok(dataclasses.is_dataclass(B), "Bulgu bir dataclass olmalı")
b = B("  SMB imzalama kapalı ", 4)
eq(b.baslik, "SMB imzalama kapalı", "başlık temizlenir")
eq(b.etiketler, [], "varsayılan etiketler []")
ok(B("a", 1).etiketler is not B("b", 1).etiketler, "her bulgunun ayrı listesi")
eq(b.kritik_mi(), True, "seviye 4 kritik")
eq(B("x", 2).kritik_mi(), False, "seviye 2 kritik değil")
eq(repr(B("x", 1, ["y"])), "Bulgu(baslik='x', seviye=1, etiketler=['y'])", "otomatik repr")
raises(ValueError, B, "x", 9, msg="seviye 9 → ValueError")
raises(ValueError, B, "x", 0, msg="seviye 0 → ValueError")
```

```solution
from dataclasses import dataclass, field

@dataclass
class Bulgu:
    baslik: str
    seviye: int
    etiketler: list = field(default_factory=list)

    def __post_init__(self):
        if not 1 <= self.seviye <= 5:
            raise ValueError(f"seviye 1-5 olmalı: {self.seviye}")
        self.baslik = self.baslik.strip()

    def kritik_mi(self):
        return self.seviye >= 4
```

```hint
`@dataclass` + alanlar tip ipuçlarıyla. Değiştirilebilir varsayılan için `field(default_factory=list)`.
```
:::

::: gorev Önem derecesi
`Seviye` adında bir `IntEnum` tanımla: `DUSUK=1`, `ORTA=2`, `YUKSEK=3`, `KRITIK=4`. Sonra `seviye_bul(puan)` fonksiyonu 0–10 arası bir zafiyet puanını seviyeye çevirsin:

| Puan | Seviye |
|---|---|
| 0 – 3.9 | DUSUK |
| 4.0 – 6.9 | ORTA |
| 7.0 – 8.9 | YUKSEK |
| 9.0 – 10 | KRITIK |

0–10 dışındaki puanlarda `ValueError` yükselt.

```starter
from enum import IntEnum

def seviye_bul(puan):
    pass
```

```test
from enum import IntEnum
S = need("Seviye", "sınıf"); need("seviye_bul")
ok(issubclass(S, IntEnum), "Seviye bir IntEnum olmalı")
eq([s.value for s in S], [1, 2, 3, 4], "değerler 1-4")
ok(seviye_bul(9.8) is S.KRITIK, "9.8 → KRITIK")
ok(seviye_bul(7.0) is S.YUKSEK, "7.0 → YUKSEK")
ok(seviye_bul(6.9) is S.ORTA, "6.9 → ORTA")
ok(seviye_bul(0) is S.DUSUK, "0 → DUSUK")
ok(seviye_bul(10) is S.KRITIK, "10 → KRITIK")
ok(seviye_bul(9) is S.KRITIK, "tam 9 → KRITIK")
ok(seviye_bul(8.9) is S.YUKSEK, "8.9 → YUKSEK")
ok(seviye_bul(4) is S.ORTA, "tam 4 → ORTA")
ok(seviye_bul(3.9) is S.DUSUK, "3.9 → DUSUK")
raises(ValueError, seviye_bul, -0.1, msg="-0.1 → ValueError")
raises(ValueError, seviye_bul, 11, msg="11 → ValueError")
ok(S.KRITIK > S.ORTA, "IntEnum karşılaştırılabilir")
```

```solution
from enum import IntEnum

class Seviye(IntEnum):
    DUSUK = 1
    ORTA = 2
    YUKSEK = 3
    KRITIK = 4

def seviye_bul(puan):
    if not 0 <= puan <= 10:
        raise ValueError(f"puan 0-10 olmalı: {puan}")
    if puan >= 9:
        return Seviye.KRITIK
    if puan >= 7:
        return Seviye.YUKSEK
    if puan >= 4:
        return Seviye.ORTA
    return Seviye.DUSUK
```

```hint
Eşikleri yukarıdan aşağı dene (önce 9, sonra 7, sonra 4) ve üyeyi döndür: `return Seviye.KRITIK`.
```
:::

::: gorev Değiştirilemez koordinat
`Nokta` adında **frozen** bir dataclass yaz (`x: int`, `y: int`). Noktalar küme elemanı olabilmeli ve atama yasak olmalı. `tasi(dx, dy)` metodu **yeni** bir Nokta döndürsün (`dataclasses.replace` işine yarar).

```starter
from dataclasses import dataclass, replace

class Nokta:
    pass
```

```test
import dataclasses
N = need("Nokta", "sınıf")
p = N(1, 2)
eq(len({N(1, 2), N(1, 2), N(3, 4)}), 2, "kümede tekrar birleşir")
raises(dataclasses.FrozenInstanceError, setattr, p, "x", 9, msg="atama yasak")
q = p.tasi(2, -1)
eq((q.x, q.y), (3, 1), "tasi(2, -1) → (3, 1)")
eq((p.x, p.y), (1, 2), "orijinal değişmez")
```

```solution
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class Nokta:
    x: int
    y: int

    def tasi(self, dx, dy):
        return replace(self, x=self.x + dx, y=self.y + dy)
```

```hint
`@dataclass(frozen=True)`. `replace(self, x=...)` değiştirilmiş yeni bir kopya üretir.
```
:::
