---
id: c16
title: Yol Adı ile Açılmış Nesne Arasındaki Güven Sınırı
summary: Yol bir addır, tanıtıcı bir nesnedir: her çağrıda ad yeniden çözülür, bu yüzden "denetle sonra aç" arasında ad başka bir nesneye bakabilir; stat ile lstat farkı, sembolik bağın izlenmesi, O_NOFOLLOW'un yalnız son bileşeni kapsaması (ölçüldü), openat/dirfd ile pencereyi daraltmak ve kararı elindeki tanıtıcıdan (fstat) vermek.
kazanim: CLA 4.3
---

::: anlat Ad ile nesne aynı şey değildir
`"veri/rapor.txt"` bir **ad**'dır. Çekirdek bu adı her sistem çağrısında **yeniden** çözer: bileşen bileşen dizinlere bakar, sembolik bağları izler ve sonunda bir dosya nesnesine (inode) varır. İki çağrı arasında ad aynı kalırken vardığı nesne değişmiş olabilir.

Açılmış bir tanıtıcı ise adı değil **nesnenin kendisini** tutar. Dosya `open`'dan sonra yeniden adlandırılsa, taşınsa, hatta silinse bile elindeki tanıtıcı aynı nesneyi okumaya devam eder.

| Çağrı | Neye bakar |
|---|---|
| `stat(yol, &s)` | adı çözer, sembolik bağları **izler**: hedefi anlatır |
| `lstat(yol, &s)` | son bileşen bir bağsa **bağın kendisini** anlatır |
| `fstat(fd, &s)` | elindeki **nesneyi** anlatır; ad hiç kullanılmaz |

`st_ino` (inode numarası) ile `st_dev` birlikte bir nesneyi dosya sisteminde tekil olarak adlandırır; "bu iki yol aynı nesne mi?" sorusunu böyle sorarsın.

```c norun
struct stat a, b;
stat("link.txt", &a);     /* bağın hedefi: normal dosya */
lstat("link.txt", &b);    /* bağın kendisi: sembolik bağ */
/* a.st_ino != b.st_ino : iki ayrı nesne */
```
:::

::: anlat Denetle–aç aralığı ve O_NOFOLLOW'un sınırı
Bu kalıp yaygındır ve yanlıştır:

```c norun
struct stat s;
if (stat(yol, &s) == 0 && S_ISREG(s.st_mode)) {   /* 1. denetim: ADA bakıldı */
    int fd = open(yol, O_RDONLY);                  /* 2. açma: AD yeniden çözüldü */
    /* denetlenen nesne ile açılan nesne aynı olmak zorunda değil */
}
```

İki çağrı arasında geçen sürede, o ada yazabilen biri onu başka bir yere çevirebilir. Buna **denetim–kullanım aralığı** (TOCTOU: time-of-check to time-of-use) denir. Dikkat: aralık yalnız `stat` ile `open` arasındadır. `open` döndükten sonra adın ne olduğu önemsizdir, çünkü artık elinde nesne vardır.

Doğru sıra **önce aç, sonra elindekini doğrula**:

```c norun
int fd = open(yol, O_RDONLY | O_NOFOLLOW);
if (fd < 0) return -1;
struct stat s;
fstat(fd, &s);                     /* kararı ADA değil, ELDEKİ NESNEYE göre ver */
if (!S_ISREG(s.st_mode)) { close(fd); return -1; }
```

`O_NOFOLLOW` son bileşen bir sembolik bağsa açmayı reddeder ve `errno`'yu **`ELOOP`** yapar (Linux'ta **40**, "Too many levels of symbolic links").

> [!TUZAK] O_NOFOLLOW yalnız SON bileşeni kapsar
> Bu derste ölçüldü: `dlink` bir dizine bağ iken `open("dlink/hedef.txt", O_RDONLY | O_NOFOLLOW)` **başarıyla açılır**. Bayrak yol boyunca bağ izlemeyi kapatmaz; yalnız son bileşenin kendisinin bağ olmasına itiraz eder. Ara dizinler hâlâ izlenir, yani "yolun hiçbir yerinde bağ olmasın" demek istiyorsan bu bayrak yetmez.

