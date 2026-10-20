---
id: yr08
title: Nerede? · Konum ve Uzunluk
summary: at, in, @a[i] ve !a[i] ile biçimin içindeki ilişkileri kur.
---

::: anlat Dosyayı başlıktan tanı
`$a at 0`, işaretin dosyanın ilk baytından başlamasını ister. `$a in (4..32)` ise bu aralıkta başlayan bir eşleşme arar. Dosya taramasında konum sıfırdan başlar; bir metnin karakter indeksi ile UTF-8 bayt indeksi Türkçe harfler yüzünden aynı olmayabilir.

`@a[1]` ilk eşleşmenin başlangıcıdır; köşeli parantez içindeki eşleşme numarası **birden** başlar. `!a[1]` ilk eşleşmenin bayt uzunluğudur. Eşleşme yoksa konum ve uzunluk tanımsız olur; önce varlığı veya sayıyı kontrol etmek koşulu daha anlaşılır kılar.

```yara
rule Baslik {
    strings:
        $a = "PF01"
        $b = "END"
    condition:
        $a at 0 and $b in (4..16)
}
```
:::

::: anlat Parçalar arasındaki ilişki
Bir işaretin konumunu diğerine bağlayabilirsin: `@son[1] > @bas[1]`. Fakat yalnızca ilk eşleşmeleri karşılaştırdığını unutma. Dosyada birden fazla başlık varsa bütün eşleşmeleri sonraki döngü dersinde inceleyeceğiz.

Regex uzunluğu değişkense `!a[1]` seçilen eşleşmenin gerçek uzunluğunu verir. Uzunluk testi yazarken regexin nasıl eşleştiğini de düşün: kısa bir regex uzun kaydın ön ekini bulabilir. Alan sonlandırıcısını desene katmak hem anlamı hem testi netleştirir.

Kaynak: [Resmî YARA belgeleri](https://yara.readthedocs.io/en/stable/writingrules.html).
:::

::: tahmin
Girdi kutusundaki veriyi bu kuralla tara. Hangi kural adı yazılır; neden?

```yara
rule Baslik {
    strings:
        $a = "PF01"
        $b = "END"
    condition:
        $a at 0 and $b in (4..16)
}
```

```stdin
PF01xxxxEND
```

???

`Baslik` eşleşir. PF01 sıfırda, END ise izin verilen aralıkta başlar.
:::

::: gorev Gerçek başlık
`Dosya_Basligi` kuralı `PF01` sıfırıncı baytta ve `END` 4–20 konumlarında başlıyorsa eşleşsin.

```starter
// Koşulları ve gereken bölümleri görev metnine göre tamamla.
rule Dosya_Basligi { condition: false }
```

```test
ok(eslesir(b"PF01xxEND", "Dosya_Basligi"), "geçerli başlık")
ok(not eslesir(b"xPF01xxEND", "Dosya_Basligi"), "başlık sıfırda değil")
ok(not eslesir(b"PF01" + b"x" * 17 + b"END", "Dosya_Basligi"), "bitiş çok ileride")
ok(eslesir(b"PF01" + b"x" * 16 + b"END", "Dosya_Basligi"), "20 konumu dahil")
```

```solution
rule Dosya_Basligi {
    strings:
        $a = "PF01"
        $b = "END"
    condition:
        $a at 0 and $b in (4..20)
}
```

```hint
Başlığın varlığı yetmez; at 0 kullan.
```
:::

::: gorev Değişken alanın uzunluğu
`Alan` kuralı `ID=`, 2–6 rakam ve `;` biçimindeki ilk kaydı bulsun; ilk eşleşme 0 konumunda ve uzunluğu tam 7 bayt olsun. Yani ilk kimlik tam üç rakam içersin.

```starter
// Koşulları ve gereken bölümleri görev metnine göre tamamla.
rule Alan { condition: false }
```

```test
ok(eslesir("ID=123; son", "Alan"), "3 rakam ve 7 bayt")
ok(not eslesir("xID=123;", "Alan"), "konum yanlış")
ok(not eslesir("ID=12;", "Alan"), "alan kısa")
ok(not eslesir("ID=1234; ID=123;", "Alan"), "ilk eşleşmenin uzunluğu ölçülmeli")
```

```solution
rule Alan {
    strings:
        $a = /ID=[0-9]{2,6};/
    condition:
        $a and @a[1] == 0 and !a[1] == 7
}
```

```hint
!a[1] bütün regex eşleşmesinin uzunluğudur: ID= ve ; de sayılır.
```
:::
