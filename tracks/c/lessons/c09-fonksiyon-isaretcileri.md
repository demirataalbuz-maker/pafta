---
id: c09
title: Fonksiyon İşaretçileri
summary: Fonksiyonun adresini tutan değişkenler, okunması zor bildirimler ve typedef, işlem kodlarıyla çalışan dağıtım tabloları, geri çağırma (callback) kalıbı ve qsort'un karşılaştırma fonksiyonu.
---

::: anlat Fonksiyonun adresi
C'de bir fonksiyonun da bir adresi vardır ve bu adres bir değişkende tutulabilir. Bildirimi ilk bakışta karışıktır; içten dışa okunur:

```c
int topla(int a, int b) { return a + b; }

int (*islem)(int, int);    // islem: iki int alıp int döndüren bir fonksiyonun İŞARETÇİSİ
islem = topla;             // fonksiyonun adı, adresi gibi davranır (&topla da olur)
int s = islem(2, 3);       // işaretçi üzerinden çağrı: 5
```

| Bildirim | Okunuşu |
|---|---|
| `int f(int)` | `f`, int alıp int döndüren bir fonksiyon |
| `int (*p)(int)` | `p`, öyle bir fonksiyonun işaretçisi |
| `int *p(int)` | dikkat: `p`, int alıp **int işaretçisi döndüren** bir fonksiyon |
| `int (*t[3])(int)` | `t`, öyle üç fonksiyon işaretçisinden oluşan bir dizi |

Okunurluk için genellikle `typedef` yazılır:

```c
typedef int (*Islem)(int, int);
Islem islemler[3] = { topla, carp, fark };
```

### Dağıtım tabloları
Bir **işlem kodunu** (opcode) bir fonksiyona eşleyen dizi, uzun bir `switch`'in yerini alır. Yorumlayıcılarda, sanal makinelerde, protokol işleyicilerinde ve komut alan her programda bu kalıbı görürsün:

```c
int topla(int a, int b) { return a + b; }
int carp(int a, int b)  { return a * b; }
int fark(int a, int b)  { return a - b; }

int (*tablo[3])(int, int) = { topla, carp, fark };

int calistir(const int *kodlar, size_t n, int baslangic) {
    int deger = baslangic;
    for (size_t i = 0; i < n; i++) {
        if (kodlar[i] < 0 || kodlar[i] >= 3) return -1;   // tablonun dışı: reddet
        deger = tablo[kodlar[i]](deger, 3);
    }
    return deger;
}
```

> [!GÜVENLİK]
> Tablo indeksi dışarıdan (bir dosyadan, bir ağ paketinden) geliyorsa sınır denetimi şarttır. Denetimsiz `tablo[kod]()` çağrısı, tablonun dışındaki rastgele bir belleği **fonksiyon adresi** sanıp oraya atlar. İkili kod incelerken "bir dizi adres ve ona indeksle yapılan dolaylı çağrı" gördüğünde bunun bir dağıtım tablosu olduğunu ve indeksin nereden geldiğini sorgula.
:::

::: anlat Geri çağırma ve qsort
Bir fonksiyona **başka bir fonksiyonu** argüman olarak vermeye geri çağırma (callback) denir. Standart kütüphanenin `qsort`'u bunun en bilinen örneğidir: neye göre sıralayacağını sen bir karşılaştırma fonksiyonuyla söylersin:

```c
typedef struct { char ad[16]; int cpu; } Sunucu;

int karsilastir(const void *a, const void *b) {
    const Sunucu *x = a, *y = b;
    if (x->cpu != y->cpu) return y->cpu - x->cpu;   // CPU'ya göre azalan
    return strcmp(x->ad, y->ad);                    // eşitlikte ada göre artan
}

qsort(liste, adet, sizeof(Sunucu), karsilastir);
```

Karşılaştırma fonksiyonu negatif dönerse `a` önce, pozitif dönerse `b` önce, sıfırsa eşit sayılır. `void *` "herhangi bir türün adresi" demektir; fonksiyon onu doğru türe çevirip kullanır.
:::

::: tahmin
Çıktı:

```c
int topla(int a, int b) { return a + b; }
int carp(int a, int b)  { return a * b; }
int fark(int a, int b)  { return a - b; }

int (*islem[3])(int, int) = { topla, carp, fark };
int kodlar[] = { 1, 0, 2, 1 };
int deger = 2;
for (int i = 0; i < 4; i++) {
    deger = islem[kodlar[i]](deger, 3);
    printf("%d\n", deger);
}
```

```gercek
6
9
6
18
```

???

`6`, `9`, `6`, `18`. Kod 1 `carp`'tır: 2 × 3 = 6. Kod 0 `topla`: 6 + 3 = 9. Kod 2 `fark`: 9 − 3 = 6. Yine kod 1: 6 × 3 = 18.
:::

::: gorev Dağıtım tablosu
Yukarıdaki `calistir` fonksiyonunun Python karşılığını yaz: `calistir(kodlar, baslangic)` her kod için tablodaki işlemi `(deger, 3)` ile uygulasın; tablonun dışında bir kod gelirse hemen `-1` döndürsün.

```starter
def calistir(kodlar, baslangic):
    deger = baslangic
    for kod in kodlar:
        if kod == 0:
            deger = deger + 3
        elif kod == 1:
            deger = deger * 3
    return deger
```

```test
need("calistir")
eq(calistir([1, 0, 2, 1], 2), 18, "tahmindeki program")
eq(calistir([], 7), 7, "boş program")
eq(calistir([2, 2, 2], 10), 1, "üç kez çıkarma")
eq(calistir([0, 3, 0], 1), -1, "tablonun dışı: 3")
eq(calistir([0, -1], 1), -1, "negatif kod da reddedilir")
```

```solution
def topla(a, b):
    return a + b


def carp(a, b):
    return a * b


def fark(a, b):
    return a - b


TABLO = [topla, carp, fark]


def calistir(kodlar, baslangic):
    deger = baslangic
    for kod in kodlar:
        if kod < 0 or kod >= len(TABLO):
            return -1
        deger = TABLO[kod](deger, 3)
    return deger
```

```hint
Python'da fonksiyonlar da değerdir: `TABLO = [topla, carp, fark]` ve `TABLO[kod](deger, 3)`.
```

```hint
Python'da `TABLO[-1]` son elemanı verir, hata vermez. C'deki sınır denetimini açıkça yaz: `kod < 0 or kod >= len(TABLO)`.
```
:::

::: gorev qsort'un sırası
`(ad, cpu)` çiftlerinden oluşan bir listeyi, yukarıdaki `karsilastir` fonksiyonuyla `qsort`'un vereceği sırayla döndüren `sirala(sunucular)` fonksiyonunu yaz.

```starter
def sirala(sunucular):
    return sorted(sunucular)
```

```test
need("sirala")
liste = [("web02", 65), ("db01", 91), ("web01", 72), ("cache01", 72), ("test01", 3)]
eq(sirala(liste), [("db01", 91), ("cache01", 72), ("web01", 72), ("web02", 65), ("test01", 3)],
   "CPU'ya göre azalan, eşitlikte ada göre")
eq(sirala([]), [], "boş liste")
```

```solution
def sirala(sunucular):
    return sorted(sunucular, key=lambda s: (-s[1], s[0]))
```

```hint
Karşılaştırma önce CPU'ya (büyük önce), sonra ada (küçük önce) bakıyor. Python'da bunu bir anahtarla söyle: `key=lambda s: (-s[1], s[0])`.
```
:::