Pencereyi daraltmanın yolu adı parça parça, elindeki dizin tanıtıcısına göre çözmektir: `openat(dirfd, "ad", ...)` adı `dirfd`'nin gösterdiği dizinde arar. Dizini bir kez açıp tanıtıcısını tutarsan, o dizin sonradan yeniden adlandırılsa bile çözüm aynı dizinde sürer.
:::

::: tahmin Bağ, stat ve O_NOFOLLOW
Klasörde `gercek.txt` normal bir dosya, `link.txt` ona giden bir sembolik bağ, `dlink` ise `alt` dizinine giden bir bağ; `alt/hedef.txt` vardır. Çıktı:

```c
struct stat s, l;
stat("link.txt", &s);
lstat("link.txt", &l);
printf("A %d %d\n", S_ISREG(s.st_mode), S_ISLNK(l.st_mode));

int fd = open("link.txt", O_RDONLY | O_NOFOLLOW);
printf("B %d %d\n", fd, errno);

int g = open("dlink/hedef.txt", O_RDONLY | O_NOFOLLOW);
printf("C %d\n", g >= 0);
```

```gercek
A 1 1
B -1 40
C 1
```

???

`A 1 1`, `B -1 40`, `C 1`.

`A`: aynı ada iki soru, iki yanıt. `stat` bağı izleyip hedefi gördü, hedef normal bir dosya (`1`); `lstat` bağın kendisine baktı, o da bir sembolik bağ (`1`). İkisi de doğru, ama **farklı nesneleri** anlatıyor.

`B`: son bileşen bir bağ olduğu için `O_NOFOLLOW` açmayı reddetti: `-1` ve `errno` **40** (`ELOOP`). Bu "çok fazla bağ seviyesi" mesajı yanıltıcıdır; burada seviye derinliği değil, bayrağın kuralı işlemiştir.

`C`: `1`, yani **açıldı**. Son bileşen `hedef.txt` normal bir dosyadır; `dlink` ara bileşeni bir bağ olmasına rağmen izlendi. `O_NOFOLLOW`'un kapsamı budur.
:::

::: gorev Son bileşen kuralı
`ac(bilesenler, nofollow, baglar)` yaz: bir yolu bileşen bileşen çözen `open` çağrısını modelle.

- `bilesenler`: yolun parçaları, ör. `["dlink", "hedef.txt"]`.
- `baglar`: sembolik bağ adlarını hedeflerine eşleyen sözlük; burada olmayan her ad normal bir dosya ya da dizindir.
- `nofollow`: `O_NOFOLLOW` verildi mi.

Çözüm soldan sağa yapılır; her bileşen bir bağsa hedefiyle değiştirilir. `nofollow` doğruysa ve **son** bileşen bir bağsa açma reddedilir: `"ELOOP"` döndür. Ara bileşenler `nofollow` olsa da izlenir. Dönüş, çözülmüş bileşenlerin `/` ile birleştirilmiş hâlidir.

Bağlar tek düzeylidir: bir bağın hedefi başka bir bağ değildir.

```starter
def ac(bilesenler, nofollow, baglar):
    if nofollow:
        return "ELOOP"
    return "/".join(baglar.get(b, b) for b in bilesenler)
```

```test
need("ac")
eq(ac(["link.txt"], False, {"link.txt": "gercek.txt"}), "gercek.txt", "bağ izlenir")
eq(ac(["link.txt"], True, {"link.txt": "gercek.txt"}), "ELOOP", "son bileşen bağ + nofollow: reddedilir")
eq(ac(["gercek.txt"], True, {"link.txt": "gercek.txt"}), "gercek.txt",
   "son bileşen bağ değilse nofollow bir şey değiştirmez")
eq(ac(["dlink", "hedef.txt"], True, {"dlink": "alt"}), "alt/hedef.txt",
   "ölçülen kural: ara bileşen bağ olsa da nofollow ile açılır")
eq(ac(["dlink", "hedef.txt"], False, {"dlink": "alt"}), "alt/hedef.txt", "nofollow'suz da aynı")
eq(ac(["dlink", "link.txt"], True, {"dlink": "alt", "link.txt": "gercek.txt"}), "ELOOP",
   "ara bileşen izlenir ama son bileşen bağsa yine reddedilir")
eq(ac(["a", "b", "c"], True, {}), "a/b/c", "hiç bağ yok")
eq(ac(["veri"], False, {}), "veri", "tek bileşen, bağ değil")
```

