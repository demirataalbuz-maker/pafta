---
id: as09
title: C Fonksiyonlarının Disassembly Kalıplarını Okumak
rank: basalti
order: 9
summary: Derleyicinin kısa devre (&&, ||), erken çıkış (guard clause), switch-case ve setcc/cmovcc optimizasyonlarıyla ürettiği gerçek disassembly çıktısını okumak.
---

::: anlat
Bir C fonksiyonu `-O1` veya `-O2` ile derlendiğinde derleyici kaynak koddaki `if / else if / else` sırasını birebir korumak zorunda değildir. Aynı matematiksel sonucu daha az dallanmayla üreten kalıplar seçer.

### Gerçek Bir C Fonksiyonu ve `clang -O1` Disassembly Çıktısı

Aşağıdaki yetkilendirme ve puan değerlendirme fonksiyonunu ve `clang -O1` + `llvm-objdump -d -M intel` çıktısını satır satır karşılaştıralım:

```c
// Windows x64: ecx = rol, edx = puan, r8d = aktif
int istek_degerlendir(int rol, int puan, int aktif) {
    if (!aktif) {
        return -1;
    }
    if (rol == 1 && puan >= 80) {
        return puan + 20;
    }
    if (rol == 2 || puan >= 50) {
        return puan + 5;
    }
    return 0;
}
```

```asm
0000000000000000 <istek_degerlendir>:
   0: 45 85 c0              test   r8d, r8d         #! aktif == 0 mı? (3. argüman: r8d)
   3: 74 18                 je     0x1d             #! aktif == 0 ise 0x1d adresine sıçra (-1 döndür)
   5: 89 d0                 mov    eax, edx         #! eax = puan (2. argüman: edx)
   7: 83 f9 01              cmp    ecx, 0x1         #! rol (ecx) ile 1'i karşılaştır
   a: 0f 95 c2              setne  dl               #! dl = (rol != 1) ? 1 : 0
   d: 83 f8 50              cmp    eax, 0x50        #! puan (eax) ile 80 (0x50) karşılaştır
  10: 41 0f 9c c0           setl   r8b              #! r8b = (puan < 80) ? 1 : 0
  14: 41 08 d0              or     r8b, dl          #! r8b = (rol != 1) | (puan < 80)  [De Morgan!]
  17: 75 0a                 jne    0x23             #! En az biri doğruysa (yani !(rol==1 && puan>=80)) 0x23'e sıçra
  19: 83 c0 14              add    eax, 0x14        #! İkisi de sağlandı: eax = puan + 20 (0x14)
  1c: c3                    ret                     #! puan + 20 döndür
  1d: b8 ff ff ff ff        mov    eax, 0xffffffff  #! eax = -1 (0xFFFFFFFF)
  22: c3                    ret                     #! -1 döndür
  23: 8d 50 05              lea    edx, [rax + 0x5] #! edx = puan + 5 (aday sonuç)
  26: 45 31 c0              xor    r8d, r8d         #! r8d = 0 (varsayılan dönüş değeri)
  29: 83 f8 32              cmp    eax, 0x32        #! puan ile 50 (0x32) karşılaştır
  2c: 44 0f 4d c2           cmovge r8d, edx         #! puan >= 50 ise r8d = puan + 5
  30: 83 f9 02              cmp    ecx, 0x2         #! rol ile 2 karşılaştır
  33: 44 0f 44 c2           cmove  r8d, edx         #! rol == 2 ise r8d = puan + 5
  37: 44 89 c0              mov    eax, r8d         #! eax = r8d
  3a: c3                    ret                     #! Sonucu döndür
```

### Bu Disassembly'de Hangi Kalıplar Var?

| Adres Aralığı | Derleyici Kalıbı | Açıklama |
|---|---|---|
| `0x00 .. 0x03` ve `0x1d` | **Guard Clause (Erken Çıkış)** | `test r8d, r8d` → `je 0x1d` ile `!aktif` durumu fonksiyonun sonundaki soğuk bloğa (`mov eax, 0xffffffff; ret`) atılır. |
| `0x07 .. 0x17` | **De Morgan ile Birleşik `&&`** | `rol == 1 && puan >= 80` koşulunu iki ayrı `jne`/`jl` sıçraması yerine `setne dl` (`rol != 1`) ve `setl r8b` (`puan < 80`) üretip `or r8b, dl` → `jne 0x23` ile **tek sıçramaya** indirger. |
| `0x23 .. 0x3a` | **`lea` + `cmovcc` ile Dallanmasız `\|\|`** | `rol == 2 \|\| puan >= 50` için hiç sıçrama (`jcc`) kullanmaz! `edx = puan + 5` ve `r8d = 0` hazırlar; `cmovge` ve `cmove` ile koşullardan herhangi biri tutarsa `r8d = edx` yapar. |

