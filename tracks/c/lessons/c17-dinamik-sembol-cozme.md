---
id: c17
title: Çalışma Zamanında Sembol Çözme
summary: Bir kütüphaneyi çalışırken adıyla yüklemek: dlopen tutamağı, dlsym ile fonksiyon ve veri sembollerini bulup işaretçiye dönüştürmek, RTLD_NOW ile RTLD_LAZY farkı, dlerror'un hatayı okuyunca temizlemesi ve dlsym'den önce temizlenmesi gerektiği; "./ad" bir yoldur ama çıplak "ad" arama sırasına bırakılır (ölçüldü: çalışma dizini aranmaz); Windows'taki LoadLibrary/GetProcAddress karşılığı.
kazanim: CLA 2.3, CLA 3.4
---

::: anlat Tutamak, sembol, işaretçi
`C10`'da bağlamayı derleme zamanında gördün: linker sembolleri çözer, program onlarla başlar. Bir kütüphaneyi **çalışırken** de yükleyebilirsin — eklenti mimarileri, isteğe bağlı bağımlılıklar ve sürüm farkını çalışma anında atlatan kod böyle yazılır.

```c norun
#include <dlfcn.h>
void *dlopen(const char *dosya, int bayrak);   /* yükle, tutamak döndür (hata: NULL) */
void *dlsym(void *tutamak, const char *ad);    /* sembolün ADRESİNİ bul */
char *dlerror(void);                            /* son hatayı ver ve TEMİZLE */
int   dlclose(void *tutamak);
```

`dlsym` bir `void *` verir: sembolün adresi. Fonksiyonsa onu bir fonksiyon işaretçisine çevirip çağırırsın, veriyse dolaylarsın.

```c norun
int (*topla)(int, int) = (int (*)(int, int)) dlsym(h, "topla");
int toplam = topla(2, 3);
int *sabit = (int *) dlsym(h, "sabit");   /* veri sembolü: adresi gelir, değeri *sabit */
```

`dlopen`'ın bayrağı sembollerin **ne zaman** çözüleceğini söyler:

| Bayrak | Anlamı |
|---|---|
| `RTLD_NOW` | yükleme sırasında çöz; sorun varsa hata erken çıkar |
| `RTLD_LAZY` | fonksiyon sembollerini ilk çağrıya ertele |
| `RTLD_GLOBAL` / `RTLD_LOCAL` | sembolleri sonra yüklenenlere açık mı tut |

Windows'ta aynı akışın karşılığı vardır; yalnız adlar ve hata yolu değişir:

| Linux | Windows | Hata nasıl anlaşılır |
|---|---|---|
| `dlopen` | `LoadLibraryW` | dönüş `NULL`, ayrıntı `GetLastError` |
| `dlsym` | `GetProcAddress` | dönüş `NULL`, ayrıntı `GetLastError` |
| `dlclose` | `FreeLibrary` | dönüş 0 ise hata |
| `dlerror` | — | Windows'ta ayrı bir "son dl hatası" yoktur |
:::

::: anlat Hata protokolü ve adın çözülmesi
`dlerror` sıradan bir "hata var mı" sorgusu değildir: **okuyunca temizler**. İki kuralı vardır.

1. `dlsym`'den **önce** `dlerror()` çağırıp eski hatayı temizle.
2. Sonucu `NULL` mı diye değil, `dlerror()` `NULL` dışında bir şey döndürdü mü diye yargıla.

```c norun
dlerror();                       /* eski hatayı at */
void *p = dlsym(h, ad);
char *hata = dlerror();
if (hata != NULL) { /* sembol yok */ }
```

Temizlemezsen önceki başarısız aramadan kalan mesajı okuyup **başarılı** bir aramayı hatalı sanırsın.

