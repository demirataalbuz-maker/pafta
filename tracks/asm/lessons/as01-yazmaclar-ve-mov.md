---
id: as01
title: Yazmaçlar, Alt Dilimler ve mov
summary: x86-64 genel amaçlı yazmaçları (rax-r15), 64/32/16/8-bit alt dilimler, 32-bit yazmada üst 32 bitin otomatik sıfırlanması kuralı, Intel ve AT&T sözdizimi farkı, mov ve xor ile sıfırlama.
---

::: anlat x86-64 yazmaç ailesi ve alt dilimler
x86-64 işlemcisinde tam sayı ve adres işlemlerinin omurgasını **16 adet 64-bit genel amaçlı yazmaç** (*general-purpose registers*) oluşturur. Bunlara ek olarak sıradaki komutun adresini tutan **`rip`** (*Instruction Pointer*) ve durum bayraklarını tutan **`rflags`** vardır.

Tarihsel geriye uyumluluk nedeniyle (16-bit 8086 → 32-bit i386 → 64-bit x86-64) aynı 64-bit yazmacın alt kısımlarına farklı adlarla erişilebilir:

```text
63                              31              15      8 7     0
+-------------------------------+---------------+--------+-------+
|                               |               |   AH   |   AL  |
|                               |               +--------+-------+
|                               |               |       AX       |
|                               +---------------+----------------+
|                               |              EAX               |
+-------------------------------+--------------------------------+
|                              RAX                               |
+----------------------------------------------------------------+
```

| 64-bit (8B) | 32-bit (4B) | 16-bit (2B) | 8-bit üst | 8-bit alt | Geleneksel rolü |
|---|---|---|---|---|---|
| `rax` | `eax` | `ax` | `ah` | `al` | dönüş değeri (*accumulator*) ve aritmetik |
| `rbx` | `ebx` | `bx` | `bh` | `bl` | korunan (*callee-saved*) taban yazmacı |
| `rcx` | `ecx` | `cx` | `ch` | `cl` | sayaç, kaydırma miktarı (`cl`), Windows 1. argüman |
| `rdx` | `edx` | `dx` | `dh` | `dl` | G/Ç, çarpma/bölme üst yarısı, Windows 2. argüman |
| `rsi` | `esi` | `si` | — | `sil` | kaynak indeks (*source index*), Linux 2. argüman |
| `rdi` | `edi` | `di` | — | `dil` | hedef indeks (*destination index*), Linux 1. argüman |
| `rbp` | `ebp` | `bp` | — | `bpl` | yığın çerçeve tabanı (*base pointer*) |
| `rsp` | `esp` | `sp` | — | `spl` | yığın tepesi (*stack pointer*) |
| `r8`–`r15` | `r8d`–`r15d` | `r8w`–`r15w` | — | `r8b`–`r15b` | x64 ile eklenen 8 yeni yazmaç |

```asm
; Intel sözdizimi: komut hedef, kaynak (hedef = kaynak)
mov rax, 0x1122334455667788   #! 64-bit rax yazmacının tamamına yaz
mov ecx, 42                   #! 32-bit ecx'e 42 yaz (rcx'in üst 32 biti sıfırlanır)
xor eax, eax                  #! rax'i sıfırlamanın en kısa ve hızlı yolu (2 bayt: 31 c0)
```

> [!NOT]
> **Intel ve AT&T sözdizimi farkı:** Pafta'da (ve Ghidra, IDA, x64dbg, `objdump -M intel` çıktılarında) **Intel sözdizimi** kullanılır: **`komut hedef, kaynak`** (`mov eax, ecx` → `eax = ecx`). Varsayılan GNU `objdump` ve `gdb` ise AT&T sözdizimi kullanır: yazmaçların başında `%`, sabitlerin başında `$` vardır ve sıra **`komut kaynak, hedef`** biçimindedir (`movl %ecx, %eax`).
:::

::: anlat Kritik x64 kuralı: 32-bit yazma üst yarıyı sıfırlar, 16/8-bit dokunmaz!
Disassembly okurken en çok hata yapılan nokta alt yazmaçlara yapılan atamaların üst bitlere etkisidir:

