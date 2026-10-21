---
id: as02
title: Aritmetik, Bit Kaydırma ve lea
summary: add, sub, inc, dec, neg, imul komutları, mantıksal (shl/shr) ve aritmetik (sal/sar) bit kaydırma farkı, lea (Load Effective Address) ile belleğe gitmeden hızlı adres ve çarpma aritmetiği.
---

::: anlat Aritmetik, bit işlemleri ve `shr` ile `sar` farkı
x86-64'te temel aritmetik ve bit komutları hedef yazmacı yerinde günceller:

| Komut | Örnek | Anlamı |
|---|---|---|
| `add hedef, kaynak` | `add eax, ecx` | `eax = eax + ecx` |
| `sub hedef, kaynak` | `sub eax, 10` | `eax = eax - 10` |
| `inc hedef` / `dec hedef` | `inc eax` | `eax = eax + 1` / `eax = eax - 1` |
| `neg hedef` | `neg eax` | `eax = -eax` (ikinin tümleyeni) |
| `imul hedef, kaynak` | `imul eax, edx` | `eax = eax * edx` |
| `imul hedef, kaynak, sabit` | `imul eax, ecx, 10` | `eax = ecx * 10` |
| `and` / `or` / `xor` / `not` | `and eax, 0xFF` | bit düzeyinde VE, VEYA, ÖZEL VEYA, DEĞİL |

Bit kaydırma komutlarında ise **işaretsiz (mantıksal)** ve **işaretli (aritmetik)** sağa kaydırma ayrımı çok kritiktir:
- **`shl reg, n`** (veya `sal`): Sola `n` bit kaydırır (`2^n` ile çarpar), sağdan `0` doldurur.
- **`shr reg, n`** (*Shift Logical Right*): Sağa `n` bit kaydırır, **soldan her zaman `0` doldurur** (`unsigned` bölme).
- **`sar reg, n`** (*Shift Arithmetic Right*): Sağa `n` bit kaydırır, **soldan işaret bitini (MSB) kopyalayarak doldurur** (`signed` negatif sayının işaretini korur!).

```asm
mov eax, -16                  #! 32-bit ikinin tümleyeninde: 0xFFFFFFF0 (işaret biti 1)
sar eax, 2                    #! aritmetik sağa kaydır: soldan 1'ler gelir -> 0xFFFFFFFC (-4)

mov ecx, -16                  #! 0xFFFFFFF0
shr ecx, 2                    #! mantıksal sağa kaydır: soldan 0'lar gelir -> 0x3FFFFFFC (1073741820)
```

> [!TUZAK]
> Disassembly'de bir tam sayı sağa kaydırılırken `shr` görüyorsan derleyici o değişkeni **işaretsiz (`unsigned`)**, `sar` görüyorsan **işaretli (`signed`)** olarak derlemiştir. Bu ipucu, değişken türlerini tersine mühendislikte çözmenin en pratik yollarından biridir.
:::

::: anlat `lea` (Load Effective Address): Belleğe gitmeyen köşeli parantez!
Normalde assembly'de köşeli parantez `[...]` bellekten okuma veya belleğe yazma anlamına gelir (`mov eax, [rcx]` → `rcx` adresindeki veriyi oku). **`lea` (*Load Effective Address*) bu kuralın tek istisnasıdır!**

`lea hedef, [taban + indeks*ölçek + kayma]` komutu köşeli parantez içindeki adresi **hesaplar**, ancak **belleğe hiç dokunmadan** çıkan sayıyı doğrudan `hedef` yazmacına yazar. Ölçek (*scale*) yalnızca **`1`, `2`, `4` veya `8`** olabilir.

Derleyiciler `lea` komutunu hem işaretçi aritmetiği hem de `RFLAGS` bayraklarını bozmadan tek komutta hızlı çarpma-toplama yapmak için çok sık kullanır:

```asm
; C'deki: int y = x * 5 + 10; (rcx = x)
lea eax, [rcx + rcx*4 + 10]   #! eax = rcx + 4*rcx + 10 = 5*rcx + 10 (belleğe erişmez!)

; C'deki: int z = a + b * 2 - 4; (rcx = a, rdx = b)
lea eax, [rcx + rdx*2 - 4]    #! tek komutta üçlü aritmetik!
```

> [!İPUCU]
> Disassembly'de `lea eax, [rcx + rcx*2]` gördüğünde bunu "bellekten bir şey okuyor" diye okuma; doğrudan `eax = rcx * 3` olarak çevir!
:::

::: tahmin
Aşağıdaki iki x86-64 fonksiyonu için sırasıyla `as02_hesap(6, 3)` ve `as02_kaydir(-16)` çağrıları yapılıyor (`rcx`/`ecx` birinci, `rdx`/`edx` ikinci argüman; `eax` dönüş değeri). Çıktı ne olur?

```asm
as02_hesap:
    lea eax, [rcx + rcx*4 + 10]
    shl edx, 2
    sub eax, edx
    ret

as02_kaydir:
    mov eax, ecx
    sar eax, 2
    ret
```

```gercek
28
-4
```

???

