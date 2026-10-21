---
id: as04
title: RFLAGS Bayrakları, cmp ve test
summary: ZF, SF, CF ve OF durum bayrakları, çıkarma yapıp sonucu atarak bayrak kuran cmp komutu, bit düzeyinde VE yapıp bayrak kuran test komutu ve setcc koşullu bayt komutları.
---

::: anlat `RFLAGS` içindeki dört temel durum bayrağı
x86-64 işlemcisinde koşullar doğrudan `if (a < b)` diye tek adımda çalışmaz: önce bir aritmetik/mantık komutu **`RFLAGS`** yazmacındaki 1-bitlik durum bayraklarını günceller, hemen ardından gelen koşullu komut (`je`, `jl`, `jb`, `setz`, `cmovg` vb.) bu bayraklara bakar.

Disassembly okurken bilmen gereken dört ana durum bayrağı şunlardır:

| Bayrak | Tam adı | Ne zaman `1` olur? | Hangi dünyada kullanılır? |
|---|---|---|---|
| **ZF** | *Zero Flag* (Sıfır) | İşlemin sonucu **tam `0`** olduğunda | Eşitlik (`==`, `!=`) ve sıfır kontrolü |
| **SF** | *Sign Flag* (İşaret) | Sonucun en üst biti (**MSB**) **`1`** olduğunda (negatif görünüm) | İşaretli (*signed*) karşılaştırma |
| **CF** | *Carry Flag* (Elde/Borç) | **İşaretsiz** toplama/çıkarmada bit genişliğinden taşma veya **borç** oluştuğunda (`a < b` işaretsiz) | İşaretsiz (*unsigned*) aritmetik ve karşılaştırma |
| **OF** | *Overflow Flag* (Taşma) | **İşaretli** aritmetikte sonuç işaret sınırını aştığında (ör. iki pozitifin toplamı negatif göründüğünde) | İşaretli (*signed*) taşma ve karşılaştırma (`SF != OF`) |

```asm
mov al, 0xFF                  #! işaretsiz 255, işaretli -1
add al, 1                     #! sonuç 8-bitte 0x00 -> ZF=1, SF=0, CF=1 (255+1 taştı), OF=0 (-1+1=0 taşmadı!)

mov bl, 0x7F                  #! işaretli +127 (8-bit tavanı)
add bl, 1                     #! sonuç 0x80 (-128) -> ZF=0, SF=1, CF=0 (127+1=128 taşmadı), OF=1 (+127+1 işaretli taştı!)
```

> [!DERİN]
> **CF ile OF'u birbirine karıştırma!** İşlemci toplama ve çıkarmada sayının `signed` mı `unsigned` mı olduğunu bilmez; ikinin tümleyeni aritmetiği her ikisi için de aynı bitleri üretir. İşlemci aynı anda **işaretsiz taşmayı `CF`'ye**, **işaretli taşmayı `OF`'a** yazar; hangi bayrağa bakacağına sonraki komut karar verir!
:::

::: anlat Sonucu yazmadan bayrak kurmak: `cmp` ve `test`
Bir karşılaştırma yaparken yazmaçtaki veriyi bozmak istemeyiz. Bunun için iki özel komut vardır:

1. **`cmp a, b` (*Compare*):** Arka planda **`a - b`** çıkarma işlemini yapar, **`RFLAGS` bayraklarını günceller**, ancak çıkan sonucu hiçbir yere yazmaz (`a` değişmez):
   - `a == b` ise `a - b == 0` → **`ZF = 1`**
   - İşaretsiz `a < b` ise çıkarmada borç (*borrow*) gerekir → **`CF = 1`**
   - İşaretli `a < b` ise → **`SF != OF`**
2. **`test a, b` (*Logical Compare*):** Arka planda **`a & b`** (bit düzeyinde VE) yapar, **`CF = 0`, `OF = 0`** sıfırlar ve sonuca göre **`ZF`** ile **`SF`** bayraklarını günceller:
   - **`test eax, eax`:** Derleyicilerin bir yazmacın **`0` olup olmadığını** (`je`/`jne`) veya **negatif olup olmadığını** (`js`/`jns`) kontrol etmek için `cmp eax, 0` yerine kullandığı standart kalıptır (daha kısa makine kodu üretir).
   - **`test cl, 0x08`:** `cl` yazmacının 3. bitinin (`8` değerli bit) açık olup olmadığını yoklar (`ZF = 0` ise bit açıktır).

