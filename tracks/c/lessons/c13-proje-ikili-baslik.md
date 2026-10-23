---
id: c13
title: Proje · İkili Dosya Ayrıştırıcı
summary: Bir ikili dosya biçiminin C tanımını okuyup Python'da güvenli bir ayrıştırıcı kurmak; paketlenmiş başlık ve kayıt yapıları, imza ve sürüm denetimi, taşmaya dayanıklı sınır denetimleri, hata kodları ve kayıt tablosundan içerik çıkarmak.
---

::: anlat Proje tanımı
Bir izleme cihazı ölçümlerini kendi ikili biçiminde (`.pft`) saklıyor. Elinde yalnızca cihazın yazılımındaki C tanımları var. Görevin, bu tanımları okuyup aynı dosyaları **güvenle** okuyan bir Python ayrıştırıcısı kurmak. Ayrıştırıcıya gelen dosya bozuk, kesik ya da kasıtlı olarak tutarsız olabilir.

```c
#pragma pack(push, 1)
typedef struct {
    char     imza[4];        // "PFTA"
    uint16_t surum;          // şu an 1
    uint16_t kayit_sayisi;   // tablodaki kayıt sayısı
    uint32_t tablo_ofseti;   // kayıt tablosunun dosyadaki konumu
} Baslik;                    // 12 bayt, little endian

typedef struct {
    uint32_t ofset;          // kaydın içeriğinin dosyadaki konumu
    uint32_t uzunluk;        // içeriğin bayt sayısı
    uint8_t  tur;            // 1: ölçüm, 2: olay, 3: not
    uint8_t  bayrak;
    uint16_t ayrilmis;       // kullanılmıyor (0)
} Kayit;                     // 12 bayt
#pragma pack(pop)

int dogrula(const uint8_t *veri, size_t boyut) {
    if (boyut < sizeof(Baslik)) return -1;                     // başlık sığmıyor
    const Baslik *b = (const Baslik *)veri;
    if (memcmp(b->imza, "PFTA", 4) != 0) return -2;            // imza yanlış
    if (b->surum != 1) return -3;                              // desteklenmeyen sürüm
    uint64_t tablo_sonu = (uint64_t)b->tablo_ofseti
                        + (uint64_t)b->kayit_sayisi * sizeof(Kayit);
    if (tablo_sonu > boyut) return -4;                         // tablo dosyanın dışına taşıyor
    const Kayit *k = (const Kayit *)(veri + b->tablo_ofseti);
    for (uint16_t i = 0; i < b->kayit_sayisi; i++) {
        if ((uint64_t)k[i].ofset + k[i].uzunluk > boyut) return -5;   // içerik dışarıda
    }
    return b->kayit_sayisi;                                    // geçerli: kayıt sayısı
}
```

### Okurken dikkat ettiklerin
- `#pragma pack(1)`: yapılarda dolgu yok (C07); başlık tam 12 bayt, her kayıt tam 12 bayt.
- Bütün çok baytlı alanlar **little endian** (C05, C08).
- Toplamalar `uint64_t` ile yapılıyor: `tablo_ofseti` ve `ofset` 32 bitlik olduğu için 32 bitte toplansalar **taşıp** küçük bir sayıya sarabilir ve denetimi atlatabilirlerdi (C06).
- Denetimler belirli bir **sırada**: önce başlığın sığdığı, sonra imza, sonra sürüm, sonra tablo, en son kayıtlar. Bir alanı okumadan önce o alanın dosyada olduğunu kanıtlamış olmak gerekir.

### Python'da: struct modülü
Python'un `struct` modülü C yapılarını biçim dizgileriyle okur:

| Biçim | Anlamı |
|---|---|
| `<` | little endian, dolgu yok |
| `4s` | 4 baytlık bayt dizisi |
| `H` | uint16 |
| `I` | uint32 |
| `B` | uint8 |

`struct.unpack_from("<4sHHI", veri, 0)` başlığın dört alanını bir demet olarak verir; `struct.calcsize("<4sHHI")` 12'dir.

> [!NOT]
> C kodundaki `(const Baslik *)veri` dönüşümü kısa ama **tanımsız davranıştır**. `veri` bir `uint8_t` dizisidir; C, bir nesneyi kendi türüyle uyuşmayan bir türden (burada `uint16_t` ve `uint32_t` alanlı `Baslik`) okumayı yasaklar. Buna katı takma ad kuralı denir (C11 6.5p7). Derleyici kurala uyulduğunu varsayarak kodu iyileştirir: x86-64'te bugün doğru çıkan sonuç (aşağıdaki tahmindeki gibi) dilin garantisi değildir, başka bir derleyicide ya da `-O` düzeyinde bozulabilir. `pack(1)` olmayan bir yapıda bir de hizalanmamış adresten okuma sorunu çıkar; bazı işlemciler bunda hata verir. Doğru yol, boyut denetiminden sonra baytları `memcpy` ile yerel bir yapıya kopyalamaktır:
>
> ```c
> Baslik b;
> memcpy(&b, veri, sizeof b);                    // boyut >= sizeof b denetlendikten sonra
> if (memcmp(b.imza, "PFTA", 4) != 0) return -2;
> if (b.surum != 1) return -3;
> ```
>
> `memcpy` baytları olduğu gibi taşır, hiçbir nesne yanlış türle okunmaz; derleyici bunu genellikle tek bir okuma komutuna çevirir. Kayıtlar da aynı yolla tek tek kopyalanır. Python'da `struct.unpack_from` baytları zaten bu şekilde okur.
:::

