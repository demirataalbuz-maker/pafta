---
id: kq16
title: Oturumlar ve Seriler
summary: Olayları sessizlik eşiğine göre oturumlara bölmek; row_window_session, prev ve row_cumsum ile elle oturum numarası, oturum özetleri ve ardışık aynı durumdaki satırları (adaları) tek bir seri olarak toplamak.
---

::: anlat Olaylardan oturumlara
SQ15'da `LAG` ve birikimli toplamla oturum kurdun. KQL'de aynı iş iki yoldan yapılır.

### Kısa yol: row_window_session
`row_window_session(zaman, ilkten_en_fazla, komsular_arasi_en_fazla, yeniden_baslat)` her satır için içinde bulunduğu oturumun **başlangıç zamanını** döndürür. Yeni oturum şu durumlarda başlar:

- bir önceki satırla arasındaki fark `komsular_arasi_en_fazla`'yı aşarsa,
- oturumun ilk satırından bu yana geçen süre `ilkten_en_fazla`'yı aşarsa,
- `yeniden_baslat` koşulu doğruysa (ör. kullanıcı değiştiyse).

```kql
istekler
| where isnotempty(kullanici)
| sort by kullanici asc, zaman asc
| extend oturum = row_window_session(zaman, 2h, 30m, kullanici != prev(kullanici))
| project kullanici, zaman, oturum
```

Oturumun başlangıç zamanı aynı zamanda oturumun **kimliğidir**: `summarize ... by kullanici, oturum` ile oturum başına özet çıkarırsın.

### Açık yol: bayrak ve birikimli toplam
Kuralı tamamen kendin belirlemek istediğinde SQL'deki yöntemin aynısı: yeni oturum bayrağı ve onun birikimli toplamı:

```kql
istekler
| where isnotempty(kullanici)
| sort by kullanici asc, zaman asc
| extend yeni = iff(kullanici != prev(kullanici) or zaman - prev(zaman) > 30m, 1, 0)
| extend oturum_no = row_cumsum(yeni, kullanici != prev(kullanici))
| where kullanici == "can"
| project zaman, yeni, oturum_no
```

> [!NOT]
> `ilkten_en_fazla` sınırı sonsuz uzayan oturumları böler. Gün boyu her 20 dakikada bir istek atan bir izleyici, yalnızca komşu kuralıyla tek ve sonsuz bir oturum olurdu. Sentinel'de oturum açma ya da etkinlik oturumu analizlerinde bu iki sınır birlikte kullanılır ve eşikler raporda yazılır.
:::

::: anlat Seriler: ardışık aynı durumlar
"Hatalar kaç dalga halinde geldi ve her dalga ne kadar sürdü?" SQ14'teki boşluk ve ada sorusudur. KQL'de en temiz çözüm, **durum değiştiğinde** artan bir sayaçtır. Aynı sayaca sahip ardışık satırlar bir seridir:

```kql
istekler
| sort by zaman asc
| extend hatali = durum >= 500
| extend grup = row_cumsum(iff(hatali != prev(hatali), 1, 0))
| project zaman, durum, hatali, grup
```

`grup` her geçişte bir artar. Ardından `summarize bas = min(zaman), bit = max(zaman), adet = count() by grup, hatali` her seriyi tek satıra indirir.

| Soru | Kalıp |
|---|---|
| kullanıcı kaç kez oturum açıp çalıştı? | `row_window_session` + `dcount(oturum)` |
| her oturum ne kadar sürdü? | `summarize min, max by oturum` + `bit - bas` |
| art arda kaç hata oldu? | geçiş sayacı (`row_cumsum` + `prev`) + `summarize by grup` |
:::

::: tahmin
İki satır yazar:

```kql
datatable(z:datetime)[datetime(2026-10-19 09:00), datetime(2026-10-19 09:20), datetime(2026-10-19 10:30), datetime(2026-10-19 10:40)]
| sort by z asc
| extend oturum = row_window_session(z, 1d, 30m)
| summarize adet = count() by oturum
| sort by oturum asc
```

???

`2026-10-19 09:00|2` ve `2026-10-19 10:30|2`. 09:20, 09:00'dan 20 dakika sonra geldiği için aynı oturumdadır. 10:30 ile 09:20 arasında 70 dakika var: 30 dakikalık komşu sınırı aşıldı, yeni oturum başladı. 10:40 ona katılır. Oturumun değeri, başlangıç zamanıdır.
:::

