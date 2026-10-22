---
id: sp05
title: rex, Metin Fonksiyonları ve Zaman
summary: rex ile metinden alan çıkarmak, like/match/replace, len/lower/substr; strptime ve strftime ile zaman, bin ile zaman dilimleri.
kazanim: PU 2.1, PU 4.1, APU 2.2, APU 2.3, APU 5.1, APU 5.2, APU 5.3, APU 12.1, APU 12.5
---

::: anlat Metinden alan çıkarmak
Kayıtların en değerli bilgisi çoğu zaman bir metnin içine gömülüdür. `rex` bir düzenli ifadenin **adlı gruplarını** yeni alanlara dönüştürür (Regex yolundaki adlı gruplar, burada `(?<ad>...)` yazımıyla):

```spl
sourcetype=sunucular
| rex field=isletim "(?<aile>\w+) (?<surum>[\d.]+)"
| table ad aile surum
```

`eval` ve `where` içinde sık kullanılan metin fonksiyonları:

| Fonksiyon | Ne yapar |
|---|---|
| `like(x, "web%")` | SQL tarzı joker eşleşme (`%`, `_`) |
| `match(x, "^db\d+")` | düzenli ifade eşleşmesi |
| `replace(x, "desen", "yeni")` | düzenli ifadeyle değiştir |
| `len(x)`, `lower(x)`, `upper(x)` | uzunluk, küçük/büyük harf |
| `substr(x, başlangıç, uzunluk)` | parça (başlangıç **1**'den sayılır) |

```spl
sourcetype=biletler
| where match(baslik, "\d")
| eval kisa = substr(baslik, 1, 12)
| table id kisa baslik
```

### Zaman
Gerçek Splunk'ta her olayın bir `_time` alanı vardır ve zamanlar "epoch" (1970'ten beri geçen saniye) olarak tutulur. Metin bir zamanı epoch'a `strptime`, epoch'u metne `strftime` çevirir; biçim kodları Python'dakiyle aynıdır (`%Y-%m-%d %H:%M`):

```spl
sourcetype=biletler
| eval an = strptime(acilis, "%Y-%m-%d %H:%M")
| eval gun = strftime(an, "%A"), saat = strftime(an, "%H")
| table id acilis gun saat
| head 5
```

`bin alan span=1d` (ya da `1h`, `15m`) zamanı dilimin başına yuvarlar; "gün başına kaç olay?" sorusunun cevabı budur:

```spl
sourcetype=biletler
| bin acilis span=1d
| stats count by acilis
```

> [!NOT]
> Gerçek Splunk'ta bu kalıbın kısa yolu `timechart span=1d count` komutudur; `_time` alanı üzerinde çalışır ve sonucu grafiğe hazır verir. Bu tezgahta zamanlar `acilis` gibi metin alanlarda durduğu için `bin` + `stats` kullanıyoruz.
:::

::: tahmin
İki satır yazar:

```spl
sourcetype=biletler
| bin acilis span=1d
| stats count by acilis
| head 2
```

???

`2026-10-12 00:00|3` ve `2026-10-13 00:00|3`. Açılış zamanları günün başına yuvarlanır, `stats` günlere göre sayar ve sonucu güne göre sıralar; `head 2` ilk iki günü tutar.
:::

::: gorev Ubuntu sürümleri
Ubuntu çalıştıran sunucular için `ad` ve işletim sisteminden `rex` ile çıkarılmış `surum` alanını (`24.04` gibi) getir.

```starter
sourcetype=sunucular isletim="Ubuntu*"
| table ad isletim
```

```test
eq(sutunlar, ["ad", "surum"], "alanlar: ad, surum")
eq(sorted(sonuc), [("cache01", "24.04"), ("izleme01", "22.04"), ("test01", "24.04"), ("web01", "24.04"), ("web02", "24.04"), ("web03", "22.04")], "altı sunucu ve sürümleri")
ok(kullanir("rex"), "rex kullan")
```

```solution
sourcetype=sunucular isletim="Ubuntu*"
| rex field=isletim "Ubuntu (?<surum>\d+\.\d+)"
| table ad surum
```

```hint
Adlı grup: `(?<surum>\d+\.\d+)`; `rex field=isletim "..."` bu grubu `surum` alanı yapar.
```
:::

::: gorev Yoğun saatler
Biletlerin açılış saatini (`saat`, `06` gibi iki haneli) çıkar ve saate göre say; en kalabalık **üç** saati, eşitlikte saate göre artan sırayla getir. Alanlar `saat` ve `count`.

```cikti
09|4
10|3
07|2
```

```starter
sourcetype=biletler
| stats count
```

```test
eq(sutunlar, ["saat", "count"], "alanlar: saat, count")
eq(sonuc, [("09", 4), ("10", 3), ("07", 2)], "en kalabalık üç saat")
```

```solution
sourcetype=biletler
| eval saat = strftime(strptime(acilis, "%Y-%m-%d %H:%M"), "%H")
| stats count by saat
| sort -count, saat
| head 3
```

```hint
Saat: `strftime(strptime(acilis, "%Y-%m-%d %H:%M"), "%H")`. Sonra `stats count by saat`.
```

```hint
İki anahtarla sırala: `sort -count, saat`, ardından `head 3`.
```
:::

::: gorev Disk biletlerinin günü
Başlığı `Disk` ile başlayan biletlerin `id`'sini ve açılış gününü (`gun`, `YYYY-AA-GG`) `id` sırasıyla getir; `where` ve `match` kullan.

```starter
sourcetype=biletler disk
| table id acilis
```

```test
eq(sutunlar, ["id", "gun"], "alanlar: id, gun")
eq(sonuc, [(1, "2026-10-12"), (13, "2026-10-16"), (20, "2026-10-19")], "üç disk bileti")
ok(kullanir("match"), "match kullan")
```

```solution
sourcetype=biletler
| where match(baslik, "^Disk")
| eval gun = substr(acilis, 1, 10)
| sort id
| table id gun
```

```hint
`where match(baslik, "^Disk")`; gün için `substr(acilis, 1, 10)` (Splunk'ta substr 1'den sayar).
```
:::
