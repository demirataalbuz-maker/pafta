---
id: c12
title: Windows API Kodunu Okumak
summary: Windows türleri (BYTE, WORD, DWORD, BOOL, HANDLE, LPCWSTR), Macar gösterimi, A ve W sürümlü fonksiyonlar, UTF-16 geniş dizgiler, cb ile cch farkı, dönüş değeri gelenekleri (FALSE, NULL, INVALID_HANDLE_VALUE) ve GetLastError ile hata kodları.
---

::: anlat Windows'un türleri ve adları
Windows için yazılmış C kodu, standart C türlerinin yerine `<windows.h>`'ın kendi adlarını kullanır. Bu adları tanımak, kodu (ve derlenmiş programların içe aktardığı fonksiyon listelerini) okumanın ilk adımıdır:

| Windows türü | Karşılığı |
|---|---|
| `BYTE`, `WORD`, `DWORD`, `QWORD` | 8, 16, 32, 64 bit işaretsiz tam sayı |
| `BOOL` | `int`: sıfır yanlış, sıfırdan farklı doğru (`TRUE` / `FALSE`) |
| `HANDLE` | bir nesneye (dosya, olay, kayıt anahtarı …) tanıtıcı; aslında bir işaretçi |
| `LPVOID` | `void *` |
| `LPSTR` / `LPCSTR` | `char *` / `const char *` |
| `LPWSTR` / `LPCWSTR` | `wchar_t *` / `const wchar_t *`: UTF-16 metin |
| `SIZE_T` | `size_t` |

`LP` ("long pointer") 16 bit Windows'tan kalma bir öneklik; bugün yalnızca "işaretçi" demektir. `C` ise `const`'tur.

### Macar gösterimi
Değişken adlarının önündeki küçük harfler türünü ya da anlamını söyler:

| Önek | Anlamı | Örnek |
|---|---|---|
| `dw` | DWORD | `dwBoyut` |
| `h` | HANDLE | `hDosya` |
| `lp`, `p` | işaretçi | `lpTampon` |
| `sz`, `psz`, `lpsz` | sıfırla biten metin | `szAd` |
| `cb` | **bayt** sayısı (count of bytes) | `cbTampon` |
| `cch` | **karakter** sayısı (count of characters) | `cchAd` |
| `b` | BOOL | `bBasarili` |

`cb` ile `cch` farkı en sık hata kaynaklarından biridir: UTF-16'da bir karakter 2 bayttır. 64 karakterlik bir `WCHAR` tamponu 128 bayttır; bir API `cch` isterken `sizeof(tampon)` vermek, ona tamponun **iki katı** yer varmış gibi söylemektir.

### A ve W fonksiyonları
Metin alan hemen her Windows fonksiyonunun iki sürümü vardır: `CreateFileA` (ANSI: sistemin kod sayfası) ve `CreateFileW` (Wide: UTF-16). Kaynakta yazılan `CreateFile` bir makrodur ve `UNICODE` tanımlıysa `CreateFileW`'ye açılır (C10). Derlenmiş programın içe aktardığı adlarda bu yüzden hep sonu `A` ya da `W` ile biten adları görürsün.

```c
const char    *a = "Pafta";      // 5 karakter + '\0' = 6 bayt
const wchar_t *w = L"Pafta";     // Windows'ta wchar_t 2 bayt: (5 + 1) × 2 = 12 bayt
```
:::

::: anlat Dönüş değerleri ve hatalar
Windows API'si hata bildirmek için tek bir kural kullanmaz; her fonksiyonun belgesine bakmak gerekir. Kod okurken en çok karşılaşılan gelenekler:

| Fonksiyon türü | Başarısızlıkta döner | Ayrıntı |
|---|---|---|
| `BOOL` döndürenler (`ReadFile`, `WriteFile`, `CloseHandle`) | `FALSE` (0) | `GetLastError()` |
| `CreateFileW`, `FindFirstFileW` | `INVALID_HANDLE_VALUE` (−1) | **NULL değil!** |
| çoğu başka tanıtıcı (`CreateEventW`, `LoadLibraryW`) | `NULL` (0) | `GetLastError()` |
| `GetFileSize` | `INVALID_FILE_SIZE` (0xFFFFFFFF) | geçerli bir boyut da olabilir; `GetLastError()` ile ayırt edilir |

```c
HANDLE h = CreateFileW(L"C:\\Veri\\ayar.cfg", GENERIC_READ, FILE_SHARE_READ, NULL,
                       OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
if (h == INVALID_HANDLE_VALUE) {
    DWORD hata = GetLastError();          // 2: ERROR_FILE_NOT_FOUND, 5: ERROR_ACCESS_DENIED
    return hata;
}
BYTE tampon[512];
DWORD okunan = 0;
if (!ReadFile(h, tampon, sizeof tampon, &okunan, NULL)) {
    DWORD hata = GetLastError();
    CloseHandle(h);
    return hata;
}
/* yalnızca 'okunan' kadar bayt geçerlidir */
CloseHandle(h);
```

| Kod | Ad |
|---|---|
| 0 | `ERROR_SUCCESS` |
| 2 | `ERROR_FILE_NOT_FOUND` |
| 3 | `ERROR_PATH_NOT_FOUND` |
| 5 | `ERROR_ACCESS_DENIED` |
| 122 | `ERROR_INSUFFICIENT_BUFFER` |

