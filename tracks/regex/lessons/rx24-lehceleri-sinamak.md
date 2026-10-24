---
id: rx24
title: Lehçeleri Gerçek Motorlarda Sınamak
summary: RX16'daki lehçe bilgisini dört gerçek motorda ölçmek: Python re, PCRE2, .NET ve JavaScript. Aynı yazımın farklı anlamı: \d ve \w'nun Unicode kapsamı, \b, satır içi bayraklar, $ ve son satır sonu, adlı grupların numarası, BMP dışı karakterler (emoji) ve UTF-16; bir deseni hedef motora taşırken neyi değiştirmek gerektiği.
---

::: anlat Desteklenmek, aynı anlama gelmek değildir
RX16'da hangi yapının hangi lehçede **bulunduğunu** gördün. Daha sinsi sorun, aynı yazımın her yerde bulunup **farklı şey eşlemesidir**. Bu dersin her adımı belirtilen motorun kendisinde çalışır: Python `re` (yolun her zamanki tezgahı), PCRE2 10.47 (UTF ve UCP kipinde), .NET Framework (Windows PowerShell 5.1'in `-match`'i ve `Select-String`'i bu motoru kullanır) ve Node'un JavaScript `RegExp`'i (`gu` bayraklarıyla). Aşağıdaki her hücre ölçülmüştür:

| Desen · metin | Python | PCRE2 | .NET | JavaScript |
|---|---|---|---|---|
| `\d+` · `1 ٣٤ ２` | `1`, `٣٤`, `２` | `1`, `٣٤`, `２` | `1`, `٣٤`, `２` | yalnız `1` |
| `\w+` · `çay ışık` | `çay`, `ışık` | `çay`, `ışık` | `çay`, `ışık` | `ay`, `k` |
| `\bış` · `ışık` | `ış` | `ış` | `ış` | hiçbiri |
| `(?i)istanbul` · `İSTANBUL ıstanbul` | ikisi | hiçbiri | `İSTANBUL` | derleme hatası |
| `(?<y>\d+)` | derleme hatası (`(?P<y>…)` ister) | ✓ | ✓ | ✓ |
| `(?<=a+)b` · `aab` | hata: sabit genişlik | hata | `b` | `b` |
| `ab$` · `ab⏎` | `ab` | `ab` | `ab` | hiçbiri |
| `😀+` · `😀😀 😀` | `😀😀`, `😀` | `😀😀`, `😀` | `😀`, `😀`, `😀` | `😀😀`, `😀` |
| `\p{L}+` · `çay 1` | hata | `çay` | `çay` | `çay` |
| `a++b`, `(?>a+)b` | ✓, ✓ | ✓, ✓ | hata, ✓ | hata, hata |

Bu tablodan çıkan dersler:

- **Rakam ve harf sınıfları Unicode'a göre farklıdır.** .NET, Python ve PCRE2 (UCP) `\d` ile Arapça-Hint ve tam genişlikli rakamları da eşler. Bir port ya da kimlik numarası doğrularken `\d` yerine **`[0-9]`** yaz; `٨٠` bir port değildir. JavaScript'te `\w` ve `\b` yalnız ASCII'dir: Türkçe bir kelime `\w+` ile parçalanır; `u` bayrağıyla `\p{L}` kullan.
- **Satır içi bayraklar** (`(?i)`, `(?m)`, `(?x)`) JavaScript'te yoktur; bayrak deseni değil `RegExp`'i kuran kodu ilgilendirir (`/…/i`). Bayrağı değiştiremediğin bir yerde deseni ona göre yazarsın.
- **`$`** Python, PCRE2 ve .NET'te metnin sonundaki **son satır sonundan önce** de eşleşir; JavaScript'te (`m` bayrağı olmadan) yalnız metnin gerçek sonunda. Metnin sonu için `\z` (.NET, PCRE2) kullanılır, ama JavaScript'te `\z` yoktur.
- **Emoji iki birimdir.** .NET metni UTF-16 birimleriyle işler: `😀+`'daki `+` emojinin yalnız ikinci yarısına uygulanır ve `😀😀` iki ayrı eşleşme olur; `.` bir emojinin yarısını eşleyebilir. JavaScript'te `u` bayrağı bunu düzeltir.

```regex
\d+|😀+
---
1 ٣٤ 😀😀
```

```meta
motor: javascript
```
:::

::: anlat .NET'in grup numaraları
Aynı desende grupların **numarası** da lehçeye göre değişir. .NET adlı grupları, adsız grupların **hepsinden sonra** numaralar; Python, PCRE2 ve JavaScript ise açılış sırasına bakar:

| `(?<y>\d{4})-(?<a>\d{2})\|x(y)?` | 1. grup | 2. grup | 3. grup |
|---|---|---|---|
| JavaScript, PCRE2 | `y` | `a` | `(y)?` |
| .NET | `(y)?` | `y` | `a` |

Bir deseni PowerShell'e taşıyıp `$Matches[1]` ile okuyan bir betik, bu yüzden sessizce yanlış alanı okur. Kural: adlı grupları **adlarıyla** oku (`$Matches.y`, `m.groups.y`), adlı ve adsız grupları aynı desende karıştırma.

```regex
(?<y>\d{4})-(?<a>\d{2})|x(y)?
---
2026-10 ve x
```

```meta
motor: dotnet
```