Bayrak sonucunu doğrudan `0` veya `1` olarak bir 8-bit yazmaca yazmak için **`setcc`** ailesi kullanılır:
- `sete al` / `setz al`: `ZF == 1` ise `al = 1`, değilse `0`
- `setne al` / `setnz al`: `ZF == 0` ise `al = 1`, değilse `0`
- `setb al` (*below* — işaretsiz `<`): `CF == 1` ise `al = 1`
- `setl al` (*less* — işaretli `<`): `SF != OF` ise `al = 1`

```asm
xor eax, eax                  #! eax = 0
test cl, 0x08                 #! cl & 0x08 hesapla; 3. bit 1 ise sonuç != 0 (ZF=0)
setnz al                      #! ZF=0 ise al = 1, değilse al = 0
```
:::

::: tahmin
Aşağıdaki üç x86-64 fonksiyonu sırasıyla `as04_test_bit(0x2C)`, `as04_cmp_u(0xFFFFFFFF, 5)` ve `as04_cmp_s(0xFFFFFFFF, 5)` argümanlarıyla çağrılıyor (`ecx` birinci, `edx` ikinci argüman). Her birinin döndürdüğü `eax` değeri nedir?

```asm
as04_test_bit:
    xor eax, eax
    test cl, 0x08
    setnz al
    ret

as04_cmp_u:
    xor eax, eax
    cmp ecx, edx
    setb al
    ret

as04_cmp_s:
    xor eax, eax
    cmp ecx, edx
    setl al
    ret
```

```gercek
1
0
1
```

???

`1`, `0`, `1`. `0x2C` sayısı ikilik tabanda `0010_1100` (`32 + 8 + 4`) olduğu için `0x2C & 0x08 = 0x08 != 0` çıkar, `ZF = 0` olur ve `setnz al` komutu `al = 1` yazar. İkinci ve üçüncü fonksiyonda `ecx = 0xFFFFFFFF` ve `edx = 5` karşılaştırılır: `setb` (*below*) **işaretsiz** bakar; işaretsiz dünyada `4294967295 < 5` yanlıştır (`CF = 0`), bu yüzden `0` döner. `setl` (*less*) ise **işaretli** bakar; işaretli dünyada `0xFFFFFFFF` sayısı `-1`'dir ve `-1 < 5` doğrudur (`SF != OF`), bu yüzden `1` döner!
:::

::: gorev 8-bit `cmp al, bl` bayrak simülatörü
8-bitlik (`0 .. 255`) iki değer üzerinde `cmp al, bl` (`al - bl`) çalıştığında oluşan dört temel bayrağı `{"ZF": int, "SF": int, "CF": int, "OF": int}` sözlüğü olarak (her bayrak `0` veya `1`) döndüren `cmp_bayraklari(al, bl)` fonksiyonunu yaz.

```starter
def cmp_bayraklari(al, bl):
    fark = (al - bl) & 0xFF
    return {"ZF": int(fark == 0), "SF": 0, "CF": 0, "OF": 0}
```

```test
need("cmp_bayraklari")
eq(cmp_bayraklari(10, 10), {"ZF": 1, "SF": 0, "CF": 0, "OF": 0}, "10 == 10: yalnızca ZF=1")
eq(cmp_bayraklari(15, 10), {"ZF": 0, "SF": 0, "CF": 0, "OF": 0}, "15 > 10: tüm bayraklar 0")
eq(cmp_bayraklari(5, 10), {"ZF": 0, "SF": 1, "CF": 1, "OF": 0}, "5 - 10 = -5 (0xFB): SF=1 ve işaretsiz borç CF=1, OF=0")
eq(cmp_bayraklari(0x80, 1), {"ZF": 0, "SF": 0, "CF": 0, "OF": 1}, "-128 (0x80) - 1 = 0x7F (+127): işaretli taşma OF=1, SF=0, CF=0!")
eq(cmp_bayraklari(0x7F, 0xFF), {"ZF": 0, "SF": 1, "CF": 1, "OF": 1}, "+127 (0x7F) - (-1 / 0xFF) = 0x80: hem CF=1 (127 < 255) hem OF=1 (+127 - (-1) = +128 taştı) hem SF=1!")
eq(cmp_bayraklari(0, 1), {"ZF": 0, "SF": 1, "CF": 1, "OF": 0}, "0 - 1 = 0xFF: ZF=0, SF=1, CF=1, OF=0")
eq(cmp_bayraklari(0xF0, 5), {"ZF": 0, "SF": 1, "CF": 0, "OF": 0}, "-16 (0xF0) - 5 = -21 (0xEB): işaretli taşma yok (OF=0), CF=0")
eq(cmp_bayraklari(10, 0xFE), {"ZF": 0, "SF": 0, "CF": 1, "OF": 0}, "10 - (-2 / 0xFE) = +12: işaretli taşma yok (OF=0), işaretsiz borç CF=1")
eq(cmp_bayraklari(0x80, 0), {"ZF": 0, "SF": 1, "CF": 0, "OF": 0}, "-128 (0x80) - 0 = -128: alt sınırda işaretli taşma yok (OF=0)")
eq(cmp_bayraklari(0xFF, 0x7F), {"ZF": 0, "SF": 1, "CF": 0, "OF": 0}, "-1 (0xFF) - 127 (0x7F) = -128: alt sınırda işaretli taşma yok (OF=0)")
eq(cmp_bayraklari(0x7F, 0), {"ZF": 0, "SF": 0, "CF": 0, "OF": 0}, "+127 (0x7F) - 0 = +127: üst sınırda işaretli taşma yok (hepsi 0)")
eq(cmp_bayraklari(0xFF, 0x80), {"ZF": 0, "SF": 0, "CF": 0, "OF": 0}, "-1 (0xFF) - (-128 / 0x80) = +127: üst sınırda işaretli taşma yok (OF=0)")
eq(cmp_bayraklari(0x7E, 0xFF), {"ZF": 0, "SF": 0, "CF": 1, "OF": 0}, "+126 (0x7E) - (-1 / 0xFF) = +127: üst sınırda OF=0, CF=1")
```

