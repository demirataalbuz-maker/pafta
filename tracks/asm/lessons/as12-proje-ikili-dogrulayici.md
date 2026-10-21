---
id: as12
title: "Proje: Disassembly'den İkili Paket Doğrulayıcı Çözümlemek"
rank: baspehlivan
order: 12
summary: Üç fonksiyonlu gerçek bir x86-64 disassembly dökümünü (başlık ayrıştırma, lea/xor tabanlı imza döngüsü ve alt fonksiyon orkestrasyonu) uçtan uca çözümlemek.
---

::: anlat
Bu bitirme projesinde kaynak kodu elimizde olmayan, `clang --target=x86_64-pc-windows-msvc -O1` ile derlenmiş bir ikili ağ/telemetri doğrulayıcı modülün `objdump -d -M intel` çıktısını baştan sona okuyacağız. Modül üç fonksiyondan oluşmaktadır:

1. **`as12_baslik_coz` (`0x00 .. 0x1b`):** Paketin ilk 4 baytlık başlığını (sihirli sayı, sürüm ve gövde uzunluğu) denetler.
2. **`as12_imza_uret` (`0x20 .. 0x47`):** Gövde baytları üzerinde `xor`, `lea eax, [r9+r9*2]` ve `add eax, 0x7` adımlarıyla 32-bit imza üretir.
3. **`as12_paket_dogrula` (`0x50 .. 0x82`):** İlk iki fonksiyonu Windows x64 ABI kurallarına göre (kalıcı `rsi`/`rdi` yazmaçlarını koruyarak, 32 bayt gölge alan + 8 bayt hizalama ayırarak ve ikinci çağrıyı kuyruk çağrısı `jmp` ile yaparak) sırayla çağırır.

### Tam Disassembly Dökümü (`objdump -d -M intel`)

```asm
0000000000000000 <as12_baslik_coz>:
   0: b8 ff ff ff ff                mov    eax, 0xffffffff              #! Varsayılan dönüş: -1 (geçersiz sihirli sayı)
   5: 66 81 39 46 50                cmp    WORD PTR [rcx], 0x5046       #! Ofset 0..1: 16-bit little-endian == 0x5046 mı? ("FP")
   a: 75 0f                         jne    0x1b <as12_baslik_coz+0x1b>  #! Eşit değilse -1 döndür
   c: b8 fe ff ff ff                mov    eax, 0xfffffffe              #! Varsayılan dönüş: -2 (desteklenmeyen sürüm)
  11: 80 79 02 02                   cmp    BYTE PTR [rcx+0x2], 0x2      #! Ofset 2: 1 bayt sürüm == 2 mi?
  15: 75 04                         jne    0x1b <as12_baslik_coz+0x1b>  #! Eşit değilse -2 döndür
  17: 0f b6 41 03                   movzx  eax, BYTE PTR [rcx+0x3]      #! Ofset 3: 1 bayt gövde uzunluğu (0..255)
  1b: c3                            ret                                 #! Sonucu (0..255, -1 veya -2) döndür
  1c: 0f 1f 40 00                   nop    DWORD PTR [rax+0x0]          #! Sonraki fonksiyonu 0x20 (16-bayt) sınırına hizala

0000000000000020 <as12_imza_uret>:
  20: 44 89 c0                      mov    eax, r8d                     #! eax = tohum (3. argüman: r8d)
  23: 85 d2                         test   edx, edx                     #! uzunluk (2. argüman: edx) <= 0 mı?
  25: 7e 20                         jle    0x47 <as12_imza_uret+0x27>   #! uzunluk <= 0 ise döngüye girmeden çık
  27: 89 d2                         mov    edx, edx                     #! rdx'in üst 32 bitini sıfırla (rdx = uzunluk)
  29: 45 31 c0                      xor    r8d, r8d                     #! r8 = 0 (indeks i = 0)
  2c: 0f 1f 40 00                   nop    DWORD PTR [rax+0x0]          #! Döngü başını 0x30 (16-bayt) sınırına hizala
  30: 46 0f b6 0c 01                movzx  r9d, BYTE PTR [rcx+r8*1]     #! r9d = govde[i] (1. argüman: rcx)
  35: 41 31 c1                      xor    r9d, eax                     #! r9d = govde[i] ^ eax
  38: 43 8d 04 49                   lea    eax, [r9+r9*2]               #! eax = r9d * 3 (32-bit adres matematiği!)
  3c: 83 c0 07                      add    eax, 0x7                     #! eax = eax + 7
  3f: 49 ff c0                      inc    r8                           #! i++
  42: 4c 39 c2                      cmp    rdx, r8                      #! uzunluk == i mi?
  45: 75 e9                         jne    0x30 <as12_imza_uret+0x10>   #! Eşit değilse döngü başına (0x30) dön
  47: c3                            ret                                 #! İmzayı (eax) döndür
  48: 0f 1f 84 00 00 00 00 00       nop    DWORD PTR [rax+rax*1+0x0]    #! Sonraki fonksiyonu 0x50 (16-bayt) sınırına hizala

0000000000000050 <as12_paket_dogrula>:
  50: 56                            push   rsi                          #! Windows x64: kalıcı rsi yazmacını yığına kaydet
  51: 57                            push   rdi                          #! Windows x64: kalıcı rdi yazmacını yığına kaydet
  52: 48 83 ec 28                   sub    rsp, 0x28                    #! 40 bayt çerçeve (32B gölge alan + 8B hizalama)
  56: 89 d6                         mov    esi, edx                     #! 2. argüman tohum (edx) -> kalıcı esi'ye sakla
  58: 48 89 cf                      mov    rdi, rcx                     #! 1. argüman paket (rcx) -> kalıcı rdi'ye sakla
  5b: e8 a0 ff ff ff                call   0x0 <as12_baslik_coz>        #! eax = as12_baslik_coz(paket)
  60: 85 c0                         test   eax, eax                     #! Dönüş değerini test et
  62: 78 17                         js     0x7b <as12_paket_dogrula+0x2b> #! Negatifse (SF == 1: -1 veya -2) 0x7b'ye sıçra!
  64: 48 83 c7 04                   add    rdi, 0x4                     #! rdi = paket + 4 (gövde başlangıcı!)
  68: 48 89 f9                      mov    rcx, rdi                     #! 1. argüman rcx = paket + 4
  6b: 89 c2                         mov    edx, eax                     #! 2. argüman edx = govde_uzunlugu (eax)
  6d: 41 89 f0                      mov    r8d, esi                     #! 3. argüman r8d = saklanan tohum (esi)
  70: 48 83 c4 28                   add    rsp, 0x28                    #! Kuyruk çağrısı öncesi çerçeveyi kapat
  74: 5f                            pop    rdi                          #! Kalıcı rdi yazmacını geri yükle
  75: 5e                            pop    rsi                          #! Kalıcı rsi yazmacını geri yükle
  76: e9 a5 ff ff ff                jmp    0x20 <as12_imza_uret>        #! Tail-call: as12_imza_uret(paket + 4, uzunluk, tohum)
  7b: 90                            nop
  7c: 48 83 c4 28                   add    rsp, 0x28                    #! Hata dalı: çerçeveyi kapat
  80: 5f                            pop    rdi                          #! Kalıcı rdi yazmacını geri yükle
  81: 5e                            pop    rsi                          #! Kalıcı rsi yazmacını geri yükle
  82: c3                            ret                                 #! Hata kodunu (eax) döndür
```

