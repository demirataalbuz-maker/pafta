---
id: c04
title: İşaretçiler ve Bellek
summary: Adres (&) ve içerik (*), işaretçi aritmetiği, dizi ile işaretçi ilişkisi, işaretçiyle değiştirme, malloc/free ve sınırlı kopyalama.
kazanim: CLA 2.3, CLA 2.4, CLA 2.5, CLA 2.6, CLA 3.6
---

::: anlat Adres ve içerik
Her değişken bellekte bir **adreste** durur. İşaretçi, bir adresi tutan değişkendir:

```c
int x = 5;
int *p = &x;        // &x: x'in adresi;  p bir int'i gösterir
printf("%d\n", *p); // *p: p'nin gösterdiği yerdeki değer → 5
*p = 9;             // gösterilen yeri değiştir
printf("%d\n", x);  // 9: x değişti
```

| Yazım | Anlamı |
|---|---|
| `int *p` | `p`, bir `int`'in adresini tutar |
| `&x` | `x`'in adresi |
| `*p` | `p`'nin gösterdiği değer |
| `p[i]` | `*(p + i)`: p'den i eleman ötedeki değer |
| `NULL` | hiçbir yeri göstermeyen işaretçi |

### Diziler ve işaretçi aritmetiği
Bir dizinin adı, ilk elemanının adresi gibi davranır. İşaretçiye 1 eklemek onu **bir eleman** (bir bayt değil) ilerletir:

```c
int d[] = {10, 20, 30, 40};
int *p = d;          // &d[0]
p++;                 // artık d[1]'i gösteriyor
printf("%d %d\n", *p, p[2]);   // 20 40
```

### İşaretçiyle değiştirmek
C'de argümanlar kopyalanarak geçtiği için, bir fonksiyonun çağıranın değişkenini değiştirmesi ancak **adresini** almasıyla olur:

```c
void degistir(int *a, int *b) {
    int gecici = *a;
    *a = *b;
    *b = gecici;
}
int x = 1, y = 2;
degistir(&x, &y);    // x = 2, y = 1
```

### Dinamik bellek
`malloc(n)` çalışma anında n baytlık bir alan ayırır ve adresini döndürür; iş bitince `free` ile geri verilir. Başarısız olursa `NULL` döner:

```c
int *dizi = malloc(100 * sizeof(int));
if (dizi == NULL) { return 1; }     // her zaman denetle
/* ... kullan ... */
free(dizi);
dizi = NULL;                        // serbest bırakılmış adresi bir daha kullanmamak için
```

> [!GÜVENLİK]
> İşaretçiyle çalışan kodda üç soru her zaman sorulur: Gösterdiği alan **ne kadar büyük**? Hâlâ **geçerli** mi (serbest bırakılmış olabilir mi)? **NULL** olabilir mi? Kopyalama işlevlerinden `strcpy` hedefin boyutunu bilmez; güvenli kod `snprintf(hedef, boyut, "%s", kaynak)` gibi boyutu alan işlevler kullanır ve sonucun her zaman `'\0'` ile bittiğini garanti eder.
:::

::: tahmin
Çıktı:

```c
int d[] = {10, 20, 30, 40};
int *p = d;
p += 2;
printf("%d %d %d\n", *p, p[1], *(p - 1));
int x = 5, *q = &x;
*q = 9;
printf("%d\n", x);
```

```gercek
30 40 20
9
```

???

`30 40 20`, sonra `9`. `p += 2` işaretçiyi iki eleman ilerletir: `*p` 30'dur, `p[1]` bir sonraki (40), `*(p - 1)` bir önceki (20). `q` x'in adresini tuttuğu için `*q = 9` doğrudan x'i değiştirir.
:::

::: gorev İşaretçiyle takas
Python'da işaretçi yoktur ama bir **liste** ve indeksler, "dizinin elemanlarının adresleri" gibi düşünülebilir. `degistir(dizi, i, j)` fonksiyonunu yaz: C'deki `degistir(&dizi[i], &dizi[j])` ile aynı etkiyi yapsın, yani listeyi **yerinde** değiştirsin ve hiçbir şey döndürmesin.

```c
void degistir(int *a, int *b) {
    int gecici = *a;
    *a = *b;
    *b = gecici;
}
```

```starter
def degistir(dizi, i, j):
    yeni = list(dizi)
    yeni[i], yeni[j] = yeni[j], yeni[i]
    return yeni
```

```test
need("degistir")
d = [10, 20, 30, 40]
sonuc = degistir(d, 0, 3)
eq(d, [40, 20, 30, 10], "liste yerinde değişmeli")
eq(sonuc, None, "C'deki void gibi hiçbir şey döndürmemeli")
d2 = [1, 2]
degistir(d2, 1, 1)
eq(d2, [1, 2], "aynı indeks: değişmez")
```

```solution
def degistir(dizi, i, j):
    gecici = dizi[i]
    dizi[i] = dizi[j]
    dizi[j] = gecici
```

```hint
Kopya oluşturma; gelen listenin kendisini değiştir. C'deki `*a = *b` burada `dizi[i] = dizi[j]`.
```
:::

::: gorev Sınırlı kopyalama
Aşağıdaki C fonksiyonu, `boyut` baytlık bir hedefe en fazla `boyut - 1` karakter kopyalar ve sonucu her zaman `'\0'` ile bitirir; kopyalanan karakter sayısını döndürür. Python'da `kopyala(boyut, kaynak)` olarak yaz: `(hedefteki metin, kopyalanan sayı)` çiftini döndürsün.

```c
size_t kopyala(char *hedef, size_t boyut, const char *kaynak) {
    if (boyut == 0) return 0;               // yazacak yer yok
    size_t i = 0;
    while (i < boyut - 1 && kaynak[i] != '\0') {
        hedef[i] = kaynak[i];
        i++;
    }
    hedef[i] = '\0';
    return i;
}
```

```starter
def kopyala(boyut, kaynak):
    return kaynak, len(kaynak)
```

```test
need("kopyala")
eq(kopyala(10, "web01"), ("web01", 5), "yer yeterli")
eq(kopyala(4, "web01"), ("web", 3), "boyut 4 → en fazla 3 karakter")
eq(kopyala(1, "web01"), ("", 0), "boyut 1 → yalnızca '\\0'")
eq(kopyala(0, "web01"), ("", 0), "boyut 0 → hiçbir şey yazılmaz")
eq(kopyala(6, "web01"), ("web01", 5), "tam sığıyor")
```

```solution
def kopyala(boyut, kaynak):
    if boyut == 0:
        return "", 0
    metin = kaynak[:boyut - 1]
    return metin, len(metin)
```

```hint
`boyut - 1` karakterlik yer var çünkü son bayt `'\0'` için ayrılıyor. Python'da `kaynak[:boyut - 1]`.
```

```hint
`boyut == 0` ayrı bir durum: C kodu hiçbir şey yazmadan 0 döndürür. Python'da `kaynak[:-1]` bunu taklit etmez, dikkat.
```
:::
