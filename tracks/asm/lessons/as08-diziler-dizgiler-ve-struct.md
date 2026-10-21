---
id: as08
title: Diziler, Dizgiler ve Struct Hizalaması
rank: buyuk-orta
order: 8
summary: Ölçekli indeksleme ([rcx + rax*4]) ile dizi erişimini, null sonlandırmalı (\x00) dizgi taramasını ve struct alan ofsetleri ile hizalama (padding) boşluklarını okumak.
---

::: anlat
Derlenmiş makine kodunda değişken adları, dizi tipleri veya `struct` tanımları kalmaz; geriye yalnızca **taban adres**, **ölçek çarpanı (`1, 2, 4, 8`)** ve **sabit ofset** kalır. Bu üç ipucuna bakarak yüksek seviye veri yapısını tersine mühendislikle yeniden kurabiliriz.

### 1. Dizi İndeksleme: `[taban + dizin*ölçek]`

Bir döngü içinde indeks yazmacı (`rax`, `rcx` vb.) her turda `1` artıyor (`inc rax`) ve bellek erişiminde `ölçek` ile çarpılıyorsa bu bir **dizi (array)** erişimidir:

| Bellek İfadesi | Ölçek | Eleman Boyutu | C Karşılığı |
|---|---|---|---|
| `BYTE PTR [rcx + rax]` | `1` | 1 bayt | `uint8_t dizi[];` veya `char s[];` → `dizi[i]` |
| `WORD PTR [rcx + rax*2]` | `2` | 2 bayt | `uint16_t dizi[];` → `dizi[i]` |
| `DWORD PTR [rcx + rax*4]` | `4` | 4 bayt | `int32_t dizi[];` → `dizi[i]` |
| `QWORD PTR [rcx + rax*8]` | `8` | 8 bayt | `uint64_t dizi[];` veya `void *dizi[];` → `dizi[i]` |

### 2. Null Sonlandırmalı (`\x00`) C Dizgileri

C dizgileri (`char *`) uzunluk bilgisi taşımaz; bellekte `0x00` baytına (`'\0'`) rastlanana kadar bayt bayt okunur:

```asm
; size_t as08_uzunluk(const char *s) -> rcx = s
as08_uzunluk:
    xor eax, eax                    #! i = 0 (hem indeks hem dönüş değeri)
.L_str:
    movzx edx, BYTE PTR [rcx + rax] #! dl = s[i] (1 bayt oku ve sıfırla genişlet)
    test dl, dl                     #! s[i] == '\0' (0x00) mı?
    je .L_str_son                   #! Sıfırsa dizgi bitti, döngüden çık
    inc eax                         #! i++
    jmp .L_str                      #! Sonraki karaktere geç
.L_str_son:
    ret                             #! Uzunluğu (eax) döndür
```

### 3. `struct` Alan Ofsetleri ve Hizalama (Padding)

Bir işaretçiye **sabit ofsetlerle** farklı boyutlarda erişiliyorsa (`BYTE PTR [rcx]`, `DWORD PTR [rcx + 4]`, `QWORD PTR [rcx + 8]`) bu bir **`struct`** yapısıdır.

İşlemci 4 baytlık (`uint32_t`) bir alanı 4'ün katı olan adresten, 8 baytlık (`uint64_t`) bir alanı 8'in katı olan adresten okumak ister (**doğal hizalama / natural alignment**). Bu yüzden derleyici alanların arasına görünmez **dolgu baytları (padding)** ekler:

```c
struct Kayit {
    uint8_t  tip;   // Ofset 0 (1 bayt)
                    // Ofset 1..3 (3 bayt PADDING! Çünkü 'kod' 4'ün katında başlamalı)
    uint32_t kod;   // Ofset 4..7 (4 bayt)
};                  // Toplam boyut: 8 bayt
```

```asm
; int as08_struct_oku(const struct Kayit *k) -> rcx = k
as08_struct_oku:
    movzx eax, BYTE PTR [rcx]       #! Ofset 0: k->tip (1 bayt işaretsiz)
    mov edx, DWORD PTR [rcx + 4]    #! Ofset 4: k->kod (4 bayt; ofset 1..3 hizalama boşluğu!)
    imul eax, 100                   #! eax = k->tip * 100
    add eax, edx                    #! eax = k->tip * 100 + k->kod
    ret
```

