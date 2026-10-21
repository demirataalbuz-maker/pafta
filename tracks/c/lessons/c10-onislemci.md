---
id: c10
title: Önişlemci ve Makrolar
summary: Derlemeden önce çalışan metin değiştirici; #define sabitleri, parametreli makrolar ve parantez tuzağı, argümanın iki kez değerlendirilmesi, #if / #ifdef ile platforma göre kod seçimi, include koruyucuları, makro dolu kodu zihinde açmak; çok dosyalı programlar: bildirim ve tanım, extern, static'in iki anlamı ve bağlayıcı hataları.
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

::: anlat Birden çok dosya: bildirim, tanım, extern ve static
Gerçek C programları birçok `.c` dosyasından oluşur. Her `.c` dosyası, eklediği başlıklarla birlikte ayrı bir **çeviri birimidir**: derleyici her birini tek başına derleyip bir nesne dosyası (`.o`, `.obj`) üretir. Sonra **bağlayıcı** (linker) nesne dosyalarını birleştirir ve bir dosyada kullanılıp başka bir dosyada tanımlanan adları birbirine bağlar:

```text
gcc -c sayac.c        →  sayac.o
gcc -c main.c         →  main.o
gcc sayac.o main.o -o program
```

| | Ne | Örnek |
|---|---|---|
| **bildirim** | "böyle bir şey var, türü bu"; yer ayırmaz | `extern int toplam;`, `int say(void);` |
| **tanım** | asıl nesneyi ya da fonksiyonun gövdesini oluşturur; programda **bir kez** olur | `int toplam = 0;`, `int say(void) { ... }` |

Başlık dosyası (`.h`) **bildirimleri** taşır, tanımlar `.c` dosyasındadır. Bir başlığa `int toplam = 0;` gibi bir tanım yazılırsa onu ekleyen her `.c` dosyası kendi tanımını üretir ve bağlayıcı "çoklu tanım" hatası verir. Bildirilip hiçbir yerde tanımlanmayan bir ad ise "tanımsız başvuru" (undefined reference) hatasıdır; bu hata derleyiciden değil **bağlayıcıdan** gelir.

`static` anahtar kelimesinin iki ayrı anlamı vardır:

| Nerede | Anlamı |
|---|---|
| dosya düzeyinde (fonksiyonların dışında) | ad **yalnızca bu dosyada** görünür (iç bağlantı); başka dosyalar göremez, aynı adı kendileri de kullanabilir |
| bir fonksiyonun içinde | değişken çağrılar arasında **değerini korur**; programın başında bir kez ilk değer alır |

Başlık iki yoldan iki kez eklenirse içindeki bildirimler iki kez görünür; tür tanımları (`struct`, `typedef`) ise hata verir. Bunu önleyen, önceki bölümde gördüğün **include koruyucusudur** (`#ifndef SAYAC_H` / `#define SAYAC_H` / `#endif`). Birçok derleyici aynı işi gören `#pragma once`'ı da tanır, ama o standart değildir.

> [!GÜVENLİK]
> Başka dosyaların kullanmaması gereken yardımcı fonksiyonları ve değişkenleri `static` yapmak, bir modülün dış dünyaya açtığı yüzeyi küçültür: hangi adların dışarıdan çağrılabildiği başlıktan okunur. Büyük bir C kodunu incelerken de bir fonksiyonun `static` olup olmadığına bakarak "bu yalnızca bu dosyanın içinden mi çağrılıyor?" sorusunu hızla cevaplarsın.
:::

::: tahmin
Üç dosyalık bir program. Ne yazar?

```c
// sayac.h
#ifndef SAYAC_H
#define SAYAC_H
extern int toplam;
int say(void);
#endif

// sayac.c
#include "sayac.h"
int toplam = 0;
static int cagri = 0;
int say(void) {
    static int yerel = 10;
    cagri++;
    yerel++;
    toplam += yerel;
    return cagri;
}

// main.c
#include <stdio.h>
#include "sayac.h"
#include "sayac.h"
static int cagri = 100;
int main(void) {
    say();
    say();
    int n = say();
    printf("%d %d %d\n", n, toplam, cagri);
    return 0;
}
```

```gercek
3 36 100
```

???

