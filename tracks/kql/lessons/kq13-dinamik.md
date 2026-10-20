---
id: kq13
title: Dinamik Veri ve mv-expand
summary: JSON taşıyan dynamic sütunlar; parse_json, .alan ve ["alan"] erişimi, dizi indeksi, tostring ile gruplamaya hazırlamak, array_length, set_has_element, bag_keys, mv-expand ile diziyi satırlara açmak ve make_set ile geri toplamak.
---

::: anlat JSON taşıyan sütunlar
Modern günlüklerde her şey düz sütunlara sığmaz: bir isteğin istemci bilgisi, bir olayın ek alanları, bir cihazın etiketleri iç içe bir **JSON** olarak gelir. KQL'de bunun türü `dynamic`'tir. Sentinel tablolarında (`AdditionalFields`, `DeviceDetail`, `Properties` gibi) her gün karşına çıkar.

`istekler` tablosunun `ayrinti` sütunu böyle bir JSON taşıyor. `parse_json` onu dinamik değere çevirir; içindeki alanlara noktayla ya da köşeli parantezle erişirsin:

```kql
istekler
| extend a = parse_json(ayrinti)
| project zaman, bolge = tostring(a.bolge), istemci_turu = tostring(a["istemci"]), etiketler = a.etiketler
| take 4
```

| Yazım | Anlamı |
|---|---|
| `d.alan` | nesnenin alanı |
| `d["alan adı"]` | aynısı; boşluk ya da özel karakter içeren adlar için |
| `d.dizi[0]`, `d.dizi[-1]` | dizinin ilk ve son elemanı |
| `array_length(d.dizi)` | eleman sayısı |
| `set_has_element(d.dizi, "x")` | dizide `x` var mı |
| `bag_keys(d)` | nesnenin alan adları |

Olmayan bir alana erişmek hata vermez, **boş** değer döndürür.

> [!TUZAK]
> Dinamik bir değerle gruplayamaz ve onu metinle güvenle karşılaştıramazsın. Gerçek Kusto `summarize ... by a.bolge` sorgusunu reddeder. Önce türünü belirt: `tostring(a.bolge)`, `toint(a.sayi)`, `todatetime(a.zaman)`. Alışkanlık edin: dinamik alanı kullanmadan önce dönüştür.
:::

::: anlat mv-expand: diziyi satırlara aç
Bir istekte birden çok etiket olabilir: `["mobil","beta"]`. "Hangi etiket kaç kez geçiyor?" sorusu için diziyi açman gerekir: her eleman **ayrı bir satır** olur, satırın öteki sütunları kopyalanır:

```kql
istekler
| extend etiket = parse_json(ayrinti).etiketler
| mv-expand etiket to typeof(string)
| summarize adet = count() by etiket
| sort by adet desc
```

`to typeof(string)` açılan elemanların türünü belirtir; belirtmezsen elemanlar dinamik kalır. Boş dizili satırlar açıldığında **kaybolur**; boş dizileri de saymak istiyorsan bunu hesaba kat.

Ters yön `make_list` ve `make_set`'tir: satırları bir diziye toplar. `make_set` tekrarları atar; sonucun sırası belli olmadığı için karşılaştırma yapacaksan `array_sort_asc` ile sırala:

```kql
istekler
| where isnotempty(kullanici)
| summarize bolgeler = array_sort_asc(make_set(tostring(parse_json(ayrinti).bolge))) by kullanici
```
:::

::: tahmin
İki satır yazar:

```kql
datatable(d:dynamic)[dynamic({"ad":"web01","etiket":["prod","eu"]}), dynamic({"ad":"web02","etiket":[]})]
| extend ad = tostring(d.ad), n = array_length(d.etiket), ilk = tostring(d.etiket[0])
| project ad, n, ilk
```

???

`web01|2|prod` ve `web02|0|`. İlk nesnenin etiket dizisinde iki eleman var, ilki `prod`. İkincisinin dizisi boş: uzunluk 0, olmayan `[0]` elemanı hata değil boş değer verir.
:::

::: gorev Bölgeye göre istek
`ayrinti` sütunundaki `bolge` alanına göre istek sayısını getir: `bolge`, `istek`; çoktan aza, eşitlikte bölgeye göre.

```starter
istekler
| summarize istek = count() by ayrinti
```

```test
eq(sutunlar, ["bolge", "istek"], "sütunlar")
eq(sonuc, [("ist", 11), ("dis", 6), ("ank", 5), ("izm", 4)], "dört bölge")
ok(kullanir("tostring"), "dinamik alanı tostring ile dönüştür")
```

```solution
istekler
| extend bolge = tostring(parse_json(ayrinti).bolge)
| summarize istek = count() by bolge
| sort by istek desc, bolge asc
```

```hint
`parse_json(ayrinti).bolge` dinamik bir değerdir; gruplamadan önce `tostring()` ile metne çevir.
```
:::

::: gorev Uygulama sürümleri
`istemci` alanı `"uygulama"` olan istekleri `surum` alanına göre say: `surum`, `istek`; sürüme göre artan.

```starter
istekler
| extend a = parse_json(ayrinti)
| summarize istek = count() by istemci = tostring(a.istemci)
```

```test
eq(sutunlar, ["surum", "istek"], "sütunlar")
eq(sonuc, [("2.4.1", 2), ("2.5.0", 2)], "iki sürüm")
```

```solution
istekler
| extend a = parse_json(ayrinti)
| where tostring(a.istemci) == "uygulama"
| summarize istek = count() by surum = tostring(a.surum)
| sort by surum asc
```

```hint
Önce süz: `where tostring(a.istemci) == "uygulama"`. Sonra `summarize ... by surum = tostring(a.surum)`.
```
:::

::: gorev Etiket sıklığı
`ayrinti` içindeki `etiketler` dizisini açarak her etiketin kaç istekte geçtiğini getir: `etiket`, `adet`; çoktan aza, eşitlikte etikete göre.

```starter
istekler
| extend etiketler = parse_json(ayrinti).etiketler
| summarize adet = count() by tostring(etiketler)
```

```test
eq(sutunlar, ["etiket", "adet"], "sütunlar")
eq(sonuc, [("mobil", 7), ("otomatik", 4), ("yeniden-deneme", 3), ("ilk-ziyaret", 2), ("beta", 1)], "beş etiket")
ok(kullanir("mv-expand"), "diziyi mv-expand ile aç")
```

```solution
istekler
| extend etiket = parse_json(ayrinti).etiketler
| mv-expand etiket to typeof(string)
| summarize adet = count() by etiket
| sort by adet desc, etiket asc
```

```hint
Başlangıç kodu dizinin tamamını tek bir değer olarak sayıyor (`["mobil","beta"]` ayrı bir grup olur). Diziyi `mv-expand` ile satırlara aç.
```

```hint
`| mv-expand etiket to typeof(string)`, sonra `summarize adet = count() by etiket`.
```
:::
