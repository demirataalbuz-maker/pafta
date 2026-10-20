---
id: yr17
title: Proje · Eğitim Paketi Biçimi
summary: Başlık, sürüm, boyut, işaret eşiği ve dar dışlamayı aynı kuralda birleştir.
---

::: anlat Tespit sözleşmesini önce yaz
Bu proje için hayali bir dosya biçimi tanımlıyoruz: ilk altı bayt `PFLAB!`, sonraki bayt sürüm 1 veya 2; dosya boyutu 16–512 bayt; içerikte ALPHA, BETA, GAMMA özelliklerinden en az ikisi. Bunlar etkisiz eğitim işaretleri. Hiçbir işletim sistemi bu biçimi program olarak çalıştırmaz.

Kuralı yazmadan önce şartları bir kontrol listesine çevir. Her olumlu örnek bütün şartları sağlamalı. Her olumsuz örnek ise mümkünse yalnız bir şartı değiştirmeli: sürüm, başlık konumu, eksik özellik veya boyut. Böylece hangi şartı atladığını test sonucu söyleyebilir.

```yara
rule Paket_Ornek {
    strings:
        $bas = "PFLAB!"
        $a = "ALPHA"
        $b = "BETA"
        $c = "GAMMA"
    condition:
        $bas at 0 and filesize >= 16 and filesize <= 512 and (uint8(6) == 1 or uint8(6) == 2) and 2 of ($a, $b, $c)
}
```
:::

::: anlat İzin işaretini bütün dosyaya yayma
İkinci görev biçime bir eğitim modu ekler: konum 7'de tam `SAFE` varsa dosya test paketi kabul edilsin ve tespit raporlanmasın. Aynı SAFE sözcüğü gövdede geçiyorsa dışlama yapmasın. Böylece “izinli metin bir yerde bulundu” gibi aşırı geniş bir filtre yerine biçimin tanımlı alanına bakarsın.

Bu işaret bir üretim güven mekanizması değildir. Gerçek bir tespit sistemindeki güven kararı taklit edilebilir metinlerden ibaret olmamalıdır. Burada öğrendiğimiz şey, koşulun kapsamını açıkça tarif etmek ve negatif testle korumaktır.

Kaynak: [Resmî YARA belgeleri](https://yara.readthedocs.io/en/stable/writingrules.html).
:::

::: tahmin
Girdi kutusundaki veriyi bu kuralla tara. Hangi kural adı yazılır; neden?

```yara
rule Paket_Ornek {
    strings:
        $bas = "PFLAB!"
        $a = "ALPHA"
        $b = "BETA"
        $c = "GAMMA"
    condition:
        $bas at 0 and filesize >= 16 and filesize <= 512 and (uint8(6) == 1 or uint8(6) == 2) and 2 of ($a, $b, $c)
}
```

```stdin
hex: 50 46 4C 41 42 21 01 41 4C 50 48 41 20 42 45 54 41
```

???

`Paket_Ornek` eşleşir. Başlık, sürüm 1, 17 bayt boyut ve ALPHA/BETA özellikleri koşulları sağlar.
:::

::: gorev Biçim dedektörü
`Paket` kuralı anlatımdaki bütün biçim koşullarını sağlasın: PFLAB! sıfırda, sürüm baytı 1 veya 2, 16–512 bayt ve ALPHA/BETA/GAMMA'dan en az ikisi.

```starter
// Koşulları ve gereken bölümleri görev metnine göre tamamla.
rule Paket { condition: false }
```

```test
def paket(version=1, body=b"ALPHA BETA"):
    return b"PFLAB!" + bytes([version]) + body
ok(eslesir(paket(), "Paket"), "sürüm bir")
ok(eslesir(paket(2, b"GAMMA BETA"), "Paket"), "sürüm iki ve başka kombinasyon")
ok(not eslesir(paket(3), "Paket"), "sürüm üç kabul edilmez")
ok(not eslesir(b"x" + paket(), "Paket"), "başlık kaymış")
ok(not eslesir(paket(body=b"ALPHA xxxx"), "Paket"), "tek özellik")
ok(not eslesir(paket() + b"x" * 512, "Paket"), "fazla büyük")
ok(not eslesir(b"PFLAB!\x01", "Paket"), "çok kısa")
```

```solution
rule Paket {
    strings:
        $bas = "PFLAB!"
        $a = "ALPHA"
        $b = "BETA"
        $c = "GAMMA"
    condition:
        $bas at 0 and filesize >= 16 and filesize <= 512 and (uint8(6) == 1 or uint8(6) == 2) and 2 of ($a, $b, $c)
}
```

```hint
Tek tek şartları and ile bağla; sürüm seçeneklerini parantez içine al.
```
:::

::: gorev Dar eğitim dışlaması
`Paket_Filtreli` önceki bütün koşulları korusun; ek olarak `SAFE` **konum 7'de** başlarsa eşleşmesin. Gövdedeki SAFE eşleşmeyi engellemesin.

```starter
// Koşulları ve gereken bölümleri görev metnine göre tamamla.
rule Paket_Filtreli { condition: false }
```

```test
ok(eslesir(b"PFLAB!\x01ALPHA BETA", "Paket_Filtreli"), "normal paket")
ok(not eslesir(b"PFLAB!\x01SAFE ALPHA BETA", "Paket_Filtreli"), "başlıkta eğitim alanı")
ok(eslesir(b"PFLAB!\x01xxxx ALPHA BETA SAFE", "Paket_Filtreli"), "gövdedeki SAFE dışlama değildir")
ok(not eslesir(b"PFLAB!\x03ALPHA BETA", "Paket_Filtreli"), "eski sürüm kontrolü korunmalı")
ok(not eslesir(b"PFLAB!\x01ALPHA xxxx", "Paket_Filtreli"), "özellik eşiği korunmalı")
```

```solution
rule Paket_Filtreli {
    strings:
        $bas = "PFLAB!"
        $a = "ALPHA"
        $b = "BETA"
        $c = "GAMMA"
        $izinli = "SAFE"
    condition:
        $bas at 0 and filesize >= 16 and filesize <= 512 and (uint8(6) == 1 or uint8(6) == 2) and 2 of ($a, $b, $c) and not ($izinli at 7)
}
```

```hint
not $izinli bütün dosyayı etkiler; not ($izinli at 7) yalnız tanımlı alanı dışlar.
```
:::
