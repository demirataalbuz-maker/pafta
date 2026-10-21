---
id: as10
title: Bellek Güvenliği, Yığın Kanaryası ve Taşma Kalıpları
rank: basalti
order: 10
summary: Yığın tamponlarının dönüş adresine göre konumunu, derleyici kanaryasını (fs:0x28 / __security_cookie) ve tam sayı taşması (jo/jc) denetimlerini okumak.
---

::: anlat
Güvenlik araştırmalarında ve ikili dosya incelemelerinde disassembly okumanın en önemli amaçlarından biri, **sınır denetimlerinin doğru yapılıp yapılmadığını** ve **derleyici güvenlik önlemlerini (mitigations)** tespit etmektir.

### 1. Yığın Tamponu (Stack Buffer) ve Kanarya (`Stack Canary`)

Bir fonksiyonun içinde `char buf[64];` gibi yerel bir tampon bulunduğunda, yığın aşağı doğru büyüdüğü için tampon `[rbp - 80]` gibi düşük bir adresten başlar, ancak `memcpy` veya `gets`/`read` ile yazılırken **yukarı doğru (daha yüksek adreslere: `saved rbp` ve `saved rip` yönüne)** dolar:

| Yığın Adresi (Düşükten Yükseğe) | İçerik | Taşma Riski |
|---|---|---|
| `[rbp - 72] .. [rbp - 9]` | `char buf[64]` (Yerel tampon) | Yazma işlemi `[rbp - 72]`'den yukarı doğru ilerler |
| `[rbp - 8]` | **Yığın Kanaryası (Stack Canary)** | Tampon ile `saved rbp` arasındaki nöbetçi değer |
| `[rbp]` | Kaydedilmiş `rbp` (`saved rbp`) | Çağıranın çerçeve işaretçisi |
| `[rbp + 8]` | **Dönüş Adresi (`saved rip`)** | `ret` komutunun sıçrayacağı adres |

Derleyici `-fstack-protector-strong` (Linux GCC/Clang) veya `/GS` (Windows MSVC) ile derleme yaptığında prolog ve epilogda şu kalıbı görürsünüz:

```asm
; Linux x86-64 kanarya kalıbı (GCC/Clang -fstack-protector-strong):
    mov rax, QWORD PTR fs:0x28          #! Prolog: TLS'ten rastgele 64-bit kanarya değerini oku
    mov QWORD PTR [rbp - 8], rax        #! Tampon ile saved rbp arasına yerleştir
    xor eax, eax                        #! Kanarya değerini yazmaçta bırakma (sızıntı önlemi)
    ; ... fonksiyon gövdesi ...
    mov rdx, QWORD PTR [rbp - 8]        #! Epilog: Yığındaki kanaryayı geri oku
    sub rdx, QWORD PTR fs:0x28          #! Orijinal kanarya ile karşılaştır (veya xor)
    jne .L_kanarya_bozuldu              #! Değişmişse ret ÇALIŞMADAN programı durdur!
    leave
    ret
.L_kanarya_bozuldu:
    call __stack_chk_fail               #! Yalnızca bozulma dalında çağrılır ve süreci sonlandırır

; Windows x64 MSVC (/GS) güvenlik çerezi kalıbı:
    mov rax, QWORD PTR [__security_cookie] #! Prolog: Global çerezi oku
    xor rax, rsp                           #! Çerezi o anki rsp ile XOR'layıp çerçeveye bağla
    mov QWORD PTR [rsp + 0x48], rax        #! Tamponun üstüne kaydet
    ; ... fonksiyon gövdesi ...
    mov rcx, QWORD PTR [rsp + 0x48]        #! Epilog (her çıkışta): Kaydedilen çerezi rcx'e oku
    xor rcx, rsp                           #! rsp ile tekrar XOR'layıp orijinal çerezi geri elde et
    call __security_check_cookie           #! Her çıkışta çağrılır; eşleşmezse __report_gsfailure'a gider!
```

### 2. Tam Sayı Çarpım Taşması (`Integer Overflow`) ve `jo` / `jc`

