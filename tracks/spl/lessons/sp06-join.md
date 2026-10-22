---
id: sp06
title: join ve Alt Arama
summary: Köşeli parantez içindeki alt arama, join ile iki kaynağı birleştirmek, type=left, max=1 davranışı ve aynı adlı alanların üzerine yazılması.
kazanim: APU 16.1, APU 16.2, APU 16.3, APU 16.4
---

::: anlat Alt arama ve join
Köşeli parantez içindeki arama, **alt aramadır**: önce o çalışır, sonucu dıştaki komuta verilir. `join` bu sonucu ortak bir alan üzerinden olaylara ekler:

```spl
sourcetype=biletler durum=açık
| join sunucu_id [search sourcetype=sunucular | rename id AS sunucu_id, ad AS sunucu | fields sunucu_id sunucu]
| table id baslik sunucu
```

Ortak alanın iki tarafta **aynı adı** taşıması gerekir; bu yüzden alt aramada `rename id AS sunucu_id` yapılır. Yalnızca gereken alanları `fields` ile seçmek iyi bir alışkanlıktır.

| Seçenek | Anlamı |
|---|---|
| `join alan [...]` | varsayılan `type=inner`: eşi olmayan olaylar düşer |
| `join type=left alan [...]` | eşi olmayan olaylar da kalır |

### Splunk join'inin iki huyu
1. **max=1**: Her olaya alt aramadan yalnızca **ilk** eşleşen satır eklenir; join olay sayısını hiçbir zaman artırmaz. KQL'in varsayılanı sol tarafı teke indirirdi, Splunk sağ tarafı indirir.
2. **Üzerine yazma**: Alt aramada dıştaki olayla **aynı adlı** bir alan varsa, olaydaki değer alt aramanınkiyle değiştirilir.

```spl
sourcetype=sunucular ad=db01
| join sorumlu_id [search sourcetype=personel | rename id AS sorumlu_id]
| table ad sorumlu_id unvan
```

> [!TUZAK]
> Yukarıdaki aramada `ad` alanı artık sunucunun adı değil, **sorumlu kişinin** adıdır: `personel` kaynağında da `ad` alanı vardı ve üzerine yazdı. Alt aramada alanları `rename` ile yeniden adlandırmak (`ad AS sorumlu`) bu sessiz hatayı önler.

> [!NOT]
> Splunk belgeleri büyük verilerde `join` yerine `stats` ile birleştirmeyi önerir: alt aramaların satır ve süre sınırları vardır. Öğrenmek ve küçük başvuru tabloları için `join` en okunur yoldur.
:::

::: tahmin
Tek bir değer:

```spl
sourcetype=sunucular ad=db01
| join sorumlu_id [search sourcetype=personel | rename id AS sorumlu_id]
| table ad
```

???

`Ayşe`. db01'in sorumlusu 3 numaralı çalışan Ayşe'dir. Alt aramadaki `personel` satırının `ad` alanı, sunucunun `ad` alanının üzerine yazar; sonuçta "db01" değil "Ayşe" görünür.
:::

::: gorev Açık biletlerin sunucusu
Açık biletlerin `id`'sini ve sunucusunun adını (`sunucu`) `id` sırasıyla getir.

```starter
sourcetype=biletler durum=açık
| join sunucu_id [search sourcetype=sunucular | fields id ad]
| sort id
| table id sunucu
```

```test
eq(sutunlar, ["id", "sunucu"], "alanlar: id, sunucu")
eq(sonuc, [(3, "db01"), (5, "dc01"), (9, "db02"), (10, "izleme01"), (12, "web03"), (15, "izleme01"), (17, "test01"), (20, "db01")], "sunucusu olan sekiz açık bilet")
```

```solution
sourcetype=biletler durum=açık
| join sunucu_id [search sourcetype=sunucular | rename id AS sunucu_id, ad AS sunucu | fields sunucu_id sunucu]
| sort id
| table id sunucu
```

```hint
Alt aramada ortak alan `sunucu_id` adını taşımalı: `rename id AS sunucu_id, ad AS sunucu`.
```
:::

::: gorev Sorumlusuz sunucu da listede
**Bütün** sunucuların adını (`ad`) ve sorumlusunun adını (`sorumlu`) ada göre sıralı getir; sorumlusu olmayan sunucu da kalsın.

```starter
sourcetype=sunucular
| join sorumlu_id [search sourcetype=personel | rename id AS sorumlu_id, ad AS sorumlu | fields sorumlu_id sorumlu]
| sort ad
| table ad sorumlu
```

```test
eq(sutunlar, ["ad", "sorumlu"], "alanlar: ad, sorumlu")
eq(len(sonuc), 12, "12 sunucunun hepsi")
ok(("test01", None) in sonuc, "test01 sorumlusuz olarak listede", got=sonuc[-3:])
```

```solution
sourcetype=sunucular
| join type=left sorumlu_id [search sourcetype=personel | rename id AS sorumlu_id, ad AS sorumlu | fields sorumlu_id sorumlu]
| sort ad
| table ad sorumlu
```

```hint
Eşi olmayanları tutmak için `join type=left`.
```
:::

::: gorev Ekiplere göre personel
Personeli ekip **adına** göre say: alanlar `ekip` ve `count`.

```cikti
Altyapı|3
Ağ|2
Uygulama|2
Veritabanı|2
```

```starter
sourcetype=personel
| stats count by ekip_id
```

```test
eq(sutunlar, ["ekip", "count"], "alanlar: ekip, count")
eq(sonuc, [("Altyapı", 3), ("Ağ", 2), ("Uygulama", 2), ("Veritabanı", 2)], "ekip başına personel")
```

```solution
sourcetype=personel
| join ekip_id [search sourcetype=ekipler | rename id AS ekip_id, ad AS ekip | fields ekip_id ekip]
| stats count by ekip
```

```hint
Önce `ekipler`'den ekip adını getir (`rename id AS ekip_id, ad AS ekip`), sonra `stats count by ekip`.
```
:::
