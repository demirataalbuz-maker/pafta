---
id: rx06
title: Adlı Gruplar ve Geri Başvuru
summary: (?P<ad>...) ile kendini anlatan desenler; \1 ve (?P=ad) ile aynı metnin tekrarını aramak.
---

::: anlat Gruplara isim ver
Numaralı gruplar beş-altı tane olunca okunmaz hale gelir: "4. grup neydi?" **Adlı gruplar** deseni kendini belgeleyen bir yapıya çevirir:

```regex
(?P<kullanici>[\w.]+)@(?P<alan>[\w.-]+)
---
ali.veli@ornek.com, destek@site.org
```

Tabloda gruplar artık `kullanici=...` ve `alan=...` olarak görünüyor. Programlama dillerinde bu bir sözlük olarak alınır (Python'da `m.groupdict()`).

> [!NOT]
> Sözdizimi motora göre değişir: Python `(?P<ad>...)`, .NET/PowerShell, JavaScript ve PCRE ise `(?<ad>...)` kullanır (Python 3.11'de bu ikinci biçim yok). Splunk'ın `rex` komutu `(?<ad>...)` ister. Bir desenle araçlar arasında taşırken önce buna bak.

### Geri başvuru: aynısı tekrar
Desen içinde `\1`, "**1. grubun yakaladığı metnin aynısı**" demektir; desenin aynısı değil, **metnin** aynısı. Adlı grupta `(?P=ad)`.

```regex
\b(\w+) \1\b
---
bu bu bir test test değil değil mi
```

Yanlışlıkla iki kez yazılmış kelimeleri bulmak için klasik desen budur. Bir başka örnek, açılış ve kapanış tırnağının aynı olmasını sağlamak:

```regex
(["']).*?\1
---
ad="ali" rol='admin' not="karışık'
```

`.*?` tembel bir niceleyicidir; RX08'de göreceksin.

> [!DERİN]
> Geri başvuru, regex'i matematiksel anlamdaki "düzenli dil" sınıfının **dışına** çıkarır: `(\w+) \1` gibi bir deseni sonlu bir otomatla tanımak mümkün değildir. Bu yüzden RE2 ve Rust'ın `regex`'i gibi garantili doğrusal zamanlı motorlar geri başvuruyu **desteklemez**. Hız garantisi ile ifade gücü arasında bir takas vardır.
:::

::: tahmin
Eşleşmeleri ayrı satırlara yaz:

```regex
(\w)\1
```

```stdin
kaar seeee oops
```

???

`aa`, `ee`, `ee`, `oo`. Her eşleşme bir harf ve hemen ardından **aynı harf**tir. `seeee` içindeki dört e iki ayrı eşleşme verir: eşleşmeler örtüşmez.
:::

::: gorev Adlı alanlar
`kullanici=ali ip=10.0.0.5` biçimindeki metinden kullanıcı adını `kullanici` adlı gruba, IP'yi `ip` adlı gruba yakalayan bir desen yaz.

```starter
kullanici=(\w+) ip=([\d.]+)
```

```test
eq(adli("olay kullanici=ali ip=10.0.0.5 durum=ok"), {"kullanici": "ali", "ip": "10.0.0.5"}, "adlı gruplar")
eq(adli("kullanici=veli_2 ip=192.168.1.20"), {"kullanici": "veli_2", "ip": "192.168.1.20"}, "alt çizgili ad")
ok("(?P<" in desen, "adlı grup sözdizimi (?P<ad>...) kullan")
```

```solution
kullanici=(?P<kullanici>\w+) ip=(?P<ip>[\d.]+)
```

```hint
`(\w+)` yerine `(?P<kullanici>\w+)`.
```
:::

::: gorev Tekrarlanan kelime
Art arda iki kez yazılmış kelimeleri bul; aralarında bir ya da daha fazla boşluk olabilir. Bir kelimenin **sonu** başka bir kelimeyle aynıysa (`kediler ler`) eşleşmemeli.

```starter
(\w+) \1
```

```test
eq(bul("bu bu bir test  test değil"), ["bu bu", "test  test"], "tekrarlanan kelimeler")
eq(bul("kediler ler"), [], "kelimenin parçası tekrar sayılmaz")
eq(bul("sorun yok"), [], "tekrar yok")
```

```solution
\b(\w+)\s+\1\b
```

```hint
İki uca da kelime sınırı koy: `\b(\w+)...\1\b`. Aradaki boşluk için `\s+`.
```
:::

::: gorev Eşleşen tırnaklar
Tek ya da çift tırnakla açılıp **aynı** tırnakla kapanan metinleri (tırnaklar dahil) bul. Açılışı çift, kapanışı tek olanlar eşleşmemeli.

```starter
["'].*?["']
```

```test
eq(bul('"a" \'b\' "c\''), ['"a"', "'b'"], "sadece aynı tırnakla kapananlar")
eq(bul("ad='ali' not=\"x\""), ["'ali'", '"x"'], "iki tür tırnak")
```

```solution
(["']).*?\1
```

```hint
Açılış tırnağını yakala, kapanışta `\1` ile aynısını iste.
```
:::
