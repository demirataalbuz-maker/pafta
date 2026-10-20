---
id: kq08
title: let, datatable ve toscalar
summary: Değerleri ve ara sonuçları let ile adlandırmak, sorguyu ; ile bağlamak, toscalar ile tek bir sayıyı sorguda kullanmak ve datatable ile sorgunun içinde küçük tablolar kurmak.
---

::: anlat let: adlandır, tekrar kullan
Gerçek sorgular büyüdükçe aynı eşik, aynı zaman aralığı ve aynı ara sonuç birkaç yerde geçer. `let` bunlara bir ad verir:

```kql
let esik = 1000;                                    // skaler: bir sayı
let yavas = istekler | where sure_ms > esik;        // tablo: bir sorgunun sonucu
yavas
| summarize adet = count() by yol
```

Kurallar:

- Her `let` ifadesi **noktalı virgülle** biter; son ifade (noktalı virgülsüz) asıl sorgudur.
- `let` ifadeleri ile sorgu **aynı blokta** durur. Pafta'da boş satır yeni bir sorgu başlattığı için aralarına boş satır koyma.
- Skaler bir `let` sayı, metin, tarih ya da süre olabilir: `let pencere = 1h;`, `let bas = datetime(2026-10-19 09:00);`.
- Tablo `let`'i bir sorgunun **tarifidir**; her kullanıldığı yerde yeniden çalışır.

Bu yolda iki yeni tablo var: `istekler` (bir iç uygulamanın web istek günlüğü: `zaman`, `istemci`, `yontem`, `yol`, `durum`, `sure_ms`, `sunucu`, `kullanici`, `ayrinti`) ve `dagitimlar` (sunuculara yapılan sürüm dağıtımları).

```kql
let pencere_bas = datetime(2026-10-19 09:00);
let pencere = 1h;
istekler
| where zaman >= pencere_bas and zaman < pencere_bas + pencere
| summarize adet = count() by sunucu
| sort by sunucu asc
```

### toscalar: sorgudan tek bir değer
Bir sorgunun sonucunu (tek satır, tek sütun) başka bir sorguda **sayı gibi** kullanmak için `toscalar()`:

```kql
let ort = toscalar(istekler | summarize avg(sure_ms));
istekler
| where sure_ms > 2 * ort
| project zaman, yol, sure_ms
| sort by sure_ms desc
```

> [!İPUCU]
> Bir tablo `let`'i birden çok yerde kullanılıyorsa ve hesaplaması pahalıysa `let x = materialize(sorgu);` yaz: sonuç bir kez hesaplanıp önbelleğe alınır. Sentinel'deki uzun tespit ve rapor sorgularında sık görürsün.
:::

::: anlat datatable: sorgunun içinde tablo
`datatable` sütunları ve türleriyle küçük bir tabloyu doğrudan sorguda kurar. Değerler satır satır, virgülle ayrılarak yazılır:

```kql
datatable(sunucu:string, ekip:string)[
    "web01", "Uygulama",
    "web02", "Uygulama",
    "web03", "Ağ"
]
| join kind=inner (istekler | summarize istek = count() by sunucu) on sunucu
| project sunucu, ekip, istek
```

İki büyük kullanımı vardır:

1. **Küçük bir başvuru tablosu**: eşikler, hedefler, sahiplik bilgisi. Veritabanında olmayan bir eşlemeyi sorguya katmanın en hızlı yolu.
2. **Sorguyu bilinen veride sınamak**: yazdığın bir sorguyu gerçek veride çalıştırmadan önce, sonucunu önceden bildiğin birkaç satırlık bir `datatable` üzerinde dene. Kenar durumlarını (boş değer, eşik sınırı, aynı zaman damgası) böyle yakalarsın.

| Tür | Örnek değer |
|---|---|
| `string` | `"web01"` |
| `int`, `long`, `real` | `42`, `3.5` |
| `bool` | `true` |
| `datetime` | `datetime(2026-10-19 08:00)` |
| `timespan` | `30m`, `2h` |
| `dynamic` | `dynamic(["a", "b"])` |
:::

::: tahmin
Tek satır yazar:

```kql
let esik = 1000;
let yavas = istekler | where sure_ms > esik;
yavas | summarize n = count(), en = max(sure_ms)
```

???

