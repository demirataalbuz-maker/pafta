---
id: p82
title: ctypes · Native Kütüphaneyi Python'dan Çağırmak
summary: ctypes ile Windows'un native kütüphanesini (kernel32) yüklemek; c tiplerinin boyutları ve 64 bit ABI; restype ve argtypes vermenin neden zorunlu olduğu (varsayılan c_int'in 64 bit işaretçiyi kırpması), geniş karakter (c_wchar_p) marshalling'i ve UTF-16 kod birimi sayımı; use_last_error ile GetLastError'u temiz okumak ve başarısız çağrıyı (dönüş değeri + hata kodu) ayırmak; gerçek derleyiciyle üretilmiş kendi test DLL'inde imzayı C başlığından kurmak (32 biti aşan dönüş, argtypes'sız double, C dizisi, void*).
timeout: 60
---

::: anlat Bir kütüphaneyi yüklemek ve tipleri tanımak
Python'un `ctypes` modülü, derlenmiş bir native kütüphaneyi (`.dll`, `.so`) yükleyip içindeki fonksiyonları doğrudan çağırmanı sağlar. Bir aracı tersine okurken, bir sistem çağrısını denerken ya da yalnız bir C API'sini anlamak için kullanılır. **Bu ders Windows'ta çalışır**; native kütüphane `kernel32`'dir.

```python
import ctypes
k = ctypes.WinDLL("kernel32", use_last_error=True)
```

| Yükleyici | Çağrı kuralı |
|---|---|
| `ctypes.CDLL(ad)` | cdecl (libc, çoğu `.so`) |
| `ctypes.WinDLL(ad)` | stdcall (Win32 API'leri) |

Native kod baytlarla çalışır; Python nesnesini o baytlara **ctypes tipleri** çevirir. Bir tipin kaç bayt olduğu platformun ABI'sini belirler:

```python
from ctypes import c_int, c_long, c_longlong, c_void_p, c_wchar, c_size_t, sizeof
print(8 * sizeof(c_void_p))        # 64  (bu Python 64 bit)
for t in (c_int, c_long, c_longlong, c_void_p, c_wchar, c_size_t):
    print(t.__name__, sizeof(t))
```

Bu derste ölçüldü (Win64, Python 3.11): `c_int` 4, `c_long` **4**, `c_longlong` 8, `c_void_p` **8**, `c_wchar` **2**, `c_size_t` 8. İki ayrıntı taşınabilirliği bozar: Windows'ta `long` 64 bitte de 4 bayttır (Linux'ta 8), ve `c_wchar` Windows'ta 2 bayt (UTF-16), Linux'ta 4 bayttır. Bir işaretçiyi tutacak değişken `c_void_p`/`c_size_t` olmalı, `c_int` değil.
:::

::: anlat restype, argtypes ve GetLastError
ctypes bir fonksiyonun imzasını bilmez. Söylemezsen **dönüşü `c_int` sayar** ve argümanları tahmin eder. 64 bitte bu sessiz bir hataya yol açar: bir işaretçi/handle döndüren fonksiyonun 8 baytlık değeri 4 bayta kırpılır.

```python
import ctypes
from ctypes import c_void_p, c_wchar_p
k = ctypes.WinDLL("kernel32", use_last_error=True)
print(k.GetModuleHandleW("kernel32.dll"))     # -1931476992  : 64 bit handle c_int'e kırpıldı
k.GetModuleHandleW.restype = c_void_p
k.GetModuleHandleW.argtypes = [c_wchar_p]
print(k.GetModuleHandleW("kernel32.dll") > 0) # True : artık tam değer
```

Bu yüzden her native fonksiyon için **önce imzayı bildir**:

- `fn.restype` = dönüş tipi (işaretçi/handle için `c_void_p`, void için `None`).
- `fn.argtypes` = argüman tiplerinin listesi. Bu, Python nesnesini doğru baytlara çevirir ve yanlış türü erkenden yakalar.

Geniş karakterli (`W` ekli) Win32 fonksiyonları `c_wchar_p` ister; ctypes `str`'i UTF-16'ya çevirir. Fonksiyonun döndürdüğü uzunluk **kod birimi** sayısıdır, karakter değil: BMP dışı bir karakter (çoğu emoji) iki kod birimidir.

