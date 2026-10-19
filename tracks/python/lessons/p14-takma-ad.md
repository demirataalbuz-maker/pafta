---
id: p14
title: Takma Ad ve Kopya
summary: İki isim aynı listeyi gösterebilir; sığ kopya, derin kopya ve [[0]*3]*3 tuzağı.
---

::: anlat İki isim, tek nesne
P02'de değişkenin bir **etiket** olduğunu söylemiştik. Değiştirilemez nesnelerde (sayı, metin) bu fark pek hissedilmez. Listelerde ise her şeyi belirler:

```python
a = [1, 2, 3]
b = a              #! kopya DEĞİL: b de aynı listeyi gösterir
b.append(4)
print(a)           #! [1, 2, 3, 4] — a da "değişti"!
print(a is b)      #! True: aynı nesne
```

`b = a` yeni bir liste oluşturmaz, aynı listeye ikinci bir etiket yapıştırır. Buna **takma ad** (aliasing) denir. Liste değiştirilebilir olduğu için bir isimden yapılan değişiklik diğerinden de görünür, çünkü ortada **tek** liste var.

Bu örneği tezgaha al ve **◎ Röntgen** çek: `a` ve `b` satırlarının yanındaki renkli kareler **aynı renktir**. Röntgen'de aynı renk aynı nesne demektir.

### Kopya almanın yolları
```python
a = [1, 2, 3]
k1 = a[:]          #! tam dilim yeni liste üretir
k2 = list(a)       #! list() de yeni liste
k3 = a.copy()      #! en okunaklısı
a.append(99)
print(a, k1, k2, k3)
print(a is k1)     #! False — farklı nesneler
```

> [!NOT]
> Bu davranış bir hata değil, tasarımdır. Büyük bir listeyi bir fonksiyona verirken kopyalanmaması **hız** ve **bellek** kazandırır. Bedeli şu: kimin neyi değiştirdiğini senin bilmen gerekir.
:::

::: tahmin
Ne yazdırır?

```python
a = [1, 2, 3]
b = a
c = a[:]
a.append(4)
print(b, c)
```

???

`[1, 2, 3, 4] [1, 2, 3]`. `b` takma addır ve değişikliği görür. `c` dilimle alınmış bağımsız bir kopyadır.
:::

::: anlat Sığ kopya ve derin kopya
`a.copy()` **sığ** (shallow) kopyadır: dıştaki liste yenidir ama **içindeki nesneler aynıdır**. İçeride başka listeler varsa onlar paylaşılır:

```python
politika = [["web", [80, 443]], ["db", [5432]]]
sig = politika.copy()
sig[0][1].append(8080)       #! iç liste ortak → politika da etkilenir!
print(politika[0])

import copy
politika = [["web", [80, 443]], ["db", [5432]]]
derin = copy.deepcopy(politika)   #! her katmanı özyinelemeli kopyalar
derin[0][1].append(8080)
print(politika[0], derin[0])
```

### Klasik tuzak: [[0] * 3] * 3
```python
yanlis = [[0] * 3] * 3       #! aynı iç listeye 3 referans!
yanlis[0][0] = 1
print(yanlis)                #! [[1, 0, 0], [1, 0, 0], [1, 0, 0]]
dogru = [[0] * 3 for _ in range(3)]   #! her satır için ayrı liste
dogru[0][0] = 1
print(dogru)
```

`* 3` listedeki **referansları** çoğaltır, nesneleri değil. Dış liste aynı iç listeyi üç kez gösterir. İkinci satırdaki yapı bir **liste üreteci** (comprehension); P18'de göreceğiz. Şimdilik "her turda yeni liste" kalıbı olarak ezberle.

> [!DERİN]
> `[0] * 3` neden sorun değil de `[[0]] * 3` sorun? Çünkü `0` değiştirilemez: `l[0] = 1` listedeki **referansı** başka bir nesneye çevirir, `0` nesnesini değiştirmez. İç liste ise yerinde değiştirilebilir. Kural şu: **değiştirilemez nesneleri paylaşmak güvenlidir, değiştirilebilirleri paylaşmak ise bilinçli bir karar olmalıdır.**