> [!İPUCU]
> Disassembly'de `0xffffffff` sabitinin `eax`'e yüklendiğini (`mov eax, 0xffffffff`) gördüğünüzde, dönüş tipi işaretli `int` ise bunun **`-1`** hata kodu olduğunu hemen hatırlayın (`0xfffffffe` → `-2`, `0xfffffffd` → `-3`).
:::

::: tahmin
```asm
; clang -O1 çıktısı (Windows x64: ecx = rol, edx = puan, r8d = aktif)
0000000000000000 <istek_degerlendir>:
       0: 45 85 c0                      test    r8d, r8d
       3: 74 18                         je      0x1d <istek_degerlendir+0x1d>
       5: 89 d0                         mov     eax, edx
       7: 83 f9 01                      cmp     ecx, 0x1
       a: 0f 95 c2                      setne   dl
       d: 83 f8 50                      cmp     eax, 0x50
      10: 41 0f 9c c0                   setl    r8b
      14: 41 08 d0                      or      r8b, dl
      17: 75 0a                         jne     0x23 <istek_degerlendir+0x23>
      19: 83 c0 14                      add     eax, 0x14
      1c: c3                            ret
      1d: b8 ff ff ff ff                mov     eax, 0xffffffff
      22: c3                            ret
      23: 8d 50 05                      lea     edx, [rax + 0x5]
      26: 45 31 c0                      xor     r8d, r8d
      29: 83 f8 32                      cmp     eax, 0x32
      2c: 44 0f 4d c2                   cmovge  r8d, edx
      30: 83 f9 02                      cmp     ecx, 0x2
      33: 44 0f 44 c2                   cmove   r8d, edx
      37: 44 89 c0                      mov     eax, r8d
      3a: c3                            ret

; Çağrılar:
; 1) istek_degerlendir(1, 85, 0)
; 2) istek_degerlendir(1, 85, 1)
; 3) istek_degerlendir(1, 60, 1)
; 4) istek_degerlendir(3, 40, 1)
```

Yukarıdaki `istek_degerlendir` fonksiyonu 4 farklı argüman üçlüsüyle çağrıldığında dönen dört satırlık çıktı nedir?

```gercek
-1
105
65
0
```

???
1. çağrı `(1, 85, 0)`: `r8d = 0` olduğu için `test r8d, r8d` → `je 0x1d` sıçrar ve `0xffffffff` (32-bit işaretli `-1`) döner.
2. çağrı `(1, 85, 1)`: `r8d = 1` (aktif), `ecx = 1` (`dl = 0`), `eax = 85 >= 0x50 (80)` (`r8b = 0`). `or r8b, dl` sonucu `0` olduğundan `jne 0x23` sıçramaz; `add eax, 0x14` (`85 + 20`) ile `105` döner.
3. çağrı `(1, 60, 1)`: `eax = 60 < 0x50 (80)` olduğu için `r8b = 1` olur ve `0x23` adresine sıçrar. `edx = 60 + 5 = 65`, `r8d = 0`. `cmp eax, 0x32 (50)` kontrolünde `60 >= 50` olduğu için `cmovge r8d, edx` çalışır ve `65` döner.
4. çağrı `(3, 40, 1)`: `0x23` bloğuna sıçrar; `40 < 50` olduğu için `cmovge` çalışmaz, `ecx = 3 != 2` olduğu için `cmove` de çalışmaz; `r8d` sıfır kalır ve `0` döner.
:::

::: gorev `istek_degerlendir` disassembly mantığını Python'da kurmak
Yukarıdaki `istek_degerlendir(rol, puan, aktif)` disassembly çıktısının yaptığı hesabı birebir uygulayan Python fonksiyonunu yaz (`aktif == 0` ise `-1`, `rol == 1` ve `puan >= 80` ise `puan + 20`, `rol == 2` veya `puan >= 50` ise `puan + 5`, aksi halde `0`).