Bellek ayırma veya kopyalama öncesinde `toplam_bayt = adet * eleman_boyutu` hesabı yapılırken, çarpım 32-bit veya 64-bit sınırını aşarsa **tam sayı taşması** oluşur ve sonuç beklenenden çok küçük çıkar. Güvenli derlenmiş kodda çarpımın hemen ardından **`jo`** (işaretli taşma: `OF == 1`) veya **`jc` / `jb`** (işaretsiz taşma: `CF == 1`) kontrolü yer alır:

```asm
; int as10_boyut_kontrol(int32_t adet, int32_t eleman_boyutu, uint32_t maks_bayt)
; Windows x64: ecx = adet, edx = eleman_boyutu, r8d = maks_bayt
as10_boyut_kontrol:
    mov eax, ecx            #! eax = adet
    imul eax, edx           #! eax = adet * eleman_boyutu (32-bit işaretli çarpım)
    jo .L_tasma             #! OF == 1 ise (32-bit işaretli sınır aşıldıysa) .L_tasma'ya sıçra!
    cmp eax, r8d            #! Toplam boyutu maks_bayt (r8d) ile karşılaştır
    ja .L_buyuk             #! İşaretsiz olarak eax > maks_bayt (veya eax negatif) ise reddet!
    ret                     #! Güvenli: toplam bayt sayısını (eax) döndür
.L_tasma:
    mov eax, -1             #! Çarpım taşması hatası: -1
    ret
.L_buyuk:
    mov eax, -2             #! Sınır aşımı hatası: -2
    ret
```

> [!GÜVENLİK]
> Yukarıdaki kodda `cmp eax, r8d` sonrasında `jg` (işaretli) yerine **`ja` (işaretsiz)** kullanılması aynı anda iki koruma sağlar: hem `eax > maks_bayt` olan pozitif değerleri yakalar hem de negatif bir `eax` (`0x80000000..0xFFFFFFFF`) oluşmuşsa işaretsiz olarak çok büyük görüneceği için `.L_buyuk` dalına düşürür.
:::

::: tahmin
```asm
; Windows x64: ecx = adet, edx = eleman_boyutu, r8d = maks_bayt
as10_boyut_kontrol:
    mov eax, ecx
    imul eax, edx
    jo .L_tasma
    cmp eax, r8d
    ja .L_buyuk
    ret
.L_tasma:
    mov eax, -1
    ret
.L_buyuk:
    mov eax, -2
    ret

; Çağrılar:
; 1) as10_boyut_kontrol(16, 4, 128)
; 2) as10_boyut_kontrol(40, 4, 128)
; 3) as10_boyut_kontrol(0x10000, 0x10000, 1024)
```

Yukarıdaki `as10_boyut_kontrol` fonksiyonu 3 farklı argüman üçlüsüyle çağrıldığında dönen üç satırlık çıktı nedir?

```gercek
64
-2
-1
```

???
1. çağrı `(16, 4, 128)`: `imul eax, edx` sonucu `16 * 4 = 64` olur ve 32-bit işaretli sınırlar içinde kaldığı için `OF = 0` (`jo` sıçramaz). `cmp 64, 128` sonrasında `64 <= 128` olduğu için `ja` sıçramaz ve `64` döner.
2. çağrı `(40, 4, 128)`: `40 * 4 = 160` (`OF = 0`), ancak `cmp 160, 128` sonrasında `160 > 128` olduğu için `ja .L_buyuk` sıçrar ve `-2` döner.
3. çağrı `(0x10000, 0x10000, 1024)`: `65536 * 65536 = 0x100000000` çarpımı 32-bit işaretli aralığı (`-2147483648 .. 2147483647`) aştığı için `imul` taşma bayrağını (`OF = 1`) yakar (`eax` alt 32-bitte `0` olsa bile!). `jo .L_tasma` taşmayı yakalar ve `-1` döner.
:::

