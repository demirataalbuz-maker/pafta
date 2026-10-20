---
id: sp15
title: Koşullu Toplama ve Aykırı Değerler
summary: count(eval(...)) ve sum(eval(if(...))) ile tek stats'ta birden çok koşul, earliest ve latest ile zamana göre ilk ve son değer, range ve dc, eventstats ile ortalama ve standart sapmayı her olaya yazıp z-puanıyla aykırı değer bulmak.
---

::: anlat Tek stats, birçok soru
SP08'de koşullu sayım için her olaya `eval` ile 0/1 bayrağı koyup `sum` almıştın. Aynı işin kısa yolu, toplama fonksiyonunun içine bir `eval` yazmaktır:

```spl
sourcetype=istekler
| stats count as istek, count(eval(durum>=500)) as hata, count(eval(sure_ms>1000)) as yavas by sunucu
```

| Kalıp | Anlamı |
|---|---|
| `count(eval(koşul)) as ad` | koşula uyan olay sayısı |
| `sum(eval(if(koşul, x, 0))) as ad` | koşula uyan olayların `x` toplamı |
| `dc(eval(if(koşul, x, null()))) as ad` | koşula uyan olaylarda farklı `x` sayısı |

`eval` içeren her toplamaya `as` ile **ad vermek zorunludur**.

### Zamana göre ilk ve son
| Fonksiyon | Döndürdüğü |
|---|---|
| `earliest(x)` | `_time`'ı en küçük olayın `x` değeri |
| `latest(x)` | `_time`'ı en büyük olayın `x` değeri: "son durum" |
| `range(x)` | en büyük − en küçük; `range(_time)` gözlem süresi (saniye) |
| `dc(x)` | farklı değer sayısı |

```spl
sourcetype=istekler
| stats earliest(yol) as ilk, latest(yol) as son, latest(durum) as son_durum by sunucu
```

> [!NOT]
> Splunk'ta bir de `first(x)` ve `last(x)` vardır: bunlar zamana değil **arama sonucundaki sıraya** bakar. Splunk olayları en yeniden eskiye getirdiği için `first` çoğu zaman en **yeni** değeri verir; bu ters görünen davranış sık bir hatadır. Zamana göre düşünüyorsan `earliest` ve `latest` kullan.
:::

::: anlat Aykırı değer: ortalamadan kaç sapma uzakta?
"Bu istek yavaş mı?" sorusunun cevabı, isteğin kendi grubuna göre ne kadar sıra dışı olduğudur. `/api/durum` için 18 ms yavaştır, `/api/rapor` için 18 ms imkânsız derecede hızlıdır. **z-puanı** bir değerin grubunun ortalamasından kaç **standart sapma** uzakta olduğunu söyler:

`z = (değer − ortalama) / standart sapma`

```spl
sourcetype=istekler
| eventstats avg(sure_ms) as ort, stdev(sure_ms) as sapma by yol
| eval z=round((sure_ms-ort)/sapma, 1)
| where z>1
| table zaman yol sure_ms z
```

| z | Yorum |
|---|---|
| 0 civarı | tipik |
| 1–2 | dikkat çekici |
| 3 ve üstü | çok sıra dışı (normal dağılımda binde birkaç) |

> [!İPUCU]
> Küçük gruplarda z-puanı güvenilmezdir: iki değerli bir grupta hiçbir değer 1'den uzak olamaz, tek değerli grupta sapma 0'dır ve bölme sonuç vermez. Sahada bu yöntemi yeterince olayı olan gruplarda ve uzun bir geçmiş penceresiyle (ör. son 7 günün ortalaması) kullanırsın. Splunk'ın Machine Learning Toolkit'i ve KQL'deki `series_decompose_anomalies` aynı fikrin gelişmiş sürümleridir.
:::

::: tahmin
Üç satır yazar:

```spl
sourcetype=istekler
| stats earliest(yol) as ilk, latest(yol) as son by sunucu
```

???

