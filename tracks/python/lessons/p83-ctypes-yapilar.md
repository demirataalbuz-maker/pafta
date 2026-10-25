---
id: p83
title: ctypes · Yapılar, Hizalama ve İşaretçiler
summary: ctypes.Structure ile C yapısı tanımlamak; doğal hizalamanın doldurma (padding) eklemesi, _pack_ ile sıkıştırma, offset ve sizeof; bir Win32 çağrısına byref ile yapı verip doldurtmak (SYSTEMTIME/FILETIME), API'nin gün-of-week gibi alanları hesaplaması, geçersiz girdide dönüş 0 + hata 87; from_buffer_copy ile ham baytları bir başlık yapısına çözmek ve on-wire paketlemenin yanlış olması durumunda alanların kayması; aynı yapının win32, win64 (LLP64) ve linux64 (LP64) yerleşimini gerçek derleyicilerin ölçümüyle karşılaştırmak.
timeout: 60
---

::: anlat Yapı, hizalama ve doldurma
C'de bir `struct` ardışık alanlardır, ama derleyici her alanı **hizalar**: 4 baytlık bir alan 4'ün katı bir adreste başlamalıdır, bu yüzden araya **doldurma** baytları girer. `ctypes.Structure` aynı kuralı uygular; bir native yapıyı Python'dan okuyacaksan boyutunu ve alan konumlarını doğru bilmen gerekir.

```python
from ctypes import Structure, c_uint8, c_uint16, c_uint32, c_uint64, sizeof
class A(Structure):
    _fields_ = [("a", c_uint8), ("b", c_uint32)]
print(sizeof(A), A.b.offset)        # 8 4  : a'dan sonra 3 doldurma, b 4. baytta
class B(Structure):
    _pack_ = 1
    _fields_ = [("a", c_uint8), ("b", c_uint32)]
print(sizeof(B), B.b.offset)        # 5 1  : _pack_=1 doldurmayı kapatır
```

Bu derste ölçüldü: `{u8, u32}` doğal hizalamada **8** bayt (b @4), `_pack_=1` ile **5** bayt (b @1). `{u8, u8, u16, u64}` doğal hizalamada **16** bayttır ve alanlar `[0, 1, 2, 8]` konumundadır — `u64`'ten önce dört bayt doldurma girer. Yapının toplam boyutu da en geniş alanının katına yuvarlanır: `{u16, u8}` → 4 bayt.

| `_fields_` | doğal `sizeof` | `_pack_=1` |
|---|---|---|
| `u8, u32` | 8 | 5 |
| `u16, u8` | 4 | 3 |
| `u8, u8, u16, u64` | 16 | 12 |

Ham baytları bir yapıya çözmek için `Yapı.from_buffer_copy(ham)` kullanılır: baytları alanlara eşler (kopyalayarak). Baytlar yapının boyutundan kısaysa `ValueError` yükseltir.

> [!TUZAK] On-wire biçim senin yapına uymak zorunda değil
> Diskte ya da ağda bir başlık çoğu zaman **paketlenmiştir** (doldurma yok). Onu doğal hizalamalı bir `Structure` ile çözersen alanlar kayar ve yanlış değer okursun. Belgelenen baytı say: biçim paketliyse yapını da `_pack_ = 1` yap. Boyut bile tutmayabilir; bir alanı okumadan önce `sizeof` ile baytların uzunluğunu karşılaştır.
:::

::: anlat Yapıyı bir API'ye doldurtmak
Bir Win32 çağrısı çoğu zaman sana bir yapı **işaretçisi** ister ve yapıyı kendisi doldurur. `ctypes.byref(nesne)` o nesnenin adresini geçirir; çağrı dönünce alanlar dolmuştur. Zaman çevrimi iyi bir örnektir: `SystemTimeToFileTime` bir `SYSTEMTIME`'ı 1601'den beri geçen 100 ns'lik sayıya (`FILETIME`) çevirir, `FileTimeToSystemTime` tersini yapar ve **haftanın gününü de hesaplar**.

