---
id: as12
title: "Proje: Disassembly'den İkili Paket Doğrulayıcı Çözümlemek"
rank: baspehlivan
order: 12
summary: Üç fonksiyonlu gerçek bir x86-64 disassembly dökümünü (başlık ayrıştırma, lea/xor tabanlı imza döngüsü ve alt fonksiyon orkestrasyonu) uçtan uca çözümlemek.
---

::: anlat
Bu bitirme projesinde kaynak kodu elimizde olmayan, derlenmiş bir ikili ağ/telemetri doğrulayıcı modülün `llvm-objdump -d -M intel` çıktısını baştan sona okuyacağız. Modül üç fonksiyondan oluşmaktadır:

1. **`as12_baslik_coz` (`0x00 .. 0x23`):** Paketin ilk 4 baytlık başlığını (sihirli sayı, sürüm ve gövde uzunluğu) denetler.
2. **`as12_imza_uret` (`0x24 .. 0x40`):** Gövde baytları üzerinde `xor` ve `lea eax, [rax + 2*rax + 7]` adımlarıyla 32-bit imza üretir.
3. **`as12_paket_dogrula` (`0x41 .. 0x70`):** İlk iki fonksiyonu Windows x64 ABI kurallarına göre (yığında gölge alan ve uçucu yazmaç kaydıyla) sırayla çağırır.

### Tam Disassembly Dökümü (`llvm-objdump -d -M intel`)

```asm
0000000000000000 <as12_baslik_coz>:
   0: 0f b7 01              movzx  eax, word ptr [rcx]          #! Ofset 0..1: 16-bit little-endian sihirli sayı
   3: 3d 46 50 00 00        cmp    eax, 0x5046                  #! Sihirli sayı == 0x5046 mı? (Bellekte: 0x46, 0x50 -> "FP")
   8: 75 0e                 jne    0x18 <as12_baslik_coz+0x18>  #! Eşit değilse -1 döndür
   a: 0f b6 41 02           movzx  eax, byte ptr [rcx + 0x2]    #! Ofset 2: 1 bayt sürüm (version)
   e: 83 f8 02              cmp    eax, 0x2                     #! Sürüm == 2 mi?
  11: 75 0b                 jne    0x1e <as12_baslik_coz+0x1e>  #! Eşit değilse -2 döndür
  13: 0f b6 41 03           movzx  eax, byte ptr [rcx + 0x3]    #! Ofset 3: 1 bayt gövde uzunluğu (payload_len)
  17: c3                    ret                                 #! Gövde uzunluğunu (0..255) döndür
  18: b8 ff ff ff ff        mov    eax, 0xffffffff              #! Hata kodu: -1 (geçersiz sihirli sayı)
  1d: c3                    ret
  1e: b8 fe ff ff ff        mov    eax, 0xfffffffe              #! Hata kodu: -2 (desteklenmeyen sürüm)
  23: c3                    ret

0000000000000024 <as12_imza_uret>:
  24: 44 89 c0              mov    eax, r8d                     #! eax = tohum (3. argüman: r8d)
  27: 45 31 c9              xor    r9d, r9d                     #! r9d = 0 (indeks i = 0)
  2a: 41 39 d1              cmp    r9d, edx                     #! i ile uzunluk (2. argüman: edx) karşılaştır
  2d: 7d 11                 jge    0x40 <as12_imza_uret+0x1c>   #! i >= uzunluk ise döngüden çık
  2f: 46 0f b6 14 09        movzx  r10d, byte ptr [rcx + r9]    #! r10d = govde[i] (1. argüman: rcx)
  34: 44 31 d0              xor    eax, r10d                    #! eax = eax ^ govde[i]
  37: 8d 44 40 07           lea    eax, [rax + 2*rax + 0x7]     #! eax = eax * 3 + 7 (32-bit aritmetik!)
  3b: 41 ff c1              inc    r9d                          #! i++
  3e: eb ea                 jmp    0x2a <as12_imza_uret+0x6>    #! Döngü başına dön
  40: c3                    ret                                 #! İmzayı (eax) döndür

0000000000000041 <as12_paket_dogrula>:
  41: 48 83 ec 28           sub    rsp, 0x28                    #! 40 bayt çerçeve (32B gölge alan + 8B kayıt/hiza)
  45: 48 89 4c 24 20        mov    qword ptr [rsp + 0x20], rcx  #! 1. argüman paket işaretçisini (rcx) yığına sakla
  4a: 89 54 24 1c           mov    dword ptr [rsp + 0x1c], edx  #! 2. argüman tohum değerini (edx) yığına sakla
  4e: e8 ad ff ff ff        call   0x0 <as12_baslik_coz>        #! eax = as12_baslik_coz(paket)
  53: 85 c0                 test   eax, eax                     #! Dönüş değerini test et
  55: 78 15                 js     0x6c <as12_paket_dogrula+0x2b> #! Negatifse (SF == 1: -1 veya -2) doğrudan çık!
  57: 48 8b 4c 24 20        mov    rcx, qword ptr [rsp + 0x20]  #! Saklanan paket adresini rcx'e geri yükle
  5c: 89 c2                 mov    edx, eax                     #! 2. argüman edx = govde_uzunlugu (eax)
  5e: 48 83 c1 04           add    rcx, 0x4                     #! 1. argüman rcx = paket + 4 (gövde başlangıcı!)
  62: 44 8b 44 24 1c        mov    r8d, dword ptr [rsp + 0x1c]  #! 3. argüman r8d = saklanan tohum değeri
  67: e8 b8 ff ff ff        call   0x24 <as12_imza_uret>        #! eax = as12_imza_uret(paket + 4, uzunluk, tohum)
  6c: 48 83 c4 28           add    rsp, 0x28                    #! Çerçeveyi kapat
  70: c3                    ret                                 #! Sonucu (hata kodu veya imza) döndür
```