::: gorev Tam sayı taşması (`imul` + `jo`) ve işaretsiz sınır (`ja`) denetimi
Yukarıdaki `as10_boyut_kontrol` assembly fonksiyonunun davranışını birebir modelleyen `guvenli_boyut_kontrol(adet, eleman_boyutu, maks_bayt)` fonksiyonunu yaz:
- `adet` ve `eleman_boyutu` 32-bit işaretli tam sayılardır.
- Gerçek matematiksel çarpım `carpim = s_adet * s_boyut` 32-bit işaretli aralığın (`-2147483648 .. 2147483647`) dışına çıkıyorsa (`imul` + `jo .L_tasma`), `-1` döndür.
- Taşma yoksa 32-bit işaretsiz karşılığını (`u_carpim = carpim & 0xFFFFFFFF`) `maks_bayt & 0xFFFFFFFF` ile karşılaştır; `u_carpim > (maks_bayt & 0xFFFFFFFF)` ise (`ja .L_buyuk`) `-2` döndür.
- Her iki kontrolden de geçerse `carpim` değerini döndür.

```starter
def guvenli_boyut_kontrol(adet, eleman_boyutu, maks_bayt):
    return adet * eleman_boyutu
```

```test
need("guvenli_boyut_kontrol")
eq(guvenli_boyut_kontrol(16, 4, 128), 64, "16 * 4 = 64 <= 128 güvenli")
eq(guvenli_boyut_kontrol(32, 4, 128), 128, "32 * 4 = 128 tam sınırda güvenli (ja sıçramaz)")
eq(guvenli_boyut_kontrol(33, 4, 128), -2, "33 * 4 = 132 > 128 sınır aşımı -> -2")
eq(guvenli_boyut_kontrol(0, 4, 128), 0, "0 * 4 = 0 güvenli")
eq(guvenli_boyut_kontrol(0x10000, 0x10000, 1024), -1, "65536 * 65536 = 2^32 taşması jo ile yakalanmalı -> -1")
eq(guvenli_boyut_kontrol(0x40000000, 2, 1024), -1, "2^30 * 2 = 2^31 işaretli pozitif taşma -> -1")
eq(guvenli_boyut_kontrol(0x7FFFFFFF, 1, 0x80000000), 0x7FFFFFFF, "0x7FFFFFFF * 1 tam işaretli üst sınırdadır (taşmaz)")
eq(guvenli_boyut_kontrol(0x80000000, 1, 1024), -2, "-2147483648 * 1 işaretli taşmaz (OF=0), işaretsiz ja sınırına takılır -> -2")
eq(guvenli_boyut_kontrol(-4, 4, 128), -2, "negatif çarpım (-16) işaretsiz ja karşılaştırmasında reddedilir -> -2")
```

```solution
def _s32(x):
    u = x & 0xFFFFFFFF
    return u - 0x100000000 if u >= 0x80000000 else u


def guvenli_boyut_kontrol(adet, eleman_boyutu, maks_bayt):
    s_adet = _s32(adet)
    s_boyut = _s32(eleman_boyutu)
    carpim = s_adet * s_boyut
    if carpim < -0x80000000 or carpim > 0x7FFFFFFF:
        return -1
    u_carpim = carpim & 0xFFFFFFFF
    u_maks = maks_bayt & 0xFFFFFFFF
    if u_carpim > u_maks:
        return -2
    return carpim
```

```hint
Önce `s_adet * s_boyut` çarpımının `[-0x80000000, 0x7FFFFFFF]` aralığında olup olmadığını kontrol et (`-1`), ardından `carpim & 0xFFFFFFFF > maks_bayt & 0xFFFFFFFF` kontrolü yap (`-2`).
```
:::

::: gorev Yığın çerçevesinde kanarya, `saved rbp` ve `saved rip` taşma analizi
Bir fonksiyonun yığın çerçevesinde yerel tampon `[rbp - buf_ofset]` adresinden başlayıp yukarı doğru yazılırken, `[rbp - kanarya_ofset]` adresinde 8 baytlık kanarya, `[rbp]` adresinde 8 baytlık `saved rbp` ve `[rbp + 8]` adresinde 8 baytlık `saved rip` bulunduğunu düşün. Tampona `yazilan_bayt` uzunluğunda veri yazıldığında hangi kritik bölgelerin üzerine yazıldığını raporlayan `yigin_tasma_analizi(buf_ofset, kanarya_ofset, yazilan_bayt)` fonksiyonunu yaz:
- Dönüş sözlüğü şu üç anahtarı içermelidir:
  - `"kanarya_bozuldu"`: `yazilan_bayt > buf_ofset - kanarya_ofset`
  - `"rbp_bozuldu"`: `yazilan_bayt > buf_ofset`
  - `"rip_bozuldu"`: `yazilan_bayt > buf_ofset + 8`
