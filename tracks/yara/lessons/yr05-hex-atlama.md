---
id: yr05
title: Hex · Atlamalar ve Alternatifler
summary: Değişken uzunluklu alanları [n-m], seçenekleri (...) ile modelle.
---

::: anlat Dosya biçimindeki değişken alan
Bir işaretin iki sabit parçası arasında değişken uzunluklu veri olabilir. `[2-4]`, arada iki ile dört bayt bulunduğunu söyler; sınırlar dahildir. `[3]` tam üç bayttır. Bu değerler hex karakter sayısı değil, **bayt sayısıdır**.

Sınırsız `[-]` atlama geniş alanları kabul eder. Böyle bir esneklik gerçekten biçimden gelmiyorsa gereksiz aday ve tarama maliyeti üretir. Küçük bir eğitim örneğinde bile en kısa ve en uzun geçerli aralığı, ayrıca iki sınırın hemen dışını test etmek iyi alışkanlıktır.

```yara
rule Aralik {
    strings:
        $a = { 50 46 [2-4] 45 4E 44 }      #! PF (50 46) ile END (45 4E 44) arasında 2, 3 veya 4 bayt
    condition:
        $a
}
```

> [!NOT] `[n-m]` bayt sayar, hex basamağı saymaz
> `[2-4]` ifadesi araya 2 ila 4 **bayt** (yani hex görünümünde 4 ila 8 onaltılık rakam) girebileceğini belirtir. Tam uzunluk biliniyorsa `[3]` yazmak `?? ?? ??` yazmakla eşdeğerdir ve daha okunaklıdır.
:::

::: anlat Tek desende seçenekler
`( 01 02 | 03 04 )`, iki baytlı iki seçenekten birini kabul eder. Seçenekler gelişigüzel joker değildir; biçimin bildiğin sürümlerini açıkça listeler. Parantez hex deseninin içinde kullanılır; koşuldaki boolean parantezden farklı bir katmandadır.

Metin işareti, hex işareti ve koşulu birlikte kullanabilirsin. Bir dosya ailesinin sürüm alanını esnetirken dosyayı tanıtan sabit başlık ve sonlandırıcıyı korumak, her şeyi `??` yapmaktan daha ayırt edicidir.

> [!TUZAK] Sınırsız `[-]` atlamaları
> `{ 50 46 [-] 45 4E 44 }` aradaki mesafeyi sınırsız bırakır; hem yanlış pozitif ihtimalini büyütür hem de büyük dosyalarda geri izleme (backtracking) maliyetini artırır. Dosya biçimindeki alanın gerçek üst sınırını (`[0-64]` gibi) her zaman belirt.

Kaynak: [Resmî YARA belgeleri](https://yara.readthedocs.io/en/stable/writingrules.html).
:::

::: tahmin
Girdi kutusundaki veriyi bu kuralla tara. Hangi kural adı yazılır; neden?

```yara
rule Aralik {
    strings:
        $a = { 50 46 [2-4] 45 4E 44 }
    condition:
        $a
}
```

```stdin
hex: 50 46 11 22 33 45 4E 44
```

???

`Aralik` eşleşir; PF ile END arasında üç bayt vardır.
:::

::: gorev Sınırları koru
`Aralik_Kurali` kuralı `BEGIN`, ardından 2–4 bayt, sonra `END` bulsun.

```starter
// Koşulları ve gereken bölümleri görev metnine göre tamamla.
rule Aralik_Kurali { condition: false }
```

```stdin
hex: 42 45 47 49 4e 78 78 45 4e 44
```

```test
for n in (2, 3, 4):
    ok(eslesir(b"BEGIN" + b"x" * n + b"END", "Aralik_Kurali"), f"geçerli uzunluk {n}")
for n in (0, 1, 5):
    ok(not eslesir(b"BEGIN" + b"x" * n + b"END", "Aralik_Kurali"), f"sınır dışı {n}")
```

```solution
rule Aralik_Kurali {
    strings:
        $a = { 42 45 47 49 4E [2-4] 45 4E 44 }
    condition:
        $a
}
```

```hint
Hex bloktaki [2-4] aralığı her iki sınırı içerir.
```
:::

::: gorev İki sürüm
`Iki_Surum` kuralı yalnızca `PF`, sonra `01 02` veya `03 04`, sonra `00` dizisini yakalasın.

```starter
// Koşulları ve gereken bölümleri görev metnine göre tamamla.
rule Iki_Surum { condition: false }
```

```stdin
hex: 50 46 01 02 00
```

```test
ok(eslesir(bytes.fromhex("50 46 01 02 00"), "Iki_Surum"), "birinci sürüm")
ok(eslesir(bytes.fromhex("50 46 03 04 00"), "Iki_Surum"), "ikinci sürüm")
ok(not eslesir(bytes.fromhex("50 46 01 04 00"), "Iki_Surum"), "iki seçeneği karıştırma")
ok(not eslesir(bytes.fromhex("50 46 03 04 FF"), "Iki_Surum"), "sonlandırıcı sabit")
```

```solution
rule Iki_Surum {
    strings:
        $a = { 50 46 ( 01 02 | 03 04 ) 00 }
    condition:
        $a
}
```

```hint
Seçeneklerin tamamını | ile ayır; her baytı bağımsız seçenek yapma.
```
:::
