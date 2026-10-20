---
id: sp11
title: lookup, inputlookup ve makeresults
summary: Başvuru tablolarıyla olayları zenginleştirmek; inputlookup ile tabloyu görmek, lookup ... OUTPUT ve OUTPUTNEW, AS ile farklı alan adlarını eşlemek, eşleşmeyen olaylar ve makeresults ile bir ifadeyi veriden bağımsız sınamak.
---

::: anlat Başvuru tabloları
Olaylar çoğu zaman bir **kod** taşır: öncelik adı, sunucu adı, durum kodu. Kodun anlamı (hedef süre, sahip ekip, şehir) başka bir tablodadır. Splunk'ta bu tablolara **lookup** denir: genellikle bir CSV dosyası ya da KV store koleksiyonudur. Bu tezgahta veritabanındaki her tablo bir lookup olarak kullanılabilir.

Önce tabloyu gör. `inputlookup` olay aramadan, doğrudan tablonun satırlarını getiren bir **üretici** komuttur; bu yüzden `|` ile başlar:

```spl
| inputlookup sla
```

`lookup` her olayı tablodaki eşiyle eşleştirir ve istenen alanları olaya ekler:

```spl
sourcetype=biletler
| lookup sla oncelik OUTPUT hedef_saat
| table id oncelik hedef_saat
| head 5
```

| Yazım | Anlamı |
|---|---|
| `lookup sla oncelik` | eşleşme alanı `oncelik`; tablonun öteki bütün alanlarını ekle |
| `lookup sla oncelik OUTPUT hedef_saat` | yalnızca `hedef_saat`'i ekle |
| `lookup sunucular ad AS sunucu OUTPUT rol sehir` | tablodaki `ad`, olaydaki `sunucu` alanıyla eşleşsin |
| `... OUTPUT hedef_saat AS hedef` | eklenen alanın adını değiştir |
| `... OUTPUTNEW hedef_saat` | olayda alan zaten doluysa üzerine yazma |

Eşi bulunmayan olay **düşmez**; eklenen alanları boş kalır. `join`'den (SP06) farkı budur: `lookup` olay sayısını değiştirmez ve alt arama çalıştırmaz, bu yüzden çok daha ucuzdur.

```spl
sourcetype=istekler durum>=500
| lookup sunucular ad AS sunucu OUTPUT rol sehir
| table zaman sunucu rol sehir
```

> [!NOT]
> Gerçek Splunk'ta lookup'lar "otomatik" de tanımlanabilir: bir sourcetype'ın her araması, sen `lookup` yazmadan alanları ekler. Sentinel'deki izleme listeleri (watchlist) ve KQL'deki `lookup` (KQ09) aynı fikrin karşılıklarıdır.
:::

::: anlat makeresults: ifadeyi sına
`| makeresults` hiçbir veri okumadan boş olay üretir. Karmaşık bir `eval` ifadesini gerçek veride çalıştırmadan önce, kenar durumlarını tek tek denemenin en hızlı yoludur:

```spl
| makeresults count=4
| streamstats count as n
| eval durum=case(n=1, 200, n=2, 404, n=3, 500, n=4, 503)
| eval sinif=case(durum>=500, "5xx", durum>=400, "4xx", true(), "2xx")
| table durum sinif
```

KQL'deki `datatable` (KQ08) gibi, sonucunu bildiğin küçük bir girdiyle ifadenin doğru çalıştığını kanıtlarsın.
:::

::: tahmin
Kaç satır, hangi değerler?

```spl
| inputlookup sla
| where hedef_saat<24
| table oncelik hedef_saat
```

???

İki satır: `kritik|4` ve `yüksek|8`. `sla` tablosunda dört öncelik var; `orta` (24) ve `düşük` (72) 24'ten küçük değil.
:::

::: gorev SLA ihlali
Çözülmüş biletlerin çözüm süresini saat olarak (bir ondalık) `sure_saat` alanına hesapla, `sla` tablosundan önceliğin `hedef_saat`'ini ekle ve **hedefi aşan** biletleri `id`, `oncelik`, `sure_saat`, `hedef_saat` alanlarıyla getir.

```starter
sourcetype=biletler durum=çözüldü
| table id oncelik acilis kapanis
```

```test
eq(sutunlar, ["id", "oncelik", "sure_saat", "hedef_saat"], "sütunlar")
eq(sonuc, [(2, "orta", 25.0, 24)], "yalnızca 2 numaralı bilet hedefi aştı")
ok(kullanir("lookup"), "hedefi lookup ile ekle")
```

```solution
sourcetype=biletler durum=çözüldü
| eval sure_saat=round((strptime(kapanis, "%Y-%m-%d %H:%M")-strptime(acilis, "%Y-%m-%d %H:%M"))/3600, 1)
| lookup sla oncelik OUTPUT hedef_saat
| where sure_saat>hedef_saat
| table id oncelik sure_saat hedef_saat
```

```hint
Süre: iki zamanı `strptime` ile epoch saniyesine çevirip çıkar, 3600'e böl.
```

```hint
`lookup sla oncelik OUTPUT hedef_saat`, sonra `where sure_saat>hedef_saat`.
```
:::

::: gorev Şehir başına istek
Her sunucunun istek sayısını hesapla, şehir bilgisini `sunucular` tablosundan `lookup` ile ekle (tablodaki ad alanı `ad`, olaydaki `sunucu`) ve şehir başına toplam isteği getir: `sehir`, `istek`.

```starter
sourcetype=istekler
| stats count by sunucu
```

```test
eq(sutunlar, ["sehir", "istek"], "sütunlar")
eq(sonuc, [("Ankara", 6), ("İstanbul", 20)], "iki şehir")
```

```solution
sourcetype=istekler
| stats count by sunucu
| lookup sunucular ad AS sunucu OUTPUT sehir
| stats sum(count) as istek by sehir
```

```hint
Alan adları farklı: `lookup sunucular ad AS sunucu OUTPUT sehir`.
```

```hint
Önce sunucu başına say, sonra zenginleştir, en son şehre göre topla: `stats sum(count) as istek by sehir`.
```
:::

::: gorev İfadeyi makeresults ile sına
`makeresults` ile dört olay üret ve `durum` alanına sırasıyla 200, 404, 500, 503 değerlerini ver. Sonra durum kodunu sınıflandıran `sinif` alanını kur (500 ve üstü `5xx`, 400 ve üstü `4xx`, gerisi `2xx`) ve `durum`, `sinif` alanlarını getir.

```starter
| makeresults count=4
| table _time
```

```test
eq(sutunlar, ["durum", "sinif"], "sütunlar")
eq(sonuc, [(200, "2xx"), (404, "4xx"), (500, "5xx"), (503, "5xx")], "dört sınama durumu")
ok(kullanir("makeresults"), "makeresults kullan")
```

```solution
| makeresults count=4
| streamstats count as n
| eval durum=case(n=1, 200, n=2, 404, n=3, 500, n=4, 503)
| eval sinif=case(durum>=500, "5xx", durum>=400, "4xx", true(), "2xx")
| table durum sinif
```

```hint
Olayları numarala: `streamstats count as n`. Sonra `eval durum=case(n=1, 200, n=2, 404, ...)`.
```
:::