- `buf_ofset <= kanarya_ofset`, `kanarya_ofset < 8` veya `yazilan_bayt < 0` ise `ValueError` fırlat.

```starter
def yigin_tasma_analizi(buf_ofset, kanarya_ofset, yazilan_bayt):
    return {"kanarya_bozuldu": False, "rbp_bozuldu": False, "rip_bozuldu": False}
```

```test
need("yigin_tasma_analizi")
eq(
    yigin_tasma_analizi(72, 8, 0),
    {"kanarya_bozuldu": False, "rbp_bozuldu": False, "rip_bozuldu": False},
    "0 bayt yazıldığında hiçbir alan bozulmaz",
)
eq(
    yigin_tasma_analizi(72, 8, 64),
    {"kanarya_bozuldu": False, "rbp_bozuldu": False, "rip_bozuldu": False},
    "64 baytlık tampona tam 64 bayt yazıldığında kanarya bozulmaz",
)
eq(
    yigin_tasma_analizi(72, 8, 65),
    {"kanarya_bozuldu": True, "rbp_bozuldu": False, "rip_bozuldu": False},
    "65. bayt kanaryanın ilk baytını bozar",
)
eq(
    yigin_tasma_analizi(72, 8, 72),
    {"kanarya_bozuldu": True, "rbp_bozuldu": False, "rip_bozuldu": False},
    "72 bayt kanaryayı tamamen ezer ama saved rbp'ye henüz ulaşmaz",
)
eq(
    yigin_tasma_analizi(72, 8, 73),
    {"kanarya_bozuldu": True, "rbp_bozuldu": True, "rip_bozuldu": False},
    "73. bayt saved rbp'nin ilk baytını bozar",
)
eq(
    yigin_tasma_analizi(72, 8, 80),
    {"kanarya_bozuldu": True, "rbp_bozuldu": True, "rip_bozuldu": False},
    "80 bayt saved rbp'yi ezer ama saved rip'e henüz ulaşmaz",
)
eq(
    yigin_tasma_analizi(72, 8, 81),
    {"kanarya_bozuldu": True, "rbp_bozuldu": True, "rip_bozuldu": True},
    "81. bayt dönüş adresinin (saved rip) üzerine yazar",
)
raises(ValueError, lambda: yigin_tasma_analizi(8, 8, 10), msg="buf_ofset <= kanarya_ofset için ValueError")
raises(ValueError, lambda: yigin_tasma_analizi(72, 4, 10), msg="kanarya_ofset < 8 için ValueError")
raises(ValueError, lambda: yigin_tasma_analizi(72, 8, -1), msg="negatif yazilan_bayt için ValueError")
```

```solution
def yigin_tasma_analizi(buf_ofset, kanarya_ofset, yazilan_bayt):
    if kanarya_ofset < 8 or buf_ofset <= kanarya_ofset or yazilan_bayt < 0:
        raise ValueError("Gecersiz cerceve ofsetleri veya yazilan bayt")
    tampon_kapasite = buf_ofset - kanarya_ofset
    return {
        "kanarya_bozuldu": yazilan_bayt > tampon_kapasite,
        "rbp_bozuldu": yazilan_bayt > buf_ofset,
        "rip_bozuldu": yazilan_bayt > buf_ofset + 8,
    }
```

```hint
Tampon `[rbp - buf_ofset]` adresinden yukarı doğru büyüdüğü için kanaryaya uzaklığı `buf_ofset - kanarya_ofset`, `saved rbp`'ye uzaklığı `buf_ofset` ve `saved rip`'e uzaklığı `buf_ofset + 8` bayttır.
```
:::