> [!GÜVENLİK]
> Çekirdek (kernel) veya ağ sürücüsü bir `struct` nesnesini `memset(&k, 0, sizeof(k))` ile sıfırlamadan yalnızca alanlarına (`k.tip = 3; k.kod = 42;`) değer atayıp kullanıcı uzayına veya ağ soketine kopyalarsa, aradaki **3 baytlık hizalama boşluğu (padding)** yığında daha önce kalmış gizli verileri (işaretçi, anahtar parçası) dışarı sızdırır (**info leak / uninitialized stack memory disclosure**).
:::

::: tahmin
```asm
; Windows x64: rcx = 1. argüman (bellek adresi)
as08_uzunluk:
    xor eax, eax
.L_str:
    movzx edx, BYTE PTR [rcx + rax]
    test dl, dl
    je .L_str_son
    inc eax
    jmp .L_str
.L_str_son:
    ret

as08_struct_oku:
    movzx eax, BYTE PTR [rcx]
    mov edx, DWORD PTR [rcx + 4]
    imul eax, 100
    add eax, edx
    ret

; Çağrılar:
; 1) as08_uzunluk(b"PAFTA\x00")
; 2) kayit_buf = bytes([3, 0, 0, 0, 42, 0, 0, 0])
;    as08_struct_oku(kayit_buf)
```

Yukarıdaki iki fonksiyon sırasıyla çağrıldığında dönen iki satırlık çıktı nedir?

```gercek
5
342
```

???
1. çağrıda `as08_uzunluk` fonksiyonu `b"PAFTA\x00"` dizgisinin baytlarını `rax = 0, 1, 2, 3, 4` indekslerinde okur (`'P'`, `'A'`, `'F'`, `'T'`, `'A'`). `rax = 5` olduğunda `BYTE PTR [rcx + 5]` değeri `0x00` (`'\0'`) olduğu için `test dl, dl` sıfır bayrağını (`ZF = 1`) yakar, `je .L_str_son` sıçrar ve `eax = 5` döner.
2. çağrıda `kayit_buf` bellekte `[0x03, 0x00, 0x00, 0x00, 0x2A, 0x00, 0x00, 0x00]` baytlarını tutar. `movzx eax, BYTE PTR [rcx]` ofset `0`'dan `3` okur; `mov edx, DWORD PTR [rcx + 4]` ise ofset `4..7`'den little-endian 32-bit `42` (`0x0000002A`) okur. `imul eax, 100` ile `300`, `add eax, edx` ile `300 + 42 = 342` döner.
:::

::: gorev Doğal hizalamalı `struct` alan ofseti ve boyut hesaplayıcısı
Bir C `struct` tanımındaki alanların boyut listesi (`alan_boyutlari`, yalnızca `1`, `2`, `4` veya `8` baytlık temel tiplerden oluşur; ör. `[1, 4, 2]`) verildiğinde, doğal hizalama kurallarına göre her alanın başlangıç ofsetini ve `struct`'ın toplam boyutunu hesaplayan `struct_yerlesimi_hesapla(alan_boyutlari)` fonksiyonunu yaz:
- Boyutu `b` (`1, 2, 4, 8`) olan her alan, `ofset % b == 0` olacak şekilde en yakın `b` katına hizalanır (araya dolgu baytları girer).
- Tüm alanlar yerleştirildikten sonra, `struct`'ın toplam boyutu en büyük alan boyutunun (`max(alan_boyutlari)`) katına yukarı yuvarlanır (`toplam % maks_hiza == 0`).
- Boş liste `[]` verilirse `([], 0)` döndür. Geçersiz bir alan boyutu (`{1, 2, 4, 8}` dışında) verilirse `ValueError` fırlat.

```starter
def struct_yerlesimi_hesapla(alan_boyutlari):
    return ([], 0)
```

