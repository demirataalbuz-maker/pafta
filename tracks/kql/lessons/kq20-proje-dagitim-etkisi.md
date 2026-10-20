---
id: kq20
title: Proje · Dağıtım Etkisi Analizi
summary: Bir arızanın kök nedenine üç tablodan yaklaşmak; dağıtım öncesi ve sonrası zaman pencerelerini karşılaştırmak, her dağıtımdan sonraki ilk hata kaydını bulmak ve dağıtım, günlük ve istek kayıtlarını tek bir olay zaman çizelgesinde birleştirmek.
---

::: anlat Proje tanımı
09:00 civarında kullanıcılar rapor ekranının hata verdiğini bildirdi. Ekip şunu soruyor: **"Sabahki dağıtım mı bozdu?"** Elinde üç kaynak var:

| Tablo | İçerik |
|---|---|
| `dagitimlar` | hangi sunucuya, ne zaman, hangi sürüm dağıtıldı |
| `istekler` | kullanıcı istekleri ve durum kodları |
| `gunluk` | uygulamanın kendi günlük mesajları |

Bir olayı incelerken izlenen yol hep aynıdır ve bu projenin üç adımıdır:

1. **Önce ve sonra**: değişiklikten önceki ve sonraki eşit uzunlukta pencereleri karşılaştır. Fark yoksa değişiklik büyük olasılıkla suçsuzdur.
2. **İlk iz**: değişiklikten sonraki ilk hata kaydı ne zaman, ne diyor? Gecikme ve mesaj, nedenin ipucudur.
3. **Zaman çizelgesi**: bütün kaynakları tek bir çizelgede birleştir ve olayların sırasını gör.

> [!NOT]
> Zamanda yan yana gelmek neden-sonuç kanıtı değildir. Önce-sonra farkı ve zaman çizelgesi bir **hipotez** kurar: "2.5.0 sürümü rapor sorgularını yavaşlattı, bağlantı havuzu doldu". Raporunda bulguyu ("dağıtımdan 6 dakika sonra hatalar başladı") ve yorumu ("büyük olasılıkla sürüm kaynaklı") ayrı yaz. Hipotezi doğrulamak için bir sonraki adım geri alma (rollback) ya da sürüm notlarını incelemektir.
:::

::: tahmin
Tek satır yazar:

```kql
dagitimlar
| summarize sunucu_sayisi = dcount(sunucu), son = max(zaman)
```

???

`2|2026-10-19 11:40`. Üç dağıtım yapılmış ama ikisi web01'e: farklı sunucu sayısı 2. En son dağıtım 11:40'ta web01'e yapılan 2.5.1'dir.
:::

::: gorev 1 · Önce ve sonra
Her dağıtım için, aynı sunucuya dağıtımdan **önceki bir saat** ve dağıtım anından itibaren **sonraki bir saat** içindeki (sınırlar dahil) istekleri karşılaştır: `dagitim`, `sunucu`, `surum`, `once_istek`, `once_hata`, `sonra_istek`, `sonra_hata` (hata: 500 ve üstü). Dağıtım anındaki istek "sonra" sayılır. Dağıtım zamanına göre artan.

```starter
dagitimlar
| join kind=inner (istekler | project istek_zamani = zaman, sunucu, durum) on sunucu
| summarize istek = count() by dagitim = zaman, sunucu, surum
```

```test
eq(sutunlar, ["dagitim", "sunucu", "surum", "once_istek", "once_hata", "sonra_istek", "sonra_hata"], "sütunlar")
eq(sonuc, [("2026-10-19 08:55", "web01", "2.5.0", 3, 0, 4, 3), ("2026-10-19 10:40", "web02", "2.5.0", 1, 0, 3, 1),
           ("2026-10-19 11:40", "web01", "2.5.1", 1, 0, 1, 0)], "üç dağıtım")
```

```solution
dagitimlar
| join kind=inner (istekler | project istek_zamani = zaman, sunucu, durum) on sunucu
| where istek_zamani between ((zaman - 1h) .. (zaman + 1h))
| extend sonra = istek_zamani >= zaman
| summarize once_istek = countif(not(sonra)), once_hata = countif(not(sonra) and durum >= 500),
            sonra_istek = countif(sonra), sonra_hata = countif(sonra and durum >= 500)
            by dagitim = zaman, sunucu, surum
| sort by dagitim asc
```

```hint
İki saatlik pencere: `where istek_zamani between ((zaman - 1h) .. (zaman + 1h))`. Her isteği bir bayrakla işaretle: `extend sonra = istek_zamani >= zaman`.
```

