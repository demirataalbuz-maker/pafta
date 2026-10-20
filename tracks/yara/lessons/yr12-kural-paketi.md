---
id: yr12
title: Kural Paketleri · private ve global
summary: Yardımcı kuralları yeniden kullan; global ön şartın bütün paketi etkilediğini gör.
---

::: anlat Kural başka bir kuralı kullanabilir
Önceden tanımlanmış bir kuralın adını koşulda boolean değer gibi kullanabilirsin. `private rule` tarama kararına katılır ama eşleşme listesinde kendi adı raporlanmaz. Ortak dosya biçimi kontrolünü küçük bir private kurala ayırmak tekrarı azaltır.

Bağımlılıkları açık tut: yardımcı kuralı onu kullanan kuraldan önce tanımla. Aynı ad alanında kural adları benzersiz olmalıdır. Paketin public kurallarının hangi yardımcı koşullara bağlı olduğunu açıklamak, yanlış bir değişikliğin birçok tespiti sessizce etkilemesini önler.

```yara
private rule PF_Bicim { strings: $a = "PF" condition: $a at 0 }     #! yardımcı kural: çıktıda tek başına raporlanmaz
rule PF_Rapor { strings: $a = "REPORT" condition: PF_Bicim and $a } #! PF_Bicim sağlandığında ve REPORT bulunduğunda raporlanır
```

> [!DERİN] `private` ve `global` değiştiricilerinin farkı
> - `private rule`: Çıktı listesinde görünmez; yalnızca başka kuralların `condition` satırında yapıtaşı olarak kullanılır.
> - `global rule`: Dosyadaki **tüm** kurallara otomatik olarak `and Global_Kural` eklenmiş gibi davranır. Çoğu zaman `private global rule` birlikte kullanılarak ortak boyut/biçim kapısı sessizce kurulur.
:::

::: anlat Global kural ortak kapıdır
`global rule` aynı ad alanındaki diğer kurallar için ortak ön şarttır. Global koşul sağlanmazsa, normalde kendi koşulu doğru olan kurallar da raporlanmaz. `private global rule` ortak kapıyı raporu kalabalıklaştırmadan kurar.

Bu etki çok geniştir: yalnız bir dosya ailesine ait ön şartı bütün bir karma pakete global koyarsan ilgisiz kuralları da kapatabilirsin. Genel filtre yerine açık bağımlılık çoğu zaman daha kolay izlenir. Bu derste iki ayrı küçük paketin davranışını test ediyoruz.

> [!TUZAK] Kural tanımlama sırası ve `global` kapsamı
> YARA kuralları yukarıdan aşağıya derlenir; bir kural yalnızca kendisinden **önce** tanımlanmış başka bir kurala başvurabilir. Ayrıca `global rule` aynı derleme birimi içindeki tüm kuralları etkilediğinden, farklı dosya türlerini tarayan kuralları aynı dosyada `global` ile birleştirmemelisin.

Kaynak: [Resmî YARA belgeleri](https://yara.readthedocs.io/en/stable/writingrules.html).
:::

::: tahmin
Girdi kutusundaki veriyi bu kuralla tara. Hangi kural adı yazılır; neden?

```yara
private rule PF_Bicim { strings: $a = "PF" condition: $a at 0 }
rule PF_Rapor { strings: $a = "REPORT" condition: PF_Bicim and $a }
```

```stdin
PF:REPORT
```

???

`PF_Rapor` yazılır; `PF_Bicim` doğru olsa da private olduğu için raporda yer almaz.
:::

::: gorev Yardımcıyı gizle
`PF_Bicim` adlı private kural PF başlığını sıfırda arasın. `PF_Rapor` adlı public kural bu biçimi ve REPORT işaretini birlikte istesin. Başka public kural bulunmasın.

```starter
// Koşulları ve gereken bölümleri görev metnine göre tamamla.
private rule PF_Bicim { condition: false }
rule PF_Rapor { condition: false }
```

```stdin
PF:REPORT
```

```test
eq(eslesenler("PF:REPORT"), ["PF_Rapor"], "yalnız public tespit raporlanmalı")
ok(not eslesir("xPF:REPORT"), "başlık sıfırda olmalı")
ok(not eslesir("PF:NOTHING"), "esas işaret gerekli")
ok(not eslesir("REPORT"), "biçim gerekli")
```

```solution
private rule PF_Bicim { strings: $a = "PF" condition: $a at 0 }
rule PF_Rapor { strings: $a = "REPORT" condition: PF_Bicim and $a }
```

```hint
private kural adı, sonraki kuralın koşulunda kullanılabilir.
```
:::

::: gorev Ortak boyut kapısı
`Kucuk_Dosya` private global kuralı dosyayı en fazla 32 baytla sınırlasın. `A_Kaydi` ALPHA; `B_Kaydi` BETA arasın. Büyük dosyada hiçbir kural raporlanmasın.

```starter
// Koşulları ve gereken bölümleri görev metnine göre tamamla.
private global rule Kucuk_Dosya { condition: false }
rule A_Kaydi { condition: false }
rule B_Kaydi { condition: false }
```

```stdin
ALPHA BETA
```

```test
eq(sorted(eslesenler("ALPHA BETA")), ["A_Kaydi", "B_Kaydi"], "iki public kural")
eq(eslesenler("ALPHA"), ["A_Kaydi"], "yalnız A")
eq(eslesenler("BETA"), ["B_Kaydi"], "yalnız B")
eq(eslesenler("ALPHA BETA" + "x" * 32), [], "global boyut kapısı")
eq(eslesenler("hicbiri"), [], "işaretsiz veri")
for boyut in (31, 32, 33):
    veri = b"ALPHA BETA" + b"x" * (boyut - len(b"ALPHA BETA"))
    beklenen = ["A_Kaydi", "B_Kaydi"] if boyut <= 32 else []
    eq(sorted(eslesenler(veri)), beklenen, f"global boyut sınırının komşusu: {boyut} bayt")
```

```solution
private global rule Kucuk_Dosya { condition: filesize <= 32 }
rule A_Kaydi { strings: $a = "ALPHA" condition: $a }
rule B_Kaydi { strings: $b = "BETA" condition: $b }
```

```hint
global ve private birlikte kullanılabilir; kapının kendisi çıktı üretmesin.
```
:::