Kaynak: [.NET grup numaralandırma kuralı](https://learn.microsoft.com/en-us/dotnet/standard/base-types/grouping-constructs-in-regular-expressions#named-matched-subexpressions), [ECMAScript RegExp ve u bayrağı](https://tc39.es/ecma262/multipage/text-processing.html#sec-regexp-regular-expression-objects).
:::

::: tahmin Aynı desen, .NET'te
Hangi parçalar yakalanır? Ayrı satırlara yaz.

```regex
\d+|😀+
```

```stdin
1 ٣٤ 😀😀
```

```meta
motor: dotnet
```

???

`1`, `٣٤`, `😀`, `😀`. .NET'te `\d` Arapça-Hint rakamlarını da kapsar: `٣٤` bir sayıdır. `😀` UTF-16'da iki birimdir (bir vekil çifti); `+` yalnız ikinci birime uygulandığı için yan yana iki emoji tek bir `😀+` eşleşmesi olmaz, iki ayrı eşleşme olur. Aynı desen JavaScript'te (`u` bayrağıyla) `1` ve `😀😀` verir.
:::

::: gorev JavaScript'te Türkçe kelimeler
JavaScript motorunda bir metindeki **kelimeleri** bul: harflerden oluşan, en az bir harfli diziler. Türkçe harfler (`ç ğ ı ö ş ü İ` ve büyükleri) kelimenin parçasıdır; rakamlar, alt çizgi, kesme işareti ve noktalama kelime değildir.

```meta
motor: javascript
```

```starter
\w+
```

```test
eq(bul("çay ışık İzmir"), ["çay", "ışık", "İzmir"], "Türkçe harfler kelimenin parçası")
eq(bul("İzmir'de 3 gün"), ["İzmir", "de", "gün"], "kesme işareti ve rakam kelimeyi böler")
eq(bul("kullanici_adi"), ["kullanici", "adi"], "alt çizgi harf değildir")
eq(bul("ÇĞIİÖŞÜ çğıiöşü"), ["ÇĞIİÖŞÜ", "çğıiöşü"], "bütün Türkçe harfler, iki büyüklükte")
eq(bul("123 _ !?"), [], "harfsiz metin")
eq(bul(""), [], "boş metin")
ok(tam("Ağrı") and not tam("Ağrı2"), "tam kelime")
```

```solution
\p{L}+
```

```hint
JavaScript'te `\w` yalnız `[A-Za-z0-9_]`'dir. Bu motor `u` bayrağıyla çalışır; Unicode özellik sınıfları kullanılabilir.
```

```hint
`\p{L}` her dildeki harfi kapsar.
```
:::

::: gorev .NET'te yalnız ASCII port
PowerShell betiğinde bir port numarasını doğrulayan deseni yaz: metnin **tamamı** 1 ile 65535 arasında, başında gereksiz sıfır olmayan bir sayı olmalı. .NET motorunda çalışır; `\d`'nin burada başka yazı sistemlerinin rakamlarını da eşlediğini unutma: `٨٠` (Arapça-Hint 80) bir port **değildir**.

```meta
motor: dotnet
```

```starter
\d{1,5}
```

```test
for p in ("1", "22", "80", "443", "8080", "65535", "9999", "10000", "59999", "64999", "65499", "65529"):
    ok(tam(p), f"geçerli port {p}")
for p in ("0", "65536", "65540", "65600", "66000", "70000", "99999", "100000", "080", "00", "-1", "", "8 0", "80 "):
    ok(not tam(p), f"geçersiz port {p!r}")
for p in ("٨٠", "８０", "٤٤٣", "1٠"):
    ok(not tam(p), f"ASCII olmayan rakam {p!r}")
```

```solution
(?:[1-9][0-9]{0,3}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])
```

```hint
`\d` yerine `[0-9]`. Aralığı basamak sayısına göre dallara böl: 1–9999, 10000–59999, 60000–64999, 65000–65499, 65500–65529, 65530–65535.
```

```hint
`tam()` deseni metnin bütününe uygular; çapa gerekmez. İlk basamak 0 olamaz: tek basamakta da `[1-9]`.
```
:::

::: gorev Bayrak koyamadığın motorda satır sonu
Bir günlük metninde **`HATA` ile biten satırların son kelimesini değil, satırın tamamını** bul. Motor JavaScript'tir ve bayrakları (`gu`) sen değiştiremezsin: `m` bayrağı yok, satır içi `(?m)` de JavaScript'te yazılamaz. Satırlar `\n` ile ayrılır; son satırın sonunda satır sonu olabilir de olmayabilir de. Eşleşen satır, satır sonu karakterini içermemeli.

```meta
motor: javascript
```

```starter
.*HATA$
```

```test
metin = "10:00 disk HATA\n10:01 tamam\n10:02 ağ HATA\n10:03 HATA değil\n10:04 son HATA"
eq(bul(metin), ["10:00 disk HATA", "10:02 ağ HATA", "10:04 son HATA"], "üç satır; ortada HATA geçen satır değil")
eq(bul(metin + "\n"), ["10:00 disk HATA", "10:02 ağ HATA", "10:04 son HATA"], "son satırın sonunda satır sonu olsa da")
eq(bul("HATA"), ["HATA"], "tek satır, yalnız HATA")
eq(bul("tamam\nHATALAR"), [], "HATALAR, HATA ile bitmez")
eq(bul("a HATA\n\nb HATA"), ["a HATA", "b HATA"], "boş satır arada")
eq(bul(""), [], "boş metin")
ok(all("\n" not in s for s in bul(metin + "\n")), "eşleşmelerde satır sonu yok")
```

```solution
[^\n]*HATA(?=\n|$)
```

```hint
`m` bayrağı olmadan JavaScript'te `$` yalnız metnin en sonudur. Satır sonunu kendin tarif et: ardından ya `\n` ya da metnin sonu gelmeli (`(?=\n|$)`).
```

```hint
`.` JavaScript'te satır sonunu eşlemez ama açık olmak için `[^\n]*` yaz: satırın başından `HATA`'ya kadar.
```
:::
