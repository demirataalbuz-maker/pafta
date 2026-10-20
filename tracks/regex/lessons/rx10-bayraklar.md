---
id: rx10
title: Bayraklar ve Okunaklı Desenler
summary: (?i) büyük-küçük harf, (?m) satırlar, (?s) satır sonunu geçen nokta, (?x) yorumlu ve boşluklu desen.
---

::: anlat Desenin davranışını değiştirmek
**Bayraklar** desenin bütününe uygulanan ayarlardır. Desenin **başına** satır içi yazılabilirler; bu yazım Python, PCRE, .NET ve birçok SIEM'de aynıdır:

| Bayrak | Anlamı |
|---|---|
| `(?i)` | büyük-küçük harf duyarsız |
| `(?m)` | çok satırlı: `^` ve `$` her satırın başı ve sonu |
| `(?s)` | "dotall": `.` satır sonunu da eşler |
| `(?x)` | ayrıntılı: boşluklar yok sayılır, `#` sonrası yorumdur |

Birleştirilebilirler: `(?im)`.

```regex
(?i)hata
---
Hata HATA hata hAtA
```

```regex
(?s)BAŞLA(.*?)BİTİR
---
BAŞLA
satır 1
satır 2
BİTİR
```

`(?s)` olmadan `.` satır sonunda durur ve bu desen hiçbir şey bulamaz.

### (?x): uzun desenleri okunur kılmak
Karmaşık bir deseni tek satıra sıkıştırmak bakımı imkânsız kılar. `(?x)` ile boşluk ve satır sonları anlamsızlaşır, `#` sonrası yorum olur:

```regex
(?x)
\(  \d{3}  \)    # alan kodu, parantez içinde
\s?              # isteğe bağlı boşluk
\d{3} - \d{4}    # numara
---
(555) 123-4567 ve (212)987-6543
```

Ayrıntılı kipte gerçek bir boşluğu eşlemek için `\ ` ya da `[ ]` yazmalısın.

> [!TUZAK]
> `(?i)` Türkçe'de sürprizlere yol açabilir: Unicode kuralına göre `I`'nın küçüğü `i`'dir, `ı` değil. `(?i)ışık` deseni `IŞIK`'ı **eşlemez**. Türkçe metinde büyük-küçük harf duyarsızlığı istiyorsan ilgili harfleri açıkça sınıf olarak yaz: `[ıI]ş[ıI]k`.
:::

::: tahmin
Eşleşmeleri ayrı satırlara yaz:

```regex
(?i)hata
```

```stdin
Hata HATA hata
```

???

`Hata`, `HATA`, `hata`. Bayrak sayesinde büyük-küçük harf farkı yok sayılır; eşleşmeler metindeki orijinal yazımla döner.
:::

::: gorev Hata satırları
Bir log metninde `error` ile **başlayan** satırların tamamını bul; büyük-küçük harf fark etmesin.

```starter
^ERROR.*
```

```test
metin = "ERROR disk dolu\ninfo tamam\nerror ağ yok\nwarn: error değil"
eq(bul(metin), ["ERROR disk dolu", "error ağ yok"], "error ile başlayan satırlar")
```

```solution
(?im)^error.*
```

```hint
İki bayrak birden: `(?im)`. Satır başı `^`.
```
:::

::: gorev Blok içeriği
`BAŞLA` ile `BİTİR` arasındaki metni **1. grupta** yakala; arada satır sonları olabilir. Testler `grup(metin, 1)` ile okuyacak.

```starter
BAŞLA(.*?)BİTİR
```

```test
eq(grup("BAŞLA\nsatır 1\nsatır 2\nBİTİR", 1), "\nsatır 1\nsatır 2\n", "çok satırlı blok")
eq(grup("önce BAŞLA tek satır BİTİR sonra", 1), " tek satır ", "tek satırlık blok")
```

```solution
(?s)BAŞLA(.*?)BİTİR
```

```hint
Noktanın satır sonunu da eşlemesi için `(?s)`.
```
:::

::: gorev Okunaklı telefon deseni
`(555) 123-4567` biçimindeki numaraları bul; parantezden sonraki boşluk isteğe bağlı. Deseni `(?x)` kipiyle, parçaları ayırarak ve en az bir yorum satırıyla yaz.

```starter
\(\d{3}\) \d{3}-\d{4}
```

```test
eq(bul("(555) 123-4567 ve (212)987-6543 ama 555-1234 değil"), ["(555) 123-4567", "(212)987-6543"], "iki numara")
ok(desen.lstrip().startswith("(?x)"), "desen (?x) ile başlamalı")
ok("#" in desen, "en az bir yorum (#) içermeli")
```

```solution
(?x)
\( \d{3} \)   # alan kodu
\s?           # isteğe bağlı boşluk
\d{3} - \d{4} # numara
```

```hint
`(?x)` kipinde boşluklar yok sayılır; parantezleri `\(` ve `\)` ile kaçışlamayı unutma.
```
:::
