---
id: as11
title: Disassembly Çıktısı, RIP-Göreli Adresleme ve Bit Döndürme
rank: baspehlivan
order: 11
summary: objdump/llvm-objdump sütunlarını, göreli sıçrama ofsetlerini (eb/74/e8), [rip + disp] adreslemesini ve rol/ror + xor özet döngülerini okumak.
---

::: anlat
Gerçek dünyada bir ikili dosyayı `objdump -d -M intel` veya `llvm-objdump -d -M intel` ile açtığınızda karşınıza üç sütunlu bir tablo çıkar:

1. **Sol sütun (`0:`, `2:`, `5:`):** Komutun bölüm (`.text`) veya bellek içindeki onaltılık adresi.
2. **Orta sütun (`89 d0`, `c1 c0 03`):** İşlemcinin gerçekte yürüttüğü ham makine kodu baytları (opcode + ModR/M + sabitler).
3. **Sağ sütun (`mov eax, edx`):** Ham baytların insan tarafından okunabilir assembly karşılığı (mnemonic + işlenenler).

```asm
0000000000000000 <as11_iz_ozet>:
   0: 89 d0                 mov    eax, edx                  #! eax = baslangic_tohum (2. argüman)
   2: 45 31 c0              xor    r8d, r8d                  #! r8 = 0 (bayt indeksi i = 0)
   5: 46 0f b6 0c 01        movzx  r9d, byte ptr [rcx + r8]  #! r9d = veri[i] (1 bayt oku)
   a: 45 84 c9              test   r9b, r9b                  #! veri[i] == 0 mı?
   d: 74 0b                 je     0x1a <as11_iz_ozet+0x1a>  #! 0x0d + 2 + 0x0b = 0x1a adresine sıçra
   f: c1 c0 03              rol    eax, 0x3                  #! eax'i 32-bit içinde sola 3 bit döndür
  12: 44 31 c8              xor    eax, r9d                  #! eax ^= veri[i]
  15: 49 ff c0              inc    r8                        #! i++
  18: eb eb                 jmp    0x5 <as11_iz_ozet+0x5>    #! 0x18 + 2 + (-21 / 0xeb) = 0x05'e dön
  1a: c3                    ret                              #! Özeti (eax) döndür
```

### 1. Göreli Sıçrama (`74 0b`, `eb eb`) ve `[rip + disp]` Nasıl Hesaplanır?

x86-64'te çoğu `jmp`, `jcc`, `call` komutu ve global değişken erişimi (`[rip + disp32]`), mutlak adres yerine **bir sonraki komutun adresine (`rip_sonraki`) göre işaretli uzaklık (displacement)** kullanır. Bu sayede kod belleğin neresine yüklenirse yüklensin (ASLR / PIE) adreslerin yeniden yamalanmasına gerek kalmaz:

$$\text{Hedef Adres} = \text{Komut Adresi} + \text{Komut Uzunluğu} + \text{İşaretli Ofset}$$

| Adres | Ham Baytlar | Uzunluk | Sonraki `rip` | İşaretli Ofset | Hedef Adres Hesabı |
|---|---|---|---|---|---|
| `0x0d` | `74 0b` (`je`) | `2` bayt | `0x0d + 2 = 0x0f` | `0x0b` (`+11`) | `0x0f + 11 = 0x1a` |
| `0x18` | `eb eb` (`jmp`) | `2` bayt | `0x18 + 2 = 0x1a` | `0xeb` (`-21`) | `0x1a - 21 = 0x05` |
| `0x40` | `48 8d 0d 19 20 00 00` (`lea rcx, [rip + 0x2019]`) | `7` bayt | `0x40 + 7 = 0x47` | `0x00002019` | `0x47 + 0x2019 = 0x2060` |

> [!NOT]
> Disassembler'larda `lea rcx, [rip + 0x2019]` satırının yanında `# 0x2060 <hata_mesaji>` gibi bir yorum görürsünüz. Buradaki `0x2060`, mevcut komutun adresi (`0x40`) ile değil, **bir sonraki komutun adresi (`0x47`)** ile `0x2019` toplanarak bulunur!