> [!TUZAK]
> `CreateFileW`'den sonra `if (h == NULL)` yazan kod hatayı hiçbir zaman yakalamaz: başarısız çağrı −1 döndürür, NULL değil. Kod incelemesinde ve hata ayıklamada en sık görülen Windows hatalarından biridir. Bir tanıtıcı döndüren fonksiyonun başarısızlık değerini her zaman belgesinden doğrula.
:::

::: tahmin
Çıktı (Windows):

```c
const char    *a = "Pafta";
const wchar_t *w = L"Pafta";
printf("%zu %zu\n", strlen(a), wcslen(w));
printf("%zu %zu\n", sizeof("Pafta"), sizeof(L"Pafta"));
```

```gercek
5 5
6 12
```

???

`5 5`: iki uzunluk fonksiyonu da sonlandırıcı hariç **karakter** sayar. `6 12`: `sizeof` ise dizinin **bayt** boyutunu verir: dar dizgi 5 + 1 bayt, geniş dizgi Windows'ta (5 + 1) × 2 bayt. Linux'ta `wchar_t` 4 bayt olduğu için ikincisi 24 olurdu.
:::

::: gorev Başarıyı doğru denetle
`basarili_mi(fonksiyon, donus)` fonksiyonunu yaz: yukarıdaki tabloya göre, verilen Windows fonksiyonunun `donus` değeri **başarı** mı (`True`), başarısızlık mı (`False`) söylesin. `INVALID_HANDLE_VALUE`'yu −1 olarak düşün. Tabloda olmayan bir fonksiyon için `None` döndürsün.

Fonksiyonlar: `CreateFileW`, `FindFirstFileW`, `CreateEventW`, `LoadLibraryW`, `ReadFile`, `WriteFile`, `CloseHandle`, `GetFileSize`.

```starter
def basarili_mi(fonksiyon, donus):
    return donus != 0
```

```test
need("basarili_mi")
eq(basarili_mi("CreateFileW", -1), False, "CreateFileW başarısız: -1")
eq(basarili_mi("CreateFileW", 0x1A4), True, "geçerli tanıtıcı")
eq(basarili_mi("FindFirstFileW", -1), False, "FindFirstFileW de -1 döndürür")
eq(basarili_mi("CreateEventW", 0), False, "CreateEventW başarısız: NULL")
eq(basarili_mi("LoadLibraryW", 0x7FF80000), True, "geçerli modül tanıtıcısı")
eq(basarili_mi("ReadFile", 0), False, "BOOL: FALSE")
eq(basarili_mi("CloseHandle", 1), True, "BOOL: TRUE")
eq(basarili_mi("GetFileSize", 0xFFFFFFFF), False, "INVALID_FILE_SIZE")
eq(basarili_mi("GetFileSize", 0), True, "0 baytlık dosya geçerli bir sonuçtur")
eq(basarili_mi("BilinmeyenFonksiyon", 0), None, "tabloda yok")
```

```solution
INVALID_HANDLE_VALUE = -1
INVALID_FILE_SIZE = 0xFFFFFFFF
BASARISIZ = {
    "CreateFileW": INVALID_HANDLE_VALUE, "FindFirstFileW": INVALID_HANDLE_VALUE,
    "CreateEventW": 0, "LoadLibraryW": 0,
    "ReadFile": 0, "WriteFile": 0, "CloseHandle": 0,
    "GetFileSize": INVALID_FILE_SIZE,
}


def basarili_mi(fonksiyon, donus):
    if fonksiyon not in BASARISIZ:
        return None
    return donus != BASARISIZ[fonksiyon]
```

```hint
Her fonksiyonun **başarısızlık değerini** bir sözlükte tut: `CreateFileW` için −1, `CreateEventW` için 0, `GetFileSize` için 0xFFFFFFFF …
```
:::

::: gorev cch ve cb
`utf16_boyut(metin)` fonksiyonunu yaz: metnin UTF-16'da kaç **karakter birimi** (`cch`, sonlandırıcı hariç) tuttuğunu ve sonlandırıcıyla birlikte kaç **bayt** (`cb`) kapladığını `(cch, cb)` olarak döndürsün. Temel düzlemin dışındaki karakterler (ör. emoji) UTF-16'da **iki** birim (vekil çifti) kaplar.

```starter
def utf16_boyut(metin):
    return len(metin), len(metin) + 1
```

```test
need("utf16_boyut")
eq(utf16_boyut("Pafta"), (5, 12), "5 birim, (5 + 1) × 2 bayt")
eq(utf16_boyut("Şehir"), (5, 12), "Türkçe harfler de tek birim")
eq(utf16_boyut(""), (0, 2), "boş metin: yalnızca sonlandırıcı")
eq(utf16_boyut("a\U0001F600"), (3, 8), "emoji iki birim kaplar")
```

```solution
def utf16_boyut(metin):
    cch = len(metin.encode("utf-16-le")) // 2
    return cch, (cch + 1) * 2
```

```hint
Python'da `len(metin)` kod noktası sayar, UTF-16 birimi değil. `metin.encode("utf-16-le")` baytlarını al; her birim 2 bayttır.
```
:::