İkinci konu adın nasıl çözüldüğüdür. `dlopen`'a verdiğin dizgi içinde `/` varsa bu bir **yoldur**, doğrudan oradan yüklenir. İçinde `/` yoksa **arama sırasına** düşer: `DT_RUNPATH`, `LD_LIBRARY_PATH`, `ld.so` önbelleği ve sistem dizinleri. Bu derste ölçüldü: aynı dizindeki `libpafta.so` için `dlopen("./libpafta.so", ...)` **başarılı**, `dlopen("libpafta.so", ...)` **başarısızdır** — çalışma dizini arama sırasında yoktur.

> [!TUZAK] Çıplak ad, yükleneni seçme hakkını arama sırasına devreder
> Hangi dosyanın yükleneceğini artık sen değil, çalışma anındaki ortam belirler: `LD_LIBRARY_PATH` değişirse ya da arama sırasındaki bir dizine aynı adla bir dosya konursa program başka bir kütüphaneyle çalışır. Yüklediğin şeyin ne olduğunu sabitlemen gerekiyorsa mutlak yol ver. Windows tarafında da arama sırası belgelidir ve aynı soruyu doğurur; orada da tam yol vermek kesin olanıdır.

`dlopen` başarısız olduğunda `NULL` döner ve nedenini `dlerror()` anlatır (dosya yok, mimari uyuşmuyor, bir bağımlılık çözülemedi). Tutamağı `dlclose` ile bırakırsın; o tutamaktan alınmış **bütün işaretçiler** bundan sonra geçersizdir.
:::

::: tahmin Ad, sembol ve hata
`libpafta.so` çalışma dizinindedir ve içinde `int topla(int, int)` vardır. Çıktı:

```c
void *a = dlopen("./libpafta.so", RTLD_NOW);
void *b = dlopen("libpafta.so", RTLD_NOW);
printf("A %d %d\n", a != NULL, b != NULL);

int (*topla)(int, int) = (int (*)(int, int)) dlsym(a, "topla");
printf("B %d\n", topla(2, 3));

dlerror();
void *y = dlsym(a, "olmayan");
printf("C %d %d\n", y == NULL, dlerror() != NULL);
```

```gercek
A 1 0
B 5
C 1 1
```

???

`A 1 0`, `B 5`, `C 1 1`.

`A`: aynı dosya, iki ad, iki sonuç. `"./libpafta.so"` içinde `/` olduğu için **yoldur** ve yüklenir (`1`). `"libpafta.so"` çıplak bir addır; arama sırasına düşer ve o sırada çalışma dizini **bulunmadığı** için yükleme başarısız olur (`0`). "Dosya yanımda duruyor" yeterli değildir.

`B`: `dlsym` sembolün adresini verdi, fonksiyon işaretçisine çevrilip çağrıldı: `5`.

`C`: olmayan bir sembol için `dlsym` `NULL` döndürdü (`1`) ve `dlerror()` bir mesaj verdi (`1`). Çağrıdan önceki `dlerror()` önemlidir: eski bir hatayı temizler, böylece okunan mesajın bu aramaya ait olduğundan emin olursun.
:::

::: gorev Adı çözen arama
`yukle(ad, arama_yolu, mevcut)` yaz: `dlopen`'ın adı nasıl çözdüğünü modelle.

- `ad` içinde `/` varsa bu bir yoldur: `mevcut` kümesinde varsa aynen döndür, yoksa `None`.
- `ad` içinde `/` yoksa `arama_yolu`'ndaki dizinleri **sırayla** dene; ilk bulunan `"<dizin>/<ad>"` dizesini döndür. Hiçbirinde yoksa `None`.
- Çalışma dizini arama yoluna kendiliğinden eklenmez.

```starter
def yukle(ad, arama_yolu, mevcut):
    for dizin in arama_yolu:
        aday = dizin + "/" + ad
        if aday in mevcut:
            return aday
    return None
```

