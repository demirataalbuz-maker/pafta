---
id: c08
title: Bayt Tamponları
summary: unsigned char tamponları, memcpy, memset ve memcmp, ofsetten little ve big endian alan okumak, sınır denetimli okuyucu fonksiyonlar, toplam ve XOR sağlama toplamları, imza (magic) baytları ve onaltılık döküm satırı.
kazanim: CLA 2.4
---

::: anlat Bir tampon, bir bayt dizisi
İkili veriyle çalışan kod (dosya ayrıştırıcıları, ağ kodu, sıkıştırma, şifreleme kütüphaneleri) veriyi bir **bayt tamponu** olarak tutar: `unsigned char buf[N]` ya da `uint8_t *veri`. Üç temel işlev neredeyse her yerde geçer:

| İşlev | Ne yapar |
|---|---|
| `memcpy(hedef, kaynak, n)` | n baytı kopyalar (alanlar çakışmamalı; çakışıyorsa `memmove`) |
| `memset(buf, 0, n)` | n baytı bir değerle doldurur: genellikle sıfırlamak için |
| `memcmp(a, b, n)` | n baytı karşılaştırır; eşitse 0 |

Dosya biçimlerinin çoğu ilk birkaç baytta bir **imza** (magic number) taşır: ZIP `50 4B 03 04` (`PK..`), PNG `89 50 4E 47`, ELF `7F 45 4C 46`, Windows yürütülebilir dosyası `4D 5A` (`MZ`). Ayrıştırıcı önce imzayı denetler:

```c
if (boyut < 4 || memcmp(veri, "PK\x03\x04", 4) != 0) {
    return -1;      // bu bir ZIP değil
}
```

### Ofsetten alan okumak
Tampondaki çok baytlı bir alanı okumak için baytlar kaydırılarak birleştirilir (C05). Dosya biçimleri çoğunlukla **little endian**, ağ protokolleri ise **big endian**'dır ("ağ bayt sırası"):

```c
uint16_t u16_le(const uint8_t *p) { return p[0] | (p[1] << 8); }
uint32_t u32_be(const uint8_t *p) {
    return ((uint32_t)p[0] << 24) | ((uint32_t)p[1] << 16) | ((uint32_t)p[2] << 8) | p[3];
}
```

Ağ kodunda bunun yerine hazır `ntohs` (16 bit) ve `ntohl` (32 bit) işlevlerini görürsün: "network to host", ağ sırasından makinenin sırasına.

> [!GÜVENLİK]
> Bir ofsetten okumadan önce **her zaman** `ofset + alan_boyutu <= tampon_boyutu` olduğunu denetle; ofset dosyanın içinden geliyorsa (yani güvenilmez veriyse) bu denetim hayatidir. Toplamayı taşmaya karşı da düşün (C06): `ofset + 4` çok büyük bir ofsette sarabilir; güvenli biçim `ofset <= boyut && boyut - ofset >= 4`'tür.
:::

::: anlat Sağlama toplamları ve döküm
Bir verinin bozulmadığını denetlemenin en basit yolu bir **sağlama toplamıdır** (checksum): baytları toplayıp ya da XOR'layıp sonucu veriyle birlikte saklamak. Okuyan taraf aynı hesabı yapar ve karşılaştırır:

```c
uint8_t toplam8(const uint8_t *b, size_t n) {
    unsigned int t = 0;
    for (size_t i = 0; i < n; i++) t += b[i];
    return (uint8_t)(t & 0xFF);
}

uint8_t xor8(const uint8_t *b, size_t n) {
    uint8_t t = 0;
    for (size_t i = 0; i < n; i++) t ^= b[i];
    return t;
}
```

Gerçek sistemlerde daha güçlü yöntemler (CRC32, Adler-32) ve bütünlük için kriptografik özetler (SHA-256) kullanılır; ama döngünün okunuşu aynıdır.

Bellek ya da dosya içeriğini incelemenin klasik görünümü **onaltılık dökümdür** (hexdump): ofset, baytlar ve yazdırılabilir karakterler:

```text
00000000  50 4b 03 04 14 00 00 00  PK......
```
:::

::: tahmin
Çıktı:

```c
unsigned char b[] = { 0x50, 0x4B, 0x03, 0x04, 0x14, 0x00 };
printf("%02X %02X %02X %02X\n", b[0], b[1], b[2], b[3]);
unsigned short v = b[4] | (b[5] << 8);
printf("%u\n", v);
unsigned char t = 0;
for (int i = 0; i < 6; i++) t ^= b[i];
printf("%02x\n", t);
printf("%d\n", memcmp(b, "PK", 2) == 0);
```

```gercek
50 4B 03 04
20
08
1
```

???

`50 4B 03 04`: `%02X` her baytı iki haneli büyük harfli onaltılık yazar. `20`: 4. ve 5. baytlar little endian okunur: 0x14 + 0x00 × 256 = 20. `08`: altı baytın XOR'u 0x08'dir; `%02x` başına sıfır koyar. `1`: ilk iki bayt 0x50 0x4B, yani `"PK"`'dir.
:::

