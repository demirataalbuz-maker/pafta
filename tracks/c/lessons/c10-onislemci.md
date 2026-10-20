---
id: c10
title: Önişlemci ve Makrolar
summary: Derlemeden önce çalışan metin değiştirici; #define sabitleri, parametreli makrolar ve parantez tuzağı, argümanın iki kez değerlendirilmesi, #if / #ifdef ile platforma göre kod seçimi, include koruyucuları ve makro dolu kodu zihinde açmak.
---

::: anlat Derleyiciden önce: metin değiştirme
C kaynağı derlenmeden önce **önişlemciden** geçer. Önişlemci C bilmez; `#` ile başlayan satırlara göre **metni değiştirir**:

| Yönerge | Ne yapar |
|---|---|
| `#include <stdio.h>` | dosyanın içeriğini buraya yapıştırır |
| `#define MAKS 64` | her `MAKS` kelimesini `64` metniyle değiştirir |
| `#define KARE(x) ((x) * (x))` | parametreli makro: argüman metni yerine konur |
| `#if`, `#ifdef`, `#elif`, `#else`, `#endif` | koşula göre kod parçalarını tutar ya da siler |
| `#error "mesaj"` | derlemeyi durdurur |

### Parantez tuzağı
Makro bir fonksiyon değildir; argümanı **hesaplamadan**, metin olarak yerleştirir:

```c
#define KARE(x) x * x
KARE(1 + 2)          // önişlemciden sonra: 1 + 2 * 1 + 2  → 5, 9 değil!

#define KARE2(x) ((x) * (x))
KARE2(1 + 2)         // ((1 + 2) * (1 + 2))  → 9
```

Bu yüzden iyi yazılmış makrolarda **her** parametre ve **bütün** gövde parantez içindedir.

### İki kez değerlendirme
Bir argüman makro gövdesinde iki kez geçiyorsa, iki kez çalışır:

```c
#define MAKS(a, b) ((a) > (b) ? (a) : (b))
int i = 5, j = 3;
int m = MAKS(i++, j);    // ((i++) > (j) ? (i++) : (j))  → i iki kez artar
```

Yan etkili (`++`, fonksiyon çağrısı) argümanları makrolara verme; okurken de bu durumu yakala.
:::

::: anlat Platforma göre kod
Aynı kaynak birden çok işletim sisteminde derlenir; farklı olan kısımlar koşullu derlemeyle ayrılır. Derleyici bazı adları kendiliğinden tanımlar: `_WIN32` (Windows), `__linux__`, `__APPLE__`, `__x86_64__`, `_M_X64` …

```c
#if defined(_WIN32)
    const char *ayrac = "\\";
#elif defined(__linux__) || defined(__APPLE__)
    const char *ayrac = "/";
#else
    #error "bilinmeyen platform"
#endif
```

Bir başlık dosyasının iki kez eklenmesini önleyen **include koruyucusu** da aynı mekanizmadır:

```c
#ifndef PAFTA_H
#define PAFTA_H
/* ... bildirimler ... */
#endif
```

