---
id: yr16
title: Kural Tasarımı · Hassasiyet ve Maliyet
summary: Belirgin atomlar, sınırlı aramalar, xor/base64 ve yanlış pozitif regresyonu.
---

::: anlat Önce ölçülebilir bir tespit amacı
Bir kuralın amacı “şüpheli bir şey bul” kadar geniş olmamalı. Bu derste amaç, sahte bir LAB paket ailesini tanımak. Sabit ve ayırt edici işaretler, sınırlı tekrarlar ve belgelenmiş boyut sınırları hem incelemeyi hem motorun işini kolaylaştırır. Geniş regex ve iç içe bütün dosya döngüleri eklemeden önce gerçekten gerekli olup olmadıklarını sor.

Kısa `AA` gibi bir işaret üretimde çok yaygın olabilir. Mümkünse anlamlı birkaç sabit baytın birleşimini ve yapısal ön şartları kullan. Hız iddiası için gerçek veriyle ölçüm gerekir; bu dersin testleri doğruluk sınırlarını gösterir, performans benchmarkı sayılmaz.

```yara
rule Lab_Ailesi {
    strings:
        $baslik = "PF-LAB;"
        $a = "feature=alpha;"
        $b = "format=2;"
    condition:
        $baslik at 0 and $a and $b and filesize <= 4096   #! başlık konumu + iki yapısal özellik + boyut sınırı
}
```

> [!DERİN] `xor` ve `base64` değiştiricileri derleme zamanında nasıl çalışır?
> - `"PAFTA" xor(1-3)` yazdığında libyara dosyayı çalışma zamanında çözmez; derleme sırasında metnin `0x01`, `0x02` ve `0x03` ile XOR'lanmış 3 bayt dizisini üretip otomatına ekler.
> - `"PAFTA_MARKER" base64` ise metnin Base64 kodlamasında oluşabilecek 3 farklı bayt hizalamasının (offset 0, 1, 2) ortak orta parçasını üretip arar.
:::

::: anlat Dönüştürülmüş metinler de yalnız bayttır
`xor(1-3)` bir metnin tek baytlık XOR anahtarları 1, 2 veya 3 ile dönüştürülmüş biçimlerini arayabilir. `base64` ise işaretin Base64 içindeki gösterimlerini arar. Bunlar bir dosyayı açıp içerik çalıştırmaz; motor alternatif bayt desenlerini tarar. Dönüşüm tanımak, verinin niyetini kanıtlamaz.

`base64` bütün dosyayı genel amaçlı çözerek yeniden taramak değildir; kısa desenler ve kenardaki Base64 karakterleri beklenmedik eşleşme sınırları oluşturabilir. Her değiştiricinin uyum kuralları vardır: örneğin her metin değiştiricisini base64 ile birlikte kullanamazsın. Görevlerde uzun, etkisiz bir eğitim işareti ve sınırları belli dönüşüm kullanıyoruz.

> [!GÜVENLİK] Çok kısa metinlerde `xor` ve `base64` gürültüsü
> 3–4 karakterlik kısa bir metne `xor` veya `base64` uygulamak, neredeyse her ikili dosyada tesadüfen geçen bayt dizileri üretir ve hem aşırı yanlış pozitife hem de yavaşlamaya yol açar. Dönüşüm değiştiricilerini yalnızca uzun ve ayırt edici işaretlerde, mümkünse dar anahtar aralığıyla (`xor(0x01-0x1f)` gibi) kullan.

