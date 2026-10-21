---
id: as03
title: Bellek Adresleme, Little-Endian ve movzx/movsx
summary: BYTE/WORD/DWORD/QWORD PTR bellek erişimleri, küçük sonlu (little-endian) bayt dizilimi, sıfırla genişletme (movzx) ve işaret bitiyle genişletme (movsx/movsxd).
---

::: anlat Bellek işlenenleri ve Little-Endian (küçük sonlu) dizilim
Assembly'de `lea` dışındaki her köşeli parantez `[...]` **belleğe erişir**. Bellekten kaç bayt okunacağını veya belleğe kaç bayt yazılacağını hem hedef yazmacın boyutu hem de boyut belirteci (*size directive*) söyler:

| Belirteç | Boyut | C karşılığı | Örnek |
|---|---|---|---|
| `BYTE PTR` | 1 bayt (8-bit) | `uint8_t` / `int8_t` | `mov al, BYTE PTR [rcx]` |
| `WORD PTR` | 2 bayt (16-bit) | `uint16_t` / `int16_t` | `mov ax, WORD PTR [rcx + 2]` |
| `DWORD PTR` | 4 bayt (32-bit) | `uint32_t` / `int32_t` | `mov eax, DWORD PTR [rcx + 4]` |
| `QWORD PTR` | 8 bayt (64-bit) | `uint64_t` / işaretçi | `mov rax, QWORD PTR [rcx + 8]` |

### Little-Endian (Küçük Sonlu) Kuralı
x86 ve x86-64 mimarisi çok baytlı tam sayıları bellekte **küçük sonlu (*little-endian*)** olarak saklar: **en düşük anlamlı bayt (LSB) en küçük bellek adresinde durur!**

Örneğin `0x11223344` sayısı `0x1000` adresinden itibaren bellekte şöyle dizilir:

```text
Adres:   [0x1000]  [0x1001]  [0x1002]  [0x1003]
Bayt:      0x44      0x33      0x22      0x11
```

Bu belleğe farklı genişliklerle baktığımızda:

```asm
; [rcx] adresinde sırasıyla 0x44, 0x33, 0x22, 0x11 baytları duruyor olsun:
mov al,  BYTE PTR [rcx]       #! al  = 0x44       (yalnızca ilk bayt)
mov ax,  WORD PTR [rcx]       #! ax  = 0x3344     (ilk 2 bayt ters birleşir: 0x33 << 8 | 0x44)
mov eax, DWORD PTR [rcx]      #! eax = 0x11223344 (4 bayt little-endian birleşir)
```

> [!TUZAK]
> Ağ protokollerinde (TCP/IP başlıkları, port numaraları) bayt sırası **Big-Endian** (*büyük sonlu*), x86 belleğinde ise **Little-Endian**'dır. Bir bellek dökümünde (hexdump) `34 12` baytlarını gördüğünde `WORD PTR` okuması bunu `0x3412` değil **`0x1234`** olarak yazmaca yükler!
:::

::: anlat Küçük veriyi büyük yazmaca taşımak: `movzx` ve `movsx`
1 baytlık (`BYTE PTR`) veya 2 baytlık (`WORD PTR`) bir veriyi 32-bit (`eax`) veya 64-bit (`rax`) bir yazmaca taşırken üst bitlerin neyle doldurulacağı sayının **işaretsiz (`unsigned`)** mi yoksa **işaretli (`signed`)** mi olduğuna bağlıdır:

- **`movzx` (*Move with Zero-Extend*):** Üst bitlerin tamamını **`0`** ile doldurur. C'deki `uint8_t` ve `uint16_t` okumalarının karşılığıdır.
- **`movsx` (*Move with Sign-Extend*):** Kaynağın en anlamlı bitini (işaret bitini: 1 baytta 7. bit, 2 baytta 15. bit) üst bitlerin tamamına **kopyalar**. C'deki `int8_t` (`char`) ve `int16_t` (`short`) okumalarının karşılığıdır. (32-bit'ten 64-bit'e işaretli genişletme için **`movsxd`** kullanılır: `movsxd rax, edx`).