```python
import ctypes
from ctypes import Structure, c_uint16, c_uint32, byref, POINTER, c_int
k = ctypes.WinDLL("kernel32", use_last_error=True)
class SYSTEMTIME(Structure):
    _fields_ = [(n, c_uint16) for n in
                ("wYear", "wMonth", "wDayOfWeek", "wDay", "wHour", "wMinute", "wSecond", "wMilliseconds")]
class FILETIME(Structure):
    _fields_ = [("lo", c_uint32), ("hi", c_uint32)]
k.SystemTimeToFileTime.argtypes = [POINTER(SYSTEMTIME), POINTER(FILETIME)]
k.SystemTimeToFileTime.restype = c_int
st = SYSTEMTIME(wYear=2026, wMonth=1, wDay=1)
ft = FILETIME()
ok = k.SystemTimeToFileTime(byref(st), byref(ft))
print(ok, (ft.hi << 32) | ft.lo)      # 1 134116992000000000
```

Doğru imza burada iki kez önemlidir: `argtypes` olmadan ctypes yapı işaretçisini yanlış geçirebilir, ve `SYSTEMTIME` alan sırası/tipi gerçek yapıyla **birebir** aynı olmalıdır (sekiz adet `WORD`), yoksa çağrı çöp okur.

Geçersiz girdide API dönüşüyle bildirir: `SystemTimeToFileTime` olmayan bir tarihte (ay 13) **0** döner ve `GetLastError` **87** (ERROR_INVALID_PARAMETER) olur. Dönüşü denetlemeden sonucu kullanma.

`byref` yalnız çağrı süresince adres geçirir; kalıcı bir işaretçi nesnesi gerekiyorsa `pointer(nesne)` kullanılır ve `p.contents` ile hedefe yazıp okuyabilirsin:

```python
from ctypes import pointer, c_int
x = c_int(5)
p = pointer(x)
p.contents.value = 9
print(x.value)                         # 9  : aynı belleğe yazdı
```
:::

::: tahmin Doldurma nerede?
```python
from ctypes import Structure, c_uint8, c_uint16, c_uint64, sizeof
class K(Structure):
    _fields_ = [("bayrak", c_uint8), ("kod", c_uint16), ("damga", c_uint64)]
print(sizeof(K), K.kod.offset, K.damga.offset)
class P(Structure):
    _pack_ = 1
    _fields_ = [("bayrak", c_uint8), ("kod", c_uint16), ("damga", c_uint64)]
print(sizeof(P), P.kod.offset, P.damga.offset)
```

???

```text
16 2 8
11 1 3
```

Doğal hizalamada `bayrak` (1 bayt) 0'da; `kod` (2 bayt) 2'nin katında başlamalı, araya 1 doldurma girer, 2'de; `damga` (8 bayt) 8'in katında başlamalı, 4'ten 8'e kadar doldurma, 8'de. Toplam 16. `_pack_ = 1` bütün doldurmayı kaldırır: `kod` 1'de, `damga` 3'te, toplam 11. Aynı üç alan, iki farklı yerleşim: bir native yapıyı okurken hangisinin geçerli olduğunu baytı sayarak doğrulamazsan yanlış ofsetten okursun.
:::

::: gorev SYSTEMTIME'ı FILETIME'a çevir
`ticke(tarihler)` yaz: her tarih `(yil, ay, gun, saat, dakika, saniye)` demetidir. Her biri için bir `SYSTEMTIME` kurup `SystemTimeToFileTime` ile 100 ns'lik `FILETIME` değerine (`(hi << 32) | lo`) çevir ve bir liste döndür. Çağrı başarısızsa (geçersiz tarih, dönüş 0) o öğe `None` olsun.

- `SYSTEMTIME` sekiz `WORD` alanıdır; `wDayOfWeek` ve `wMilliseconds`'ı 0 bırak.
- İmzayı bildir; dönüşü denetlemeden değeri kullanma.