Kaynak: [Resmî YARA belgeleri](https://yara.readthedocs.io/en/stable/writingrules.html).
:::

::: tahmin
Girdi kutusundaki veriyi bu kuralla tara. Hangi kural adı yazılır; neden?

```yara
rule Lab_Ailesi {
    strings:
        $baslik = "PF-LAB;"
        $a = "feature=alpha;"
        $b = "format=2;"
    condition:
        $baslik at 0 and $a and $b and filesize <= 4096
}
```

```stdin
PF-LAB;feature=alpha;format=2;
```

???

`Lab_Ailesi` eşleşir. Başlık sıfırda, iki özellik mevcut ve dosya boyut sınırının altındadır.
:::

::: gorev Yakın yanlış pozitifleri ayır
`Hassas_Lab` kuralı PF-LAB; başlığı sıfırda, `feature=alpha;` ve `format=2;` işaretleri birlikte, dosya en fazla 4096 bayt ise eşleşsin.

```starter
// Koşulları ve gereken bölümleri görev metnine göre tamamla.
rule Hassas_Lab { condition: false }
```

```stdin
PF-LAB;feature=alpha;format=2;
```

```test
positives = [b"PF-LAB;feature=alpha;format=2;", b"PF-LAB;format=2; other;feature=alpha;"]
negatives = [b"manual PF-LAB;feature=alpha;format=2;", b"PF-LAB;feature=beta;format=2;", b"PF-LAB;feature=alpha;format=3;", positives[0] + b"x" * 4096, b""]
eq(sum(eslesir(x, "Hassas_Lab") for x in positives), len(positives), "olumlu kümenin tamamı")
eq(sum(eslesir(x, "Hassas_Lab") for x in negatives), 0, "yakın olumsuz kümede yanlış pozitif yok")
for boyut in (4095, 4096, 4097):
    veri = positives[0] + b"x" * (boyut - len(positives[0]))
    eq(eslesir(veri, "Hassas_Lab"), boyut <= 4096, f"biçim sabitken boyut sınırının komşusu: {boyut} bayt")
```

```solution
rule Hassas_Lab {
    strings:
        $baslik = "PF-LAB;"
        $a = "feature=alpha;"
        $b = "format=2;"
    condition:
        $baslik at 0 and $a and $b and filesize <= 4096
}
```

```hint
Bir şartı değişmiş komşu örneklerin her birini reddet.
```
:::

::: gorev Sınırlı XOR tanıma
`Xor_Isaret` kuralı `PAFTA_XOR_LAB_MARKER` işaretinin yalnız 1, 2 veya 3 tek bayt anahtarla XOR edilmiş biçimlerini yakalasın; düz metin ve anahtar 4 kabul edilmesin.

```starter
// Koşulları ve gereken bölümleri görev metnine göre tamamla.
rule Xor_Isaret { condition: false }
```

```stdin
Q@GU@^YNS^M@C^L@SJDS
```

```test
raw = b"PAFTA_XOR_LAB_MARKER"
for key in (1, 2, 3):
    data = bytes(x ^ key for x in raw)
    ok(eslesir(data, "Xor_Isaret"), f"izinli anahtar {key}")
ok(not eslesir(raw, "Xor_Isaret"), "anahtar sıfır bu aralıkta değil")
ok(not eslesir(bytes(x ^ 4 for x in raw), "Xor_Isaret"), "anahtar dört aralık dışında")
```

```solution
rule Xor_Isaret {
    strings:
        $a = "PAFTA_XOR_LAB_MARKER" xor(1-3)
    condition:
        $a
}
```

```hint
xor tek başına daha geniş bir anahtar kümesini kapsar; görev aralığı xor(1-3).
```
:::

::: gorev Base64 içindeki işaret
`B64_Isaret` kuralı `PAFTA_BASE64_LAB_MARKER` işaretinin Base64 gösterimini bulsun. Düz işaret tek başına eşleşmesin.

```starter
// Koşulları ve gereken bölümleri görev metnine göre tamamla.
rule B64_Isaret { condition: false }
```

```stdin
UEFGVEFfQkFTRTY0X0xBQl9NQVJLRVJ0YWls
```

```test
import base64
raw = b"PAFTA_BASE64_LAB_MARKER"
for prefix in (b"", b"x", b"xx"):
    ok(eslesir(base64.b64encode(prefix + raw + b"tail"), "B64_Isaret"), "üç Base64 hizası")
ok(not eslesir(raw, "B64_Isaret"), "düz metin ayrı gösterimdir")
ok(not eslesir(base64.b64encode(b"OTHER_BASE64_LAB_MARKER"), "B64_Isaret"), "başka işaret")
```

```solution
rule B64_Isaret {
    strings:
        $a = "PAFTA_BASE64_LAB_MARKER" base64
    condition:
        $a
}
```

```hint
base64 modifier işaretin kodlanmış biçimlerini tarar; normal metin araması ekleme.
```
:::
