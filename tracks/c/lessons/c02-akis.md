---
id: c02
title: Akış ve Fonksiyonlar
summary: if, for, while; switch ve break'siz düşme; i++ ile ++i; fonksiyonlar, değerle geçirme ve kapsam.
kazanim: CLA 2.7, CLA 3.1, CLA 3.2, CLA 3.3, CLA 3.4, CLA 3.5, CLA 3.6
---

::: anlat Akış denetimi
C'nin akış yapıları Python'dakilere benzer ama söz dizimi farklıdır: koşullar parantez içinde, bloklar süslü parantez içindedir; girinti yalnızca okunurluk içindir.

```c
for (int i = 0; i < 5; i++) {        // başlangıç; koşul; her turdan sonra
    if (i == 2) continue;            // bu turu atla
    if (i == 4) break;               // döngüden çık
    printf("%d ", i);                // 0 1 3
}

int n = 27, adim = 0;
while (n != 1) {                     // Collatz dizisi
    n = (n % 2 == 0) ? n / 2 : 3 * n + 1;   // koşul ? doğruysa : yanlışsa
    adim++;
}
printf("%d adım\n", adim);
```

### switch ve düşme
`switch` bir değeri `case` etiketleriyle karşılaştırır ve eşleşen etiketten itibaren **aşağı doğru** çalışmaya devam eder; `break` görene kadar. Buna düşme (fall-through) denir:

```c
switch (seviye) {
    case 1:  printf("kritik ");      // break yok: aşağı düşer
    case 2:  printf("hata ");
             break;
    case 3:  printf("uyarı ");
             break;
    default: printf("bilgi ");
}
```

`seviye` 1 ise "kritik hata ", 2 ise "hata ", 3 ise "uyarı ", başka bir değerse "bilgi " basılır.

> [!TUZAK]
> Unutulmuş bir `break`, C kodlarındaki klasik hatalardandır: kod okurken her `case`'in sonunda `break` olup olmadığına bak. Bilerek düşürülen yerlerde iyi kodda `// bilerek düşüyor` gibi bir not bulunur.

### i++ ve ++i
`i++` değeri **önce kullanır, sonra artırır**; `++i` önce artırır, sonra kullanır. Tek başına bir satırda fark yoktur; bir ifadenin içinde vardır:

```c
int i = 5;
int a = i++;      // a = 5, i = 6
int b = ++i;      // i = 7, b = 7
```

### Fonksiyonlar ve değerle geçirme
C'de argümanlar **kopyalanarak** geçer: fonksiyon içinde parametreyi değiştirmek çağıranın değişkenini değiştirmez (bunu yapmak için işaretçi gerekir, C04'te).

```c
int kare(int x) { x = x * x; return x; }
int s = 4;
int k = kare(s);     // k = 16, s hâlâ 4
```
:::

::: tahmin
`x` 2 iken çıktı nedir?

```c
int x = 2;
switch (x) {
    case 1: printf("bir\n");
    case 2: printf("iki\n");
    case 3: printf("üç\n");
    default: printf("diğer\n");
}
```

```gercek
iki
üç
diğer
```

???

`iki`, `üç`, `diğer`. Eşleşme `case 2`'de başlar ve hiçbir `case`'te `break` olmadığı için aşağıdaki bütün etiketlerin kodu da çalışır.
:::

::: gorev Düşen switch
Aşağıdaki C fonksiyonunun **basacağı kelimeleri** sırayla bir liste olarak döndüren `seviye_metni(seviye)` fonksiyonunu Python'da yaz.

```c
void seviye_metni(int seviye) {
    switch (seviye) {
        case 1:  printf("kritik ");
        case 2:  printf("hata ");
                 break;
        case 3:  printf("uyarı ");
                 break;
        default: printf("bilgi ");
    }
}
```

```starter
def seviye_metni(seviye):
    return {1: ["kritik"], 2: ["hata"], 3: ["uyarı"]}.get(seviye, ["bilgi"])
```

```test
need("seviye_metni")
eq(seviye_metni(1), ["kritik", "hata"], "1 → kritik, hata (düşme)")
eq(seviye_metni(2), ["hata"], "2 → hata")
eq(seviye_metni(3), ["uyarı"], "3 → uyarı")
eq(seviye_metni(9), ["bilgi"], "9 → bilgi")
```

```solution
def seviye_metni(seviye):
    if seviye == 1:
        return ["kritik", "hata"]
    if seviye == 2:
        return ["hata"]
    if seviye == 3:
        return ["uyarı"]
    return ["bilgi"]
```

```hint
`case 1`'in sonunda `break` yok: 1 geldiğinde `case 2`'nin kodu da çalışır.
```
:::

::: gorev Basamak toplamı
Aşağıdaki C fonksiyonunu Python'a `basamak_toplami(n)` olarak çevir. Negatif sayılarda da C ile **aynı** sonucu vermeli.

```c
int basamak_toplami(int n) {
    int toplam = 0;
    while (n != 0) {
        toplam += n % 10;
        n /= 10;
    }
    return toplam;
}
```

```starter
def basamak_toplami(n):
    toplam = 0
    while n != 0:
        toplam += n % 10
        n //= 10
    return toplam
```

```test
need("basamak_toplami")
eq(basamak_toplami(1234), 10, "1234 → 10")
eq(basamak_toplami(0), 0, "0 → 0")
eq(basamak_toplami(-123), -6, "-123 → -6 (C'de kalan da bölünenin işaretini alır)")
eq(basamak_toplami(-90), -9, "-90 → -9")
```

```solution
def basamak_toplami(n):
    toplam = 0
    while n != 0:
        kalan = n - int(n / 10) * 10      # C'deki %: işaret bölünenden
        toplam += kalan
        n = int(n / 10)                   # C'deki /: sıfıra doğru keser
    return toplam
```

```hint
Başlangıç kodu negatif sayıda sonsuza kadar döner: Python'da `-1 // 10` → `-1`, hiç 0'a ulaşmaz.
```

```hint
C'nin `/` ve `%` işleçlerini taklit et: `int(n / 10)` ve `n - int(n / 10) * 10`.
```

```meta
timeout: 5
```
:::