```starter
def istek_degerlendir(rol, puan, aktif):
    return 0
```

```test
need("istek_degerlendir")
eq(istek_degerlendir(1, 85, 0), -1, "aktif=0 iken erken çıkışla -1 dönmeli")
eq(istek_degerlendir(2, 100, 0), -1, "aktif=0 iken rol=2 olsa bile -1 dönmeli")
eq(istek_degerlendir(1, 80, 1), 100, "rol=1 ve puan=80 sınırında puan + 20 = 100")
eq(istek_degerlendir(1, 79, 1), 84, "rol=1 ve puan=79 iken ikinci dala düşüp puan + 5 = 84")
eq(istek_degerlendir(2, 80, 1), 85, "rol=2 ve puan=80 iken puan + 5 = 85")
eq(istek_degerlendir(2, 10, 1), 15, "rol=2 iken puan < 50 olsa bile puan + 5 = 15")
eq(istek_degerlendir(3, 50, 1), 55, "rol=3 ve puan=50 sınırında puan + 5 = 55")
eq(istek_degerlendir(3, 49, 1), 0, "rol=3 ve puan=49 sınırında 0")
eq(istek_degerlendir(1, 49, -5), 0, "aktif != 0 (ör. -5) aktif sayılır")
```

```solution
def istek_degerlendir(rol, puan, aktif):
    if aktif == 0:
        return -1
    if rol == 1 and puan >= 80:
        return puan + 20
    if rol == 2 or puan >= 50:
        return puan + 5
    return 0
```

```hint
Önce `aktif == 0` kontrolüyle `-1` döndür, ardından sırasıyla `rol == 1 and puan >= 80` ve `rol == 2 or puan >= 50` koşullarını uygula.
```
:::

::: gorev Dallanmasız `cmovcc` koşullu atama simülatörü
Disassembly'de sıkça karşılaşılan `cmp <sol>, <sag>` + `cmov<kosul> <hedef>, <kaynak>` dallanmasız atama kalıbını simüle eden `cmov_uygula(komut, cmp_sol, cmp_sag, hedef_deger, kaynak_deger)` fonksiyonunu yaz:
- `cmp_sol` ve `cmp_sag` 32-bit değerlerdir (işaretli ve işaretsiz yorumlarını 32-bit olarak hesapla).
- Desteklenecek `komut` değerleri (büyük/küçük harf duyarsız):
  - `"cmove"` / `"cmovz"`: eşitse `kaynak_deger`, değilse `hedef_deger`
  - `"cmovne"` / `"cmovnz"`: eşit değilse `kaynak_deger`, değilse `hedef_deger`
  - İşaretli: `"cmovg"`, `"cmovge"`, `"cmovl"`, `"cmovle"`
  - İşaretsiz: `"cmova"`, `"cmovae"`, `"cmovb"`, `"cmovbe"`
- Tanınmayan komut verilirse `ValueError` fırlat.

```starter
def cmov_uygula(komut, cmp_sol, cmp_sag, hedef_deger, kaynak_deger):
    return hedef_deger
```