`3 36 100`. `say()` üç kez çağrılır ve `sayac.c`'nin kendi `cagri`'sini 3'e çıkarır. Fonksiyonun içindeki `static int yerel` çağrılar arasında değerini korur: 11, 12 ve 13 olur ve `toplam`'a eklenir: 36. `main.c`'deki `static int cagri = 100` başka bir değişkendir: iki dosyanın `static` adları birbirini görmez, bu yüzden çakışmaz ve 100 kalır. `sayac.h` iki kez eklendi ama koruyucu sayesinde ikinci ekleme boş geçer.
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

::: gorev Bağlayıcı
`bagla(birimler)` fonksiyonu bir bağlayıcının iki temel hatasını bulsun. `birimler` bir sözlük: dosya adı → `{"tanim": [...], "static": [...], "kullan": [...]}` (anahtarlardan biri eksik olabilir):

- `tanim`: dosyanın tanımladığı, dışarıya açık adlar
- `static`: dosyanın `static` olarak tanımladığı adlar; yalnızca o dosyada görünür
- `kullan`: dosyanın kullandığı adlar

Dönüş, hata metinlerinin **tekrarsız ve alfabetik sıralı** listesi:

- `"çoklu tanım: AD (a.c, b.c)"`: dışarıya açık bir ad birden çok dosyada tanımlanmışsa (dosyalar alfabetik, virgül ve boşlukla)
- `"tanımsız başvuru: AD (dosya.c)"`: bir dosyanın kullandığı ad ne o dosyanın `tanim` ya da `static` listesinde, ne de herhangi bir dosyanın `tanim` listesindeyse

```starter
def bagla(birimler):
    return []
```

```test
need("bagla")
libc = {"tanim": ["printf"]}
eq(bagla({"main.c": {"kullan": ["say", "toplam", "printf"]}, "sayac.c": {"tanim": ["say", "toplam"], "static": ["cagri"]}, "libc": libc}),
   [], "sağlam program")
eq(bagla({"a.c": {"tanim": ["toplam", "say"]}, "b.c": {"tanim": ["toplam"], "kullan": ["say"]}}),
   ["çoklu tanım: toplam (a.c, b.c)"], "başlığa yazılmış tanım: iki dosyada toplam")
eq(bagla({"c.c": {"tanim": ["x"]}, "a.c": {"tanim": ["x"]}, "b.c": {"tanim": ["x"]}}),
   ["çoklu tanım: x (a.c, b.c, c.c)"], "üç dosya, alfabetik")
eq(bagla({"a.c": {"static": ["cagri"]}, "b.c": {"static": ["cagri"], "kullan": ["cagri"]}}), [], "iki dosyanın static adları çakışmaz")
eq(bagla({"a.c": {"static": ["yardimci"]}, "b.c": {"kullan": ["yardimci", "yardimci"]}}),
   ["tanımsız başvuru: yardimci (b.c)"], "başka dosyanın static adı görünmez; aynı hata bir kez")
eq(bagla({"a.c": {"static": ["log"], "kullan": ["log"]}, "b.c": {"tanim": ["log"]}, "c.c": {"kullan": ["log"]}}),
   [], "static log ile açık log ayrı; c.c açık olanı bulur")
eq(bagla({"main.c": {"kullan": ["say", "yok"]}, "x.c": {"kullan": ["yok"]}}),
   ["tanımsız başvuru: say (main.c)", "tanımsız başvuru: yok (main.c)", "tanımsız başvuru: yok (x.c)"],
   "her dosya-ad çifti için bir hata, sıralı")
eq(bagla({}), [], "boş")
```

```solution
def bagla(birimler):
    hatalar = set()
    tanimlayan = {}
    for dosya, birim in birimler.items():
        for ad in birim.get("tanim", []):
            tanimlayan.setdefault(ad, []).append(dosya)
    for ad, dosyalar in tanimlayan.items():
        if len(dosyalar) > 1:
            hatalar.add(f"çoklu tanım: {ad} ({', '.join(sorted(dosyalar))})")
    for dosya, birim in birimler.items():
        yerel = set(birim.get("tanim", [])) | set(birim.get("static", []))
        for ad in birim.get("kullan", []):
            if ad not in yerel and ad not in tanimlayan:
                hatalar.add(f"tanımsız başvuru: {ad} ({dosya})")
    return sorted(hatalar)
```

```hint
Önce bütün dosyalardaki açık tanımları ad → dosyalar diye topla; birden çok dosyası olan ad çoklu tanımdır. Sonra her dosyanın kullandığı adı önce kendi tanımlarında ve static'lerinde, sonra açık tanımlarda ara.
```
:::

