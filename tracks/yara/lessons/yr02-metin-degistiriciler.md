---
id: yr02
title: Metinler · Harf, Kodlama ve Sınır
summary: nocase, ascii, wide ve fullword ile neyin eşleştiğini bilinçli seç.
---

::: anlat Aynı görünen metnin farklı baytları
`nocase` metin eşleşmesini büyük-küçük harften bağımsız yapar. `ascii` normal tek baytlı biçimdir; metinlerde varsayılan davranıştır. `wide` ise her karakter arasına sıfır baytı koyulmuş biçimi arar. Bunu tüm Unicode kodlamalarını tanıyan bir özellik sanma: burada kullandığımız ASCII işaretinin UTF-16LE benzeri gösterimidir.

`ascii wide` iki gösterimi de kabul eder. Girdi kutusunda ham sıfır baytı yazmak yerine `hex: 50 00 41 00 ...` biçimini kullanabilirsin; testler `bytes` ile doğrudan binary veri sağlar.

```yara
rule Iki_Kodlama {
    strings:
        $a = "PAFTA" ascii wide nocase   #! tek bayt (ascii) + çift bayt sıfır aralıklı (wide) + harf duyarsız
    condition:
        $a                               #! iki kodlamadan herhangi biri eşleşirse doğru döner
}
```

> [!DERİN] `wide` tam olarak ne üretir?
> `wide` değiştiricisi ASCII karakterlerinin her birinin yanına `0x00` baytı ekleyerek (`50 00 41 00 46 00 54 00 41 00`) arama yapar. Tek başına `wide` yazarsan normal ASCII kopyayı artık aramaz; her iki biçimi de yakalamak için `ascii wide` birlikte yazılır.

```stdin
hex: 70 00 61 00 66 00 74 00 61 00
```
:::

::: anlat Bir sözcük ile bir parçayı ayırmak
`fullword`, işaretin alfanümerik bir sözcüğün içinden alınmasını engeller. Bu sınır bayt ve motor kurallarıyla değerlendirilir; doğal dildeki bütün Türkçe sözcük kurallarını kapsadığı varsayılmaz. `LAB` ararken `LABORATORY` dosyalarını da yakalıyorsan yararlıdır.

Değiştiriciyi eklemek kuralı otomatik olarak daha iyi yapmaz. Dosya biçiminde işaret bilerek başka karaktere bitişikse `fullword` gerçek eşleşmeyi kaybettirebilir. Önce beklenen veri biçimini tanımla, sonra olumlu ve sınırda olumsuz örnekleri yaz.

> [!TUZAK] `fullword` sınırlarını yanlış varsaymak
> `fullword` yalnızca işaretin solundaki ve sağındaki baytın alfanümerik (`a-z`, `A-Z`, `0-9`) olup olmadığına bakar. Noktalama işaretleri (`=`, `;`, `:`, `-`) sözcük sınırı sayılır; bu yüzden `state=ready;` içindeki `ready` bir `fullword` eşleşmesidir, ancak `ready_state` içindeki `_` alfanümerik komşulukla birleştiğinde davranışı test etmeden varsaymamalısın.

Kaynak: [Resmî YARA belgeleri](https://yara.readthedocs.io/en/stable/writingrules.html).
:::

::: tahmin
Girdi kutusundaki veriyi bu kuralla tara. Hangi kural adı yazılır; neden?

```yara
rule Sozcuk {
    strings:
        $a = "LAB" fullword nocase
    condition:
        $a
}
```

```stdin
status=lab; tamam
```

???

`Sozcuk` eşleşir: harf farkı yok sayılır ve `=` ile `;` sözcük sınırı oluşturur.
:::

::: gorev Harf farkına dayan
`Surum` kuralı `pafta_agent` işaretini harf farkı olmadan arasın.

```starter
// Koşulları ve gereken bölümleri görev metnine göre tamamla.
rule Surum { condition: false }
```

```stdin
PAFTA_AGENT
```

```test
ok(eslesir("PAFTA_AGENT", "Surum"), "büyük harf")
ok(eslesir("PaFtA_AgEnT", "Surum"), "karışık harf")
ok(not eslesir("pafta_agency", "Surum"), "farklı metin")
```

```solution
rule Surum {
    strings:
        $a = "pafta_agent" nocase
    condition:
        $a
}
```

```hint
Metin tanımının sonuna nocase eklenir.
```
:::

::: gorev ASCII ve geniş metin
`Kodlamalar` kuralı `LABKEY` işaretinin hem ASCII hem sıfır aralıklı geniş biçimini yakalasın. Harf farkı önemli kalsın.

```starter
// Koşulları ve gereken bölümleri görev metnine göre tamamla.
rule Kodlamalar { condition: false }
```

```stdin
xxLABKEYyy
```

```test
ok(eslesir(b"xxLABKEYyy", "Kodlamalar"), "ASCII biçimi")
ok(eslesir("LABKEY".encode("utf-16le"), "Kodlamalar"), "wide biçimi")
ok(not eslesir(b"labkey", "Kodlamalar"), "harf farkı korunmalı")
ok(not eslesir("LABKEY".encode("utf-16be"), "Kodlamalar"), "wide genel Unicode dönüştürücüsü değildir")
```

```solution
rule Kodlamalar {
    strings:
        $a = "LABKEY" ascii wide
    condition:
        $a
}
```

```hint
Sadece wide yazarsan normal ASCII biçimini dışarıda bırakırsın.
```
:::

::: gorev Tam sözcük
`Durum` kuralı `READY` sözcüğünü harf farkı olmadan bulsun; `ALREADY` ve `READYMADE` eşleşmesin.

```starter
// Koşulları ve gereken bölümleri görev metnine göre tamamla.
rule Durum { condition: false }
```

```stdin
state=ready;
```

```test
ok(eslesir("state=ready;", "Durum"), "bağımsız sözcük")
ok(not eslesir("ALREADY", "Durum"), "soldan bitişik")
ok(not eslesir("READYMADE", "Durum"), "sağdan bitişik")
```

```solution
rule Durum {
    strings:
        $a = "READY" nocase fullword
    condition:
        $a
}
```

```hint
nocase ile fullword aynı metinde kullanılabilir.
```
:::
