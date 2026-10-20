---
id: yr14
title: Hash Modülü · Birebir Kimlik
summary: Bütün dosya ve alan hashlerini ayır; bir bayt değişiminin etkisini test et.
---

::: anlat Hash aynı dosyayı bulmak için
`import "hash"` modülü, dosyanın belirli baytlarının özetini hesaplar. `hash.sha256(0, filesize)` bütün veriyi kapsar. Sonuç küçük harfli hex metindir; koşuldaki beklenen değer de aynı biçimde olmalıdır.

Tam dosya özeti aynı örneği tanımada çok seçicidir. Buna karşılık tek bayt değişikliği, zararsız bir sürüm güncellemesi bile, özeti değiştirir. Bu yüzden hash eşitliği dosya ailesindeki bütün varyantları yakalayan yapısal bir kuralın yerini tutmaz. Bu dersin referansı sıradan bir eğitim metnidir.

```yara
import "hash"                                                        #! kriptografik özet modülü
rule Referans {
    condition:
        hash.sha256(0, filesize) == "358a8d18b877ed16ad935c687f59f2f87de8358d58735f5debbde4511215fbdc" #! 0. bayttan itibaren filesize uzunluğunda SHA-256
}
```

> [!DERİN] `hash.sha256(offset, length)` ikinci parametresi uzunluktur!
> Dilimleme kullanan dillerin aksine `hash.sha256(4, 8)` konum 4'ten konum 8'e kadar değil, **konum 4'ten başlayarak 8 bayt** (`4..11`) okur! Sabit bir başlık veya bölüm özetini alırken `(başlangıç, uzunluk)` çiftini doğru hesapla.
:::

::: anlat Aralık özeti ve sınır denetimi
`hash.sha256(4, 8)` konum 4'ten başlayan 8 baytın özetidir; ikinci argüman bitiş konumu değildir. Dosya biçiminde sabit bir bölümü doğrularken önce o alanın dosyada bulunduğunu denetle. Örneğin konum 4'te dört bayt için en az sekiz bayt gerekir.

Modül MD5 ve SHA1 de sunar; bunlar eski örnek kimliği listelerinde görülebilir. Burada yeni örneklerimizde SHA256 kullanıyoruz. Bir hash eşleşmesi yalnızca verinin kimliğine dair bulgudur; dosyanın nereden geldiği ve neden önemli olduğu ayrı analiz bilgisidir.

> [!TUZAK] Büyük harfli hex özet yazmak
> `hash.md5`, `hash.sha1` ve `hash.sha256` her zaman **küçük harfli** onaltılık metin döndürür. Tehdit istihbaratı raporundan kopyaladığın büyük harfli (`"358A8D..."`) özeti küçük harfe çevirmeden `==` ile karşılaştırırsan kural hiçbir zaman eşleşmez!

Kaynak: [Resmî YARA belgeleri](https://yara.readthedocs.io/en/stable/modules/hash.html).
:::

::: tahmin
Girdi kutusundaki veriyi bu kuralla tara. Hangi kural adı yazılır; neden?

```yara
import "hash"
rule Referans {
    condition:
        hash.sha256(0, filesize) == "358a8d18b877ed16ad935c687f59f2f87de8358d58735f5debbde4511215fbdc"
}
```

```stdin
PAFTA_REFERENCE_V1
```

???

`Referans` eşleşir; girdi, özeti kuralda bulunan referans verinin birebir aynısıdır.
:::

::: gorev Birebir referans
`Tam_Referans` kuralı yalnızca `PAFTA_REFERENCE_V1` verisinin bütün dosya SHA256 özetiyle eşleşsin. Beklenen özet: `358a8d18b877ed16ad935c687f59f2f87de8358d58735f5debbde4511215fbdc`.

```starter
// Koşulları ve gereken bölümleri görev metnine göre tamamla.
rule Tam_Referans { condition: false }
```

```stdin
PAFTA_REFERENCE_V1
```

```test
ok(eslesir(b"PAFTA_REFERENCE_V1", "Tam_Referans"), "birebir referans")
ok(not eslesir(b"PAFTA_REFERENCE_V2", "Tam_Referans"), "tek bayt değişik")
ok(not eslesir(b"xPAFTA_REFERENCE_V1", "Tam_Referans"), "önek eklenmiş")
ok(not eslesir(b"PAFTA_REFERENCE_V1\n", "Tam_Referans"), "satır sonu da bayttır")
```

```solution
import "hash"
rule Tam_Referans {
    condition:
        hash.sha256(0, filesize) == "358a8d18b877ed16ad935c687f59f2f87de8358d58735f5debbde4511215fbdc"
}
```

```hint
Dosyanın tamamı için başlangıç 0 ve uzunluk filesize olmalı.
```
:::

::: gorev Sabit alan özeti
`Alan_Ozeti` kuralı en az sekiz baytlık veride konum 4'teki dört baytın SHA256 değerini denetlesin. Beklenen alan `ABCD`, özeti `e12e115acf4552b2568b55e93cbd39394c4ef81c82447fafc997882a02d23677`; alan dışındaki baytlar değişebilir.

```starter
// Koşulları ve gereken bölümleri görev metnine göre tamamla.
rule Alan_Ozeti { condition: false }
```

```stdin
HEADABCDTAIL
```

```test
ok(eslesir(b"HEADABCDTAIL", "Alan_Ozeti"), "alan doğru")
ok(eslesir(b"xxxxABCD", "Alan_Ozeti"), "alan dışı değişebilir")
ok(not eslesir(b"HEADABCETAIL", "Alan_Ozeti"), "alan değişti")
ok(not eslesir(b"ABCDHEAD", "Alan_Ozeti"), "doğru bayt yanlış konumda")
ok(not eslesir(b"HEADABC", "Alan_Ozeti"), "kısa dosya")
```

```solution
import "hash"
rule Alan_Ozeti {
    condition:
        filesize >= 8 and hash.sha256(4, 4) == "e12e115acf4552b2568b55e93cbd39394c4ef81c82447fafc997882a02d23677"
}
```

```hint
İkinci hash argümanı uzunluktur; 4..8 gibi bir bitiş konumu değildir.
```
:::
