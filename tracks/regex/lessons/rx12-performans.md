---
id: rx12
title: Performans ve Tuzaklar
summary: Geri izlemenin bedeli, alternatif sırası, iç içe niceleyiciler, atomik grup ve iyelik niceleyicisi.
---

::: anlat Motor nasıl düşünür?
Python, PCRE, .NET ve JavaScript'in regex motorları **geri izlemeli** (backtracking) motorlardır: deseni soldan sağa dener, bir yerde tutmazsa en son seçim noktasına **geri döner** ve başka bir yol dener.

İlk sonuç: **alternatiflerde ilk tutan kazanır**, en uzunu değil.

```regex
kat|katman
---
katman
```

Motor `katman`'ın başında önce `kat`'ı dener, tutar ve eşleşmeyi orada bitirir. Uzun alternatifi öne al ya da sınırla zorla: `katman|kat` veya `\b(?:kat|katman)\b`.

### Felaket geri izleme
İç içe niceleyiciler (`(a+)+`, `(\w*)*`, `(a|a)*`) eşleşmeyen bir girdide **üstel** sayıda yol dener. `^(a+)+b$` deseni 30 `a` ve sonunda `c` olan bir metinde yüz milyonlarca deneme yapar; bu makinede ölçülen süre 20 saniyeyi aşıyor. Her ek karakter süreyi yaklaşık ikiye katlar: 26 karakterde 1,5 saniye, 30'da 23 saniye.

Bu bir performans hatası olmanın ötesinde bir **hizmet reddi** (ReDoS) açığıdır: kullanıcı girdisine uygulanan tek bir kötü desen, sunucuyu kilitleyebilir. Savunma:

1. İç içe niceleyicilerden kaçın: `(a+)+` aslında `a+` demektir
2. `.*` yerine **kesin sınıflar** kullan: `[^&]*`, `[^"]*`
3. Deseni **çapala** ve girdi uzunluğunu sınırla
4. Geri izlemeyi kesen yapıları kullan (aşağıda)
5. Kritik yerlerde doğrusal zamanlı motorlar tercih et (RE2; Go ve Rust'ın varsayılanı)

### Atomik grup ve iyelik niceleyicisi
Python 3.11 iki yeni yapı getirdi (PCRE ve Java'da çoktan vardı):

- **Atomik grup** `(?>...)`: grup bir kez eşleştikten sonra içine **geri dönülmez**
- **İyelik niceleyicisi** `*+`, `++`, `?+`: açgözlü gibi alır ama **hiç geri vermez**

```regex
\d++\b
---
port 8080 ve 443 sürüm 2a
```

`2a`'da `\d++` `2`'yi alır, sonra `\b` tutmaz ve iyelik niceleyicisi geri vermediği için o konum hızla elenir.

> [!DERİN]
> Geri izleme olmayan motorlar (RE2, Thompson NFA) her zaman doğrusal zamanda çalışır ama geri başvuru (`\1`) ve bakınma desteklemez. Google, kullanıcıların yazdığı desenleri çalıştırdığı her yerde (Code Search, BigQuery) bu yüzden RE2 kullanır. SIEM'lerin bir kısmı da kullanıcı sorgularındaki regex'leri benzer şekilde sınırlar.
:::

::: tahmin
Eşleşmeyi yaz:

```regex
kat|katman
```

```stdin
katman
```

???

`kat`. Motor alternatifleri soldan sağa dener ve ilk tutanda durur. `katman` daha uzun olduğu halde hiç denenmez, çünkü `kat` zaten tuttu.
:::

::: gorev Alternatif sırası
`kat` ve `katman` kelimelerini metinde **bütün olarak** bul.

```starter
kat|katman
```

```test
eq(bul("kat katman kat. katmanlar"), ["kat", "katman", "kat"], "iki kelime de tam eşleşmeli, katmanlar değil")
```

```solution
\b(?:katman|kat)\b
```

```hint
Uzun alternatifi öne al ve kelime sınırlarıyla çevrele.
```
:::

::: gorev Yavaş deseni düzelt
Bu desen "metin bir ya da daha fazla `a` ve ardından tek bir `b`'den oluşuyor mu?" diye soruyor ama iç içe niceleyicisi yüzünden eşleşmeyen uzun girdilerde takılıyor. Aynı soruyu **hızlı** cevaplayan bir desen yaz.

```starter
^(a+)+b$
```

```meta
timeout: 8
```

```test
ok(eslesir("aaab"), "aaab eşleşmeli")
ok(eslesir("ab"), "ab eşleşmeli")
ok(not eslesir("b"), "sadece b eşleşmemeli")
ok(not eslesir("a" * 30 + "c"), "uzun ve eşleşmeyen girdi hızla reddedilmeli")
```

```solution
^a+b$
```

```hint
`(a+)+` ile `a+` aynı metinleri eşler; fark sadece motorun deneyeceği yol sayısındadır.
```
:::

::: gorev Kesin sınıfla alan çıkar
Bir URL sorgu metninden `id` parametresinin değerini **1. grupta** yakala: değer `&`'ye, boşluğa ya da metnin sonuna kadar sürer.

```starter
id=(.*)
```

```test
eq(grup("/rapor?id=42&tur=pdf", 1), "42", "& öncesi")
eq(grup("id=abc def", 1), "abc", "boşluk öncesi")
eq(grup("x=1&id=7", 1), "7", "metnin sonu")
```

```solution
\bid=([^&\s]*)
```

```hint
`.*` her şeyi yutar. "Ne `&` ne boşluk" olan karakterler: `[^&\s]*`.
```
:::
