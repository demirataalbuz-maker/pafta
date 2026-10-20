---
id: yr04
title: Bayt Desenleri · Hex ve Joker
summary: Metin yerine bayt ara; ?? ve yarım bayt jokerini kontrollü kullan.
---

::: anlat Hex görünümü metin değildir
`{ 50 41 46 54 41 }`, ASCII `PAFTA` metninin baytlarıdır. Sondaki `00` metin sonlandırıcı olabilir ama YARA için sıradan bir bayttır. İkili biçimleri incelerken bayt değeri ile ekranda görünen karakteri ayırmalısın.

Hex deseninde `??` herhangi bir bayt, `A?` ise üst yarısı A olan herhangi bir bayttır. `?F` alt yarısı F olanları kabul eder. Esneklik her eklendiğinde aday sayısı büyür: sabit işaretleri mümkün olduğu kadar anlamlı tut.

```yara
rule Baytlar {
    strings:
        $a = { 50 41 46 54 41 00 ?? A? }
    condition:
        $a
}
```
:::

::: anlat Girdiyi doğru biçimde ver
Pafta girdi kutusunda `hex:` öneki hex rakamlarını bayta çevirir. `hex: 41 42` iki bayttır; `41 42` yazarsan beş karakterlik sıradan metindir. Testlerde `bytes.fromhex(...)` aynı işi açıkça yapar.

Hex deseni bir dosyanın her yerinde aranır. Dosya başlığı olduğunu söylemek için ileride `$a at 0` yazacağız. Şimdilik bir işaretin varlığını öğreniyoruz; aynı baytların metin, görsel veya başka bir dosyada tesadüfen bulunabileceğini de olumsuz örneklerle kontrol ediyoruz.

Kaynak: [Resmî YARA belgeleri](https://yara.readthedocs.io/en/stable/writingrules.html).
:::

::: tahmin
Girdi kutusundaki veriyi bu kuralla tara. Hangi kural adı yazılır; neden?

```yara
rule Baytlar {
    strings:
        $a = { 50 41 46 54 41 00 ?? A? }
    condition:
        $a
}
```

```stdin
hex: 50 41 46 54 41 00 77 AB
```

???

`Baytlar` eşleşir: 77 değeri `??`, AB değeri `A?` ile kabul edilir.
:::

::: gorev Sürüm baytı
`Surum_Bayti` kuralı `50 41 46 54 41`, ardından herhangi bir sürüm baytı ve `00 FF` dizisini bulsun.

```starter
// Koşulları ve gereken bölümleri görev metnine göre tamamla.
rule Surum_Bayti { condition: false }
```

```test
ok(eslesir(bytes.fromhex("50 41 46 54 41 01 00 FF"), "Surum_Bayti"), "birinci sürüm")
ok(eslesir(bytes.fromhex("50 41 46 54 41 AB 00 FF"), "Surum_Bayti"), "farklı sürüm")
ok(not eslesir(bytes.fromhex("50 41 46 54 41 01 00 FE"), "Surum_Bayti"), "sabit bitiş değişmemeli")
ok(not eslesir(b"PAFTA00FF", "Surum_Bayti"), "hex rakamlarını metin sanma")
```

```solution
rule Surum_Bayti {
    strings:
        $a = { 50 41 46 54 41 ?? 00 FF }
    condition:
        $a
}
```

```hint
Bir sürüm baytı için bir tane ?? yeterlidir.
```
:::

::: gorev Yarım bayt ailesi
`Nible` kuralı `50 46`, sonra `A0`–`AF` aralığındaki bir bayt, sonra `0F`–`FF` içinde alt yarısı F olan bir bayt arasın.

```starter
// Koşulları ve gereken bölümleri görev metnine göre tamamla.
rule Nible { condition: false }
```

```test
ok(eslesir(bytes.fromhex("50 46 A0 0F"), "Nible"), "alt sınır")
ok(eslesir(bytes.fromhex("50 46 AF FF"), "Nible"), "üst sınır")
ok(not eslesir(bytes.fromhex("50 46 B0 0F"), "Nible"), "A ailesi dışında")
ok(not eslesir(bytes.fromhex("50 46 A0 F0"), "Nible"), "alt yarı F değil")
```

```solution
rule Nible {
    strings:
        $a = { 50 46 A? ?F }
    condition:
        $a
}
```

```hint
Her hex baytı iki yarım bayttan oluşur: A? ve ?F.
```
:::