1. **32-bit alt yazmaca (`eax`, `ecx`, `r8d` vb.) yazan her komut, 64-bit yazmacın üst 32 bitini (`[63:32]`) otomatik olarak sıfırlar!** Bu nedenle derleyiciler `rax`'e küçük bir pozitif sayı yüklerken `mov rax, 5` (7 bayt) yerine `mov eax, 5` (5 bayt) üretir.
2. **16-bit (`ax`, `cx`, `r8w`) veya 8-bit (`al`, `ah`, `cl`, `r8b`) alt yazmaca yazmak ise üst bitlere DOKUNMAZ!** Yalnızca o 16 veya 8 bitlik dilim değişir; geri kalan bitler eski değerini korur.

```asm
mov rax, 0xAABBCCDDEEFF1122   #! rax = 0xAABBCCDDEEFF1122
mov eax, 0x12345678           #! 32-bit yazma! Üst 32 bit sıfırlanır -> rax = 0x0000000012345678
mov ax,  0xABCD               #! 16-bit yazma! Üst bitler korunur  -> rax = 0x000000001234ABCD
mov al,  0xEF                 #! 8-bit alt!    Yalnızca [7:0]      -> rax = 0x000000001234ABEF
mov ah,  0x99                 #! 8-bit üst!    Yalnızca [15:8]     -> rax = 0x00000000123499EF
```

> [!TUZAK]
> Bir fonksiyonda `cmp al, 0` veya `mov al, 1` gördüğünde `rax`'in tamamının `1` olduğunu varsayma! Eğer öncesinde `xor eax, eax` yapılmamışsa `rax`'in üst 56 bitinde önceki işlemlerden kalan çöp veriler duruyor olabilir.
:::

::: tahmin
Aşağıdaki üç x86-64 fonksiyonu sırasıyla çalıştırılıyor: `as01_adim1(0xAABBCCDDEEFF1122)` çağrısının sonucu `r1`, `as01_adim2(r1)` sonucu `r2` ve `as01_adim3(r2)` sonucu `r3` olarak `0x{:08X}` biçiminde yazdırılıyor. Çıktı ne olur?

```asm
; Windows x64: ilk argüman rcx'te gelir, dönüş değeri rax'tedir.
as01_adim1:
    mov rax, rcx              ; rax = 0xAABBCCDDEEFF1122
    mov eax, 0x12345678
    ret

as01_adim2:
    mov rax, rcx              ; rax = r1
    mov ax, 0xABCD
    ret

as01_adim3:
    mov rax, rcx              ; rax = r2
    mov ah, 0xFF
    mov al, 0x00
    ret
```

```gercek
0x12345678
0x1234ABCD
0x1234FF00
```

???

`0x12345678`, `0x1234ABCD`, `0x1234FF00`. `as01_adim1` içinde `mov eax, 0x12345678` 32-bit bir yazma olduğu için `rax`'in üst 32 bitindeki `0xAABBCCDD` otomatik sıfırlanır ve `0x12345678` döner. `as01_adim2` içinde `mov ax, 0xABCD` 16-bitlik bir yazmadır; üst bitlere dokunmaz, yalnızca alt 16 biti (`0x5678`) değiştirip `0x1234ABCD` yapar. `as01_adim3` içinde `mov ah, 0xFF` `[15:8]` bitlerini (`0xAB` -> `0xFF`), `mov al, 0x00` ise `[7:0]` bitlerini (`0xCD` -> `0x00`) günceller ve `0x1234FF00` üretir.
:::

::: gorev 64-bit yazmacı alt dilimlerine ayırmak
Verilen 64-bit işaretsiz tam sayı `rax` değerinden sırasıyla `(eax, ax, ah, al)` alt yazmaçlarının sayısal değerlerini (işaretsiz tam sayı dörtlüsü olarak) döndüren `yazmac_dilimle(rax)` fonksiyonunu Python'da yaz.

```starter
def yazmac_dilimle(rax):
    return (rax, rax, 0, 0)
```

```test
need("yazmac_dilimle")
eq(yazmac_dilimle(0xAABBCCDDEEFF1122), (0xEEFF1122, 0x1122, 0x11, 0x22), "0xAABBCCDDEEFF1122 dilimleri")
eq(yazmac_dilimle(0x0000000100000000), (0, 0, 0, 0), "yalnızca 32. bit 1 iken alt 32-bit dilimlerin hepsi 0 olmalı")
eq(yazmac_dilimle(0xFFFFFFFF), (0xFFFFFFFF, 0xFFFF, 0xFF, 0xFF), "alt 32 bit tamamen 1 iken sınır değerleri")
eq(yazmac_dilimle(0x0000FF00), (0xFF00, 0xFF00, 0xFF, 0x00), "yalnızca ah (bits 15..8) dolu iken al=0, ah=255")
eq(yazmac_dilimle(0x000000FF), (0xFF, 0xFF, 0x00, 0xFF), "yalnızca al (bits 7..0) dolu iken ah=0, al=255")
```