```solution
def cmp_bayraklari(al, bl):
    a = al & 0xFF
    b = bl & 0xFF
    sonuc = (a - b) & 0xFF
    zf = 1 if sonuc == 0 else 0
    sf = 1 if (sonuc & 0x80) else 0
    cf = 1 if a < b else 0
    sa = a - 256 if (a & 0x80) else a
    sb = b - 256 if (b & 0x80) else b
    of = 1 if not (-128 <= sa - sb <= 127) else 0
    return {"ZF": zf, "SF": sf, "CF": cf, "OF": of}
```

```hint
`sonuc = (a - b) & 0xFF` üzerinden `ZF` (`sonuc == 0`) ve `SF` (`(sonuc & 0x80) != 0`) bulunur. `CF` işaretsiz borçtur (`a < b`). `OF` ise işaretli değerlerin farkı `sa - sb` `[-128, 127]` aralığı dışına çıktığında `1` olur.
```
:::

::: gorev `test eax, edx` komutunun bayrak analizi
32-bit `eax` ve `edx` değerleri üzerinde `test eax, edx` komutu çalıştığında oluşan `(sonuc32, zf, sf)` üçlüsünü döndüren `test_analiz(eax, edx)` fonksiyonunu yaz (`sonuc32` 32-bit işaretsiz `eax & edx` değeri, `zf` ve `sf` ise `0` veya `1`).

```starter
def test_analiz(eax, edx):
    return (eax & edx, 0, 0)
```

```test
need("test_analiz")
eq(test_analiz(0, 0), (0, 1, 0), "test 0, 0 -> sonuc=0, ZF=1, SF=0")
eq(test_analiz(0x2C, 0x08), (0x08, 0, 0), "0x2C & 0x08 = 8 -> ZF=0, SF=0")
eq(test_analiz(0x2C, 0x10), (0, 1, 0), "0x2C & 0x10 = 0 -> ZF=1, SF=0")
eq(test_analiz(0x80000000, 0x80000000), (0x80000000, 0, 1), "en üst bit (bit 31) 1 ise SF=1, ZF=0")
eq(test_analiz(0xFFFFFFFF, 0x7FFFFFFF), (0x7FFFFFFF, 0, 0), "bit 31 maskelenip 0 olunca SF=0 olmalı")
eq(test_analiz(-1, -1), (0xFFFFFFFF, 0, 1), "negatif girdi 32-bit maskelenmeli -> 0xFFFFFFFF, ZF=0, SF=1")
```

```solution
def test_analiz(eax, edx):
    sonuc = (eax & edx) & 0xFFFFFFFF
    zf = 1 if sonuc == 0 else 0
    sf = 1 if (sonuc & 0x80000000) else 0
    return (sonuc, zf, sf)
```

```hint
`sonuc = (eax & edx) & 0xFFFFFFFF` hesapla; `sonuc == 0` ise `zf = 1`, `sonuc & 0x80000000` sıfırdan farklıysa `sf = 1`.
```
:::