```hint
Dört sayıyı tek `summarize`'da `countif` ile hesapla: `countif(not(sonra))`, `countif(sonra and durum >= 500)` …
```
:::

::: gorev 2 · İlk hata kaydı
Her dağıtımdan sonraki **30 dakika** içinde (sınırlar dahil), aynı sunucunun `gunluk` tablosuna düşen **ilk** `ERROR` seviyeli kaydı bul: `dagitim`, `sunucu`, `gecikme` (dağıtımdan ilk hataya kadar geçen süre), `mesaj`; dağıtım zamanına göre artan. Hata kaydı olmayan dağıtım listede olmasın.

```starter
dagitimlar
| join kind=inner (gunluk | where seviye == "ERROR" | project hata_zamani = zaman, sunucu, mesaj) on sunucu
| project dagitim = zaman, sunucu, hata_zamani, mesaj
```

```test
eq(sutunlar, ["dagitim", "sunucu", "gecikme", "mesaj"], "sütunlar")
eq(sonuc, [("2026-10-19 08:55", "web01", "00:06:00", "yavaş sorgu tablo=raporlar sure=2300ms"),
           ("2026-10-19 10:40", "web02", "00:02:00", "yavaş sorgu tablo=raporlar sure=2600ms")], "iki dağıtımdan sonra hata var")
ok(kullanir("arg_min"), "ilk kaydı arg_min ile al")
```

```solution
dagitimlar
| join kind=inner (gunluk | where seviye == "ERROR" | project hata_zamani = zaman, sunucu, mesaj) on sunucu
| where hata_zamani between (zaman .. zaman + 30m)
| summarize arg_min(hata_zamani, mesaj) by dagitim = zaman, sunucu
| extend gecikme = hata_zamani - dagitim
| project dagitim, sunucu, gecikme, mesaj
| sort by dagitim asc
```

```hint
Pencere: `where hata_zamani between (zaman .. zaman + 30m)`. Her dağıtımın ilk hatası: `summarize arg_min(hata_zamani, mesaj) by dagitim = zaman, sunucu`.
```

```hint
Gecikme iki anın farkıdır: `extend gecikme = hata_zamani - dagitim`.
```
:::

::: gorev 3 · Olay zaman çizelgesi
web01 için `2026-10-19 08:50` ile `09:15` arasındaki (sınırlar dahil) olayları tek bir çizelgede birleştir. Her kaynaktan gelen satır için `olay` sütununu şöyle kur:

- dağıtım → `"dağıtım 2.5.0"` (`strcat("dağıtım ", surum)`)
- `gunluk`'teki `ERROR` kayıtları → mesajın kendisi
- 500 ve üstü durum kodlu istekler → `"GET /api/rapor → 500"` (yöntem, yol, ok işareti ve durum kodu)

Sonuç: `zaman`, `olay`; zamana göre, aynı zamanda olaya göre artan.

```starter
union dagitimlar, gunluk, istekler
| where sunucu == "web01"
| project zaman
| sort by zaman asc
```

```test
eq(sutunlar, ["zaman", "olay"], "sütunlar")
eq(sonuc, [("2026-10-19 08:55", "dağıtım 2.5.0"),
           ("2026-10-19 09:01", "GET /api/rapor → 500"),
           ("2026-10-19 09:01", "yavaş sorgu tablo=raporlar sure=2300ms"),
           ("2026-10-19 09:02", "GET /api/rapor → 500"),
           ("2026-10-19 09:02", "bağlantı havuzu dolu aktif=50 bekleyen=12"),
           ("2026-10-19 09:12", "GET /api/rapor → 503"),
           ("2026-10-19 09:12", "bağlantı havuzu dolu aktif=50 bekleyen=31")], "yedi olay")
ok(kullanir("union"), "kaynakları union ile birleştir")
```

```solution
let bas = datetime(2026-10-19 08:50);
let bit = datetime(2026-10-19 09:15);
union
    (dagitimlar | extend olay = strcat("dağıtım ", surum)),
    (gunluk | where seviye == "ERROR" | extend olay = mesaj),
    (istekler | where durum >= 500 | extend olay = strcat(yontem, " ", yol, " → ", tostring(durum)))
| where sunucu == "web01" and zaman between (bas .. bit)
| project zaman, olay
| sort by zaman asc, olay asc
```

```hint
Her kaynağı önce parantez içinde hazırla: süz ve `extend olay = ...` ile ortak sütunu kur. Sonra `union (...), (...), (...)`.
```

```hint
Birleşmeden sonra `where sunucu == "web01" and zaman between (...)`, `project zaman, olay` ve `sort by zaman asc, olay asc`.
```
:::