Bir çağrı başarısız olduğunda nedenini `GetLastError` söyler. ctypes bunu güvenli okumak için kütüphaneyi `use_last_error=True` ile yükletir ve değeri `ctypes.get_last_error()` ile verir (işletim sisteminin `GetLastError`'u başka çağrılarla ezilebilir; bu yol çağrının hemen sonrasını saklar):

```python
import ctypes
from ctypes import get_last_error
k = ctypes.WinDLL("kernel32", use_last_error=True)
k.SetLastError(0)
h = k.GetModuleHandleW("pafta_yok.dll")       # yüklü değil
print(h, get_last_error())                    # 0 126   (126 = ERROR_MOD_NOT_FOUND)
```

> [!TUZAK] Dönüş değeri "hata" demektir, hata kodu "neden"
> Önce **dönüş değerine** bak: fonksiyon başarısızlığı dönüşüyle bildirir (handle 0, dönüş 0/`FALSE`). Hata kodunu **ancak dönüş başarısızlık diyorsa** oku; başarılı bir çağrıdan sonra `GetLastError` eski bir değeri taşıyabilir, sıfırlamaz. Bir de hata kodunu çağrının **hemen** ardından oku: araya giren her Win32 çağrısı onu değiştirir.
:::

::: tahmin restype'siz handle
```python
import ctypes
from ctypes import c_void_p
k = ctypes.WinDLL("kernel32", use_last_error=True)
a = k.GetModuleHandleW("kernel32.dll")
k.GetModuleHandleW.restype = c_void_p
b = k.GetModuleHandleW("kernel32.dll")
print(a < 0)
print(b > 0xffffffff)
print(a == (b & 0xffffffff) - 0x100000000)
```

???

```text
True
True
True
```

İlk çağrıda `restype` ayarlı değil: dönüş `c_int` sayılır ve gerçek 64 bitlik handle'ın yalnız alt 4 baytı, **işaretli** olarak alınır — büyük bir handle'ın en üst biti 1 olduğu için `a` negatif çıkar. `restype = c_void_p` dedikten sonra `b` tam değerdir ve 32 bitin üstündedir. Üçüncü satır ilişkiyi gösterir: `a`, `b`'nin alt 32 bitinin işaretli yorumudur. Handle/işaretçi döndüren bir fonksiyonda `restype`'i ayarlamayı unutmak, karşılaştırmaları ve sonraki çağrılara geçirmeyi sessizce bozar.
:::

::: gorev İmzayı bildir ve genişliği ölç
`uzunluklar(metinler)` yaz: `kernel32`'nin `lstrlenW` fonksiyonunu doğru imzayla (`argtypes=[c_wchar_p]`, `restype=c_int`) kurup her metnin uzunluğunu ölçen bir liste döndür. `lstrlenW` UTF-16 **kod birimi** sayar.

- Boş metin 0 verir.
- `metinler` boşsa `[]` döndür.

```starter
import ctypes
from ctypes import c_wchar_p, c_int

def uzunluklar(metinler):
    k = ctypes.WinDLL("kernel32", use_last_error=True)
    return [k.lstrlenW(m) for m in metinler]
```

```test
f = need("uzunluklar")
eq(f(["", "a", "pafta"]), [0, 1, 5], "boş, tek harf, beş harf")
eq(f(["pafta çğüş"]), [10], "Türkçe harfler BMP: her biri tek kod birimi")
eq(f(["ab\U0001F600cd"]), [6], "emoji BMP dışı: iki kod birimi sayılır (a b 😀=2 c d)")
eq(f([]), [], "boş liste")
import ctypes, inspect, re
# İmza bildirilmişse ctypes yanlış türü çağrıdan önce reddeder; bildirilmemişse baytları
# geniş karakter sanıp sayı döndürür (bu derste ölçüldü: b"abc" → 2).
raises(ctypes.ArgumentError, f, [b"abc"], msg="argtypes bildirilince bytes argümanı reddedilir")
src = re.sub(r"#[^\n]*", "", inspect.getsource(f))      # yorum satırı imza yerine geçmez
ok("argtypes" in src and "restype" in src, "imzayı bildir: argtypes ve restype")
```

```solution
import ctypes
from ctypes import c_wchar_p, c_int

def uzunluklar(metinler):
    k = ctypes.WinDLL("kernel32", use_last_error=True)
    k.lstrlenW.argtypes = [c_wchar_p]
    k.lstrlenW.restype = c_int
    return [k.lstrlenW(m) for m in metinler]
```

```hint
Fonksiyon nesnesini bir kez alıp imzasını ayarla: `fn = k.lstrlenW; fn.argtypes = [c_wchar_p]; fn.restype = c_int`. Sonra her metin için `fn(m)`.
```
:::

::: gorev Yüklü mü, değilse neden
`modul_durumu(adlar)` yaz: her modül adı için `GetModuleHandleW` çağırıp `(ad, yuklu, hata)` demetlerinden bir liste döndür.

- `yuklu`: handle sıfırdan farklıysa `True`.
- `hata`: yüklü değilse `GetLastError` değeri (ör. yüklenmemiş modül için 126); yüklüyse `0`.
- Handle'ı `restype = c_void_p` ile al (kırpılmasın); kütüphaneyi `use_last_error=True` ile yükle ve hata kodunu çağrının **hemen** ardından, yalnız handle 0 ise oku.

```setup
import ctypes
# Testin karşılaştırması için gerçek bir yüklü ve bir yüklü-olmayan modül adı hazırla
```

```starter
import ctypes
from ctypes import c_void_p, c_wchar_p, get_last_error

def modul_durumu(adlar):
    k = ctypes.WinDLL("kernel32", use_last_error=True)
    sonuc = []
    for ad in adlar:
        h = k.GetModuleHandleW(ad)
        sonuc.append((ad, h != 0, get_last_error()))
    return sonuc
```

```test
f = need("modul_durumu")
r = f(["kernel32.dll", "pafta_yok_12345.dll", "ntdll.dll"])
eq([(ad, yuklu) for ad, yuklu, _ in r],
   [("kernel32.dll", True), ("pafta_yok_12345.dll", False), ("ntdll.dll", True)],
   "kernel32 ve ntdll yüklü; uydurma ad değil")
eq([h for _, yuklu, h in r if yuklu], [0, 0], "yüklü modüllerde hata 0")
eq([h for ad, yuklu, h in r if not yuklu], [126], "yüklü olmayan modül: ERROR_MOD_NOT_FOUND (126)")
eq(f([]), [], "boş liste")
# Yüklü handle 32 biti aşar (bu derste ölçüldü: kernel32 → 0x7ffa8ce00000; varsayılan c_int
# restype onu negatif bir sayıya kırpar). Kırpılan değer de sıfırdan farklı olduğu için bu
# görevin dönüşünden anlaşılmaz; kaynakta aranır, yorum satırı yeterli sayılmaz.
import inspect, re
ok("c_void_p" in re.sub(r"#[^\n]*", "", inspect.getsource(f)), "handle'ı c_void_p restype ile al")
```

```solution
import ctypes
from ctypes import c_void_p, c_wchar_p, get_last_error

def modul_durumu(adlar):
    k = ctypes.WinDLL("kernel32", use_last_error=True)
    k.GetModuleHandleW.argtypes = [c_wchar_p]
    k.GetModuleHandleW.restype = c_void_p
    sonuc = []
    for ad in adlar:
        k.SetLastError(0)
        h = k.GetModuleHandleW(ad)
        if h:
            sonuc.append((ad, True, 0))
        else:
            sonuc.append((ad, False, get_last_error()))
    return sonuc
```

```hint
`restype = c_void_p` olmazsa büyük bir handle negatife kırpılır ve `h != 0` yine doğru olsa da handle'ı sonraki çağrıya geçiremezsin. Hata kodunu yalnız `h` 0 (yüklü değil) iken oku; yüklüyken `0` yaz.
```

```hint
`GetLastError` başarılı çağrıdan sonra sıfırlanmaz. Her çağrıdan önce `k.SetLastError(0)` ve çağrının hemen ardından `get_last_error()` okursan eski değerleri taşımazsın.
```
:::

::: anlat Kendi test kitaplığın
`kernel32` gerçek ama senin yazmadığın bir kitaplıktır; imzasını belgeden okursun. Bir aracın kendi DLL'ini ya da `.so`'sunu çağırırken ise imzayı çoğu zaman **C başlık dosyasından** çıkarırsın. Bu bölümde dersin hazırlığı aşağıdaki C kaynağını Kali'deki `x86_64-w64-mingw32-gcc` ile 64 bit bir Windows DLL'ine derler ve çalışma klasörüne `pafta_test.dll` adıyla koyar. Kod yalnız hesap yapar; dosyaya ya da ağa dokunmaz.

```c norun
__declspec(dllexport) long long carp(int a, int b) { return (long long)a * b; }
__declspec(dllexport) double yarim(double x) { return x / 2; }
__declspec(dllexport) int topla(const int *d, int n) { int t = 0; for (int i = 0; i < n; i++) t += d[i]; return t; }
__declspec(dllexport) void *adres(void) { return (void *)0x123456789ABCULL; }
```

| C imzası | `restype` | `argtypes` |
|---|---|---|
| `long long carp(int, int)` | `c_longlong` | `[c_int, c_int]` |
| `double yarim(double)` | `c_double` | `[c_double]` |
| `int topla(const int *, int)` | `c_int` (varsayılan) | `[POINTER(c_int), c_int]` |
| `void *adres(void)` | `c_void_p` | `[]` |

Bu derste ölçülen üç hata:

- `restype` verilmezse ctypes dönüşü `int` (32 bit) sayar: `carp(100000, 100000)` 10 000 000 000 yerine **1410065408** döner (alt 32 bit).
- `argtypes` verilmezse ctypes Python `float`'ını **dönüştürmez**: `yarim(3.0)` `ArgumentError: Don't know how to convert parameter 1` verir. Tam sayıyı ise sessizce `int` olarak geçirir. Bu durumda işlev kayan nokta yazmacındaki anlamsız bir değeri okur.
- `argtypes` `POINTER(c_int)` diyorsa Python listesi kabul edilmez (`expected LP_c_long instance instead of list`). Önce bir C dizisi kur: `(c_int * len(liste))(*liste)`. (`c_int`, Windows'ta `c_long`'un takma adıdır; mesaj bu yüzden `LP_c_long` der.)

```setup
import os, runpy, shutil, sys
_s = next(os.path.dirname(m.__file__) for m in list(sys.modules.values())
          if os.path.basename(getattr(m, "__file__", None) or "") == "py_harness.py")
runpy.run_path(os.path.join(_s, "ctypes_lab.py"))
import ctlab
KAYNAK = r'''__declspec(dllexport) long long carp(int a, int b) { return (long long)a * b; }
__declspec(dllexport) double yarim(double x) { return x / 2; }
__declspec(dllexport) int topla(const int *d, int n) { int t = 0; for (int i = 0; i < n; i++) t += d[i]; return t; }
__declspec(dllexport) void *adres(void) { return (void *)0x123456789ABCULL; }
'''
shutil.copyfile(ctlab.derle(KAYNAK, "win64-dll"), "pafta_test.dll")
```
:::

::: tahmin Kendi kitaplığında imza
Çalışma klasöründe yukarıdaki `pafta_test.dll` var. Ne yazar?

```python
import ctypes, os

L = ctypes.CDLL(os.path.abspath("pafta_test.dll"))
print(L.carp(100000, 100000))
L.carp.restype = ctypes.c_longlong
print(L.carp(100000, 100000))
L.yarim.restype = ctypes.c_double
print(L.yarim(3))
L.yarim.argtypes = [ctypes.c_double]
print(L.yarim(3))
```

???

`1410065408`, `10000000000`, `1e-323` ve `1.5`.

İlk çağrıda `restype` yok: 10¹⁰'un yalnız alt 32 biti okunur. İkinci çağrıda dönüş doğru genişlikte. Üçüncüsü sinsidir: dönüş türü doğru (`c_double`), ama `argtypes` olmadığı için `3` bir **tam sayı** olarak, bit deseni `3` olarak geçti. İşlev bu deseni double sanıp ikiye böldü ve en küçük normal-altı sayılardan biri çıktı. Hata yok, uyarı yok. `argtypes` verilince ctypes `3`'ü `3.0`'a çevirir ve sonuç `1.5` olur.

```setup
import os, runpy, shutil, sys
_s = next(os.path.dirname(m.__file__) for m in list(sys.modules.values())
          if os.path.basename(getattr(m, "__file__", None) or "") == "py_harness.py")
runpy.run_path(os.path.join(_s, "ctypes_lab.py"))
import ctlab
KAYNAK = r'''__declspec(dllexport) long long carp(int a, int b) { return (long long)a * b; }
__declspec(dllexport) double yarim(double x) { return x / 2; }
__declspec(dllexport) int topla(const int *d, int n) { int t = 0; for (int i = 0; i < n; i++) t += d[i]; return t; }
__declspec(dllexport) void *adres(void) { return (void *)0x123456789ABCULL; }
'''
shutil.copyfile(ctlab.derle(KAYNAK, "win64-dll"), "pafta_test.dll")
```
:::

::: gorev İmzaları başlıktan kur
`kendi_kitaplik(a, b, x, sayilar)` yaz. Çalışma klasöründeki `pafta_test.dll`'i yükle (tam yoluyla), dört işlevin `restype`/`argtypes`'ını yukarıdaki C imzalarına göre bildir ve şu demeti döndür:

`(carp(a, b), yarim(x), topla(sayilar), adres())`

- `x` tam sayı da olabilir; `yarim` her zaman doğru sonucu vermeli.
- `sayilar` bir Python listesidir; `topla`'ya C dizisi olarak ver, uzunluğu da geç.
- `adres()`'in değerini Python tam sayısı olarak döndür.

```setup
import os, runpy, shutil, sys
_s = next(os.path.dirname(m.__file__) for m in list(sys.modules.values())
          if os.path.basename(getattr(m, "__file__", None) or "") == "py_harness.py")
runpy.run_path(os.path.join(_s, "ctypes_lab.py"))
import ctlab
KAYNAK = r'''__declspec(dllexport) long long carp(int a, int b) { return (long long)a * b; }
__declspec(dllexport) double yarim(double x) { return x / 2; }
__declspec(dllexport) int topla(const int *d, int n) { int t = 0; for (int i = 0; i < n; i++) t += d[i]; return t; }
__declspec(dllexport) void *adres(void) { return (void *)0x123456789ABCULL; }
'''
shutil.copyfile(ctlab.derle(KAYNAK, "win64-dll"), "pafta_test.dll")
```

```starter
import ctypes, os

def kendi_kitaplik(a, b, x, sayilar):
    L = ctypes.CDLL(os.path.abspath("pafta_test.dll"))
    dizi = (ctypes.c_int * len(sayilar))(*sayilar)
    return (L.carp(a, b), L.yarim(ctypes.c_double(x)), L.topla(dizi, len(sayilar)), L.adres())
```

```test
f = need("kendi_kitaplik")
eq(f(100000, 100000, 3.0, [1, 2, 3, 4]), (10000000000, 1.5, 10, 0x123456789ABC),
   "dönüş 32 biti aşar: restype c_longlong; işaretçi 48 bit: restype c_void_p")
eq(f(-70000, 70000, 3, []), (-4900000000, 1.5, 0, 0x123456789ABC),
   "negatif çarpım; x tam sayı gelse de argtypes onu double'a çevirir; boş dizi 0")
eq(f(7, 6, -5, [10, -3]), (42, -2.5, 7, 0x123456789ABC), "küçük değerler ve negatif double")
r = f(46341, 46341, 1, [2147483647, 1])
eq(r[0], 2147488281, "2³¹'i biraz aşan çarpım: int olarak okunsaydı negatif çıkardı")
ok(isinstance(r[3], int), "adres Python tam sayısı", got=type(r[3]).__name__)
```

```solution
import ctypes, os
from ctypes import POINTER, c_double, c_int, c_longlong, c_void_p

def kendi_kitaplik(a, b, x, sayilar):
    L = ctypes.CDLL(os.path.abspath("pafta_test.dll"))
    L.carp.argtypes, L.carp.restype = [c_int, c_int], c_longlong
    L.yarim.argtypes, L.yarim.restype = [c_double], c_double
    L.topla.argtypes, L.topla.restype = [POINTER(c_int), c_int], c_int
    L.adres.argtypes, L.adres.restype = [], c_void_p
    dizi = (c_int * len(sayilar))(*sayilar)
    return (L.carp(a, b), L.yarim(x), L.topla(dizi, len(sayilar)), L.adres())
```

```hint
Her işlevin iki özniteliği var: `L.carp.restype = c_longlong`, `L.carp.argtypes = [c_int, c_int]`. `restype` verilmeyen her işlev `int` döndürüyor sayılır.
```

```hint
`void *` dönen işlevde `restype = c_void_p` ver. ctypes bu değeri doğrudan Python tam sayısı olarak döndürür; işaretçi `NULL` olsaydı `None` dönerdi.
```
:::
