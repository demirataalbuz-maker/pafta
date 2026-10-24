---
id: p82
title: ctypes · Native Kütüphaneyi Python'dan Çağırmak
summary: ctypes ile Windows'un native kütüphanesini (kernel32) yüklemek; c tiplerinin boyutları ve 64 bit ABI; restype ve argtypes vermenin neden zorunlu olduğu (varsayılan c_int'in 64 bit işaretçiyi kırpması), geniş karakter (c_wchar_p) marshalling'i ve UTF-16 kod birimi sayımı; use_last_error ile GetLastError'u temiz okumak ve başarısız çağrıyı (dönüş değeri + hata kodu) ayırmak.
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
import inspect
src = inspect.getsource(f)
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
# yüklü handle gerçekten 32 biti aşabilir: c_void_p ile kırpılmadan alınmalı
import inspect
ok("c_void_p" in inspect.getsource(f), "handle'ı c_void_p restype ile al")
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
