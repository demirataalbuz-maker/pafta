---
id: as05
title: Koşullu Dallanma, Döngüler ve cmov
rank: kucuk-orta
order: 5
summary: İşaretsiz (ja/jb) ve işaretli (jg/jl) sıçrama komutlarını, ileri/geri dallanma ile if/else ve while kalıplarını ve dallanmasız cmovcc komutlarını okumak.
---

::: anlat
İşlemci normalde komutları yukarıdan aşağıya sırayla yürütür ve `rip` (Instruction Pointer) yazmacı her komuttan sonra bir sonrakinin adresine ilerler. Akışı değiştiren komutlar `rip` değerini doğrudan hedef etikete (adrese) yönlendirir.

Disassembly okurken en kritik ayrım, **işaretsiz (unsigned)** sıçramalar ile **işaretli (signed)** sıçramaların farklı İngilizce kelimeler kullanmasıdır:

- **İşaretsiz (`uint32_t`, `size_t`, bellek adresleri):** **Above (`a`)** ve **Below (`b`)** kelimeleri kullanılır (`CF` ve `ZF` bayraklarına bakar).
- **İşaretli (`int32_t`, `long`):** **Greater (`g`)** ve **Less (`l`)** kelimeleri kullanılır (`SF`, `OF` ve `ZF` bayraklarına bakar).

| Komut | Eş Anlamlısı | Anlamı (`cmp A, B` sonrası) | Tür | Bayrak Koşulu |
|---|---|---|---|---|
| `jmp hedef` | — | Koşulsuz sıçra (`goto`) | — | Koşulsuz |
| `je` | `jz` | Eşitse sıçra (`A == B`) | Ortak | `ZF == 1` |
| `jne` | `jnz` | Eşit değilse sıçra (`A != B`) | Ortak | `ZF == 0` |
| `ja` | `jnbe` | Üstündeyse (`A > B`) | İşaretsiz | `CF == 0` ve `ZF == 0` |
| `jae` | `jnb` / `jnc` | Üstünde veya eşitse (`A >= B`) | İşaretsiz | `CF == 0` |
| `jb` | `jnae` / `jc` | Altındaysa (`A < B`) | İşaretsiz | `CF == 1` |
| `jbe` | `jna` | Altında veya eşitse (`A <= B`) | İşaretsiz | `CF == 1` veya `ZF == 1` |
| `jg` | `jnle` | Büyükse (`A > B`) | İşaretli | `ZF == 0` ve `SF == OF` |
| `jge` | `jnl` | Büyük veya eşitse (`A >= B`) | İşaretli | `SF == OF` |
| `jl` | `jnge` | Küçükse (`A < B`) | İşaretli | `SF != OF` |
| `jle` | `jng` | Küçük veya eşitse (`A <= B`) | İşaretli | `ZF == 1` veya `SF != OF` |
| `js` / `jns` | — | Negatifse (`SF==1`) / Pozitif-sıfırsa (`SF==0`) | İşaretli | `SF` |

> [!GÜVENLİK]
> C kodunda uzunluk veya dizin parametresi `int` (işaretli) tanımlanıp üst sınır denetimi `if (uzunluk > MAKS)` ile yapıldığında derleyici `jg` veya `jle` üretir. Saldırgan `-1` (`0xFFFFFFFF`) gönderdiğinde işaretli karşılaştırma `-1 <= MAKS` koşulunu doğru sayar; ancak aynı değer `memcpy` fonksiyonuna `size_t` (işaretsiz) olarak geçtiğinde `4294967295` baytlık dev bir kopyalamaya dönüşür. Güvenli sınır denetimlerinde disassembly'de `ja` / `jbe` (işaretsiz) görülmelidir.

### İleri Sıçrama (`if/else`) ve Geri Sıçrama (`while/for`)

Disassembly çıktısında ok yönü veya hedef adresin mevcut adresten büyük/küçük olması kalıbı hemen ele verir:

- **İleri sıçrama (daha yüksek adrese):** Bir blok atlanıyordur → `if` veya `if/else` yapısı.
- **Geri sıçrama (daha düşük adrese):** Daha önce çalışmış bir etikete dönülüyordur → `while`, `for` veya `do-while` döngüsü.

```asm
; C karşılığı:
; int toplam = 0;
; while (n > 1) { toplam += n; n >>= 1; }
; return toplam;

as05_dongu:
    xor eax, eax        #! toplam = 0 (dönüş değeri yazmacı)
.L_bas:
    cmp ecx, 1          #! n ile 1'i karşılaştır
    jle .L_son          #! İLERİ SIÇRAMA: n <= 1 ise (işaretli) döngüden çık (.L_son)
    add eax, ecx        #! toplam += n
    shr ecx, 1          #! n = n >> 1 (ikiye böl)
    jmp .L_bas          #! GERİ SIÇRAMA: döngü başına (.L_bas) dön
.L_son:
    ret                 #! toplam'ı (eax) döndür
```

### Dallanmasız Koşullu Atama: `cmovcc`

