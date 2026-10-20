---
id: yr06
title: YARA İçinde Düzenli İfadeler
summary: YARA regex sözdizimi, sınırlı tekrar ve metin değiştiricilerini gerçek motorla dene.
---

::: anlat Regex bir arama aracı, dilin bütünü değil
YARA regex tanımı eğik çizgiler arasındadır: `/LAB[0-9]{3}/`. Bu Python `re` ya da PCRE motorunun aynısı değildir. Geri başvuru ve bakınma gibi her başka regex dilindeki özelliğin burada bulunduğunu varsayma. Desteklenen yapıları YARA belgesinden kontrol et; dersler bu motorda gerçekten derlenir.

`[0-9]`, `{3}` ve alternatifler, değişken ama sınırlı işaretleri tarif eder. Nokta ve `*` ile bütün dosyayı yutmaya çalışmak yerine, biçimde beklediğin karakter sınıfını ve uzunluk sınırını kullan.

```yara
rule Kayit_No {
    strings:
        $a = /LAB-[0-9]{3};/
    condition:
        $a
}
```
:::

::: anlat Sınırlar ve kaçışlar
Bir metin içindeki nokta literal olacaksa `\.` yazılır. Regex sonundaki `nocase` değiştiricisi metin tanımlarına benzer biçimde harf farkını yok sayabilir. Regex ile `fullword` de kullanılabilir; ama o zaman regexin başı ve sonundaki karakterlerin sözcük sınırıyla ilişkisini ayrıca düşün.

Bu görevlerde sahte dosya sürümü ve iş kimliği arıyoruz. Olumsuz örnekler eksik basamak, fazla basamak ve benzer uzantıları içerir. Kuralın bir pozitif örneği bulması kadar, yakın komşularını reddetmesi de öğretilen davranışın parçasıdır.

Kaynak: [Resmî YARA belgeleri](https://yara.readthedocs.io/en/stable/writingrules.html).
:::

::: tahmin
Girdi kutusundaki veriyi bu kuralla tara. Hangi kural adı yazılır; neden?

```yara
rule Kayit_No {
    strings:
        $a = /LAB-[0-9]{3};/
    condition:
        $a
}
```

```stdin
kayit=LAB-207; son
```

???

`Kayit_No` eşleşir. Üç rakamdan sonra noktalı virgül gelir.
:::

::: gorev Sabit kimlik biçimi
`Is_Kimligi` kuralı `JOB-`, tam dört rakam ve `;` dizisini bulsun. Küçük harfli job kabul edilmesin.

```starter
// Koşulları ve gereken bölümleri görev metnine göre tamamla.
rule Is_Kimligi { condition: false }
```

```test
ok(eslesir("JOB-0042;", "Is_Kimligi"), "dört rakam")
ok(not eslesir("JOB-042;", "Is_Kimligi"), "eksik rakam")
ok(not eslesir("JOB-00042;", "Is_Kimligi"), "fazla rakam")
ok(not eslesir("job-0042;", "Is_Kimligi"), "harf farkı korunmalı")
```

```solution
rule Is_Kimligi {
    strings:
        $a = /JOB-[0-9]{4};/
    condition:
        $a
}
```

```hint
Rakam tekrarını {4} ile sınırla; bitiş işaretini de desene dahil et.
```
:::

::: gorev Nokta gerçek nokta
`Ayar_Dosyasi` kuralı `pafta.conf` sözcüğünü harf farkı olmadan bulsun; `paftaXconf` ve `pafta.configuration` eşleşmesin.

```starter
// Koşulları ve gereken bölümleri görev metnine göre tamamla.
rule Ayar_Dosyasi { condition: false }
```

```test
ok(eslesir("file=PAFTA.CONF;", "Ayar_Dosyasi"), "harf farkı yok")
ok(not eslesir("paftaXconf", "Ayar_Dosyasi"), "nokta joker olmamalı")
ok(not eslesir("pafta.configuration", "Ayar_Dosyasi"), "sözcük sonu")
```

```solution
rule Ayar_Dosyasi {
    strings:
        $a = /pafta\.conf/ nocase fullword
    condition:
        $a
}
```

```hint
Regex noktasını kaçır: \. Ardından nocase ve fullword eklenebilir.
```
:::
