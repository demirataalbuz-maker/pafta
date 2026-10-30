---
id: c15
title: POSIX Tanıtıcıları · Kısa Okuma, EOF ve Hata
summary: FILE * yerine çıplak dosya tanıtıcısı: read ve write'ın dönüşü "istenen" değil "gerçekleşen"dir; kısa okuma normaldir, 0 dosya sonudur, -1 hatadır ve nedeni errno'dadır; pipe bir bayt akışıdır, yazma sınırları korunmaz; okuyucusuz pipe'a yazmak EPIPE, kapalı tanıtıcıdan okumak EBADF verir; tam okuma ve tam yazma döngülerinin neden şart olduğu.
kazanim: CLA 4.3
---

::: anlat Tanıtıcı, akış değildir
`C11`'de dosyaları `FILE *` ile okudun: `fread`, `fgets` ve arkalarındaki tampon. Bir seviye altta **dosya tanıtıcısı** (file descriptor) vardır: çekirdeğin açık dosya tablosundaki girdiyi gösteren küçük bir tam sayı. `0` stdin, `1` stdout, `2` stderr'dir; `open`, `pipe` ve `socket` yenilerini üretir.

```c norun
#include <unistd.h>
ssize_t read(int fd, void *buf, size_t n);
ssize_t write(int fd, const void *buf, size_t n);
```

İkisinin de dönüşü `ssize_t`'tir ve anlamı şudur: **gerçekten aktarılan bayt sayısı**. "İstediğim kadarını aldım" varsayımı buradaki en yaygın hatadır.

| Dönüş | Anlamı |
|---|---|
| `n > 0` | `n` bayt aktarıldı — istenenden **az** olabilir |
| `0` (read) | dosya sonu: yazan uç kapandı ya da dosya bitti |
| `-1` | hata; nedeni `errno`'da |

Kısa okuma bir arıza değildir, normaldir: tamponun tamamı dolacak kadar veri henüz gelmemiştir. Bu derste ölçüldü (Kali, gcc 16.2.0): bir pipe'a 100 bayt yazıp 64 baytlık tamponla okunduğunda `read` sırayla **64**, **36** ve **0** döner.

> [!TUZAK] Pipe bir bayt akışıdır, mesaj akışı değil
> Yazma sınırları korunmaz. Ölçüldü: pipe'a ayrı ayrı `write(fd, "abc", 3)` ve `write(fd, "def", 3)` yapıp tek bir `read(fd, buf, 10)` çağırdığında dönüş **6**'dır — iki yazma tek okumada birleşti. Tersi de olur: tek bir yazma birkaç okumaya bölünebilir. Kendi mesaj sınırını istiyorsan uzunluk öneki ya da ayırıcı gibi bir çerçeveleme kuralını sen koyarsın.
:::

::: anlat Döngü ve hata akışı
Kısa aktarım normal olduğu için tek bir çağrıya güvenemezsin; **döngü** yazarsın. Okumada durma koşulları üçtür: istenen kadar biriktin, `0` geldi (dosya sonu), `-1` geldi (hata).

```c norun
size_t toplam = 0;
while (toplam < istenen) {
    ssize_t n = read(fd, buf + toplam, istenen - toplam);
    if (n == 0) break;                      /* dosya sonu: istenenden az aldık */
    if (n < 0) { if (errno == EINTR) continue; return -1; }   /* sinyal kesmişse yeniden dene */
    toplam += n;
}
```

Yazma tarafında `0` dönüşünün özel bir anlamı yoktur; orada da ilerlediğin kadarını sayıp kalanı yeniden yazarsın. `EINTR` bir hata değil, "bir sinyal çağrıyı böldü" demektir; iş yapılmadan dönülmüştür ve çağrı yinelenir.