```asm
; Bellekte [rcx] adresinde 0xFC (252 veya işaretli -4) baytı dursun:
movzx eax, BYTE PTR [rcx]     #! sıfırla genişlet: eax = 0x000000FC (252)
movsx eax, BYTE PTR [rcx]     #! işaretle genişlet (0xFC >= 0x80): eax = 0xFFFFFFFC (-4)

; Bellekte [rcx + 1] adresinde 0x7F (127, işaret biti 0) baytı dursun:
movzx edx, BYTE PTR [rcx + 1] #! edx = 0x0000007F (127)
movsx edx, BYTE PTR [rcx + 1] #! işaret biti 0 olduğu için edx = 0x0000007F (127)
```

> [!GÜVENLİK]
> C kodunda `char` (işaretli 1 bayt) bir uzunluk alanı `movsx eax, BYTE PTR [rcx]` ile okunduğunda, `0x80` (`128`) ve üzerindeki her bayt negatif bir 32-bit tam sayıya (`-128 .. -1`) dönüşür! Dizi indeksi veya uzunluk kontrolünde `movsx` görmek, negatif indeksleme hatasının (*signedness bug*) habercisidir.
:::

::: tahmin
Bellekte `rcx` adresinde sırasıyla `[0x34, 0x12, 0xFC, 0x00]` baytları duruyor. Aşağıdaki üç fonksiyon aynı bellek adresine uygulanıp ilk ikisi işaretli onluk tam sayı, üçüncüsü `0x{:04X}` biçiminde yazdırılıyor. Çıktı ne olur?

```asm
as03_u8:
    movzx eax, BYTE PTR [rcx + 2]
    ret

as03_s8:
    movsx eax, BYTE PTR [rcx + 2]
    ret

as03_u16:
    movzx eax, WORD PTR [rcx]
    ret
```

```gercek
252
-4
0x1234
```

???

`252`, `-4`, `0x1234`. `[rcx + 2]` adresindeki bayt `0xFC`'dir. `as03_u8` bunu `movzx` ile sıfırla genişleterek `0x000000FC` (`252`) yapar. `as03_s8` aynı `0xFC` baytını `movsx` ile işaretle genişletir; `0xFC`'nin en üst biti `1` olduğu için üst 24 bit `1` ile dolar (`0xFFFFFFFC`), bu da 32-bit işaretli tam sayıda `-4` demektir. `as03_u16` ise `[rcx]` adresinden 2 baytlık `WORD PTR` (`0x34, 0x12`) okur; little-endian kuralıyla düşük adresteki `0x34` alt bayta, `0x12` üst bayta yerleşir ve `0x1234` döner.
:::

::: gorev Little-Endian bellek okuyucu (`movzx` / `movsx`)
Verilen `bellek` (`bytes`) tamponundan `ofset` konumunda `boyut` (`1`, `2` veya `4` bayt) genişliğinde little-endian okuma yapan `bellekten_oku(bellek, ofset, boyut, isaretli_mi=False)` fonksiyonunu yaz:
- `boyut` `1`, `2` veya `4` değilse `ValueError` fırlat.
- `ofset < 0` veya `ofset + boyut > len(bellek)` ise `IndexError` fırlat.
- `isaretli_mi` `False` ise `movzx` (işaretsiz `0 .. 2^(8*boyut)-1`), `True` ise `movsx` (işaretli tam sayı) değerini döndür.

```starter
def bellekten_oku(bellek, ofset, boyut, isaretli_mi=False):
    return bellek[ofset]
```

