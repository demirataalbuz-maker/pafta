---
id: sp07
title: Zaman Çizelgesi
summary: Her olayın _time alanı; timechart ile zamanı dilimlere bölmek, by ile seriler, count(eval(...)) as ile koşullu sayım, boş dilimlerin sıfırla dolması, bin _time ile stats ve günün saatine göre özet.
---

::: anlat _time ve timechart
Gerçek Splunk'ta her olayın bir **`_time`** alanı vardır: olayın gerçekleştiği an, epoch saniyesi olarak saklanır, ekranda tarih olarak görünür. Bu yolda artık yeni kaynaklar var ve hepsinde `_time` hazır:

| sourcetype | İçerik |
|---|---|
| `istekler` | bir iç uygulamanın web istek günlüğü: `yontem`, `yol`, `durum`, `sure_ms`, `sunucu`, `kullanici`, `istemci` |
| `gunluk` | uygulama günlüğü: `seviye`, `mesaj` |
| `dagitimlar` | sürüm dağıtımları: `sunucu`, `surum` |
| `isler` | gece bakım işlerinin başladı / bitti satırları |

```spl
sourcetype=istekler
| head 3
| table _time sunucu yol durum
```

`timechart` zamanı eşit **dilimlere** böler ve her dilim için bir toplama hesaplar. Splunk panolarındaki çizgi grafiklerin neredeyse hepsi bir `timechart`'tır:

```spl
sourcetype=istekler
| timechart span=1h count
```

| Yazım | Sonuç |
|---|---|
| `timechart span=1h count` | saat başına olay sayısı |
| `timechart span=1h count by sunucu` | her sunucu ayrı bir sütun (seri) |
| `timechart span=30m avg(sure_ms)` | yarım saatlik ortalama |
| `timechart span=1h count(eval(durum>=500)) as hata` | yalnızca koşula uyan olayları say |

`count(eval(koşul))` Splunk'ın en çok kullanılan kalıplarından biridir: koşul doğru olan olayları sayar. Sonucuna mutlaka `as` ile **ad vermelisin**; Splunk adsız bırakılmasına izin vermez.

> [!NOT]
> `timechart` olay bulunmayan dilimleri **atlamaz**: ilk ve son dilim arasındaki boş dilimler `count` için 0 olur. `stats count by` ise yalnızca olayı olan grupları verir. Grafikte eğrinin "kopmaması" bu yüzdendir. Gerçek Splunk'ta zaman aralığı arama çubuğundan ya da `earliest=-24h` gibi bir ifadeyle seçilir; bu tezgahta veri sabit bir güne ait.
:::

::: anlat bin _time ve günün saati
`timechart`'ın yaptığını açıkça yazmak istersen `bin` ile `_time`'ı dilimin başına yuvarla, sonra `stats` kullan:

```spl
sourcetype=istekler
| bin _time span=1h
| stats count by _time
```

Fark: bu yol boş dilimleri doldurmaz ama birden çok alana göre gruplamana izin verir (`stats count by _time sunucu yol`).

"Günün hangi saatleri yoğun?" sorusu ise zamandan bir **parça** ister. `strftime` `_time`'ı istediğin biçimde metne çevirir:

```spl
sourcetype=istekler
| eval saat=strftime(_time, "%H")
| stats count by saat
```

| Biçim | Anlamı |
|---|---|
| `%Y-%m-%d` | tarih |
| `%H`, `%M` | saat, dakika |
| `%A` | haftanın günü (İngilizce ad) |
| `%w` | haftanın günü, 0 = pazar |
:::

::: tahmin
Kaç satır, hangi değerler?

```spl
sourcetype=istekler durum>=500
| timechart span=30m count
```

???

Dört satır: `2026-10-19 09:00|3`, `2026-10-19 09:30|0`, `2026-10-19 10:00|0`, `2026-10-19 10:30|1`. Hatalar 09:01, 09:02, 09:12 ve 10:42'de. `timechart` ilk dilimden (09:00) son dilime (10:30) kadar her yarım saati gösterir; arada hata olmayan iki dilim 0 olur.
:::

::: gorev Saatlik hata sayısı
Her saat için 500 ve üstü durum kodlu istek sayısını `hata` adıyla getir; hatasız saatler 0 görünsün. Arama bütün isteklerden başlasın (hataları önceden süzme), böylece günün dört saatinin hepsi çizelgede olsun.

```starter
sourcetype=istekler durum>=500
| stats count by sunucu
```

```test
eq(sutunlar, ["_time", "hata"], "sütunlar: _time, hata")
eq(sonuc, [("2026-10-19 08:00", 0), ("2026-10-19 09:00", 3), ("2026-10-19 10:00", 1), ("2026-10-19 11:00", 0)], "dört saat")
ok(kullanir("timechart"), "timechart kullan")
```

```solution
sourcetype=istekler
| timechart span=1h count(eval(durum>=500)) as hata
```

```hint
`timechart span=1h` ile başla; koşullu sayım: `count(eval(durum>=500)) as hata`.
```
:::

::: gorev Sunucu başına saatlik istek
Her saat için her sunucunun istek sayısını ayrı bir sütunda getir.

```starter
sourcetype=istekler
| timechart span=1h count
```

```test
eq(sutunlar, ["_time", "web01", "web02", "web03"], "her sunucu bir sütun")
eq(sonuc, [("2026-10-19 08:00", 3, 3, 1), ("2026-10-19 09:00", 4, 2, 2),
           ("2026-10-19 10:00", 2, 3, 2), ("2026-10-19 11:00", 2, 1, 1)], "dört saat, üç seri")
```

```solution
sourcetype=istekler
| timechart span=1h count by sunucu
```

```hint
Seriye bölmek için `by`: `timechart span=1h count by sunucu`.
```
:::

::: gorev Günün saatine göre ortalama süre
İstekleri günün saatine göre (`saat`: iki haneli saat, `08` gibi) grupla ve ortalama süreyi tam sayıya yuvarlanmış olarak `ort` adıyla getir.

```starter
sourcetype=istekler
| stats avg(sure_ms) as ort
```

```test
eq(sutunlar, ["saat", "ort"], "sütunlar: saat, ort")
eq(sonuc, [("08", 230), ("09", 870), ("10", 673), ("11", 121)], "dört saat")
ok(kullanir("strftime"), "saati strftime ile çıkar")
```

```solution
sourcetype=istekler
| eval saat=strftime(_time, "%H")
| stats avg(sure_ms) as ort by saat
| eval ort=round(ort, 0)
```

```hint
`eval saat=strftime(_time, "%H")`, sonra `stats avg(sure_ms) as ort by saat`.
```

```hint
Yuvarlama: `eval ort=round(ort, 0)`.
```
:::