### İkili Paket Formatının Özeti

Disassembly'deki bellek ofsetlerini birleştirdiğimizde paketin bellek şeması tamamen ortaya çıkar:

| Ofset | Boyut | Erişim Komutu | Beklenen Değer / Anlam |
|---|---|---|---|
| `0..1` | 2 bayt (`WORD`) | `movzx eax, word ptr [rcx]` | `0x5046` → Little-endian bellekte **`0x46, 0x50`** (`b"FP"`) |
| `2` | 1 bayt (`BYTE`) | `movzx eax, byte ptr [rcx + 2]` | `0x02` → Protokol sürümü (`2`) |
| `3` | 1 bayt (`BYTE`) | `movzx eax, byte ptr [rcx + 3]` | `N` (`0..255`) → Gövde (payload) bayt uzunluğu |
| `4 .. 4+N-1` | `N` bayt | `add rcx, 4` → `[rcx + r9]` | İmza döngüsüne giren gövde baytları |

> [!TUZAK]
> `cmp eax, 0x5046` satırına bakıp paketin ilk iki baytına `[0x50, 0x46]` yazmak en klasik tersine mühendislik hatasıdır! x86-64 little-endian olduğu için `word ptr [rcx]` okuması `0x5046` üretsin istiyorsak bellekteki ilk bayt en düşük anlamlı bayt olan **`0x46`** (`'F'`), ikinci bayt **`0x50`** (`'P'`) olmalıdır.
:::

::: tahmin
```asm
; Yukarıdaki as12_baslik_coz, as12_imza_uret ve as12_paket_dogrula fonksiyonları
; Windows x64: rcx = paket adresi, edx = tohum (5)
;
; pkt1 = bytes([0x46, 0x50, 2, 2, 10, 20])
; pkt2 = bytes([0x50, 0x46, 2, 2, 10, 20])
; pkt3 = bytes([0x46, 0x50, 1, 2, 10, 20])
;
; Çağrılar:
; 1) as12_paket_dogrula(pkt1, 5)
; 2) as12_paket_dogrula(pkt2, 5)
; 3) as12_paket_dogrula(pkt3, 5)
```

