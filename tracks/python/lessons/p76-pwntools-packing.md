---
id: p76
title: pwntools · Bayttan Alana
summary: Hazır betikte context, p16/p32 ve u16/u32 çağrılarını okumak; endian, işaret ve uzunluk denetimiyle yerel bir kaydı paketlemek ve açmak.
backend: wsl
timeout: 60
---

::: anlat Hazır betiğin veri akışını oku
P51'de bytes/struct, P54'te subprocess gördün. Burada aynı bilgiye **pwntools** arayüzünden bakıyoruz. Bir CTF betiğinde önce ortamı, sonra verinin **kaç bayt olduğunu**, en son bu baytların nereye gittiğini izle. Bu dersin çıktısı yalnız bellekteki bir kayıttır.

Tezgah gerçek Kali WSL Python'unda kurulu **pwntools 4.15.0** paketini kullanır; Windows Python'u veya temiz P75 venv'i bu paketi otomatik görmez. Koşucunun dağıtımı `PAFTA_WSL_DISTRO` ayarından gelir. Aşağıdaki envanter başka makinede farklı olabilir; eksik paket otomatik kurulmaz.

Görev hazırlığı `PWNLIB_NOTERM=1` ayarlar: Pafta'nın çıktı kutusu etkileşimli bir terminal olmadığı için pwntools'un terminal denetimi kapatılır. Paketleme ve süreç API'leri gerçek kütüphanede çalışmaya devam eder.

```setup
import os
os.environ["PWNLIB_NOTERM"] = "1"
```
```python
import importlib.metadata
import pwnlib
import sys
print(sys.executable)
print(importlib.metadata.version("pwntools"))
print(pwnlib.__file__)
```

Hazır betikteki `from pwn import *` geniş bir yardımcı kümesini içeri alır. Burada hangi çağrının nereden geldiğini görebilmek için dar import kullanıyoruz. Kurulu paketin adı `pwntools`, import yolu `pwnlib` olabilir; aynı isim olmak zorunda değiller.
:::

::: anlat Context, endian ve işaret
`p16` bir tamsayıyı 16 bit / iki bayta paketler; `u16` iki baytı tamsayıya açar. `p32/u32` dört bayt kullanır. `endian` bayt sırasını, `sign` işaretli yorumu seçer. `context.local(...)` geçici ayar sağlar ve blok bitince eski ayara döner. Fonksiyonun sözleşmesi sabitse parametreleri açıkça ver.

```setup
import os
os.environ["PWNLIB_NOTERM"] = "1"
```
```python
from pwnlib.context import context
from pwnlib.util.packing import p16, u16

with context.local(endian="big", signed=False):
    print(p16(0x1234).hex())
    with context.local(endian="little"):
        print(p16(0x1234).hex())
    print(u16(b"\xff\xff", sign=True))
    print(context.endian)
```

Burada `p16` her iki context'te de **iki bayt** üretir; `context.bits` değiştirmek `p16`yı `p64` yapmaz. 16 bit unsigned aralık 0–65535, signed aralık −32768–32767'dir. Sığmayan sayıyı sessizce maskeleyip kesmek protokol hatasını saklar.

