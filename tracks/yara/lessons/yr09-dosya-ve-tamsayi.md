---
id: yr09
title: Dosya Boyutu ve Sayısal Alanlar
summary: filesize, uint8/16/32 ve endian ile küçük ikili dosya başlıklarını oku.
---

::: anlat Baytlardan sayıya
`filesize` taranan dosyanın bayt uzunluğudur. `KB` ve `MB` boyut ekleri ikili katlardır; burada küçük testler için doğrudan bayt sayısı kullanacağız. `uint16(4)` konum 4'ten iki baytı **little endian** sayıya çevirir. `uint16be(4)` aynı baytları big endian yorumlar.

Bir dosya `01 00` içeriyorsa little endian değeri 1, big endian değeri 256 olur. `uint8` tek bayt okur; işaretli türler için `int8`, `int16` gibi işlevler de vardır. Biçimin alan tanımına göre seçim yap; yazıldığı bilgisayarın mimarisini tahmin ederek karar verme.

```yara
rule Kucuk_Bicim {
    strings:
        $a = "PF"
    condition:
        filesize >= 6 and $a at 0 and uint16(2) == 1   #! 2. bayttaki 16-bit little-endian tamsayı 1 olmalı
}
```

> [!DERİN] Little-endian (`uint16`) ve Big-endian (`uint16be`)
> Bellekte `01 02` baytları dururken:
> - `uint16(konum)` düşük anlamlı baytı önce okur: `0x0201` (`513`).
> - `uint16be(konum)` yüksek anlamlı baytı önce okur: `0x0102` (`258`).
> Ağ protokolleri ve bazı arşiv başlıkları big-endian, Windows PE ve x86/x64 yapıları ise little-endian kullanır.
:::

::: anlat Önce sınır, sonra okuma
Dosyada bulunmayan baytı okumak tanımsız sonuç üretir; bir istisnayla Python kodu gibi davranacağını bekleme. Koşulu dosya uzunluğuna dair açık bir ön şartla yazmak niyeti korur. Bu dersin biçimi: iki bayt PF başlığı, iki bayt sürüm, sonra içerik.

PE gibi karmaşık dosyalarda bütün alanları elle okumak yerine PE modülünü kullanacağız. Elle okuma hâlâ küçük özel biçimler, sabit işaretler ve başlık doğrulaması için yararlıdır. Bu örnekler dosya biçimi öğrenmek içindir; veriyi çalıştırmaz.

> [!TUZAK] Tüm dosyayı tarayan string ile doğrudan `uint` okuma sırası
> `filesize` ve `uint16(2)` kontrolleri sabit zamanda ($O(1)$) çalışır. Koşulun başına `filesize` sınırını ve başlık kontrolünü koymak, boyut dışı dosyaları anlamlandırırken hem okunabilirliği hem güvenliği artırır.

Kaynak: [Resmî YARA belgeleri](https://yara.readthedocs.io/en/stable/writingrules.html).
:::

::: tahmin
Girdi kutusundaki veriyi bu kuralla tara. Hangi kural adı yazılır; neden?

```yara
rule Kucuk_Bicim {
    strings:
        $a = "PF"
    condition:
        filesize >= 6 and $a at 0 and uint16(2) == 1
}
```

```stdin
hex: 50 46 01 00 41 42
```

???

`Kucuk_Bicim` eşleşir. Dosya 6 bayt, PF sıfırda ve sürüm little endian 1.
:::

::: gorev Boyut sınırları
`Boyutlu` kuralı `PF` ile başlayan, 8–64 bayt uzunluğunda dosyaları kabul etsin; iki sınır dahil olsun.

```starter
// Koşulları ve gereken bölümleri görev metnine göre tamamla.
rule Boyutlu { condition: false }
```

```stdin
PFxxxxxx
```

```test
for n in (8, 16, 64):
    ok(eslesir(b"PF" + b"x" * (n - 2), "Boyutlu"), f"geçerli {n}")
for n in (2, 7, 65):
    ok(not eslesir(b"PF" + b"x" * (n - 2), "Boyutlu"), f"sınır dışı {n}")
ok(not eslesir(b"XX" + b"x" * 6, "Boyutlu"), "boyut tek başına yetmez")
```

```solution
rule Boyutlu {
    strings:
        $a = "PF"
    condition:
        $a at 0 and filesize >= 8 and filesize <= 64
}
```

```hint
İki boyut karşılaştırmasını ve başlığı and ile birleştir.
```
:::

::: gorev Alanı doğru endian ile oku
`Surum_Alanli` kuralı en az 8 baytlık PF dosyasında konum 2'de little endian sürüm 0x1234 ve konum 4'te big endian değer 0x0102 istesin.

```starter
// Koşulları ve gereken bölümleri görev metnine göre tamamla.
rule Surum_Alanli { condition: false }
```

```stdin
hex: 50 46 34 12 01 02 00 00
```

```test
ok(eslesir(bytes.fromhex("50 46 34 12 01 02 00 00"), "Surum_Alanli"), "iki endian alanı")
ok(not eslesir(bytes.fromhex("50 46 12 34 01 02 00 00"), "Surum_Alanli"), "little endian alan ters")
ok(not eslesir(bytes.fromhex("50 46 34 12 02 01 00 00"), "Surum_Alanli"), "big endian alan ters")
ok(not eslesir(b"PF", "Surum_Alanli"), "kısa dosya")
```

```solution
rule Surum_Alanli {
    strings:
        $a = "PF"
    condition:
        filesize >= 8 and $a at 0 and uint16(2) == 0x1234 and uint16be(4) == 0x0102
}
```

```hint
uint16 varsayılan olarak little endian; ters sıra için uint16be kullan.
```
:::