::: gorev Kullanıcı başına oturum sayısı
Boş olmayan her kullanıcının isteklerini oturumlara böl: ardışık iki istek arasında **30 dakikadan** uzun sessizlik ya da oturumun başından bu yana **2 saatten** fazla süre yeni oturum başlatsın. Her kullanıcının oturum sayısını getir: `kullanici`, `oturum_sayisi`; çoktan aza, eşitlikte kullanıcıya göre.

```starter
istekler
| where isnotempty(kullanici)
| summarize istek = count() by kullanici
```

```test
eq(sutunlar, ["kullanici", "oturum_sayisi"], "sütunlar")
eq(sonuc, [("ayse", 4), ("can", 3), ("mert", 3), ("zeynep", 2), ("selin", 1)], "beş kullanıcı")
```

```solution
istekler
| where isnotempty(kullanici)
| sort by kullanici asc, zaman asc
| extend oturum = row_window_session(zaman, 2h, 30m, kullanici != prev(kullanici))
| summarize oturum_sayisi = dcount(oturum) by kullanici
| sort by oturum_sayisi desc, kullanici asc
```

```hint
Önce `sort by kullanici asc, zaman asc`, sonra `row_window_session(zaman, 2h, 30m, kullanici != prev(kullanici))`.
```

```hint
Her oturumun değeri başlangıç zamanı olduğu için oturum sayısı, farklı değerlerin sayısıdır: `dcount(oturum)`.
```
:::

::: gorev Oturum özeti
Aynı kurallarla `can` ve `zeynep` kullanıcılarının her oturumunu özetle: `kullanici`, `bas`, `bit`, `istek`, `sure` (`bit - bas`, süre türünde); kullanıcıya sonra başlangıca göre artan.

```starter
istekler
| where kullanici in ("can", "zeynep")
| summarize bas = min(zaman), bit = max(zaman), istek = count() by kullanici
```

```test
eq(sutunlar, ["kullanici", "bas", "bit", "istek", "sure"], "sütunlar")
eq(sonuc, [("can", "2026-10-19 08:05", "2026-10-19 08:05", 1, "00:00:00"),
           ("can", "2026-10-19 08:46", "2026-10-19 09:15", 2, "00:29:00"),
           ("can", "2026-10-19 10:42", "2026-10-19 10:44", 2, "00:02:00"),
           ("zeynep", "2026-10-19 09:01", "2026-10-19 09:20", 3, "00:19:00"),
           ("zeynep", "2026-10-19 11:47", "2026-10-19 11:47", 1, "00:00:00")], "beş oturum")
```

```solution
istekler
| where kullanici in ("can", "zeynep")
| sort by kullanici asc, zaman asc
| extend oturum = row_window_session(zaman, 2h, 30m, kullanici != prev(kullanici))
| summarize bas = min(zaman), bit = max(zaman), istek = count() by kullanici, oturum
| extend sure = bit - bas
| project kullanici, bas, bit, istek, sure
| sort by kullanici asc, bas asc
```

```hint
Önceki görevin oturum sütununu kur, sonra `summarize bas = min(zaman), bit = max(zaman), istek = count() by kullanici, oturum`.
```
:::

::: gorev Hata serileri
Bütün istekleri zamana göre sıraya koy ve art arda gelen 500 ve üstü durum kodlu isteklerin **serilerini** bul: her seri için `bas`, `bit`, `adet`; başlangıca göre artan.

```starter
istekler
| where durum >= 500
| project zaman, sunucu, durum
| sort by zaman asc
```

```test
eq(sutunlar, ["bas", "bit", "adet"], "sütunlar")
eq(sonuc, [("2026-10-19 09:01", "2026-10-19 09:02", 2), ("2026-10-19 09:12", "2026-10-19 09:12", 1),
           ("2026-10-19 10:42", "2026-10-19 10:42", 1)], "üç seri")
```

```solution
istekler
| sort by zaman asc
| extend hatali = durum >= 500
| extend grup = row_cumsum(iff(hatali != prev(hatali), 1, 0))
| summarize bas = min(zaman), bit = max(zaman), adet = count() by grup, hatali
| where hatali
| project bas, bit, adet
| sort by bas asc
```

```hint
Hataları önceden süzersen aralarındaki başarılı istekler kaybolur ve seriler ayırt edilemez. Bütün istekleri sırala, her satıra `hatali = durum >= 500` bayrağını koy.
```

```hint
Geçiş sayacı: `row_cumsum(iff(hatali != prev(hatali), 1, 0))`. Sonra `summarize ... by grup, hatali` ve `where hatali`.
```
:::
