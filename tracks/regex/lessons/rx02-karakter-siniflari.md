---
id: rx02
title: Karakter Sınıfları
summary: Köşeli parantez "bu karakterlerden biri" demektir; aralıklar, olumsuzlama ve \d \w \s kısayolları.
---

::: anlat Köşeli parantez: bu karakterlerden biri
`[...]` bir **karakter sınıfıdır**: içindeki karakterlerden **tam olarak biriyle** eşleşir.

```regex
gr[ae]y
---
gray grey groy GRAY
```

İçeride **aralık** yazabilirsin: `[0-9]`, `[a-z]`, `[A-F]`, birleşik olarak `[0-9a-fA-F]` (onaltılık rakam).

Köşeli parantezin hemen başına `^` koyarsan anlam tersine döner: "bu karakterler **dışında** herhangi biri".

```regex
[^aeıioöuü\s]
---
ağaç
```

Sınıfın içinde çoğu metakarakter sıradan karakterdir: `[.?*]` gerçek nokta, soru işareti ya da yıldız arar. İçeride özel kalanlar sadece `]`, `\`, baştaki `^` ve aradaki `-`'dir. Tireyi düz karakter olarak istiyorsan sona koy: `[a-z-]`.

### Kısayollar
| Kısayol | Anlamı | Tersi |
|---|---|---|
| `\d` | rakam | `\D` rakam olmayan |
| `\w` | harf, rakam, alt çizgi ("kelime karakteri") | `\W` |
| `\s` | boşluk karakteri (boşluk, sekme, satır sonu) | `\S` |

```regex
\d\d:\d\d
---
Toplantı 09:30, öğle 12:5, akşam 18:45
```

> [!DERİN]
> Python 3'te `\d` ve `\w` **Unicode**'dur: `\w` Türkçe harfleri (`ş`, `ğ`, `ı`) kapsar, `\d` Arapça-Hint rakamlarını bile eşler. grep, JavaScript ve birçok SIEM motorunda ise `\w` sadece ASCII'dir (`[A-Za-z0-9_]`). Aynı desen iki araçta farklı sonuç verebilir. Kesinlik istiyorsan sınıfı açık yaz: `[0-9]`, `[A-Za-zÇĞİÖŞÜçğıöşü]`.
:::

::: tahmin
Desen her eşleşmede **tek bir** karakter yakalar. Eşleşmeleri sırayla, her birini ayrı satıra yaz.

```regex
[aeıioöuü]
```

```stdin
merhaba dünya
```

???

`e`, `a`, `a`, `ü`, `a` (beş satır). Sınıf tek karakter eşler. Metindeki her sesli harf ayrı bir eşleşmedir.
:::

::: gorev Onaltılık rakam
Tek bir **onaltılık rakamı** (0–9, a–f, A–F) eşleyen bir desen yaz.

```starter
[0-9a-f]
```

```test
eq(bul("C0FFEE x9z"), ["C", "0", "F", "F", "E", "E", "9"], "büyük harfler de dahil")
ok(not eslesir("ghijk"), "g-k arası onaltılık değil")
```

```solution
[0-9a-fA-F]
```

```hint
Birden çok aralık aynı sınıfta yan yana yazılabilir: `[0-9a-fA-F]`.
```
:::

::: gorev Saat
`SS:DD` biçimindeki saatleri bul: iki rakam, iki nokta, iki rakam. `12:5` gibi eksik olanlar eşleşmemeli.

```starter
\d:\d
```

```test
eq(bul("Başla 09:30, ara 12:5, bitiş 18:45"), ["09:30", "18:45"], "sadece tam saatler")
```

```solution
\d\d:\d\d
```

```hint
Her `\d` tek bir rakamdır. İki rakam için iki kez yaz (RX03'te bunun kısa yolunu göreceksin).
```
:::

::: gorev Kelimeler
Boşluk olmayan karakterlerden oluşan **dizileri** (kelimeleri) bul. Sekmeler ve art arda boşluklar ayırıcıdır. Bir sonraki paftada göreceğin `+` niceleyicisine burada ihtiyacın var: `X+` "bir ya da daha fazla X" demektir.

```starter
\w
```

```test
eq(bul("  log  analiz\taracı v2.1 "), ["log", "analiz", "aracı", "v2.1"], "dört kelime")
```

```solution
\S+
```

```hint
"Boşluk olmayan" karakter `\S`'dir (büyük S). Bir ya da daha fazlası: `\S+`.
```
:::