### İkili Paket Formatının Özeti

Disassembly'deki bellek ofsetlerini birleştirdiğimizde paketin bellek şeması tamamen ortaya çıkar:

| Ofset | Boyut | Erişim Komutu | Beklenen Değer / Anlam |
|---|---|---|---|
| `0..1` | 2 bayt (`WORD`) | `cmp WORD PTR [rcx], 0x5046` | `0x5046` → Little-endian bellekte **`0x46, 0x50`** (`b"FP"`) |
| `2` | 1 bayt (`BYTE`) | `cmp BYTE PTR [rcx+0x2], 0x2` | `0x02` → Protokol sürümü (`2`) |
| `3` | 1 bayt (`BYTE`) | `movzx eax, BYTE PTR [rcx+0x3]` | `N` (`0..255`) → Gövde (payload) bayt uzunluğu |
| `4 .. 4+N-1` | `N` bayt | `add rdi, 0x4` → `[rcx+r8*1]` | İmza döngüsüne giren gövde baytları |

> [!TUZAK]
> `cmp WORD PTR [rcx], 0x5046` satırına bakıp paketin ilk iki baytına `[0x50, 0x46]` yazmak en klasik tersine mühendislik hatasıdır! x86-64 little-endian olduğu için `WORD PTR [rcx]` karşılaştırması `0x5046` ile eşleşsin istiyorsak bellekteki ilk bayt en düşük anlamlı bayt olan **`0x46`** (`'F'`), ikinci bayt **`0x50`** (`'P'`) olmalıdır.
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
1. çağrı (`pkt1`): İlk iki bayt `[0x46, 0x50]` little-endian olarak `0x5046` okunur (sihirli sayı doğru). Ofset 2'deki sürüm `2` (doğru), ofset 3'teki gövde uzunluğu `2` döner. `as12_imza_uret(paket + 4, 2, 5)` kuyruk çağrısıyla (`jmp 0x20`) çalışır:
- Başlangıçta `eax = 5`.
- 1. gövde baytı `10`: `r9d = 10 ^ 5 = 15`; `lea eax, [r9+r9*2]` + `add eax, 0x7` → `15 * 3 + 7 = 52`.
- 2. gövde baytı `20`: `r9d = 20 ^ 52 = 32`; `lea eax, [r9+r9*2]` + `add eax, 0x7` → `32 * 3 + 7 = 103`.
Sonuç `103` döner.
2. çağrı (`pkt2`): İlk iki bayt `[0x50, 0x46]` little-endian olarak `0x4650 != 0x5046` okunduğu için `as12_baslik_coz` `-1` (`0xffffffff`) döndürür; `test eax, eax` → `js 0x7b` dallanmasıyla doğrudan `-1` döner.
3. çağrı (`pkt3`): Sihirli sayı doğru (`0x5046`), ancak ofset 2'deki sürüm `1 != 2` olduğu için `as12_baslik_coz` `-2` (`0xfffffffe`) döndürür; `js 0x7b` dallanmasıyla doğrudan `-2` döner.
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
  - `eax = (eax * 3 + 7) & 0xFFFFFFFF` (`lea eax, [r9+r9*2]` ve `add eax, 0x7`)
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