### 2. Bit Döndürme Komutları: `rol` (Rotate Left) ve `ror` (Rotate Right)

Normal kaydırma (`shl` / `shr`) taşan bitleri çöpe atıp yerine `0` doldururken, **döndürme (`rol` / `ror`)** bir uçtan taşan bitleri diğer uçtan geri sokar. Bu yüzden protokol kontrol toplamlarında (checksum), hash fonksiyonlarında ve şifreleme rutinlerinde çok sık kullanılır:

- **`rol eax, k` (32-bit sola döndürme):** En üstten çıkan `k` bit, en sağdaki alt bitlere yerleşir:
  `((eax << k) | (eax >> (32 - k))) & 0xFFFFFFFF`
- **`ror eax, k` (32-bit sağa döndürme):** En sağdan çıkan `k` bit, en soldaki üst bitlere yerleşir:
  `((eax >> k) | (eax << (32 - k))) & 0xFFFFFFFF`
:::

::: tahmin
```asm
; llvm-objdump -d -M intel çıktısı
; Windows x64: rcx = null sonlandırmalı dizgi, edx = başlangıç tohumu
0000000000000000 <as11_iz_ozet>:
       0: 89 d0                         mov     eax, edx
       2: 45 31 c0                      xor     r8d, r8d
       5: 46 0f b6 0c 01                movzx   r9d, byte ptr [rcx + r8]
       a: 45 84 c9                      test    r9b, r9b
       d: 74 0b                         je      0x1a <as11_iz_ozet+0x1a>
       f: c1 c0 03                      rol     eax, 0x3
      12: 44 31 c8                      xor     eax, r9d
      15: 49 ff c0                      inc     r8
      18: eb eb                         jmp     0x5 <as11_iz_ozet+0x5>
      1a: c3                            ret

; Çağrılar (sonuçlar 0x{:04X} biçiminde yazdırılıyor):
; 1) as11_iz_ozet(b"AB\x00", 0x10)
; 2) as11_iz_ozet(b"OK\x00", 0x05)
```

Yukarıdaki `as11_iz_ozet` fonksiyonu `b"AB"` (`'A'=0x41, 'B'=0x42`) ve `0x10` tohumuyla, ardından `b"OK"` (`'O'=0x4F, 'K'=0x4B`) ve `0x05` tohumuyla çağrıldığında yazdırılan iki satırlık onaltılık çıktı nedir?

```gercek
0x064A
0x0373
```

???
1. çağrı (`b"AB"`, tohum `0x10`):
- Başlangıçta `eax = 0x10`.
- 1. bayt `'A'` (`0x41`): `rol eax, 3` → `0x10 << 3 = 0x80`; `xor eax, 0x41` → `0x80 ^ 0x41 = 0xC1`.
- 2. bayt `'B'` (`0x42`): `rol eax, 3` → `0xC1 << 3 = 0x0608`; `xor eax, 0x42` → `0x0608 ^ 0x42 = 0x064A`.
- 3. bayt `0x00`: `test r9b, r9b` → `je 0x1a` ile döngüden çıkar ve `0x064A` döner.

2. çağrı (`b"OK"`, tohum `0x05`):
- Başlangıçta `eax = 0x05`.
- 1. bayt `'O'` (`0x4F`): `rol eax, 3` → `0x05 << 3 = 0x28`; `xor eax, 0x4F` → `0x28 ^ 0x4F = 0x67`.
- 2. bayt `'K'` (`0x4B`): `rol eax, 3` → `0x67 << 3 = 0x0338`; `xor eax, 0x4B` → `0x0338 ^ 0x4B = 0x0373`.
- 3. bayt `0x00` ile döngü biter ve `0x0373` döner.
:::

