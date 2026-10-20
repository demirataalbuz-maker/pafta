---
id: sp17
title: Proje · SLA Uyum Raporu
summary: Bilet verisinden hizmet seviyesi raporu kurmak; çözüm süresini hesaplayıp sla lookup'ıyla karşılaştırmak, öncelik başına uyum oranı ve toplam satırı, açık biletlerin yaşı ve hedefini aşanlar.
---

::: anlat Proje tanımı
BT müdürü her hafta bir **SLA (hizmet seviyesi) raporu** istiyor: biletler öncelik başına hedef sürelerinde çözülüyor mu, ve şu an açık olup hedefini çoktan aşmış bilet var mı? Hedef süreler `sla` lookup'ında:

```spl
| inputlookup sla
```

Rapor üç parçadan oluşacak:

| Adım | Soru | Araçlar |
|---|---|---|
| 1 | her çözülmüş bilet hedefinde mi? | `strptime`, `lookup`, `if` |
| 2 | öncelik başına uyum oranı ne? | `count(eval())`, `appendpipe` |
| 3 | hangi açık biletler gecikti? | `now()`, `lookup`, `sort` |

### Süre hesabı
`acilis` ve `kapanis` metin olarak duruyor (`2026-10-12 08:15`). Süre için ikisini de `strptime` ile epoch saniyesine çevir ve çıkar; saate çevirmek için 3600'e böl. Açık biletin yaşı için kapanış yerine "şimdi"yi kullan: `now()` (bu tezgahta sabit: 2026-10-19 12:00).

> [!NOT]
> Gerçek bir SLA hesabında çoğu zaman **iş saatleri** ve tatiller sayılmaz, bilet "beklemede" durumundayken saat durur. Bu projede takvim saatiyle hesaplıyoruz; raporda hangi tanımı kullandığını mutlaka yaz.
:::

::: tahmin
Tek bir sayı:

```spl
sourcetype=biletler durum=açık
| stats count
```

???

`9`. Biletlerin 11'i çözülmüş, 9'u hâlâ açık.
:::

::: gorev 1 · Bilet başına hedef
Çözülmüş her bilet için çözüm süresini saat olarak (bir ondalık) `sure_saat` alanına hesapla, `hedef_saat`'i `sla` lookup'ından ekle ve `sonuc` alanına süre hedefi aşıyorsa `"aşıldı"`, aşmıyorsa `"hedefte"` yaz: `id`, `oncelik`, `sure_saat`, `hedef_saat`, `sonuc`.

```starter
sourcetype=biletler durum=çözüldü
| table id oncelik acilis kapanis
```

```test
eq(sutunlar, ["id", "oncelik", "sure_saat", "hedef_saat", "sonuc"], "sütunlar")
eq(len(sonuc), 11, "on bir çözülmüş bilet")
eq([r for r in sonuc if r[4] == "aşıldı"], [(2, "orta", 25.0, 24, "aşıldı")], "yalnızca 2 numaralı bilet aştı")
eq(sonuc[8], (14, "orta", 24.0, 24, "hedefte"), "tam sınırdaki bilet hedefte sayılır")
```

```solution
sourcetype=biletler durum=çözüldü
| eval sure_saat=round((strptime(kapanis, "%Y-%m-%d %H:%M")-strptime(acilis, "%Y-%m-%d %H:%M"))/3600, 1)
| lookup sla oncelik OUTPUT hedef_saat
| eval sonuc=if(sure_saat>hedef_saat, "aşıldı", "hedefte")
| table id oncelik sure_saat hedef_saat sonuc
```

```hint
Süre: `round((strptime(kapanis, "%Y-%m-%d %H:%M")-strptime(acilis, "%Y-%m-%d %H:%M"))/3600, 1)`.
```

```hint
`lookup sla oncelik OUTPUT hedef_saat`, sonra `eval sonuc=if(sure_saat>hedef_saat, "aşıldı", "hedefte")`.
```
:::

::: gorev 2 · Öncelik başına uyum
Çözülmüş biletler için öncelik başına çözülen bilet sayısını (`cozulen`), hedefinde çözülenleri (`hedef_ici`) ve uyum oranını (`uyum`, yüzde, bir ondalık) getir; en alta `oncelik` alanı `TOPLAM` olan bir toplam satırı ekle (toplamın uyum oranı da hesaplansın).

```starter
sourcetype=biletler durum=çözüldü
| stats count as cozulen by oncelik
```

```test
eq(sutunlar, ["oncelik", "cozulen", "hedef_ici", "uyum"], "sütunlar")
eq(sonuc, [("düşük", 2, 2, 100.0), ("kritik", 3, 3, 100.0), ("orta", 3, 2, 66.7), ("yüksek", 3, 3, 100.0),
           ("TOPLAM", 11, 10, 90.9)], "dört öncelik ve toplam")
```

```solution
sourcetype=biletler durum=çözüldü
| eval sure_saat=round((strptime(kapanis, "%Y-%m-%d %H:%M")-strptime(acilis, "%Y-%m-%d %H:%M"))/3600, 1)
| lookup sla oncelik OUTPUT hedef_saat
| stats count as cozulen, count(eval(sure_saat<=hedef_saat)) as hedef_ici by oncelik
| appendpipe [stats sum(cozulen) as cozulen, sum(hedef_ici) as hedef_ici | eval oncelik="TOPLAM"]
| eval uyum=round(100*hedef_ici/cozulen, 1)
```

```hint
Hedefte çözülenler: `count(eval(sure_saat<=hedef_saat)) as hedef_ici`.
```

```hint
Toplam satırını oran hesaplanmadan **önce** ekle; böylece `eval uyum=...` toplam satırına da uygulanır.
```
:::

::: gorev 3 · Geciken açık biletler
Açık biletlerin yaşını (şimdiden açılış anına kadar geçen süre, saat, bir ondalık) `yas_saat` alanına hesapla, `hedef_saat`'i ekle ve **hedefini aşmış** açık biletleri en yaşlıdan en gence getir: `id`, `oncelik`, `yas_saat`, `hedef_saat`.

```starter
sourcetype=biletler durum=açık
| table id oncelik acilis
```

```test
eq(sutunlar, ["id", "oncelik", "yas_saat", "hedef_saat"], "sütunlar")
eq(sonuc, [(3, "orta", 165.7, 24), (5, "yüksek", 145.5, 8), (9, "yüksek", 116.5, 8), (10, "düşük", 98.8, 72),
           (12, "orta", 94.3, 24), (15, "düşük", 73.0, 72)], "hedefini aşmış altı açık bilet")
ok(kullanir("now"), "şimdiki zaman için now() kullan")
```

```solution
sourcetype=biletler durum=açık
| eval yas_saat=round((now()-strptime(acilis, "%Y-%m-%d %H:%M"))/3600, 1)
| lookup sla oncelik OUTPUT hedef_saat
| where yas_saat>hedef_saat
| sort -yas_saat
| table id oncelik yas_saat hedef_saat
```

```hint
Yaş: `round((now()-strptime(acilis, "%Y-%m-%d %H:%M"))/3600, 1)`.
```

```hint
`where yas_saat>hedef_saat`, sonra `sort -yas_saat`.
```
:::
