---
id: yr03
title: Kural Kimliği ve Olumsuz Koşullar
summary: meta ve tags ile bakım yapılabilir kural yaz; dışlamanın etkisini sınırla.
---

::: anlat Kuralı senden sonra kim okuyacak?
Bir kural yalnızca koşuldan ibaret değildir. `meta` içine yazar, açıklama ve sürüm gibi bakım bilgisi koyarsın. Bunlar eşleşme koşulunu değiştirmez; sonuçla birlikte taşınır. Etiketler kural adından sonra `: egitim dosya` şeklinde yazılır. Kural ve etiket adları boşluk içermez.

YARA bu alanlara tehdit bilgisi doğrulaması yapmaz. `severity = "high"` yazmak dosyanın tehlikeli olduğunu kanıtlamaz. Eğitim kuralını açıkça eğitim diye etiketle; gerekçeyi açıklamada koru. Sayı, metin ve boolean meta değerleri farklı türlerdir.

```yara
rule Kimlik : egitim belge {
 meta:
  author = "Pafta"
  revision = 1
  production = false
 strings:
  $a = "LAB_REPORT"
 condition:
  $a
}
```
:::

::: anlat Dışlama filtresi dar olmalı
`$a and not $izinli` ifadesinde izinli işaret dosyanın **herhangi bir yerinde** bulunursa kural susar. Bu bazen doğru politikadır, bazen fazla geniş bir dışlamadır. Filtreyi yazarken saldırı davranışı öğreten kod değil, karar sınırlarını gösteren etkisiz veri kullanıyoruz.

Bir güvenilirlik işaretine tek başına güvenilmez; gerçek üretimde imza doğrulaması, kaynağın güvenilirliği ve süreç bağlamı gibi ek bilgiler gerekir. Bu ders sadece kural mantığını kurar. Sonraki konum derslerinde dışlamayı başlığa ya da belirli aralığa daraltacağız.

Kaynak: [Resmî YARA belgeleri](https://yara.readthedocs.io/en/stable/writingrules.html).
:::

::: tahmin
Girdi kutusundaki veriyi bu kuralla tara. Hangi kural adı yazılır; neden?

```yara
rule Rapor {
    strings:
        $a = "LAB_REPORT"
        $izinli = "APPROVED_TEST"
    condition:
        $a and not $izinli
}
```

```stdin
LAB_REPORT: egitim
```

???

`Rapor` eşleşir. Gerekli işaret var; dışlama işareti yok.
:::

::: gorev Bakım bilgisi
`Bakimli` kuralını `egitim` ve `dosya` etiketleriyle yaz. `meta` içinde `author = "Pafta"`, `revision = 2`, `production = false` bulunsun. Koşul `LAB_META` işaretini arasın.

```starter
// Koşulları ve gereken bölümleri görev metnine göre tamamla.
rule Bakimli { condition: false }
```

```test
matches = derle(src).match(data=b"LAB_META")
ok(len(matches) == 1, "pozitif örnek")
if matches:
    eq(matches[0].rule, "Bakimli", "kural adı")
    ok(set(matches[0].tags) == {"egitim", "dosya"}, "iki eğitim etiketi")
    eq(matches[0].meta.get("author"), "Pafta", "yazar")
    eq(matches[0].meta.get("revision"), 2, "sayısal sürüm")
    eq(matches[0].meta.get("production"), False, "boolean üretim bilgisi")
ok(not eslesir("LAB_OTHER", "Bakimli"), "meta eşleşme sebebi değildir")
```

```solution
rule Bakimli : egitim dosya {
 meta:
  author = "Pafta"
  revision = 2
  production = false
 strings:
  $a = "LAB_META"
 condition:
  $a
}
```

```hint
meta ve strings ayrı bölümlerdir; etiketler rule adından sonra gelir.
```
:::

::: gorev Yanlış pozitifi dışla
`Dislama` kuralı `LAB_REPORT` varsa, fakat `APPROVED_TEST` yoksa eşleşsin.

```starter
// Koşulları ve gereken bölümleri görev metnine göre tamamla.
rule Dislama { condition: false }
```

```test
ok(eslesir("LAB_REPORT normal", "Dislama"), "esas işaret")
ok(not eslesir("LAB_REPORT APPROVED_TEST", "Dislama"), "izinli örnek dışarıda")
ok(not eslesir("APPROVED_TEST", "Dislama"), "sadece izin işareti")
ok(not eslesir("rapor yok", "Dislama"), "işaretsiz veri")
```

```solution
rule Dislama {
    strings:
        $a = "LAB_REPORT"
        $izinli = "APPROVED_TEST"
    condition:
        $a and not $izinli
}
```

```hint
`not` yalnızca sonraki ifadeyi tersine çevirir; birlikte kullanacağın koşulları parantezleyebilirsin.
```
:::
