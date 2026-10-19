---
id: rx03
title: Niceleyiciler
summary: Kaç kez? *, +, ?, {n}, {n,}, {n,m} ve önceki öğeye uygulanma kuralı.
---

::: anlat Kaç kez?
**Niceleyiciler** kendilerinden **hemen önceki** öğenin kaç kez tekrarlanacağını söyler:

| Niceleyici | Anlamı |
|---|---|
| `*` | 0 ya da daha fazla |
| `+` | 1 ya da daha fazla |
| `?` | 0 ya da 1 (isteğe bağlı) |
| `{3}` | tam 3 |
| `{2,}` | en az 2 |
| `{2,4}` | 2 ile 4 arası |

```regex
colou?r
---
color colour colouur
```

`u?` "u olabilir de olmayabilir de" demektir. `colouur`'da iki u var, bu yüzden tutmaz.

"Önceki öğe" tek bir karakter, bir karakter sınıfı ya da parantezli bir grup olabilir (P05):

```regex
\d{3}-\d{4}
---
555-1234, 55-12345, 5555-12345
```

Üçüncü eşleşmeye dikkat: `5555-12345` içinden `555-1234` çıktı. Niceleyici "en az/en çok bu kadar" der ama desene "burada başla, burada bit" demez. Sınırları P04'te öğreneceksin.

```regex
a{2,3}
---
a aa aaa aaaa
```

`aaaa` metninden önce `aaa` alınır (niceleyiciler **açgözlüdür**: olabildiğince fazla alır), kalan tek `a` ise yetmez. Açgözlülüğü P07'de derinlemesine göreceğiz.

> [!TUZAK]
> `ab+` "a, sonra bir ya da daha fazla b" demektir, "ab'nin tekrarı" değil. Tekrar edilecek şey birden fazla karakterse onu grupla: `(ab)+`.
:::

::: tahmin
Eşleşmeleri ayrı satırlara yaz:

```regex
\d+
```

```stdin
a1b22c333
```

???

`1`, `22`, `333`. `+` olabildiğince çok rakam alır, bu yüzden `22` iki ayrı `2` değil tek bir eşleşmedir.
:::

::: gorev İki yazım
Hem `color` hem `colour` yazımını eşle, `colouur`'u eşleme.

```starter
colour
```

```test
eq(bul("color colour colouur"), ["color", "colour"], "iki geçerli yazım")
```

```solution
colou?r
```

```hint
`?` önceki karakteri isteğe bağlı yapar.
```
:::

::: gorev Renk kodu
`#` ile başlayan **tam 6** onaltılık rakamlı renk kodlarını bul. 3 haneli kısa biçim ya da geçersiz karakter içerenler eşleşmemeli.

```starter
#[0-9a-fA-F]+
```

```test
eq(bul("#ff00aa #FFF #12345g #A1B2C3"), ["#ff00aa", "#A1B2C3"], "sadece 6 haneli geçerli kodlar")
```

```solution
#[0-9a-fA-F]{6}
```

```hint
Tam sayıda tekrar: `{6}`.
```
:::

::: gorev Boşlukları sadeleştir
Bu görevde desenin bir **değiştirme** işleminde kullanılacak: testler `degistir(metin, " ")` çağırarak desenin eşleştiği her yeri tek bir boşlukla değiştirecek. Art arda gelen boşlukları teke indiren deseni yaz.

```starter
  
```

```test
eq(degistir("a   b  c", " "), "a b c", "art arda boşluklar teke iner")
eq(degistir("tek boşluk", " "), "tek boşluk", "tek boşluklar aynı kalır")
eq(degistir("çok     boşluk  var", " "), "çok boşluk var", "uzun boşluk dizileri")
```

```solution
 +
```

```hint
"Bir ya da daha fazla boşluk": boşluk karakteri ve ardından `+`.
```
:::
