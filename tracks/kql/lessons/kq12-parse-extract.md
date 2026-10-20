---
id: kq12
title: Metinden Alan Çıkarmak
summary: parse ile sabit biçimli mesajları sütunlara bölmek, türlü sütunlar ve * joker, parse-where ile uymayanları elemek, kind=regex, extract ile tek alan, extract_all ve split ile diziler, replace_regex ile günlük kalıplarını bulmak.
---

::: anlat parse: mesajı sütunlara böl
Günlüklerin büyük kısmı serbest metindir. Bu yolun `gunluk` tablosundaki mesajlara bak:

```kql
gunluk
| project zaman, sunucu, seviye, mesaj
| take 5
```

Aynı türden mesajlar aynı **kalıbı** izler: `yavaş sorgu tablo=raporlar sure=2300ms`. `parse` bu kalıbı tarif etmeni ister: sabit metinler tırnak içinde, çıkarılacak alanlar ad olarak:

```kql
gunluk
| parse mesaj with "yavaş sorgu tablo=" tablo " sure=" sure:int "ms"
| project zaman, tablo, sure
| take 3
```

| Desen öğesi | Anlamı |
|---|---|
| `"metin"` | tam bu metin |
| `ad` | bir sonraki sabit metne kadar olan kısım, `ad` sütununa |
| `ad:int`, `ad:real`, `ad:timespan` | türüyle birlikte; sayı türleri yalnızca sayıyı kabul eder |
| `*` | atla: herhangi bir metin |

Desen metnin **başından** eşleşir. Baştaki kısmı atlamak için `*` ile başla: `parse mesaj with * "surum=" surum`. Kalıba uymayan satırlar **düşmez**: yeni sütunları boş kalır. Uymayanları elemek için `parse-where` kullan:

```kql
gunluk
| parse-where mesaj with * "surum=" surum
| project zaman, sunucu, surum
```

### kind=regex
Sabit metinlerin yerine regex parçaları yazmak gerekirse `parse kind=regex` kullan. Parçalar Regex yolundaki desenlerdir; `@"..."` ham metin yazımı ters eğik çizgileri korur:

```kql
gunluk
| where mesaj has "doluluk"
| parse kind=regex mesaj with ".*?bolum=" bolum @"\s+doluluk=" doluluk:int "%"
| summarize en_yuksek = max(doluluk), kayit = count() by bolum
```

> [!İPUCU]
> `parse`'tan önce `where mesaj has "..."` ile kalıbın geçtiği satırları süz. `has` terim dizinini kullanır ve milyarlarca satırlık tablolarda `contains`'ten kat kat hızlıdır (KQ03). Önce ucuz süzgeç, sonra pahalı ayrıştırma.
:::

::: anlat extract, extract_all, split, replace_regex
Kalıbın tamamını değil, mesajın herhangi bir yerindeki **tek bir alanı** istiyorsan `extract` daha kısadır. Regex'in yakalanan grubunu döndürür; eşleşme yoksa boş değer verir:

```kql
gunluk
| extend bekleyen = toint(extract(@"bekleyen=(\d+)", 1, mesaj))
| where isnotnull(bekleyen)
| project zaman, sunucu, bekleyen
```

| Fonksiyon | Döndürdüğü |
|---|---|
| `extract(regex, grup, metin)` | ilk eşleşmenin o grubu |
| `extract_all(regex, metin)` | bütün eşleşmeler, dinamik **dizi**: `["2","4","1"]` |
| `split(metin, ayırıcı)` | parçalar, dinamik dizi; `split(m, " ")[0]` ilk parça, `[-1]` son parça |
| `replace_regex(metin, regex, yeni)` | eşleşmeleri değiştirilmiş metin; `\1` grup başvurusu |

### Günlük kalıplarını bulmak
Binlerce satırlık bir günlükte "hangi tür mesajlar var?" sorusunun hızlı cevabı, değişen kısımları (sayılar, kimlikler) silip geriye kalan **kalıbı** saymaktır:

```kql
gunluk
| extend kalip = replace_regex(mesaj, @"\d+", "#")
| summarize adet = count() by kalip
| sort by adet desc
```

`hizmet başladı surum=2.5.0` ile `surum=2.4.1` aynı kalıba (`surum=#.#.#`) düşer. Yeni ya da nadir bir kalıp çoğu zaman yeni bir sorunun ilk izidir.
:::

