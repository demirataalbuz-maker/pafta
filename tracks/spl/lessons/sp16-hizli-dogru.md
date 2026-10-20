---
id: sp16
title: Hızlı ve Doğru Arama
summary: Splunk'ın indeksi nasıl kullandığı; süzgeçleri ilk | işaretinden önce yazmak, where ile search farkı ve büyük-küçük harf, fields ile erken daraltmak, baştaki joker karakterin maliyeti, stats'ı transaction ve join'e tercih etmek ve olay sırasına güvenmemek.
---

::: anlat Splunk veriyi nasıl okur?
Splunk olayları zaman dilimlerine bölünmüş **bucket**'larda saklar ve her bucket için bir **terim dizini** (tsidx) tutar. Aramanın ilk kısmı, yani ilk `|` işaretinden önceki her şey, bu dizinle çalışır: Splunk yalnızca eşleşen olayları diskten okur. `|`'dan sonraki komutlar ise okunmuş olaylar üzerinde, bellekte çalışır.

| Kural | Neden |
|---|---|
| **zaman aralığını daralt** | okunmayan bucket hiç açılmaz |
| **süzgeçleri ilk `\|`'dan önce yaz**: `sourcetype=istekler durum>=500 sunucu=web01` | dizin eşleşmeyen olayları baştan eler |
| `\| where` ve `\| search` ile süzmeyi sona bırakma | önce bütün olaylar okunur, sonra atılır |
| `\| fields` ile gereksiz alanları erken bırak | sonraki komutlara daha az veri akar |
| baştaki joker karakterden kaçın: `yol=*rapor` | dizin önekle çalışır; baştaki `*` her terime bakmayı gerektirir |
| `stats`'ı `transaction` ve `join`'e tercih et | biri akışta toplar, ötekiler bütün olayları belleğe alır |

```spl
sourcetype=istekler durum>=500 sunucu=web01
| fields yol durum
| stats count by yol
```

Aynı sonucu veren `sourcetype=istekler | where durum>=500 AND sunucu="web01" | stats count by yol` araması 26 değil milyonlarca olaylık bir indekste bütün olayları okur.
:::

::: anlat Doğruluk tuzakları
| Tuzak | Ne olur | Doğrusu |
|---|---|---|
| `where` büyük-küçük harfe **duyarlıdır** | `where seviye="error"` hiçbir şey bulmaz | `search seviye=error` ya da `where lower(seviye)="error"` |
| `search` duyarsızdır | `seviye=error`, `ERROR`'u bulur | çoğu zaman istenen budur |
| `!=` alanı olmayanları almaz | eksik veri sessizce düşer | `NOT alan=değer` (SP01) |
| `OR`, `AND`'den önce bağlanır | beklenmedik sonuç | parantez kullan (SP01) |
| `head`, `dedup`, `first` **sıraya** bağlıdır | yanlış olay seçilir | sırayı `sort` ile açıkça kur |

Sonuncusu özellikle sinsidir. Gerçek Splunk olayları **en yeniden eskiye** getirir; bu yüzden `dedup sunucu` her sunucunun en yeni olayını tutar. Pafta tezgahında tablolar eskiden yeniye okunur ve aynı arama en eski olayı tutar. Doğru sonucun bir varsayılan sıraya bağlı olduğu her aramada sırayı **açıkça** yaz:

```spl
sourcetype=istekler
| sort -_time
| dedup sunucu
| table sunucu zaman durum
```

> [!İPUCU]
> Gerçek bir Splunk'ta aramanın neye ne kadar zaman harcadığını **Job Inspector** gösterir (arama sonucunun üstündeki "Job → Inspect Job"). Yavaş bir aramada önce oraya bak: süre çoğu zaman tek bir komutta, genellikle `join`, `transaction` ya da baştaki bir joker karakterde toplanır.
:::

::: tahmin
Kaç satır yazar?

```spl
sourcetype=gunluk
| where seviye="error"
| stats count by sunucu
```

???

Hiç satır yazmaz. `where` büyük-küçük harfe duyarlıdır ve `gunluk`'teki seviyeler `ERROR` diye büyük harfle yazılmış; `"error"` hiçbir olayla eşleşmez. `search seviye=error` ise duyarsız olduğu için web01'den 3, web02'den 2 kayıt bulurdu.
:::

::: gorev Süzgeci başa al
Aşağıdaki arama doğru sonucu veriyor ama bütün olayları okuyup sonra süzüyor. Aynı sonucu verecek şekilde yeniden yaz: süzgeçler ilk `|` işaretinden **önce** dursun ve `where` kullanma.

```starter
sourcetype=istekler
| where durum>=500 AND sunucu="web01"
| stats count by yol
```

```test
eq(sutunlar, ["yol", "count"], "sütunlar")
eq(sonuc, [("/api/rapor", 3)], "aynı sonuç")
ilk = src.split("|", 1)[0]
ok("durum" in ilk and "web01" in ilk, "durum ve sunucu süzgeçleri ilk | işaretinden önce olmalı")
ok(not kullanir("where"), "where kullanma")
```

```solution
sourcetype=istekler durum>=500 sunucu=web01
| stats count by yol
```

```hint
Arama çubuğunda alan karşılaştırmaları doğrudan yazılır: `sourcetype=istekler durum>=500 sunucu=web01`.
```
:::

::: gorev Büyük-küçük harf
`gunluk` kaynağında seviyesi `error` olan kayıtları sunucuya göre say. Başlangıç kodu hiçbir sonuç döndürmüyor; düzelt.

```starter
sourcetype=gunluk
| where seviye="error"
| stats count by sunucu
```

```test
eq(sutunlar, ["sunucu", "count"], "sütunlar")
eq(sonuc, [("web01", 3), ("web02", 2)], "iki sunucu")
```

```solution
sourcetype=gunluk seviye=error
| stats count by sunucu
```

```hint
`where` duyarlıdır, `search` değildir. Süzgeci arama çubuğuna taşı: `sourcetype=gunluk seviye=error`. (Ya da `where lower(seviye)="error"`; ama ilki hem doğru hem hızlı.)
```
:::

::: gorev Sıraya güvenme
Her sunucunun **en son** isteğinin `zaman` ve `durum` alanlarını `dedup` ile getir: `sunucu`, `zaman`, `durum`; en son isteği en yeni olan sunucu en üstte.

```starter
sourcetype=istekler
| dedup sunucu
| table sunucu zaman durum
```

```test
eq(sutunlar, ["sunucu", "zaman", "durum"], "sütunlar")
eq(sonuc, [("web01", "2026-10-19 11:47", 200), ("web03", "2026-10-19 11:31", 200), ("web02", "2026-10-19 11:20", 201)],
   "her sunucunun en yeni isteği")
ok(kullanir("dedup"), "dedup kullan")
```

```solution
sourcetype=istekler
| sort -_time
| dedup sunucu
| table sunucu zaman durum
```

```hint
`dedup` her değerin **ilk gördüğü** olayı tutar. Başlangıç kodu bu tezgahta en eski isteği buluyor; önce en yeniden eskiye sırala: `sort -_time`.
```
:::