```starter
import ctypes
from ctypes import Structure, c_uint16, c_uint32, byref, POINTER, c_int

class SYSTEMTIME(Structure):
    _fields_ = [(n, c_uint16) for n in
                ("wYear", "wMonth", "wDayOfWeek", "wDay", "wHour", "wMinute", "wSecond", "wMilliseconds")]
class FILETIME(Structure):
    _fields_ = [("lo", c_uint32), ("hi", c_uint32)]

def ticke(tarihler):
    k = ctypes.WinDLL("kernel32", use_last_error=True)
    sonuc = []
    for yil, ay, gun, saat, dakika, saniye in tarihler:
        st = SYSTEMTIME(yil, ay, 0, gun, saat, dakika, saniye, 0)
        ft = FILETIME()
        k.SystemTimeToFileTime(byref(st), byref(ft))
        sonuc.append((ft.hi << 32) | ft.lo)
    return sonuc
```

```test
f = need("ticke")
eq(f([(2026, 1, 1, 0, 0, 0)]), [134116992000000000], "2026-01-01 00:00:00")
eq(f([(2026, 3, 15, 12, 30, 45)]), [134180514450000000], "saat/dakika/saniye de 100 ns'ye katılır")
eq(f([(2000, 1, 1, 0, 0, 0)]), [125911584000000000], "erken tarih")
eq(f([(2026, 13, 1, 0, 0, 0)]), [None], "geçersiz ay: dönüş 0 → None")
eq(f([(2026, 1, 1, 0, 0, 0), (2026, 13, 40, 0, 0, 0), (2000, 1, 1, 0, 0, 0)]),
   [134116992000000000, None, 125911584000000000], "geçerli ve geçersiz karışık")
eq(f([]), [], "boş liste")
```

```solution
import ctypes
from ctypes import Structure, c_uint16, c_uint32, byref, POINTER, c_int

class SYSTEMTIME(Structure):
    _fields_ = [(n, c_uint16) for n in
                ("wYear", "wMonth", "wDayOfWeek", "wDay", "wHour", "wMinute", "wSecond", "wMilliseconds")]
class FILETIME(Structure):
    _fields_ = [("lo", c_uint32), ("hi", c_uint32)]

def ticke(tarihler):
    k = ctypes.WinDLL("kernel32", use_last_error=True)
    k.SystemTimeToFileTime.argtypes = [POINTER(SYSTEMTIME), POINTER(FILETIME)]
    k.SystemTimeToFileTime.restype = c_int
    sonuc = []
    for yil, ay, gun, saat, dakika, saniye in tarihler:
        st = SYSTEMTIME(yil, ay, 0, gun, saat, dakika, saniye, 0)
        ft = FILETIME()
        if k.SystemTimeToFileTime(byref(st), byref(ft)):
            sonuc.append((ft.hi << 32) | ft.lo)
        else:
            sonuc.append(None)
    return sonuc
```

```hint
`SystemTimeToFileTime` başarıda sıfırdan farklı döner. Dönüşü `if` ile denetle: başarıda `(ft.hi << 32) | ft.lo`, başarısızda `None` ekle.
```

```hint
`SYSTEMTIME(yil, ay, 0, gun, ...)` konum sırasına göre: üçüncü alan `wDayOfWeek`, onu 0 bırak. `byref(st)` ve `byref(ft)` ile adresleri geçir.
```
:::

::: gorev Paketli başlığı çöz
`coz_baslik(ham)` yaz: `ham` bir **paketli** (doldurmasız) başlığın baytlarıdır. Alanlar sırayla: `sihir` (4 bayt, küçük-endian u32), `surum` (2 bayt u16), `bayrak` (1 bayt u8), `uzunluk` (4 bayt u32) — toplam 11 bayt. Bir `ctypes.Structure` ile çözüp:

- `sihir`, `b"PAFT"`'ın küçük-endian u32 değerine eşitse `(surum, bayrak, uzunluk)` döndür.
- `sihir` tutmuyorsa ya da `ham` 11 bayttan kısaysa `None` döndür.

