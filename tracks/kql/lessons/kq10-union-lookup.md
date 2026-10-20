---
id: kq10
title: union ve lookup
summary: Farklı tabloları alt alta birleştirip tek bir zaman çizelgesi kurmak (union, withsource), küçük bir başvuru tablosuyla satırları zenginleştirmek (lookup) ve lookup'ın join'den farkı.
---

::: anlat union: tabloları alt alta koymak
`join` tabloları **yan yana** birleştirir: her satır, öteki tablodaki eşiyle genişler. `union` ise **alt alta** koyar: satırlar çoğalır, sütunlar **adlarına göre** hizalanır. Bir tabloda olmayan sütun, o tablodan gelen satırlarda boş kalır.

```kql
union withsource=Kaynak istekler, dagitimlar
| where sunucu == "web01" and zaman between (datetime(2026-10-19 08:50) .. datetime(2026-10-19 09:10))
| project zaman, Kaynak, durum, surum
| sort by zaman asc
```

Bu sorgu, bir arızayı incelerken en çok ihtiyaç duyacağın şeyi verir: **tek bir zaman çizelgesi**. 08:55'te web01'e 2.5.0 sürümü dağıtılmış, altı dakika sonra 500 hataları başlamış. İki ayrı tabloya ayrı ayrı bakarken bu ilişki gözden kaçabilir.

| Biçim | Anlamı |
|---|---|
| `union A, B` | A ve B'nin satırları |
| `A \| union B` | borudaki sonuç ve B |
| `union withsource=Kaynak A, B` | satırın hangi tablodan geldiğini `Kaynak` sütununa yaz |
| `union A, (B \| where ...)` | parantez içinde süzülmüş bir sorgu da birleşebilir |

> [!NOT]
> `union` satırların sırasını korumaz. Zaman çizelgesi kuruyorsan sonunda mutlaka `sort by zaman` yaz. Sentinel'de aynı türden olayları farklı kaynaklardan toplamanın (ör. farklı ürünlerin oturum günlükleri) temel aracı `union`'dır; sütun adları farklıysa önce her parçayı `project` ile aynı adlara getirirsin.
:::

::: anlat lookup: zenginleştirmek
Bir günlük satırında çoğu zaman yalnızca bir kimlik vardır: sunucu adı, kullanıcı adı, IP. Rolü, şehri, sahibi ise başka bir tablodadır. Büyük bir olay tablosunu küçük bir **başvuru** (boyut) tablosuyla genişletmenin aracı `lookup`'tır:

```kql
istekler
| where durum >= 500
| lookup (sunucular | project sunucu = ad, rol, sehir) on sunucu
| project zaman, sunucu, rol, sehir, durum
| sort by zaman asc
```

| | `join` | `lookup` |
|---|---|---|
| varsayılan tür | `innerunique` | `leftouter`: eşi olmayan satır **düşmez** |
| anahtar sütun | iki kez gelir (`sunucu`, `sunucu1`) | bir kez gelir |
| amaç | iki olay kümesini ilişkilendirmek | olay satırlarına bilgi eklemek |
| sağ taraf | herhangi bir tablo | küçük olmalı (bellekte tutulur) |

`lookup`'ın varsayılanı `leftouter` olduğu için eşi bulunmayan satırlar sonuçta kalır ve eklenen sütunları boş olur. Böylece eksik başvuru bilgisi sessizce kaybolmaz, görünür kalır. Yalnızca eşi olanları istiyorsan `lookup kind=inner` yaz.
:::

::: tahmin
Tek satır yazar:

```kql
union istekler, dagitimlar
| summarize n = count(), sunucular = dcount(sunucu)
```

???

`29|3`. `istekler`'de 26, `dagitimlar`'da 3 satır var; `union` bunları alt alta koyar. `sunucu` sütunu iki tabloda da aynı adla bulunduğu için tek bir sütunda birleşir; farklı sunucu sayısı (web01, web02, web03) 3'tür.
:::

::: gorev Dağıtım ve hatalar tek çizelgede
`istekler` ve `dagitimlar` tablolarını, satırın kaynağını `Kaynak` sütununa yazarak birleştir. **web01** için `2026-10-19 08:50` ile `09:10` arasındaki (ikisi dahil) kayıtları `zaman`, `Kaynak`, `durum`, `surum` sütunlarıyla, zamana göre artan sırayla getir.

