---
id: c01
title: Bir C Programını Okumak
summary: main ve #include, türler, printf biçim belirteçleri, tam sayı bölmesinin sıfıra doğru kesmesi ve karakterlerin aslında sayı olması.
kazanim: CLA 1.1, CLA 1.4, CLA 2.1, CLA 4.4
---

::: anlat C programının iskeleti
Bu yolda C kodunu **okuyacak**, ne yaptığını tahmin edecek ve görevlerde aynı davranışı Python'da kuracaksın. Önce bir programın iskeleti:

```c
#include <stdio.h>              // printf'in bildirimi bu başlık dosyasında

int main(void) {                // program buradan başlar
    int sayac = 3;              // tam sayı
    double oran = 0.75;         // ondalıklı sayı
    char harf = 'K';            // tek karakter (aslında küçük bir sayı)
    const char *ad = "web01";   // metin: karakter dizisinin adresi

    printf("%s: %d kayıt, oran %.2f, harf %c\n", ad, sayac, oran, harf);
    return 0;                   // 0 = başarı
}
```

Her değişkenin bir **türü** vardır ve tür değişmez. `printf` ilk argümandaki biçim metnini yazar; `%` ile başlayan belirteçlerin yerine sıradaki argümanları koyar:

| Belirteç | Ne basar | Örnek |
|---|---|---|
| `%d` | tam sayı | `42` |
| `%5d`, `%-5d` | 5 haneye sağa / sola yaslı | `   42`, `42   ` |
| `%f`, `%.2f` | ondalıklı (varsayılan 6 hane) / 2 hane | `3.500000`, `3.50` |
| `%s` | metin | `web01` |
| `%c` | karakter | `K` |
| `%x`, `%08x` | onaltılık / 8 haneye sıfırla dolu | `ff`, `000000ff` |
| `%%` | yüzde işareti | `%` |

### Tam sayı aritmetiği
İki tam sayının bölümü tam sayıdır ve küsurat **sıfıra doğru** atılır. `%` kalanı verir ve işaretini bölünenden alır:

```c
printf("%d %d\n", 7 / 2, 7 % 2);      // 3 1
printf("%d %d\n", -7 / 2, -7 % 2);    // -3 -1
printf("%f\n", 7 / 2);                // YANLIŞ: tam sayıyı %f ile basmak tanımsız davranış
printf("%.1f\n", 7 / 2.0);            // 3.5
```

> [!TUZAK]
> Python'da `-7 // 2` sonucu `-4`'tür (aşağı yuvarlar), C'de `-7 / 2` sonucu `-3`'tür (sıfıra doğru keser). C kodunu Python'a çevirirken negatif sayılarda bu fark sessizce yanlış sonuç üretir. Python'da C davranışı için `int(a / b)` ya da `math.trunc(a / b)`.

### Karakterler sayıdır
`char` küçük bir tam sayıdır; `'A'` 65 demektir. Bu yüzden karakterlerle aritmetik yapılabilir: `'A' + 2` → `'C'`, `'7' - '0'` → `7`.
:::

::: tahmin
Programın çıktısı:

```c
#include <stdio.h>

int main(void) {
    int a = 7, b = 2;
    printf("%d %d\n", a / b, a % b);
    printf("%.2f\n", (double)a / b);
    printf("%c%c\n", 'A' + 2, 'a' + 1);
    printf("%x\n", 255);
    return 0;
}
```

```gercek
3 1
3.50
Cb
ff
```

???

`3 1`, `3.50`, `Cb`, `ff`. Tam sayı bölmesi 3, kalan 1. `(double)a` önce a'yı ondalığa çevirir, bölme ondalıklı yapılır ve iki haneyle basılır. `'A' + 2` C, `'a' + 1` b karakteridir. 255 onaltılık tabanda `ff`'dir.
:::

::: gorev C gibi ortalama
Aşağıdaki C fonksiyonunun **birebir** aynısını Python'da `ortalama(a, b, c)` adıyla yaz. Negatif sayılarda da C ile aynı sonucu vermeli.

```c
int ortalama(int a, int b, int c) {
    return (a + b + c) / 3;
}
```

```starter
def ortalama(a, b, c):
    return (a + b + c) // 3
```

```test
need("ortalama")
eq(ortalama(1, 2, 4), 2, "ortalama(1, 2, 4)")
eq(ortalama(10, 10, 11), 10, "ortalama(10, 10, 11)")
eq(ortalama(-7, 0, 0), -2, "ortalama(-7, 0, 0): C sıfıra doğru keser → -2")
eq(ortalama(-1, -1, -2), -1, "ortalama(-1, -1, -2) → -1")
```

```solution
def ortalama(a, b, c):
    return int((a + b + c) / 3)
```

```hint
Python'un `//` işleci aşağı yuvarlar: `-7 // 3` → `-3`. C ise sıfıra doğru keser: `-7 / 3` → `-2`.
```

```hint
`int(x / 3)` ya da `math.trunc(x / 3)` sıfıra doğru keser.
```
:::

::: gorev printf biçimi
Aşağıdaki C satırının ürettiği metni (sondaki satır sonu hariç) döndüren `bicimle(ad, deger)` fonksiyonunu Python'da yaz.

```c
printf("%-8s|%6.1f|%04d\n", ad, deger, (int)deger);
```

```starter
def bicimle(ad, deger):
    return f"{ad}|{deger}|{int(deger)}"
```

```test
need("bicimle")
eq(bicimle("web01", 72.46), "web01   |  72.5|0072", "web01, 72.46")
eq(bicimle("db", 5.0), "db      |   5.0|0005", "db, 5.0")
eq(bicimle("yedek0123", 123.25), "yedek0123| 123.2|0123", "8'den uzun ad kesilmez")
```

```solution
def bicimle(ad, deger):
    return f"{ad:<8}|{deger:6.1f}|{int(deger):04d}"
```

```hint
`%-8s` → `{ad:<8}`, `%6.1f` → `{deger:6.1f}`, `%04d` → `{x:04d}`.
```

```hint
`(int)deger` C'de sıfıra doğru keser; pozitif sayılarda Python'daki `int()` aynı işi yapar.
```
:::