[Kaynak: packing](https://docs.pwntools.com/en/stable/util/packing.html), [context.local](https://docs.pwntools.com/en/stable/context.html).
:::

::: tahmin Aynı bayt, iki yorum
```setup
import os
os.environ["PWNLIB_NOTERM"] = "1"
```
```python
from pwnlib.context import context
from pwnlib.util.packing import p16, u16

with context.local(endian="big", signed=False):
    ham = p16(0x8001)
    print(ham.hex(), u16(ham), u16(ham, sign=True))
    with context.local(endian="little"):
        print(u16(ham))
    print(context.endian)
```

???

```text
8001 32769 -32767
384
big
```

`80 01` big-endian unsigned yorumda 32769, signed yorumda −32767'dir. Little-endian yorum `0x0180 = 384` olur. İç context dış ayarı kalıcı değiştirmez.
:::

::: anlat Dersin kayıt biçimi
Bu **Pafta için tasarlanmış küçük bir biçimdir**, gerçek bir ağ protokolü diye sunulmaz:

| Baytlar | Alan |
|---|---|
| 0–1 | Gövde uzunluğu: 16 bit unsigned, big-endian |
| 2–5 | Ölçüm: 32 bit signed, little-endian |
| 6 ve sonrası | 0–16 baytlık gövde |

Uzunluk metin karakteri sayısı değil **bayt sayısıdır**. Örneğin `"ş".encode("utf-8")` iki bayt üretir. Her alanın endian'ı farklı olabilir; makinenin mimarisi protokolün alan düzeni yerine geçmez.
:::

::: gorev Hazır paketleyiciyi uyarla
`cerceve_yaz(sayi, veri)` yaz: yukarıdaki biçimde bir `bytes` döndürsün.
`sayi` tam olarak `int` olmalı (`bool` kabul edilmez), −2147483648 ile 2147483647 **dahil** aralığında olmalı. `veri` `bytes` olmalı ve uzunluğu 0–16 **dahil** olmalı. Her geçersiz girişte `ValueError` yükselt. Dışarıdaki context ayarını değiştirme.

```setup
import os
os.environ["PWNLIB_NOTERM"] = "1"
```
```starter
from pwnlib.util.packing import p16, p32

def cerceve_yaz(sayi, veri):
    return p16(len(veri)) + p32(sayi) + veri
```
```test
import struct
from pwnlib.context import context
f = need("cerceve_yaz")
with context.local(endian="big", signed=True):
    for sayi in (-2147483648, -2147483647, -1, 0, 1, 0x12345678, 2147483646, 2147483647):
        for veri in (b"", b"\x00", b"\xff\x00AB", bytes(range(15)), bytes(range(16))):
            beklenen = struct.pack(">H", len(veri)) + struct.pack("<i", sayi) + veri
            eq(f(sayi, veri), beklenen, f"sayi={sayi}, uzunluk={len(veri)}")
    eq((context.endian, context.signed), ("big", True), "Çağrı context'i korur")
with context.local(endian="little", signed=False):
    eq(f(-1, b"AB"), b"\x00\x02\xff\xff\xff\xffAB", "Alanlar dış context'ten bağımsız")
    eq((context.endian, context.signed), ("little", False), "İkinci context de korunur")
for sayi in (-2147483649, 2147483648, True, 1.5, "1", None):
    raises(ValueError, f, sayi, b"", msg=f"Geçersiz sayı: {sayi!r}")
for veri in (b"x" * 17, "AB", bytearray(b"AB"), None):
    raises(ValueError, f, 0, veri, msg="Uzunluk ve bytes türü denetlenir")
```
```solution
from pwnlib.util.packing import p16, p32

def cerceve_yaz(sayi, veri):
    if type(sayi) is not int or not -2147483648 <= sayi <= 2147483647:
        raise ValueError("32 bit signed sayı gerekli")
    if not isinstance(veri, bytes) or len(veri) > 16:
        raise ValueError("En fazla 16 bayt gerekli")
    return (p16(len(veri), endian="big", sign=False)
            + p32(sayi, endian="little", sign=True) + veri)
```
```hint
Önce tür ve aralıkları doğrula. İki alanın endian ve sign seçeneklerini ayrı ayrı ver; varsayılan context'e güvenme.
```
:::

::: gorev Gelen kaydı aç
`cerceve_oku(ham)` yaz. Geçerli kayıtta `(sayi, veri)` tuple'ı döndürsün.
`ham` bytes olmalı; en az altı baytlık başlığı bulunmalı; bildirilen uzunluk 0–16 dahil olmalı ve **dosyanın toplam uzunluğu tam `6 + uzunluk`** olmalı. Kısa veri kadar sonda fazladan bayt da `ValueError` sebebidir. Context'i değiştirme.

```setup
import os
os.environ["PWNLIB_NOTERM"] = "1"
```
```starter
from pwnlib.util.packing import u16, u32

def cerceve_oku(ham):
    return u32(ham[2:6]), ham[6:]
```
```test
import struct
from pwnlib.context import context
f = need("cerceve_oku")
with context.local(endian="big", signed=False):
    for sayi in (-2147483648, -1, 0, 0x12345678, 2147483647):
        for veri in (b"", b"\x00", b"\xffab", bytes(range(15)), bytes(range(16))):
            ham = struct.pack(">H", len(veri)) + struct.pack("<i", sayi) + veri
            eq(f(ham), (sayi, veri), f"sayi={sayi}, uzunluk={len(veri)}")
    eq((context.endian, context.signed), ("big", False), "Context korunur")
with context.local(endian="little", signed=True):
    eq(f(b"\x00\x01\xff\xff\xff\xffZ"), (-1, b"Z"), "İkinci context")
for ham in (b"", b"\0" * 5, b"\0" * 7, b"\0\1" + b"\0" * 4,
            b"\0\2" + b"\0" * 4 + b"X", b"\0\1" + b"\0" * 4 + b"XY",
            b"\0\x11" + b"\0" * 4 + b"x" * 17,
            b"\xff\xff" + b"\0" * 4, "", bytearray(6), None):
    raises(ValueError, f, ham, msg="Eksik/fazla/uygunsuz kayıt reddedilir")
```
```solution
from pwnlib.util.packing import u16, u32

def cerceve_oku(ham):
    if not isinstance(ham, bytes) or len(ham) < 6:
        raise ValueError("Eksik başlık")
    uzunluk = u16(ham[:2], endian="big", sign=False)
    if uzunluk > 16 or len(ham) != 6 + uzunluk:
        raise ValueError("Uzunluk uyuşmuyor")
    sayi = u32(ham[2:6], endian="little", sign=True)
    return sayi, ham[6:]
```
```hint
İlk iki bayttaki uzunluğu açmadan önce başlığın varlığını denetle. Gövdeyi kesip fazlalığı atmak bozuk kaydı sessizce kabul eder.
```
:::