```test
need("struct_yerlesimi_hesapla")
eq(struct_yerlesimi_hesapla([]), ([], 0), "boş struct ([], 0)")
eq(struct_yerlesimi_hesapla([1, 4]), ([0, 4], 8), "uint8_t (0), 3B pad, uint32_t (4) -> toplam 8")
eq(struct_yerlesimi_hesapla([1, 4, 1]), ([0, 4, 8], 12), "son alan 1B olsa da toplam boyut 4'ün katına (12) yuvarlanmalı")
eq(struct_yerlesimi_hesapla([1, 1, 2, 8]), ([0, 1, 2, 8], 16), "[1, 1, 2, 8] -> ofsetler [0, 1, 2, 8], toplam 16")
eq(struct_yerlesimi_hesapla([8, 4, 2, 1]), ([0, 8, 12, 14], 16), "büyükten küçüğe sıralı alanlar -> [0, 8, 12, 14], toplam 16")
raises(ValueError, lambda: struct_yerlesimi_hesapla([1, 3, 4]), msg="3 baytlık temel alan boyutu için ValueError")
```

```solution
def struct_yerlesimi_hesapla(alan_boyutlari):
    if not alan_boyutlari:
        return ([], 0)
    gecerli = {1, 2, 4, 8}
    ofsetler = []
    imlec = 0
    for b in alan_boyutlari:
        if b not in gecerli:
            raise ValueError(f"Gecersiz alan boyutu: {b}")
        kalan = imlec % b
        if kalan != 0:
            imlec += b - kalan
        ofsetler.append(imlec)
        imlec += b

    maks_hiza = max(alan_boyutlari)
    if imlec % maks_hiza != 0:
        imlec += maks_hiza - (imlec % maks_hiza)
    return (ofsetler, imlec)
```

```hint
Her alan için `imlec % b != 0` ise `imlec += b - (imlec % b)` yaparak hizala; döngü sonunda toplam boyutu `max(alan_boyutlari)` katına tamamla.
```
:::

::: gorev Null sonlandırmalı (`\x00`) C dizgisi okuyucu
Ham `bellek` (`bytes`) içinde verilen `baslangic` ofsetinden itibaren null sonlandırmalı (`0x00`) ASCII dizgiyi (`BYTE PTR [rcx + rax]` döngüsü gibi) okuyan `c_dizgi_oku(bellek, baslangic=0)` fonksiyonunu yaz:
- `baslangic` ofsetinden başlayarak ilk `0x00` baytına kadar olan baytları ASCII (`decode("ascii")`) olarak çözer ve `(dizgi, uzunluk)` ikilisini döndürür (`0x00` baytı uzunluğa dahil değildir).
- `baslangic < 0`, `baslangic >= len(bellek)` veya bellek sonuna kadar hiç `0x00` sonlandırıcı bulunamazsa `ValueError` fırlat.

```starter
def c_dizgi_oku(bellek, baslangic=0):
    return ("", 0)
```

```test
need("c_dizgi_oku")
buf = b"PAFTA\x00GIZLI\x00\x00"
eq(c_dizgi_oku(buf, 0), ("PAFTA", 5), "0. ofsetten PAFTA (uzunluk 5)")
eq(c_dizgi_oku(buf, 6), ("GIZLI", 5), "6. ofsetten GIZLI (uzunluk 5)")
eq(c_dizgi_oku(buf, 11), ("", 0), "hemen 0x00 varsa boş dizgi ('', 0)")
raises(ValueError, lambda: c_dizgi_oku(b"SONSUZ", 0), msg="null sonlandırıcı yoksa ValueError")
raises(ValueError, lambda: c_dizgi_oku(buf, -1), msg="negatif başlangıç için ValueError")
raises(ValueError, lambda: c_dizgi_oku(buf, len(buf)), msg="bellek boyutu dışındaki başlangıç için ValueError")
```

```solution
def c_dizgi_oku(bellek, baslangic=0):
    if baslangic < 0:
        raise ValueError("Gecersiz baslangic ofseti")
    son = bellek.find(0, baslangic)
    if son == -1:
        raise ValueError("Null sonlandirici (0x00) bulunamadi")
    dilim = bellek[baslangic:son]
    return (dilim.decode("ascii"), len(dilim))
```

```hint
`bellek.find(0, baslangic)` ile ilk `0x00` baytının indeksini bul; `-1` dönerse `ValueError` fırlat.
```
:::
