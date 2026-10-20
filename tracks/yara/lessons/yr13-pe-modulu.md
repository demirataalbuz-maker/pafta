---
id: yr13
title: PE Modülü · Dosya Biçimini Tanımak
summary: MZ başlığıyla yetinme; pe.is_pe, makine türü, bölüm sayısı ve DLL bayrağını değerlendir.
---

::: anlat Başlık işareti ile geçerli yapı aynı şey değil
Windows PE dosyaları çoğu kez MZ ile başlar; fakat MZ yazan her veri bir PE değildir. `import "pe"` ile gerçek YARA PE modülünü kullanırsın. `pe.is_pe` motorun dosyayı PE olarak tanıyıp tanımadığını söyler; ardından makine türü, bölüm sayısı ve özellikler okunabilir.

Bu dersin testleri sıfırdan oluşturulmuş **etkisiz PE başlıkları ve LABDATA baytlarıdır**. Bir dosyayı açıp çalıştırma yoktur. Amaç örnek malware arşivi biriktirmek değil, dosya biçimi şartlarını doğru kurmaktır. PE olması ya da DLL olması tek başına kötü amaçlılık anlamına gelmez.

```yara
import "pe"
rule PE_Ornek { condition: pe.is_pe and pe.machine == pe.MACHINE_I386 }
```
:::

::: anlat Alanlar, bayraklar ve tanımsız değerler
`pe.machine` COFF makine alanıdır; `pe.number_of_sections` bölüm sayısıdır. `pe.characteristics` bir bit kümesidir: `pe.characteristics & pe.DLL` sıfır değilse DLL bayrağı vardır. Bu bir metin karşılaştırması değildir.

PE olmayan veride birçok modül alanı tanımsız kalabilir; `pe.is_pe` ön şartı hem niyeti hem okuma sırasını netleştirir. Gerçek incelemelerde importlar, exportlar, bölüm adları ve imza bilgileri de yararlı olabilir; bir alanı bütün aile için zorunlu kılmadan önce farklı derleyici ve sürüm örnekleriyle sınamak gerekir.