`28`, `-4`. `as02_hesap(6, 3)` çağrısında `rcx = 6` ve `rdx = 3` gelir. `lea eax, [rcx + rcx*4 + 10]` komutu belleğe gitmeden `6 + 6*4 + 10 = 40` hesaplar. `shl edx, 2` komutu `3`'ü 2 bit sola kaydırıp (`3 * 4`) `12` yapar; `sub eax, edx` ise `40 - 12 = 28` döndürür. `as02_kaydir(-16)` çağrısında `sar eax, 2` işaret bitini koruyarak sağa 2 bit kaydırır ve `-16 >> 2 = -4` döndürür.
:::

::: gorev `lea` adres ve aritmetik hesaplayıcısı
`lea eax, [taban + indeks * olcek + kayma]` komutunun 32-bit işaretsiz sonucunu (`0 .. 0xFFFFFFFF`) hesaplayan `lea_hesapla(taban, indeks, olcek=1, kayma=0)` fonksiyonunu yaz:
- x86-64 adreslemesinde `olcek` (*scale*) yalnızca `1`, `2`, `4` veya `8` olabilir; başka bir değer verilirse `ValueError` fırlat.
- Sonucu 32-bit (`eax`) sınırına (`& 0xFFFFFFFF`) maskeleyerek döndür.

```starter
def lea_hesapla(taban, indeks, olcek=1, kayma=0):
    return taban + indeks * olcek + kayma
```

```test
need("lea_hesapla")
eq(lea_hesapla(6, 6, 4, 10), 40, "[rcx + rcx*4 + 10] -> 6 + 24 + 10 = 40")
eq(lea_hesapla(100, 5, 1, -20), 85, "ölçek 1 ve negatif kayma (-20) doğru hesaplanmalı")
eq(lea_hesapla(0, 7, 2, 0), 14, "ölçek 2 geçerli olmalı")
eq(lea_hesapla(10, 3, 8, 5), 39, "ölçek 8 geçerli olmalı")
eq(lea_hesapla(0xFFFFFFFF, 1, 1, 0), 0, "32-bit eax taşmasında alt 32 bite (& 0xFFFFFFFF) sarılmalı")
eq(lea_hesapla(0, 0, 1, -1), 0xFFFFFFFF, "negatif sonuç 32-bit işaretsiz değere maskelenmeli")
raises(ValueError, lambda: lea_hesapla(1, 1, 3, 0), msg="ölçek 3 x86'da geçersizdir -> ValueError")
raises(ValueError, lambda: lea_hesapla(1, 1, 0, 0), msg="ölçek 0 geçersizdir -> ValueError")
raises(ValueError, lambda: lea_hesapla(1, 1, 16, 0), msg="ölçek 16 geçersizdir -> ValueError")
```

```solution
def lea_hesapla(taban, indeks, olcek=1, kayma=0):
    if olcek not in (1, 2, 4, 8):
        raise ValueError(f"Geçersiz ölçek: {olcek}")
    return (taban + indeks * olcek + kayma) & 0xFFFFFFFF
```

```hint
Önce `olcek not in (1, 2, 4, 8)` kontrolü yapıp `ValueError` fırlat, ardından toplamı `& 0xFFFFFFFF` ile maskele.
```
:::

::: gorev Mantıksal (`shr`) ve aritmetik (`sar`) sağa kaydırma
Verilen 32-bit tam sayı `deger32` ve kaydırma miktarı `miktar` (`0 <= miktar <= 31`) için `shr eax, miktar` ve `sar eax, miktar` komutlarının üreteceği 32-bit işaretsiz yazmaç değerlerini `(shr_sonuc, sar_sonuc)` ikilisi olarak döndüren `kaydirma_farki(deger32, miktar)` fonksiyonunu yaz.

```starter
def kaydirma_farki(deger32, miktar):
    u = deger32 & 0xFFFFFFFF
    return (u >> miktar, u >> miktar)
```

```test
need("kaydirma_farki")
eq(kaydirma_farki(0xFFFFFFF0, 2), (0x3FFFFFFC, 0xFFFFFFFC), "-16 (0xFFFFFFF0) >> 2: shr soldan 0, sar soldan 1 doldurur")
eq(kaydirma_farki(0x80000000, 1), (0x40000000, 0xC0000000), "en küçük negatif 0x80000000 >> 1 sınır testi")
eq(kaydirma_farki(0x7FFFFFFF, 1), (0x3FFFFFFF, 0x3FFFFFFF), "en büyük pozitif 0x7FFFFFFF (MSB=0) için shr ve sar aynıdır")
eq(kaydirma_farki(0xFFFFFFFF, 31), (1, 0xFFFFFFFF), "-1 değerini 31 bit kaydırınca shr=1, sar=0xFFFFFFFF")
eq(kaydirma_farki(0x80000000, 0), (0x80000000, 0x80000000), "0 bit kaydırma değeri değiştirmemeli")
```

```solution
def kaydirma_farki(deger32, miktar):
    u = deger32 & 0xFFFFFFFF
    shr_sonuc = u >> miktar
    isaretli = u - 0x100000000 if (u & 0x80000000) else u
    sar_sonuc = (isaretli >> miktar) & 0xFFFFFFFF
    return (shr_sonuc, sar_sonuc)
```

```hint
32-bit değeri önce `u = deger32 & 0xFFFFFFFF` yap. `shr` doğrudan `u >> miktar` olur. `sar` için `u & 0x80000000` (en üst bit 1 mi) kontrolüyle Python'daki işaretli karşılığına (`u - 0x100000000`) çevir, `>> miktar` uygula ve tekrar `& 0xFFFFFFFF` ile maskele.
```
:::