Yukarıdaki üç paket `tohum = 5` ile `as12_paket_dogrula` fonksiyonuna verildiğinde dönen üç satırlık çıktı nedir?

```gercek
103
-1
-2
```

???
1. çağrı (`pkt1`): İlk iki bayt `[0x46, 0x50]` little-endian olarak `0x5046` okunur (sihirli sayı doğru). Ofset 2'deki sürüm `2` (doğru), ofset 3'teki gövde uzunluğu `2` döner. `as12_imza_uret(paket + 4, 2, 5)` çağrılır:
- Başlangıçta `eax = 5`.
- 1. gövde baytı `10`: `eax = 5 ^ 10 = 15`; `lea eax, [rax + 2*rax + 7]` → `15 * 3 + 7 = 52`.
- 2. gövde baytı `20`: `eax = 52 ^ 20 = 32`; `lea eax, [rax + 2*rax + 7]` → `32 * 3 + 7 = 103`.
Sonuç `103` döner.
2. çağrı (`pkt2`): İlk iki bayt `[0x50, 0x46]` little-endian olarak `0x4650 != 0x5046` okunduğu için `as12_baslik_coz` `-1` (`0xffffffff`) döndürür; `test eax, eax` → `js` dallanmasıyla doğrudan `-1` döner.
3. çağrı (`pkt3`): Sihirli sayı doğru (`0x5046`), ancak ofset 2'deki sürüm `1 != 2` olduğu için `as12_baslik_coz` `-2` (`0xfffffffe`) döndürür; `js` dallanmasıyla doğrudan `-2` döner.
:::

::: gorev Adım 1: `as12_baslik_coz` başlık ayrıştırıcısı
`as12_baslik_coz` fonksiyonunun disassembly mantığını birebir uygulayan `baslik_coz(paket)` fonksiyonunu yaz:
- `len(paket) < 4` ise `ValueError` fırlat.
- Ofset `0..1` little-endian 16-bit değeri `0x5046` değilse `-1` döndür.
- Ofset `2` değeri `2` değilse `-2` döndür.
- Aksi halde ofset `3`'teki gövde uzunluğunu (`0..255`) döndür.

```starter
def baslik_coz(paket):
    return -1
```

```test
need("baslik_coz")
eq(baslik_coz(bytes([0x46, 0x50, 2, 0])), 0, "geçerli başlık, 0 uzunluk")
eq(baslik_coz(bytes([0x46, 0x50, 2, 255])), 255, "geçerli başlık, 255 uzunluk")
eq(baslik_coz(bytes([0x50, 0x46, 2, 10])), -1, "ters endian sihirli sayı -> -1")
eq(baslik_coz(bytes([0x46, 0x50, 1, 10])), -2, "yanlış sürüm (1 != 2) -> -2")
eq(baslik_coz(bytes([0x00, 0x00, 1, 10])), -1, "önce sihirli sayı kontrol edilmeli -> -1")
raises(ValueError, lambda: baslik_coz(b"FP\x02"), msg="4 bayttan kısa paket için ValueError")
```

```solution
def baslik_coz(paket):
    if len(paket) < 4:
        raise ValueError("Paket en az 4 bayt olmalidir")
    magic = paket[0] | (paket[1] << 8)
    if magic != 0x5046:
        return -1
    if paket[2] != 2:
        return -2
    return paket[3]
```

```hint
Little-endian 16-bit okuma için `paket[0] | (paket[1] << 8)` değerini `0x5046` ile karşılaştır.
```
:::