::: gorev 32-bit `rol` / `ror` bit döndürme ve `as11_iz_ozet` simülatörü
32-bit bir yazmaç üzerinde `rol` (sola döndürme) veya `ror` (sağa döndürme) işlemini uygulayan `bit_dondur32(yon, deger, miktar)` ve yukarıdaki `as11_iz_ozet` disassembly fonksiyonunu herhangi bir `veri` (`bytes`, ilk `0x00` baytına kadar veya `0x00` yoksa sonuna kadar) ve `tohum` (`int`) için çalıştıran `iz_ozet_hesapla(veri, tohum)` fonksiyonlarını yaz:
- `bit_dondur32`: `yon` `"rol"` veya `"ror"` (büyük/küçük harf duyarsız) olmalıdır; farklı bir değerde `ValueError` fırlat. x86 işlemcilerde kaydırma/döndürme miktarı `miktar & 31` (`% 32`) olarak maskelenir ve sonuç 32-bit işaretsiz (`& 0xFFFFFFFF`) döner.
- `iz_ozet_hesapla`: `eax = tohum & 0xFFFFFFFF` ile başlar; `veri` içindeki her bayt için (`0x00` görülürse durur) sırasıyla `eax = bit_dondur32("rol", eax, 3)` ve `eax = eax ^ bayt` uygular.

```starter
def bit_dondur32(yon, deger, miktar):
    return deger & 0xFFFFFFFF

def iz_ozet_hesapla(veri, tohum):
    return tohum & 0xFFFFFFFF
```

```test
need("bit_dondur32")
need("iz_ozet_hesapla")
eq(bit_dondur32("rol", 0x80000001, 1), 0x00000003, "rol 1: en üst bit (bit 31) en alt bite (bit 0) sarılmalı")
eq(bit_dondur32("ror", 0x00000003, 1), 0x80000001, "ror 1: en alt bit (bit 0) en üst bite (bit 31) sarılmalı")
eq(bit_dondur32("rol", 0x12345678, 0), 0x12345678, "0 bit döndürme değeri değiştirmemeli")
eq(bit_dondur32("rol", 0x12345678, 32), 0x12345678, "32 bit döndürme (32 & 31 == 0) değeri değiştirmemeli")
eq(bit_dondur32("ROR", 0xF0000000, 4), 0x0F000000, "ROR büyük harfle de çalışmalı")
raises(ValueError, lambda: bit_dondur32("shl", 1, 1), msg="bilinmeyen döndürme yönü için ValueError")

eq(iz_ozet_hesapla(b"AB\x00", 0x10), 0x064A, "AB ve 0x10 için gerçek CPU sonucu 0x064A")
eq(iz_ozet_hesapla(b"AB\x00SONRASI_OKUNMAZ", 0x10), 0x064A, "0x00 sonlandırıcıdan sonraki baytlar okunmamalı")
eq(iz_ozet_hesapla(b"OK", 0x05), 0x0373, "OK ve 0x05 için gerçek CPU sonucu 0x0373")
eq(iz_ozet_hesapla(b"\x00ABC", 0x99), 0x99, "ilk bayt 0x00 ise tohum değişmeden dönmeli")
eq(iz_ozet_hesapla(b"A", 0x20000000), (0x00000001 ^ 0x41), "rol 3 sırasında üstten taşan bit en sağa geçmeli")
```

```solution
def bit_dondur32(yon, deger, miktar):
    y = yon.strip().lower()
    u = deger & 0xFFFFFFFF
    k = miktar & 31
    if y == "rol":
        if k == 0:
            return u
        return ((u << k) | (u >> (32 - k))) & 0xFFFFFFFF
    if y == "ror":
        if k == 0:
            return u
        return ((u >> k) | (u << (32 - k))) & 0xFFFFFFFF
    raise ValueError(f"Gecersiz dondurme yonu: {yon}")


def iz_ozet_hesapla(veri, tohum):
    eax = tohum & 0xFFFFFFFF
    for b in veri:
        if b == 0:
            break
        eax = bit_dondur32("rol", eax, 3)
        eax ^= b
    return eax & 0xFFFFFFFF
```