::: tahmin
Bu 12 bayt başlık olarak okunduğunda `kayit_sayisi` ve `tablo_ofseti` ne olur?

```c
uint8_t veri[12] = { 'P','F','T','A', 0x01,0x00, 0x02,0x00, 0x0C,0x00,0x00,0x00 };
const Baslik *b = (const Baslik *)veri;
printf("%u %u %u\n", b->surum, b->kayit_sayisi, b->tablo_ofseti);
```

```gercek
1 2 12
```

???

`1 2 12`. Alanlar little endian: `01 00` → 1, `02 00` → 2, `0C 00 00 00` → 12. Kayıt tablosu hemen başlığın arkasından, 12. bayttan başlıyor.
:::

::: gorev 1 · Başlığı oku
`baslik_oku(veri)` fonksiyonunu yaz: `veri` başlığı içermeyecek kadar kısaysa `None`, değilse `{"imza": ..., "surum": ..., "kayit_sayisi": ..., "tablo_ofseti": ...}` sözlüğünü döndürsün (`imza` 4 baytlık `bytes`).

```starter
def baslik_oku(veri):
    return {"imza": veri[:4], "surum": veri[4], "kayit_sayisi": veri[6], "tablo_ofseti": veri[8]}
```

```test
import struct
need("baslik_oku")
b = struct.pack("<4sHHI", b"PFTA", 1, 2, 12)
eq(baslik_oku(b), {"imza": b"PFTA", "surum": 1, "kayit_sayisi": 2, "tablo_ofseti": 12}, "küçük değerler")
b2 = struct.pack("<4sHHI", b"PFTA", 1, 300, 70000)
eq(baslik_oku(b2), {"imza": b"PFTA", "surum": 1, "kayit_sayisi": 300, "tablo_ofseti": 70000}, "çok baytlı değerler")
eq(baslik_oku(b"PFTA\x01\x00"), None, "kesik başlık")
eq(baslik_oku(b""), None, "boş dosya")
```

```solution
import struct

BASLIK = struct.Struct("<4sHHI")


def baslik_oku(veri):
    if len(veri) < BASLIK.size:
        return None
    imza, surum, kayit_sayisi, tablo_ofseti = BASLIK.unpack_from(veri, 0)
    return {"imza": imza, "surum": surum, "kayit_sayisi": kayit_sayisi, "tablo_ofseti": tablo_ofseti}
```

```hint
Başlangıç kodu çok baytlı alanların yalnızca ilk baytını okuyor. `struct.unpack_from("<4sHHI", veri, 0)` dört alanı doğru okur.
```

```hint
Önce uzunluğu denetle: `len(veri) < 12` ise `None`.
```
:::

::: gorev 2 · Doğrula
C'deki `dogrula` fonksiyonunu aynı dönüş kodlarıyla (−1 … −5 ya da kayıt sayısı) Python'da yaz.

```starter
def dogrula(veri):
    if veri[:4] != b"PFTA":
        return -2
    return veri[6]
```

```test
import struct
need("dogrula")
def dosya(imza=b"PFTA", surum=1, kayitlar=(), tablo_ofseti=None, ek=b""):
    kayit_sayisi = len(kayitlar)
    if tablo_ofseti is None:
        tablo_ofseti = 12
    gövde = b"".join(struct.pack("<IIBBH", *k) for k in kayitlar)
    return struct.pack("<4sHHI", imza, surum, kayit_sayisi, tablo_ofseti) + gövde + ek

icerik = b"cpu=72;bellek=61"
iyi = dosya(kayitlar=[(36, len(icerik), 1, 0, 0), (36, 6, 3, 0, 0)], ek=icerik)
eq(dogrula(iyi), 2, "geçerli dosya: 2 kayıt")
eq(dogrula(iyi[:10]), -1, "başlık sığmıyor")
eq(dogrula(dosya(imza=b"PFTX")), -2, "yanlış imza")
eq(dogrula(dosya(surum=2)), -3, "desteklenmeyen sürüm")
eq(dogrula(dosya(kayitlar=[(0, 0, 1, 0, 0)])[:20]), -4, "kesik tablo")
eq(dogrula(dosya(kayitlar=[(36, 100, 1, 0, 0)], ek=b"az")), -5, "içerik dosyanın dışında")
eq(dogrula(dosya(kayitlar=[(0xFFFFFFF0, 0x20, 1, 0, 0)])), -5, "32 bitte sarabilecek toplam da yakalanır")
eq(dogrula(dosya(kayitlar=[(1, 1, 1, 0, 0)], tablo_ofseti=0xFFFFFFFF)), -4, "dev tablo ofseti")
eq(dogrula(dosya()), 0, "kayıtsız geçerli dosya")
```