Yapıyı `_pack_ = 1` yapmazsan `uzunluk` yanlış ofsetten okunur: on-wire biçim paketlidir.

```setup
import struct
SIHIR = int.from_bytes(b"PAFT", "little")
```

```starter
import ctypes, struct
from ctypes import Structure, c_uint32, c_uint16, c_uint8, sizeof

class Baslik(Structure):
    _fields_ = [("sihir", c_uint32), ("surum", c_uint16), ("bayrak", c_uint8), ("uzunluk", c_uint32)]

def coz_baslik(ham):
    b = Baslik.from_buffer_copy(ham)
    return (b.surum, b.bayrak, b.uzunluk)
```

```test
import struct
f = need("coz_baslik")
SIHIR = int.from_bytes(b"PAFT", "little")
ham = struct.pack("<IHBI", SIHIR, 2, 1, 1000)
eq(len(ham), 11, "paketli başlık 11 bayt")
eq(f(ham), (2, 1, 1000), "sürüm, bayrak ve uzunluk doğru çözülür (paketli)")
eq(f(struct.pack("<IHBI", SIHIR, 5, 255, 70000)), (5, 255, 70000), "u32 uzunluk 65535'i aşar")
eq(f(struct.pack("<IHBI", int.from_bytes(b"XXXX", "little"), 2, 1, 1000)), None, "yanlış sihir")
eq(f(ham[:-1]), None, "10 bayt: eksik başlık")
eq(f(b""), None, "boş")
# Paketli çözüm şart: doğal hizalamalı yapı uzunluğu 8. ofsetten okur, paketli baytta oradaki değer farklıdır
eq(f(struct.pack("<IHBI", SIHIR, 1, 0, 0x04030201)), (1, 0, 0x04030201),
   "uzunluk paketli ofsetten (7) okunur; doğal hizalama (ofset 8) başka değer verirdi")
```

```solution
import ctypes, struct
from ctypes import Structure, c_uint32, c_uint16, c_uint8, sizeof

class Baslik(Structure):
    _pack_ = 1
    _fields_ = [("sihir", c_uint32), ("surum", c_uint16), ("bayrak", c_uint8), ("uzunluk", c_uint32)]

SIHIR = int.from_bytes(b"PAFT", "little")

def coz_baslik(ham):
    if len(ham) < sizeof(Baslik):
        return None
    b = Baslik.from_buffer_copy(ham)
    if b.sihir != SIHIR:
        return None
    return (b.surum, b.bayrak, b.uzunluk)
```

```hint
`_pack_ = 1` olmadan `sizeof(Baslik)` 12 olur ve `uzunluk` 8. ofsetten okunur; paketli baytta o alan 7. ofsettedir. Önce `len(ham) < sizeof(Baslik)` denetle, sonra `from_buffer_copy`.
```

```hint
`SIHIR = int.from_bytes(b"PAFT", "little")` ile beklenen sihri hesapla. `from_buffer_copy` kısa baytta `ValueError` atar; bunu önlemek için uzunluğu önceden denetle.
```
:::

::: anlat 32 bit, 64 bit ve iki farklı "64 bit"
`ctypes.Structure` yapıyı **çalıştığın yorumlayıcının** ABI'sine göre dizer. Bu laboratuvarın Python'u 64 bit Windows'tur. Bir aracın 32 bit sürümüyle ya da Linux'taki karşılığıyla aynı yapıyı paylaşıyorsan boyutlar değişir. Değişmeyeceğini varsaymak, alanları kaydırarak okumak demektir.

Aşağıdaki tablo bu derste **ölçüldü**. Aynı C programı Kali'de üç derleyiciyle derlendi: `i686-w64-mingw32-gcc` (32 bit Windows, Windows'ta WOW64 ile çalıştı), `x86_64-w64-mingw32-gcc` (64 bit Windows) ve `gcc` (64 bit Linux). Her hücre `sizeof / hizalama`:

| Tür | win32 | win64 | linux64 |
|---|---|---|---|
| `char` | 1 / 1 | 1 / 1 | 1 / 1 |
| `short` | 2 / 2 | 2 / 2 | 2 / 2 |
| `int` | 4 / 4 | 4 / 4 | 4 / 4 |
| `long` | 4 / 4 | **4 / 4** | **8 / 8** |
| `long long` | 8 / 8 | 8 / 8 | 8 / 8 |
| `double` | 8 / 8 | 8 / 8 | 8 / 8 |
| `void *` | **4 / 4** | 8 / 8 | 8 / 8 |

İki ayrı "64 bit" var. Windows **LLP64**'tür: `long` 64 bitte de 4 bayttır, yalnız işaretçi ve `long long` 8'dir. Linux **LP64**'tür: `long` de 8'dir. `ctypes.c_long` bu yüzden Windows'ta 4, Linux'ta 8 bayttır. Genişliği sabit bir alan istiyorsan `c_int32`/`c_int64` kullan.

Yapıya etkisi (aynı ölçüm):

| Yapı | win32 | win64 | linux64 |
|---|---|---|---|
| `{char c; void *p; short s;}` | 12 bayt, `p` 4'te, `s` 8'de | 24, 8, 16 | 24, 8, 16 |
| `{char c; long l;}` | 8 bayt, `l` 4'te | 8, 4 | **16, 8** |
| `{char c; long long q;}` | 16 bayt, `q` 8'de | 16, 8 | 16, 8 |

Kural her ABI'de aynıdır, yalnız tablo değişir. Her alan kendi hizalamasının katı olan ilk ofsete konur. Yapının boyutu, en büyük alan hizalamasının katına yuvarlanır (dizide bir sonraki eleman da hizalı başlasın diye).

> [!NOT] 32 bit Windows'ta `long long` da 8'e hizalanır
> 32 bit Linux'un ABI belgesine (i386 System V) göre `long long` ve `double` yapı içinde 4'e hizalanır. Bu laboratuvarda 32 bit Linux derleyicisi yok; bu satır ölçülmedi. Windows'un 32 bit ABI'si ise onları 8'e hizalar: yukarıdaki üçüncü satırı (`q` 8'de) bu derste ölçtük. Aynı "32 bit" de işletim sistemine göre farklıdır.
:::

::: gorev Üç hedefte aynı yapı
`duzen(hedef, alanlar)` yaz. `hedef` `"win32"`, `"win64"` ya da `"linux64"`; `alanlar` C türü adlarının listesidir (`"char"`, `"short"`, `"int"`, `"long"`, `"long long"`, `"double"`, `"void*"`). Yapıyı yukarıdaki ölçülmüş tabloya ve hizalama kuralına göre diz, `(boyut, [ofsetler])` döndür.

Bilinmeyen hedef, bilinmeyen tür ya da boş alan listesi için `None` döndür.

Testler sonucunu, aynı yapıların gerçek derleyicilerle derlenip **çalıştırılan** programlarının yazdığı `sizeof`/`offsetof` değerleriyle karşılaştırır. Derleyiciyi kendin çağırma; kuralı yaz.

```setup
import os, runpy, sys
_s = next(os.path.dirname(m.__file__) for m in list(sys.modules.values())
          if os.path.basename(getattr(m, "__file__", None) or "") == "py_harness.py")
runpy.run_path(os.path.join(_s, "ctypes_lab.py"))
```

```starter
def duzen(hedef, alanlar):
    boyutlar = {"char": 1, "short": 2, "int": 4, "long": 4, "long long": 8, "double": 8, "void*": 8}
    ofsetler, simdi = [], 0
    for alan in alanlar:
        ofsetler.append(simdi)
        simdi += boyutlar[alan]
    return (simdi, ofsetler)
```