Kaynak: [Resmî YARA belgeleri](https://yara.readthedocs.io/en/stable/modules/pe.html).
:::

::: tahmin
Girdi kutusundaki veriyi bu kuralla tara. Hangi kural adı yazılır; neden?

```yara
import "pe"
rule PE_Degil { condition: not pe.is_pe }
```

```stdin
MZ bu sadece bir metin
```

???

`PE_Degil` eşleşir. MZ ile başlamak motorun PE yapısı tanıması için yeterli değildir.
:::

::: gorev Gerçek PE ve makine alanı
`PE_32` kuralı PE olarak tanınan, makine alanı `pe.MACHINE_I386` olan veriyi yakalasın.

```starter
// Koşulları ve gereken bölümleri görev metnine göre tamamla.
rule PE_32 { condition: false }
```

```test
def pe_ornegi(machine=0x14c, sections=1, dll=False):
    import struct
    data = bytearray(0x200 * (sections + 1))
    data[:2] = b"MZ"
    struct.pack_into("<I", data, 0x3c, 0x80)
    data[0x80:0x84] = b"PE\x00\x00"
    struct.pack_into("<HHIIIHH", data, 0x84, machine, sections, 0, 0, 0, 0xe0, 0x0102 | (0x2000 if dll else 0))
    off = 0x98
    struct.pack_into("<H", data, off, 0x10b)
    struct.pack_into("<I", data, off + 16, 0x1000)
    struct.pack_into("<I", data, off + 20, 0x1000)
    struct.pack_into("<I", data, off + 28, 0x400000)
    struct.pack_into("<II", data, off + 32, 0x1000, 0x200)
    struct.pack_into("<HH", data, off + 40, 4, 0)
    struct.pack_into("<II", data, off + 56, 0x1000 * (sections + 1), 0x200)
    struct.pack_into("<H", data, off + 68, 3)
    struct.pack_into("<I", data, off + 92, 16)
    for i in range(sections):
        sec = 0x178 + i * 40
        name = (".lab" + str(i)).encode("ascii")
        data[sec:sec + len(name)] = name
        struct.pack_into("<IIII", data, sec + 8, 8, 0x1000 * (i + 1), 0x200, 0x200 * (i + 1))
        struct.pack_into("<I", data, sec + 36, 0x40000040)
        data[0x200 * (i + 1):0x200 * (i + 1) + 8] = b"LABDATA!"
    return bytes(data)

ok(eslesir(pe_ornegi(), "PE_32"), "sentetik I386 PE")
ok(not eslesir(pe_ornegi(machine=0x8664), "PE_32"), "makine alanı farklı")
ok(not eslesir(b"MZ" + b"x" * 500, "PE_32"), "yalnız MZ yeterli değil")
ok(not eslesir(b"normal text", "PE_32"), "PE olmayan veri")
```

```solution
import "pe"
rule PE_32 { condition: pe.is_pe and pe.machine == pe.MACHINE_I386 }
```

```hint
Önce import "pe", sonra pe.is_pe ile pe.machine koşullarını birleştir.
```
:::

::: gorev İki bölümlü DLL
`PE_DLL` kuralı PE, DLL bayrağı set edilmiş ve tam iki bölümlü dosyaları istesin.

```starter
// Koşulları ve gereken bölümleri görev metnine göre tamamla.
rule PE_DLL { condition: false }
```

```test
def pe_ornegi(machine=0x14c, sections=1, dll=False):
    import struct
    data = bytearray(0x200 * (sections + 1))
    data[:2] = b"MZ"
    struct.pack_into("<I", data, 0x3c, 0x80)
    data[0x80:0x84] = b"PE\x00\x00"
    struct.pack_into("<HHIIIHH", data, 0x84, machine, sections, 0, 0, 0, 0xe0, 0x0102 | (0x2000 if dll else 0))
    off = 0x98
    struct.pack_into("<H", data, off, 0x10b)
    struct.pack_into("<I", data, off + 16, 0x1000)
    struct.pack_into("<I", data, off + 20, 0x1000)
    struct.pack_into("<I", data, off + 28, 0x400000)
    struct.pack_into("<II", data, off + 32, 0x1000, 0x200)
    struct.pack_into("<HH", data, off + 40, 4, 0)
    struct.pack_into("<II", data, off + 56, 0x1000 * (sections + 1), 0x200)
    struct.pack_into("<H", data, off + 68, 3)
    struct.pack_into("<I", data, off + 92, 16)
    for i in range(sections):
        sec = 0x178 + i * 40
        name = (".lab" + str(i)).encode("ascii")
        data[sec:sec + len(name)] = name
        struct.pack_into("<IIII", data, sec + 8, 8, 0x1000 * (i + 1), 0x200, 0x200 * (i + 1))
        struct.pack_into("<I", data, sec + 36, 0x40000040)
        data[0x200 * (i + 1):0x200 * (i + 1) + 8] = b"LABDATA!"
    return bytes(data)

ok(eslesir(pe_ornegi(sections=2, dll=True), "PE_DLL"), "iki bölüm ve DLL")
ok(not eslesir(pe_ornegi(sections=2, dll=False), "PE_DLL"), "DLL bayrağı yok")
ok(not eslesir(pe_ornegi(sections=1, dll=True), "PE_DLL"), "bölüm sayısı yanlış")
ok(not eslesir(b"MZ", "PE_DLL"), "eksik yapı")
```

```solution
import "pe"
rule PE_DLL { condition: pe.is_pe and (pe.characteristics & pe.DLL) != 0 and pe.number_of_sections == 2 }
```

```hint
Bayrak alanı bit düzeyindedir; & ile test edilir.
```
:::
