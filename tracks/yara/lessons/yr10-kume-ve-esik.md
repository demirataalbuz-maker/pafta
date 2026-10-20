---
id: yr10
title: İşaret Kümeleri ve Eşikler
summary: any/all/N of ve ad jokerleriyle büyüyen kuralları okunur tut.
---

::: anlat Koşulu tekrar tekrar yazma
`any of them` tanımlı metinlerden en az birini; `all of them` hepsini ister. `2 of ($a, $b, $c)` bu üç farklı işaretten en az ikisini ister. Aynı işaretin on kez tekrarlanması iki farklı işaret sayılmaz; tekrar sayısı için önceki `#a` konusu vardır.

`$oz_*` gibi ad jokerleriyle bir aile seçebilirsin. Bu joker taranan veriye değil, kuraldaki **işaret adlarına** uygulanır. Böylece gerekli başlığı `$baslik`, destek işaretlerini `$oz_1`, `$oz_2` diye ayırırsın.

```yara
rule Iki_Ozellik {
    strings:
        $a = "LAB_ALPHA"
        $b = "LAB_BETA"
        $c = "LAB_GAMMA"
    condition:
        2 of them
}
```
:::

::: anlat Yeni işaret eklemenin etkisi
`all of them` yazdığın kurala yeni bir string eklediğinde karar koşulu da değişir: artık yeni işaret de zorunludur. `2 of ($oz_*)` ise yalnızca seçtiğin aileyi sayar. Küçük kurallarda kolay görünen bu fark, bakım sırasında önemli bir regresyon kaynağıdır.

Eşik seçimi test verisinden ve tespit amacından gelmelidir. Daha çok işaret istemek yanlış pozitifi azaltabilir, ancak gerçek örneklerde bazı alanlar isteğe bağlıysa kaçırma oranını artırabilir. Bu derste değişik kombinasyonları test ederek koşulun bütün durumlarını görürüz.

Kaynak: [Resmî YARA belgeleri](https://yara.readthedocs.io/en/stable/writingrules.html).
:::

::: tahmin
Girdi kutusundaki veriyi bu kuralla tara. Hangi kural adı yazılır; neden?

```yara
rule Iki_Ozellik {
    strings:
        $a = "LAB_ALPHA"
        $b = "LAB_BETA"
        $c = "LAB_GAMMA"
    condition:
        2 of them
}
```

```stdin
LAB_ALPHA LAB_GAMMA
```

???

`Iki_Ozellik` eşleşir. Üç farklı işaretin ikisi vardır; Beta zorunlu değildir.
:::

::: gorev Üçten ikisi
`Iki_Uc` kuralında ALPHA, BETA ve GAMMA işaretlerinden en az ikisi bulunsun.

```starter
// Koşulları ve gereken bölümleri görev metnine göre tamamla.
rule Iki_Uc { condition: false }
```

```test
for x in ("ALPHA BETA", "ALPHA GAMMA", "BETA GAMMA", "ALPHA BETA GAMMA"):
    ok(eslesir(x, "Iki_Uc"), "iki ya da üç farklı işaret")
for x in ("ALPHA ALPHA", "BETA", "GAMMA", ""):
    ok(not eslesir(x, "Iki_Uc"), "aynı işareti tekrarlamak yetmez")
```

```solution
rule Iki_Uc {
    strings:
        $a = "ALPHA"
        $b = "BETA"
        $c = "GAMMA"
    condition:
        2 of them
}
```

```hint
2 of them farklı string tanımlarını sayar.
```
:::

::: gorev Başlık artı özellik ailesi
`Aile` kuralında `$baslik = "PFAMILY"` zorunlu; `$oz_1 = "FEATURE_A"`, `$oz_2 = "FEATURE_B"`, `$oz_3 = "FEATURE_C"` ailesinden de en az ikisi bulunsun.

```starter
// Koşulları ve gereken bölümleri görev metnine göre tamamla.
rule Aile { condition: false }
```

```test
ok(eslesir("PFAMILY FEATURE_A FEATURE_C", "Aile"), "başlık ve iki özellik")
ok(not eslesir("FEATURE_A FEATURE_B FEATURE_C", "Aile"), "başlık zorunlu")
ok(not eslesir("PFAMILY FEATURE_A", "Aile"), "başlık ikinci özellik sayılmamalı")
ok(not eslesir("PFAMILY PFAMILY", "Aile"), "tekrarlı başlık yetmez")
```

```solution
rule Aile {
    strings:
        $baslik = "PFAMILY"
        $oz_1 = "FEATURE_A"
        $oz_2 = "FEATURE_B"
        $oz_3 = "FEATURE_C"
    condition:
        $baslik and 2 of ($oz_*)
}
```

```hint
them yerine ($oz_*) kullanarak başlığı eşik hesabının dışında tut.
```
:::