```starter
istekler
| where sunucu == "web01"
| project zaman, durum
```

```test
eq(sutunlar, ["zaman", "Kaynak", "durum", "surum"], "sütunlar")
eq(sonuc, [("2026-10-19 08:55", "dagitimlar", None, "2.5.0"),
           ("2026-10-19 09:01", "istekler", 500, None),
           ("2026-10-19 09:02", "istekler", 500, None)], "dağıtımdan hemen sonra iki hata")
ok(kullanir("withsource"), "kaynağı withsource ile yaz")
```

```solution
union withsource=Kaynak istekler, dagitimlar
| where sunucu == "web01" and zaman between (datetime(2026-10-19 08:50) .. datetime(2026-10-19 09:10))
| project zaman, Kaynak, durum, surum
| sort by zaman asc
```

```hint
`union withsource=Kaynak istekler, dagitimlar` ile başla; süzgeç birleşmeden **sonra** gelir, böylece iki tabloya birden uygulanır.
```

```hint
Zaman aralığı: `zaman between (datetime(2026-10-19 08:50) .. datetime(2026-10-19 09:10))`.
```
:::

::: gorev Hataları sunucu bilgisiyle zenginleştir
Durum kodu 500 ve üstü olan istekleri, `sunucular` tablosundan alınan `rol` ve `sehir` bilgisiyle zenginleştir: `zaman`, `sunucu`, `rol`, `sehir`, `durum`; zamana göre artan. Birleştirme için `lookup` kullan (`sunucular`'daki ad sütunu `ad`, istekteki `sunucu`).

```starter
istekler
| where durum >= 500
| project zaman, sunucu, durum
```

```test
eq(sutunlar, ["zaman", "sunucu", "rol", "sehir", "durum"], "sütunlar")
eq(sonuc, [("2026-10-19 09:01", "web01", "web", "İstanbul", 500), ("2026-10-19 09:02", "web01", "web", "İstanbul", 500),
           ("2026-10-19 09:12", "web01", "web", "İstanbul", 503), ("2026-10-19 10:42", "web02", "web", "İstanbul", 500)],
   "dört hata, sunucu bilgisiyle")
ok(kullanir("lookup"), "lookup kullan")
```

```solution
istekler
| where durum >= 500
| lookup (sunucular | project sunucu = ad, rol, sehir) on sunucu
| project zaman, sunucu, rol, sehir, durum
| sort by zaman asc
```

```hint
Başvuru tablosunun anahtarını istekteki adla aynı yap: `(sunucular | project sunucu = ad, rol, sehir)`.
```

```hint
`| lookup (...) on sunucu`, sonra `project` ve `sort by zaman asc`.
```
:::

::: gorev Sahibi olmayan sunucu
Sunucu sahiplerini bir `datatable` ile tanımla: `web01` ve `web02` → `"Uygulama"`. Sunucu başına istek sayısını hesapla, sahip bilgisini `lookup` ile ekle; sahibi tanımlı olmayan sunucunun ekibi `"atanmamış"` görünsün. Sütunlar: `sunucu`, `ekip`, `istek`; sunucuya göre artan.

```starter
istekler
| summarize istek = count() by sunucu
```

```test
eq(sutunlar, ["sunucu", "ekip", "istek"], "sütunlar")
eq(sonuc, [("web01", "Uygulama", 11), ("web02", "Uygulama", 9), ("web03", "atanmamış", 6)], "web03 de listede")
```

```solution
let sahipler = datatable(sunucu:string, ekip:string)["web01", "Uygulama", "web02", "Uygulama"];
istekler
| summarize istek = count() by sunucu
| lookup sahipler on sunucu
| extend ekip = iff(isempty(ekip), "atanmamış", ekip)
| project sunucu, ekip, istek
| sort by sunucu asc
```

```hint
`lookup`'ın varsayılanı `leftouter`'dır: web03 sonuçta kalır ama `ekip` sütunu boş olur.
```

```hint
Boş ekibi doldur: `extend ekip = iff(isempty(ekip), "atanmamış", ekip)`.
```
:::