```test
need("bellekten_oku")
buf = bytes([0x34, 0x12, 0xFC, 0x7F, 0x80, 0xFF])
eq(bellekten_oku(buf, 0, 2, False), 0x1234, "WORD PTR [0]: 0x34, 0x12 -> 0x1234")
eq(bellekten_oku(buf, 2, 1, False), 252, "movzx BYTE PTR [2]: 0xFC -> 252")
eq(bellekten_oku(buf, 2, 1, True), -4, "movsx BYTE PTR [2]: 0xFC -> -4")
eq(bellekten_oku(buf, 3, 1, True), 127, "movsx sınır: 0x7F (127) pozitif kalmalı")
eq(bellekten_oku(buf, 4, 1, True), -128, "movsx sınır: 0x80 (-128) negatif olmalı")
eq(bellekten_oku(buf, 4, 2, True), -128, "WORD PTR [4]: 0x80, 0xFF -> 0xFF80 -> -128")
eq(bellekten_oku(buf, 0, 4, False), 0x7FFC1234, "DWORD PTR [0]: 4 bayt little-endian")
raises(IndexError, lambda: bellekten_oku(buf, 5, 2, False), msg="tampon sonunu aşan okuma IndexError")
raises(IndexError, lambda: bellekten_oku(buf, -1, 1, False), msg="negatif ofset IndexError")
raises(ValueError, lambda: bellekten_oku(buf, 0, 3, False), msg="boyut=3 geçersiz -> ValueError")
```

```solution
def bellekten_oku(bellek, ofset, boyut, isaretli_mi=False):
    if boyut not in (1, 2, 4):
        raise ValueError(f"Geçersiz boyut: {boyut}")
    if ofset < 0 or ofset + boyut > len(bellek):
        raise IndexError("Bellek sınırları dışında okuma")
    dilim = bellek[ofset : ofset + boyut]
    return int.from_bytes(dilim, byteorder="little", signed=isaretli_mi)
```

```hint
Önce `boyut not in (1, 2, 4)` ve `ofset < 0 or ofset + boyut > len(bellek)` sınırlarını denetle. Ardından `int.from_bytes(bellek[ofset:ofset+boyut], "little", signed=isaretli_mi)` kullanabilirsin.
```
:::

::: gorev `movzx` ve `movsx` 32-bit yazmaç karşılaştırması
Tek bir bayt değeri `b` (`0 <= b <= 255`) verildiğinde:
1. `movzx eax, bl`
2. `movsx eax, bl`
komutlarının ardından `eax` yazmacında oluşan 32-bit bit örüntüsünü `("0x{:08X}", "0x{:08X}")` biçiminde iki büyük harfli hex metin ikilisi olarak döndüren `uzanti_karsilastir(b)` fonksiyonunu yaz.

```starter
def uzanti_karsilastir(b):
    return (f"0x{b:08X}", f"0x{b:08X}")
```

```test
need("uzanti_karsilastir")
eq(uzanti_karsilastir(0x00), ("0x00000000", "0x00000000"), "0x00 için ikisi de sıfır")
eq(uzanti_karsilastir(0x7F), ("0x0000007F", "0x0000007F"), "sınır 0x7F (127): işaret biti 0 olduğu için ikisi de 0x0000007F")
eq(uzanti_karsilastir(0x80), ("0x00000080", "0xFFFFFF80"), "sınır 0x80 (-128): işaret biti 1 olduğu için movsx üstü FF ile doldurur")
eq(uzanti_karsilastir(0xFC), ("0x000000FC", "0xFFFFFFFC"), "0xFC (-4) için 0x000000FC ve 0xFFFFFFFC")
eq(uzanti_karsilastir(0xFF), ("0x000000FF", "0xFFFFFFFF"), "0xFF (-1) için 0x000000FF ve 0xFFFFFFFF")
```

```solution
def uzanti_karsilastir(b):
    b &= 0xFF
    zx = b
    sx = (b | 0xFFFFFF00) if (b & 0x80) else b
    return (f"0x{zx:08X}", f"0x{sx:08X}")
```

```hint
`b & 0x80` sıfırdan farklıysa (7. bit `1` ise) `movsx` üst 24 biti `1` yapar (`b | 0xFFFFFF00`), aksi halde `b` olarak kalır.
```
:::
