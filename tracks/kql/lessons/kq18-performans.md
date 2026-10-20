---
id: kq18
title: Hızlı ve Doğru Sorgu
summary: Kusto'nun veriyi nasıl okuduğu; zaman süzgecini başa koymak, has ile terim dizini, ayrıştırmadan önce süzmek, birleştirmeden önce özetlemek, sütunları erken bırakmak ve sık doğruluk tuzakları (has'ın terim mantığı, büyük-küçük harf, innerunique, take).
---

::: anlat Kusto veriyi nasıl okur?
Sentinel ya da Data Explorer'da bir tablo milyarlarca satır olabilir. Kusto bu veriyi **zamana göre parçalara** (extent) bölünmüş, sütun sütun sıkıştırılmış ve **terimleri dizinlenmiş** halde saklar. Hızlı sorgunun sırrı, motorun okumak zorunda olduğu veriyi en baştan azaltmaktır:

| Sıra | Kural | Neden |
|---|---|---|
| 1 | **zaman süzgeci ilk aşama**: `where zaman > ago(1d)` | ilgisiz zaman parçaları hiç açılmaz |
| 2 | **dizinli süzgeçler**: `has`, `==`, `in` | terim dizini doğrudan eşleşen satırlara gider |
| 3 | **pahalı işler sonra**: `parse`, `extract`, `contains`, `matches regex` | yalnızca kalan satırlarda çalışır |
| 4 | **sütunları erken bırak**: `project` | sütun deposunda okunmayan sütun maliyet doğurmaz |
| 5 | **birleştirmeden önce özetle** | `join`'e milyon değil birkaç yüz satır girer |
| 6 | **küçük tablo solda**, boyut tablosu için `lookup` | birleştirme küçük tarafı belleğe alır |

Aynı sonucu veren iki sorgu arasında saniyelerle dakikalar kadar fark olabilir. Sentinel'de bu, sorgunun zaman aşımına uğraması ya da analitik kuralların gecikmesi demektir.

```kql
gunluk
| where zaman >= datetime(2026-10-19 09:00)              // 1: zaman
| where mesaj has "yavaş"                                 // 2: dizinli terim
| parse-where mesaj with "yavaş sorgu tablo=" tablo " sure=" sure:int "ms"   // 3: pahalı iş
| summarize toplam = sum(sure) by tablo
```

### has ile contains
`has` **bütün terimi** arar ve dizini kullanır; `contains` metnin her yerinde **alt dizgi** arar ve her satırı tarar. Terim, harf ve rakamlardan oluşan kesintisiz bir dizidir: `/api/raporlar` metninin terimleri `api` ve `raporlar`'dır.

```kql
datatable(m:string)["/api/rapor", "/api/raporlar", "rapor-v2"]
| extend a = m has "rapor", b = m contains "rapor", c = m has "rap"
```

Ön ek aramak için `hasprefix`, büyük-küçük harf duyarlı ve daha da hızlı arama için `has_cs` vardır.
:::

::: anlat Doğruluk tuzakları
Hızlı ama yanlış bir sorgu, yavaş bir sorgudan daha tehlikelidir. KQL'de en sık yapılan hatalar:

| Tuzak | Belirti | Doğrusu |
|---|---|---|
| `==` büyük-küçük harfe **duyarlıdır** | `seviye == "error"` hiçbir şey bulmaz | `=~`, `in~`, `has` (duyarsız) |
| `has` terim arar | `has "rap"`, `rapor`'u bulmaz | tam terim ya da `hasprefix` |
| `join` varsayılanı `innerunique` | sol tablodan satır kaybolur | `kind=inner` (KQ06, KQ11) |
| `take` rastgeledir | her çalıştırmada farklı satırlar | `top N by ...` ya da `sort` + `take` |
| dinamik değerle gruplamak | hata ya da beklenmedik gruplar | önce `tostring()` (KQ13) |
| boş değerli karşılaştırma | `x != "a"` boş `x`'i elemez ya da beklenmedik davranır | `isempty()` / `isnotempty()` ile açıkça ele al |

> [!İPUCU]
> Uzun bir sorguyu yazarken her aşamadan sonra `| take 10` ya da `| count` ekleyip ara sonuca bak. Hatanın hangi aşamada başladığını bulmanın en hızlı yolu budur. Bitmiş sorguyu da önce küçük bir zaman aralığında çalıştır, sonuç doğruysa aralığı genişlet.
:::

::: tahmin
Üç satır yazar:

```kql
datatable(m:string)["/api/rapor", "/api/raporlar", "rapor-v2"]
| extend a = m has "rapor", b = m contains "rapor", c = m has "rap"
```

???

`/api/rapor|true|true|false`, `/api/raporlar|false|true|false`, `rapor-v2|true|true|false`. `has "rapor"`, `raporlar` terimini bulmaz: terim `rapor` değil `raporlar`'dır. `rapor-v2`'de tire terimleri ayırdığı için `rapor` ayrı bir terimdir. `contains` alt dizgi aradığı için üçünde de doğrudur. `has "rap"` ise hiçbir terimle tam eşleşmez.
:::

::: gorev Sorguyu yeniden düzenle
Aşağıdaki başlangıç sorgusu doğru sonucu veriyor ama her satırı ayrıştırıp sonra süzüyor. Aynı sonucu verecek şekilde yeniden düzenle: **ilk aşama zaman süzgeci** olsun, `parse`'tan önce mesajı `has` ile süz, kalıba uymayan satırları `parse-where` ile ele.

```starter
gunluk
| parse mesaj with "yavaş sorgu tablo=" tablo " sure=" sure:int "ms"
| where zaman >= datetime(2026-10-19 09:00) and isnotempty(tablo)
| summarize toplam = sum(sure) by tablo
```

```test
eq(sutunlar, ["tablo", "toplam"], "sütunlar")
eq(sonuc, [("raporlar", 6800)], "aynı sonuç")
asamalar = [a.strip() for a in src.split("|")[1:]]
ok(bool(asamalar) and asamalar[0].startswith("where") and "zaman" in asamalar[0], "ilk aşama zaman süzgeci olmalı")
ok(" has " in src and src.find(" has ") < src.find("parse"), "parse'tan önce has ile süz")
ok(kullanir("parse-where"), "parse-where kullan")
```

```solution
gunluk
| where zaman >= datetime(2026-10-19 09:00)
| where mesaj has "yavaş"
| parse-where mesaj with "yavaş sorgu tablo=" tablo " sure=" sure:int "ms"
| summarize toplam = sum(sure) by tablo
```

```hint
Sıra: `where zaman >= ...`, sonra `where mesaj has "yavaş"`, sonra `parse-where`, en son `summarize`.
```
:::

::: gorev Önce özetle, sonra zenginleştir
Şehir başına istek sayısını hesaplayan başlangıç sorgusu, **her isteği** sunucular tablosuyla birleştiriyor. Önce istekleri sunucu başına özetle, sonra küçük sonucu şehir bilgisiyle zenginleştir ve şehre göre topla: `sehir`, `istek`; çoktan aza.

```starter
istekler
| join kind=inner (sunucular | project sunucu = ad, sehir) on sunucu
| summarize istek = count() by sehir
| sort by istek desc
```

```test
eq(sutunlar, ["sehir", "istek"], "sütunlar")
eq(sonuc, [("İstanbul", 20), ("Ankara", 6)], "aynı sonuç")
s = src.find("summarize")
b = max(src.find("lookup"), src.find("join"))
ok(s != -1 and b != -1 and s < b, "birleştirmeden önce özetle")
```

```solution
istekler
| summarize istek = count() by sunucu
| lookup (sunucular | project sunucu = ad, sehir) on sunucu
| summarize istek = sum(istek) by sehir
| sort by istek desc
```

```hint
İlk aşama: `summarize istek = count() by sunucu`. 26 satır 3 satıra iner; birleştirme bu üç satırla yapılır.
```

```hint
Zenginleştirmeden sonra şehir başına yeniden topla: `summarize istek = sum(istek) by sehir`.
```
:::

::: gorev Büyük-küçük harf
`gunluk` tablosunda seviyesi `error` ya da `warn` olan kayıtları seviyeye göre say: `seviye`, `adet`; seviyeye göre artan. Seviyeler tabloda büyük harfle yazılı; listeyi küçük harfle bırak ve karşılaştırmayı büyük-küçük harfe **duyarsız** yap.

```starter
gunluk
| where seviye in ("error", "warn")
| summarize adet = count() by seviye
| sort by seviye asc
```

```test
eq(sutunlar, ["seviye", "adet"], "sütunlar")
eq(sonuc, [("ERROR", 5), ("WARN", 6)], "iki seviye")
ok('"error"' in src, "listeyi küçük harfle bırak")
```

```solution
gunluk
| where seviye in~ ("error", "warn")
| summarize adet = count() by seviye
| sort by seviye asc
```

```hint
`in` büyük-küçük harfe duyarlıdır. Duyarsız sürümü: `in~`.
```
:::