> [!TUZAK]
> Bir listeyi `for` ile dolaşırken **aynı listeden eleman silme**. Döngü indeksi kayar ve bazı elemanları atlarsın. Bunun yerine bir kopya üzerinde dolaş (`for x in liste[:]:`) ya da filtrelenmiş yeni bir liste üret.
:::

::: tahmin
Ne yazdırır?

```python
izgara = [[0] * 2] * 2
izgara[0][0] = 1
print(izgara)
```

???

`[[1, 0], [1, 0]]`. Dış liste aynı `[0, 0]` listesini iki kez gösterir. Birini değiştirmek "ikisini" birden değiştirir, çünkü aslında tek liste vardır.
:::

::: gorev Izgara hatasını düzelt
Aşağıdaki kod 3×3'lük bir ızgara kuruyor ama tek bir hücreyi değiştirince bütün sütun değişiyor. **Her satırı ayrı bir liste** olacak şekilde düzelt. Beklenen çıktı:

```cikti
[[0, 0, 0], [0, 5, 0], [0, 0, 0]]
```

```starter
izgara = [[0] * 3] * 3
izgara[1][1] = 5
print(izgara)
```

```test
eq(out.strip(), "[[0, 0, 0], [0, 5, 0], [0, 0, 0]]", "Sadece ortadaki hücre 5 olmalı")
ok(izgara[0] is not izgara[1] and izgara[1] is not izgara[2] and izgara[0] is not izgara[2], "Üç satır üç ayrı liste nesnesi olmalı")
```

```solution
izgara = [[0] * 3 for _ in range(3)]
izgara[1][1] = 5
print(izgara)
```

```hint
Her satır için yeni bir `[0, 0, 0]` üretmelisin: bir `for` döngüsüyle `append` edebilir ya da `[[0] * 3 for _ in range(3)]` yazabilirsin.
```
:::

::: gorev Kuralların yedeği
Güvenlik duvarı kurallarını değiştirmeden önce **bağımsız** bir yedek al: `yedek` adında bir kopya oluştur, **sonra** `kurallar`'a `"deny all"` ekle. Ardından iki listeyi ayrı satırlarda yazdır.

```cikti
['allow 22', 'allow 80', 'deny all']
['allow 22', 'allow 80']
```

```starter
kurallar = ["allow 22", "allow 80"]
yedek = kurallar
kurallar.append("deny all")
print(kurallar)
print(yedek)
```

```test
eq(kurallar, ["allow 22", "allow 80", "deny all"], "kurallar'da 3 kural olmalı")
eq(yedek, ["allow 22", "allow 80"], "yedek değişmeden kalmalı")
ok(yedek is not kurallar, "yedek ile kurallar farklı nesneler olmalı")
```

```solution
kurallar = ["allow 22", "allow 80"]
yedek = kurallar.copy()
kurallar.append("deny all")
print(kurallar)
print(yedek)
```

```hint
`yedek = kurallar` takma ad üretir. `.copy()`, `list(...)` ya da `[:]` kullan.
```
:::

::: gorev Derin kopya
`politika` iç içe bir yapı. Ondan `kopya` adında **tamamen bağımsız** bir kopya üret, sonra **kopyanın** web portlarına (`kopya[0][1]`) `8080` ekle. Orijinal `politika` hiç değişmemeli.

```starter
politika = [["web", [80, 443]], ["db", [5432]]]
kopya = politika.copy()
kopya[0][1].append(8080)
print(politika)
print(kopya)
```

```test
eq(politika, [["web", [80, 443]], ["db", [5432]]], "politika değişmemeli")
eq(kopya[0][1], [80, 443, 8080], "kopya'nın web portlarında 8080 olmalı")
ok(kopya[0] is not politika[0] and kopya[0][1] is not politika[0][1], "İç listeler de ayrı nesneler olmalı")
```

```solution
import copy
politika = [["web", [80, 443]], ["db", [5432]]]
kopya = copy.deepcopy(politika)
kopya[0][1].append(8080)
print(politika)
print(kopya)
```

```hint
Sığ kopya iç listeleri paylaşır. `import copy` ve `copy.deepcopy(...)`.
```
:::