Modern derleyiciler (`-O1`, `-O2`) küçük `if/else` veya üçlü operatör (`koşul ? x : y`) ifadelerinde işlemcinin dallanma tahmincisini (branch predictor) yormamak için `cmovcc` (Conditional Move) kullanır:

```asm
cmp ecx, 100
cmovg ecx, edx          #! Eğer ecx > 100 ise (işaretli) ecx = edx yap; değilse dokunma
```

> [!İPUCU]
> Derleyici `if (x > 10) y = 1;` yazdığınızda assembly'de genellikle **ters koşulla** (`cmp eax, 10` → `jle .L_atla`) kod üretir. Çünkü assembly'de amaç "koşul sağlanmazsa gövdeyi atlamak"tır.
:::

::: tahmin
```asm
; Windows x64: ecx = n (int32)
as05_dongu:
    xor eax, eax
.L_bas:
    cmp ecx, 1
    jle .L_son
    add eax, ecx
    shr ecx, 1
    jmp .L_bas
.L_son:
    ret

; Çağrılar:
; 1) as05_dongu(10)
; 2) as05_dongu(1)
```

Yukarıdaki `as05_dongu` fonksiyonu sırasıyla `10` ve `1` argümanlarıyla çağrıldığında dönen iki satırlık çıktı nedir?

```gercek
17
0
```

???
İlk çağrıda `ecx = 10` ve `eax = 0` ile başlanır:
1. tur: `cmp 10, 1` → `jle` sıçramaz; `eax = 0 + 10 = 10`, `shr ecx, 1` ile `ecx = 5`.
2. tur: `cmp 5, 1` → `jle` sıçramaz; `eax = 10 + 5 = 15`, `shr ecx, 1` ile `ecx = 2`.
3. tur: `cmp 2, 1` → `jle` sıçramaz; `eax = 15 + 2 = 17`, `shr ecx, 1` ile `ecx = 1`.
4. tur: `cmp 1, 1` → `ZF = 1` olduğundan `jle .L_son` sıçrar ve `17` döner.
İkinci çağrıda `ecx = 1` ile girilir; ilk `cmp 1, 1` kontrolünde `jle .L_son` doğrudan sıçradığı için döngü gövdesi hiç çalışmaz ve `0` döner.
:::

::: gorev İşaretsiz (`ja`/`jb`) ve işaretli (`jg`/`jl`) sıçrama karar vericisi
Bir `cmp A, B` komutunun ardından gelen sıçrama komutunun (`komut`) **A** ve **B** tam sayıları için sıçrayıp sıçramayacağını (`True` / `False`) hesaplayan `sicrama_olur_mu(komut, a, b)` fonksiyonunu yaz:
- `a` ve `b` 32-bit değerlerdir; önce işaretsiz karşılıklarını (`ua = a & 0xFFFFFFFF`, `ub = b & 0xFFFFFFFF`) ve işaretli karşılıklarını (`sa = ua - 0x100000000 if ua >= 0x80000000 else ua`, `sb = ...`) hesapla.
- Desteklenecek komutlar (büyük/küçük harf duyarsız):
  - `"jmp"` → her zaman `True`
  - `"je"`, `"jz"` → `ua == ub`
  - `"jne"`, `"jnz"` → `ua != ub`
  - İşaretsiz: `"ja"` (`ua > ub`), `"jae"` (`ua >= ub`), `"jb"` (`ua < ub`), `"jbe"` (`ua <= ub`)
  - İşaretli: `"jg"` (`sa > sb`), `"jge"` (`sa >= sb`), `"jl"` (`sa < sb`), `"jle"` (`sa <= sb`)
- Tanınmayan bir komut verilirse `ValueError` fırlat.

```starter
def sicrama_olur_mu(komut, a, b):
    return False
```

