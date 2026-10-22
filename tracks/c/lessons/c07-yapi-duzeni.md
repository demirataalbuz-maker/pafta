---
id: c07
title: Yapıların Bellek Düzeni
summary: struct alanlarının hizalanması ve dolgu baytları, sizeof ve offsetof, alan sırasının boyutu değiştirmesi, dosya biçimleri için #pragma pack, yapı dizileri ve ok işleci, union ile aynı belleği farklı türde okumak.
kazanim: CLA 1.2, CLA 2.6
---

::: anlat Hizalama ve dolgu
Bir yapının boyutu, alanlarının boyutlarının toplamı **olmayabilir**. İşlemciler bir `int`'i 4'ün katı olan bir adresten, bir `int64_t`'yi 8'in katından daha hızlı (bazı mimarilerde zorunlu olarak) okur. Bu yüzden derleyici alanların arasına **dolgu** (padding) baytları koyar:

```c
struct A { char c; int i; };            // c: ofset 0, 3 bayt dolgu, i: ofset 4  → sizeof 8
struct B { char c; int i; char d; };    // c 0, i 4, d 8, sonra 3 bayt dolgu      → sizeof 12
struct C { int i; char c; char d; };    // i 0, c 4, d 5, sonra 2 bayt dolgu      → sizeof 8
```

Kurallar (x86-64 ve ARM64'teki yaygın ABI'ler için):

1. Her alan, kendi boyutunun katı olan bir ofsete yerleşir: `char` 1, `short` 2, `int` 4, `int64_t` ve işaretçi 8.
2. Yapının toplam boyutu, en büyük hizalamaya sahip alanın katına **yuvarlanır**; böylece yapı dizisindeki her eleman da hizalı kalır.

`B` ile `C` aynı alanları taşır ama `C`, alanlar büyükten küçüğe sıralandığı için 4 bayt daha küçüktür. Milyonlarca kaydı bellekte tutan kodda bu fark önemlidir.

| İfade | Değeri |
|---|---|
| `sizeof(struct B)` | 12 |
| `offsetof(struct B, d)` | 8 (`<stddef.h>`) |

### Dosya biçimleri: #pragma pack
Bir dosya başlığı ya da ağ paketi, dolgusuz ve **bayt bayt** tanımlanmış bir düzene sahiptir. C kodu bu düzeni bir yapıyla örtüştürmek için dolguyu kapatır:

```c
#pragma pack(push, 1)
typedef struct {
    char     imza[2];     // ofset 0
    uint32_t boyut;       // ofset 2 (dolgu yok!)
    uint16_t surum;       // ofset 6
} Baslik;                 // sizeof 8
#pragma pack(pop)
```

İkili dosya ayrıştıran kodda `#pragma pack(1)` ya da `__attribute__((packed))` görürsen, yapının bir disk ya da ağ düzenini birebir yansıttığını anla.
:::

::: anlat Yapı dizileri, ok ve union
```c
typedef struct { char ad[16]; int cpu; } Sunucu;
Sunucu liste[3] = { {"web01", 72}, {"db01", 91}, {"web02", 65} };
Sunucu *p = &liste[1];
printf("%s %d\n", p->ad, p->cpu);   // db01 91      p->cpu, (*p).cpu ile aynıdır
p++;                                 // bir sonraki YAPIYA: sizeof(Sunucu) kadar ilerler
```

`union` bütün alanlarını **aynı adreste** tutar; boyutu en büyük alanınkidir. Aynı baytları farklı türlerde okumanın yoludur:

```c
union {
    uint32_t sayi;
    uint8_t  bayt[4];
} v;
v.sayi = 0x11223344;
printf("%02x\n", v.bayt[0]);   // little endian makinede 44: en düşük bayt önce
```

