---
id: c06
title: Tam Sayılar ve Taşma
summary: stdint.h türleri ve aralıkları, işaretsiz sayılarda sarma (mod 2ⁿ), işaretli taşmanın tanımsız olması, küçük türe atamada kesilme, char'ın işaret uzatması, işaretli ile işaretsiz karşılaştırma tuzağı ve size_t ile uzunluk denetimlerindeki alttan taşma.
kazanim: CLA 2.2
---

::: anlat Kaç bit, hangi aralık?
C'de bir tam sayı türü bellekte **sabit sayıda bit** kaplar ve o bitlere sığmayan değeri tutamaz. Düşük seviyeli kodda boyutun belli olması için `<stdint.h>` türleri kullanılır:

| Tür | Bit | Aralık |
|---|---|---|
| `uint8_t` / `int8_t` | 8 | 0 … 255 / −128 … 127 |
| `uint16_t` / `int16_t` | 16 | 0 … 65 535 / −32 768 … 32 767 |
| `uint32_t` / `int32_t` | 32 | 0 … 4 294 967 295 / ±2,1 milyar |
| `uint64_t` / `int64_t` | 64 | 0 … 1,8 × 10¹⁹ |
| `size_t` | 64 (64 bit sistemde) | uzunluklar ve boyutlar için, **işaretsiz** |

`int` çoğu sistemde 32 bittir. `long` ise Linux'ta 64, Windows'ta 32 bittir; ikili dosya biçimlerinde bu yüzden `long` değil sabit boyutlu türler görürsün.

### İşaretsiz sayı sarar
İşaretsiz bir sayı sınırını aşınca **başa sarar**: sonuç her zaman 2ⁿ'e göre kalandır.

```c
uint8_t a = 250;
a = a + 10;          // 260 sığmaz: 260 - 256 = 4
unsigned int x = 0;
x = x - 1;           // 4294967295 (0xFFFFFFFF)
```

**İşaretli** taşma ise **tanımsız davranıştır**: derleyici "bu asla olmaz" diye varsayıp kodu beklenmedik biçimde değiştirebilir. Okuduğun kodda `int` ile büyüyen bir sayaç görürsen sınırını düşün.

### Küçük türe atama ve işaret uzatma
Bir değeri daha küçük bir türe atamak **üst bitleri atar**, yalnızca alt bitler kalır: `(uint8_t)0x1234` → `0x34`. Ters yönde, işaretli bir `char` daha büyük bir türe genişlerken **işaret biti** kopyalanır:

```c
signed char s = (signed char)0xF0;   // bitler 11110000 → -16
unsigned char u = 0xF0;              // aynı bitler → 240
int i = s;                           // -16 (0xFFFFFFF0)
int j = u;                           // 240 (0x000000F0)
```

Bir bayt tamponunu `char *` ile okuyan kod, 0x80'den büyük baytları negatif sayı olarak görür. İkili veriyle çalışan kodda bu yüzden hep `unsigned char` ya da `uint8_t` kullanılır.
:::

::: anlat İki klasik tuzak
**İşaretli ile işaretsiz karşılaştırma.** Bir işlemde biri işaretsizse, işaretli olan da işaretsize çevrilir. `-1`, `0xFFFFFFFF` olur ve her şeyden büyüktür:

```c
int uzunluk = -1;
unsigned int sinir = 100;
if (uzunluk < sinir) { /* buraya GİRMEZ: -1, 4294967295 olarak karşılaştırılır */ }
```

**Uzunluk denetiminde alttan taşma.** `size_t` işaretsiz olduğu için bir çıkarma işleminin sonucu negatif olamaz; sarar:

```c
int baslik_var_mi(size_t uzunluk) {
    if (uzunluk - 4 >= 8)     // "en az 12 bayt var mı?" diye yazılmış
        return 1;
    return 0;
}
```

`uzunluk` 2 olduğunda `2 - 4` sonucu −2 değil, 18 446 744 073 709 551 614'tür ve koşul **doğru** çıkar. Denetim, en çok korunması gereken durumda, yani veri çok kısayken başarısız olur. Doğrusu çıkarmadan önce karşılaştırmaktır: `if (uzunluk >= 12)`.

> [!GÜVENLİK]
> Kod okurken uzunluk ve boyut hesaplarında üç şeye bak: **çıkarma** (alttan taşabilir mi?), **çarpma ve toplama** (üstten taşıp küçük bir sayıya sarabilir mi?), **tür değişimi** (işaretli ile işaretsiz karışıyor mu, büyük değer küçük türe mi atanıyor?). Bellek taşmalarının büyük kısmı bu üç yerden birinde başlar.
:::

::: tahmin
Çıktı:

```c
uint8_t a = 200, b = 100;
uint8_t c = a + b;
int d = a + b;
printf("%u %d\n", c, d);
signed char s = (signed char)0xF0;
unsigned char u = 0xF0;
printf("%d %d\n", s, u);
unsigned int x = 0;
x = x - 1;
printf("%u %x\n", x, x);
printf("%d\n", -1 < 1u);
```

```gercek
44 300
-16 240
4294967295 ffffffff
0
```

???

`44 300`: toplama `int` olarak yapılır (300), ama `uint8_t c`'ye atanınca alt 8 bit kalır: 300 − 256 = 44. `d` ise `int` olduğu için 300'ü tutar. `-16 240`: aynı 0xF0 baytı işaretli okununca −16, işaretsiz okununca 240'tır. `4294967295 ffffffff`: işaretsiz 0'dan 1 çıkarmak başa sarar. `0`: `-1`, işaretsize çevrilip 4294967295 olur ve 1'den küçük değildir.
:::

::: gorev Kesme ve işaret
İki fonksiyon yaz:

- `kes(deger, bit)`: değeri `bit` bitlik **işaretsiz** bir türe atanmış gibi döndürsün: C'deki `(uint8_t)deger`, `(uint16_t)deger` ...
- `isaretli(deger, bit)`: `bit` bitlik bir bit dizisini **ikiye tümleyen** işaretli sayı olarak yorumlasın: `(int8_t)0xF0` → −16.

```starter
def kes(deger, bit):
    return deger


def isaretli(deger, bit):
    return deger
```

```test
need("kes")
need("isaretli")
eq(kes(300, 8), 44, "(uint8_t)300 = 44")
eq(kes(-1, 8), 255, "(uint8_t)-1 = 255")
eq(kes(0x12345678, 16), 0x5678, "üst bitler atılır")
eq(kes(70000, 16), 4464, "(uint16_t)70000 = 4464")
eq(isaretli(0xF0, 8), -16, "0xF0 → -16")
eq(isaretli(0x7F, 8), 127, "en büyük pozitif 8 bit")
eq(isaretli(0x80, 8), -128, "en küçük negatif 8 bit")
eq(isaretli(0xFFFF, 16), -1, "16 bit, hepsi 1 → -1")
eq(isaretli(5, 8), 5, "küçük pozitif aynı kalır")
```

```solution
def kes(deger, bit):
    return deger & ((1 << bit) - 1)


def isaretli(deger, bit):
    deger = kes(deger, bit)
    if deger >= 1 << (bit - 1):
        deger -= 1 << bit
    return deger
```

```hint
Kesme, alt `bit` biti tutan bir maskeyle VE'lemektir: `deger & ((1 << bit) - 1)`. Python'da negatif sayılar da bu maskeyle doğru sonucu verir.
```

```hint
İşaretli yorum: en üst bit 1 ise (değer ≥ 2^(bit−1)) sayı negatiftir; 2^bit çıkar.
```
:::

::: gorev Alttan taşan denetim
Yukarıdaki `baslik_var_mi` fonksiyonunu, `size_t`'nin 64 bit işaretsiz olduğu bir sistemde **olduğu gibi** (hatasıyla birlikte) Python'da yaz. Ardından aynı denetimin doğru sürümünü `duzeltilmis(uzunluk)` olarak yaz. İkisi de 1 ya da 0 döndürsün.

```c
int baslik_var_mi(size_t uzunluk) {
    if (uzunluk - 4 >= 8)
        return 1;
    return 0;
}
```

```starter
def baslik_var_mi(uzunluk):
    return 1 if uzunluk - 4 >= 8 else 0


def duzeltilmis(uzunluk):
    return 1 if uzunluk - 4 >= 8 else 0
```

```test
need("baslik_var_mi")
need("duzeltilmis")
eq(baslik_var_mi(12), 1, "12 bayt: yeterli")
eq(baslik_var_mi(11), 0, "11 bayt: yetersiz")
eq(baslik_var_mi(2), 1, "hata: 2 - 4 sarar ve koşul doğru çıkar")
eq(baslik_var_mi(0), 1, "hata: 0 - 4 de sarar")
eq(baslik_var_mi(4), 0, "4 - 4 = 0: yetersiz")
eq([duzeltilmis(n) for n in (0, 2, 4, 11, 12, 100)], [0, 0, 0, 0, 1, 1], "doğru sürüm")
```

```solution
def baslik_var_mi(uzunluk):
    fark = (uzunluk - 4) % 2**64
    return 1 if fark >= 8 else 0


def duzeltilmis(uzunluk):
    return 1 if uzunluk >= 12 else 0
```

```hint
Python'un tam sayıları sarmaz. 64 bit işaretsiz çıkarmayı taklit etmek için sonucu 2⁶⁴'e göre kalana çevir: `(uzunluk - 4) % 2**64`.
```

```hint
Doğru sürüm çıkarma yapmaz, doğrudan karşılaştırır: `uzunluk >= 12`.
```
:::