::: gorev Adım 2: `as12_imza_uret` döngüsü (`xor` + `lea`)
`as12_imza_uret` fonksiyonunun disassembly mantığını birebir uygulayan `imza_uret(govde, uzunluk, tohum)` fonksiyonunu yaz:
- `uzunluk < 0` veya `uzunluk > len(govde)` ise `ValueError` fırlat.
- `eax = tohum & 0xFFFFFFFF` ile başla; `i = 0 .. uzunluk - 1` aralığındaki her `govde[i]` baytı için sırasıyla:
  - `eax = (eax ^ govde[i]) & 0xFFFFFFFF`
  - `eax = (eax * 3 + 7) & 0xFFFFFFFF` (`lea eax, [rax + 2*rax + 7]`)
- Sonuçtaki 32-bit değeri **işaretli 32-bit `int`** (`>= 0x80000000` ise `- 0x100000000`) olarak döndür.

```starter
def imza_uret(govde, uzunluk, tohum):
    return tohum
```

```test
need("imza_uret")
eq(imza_uret(bytes([10, 20]), 2, 5), 103, "[10, 20] ve tohum=5 için imza 103")
eq(imza_uret(bytes([10, 20, 99]), 2, 5), 103, "yalnızca ilk 'uzunluk' bayt işlenmeli")
eq(imza_uret(b"", 0, 42), 42, "0 uzunlukta döngüye girmeden tohum dönmeli")
eq(imza_uret(b"", 0, 0x80000000), -0x80000000, "0x80000000 tam işaretli negatif alt sınır (-2147483648)")
eq(imza_uret(b"\x00", 1, 0x30000000), (0x90000007 - 0x100000000), "32-bit taşma ve işaretli 32-bit dönüş")
raises(ValueError, lambda: imza_uret(b"AB", -1, 0), msg="negatif uzunluk için ValueError")
raises(ValueError, lambda: imza_uret(b"AB", 3, 0), msg="gövdeden büyük uzunluk için ValueError")
```

```solution
def _s32(deger):
    u = deger & 0xFFFFFFFF
    return u - 0x100000000 if u >= 0x80000000 else u


def imza_uret(govde, uzunluk, tohum):
    if uzunluk < 0 or uzunluk > len(govde):
        raise ValueError("Gecersiz govde uzunlugu")
    eax = tohum & 0xFFFFFFFF
    for i in range(uzunluk):
        eax = (eax ^ govde[i]) & 0xFFFFFFFF
        eax = (eax * 3 + 7) & 0xFFFFFFFF
    return _s32(eax)
```

```hint
Her adımda `eax = ((eax ^ govde[i]) * 3 + 7) & 0xFFFFFFFF` uygula ve döngü sonunda 32-bit işaretli tam sayıya çevir.
```
:::

::: gorev Adım 3: `paket_dogrula` ve geçerli paket üretici
`as12_paket_dogrula` orkestrasyonunu ve tersine mühendislikle geçerli paket üretimini tamamla:
- `paket_dogrula(paket, tohum)`: Önce `baslik_coz(paket)` çağırır; sonuç negatifse (`< 0`) doğrudan o hata kodunu döndürür. Negatif değilse (`uzunluk = sonuc`), `paket[4:]` içinde en az `uzunluk` bayt bulunduğunu doğrular (yoksa `ValueError` fırlatır) ve `imza_uret(paket[4:], uzunluk, tohum)` sonucunu döndürür.
- `gecerli_paket_olustur(govde, tohum)`: Verilen `govde` (`len(govde) <= 255`, aksi halde `ValueError`) için `as12_baslik_coz` kontrolünden geçen 4 baytlık başlığı (`0x5046` little-endian + sürüm `2` + `len(govde)`) ve gövdeyi birleştirip `(paket, beklenen_imza)` ikilisini döndürür.

```starter
def paket_dogrula(paket, tohum):
    return -1

def gecerli_paket_olustur(govde, tohum):
    return (b"", 0)
```