::: tahmin
Üç satır yazar:

```kql
datatable(m:string)["disk bolum=/var doluluk=81%", "disk bolum=/data doluluk=93%", "hizmet başladı"]
| parse m with "disk bolum=" bolum " doluluk=" doluluk:int "%"
| project bolum, doluluk
```

???

`/var|81`, `/data|93` ve boş bir satır: `|`. İlk iki satır kalıba uyar. Üçüncüsü uymaz ama `parse` satırı düşürmez; `bolum` ve `doluluk` boş kalır. Uymayan satırları elemek için `parse-where` kullanılır.
:::

::: gorev Yavaş sorgular
`gunluk` tablosundaki `yavaş sorgu tablo=... sure=...ms` mesajlarını ayrıştır ve her tablo için yavaş sorgu sayısını ve en uzun süreyi (milisaniye, sayı) getir: `tablo`, `adet`, `en_uzun`; en uzun süreye göre azalan. Kalıba uymayan satırlar sonuca girmesin.

```starter
gunluk
| where mesaj contains "yavaş sorgu"
| summarize adet = count()
```

```test
eq(sutunlar, ["tablo", "adet", "en_uzun"], "sütunlar")
eq(sonuc, [("raporlar", 3, 2600), ("biletler", 1, 850)], "iki tablo")
ok(kullanir("parse") or kullanir("parse-where"), "parse ile ayrıştır")
```

```solution
gunluk
| parse-where mesaj with "yavaş sorgu tablo=" tablo " sure=" sure:int "ms"
| summarize adet = count(), en_uzun = max(sure) by tablo
| sort by en_uzun desc
```

```hint
Kalıp: `"yavaş sorgu tablo=" tablo " sure=" sure:int "ms"`. Sürenin sayı olarak karşılaştırılabilmesi için türünü yaz.
```

```hint
`parse-where` kalıba uymayan satırları eler; sonra `summarize adet = count(), en_uzun = max(sure) by tablo`.
```
:::

::: gorev Bağlantı havuzunda bekleyenler
Mesajında `bekleyen=` sayısı geçen kayıtları bul ve bu sayıyı **tam sayı** olarak `bekleyen` sütununa çıkar: `zaman`, `sunucu`, `bekleyen`; bekleyen sayısına göre azalan. `extract` kullan.

```starter
gunluk
| where mesaj contains "bekleyen"
| project zaman, sunucu, mesaj
```

```test
eq(sutunlar, ["zaman", "sunucu", "bekleyen"], "sütunlar")
eq(sonuc, [("2026-10-19 09:12", "web01", 31), ("2026-10-19 09:02", "web01", 12), ("2026-10-19 10:43", "web02", 5)], "üç kayıt")
ok(kullanir("extract"), "extract kullan")
```

```solution
gunluk
| extend bekleyen = toint(extract(@"bekleyen=(\d+)", 1, mesaj))
| where isnotnull(bekleyen)
| project zaman, sunucu, bekleyen
| sort by bekleyen desc
```

```hint
`extract(@"bekleyen=(\d+)", 1, mesaj)` sayıyı metin olarak verir; sıralamanın sayısal olması için `toint()` ile sar.
```
:::

::: gorev Günlük kalıpları
Mesajlardaki **her rakam dizisini** `#` ile değiştirerek kalıp çıkar ve en sık görülen üç kalıbı getir: `kalip`, `adet`; adede göre azalan, eşitlikte kalıba göre artan.

```starter
gunluk
| summarize adet = count() by mesaj
| sort by adet desc
| take 3
```

```test
eq(sutunlar, ["kalip", "adet"], "sütunlar")
eq(sonuc, [("hizmet başladı surum=#.#.#", 4), ("bağlantı havuzu dolu aktif=# bekleyen=#", 3),
           ("disk uyarısı bolum=/var doluluk=#%", 3)], "en sık üç kalıp")
ok(kullanir("replace_regex"), "replace_regex kullan")
```

```solution
gunluk
| extend kalip = replace_regex(mesaj, @"\d+", "#")
| summarize adet = count() by kalip
| sort by adet desc, kalip asc
| take 3
```

```hint
`replace_regex(mesaj, @"\d+", "#")`: her rakam dizisi tek bir `#` olur.
```

```hint
Eşit adetli kalıpların sırası için ikinci bir anahtar: `sort by adet desc, kalip asc`.
```
:::
