---
id: yr15
title: Math Modülü · Dağılım Bir Bulgudur
summary: Entropy, mean ve percentage ile veriyi ölç; ölçümü tek başına hüküm sayma.
---

::: anlat Entropi neyi ölçer?
`math.entropy(0, filesize)` bayt değerlerinin dağılımından bir ölçü üretir. Hep aynı bayttan oluşan veri düşük; 0..255 değerleri dengeli dağılan veri yüksek entropilidir. Bu ölçüm bir şifreleme ya da kötü amaçlılık ispatı değildir: sıkıştırılmış zararsız bir görsel de yüksek değer verebilir.

Gerçekçi bir koşul, dosya biçimi işaretini ve boyut sınırını dağılım bilgisiyle birlikte kullanır. Ayrıca çok kısa örneklerde istatistik kararsız olabilir. Eğitim görevleri sonucu belirli, sentetik veriler kullanır; rastgele sayı üretmeye dayanmaz.

```yara
import "math"
rule Tekrarli {
    condition:
        filesize >= 16 and math.entropy(0, filesize) < 1.0
}
```
:::

::: anlat Ortalama ile bayt oranı aynı ölçüm değil
`math.mean(0, filesize)` baytların sayısal ortalamasını verir. `math.percentage(0x00)` ise sıfır baytlarının dosyadaki oranıdır; 0 ile 1 arasında değer döner. `math.count(0x00)` oran değil, sayıdır. Fonksiyonun birimini anlamadan eşik yazma.

Bir ölçüm koşulunu doğrularken eşik altı, eşik üstü ve biçimi yanlış örnekleri ayrı tut. Son derste bu olumlu/olumsuz kümesini regresyon test paketine dönüştüreceğiz. İstatistiksel bir özellik bir dosyayı tek başına güvenilir veya zararlı ilan etmez.

Kaynak: [Resmî YARA belgeleri](https://yara.readthedocs.io/en/stable/modules/math.html).
:::

::: tahmin
Girdi kutusundaki veriyi bu kuralla tara. Hangi kural adı yazılır; neden?

```yara
import "math"
rule Tekrarli {
    condition:
        filesize >= 16 and math.entropy(0, filesize) < 1.0
}
```

```stdin
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
```

???

`Tekrarli` eşleşir; veri yeterince uzundur ve tek bayt değeri tekrarlandığı için entropisi düşüktür.
:::

::: gorev Biçim ve yüksek dağılım
`Dengeli_Lab` kuralı `LABPACK` ile başlayan, en az 512 baytlık ve bütün dosya entropisi 7.5'ten büyük veriyi yakalasın.

```starter
// Koşulları ve gereken bölümleri görev metnine göre tamamla.
rule Dengeli_Lab { condition: false }
```

```test
ok(eslesir(b"LABPACK" + bytes(range(256)) * 2, "Dengeli_Lab"), "biçim ve dengeli dağılım")
ok(not eslesir(b"LABPACK" + b"A" * 600, "Dengeli_Lab"), "düşük entropi")
ok(not eslesir(b"OTHERXX" + bytes(range(256)) * 2, "Dengeli_Lab"), "dağılım tek başına yetmez")
ok(not eslesir(b"LABPACK" + bytes(range(128)), "Dengeli_Lab"), "kısa örnek")
for boyut in (511, 512, 513):
    veri = b"LABPACK" + (bytes(range(256)) * 2)[:boyut - 7]
    eq(eslesir(veri, "Dengeli_Lab"), boyut >= 512, f"yüksek entropide boyut sınırının komşusu: {boyut} bayt")

def entropi_ornegi(yon):
    # 512 baytta 128 sembol ikişer, 64 sembol dörder: H = 7.5 tam.
    # Bir sayımı taşımak aynı boyutta eşiğin alt/üst komşu dağılımını verir.
    from collections import Counter
    sayilar = Counter({bayt: 2 for bayt in range(128)})
    sayilar.update({bayt: 4 for bayt in range(128, 192)})
    sayilar[0] += yon
    sayilar[128] -= yon
    baslik = b"LABPACK"
    sayilar.subtract(baslik)
    return baslik + b"".join(bytes([bayt]) * sayilar[bayt] for bayt in sorted(sayilar))

ok(not eslesir(entropi_ornegi(-1), "Dengeli_Lab"), "aynı boyutta entropi 7.5'in hemen altında")
ok(not eslesir(entropi_ornegi(0), "Dengeli_Lab"), "entropi tam 7.5: büyük koşulu eşitliği reddetmeli")
ok(eslesir(entropi_ornegi(1), "Dengeli_Lab"), "aynı boyutta entropi 7.5'in hemen üstünde")
```

```solution
import "math"
rule Dengeli_Lab {
    strings:
        $a = "LABPACK"
    condition:
        $a at 0 and filesize >= 512 and math.entropy(0, filesize) > 7.5
}
```

```hint
Boyut ve başlık ön şartını math.entropy sonucu ile birleştir.
```
:::

::: gorev Sıfır baytı oranı
`Sifir_Yogun` kuralı `PF` başlıklı, en az 16 baytlık dosyada sıfır baytı oranı en az 0.75 ise eşleşsin.

```starter
// Koşulları ve gereken bölümleri görev metnine göre tamamla.
rule Sifir_Yogun { condition: false }
```

```test
ok(eslesir(b"PF" + b"\x00" * 30, "Sifir_Yogun"), "yüksek sıfır oranı")
ok(eslesir(b"PFAB" + b"\x00" * 12, "Sifir_Yogun"), "tam 0.75 sınırı")
ok(not eslesir(b"PF" + b"A" * 30, "Sifir_Yogun"), "sıfır oranı düşük")
ok(not eslesir(b"XX" + b"\x00" * 30, "Sifir_Yogun"), "başlık yanlış")
ok(not eslesir(b"PF" + b"\x00" * 6, "Sifir_Yogun"), "kısa dosya")
```

```solution
import "math"
rule Sifir_Yogun {
    strings:
        $a = "PF"
    condition:
        $a at 0 and filesize >= 16 and math.percentage(0x00) >= 0.75
}
```

```hint
percentage oran döndürür; yüzde 75 için 75 değil 0.75 yaz.
```
:::
