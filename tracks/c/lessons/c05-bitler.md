---
id: c05
title: Yapılar, Bitler ve Onaltılık
summary: struct ve typedef, bit işleçleri (& | ^ ~ << >>), bayrak maskeleri, onaltılık gösterim ve baytları little endian okumak.
kazanim: CLA 1.2, CLA 2.1
---

::: anlat Yapılar
`struct` birden çok alanı tek bir türde toplar; Python'daki basit bir sınıf ya da sözlüğe benzer:

```c
typedef struct {
    char ad[16];
    int cpu;
    unsigned int bayraklar;
} Sunucu;

Sunucu s = { "web01", 72, 0 };
Sunucu *p = &s;
printf("%s %d\n", s.ad, p->cpu);    // nokta: yapının kendisi; ok: işaretçi üzerinden
```

### Bit işleçleri
Düşük seviyeli kodda (sürücüler, dosya biçimleri, ağ protokolleri, ikili dosya incelemesi) birçok bilgi **tek tek bitlerde** saklanır:

| İşleç | Anlamı | Örnek (8 bit) |
|---|---|---|
| `a & b` | VE: ikisinde de 1 olan bitler | `1100 & 1010` → `1000` |
| `a \| b` | VEYA: herhangi birinde 1 olanlar | `1100 \| 1010` → `1110` |
| `a ^ b` | ÖZEL VEYA: farklı olanlar | `1100 ^ 1010` → `0110` |
| `~a` | bütün bitleri çevir | `~00001111` → `11110000` |
| `a << n` | n bit sola kaydır (× 2ⁿ) | `1 << 3` → `1000` (8) |
| `a >> n` | n bit sağa kaydır (÷ 2ⁿ) | `0xAB >> 4` → `0xA` |

### Bayrak kalıbı
Her bit bir evet/hayır bilgisidir. Biti açmak, sınamak ve kapatmak için hep aynı üç satır kullanılır:

```c
#define OKU      (1 << 2)   // 4
#define YAZ      (1 << 1)   // 2
#define CALISTIR (1 << 0)   // 1

unsigned int izin = 0;
izin |= OKU | YAZ;               // aç:    izin = 6
if (izin & YAZ) { /* ... */ }    // sına:  sıfırdan farklıysa açık
izin &= ~YAZ;                    // kapat: izin = 4
```

### Onaltılık ve bayt sırası
Bir bayt 8 bittir ve onaltılık tabanda tam iki hanedir: `0xFF` = 255. Çok baytlı bir sayı belleğe yazılırken x86 ve ARM işlemciler **en düşük baytı önce** yazar (little endian). `0x12345678` bellekte `78 56 34 12` olarak durur. Bir ikili dosyadan 4 bayt okuyup sayıya çevirirken bu yüzden kaydırarak birleştirilir:

```c
unsigned char b[4] = { 0x78, 0x56, 0x34, 0x12 };
unsigned int deger = b[0] | (b[1] << 8) | (b[2] << 16) | (b[3] << 24);
printf("%08x\n", deger);    // 12345678
```

> [!NOT]
> Bir ikili dosyayı onaltılık görüntüleyicide açtığında gördüğün `78 56 34 12` dizisinin aslında `0x12345678` sayısı olduğunu fark etmek, dosya biçimlerini ve bellek dökümlerini okumanın ilk adımıdır.
:::

::: tahmin
Çıktı:

```c
unsigned int bayrak = 0;
bayrak |= 1 << 0;
bayrak |= 1 << 3;
printf("%u %x\n", bayrak, bayrak);
printf("%d\n", (bayrak & (1 << 3)) != 0);
bayrak &= ~(1 << 0);
printf("%u\n", bayrak);
printf("%x\n", 0xAB >> 4);
```

```gercek
9 9
1
8
a
```

???

`9 9`, `1`, `8`, `a`. 0. ve 3. bitler açılınca değer 1 + 8 = 9 olur; onaltılıkta da 9'dur. 3. bit açık olduğu için sınama 1 verir. 0. bit kapatılınca 8 kalır. `0xAB` dört bit sağa kayınca üst yarısı `0xA` kalır.
:::

::: gorev İzin metni
Aşağıdaki C fonksiyonunun ürettiği metni döndüren `izin_metni(m)` fonksiyonunu Python'da yaz.

```c
#define OKU      4
#define YAZ      2
#define CALISTIR 1

void izin_metni(int m, char *cikti) {      // cikti en az 4 bayt
    cikti[0] = (m & OKU)      ? 'r' : '-';
    cikti[1] = (m & YAZ)      ? 'w' : '-';
    cikti[2] = (m & CALISTIR) ? 'x' : '-';
    cikti[3] = '\0';
}
```

```starter
def izin_metni(m):
    return "rwx"
```

```test
need("izin_metni")
eq(izin_metni(7), "rwx", "7 → rwx")
eq(izin_metni(6), "rw-", "6 → rw-")
eq(izin_metni(5), "r-x", "5 → r-x")
eq(izin_metni(0), "---", "0 → ---")
eq(izin_metni(12), "r--", "12: yalnızca alttaki üç bit önemli → r--")
```

```solution
def izin_metni(m):
    return ("r" if m & 4 else "-") + ("w" if m & 2 else "-") + ("x" if m & 1 else "-")
```

```hint
Python'da da `&` aynı işi yapar: `m & 4` sıfırdan farklıysa okuma izni var.
```
:::

::: gorev Little endian okuma
4 baytlık bir `bytes` nesnesini C kodundaki gibi **little endian** okuyup işaretsiz tam sayı döndüren `oku_le(b)` fonksiyonunu yaz (hazır `int.from_bytes` kullanmadan, kaydırmalarla).

```c
unsigned int oku_le(const unsigned char *b) {
    return b[0] | (b[1] << 8) | (b[2] << 16) | ((unsigned int)b[3] << 24);
}
```

```starter
def oku_le(b):
    return (b[0] << 24) | (b[1] << 16) | (b[2] << 8) | b[3]
```

```test
need("oku_le")
eq(oku_le(bytes([0x78, 0x56, 0x34, 0x12])), 0x12345678, "78 56 34 12 → 0x12345678")
eq(oku_le(bytes([0xFF, 0, 0, 0])), 255, "FF 00 00 00 → 255")
eq(oku_le(bytes([0, 0, 0, 0x80])), 0x80000000, "en üst bit")
ok(not calls("from_bytes"), "int.from_bytes kullanma; kaydırmalarla birleştir")
```

```solution
def oku_le(b):
    return b[0] | (b[1] << 8) | (b[2] << 16) | (b[3] << 24)
```

```hint
Little endian'da **ilk** bayt en düşük değerlidir: `b[0]` kaydırılmaz, `b[3]` 24 bit sola kaydırılır.
```
:::
