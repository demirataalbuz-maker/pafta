---
id: c14
title: Heap Sahipliği, Alias ve realloc
summary: Bir heap bloğunun sahibi kimdir: malloc/free eşleşmesi, aynı bloğa bakan ikinci bir işaretçinin (alias) free'den sonra sarkması; realloc sözleşmesi — başarıda eski işaretçi geçersizdir, başarısızlıkta NULL döner ve eski blok dokunulmadan kalır, bu yüzden `p = realloc(p, n)` yazmak tek referansı kaybettirir; realloc(p, 0) ve malloc(0) kenar durumları; tanımsız davranışın tek bir çıktısı olmadığı ve ASan'ın ne yaptığı.
kazanim: CLA 2.3, CLA 2.6, CLA 2.7
---

::: anlat Sahiplik: bloğu kim bırakacak?
`malloc` bir blok verir, `free` onu geri alır. C bunu senin yerine izlemez: her blok için **tek bir sahip** belirlemek ve o sahibin tam bir kez `free` çağırması programın sözleşmesidir. Bu sözleşme kodda yazılı değildir; fonksiyon adlarında ve yorumlarda yaşar.

```c norun
char *kopyala(const char *s);   /* ÇAĞIRAN serbest bırakır */
void  yazdir(const char *s);    /* sahiplik değişmez, yalnız okur */
void  yut(char *s);             /* sahiplik BU fonksiyona geçer */
```

Bir bloğa bakan ikinci bir işaretçi **alias**'tır. Alias yeni bir blok değildir; aynı baytları gösterir:

```c norun
char *a = malloc(8);
char *b = a;        /* alias: tek blok, iki ad */
free(a);            /* blok gitti */
                    /* b artık SARKAN (dangling): değerini okumak bile tanımsız */
```

`free(a)` çağrısı `a`'yı `NULL` yapmaz; `a` da `b` de eski adresi taşımaya devam eder. Serbest bırakılmış bir bloğu okumak, yazmak ya da ikinci kez `free` etmek **tanımsız davranıştır**: çökme de olabilir, sessizce "çalışıyor" gibi görünmek de.

> [!TUZAK] Tanımsız davranışın tek bir doğru çıktısı yoktur
> Sarkan bir işaretçiden okuyan bir programın ne basacağını tahmin etmeye çalışma: derleyiciye, optimizasyon düzeyine ve çalıştırma anına göre değişir. Bu derste tahmin edilen bütün çıktılar **tanımlı** davranıştandır. Tanımsız olanı görmek için araç kullanılır: `gcc -fsanitize=address` ile derlenen program use-after-free ve double-free'yi yakalayıp raporlar. Rapor metni sürümle değişir; bu ders Kali'deki **gcc 16.2.0** ile ölçüldü.
:::

::: anlat realloc sözleşmesi
`realloc(p, n)` bloğu büyütür ya da küçültür. Döndürdüğü işaretçi `p` ile **aynı olmak zorunda değildir**: yerinde büyütemezse yeni bir blok ayırır, içeriği kopyalar ve eskisini kendisi `free` eder. Bu yüzden başarıdan sonra `p` geçersizdir; artık yalnız dönen değeri kullanırsın.

Asıl incelik başarısızlıkta:

| Durum | Dönüş | Eski blok |
|---|---|---|
| Başarı | yeni (ya da aynı) adres | `realloc` serbest bıraktı, `p` artık geçersiz |
| **Başarısızlık** | `NULL` | **dokunulmadı**, `p` hâlâ geçerli ve senin sorumluluğunda |

```c norun
char *yeni = realloc(p, n);
if (yeni == NULL) {
    /* p hâlâ geçerli: ya kullanmaya devam et ya da free(p) */
    return -1;
}
p = yeni;                       /* ancak başarıdan sonra ata */
```

> [!TUZAK] `p = realloc(p, n)` başarısızlıkta sızdırır
> Dönüşü doğrudan `p`'ye atarsan ve `realloc` başarısız olursa `p` `NULL` olur — ama eski blok **durmaktadır** ve ona bakan başka işaretçi kalmamıştır. Blok artık serbest bırakılamaz: sızıntı. Üstelik `free(p)` çağırsan bile `free(NULL)` hiçbir şey yapmaz, sızıntı kalır.