> [!İPUCU]
> Makrolarla dolu bir kodu anlamakta zorlanırsan önişlemcinin çıktısına bak: `gcc -E dosya.c` (MSVC'de `cl /E`) bütün makroları açılmış hâliyle gösterir. İkili kod incelerken ise makro yoktur: derleyici onları çoktan açmış, sabitler sayıya dönüşmüştür. `#define BUF_BOYUTU 512` kaynakta bir addır, derlenmiş kodda yalnızca `0x200`'dür.
:::

::: tahmin
Çıktı:

```c
#define KARE(x) x * x
#define KARE2(x) ((x) * (x))
#define TOPLA(a, b) a + b

printf("%d %d\n", KARE(1 + 2), KARE2(1 + 2));
printf("%d\n", 2 * TOPLA(3, 4));
```

```gercek
5 9
10
```

???

`5 9`: `KARE(1 + 2)` metni `1 + 2 * 1 + 2` olur; çarpma önce yapıldığı için 1 + 2 + 2 = 5. `KARE2` parantezli olduğu için 9. `10`: `2 * TOPLA(3, 4)` metni `2 * 3 + 4` olur, 14 değil 10. `TOPLA`'nın gövdesi `((a) + (b))` yazılmalıydı.
:::

::: gorev Makroyu aç
Önişlemcinin parametreli bir makroyu nasıl açtığını taklit eden `ac(govde, parametreler, argumanlar)` fonksiyonunu yaz: gövdedeki her parametre **adını** (yalnızca bütün kelime olarak) karşılık gelen argüman metniyle değiştirsin ve sonuç metni döndürsün.

```starter
def ac(govde, parametreler, argumanlar):
    for p, a in zip(parametreler, argumanlar):
        govde = govde.replace(p, a)
    return govde
```

```test
need("ac")
eq(ac("x * x", ["x"], ["1 + 2"]), "1 + 2 * 1 + 2", "KARE(1 + 2)")
eq(eval(ac("x * x", ["x"], ["1 + 2"])), 5, "açılmış metnin değeri 5")
eq(ac("((x) * (x))", ["x"], ["1 + 2"]), "((1 + 2) * (1 + 2))", "parantezli KARE2")
eq(ac("a + b", ["a", "b"], ["3", "4"]), "3 + 4", "iki parametre")
eq(ac("max_x + x", ["x"], ["5"]), "max_x + 5", "başka bir adın içindeki x değişmez")
```

```solution
import re


def ac(govde, parametreler, argumanlar):
    eslesme = dict(zip(parametreler, argumanlar))
    return re.sub(r"\b[A-Za-z_]\w*\b", lambda m: eslesme.get(m.group(0), m.group(0)), govde)
```

```hint
Başlangıç kodu `max_x` içindeki `x`'i de değiştiriyor. Önişlemci **adları** (token) değiştirir, alt dizgileri değil.
```

```hint
Gövdedeki her adı bul (`\b[A-Za-z_]\w*\b`) ve parametreyse argümanla değiştir: `re.sub(desen, lambda m: ..., govde)`. Bütün parametreleri tek geçişte değiştirmek, bir argümanın içindeki adın yeniden değiştirilmesini de önler.
```
:::

::: gorev Hangi kol derlenir?
Yukarıdaki `#if defined(_WIN32) ... #elif ... #else #error` bloğunu taklit eden `ayrac(tanimlar)` fonksiyonunu yaz: `tanimlar`, derleyicinin tanımladığı adların bir kümesidir. Fonksiyon seçilen koldaki ayıracı döndürsün; hiçbir kol seçilmezse (derleme hatası) `None` döndürsün.

```starter
def ayrac(tanimlar):
    if "_WIN32" in tanimlar:
        return "\\"
    return "/"
```

```test
need("ayrac")
eq(ayrac({"_WIN32", "_M_X64"}), "\\", "Windows")
eq(ayrac({"__linux__", "__x86_64__"}), "/", "Linux")
eq(ayrac({"__APPLE__"}), "/", "macOS")
eq(ayrac({"_WIN32", "__linux__"}), "\\", "ilk doğru kol kazanır")
eq(ayrac(set()), None, "hiçbiri: #error")
eq(ayrac({"__FreeBSD__"}), None, "bilinmeyen platform")
```

```solution
def ayrac(tanimlar):
    if "_WIN32" in tanimlar:
        return "\\"
    if "__linux__" in tanimlar or "__APPLE__" in tanimlar:
        return "/"
    return None
```

```hint
`#elif` kolu yalnızca `__linux__` ya da `__APPLE__` tanımlıysa seçilir; ikisi de yoksa `#else` kolundaki `#error` derlemeyi durdurur.
```
:::
