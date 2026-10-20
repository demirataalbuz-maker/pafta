---
id: yr01
title: YARA · İlk Kuralın
summary: Dosyayı çalıştırmadan baytlarında işaret ara; rule, strings, condition ve ilk olumlu/olumsuz test.
---

::: anlat Bir eşleşme bir iddiadır
YARA, verilen **baytların** bir kurala uyup uymadığını söyler. Dosyayı çalıştırmaz ve bir metni görmek tek başına dosyanın zararlı olduğunu kanıtlamaz. Bu yolda yalnızca kendimiz ürettiğimiz, etkisiz eğitim verilerini tarayacağız.

Bir kuralın adı raporda görünür. `strings` aranacak işaretleri tanımlar; `$etiket` o işaretin adıdır. `condition` kararın kendisidir ve zorunludur. Noktalı virgül gerekmez. Pafta gerçek **libyara** motorunu kullanır: Python ile benzetim yapmaz. Girdi kutusuna sıradan metin yazınca UTF-8 baytları taranır.

```yara
rule Egitim_Isareti {
    strings:
        $etiket = "PAFTA_LAB"
    condition:
        $etiket
}
```
:::

::: anlat Derlemek, taramak ve karar vermek
Önce kural derlenir; yazım hatası varsa veri taranmadan hata alırsın. Sonra aynı derlenmiş kural farklı veriler üzerinde çalışır. Büyük-küçük harf varsayılan olarak önemlidir: `PAFTA_LAB` ile `pafta_lab` farklı baytlardır.

Olumlu örnek kuralın yakalaması gereken veridir; olumsuz örnek yakalamaması gerekendir. Sadece olumlu örneği denemek, `condition: true` yazan bir kuralı bile başarılı gösterir. Her görev bu yüzden ikisini de sınar. Pafta çıktısı eşleşen **kural adlarını** satır satır gösterir; boş çıktı eşleşme yok demektir.

Kaynak: [Resmî YARA belgeleri](https://yara.readthedocs.io/en/stable/writingrules.html).
:::

::: tahmin
Girdi kutusundaki veriyi bu kuralla tara. Hangi kural adı yazılır; neden?

```yara
rule Egitim_Isareti {
    strings:
        $etiket = "PAFTA_LAB"
    condition:
        $etiket
}
```

```stdin
rapor: PAFTA_LAB tamam
```

???

`Egitim_Isareti` yazılır; işaret girdi içinde bulunur. Önündeki ve arkasındaki metin bunu engellemez.
:::

::: gorev İlk imza
`Ilk_Imza` kuralı tam olarak `LAB_TOKEN_42` bayt dizisini içeren veriyi yakalasın.

```starter
// Koşulları ve gereken bölümleri görev metnine göre tamamla.
rule Ilk_Imza { condition: false }
```

```test
ok(eslesir("bas:LAB_TOKEN_42:son", "Ilk_Imza"), "işaret içeride bulunmalı")
ok(not eslesir("LAB_TOKEN_43", "Ilk_Imza"), "benzer işaret kabul edilmemeli")
ok(not eslesir("lab_token_42", "Ilk_Imza"), "varsayılan eşleşme harfe duyarlı")
ok(not eslesir(b"", "Ilk_Imza"), "boş veri eşleşmemeli")
```

```solution
rule Ilk_Imza {
    strings:
        $a = "LAB_TOKEN_42"
    condition:
        $a
}
```

```hint
strings bölümünde bir metin tanımla; condition bölümünde onun $adını kullan.
```
:::

::: gorev İki işaret birlikte
`Iki_Isaret` kuralı ancak **hem** `LAB_START` **hem** `LAB_END` varsa eşleşsin. Sıralama henüz önemli değil.

```starter
// Koşulları ve gereken bölümleri görev metnine göre tamamla.
rule Iki_Isaret { condition: false }
```

```test
ok(eslesir("LAB_START veri LAB_END", "Iki_Isaret"), "ikisi birlikte")
ok(eslesir("LAB_END sonra LAB_START", "Iki_Isaret"), "bu görevde sıralama aranmaz")
ok(not eslesir("LAB_START", "Iki_Isaret"), "yalnız başlangıç yetmez")
ok(not eslesir("LAB_END", "Iki_Isaret"), "yalnız bitiş yetmez")
```

```solution
rule Iki_Isaret {
    strings:
        $bas = "LAB_START"
        $son = "LAB_END"
    condition:
        $bas and $son
}
```

```hint
`and` her iki koşulu da ister; `or` herhangi birini yeterli sayar.
```
:::
