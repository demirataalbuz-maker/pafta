---
id: rx09
title: Bakınma (Lookaround)
summary: Tüketmeden bakmak; (?=...) ileriye, (?!...) olumsuz ileriye, (?<=...) ve (?<!...) geriye bakınma.
---

::: anlat Bakar ama almaz
**Bakınma** (lookaround) grupları, çapalar gibi **konum** eşler: bir koşulun sağlanıp sağlanmadığına bakar ama karakterleri eşleşmeye **katmaz**.

| Sözdizimi | Ad | Anlamı |
|---|---|---|
| `X(?=Y)` | ileriye bakınma | X'ten sonra Y geliyorsa X |
| `X(?!Y)` | olumsuz ileriye bakınma | X'ten sonra Y gelmiyorsa X |
| `(?<=Y)X` | geriye bakınma | X'ten önce Y varsa X |
| `(?<!Y)X` | olumsuz geriye bakınma | X'ten önce Y yoksa X |

```regex
\d+(?= TL)
---
Fiyat 250 TL, kargo 30 TL, 5 adet
```

Sadece sayılar eşleşti; ` TL` kontrol edildi ama eşleşmeye girmedi.

```regex
(?<=\$)\d+
---
toplam $40, indirim 5, vergi $7
```

### Birden fazla koşul: ileriye bakınma zinciri
İleriye bakınmalar aynı konumda art arda yazılabilir. Her biri "metnin geri kalanında şu var mı?" diye bakar; hepsi geçerse desen ilerler. Parola politikası denetimi klasik örnektir:

```regex
^(?=.*\d)(?=.*[a-zçğıöşü])(?=.*[A-ZÇĞİÖŞÜ]).{12,}$
---
GüvenliParola2026
```

> [!NOT]
> Python'da geriye bakınma **sabit uzunlukta** olmalıdır: `(?<=\$)` olur, `(?<=\$+)` olmaz (`re.error`). .NET ve PowerShell değişken uzunluğa izin verir, JavaScript son sürümlerde izin verir, grep `-P` (PCRE) vermez. Taşınabilir bir desen istiyorsan geriye bakınmayı sabit uzunlukta tut.
:::

::: tahmin
Eşleşmeleri ayrı satırlara yaz:

```regex
\d+(?= TL)
```

```stdin
Fiyat 250 TL, kargo 30 TL, 5 adet
```

???

`250`, `30`. `5`'ten sonra ` TL` değil ` adet` geliyor; ileriye bakınma tutmaz. ` TL` ise eşleşmenin parçası değildir.
:::

::: gorev TL tutarları
Sonunda `TL` olan tutarları bul (araya bir boşluk girebilir de girmeyebilir de); eşleşmede **sadece sayı** olsun. Ondalık kısım virgülle ayrılabilir (`1,5`).

```starter
\d+ TL
```

```test
eq(bul("250 TL, 1,5TL, 30 $, 12 TLX"), ["250", "1,5", "12"], "TL'den önceki sayılar")
```

```solution
\d+(?:,\d+)?(?= ?TL)
```

```hint
Sayı: `\d+(?:,\d+)?`. Ardından ileriye bakınma: `(?= ?TL)`.
```
:::

::: gorev Çalıştırılabilir olmayan dosyalar
`ad.uzanti` biçimindeki dosya adlarından uzantısı **tam olarak** `exe` **olmayanları** bul. `d.exefile` gibi `exe` ile başlayan ama `exe` olmayan uzantılar dahil edilmeli.

```starter
\b\w+\.\w+
```

```test
eq(bul("a.txt b.exe c.pdf d.exefile"), ["a.txt", "c.pdf", "d.exefile"], "exe hariç")
eq(bul("kur.exe"), [], "sadece exe varsa boş")
```

```solution
\b\w+\.(?!exe\b)\w+
```

```hint
Noktadan sonra olumsuz ileriye bakınma: `(?!exe\b)`. `\b` sayesinde `exefile` elenmez.
```
:::

::: gorev Parola politikası
Bir parolanın **tamamının** şu kurallara uyup uymadığını denetleyen desen yaz: en az 12 karakter, en az bir rakam, en az bir küçük harf, en az bir büyük harf (Türkçe harfler dahil).

```starter
.{12,}
```

```test
ok(tam("GüvenliParola2026"), "geçerli parola")
ok(not tam("kisaA1"), "kısa")
ok(not tam("hepsikucukharf12"), "büyük harf yok")
ok(not tam("HEPSIBUYUK12345"), "küçük harf yok")
ok(not tam("UzunAmaRakamYokİşte"), "rakam yok")
ok(tam("ŞİFRELERuzun9x"), "Türkçe büyük harflerle de çalışmalı")
```

```solution
^(?=.*\d)(?=.*[a-zçğıöşü])(?=.*[A-ZÇĞİÖŞÜ]).{12,}$
```

```hint
Her koşul için başa bir ileriye bakınma: `(?=.*\d)`, `(?=.*[a-z...])`, `(?=.*[A-Z...])`. Sonra uzunluk: `.{12,}`.
```
:::