```test
need("paket_dogrula")
need("gecerli_paket_olustur")
pkt1 = bytes([0x46, 0x50, 2, 2, 10, 20])
pkt2 = bytes([0x50, 0x46, 2, 2, 10, 20])
pkt3 = bytes([0x46, 0x50, 1, 2, 10, 20])
eq(paket_dogrula(pkt1, 5), 103, "pkt1 doğrulaması 103 dönmeli")
eq(paket_dogrula(pkt2, 5), -1, "pkt2 hatalı sihirli sayı -> -1")
eq(paket_dogrula(pkt3, 5), -2, "pkt3 hatalı sürüm -> -2")
eq(paket_dogrula(bytes([0x46, 0x50, 2, 2, 10, 20, 99, 88]), 5), 103, "fazladan kuyruk baytları imzayı etkilememeli")
raises(ValueError, lambda: paket_dogrula(bytes([0x46, 0x50, 2, 5, 10, 20]), 5), msg="eksik gövde için ValueError")

uretilen_pkt, uretilen_imza = gecerli_paket_olustur(bytes([10, 20]), 5)
eq(uretilen_pkt, pkt1, "üretilen paket [0x46, 0x50, 2, 2, 10, 20] olmalı")
eq(uretilen_imza, 103, "üretilen imza 103 olmalı")
eq(paket_dogrula(uretilen_pkt, 5), uretilen_imza, "üretilen paket doğrulamadan geçmeli")

bos_pkt, bos_imza = gecerli_paket_olustur(b"", 19)
eq(bos_pkt, bytes([0x46, 0x50, 2, 0]), "boş gövdeli paket başlığı")
eq(bos_imza, 19, "boş gövdede imza tohuma eşit olmalı")
eq(gecerli_paket_olustur(b"", 0x80000000)[1], -0x80000000, "0x80000000 tohumu işaretli -2147483648 dönmeli")
eq(len(gecerli_paket_olustur(b"A" * 255, 1)[0]), 259, "tam 255 baytlık gövde geçerlidir (4 + 255 = 259 bayt)")
raises(ValueError, lambda: gecerli_paket_olustur(b"A" * 256, 1), msg="255 bayttan uzun gövde için ValueError")
```

```solution
def _s32(deger):
    u = deger & 0xFFFFFFFF
    return u - 0x100000000 if u >= 0x80000000 else u


def baslik_coz(paket):
    if len(paket) < 4:
        raise ValueError("Paket en az 4 bayt olmalidir")
    magic = paket[0] | (paket[1] << 8)
    if magic != 0x5046:
        return -1
    if paket[2] != 2:
        return -2
    return paket[3]


def imza_uret(govde, uzunluk, tohum):
    if uzunluk < 0 or uzunluk > len(govde):
        raise ValueError("Gecersiz govde uzunlugu")
    eax = tohum & 0xFFFFFFFF
    for i in range(uzunluk):
        eax = (eax ^ govde[i]) & 0xFFFFFFFF
        eax = (eax * 3 + 7) & 0xFFFFFFFF
    return _s32(eax)


def paket_dogrula(paket, tohum):
    uzunluk = baslik_coz(paket)
    if uzunluk < 0:
        return uzunluk
    govde = paket[4:]
    if len(govde) < uzunluk:
        raise ValueError("Paket govdesi basliktaki uzunluktan kisa")
    return imza_uret(govde, uzunluk, tohum)


def gecerli_paket_olustur(govde, tohum):
    if len(govde) > 255:
        raise ValueError("Govde uzunlugu en fazla 255 bayt olabilir")
    baslik = bytes([0x46, 0x50, 2, len(govde)])
    paket = baslik + govde
    imza = paket_dogrula(paket, tohum)
    return (paket, imza)
```

```hint
`gecerli_paket_olustur` içinde `bytes([0x46, 0x50, 2, len(govde)]) + govde` ile paketi kurup `paket_dogrula` ile imzasını hesapla.
```
:::