```solution
import struct

BASLIK = struct.Struct("<4sHHI")
KAYIT = struct.Struct("<IIBBH")


def dogrula(veri):
    boyut = len(veri)
    if boyut < BASLIK.size:
        return -1
    imza, surum, kayit_sayisi, tablo_ofseti = BASLIK.unpack_from(veri, 0)
    if imza != b"PFTA":
        return -2
    if surum != 1:
        return -3
    if tablo_ofseti + kayit_sayisi * KAYIT.size > boyut:
        return -4
    for i in range(kayit_sayisi):
        ofset, uzunluk, _, _, _ = KAYIT.unpack_from(veri, tablo_ofseti + i * KAYIT.size)
        if ofset + uzunluk > boyut:
            return -5
    return kayit_sayisi
```

```hint
Sıra önemli: uzunluk (−1), imza (−2), sürüm (−3), tablo (−4), kayıtlar (−5). Python'un tam sayıları taşmadığı için `uint64_t` dönüşümüne gerek yok; toplamı doğrudan karşılaştır.
```

```hint
Kayıt `i`, `tablo_ofseti + i * 12` konumundadır: `struct.unpack_from("<IIBBH", veri, konum)`.
```
:::

::: gorev 3 · Kayıtları çıkar
`kayitlari_oku(veri)` fonksiyonunu yaz: dosya geçersizse (`dogrula` negatif dönerse) boş liste, geçerliyse her kayıt için `{"tur": ..., "bayrak": ..., "icerik": ...}` sözlüklerinin listesini döndürsün (`icerik`: kaydın gösterdiği baytlar). Önceki görevlerin fonksiyonlarını bu görevin kodunda da tanımla.

```starter
def kayitlari_oku(veri):
    return []
```

```test
import struct
need("kayitlari_oku")
icerik = b"cpu=72;bellek=61"
not_ = b"bakim"
govde = struct.pack("<IIBBH", 36, len(icerik), 1, 0, 0) + struct.pack("<IIBBH", 36 + len(icerik), len(not_), 3, 1, 0)
iyi = struct.pack("<4sHHI", b"PFTA", 1, 2, 12) + govde + icerik + not_
eq(kayitlari_oku(iyi), [{"tur": 1, "bayrak": 0, "icerik": b"cpu=72;bellek=61"},
                        {"tur": 3, "bayrak": 1, "icerik": b"bakim"}], "iki kayıt")
eq(kayitlari_oku(iyi[:30]), [], "kesik dosya: hiçbir şey okunmaz")
eq(kayitlari_oku(b"XXXX" + iyi[4:]), [], "yanlış imza")
sonda = struct.pack("<4sHHI", b"PFTA", 1, 1, 16) + b"ping" + struct.pack("<IIBBH", 12, 4, 2, 0, 0)
eq(kayitlari_oku(sonda), [{"tur": 2, "bayrak": 0, "icerik": b"ping"}], "kayıt tablosu dosyanın tam sonunda bitiyor")
need("dogrula")
eq(dogrula(struct.pack("<4sHHI", b"PFTA", 1, 0, 12)), 0, "yalnızca başlık (12 bayt, 0 kayıt) geçerli")
```

```solution
import struct

BASLIK = struct.Struct("<4sHHI")
KAYIT = struct.Struct("<IIBBH")


def dogrula(veri):
    boyut = len(veri)
    if boyut < BASLIK.size:
        return -1
    imza, surum, kayit_sayisi, tablo_ofseti = BASLIK.unpack_from(veri, 0)
    if imza != b"PFTA":
        return -2
    if surum != 1:
        return -3
    if tablo_ofseti + kayit_sayisi * KAYIT.size > boyut:
        return -4
    for i in range(kayit_sayisi):
        ofset, uzunluk, _, _, _ = KAYIT.unpack_from(veri, tablo_ofseti + i * KAYIT.size)
        if ofset + uzunluk > boyut:
            return -5
    return kayit_sayisi


def kayitlari_oku(veri):
    if dogrula(veri) < 0:
        return []
    _, _, kayit_sayisi, tablo_ofseti = BASLIK.unpack_from(veri, 0)
    sonuc = []
    for i in range(kayit_sayisi):
        ofset, uzunluk, tur, bayrak, _ = KAYIT.unpack_from(veri, tablo_ofseti + i * KAYIT.size)
        sonuc.append({"tur": tur, "bayrak": bayrak, "icerik": veri[ofset:ofset + uzunluk]})
    return sonuc
```

```hint
Önce `dogrula`; negatifse hiçbir alana dokunmadan `[]` döndür. Doğrulanmamış bir ofsetten okumamak, C'de bellek hatasını, Python'da sessizce kesik veriyi önler.
```

```hint
Her kayıt için `veri[ofset:ofset + uzunluk]` içeriktir.
```
:::