```test
import ctypes, ctlab
f = need("duzen")
YAPILAR = [["char", "int"], ["char", "long long"], ["char", "void*", "short"], ["char", "long"],
           ["short", "char", "double", "char"], ["void*", "char"], ["int", "char", "char", "long"],
           ["char"], ["long long", "char"], ["char", "short", "char", "int"], ["char", "char", "void*"],
           ["long", "void*", "int"]]
satirlar = ["#include <stdio.h>", "#include <stddef.h>"]
for i, alanlar in enumerate(YAPILAR):
    govde = " ".join(f"{t.replace('void*', 'void *')} f{j};" for j, t in enumerate(alanlar))
    satirlar.append(f"struct S{i} {{ {govde} }};")
satirlar.append("int main(void) {")
for i, alanlar in enumerate(YAPILAR):
    ofs = "".join(f' printf(" %zu", offsetof(struct S{i}, f{j}));' for j in range(len(alanlar)))
    satirlar.append(f'    printf("%zu", sizeof(struct S{i}));{ofs} printf("\\n");')
satirlar.append("    return 0;\n}\n")
KAYNAK = "\n".join(satirlar)
for hedef in ("win32", "win64", "linux64"):
    olcum = ctlab.calistir(KAYNAK, hedef).split("\n")
    for alanlar, satir in zip(YAPILAR, olcum):
        sayilar = [int(s) for s in satir.split()]
        eq(f(hedef, alanlar), (sayilar[0], sayilar[1:]), f"{hedef} {{{', '.join(alanlar)}}}: gerçek derleyicinin ölçümü")
C = {"char": ctypes.c_char, "short": ctypes.c_short, "int": ctypes.c_int, "long": ctypes.c_long,
     "long long": ctypes.c_longlong, "double": ctypes.c_double, "void*": ctypes.c_void_p}
for alanlar in YAPILAR[:4]:
    Y = type("Y", (ctypes.Structure,), {"_fields_": [(f"f{j}", C[t]) for j, t in enumerate(alanlar)]})
    eq(f("win64", alanlar), (ctypes.sizeof(Y), [getattr(Y, f"f{j}").offset for j in range(len(alanlar))]),
       "win64 bu Python'un kendi ctypes yerleşimiyle aynı")
eq(f("win16", ["char"]), None, "bilinmeyen hedef")
eq(f("win64", ["char", "float128"]), None, "bilinmeyen tür")
eq(f("linux64", []), None, "boş alan listesi")
ok("ctlab" not in src and "subprocess" not in src, "derleyiciyi çağırma; kuralı kendin yaz")
```

```solution
TURLER = {
    "win32":   {"char": 1, "short": 2, "int": 4, "long": 4, "long long": 8, "double": 8, "void*": 4},
    "win64":   {"char": 1, "short": 2, "int": 4, "long": 4, "long long": 8, "double": 8, "void*": 8},
    "linux64": {"char": 1, "short": 2, "int": 4, "long": 8, "long long": 8, "double": 8, "void*": 8},
}

def duzen(hedef, alanlar):
    tablo = TURLER.get(hedef)
    if tablo is None or not alanlar or any(a not in tablo for a in alanlar):
        return None
    ofsetler, simdi, en_buyuk = [], 0, 1
    for alan in alanlar:
        boyut = hizalama = tablo[alan]          # bu türlerde hizalama boyuta eşit (ölçüldü)
        simdi = (simdi + hizalama - 1) // hizalama * hizalama
        ofsetler.append(simdi)
        simdi += boyut
        en_buyuk = max(en_buyuk, hizalama)
    return ((simdi + en_buyuk - 1) // en_buyuk * en_buyuk, ofsetler)
```

```hint
Bir alanı koymadan önce ofseti hizalamanın katına yuvarla: `(simdi + h - 1) // h * h`. Bütün alanlar bitince toplam boyutu da en büyük hizalamanın katına yuvarla. `{"void*", "char"}` win64'te 9 değil 16'dır.
```

```hint
Üç hedefin farkı yalnız iki türde: `void*` (win32'de 4) ve `long` (linux64'te 8). Her hedef için bir boyut tablosu kur; ölçülen tablodaki bütün türlerde hizalama boyuta eşittir.
```
:::