::: gorev Ön işlemci
`on_isle(dosyalar, ana)` fonksiyonu küçük bir ön işlemci gibi çalışsın. `dosyalar`: dosya adı → satır listesi. Kenar boşlukları atılınca şu yönergelerle başlayan satırlar yönergedir; geri kalan her satır bir kod satırıdır:

- `#include "ad"`: o dosyanın satırlarını (kendi yönergeleri de işlenerek) buraya koyar
- `#define M`: `M`'yi tanımlar; tanım bütün işlem boyunca geçerlidir
- `#ifndef M` … `#endif`: `M` tanımlıysa aradaki satırlar atlanır (atlanan bölgedeki yönergeler de); bu bloklar iç içe olabilir

Dönüş: `ana`'dan başlayarak ön işlemden geçen **kod satırları**, sırasıyla ve olduğu gibi.

```starter
def on_isle(dosyalar, ana):
    return [s for s in dosyalar[ana] if not s.startswith("#")]
```

```test
need("on_isle")
korumali = ["#ifndef SAYAC_H", "#define SAYAC_H", "extern int toplam;", "int say(void);", "#endif"]
ana = ['#include "sayac.h"', '#include "sayac.h"', "int main(void) {", "    return say();", "}"]
eq(on_isle({"sayac.h": korumali, "main.c": ana}, "main.c"),
   ["extern int toplam;", "int say(void);", "int main(void) {", "    return say();", "}"], "koruyucu: ikinci ekleme boş geçer")
eq(on_isle({"sayac.h": korumali[2:4], "main.c": ana}, "main.c"),
   ["extern int toplam;", "int say(void);", "extern int toplam;", "int say(void);", "int main(void) {", "    return say();", "}"],
   "koruyucusuz başlık iki kez gelir")
dongu = {"a.h": ["#ifndef A_H", "#define A_H", '#include "b.h"', "int a;", "#endif"],
         "b.h": ["#ifndef B_H", "#define B_H", '#include "a.h"', "int b;", "#endif"],
         "main.c": ['#include "a.h"', '#include "b.h"', "int m;"]}
eq(on_isle(dongu, "main.c"), ["int b;", "int a;", "int m;"], "birbirini ekleyen başlıklar sonsuza dek dönmez")
ic_ice = {"x.c": ["#define HATA_AYIKLA", "#ifndef SESSIZ", "satir1", "#ifndef HATA_AYIKLA", "satir2", "#endif", "satir3", "#endif", "satir4"]}
eq(on_isle(ic_ice, "x.c"), ["satir1", "satir3", "satir4"], "iç içe blok: içteki atlanır, dıştaki sürer")
atla = {"y.c": ["#ifndef YOK", "#ifndef VAR", "a", "#endif", "#endif", "#define VAR", "#ifndef VAR", '#include "z.h"', "b", "#endif", "c"],
        "z.h": ["z"]}
eq(on_isle(atla, "y.c"), ["a", "c"], "atlanan bölgedeki include işlenmez")
eq(on_isle({"w.c": ["  #define W", "#ifndef W", "w", "#endif", "  kod  "]}, "w.c"), ["  kod  "],
   "yönergenin önündeki boşluk atılır; kod satırı olduğu gibi kalır")
```

```solution
def on_isle(dosyalar, ana):
    tanimli = set()
    cikti = []

    def isle(ad):
        yigin = []
        for satir in dosyalar[ad]:
            s = satir.strip()
            etkin = all(yigin)
            if s.startswith("#ifndef "):
                yigin.append(etkin and s.split()[1] not in tanimli)
            elif s == "#endif":
                yigin.pop()
            elif not etkin:
                continue
            elif s.startswith("#define "):
                tanimli.add(s.split()[1])
            elif s.startswith("#include "):
                isle(s.split('"')[1])
            else:
                cikti.append(satir)

    isle(ana)
    return cikti
```

```hint
Açık `#ifndef` bloklarını bir yığında tut: her blok için "bu bölge etkin mi?" değerini sakla. Bir satır, yığındaki bütün değerler doğruysa (`all(yigin)`) işlenir; dış blok kapalıysa içteki de kapalıdır.
```

```hint
`#ifndef` ve `#endif` atlanan bölgede de sayılmalı (yığına girip çıkmalı), yoksa blokların sonu karışır. `#include` için kendini özyinelemeli çağır; tanımlar bütün dosyalar için ortak bir kümede durur.
```
:::