`5|2600`. Süresi 1000 milisaniyeyi aşan beş istek var (2300, 2410, 1900, 2600, 1200); en yavaşı 2600 ms. `yavas` bir tablo `let`'idir: `istekler | where sure_ms > 1000` sorgusunun adı.
:::

::: gorev Eşikleri let ile tanımla
`let` ile iki değer tanımla: `yol_adi = "/api/rapor"` ve `esik = 1000`. Bu yola gelen ve süresi eşiği aşan isteklerin `zaman`, `kullanici`, `sure_ms` değerlerini zamana göre artan sırayla getir.

```starter
istekler
| where yol == "/api/rapor" and sure_ms > 1000
| project zaman, kullanici, sure_ms
```

```test
eq(sutunlar, ["zaman", "kullanici", "sure_ms"], "sütunlar")
eq(sonuc, [("2026-10-19 09:01", "zeynep", 2300), ("2026-10-19 09:02", "zeynep", 2410), ("2026-10-19 09:20", "zeynep", 1900),
           ("2026-10-19 10:42", "can", 2600), ("2026-10-19 10:44", "can", 1200)], "beş yavaş rapor isteği")
ok(kullanir("let yol_adi") and kullanir("let esik"), "iki let ifadesi")
```

```solution
let yol_adi = "/api/rapor";
let esik = 1000;
istekler
| where yol == yol_adi and sure_ms > esik
| project zaman, kullanici, sure_ms
| sort by zaman asc
```

```hint
`let yol_adi = "/api/rapor";` ve `let esik = 1000;` satırlarını sorgunun üstüne yaz, aralarına boş satır koyma. Sıralamayı da unutma: `sort by zaman asc`.
```
:::

::: gorev Genel ortalamanın üstündeki sunucular
Bütün isteklerin ortalama süresini `toscalar` ile hesapla. Ortalama süresi bu genel ortalamanın **üstünde** olan sunucuları `sunucu`, `ort` (bir ondalığa yuvarlanmış) sütunlarıyla, ortalamaya göre azalan sırayla getir.

```starter
istekler
| summarize ort = round(avg(sure_ms), 1) by sunucu
```

```test
eq(sutunlar, ["sunucu", "ort"], "sütunlar")
eq(sonuc, [("web01", 788.2), ("web02", 548.9)], "genel ortalama (529.4 ms) üstündeki iki sunucu")
ok(kullanir("toscalar"), "genel ortalamayı toscalar ile hesapla")
```

```solution
let genel = toscalar(istekler | summarize avg(sure_ms));
istekler
| summarize ort = round(avg(sure_ms), 1) by sunucu
| where ort > genel
| sort by ort desc
```

```hint
`let genel = toscalar(istekler | summarize avg(sure_ms));` ile genel ortalamayı bir sayıya çevir.
```

```hint
Sunucu başına ortalamayı hesapladıktan sonra `where ort > genel` ile süz, `sort by ort desc` ile sırala.
```
:::

::: gorev Hedef tablosu
Her yol için bir gecikme hedefi var: `/api/bilet` 200 ms, `/api/rapor` 1500 ms, `/api/durum` 50 ms, `/` 100 ms. Bu hedefleri bir `datatable` ile tanımla (`yol:string`, `hedef_ms:int`), isteklerle birleştir ve hedefini aşan istekleri yol başına say: `yol`, `asim`; çoktan aza, eşitlikte yola göre. Hedefi tanımlı olmayan yollar sonuçta olmasın.

```starter
istekler
| summarize asim = count() by yol
```

```test
eq(sutunlar, ["yol", "asim"], "sütunlar")
eq(sonuc, [("/api/rapor", 4), ("/api/bilet", 2)], "iki yolda hedef aşımı")
ok(kullanir("datatable"), "hedefleri datatable ile tanımla")
```

```solution
let hedefler = datatable(yol:string, hedef_ms:int)[
    "/api/bilet", 200,
    "/api/rapor", 1500,
    "/api/durum", 50,
    "/", 100
];
istekler
| join kind=inner hedefler on yol
| where sure_ms > hedef_ms
| summarize asim = count() by yol
| sort by asim desc, yol asc
```

```hint
`let hedefler = datatable(yol:string, hedef_ms:int)[ "/api/bilet", 200, ... ];` Sonra `istekler | join kind=inner hedefler on yol`.
```

```hint
Birleştirmeden sonra her satırda hem `sure_ms` hem `hedef_ms` var: `where sure_ms > hedef_ms`, ardından `summarize asim = count() by yol`.
```
:::
