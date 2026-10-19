---
id: rx04
title: Çapalar ve Sınırlar
summary: ^ ve $ ile satır başı/sonu, \b ile kelime sınırı, \A ve \Z ile metnin kesin başı ve sonu.
---

::: anlat Karakter değil, konum eşleyen öğeler
Şimdiye kadarki her öğe bir **karakter** tüketti. **Çapalar** ise karakter tüketmez, bir **konumu** eşler:

| Çapa | Konum |
|---|---|
| `^` | metnin başı (çok satırlı kipte: her satırın başı) |
| `$` | metnin sonu (çok satırlı kipte: her satırın sonu) |
| `\b` | kelime sınırı: bir kelime karakteri ile kelime olmayan karakter arası |
| `\B` | kelime sınırı **olmayan** konum |
| `\A` / `\Z` | metnin kesin başı / kesin sonu (kipten bağımsız) |

```regex
\bkat\b
---
kat katman merdiven kat. ikikat
```

`\b` sayesinde `katman` ve `ikikat` içindeki `kat` dışarıda kaldı. `kat.`'taki nokta kelime karakteri olmadığı için orada bir sınır var ve eşleşme oluyor.

### Doğrulama: baştan sona
Bir alanın **tamamen** bir desene uyup uymadığını sınamak için deseni iki uçtan çapala:

```regex
^\d{4}$
---
1234
```

Çapasız `\d{4}`, `ab12345cd` içinde de bir eşleşme bulurdu. Girdi doğrulamada çapasız desen, izin listesini delik deşik eder.

### Çok satırlı kip
Varsayılan olarak `^` ve `$` sadece **bütün metnin** başı ve sonudur. Desenin başına `(?m)` yazarsan her satıra uygulanırlar:

```regex
(?m)^#.*
---
# yorum
port=22
#son
```

> [!TUZAK]
> Python'da (ve birçok motorda) `$` metnin sonundaki **tek bir satır sonundan önce** de eşleşir: `^\d{4}$` deseni `"1234\n"` metnini de kabul eder. Satır sonu bile istemiyorsan `\Z` kullan: `^\d{4}\Z`. Kullanıcı girdisini doğrularken bu fark, beklenmedik karakterlerin kontrolden geçmesine yol açabilir.
:::

::: tahmin
Eşleşmeleri ayrı satırlara yaz:

```regex
\bkat\b
```

```stdin
kat katman merdiven kat.
```

???

`kat`, `kat`. İlki metnin başındaki kelime, ikincisi sondaki `kat.` içindeki. `katman`'da `kat`'tan sonra `m` geldiği için sınır yok.
:::

::: gorev Bütün kelime
Sadece **kelime olarak** geçen `log`'u bul. `login`, `catalog` ve `blog` içindeki `log` eşleşmemeli.

```starter
log
```

```test
eq(bul("log login catalog log.txt blog"), ["log", "log"], "sadece bağımsız log kelimeleri")
```

```solution
\blog\b
```

```hint
Kelime sınırı: `\b` deseninin iki ucuna.
```
:::

::: gorev Dört haneli PIN
Bir PIN alanını doğrulayan desen yaz: metnin **tamamı** tam 4 rakam olmalı. Sonunda satır sonu karakteri bile olmamalı.

```starter
^\d{4}$
```

```test
ok(eslesir("1234"), "'1234' geçerli")
ok(not eslesir("12345"), "5 hane geçersiz")
ok(not eslesir("a1234"), "baştaki harf geçersiz")
ok(not eslesir("123"), "3 hane geçersiz")
ok(not eslesir("1234\n"), "sondaki satır sonu da geçersiz ($ değil \\Z kullan)")
```

```solution
^\d{4}\Z
```

```hint
`$` sondaki tek bir `\n`'den önce de eşleşir. Metnin kesin sonu `\Z`'dir.
```
:::

::: gorev Yorum satırları
Bir yapılandırma dosyasında `#` ile başlayan yorum satırlarını bul; satır başındaki girintiyi de içersin. Satırın ortasındaki `#` yorum sayılmaz.

```starter
#.*
```

```test
metin = "# baslik\nport=22 # bu yorum degil\n  # girintili yorum\nhost=web01"
eq(bul(metin), ["# baslik", "  # girintili yorum"], "satır başındaki (girintili) yorumlar")
```

```solution
(?m)^[ \t]*#.*
```

```hint
Her satırın başı için `(?m)^`. Girinti: boşluk ya da sekme, sıfır ya da daha fazla.
```

```hint
Girintiyi `\s*` ile yazarsan satır sonlarını da aşabilir; `[ \t]*` daha kesindir.
```
:::