```test
need("cmov_uygula")
eq(cmov_uygula("cmovge", 50, 50, 0, 55), 55, "cmovge 50 >= 50 doğru -> kaynak (55)")
eq(cmov_uygula("cmovge", 49, 50, 0, 54), 0, "cmovge 49 >= 50 yanlış -> hedef (0)")
eq(cmov_uygula("cmovg", 50, 50, 0, 55), 0, "cmovg 50 > 50 yanlış -> hedef (0)")
eq(cmov_uygula("cmovg", 51, 50, 0, 55), 55, "cmovg 51 > 50 doğru -> kaynak (55)")
eq(cmov_uygula("cmove", 2, 2, 0, 45), 45, "cmove eşitlikte kaynak (45)")
eq(cmov_uygula("cmovz", 2, 2, 0, 45), 45, "cmovz eşitlikte kaynak (45)")
eq(cmov_uygula("cmovz", 2, 3, 0, 45), 0, "cmovz eşit değilse hedef (0)")
eq(cmov_uygula("cmovne", 2, 2, 0, 45), 0, "cmovne eşitlikte hedef (0)")
eq(cmov_uygula("cmovnz", 2, 3, 0, 45), 45, "cmovnz eşit değilse kaynak (45)")
eq(cmov_uygula("cmovnz", 2, 2, 0, 45), 0, "cmovnz eşitlikte hedef (0)")
eq(cmov_uygula("cmovl", -1, 5, 10, 99), 99, "cmovl işaretli -1 < 5 doğru -> 99")
eq(cmov_uygula("cmovl", 5, 5, 10, 99), 10, "cmovl eşitlikte yanlış -> 10")
eq(cmov_uygula("cmovl", 0x80000000, 0, 10, 99), 99, "cmovl 0x80000000 (-2147483648) < 0 doğru -> 99")
eq(cmov_uygula("cmovle", -5, -5, 10, 99), 99, "cmovle eşitlikte doğru -> 99")
eq(cmov_uygula("cmovle", -6, -5, 10, 99), 99, "cmovle -6 <= -5 doğru -> 99")
eq(cmov_uygula("cmovle", -4, -5, 10, 99), 10, "cmovle -4 <= -5 yanlış -> 10")
eq(cmov_uygula("cmovb", 0xFFFFFFFF, 5, 10, 99), 10, "cmovb işaretsiz 0xFFFFFFFF < 5 yanlış -> 10")
eq(cmov_uygula("cmovb", 5, 5, 10, 99), 10, "cmovb eşitlikte yanlış -> 10")
eq(cmov_uygula("cmovb", 4, 5, 10, 99), 99, "cmovb 4 < 5 doğru -> 99")
eq(cmov_uygula("cmova", 0xFFFFFFFF, 5, 10, 99), 99, "cmova işaretsiz 0xFFFFFFFF > 5 doğru -> 99")
eq(cmov_uygula("cmova", 5, 5, 10, 99), 10, "cmova eşitlikte yanlış -> 10")
eq(cmov_uygula("cmovae", 5, 5, 10, 99), 99, "cmovae eşitlikte doğru -> 99")
eq(cmov_uygula("cmovae", 6, 5, 10, 99), 99, "cmovae 6 >= 5 doğru -> 99")
eq(cmov_uygula("cmovae", 4, 5, 10, 99), 10, "cmovae 4 >= 5 yanlış -> 10")
eq(cmov_uygula("cmovbe", 5, 5, 10, 99), 99, "cmovbe eşitlikte doğru -> 99")
eq(cmov_uygula("cmovbe", 4, 5, 10, 99), 99, "cmovbe 4 <= 5 doğru -> 99")
eq(cmov_uygula("cmovbe", 6, 5, 10, 99), 10, "cmovbe 6 <= 5 yanlış -> 10")
raises(ValueError, lambda: cmov_uygula("cmovxx", 1, 2, 3, 4), msg="bilinmeyen cmov komutu için ValueError")
```

```solution
def _s32(x):
    u = x & 0xFFFFFFFF
    return u - 0x100000000 if u >= 0x80000000 else u


def cmov_uygula(komut, cmp_sol, cmp_sag, hedef_deger, kaynak_deger):
    k = komut.strip().lower()
    ua = cmp_sol & 0xFFFFFFFF
    ub = cmp_sag & 0xFFFFFFFF
    sa = _s32(cmp_sol)
    sb = _s32(cmp_sag)

    tablo = {
        "cmove": ua == ub,
        "cmovz": ua == ub,
        "cmovne": ua != ub,
        "cmovnz": ua != ub,
        "cmovg": sa > sb,
        "cmovge": sa >= sb,
        "cmovl": sa < sb,
        "cmovle": sa <= sb,
        "cmova": ua > ub,
        "cmovae": ua >= ub,
        "cmovb": ua < ub,
        "cmovbe": ua <= ub,
    }
    if k not in tablo:
        raise ValueError(f"Bilinmeyen cmov komutu: {komut}")
    return kaynak_deger if tablo[k] else hedef_deger
```

```hint
Koşul doğruysa `kaynak_deger`, yanlışsa `hedef_deger` döndür; `g/ge/l/le` için işaretli, `a/ae/b/be` için işaretsiz 32-bit karşılaştırma yap.
```
:::