```solution
def yazmac_dilimle(rax):
    eax = rax & 0xFFFFFFFF
    ax = rax & 0xFFFF
    ah = (rax >> 8) & 0xFF
    al = rax & 0xFF
    return (eax, ax, ah, al)
```

```hint
Bit maskeleri ve sağa kaydırma kullan: `eax = rax & 0xFFFFFFFF`, `ax = rax & 0xFFFF`, `ah = (rax >> 8) & 0xFF`, `al = rax & 0xFF`.
```
:::

::: gorev Alt yazmaca `mov` yazmasını simüle etmek
Mevcut 64-bit `rax` değeri üzerine `hedef` (`"rax"`, `"eax"`, `"ax"`, `"ah"` veya `"al"`) yazmacına `deger` yazıldığında oluşan yeni 64-bit `rax` değerini döndüren `mov_uygula(rax, hedef, deger)` fonksiyonunu kur:
- `"rax"`: 64-bit (`deger & 0xFFFFFFFFFFFFFFFF`) yazar.
- `"eax"`: 32-bit (`deger & 0xFFFFFFFF`) yazar ve **üst 32 biti sıfırlar**.
- `"ax"`: yalnızca alt 16 biti (`[15:0]`) günceller; üst 48 bit korunur.
- `"ah"`: yalnızca `[15:8]` arasındaki 8 biti günceller; diğer tüm bitler korunur.
- `"al"`: yalnızca `[7:0]` arasındaki 8 biti günceller; diğer tüm bitler korunur.
- Geçersiz bir `hedef` verilirse `ValueError` fırlat.

```starter
def mov_uygula(rax, hedef, deger):
    return deger
```

```test
need("mov_uygula")
baslangic = 0xFEDCBA9876543210
eq(mov_uygula(baslangic, "rax", 0x1111222233334444), 0x1111222233334444, "rax tüm 64 biti değiştirmeli")
eq(mov_uygula(baslangic, "eax", 0x12345678), 0x0000000012345678, "eax üst 32 biti sıfırlamalı!")
eq(mov_uygula(baslangic, "eax", 0), 0, "mov eax, 0 tüm 64-bit rax'i sıfırlamalı")
eq(mov_uygula(baslangic, "ax", 0xAAAA), 0xFEDCBA987654AAAA, "ax yalnızca alt 16 biti değiştirmeli, üst 48 bit korunmalı")
eq(mov_uygula(baslangic, "al", 0xFF), 0xFEDCBA98765432FF, "al yalnızca [7:0] bitlerini değiştirmeli")
eq(mov_uygula(baslangic, "ah", 0x99), 0xFEDCBA9876549910, "ah yalnızca [15:8] bitlerini değiştirmeli, al (0x10) korunmalı")
eq(mov_uygula(baslangic, "al", 0x1FF), 0xFEDCBA98765432FF, "deger fazladan bit taşısa bile hedef genişliğiyle maskelenmeli")
raises(ValueError, lambda: mov_uygula(0, "ebx", 1), msg="bilinmeyen hedef yazmaç için ValueError")
```

```solution
def mov_uygula(rax, hedef, deger):
    rax &= 0xFFFFFFFFFFFFFFFF
    if hedef == "rax":
        return deger & 0xFFFFFFFFFFFFFFFF
    if hedef == "eax":
        return deger & 0xFFFFFFFF
    if hedef == "ax":
        return (rax & ~0xFFFF) | (deger & 0xFFFF)
    if hedef == "ah":
        return (rax & ~0xFF00) | ((deger & 0xFF) << 8)
    if hedef == "al":
        return (rax & ~0xFF) | (deger & 0xFF)
    raise ValueError(f"Geçersiz hedef: {hedef}")
```

```hint
Parçalı güncelleme için önce eski bitleri `rax & ~maske` ile temizle, ardından yeni değeri `|` (VEYA) ile yerleştir. `"eax"` durumunda üst bitleri koruma, doğrudan `deger & 0xFFFFFFFF` döndür.
```
:::