::: gorev Sınır denetimli okuyucular
İki fonksiyon yaz. Tampon bir `bytes` nesnesidir; okuma tamponun dışına taşacaksa `None` döndürsünler (C'deki "-1: hata" dönüşü gibi):

- `oku_u16_le(b, ofset)`: ofsetteki 2 baytı little endian sayı olarak
- `oku_u32_be(b, ofset)`: ofsetteki 4 baytı big endian sayı olarak

```starter
def oku_u16_le(b, ofset):
    return b[ofset] | (b[ofset + 1] << 8)


def oku_u32_be(b, ofset):
    return (b[ofset] << 24) | (b[ofset + 1] << 16) | (b[ofset + 2] << 8) | b[ofset + 3]
```

```test
need("oku_u16_le")
need("oku_u32_be")
veri = bytes([0x50, 0x4B, 0x03, 0x04, 0x14, 0x00, 0xC0, 0xA8, 0x01, 0x0A])
eq(oku_u16_le(veri, 4), 20, "0x0014")
eq(oku_u16_le(veri, 0), 0x4B50, "PK → 0x4B50")
eq(oku_u32_be(veri, 6), 0xC0A8010A, "192.168.1.10'un ağ sırası")
eq(oku_u16_le(veri, 9), None, "son baytta 2 bayt yok")
eq(oku_u32_be(veri, 7), None, "taşan okuma")
eq(oku_u16_le(veri, -1), None, "negatif ofset")
eq(oku_u32_be(b"", 0), None, "boş tampon")
eq(oku_u16_le(veri, 8), 0x0A01, "son iki bayt okunabilir (ofset = len - 2)")
```

```solution
def oku_u16_le(b, ofset):
    if ofset < 0 or ofset + 2 > len(b):
        return None
    return b[ofset] | (b[ofset + 1] << 8)


def oku_u32_be(b, ofset):
    if ofset < 0 or ofset + 4 > len(b):
        return None
    return (b[ofset] << 24) | (b[ofset + 1] << 16) | (b[ofset + 2] << 8) | b[ofset + 3]
```

```hint
Okumadan önce denetle: `ofset < 0 or ofset + 2 > len(b)` ise `None`. Python'da negatif indeks sondan sayar; C'de böyle bir kolaylık yok, açıkça reddet.
```
:::

::: gorev Sağlama toplamı
Yukarıdaki `toplam8` fonksiyonunu Python'da yaz. Bir de `tumleyen(b)` yaz: verinin sonuna eklendiğinde bütün baytların 8 bitlik toplamını **sıfır** yapan baytı döndürsün (birçok eski biçimin kullandığı "toplam sıfır olmalı" denetimi).

```starter
def toplam8(b):
    return sum(b)


def tumleyen(b):
    return 0
```

```test
need("toplam8")
need("tumleyen")
eq(toplam8(b"\x01\x02\x03"), 6, "küçük toplam")
eq(toplam8(bytes([200, 100])), 44, "300 → 8 bit: 44")
eq(toplam8(b""), 0, "boş veri")
eq(tumleyen(bytes([200, 100])), 212, "44 + 212 = 256 → 0")
eq(tumleyen(b"\x00"), 0, "toplam zaten sıfır")
veri = b"PAFTA"
eq(toplam8(veri + bytes([tumleyen(veri)])), 0, "eklenince toplam sıfır")
```

```solution
def toplam8(b):
    return sum(b) & 0xFF


def tumleyen(b):
    return (256 - toplam8(b)) & 0xFF
```

```hint
C'deki `(uint8_t)(t & 0xFF)`: toplamın alt 8 biti.
```

```hint
Tümleyen: toplamı 256'ya tamamlayan sayı, yine 8 bite kesilmiş: `(256 - toplam8(b)) & 0xFF`. Toplam 0 ise sonuç da 0 olmalı.
```
:::

::: gorev Onaltılık döküm satırı
Aşağıdaki C kodu bir döküm satırı yazar. Aynı metni (satır sonu olmadan) döndüren `dokum_satiri(ofset, b)` fonksiyonunu yaz; `b` en fazla 8 baytlık bir `bytes` nesnesidir.

```c
void dokum_satiri(size_t ofset, const uint8_t *b, size_t n) {
    printf("%08zx  ", ofset);
    for (size_t i = 0; i < 8; i++) {
        if (i < n) printf("%02x ", b[i]);
        else       printf("   ");
    }
    printf(" ");
    for (size_t i = 0; i < n; i++)
        putchar(b[i] >= 0x20 && b[i] < 0x7F ? b[i] : '.');
    putchar('\n');
}
```

```starter
def dokum_satiri(ofset, b):
    return " ".join(f"{x:02x}" for x in b)
```

```test
need("dokum_satiri")
eq(dokum_satiri(0, bytes([0x50, 0x4B, 0x03, 0x04, 0x14, 0x00, 0x00, 0x00])),
   "00000000  50 4b 03 04 14 00 00 00  PK......", "tam satır")
eq(dokum_satiri(16, b"web01"), "00000010  77 65 62 30 31           web01", "eksik satır boşlukla tamamlanır")
eq(dokum_satiri(255, b"\x7f\x41"), "000000ff  7f 41                    .A", "0x7F yazdırılamaz")
eq(dokum_satiri(0, b"a b~"), "00000000  61 20 62 7e" + " " * 14 + "a b~", "boşluk (0x20) ve ~ (0x7E) yazdırılabilir")
```

```solution
def dokum_satiri(ofset, b):
    satir = f"{ofset:08x}  "
    for i in range(8):
        satir += f"{b[i]:02x} " if i < len(b) else "   "
    satir += " "
    satir += "".join(chr(x) if 0x20 <= x < 0x7F else "." for x in b)
    return satir
```

```hint
Ofset: `f"{ofset:08x}  "` (sonunda iki boşluk). Her bayt `"xx "`, eksik baytlar üç boşluk.
```

```hint
Bayt bölümünden sonra bir boşluk daha, sonra her bayt yazdırılabilirse (0x20 ile 0x7E arası) karakteri, değilse `.`.
```
:::