```solution
def ac(bilesenler, nofollow, baglar):
    if nofollow and bilesenler[-1] in baglar:
        return "ELOOP"
    return "/".join(baglar.get(b, b) for b in bilesenler)
```

```hint
Başlangıç kodu `nofollow`'u bütün yola uyguluyor. Bayrak yalnız `bilesenler[-1]` bir bağ olduğunda devreye girer; ara bileşenler her durumda çözülür.
```
:::

::: gorev Denetim–kullanım aralığı
`sonuc(olaylar)` yaz: bir programın bir yolu denetleyip sonra açmasını, araya dışarıdan bir değişiklik girebildiği zaman çizelgesiyle modelle. `olaylar` sırayla uygulanır:

- `("denetle", inode)`: program adı `stat`'lar ve o anda adın gösterdiği nesneyi (`inode`) görüp kararını buna göre verir.
- `("degistir", inode)`: dışarıdan biri adı başka bir nesneye yöneltir.
- `("ac",)`: program adı açar ve o anda adın gösterdiği nesnenin tanıtıcısını alır.

Dönüş `(denetlenen, acilan, guvenli)`: programın karar verdiği nesne, elinde kalan nesne ve ikisinin aynı olup olmadığı. Hiç `denetle` yoksa `denetlenen` `None`, hiç `ac` yoksa `acilan` `None` olur; ikisinden biri `None` ise `guvenli` `False`'tur. Birden çok `denetle` ya da `ac` varsa **sonuncusu** geçerlidir.

```starter
def sonuc(olaylar):
    denetlenen = acilan = None
    for olay in olaylar:
        if olay[0] == "denetle":
            denetlenen = olay[1]
        elif olay[0] == "ac":
            acilan = denetlenen
    return (denetlenen, acilan, True)
```

```test
need("sonuc")
eq(sonuc([("denetle", 10), ("ac",)]), (10, 10, True), "araya bir şey girmedi: açılan, denetlenendir")
eq(sonuc([("denetle", 10), ("degistir", 99), ("ac",)]), (10, 99, False),
   "denetim ile açma arasında ad başka nesneye yöneldi")
eq(sonuc([("denetle", 10), ("ac",), ("degistir", 99)]), (10, 10, True),
   "açtıktan sonraki değişiklik elindeki tanıtıcıyı etkilemez")
eq(sonuc([("degistir", 99), ("denetle", 99), ("ac",)]), (99, 99, True), "denetimden önceki değişiklik sorun değil")
eq(sonuc([("denetle", 10), ("degistir", 99), ("degistir", 10), ("ac",)]), (10, 10, True),
   "geri döndürülen değişiklik: açılan yine denetlenen nesne")
eq(sonuc([("ac",)]), (None, None, False), "hiç denetlenmeden açmak güvenli sayılmaz")
eq(sonuc([("denetle", 10)]), (10, None, False), "açılmadıysa elde nesne yok")
eq(sonuc([("denetle", 10), ("degistir", 99), ("denetle", 99), ("ac",)]), (99, 99, True),
   "son denetim geçerlidir")
eq(sonuc([]), (None, None, False), "boş zaman çizelgesi")
```

```solution
def sonuc(olaylar):
    simdiki = None
    denetlenen = acilan = None
    for olay in olaylar:
        if olay[0] == "denetle":
            denetlenen = simdiki = olay[1]
        elif olay[0] == "degistir":
            simdiki = olay[1]
        elif olay[0] == "ac":
            acilan = simdiki
    guvenli = denetlenen is not None and acilan is not None and denetlenen == acilan
    return (denetlenen, acilan, guvenli)
```

```hint
Adın o an gösterdiği nesneyi ayrı bir değişkende tut: `denetle` hem onu okur hem kararı kaydeder, `degistir` yalnız onu değiştirir, `ac` yalnız onu okur. Başlangıç kodu `ac` sırasında denetlenen değeri kopyalıyor; aradaki `degistir`'i hiç görmüyor.
```

```hint
`guvenli` üç koşulun hepsini ister: denetlenmiş olmalı, açılmış olmalı ve ikisi aynı nesne olmalı. Açılmadan güvenli denemez.
```
:::