Ölçülen iki hata (`errno` değerleri Linux'ta):

| Durum | Dönüş | `errno` | `strerror` |
|---|---|---|---|
| Okuyucu ucu kapalı pipe'a `write` | `-1` | **32** `EPIPE` | Broken pipe |
| Kapatılmış bir tanıtıcıdan `read` | `-1` | **9** `EBADF` | Bad file descriptor |

`EPIPE` bir ayrıntı daha taşır: varsayılan olarak çekirdek önce **SIGPIPE** gönderir ve program sessizce ölür. Yukarıdaki `-1`/`EPIPE` ancak sinyal yok sayıldığında (`signal(SIGPIPE, SIG_IGN)`) görülür. Bir sunucu yazarken bu yüzden SIGPIPE'ı yok sayıp `write`'ın dönüşünü denetlersin.

> [!TUZAK] `errno` yalnız hata dönüşünden sonra anlamlıdır
> Başarılı bir çağrı `errno`'yu sıfırlamaz; içinde eski bir değer durur. Önce dönüşe bak (`-1` mi?), ancak ondan sonra `errno`'yu oku. Araya giren her kütüphane çağrısı da `errno`'yu değiştirebilir, bu yüzden hemen oku ya da bir değişkene al.
:::

::: tahmin Pipe'ta kısa okuma ve dosya sonu
```c
int fd[2]; pipe(fd);
write(fd[1], "merhaba", 7);
char buf[64];
ssize_t n = read(fd[0], buf, sizeof buf);
printf("A %zd\n", n);
close(fd[1]);
printf("B %zd\n", read(fd[0], buf, sizeof buf));
printf("C %zd\n", read(fd[0], buf, sizeof buf));
```

```gercek
A 7
B 0
C 0
```

???

`A 7`, `B 0`, `C 0`.

`A`: tampon 64 bayt ama pipe'ta yalnız 7 bayt var; `read` **64 bekleyip** değil, eldeki 7 baytı verip hemen döner. İstenen ile dönen arasındaki bu fark kısa okumadır.

`B`: yazan uç `close` edildi ve pipe boş; artık veri gelme ihtimali yoktur, bu yüzden `read` **0** döndürür — dosya sonu. Dikkat: `fd[1]` kapanmasaydı `read` veri bekleyerek **bloke olurdu**; 0 dönüşü "şu an veri yok" değil, "bir daha gelmeyecek" demektir.

`C`: dosya sonu kalıcıdır. Sonraki okumalar da 0 döner; bu bir hata değildir, `errno` ayarlanmaz.
:::

::: gorev Okuma çağrılarının dönüşleri
`okumalar(toplam, tampon)` yaz: `toplam` baytlık bir kaynağı `tampon` baytlık bir tamponla sonuna kadar okuyan döngüde `read`'in sırayla döndüreceği değerleri liste olarak ver. Her çağrı kalan ile tampon boyutunun küçüğünü döndürür; son eleman dosya sonunu bildiren `0`'dır.

```starter
def okumalar(toplam, tampon):
    return [tampon] * (toplam // tampon) + [0]
```

```test
need("okumalar")
eq(okumalar(7, 64), [7, 0], "ölçülen durum: 7 bayt, 64'lük tampon")
eq(okumalar(100, 64), [64, 36, 0], "ölçülen durum: 100 bayt 64+36 olarak gelir")
eq(okumalar(128, 64), [64, 64, 0], "tam bölünen boyutta da sonda bir 0 okuması vardır")
eq(okumalar(0, 64), [0], "boş kaynak: ilk okuma dosya sonu")
eq(okumalar(1, 1), [1, 0], "en küçük tampon")
eq(okumalar(5, 1), [1, 1, 1, 1, 1, 0], "bir baytlık tampon beş çağrı artı dosya sonu")
```

```solution
def okumalar(toplam, tampon):
    sonuc, kalan = [], toplam
    while kalan > 0:
        n = min(tampon, kalan)
        sonuc.append(n)
        kalan -= n
    sonuc.append(0)
    return sonuc
```

```hint
Başlangıç kodu iki şeyi kaçırıyor: tam bölünmeyen son parçayı ve `toplam` 0 olduğunda bile yapılan bir okumayı. Döngüyü kalan bayt üzerinden kur, bittikten sonra listeye `0` ekle.
```
:::

::: gorev Tam okuma döngüsü
`tam_oku(donusler, istenen)` yaz: `read` çağrılarının sırayla `donusler` listesindeki değerleri döndürdüğünü varsay ve `istenen` baytı biriktirmeye çalışan döngüyü modelle. Dönüş `(toplam, durum)`:

- `"tam"`: `istenen` bayta ulaşıldı.
- `"eof"`: `0` geldi, dosya sonu; biriken `istenen`'den azdır.
- `"hata"`: `-1` geldi; o çağrıda bayt aktarılmaz, döngü biter.

Döngü `istenen` bayta ulaşınca durur; listede kalan dönüşler kullanılmaz. Gerçek döngü `read`'e her turda **kalan** kadarını istediği için dönüş kalanı aşamaz: listede kalandan büyük bir değer varsa yalnız kalan kadarı sayılır.

```starter
def tam_oku(donusler, istenen):
    return (sum(donusler), "tam")
```

```test
need("tam_oku")
eq(tam_oku([4, 4, 4], 12), (12, "tam"), "üç kısa okuma istenen toplamı verir")
eq(tam_oku([12], 12), (12, "tam"), "tek çağrıda tamamlanabilir")
eq(tam_oku([4, 0], 12), (4, "eof"), "dosya sonu: eksik veriyle biter")
eq(tam_oku([4, -1], 12), (4, "hata"), "hata: o çağrıda bayt eklenmez")
eq(tam_oku([-1], 12), (0, "hata"), "ilk çağrıda hata")
eq(tam_oku([0], 12), (0, "eof"), "hiç veri gelmeden dosya sonu")
eq(tam_oku([8, 8], 12), (12, "tam"), "istenene ulaşınca durur, fazlası alınmaz")
eq(tam_oku([4, 4, 4, 99], 12), (12, "tam"), "istenen dolunca kalan dönüşler kullanılmaz")
eq(tam_oku([], 0), (0, "tam"), "hiç bayt istenmezse döngüye girilmez")
```

```solution
def tam_oku(donusler, istenen):
    toplam, i = 0, 0
    while toplam < istenen:
        n = donusler[i]
        i += 1
        if n == 0:
            return (toplam, "eof")
        if n < 0:
            return (toplam, "hata")
        toplam += min(n, istenen - toplam)
    return (toplam, "tam")
```

```hint
Üç çıkış yolu var: biriken `istenen`'e ulaştı (`tam`), `0` geldi (`eof`), `-1` geldi (`hata`). Sırayı koru: önce `0` ve `-1` denetlenir, çünkü onlar bayt taşımaz; ancak ondan sonra `min(n, istenen - toplam)` kadarı eklenir.
```
:::