```test
need("yukle")
eq(yukle("./libp.so", ["/lib"], {"./libp.so"}), "./libp.so", "içinde / olan ad bir yoldur")
eq(yukle("libp.so", ["/lib", "/usr/lib"], {"./libp.so"}),
   None, "ölçülen durum: çıplak ad aranır, çalışma dizini arama yolunda değildir")
eq(yukle("libp.so", ["/lib", "/usr/lib"], {"/usr/lib/libp.so"}), "/usr/lib/libp.so", "arama yolunda bulundu")
eq(yukle("libp.so", ["/lib", "/usr/lib"], {"/lib/libp.so", "/usr/lib/libp.so"}),
   "/lib/libp.so", "iki dizinde de varsa sıradaki ilki kazanır")
eq(yukle("/opt/kesin/libp.so", [], {"/opt/kesin/libp.so"}), "/opt/kesin/libp.so", "mutlak yol arama yapmaz")
eq(yukle("/opt/kesin/libp.so", ["/lib"], {"/lib/libp.so"}), None, "yol verildiyse başka yere bakılmaz")
eq(yukle("libp.so", [], {"/lib/libp.so"}), None, "boş arama yolu")
eq(yukle("alt/libp.so", ["/lib"], {"alt/libp.so"}), "alt/libp.so", "göreli de olsa / varsa yoldur")
```

```solution
def yukle(ad, arama_yolu, mevcut):
    if "/" in ad:
        return ad if ad in mevcut else None
    for dizin in arama_yolu:
        aday = dizin + "/" + ad
        if aday in mevcut:
            return aday
    return None
```

```hint
Başlangıç kodu her adı aramaya sokuyor. Önce `"/" in ad` diye sor: yol ise arama hiç yapılmaz, yalnız o dosyaya bakılır.
```
:::

::: gorev dlerror protokolü
`aramalar(tablo, adlar)` yaz: bir tutamakta sırayla birkaç sembol aranmasını modelle. `tablo` sembol adlarını değerlerine eşler. Her arama için:

1. `dlerror()` çağrılıp varsa eski hata temizlenir.
2. `dlsym` yapılır: sembol `tablo`'da varsa değeri, yoksa `None`.
3. `dlerror()` yeniden okunur: yalnız **bu** arama başarısızsa bir hata vardır.

Dönüş, her arama için `(deger, hatali)` demetlerinden bir liste. Başarılı aramada `hatali` `False` olmalıdır — önceki başarısız aramadan kalan hata buna sızmamalıdır.

```starter
def aramalar(tablo, adlar):
    sonuc = []
    hata = False
    for ad in adlar:
        if ad in tablo:
            sonuc.append((tablo[ad], hata))
        else:
            hata = True
            sonuc.append((None, True))
    return sonuc
```

```test
need("aramalar")
eq(aramalar({"topla": 5}, ["topla"]), [(5, False)], "bulunan sembol")
eq(aramalar({"topla": 5}, ["yok"]), [(None, True)], "bulunmayan sembol hata verir")
eq(aramalar({"topla": 5}, ["topla", "yok", "topla"]), [(5, False), (None, True), (5, False)],
   "başarısız aramadan kalan hata sonraki başarılı aramaya sızmamalı")
eq(aramalar({"a": 1, "b": 2}, ["yok", "yok2", "a"]), [(None, True), (None, True), (1, False)],
   "üst üste iki hata, sonra başarı")
eq(aramalar({"sifir": 0}, ["sifir"]), [(0, False)],
   "değeri 0 olan sembol bulunmuştur: kararı değere değil hataya göre ver")
eq(aramalar({}, []), [], "hiç arama yok")
```

```solution
def aramalar(tablo, adlar):
    sonuc = []
    for ad in adlar:
        bulundu = ad in tablo
        sonuc.append((tablo[ad] if bulundu else None, not bulundu))
    return sonuc
```

```hint
Her tur kendi başına değerlendirilir: önceki turun hatasını taşıyan bir değişken tutma. `dlerror()`'u aramadan önce çağırmanın modeldeki karşılığı tam olarak budur.
```

```hint
Değeri `0` olan bir sembol de bulunmuş sayılır. "Değer yanlışsa hata vardır" diye yazarsan böyle sembollerde yanılırsın; ölçüt sembolün tabloda olup olmadığıdır.
```
:::