```test
need("sicrama_olur_mu")
eq(sicrama_olur_mu("jmp", 0, 100), True, "jmp her zaman sıçrar")
eq(sicrama_olur_mu("je", 42, 42), True, "je eşitlikte sıçrar")
eq(sicrama_olur_mu("JZ", 42, 43), False, "JZ eşit değilse sıçramaz")
eq(sicrama_olur_mu("jne", 42, 43), True, "jne eşit değilse sıçrar")
eq(sicrama_olur_mu("jnz", 10, 10), False, "jnz eşitlikte sıçramaz")
eq(sicrama_olur_mu("ja", 0xFFFFFFFF, 5), True, "ja işaretsizdir: 0xFFFFFFFF > 5")
eq(sicrama_olur_mu("jb", 0xFFFFFFFF, 5), False, "jb işaretsizdir: 0xFFFFFFFF < 5 yanlış")
eq(sicrama_olur_mu("jg", 0xFFFFFFFF, 5), False, "jg işaretlidir: -1 > 5 yanlış")
eq(sicrama_olur_mu("jl", 0xFFFFFFFF, 5), True, "jl işaretlidir: -1 < 5 doğru")
eq(sicrama_olur_mu("ja", 10, 10), False, "ja eşitlikte sıçramaz")
eq(sicrama_olur_mu("jae", 10, 10), True, "jae eşitlikte sıçrar")
eq(sicrama_olur_mu("jb", 10, 10), False, "jb eşitlikte sıçramaz")
eq(sicrama_olur_mu("jbe", 10, 10), True, "jbe eşitlikte sıçrar")
eq(sicrama_olur_mu("jg", -5, -5), False, "jg eşitlikte sıçramaz")
eq(sicrama_olur_mu("jge", -5, -5), True, "jge eşitlikte sıçrar")
eq(sicrama_olur_mu("jl", -5, -5), False, "jl eşitlikte sıçramaz")
eq(sicrama_olur_mu("jle", -5, -5), True, "jle eşitlikte sıçrar")
eq(sicrama_olur_mu("jg", -2, -10), True, "işaretli -2 > -10")
eq(sicrama_olur_mu("ja", -2, -10), True, "işaretsiz 0xFFFFFFFE > 0xFFFFFFF6")
eq(sicrama_olur_mu("jl", 0x80000000, 0), True, "0x80000000 (-2147483648) < 0 işaretli sınır testi")
eq(sicrama_olur_mu("jae", 12, 10), True, "jae 12 >= 10 doğru")
eq(sicrama_olur_mu("jae", 8, 10), False, "jae 8 >= 10 yanlış")
eq(sicrama_olur_mu("jbe", 8, 10), True, "jbe 8 <= 10 doğru")
eq(sicrama_olur_mu("jbe", 12, 10), False, "jbe 12 <= 10 yanlış")
eq(sicrama_olur_mu("jge", -2, -5), True, "jge -2 >= -5 doğru")
eq(sicrama_olur_mu("jge", -8, -5), False, "jge -8 >= -5 yanlış")
eq(sicrama_olur_mu("jle", -8, -5), True, "jle -8 <= -5 doğru")
eq(sicrama_olur_mu("jle", -2, -5), False, "jle -2 <= -5 yanlış")
raises(ValueError, lambda: sicrama_olur_mu("jxx", 1, 2), msg="bilinmeyen sıçrama komutu için ValueError")
```

```solution
def _signed32(deger):
    u = deger & 0xFFFFFFFF
    return u - 0x100000000 if u >= 0x80000000 else u


def sicrama_olur_mu(komut, a, b):
    k = komut.strip().lower()
    ua = a & 0xFFFFFFFF
    ub = b & 0xFFFFFFFF
    sa = _signed32(a)
    sb = _signed32(b)

    if k == "jmp":
        return True
    if k in ("je", "jz"):
        return ua == ub
    if k in ("jne", "jnz"):
        return ua != ub
    if k == "ja":
        return ua > ub
    if k == "jae":
        return ua >= ub
    if k == "jb":
        return ua < ub
    if k == "jbe":
        return ua <= ub
    if k == "jg":
        return sa > sb
    if k == "jge":
        return sa >= sb
    if k == "jl":
        return sa < sb
    if k == "jle":
        return sa <= sb
    raise ValueError(f"Bilinmeyen sicrama komutu: {komut}")
```

```hint
Önce `ua = a & 0xFFFFFFFF` ve `sa = ua - 0x100000000 if ua >= 0x80000000 else ua` ile hem işaretsiz hem işaretli 32-bit değerleri hazırla; `ja/jae/jb/jbe` için `ua, ub`, `jg/jge/jl/jle` için `sa, sb` karşılaştır.
```
:::

::: gorev Geri sıçramalı (`jmp .L_bas`) döngü izleyici
Yukarıdaki `as05_dongu` kalıbının genelleştirilmiş halini simüle eden `dongu_izle(n, alt_sinir)` fonksiyonunu yaz:
- `toplam = 0`, `adim = 0` ile başlar.
- `n > alt_sinir` (`cmp ecx, alt_sinir` → `jle .L_son` ile çıkış) olduğu sürece her adımda `toplam += n`, `n = n >> 1` ve `adim += 1` yapar.
- Döngü bittiğinde `(toplam, adim)` ikilisini döndürür.

```starter
def dongu_izle(n, alt_sinir):
    return (0, 0)
```

```test
need("dongu_izle")
eq(dongu_izle(10, 1), (17, 3), "10 -> 5 -> 2 -> 1: toplam 17, 3 adım")
eq(dongu_izle(1, 1), (0, 0), "n == alt_sinir iken jle hemen çıkar: (0, 0)")
eq(dongu_izle(0, 1), (0, 0), "n < alt_sinir iken döngüye girmez: (0, 0)")
eq(dongu_izle(16, 0), (31, 5), "16+8+4+2+1 = 31, 5 adım")
eq(dongu_izle(8, 2), (12, 2), "8+4 = 12, 2 adım (n=2 olunca jle çıkar)")
```

```solution
def dongu_izle(n, alt_sinir):
    toplam = 0
    adim = 0
    while n > alt_sinir:
        toplam += n
        n = n >> 1
        adim += 1
    return (toplam, adim)
```

```hint
`while n > alt_sinir:` döngüsü içinde `toplam += n`, `n >>= 1` ve `adim += 1` güncelle.
```
:::
