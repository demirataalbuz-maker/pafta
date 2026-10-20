---
id: sp14
title: append ve appendpipe
summary: Sonuçların altına başka bir aramanın sonuçlarını eklemek (append), mevcut sonuç üzerinde çalışan bir alt boru ile toplam ve ara toplam satırları (appendpipe), iki kaynağı append ve stats ile tek satırda birleştirmek ve fillnull.
---

::: anlat Sonuçların altına eklemek
`join` (SP06) iki aramayı **yan yana** birleştirir. `append` ise ikinci aramanın sonuçlarını birincinin **altına** koyar; KQL'deki `union`'a benzer:

```spl
sourcetype=istekler durum>=500
| stats count as istek_hatasi by sunucu
| append [search sourcetype=gunluk seviye=ERROR | stats count as gunluk_hatasi by sunucu]
```

Sonuçta aynı sunucu iki kez görünür: bir satırda istek hataları, ötekinde günlük hataları. Bunları tek satıra indirmenin Splunk kalıbı, ardından bir `stats` daha çalıştırmaktır:

```spl
sourcetype=istekler durum>=500
| stats count as istek_hatasi by sunucu
| append [search sourcetype=gunluk seviye=ERROR | stats count as gunluk_hatasi by sunucu]
| stats max(istek_hatasi) as istek_hatasi, max(gunluk_hatasi) as gunluk_hatasi by sunucu
| fillnull value=0
```

`append` + `stats` çoğu zaman `join`'den hem hızlı hem güvenlidir: `join`'in alt arama sınırları ve `max=1` davranışı (SP06) burada yoktur.

### fillnull
| Yazım | Anlamı |
|---|---|
| `fillnull` | bütün boş alanları 0 yap |
| `fillnull value=0 hata uyari` | yalnızca bu alanları |
| `fillnull value="yok" sahip` | metinle doldur |
:::

::: anlat appendpipe: toplam satırı
`appendpipe` köşeli parantez içindeki boruyu **mevcut sonuçların üzerinde** çalıştırır ve çıkanı sonuçların altına ekler. Raporların sonundaki "TOPLAM" satırı böyle eklenir:

```spl
sourcetype=istekler
| stats count by sunucu
| appendpipe [stats sum(count) as count | eval sunucu="TOPLAM"]
```

İç boruda `by` kullanırsan **ara toplamlar** elde edersin. Sonra sıralayarak her ara toplamı kendi grubunun altına yerleştir:

```spl
sourcetype=istekler
| stats count by sunucu yontem
| appendpipe [stats sum(count) as count by sunucu | eval yontem="TOPLAM"]
| sort sunucu yontem
```

| Komut | Alt arama neyi okur? |
|---|---|
| `append [search ...]` | yeni bir arama: başka bir kaynaktan |
| `appendpipe [...]` | şimdiye kadarki sonuçlar |
:::

::: tahmin
Dört satır yazar:

```spl
sourcetype=istekler
| stats count by sunucu
| appendpipe [stats sum(count) as count | eval sunucu="TOPLAM"]
```

???

`web01|11`, `web02|9`, `web03|6` ve en altta `TOPLAM|26`. `appendpipe` üç satırlık sonucu alır, toplar (11 + 9 + 6) ve tek bir satırı altına ekler.
:::

::: gorev Toplam satırlı hata raporu
Her sunucu için istek sayısını (`istek`) ve 500 ve üstü durum kodlu istek sayısını (`hata`) getir; en alta `sunucu` alanı `TOPLAM` olan bir toplam satırı ekle.

```starter
sourcetype=istekler
| stats count as istek, count(eval(durum>=500)) as hata by sunucu
```

```test
eq(sutunlar, ["sunucu", "istek", "hata"], "sütunlar")
eq(sonuc, [("web01", 11, 3), ("web02", 9, 1), ("web03", 6, 0), ("TOPLAM", 26, 4)], "üç sunucu ve toplam")
ok(kullanir("appendpipe"), "toplamı appendpipe ile ekle")
```

```solution
sourcetype=istekler
| stats count as istek, count(eval(durum>=500)) as hata by sunucu
| appendpipe [stats sum(istek) as istek, sum(hata) as hata | eval sunucu="TOPLAM"]
```

```hint
`appendpipe [stats sum(istek) as istek, sum(hata) as hata | eval sunucu="TOPLAM"]`.
```
:::

::: gorev İstek hataları ve günlük hataları
Her sunucu için 500 ve üstü durum kodlu istek sayısını (`istek_hatasi`) ve `gunluk` kaynağındaki `ERROR` seviyeli kayıt sayısını (`gunluk_hatasi`) **tek satırda** getir: `sunucu`, `istek_hatasi`, `gunluk_hatasi`; olmayan değer 0. `join` kullanma.

```starter
sourcetype=istekler durum>=500
| stats count as istek_hatasi by sunucu
| append [search sourcetype=gunluk seviye=ERROR | stats count as gunluk_hatasi by sunucu]
```

```test
eq(sutunlar, ["sunucu", "istek_hatasi", "gunluk_hatasi"], "sütunlar")
eq(sonuc, [("web01", 3, 3), ("web02", 1, 2)], "sunucu başına tek satır")
ok(not kullanir("join"), "join kullanma")
```

```solution
sourcetype=istekler durum>=500
| stats count as istek_hatasi by sunucu
| append [search sourcetype=gunluk seviye=ERROR | stats count as gunluk_hatasi by sunucu]
| stats max(istek_hatasi) as istek_hatasi, max(gunluk_hatasi) as gunluk_hatasi by sunucu
| fillnull value=0
```

```hint
Başlangıç kodu her sunucuyu iki ayrı satırda veriyor. Bir `stats ... by sunucu` daha ekleyerek satırları birleştir: her alanın tek dolu değerini `max()` ile al.
```
:::

::: gorev Ara toplamlar
Her sunucu ve yöntem için istek sayısını (`count`) getir; her sunucunun altına `yontem` alanı `TOPLAM` olan bir ara toplam satırı ekle. Sonuç sunucuya, sonra yönteme göre sıralı olsun.

```starter
sourcetype=istekler
| stats count by sunucu yontem
```

```test
eq(sutunlar, ["sunucu", "yontem", "count"], "sütunlar")
eq(sonuc, [("web01", "GET", 11), ("web01", "TOPLAM", 11), ("web02", "DELETE", 1), ("web02", "GET", 5),
           ("web02", "POST", 2), ("web02", "PUT", 1), ("web02", "TOPLAM", 9), ("web03", "GET", 6),
           ("web03", "TOPLAM", 6)], "her sunucunun altında ara toplam")
```

```solution
sourcetype=istekler
| stats count by sunucu yontem
| appendpipe [stats sum(count) as count by sunucu | eval yontem="TOPLAM"]
| sort sunucu yontem
```

```hint
İç boruda gruplama: `appendpipe [stats sum(count) as count by sunucu | eval yontem="TOPLAM"]`.
```

```hint
Ara toplamlar en altta toplanır; `sort sunucu yontem` her birini kendi sunucusunun altına taşır.
```
:::
