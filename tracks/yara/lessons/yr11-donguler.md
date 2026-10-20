---
id: yr11
title: Döngüler · Eşleşmeler Üzerinde Gezmek
summary: for..of ve for i ile bütün işaretleri veya bütün konumları denetle.
---

::: anlat Her işarete aynı koşulu uygula
`for all of ($alan_*) : ( $ in (0..63) )`, seçilen her stringin ilk 64 baytta en az bir eşleşmesi olmasını ister. Döngü içindeki `$`, o anki stringdir. Böylece aynı konum şartını birçok işaret için tekrarlamadan yazarsın.

`for any of (...)` en az bir stringin parantezdeki şartı sağlamasını yeterli sayar. Bu yapı `all of` ile benzer görünür, ancak gövdesinde sayım, konum veya uzunluk gibi daha ayrıntılı şartlar kurabilir.

```yara
rule Baslik_Alanlari {
    strings:
        $alan_a = "TYPE="
        $alan_b = "VER="
    condition:
        for all of ($alan_*) : ( $ in (0..31) )
}
```
:::

::: anlat Yalnız ilk eşleşmeye bakma
`for any i in (1..#a) : ( @a[i] == 16 )`, `$a` işaretinin eşleşmeleri arasında konum 16'da başlayan bir örnek arar. Köşeli parantezdeki i eşleşme numarasıdır; konum değildir. `#a > 0` gibi bir varlık ön şartı niyeti açık tutar.

Çok büyük veya iç içe aralık döngüleri tarama maliyetini artırabilir. Bir işaretin sabit aralıkta varlığı yeterliyse `$a in (...)` daha sade olabilir. Döngü seçimini, gerçekten her eşleşmeye özel bir ilişki kurman gerekip gerekmediğine göre yap.

Kaynak: [Resmî YARA belgeleri](https://yara.readthedocs.io/en/stable/writingrules.html).
:::

::: tahmin
Girdi kutusundaki veriyi bu kuralla tara. Hangi kural adı yazılır; neden?

```yara
rule Baslik_Alanlari {
    strings:
        $alan_a = "TYPE="
        $alan_b = "VER="
    condition:
        for all of ($alan_*) : ( $ in (0..31) )
}
```

```stdin
TYPE=lab;VER=1;
```

???

`Baslik_Alanlari` eşleşir; iki farklı alan da ilk 32 baytta başlar.
:::

::: gorev Her alan başlıkta
`Butun_Alanlar` kuralında TYPE=, VER= ve SIZE= işaretlerinin her biri ilk 32 baytta başlasın.

```starter
// Koşulları ve gereken bölümleri görev metnine göre tamamla.
rule Butun_Alanlar { condition: false }
```

```test
ok(eslesir("TYPE=x;VER=1;SIZE=9;", "Butun_Alanlar"), "üç alan başlıkta")
ok(not eslesir("TYPE=x;VER=1;", "Butun_Alanlar"), "alan eksik")
ok(not eslesir(b"TYPE=x;VER=1;" + b"x" * 30 + b"SIZE=9;", "Butun_Alanlar"), "bir alan çok geç")
```

```solution
rule Butun_Alanlar {
    strings:
        $alan_a = "TYPE="
        $alan_b = "VER="
        $alan_c = "SIZE="
    condition:
        for all of ($alan_*) : ( $ in (0..31) )
}
```

```hint
for all of ($alan_*) gövdesindeki $ o anki stringi gösterir.
```
:::

::: gorev Yakın eşleşme çifti
`Yakin_Cift` kuralı en az iki `TAG` eşleşmesi arasından, ardışık eşleşmelerin başlangıçları arasında tam 8 bayt bulunan bir çift istesin.

```starter
// Koşulları ve gereken bölümleri görev metnine göre tamamla.
rule Yakin_Cift { condition: false }
```

```test
ok(eslesir(b"TAG" + b"x" * 5 + b"TAG", "Yakin_Cift"), "sekiz bayt aralıklı")
ok(eslesir(b"TAGxTAG" + b"x" * 5 + b"TAG", "Yakin_Cift"), "ilk çift değil sonraki çift")
ok(not eslesir(b"TAG" + b"x" * 4 + b"TAG", "Yakin_Cift"), "yedi bayt aralıklı")
ok(not eslesir("TAG", "Yakin_Cift"), "tek eşleşme")
```

```solution
rule Yakin_Cift {
    strings:
        $a = "TAG"
    condition:
        #a >= 2 and for any i in (1..#a - 1) : ( @a[i + 1] - @a[i] == 8 )
}
```

```hint
Eşleşme numarası i için @a[i + 1] ile @a[i] farkını hesapla.
```
:::