`web01|/api/bilet|/api/bilet`, `web02|/api/bilet/42|/api/bilet`, `web03|/api/durum|/api/durum`. web01'in ilk isteği 08:02'de, son isteği 11:47'de, ikisi de `/api/bilet`. web02'nin ilk isteği 08:05'te `/api/bilet/42`, sonuncusu 11:20'de `/api/bilet`. web03 yalnızca durum ve ana sayfa isteği almış; ilki ve sonuncusu `/api/durum`.
:::

::: gorev Tek stats ile sunucu karnesi
Her sunucu için tek bir `stats` ile şunları getir: `istek` (istek sayısı), `hata` (500 ve üstü), `yavas` (süresi 1000 ms'yi aşan), `son_durum` (zamana göre en son isteğin durum kodu).

```starter
sourcetype=istekler
| stats count as istek by sunucu
```

```test
eq(sutunlar, ["sunucu", "istek", "hata", "yavas", "son_durum"], "sütunlar")
eq(sonuc, [("web01", 11, 3, 3, 200), ("web02", 9, 1, 2, 201), ("web03", 6, 0, 0, 200)], "üç sunucu")
ok(kullanir("latest"), "son durumu latest ile al")
```

```solution
sourcetype=istekler
| stats count as istek, count(eval(durum>=500)) as hata, count(eval(sure_ms>1000)) as yavas, latest(durum) as son_durum by sunucu
```

```hint
Koşullu sayımlar: `count(eval(durum>=500)) as hata`, `count(eval(sure_ms>1000)) as yavas`.
```

```hint
Zamana göre son değer: `latest(durum) as son_durum`.
```
:::

::: gorev Kullanıcının ilk ve son isteği
Kullanıcısı olan her kullanıcı için istek sayısını ve zamana göre **ilk** ve **son** isteğinin yolunu getir: `kullanici`, `istek`, `ilk_yol`, `son_yol`.

```starter
sourcetype=istekler kullanici=*
| stats count as istek by kullanici
```

```test
eq(sutunlar, ["kullanici", "istek", "ilk_yol", "son_yol"], "sütunlar")
eq(sonuc, [("ayse", 5, "/api/bilet", "/api/bilet"), ("can", 5, "/api/bilet/42", "/api/rapor"),
           ("mert", 4, "/api/bilet", "/api/rapor"), ("selin", 1, "/api/bilet", "/api/bilet"),
           ("zeynep", 4, "/api/rapor", "/api/bilet")], "beş kullanıcı")
```

```solution
sourcetype=istekler kullanici=*
| stats count as istek, earliest(yol) as ilk_yol, latest(yol) as son_yol by kullanici
```

```hint
`earliest(yol) as ilk_yol, latest(yol) as son_yol`.
```
:::

::: gorev Yolunun z-puanı
Her isteğin, **kendi yolunun** ortalamasına ve standart sapmasına göre z-puanını (bir ondalık) hesapla ve z-puanı 1'i aşan istekleri `zaman`, `yol`, `sure_ms`, `z` alanlarıyla getir.

```starter
sourcetype=istekler
| eventstats avg(sure_ms) as ort by yol
| where sure_ms>ort
| table zaman yol sure_ms
```

```test
eq(sutunlar, ["zaman", "yol", "sure_ms", "z"], "sütunlar")
eq(sonuc, [("2026-10-19 08:12", "/api/bilet", 310, 1.8), ("2026-10-19 10:30", "/api/durum", 18, 1.3),
           ("2026-10-19 10:42", "/api/rapor", 2600, 1.2), ("2026-10-19 11:20", "/api/bilet", 280, 1.4)], "dört aykırı istek")
ok(kullanir("stdev"), "standart sapma için stdev kullan")
```

```solution
sourcetype=istekler
| eventstats avg(sure_ms) as ort, stdev(sure_ms) as sapma by yol
| eval z=round((sure_ms-ort)/sapma, 1)
| where z>1
| table zaman yol sure_ms z
```

```hint
Ortalama ve sapmayı birlikte yaz: `eventstats avg(sure_ms) as ort, stdev(sure_ms) as sapma by yol`.
```

```hint
`eval z=round((sure_ms-ort)/sapma, 1)`, sonra `where z>1`.
```
:::
