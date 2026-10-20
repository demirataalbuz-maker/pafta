---
id: yr07
title: Kaç Kere? · Eşleşme Sayıları
summary: #a ile varlık yerine tekrar sayısını ölç; aralıkta saymayı öğren.
---

::: anlat Bir tane bulmak ile tekrar örüntüsü farklıdır
`$a` bir işaret bulunup bulunmadığıdır; `#a` kaç kez bulunduğudur. `#a >= 3` en az üç eşleşme ister. Uzun bir dosyada tekrar sayısı tek bir işaretten daha açıklayıcı olabilir, ama dosyanın büyüklüğü ve biçimi sayıyı etkiler.

Sayımda eşleşmelerin nerede olduğu henüz dikkate alınmaz. İlk 32 bayttaki kayıt sayısını istiyorsan `#a in (0..31)` kullanabilirsin. Aralığın sınırları bayt konumudur ve dahildir. Bir etiketin aynı dosyada birçok yerde geçebileceğini tasarıma kat.

```yara
rule Tekrar {
    strings:
        $a = "EVT;"                        #! sayılacak kayıt izi
    condition:
        #a >= 3                            #! dosyadaki toplam eşleşme sayısı en az 3 olmalı
}
```

> [!NOT] `$a` mantıksal varlıktır, `#a` ise tamsayıdır
> Koşulda `$a` yazmak aslında `#a > 0` demektir. `#a in (0..31) >= 2` yazdığında ise tüm dosyadaki eşleşmeleri değil, yalnızca ilk 32 bayt içinde başlayan eşleşmeleri sayarsın.
:::

::: anlat Eşiğin iki yanını test et
Bir eşik görevi yalnızca 10 eşleşmeli örnekle doğrulanmaz. Eşik 3 ise 2, 3 ve 4 tekrar özellikle değerlidir. Tam sayı şartı ile alt sınır şartını karıştırma: `#a == 3`, dört eşleşmeli veriyi reddeder; `#a >= 3` kabul eder.

Birden fazla işaretin sayısını da birlikte kullanabilirsin. Örneğin eğitim raporu iki hata kaydı ve hiç onay kaydı içeriyorsa eşleşebilir. Bu bir zaman korelasyonu değildir; dosya içindeki bayt örüntülerinin sayımıdır. Zaman ve kullanıcı bağlamı için Sigma/KQL/SPL yolundaki olay modelleri gerekir.

> [!TUZAK] Eşik sınırında `<` ile `<=` veya `==` ile `>=` karışıklığı
> ”En az 3 kayıt” yerine `== 3` yazarsan 4 kayıtlı gerçek örneği kaçırırsın; `> 3` yazarsan tam 3 kayıtlı sınır örneğini reddedersin. Eşik kurallarını her zaman `eşik - 1`, `eşik` ve `eşik + 1` örnekleriyle sına.

Kaynak: [Resmî YARA belgeleri](https://yara.readthedocs.io/en/stable/writingrules.html).
:::

::: tahmin
Girdi kutusundaki veriyi bu kuralla tara. Hangi kural adı yazılır; neden?

```yara
rule Tekrar {
    strings:
        $a = "EVT;"
    condition:
        #a >= 3
}
```

```stdin
EVT;EVT;EVT;
```

???

`Tekrar` eşleşir. Üç ayrı EVT; işareti bulunur ve eşik dahildir.
:::

::: gorev En az üç kayıt
`Uc_Kayit` kuralı `EVT;` işaretini en az üç kez içeren veriyi yakalasın.

```starter
// Koşulları ve gereken bölümleri görev metnine göre tamamla.
rule Uc_Kayit { condition: false }
```

```stdin
EVT;EVT;EVT;
```

```test
for n in (0, 1, 2):
    ok(not eslesir("EVT;" * n, "Uc_Kayit"), f"eşik altı {n}")
for n in (3, 4, 7):
    ok(eslesir("EVT;" * n, "Uc_Kayit"), f"eşik ve üstü {n}")
```

```solution
rule Uc_Kayit {
    strings:
        $a = "EVT;"
    condition:
        #a >= 3
}
```

```hint
Varlık için $a, sayım için #a kullanılır.
```
:::

::: gorev Yalnız başlık aralığında
`Baslik_Sayimi` kuralı ilk 16 bayt içinde **başlayan** en az iki `OK;` eşleşmesi istesin. Sonraki eşleşmeler hesaba katılmasın.

```starter
// Koşulları ve gereken bölümleri görev metnine göre tamamla.
rule Baslik_Sayimi { condition: false }
```

```stdin
OK;xxOK;zzzzzzzzzzzzzzzzzzzz
```

```test
ok(eslesir(b"OK;xxOK;" + b"z" * 20, "Baslik_Sayimi"), "başlıkta iki kayıt")
ok(not eslesir(b"OK;" + b"z" * 20 + b"OK;", "Baslik_Sayimi"), "ikinci kayıt başlık dışında")
ok(not eslesir(b"z" * 16 + b"OK;OK;", "Baslik_Sayimi"), "hepsi aralık dışında")
ok(eslesir(b"OK;" + b"z" * 12 + b"OK;", "Baslik_Sayimi"), "15 konumundaki başlangıç dahil")
```

```solution
rule Baslik_Sayimi {
    strings:
        $a = "OK;"
    condition:
        #a in (0..15) >= 2
}
```

```hint
Aralık 0..15; ölçülen şey eşleşmenin başladığı konumdur.
```
:::