İki kenar durum (ölçüldü, glibc):

- `realloc(p, 0)` bu libc'de bloğu serbest bırakıp `NULL` döner. Bu davranış **uygulamaya bağlıdır** ve C23'te tanımsız sayılmıştır; "küçült" diye bunu kullanma.
- `malloc(0)` `NULL` **döndürmez**: serbest bırakılabilir, benzersiz bir işaretçi verir. Yani `NULL` dönüşünü "bellek bitti" diye okurken boyutun 0 olmadığından emin ol.
- `free(NULL)` güvenlidir ve hiçbir şey yapmaz.
:::

::: tahmin realloc başarısız olursa
`(size_t)-1` baytlık bir istek kesin başarısız olur. Çıktı:

```c
char *p = malloc(16);
strcpy(p, "veri");
char *q = realloc(p, (size_t)-1);
printf("A %d %s\n", q == NULL, p);

char *a = malloc(8);
strcpy(a, "abc");
a = realloc(a, (size_t)-1);
printf("B %d\n", a == NULL);

free(p);
free(NULL);
printf("C bitti\n");
```

```gercek
A 1 veri
B 1
C bitti
```

???

`A 1 veri`, `B 1`, `C bitti`.

`A` satırı sözleşmenin ikinci yarısını gösterir: `realloc` başarısız oldu (`q == NULL`, yani `1`), ama `p`'nin gösterdiği blok **dokunulmadı** — içindeki `"veri"` hâlâ orada ve `free(p)` ile düzgünce bırakılabiliyor. `B` satırı aynı başarısızlığın yanlış yazılmış hâlidir: dönüş doğrudan `a`'ya atandığı için `a` `NULL` oldu ve 8 baytlık bloğa bakan son işaretçi kayboldu; o blok programın sonuna kadar sızar. Dikkat: `B` satırı sızıntıyı **göstermez**, program hiçbir şey söylemeden devam eder. Sızıntıyı ancak bir araç (ASan, valgrind) ya da kodu okuyan sen fark edersin.
:::

::: gorev İki yazım, iki sonuç
`buyut(blok, basarili, guvenli)` yaz: bir `realloc` çağrısının ardından programın elinde ne kaldığını modelle. `blok` bir blok kimliğidir (tam sayı); başarılı bir `realloc` **yeni** bir blok verir ve onun kimliği `blok + 1`'dir.

Dönüş `(aktif, sizan)`:

- `aktif`: programın hâlâ kullanabildiği bloğun kimliği, hiçbiri kalmadıysa `None`.
- `sizan`: artık hiçbir işaretçinin göstermediği, serbest bırakılamayan bloğun kimliği; yoksa `None`.

`guvenli` yazım `yeni = realloc(blok, n); if (yeni) blok = yeni;`, güvensiz yazım `blok = realloc(blok, n);` demektir.

```starter
def buyut(blok, basarili, guvenli):
    return (blok + 1, None)
```

```test
need("buyut")
eq(buyut(1, True, True), (2, None), "güvenli + başarı: yeni blok aktif, eski blok realloc tarafından bırakıldı")
eq(buyut(1, False, True), (1, None), "güvenli + başarısızlık: eski blok hâlâ geçerli, sızıntı yok")
eq(buyut(1, True, False), (2, None), "güvensiz + başarı: fark yok, iki yazım da doğru çalışır")
eq(buyut(1, False, False), (None, 1), "güvensiz + başarısızlık: işaretçi NULL oldu, eski blok sızdı")
eq(buyut(7, False, False), (None, 7), "sızan blok, girilen bloğun kimliğidir")
eq(buyut(7, True, True), (8, None), "yeni kimlik blok + 1")
```

```solution
def buyut(blok, basarili, guvenli):
    if basarili:
        return (blok + 1, None)
    if guvenli:
        return (blok, None)
    return (None, blok)
```

```hint
Dört durumdan yalnız biri sızdırır: güvensiz yazım **ve** başarısız `realloc`. Başarı durumunda iki yazım da aynı sonucu verir; fark yalnız başarısızlıkta ortaya çıkar.
```
:::

::: gorev Sahiplik izleyicisi
`izle(islemler)` yaz: `malloc`/`free`/alias adımlarını sırayla uygulayıp `(sizan, hatalar)` döndür.

Her işlem bir demettir:

- `("al", ad)`: yeni bir blok ayırır ve `ad`'a bağlar.
- `("kopyala", yeni, eski)`: `yeni = eski;` — **aynı** bloğa ikinci bir ad (alias), yeni blok ayrılmaz.
- `("birak", ad)`: `free(ad)`.
- `("yaz", ad)`: bloğa yazar.

Dönüş:

- `sizan`: hiç serbest bırakılmamış blok sayısı.
- `hatalar`: oluştukları sırada, `"cift-birak:<ad>"` (zaten bırakılmış bir bloğu bırakmak) ve `"sarkan-yaz:<ad>"` (bırakılmış bir bloğa yazmak) dizgileri.

Hiç ayrılmamış bir ada yapılan `birak` ya da `yaz` işlemi yoktur; adlar kullanılmadan önce `al` ya da `kopyala` ile bağlanır.

```starter
def izle(islemler):
    sizan = 0
    for islem in islemler:
        if islem[0] == "al":
            sizan += 1
        elif islem[0] == "birak":
            sizan -= 1
    return (sizan, [])
```

```test
need("izle")
eq(izle([("al", "a"), ("birak", "a")]), (0, []), "düzgün eşleşme")
eq(izle([("al", "a")]), (1, []), "bırakılmayan blok sızar")
eq(izle([("al", "a"), ("al", "b"), ("birak", "a")]), (1, []), "iki bloktan biri sızar")
eq(izle([("al", "a"), ("kopyala", "b", "a"), ("birak", "a")]), (0, []),
   "alias yeni blok değildir: tek blok bir kez bırakıldı, sızıntı yok")
eq(izle([("al", "a"), ("kopyala", "b", "a")]), (1, []),
   "iki ad tek bloğu gösterir: sızıntı ada göre değil bloğa göre sayılır")
eq(izle([("al", "a"), ("kopyala", "b", "a"), ("birak", "a"), ("birak", "b")]), (0, ["cift-birak:b"]),
   "alias üzerinden ikinci free aynı bloğu hedefler")
eq(izle([("al", "a"), ("kopyala", "b", "a"), ("birak", "a"), ("yaz", "b")]), (0, ["sarkan-yaz:b"]),
   "free'den sonra alias sarkar")
eq(izle([("al", "a"), ("birak", "a"), ("yaz", "a"), ("birak", "a")]),
   (0, ["sarkan-yaz:a", "cift-birak:a"]), "hatalar oluştukları sırada")
eq(izle([("al", "a"), ("yaz", "a"), ("birak", "a")]), (0, []), "geçerli bloğa yazmak hata değil")
eq(izle([]), (0, []), "boş liste")
eq(izle([("al", "a"), ("kopyala", "b", "a"), ("al", "a"), ("birak", "a")]), (1, []),
   "ad yeniden bağlanınca eski blok yalnız b üzerinden erişilir ve bırakılmaz")
```

```solution
def izle(islemler):
    bloklar = {}          # blok kimliği -> bırakıldı mı
    adlar = {}            # ad -> blok kimliği
    hatalar = []
    for islem in islemler:
        if islem[0] == "al":
            kimlik = len(bloklar)
            bloklar[kimlik] = False
            adlar[islem[1]] = kimlik
        elif islem[0] == "kopyala":
            adlar[islem[1]] = adlar[islem[2]]
        elif islem[0] == "birak":
            kimlik = adlar[islem[1]]
            if bloklar[kimlik]:
                hatalar.append(f"cift-birak:{islem[1]}")
            else:
                bloklar[kimlik] = True
        elif islem[0] == "yaz":
            if bloklar[adlar[islem[1]]]:
                hatalar.append(f"sarkan-yaz:{islem[1]}")
    return (sum(1 for birakildi in bloklar.values() if not birakildi), hatalar)
```

```hint
Adları bloklardan ayır: bir sözlük `ad -> blok kimliği`, bir sözlük `blok kimliği -> bırakıldı mı`. `kopyala` yalnız ad sözlüğüne yeni bir giriş ekler, yeni blok üretmez.
```

```hint
Sızıntı sayısı, bırakılmamış **blok** sayısıdır; ada göre sayma. Aynı bloğa iki ad bağlıysa o blok bir kez sayılır ve bir kez bırakılması yeter.
```
:::