> [!NOT]
> Bellek dökümlerinde ve ikili dosyalarda bir yapıyı elle çözerken ofsetleri dolguyu hesaba katarak bul: "ilk alan 1 bayt, ikinci alan 4 baytsa ikincisi ofset 1'de değil 4'te başlar." Yanlış ofset, bütün sonraki alanları kaydırır.
:::

::: tahmin
Çıktı (x86-64, 64 bit Windows ya da Linux):

```c
struct A { char c; int i; };
struct B { char c; int i; char d; };
struct C { int i; char c; char d; };
printf("%zu %zu %zu\n", sizeof(struct A), sizeof(struct B), sizeof(struct C));
union { uint32_t u; uint8_t b[4]; } v;
v.u = 0x11223344;
printf("%x\n", v.b[0]);
```

```gercek
8 12 8
44
```

???

`8 12 8`: `A`'da `char`'dan sonra 3 bayt dolgu, `int` ofset 4'te. `B`'de `d` ofset 8'de, yapı 4'ün katına (12) yuvarlanır. `C`'de iki `char` `int`'ten sonra ard arda durur (ofset 4 ve 5), 8'e yuvarlanır. `44`: union'ın baytları sayının bellekteki hâlidir; little endian'da en düşük bayt (0x44) önce gelir.
:::

::: gorev Yapının boyutu
Alanların boyutlarını (1, 2, 4 ya da 8 bayt; her alanın hizalaması boyutuna eşit) sırayla alan `yapi_boyutu(alanlar)` fonksiyonunu yaz: yukarıdaki iki kurala göre `sizeof` değerini döndürsün.

```starter
def yapi_boyutu(alanlar):
    return sum(alanlar)
```

```test
need("yapi_boyutu")
eq(yapi_boyutu([1, 4]), 8, "char, int")
eq(yapi_boyutu([1, 4, 1]), 12, "char, int, char")
eq(yapi_boyutu([4, 1, 1]), 8, "int, char, char")
eq(yapi_boyutu([1, 8]), 16, "char, int64_t")
eq(yapi_boyutu([2, 1]), 4, "short, char: 2'nin katına yuvarlanır")
eq(yapi_boyutu([1, 1, 1]), 3, "üç char: dolgu yok")
eq(yapi_boyutu([8, 4]), 16, "int64_t, int: 8'in katına")
```

```solution
def yapi_boyutu(alanlar):
    ofset = 0
    for boyut in alanlar:
        if ofset % boyut:
            ofset += boyut - ofset % boyut
        ofset += boyut
    hiza = max(alanlar)
    if ofset % hiza:
        ofset += hiza - ofset % hiza
    return ofset
```

```hint
Her alan için: şu anki ofset alanın boyutunun katı değilse, katına kadar ilerle; sonra alanı ekle.
```

```hint
Sonunda toplamı en büyük alanın katına yuvarla.
```
:::

::: gorev Alanların ofsetleri
Aynı kurallarla her alanın yapı içindeki ofsetini (C'deki `offsetof`) liste olarak döndüren `ofsetler(alanlar)` fonksiyonunu yaz.

```starter
def ofsetler(alanlar):
    sonuc, ofset = [], 0
    for boyut in alanlar:
        sonuc.append(ofset)
        ofset += boyut
    return sonuc
```

```test
need("ofsetler")
eq(ofsetler([1, 4, 1]), [0, 4, 8], "char, int, char")
eq(ofsetler([4, 1, 1]), [0, 4, 5], "int, char, char")
eq(ofsetler([1, 2, 1, 8]), [0, 2, 4, 8], "char, short, char, int64_t")
eq(ofsetler([8]), [0], "tek alan")
```

```solution
def ofsetler(alanlar):
    sonuc, ofset = [], 0
    for boyut in alanlar:
        if ofset % boyut:
            ofset += boyut - ofset % boyut
        sonuc.append(ofset)
        ofset += boyut
    return sonuc
```

```hint
Başlangıç kodu dolguyu unutuyor. Alanı eklemeden önce ofseti alanın boyutunun katına yuvarla.
```
:::