```hint
32-bit sola döndürme için `((u << k) | (u >> (32 - k))) & 0xFFFFFFFF`, sağa döndürme için `((u >> k) | (u << (32 - k))) & 0xFFFFFFFF` kullan.
```
:::

::: gorev RIP-göreli adres ve kısa sıçrama (`eb` / `74`) hedef hesaplayıcısı
Bir komutun bulunduğu `komut_adresi`, `komut_uzunlugu` ve komutun içindeki işaretli göreli ofset (`goreli_ofset`) verildiğinde hedef bellek adresini hesaplayan `rip_hedef_hesapla(komut_adresi, komut_uzunlugu, goreli_ofset)` fonksiyonunu ve 2 baytlık kısa sıçrama (`eb <disp8>` veya `74 <disp8>`) ham bayt dizisini (`ham_baytlar`) alıp hedef adresi döndüren `kisa_sicrama_hedefi(komut_adresi, ham_baytlar)` fonksiyonunu yaz:
- `komut_adresi < 0` veya `komut_uzunlugu <= 0` ise `ValueError` fırlat.
- `kisa_sicrama_hedefi`: `len(ham_baytlar) != 2` ise `ValueError` fırlat. 2. bayt (`ham_baytlar[1]`) 8-bit **işaretli** (`>= 0x80` ise `- 0x100`) ofsettir ve komut uzunluğu `2`'dir.

```starter
def rip_hedef_hesapla(komut_adresi, komut_uzunlugu, goreli_ofset):
    return komut_adresi + goreli_ofset

def kisa_sicrama_hedefi(komut_adresi, ham_baytlar):
    return komut_adresi
```

```test
need("rip_hedef_hesapla")
need("kisa_sicrama_hedefi")
eq(rip_hedef_hesapla(0, 2, 5), 7, "0x0 adresindeki komut geçerli olmalı")
eq(rip_hedef_hesapla(0x40, 7, 0x2019), 0x2060, "0x40 + 7 + 0x2019 = 0x2060")
eq(kisa_sicrama_hedefi(0x0D, bytes.fromhex("74 0b")), 0x1A, "je 0x1a: 0x0d + 2 + 11 = 0x1a")
eq(kisa_sicrama_hedefi(0x18, bytes.fromhex("eb eb")), 0x05, "jmp 0x5: 0x18 + 2 + (-21) = 0x05")
eq(kisa_sicrama_hedefi(0x100, bytes.fromhex("75 80")), 0x100 + 2 - 128, "disp8=0x80 (-128) sınır testi")
raises(ValueError, lambda: rip_hedef_hesapla(-1, 2, 0), msg="negatif komut adresi için ValueError")
raises(ValueError, lambda: rip_hedef_hesapla(0x10, 0, 5), msg="0 uzunluklu komut için ValueError")
raises(ValueError, lambda: kisa_sicrama_hedefi(0x10, b"\xeb"), msg="1 baytlık eksik komut için ValueError")
raises(ValueError, lambda: kisa_sicrama_hedefi(0x10, b"\xeb\x00\x00"), msg="3 baytlık komut için ValueError")
```

```solution
def rip_hedef_hesapla(komut_adresi, komut_uzunlugu, goreli_ofset):
    if komut_adresi < 0 or komut_uzunlugu <= 0:
        raise ValueError("Gecersiz komut adresi veya uzunlugu")
    return komut_adresi + komut_uzunlugu + goreli_ofset


def kisa_sicrama_hedefi(komut_adresi, ham_baytlar):
    if len(ham_baytlar) != 2:
        raise ValueError("Kisa sicrama komutu 2 bayt olmalidir")
    disp8 = ham_baytlar[1]
    if disp8 >= 0x80:
        disp8 -= 0x100
    return rip_hedef_hesapla(komut_adresi, 2, disp8)
```

```hint
Hedef adres her zaman `komut_adresi + komut_uzunlugu + goreli_ofset` formülüyle bulunur; `disp8 >= 0x80` ise `disp8 - 256` ile işaretli değere çevir.
```
:::
